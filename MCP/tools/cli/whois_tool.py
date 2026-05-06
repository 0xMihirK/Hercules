"""
whois MCP Tool — Domain/IP registration lookup.
"""
from __future__ import annotations
from typing import Annotated
from tools._base import require_tool, run_command, sanitize_arg, sanitize_target

def register_whois_tools(mcp):

    @mcp.tool(tags={'cli', 'dns', 'whois'}, annotations={'title': 'WHOIS Lookup', 'readOnlyHint': True, 'openWorldHint': True})
    async def cli_whois_lookup(target: Annotated[str, 'Domain name or IP address to look up'], server: Annotated[str | None, 'Specific WHOIS server to query (-h)']=None, port: Annotated[int | None, 'WHOIS server port (-p)']=None, no_referral: Annotated[bool, "Don't follow referrals"]=False, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=30, wait_for_previous: bool=False) -> dict:
        """Perform WHOIS lookup for a domain or IP address."""
        require_tool('whois')
        args = ['whois']
        if server:
            args.extend(['-h', sanitize_arg(server, 'server')])
        if port:
            args.extend(['-p', str(port)])
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        args.append(sanitize_target(target))
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'output': result.stdout, 'errors': result.stderr}