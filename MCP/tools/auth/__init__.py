# AUTH & PASSWORD tools


def register_all(mcp):
    """Register all auth & password tools."""
    from .hydra_tool import register_hydra_tools
    from .john_tool import register_john_tools

    register_hydra_tools(mcp)
    register_john_tools(mcp)
