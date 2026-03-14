"""
ProtoForge Gateway API
"""

import os
import json
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from src.config import get_config, reload_config
from src.models.factory import ModelFactory
from src.skills import get_skills_loader
from src.mcp import get_mcp_manager
from src.agents.memory import get_memory_system, init_memory_system


app = FastAPI(title="ProtoForge Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = "default"
    model_name: Optional[str] = None


class ModelUpdate(BaseModel):
    name: str
    enabled: bool


class SkillUpdate(BaseModel):
    enabled: bool


class MCPConfig(BaseModel):
    mcpServers: dict


class GenerateRequest(BaseModel):
    prompt: str
    mode: str = "software"  # software, hardware, hybrid
    api_key: str
    provider: str = "openai"


class DepositRequest(BaseModel):
    user_id: str
    amount: float


class TestApiRequest(BaseModel):
    api_key: str
    provider: str = "openai"


class AutoDetectRequest(BaseModel):
    api_key: str
    provider: str = "openai"


# Routes
@app.get("/")
async def root():
    """Root endpoint - Serve UI"""
    from pathlib import Path
    template_path = Path(__file__).parent / "templates" / "index.html"
    if template_path.exists():
        from fastapi.responses import FileResponse
        return FileResponse(template_path)
    return {
        "service": "ProtoForge Gateway",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "models": "/api/models",
            "skills": "/api/skills",
            "memory": "/api/memory",
            "mcp": "/api/mcp/config",
            "uploads": "/api/threads/{id}/uploads"
        }
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "service": "protoforge-gateway"}


@app.post("/api/test")
async def test_api(request: TestApiRequest):
    """Test an API key with a simple request"""
    from src.gateway.generator import ProtoForgeGenerator, PROVIDERS
    
    try:
        generator = ProtoForgeGenerator(
            api_key=request.api_key,
            provider=request.provider
        )
        
        # Get the model from config
        model_name = generator.config.get('model', 'unknown')
        
        # Make a simple test call
        response = generator._call_ai(
            system_prompt="You are a helpful assistant. Reply with 'OK' if you understand.",
            user_prompt="Say OK"
        )
        
        return {
            "success": True,
            "provider": request.provider,
            "model": model_name,
            "response": response[:100]
        }
    except Exception as e:
        return {
            "success": False,
            "provider": request.provider,
            "error": str(e)
        }


