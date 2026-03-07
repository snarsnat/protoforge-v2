# ProtoForge ⚡

**AI-Powered Prototyping Super Agent Harness**

ProtoForge is an open-source SuperAgent harness that researches, designs, and creates prototypes. With the help of sandboxes, memories, tools, skills and subagents, it handles different levels of tasks that could take minutes to hours.

## Features

- **🦌 Agentic AI**: LangGraph-powered AI that thinks, plans, and executes
- **📦 Sandbox Execution**: Isolated containerized code generation
- **🔧 Skills System**: Extensible skill framework for specialized tasks
- **🧠 Long-Term Memory**: Remembers your preferences and context
- **⚡ Subagents**: Spawn parallel agents for complex multi-step tasks
- **🔌 MCP Support**: Model Context Protocol integration
- **🎨 Diagrams**: Mermaid.js circuit and component diagrams
- **🎲 3D Models**: Auto-generated 3D prototypes
- **🔐 Your API Key**: Use your own keys - your data, your controls

## Quick Start

### Docker (Recommended)

```bash
# Clone and setup
git clone https://github.com/snarsnat/protoforge.git
cd protoforge

# Generate config
make config

# Edit config.yaml with your API keys
nano config.yaml

# Start services
make docker-init
make docker-start
```

Access at http://localhost:8001

### Local Development

```bash
# Install dependencies
make install

# Run all services
make dev
```

## Configuration

Edit `config.yaml`:

```yaml
models:
  - name: gpt-4o
    display_name: GPT-4o
    use: langchain_openai:ChatOpenAI
    model: gpt-4o
    api_key: $OPENAI_API_KEY
    supports_thinking: false
    supports_vision: true
```

Set API keys in `.env`:

```bash
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
DEEPSEEK_API_KEY=your-key-here
```

## Architecture

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

## Skills

Skills define what ProtoForge can do:

```markdown
# skills/public/research/SKILL.md
name: research
description: Research any topic deeply
...
```

Built-in skills:
- **Research**: Deep research on any topic
- **Report Generation**: Create comprehensive reports
- **Diagram Generation**: Generate circuit/component diagrams
- **3D Modeling**: Create 3D prototype specifications
- **Code Generation**: Generate software code
- **Web Pages**: Create web applications

## Development

```bash
# Check prerequisites
make check

# Install all dependencies
make install

# Run development
make dev

# Run tests
make test

# Lint code
make lint
```

## License

MIT License - See LICENSE file

## Acknowledgments

ProtoForge is built upon the incredible work of:
- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [DeerFlow](https://github.com/bytedance/deer-flow) - Inspiration

---

*Built for makers, by makers* ⚡
