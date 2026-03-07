"""
ProtoForge Sandbox System
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from pathlib import Path
import shutil
import uuid


class Sandbox(ABC):
    """Abstract sandbox interface"""
    
    @abstractmethod
    def execute_command(
        self, 
        command: str, 
        timeout: int = 60
    ) -> tuple[int, str, str]:
        """Execute a command, return (returncode, stdout, stderr)"""
        pass
    
    @abstractmethod
    def read_file(self, path: str) -> str:
        """Read a file"""
        pass
    
    @abstractmethod
    def write_file(self, path: str, content: str) -> None:
        """Write a file"""
        pass
    
    @abstractmethod
    def list_dir(self, path: str = ".") -> list[dict[str, Any]]:
        """List directory contents"""
        pass
    
    @abstractmethod
    def delete_file(self, path: str) -> None:
        """Delete a file"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up sandbox resources"""
        pass


class LocalSandbox(Sandbox):
    """Local filesystem sandbox"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self._sandbox_id = "local"
    
    @property
    def sandbox_id(self) -> str:
        return self._sandbox_id
    
    def execute_command(
        self, 
        command: str, 
        timeout: int = 60
    ) -> tuple[int, str, str]:
        """Execute command locally"""
        import subprocess
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.workspace_dir),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 124, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def read_file(self, path: str) -> str:
        """Read file"""
        full_path = self.workspace_dir / path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return full_path.read_text()
    
    def write_file(self, path: str, content: str) -> None:
        """Write file"""
        full_path = self.workspace_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
    
    def list_dir(self, path: str = ".") -> list[dict[str, Any]]:
        """List directory"""
        full_path = self.workspace_dir / path
        if not full_path.exists():
            return []
        
        items = []
        for item in full_path.iterdir():
            items.append({
                "name": item.name,
                "type": "dir" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else 0
            })
        return items
    
    def delete_file(self, path: str) -> None:
        """Delete file"""
        full_path = self.workspace_dir / path
        if full_path.exists():
            if full_path.is_file():
                full_path.unlink()
            elif full_path.is_dir():
                shutil.rmtree(full_path)
    
    def cleanup(self) -> None:
        """Clean up workspace"""
        if self.workspace_dir.exists():
            shutil.rmtree(self.workspace_dir)


class SandboxProvider:
    """Sandbox provider with lifecycle management"""
    
    def __init__(self):
        self._sandboxes: dict[str, Sandbox] = {}
    
    def acquire(self, thread_id: str, workspace_base: str = "./data/threads") -> Sandbox:
        """Acquire a sandbox for a thread"""
        if thread_id in self._sandboxes:
            return self._sandboxes[thread_id]
        
        workspace_dir = Path(workspace_base) / thread_id / "workspace"
        sandbox = LocalSandbox(str(workspace_dir))
        self._sandboxes[thread_id] = sandbox
        return sandbox
    
    def get(self, thread_id: str) -> Optional[Sandbox]:
        """Get existing sandbox"""
        return self._sandboxes.get(thread_id)
    
    def release(self, thread_id: str) -> None:
        """Release a sandbox"""
        if thread_id in self._sandboxes:
            self._sandboxes[thread_id].cleanup()
            del self._sandboxes[thread_id]
    
    def release_all(self) -> None:
        """Release all sandboxes"""
        for sandbox in self._sandboxes.values():
            sandbox.cleanup()
        self._sandboxes.clear()


# Global provider
_sandbox_provider = SandboxProvider()


def get_sandbox_provider() -> SandboxProvider:
    """Get global sandbox provider"""
    return _sandbox_provider
