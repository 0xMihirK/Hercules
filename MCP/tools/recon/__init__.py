# RECON & SCANNING tools


def register_all(mcp):
    """Register all recon & scanning tools."""
    from .nmap_tool import register_nmap_tools
    from .gobuster_tool import register_gobuster_tools
    from .nuclei_tool import register_nuclei_tools

    register_nmap_tools(mcp)
    register_gobuster_tools(mcp)
    register_nuclei_tools(mcp)
