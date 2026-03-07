"""
ProtoForge Model Factory
Creates LLM instances from configuration
"""

import os
from typing import Optional, Any, TYPE_CHECKING

# Lazy imports to avoid slow module loading
if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

from src.config import get_config


class ModelFactory:
    """Factory for creating language models"""
    
    _instances: dict = {}
    
    @classmethod
    def create_chat_model(
        cls,
        name: str,
        thinking_enabled: bool = False,
        **kwargs
    ) -> "BaseChatModel":
        """Create a chat model instance"""
        
        # Check cache
        cache_key = f"{name}:{thinking_enabled}"
        if cache_key in cls._instances:
            return cls._instances[cache_key]
        
        # Get model config
        config = get_config()
        model_config = None
        for m in config.models:
            if m.name == name:
                model_config = m
                break
        
        if not model_config:
            raise ValueError(f"Model '{name}' not found in config")
        
        # Resolve API key
        api_key = model_config.api_key
        if api_key.startswith("$"):
            api_key = os.getenv(api_key[1:], "")
        
        # Create model based on 'use' path
        model = cls._create_from_path(
            path=model_config.use,
            model=model_config.model,
            api_key=api_key,
            thinking_enabled=thinking_enabled,
            supports_vision=model_config.supports_vision,
            max_tokens=model_config.max_tokens,
            temperature=model_config.temperature,
            **kwargs
        )
        
        cls._instances[cache_key] = model
        return model
    
    @classmethod
    def _create_from_path(
        cls,
        path: str,
        **kwargs
    ) -> "BaseChatModel":
        """Create model from class path"""
        
        # Parse path (e.g., "langchain_openai:ChatOpenAI")
        if ":" in path:
            module_path, class_name = path.rsplit(":", 1)
        else:
            module_path = "langchain_openai"
            class_name = path
        
        # Import and create
        try:
            from importlib import import_module
            module = import_module(module_path)
            cls_instance = getattr(module, class_name)
            
            # Filter kwargs for this class
            allowed_kwargs = {
                "model", "api_key", "max_tokens", "temperature",
                "model_name", "google_api_key", "anthropic_api_key"
            }
            filtered_kwargs = {
                k: v for k, v in kwargs.items()
                if k in allowed_kwargs
            }
            
            return cls_instance(**filtered_kwargs)
            
        except ImportError as e:
            raise ImportError(
                f"Cannot import '{module_path}'. "
                f"Install required package: uv add {module_path}"
            ) from e
    
    @classmethod
    def list_models(cls) -> list[dict[str, Any]]:
        """List available models"""
        config = get_config()
        return [
            {
                "name": m.name,
                "display_name": m.display_name,
                "supports_thinking": m.supports_thinking,
                "supports_vision": m.supports_vision,
            }
            for m in config.models
        ]
    
    @classmethod
    def get_default_model(cls) -> "BaseChatModel":
        """Get default model"""
        config = get_config()
        if not config.models:
            raise ValueError("No models configured")
        return cls.create_chat_model(config.models[0].name)
    
    @classmethod
    def clear_cache(cls):
        """Clear model cache"""
        cls._instances.clear()
