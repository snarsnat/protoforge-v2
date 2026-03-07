"""
ProtoForge Tests
"""

import pytest
from src.config import Config, ModelConfig, SandboxConfig


def test_config_loading():
    """Test configuration loading"""
    config = Config()
    assert config is not None


def test_model_config():
    """Test model configuration"""
    model = ModelConfig(
        name="test",
        display_name="Test Model",
        use="langchain_openai:ChatOpenAI",
        model="gpt-4",
        api_key="$TEST_KEY"
    )
    assert model.name == "test"
    assert model.supports_thinking == False


def test_sandbox_config():
    """Test sandbox configuration"""
    sandbox = SandboxConfig()
    assert sandbox.use is not None


def test_tools_config():
    """Test tools configuration"""
    from src.config import ToolConfig, ToolGroupConfig
    
    tool = ToolConfig(use="test", group="test")
    assert tool.use == "test"
    
    group = ToolGroupConfig(name="test", description="Test group")
    assert group.name == "test"


if __name__ == "__main__":
    pytest.main([__file__])
