"""ProtoForge Frontend - Main Page"""

import { useState, useEffect } from 'react'

export default function Home() {
  const [prompt, setPrompt] = useState('')
  const [mode, setMode] = useState('software')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [apiKey, setApiKey] = useState('')
  const [provider, setProvider] = useState('openai')

  const handleGenerate = async () => {
    if (!prompt.trim()) return
    
    setLoading(true)
    try {
      const res = await fetch('/api/langgraph/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: `[${mode}] ${prompt}`,
          thread_id: 'default'
        })
      })
      
      const data = await res.json()
      setResult(data)
    } catch (err) {
      console.error(err)
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
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
            <option value="deepseek">DeepSeek</option>
          </select>
          <input
            type="password"
            placeholder="API Key"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
          />
        </section>

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
          gap: 1rem;
          margin-bottom: 1rem;
        }
        .config input, .config select {
          padding: 0.5rem;
          font-size: 1rem;
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
