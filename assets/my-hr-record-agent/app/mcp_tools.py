"""MCP tool loader — owned indirection layer over mcp_providers.agw.

Import get_mcp_tools from here in application code. Tests patch this module
to inject mock tools without modifying production code.
"""

from mcp_providers.agw import get_mcp_tools

__all__ = ["get_mcp_tools"]
