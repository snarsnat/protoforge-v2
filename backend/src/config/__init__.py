"""
ProtoForge Configuration System
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Model configuration"""
    name: str
    display_name: str
    use: str
    model: str
    api_key: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7
    supports_thinking: bool = False
    supports_vision: bool = False


class ToolConfig(BaseModel):
    """Tool configuration"""
    use: str
    group: str = "builtin"


class ToolGroupConfig(BaseModel):
    """Tool group configuration"""
    name: str
    description: str = ""


class SandboxConfig(BaseModel):
    """Sandbox configuration"""
    use: str = "src.community.local_sandbox:LocalSandboxProvider"


class SkillsConfig(BaseModel):
    """Skills configuration"""
    path: str = "./skills"
    container_path: str = "/mnt/skills"


class TitleConfig(BaseModel):
    """Title generation config"""
    enabled: bool = True
    max_words: int = 10
    max_chars: int = 80


class SubagentsConfig(BaseModel):
    """Subagents configuration"""
    enabled: bool = True


class MemoryConfig(BaseModel):
    """Memory configuration"""
    enabled: bool = True
    injection_enabled: bool = True
    storage_path: str = "./data/memory.json"
    debounce_seconds: int = 30
    max_facts: int = 100
    fact_confidence_threshold: float = 0.7
    max_injection_tokens: int = 2000
    model_name: Optional[str] = None


class SummarizationConfig(BaseModel):
    """Summarization configuration"""
    enabled: bool = False
    trigger: str = "tokens"
    threshold: int = 100000
    keep_policy: str = "recent"
    keep_count: int = 10


class Config(BaseModel):
    """Main configuration"""
    models: List[ModelConfig] = Field(default_factory=list)
    tools: List[ToolConfig] = Field(default_factory=list)
    tool_groups: List[ToolGroupConfig] = Field(default_factory=list)
    sandbox: SandboxConfig = Field(default_factory=SandboxConfig)
    skills: SkillsConfig = Field(default_factory=SkillsConfig)
    title: TitleConfig = Field(default_factory=TitleConfig)
    subagents: SubagentsConfig = Field(default_factory=SubagentsConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    summarization: SummarizationConfig = Field(default_factory=SummarizationConfig)


class ConfigManager:
    """Configuration manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config()
        self._config: Optional[Config] = None
    
    def _find_config(self) -> str:
        """Find config file"""
        # Check env var
        if path := os.getenv("PROTOFORGE_CONFIG_PATH"):
            return path
        
        # Check current directory
        for name in ["config.yaml", "../config.yaml"]:
            path = Path(name)
            if path.exists():
                return str(path.absolute())
        
        return "config.yaml"
    
    def load(self) -> Config:
        """Load configuration"""
        if self._config:
            return self._config
        
        config_data = {}
        
        if Path(self.config_path).exists():
            with open(self.config_path) as f:
                config_data = yaml.safe_load(f) or {}
        
        # Resolve environment variables
        config_data = self._resolve_env_vars(config_data)
        
        self._config = Config(**config_data)
        return self._config
    
    def _resolve_env_vars(self, data: Any) -> Any:
        """Recursively resolve $VAR environment variables"""
        if isinstance(data, dict):
            return {k: self._resolve_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._resolve_env_vars(item) for item in data]
        elif isinstance(data, str) and data.startswith("$"):
            env_var = data[1:]
            return os.getenv(env_var, data)
        return data
    
    @property
    def config(self) -> Config:
        """Get config (lazy load)"""
        if not self._config:
            self._config = self.load()
        return self._config


# Global config instance
_config_manager = ConfigManager()


def get_config() -> Config:
    """Get global config"""
    return _config_manager.config


def reload_config():
    """Reload configuration"""
    global _config_manager
    _config_manager = ConfigManager()
    return _config_manager.load()
