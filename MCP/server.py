#!/usr/bin/env python3
"""
Security Toolkit MCP Server
============================

A unified MCP server exposing 60 security and CLI tools for AI agents.

Categories:
  - RECON & SCANNING:  nmap, gobuster, nuclei
  - WEB APP TESTING:   ffuf, sqlmap, dalfox, arjun, wafw00f
  - AUTH & PASSWORD:    hydra, john the ripper
  - CTF & FORENSICS:   volatility3, exiftool, steghide, foremost
  - EXPLOITATION:      metasploit, searchsploit
  - BASIC CLI:         curl, netcat, dig, whois, traceroute, ssh/scp,
                       openssl, strings, xxd, grep, awk, sed, ftp

Usage:
  python server.py                      # Run with stdio transport
  fastmcp dev server.py                 # Run with MCP Inspector
  fastmcp install server.py             # Install into Claude Desktop
"""

from __future__ import annotations

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Create the server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="SecurityToolkit",
    instructions="""\
You are connected to a comprehensive security toolkit MCP server.
It provides 60 tools across 6 categories:

## RECON & SCANNING (prefix: recon_)
- recon_nmap_scan — Full Nmap network scanning
- recon_gobuster_scan — Directory/DNS/VHost/Fuzz brute-forcing
- recon_nuclei_scan — Vulnerability scanning with templates
- recon_nuclei_scan_custom — Run inline custom YAML templates
- recon_nuclei_template_create — Write custom Nuclei YAML templates
- recon_nuclei_template_list — List custom templates
- recon_nuclei_template_validate — Validate templates

## WEB APP TESTING (prefix: webapp_)
- webapp_ffuf_fuzz — Fast web fuzzing (directories, params, vhosts)
- webapp_sqlmap_scan — SQL injection detection & exploitation
- webapp_dalfox_scan — XSS vulnerability scanning
- webapp_arjun_discover — HTTP parameter discovery
- webapp_wafw00f_detect — WAF detection

## AUTH & PASSWORD (prefix: auth_)
- auth_hydra_attack — Network login brute-forcing (50+ protocols)
- auth_john_crack — Password hash cracking
- auth_john_show — Show cracked passwords

## CTF & FORENSICS (prefix: forensics_)
- forensics_volatility_analyze — Memory dump analysis
- forensics_exiftool_read/write/remove — File metadata operations
- forensics_steghide_embed/extract/info — Steganography
- forensics_foremost_recover — File carving from disk images

## EXPLOITATION (prefix: exploit_)
### Metasploit Framework
- exploit_msf_list_exploits — Search/list available exploits
- exploit_msf_list_payloads — List payloads filtered by platform/arch
- exploit_msf_generate_payload — Generate payloads/shellcode (msfvenom)
- exploit_msf_run_exploit — Run exploit modules (sync or async)
- exploit_msf_run_post — Run post-exploitation modules
- exploit_msf_run_auxiliary — Run auxiliary scanners
- exploit_msf_list_sessions — List active sessions
- exploit_msf_session_command — Execute commands in sessions
- exploit_msf_terminate_session — Kill sessions
- exploit_msf_list_listeners — List active listeners
- exploit_msf_start_listener — Start multi/handler listener
- exploit_msf_stop_job — Stop background jobs
- exploit_msf_server_info — Server status, network info, sessions
- exploit_msf_cleanup — Clean up consoles, jobs, and sessions
### Exploit-DB
- exploit_searchsploit_search — Search Exploit-DB
- exploit_searchsploit_examine — View exploit code
- exploit_searchsploit_update — Update Exploit-DB

## BASIC CLI (prefix: cli_)
- cli_curl_request — HTTP requests
- cli_netcat_connect/listen — TCP/UDP networking
- cli_dig_lookup — DNS lookups
- cli_whois_lookup — Domain/IP registration info
- cli_traceroute_run — Network path tracing
- cli_ssh_execute — Remote command execution
- cli_scp_transfer — File transfer over SSH
- cli_openssl_cert_info/connect/generate — TLS/SSL operations
- cli_strings_extract — Extract strings from binaries
- cli_xxd_dump/reverse — Hex dump and conversion
- cli_grep_search — Pattern matching in files
- cli_awk_process — Text processing
- cli_sed_transform — Stream editing
- cli_ftp_list/download/upload — FTP operations

Always use the appropriate category tool for the task.
Tools require the underlying binary to be installed on the system.

## WORDLISTS & DICTIONARIES
A comprehensive collection of wordlists (SecLists) is available locally via symlink at:
`/home/mihir/Documents/Agent/MCP/SecLists/` or `./SecLists/`
Use this path when executing tools like Hydra, John, FFuf, or Gobuster. Example paths:
- Passwords: `./SecLists/Passwords/Leaked-Databases/rockyou.txt`
- Web Discovery: `./SecLists/Discovery/Web-Content/raft-large-directories.txt`
""",
)

# ---------------------------------------------------------------------------
# Register all tool modules
# ---------------------------------------------------------------------------

from tools.recon import register_all as register_recon
from tools.webapp import register_all as register_webapp
from tools.auth import register_all as register_auth
from tools.forensics import register_all as register_forensics
from tools.exploitation import register_all as register_exploitation
from tools.cli import register_all as register_cli

register_recon(mcp)
register_webapp(mcp)
register_auth(mcp)
register_forensics(mcp)
register_exploitation(mcp)
register_cli(mcp)


# ---------------------------------------------------------------------------
# Privilege Escalation Resources
# ---------------------------------------------------------------------------
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

@mcp.resource("privesc://linux/linpeas")
def read_linpeas() -> str:
    """Provides the source code for linpeas_small.sh (Linux Privilege Escalation)"""
    return (BASE_DIR / "data" / "privesc" / "linpeas_min.sh").read_text()

@mcp.resource("privesc://windows/winpeas")
def read_winpeas() -> str:
    """Provides the source code for winPEAS.bat (Windows Privilege Escalation)"""
    return (BASE_DIR / "data" / "privesc" / "winpeas_min.bat").read_text()

@mcp.resource("privesc://windows/powerup")
def read_powerup() -> str:
    """Provides the source code for PowerUp.ps1 (PowerShell Privilege Escalation checks)"""
    return (BASE_DIR / "data" / "privesc" / "powerup_min.ps1").read_text(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
