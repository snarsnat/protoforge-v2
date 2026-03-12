"""ProtoForge Frontend - Main Page"""

import { useState, useEffect } from 'react'

export default function Home() {
  const [prompt, setPrompt] = useState('')
  const [mode, setMode] = useState('software')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [apiKey, setApiKey] = useState('')
  const [provider, setProvider] = useState('groq')
  const [modelName, setModelName] = useState('')
  const [testingKey, setTestingKey] = useState(false)
  const [keyStatus, setKeyStatus] = useState<{valid: boolean, message: string, detectedModel?: string} | null>(null)

  const handleAutoDetect = async () => {
    if (!apiKey.trim()) {
      setKeyStatus({ valid: false, message: 'Please enter an API key first' })
      return
    }
    
    setTestingKey(true)
    setKeyStatus(null)
    
    try {
      const res = await fetch('http://localhost:8001/api/auto-detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: apiKey,
          provider: provider
        })
      })
      
      const data = await res.json()
      
      if (data.success) {
        setKeyStatus({ 
          valid: true, 
          message: `Auto-detected: ${data.model}`,
          detectedModel: data.model
        })
        setModelName(data.model)
      } else {
        setKeyStatus({ valid: false, message: data.error || 'Auto-detect failed' })
      }
    } catch (err: any) {
      setKeyStatus({ valid: false, message: `Failed to connect: ${err.message}` })
    } finally {
      setTestingKey(false)
    }
  }

  const handleTestKey = async () => {
    if (!apiKey.trim()) {
      setKeyStatus({ valid: false, message: 'Please enter an API key' })
      return
    }
    
    setTestingKey(true)
    setKeyStatus(null)
    
    try {
      const res = await fetch('http://localhost:8001/api/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: apiKey,
          provider: provider
        })
      })
      
      const data = await res.json()
      
      if (data.success) {
        setKeyStatus({ 
          valid: true, 
          message: 'API key works!',
          detectedModel: data.model || undefined
        })
        if (data.model) {
          setModelName(data.model)
        }
      } else {
        setKeyStatus({ valid: false, message: data.error || 'API key failed' })
      }
    } catch (err: any) {
      setKeyStatus({ valid: false, message: `Failed to connect: ${err.message}` })
    } finally {
      setTestingKey(false)
    }
  }

  const handleGenerate = async () => {
    if (!prompt.trim()) return
    if (!apiKey.trim()) {
      alert('Please enter an API key or test it first')
      return
    }
    
    setLoading(true)
    setResult(null)
    
    try {
      const res = await fetch('http://localhost:8001/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt,
          mode: mode,
          api_key: apiKey,
          provider: provider,
          model_name: modelName || undefined
        })
      })
      
      const data = await res.json()
      setResult(data)
    } catch (err: any) {
      console.error(err)
      setResult({ error: `Failed to fetch: ${err.message}. Make sure the backend is running on http://localhost:8001` })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header className="header">
        <h1>⚡ ProtoForge</h1>
        <p>AI-Powered Prototyping Engine</p>
      </header>

      <main>
        <section className="config">
          <select value={provider} onChange={e => setProvider(e.target.value)}>
            <option value="groq">Groq (Recommended - Free)</option>
            <option value="together">Together AI (Free)</option>
            <option value="siliconflow">SiliconFlow (Free)</option>
            <option value="deepseek">DeepSeek (Free)</option>
            <option value="zhipu">Zhipu/GLM (Free)</option>
            <option value="qwen">Qwen (Free)</option>
            <option value="kimi">Kimi/Moonshot (Free)</option>
            <option value="minimax">MiniMax (Free)</option>
            <option value="volcengine">VolcEngine (Free)</option>
            <option value="openai">OpenAI ($5 credit)</option>
            <option value="anthropic">Anthropic (Free tier)</option>
            <option value="ollama">Ollama (Local)</option>
          </select>
          <input
            type="password"
            placeholder="API Key"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            style={{ flex: 1 }}
          />
          <button onClick={handleAutoDetect} disabled={testingKey} style={{ whiteSpace: 'nowrap', background: '#ff3e00' }}>
            {testingKey ? 'Detecting...' : 'Auto-Detect'}
          </button>
          <button onClick={handleTestKey} disabled={testingKey} style={{ whiteSpace: 'nowrap' }}>
            {testingKey ? 'Testing...' : 'Test Key'}
          </button>
        </section>
        
        {keyStatus && (
          <section className={`key-status ${keyStatus.valid ? 'valid' : 'invalid'}`}>
            {keyStatus.valid ? '✅' : '❌'} {keyStatus.message}
            {keyStatus.detectedModel && <span> • Using: {keyStatus.detectedModel}</span>}
          </section>
        )}

        <section className="mode-selector">
          {['software', 'hardware', 'hybrid'].map(m => (
            <label key={m} className={mode === m ? 'active' : ''}>
              <input
                type="radio"
                name="mode"
                value={m}
                checked={mode === m}
                onChange={e => setMode(e.target.value)}
              />
              {m.charAt(0).toUpperCase() + m.slice(1)}
            </label>
          ))}
        </section>

        <section className="input">
          <textarea
            placeholder="Describe what you want to build..."
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            rows={4}
          />
          <button onClick={handleGenerate} disabled={loading}>
            {loading ? 'Generating...' : 'Generate'}
          </button>
        </section>

        {result && (
          <section className="result">
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </section>
        )}
      </main>

      <style jsx>{`
        .container {
          max-width: 800px;
          margin: 0 auto;
          padding: 2rem;
          font-family: system-ui, sans-serif;
        }
        .header {
          text-align: center;
          margin-bottom: 2rem;
        }
        .header h1 {
          font-size: 2rem;
          margin: 0;
        }
        .config {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }
        .config input, .config select {
          padding: 0.5rem;
          font-size: 1rem;
        }
        .config button {
          padding: 0.5rem 1rem;
          font-size: 1rem;
          background: #333;
          color: white;
          border: 2px solid #333;
          cursor: pointer;
        }
        .config button:disabled {
          opacity: 0.5;
        }
        .key-status {
          padding: 0.5rem;
          margin-bottom: 1rem;
          border: 2px solid;
          font-size: 0.9rem;
        }
        .key-status.valid {
          background: #1a4a1a;
          border-color: #2d7a2d;
          color: #8f8;
        }
        .key-status.invalid {
          background: #4a1a1a;
          border-color: #7a2d2d;
          color: #f88;
        }
        .mode-selector {
          display: flex;
          gap: 0;
          margin-bottom: 1rem;
          border: 2px solid #333;
        }
        .mode-selector label {
          flex: 1;
          padding: 1rem;
          text-align: center;
          cursor: pointer;
          background: #141414;
          color: #888;
          border-right: 1px solid #333;
        }
        .mode-selector label:last-child {
          border-right: none;
        }
        .mode-selector label.active {
          background: #ff3e00;
          color: white;
        }
        .input {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .input textarea {
          padding: 1rem;
          font-size: 1rem;
          background: #141414;
          color: #f0f0f0;
          border: 2px solid #333;
          resize: vertical;
        }
        .input button {
          padding: 1rem 2rem;
          font-size: 1rem;
          background: #ff3e00;
          color: white;
          border: none;
          cursor: pointer;
        }
        .input button:disabled {
          opacity: 0.6;
        }
        .result {
          margin-top: 2rem;
          padding: 1rem;
          background: #141414;
          border: 2px solid #333;
        }
        .result pre {
          overflow-x: auto;
          color: #888;
        }
      `}</style>
    </div>
  )
}
