"""
traceroute MCP Tool — Network path tracing.
"""
from __future__ import annotations
from typing import Annotated, Literal
from tools._base import require_tool, run_command, sanitize_arg, sanitize_target

def register_traceroute_tools(mcp):

    @mcp.tool(tags={'cli', 'network', 'traceroute'}, annotations={'title': 'Traceroute', 'readOnlyHint': True, 'openWorldHint': True})
    async def cli_traceroute_run(target: Annotated[str, 'Target host/IP to trace route to'], max_hops: Annotated[int, 'Maximum number of hops']=30, protocol: Annotated[Literal['udp', 'icmp', 'tcp'] | None, 'Probe protocol']=None, port: Annotated[int | None, 'Destination port (for TCP/UDP probes)']=None, packet_size: Annotated[int | None, 'Probe packet size in bytes']=None, source: Annotated[str | None, 'Source address to use (-s)']=None, wait_secs: Annotated[int, 'Probe response timeout in seconds (-w)']=5, queries: Annotated[int | None, 'Number of probes per hop (-q)']=None, no_dns: Annotated[bool, "Don't resolve IP addresses to hostnames (-n)"]=False, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=120, wait_for_previous: bool=False) -> dict:
        """Trace the network path to a target host."""
        require_tool('traceroute')
        args = ['traceroute']
        if protocol == 'icmp':
            args.append('-I')
        elif protocol == 'tcp':
            args.append('-T')
        args.extend(['-m', str(max_hops)])
        args.extend(['-w', str(wait_secs)])
        if port:
            args.extend(['-p', str(port)])
        if packet_size:
            args.append(str(packet_size))
        if source:
            args.extend(['-s', sanitize_arg(source, 'source')])
        if queries:
            args.extend(['-q', str(queries)])
        if no_dns:
            args.append('-n')
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        args.append(sanitize_target(target))
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'output': result.stdout, 'errors': result.stderr}