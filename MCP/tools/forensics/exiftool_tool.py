"""
ExifTool MCP Tool — Read, write, and remove metadata from files.

Supports JPEG, PNG, PDF, video, audio, and 400+ file formats.
"""
from __future__ import annotations
from typing import Annotated
from tools._base import require_tool, run_command, sanitize_arg
import json

def register_exiftool_tools(mcp):
    """Register ExifTool tools on the given FastMCP instance."""

    @mcp.tool(tags={'forensics', 'metadata', 'exiftool'}, annotations={'title': 'ExifTool Metadata Reader', 'readOnlyHint': True, 'openWorldHint': False})
    async def forensics_exiftool_read(file_path: Annotated[str, 'Path to file(s) or directory to read metadata from'], tags: Annotated[str | None, "Specific tags to extract (comma-sep, e.g. 'Author,DateCreated')"]=None, all_tags: Annotated[bool, 'Extract all tags including duplicates']=False, recursive: Annotated[bool, 'Process directories recursively']=False, file_type: Annotated[str | None, "Filter by file extension (e.g. 'jpg', 'pdf')"]=None, group_headings: Annotated[bool, 'Show tag group names (e.g. EXIF:, IPTC:)']=False, sort_output: Annotated[bool, 'Sort output alphabetically by tag name']=False, binary_output: Annotated[bool, 'Output binary values (for extracting thumbnails etc.)']=False, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=120, wait_for_previous: bool=False) -> dict:
        """
        Read metadata from files using ExifTool.

        Returns structured JSON metadata for the given file(s).
        Supports 400+ file formats including images, videos, PDFs, and documents.
        """
        require_tool('exiftool')
        args = ['exiftool', '-json']
        if tags:
            for t in tags.split(','):
                args.append(f'-{t.strip()}')
        if all_tags:
            args.append('-all')
        if recursive:
            args.append('-r')
        if file_type:
            args.extend(['-ext', sanitize_arg(file_type, 'file_type')])
        if group_headings:
            args.append('-G')
        if sort_output:
            args.append('-s')
        if binary_output:
            args.append('-b')
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        args.append(sanitize_arg(file_path, 'file_path'))
        result = await run_command(args, timeout=cmd_timeout)
        metadata = []
        if result.stdout.strip():
            try:
                metadata = json.loads(result.stdout)
            except json.JSONDecodeError:
                pass
        return {'command': result.command, 'return_code': result.return_code, 'file_count': len(metadata), 'metadata': metadata, 'errors': result.stderr}

    @mcp.tool(tags={'forensics', 'metadata', 'exiftool'}, annotations={'title': 'ExifTool Metadata Writer', 'readOnlyHint': False, 'openWorldHint': False})
    async def forensics_exiftool_write(file_path: Annotated[str, 'Path to file to modify'], tags: Annotated[str, "Tags to set as 'Tag=Value' pairs separated by '||' (e.g. 'Author=Agent||Title=Report')"], overwrite_original: Annotated[bool, 'Overwrite original file (no backup)']=False, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=60, wait_for_previous: bool=False) -> dict:
        """
        Write (set/modify) metadata tags on a file using ExifTool.
        """
        require_tool('exiftool')
        args = ['exiftool']
        for pair in tags.split('||'):
            pair = pair.strip()
            if '=' in pair:
                args.append(f'-{pair}')
        if overwrite_original:
            args.append('-overwrite_original')
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        args.append(sanitize_arg(file_path, 'file_path'))
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'output': result.stdout, 'errors': result.stderr}

    @mcp.tool(tags={'forensics', 'metadata', 'exiftool'}, annotations={'title': 'ExifTool Metadata Remover', 'readOnlyHint': False, 'openWorldHint': False, 'destructiveHint': True})
    async def forensics_exiftool_remove(file_path: Annotated[str, 'Path to file to strip metadata from'], specific_tags: Annotated[str | None, 'Specific tags to remove (comma-sep). If None, removes all.']=None, overwrite_original: Annotated[bool, 'Overwrite original file (no backup)']=False, cmd_timeout: Annotated[int, 'Command timeout in seconds']=60, wait_for_previous: bool=False) -> dict:
        """
        Remove metadata from a file using ExifTool.

        Without specific_tags, removes ALL metadata. Use specific_tags
        to selectively remove only certain fields.
        """
        require_tool('exiftool')
        args = ['exiftool']
        if specific_tags:
            for t in specific_tags.split(','):
                args.append(f'-{t.strip()}=')
        else:
            args.append('-all=')
        if overwrite_original:
            args.append('-overwrite_original')
        args.append(sanitize_arg(file_path, 'file_path'))
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'output': result.stdout, 'errors': result.stderr}