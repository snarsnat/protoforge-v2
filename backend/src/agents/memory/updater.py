"""
ProtoForge Memory System
"""

import json
import os
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid


@dataclass
class Fact:
    """Memory fact"""
    id: str
    content: str
    category: str  # preference, knowledge, context, behavior, goal
    confidence: float
    created_at: str
    source: str = ""


@dataclass
class MemoryData:
    """Memory data structure"""
    user_context: dict = field(default_factory=dict)
    history: list = field(default_factory=list)
    facts: list = field(default_factory=list)
    last_updated: str = ""


class MemoryStore:
    """Persistent memory storage"""
    
    def __init__(self, storage_path: str = "./data/memory.json"):
        self.storage_path = Path(storage_path)
        self._data: MemoryData = MemoryData()
        self._load()
    
    def _load(self) -> None:
        """Load memory from disk"""
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text())
                self._data = MemoryData(**data)
            except Exception as e:
                print(f"Error loading memory: {e}")
    
    def _save(self) -> None:
        """Save memory to disk"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Atomic write
        temp_path = self.storage_path.with_suffix('.tmp')
        temp_path.write_text(json.dumps(asdict(self._data), indent=2))
        temp_path.replace(self.storage_path)
    
    def get_all(self) -> dict:
        """Get all memory data"""
        return asdict(self._data)
    
    def update_context(self, context: dict) -> None:
        """Update user context"""
        self._data.user_context.update(context)
        self._data.last_updated = datetime.now().isoformat()
        self._save()
    
    def add_fact(self, content: str, category: str, confidence: float, source: str = "") -> None:
        """Add a fact"""
        fact = Fact(
            id=str(uuid.uuid4()),
            content=content,
            category=category,
            confidence=confidence,
            created_at=datetime.now().isoformat(),
            source=source
        )
        
        # Check for duplicates
        existing = [f for f in self._data.facts if f.content == content]
        if existing:
            # Update existing
            existing[0].confidence = max(existing[0].confidence, confidence)
            existing[0].created_at = datetime.now().isoformat()
        else:
            self._data.facts.append(fact)
        
        self._data.last_updated = datetime.now().isoformat()
        self._save()
    
    def get_facts(self, max_facts: int = 15, min_confidence: float = 0.7) -> list[dict]:
        """Get top facts"""
        facts = [
            f for f in self._data.facts 
            if f.confidence >= min_confidence
        ]
        facts.sort(key=lambda x: x.confidence, reverse=True)
        return [asdict(f) for f in facts[:max_facts]]
    
    def clear(self) -> None:
        """Clear all memory"""
        self._data = MemoryData()
        self._save()


class MemorySystem:
    """LLM-powered memory extraction and management"""
    
    def __init__(
        self,
        storage_path: str = "./data/memory.json",
        enabled: bool = True,
        injection_enabled: bool = True,
        max_facts: int = 100,
        fact_confidence_threshold: float = 0.7,
        max_injection_tokens: int = 2000
    ):
        self.store = MemoryStore(storage_path)
        self.enabled = enabled
        self.injection_enabled = injection_enabled
        self.max_facts = max_facts
        self.fact_confidence_threshold = fact_confidence_threshold
        self.max_injection_tokens = max_injection_tokens
    
    def get_injection_prompt(self) -> str:
        """Get memory injection for prompts"""
        if not self.injection_enabled:
            return ""
        
        facts = self.store.get_facts(
            max_facts=15,
            min_confidence=self.fact_confidence_threshold
        )
        
        if not facts:
            return ""
        
        lines = ["\n\n## User Context\n"]
        
        # Add facts
        lines.append("### Known Facts:")
        for fact in facts[:10]:
            lines.append(f"- {fact['content']}")
        
        # Add context
        context = self.store.get_all().get("user_context", {})
        if context:
            lines.append("\n### User Context:")
            for key, value in context.items():
                lines.append(f"- {key}: {value}")
        
        return "\n".join(lines)
    
    async def process_conversation(self, messages: list[dict]) -> None:
        """Process conversation and extract memories"""
        if not self.enabled:
            return
        
        # This would use an LLM to extract facts from conversation
        # For now, just a placeholder
        pass
    
    def get_status(self) -> dict:
        """Get memory status"""
        data = self.store.get_all()
        return {
            "enabled": self.enabled,
            "injection_enabled": self.injection_enabled,
            "fact_count": len(data.get("facts", [])),
            "last_updated": data.get("last_updated", "")
        }


# Global memory system
_memory_system: Optional[MemorySystem] = None


def get_memory_system() -> Optional[MemorySystem]:
    """Get global memory system"""
    return _memory_system


def init_memory_system(**config) -> MemorySystem:
    """Initialize memory system"""
    global _memory_system
    _memory_system = MemorySystem(**config)
    return _memory_system
