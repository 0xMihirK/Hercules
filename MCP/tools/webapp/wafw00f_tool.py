"""
Wafw00f MCP Tool — Web Application Firewall detection.

Identifies WAF products protecting web applications.
"""
from __future__ import annotations
from typing import Annotated
from tools._base import require_tool, run_command, sanitize_arg, sanitize_target

def register_wafw00f_tools(mcp):
    """Register wafw00f tools on the given FastMCP instance."""

    @mcp.tool(tags={'webapp', 'waf', 'wafw00f'}, annotations={'title': 'Wafw00f WAF Detector', 'readOnlyHint': True, 'openWorldHint': True})
    async def webapp_wafw00f_detect(target: Annotated[str, "Target URL to check for WAF (e.g. 'https://example.com')"], test_all: Annotated[bool, 'Test for all known WAFs (not just first match)']=False, specific_waf: Annotated[str | None, "Test for a specific WAF only (e.g. 'Cloudflare')"]=None, input_file: Annotated[str | None, 'Path to file containing list of target URLs']=None, proxy: Annotated[str | None, 'HTTP proxy URL']=None, headers: Annotated[str | None, "Custom headers (Header: Value). Sep with '||'"]=None, verbose: Annotated[bool, 'Verbose output']=False, find_all: Annotated[bool, 'Find all WAFs, do not stop at first']=False, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=120, wait_for_previous: bool=False) -> dict:
        """
        Detect Web Application Firewalls (WAFs) protecting a target website.

        Uses wafw00f to identify WAF products like Cloudflare, AWS WAF,
        ModSecurity, Akamai, etc.
        """
        require_tool('wafw00f')
        args = ['wafw00f']
        if input_file:
            args.extend(['-i', sanitize_arg(input_file, 'input_file')])
        else:
            args.append(sanitize_target(target))
        if test_all:
            args.append('-a')
        if specific_waf:
            args.extend(['-t', sanitize_arg(specific_waf, 'specific_waf')])
        if proxy:
            args.extend(['-p', sanitize_arg(proxy, 'proxy')])
        if headers:
            for h in headers.split('||'):
                args.extend(['-H', h.strip()])
        if verbose:
            args.append('-v')
        if find_all:
            args.append('-a')
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'output': result.stdout, 'errors': result.stderr}