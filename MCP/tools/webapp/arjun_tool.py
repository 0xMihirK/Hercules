"""
Arjun MCP Tool — HTTP parameter discovery.

Discovers hidden GET/POST/JSON/XML parameters on web endpoints.
"""
from __future__ import annotations
from typing import Annotated, Literal
from tools._base import require_tool, run_command, sanitize_arg, sanitize_target, make_temp_file, parse_json_file
import os

def register_arjun_tools(mcp):
    """Register Arjun tools on the given FastMCP instance."""

    @mcp.tool(tags={'webapp', 'parameter-discovery', 'arjun'}, annotations={'title': 'Arjun HTTP Parameter Discovery', 'readOnlyHint': True, 'openWorldHint': True})
    async def webapp_arjun_discover(url: Annotated[str, 'Target URL to discover parameters on'], method: Annotated[Literal['GET', 'POST', 'JSON', 'XML'], 'HTTP method / body type to use']='GET', wordlist: Annotated[str | None, 'Path to custom parameter wordlist']=None, input_file: Annotated[str | None, 'Path to file containing target URLs (-i)']=None, import_burp: Annotated[str | None, 'Path to Burp Suite export file to import']=None, import_raw: Annotated[str | None, 'Path to raw HTTP request file']=None, headers: Annotated[str | None, "Custom headers (Header: Value). Sep with '||'"]=None, delay: Annotated[int | None, 'Delay between requests in seconds']=None, timeout_secs: Annotated[int, 'HTTP request timeout in seconds']=15, threads: Annotated[int, 'Number of threads']=2, include: Annotated[str | None, 'Parameters to include in every request (comma-sep)']=None, stable: Annotated[bool, 'Only report confirmed parameters']=False, output_file: Annotated[str | None, 'Save results to file']=None, quiet: Annotated[bool, 'Quiet mode']=False, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=300, wait_for_previous: bool=False) -> dict:
        """
        Discover hidden HTTP parameters using Arjun.

        Arjun probes endpoints with large parameter wordlists to find
        parameters that affect the response, supporting GET, POST, JSON,
        and XML body types.
        """
        require_tool('arjun')
        args = ['arjun', '-u', sanitize_target(url)]
        args.extend(['-m', method])
        if wordlist:
            args.extend(['-w', sanitize_arg(wordlist, 'wordlist')])
        if input_file:
            args.extend(['-i', sanitize_arg(input_file, 'input_file')])
        if import_burp:
            args.extend(['--import', sanitize_arg(import_burp, 'import_burp')])
        if headers:
            for h in headers.split('||'):
                args.extend(['--headers', h.strip()])
        if delay:
            args.extend(['-d', str(delay)])
        args.extend(['-T', str(timeout_secs)])
        args.extend(['-t', str(threads)])
        if include:
            args.extend(['--include', sanitize_arg(include, 'include')])
        if stable:
            args.append('--stable')
        json_out = make_temp_file(suffix='.json')
        args.extend(['-oJ', json_out])
        if quiet:
            args.append('-q')
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        result = await run_command(args, timeout=cmd_timeout)
        parsed = {}
        if os.path.exists(json_out):
            try:
                parsed = parse_json_file(json_out)
            except Exception as e:
                parsed = {'parse_error': str(e)}
            finally:
                os.unlink(json_out)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'discovered_parameters': parsed, 'raw_output': result.stdout, 'errors': result.stderr}