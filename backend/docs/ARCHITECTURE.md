# Architecture

## Overview

ProtoForge is built as a modular Super Agent harness with the following components:

```
┌─────────────────────────────────────────────────────────┐
│                   Nginx (Port 2026)                      │
│              Unified reverse proxy                       │
└───────────┬─────────────────────┬───────────────────────┘
            │                     │
  /api/langgraph/*               /api/* (other)
            │                     │
            ▼                     ▼
┌───────────────────────┐  ┌────────────────────────────┐
│   LangGraph Server    │  │     Gateway API (8001)     │
│      (Port 2024)      │  │      FastAPI REST          │
│                       │  │                             │
│ ┌──────────────────┐ │  │ Models, MCP, Skills,       │
│ │    Lead Agent    │ │  │ Memory, Uploads,           │
│ │ ┌──────────────┐  │ │  │ Artifacts                  │
│ │ │ Middleware   │  │  │ └────────────────────────────┘
│ │ │    Chain     │  │  │
│ │ └──────────────┘  │  │
│ │ ┌──────────────┐  │  │
│ │ │    Tools     │  │  │
│ │ └──────────────┘  │  │
│ │ ┌──────────────┐  │  │
│ │ │  Subagents   │  │  │
│ │ └──────────────┘  │  │
│ └────────────────────┘  │
└─────────────────────────┘
```

## Components

### Agent System

- **Lead Agent**: Main LangGraph agent with middleware chain
- **Middleware**: ThreadData, Uploads, Sandbox, Summarization, TodoList, Title, Memory, ViewImage, Clarification
- **Thread State**: Per-thread isolated state

### Sandbox

- **Local Sandbox**: Filesystem-based execution
- **Docker Sandbox**: Containerized execution
- **Tools**: bash, read_file, write_file, ls, str_replace

### Skills

Skills are loaded from `./skills/{public,custom}/`:

- **research**: Deep research
- **report-generation**: Report creation
- **diagram-generation**: Mermaid diagrams
- **code-generation**: Code creation
- **3d-modeling**: 3D models
- **web-page**: Web applications

### Memory

Persistent memory with:
- Fact extraction
- Context tracking
- User preferences
- Injection into prompts

### Subagents

Parallel task execution:
- general-purpose: Full tool access
- bash: Command specialist
- diagram: Diagram generation
- 3d-model: 3D modeling

### MCP

Model Context Protocol support:
- stdio servers
- SSE servers
- HTTP servers
- OAuth authentication
