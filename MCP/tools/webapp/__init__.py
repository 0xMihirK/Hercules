# WEB APP TESTING tools


def register_all(mcp):
    """Register all web app testing tools."""
    from .ffuf_tool import register_ffuf_tools
    from .sqlmap_tool import register_sqlmap_tools
    from .dalfox_tool import register_dalfox_tools
    from .arjun_tool import register_arjun_tools
    from .wafw00f_tool import register_wafw00f_tools

    register_ffuf_tools(mcp)
    register_sqlmap_tools(mcp)
    register_dalfox_tools(mcp)
    register_arjun_tools(mcp)
    register_wafw00f_tools(mcp)
