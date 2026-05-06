"""
Volatility 3 MCP Tool — Memory forensics framework.

Supports all major Volatility3 plugins for Windows, Linux, and macOS memory analysis.
"""
from __future__ import annotations
from typing import Annotated, Literal
from tools._base import require_tool, run_command, sanitize_arg

def register_volatility_tools(mcp):
    """Register Volatility 3 tools on the given FastMCP instance."""

    @mcp.tool(tags={'forensics', 'memory', 'volatility'}, annotations={'title': 'Volatility 3 Memory Analyzer', 'readOnlyHint': True, 'openWorldHint': False})
    async def forensics_volatility_analyze(dump_file: Annotated[str, 'Path to memory dump file'], plugin: Annotated[str, 'Volatility3 plugin to run. Common plugins:\nWindows: windows.pslist, windows.pstree, windows.cmdline, windows.netscan, windows.filescan, windows.dlllist, windows.malfind, windows.hivelist, windows.hashdump, windows.handles, windows.svcscan, windows.driverirp, windows.registry.printkey, windows.vadinfo, windows.memmap, windows.envars, windows.getsids, windows.privileges, windows.sessions\nLinux: linux.pslist, linux.pstree, linux.bash, linux.check_afinfo, linux.check_creds, linux.check_idt, linux.check_modules, linux.check_syscall, linux.elfs, linux.lsmod, linux.malfind, linux.proc.maps\nMac: mac.pslist, mac.pstree, mac.bash, mac.check_syscall, mac.ifconfig, mac.lsmod, mac.malfind, mac.netstat\nGeneric: timeliner.Timeliner, layerwriter.LayerWriter'], plugin_args: Annotated[str | None, 'Plugin-specific arguments as key=value pairs (space-separated)']=None, pid: Annotated[int | None, 'Filter by specific process ID']=None, dump_dir: Annotated[str | None, 'Directory to dump extracted artifacts']=None, output_format: Annotated[Literal['text', 'json', 'csv'] | None, 'Output renderer format']=None, symbol_table: Annotated[str | None, 'Path to custom symbol table / ISF file']=None, quiet: Annotated[bool, 'Suppress progress output']=False, extra_args: Annotated[str | None, 'Additional raw arguments']=None, cmd_timeout: Annotated[int, 'Command timeout in seconds']=600, wait_for_previous: bool=False) -> dict:
        """
        Analyze a memory dump using Volatility 3 plugins.

        Provide the path to a memory dump and the plugin name.
        Supports all Volatility3 plugins for Windows, Linux, and macOS memory analysis.
        """
        require_tool('vol')
        args = ['vol', '-f', sanitize_arg(dump_file, 'dump_file')]
        if symbol_table:
            args.extend(['--symbol-path', sanitize_arg(symbol_table, 'symbol_table')])
        if output_format:
            args.extend(['-r', output_format])
        if quiet:
            args.append('-q')
        args.append(sanitize_arg(plugin, 'plugin'))
        if pid is not None:
            args.extend(['--pid', str(pid)])
        if dump_dir:
            args.extend(['--dump-dir', sanitize_arg(dump_dir, 'dump_dir')])
        if plugin_args:
            for pa in plugin_args.split():
                args.append(sanitize_arg(pa, 'plugin_arg'))
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        result = await run_command(args, timeout=cmd_timeout)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'output': result.stdout, 'errors': result.stderr}