"""
SQLMap MCP Tool — Automatic SQL injection detection and exploitation.

Full feature set: detection, enumeration, OS interaction, tamper scripts.
"""
from __future__ import annotations
from typing import Annotated, Literal
from tools._base import require_tool, run_command, sanitize_arg, sanitize_target

def register_sqlmap_tools(mcp):
    """Register SQLMap tools on the given FastMCP instance."""

    @mcp.tool(tags={'webapp', 'sqli', 'sqlmap'}, annotations={'title': 'SQLMap SQL Injection Scanner', 'readOnlyHint': False, 'openWorldHint': True, 'destructiveHint': True})
    async def webapp_sqlmap_scan(url: Annotated[str | None, 'Target URL with query parameters']=None, request_file: Annotated[str | None, 'Path to saved HTTP request file (-r)']=None, google_dork: Annotated[str | None, 'Google dork to find targets (-g)']=None, level: Annotated[int, 'Detection level 1-5 (higher = more payloads)']=1, risk: Annotated[int, 'Risk level 1-3 (higher = more dangerous payloads)']=1, technique: Annotated[str | None, 'SQL injection techniques to test (B,E,U,S,T,Q)']=None, dbms: Annotated[str | None, "Force specific DBMS (e.g. 'MySQL', 'PostgreSQL')"]=None, parameter: Annotated[str | None, 'Specific parameter(s) to test (-p)']=None, prefix: Annotated[str | None, 'Injection payload prefix']=None, suffix: Annotated[str | None, 'Injection payload suffix']=None, list_dbs: Annotated[bool, 'Enumerate databases (--dbs)']=False, list_tables: Annotated[bool, 'Enumerate tables (--tables)']=False, list_columns: Annotated[bool, 'Enumerate columns (--columns)']=False, dump: Annotated[bool, 'Dump entries (--dump)']=False, dump_all: Annotated[bool, 'Dump all databases (--dump-all)']=False, database: Annotated[str | None, 'Target database name (-D)']=None, table: Annotated[str | None, 'Target table name (-T)']=None, column: Annotated[str | None, 'Target column(s) (-C)']=None, count: Annotated[bool, 'Get row count for tables (--count)']=False, schema: Annotated[bool, 'Enumerate DBMS schema (--schema)']=False, current_user: Annotated[bool, 'Retrieve DBMS current user (--current-user)']=False, current_db: Annotated[bool, 'Retrieve DBMS current database (--current-db)']=False, hostname: Annotated[bool, 'Retrieve DBMS hostname (--hostname)']=False, is_dba: Annotated[bool, 'Detect if current user is DBA (--is-dba)']=False, passwords: Annotated[bool, 'Enumerate users password hashes (--passwords)']=False, privileges: Annotated[bool, 'Enumerate user privileges (--privileges)']=False, roles: Annotated[bool, 'Enumerate user roles (--roles)']=False, os_shell: Annotated[bool, 'Prompt for an interactive OS shell (--os-shell)']=False, os_cmd: Annotated[str | None, 'Execute OS command (--os-cmd)']=None, file_read: Annotated[str | None, 'Read a file from the DBMS server (--file-read)']=None, file_write: Annotated[str | None, 'Write a local file to DBMS server (--file-write)']=None, file_dest: Annotated[str | None, 'Destination path on DBMS server (--file-dest)']=None, tamper: Annotated[str | None, "Comma-separated tamper scripts (e.g. 'space2comment,between')"]=None, random_agent: Annotated[bool, 'Use random User-Agent header']=False, method: Annotated[str | None, 'Force HTTP method (GET, POST, PUT)']=None, data: Annotated[str | None, 'POST data string']=None, cookie: Annotated[str | None, 'HTTP Cookie header value']=None, user_agent: Annotated[str | None, 'Custom User-Agent']=None, referer: Annotated[str | None, 'HTTP Referer header']=None, headers_extra: Annotated[str | None, "Extra headers (Header: Value). Sep with '||'"]=None, proxy: Annotated[str | None, 'HTTP proxy URL']=None, tor: Annotated[bool, 'Use Tor anonymity network']=False, batch: Annotated[bool, 'Non-interactive mode — use defaults (--batch)']=True, threads: Annotated[int, 'Number of concurrent threads']=1, forms: Annotated[bool, 'Automatically test forms (--forms)']=False, crawl_depth: Annotated[int | None, 'Crawl website from target URL (--crawl)']=None, output_dir: Annotated[str | None, 'Custom output directory']=None, verbose_level: Annotated[int | None, 'Verbosity level 0-6 (-v)']=None, flush_session: Annotated[bool, 'Flush session files (--flush-session)']=False, fresh_queries: Annotated[bool, 'Ignore session query results (--fresh-queries)']=False, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=600, wait_for_previous: bool=False) -> dict:
        """
        Run SQLMap for automatic SQL injection detection and exploitation.

        Provide a URL with query parameters, a saved request file, or a Google dork.
        Control detection depth with level/risk, and enumerate databases/tables/data.
        """
        require_tool('sqlmap')
        args = ['sqlmap']
        if url:
            args.extend(['-u', sanitize_target(url)])
        elif request_file:
            args.extend(['-r', sanitize_arg(request_file, 'request_file')])
        elif google_dork:
            args.extend(['-g', google_dork])
        else:
            return {'error': 'Provide url, request_file, or google_dork'}
        args.extend(['--level', str(level)])
        args.extend(['--risk', str(risk)])
        if technique:
            args.extend(['--technique', sanitize_arg(technique, 'technique')])
        if dbms:
            args.extend(['--dbms', sanitize_arg(dbms, 'dbms')])
        if parameter:
            args.extend(['-p', sanitize_arg(parameter, 'parameter')])
        if prefix:
            args.extend(['--prefix', prefix])
        if suffix:
            args.extend(['--suffix', suffix])
        if list_dbs:
            args.append('--dbs')
        if list_tables:
            args.append('--tables')
        if list_columns:
            args.append('--columns')
        if dump:
            args.append('--dump')
        if dump_all:
            args.append('--dump-all')
        if database:
            args.extend(['-D', sanitize_arg(database, 'database')])
        if table:
            args.extend(['-T', sanitize_arg(table, 'table')])
        if column:
            args.extend(['-C', sanitize_arg(column, 'column')])
        if count:
            args.append('--count')
        if schema:
            args.append('--schema')
        if current_user:
            args.append('--current-user')
        if current_db:
            args.append('--current-db')
        if hostname:
            args.append('--hostname')
        if is_dba:
            args.append('--is-dba')
        if passwords:
            args.append('--passwords')
        if privileges:
            args.append('--privileges')
        if roles:
            args.append('--roles')
        if os_shell:
            args.append('--os-shell')
        if os_cmd:
            args.extend(['--os-cmd', os_cmd])
        if file_read:
            args.extend(['--file-read', file_read])
        if file_write:
            args.extend(['--file-write', sanitize_arg(file_write, 'file_write')])
        if file_dest:
            args.extend(['--file-dest', file_dest])
        if tamper:
            args.extend(['--tamper', sanitize_arg(tamper, 'tamper')])
        if random_agent:
            args.append('--random-agent')
        if method:
            args.extend(['--method', method.upper()])
        if data:
            args.extend(['--data', data])
        if cookie:
            args.extend(['--cookie', cookie])
        if user_agent:
            args.extend(['--user-agent', user_agent])
        if referer:
            args.extend(['--referer', referer])
        if headers_extra:
            for h in headers_extra.split('||'):
                args.extend(['--headers', h.strip()])
        if proxy:
            args.extend(['--proxy', sanitize_arg(proxy, 'proxy')])
        if tor:
            args.append('--tor')
        if batch:
            args.append('--batch')
        args.extend(['--threads', str(threads)])
        if forms:
            args.append('--forms')
        if crawl_depth:
            args.extend(['--crawl', str(crawl_depth)])
        if output_dir:
            args.extend(['--output-dir', sanitize_arg(output_dir, 'output_dir')])
        if verbose_level is not None:
            args.extend(['-v', str(verbose_level)])
        if flush_session:
            args.append('--flush-session')
        if fresh_queries:
            args.append('--fresh-queries')
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'output': result.stdout, 'errors': result.stderr}