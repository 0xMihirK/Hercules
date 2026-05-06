"""
FTP MCP Tool — FTP client for file operations.
"""
from __future__ import annotations
from typing import Annotated
from tools._base import require_tool, run_command, sanitize_arg, sanitize_target

def register_ftp_tools(mcp):

    @mcp.tool(tags={'cli', 'file-transfer', 'ftp'}, annotations={'title': 'FTP List Directory', 'readOnlyHint': True, 'openWorldHint': True})
    async def cli_ftp_list(host: Annotated[str, 'FTP server hostname/IP'], username: Annotated[str, 'FTP username']='anonymous', password: Annotated[str, 'FTP password']='anonymous@', remote_dir: Annotated[str | None, 'Remote directory to list']=None, port: Annotated[int, 'FTP port']=21, passive: Annotated[bool, 'Use passive mode']=True, tls: Annotated[bool, 'Use FTPS (FTP over TLS)']=False, cmd_timeout: Annotated[int, 'Command timeout in seconds']=30, wait_for_previous: bool=False) -> dict:
        """List files on an FTP server."""
        require_tool('curl')
        url = f'ftp://{sanitize_target(host)}:{port}/'
        if remote_dir:
            url += sanitize_arg(remote_dir, 'remote_dir')
            if not url.endswith('/'):
                url += '/'
        args = ['curl', '-s', '--list-only', '-u', f'{username}:{password}', url]
        if not passive:
            args.append('--ftp-port')
        if tls:
            args.append('--ssl-reqd')
        result = await run_command(args, timeout=cmd_timeout)
        files = [f for f in result.stdout.strip().splitlines() if f.strip()]
        return {'command': result.command, 'return_code': result.return_code, 'file_count': len(files), 'files': files, 'errors': result.stderr}

    @mcp.tool(tags={'cli', 'file-transfer', 'ftp'}, annotations={'title': 'FTP Download File', 'readOnlyHint': False, 'openWorldHint': True})
    async def cli_ftp_download(host: Annotated[str, 'FTP server hostname/IP'], remote_path: Annotated[str, 'Remote file path to download'], local_path: Annotated[str, 'Local path to save file to'], username: Annotated[str, 'FTP username']='anonymous', password: Annotated[str, 'FTP password']='anonymous@', port: Annotated[int, 'FTP port']=21, tls: Annotated[bool, 'Use FTPS']=False, cmd_timeout: Annotated[int, 'Command timeout in seconds']=300, wait_for_previous: bool=False) -> dict:
        """Download a file from an FTP server."""
        require_tool('curl')
        url = f"ftp://{sanitize_target(host)}:{port}/{sanitize_arg(remote_path, 'remote_path')}"
        args = ['curl', '-s', '-u', f'{username}:{password}', '-o', sanitize_arg(local_path, 'local_path'), url]
        if tls:
            args.append('--ssl-reqd')
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'output': result.stdout, 'errors': result.stderr}

    @mcp.tool(tags={'cli', 'file-transfer', 'ftp'}, annotations={'title': 'FTP Upload File', 'readOnlyHint': False, 'openWorldHint': True})
    async def cli_ftp_upload(host: Annotated[str, 'FTP server hostname/IP'], local_path: Annotated[str, 'Local file path to upload'], remote_path: Annotated[str, 'Remote destination path'], username: Annotated[str, 'FTP username']='anonymous', password: Annotated[str, 'FTP password']='anonymous@', port: Annotated[int, 'FTP port']=21, tls: Annotated[bool, 'Use FTPS']=False, create_dirs: Annotated[bool, 'Create remote directories as needed']=False, cmd_timeout: Annotated[int, 'Command timeout in seconds']=300, wait_for_previous: bool=False) -> dict:
        """Upload a file to an FTP server."""
        require_tool('curl')
        url = f"ftp://{sanitize_target(host)}:{port}/{sanitize_arg(remote_path, 'remote_path')}"
        args = ['curl', '-s', '-u', f'{username}:{password}', '-T', sanitize_arg(local_path, 'local_path'), url]
        if tls:
            args.append('--ssl-reqd')
        if create_dirs:
            args.append('--ftp-create-dirs')
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'output': result.stdout, 'errors': result.stderr}