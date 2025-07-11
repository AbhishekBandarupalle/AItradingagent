"""
MCP (Model Context Protocol) module for AI trading agent.

This module contains the MCP server and client components for handling
LLM interactions and trade data management.
"""

from .mcp_client import MCPClient

# Import server conditionally to avoid dependency issues
try:
    from .mcp_server import app as mcp_server_app
    __all__ = ['MCPClient', 'mcp_server_app']
except ImportError:
    __all__ = ['MCPClient'] 