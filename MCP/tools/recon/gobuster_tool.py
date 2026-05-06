"""
Gobuster MCP Tool — Directory, DNS, VHost, and Fuzz brute-forcing.

Supports all four Gobuster modes with full option coverage.
"""
from __future__ import annotations
from typing import Annotated, Literal
from tools._base import require_tool, run_command, sanitize_arg, sanitize_target

def register_gobuster_tools(mcp):
    """Register all Gobuster tools on the given FastMCP instance."""

    @mcp.tool(tags={'recon', 'scanning', 'gobuster', 'directory'}, annotations={'title': 'Gobuster Directory/DNS/VHost/Fuzz Scanner', 'readOnlyHint': True, 'openWorldHint': True})
    async def recon_gobuster_scan(mode: Annotated[Literal['dir', 'dns', 'vhost', 'fuzz'], 'Gobuster mode'], target: Annotated[str, 'Target URL (dir/vhost/fuzz) or domain (dns)'], wordlist: Annotated[str, 'Path to wordlist file'], extensions: Annotated[str | None, "File extensions to search for (e.g. 'php,html,txt')"]=None, status_codes: Annotated[str | None, "Positive status codes (e.g. '200,301,302')"]=None, status_codes_blacklist: Annotated[str | None, 'Negative status codes to skip']=None, discover_backup: Annotated[bool, 'Search for backup files']=False, no_tls_validation: Annotated[bool, 'Skip TLS certificate verification']=False, follow_redirect: Annotated[bool, 'Follow redirects']=False, expanded: Annotated[bool, 'Show full URLs in output']=False, no_status: Annotated[bool, "Don't print status codes"]=False, hide_length: Annotated[bool, 'Hide response length']=False, add_slash: Annotated[bool, 'Append / to each request']=False, wildcard: Annotated[bool, 'Force continued operation on wildcard responses']=False, show_cname: Annotated[bool, 'Show CNAME records (dns mode)']=False, show_ips: Annotated[bool, 'Show IP addresses (dns mode)']=False, resolver: Annotated[str | None, 'Use custom DNS resolver']=None, threads: Annotated[int, 'Number of concurrent threads']=10, delay: Annotated[str | None, "Delay between requests (e.g. '100ms', '1s')"]=None, timeout_secs: Annotated[int, 'HTTP timeout in seconds']=10, cookies: Annotated[str | None, 'Cookies to send (key=value)']=None, headers: Annotated[str | None, "Extra headers (Header: Value). Separate multiple with '||'"]=None, username: Annotated[str | None, 'Username for basic auth']=None, password: Annotated[str | None, 'Password for basic auth']=None, user_agent: Annotated[str | None, 'Custom User-Agent string']=None, proxy: Annotated[str | None, 'HTTP proxy URL']=None, pattern_file: Annotated[str | None, 'File containing replacement patterns']=None, output_file: Annotated[str | None, 'Save results to file']=None, no_error: Annotated[bool, "Don't display errors"]=False, quiet: Annotated[bool, 'Quiet mode — only show results']=False, verbose: Annotated[bool, 'Verbose output']=False, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=600, wait_for_previous: bool=False) -> dict:
        """
        Run Gobuster in the specified mode for content discovery, DNS brute-forcing,
        virtual host discovery, or fuzzing.
        """
        require_tool('gobuster')
        target = sanitize_target(target)
        args = ['gobuster', mode]
        if mode == 'dns':
            args.extend(['-d', target])
        else:
            args.extend(['-u', target])
        args.extend(['-w', sanitize_arg(wordlist, 'wordlist')])
        args.extend(['-t', str(threads)])
        if mode == 'dir':
            if extensions:
                args.extend(['-x', sanitize_arg(extensions, 'extensions')])
            if status_codes:
                args.extend(['-s', sanitize_arg(status_codes, 'status_codes')])
            if status_codes_blacklist:
                args.extend(['-b', sanitize_arg(status_codes_blacklist, 'blacklist')])
            if discover_backup:
                args.append('-d')
            if add_slash:
                args.append('-f')
            if expanded:
                args.append('-e')
            if no_status:
                args.append('-n')
            if hide_length:
                args.append('--hide-length')
        if mode == 'dns':
            if show_cname:
                args.append('--show-cname')
            if show_ips:
                args.append('-i')
            if resolver:
                args.extend(['-r', sanitize_arg(resolver, 'resolver')])
        if no_tls_validation:
            args.append('-k')
        if follow_redirect:
            args.append('-r') if mode != 'dns' else None
        if wildcard:
            args.append('--wildcard')
        if delay:
            args.extend(['--delay', sanitize_arg(delay, 'delay')])
        if timeout_secs:
            args.extend(['--timeout', f'{timeout_secs}s'])
        if cookies:
            args.extend(['-c', sanitize_arg(cookies, 'cookies')])
        if headers:
            for h in headers.split('||'):
                args.extend(['-H', h.strip()])
        if username:
            args.extend(['-U', sanitize_arg(username, 'username')])
        if password:
            args.extend(['-P', sanitize_arg(password, 'password')])
        if user_agent:
            args.extend(['-a', user_agent])
        if proxy:
            args.extend(['--proxy', sanitize_arg(proxy, 'proxy')])
        if pattern_file:
            args.extend(['-p', sanitize_arg(pattern_file, 'pattern_file')])
        if output_file:
            args.extend(['-o', sanitize_arg(output_file, 'output_file')])
        if no_error:
            args.append('--no-error')
        if quiet:
            args.append('-q')
        if verbose:
            args.append('-v')
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'output': result.stdout, 'errors': result.stderr}