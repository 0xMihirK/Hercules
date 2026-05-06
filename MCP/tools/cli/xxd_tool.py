"""
xxd MCP Tool — Hexdump and reverse hex.
"""
from __future__ import annotations
from typing import Annotated
from tools._base import require_tool, run_command, sanitize_arg

def register_xxd_tools(mcp):

    @mcp.tool(tags={'cli', 'binary-analysis', 'xxd'}, annotations={'title': 'xxd Hexdump', 'readOnlyHint': True, 'openWorldHint': False})
    async def cli_xxd_dump(file_path: Annotated[str, 'Path to file to hexdump'], length: Annotated[int | None, 'Number of bytes to dump (-l)']=None, seek: Annotated[int | None, 'Start at byte offset (-s)']=None, columns: Annotated[int | None, 'Octets per line (-c, default 16)']=None, plain: Annotated[bool, 'Plain hex output without ASCII (-p)']=False, include: Annotated[bool, 'Output in C include style (-i)']=False, uppercase: Annotated[bool, 'Use upper case hex letters (-u)']=False, bits: Annotated[bool, 'Binary (bits) dump instead of hex (-b)']=False, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=60, wait_for_previous: bool=False) -> dict:
        """Create a hexdump of a file."""
        require_tool('xxd')
        args = ['xxd']
        if length:
            args.extend(['-l', str(length)])
        if seek:
            args.extend(['-s', str(seek)])
        if columns:
            args.extend(['-c', str(columns)])
        if plain:
            args.append('-p')
        if include:
            args.append('-i')
        if uppercase:
            args.append('-u')
        if bits:
            args.append('-b')
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        args.append(sanitize_arg(file_path, 'file_path'))
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'output': result.stdout, 'errors': result.stderr}

    @mcp.tool(tags={'cli', 'binary-analysis', 'xxd'}, annotations={'title': 'xxd Reverse (Hex to Binary)', 'readOnlyHint': False, 'openWorldHint': False})
    async def cli_xxd_reverse(input_file: Annotated[str, 'Path to hex file to convert back to binary'], output_file: Annotated[str, 'Path to output binary file'], plain: Annotated[bool, 'Input is plain hex (-p)']=False, cmd_timeout: Annotated[int, 'Command timeout in seconds']=30, wait_for_previous: bool=False) -> dict:
        """Convert hexdump back to binary (reverse operation)."""
        require_tool('xxd')
        args = ['xxd', '-r']
        if plain:
            args.append('-p')
        args.extend([sanitize_arg(input_file, 'input'), sanitize_arg(output_file, 'output')])
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'output': result.stdout, 'errors': result.stderr}