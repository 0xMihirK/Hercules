"""
Dalfox MCP Tool — XSS vulnerability scanner.

Supports URL/pipe/file modes, custom payloads, blind XSS, WAF bypass.
"""
from __future__ import annotations
from typing import Annotated, Literal
from tools._base import require_tool, run_command, sanitize_arg, sanitize_target, parse_json_lines

def register_dalfox_tools(mcp):
    """Register Dalfox tools on the given FastMCP instance."""

    @mcp.tool(tags={'webapp', 'xss', 'dalfox'}, annotations={'title': 'Dalfox XSS Scanner', 'readOnlyHint': True, 'openWorldHint': True})
    async def webapp_dalfox_scan(target: Annotated[str, 'Target URL to scan for XSS'], mode: Annotated[Literal['url', 'file', 'sxss'], 'Scan mode']='url', target_file: Annotated[str | None, 'Path to file containing target URLs (file mode)']=None, custom_payload: Annotated[str | None, 'Custom XSS payload to test']=None, custom_payload_file: Annotated[str | None, 'Path to file with custom payloads']=None, blind_url: Annotated[str | None, 'Blind XSS callback URL for out-of-band detection']=None, parameter: Annotated[str | None, 'Specific parameter to test']=None, data: Annotated[str | None, 'POST data (param=value)']=None, method: Annotated[str | None, 'HTTP method (GET, POST, PUT, etc.)']=None, cookie: Annotated[str | None, 'Cookie header value']=None, headers: Annotated[str | None, "Custom headers (Header: Value). Sep with '||'"]=None, user_agent: Annotated[str | None, 'Custom User-Agent']=None, proxy: Annotated[str | None, 'HTTP proxy URL']=None, waf_evasion: Annotated[bool, 'Enable WAF evasion techniques']=False, mining_dom: Annotated[bool, 'Enable DOM-based XSS mining']=False, mining_dict: Annotated[bool, 'Enable dictionary-based mining']=False, deep_domxss: Annotated[bool, 'Deep DOM XSS scanning']=False, follow_redirects: Annotated[bool, 'Follow HTTP redirects']=False, timeout_secs: Annotated[int, 'HTTP timeout in seconds']=10, delay: Annotated[int | None, 'Delay between requests in ms']=None, worker: Annotated[int, 'Number of workers']=100, json_output: Annotated[bool, 'Enable JSON output']=True, only_discovery: Annotated[bool, 'Only perform parameter analysis, not full XSS testing']=False, silence: Annotated[bool, 'Silent mode']=False, verbose: Annotated[bool, 'Verbose output']=False, no_color: Annotated[bool, 'Disable colored output']=True, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=600, wait_for_previous: bool=False) -> dict:
        """
        Run Dalfox XSS vulnerability scanner against a target URL.

        Supports reflected, stored, and DOM-based XSS detection with
        custom payloads, blind XSS callbacks, and WAF bypass options.
        """
        require_tool('dalfox')
        args = ['dalfox']
        if mode == 'file' and target_file:
            args.extend(['file', sanitize_arg(target_file, 'target_file')])
        elif mode == 'sxss':
            args.extend(['sxss', sanitize_target(target)])
        else:
            args.extend(['url', sanitize_target(target)])
        if custom_payload:
            args.extend(['--custom-payload', custom_payload])
        if custom_payload_file:
            args.extend(['--custom-payload-file', sanitize_arg(custom_payload_file, 'payload_file')])
        if blind_url:
            args.extend(['--blind', sanitize_arg(blind_url, 'blind_url')])
        if parameter:
            args.extend(['-p', sanitize_arg(parameter, 'parameter')])
        if data:
            args.extend(['-d', data])
        if method:
            args.extend(['--method', method.upper()])
        if cookie:
            args.extend(['-C', cookie])
        if headers:
            for h in headers.split('||'):
                args.extend(['-H', h.strip()])
        if user_agent:
            args.extend(['--user-agent', user_agent])
        if proxy:
            args.extend(['--proxy', sanitize_arg(proxy, 'proxy')])
        if waf_evasion:
            args.append('--waf-evasion')
        if mining_dom:
            args.append('--mining-dom')
        if mining_dict:
            args.append('--mining-dict')
        if deep_domxss:
            args.append('--deep-domxss')
        if follow_redirects:
            args.append('--follow-redirects')
        args.extend(['--timeout', str(timeout_secs)])
        if delay:
            args.extend(['--delay', str(delay)])
        args.extend(['--worker', str(worker)])
        if json_output:
            args.extend(['--format', 'json'])
        if only_discovery:
            args.append('--only-discovery')
        if silence:
            args.append('--silence')
        if verbose:
            args.append('--verbose')
        if no_color:
            args.append('--no-color')
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        result = await run_command(args, timeout=cmd_timeout)
        findings = []
        if json_output and result.stdout:
            findings = parse_json_lines(result.stdout)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'findings_count': len(findings), 'findings': findings, 'raw_output': result.stdout if not findings else '', 'errors': result.stderr}