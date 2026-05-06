"""
Foremost MCP Tool — File carving / data recovery.

Recovers files from disk images based on headers, footers, and data structures.
"""
from __future__ import annotations
from typing import Annotated
from tools._base import require_tool, run_command, sanitize_arg, OUTPUT_DIR

def register_foremost_tools(mcp):
    """Register Foremost tools on the given FastMCP instance."""

    @mcp.tool(tags={'forensics', 'file-carving', 'foremost'}, annotations={'title': 'Foremost File Carver / Data Recovery', 'readOnlyHint': False, 'openWorldHint': False})
    async def forensics_foremost_recover(input_file: Annotated[str, 'Path to disk image or file to carve from'], output_dir: Annotated[str | None, 'Output directory for recovered files']=None, file_types: Annotated[str | None, "Comma-separated file types to recover (e.g. 'jpg,png,pdf,doc,zip,exe,gif,bmp,avi,mpg,wav,ole,rar,htm,cpp'). Default: all supported types"]=None, verbose: Annotated[bool, 'Verbose mode — log all files found']=False, quiet: Annotated[bool, 'Quiet mode — suppress output']=False, audit_only: Annotated[bool, 'Only audit — write to audit file, not extract']=False, indirect_blocks: Annotated[bool, 'Detect indirect block use for Unix file systems']=False, config_file: Annotated[str | None, 'Path to custom configuration file']=None, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=600, wait_for_previous: bool=False) -> dict:
        """
        Recover (carve) files from a disk image or raw file using Foremost.

        Identifies files by headers, footers, and internal data structures.
        Common use cases: recovering deleted files from disk images,
        CTF forensics challenges, evidence recovery.
        """
        require_tool('foremost')
        args = ['foremost']
        if file_types:
            args.extend(['-t', sanitize_arg(file_types, 'file_types')])
        if output_dir:
            args.extend(['-o', sanitize_arg(output_dir, 'output_dir')])
        else:
            default_out = str(OUTPUT_DIR / 'foremost_output')
            args.extend(['-o', default_out])
        if verbose:
            args.append('-v')
        if quiet:
            args.append('-q')
        if audit_only:
            args.append('-a')
        if indirect_blocks:
            args.append('-d')
        if config_file:
            args.extend(['-c', sanitize_arg(config_file, 'config_file')])
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        args.extend(['-i', sanitize_arg(input_file, 'input_file')])
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'output': result.stdout, 'errors': result.stderr}