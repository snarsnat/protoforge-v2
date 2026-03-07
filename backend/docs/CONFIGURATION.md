# Configuration Guide

## config.yaml

The main configuration file for ProtoForge.

### Models Section

```yaml
models:
  - name: gpt-4o           # Internal identifier
    display_name: GPT-4o   # Human-readable name
    use: langchain_openai:ChatOpenAI  # LangChain class
    model: gpt-4o          # Model identifier
    api_key: $OPENAI_API_KEY  # API key (use env var)
    supports_thinking: false
    supports_vision: true
    max_tokens: 4096
    temperature: 0.7
```

### Supported Providers

- **OpenAI**: `langchain_openai:ChatOpenAI`
- **Anthropic**: `langchain_anthropic:ChatAnthropic`
- **DeepSeek**: `langchain_openai:ChatOpenAI` with `base_url: https://api.deepseek.com/v1`
- **Google**: `langchain_google_genai:ChatGoogleGenerativeAI`

### Tools Section

```yaml
tools:
  - use: src.community.web_search:TavilySearch
    group: community
```

### Sandbox Configuration

```yaml
sandbox:
  use: src.community.local_sandbox:LocalSandboxProvider
  # Or for Docker:
  # use: src.community.docker_sandbox:DockerSandboxProvider
```

### Memory Configuration

```yaml
memory:
  enabled: true
  injection_enabled: true
  storage_path: ./data/memory.json
  debounce_seconds: 30
  max_facts: 100
  fact_confidence_threshold: 0.7
  max_injection_tokens: 2000
```

### Subagents Configuration

```yaml
subagents:
  enabled: true
  max_concurrent: 3
  timeout: 900
```
