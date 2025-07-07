"""
Browser skills module for WebSurfer-β v2.0

This module provides asynchronous browser automation capabilities
using the Browser MCP (Model Context Protocol) server.
"""

from .mcp_server_manager import MCPServerManager
from .mcp_client import MCPClient
from .actions import Browser

__all__ = ['MCPServerManager', 'MCPClient', 'Browser'] 