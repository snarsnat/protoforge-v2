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
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "meta-llama/llama-3.1-8b-instruct"  # Free tier available, many models
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
        
        # Normalize project_dir to absolute path
        base = Path(project_dir).resolve()
        project_id = str(uuid.uuid4())[:8]
        project_path = base / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Ensure subdirectories exist for all modes
        (project_path / "software").mkdir(parents=True, exist_ok=True)
        (project_path / "hardware").mkdir(parents=True, exist_ok=True)
        
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
        """Generate software project with REAL working code"""
        
        # Generate HTML with AI
        html_prompt = f"""Generate a COMPLETE, WORKING index.html for: {prompt}
Include: proper HTML5 structure, CDN links for any libraries needed, all UI elements, forms, buttons, containers.
Make it production-ready with real functionality. Output ONLY the HTML code, no explanations."""
        html_content = self._call_ai("You are an expert frontend developer. Write complete, working HTML files.", html_prompt)
        # Extract and validate HTML (case-insensitive)
        html_lower = html_content.lower()
        if '<html' in html_lower and '</html>' in html_lower:
            start = html_lower.find('<html')
            end = html_lower.rfind('</html>') + len('</html>')
            html_content = html_content[start:end]
        else:
            # Fallback placeholder HTML if AI failed to produce valid HTML
            html_content = "<html><body><h1>ProtoForge - Software content not generated</h1><p>The AI did not return valid HTML. Please retry generation.</p></body></html>"
        (project_path / 'software' / 'index.html').write_text(html_content)
        
        # Generate CSS with AI
        css_prompt = f"""Generate COMPLETE, WORKING CSS for: {prompt}
Include: responsive design, modern styling, animations, dark/light mode support if relevant.
Make it look professional. Output ONLY the CSS code, no explanations."""
        css_content = self._call_ai("You are an expert CSS developer. Write complete, production-ready stylesheets.", css_prompt)
        # Extract CSS
        if '```css' in css_content:
            css_content = css_content.split('```css')[1].split('```')[0].strip()
        (project_path / 'software' / 'style.css').write_text(css_content)
        
        # Generate JavaScript with AI
        js_prompt = f"""Generate COMPLETE, WORKING JavaScript for: {prompt}
Include: event handlers, DOM manipulation, API calls if needed, error handling, real functionality.
Make it fully functional. Output ONLY the JavaScript code, no explanations."""
        js_content = self._call_ai("You are an expert JavaScript developer. Write complete, working application code.", js_prompt)
        # Extract JS
        if '```javascript' in js_content or '```js' in js_content:
            for marker in ['```javascript', '```js']:
                if marker in js_content:
                    js_content = js_content.split(marker)[1].split('```')[0].strip()
                    break
        (project_path / 'software' / 'app.js').write_text(js_content)
        
        files = [
            {'name': 'software/index.html', 'type': 'html'},
            {'name': 'software/style.css', 'type': 'css'},
            {'name': 'software/app.js', 'type': 'javascript'}
        ]
        
        # Generate tech specs with AI
        specs_prompt = f"""Analyze this project: {prompt}
Generate technical specifications including: architecture, tech stack, features, API endpoints (if any), data flow.
Be specific and detailed. Output as plain text."""
        specs = self._call_ai("You are a software architect. Write detailed technical specifications.", specs_prompt)
        
        # Generate deployment instructions with AI
        instructions_prompt = f"""Generate step-by-step deployment instructions for: {prompt}
Include: 1) Setup/Installation, 2) Configuration, 3) Running locally, 4) Deployment steps, 5) Testing.
Be specific with commands and file paths. Output as a numbered list."""
        instructions_response = self._call_ai("You are a DevOps engineer. Write clear deployment instructions.", instructions_prompt)
        instructions = [line.strip() for line in instructions_response.split('\n') if line.strip()]
        
        # Combine all code for display
        code_content = f"// === index.html ===\n{html_content}\n\n// === style.css ===\n{css_content}\n\n// === app.js ===\n{js_content}"
        
        # Build file contents map for frontend (with software/ prefix)
        file_contents = {
            'software/index.html': html_content,
            'software/style.css': css_content,
            'software/app.js': js_content
        }
        
        return {
            'project_id': project_path.name,
            'files': files,
            'file_contents': file_contents,
            'mode': 'software',
            'description': analysis.get('description', prompt),
            'code': code_content,
            'specs': specs,
            'components': [],
            'instructions': instructions,
            'diagram': None
        }
    
    def _generate_hardware(self, prompt: str, analysis: Dict, project_path: Path) -> Dict[str, Any]:
        """Generate hardware project with REAL diagrams, BOM, and instructions"""
        
        # Generate Mermaid circuit diagram with AI
        diagram_prompt = f"""Generate a Mermaid.js circuit diagram for: {prompt}
Use mermaid graph TD or flowchart syntax. Include all components, connections, power supply, inputs/outputs.
Make it a proper circuit diagram that will render. Output ONLY the mermaid code, no explanations.
Example format:
graph TD
    A[Component1] --> B[Component2]
    B --> C[Output]"""
        diagram = self._call_ai("You are an electrical engineer. Create Mermaid.js circuit diagrams.", diagram_prompt)
        # Extract mermaid code robustly
        diagram_lower = diagram.lower()
        if '```mermaid' in diagram_lower:
            diagram = diagram.split('```mermaid')[1].split('```')[0].strip()
        elif '```' in diagram:
            diagram = diagram.split('```')[1].split('```')[0].strip()
        elif 'graph TD' in diagram or 'graph LR' in diagram or 'flowchart' in diagram:
            # Already valid mermaid, just strip whitespace
            diagram = diagram.strip()
        else:
            # Fallback: try to find any mermaid-like content or use as-is
            diagram = diagram.strip()
        # Ensure diagram starts with valid mermaid syntax
        if not (diagram.startswith('graph') or diagram.startswith('flowchart') or diagram.startswith('sequenceDiagram')):
            # Prepend graph TD if missing
            if 'graph TD' not in diagram and 'graph LR' not in diagram:
                diagram = 'graph TD\n' + diagram
        (project_path / 'hardware' / 'diagram.mmd').write_text(diagram)
        
        # Generate BOM with AI
        bom_prompt = f"""Generate a complete Bill of Materials (BOM) for: {prompt}
Return JSON array with: name, qty (quantity), ref (reference designator like R1, C1, U1), notes (description/specs).
Example: [{{"name": "Resistor 10k", "qty": 2, "ref": "R1,R2", "notes": "1/4W 5%"}}]
Output ONLY valid JSON array."""
        bom_response = self._call_ai("You are a hardware engineer. Create detailed bills of materials.", bom_prompt)
        # Extract JSON
        components = []
        try:
            start = bom_response.find('[')
            end = bom_response.rfind(']') + 1
            if start >= 0 and end > start:
                components = json.loads(bom_response[start:end])
        except:
            components = [{'name': 'Component', 'qty': 1, 'ref': 'X1', 'notes': 'See diagram'}]
        (project_path / 'hardware' / 'bom.json').write_text(json.dumps(components, indent=2))
        
        # Generate build instructions with AI
        instructions_prompt = f"""Generate step-by-step build instructions for: {prompt}
Include: 1) Components needed, 2) Tools required, 3) Assembly steps (numbered), 4) Wiring connections, 5) Testing procedure, 6) Troubleshooting.
Be extremely specific with wire colors, pin numbers, and safety warnings. Output as numbered steps."""
        instructions_response = self._call_ai("You are a hardware technician. Write detailed assembly instructions.", instructions_prompt)
        instructions = [line.strip() for line in instructions_response.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        # Generate specs
        specs_prompt = f"""Generate technical specifications for this hardware project: {prompt}
Include: voltage requirements, current draw, dimensions, weight, operating temperature, interfaces, certifications needed.
Be specific with numbers and units."""
        specs = self._call_ai("You are a hardware engineer. Write detailed technical specifications.", specs_prompt)
        
        files = [
            {'name': 'hardware/diagram.mmd', 'type': 'mermaid'},
            {'name': 'hardware/bom.json', 'type': 'json'},
            {'name': 'hardware/instructions.md', 'type': 'markdown'}
        ]
        
        # Save instructions
        (project_path / 'hardware' / 'instructions.md').write_text('\n'.join(instructions))
        
        # Build file contents map (with hardware/ prefix)
        file_contents = {
            'hardware/diagram.mmd': diagram,
            'hardware/bom.json': json.dumps(components, indent=2),
            'hardware/instructions.md': '\n'.join(instructions)
        }
        
        return {
            'project_id': project_path.name,
            'files': files,
            'file_contents': file_contents,
            'mode': 'hardware',
            'description': analysis.get('description', prompt),
            'code': diagram,
            'diagram': diagram,
            'specs': specs,
            'components': components,
            'instructions': instructions
        }
    
    def _generate_hybrid(self, prompt: str, analysis: Dict, project_path: Path) -> Dict[str, Any]:
        """Generate hybrid hardware+software project with ALL real content"""
        
        # Generate both - software and hardware methods now write to their own subdirs
        software_result = self._generate_software(prompt, analysis, project_path)
        hardware_result = self._generate_hardware(prompt, analysis, project_path)
        
        files = software_result['files'] + hardware_result['files']
        
        # Combine file contents (already prefixed with software/ or hardware/)
        file_contents = {}
        for fname, content in software_result.get('file_contents', {}).items():
            file_contents[fname] = content
        for fname, content in hardware_result.get('file_contents', {}).items():
            file_contents[fname] = content
        
        # Combine all content
        code_content = f"// === SOFTWARE CODE ===\n{software_result.get('code', '')}\n\n// === HARDWARE DIAGRAM ===\n{hardware_result.get('diagram', '')}"
        specs_content = f"=== SOFTWARE SPECS ===\n{software_result.get('specs', '')}\n\n=== HARDWARE SPECS ===\n{hardware_result.get('specs', '')}"
        instructions = software_result.get('instructions', []) + hardware_result.get('instructions', [])
        components = hardware_result.get('components', [])
        diagram = hardware_result.get('diagram', '')
        
        return {
            'project_id': project_path.name,
            'files': files,
            'file_contents': file_contents,
            'mode': 'hybrid',
            'description': analysis.get('description', prompt),
            'code': code_content,
            'specs': specs_content,
            'diagram': diagram,
            'components': components,
            'instructions': instructions
        }