@app.post("/api/auto-detect")
async def auto_detect_model(request: AutoDetectRequest):
    """Auto-detect the best free tier model for a provider"""
    from src.gateway.generator import ProtoForgeGenerator, PROVIDERS
    
    # Free tier models to try for each provider
    FREE_MODELS = {
        "groq": ["llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        "together": ["meta-llama/Llama-3.2-3B-Instruct", "meta-llama/Llama-3-8B-Instruct"],
        "siliconflow": ["deepseek-ai/DeepSeek-V2.5", "Qwen/Qwen2.5-7B-Instruct"],
        "deepseek": ["deepseek-chat"],
        "zhipu": ["glm-4-flash"],
        "qwen": ["qwen-turbo", "qwen2.5-7b-instruct"],
        "kimi": ["moonshot-v1-8k"],
        "minimax": ["abab6.5s-chat", "abab6-chat"],
        "volcengine": ["doubao-lite-4k"],
        "openai": ["gpt-3.5-turbo"],
        "anthropic": ["claude-instant-1.2"],
        "ollama": ["llama3.2", "qwen2.5"],
    }
    
    provider = request.provider.lower()
    models_to_try = FREE_MODELS.get(provider, [])
    
    if not models_to_try:
        return {
            "success": False,
            "error": f"No free tier models known for provider: {provider}"
        }
    
    for model in models_to_try:
        try:
            generator = ProtoForgeGenerator(
                api_key=request.api_key,
                provider=provider
            )
            
            # Temporarily override the model
            original_model = generator.config.get('model')
            generator.config['model'] = model
            
            response = generator._call_ai(
                system_prompt="Reply with only 'OK'",
                user_prompt="Say OK"
            )
            
            # Restore original model
            if original_model:
                generator.config['model'] = original_model
            
            return {
                "success": True,
                "provider": provider,
                "model": model,
                "message": f"Found working model: {model}"
            }
            
        except Exception as e:
            # Try next model
            continue
    
    return {
        "success": False,
        "error": "No free tier models worked. Check your API key or try a different provider."
    }


@app.get("/api/models")
async def list_models():
    """List available models"""
    models = ModelFactory.list_models()
    return {"models": models}


@app.get("/api/models/{name}")
async def get_model(name: str):
    """Get model details"""
    config = get_config()
    for m in config.models:
        if m.name == name:
            return {
                "name": m.name,
                "display_name": m.display_name,
                "supports_thinking": m.supports_thinking,
                "supports_vision": m.supports_vision,
            }
    raise HTTPException(status_code=404, detail="Model not found")


@app.get("/api/skills")
async def list_skills():
    """List available skills"""
    config = get_config()
    loader = get_skills_loader(config.skills.path)
    skills = loader.load_skills()
    
    return {
        "skills": [
            {
                "name": s.name,
                "description": s.description,
                "enabled": s.enabled,
                "path": s.path
            }
            for s in skills.values()
        ]
    }


@app.put("/api/skills/{name}")
async def update_skill(name: str, update: SkillUpdate):
    """Update skill enabled state"""
    config = get_config()
    loader = get_skills_loader(config.skills.path)
    loader.load_skills()
    
    if update.enabled:
        loader.enable_skill(name)
    else:
        loader.disable_skill(name)
    
    return {"success": True, "name": name, "enabled": update.enabled}


@app.get("/api/mcp/config")
async def get_mcp_config():
    """Get MCP configuration"""
    manager = get_mcp_manager()
    return manager.get_config_dict()


@app.put("/api/mcp/config")
async def update_mcp_config(config: MCPConfig):
    """Update MCP configuration"""
    manager = get_mcp_manager()
    manager.load_config(config.dict())
    
    # Save to extensions config
    extensions_path = Path("extensions_config.json")
    if extensions_path.exists():
        extensions = json.loads(extensions_path.read_text())
    else:
        extensions = {}
    
    extensions["mcpServers"] = config.mcpServers
    extensions_path.write_text(json.dumps(extensions, indent=2))
    
    return {"success": True}


@app.get("/api/memory")
async def get_memory():
    """Get memory data"""
    memory = get_memory_system()
    if not memory:
        return {"error": "Memory not enabled"}
    return memory.store.get_all()


@app.get("/api/memory/status")
async def get_memory_status():
    """Get memory status"""
    memory = get_memory_system()
    if not memory:
        return {"enabled": False}
    return memory.get_status()


@app.post("/api/memory/reload")
async def reload_memory():
    """Reload memory"""
    # Would reload from disk
    return {"success": True}


@app.post("/api/test-key")
async def test_api_key(request: TestApiRequest):
    """Test if an API key works"""
    try:
        from src.gateway.generator import ProtoForgeGenerator
        
        generator = ProtoForgeGenerator(
            api_key=request.api_key,
            provider=request.provider
        )
        
        # Try a simple call
        response = generator._call_ai(
            system_prompt="You are a helpful assistant. Reply with just 'OK' if you understand.",
            user_prompt="Reply with 'OK'"
        )
        
        if "ok" in response.lower():
            return {"success": True, "message": "API key works!", "response": response[:100]}
        else:
            return {"success": True, "message": "API key accepted but response unexpected", "response": response[:100]}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/generate")
async def generate(request: GenerateRequest):
    """Generate a prototype using AI"""
    import traceback
    try:
        from src.gateway.generator import ProtoForgeGenerator
        
        print(f"Generating: mode={request.mode}, provider={request.provider}")
        print(f"Prompt: {request.prompt[:100]}...")
        
        # Create generator
        generator = ProtoForgeGenerator(
            api_key=request.api_key,
            provider=request.provider
        )
        
        # Generate
        import os
        result = generator.generate(
            prompt=request.prompt,
            mode=request.mode,
            project_dir=os.path.join(os.path.dirname(__file__), "../../data/projects")
        )
        
        print(f"Generated {len(result.get('files', []))} files")
        return result
        
    except Exception as e:
        print(f"Generate error: {e}")
        traceback.print_exc()
        return {"error": str(e), "files": [], "mode": request.mode}


@app.get("/api/preview/{project_id}")
async def preview_project(project_id: str):
    """Serve HTML preview of generated project"""
    from fastapi.responses import HTMLResponse, FileResponse
    from pathlib import Path
    
    project_dir = Path(__file__).parent / "../../data/projects" / project_id
    
    # Try to find index.html
    index_path = project_dir / "index.html"
    if not index_path.exists():
        # Try subdirectories for hybrid projects
        software_dir = project_dir / "software"
        if software_dir.exists():
            index_path = software_dir / "index.html"
    
    if not index_path.exists():
        return HTMLResponse("<html><body><h1>No preview available</h1><p>Project files not found.</p></body></html>", status_code=404)
    
    return FileResponse(index_path, media_type="text/html")


@app.get("/api/download/{project_id}")
async def download_project(project_id: str):
    """Download project as ZIP file"""
    import zipfile
    from io import BytesIO
    
    project_dir = Path(__file__).parent / "../../data/projects" / project_id
    
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create ZIP in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Walk through project directory
        for file_path in project_dir.rglob('*'):
            if file_path.is_file():
                # Calculate relative path for ZIP
                arcname = file_path.relative_to(project_dir)
                zip_file.write(file_path, arcname)
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={project_id}.zip"}
    )


