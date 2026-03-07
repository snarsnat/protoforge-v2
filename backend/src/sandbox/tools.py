"""
ProtoForge Sandbox Tools
"""

import json
from typing import Any, Callable
from langchain_core.tools import BaseTool
from pydantic import Field

from src.sandbox.sandbox import get_sandbox_provider


class BashTool(BaseTool):
    """Execute bash commands"""
    
    name: str = "bash"
    description: str = """Execute bash commands in the sandbox. 
Use this to run code, build projects, install dependencies, etc.
Returns (returncode, stdout, stderr)."""
    
    sandbox_provider: Any = Field(default_factory=get_sandbox_provider)
    
    def _run(self, command: str, timeout: int = 60) -> str:
        """Execute command"""
        # Get sandbox from thread context (would be set by middleware)
        sandbox = self.sandbox_provider.get("local")
        if not sandbox:
            return "Error: No sandbox available"
        
        returncode, stdout, stderr = sandbox.execute_command(command, timeout)
        
        result = {
            "returncode": returncode,
            "stdout": stdout,
            "stderr": stderr
        }
        return json.dumps(result)


class ReadFileTool(BaseTool):
    """Read file from sandbox"""
    
    name: str = "read_file"
    description: str = "Read a file from the sandbox workspace"
    
    sandbox_provider: Any = Field(default_factory=get_sandbox_provider)
    
    def _run(self, path: str, lines: int = 0, offset: int = 0) -> str:
        """Read file"""
        sandbox = self.sandbox_provider.get("local")
        if not sandbox:
            return "Error: No sandbox available"
        
        try:
            content = sandbox.read_file(path)
            lines_list = content.split("\n")
            
            if offset > 0:
                lines_list = lines_list[offset:]
            if lines > 0:
                lines_list = lines_list[:lines]
            
            return "\n".join(lines_list)
        except FileNotFoundError:
            return f"Error: File not found: {path}"
        except Exception as e:
            return f"Error: {str(e)}"


class WriteFileTool(BaseTool):
    """Write file to sandbox"""
    
    name: str = "write_file"
    description: str = """Write content to a file in the sandbox workspace.
Creates directories if needed. Use this to create code files, configs, etc."""
    
    sandbox_provider: Any = Field(default_factory=get_sandbox_provider)
    
    def _run(self, path: str, content: str, append: bool = False) -> str:
        """Write file"""
        sandbox = self.sandbox_provider.get("local")
        if not sandbox:
            return "Error: No sandbox available"
        
        try:
            if append:
                try:
                    existing = sandbox.read_file(path)
                    content = existing + "\n" + content
                except FileNotFoundError:
                    pass
            
            sandbox.write_file(path, content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error: {str(e)}"


class ListDirTool(BaseTool):
    """List directory contents"""
    
    name: str = "ls"
    description: str = "List directory contents (like ls)"
    
    sandbox_provider: Any = Field(default_factory=get_sandbox_provider)
    
    def _run(self, path: str = ".") -> str:
        """List directory"""
        sandbox = self.sandbox_provider.get("local")
        if not sandbox:
            return "Error: No sandbox available"
        
        try:
            items = sandbox.list_dir(path)
            if not items:
                return "(empty)"
            
            lines = []
            for item in items:
                prefix = "d" if item["type"] == "dir" else "f"
                size = item.get("size", 0)
                lines.append(f"{prefix} {size:>8} {item['name']}")
            
            return "\n".join(lines)
        except Exception as e:
            return f"Error: {str(e)}"


class StrReplaceTool(BaseTool):
    """Replace string in file"""
    
    name: str = "str_replace"
    description: str = """Replace a string in a file. 
Provide the exact old string to find and the new string to replace it with.
Can replace all occurrences or just the first."""
    
    sandbox_provider: Any = Field(default_factory=get_sandbox_provider)
    
    def _run(
        self, 
        path: str, 
        old: str, 
        new: str, 
        replace_all: bool = False
    ) -> str:
        """Replace string"""
        sandbox = self.sandbox_provider.get("local")
        if not sandbox:
            return "Error: No sandbox available"
        
        try:
            content = sandbox.read_file(path)
            
            if replace_all:
                new_content = content.replace(old, new)
            else:
                new_content = content.replace(old, new, 1)
            
            sandbox.write_file(path, new_content)
            return f"Successfully replaced in {path}"
        except FileNotFoundError:
            return f"Error: File not found: {path}"
        except Exception as e:
            return f"Error: {str(e)}"


def get_sandbox_tools() -> list[BaseTool]:
    """Get all sandbox tools"""
    return [
        BashTool(),
        ReadFileTool(),
        WriteFileTool(),
        ListDirTool(),
        StrReplaceTool(),
    ]
