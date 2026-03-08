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
from src.gateway.credits import CreditSystem


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


class CreditCheckRequest(BaseModel):
    user_id: str
    mode: str = "software"


# Initialize credit system
credit_system = CreditSystem(data_dir="./data")


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
        result = generator.generate(
            prompt=request.prompt,
            mode=request.mode,
            project_dir="./data/projects"
        )
        
        print(f"Generated {len(result.get('files', []))} files")
        return result
        
    except Exception as e:
        print(f"Generate error: {e}")
        traceback.print_exc()
        return {"error": str(e), "files": [], "mode": request.mode}


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


# Credit System Routes
@app.post("/api/credits/deposit")
async def deposit_credits(request: DepositRequest):
    """Deposit credits into user account"""
    result = credit_system.deposit(request.user_id, request.amount)
    return result


@app.get("/api/credits/balance/{user_id}")
async def get_balance(user_id: str):
    """Get user's credit balance"""
    balance = credit_system.get_balance(user_id)
    return {
        "balance": balance['balance'],
        "deposited": balance['deposited'],
        "prompts_used": balance['prompts_used'],
        "free_prompts_remaining": balance.get('prompts_free', 0)
    }


@app.post("/api/credits/check")
async def check_credits(request: CreditCheckRequest):
    """Check if user can make a prompt"""
    can_prompt, message = credit_system.can_prompt(request.user_id, request.mode)
    cost = credit_system.get_cost(request.mode)
    return {
        "can_prompt": can_prompt,
        "message": message,
        "cost": cost,
        "mode": request.mode
    }


@app.post("/api/credits/use")
async def use_credits(request: CreditCheckRequest):
    """Use a prompt (deduct credits)"""
    result = credit_system.use_prompt(request.user_id, request.mode)
    return result


# Generation endpoint with credit check
@app.post("/api/generate")
async def generate_with_credits(request: GenerateRequest):
    """Generate prototype with credit system"""
    user_id = request.api_key[:8]  # Use API key prefix as user ID
    
    # Check credits first
    can_prompt, message = credit_system.can_prompt(user_id, request.mode)
    if not can_prompt:
        raise HTTPException(status_code=402, detail=message)
    
    # Use the prompt (deduct credits)
    credit_result = credit_system.use_prompt(user_id, request.mode)
    
    # Proceed with generation (import here to avoid circular imports)
    from src.gateway.generator import ProtoForgeGenerator
    
    generator = ProtoForgeGenerator(
        api_key=request.api_key,
        provider=request.provider
    )
    
    try:
        result = generator.generate(
            prompt=request.prompt,
            mode=request.mode,
            project_dir="./data/projects"
        )
        
        # Add credit info to response
        result['credits'] = credit_result
        return result
        
    except Exception as e:
        # Refund credits on failure
        if credit_result['type'] == 'paid':
            credit_system.deposit(user_id, credit_result['cost'])
        raise HTTPException(status_code=500, detail=str(e))


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
