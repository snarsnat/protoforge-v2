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

Many providers offer **free tier** API keys that work with ProtoForge:

| Provider | Free Tier | Link | Notes |
|----------|-----------|------|-------|
| **OpenAI** | $5 credit | [platform.openai.com](https://platform.openai.com) | Recommended - most reliable |
| **Anthropic** | $5 credit | [console.anthropic.com](https://console.anthropic.com) | Great for Claude models |
| **DeepSeek** | Yes | [platform.deepseek.com](https://platform.deepseek.com) | Generous free tier |
| **MiniMax** | Yes | [platform.minimax.io](https://platform.minimax.io) | Great for coding |
| **Kimi (Moonshot)** | Yes | [platform.moonshot.ai](https://platform.moonshot.ai) | Strong reasoning |
| **Zhipu (GLM)** | Yes | [open.bigmodel.cn](https://open.bigmodel.cn) | Chinese models |
| **Qwen** | Yes | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com) | Alibaba's models |
| **SiliconFlow** | Yes | [siliconflow.cn](https://siliconflow.cn) | Many free models |
| **Together AI** | Yes | [together.ai](https://together.ai) | Llama, Qwen free |
| **Groq** | Yes | [groq.com](https://groq.com) | Ultra-fast inference |
| **Volcano Engine** | Yes | [console.volcengine.com](https://console.volcengine.com) | BytePlus/Doubao |

### How Free Tier API Keys Work

Free tier API keys work just like paid keys — they're authenticated the same way. The difference is:

1. **Rate limits** - Free keys have stricter limits (fewer requests/minute)
2. **Usage caps** - Free keys stop working after a certain amount of usage
3. **Model restrictions** - Some free tiers only work with specific models

ProtoForge passes your API key directly to the AI provider's API. We never store or proxy your key — all requests go directly from your browser to the provider.

## Credit System

ProtoForge uses a **pay-per-prompt** credit system:

- **First prompt is FREE** - No credits required to start
- **Software prompts**: $0.01 (1 cent)
- **Hardware prompts**: $0.02 (2 cents) 
- **Hybrid prompts**: $0.03 (3 cents)

### Depositing Credits

Deposit credits via the web interface or programmatically:

```bash
# Deposit via API
curl -X POST http://localhost:8001/api/credits/deposit \
  -H "Content-Type: application/json" \
  -d '{"user_id": "your_id", "amount": 10.00}'
```

Credits never expire. You can check your balance anytime.

---

## Support ProtoForge

If ProtoForge helps you build, consider supporting development!

### Buy Me a Coffee

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Donate-orange?style=flat&logo=buy-me-a-coffee)](https://buymeacoffee.com/happinezreal)

### Crypto Donations

**Ethereum (ERC-20)**: `0xbdEe8f109c4B5d308b7815413937e292242AA486`

```
0xbdEe8f109c4B5d308b7815413937e292242AA486
```

Any amount appreciated! 🙏

---

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
│   │   │   ├── credits.py   # Credit system
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
MINIMAX_API_KEY=sk-...
KIMI_API_KEY=sk-...
ZHIPU_API_KEY=sk-...
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
    minimax: abab6.5s-chat
    kimi: kimi-k2.5
    zhipu: glm-4
```

## Author

Built by [@happinezreal](https://x.com/happinezreal)

---

*Built for makers, by makers* ⚡
