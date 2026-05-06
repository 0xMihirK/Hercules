# BASIC CLI tools


def register_all(mcp):
    """Register all basic CLI tools."""
    from .curl_tool import register_curl_tools
    from .netcat_tool import register_netcat_tools
    from .dig_tool import register_dig_tools
    from .whois_tool import register_whois_tools
    from .traceroute_tool import register_traceroute_tools
    from .ssh_tool import register_ssh_tools
    from .openssl_tool import register_openssl_tools
    from .strings_tool import register_strings_tools
    from .xxd_tool import register_xxd_tools
    from .grep_awk_sed_tool import register_grep_awk_sed_tools
    from .ftp_tool import register_ftp_tools

    register_curl_tools(mcp)
    register_netcat_tools(mcp)
    register_dig_tools(mcp)
    register_whois_tools(mcp)
    register_traceroute_tools(mcp)
    register_ssh_tools(mcp)
    register_openssl_tools(mcp)
    register_strings_tools(mcp)
    register_xxd_tools(mcp)
    register_grep_awk_sed_tools(mcp)
    register_ftp_tools(mcp)
