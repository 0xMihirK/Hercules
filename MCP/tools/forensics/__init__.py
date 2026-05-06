# CTF & FORENSICS tools


def register_all(mcp):
    """Register all forensics & CTF tools."""
    from .volatility_tool import register_volatility_tools
    from .exiftool_tool import register_exiftool_tools
    from .steghide_tool import register_steghide_tools
    from .foremost_tool import register_foremost_tools

    register_volatility_tools(mcp)
    register_exiftool_tools(mcp)
    register_steghide_tools(mcp)
    register_foremost_tools(mcp)
