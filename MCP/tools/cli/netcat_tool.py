"""
Netcat (nc) MCP Tool — TCP/UDP networking utility.

Connect, listen, port scan, and data transfer.
"""
from __future__ import annotations
from typing import Annotated
from tools._base import require_tool, run_command, sanitize_arg, sanitize_target

def register_netcat_tools(mcp):

    @mcp.tool(tags={'cli', 'network', 'netcat'}, annotations={'title': 'Netcat Connect', 'readOnlyHint': True, 'openWorldHint': True})
    async def cli_netcat_connect(host: Annotated[str, 'Target host/IP to connect to'], port: Annotated[int, 'Target port'], data: Annotated[str | None, 'Data to send after connecting']=None, udp: Annotated[bool, 'Use UDP instead of TCP']=False, verbose: Annotated[bool, 'Verbose output (-v)']=True, wait_secs: Annotated[int, 'Timeout for connection in seconds (-w)']=5, zero_io: Annotated[bool, 'Zero-I/O mode — report connection status only (-z)']=False, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=30, wait_for_previous: bool=False) -> dict:
        """Connect to a host:port using netcat. Optionally send data."""
        require_tool('nc')
        args = ['nc']
        if verbose:
            args.append('-v')
        if udp:
            args.append('-u')
        if zero_io:
            args.append('-z')
        args.extend(['-w', str(wait_secs)])
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        args.extend([sanitize_target(host), str(port)])
        result = await run_command(args, timeout=cmd_timeout, stdin_data=data)
        return {'command': result.command, 'return_code': result.return_code, 'output': result.stdout, 'errors': result.stderr}

    @mcp.tool(tags={'cli', 'network', 'netcat'}, annotations={'title': 'Netcat Listen', 'readOnlyHint': False, 'openWorldHint': True})
    async def cli_netcat_listen(port: Annotated[int, 'Port to listen on'], udp: Annotated[bool, 'Use UDP instead of TCP']=False, verbose: Annotated[bool, 'Verbose output (-v)']=True, keep_open: Annotated[bool, 'Keep listening after first connection (-k)']=False, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Timeout (listener will be killed after this)']=30, wait_for_previous: bool=False) -> dict:
        """Start a netcat listener on the given port (with timeout)."""
        require_tool('nc')
        args = ['nc', '-l']
        if verbose:
            args.append('-v')
        if udp:
            args.append('-u')
        if keep_open:
            args.append('-k')
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        args.append(str(port))
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'output': result.stdout, 'errors': result.stderr}