<img src="https://i.imgur.com/S6lNJLn.png" alt="ProtoForge" width="100%"/>

# ProtoForge ⚡

[![X](https://img.shields.io/badge/Follow-@happinezreal-000000?style=flat&logo=x)](https://x.com/happinezreal)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Donate-orange?style=flat&logo=buy-me-a-coffee)](https://buymeacoffee.com/nebsol) 

**AI-Powered Prototyping Engine**

Build real software, hardware, and hybrid prototypes with AI.

Built my me a 13 year old ⚡️ 
---

## What is ProtoForge?

ProtoForge is an AI-powered builder that generates real prototypes:

- **Software** → Web apps, APIs, scripts with actual code
- **Hardware** → Circuit diagrams (Mermaid.js), 3D models, BOMs
- **Hybrid** → Combined hardware + software systems

Just describe what you want, select a mode, and ProtoForge generates the files.
![View how Protoforge works](protoforge_architecture.svg)

## Quick Start

### 1. Clone the Repo

```bash
git clone https://github.com/snarsnat/protoforge-v2.git
cd protoforge-v2
```

### 2. Install Dependencies

```bash
cd backend
pip3 install -r ../requirements.txt
```

**Note:** If you're using conda, make sure to install in your conda environment:
```bash
conda activate your-env  # if using conda
pip3 install -r ../requirements.txt
```

### 3. Run the Server

```bash
cd backend
PYTHONPATH=. python3 -m src.gateway.app
```

Server will start on `http://localhost:8001`

### 4. Open in Browser

Navigate to **http://localhost:8001** in your browser.

> **Troubleshooting:** If you see "Failed to fetch" errors, hard refresh your browser (`Cmd+Shift+R` on Mac, `Ctrl+Shift+R` on Windows) to clear cached files.

---

## 🖥️ Desktop App (macOS)

Prefer a native app? ProtoForge is available as a macOS .dmg installer!

### Install from .dmg

1. **Download** the latest `.dmg` from [Releases](https://github.com/snarsnat/protoforge-v2/releases)
2. **Open** the `.dmg` file
3. **Drag** ProtoForge to your Applications folder
4. **Launch** from Applications

> **First Launch on macOS:** If you see a security warning:
> - Right-click `ProtoForge.app` → **Open**
> - Click **"Open Anyway"** in Security & Privacy
> - Or run: `xattr -rd com.apple.quarantine /Applications/ProtoForge.app`

### Build from Source

```bash
cd desktop
chmod +x scripts/build.sh
./scripts/build.sh
```

The `.dmg` will be created in `desktop/dist/ProtoForge-2.0.0.dmg`

See [`desktop/README.md`](desktop/README.md) for full build instructions.

---

## API Configuration

### 🆓 Free Tier API Keys (Recommended)

These providers offer **free tier** API keys that work great with ProtoForge:

| Provider | Free Tier Model | Notes |
|----------|-----------------|-------|
| **Groq** | `llama-3.1-8b-instant` or `mixtral-8x7b-32768` | Very generous free tier, 20 req/min |
| **Together AI** | `meta-llama/Llama-3.2-3B-Instruct` or any model with "free" label | Limited daily tokens |
| **SiliconFlow** | `deepseek-ai/DeepSeek-V2.5` or `Qwen/Qwen2.5-7B-Instruct` | Chinese provider, very generous |
| **DeepSeek** | `deepseek-chat` (V3) or `deepseek-coder` | Has free tier but rate limited |
| **Zhipu (GLM)** | `glm-4-flash` (specifically the -flash suffix) | Free tier is `glm-4-flash`, NOT `glm-4` |
| **Qwen** | `qwen-turbo` or `qwen2.5-7b-instruct` | Alibaba, free tier is specific models |
| **Kimi** | `moonshot-v1-8k` | Moonshot free tier, NOT `kimi-k2.5` |
| **OpenAI** | `gpt-3.5-turbo` | $5 credit, NO gpt-4/gpt-4o |
| **Anthropic** | `claude-instant-1.2` | Free tier is instant, NOT sonnet |
| **MiniMax** | `abab6.5s-chat` or `abab6-chat` | Check their docs, often changes |
| **VolcEngine** | `doubao-lite-4k` or `ep-202...` (endpoint ID) | ByteDance, uses endpoint IDs not model names |
| **Ollama** | Any local model (`llama3.2`, `qwen2.5`, etc.) | Runs locally, completely free |

**Get your free API keys:**
- Groq: [groq.com](https://console.groq.com/keys)
- Together AI: [together.ai](https://api.together.xyz/settings/api-keys)
- SiliconFlow: [siliconflow.cn](https://cloud.siliconflow.cn/account/ak)
- DeepSeek: [platform.deepseek.com](https://platform.deepseek.com/api-keys)
- Zhipu: [bigmodel.cn](https://open.bigmodel.cn/)
- Qwen: [dashscope.aliyun.com](https://dashscope.aliyun.com/)
- Kimi: [moonshot.ai](https://platform.moonshot.ai/)
- OpenAI: [platform.openai.com](https://platform.openai.com/)
- Anthropic: [anthropic.com](https://console.anthropic.com/)
- MiniMax: [minimax.chat](https://api.minimax.chat/)
- VolcEngine: [volces.com](https://www.volces.com/)
- Ollama: [ollama.ai](https://ollama.ai/) (local installation)

### Test Your API Key

Use the **"Test Key"** button in the UI, or test via curl:

```bash
# Test Groq (recommended for free tier)
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_GROQ_KEY", "provider": "groq"}'

# Test Together AI
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_TOGETHER_KEY", "provider": "together"}'

# Test OpenAI
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_OPENAI_KEY", "provider": "openai"}'

# Test Anthropic
curl -X POST http://localhost:8001/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "YOUR_ANTHROPIC_KEY", "provider": "anthropic"}'
```

**Expected responses:**
- ✅ `{"success": true, ...}` - Your key works!
- ❌ `{"success": false, "error": "..."}` - Check the error message for details

**Common issues:**
- "Invalid API Key" → Double-check your key, no extra spaces
- "Rate limit exceeded" → Wait a bit, free tiers have limits
- "Model not available" → The selected model may require paid tier

---

## Supported Providers

ProtoForge supports **13+ AI providers**. Free tier keys work great!

### ✅ Recommended (Free Tier Friendly)
- **Groq** - Fast, free inference (Llama models)
- **Together AI** - Free credits, many models
- **SiliconFlow** - Free tier available
- **DeepSeek** - Free credits on signup

### ✅ Also Supported
- OpenAI, Anthropic, MiniMax, Kimi (Moonshot), Zhipu (GLM), Qwen, VolcEngine, Ollama (local)

**Note:** ProtoForge uses your API key directly - no proxying, no storage. Keys are sent straight to the provider.

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
