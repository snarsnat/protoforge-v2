<img src="https://raw.githubusercontent.com/snarsnat/protoforge-v2/main/assets/logo.svg" alt="ProtoForge" width="200"/>

# ProtoForge ⚡

**AI-Powered Prototyping Engine**

Build real software, hardware, and hybrid prototypes with AI.

[![X](https://img.shields.io/badge/Follow-@happinezreal-000000?style=flat&logo=x)](https://x.com/happinezreal)

## What is ProtoForge?

ProtoForge is an AI-powered builder that generates real prototypes:

- **Software** → Web apps, APIs, scripts with actual code
- **Hardware** → Circuit diagrams (Mermaid.js), 3D models, BOMs
- **Hybrid** → Combined hardware + software systems
- **Research** → Deep research and analysis
- **Reports** → Documentation and reports
- **Diagrams** → Mermaid diagrams and flowcharts
- **3D Models** → Three.js prototypes

Just describe what you want, select a skill or mode, and ProtoForge generates the files.

## Quick Start

### 1. Clone the Repo

```bash
git clone https://github.com/snarsnat/protoforge-v2.git
cd protoforge-v2
```

### 2. Install Dependencies

```bash
cd backend
pip install -r ../requirements.txt
```

### 3. Run the Server

```bash
PYTHONPATH=. python3 -m src.gateway.app
```

### 4. Open in Browser

```
http://localhost:8001
```

### 5. Configure API Key

1. Enter your API key in the sidebar (Provider: OpenAI recommended)
2. Click "Connect"
3. Start building!

## Getting an API Key

| Provider | Link | Notes |
|----------|------|-------|
| OpenAI | [platform.openapi.com](https://platform.openai.com) | Recommended - most reliable |
| Anthropic | [console.anthropic.com](https://console.anthropic.com) | Great for Claude models |
| DeepSeek | [platform.deepseek.com](https://platform.deepseek.com) | May have rate limits |

## New UI Features

The redesigned UI includes:

- **Sidebar** - Logo, New Project button, navigation
- **Skills Grid** - Quick access to Research, Reports, Diagrams, 3D, Code, Web
- **Project List** - Switch between projects with status indicators
- **Chat Panel** - AI conversation with code blocks
- **Preview Panel** - Preview/Code/Files tabs
- **Device Toggles** - Mobile, Tablet, Desktop preview modes
- **Resize Handle** - Drag to adjust chat/preview split
- **Share/Export/Download** - Project actions in header

## Project Structure

```
protoforge/
├── backend/
│   ├── src/
│   │   ├── gateway/         # FastAPI web server
│   │   │   ├── app.py       # Main application
│   │   │   ├── generator.py # AI code generation
│   │   │   └── templates/   # HTML templates
│   │   ├── agents/          # AI agents
│   │   ├── skills/          # Skill definitions
│   │   ├── sandbox/         # Sandboxed execution
│   │   └── tools/           # Built-in tools
│   └── requirements.txt
├── frontend/                # Next.js frontend (optional)
├── skills/                 # Public skills
├── assets/                 # Logo and static assets
└── config.example.yaml      # Config template
```

## Tech Stack

- **Backend**: Python, FastAPI, LangChain, LangGraph
- **Frontend**: Vanilla JS (no frameworks)
- **Design**: Anti-trope - dark theme, sharp edges, monospace fonts, red accent (#e63946)

## Configuration

### Environment Variables

Create a `.env` file:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...
```

### Config File

Copy `config.example.yaml` to `config.yaml` and customize:

```yaml
models:
  default: gpt-4o
  providers:
    openai: gpt-4o
    anthropic: claude-sonnet-4-20250514
    deepseek: deepseek-chat
```

## Author

Built by [@happinezreal](https://x.com/happinezreal)

---

*Built for makers, by makers* ⚡
