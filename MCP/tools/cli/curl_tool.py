"""
curl MCP Tool — HTTP client wrapper.

Full HTTP request capabilities with headers, auth, cookies, proxy, and SSL.
"""
from __future__ import annotations
from typing import Annotated, Literal
from tools._base import require_tool, run_command, sanitize_arg, sanitize_target

def register_curl_tools(mcp):

    @mcp.tool(tags={'cli', 'http', 'curl'}, annotations={'title': 'cURL HTTP Client', 'readOnlyHint': True, 'openWorldHint': True})
    async def cli_curl_request(url: Annotated[str, 'Target URL'], method: Annotated[str, 'HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)']='GET', headers: Annotated[str | None, "Custom headers (Header: Value). Sep with '||'"]=None, data: Annotated[str | None, 'Request body / POST data']=None, data_file: Annotated[str | None, 'Path to file to send as request body (@file)']=None, form_data: Annotated[str | None, "Form data (key=value). Sep with '||'. Use @file for uploads."]=None, auth_basic: Annotated[str | None, "Basic auth as 'user:password'"]=None, auth_bearer: Annotated[str | None, 'Bearer token']=None, auth_digest: Annotated[str | None, "Digest auth as 'user:password'"]=None, cookies: Annotated[str | None, 'Cookies (name=value; name2=value2)']=None, cookie_jar: Annotated[str | None, 'Path to save cookies to']=None, cookie_file: Annotated[str | None, 'Path to read cookies from']=None, follow_redirects: Annotated[bool, 'Follow redirects (-L)']=True, max_redirects: Annotated[int | None, 'Max redirects to follow']=None, timeout_secs: Annotated[int, 'Connection timeout in seconds']=30, max_time: Annotated[int | None, 'Maximum time for entire operation in seconds']=None, proxy: Annotated[str | None, 'Proxy URL (http, https, socks5)']=None, insecure: Annotated[bool, 'Skip SSL certificate verification (-k)']=False, cert: Annotated[str | None, 'Client certificate file path']=None, key: Annotated[str | None, 'Client private key file path']=None, user_agent: Annotated[str | None, 'Custom User-Agent']=None, referer: Annotated[str | None, 'Referer header']=None, compressed: Annotated[bool, 'Request compressed response']=False, include_headers: Annotated[bool, 'Include response headers in output (-i)']=True, head_only: Annotated[bool, 'HEAD request — get headers only (-I)']=False, silent: Annotated[bool, 'Silent mode — no progress/errors (-s)']=True, verbose: Annotated[bool, 'Verbose output (-v)']=False, output_file: Annotated[str | None, 'Save response body to file']=None, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=120, wait_for_previous: bool=False) -> dict:
        """
        Make an HTTP request using cURL with full control over method,
        headers, auth, cookies, proxy, SSL, and response handling.
        """
        require_tool('curl')
        args = ['curl']
        if silent:
            args.append('-s')
        if include_headers:
            args.append('-i')
        if head_only:
            args.append('-I')
        if verbose:
            args.append('-v')
        args.extend(['-X', method.upper()])
        if headers:
            for h in headers.split('||'):
                args.extend(['-H', h.strip()])
        if data:
            args.extend(['-d', data])
        if data_file:
            args.extend(['-d', f"@{sanitize_arg(data_file, 'data_file')}"])
        if form_data:
            for f in form_data.split('||'):
                args.extend(['-F', f.strip()])
        if auth_basic:
            args.extend(['-u', auth_basic])
        if auth_bearer:
            args.extend(['-H', f'Authorization: Bearer {auth_bearer}'])
        if auth_digest:
            args.extend(['--digest', '-u', auth_digest])
        if cookies:
            args.extend(['-b', cookies])
        if cookie_file:
            args.extend(['-b', sanitize_arg(cookie_file, 'cookie_file')])
        if cookie_jar:
            args.extend(['-c', sanitize_arg(cookie_jar, 'cookie_jar')])
        if follow_redirects:
            args.append('-L')
        if max_redirects:
            args.extend(['--max-redirs', str(max_redirects)])
        args.extend(['--connect-timeout', str(timeout_secs)])
        if max_time:
            args.extend(['--max-time', str(max_time)])
        if proxy:
            args.extend(['-x', sanitize_arg(proxy, 'proxy')])
        if insecure:
            args.append('-k')
        if cert:
            args.extend(['--cert', sanitize_arg(cert, 'cert')])
        if key:
            args.extend(['--key', sanitize_arg(key, 'key')])
        if user_agent:
            args.extend(['-A', user_agent])
        if referer:
            args.extend(['-e', referer])
        if compressed:
            args.append('--compressed')
        if output_file:
            args.extend(['-o', sanitize_arg(output_file, 'output_file')])
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        args.append(sanitize_target(url))
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'response': result.stdout, 'errors': result.stderr}