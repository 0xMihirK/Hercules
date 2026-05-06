"""
John the Ripper MCP Tool — Password hash cracker.

Supports multiple modes: single, wordlist, incremental, mask.
"""
from __future__ import annotations
from typing import Annotated, Literal
from tools._base import require_tool, run_command, sanitize_arg

def register_john_tools(mcp):
    """Register John the Ripper tools on the given FastMCP instance."""

    @mcp.tool(tags={'auth', 'password', 'john', 'hash-cracking'}, annotations={'title': 'John the Ripper Password Cracker', 'readOnlyHint': False, 'openWorldHint': False})
    async def auth_john_crack(hash_file: Annotated[str, 'Path to file containing password hashes'], mode: Annotated[Literal['default', 'single', 'wordlist', 'incremental', 'mask'] | None, 'Cracking mode (default runs single → wordlist → incremental)']=None, wordlist: Annotated[str | None, 'Path to wordlist file (for wordlist mode)']=None, rules: Annotated[str | None, "Enable word mangling rules (e.g. 'Jumbo', 'All', 'Best64')"]=None, mask: Annotated[str | None, "Mask pattern (e.g. '?u?l?l?l?d?d') for mask mode"]=None, incremental_mode: Annotated[str | None, "Incremental mode charset (e.g. 'Digits', 'Alnum', 'ASCII')"]=None, format: Annotated[str | None, "Force hash format (e.g. 'raw-md5', 'bcrypt', 'sha256crypt', 'NT')"]=None, session: Annotated[str | None, 'Session name for save/restore']=None, restore: Annotated[str | None, 'Restore a previous session']=None, min_length: Annotated[int | None, 'Minimum password length']=None, max_length: Annotated[int | None, 'Maximum password length']=None, fork: Annotated[int | None, 'Number of parallel processes']=None, pot_file: Annotated[str | None, 'Custom pot file path to store cracked passwords']=None, show_types: Annotated[bool, 'Show supported hash formats (--list=formats)']=False, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=3600, wait_for_previous: bool=False) -> dict:
        """
        Crack password hashes using John the Ripper.

        Supports single crack, wordlist (+rules), incremental, and mask modes.
        Provide a hash file and optionally specify the format and cracking mode.
        """
        require_tool('john')
        if show_types:
            result = await run_command(['john', '--list=formats'], timeout=30)
            return {'command': result.command, 'supported_formats': result.stdout}
        args = ['john']
        if mode == 'single':
            args.append('--single')
        elif mode == 'wordlist':
            if wordlist:
                args.extend(['--wordlist', sanitize_arg(wordlist, 'wordlist')])
            else:
                args.append('--wordlist')
        elif mode == 'incremental':
            if incremental_mode:
                args.append(f"--incremental={sanitize_arg(incremental_mode, 'incremental')}")
            else:
                args.append('--incremental')
        elif mode == 'mask':
            if mask:
                args.extend(['--mask', sanitize_arg(mask, 'mask')])
        if rules:
            args.append(f"--rules={sanitize_arg(rules, 'rules')}")
        if format:
            args.append(f"--format={sanitize_arg(format, 'format')}")
        if session:
            args.extend(['--session', sanitize_arg(session, 'session')])
        if restore:
            args.extend(['--restore', sanitize_arg(restore, 'restore')])
        if min_length:
            args.extend(['--min-length', str(min_length)])
        if max_length:
            args.extend(['--max-length', str(max_length)])
        if fork:
            args.extend(['--fork', str(fork)])
        if pot_file:
            args.extend(['--pot', sanitize_arg(pot_file, 'pot_file')])
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        args.append(sanitize_arg(hash_file, 'hash_file'))
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'output': result.stdout, 'errors': result.stderr}

    @mcp.tool(tags={'auth', 'password', 'john', 'hash-cracking'}, annotations={'title': 'John the Ripper — Show Cracked Passwords', 'readOnlyHint': True, 'openWorldHint': False})
    async def auth_john_show(hash_file: Annotated[str, 'Path to hash file to show cracked passwords for'], format: Annotated[str | None, 'Hash format']=None, pot_file: Annotated[str | None, 'Custom pot file path']=None, wait_for_previous: bool=False) -> dict:
        """
        Show passwords that have been previously cracked by John the Ripper.
        """
        require_tool('john')
        args = ['john', '--show']
        if format:
            args.append(f"--format={sanitize_arg(format, 'format')}")
        if pot_file:
            args.extend(['--pot', sanitize_arg(pot_file, 'pot_file')])
        args.append(sanitize_arg(hash_file, 'hash_file'))
        result = await run_command(args, timeout=30)
        return {'command': result.command, 'return_code': result.return_code, 'cracked_passwords': result.stdout, 'errors': result.stderr}