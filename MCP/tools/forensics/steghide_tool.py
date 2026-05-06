"""
Steghide MCP Tool — Steganography embed/extract/info.

Hide and extract data within image and audio files.
"""
from __future__ import annotations
from typing import Annotated, Literal
from tools._base import require_tool, run_command, sanitize_arg

def register_steghide_tools(mcp):
    """Register Steghide tools on the given FastMCP instance."""

    @mcp.tool(tags={'forensics', 'steganography', 'steghide'}, annotations={'title': 'Steghide Embed Data', 'readOnlyHint': False, 'openWorldHint': False})
    async def forensics_steghide_embed(cover_file: Annotated[str, 'Path to cover file (JPEG, BMP, WAV, AU)'], embed_file: Annotated[str, 'Path to file to embed/hide'], stego_file: Annotated[str | None, 'Output stego file path (default: overwrite cover)']=None, passphrase: Annotated[str | None, 'Passphrase for encryption (empty = no encryption)']=None, encryption: Annotated[str | None, "Encryption algorithm (e.g. 'rijndael-128', 'des', 'none')"]=None, compression: Annotated[int | None, 'Compression level 1-9 (1=fast, 9=best)']=None, force: Annotated[bool, 'Overwrite existing stego file']=False, cmd_timeout: Annotated[int, 'Command timeout in seconds']=120, wait_for_previous: bool=False) -> dict:
        """
        Embed (hide) data inside a cover file using steganography.
        """
        require_tool('steghide')
        args = ['steghide', 'embed']
        args.extend(['-cf', sanitize_arg(cover_file, 'cover_file')])
        args.extend(['-ef', sanitize_arg(embed_file, 'embed_file')])
        if stego_file:
            args.extend(['-sf', sanitize_arg(stego_file, 'stego_file')])
        if passphrase is not None:
            args.extend(['-p', passphrase])
        else:
            args.extend(['-p', ''])
        if encryption:
            args.extend(['-e', sanitize_arg(encryption, 'encryption')])
        if compression is not None:
            args.extend(['-z', str(compression)])
        if force:
            args.append('-f')
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'output': result.stdout, 'errors': result.stderr}

    @mcp.tool(tags={'forensics', 'steganography', 'steghide'}, annotations={'title': 'Steghide Extract Data', 'readOnlyHint': False, 'openWorldHint': False})
    async def forensics_steghide_extract(stego_file: Annotated[str, 'Path to stego file containing hidden data'], extract_to: Annotated[str | None, 'Output file path for extracted data']=None, passphrase: Annotated[str | None, 'Passphrase for decryption (empty = no passphrase)']=None, force: Annotated[bool, 'Overwrite existing output file']=False, cmd_timeout: Annotated[int, 'Command timeout in seconds']=120, wait_for_previous: bool=False) -> dict:
        """
        Extract hidden data from a steganographic file.
        """
        require_tool('steghide')
        args = ['steghide', 'extract']
        args.extend(['-sf', sanitize_arg(stego_file, 'stego_file')])
        if extract_to:
            args.extend(['-xf', sanitize_arg(extract_to, 'extract_to')])
        if passphrase is not None:
            args.extend(['-p', passphrase])
        else:
            args.extend(['-p', ''])
        if force:
            args.append('-f')
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'output': result.stdout, 'errors': result.stderr}

    @mcp.tool(tags={'forensics', 'steganography', 'steghide'}, annotations={'title': 'Steghide Info', 'readOnlyHint': True, 'openWorldHint': False})
    async def forensics_steghide_info(stego_file: Annotated[str, 'Path to file to inspect'], passphrase: Annotated[str | None, 'Passphrase (if encrypted)']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=30, wait_for_previous: bool=False) -> dict:
        """
        Display information about a stego file (capacity, embedded data details).
        """
        require_tool('steghide')
        args = ['steghide', 'info', sanitize_arg(stego_file, 'stego_file')]
        if passphrase is not None:
            args.extend(['-p', passphrase])
        else:
            args.extend(['-p', ''])
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'info': result.stdout, 'errors': result.stderr}