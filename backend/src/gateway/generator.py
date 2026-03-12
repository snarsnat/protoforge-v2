"""
ProtoForge Generator - AI-powered prototyping
Uses OpenAI-compatible API calls for most providers
"""

import os
import json
import uuid
import requests
from pathlib import Path
from typing import Dict, Any, Optional


# Provider configurations - OpenAI-compatible endpoints
# Models selected for FREE TIER compatibility
PROVIDERS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo"  # Free tier: $5 credit, NO gpt-4/gpt-4o
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "model": "claude-instant-1.2",  # Free tier is instant, NOT sonnet
        "auth_header": "x-api-key",
        "auth_type": "anthropic"
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat"  # V3, free tier but rate limited
    },
    "kimi": {
        "base_url": "https://api.moonshot.ai/v1",
        "model": "moonshot-v1-8k"  # Free tier, NOT kimi-k2.5
    },
    "moonshot": {
        "base_url": "https://api.moonshot.ai/v1", 
        "model": "moonshot-v1-8k"
    },
    "minimax": {
        "base_url": "https://api.minimax.chat/v1",
        "model": "abab6.5s-chat"  # or abab6-chat
    },
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash"  # Free tier is glm-4-flash, NOT glm-4
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-turbo"  # or qwen2.5-7b-instruct
    },
    "volcengine": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-lite-4k"  # Uses endpoint IDs, this is a lite model
    },
    "siliconflow": {
        "base_url": "https://api.siliconflow.cn/v1",
        "model": "deepseek-ai/DeepSeek-V2.5"  # Chinese provider, very generous
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "model": "meta-llama/Llama-3.2-3B-Instruct"  # Free tier model
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.1-8b-instant"  # Very generous: 20 req/min
    },
    "ollama": {
        "base_url": "http://localhost:11434",
        "model": "llama3.2"  # Local, completely free
    }
}


