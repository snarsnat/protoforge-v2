<img src="https://i.imgur.com/S6lNJLn.png" alt="ProtoForge" width="100%"/>

# ProtoForge ⚡

[![X](https://img.shields.io/badge/Follow-@happinezreal-000000?style=flat&logo=x)](https://x.com/happinezreal)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Donate-orange?style=flat&logo=buy-me-a-coffee)](https://buymeacoffee.com/nebsol)

**AI-Powered Prototyping Engine**

Build real software, hardware, and hybrid prototypes with AI.

---

## What is ProtoForge?

ProtoForge is an AI-powered builder that generates real prototypes:

- **Software** → Web apps, APIs, scripts with actual code
- **Hardware** → Circuit diagrams (Mermaid.js), 3D models, BOMs
- **Hybrid** → Combined hardware + software systems

Just describe what you want, select a mode, and ProtoForge generates the files.

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

---

## API Configuration

### Test Your API Key

Before building, test your API key to make sure it works:

```bash
# Test OpenAI
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_OPENAI_KEY", "provider": "openai"}'

# Test Anthropic
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_ANTHROPIC_KEY", "provider": "anthropic"}'

# Test DeepSeek
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_DEEPSEEK_KEY", "provider": "deepseek"}'

# Test MiniMax
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_MINIMAX_KEY", "provider": "minimax"}'

# Test Kimi (Moonshot)
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_KIMI_KEY", "provider": "kimi"}'

# Test Zhipu (GLM)
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_ZHIPU_KEY", "provider": "zhipu"}'

# Test Qwen
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_QWEN_KEY", "provider": "qwen"}'

# Test Volcano Engine
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_VOLCENGINE_KEY", "provider": "volcengine"}'

# Test SiliconFlow
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_SILICONFLOW_KEY", "provider": "siliconflow"}'

# Test Together AI
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_TOGETHER_KEY", "provider": "together"}'

# Test Groq
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_GROQ_KEY", "provider": "groq"}'
```

If you get `{"success": true, ...}`, your key works! If you get billing errors, check your API key has credits available.

---

## Getting an API Key

Many providers offer **free tier** API keys:

| Provider | Free Tier | Link |
|----------|-----------|------|
| **OpenAI** | $5 credit | [platform.openai.com](https://platform.openai.com) |
| **Anthropic** | $5 credit | [console.anthropic.com](https://console.anthropic.com) |
| **DeepSeek** | Yes | [platform.deepseek.com](https://platform.deepseek.com) |
| **MiniMax** | Yes | [platform.minimax.io](https://platform.minimax.io) |
| **Kimi (Moonshot)** | Yes | [platform.moonshot.ai](https://platform.moonshot.ai) |
| **Zhipu (GLM)** | Yes | [open.bigmodel.cn](https://open.bigmodel.cn) |
| **Qwen** | Yes | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com) |
| **SiliconFlow** | Yes | [siliconflow.cn](https://siliconflow.cn) |
| **Together AI** | Yes | [together.ai](https://together.ai) |
| **Groq** | Yes | [groq.com](https://groq.com) |
| **Volcano Engine** | Yes | [console.volcengine.com](https://console.volcengine.com) |

### Free Tier API Keys

Free tier API keys work exactly like paid keys - they use the same API endpoints. The difference is:
- **Rate limits** - Fewer requests per minute
- **Usage caps** - Limited spend per month
- **Model restrictions** - Some free tiers only work with specific models

ProtoForge passes your key directly to the provider. No proxying, no storage.

---

## Anti-Trope Design

ProtoForge is deliberately designed **opposite** to typical AI builder aesthetics:

| AI Builder Tropes | ProtoForge |
|------------------|------------|
| Purple/indigo gradients | Solid dark/light colors only |
| Rounded corners everywhere | Sharp edges (0px radius) |
| Shadows and glows | Flat design |
| Frosted glass effects | No blur |
| Inter/Space Grotesk fonts | IBM Plex Mono |
| Sparkle emojis | No sparkles |
| Hero sections | No hero |
| Light themes | Dark/light with orange accent |

---

## Features

### Mode Selection
- **Software** - Web apps, APIs, scripts
- **Hardware** - Circuit diagrams, 3D models, BOMs
- **Hybrid** - Combined hardware + software

### Browser Mockup
- **3D Model** - Interactive 3D view (hardware/hybrid)
- **Diagram** - Drag circuit boards, connected wires
- **BOM** - Checkable Bill of Materials
- **Code** - File browser with syntax highlighting
- **Instructions** - Step-by-step build guide

### Export Options
- **Download** - Get all files as .zip
- **Share** - Post to X, Facebook, LinkedIn, WhatsApp, Email

### Theme
- **Light Mode** - Orange borders (#ff3e00), white background, black text
- **Dark Mode** - Orange borders, black background, white text

---

## Author

Built by [@happinezreal](https://x.com/happinezreal)

---

*Built for makers, by makers* ⚡
