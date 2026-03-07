"""
ProtoForge Gateway API
"""

import os
import json
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    name: str
    enabled: bool


class MCPConfig(BaseModel):
    mcpServers: dict


# Routes
@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "service": "protoforge-gateway"}


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
