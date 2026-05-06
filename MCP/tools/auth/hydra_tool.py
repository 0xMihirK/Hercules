"""
Hydra MCP Tool — Network login cracker.

Supports 50+ protocols including SSH, FTP, HTTP, SMB, RDP, MySQL, etc.
"""
from __future__ import annotations
from typing import Annotated
from tools._base import require_tool, run_command, sanitize_arg, sanitize_target

def register_hydra_tools(mcp):
    """Register Hydra tools on the given FastMCP instance."""

    @mcp.tool(tags={'auth', 'password', 'hydra', 'brute-force'}, annotations={'title': 'Hydra Network Login Cracker', 'readOnlyHint': False, 'openWorldHint': True, 'destructiveHint': True})
    async def auth_hydra_attack(target: Annotated[str, 'Target IP or hostname'], service: Annotated[str, 'Service/protocol to attack (ssh, ftp, http-get, http-post-form, smtp, pop3, imap, mysql, mssql, postgres, rdp, telnet, smb, vnc, snmp, ldap, http-get-form, http-post, socks5, etc.)'], username: Annotated[str | None, 'Single username to test (-l)']=None, username_list: Annotated[str | None, 'Path to username wordlist (-L)']=None, password: Annotated[str | None, 'Single password to test (-p)']=None, password_list: Annotated[str | None, 'Path to password wordlist (-P)']=None, combo_file: Annotated[str | None, 'Path to colon-separated user:pass file (-C)']=None, port: Annotated[int | None, 'Target port (default: service default)']=None, service_options: Annotated[str | None, "Service-specific options (-m). E.g. for http-post-form: '/login:user=^USER^&pass=^PASS^:F=incorrect'"]=None, threads: Annotated[int, 'Number of parallel connections']=16, wait_time: Annotated[int | None, 'Wait time between connections in seconds (-w)']=None, exit_on_first: Annotated[bool, 'Stop after first valid pair found (-f)']=False, exit_on_first_per_host: Annotated[bool, 'Stop per host after first valid pair (-F)']=False, loop_users: Annotated[bool, 'Loop around users, not passwords (-u)']=False, use_ssl: Annotated[bool, 'Connect via SSL (-S)']=False, proxy: Annotated[str | None, 'Proxy in format http://host:port or socks5://host:port']=None, verbose: Annotated[bool, 'Verbose mode — show login+pass for each attempt (-v)']=False, very_verbose: Annotated[bool, 'Very verbose (-V)']=False, show_attempts: Annotated[bool, 'Show each attempt as login:password (-d for debug)']=False, output_file: Annotated[str | None, 'Save results to file (-o)']=None, restore: Annotated[str | None, 'Restore a previous aborted session']=None, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=600, wait_for_previous: bool=False) -> dict:
        """
        Run Hydra to brute-force network service credentials.

        Supports 50+ protocols. Provide a username/password (or wordlists)
        and the target service. For HTTP form attacks, use service 'http-post-form'
        with service_options specifying the form path and failure string.
        """
        require_tool('hydra')
        args = ['hydra']
        if username:
            args.extend(['-l', sanitize_arg(username, 'username')])
        elif username_list:
            args.extend(['-L', sanitize_arg(username_list, 'username_list')])
        if password:
            args.extend(['-p', sanitize_arg(password, 'password')])
        elif password_list:
            args.extend(['-P', sanitize_arg(password_list, 'password_list')])
        if combo_file:
            args.extend(['-C', sanitize_arg(combo_file, 'combo_file')])
        args.extend(['-t', str(threads)])
        if wait_time:
            args.extend(['-w', str(wait_time)])
        if exit_on_first:
            args.append('-f')
        if exit_on_first_per_host:
            args.append('-F')
        if loop_users:
            args.append('-u')
        if use_ssl:
            args.append('-S')
        if proxy:
            args.extend(['-o', sanitize_arg(proxy, 'proxy')])
        if port:
            args.extend(['-s', str(port)])
        if verbose:
            args.append('-v')
        if very_verbose:
            args.append('-V')
        if show_attempts:
            args.append('-d')
        if output_file:
            args.extend(['-o', sanitize_arg(output_file, 'output_file')])
        if restore:
            args.extend(['-R', sanitize_arg(restore, 'restore')])
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        args.append(sanitize_target(target))
        args.append(sanitize_arg(service, 'service'))
        if service_options:
            args.append(service_options)
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'output': result.stdout, 'errors': result.stderr}