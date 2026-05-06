"""
Nmap MCP Tool — Full-featured network scanner wrapper.

Exposes the complete Nmap feature set: scan types, host discovery,
port specification, service/version/OS detection, script scanning,
timing, and structured XML output parsing.
"""
from __future__ import annotations
import os
from typing import Annotated, Literal
from pydantic import Field
from tools._base import OUTPUT_DIR, parse_xml_to_dict, require_tool, run_command, sanitize_arg, sanitize_target

def register_nmap_tools(mcp):
    """Register all Nmap tools on the given FastMCP instance."""

    @mcp.tool(tags={'recon', 'scanning', 'nmap'}, annotations={'title': 'Nmap Network Scanner', 'readOnlyHint': True, 'openWorldHint': True})
    async def recon_nmap_scan(target: Annotated[str, 'Target IP, hostname, CIDR range, or comma-separated list'], scan_type: Annotated[Literal['syn', 'connect', 'udp', 'ack', 'fin', 'xmas', 'null', 'ping'], 'Type of scan to perform']='syn', ports: Annotated[str | None, "Port specification (e.g. '22,80,443', '1-1024', '-' for all)"]=None, top_ports: Annotated[int | None, 'Scan the N most common ports']=None, fast_mode: Annotated[bool, 'Fast mode — scan only top 100 ports (-F)']=False, service_version: Annotated[bool, 'Probe open ports for service/version info (-sV)']=False, version_intensity: Annotated[int | None, Field(description='Version detection intensity 0-9', ge=0, le=9)]=None, os_detection: Annotated[bool, 'Enable OS detection (-O)']=False, script_scan: Annotated[bool, 'Run default NSE scripts (-sC)']=False, scripts: Annotated[str | None, "Comma-separated NSE scripts or categories (e.g. 'vuln,safe')"]=None, script_args: Annotated[str | None, 'NSE script arguments (key=value pairs)']=None, aggressive: Annotated[bool, 'Aggressive mode — enables -A (OS, version, scripts, traceroute)']=False, timing: Annotated[Literal['T0', 'T1', 'T2', 'T3', 'T4', 'T5'] | None, 'Timing template (T0=paranoid … T5=insane)']=None, no_ping: Annotated[bool, 'Treat all hosts as online — skip host discovery (-Pn)']=False, ping_only: Annotated[bool, 'Ping scan only — no port scan (-sn)']=False, tcp_syn_discovery: Annotated[str | None, 'TCP SYN discovery ports (-PS<ports>)']=None, tcp_ack_discovery: Annotated[str | None, 'TCP ACK discovery ports (-PA<ports>)']=None, udp_discovery: Annotated[str | None, 'UDP discovery ports (-PU<ports>)']=None, min_rate: Annotated[int | None, 'Minimum packets per second']=None, max_rate: Annotated[int | None, 'Maximum packets per second']=None, max_retries: Annotated[int | None, 'Maximum port scan probe retransmissions']=None, host_timeout: Annotated[str | None, "Give up on host after this time (e.g. '5m')"]=None, source_port: Annotated[int | None, 'Use given source port number']=None, interface: Annotated[str | None, 'Network interface to use']=None, spoof_mac: Annotated[str | None, 'Spoof MAC address']=None, decoys: Annotated[str | None, "Cloak scan with decoys (e.g. 'D1,D2,ME')"]=None, data_length: Annotated[int | None, 'Append random data to sent packets']=None, verbosity: Annotated[Literal[0, 1, 2] | None, 'Verbosity level (0=default, 1=-v, 2=-vv)']=None, reason: Annotated[bool, 'Display the reason a port is in a particular state (--reason)']=False, traceroute: Annotated[bool, 'Trace hop path to each host (--traceroute)']=False, privileged: Annotated[bool, 'Assume user is fully privileged (--privileged)']=False, extra_args: Annotated[str | None, 'Additional raw arguments (space-separated, validated)']=None, timeout: Annotated[int, 'Command timeout in seconds']=300, wait_for_previous: bool=False) -> dict:
        """
        Run an Nmap scan with full control over scan parameters.

        Returns structured results parsed from Nmap's XML output, including
        host status, open ports, services, OS guesses, and script output.
        """
        require_tool('nmap')
        target = sanitize_target(target)
        args = ['nmap']
        scan_map = {'syn': '-sS', 'connect': '-sT', 'udp': '-sU', 'ack': '-sA', 'fin': '-sF', 'xmas': '-sX', 'null': '-sN', 'ping': '-sn'}
        if scan_type == 'ping':
            args.append('-sn')
        else:
            args.append(scan_map[scan_type])
        if ports:
            args.extend(['-p', sanitize_arg(ports, 'ports')])
        if top_ports:
            args.extend(['--top-ports', str(top_ports)])
        if fast_mode:
            args.append('-F')
        if service_version:
            args.append('-sV')
        if version_intensity is not None:
            args.extend(['--version-intensity', str(version_intensity)])
        if os_detection:
            args.append('-O')
        if script_scan:
            args.append('-sC')
        if scripts:
            args.extend(['--script', sanitize_arg(scripts, 'scripts')])
        if script_args:
            args.extend(['--script-args', sanitize_arg(script_args, 'script_args')])
        if aggressive:
            args.append('-A')
        if timing:
            args.append(f'-{timing}')
        if no_ping:
            args.append('-Pn')
        if ping_only:
            args.append('-sn')
        if tcp_syn_discovery:
            args.append(f"-PS{sanitize_arg(tcp_syn_discovery, 'tcp_syn_discovery')}")
        if tcp_ack_discovery:
            args.append(f"-PA{sanitize_arg(tcp_ack_discovery, 'tcp_ack_discovery')}")
        if udp_discovery:
            args.append(f"-PU{sanitize_arg(udp_discovery, 'udp_discovery')}")
        if min_rate:
            args.extend(['--min-rate', str(min_rate)])
        if max_rate:
            args.extend(['--max-rate', str(max_rate)])
        if max_retries is not None:
            args.extend(['--max-retries', str(max_retries)])
        if host_timeout:
            args.extend(['--host-timeout', sanitize_arg(host_timeout, 'host_timeout')])
        if source_port:
            args.extend(['--source-port', str(source_port)])
        if interface:
            args.extend(['-e', sanitize_arg(interface, 'interface')])
        if spoof_mac:
            args.extend(['--spoof-mac', sanitize_arg(spoof_mac, 'spoof_mac')])
        if decoys:
            args.extend(['-D', sanitize_arg(decoys, 'decoys')])
        if data_length:
            args.extend(['--data-length', str(data_length)])
        if verbosity == 1:
            args.append('-v')
        elif verbosity == 2:
            args.append('-vv')
        if reason:
            args.append('--reason')
        if traceroute:
            args.append('--traceroute')
        if privileged:
            args.append('--privileged')
        xml_path = os.path.join(str(OUTPUT_DIR), f'nmap_{os.getpid()}.xml')
        args.extend(['-oX', xml_path])
        if extra_args:
            for a in extra_args.split():
                args.append(sanitize_arg(a, 'extra_args'))
        args.append(target)
        result = await run_command(args, timeout=timeout)
        parsed = {}
        if os.path.exists(xml_path):
            try:
                parsed = parse_xml_to_dict(xml_path)
            except Exception as e:
                parsed = {'xml_parse_error': str(e)}
            finally:
                os.unlink(xml_path)
        return {'command': result.command, 'return_code': result.return_code, 'timed_out': result.timed_out, 'raw_output': result.stdout, 'errors': result.stderr, 'parsed': parsed}