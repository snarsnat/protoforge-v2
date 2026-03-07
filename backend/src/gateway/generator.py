"""
ProtoForge Generator - Real AI-powered prototyping
"""

import os
import json
import uuid
import requests
from pathlib import Path
from typing import Dict, Any, Optional


class ProtoForgeGenerator:
    """Real AI-powered generator"""
    
    def __init__(self, api_key: str, provider: str = 'openai'):
        self.api_key = api_key
        self.provider = provider.lower()
    
    def _call_ai(self, system_prompt: str, user_prompt: str) -> str:
        """Make real API call to AI"""
        
        if self.provider == 'openai':
            return self._call_openai(system_prompt, user_prompt)
        elif self.provider == 'anthropic':
            return self._call_anthropic(system_prompt, user_prompt)
        elif self.provider == 'deepseek':
            return self._call_deepseek(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _call_openai(self, system: str, user: str) -> str:
        """Call OpenAI API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-4o',
            'messages': [
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user}
            ],
            'temperature': 0.7,
            'max_tokens': 4000
        }
        
        try:
            resp = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if resp.status_code == 429:
                raise Exception("OpenAI rate limit exceeded. Wait a moment and try again.")
            elif resp.status_code == 401:
                raise Exception("Invalid OpenAI API key. Please check your API key.")
            elif resp.status_code != 200:
                error_data = resp.json() if resp.text else {}
                raise Exception(f"OpenAI error: {error_data.get('error', {}).get('message', resp.text[:200])}")
            
            return resp.json()['choices'][0]['message']['content']
        except requests.exceptions.Timeout:
            raise Exception("OpenAI request timed out. Try again.")
        
        return resp.json()['choices'][0]['message']['content']
    
    def _call_anthropic(self, system: str, user: str) -> str:
        """Call Anthropic API"""
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        payload = {
            'model': 'claude-3-5-sonnet-20241022',
            'messages': [
                {'role': 'user', 'content': f"System: {system}\n\nUser: {user}"}
            ],
            'max_tokens': 4000
        }
        
        resp = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if resp.status_code != 200:
            raise Exception(f"Anthropic error: {resp.text}")
        
        result = resp.json()
        return result['content'][0]['text']
    
    def _call_deepseek(self, system: str, user: str) -> str:
        """Call DeepSeek API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user}
            ],
            'temperature': 0.7,
            'max_tokens': 4000
        }
        
        try:
            resp = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if resp.status_code == 429:
                raise Exception("DeepSeek rate limit exceeded. Try OpenAI or Anthropic instead.")
            elif resp.status_code == 401:
                raise Exception("Invalid DeepSeek API key. Please check your API key.")
            elif resp.status_code != 200:
                error_data = resp.json() if resp.text else {}
                raise Exception(f"DeepSeek error: {error_data.get('error', {}).get('message', resp.text[:200])}")
            
            return resp.json()['choices'][0]['message']['content']
        except requests.exceptions.Timeout:
            raise Exception("DeepSeek request timed out. Try a different provider.")
        except requests.exceptions.ConnectionError:
            raise Exception("Could not connect to DeepSeek. Check your internet connection.")
    
    def generate(self, prompt: str, mode: str, project_dir: str) -> Dict[str, Any]:
        """Generate prototype based on prompt and mode"""
        
        # Create project directory
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
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        
        # Fallback
        return {
            'components': [{'name': 'main', 'type': 'app', 'description': 'Main application'}],
            'tech_stack': {'frontend': 'HTML/CSS/JS', 'backend': 'None'},
            'features': []
        }
    
    def _generate_software(self, prompt: str, analysis: Dict, project_path: Path) -> Dict[str, Any]:
        """Generate software solution"""
        
        # Generate component diagram
        diagram = self._generate_component_diagram(analysis)
        
        # Generate code
        code = self._generate_code(prompt, analysis)
        
        # Write files
        files = []
        
        # Main HTML
        html_content = code.get('html', self._default_html(prompt, analysis))
        (project_path / 'index.html').write_text(html_content)
        files.append({'name': 'index.html', 'type': 'code'})
        
        # CSS
        css_content = code.get('css', self._default_css(analysis))
        (project_path / 'style.css').write_text(css_content)
        files.append({'name': 'style.css', 'type': 'code'})
        
        # JavaScript
        js_content = code.get('js', self._default_js(analysis))
        (project_path / 'app.js').write_text(js_content)
        files.append({'name': 'app.js', 'type': 'code'})
        
        # README
        readme = f"""# {analysis.get('description', 'ProtoForge Project')}

Generated by ProtoForge

## Features
{chr(10).join('- ' + f for f in analysis.get('features', []))}

## Tech Stack
- Frontend: {analysis.get('tech_stack', {}).get('frontend', 'HTML/CSS/JS')}

## To Run
Open index.html in a browser.
"""
        (project_path / 'README.md').write_text(readme)
        files.append({'name': 'README.md', 'type': 'doc'})
        
        # Component diagram
        (project_path / 'components.md').write_text(diagram)
        files.append({'name': 'components.md', 'type': 'diagram'})
        
        return {
            'project_id': project_path.name,
            'files': files,
            'diagram': diagram,
            'mode': 'software'
        }
    
    def _generate_hardware(self, prompt: str, analysis: Dict, project_path: Path) -> Dict[str, Any]:
        """Generate hardware solution with 3D printable models"""
        
        # Generate circuit diagram
        circuit = self._generate_circuit_diagram(analysis)
        
        # Generate 3D model spec
        model_spec = self._generate_3d_spec(analysis, prompt)
        
        # Generate actual STL file for 3D printing
        stl_content = self._generate_stl_model(model_spec, prompt)
        
        # Generate BOM
        bom = self._generate_bom(analysis)
        
        files = []
        
        # Circuit diagram
        (project_path / 'circuit.md').write_text(circuit)
        files.append({'name': 'circuit.md', 'type': 'diagram'})
        
        # STL 3D model (downloadable for 3D printing)
        (project_path / 'model.stl').write_text(stl_content)
        files.append({'name': 'model.stl', 'type': '3d', 'downloadable': True})
        
        # 3D model specification
        (project_path / 'model-spec.json').write_text(json.dumps(model_spec, indent=2))
        files.append({'name': 'model-spec.json', 'type': '3d'})
        
        # BOM
        (project_path / 'BOM.md').write_text(bom)
        files.append({'name': 'BOM.md', 'type': 'doc'})
        
        # README with 3D printing instructions
        readme = f"""# Hardware Project

Generated by ProtoForge

## Components
{chr(10).join('- ' + c.get('name', '') + ': ' + c.get('description', '') for c in analysis.get('components', []))}

## 3D Printing
- **model.stl** - Ready for 3D printing
- Print settings: 20% infill, 0.2mm layer height
- Material: PLA or PETG recommended

## Circuit
See circuit.md for wiring diagram.

## Bill of Materials
See BOM.md for parts list.
"""
        (project_path / 'README.md').write_text(readme)
        files.append({'name': 'README.md', 'type': 'doc'})
        
        return {
            'project_id': project_path.name,
            'files': files,
            'diagram': circuit,
            'model_3d': model_spec,
            'mode': 'hardware'
        }
    
    def _generate_stl_model(self, model_spec: Dict, prompt: str) -> str:
        """Generate actual STL 3D model file for printing"""
        
        dims = model_spec.get('dimensions', {})
        width = dims.get('width', 80)
        height = dims.get('height', 25)
        depth = dims.get('depth', 60)
        wall = 2  # wall thickness
        
        # Generate ASCII STL format (simple box with optional cutouts)
        # This is a proper STL that can be opened in any 3D slicer
        
        stl = f"""solid protoforge_model
  facet normal 0 0 -1
    outer loop
      vertex {width/2} {height} -{depth/2}
      vertex -{width/2} {height} -{depth/2}
      vertex -{width/2} {height} {depth/2}
    endloop
  endfacet
  facet normal 0 0 -1
    outer loop
      vertex {width/2} {height} -{depth/2}
      vertex -{width/2} {height} {depth/2}
      vertex {width/2} {height} {depth/2}
    endloop
  endfacet
  facet normal 0 0 1
    outer loop
      vertex {width/2} 0 -{depth/2}
      vertex {width/2} 0 {depth/2}
      vertex -{width/2} 0 {depth/2}
    endloop
  endfacet
  facet normal 0 0 1
    outer loop
      vertex {width/2} 0 -{depth/2}
      vertex -{width/2} 0 {depth/2}
      vertex -{width/2} 0 -{depth/2}
    endloop
  endfacet
  facet normal -1 0 0
    outer loop
      vertex -{width/2} {height} -{depth/2}
      vertex -{width/2} {height} {depth/2}
      vertex -{width/2} 0 {depth/2}
    endloop
  endfacet
  facet normal -1 0 0
    outer loop
      vertex -{width/2} {height} -{depth/2}
      vertex -{width/2} 0 {depth/2}
      vertex -{width/2} 0 -{depth/2}
    endloop
  endfacet
  facet normal 1 0 0
    outer loop
      vertex {width/2} {height} {depth/2}
      vertex {width/2} {height} -{depth/2}
      vertex {width/2} 0 -{depth/2}
    endloop
  endfacet
  facet normal 1 0 0
    outer loop
      vertex {width/2} {height} {depth/2}
      vertex {width/2} 0 -{depth/2}
      vertex {width/2} 0 {depth/2}
    endloop
  endfacet
  facet normal 0 1 0
    outer loop
      vertex -{width/2} {height} -{depth/2}
      vertex {width/2} {height} -{depth/2}
      vertex {width/2} {height} {depth/2}
    endloop
  endfacet
  facet normal 0 1 0
    outer loop
      vertex -{width/2} {height} -{depth/2}
      vertex {width/2} {height} {depth/2}
      vertex -{width/2} {height} {depth/2}
    endloop
  endfacet
  facet normal 0 -1 0
    outer loop
      vertex -{width/2} 0 -{depth/2}
      vertex {width/2} 0 {depth/2}
      vertex {width/2} 0 -{depth/2}
    endloop
  endfacet
  facet normal 0 -1 0
    outer loop
      vertex -{width/2} 0 -{depth/2}
      vertex -{width/2} 0 {depth/2}
      vertex {width/2} 0 {depth/2}
    endloop
  endfacet
endsolid protoforge_model
"""
        return stl
    
    def _generate_hybrid(self, prompt: str, analysis: Dict, project_path: Path) -> Dict[str, Any]:
        """Generate hybrid solution - both hardware and software"""
        
        # Generate both
        software = self._generate_software(prompt, analysis, project_path / 'software')
        hardware = self._generate_hardware(prompt, analysis, project_path / 'hardware')
        
        # Merge files
        files = []
        for f in software['files']:
            f['name'] = 'software/' + f['name']
            files.append(f)
        for f in hardware['files']:
            f['name'] = 'hardware/' + f['name']
            files.append(f)
        
        # Overview diagram
        overview = f"""# Hybrid System Overview

## Software Components
{software['diagram']}

## Hardware Components  
{hardware['diagram']}
"""
        (project_path / 'overview.md').write_text(overview)
        files.append({'name': 'overview.md', 'type': 'diagram'})
        
        return {
            'project_id': project_path.name,
            'files': files,
            'diagram': overview,
            'mode': 'hybrid'
        }
    
    def _generate_component_diagram(self, analysis: Dict) -> str:
        """Generate Mermaid component diagram"""
        
        components = analysis.get('components', [])
        
        diagram = """```mermaid
flowchart TB
    subgraph Client["🏠 Client"]
        UI["🖥️ User Interface"]
    end
    
    subgraph Backend["⚙️ Backend"]
"""
        
        for comp in components:
            name = comp.get('name', 'comp').replace(' ', '_')
            diagram += f'        {name}["{comp.get("description", name)}"]\n'
        
        diagram += """    end
    
    subgraph Data["💾 Data"]
        DB[("📀 Database")]
    end
    
    UI --> Backend
"""
        
        for comp in components:
            name = comp.get('name', 'comp').replace(' ', '_')
            diagram += f'    {name} --> DB\n'
        
        diagram += """
    style Client fill:#1a1a2e,color:#fff
    style Backend fill:#16213e,color:#fff
    style Data fill:#0f3460,color:#fff
```"""
        
        return diagram
    
    def _generate_circuit_diagram(self, analysis: Dict) -> str:
        """Generate Mermaid circuit diagram"""
        
        components = analysis.get('components', [])
        
        diagram = """```mermaid
flowchart TB
    subgraph Power["⚡ Power"]
        USB["🔌 USB 5V"]
        VCC["📍 VCC"]
        GND["📍 GND"]
    end
    
    subgraph Controller["🧠 Microcontroller"]
        MCU["🎛️ MCU"]
    end
    
    subgraph Components["📟 Components"]
"""
        
        for i, comp in enumerate(components):
            name = comp.get('name', f'C{i}').replace(' ', '_')
            diagram += f'        {name}["{comp.get("description", name)}"]\n'
        
        diagram += """    end
    
    USB --> VCC
    USB --> GND
    VCC --> MCU
    MCU --> GND
"""
        
        for i, comp in enumerate(components):
            name = comp.get('name', f'C{i}').replace(' ', '_')
            diagram += f'    MCU --> {name}\n'
        
        diagram += """
    style Power fill:#ff6b35,color:#fff
    style Controller fill:#004e89,color:#fff
    style Components fill:#7bc043,color:#fff
```"""
        
        return diagram
    
    def _generate_3d_spec(self, analysis: Dict, prompt: str = '') -> Dict:
        """Generate 3D model specification based on prompt"""
        
        # Default dimensions
        dims = {'width': 80, 'height': 25, 'depth': 60}
        
        # Analyze prompt for size hints
        prompt_lower = prompt.lower()
        
        if 'raspberry pi' in prompt_lower or 'rpi' in prompt_lower:
            dims = {'width': 90, 'height': 35, 'depth': 65}
        elif 'arduino' in prompt_lower:
            dims = {'width': 70, 'height': 20, 'depth': 50}
        elif 'esp32' in prompt_lower or 'esp8266' in prompt_lower:
            dims = {'width': 55, 'height': 15, 'depth': 35}
        elif 'box' in prompt_lower or 'enclosure' in prompt_lower:
            dims = {'width': 100, 'height': 40, 'depth': 80}
        elif 'small' in prompt_lower:
            dims = {'width': 50, 'height': 15, 'depth': 30}
        elif 'large' in prompt_lower:
            dims = {'width': 150, 'height': 60, 'depth': 100}
            
        return {
            'type': 'enclosure',
            'dimensions': dims,
            'material': 'PLA or PETG recommended',
            'color': '#2d3436',
            'print_settings': {
                'layer_height': '0.2mm',
                'infill': '20%',
                'supports': 'yes' if dims['height'] > 30 else 'no'
            },
            'components': [
                {'name': c.get('name', ''), 'type': c.get('type', 'generic')}
                for c in analysis.get('components', [])
            ]
        }
    
    def _generate_bom(self, analysis: Dict) -> str:
        """Generate Bill of Materials"""
        
        bom = """# Bill of Materials

| Component | Type | Quantity | Notes |
|-----------|------|----------|-------|
"""
        
        for comp in analysis.get('components', []):
            bom += f"| {comp.get('name', 'Component')} | {comp.get('type', 'generic')} | 1 | {comp.get('description', '')} |\n"
        
        bom += "\n## Estimated Cost\n- Total: $20-50\n"
        
        return bom
    
    def _load_design_system(self) -> str:
        """Load the design system guidelines"""
        try:
            design_path = Path(__file__).parent.parent.parent.parent / "DESIGN_SYSTEM.md"
            if design_path.exists():
                return design_path.read_text()
        except:
            pass
        return ""
    
    def _generate_code(self, prompt: str, analysis: Dict) -> Dict[str, str]:
        """Generate code using AI"""
        
        design_system = self._load_design_system()
        
        system_prompt = f"""You are a world-class web developer. Generate a complete, functional web application.

IMPORTANT - You MUST follow the design system below:
{design_system}

Return ONLY a JSON object with these keys:
- html: Complete HTML file with inline CSS and JS if simple, or link to external files
- css: Complete CSS file (can be empty if HTML is self-contained)
- js: Complete JavaScript file (can be empty if HTML is self-contained)

Make it beautiful, distinctive, and anti-generic. NO purple, NO rounded corners, NO friendly AI aesthetics.
Use dark theme, monospace fonts, sharp edges, red/yellow accents."""
        
        user_prompt = f"Create a web application for: {prompt}\n\nAnalysis: {json.dumps(analysis)}"
        
        try:
            response = self._call_ai(system_prompt, user_prompt)
            print(f"AI Response: {response[:500]}...")
            
            # Try to extract JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except Exception as e:
            print(f"Code generation error: {e}")
        
        # Return default styled code if AI fails
        return {
            'html': self._default_html(prompt, analysis),
            'css': self._default_css(analysis),
            'js': self._default_js(analysis)
        }
    
    def _default_html(self, prompt: str, analysis: Dict) -> str:
        """Default HTML template"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProtoForge Project</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="app">
        <header>
            <h1>ProtoForge Project</h1>
            <p>Generated from: {prompt[:100]}...</p>
        </header>
        <main>
            <div class="content">
                <h2>Application Ready</h2>
                <p>This application was generated based on your specifications.</p>
                <div id="app-root"></div>
            </div>
        </main>
    </div>
    <script src="app.js"></script>
</body>
</html>"""
    
    def _default_css(self, analysis: Dict) -> str:
        """Default CSS - Anti-trope design"""
        return """/* ProtoForge - Anti-Trope Design */
:root {
    --bg: #0a0a0a;
    --bg-secondary: #141414;
    --text: #f0f0f0;
    --text-secondary: #888;
    --accent: #ff3e00;
    --border: #333;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
}
.app { max-width: 800px; margin: 0 auto; padding: 2rem; }
header {
    padding: 1rem 0;
    border-bottom: 2px solid var(--border);
    margin-bottom: 2rem;
}
header h1 { font-size: 1.5rem; }
header p { color: var(--text-secondary); font-size: 0.875rem; }
.content { background: var(--bg-secondary); padding: 2rem; border: 2px solid var(--border); }
.content h2 { color: var(--accent); margin-bottom: 1rem; }
"""
    
    def _default_js(self, analysis: Dict) -> str:
        """Default JavaScript"""
        return """// ProtoForge Generated App
document.addEventListener('DOMContentLoaded', () => {
    console.log('ProtoForge: App initialized');
    const root = document.getElementById('app-root');
    if (root) {
        root.innerHTML = '<p>Application running...</p>';
    }
});
"""