@app.post("/api/threads/{thread_id}/uploads")
async def upload_files(thread_id: str, files: list[UploadFile] = File(...)):
    """Upload files to thread"""
    upload_dir = Path(f"./data/threads/{thread_id}/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    uploaded = []
    for file in files:
        content = await file.read()
        file_path = upload_dir / file.filename
        file_path.write_bytes(content)
        uploaded.append(file.filename)
    
    return {"success": True, "files": uploaded}


@app.get("/api/threads/{thread_id}/uploads/list")
async def list_uploads(thread_id: str):
    """List uploaded files"""
    upload_dir = Path(f"./data/threads/{thread_id}/uploads")
    if not upload_dir.exists():
        return {"files": [], "count": 0}
    
    files = [f.name for f in upload_dir.iterdir() if f.is_file()]
    return {"files": files, "count": len(files)}


@app.get("/api/threads/{thread_id}/artifacts/{path:path}")
async def get_artifact(thread_id: str, path: str, download: bool = False):
    """Get artifact file"""
    artifact_path = Path(f"./data/threads/{thread_id}/outputs/{path}")
    if not artifact_path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    content = artifact_path.read_bytes()
    
    from fastapi.responses import Response
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={path}"}
        if download else {}
    )


def init_app():
    """Initialize application"""
    # Load config
    config = get_config()
    
    # Initialize memory
    if config.memory.enabled:
        init_memory_system(
            storage_path=config.memory.storage_path,
            enabled=config.memory.enabled,
            injection_enabled=config.memory.injection_enabled,
            max_facts=config.memory.max_facts,
            fact_confidence_threshold=config.memory.fact_confidence_threshold,
            max_injection_tokens=config.memory.max_injection_tokens
        )
    
    # Load MCP config
    extensions_path = Path("extensions_config.json")
    if extensions_path.exists():
        extensions = json.loads(extensions_path.read_text())
        mcp_manager = get_mcp_manager()
        mcp_manager.load_config(extensions)


if __name__ == "__main__":
    import uvicorn
    init_app()
    uvicorn.run(app, host="0.0.0.0", port=8001)
