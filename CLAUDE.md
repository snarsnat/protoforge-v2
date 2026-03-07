# CLAUDE.md - ProtoForge

This file provides guidance for AI coding assistants working on ProtoForge.

## Project Overview

ProtoForge is an open-source Super Agent harness that researches, designs, and creates prototypes. Built on LangGraph and LangChain.

## Architecture

- **Backend**: Python with LangGraph/LangChain
- **Frontend**: Next.js with React
- **Gateway**: FastAPI REST API
- **Sandbox**: Local/Docker execution

## Key Directories

```
protoforge/
├── backend/src/
│   ├── agents/         # Agent system & lead agent
│   ├── gateway/        # FastAPI REST API
│   ├── sandbox/       # Execution environment
│   ├── subagents/     # Parallel task execution
│   ├── tools/         # Tool definitions
│   ├── skills/        # Skill loader
│   ├── memory/        # Persistent memory
│   ├── mcp/           # MCP integration
│   ├── models/        # LLM factory
│   ├── config/        # Configuration
│   └── community/     # Web tools
├── frontend/          # Next.js app
├── skills/           # Agent skills
└── docs/             # Documentation
```

## Commands

```bash
# Install
make install

# Development
make dev

# Docker
make docker-start

# Tests
make test
```

## Configuration

Edit `config.yaml` to configure models, tools, and settings.

## Important Notes

- Uses LangGraph for agent orchestration
- Skills are loaded from `skills/{public,custom}/`
- Memory persists to JSON file
- Subagents run in parallel with timeout
