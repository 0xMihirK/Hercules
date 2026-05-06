"""
FFuf MCP Tool — Fast web fuzzer wrapper.

Full support for directory/parameter/header/vhost fuzzing,
matchers, filters, recursion, multiple wordlists, and JSON output.
"""
from __future__ import annotations
from typing import Annotated, Literal
from tools._base import parse_json_file, require_tool, run_command, sanitize_arg, sanitize_target, make_temp_file
import os

def register_ffuf_tools(mcp):
    """Register FFuf tools on the given FastMCP instance."""

    @mcp.tool(tags={'webapp', 'fuzzing', 'ffuf'}, annotations={'title': 'FFuf Web Fuzzer', 'readOnlyHint': True, 'openWorldHint': True})
    async def webapp_ffuf_fuzz(url: Annotated[str, "Target URL with FUZZ keyword (e.g. 'http://target/FUZZ')"], wordlist: Annotated[str, 'Path to wordlist file (mapped to FUZZ keyword)'], wordlist2: Annotated[str | None, 'Second wordlist path (mapped to FUZ2 keyword)']=None, method: Annotated[str, 'HTTP method']='GET', data: Annotated[str | None, 'POST data (use FUZZ keyword for fuzzing)']=None, headers: Annotated[str | None, "Custom headers (Header: Value). Sep with '||'"]=None, cookies: Annotated[str | None, 'Cookie data (name=value)']=None, match_codes: Annotated[str | None, "Match HTTP status codes (e.g. '200,301,302')"]=None, match_size: Annotated[str | None, 'Match response size']=None, match_words: Annotated[str | None, 'Match word count in response']=None, match_lines: Annotated[str | None, 'Match line count in response']=None, match_regex: Annotated[str | None, 'Match response with regex']=None, match_time: Annotated[str | None, "Match response time (e.g. '>500')"]=None, filter_codes: Annotated[str | None, 'Filter (exclude) HTTP status codes']=None, filter_size: Annotated[str | None, 'Filter response size']=None, filter_words: Annotated[str | None, 'Filter word count']=None, filter_lines: Annotated[str | None, 'Filter line count']=None, filter_regex: Annotated[str | None, 'Filter with regex']=None, filter_time: Annotated[str | None, 'Filter response time']=None, threads: Annotated[int, 'Number of concurrent threads']=40, rate: Annotated[int | None, 'Requests per second limit']=None, delay: Annotated[str | None, "Delay between requests (e.g. '0.1')"]=None, recursion: Annotated[bool, 'Enable recursion on found directories']=False, recursion_depth: Annotated[int | None, 'Max recursion depth']=None, recursion_strategy: Annotated[Literal['default', 'greedy'] | None, 'Recursion strategy']=None, extensions: Annotated[str | None, "Extensions to add to wordlist entries (e.g. '.php,.html')"]=None, proxy: Annotated[str | None, 'HTTP proxy URL']=None, replay_proxy: Annotated[str | None, 'Replay matched requests through this proxy']=None, timeout: Annotated[int, 'HTTP request timeout in seconds']=10, follow_redirects: Annotated[bool, 'Follow redirects']=False, max_redirects: Annotated[int | None, 'Maximum redirect hops']=None, auto_calibrate: Annotated[bool, 'Automatically calibrate filtering options']=False, stop_on_errors: Annotated[bool, 'Stop on spurious errors']=False, stop_on_all: Annotated[bool, 'Stop after first match']=False, silent: Annotated[bool, 'Silent mode — only show results']=False, verbose: Annotated[bool, 'Verbose output']=False, no_color: Annotated[bool, 'Disable colored output']=True, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=600, wait_for_previous: bool=False) -> dict:
        """
        Run FFuf web fuzzer for directory/file/parameter/vhost discovery.

        Place the FUZZ keyword in the URL, headers, or POST data to indicate
        where wordlist entries should be substituted.
        """
        require_tool('ffuf')
        args = ['ffuf']
        args.extend(['-u', url])
        args.extend(['-w', sanitize_arg(wordlist, 'wordlist')])
        if wordlist2:
            args.extend(['-w', f"{sanitize_arg(wordlist2, 'wordlist2')}:FUZ2"])
        args.extend(['-X', method.upper()])
        if data:
            args.extend(['-d', data])
        if headers:
            for h in headers.split('||'):
                args.extend(['-H', h.strip()])
        if cookies:
            args.extend(['-b', cookies])
        if match_codes:
            args.extend(['-mc', sanitize_arg(match_codes, 'mc')])
        if match_size:
            args.extend(['-ms', sanitize_arg(match_size, 'ms')])
        if match_words:
            args.extend(['-mw', sanitize_arg(match_words, 'mw')])
        if match_lines:
            args.extend(['-ml', sanitize_arg(match_lines, 'ml')])
        if match_regex:
            args.extend(['-mr', match_regex])
        if match_time:
            args.extend(['-mt', sanitize_arg(match_time, 'mt')])
        if filter_codes:
            args.extend(['-fc', sanitize_arg(filter_codes, 'fc')])
        if filter_size:
            args.extend(['-fs', sanitize_arg(filter_size, 'fs')])
        if filter_words:
            args.extend(['-fw', sanitize_arg(filter_words, 'fw')])
        if filter_lines:
            args.extend(['-fl', sanitize_arg(filter_lines, 'fl')])
        if filter_regex:
            args.extend(['-fr', filter_regex])
        if filter_time:
            args.extend(['-ft', sanitize_arg(filter_time, 'ft')])
        args.extend(['-t', str(threads)])
        if rate:
            args.extend(['-rate', str(rate)])
        if delay:
            args.extend(['-p', sanitize_arg(delay, 'delay')])
        if recursion:
            args.append('-recursion')
        if recursion_depth:
            args.extend(['-recursion-depth', str(recursion_depth)])
        if recursion_strategy:
            args.extend(['-recursion-strategy', recursion_strategy])
        if extensions:
            args.extend(['-e', sanitize_arg(extensions, 'extensions')])
        if proxy:
            args.extend(['-x', sanitize_arg(proxy, 'proxy')])
        if replay_proxy:
            args.extend(['-replay-proxy', sanitize_arg(replay_proxy, 'replay_proxy')])
        args.extend(['-timeout', str(timeout)])
        if follow_redirects:
            args.append('-r')
        if max_redirects:
            args.extend(['-maxredirects', str(max_redirects)])
        if auto_calibrate:
            args.append('-ac')
        if stop_on_errors:
            args.append('-se')
        if stop_on_all:
            args.append('-sa')
        if silent:
            args.append('-s')
        if verbose:
            args.append('-v')
        if no_color:
            args.append('-noninteractive')
        json_out = make_temp_file(suffix='.json')
        args.extend(['-o', json_out, '-of', 'json'])
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
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'results': parsed.get('results', []) if isinstance(parsed, dict) else [], 'raw_output': result.stdout, 'errors': result.stderr}