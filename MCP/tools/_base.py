"""
Shared helpers for all security tool wrappers.

Provides:
- Async subprocess execution with timeout & output capture
- Input sanitization to prevent command injection
- Common output parsers (XML, JSON)
- Tool-availability checks
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT = 300  # 5 minutes
MAX_OUTPUT_CHARS = 100_000  # ~100 KB inline limit

# Base directory for project files (templates, outputs, etc.)
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure working directories exist
TEMPLATES_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class CommandResult:
    """Result of a subprocess execution."""
    command: str
    return_code: int
    stdout: str
    stderr: str
    timed_out: bool = False

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "command": self.command,
            "return_code": self.return_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }
        if self.timed_out:
            result["timed_out"] = True
        return result


# ---------------------------------------------------------------------------
# Input sanitisation
# ---------------------------------------------------------------------------

# Characters that should never appear in a user-supplied argument
_DANGEROUS_CHARS = re.compile(r"[;&|`$(){}!<>\n\r]")


def sanitize_arg(value: str, name: str = "argument") -> str:
    """Validate a single CLI argument — reject shell meta-characters."""
    if _DANGEROUS_CHARS.search(value):
        raise ValueError(
            f"Invalid characters in {name}: {value!r}. "
            "Shell meta-characters are not allowed."
        )
    return value


def sanitize_target(target: str) -> str:
    """Validate a target (IP, hostname, URL) against injection."""
    return sanitize_arg(target, "target")


# ---------------------------------------------------------------------------
# Tool availability
# ---------------------------------------------------------------------------


def check_tool_installed(tool_name: str) -> bool:
    """Return True if *tool_name* binary is on $PATH."""
    return shutil.which(tool_name) is not None


def require_tool(tool_name: str) -> None:
    """Raise RuntimeError if *tool_name* is not installed."""
    if not check_tool_installed(tool_name):
        raise RuntimeError(
            f"'{tool_name}' is not installed or not on $PATH. "
            f"Please install it before using this tool."
        )


# ---------------------------------------------------------------------------
# Async command runner
# ---------------------------------------------------------------------------


import httpx

async def _stream_output(stream, is_stderr: bool, command_name: str, scan_id: str) -> str:
    """Read lines from a stream and POST them to the backend."""
    output_lines = []
    async for line_bytes in stream:
        line = line_bytes.decode(errors="replace")
        output_lines.append(line)
        line_stripped = line.strip()
        if line_stripped and scan_id:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"http://localhost:8000/api/internal/stream_log/{scan_id}",
                        json={"message": f"[{command_name}] {line_stripped}", "phase": "running", "progress": 0},
                        timeout=1.0
                    )
            except Exception:
                pass
    return "".join(output_lines)

async def run_command(
    args: list[str],
    *,
    timeout: int = DEFAULT_TIMEOUT,
    cwd: str | Path | None = None,
    env: dict[str, str] | None = None,
    stdin_data: str | None = None,
) -> CommandResult:
    """
    Run *args* as a subprocess.  Never uses shell=True.

    Returns a ``CommandResult`` with stdout, stderr, return code, and
    whether a timeout occurred.
    """
    cmd_str = " ".join(args)
    command_name = args[0]
    scan_id = os.environ.get("SCAN_ID")

    merged_env = {**os.environ, **(env or {})}

    proc = await asyncio.create_subprocess_exec(
        *args,
        stdin=asyncio.subprocess.PIPE if stdin_data is not None else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
        env=merged_env,
    )

    if stdin_data and proc.stdin:
        proc.stdin.write(stdin_data.encode())
        await proc.stdin.drain()
        proc.stdin.close()

    timed_out = False
    stdout = ""
    stderr = ""
    
    try:
        stdout_task = asyncio.create_task(_stream_output(proc.stdout, False, command_name, scan_id))
        stderr_task = asyncio.create_task(_stream_output(proc.stderr, True, command_name, scan_id))
        
        await asyncio.wait_for(
            asyncio.gather(stdout_task, stderr_task, proc.wait()),
            timeout=timeout,
        )
        stdout = stdout_task.result()
        stderr = stderr_task.result()
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        timed_out = True
        # If tasks didn't finish, we might not get full output, but we try our best.
        if not stdout_task.done():
            stdout_task.cancel()
        if not stderr_task.done():
            stderr_task.cancel()
        stderr += f"\nCommand timed out after {timeout}s"

    # Truncate very large outputs
    if len(stdout) > MAX_OUTPUT_CHARS:
        stdout = stdout[:MAX_OUTPUT_CHARS] + f"\n\n... [truncated — {len(stdout)} chars total]"
    if len(stderr) > MAX_OUTPUT_CHARS:
        stderr = stderr[:MAX_OUTPUT_CHARS] + f"\n\n... [truncated — {len(stderr)} chars total]"

    # Provide helpful hints for common syntax errors
    if proc.returncode != 0 and stderr:
        lower_err = stderr.lower()
        if any(msg in lower_err for msg in ["unrecognized option", "invalid option", "illegal option", "invalid argument", "unknown parameter"]):
            stderr += "\n\n[MCP Hint]: A syntax error, invalid flag, or version mismatch occurred. To fix this, verify the exact tool parameters expected by the installed CLI version, or temporarily drop the parameter causing the crash."

    return CommandResult(
        command=cmd_str,
        return_code=proc.returncode if proc.returncode is not None else -1,
        stdout=stdout,
        stderr=stderr,
        timed_out=timed_out,
    )


# ---------------------------------------------------------------------------
# Output parsers
# ---------------------------------------------------------------------------


def parse_json_file(path: str | Path) -> Any:
    """Read and parse a JSON file, returning the Python object."""
    with open(path) as f:
        return json.load(f)


def parse_json_lines(text: str) -> list[dict]:
    """Parse newline-delimited JSON (JSONL) text."""
    results: list[dict] = []
    for line in text.strip().splitlines():
        line = line.strip()
        if line:
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return results


def parse_xml_to_dict(path: str | Path) -> dict[str, Any]:
    """Minimal XML → dict conversion (for Nmap XML output, etc.)."""
    tree = ET.parse(path)
    root = tree.getroot()
    return _xml_elem_to_dict(root)


def _xml_elem_to_dict(elem: ET.Element) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if elem.attrib:
        result["@attributes"] = dict(elem.attrib)
    children: dict[str, list] = {}
    for child in elem:
        tag = child.tag
        children.setdefault(tag, []).append(_xml_elem_to_dict(child))
    for tag, items in children.items():
        result[tag] = items if len(items) > 1 else items[0]
    if elem.text and elem.text.strip():
        result["#text"] = elem.text.strip()
    return result


def make_temp_file(suffix: str = "", content: str = "") -> str:
    """Create a temporary file and return its path.  Caller must clean up."""
    fd, path = tempfile.mkstemp(suffix=suffix, dir=str(OUTPUT_DIR))
    if content:
        with os.fdopen(fd, "w") as f:
            f.write(content)
    else:
        os.close(fd)
    return path