class ProtoForgeGenerator:
    """Real AI-powered generator"""
    
    def __init__(self, api_key: str, provider: str = 'openai'):
        self.api_key = api_key
        self.provider = provider.lower()
        self.config = PROVIDERS.get(self.provider, PROVIDERS["openai"])
    
    def _call_ai(self, system_prompt: str, user_prompt: str) -> str:
        """Make API call to AI provider"""
        
        if self.provider == "anthropic":
            return self._call_anthropic(system_prompt, user_prompt)
        elif self.provider == "zhipu":
            return self._call_zhipu(system_prompt, user_prompt)
        elif self.provider == "volcengine":
            return self._call_volcengine(system_prompt, user_prompt)
        elif self.provider == "minimax":
            return self._call_minimax(system_prompt, user_prompt)
        elif self.provider == "ollama":
            return self._call_ollama(system_prompt, user_prompt)
        else:
            # Use OpenAI-compatible API
            return self._call_openai_compatible(system_prompt, user_prompt)
    
    def _call_openai_compatible(self, system: str, user: str) -> str:
        """Call OpenAI-compatible API (DeepSeek, Kimi, Groq, Together, SiliconFlow, Qwen, etc.)"""
        
        url = f"{self.config['base_url']}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.config['model'],
            'messages': [
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user}
            ],
            'temperature': 0.7,
            'max_tokens': 4000
        }
        
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            
            print(f"[{self.provider}] Status: {resp.status_code}")
            print(f"[{self.provider}] Response: {resp.text[:500]}")
            
            # Try to parse error response
            error_detail = ""
            try:
                error_data = resp.json() if resp.text else {}
                if 'error' in error_data:
                    if isinstance(error_data['error'], dict):
                        error_detail = error_data['error'].get('message', str(error_data['error']))
                    else:
                        error_detail = str(error_data['error'])
            except:
                error_detail = resp.text[:300]
            
            if resp.status_code == 429:
                # Rate limit - could be free tier limit or actual rate limit
                if 'insufficient balance' in error_detail.lower() or 'suspended' in error_detail.lower():
                    raise Exception(f"{self.provider}: Account has insufficient balance or is suspended. Add credits at {self.provider} platform.")
                elif 'quota' in error_detail.lower() or 'limit' in error_detail.lower():
                    raise Exception(f"{self.provider}: Rate limit exceeded. {error_detail}")
                else:
                    raise Exception(f"{self.provider}: Rate limit or quota exceeded. {error_detail}")
            elif resp.status_code == 401:
                # Authentication failed - could be invalid key or key needs activation
                if 'billing' in error_detail.lower() or 'payment' in error_detail.lower():
                    raise Exception(f"{self.provider}: API key requires billing setup. {error_detail}")
                else:
                    raise Exception(f"{self.provider}: Invalid or inactive API key. {error_detail}")
            elif resp.status_code == 400:
                # Bad request - often wrong model for the tier
                if 'model' in error_detail.lower():
                    raise Exception(f"{self.provider}: Model not available. {error_detail}")
                else:
                    raise Exception(f"{self.provider}: Request error. {error_detail}")
            elif resp.status_code == 403:
                # Forbidden - often free tier restrictions
                if 'free' in error_detail.lower() or 'tier' in error_detail.lower():
                    raise Exception(f"{self.provider}: Free tier restriction. {error_detail}")
                else:
                    raise Exception(f"{self.provider}: Access forbidden. {error_detail}")
            elif resp.status_code != 200:
                raise Exception(f"{self.provider} error ({resp.status_code}): {error_detail or resp.text[:300]}")
            
            return resp.json()['choices'][0]['message']['content']
            
        except requests.exceptions.Timeout:
            raise Exception(f"{self.provider} request timed out. Try again.")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Could not connect to {self.provider}. Check your internet.")
    
    def _call_anthropic(self, system: str, user: str) -> str:
        """Call Anthropic API"""
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        payload = {
            'model': self.config['model'],
            'max_tokens': 4000,
            'messages': [
                {'role': 'user', 'content': f"System: {system}\n\nUser: {user}"}
            ]
        }
        
        try:
            resp = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=payload,
                timeout=120
            )
            
            print(f"[anthropic] Status: {resp.status_code}")
            print(f"[anthropic] Response: {resp.text[:200]}")
            
            if resp.status_code == 429:
                raise Exception("Anthropic rate limit. Wait and try again.")
            elif resp.status_code == 401:
                raise Exception("Invalid Anthropic API key.")
            
            return resp.json()['content'][0]['text']
            
        except requests.exceptions.Timeout:
            raise Exception("Anthropic request timed out.")
    
    def _call_zhipu(self, system: str, user: str) -> str:
        """Call Zhipu (GLM) API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.config['model'],  # Uses glm-4-flash (free tier)
            'messages': [
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user}
            ]
        }
        
        try:
            resp = requests.post(
                'https://open.bigmodel.cn/api/paas/v4/chat/completions',
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if resp.status_code != 200:
                raise Exception(f"Zhipu error: {resp.text[:200]}")
            
            return resp.json()['choices'][0]['message']['content']
            
        except requests.exceptions.Timeout:
            raise Exception("Zhipu request timed out.")
    
    def _call_volcengine(self, system: str, user: str) -> str:
        """Call Volcano Engine API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.config['model'],  # Uses doubao-lite-4k (free tier)
            'messages': [
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user}
            ]
        }
        
        try:
            resp = requests.post(
                'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if resp.status_code != 200:
                raise Exception(f"Volcano error: {resp.text[:200]}")
            
            return resp.json()['choices'][0]['message']['content']
            
        except requests.exceptions.Timeout:
            raise Exception("Volcano request timed out.")
    
    def _call_minimax(self, system: str, user: str) -> str:
        """Call MiniMax API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.config['model'],  # Uses abab6.5s-chat (free tier)
            'messages': [
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user}
            ]
        }
        
        try:
            resp = requests.post(
                'https://api.minimax.chat/v1/text/chatcompletion_v2',
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if resp.status_code == 401:
                raise Exception("Invalid MiniMax API key. Check your account.")
            elif resp.status_code != 200:
                raise Exception(f"MiniMax error: {resp.text[:200]}")
            
            return resp.json()['choices'][0]['message']['content']
            
        except requests.exceptions.Timeout:
            raise Exception("MiniMax request timed out.")
    
    def _call_ollama(self, system: str, user: str) -> str:
        """Call Ollama local AI"""
        
        url = f"{self.config['base_url']}/api/generate"
        
        payload = {
            'model': self.config['model'],
            'prompt': f"System: {system}\n\nUser: {user}",
            'stream': False
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=120)
            
            if resp.status_code != 200:
                raise Exception(f"Ollama error: {resp.text[:100]}")
            
            return resp.json().get('response', 'No response')
            
        except requests.exceptions.ConnectionError:
            raise Exception("Ollama not running. Start with: ollama serve")
        except requests.exceptions.Timeout:
            raise Exception("Ollama request timed out.")
    
    def generate(self, prompt: str, mode: str, project_dir: str) -> Dict[str, Any]:
        """Generate prototype based on prompt and mode"""
        
        project_id = str(uuid.uuid4())[:8]
        project_path = Path(project_dir) / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Analyze request with AI
        analysis = self._analyze_request(prompt, mode)
        
        # Generate based on mode
        if mode == 'software':
            return self._generate_software(prompt, analysis, project_path)
        elif mode == 'hardware':
            return self._generate_hardware(prompt, analysis, project_path)
        elif mode == 'hybrid':
            return self._generate_hybrid(prompt, analysis, project_path)
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    def _analyze_request(self, prompt: str, mode: str) -> Dict[str, Any]:
        """Analyze what needs to be built"""
        
        system_prompt = f"""You are a software/hardware architect analyzing a user's request for a {mode} project.
Analyze and provide a detailed specification in JSON format with these keys:
- components: array of components needed (name, type, description)
- tech_stack: technologies to use
- features: key features to implement
- description: brief description of the project

Return ONLY valid JSON."""
        
        user_prompt = f"Analyze this request: {prompt}"
        
        response = self._call_ai(system_prompt, user_prompt)
        
        # Extract JSON
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        
        return {"description": prompt, "components": [], "tech_stack": [], "features": []}
    
    def _generate_software(self, prompt: str, analysis: Dict, project_path: Path) -> Dict[str, Any]:
        """Generate software project"""
        
        system_prompt = """You are a full-stack developer. Generate a complete web application.
Create these files:
1. index.html - Main HTML file
2. style.css - Styles
3. app.js - JavaScript functionality

Output ONLY valid code for each file, properly formatted. No explanations."""
        
        user_prompt = f"Create a web app: {prompt}"
        
        # Generate code
        code_response = self._call_ai(system_prompt, user_prompt)
        
        files = []
        
        # Try to extract code blocks
        try:
            # Look for HTML
            if '<html' in code_response.lower() or '<!DOCTYPE' in code_response:
                html_start = code_response.find('<html')
                if html_start == -1:
                    html_start = code_response.find('<!DOCTYPE')
                html_end = code_response.rfind('</html>') + 7
                if html_end > 6:
                    html_content = code_response[html_start:html_end]
                    (project_path / 'index.html').write_text(html_content)
                    files.append({'name': 'index.html', 'type': 'html'})
            
            # Look for CSS
            if 'css' in code_response.lower():
                css_parts = code_response.split('```css')
                for i, part in enumerate(css_parts[1:], 1):
                    end = part.find('```')
                    if end > 0:
                        css_content = part[:end].strip()
                        (project_path / 'style.css').write_text(css_content)
                        files.append({'name': 'style.css', 'type': 'css'})
                        break
                else:
                    # No code blocks, try inline
                    (project_path / 'style.css').write_text('/* Styles */')
                    files.append({'name': 'style.css', 'type': 'css'})
            
            # Look for JS
            if 'javascript' in code_response.lower() or 'script' in code_response.lower():
                js_parts = code_response.split('```javascript')
                for i, part in enumerate(js_parts[1:], 1):
                    end = part.find('```')
                    if end > 0:
                        js_content = part[:end].strip()
                        (project_path / 'app.js').write_text(js_content)
                        files.append({'name': 'app.js', 'type': 'javascript'})
                        break
                else:
                    (project_path / 'app.js').write_text('// App code')
                    files.append({'name': 'app.js', 'type': 'javascript'})
                    
        except Exception as e:
            print(f"Error parsing code: {e}")
        
        # Ensure at least basic files exist
        if not files:
            (project_path / 'index.html').write_text('<!DOCTYPE html>\n<html><body><h1>Hello</h1></body></html>')
            (project_path / 'style.css').write_text('body { font-family: sans-serif; }')
            (project_path / 'app.js').write_text('console.log("Hello");')
            files = [
                {'name': 'index.html', 'type': 'html'},
                {'name': 'style.css', 'type': 'css'},
                {'name': 'app.js', 'type': 'javascript'}
            ]
        
        return {
            'project_id': project_id,
            'files': files,
            'mode': 'software',
            'description': analysis.get('description', prompt)
        }
    
    def _generate_hardware(self, prompt: str, analysis: Dict, project_path: Path) -> Dict[str, Any]:
        """Generate hardware project"""
        
        system_prompt = """You are a hardware engineer. Generate a circuit diagram and BOM.
Create:
1. circuit.md - Mermaid diagram of the circuit
2. bom.md - Bill of Materials with components
3. instructions.md - Build instructions

Output ONLY valid markdown."""
        
        user_prompt = f"Design hardware for: {prompt}"
        
        response = self._call_ai(system_prompt, user_prompt)
        
        files = []
        
        # Save response as markdown
        (project_path / 'hardware.md').write_text(response)
        files.append({'name': 'hardware.md', 'type': 'markdown'})
        
        # Create diagram file
        diagram = f"# Hardware Design\n\n{analysis.get('description', prompt)}\n\n## Components\n"
        for comp in analysis.get('components', []):
            diagram += f"- {comp.get('name', 'Component')}: {comp.get('description', '')}\n"
        
        (project_path / 'diagram.md').write_text(diagram)
        files.append({'name': 'diagram.md', 'type': 'diagram'})
        
        return {
            'project_id': project_id,
            'files': files,
            'mode': 'hardware',
            'description': analysis.get('description', prompt)
        }
    
    def _generate_hybrid(self, prompt: str, analysis: Dict, project_path: Path) -> Dict[str, Any]:
        """Generate hybrid hardware+software project"""
        
        # Generate both
        software_result = self._generate_software(prompt, analysis, project_path / 'software')
        hardware_result = self._generate_hardware(prompt, analysis, project_path / 'hardware')
        
        files = software_result['files'] + hardware_result['files']
        
        return {
            'project_id': project_id,
            'files': files,
            'mode': 'hybrid',
            'description': analysis.get('description', prompt)
        }
