"""
strings MCP Tool — Extract printable strings from binary files.
"""
from __future__ import annotations
from typing import Annotated, Literal
from tools._base import require_tool, run_command, sanitize_arg

def register_strings_tools(mcp):

    @mcp.tool(tags={'cli', 'binary-analysis', 'strings'}, annotations={'title': 'strings — Extract Printable Strings', 'readOnlyHint': True, 'openWorldHint': False})
    async def cli_strings_extract(file_path: Annotated[str, 'Path to binary file'], min_length: Annotated[int, 'Minimum string length to extract']=4, encoding: Annotated[Literal['s', 'S', 'b', 'l', 'B', 'L'] | None, 'Character encoding: s=7-bit ASCII, S=8-bit, b=16-bit big-endian, l=16-bit little-endian, B=32-bit big, L=32-bit little']=None, offset: Annotated[bool, 'Print the offset of each string (-t d)']=False, radix: Annotated[Literal['o', 'd', 'x'] | None, 'Offset radix: o=octal, d=decimal, x=hex (-t)']=None, all_sections: Annotated[bool, 'Scan entire file, not just data sections (-a)']=True, grep_pattern: Annotated[str | None, 'Filter output with grep pattern']=None, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=120, wait_for_previous: bool=False) -> dict:
        """Extract printable strings from a binary file."""
        require_tool('strings')
        args = ['strings']
        args.extend(['-n', str(min_length)])
        if encoding:
            args.extend(['-e', encoding])
        if offset or radix:
            args.extend(['-t', radix or 'd'])
        if all_sections:
            args.append('-a')
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        args.append(sanitize_arg(file_path, 'file_path'))
        result = await run_command(args, timeout=cmd_timeout)
        output = result.stdout
        if grep_pattern:
            lines = output.splitlines()
            import re
            try:
                pat = re.compile(grep_pattern, re.IGNORECASE)
                lines = [l for l in lines if pat.search(l)]
            except re.error:
                lines = [l for l in lines if grep_pattern.lower() in l.lower()]
            output = '\n'.join(lines)
        return {'command': result.command, 'return_code': result.return_code, 'string_count': len(output.splitlines()), 'output': output, 'errors': result.stderr}