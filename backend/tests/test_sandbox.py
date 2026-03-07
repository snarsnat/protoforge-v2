"""
Test sandbox system
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.sandbox.sandbox import LocalSandbox, SandboxProvider


def test_local_sandbox():
    """Test local sandbox"""
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = LocalSandbox(tmpdir)
        
        # Write file
        sandbox.write_file("test.txt", "Hello World")
        
        # Read file
        content = sandbox.read_file("test.txt")
        assert content == "Hello World"
        
        # List dir
        items = sandbox.list_dir(".")
        assert len(items) > 0
        
        # Cleanup
        sandbox.cleanup()


def test_sandbox_provider():
    """Test sandbox provider"""
    provider = SandboxProvider()
    
    # Acquire sandbox
    sandbox = provider.acquire("test-thread")
    assert sandbox is not None
    assert sandbox.sandbox_id == "local"
    
    # Get existing
    sandbox2 = provider.get("test-thread")
    assert sandbox2 is not None
    
    # Release
    provider.release("test-thread")


def test_sandbox_execute():
    """Test sandbox command execution"""
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = LocalSandbox(tmpdir)
        
        # Execute command
        returncode, stdout, stderr = sandbox.execute_command("echo 'test'")
        
        assert returncode == 0
        assert "test" in stdout
        
        sandbox.cleanup()


if __name__ == "__main__":
    pytest.main([__file__])
