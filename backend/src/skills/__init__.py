"""
ProtoForge Skills System
"""

import os
import json
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class Skill:
    """Skill definition"""
    name: str
    description: str
    path: str
    enabled: bool = True
    license: Optional[str] = None
    allowed_tools: list[str] = None
    
    def __post_init__(self):
        if self.allowed_tools is None:
            self.allowed_tools = []


class SkillsLoader:
    """Load and manage skills"""
    
    def __init__(self, skills_path: str = "./skills"):
        self.skills_path = Path(skills_path)
        self._skills: dict[str, Skill] = {}
        self._extensions_config: dict[str, Any] = {}
    
    def load_skills(self, extensions_config: Optional[dict] = None) -> dict[str, Skill]:
        """Load all skills from skills directory"""
        self._skills = {}
        self._extensions_config = extensions_config or {}
        
        # Scan public skills
        public_skills = self.skills_path / "public"
        if public_skills.exists():
            self._scan_skill_dir(public_skills, "public")
        
        # Scan custom skills
        custom_skills = self.skills_path / "custom"
        if custom_skills.exists():
            self._scan_skill_dir(custom_skills, "custom")
        
        # Apply enabled state from extensions config
        self._apply_enabled_state()
        
        return self._skills
    
    def _scan_skill_dir(self, base_path: Path, category: str) -> None:
        """Scan directory for skills"""
        if not base_path.exists():
            return
        
        for skill_dir in base_path.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue
            
            skill = self._parse_skill_file(skill_file, category)
            if skill:
                self._skills[skill.name] = skill
    
    def _parse_skill_file(self, path: Path, category: str) -> Optional[Skill]:
        """Parse SKILL.md file"""
        try:
            content = path.read_text()
            
            # Parse YAML frontmatter
            name = path.parent.name
            description = ""
            license_str = None
            allowed_tools = []
            
            # Simple frontmatter parsing
            if content.startswith("---"):
                end = content.find("---", 3)
                if end > 0:
                    frontmatter = content[3:end]
                    for line in frontmatter.split("\n"):
                        if ":" in line:
                            key, value = line.split(":", 1)
                            value = value.strip().strip('"').strip("'")
                            if key == "description":
                                description = value
                            elif key == "license":
                                license_str = value
                            elif key == "allowed-tools":
                                allowed_tools = [t.strip() for t in value.split(",")]
            
            return Skill(
                name=name,
                description=description or f"Skill: {name}",
                path=str(path.parent),
                allowed_tools=allowed_tools
            )
        except Exception as e:
            print(f"Error parsing skill {path}: {e}")
            return None
    
    def _apply_enabled_state(self) -> None:
        """Apply enabled state from extensions config"""
        skills_config = self._extensions_config.get("skills", {})
        for name, skill in self._skills.items():
            if name in skills_config:
                skill.enabled = skills_config[name].get("enabled", True)
    
    def get_enabled_skills(self) -> list[Skill]:
        """Get list of enabled skills"""
        return [s for s in self._skills.values() if s.enabled]
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get skill by name"""
        return self._skills.get(name)
    
    def enable_skill(self, name: str) -> None:
        """Enable a skill"""
        if name in self._skills:
            self._skills[name].enabled = True
    
    def disable_skill(self, name: str) -> None:
        """Disable a skill"""
        if name in self._skills:
            self._skills[name].enabled = False
    
    def get_skill_prompt_injection(self) -> str:
        """Generate prompt injection for enabled skills"""
        skills = self.get_enabled_skills()
        if not skills:
            return ""
        
        lines = ["\n\n## Available Skills\n"]
        for skill in skills:
            lines.append(f"### {skill.name}")
            lines.append(f"{skill.description}\n")
            if skill.allowed_tools:
                lines.append(f"Allowed tools: {', '.join(skill.allowed_tools)}\n")
        
        return "\n".join(lines)


# Global skills loader
_skills_loader: Optional[SkillsLoader] = None


def get_skills_loader(skills_path: str = "./skills") -> SkillsLoader:
    """Get global skills loader"""
    global _skills_loader
    if not _skills_loader:
        _skills_loader = SkillsLoader(skills_path)
    return _skills_loader
