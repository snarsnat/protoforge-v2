---
name: code-generation
description: Generate software code for web apps, APIs, and scripts
allowed-tools: bash, write_file, read_file
---

# Code Generation Skill

This skill generates software code based on user requirements.

## Usage

When the user asks for:
- Web applications
- APIs
- Scripts
- Full-stack applications

Analyze the requirements and generate appropriate code files.

## Web App Template

For web apps, generate:
- `index.html` - Main HTML file
- `style.css` - Styles (follow anti-trope design)
- `app.js` - JavaScript logic

## API Template

For APIs, generate:
- `server.py` - Flask/FastAPI server
- `requirements.txt` - Dependencies
- `config.json` - Configuration

## Design Guidelines

Follow anti-trope principles:
- No purple gradients
- No rounded corners
- Use monospace fonts for code
- Sharp, industrial aesthetic

## Output Files

Save to:
- `/mnt/user-data/workspace/` - Code files
- Present files when complete using `present_files`
