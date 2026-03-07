"""
ProtoForge MCP Integration
"""

import json
from typing import Any, Optional
from pathlib import Path


class MCPServer:
    """MCP server configuration"""
    
    def __init__(
        self,
        name: str,
        enabled: bool = True,
        server_type: str = "stdio",  # stdio, sse, http
        command: Optional[str] = None,
        args: Optional[list] = None,
        env: Optional[dict] = None,
        url: Optional[str] = None,
        headers: Optional[dict] = None,
        oauth: Optional[dict] = None,
        description: str = ""
    ):
        self.name = name
        self.enabled = enabled
        self.server_type = server_type
        self.command = command
        self.args = args or []
        self.env = env or {}
        self.url = url
        self.headers = headers or {}
        self.oauth = oauth
        self.description = description


class MCPManager:
    """Manage MCP servers"""
    
    def __init__(self):
        self._servers: dict[str, MCPServer] = {}
        self._tools: dict[str, list] = {}  # server_name -> tools
    
    def load_config(self, config: dict) -> None:
        """Load MCP configuration"""
        self._servers = {}
        
        for name, server_config in config.get("mcpServers", {}).items():
            server = MCPServer(
                name=name,
                enabled=server_config.get("enabled", True),
                server_type=server_config.get("type", "stdio"),
                command=server_config.get("command"),
                args=server_config.get("args", []),
                env=server_config.get("env", {}),
                url=server_config.get("url"),
                headers=server_config.get("headers", {}),
                oauth=server_config.get("oauth"),
                description=server_config.get("description", "")
            )
            self._servers[name] = server
    
    def get_enabled_servers(self) -> list[MCPServer]:
        """Get enabled servers"""
        return [s for s in self._servers.values() if s.enabled]
    
    def get_server(self, name: str) -> Optional[MCPServer]:
        """Get server by name"""
        return self._servers.get(name)
    
    def enable_server(self, name: str) -> None:
        """Enable server"""
        if name in self._servers:
            self._servers[name].enabled = True
    
    def disable_server(self, name: str) -> None:
        """Disable server"""
        if name in self._servers:
            self._servers[name].enabled = False
    
    def get_tools(self, server_name: str) -> list:
        """Get tools from server (lazy loaded)"""
        if server_name not in self._tools:
            # Would load tools from MCP server
            self._tools[server_name] = []
        return self._tools[server_name]
    
    def get_all_tools(self) -> list:
        """Get all MCP tools"""
        tools = []
        for server in self.get_enabled_servers():
            tools.extend(self.get_tools(server.name))
        return tools
    
    def get_config_dict(self) -> dict:
        """Get configuration as dict"""
        return {
            "mcpServers": {
                name: {
                    "enabled": server.enabled,
                    "type": server.server_type,
                    "command": server.command,
                    "args": server.args,
                    "env": server.env,
                    "url": server.url,
                    "headers": server.headers,
                    "oauth": server.oauth,
                    "description": server.description
                }
                for name, server in self._servers.items()
            }
        }


# Global MCP manager
_mcp_manager: Optional[MCPManager] = None


def get_mcp_manager() -> MCPManager:
    """Get global MCP manager"""
    global _mcp_manager
    if not _mcp_manager:
        _mcp_manager = MCPManager()
    return _mcp_manager
