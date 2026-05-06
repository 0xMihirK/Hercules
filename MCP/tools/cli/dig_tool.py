"""
dig MCP Tool — DNS lookup utility.
"""
from __future__ import annotations
from typing import Annotated, Literal
from tools._base import require_tool, run_command, sanitize_arg, sanitize_target

def register_dig_tools(mcp):

    @mcp.tool(tags={'cli', 'dns', 'dig'}, annotations={'title': 'dig DNS Lookup', 'readOnlyHint': True, 'openWorldHint': True})
    async def cli_dig_lookup(domain: Annotated[str, 'Domain name to query'], record_type: Annotated[Literal['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'PTR', 'SRV', 'ANY'] | None, 'DNS record type to query']=None, server: Annotated[str | None, 'Specific DNS server to query (@server)']=None, short: Annotated[bool, 'Short output — only answers (+short)']=False, trace: Annotated[bool, 'Trace delegation path (+trace)']=False, dnssec: Annotated[bool, 'Request DNSSEC records (+dnssec)']=False, reverse: Annotated[bool, 'Reverse DNS lookup (-x)']=False, tcp: Annotated[bool, 'Use TCP instead of UDP (+tcp)']=False, no_recurse: Annotated[bool, 'Non-recursive query (+norecurse)']=False, timeout_secs: Annotated[int, 'Query timeout in seconds']=10, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=30, wait_for_previous: bool=False) -> dict:
        """Perform DNS lookups using dig."""
        require_tool('dig')
        args = ['dig']
        if server:
            args.append(f"@{sanitize_arg(server, 'server')}")
        if reverse:
            args.extend(['-x', sanitize_target(domain)])
        else:
            args.append(sanitize_target(domain))
        if record_type:
            args.append(record_type)
        if short:
            args.append('+short')
        if trace:
            args.append('+trace')
        if dnssec:
            args.append('+dnssec')
        if tcp:
            args.append('+tcp')
        if no_recurse:
            args.append('+norecurse')
        args.append(f'+time={timeout_secs}')
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'output': result.stdout, 'errors': result.stderr}