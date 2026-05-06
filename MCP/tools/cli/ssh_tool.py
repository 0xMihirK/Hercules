"""
SSH MCP Tool — Remote command execution and file transfer.
"""
from __future__ import annotations
from typing import Annotated
from tools._base import require_tool, run_command, sanitize_arg, sanitize_target

def register_ssh_tools(mcp):

    @mcp.tool(tags={'cli', 'remote', 'ssh'}, annotations={'title': 'SSH Remote Command', 'readOnlyHint': False, 'openWorldHint': True})
    async def cli_ssh_execute(host: Annotated[str, 'Remote host/IP'], command: Annotated[str, 'Command to execute on the remote host'], user: Annotated[str | None, 'SSH username']=None, password: Annotated[str | None, 'SSH password (uses sshpass)']=None, port: Annotated[int, 'SSH port']=22, key_file: Annotated[str | None, 'Path to private key file (-i)']=None, strict_host_key: Annotated[bool, 'Strict host key checking']=False, connect_timeout: Annotated[int, 'Connection timeout in seconds']=10, extra_args: Annotated[str | None, 'Additional SSH arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=120, wait_for_previous: bool=False) -> dict:
        """Execute a command on a remote host via SSH."""
        require_tool('ssh')
        args = []
        if password:
            require_tool('sshpass')
            args.extend(['sshpass', '-p', password])
        args.append('ssh')
        args.extend(['-p', str(port)])
        args.extend(['-o', f'ConnectTimeout={connect_timeout}'])
        if not strict_host_key:
            args.extend(['-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null'])
        if key_file:
            args.extend(['-i', sanitize_arg(key_file, 'key_file')])
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        target = f"{sanitize_arg(user, 'user')}@{sanitize_target(host)}" if user else sanitize_target(host)
        args.append(target)
        args.append(command)
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'output': result.stdout, 'errors': result.stderr}

    @mcp.tool(tags={'cli', 'remote', 'ssh', 'scp'}, annotations={'title': 'SCP File Transfer', 'readOnlyHint': False, 'openWorldHint': True})
    async def cli_scp_transfer(source: Annotated[str, 'Source path (local path or user@host:path)'], destination: Annotated[str, 'Destination path (local path or user@host:path)'], password: Annotated[str | None, 'SSH password (uses sshpass)']=None, port: Annotated[int, 'SSH port']=22, key_file: Annotated[str | None, 'Path to private key file (-i)']=None, recursive: Annotated[bool, 'Copy directories recursively (-r)']=False, strict_host_key: Annotated[bool, 'Strict host key checking']=False, extra_args: Annotated[str | None, 'Additional SCP arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=300, wait_for_previous: bool=False) -> dict:
        """Transfer files between local and remote hosts using SCP."""
        require_tool('scp')
        args = []
        if password:
            require_tool('sshpass')
            args.extend(['sshpass', '-p', password])
        args.append('scp')
        args.extend(['-P', str(port)])
        if not strict_host_key:
            args.extend(['-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null'])
        if key_file:
            args.extend(['-i', sanitize_arg(key_file, 'key_file')])
        if recursive:
            args.append('-r')
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        args.extend([source, destination])
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'output': result.stdout, 'errors': result.stderr}