"""
Test skills system
"""

import pytest
import tempfile
from pathlib import Path

from src.skills import Skill, SkillsLoader


def test_skill_creation():
    """Test skill creation"""
    skill = Skill(
        name="test-skill",
        description="Test skill description",
        path="/path/to/skill"
    )
    
    assert skill.name == "test-skill"
    assert skill.enabled == True


def test_skills_loader():
    """Test skills loader"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test skills directory
        skills_dir = Path(tmpdir) / "skills"
        skills_dir.mkdir()
        
        # Create a skill
        skill_dir = skills_dir / "public" / "test-skill"
        skill_dir.mkdir(parents=True)
        
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: test-skill
description: A test skill
allowed-tools: bash, read_file
---

# Test Skill

This is a test skill.
""")
        
        # Load skills
        loader = SkillsLoader(str(skills_dir))
        skills = loader.load_skills()
        
        assert "test-skill" in skills
        assert skills["test-skill"].description == "A test skill"


def test_skill_enable_disable():
    """Test skill enable/disable"""
    skill = Skill(
        name="test",
        description="Test",
        path="/test",
        enabled=True
    )
    
    skill.disable()
    assert skill.enabled == False
    
    skill.enable()
    assert skill.enabled == True


if __name__ == "__main__":
    pytest.main([__file__])
