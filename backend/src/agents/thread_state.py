"""
ProtoForge Thread State
"""

from typing import Annotated, Any, Optional
from pydantic import BaseModel, Field
from langgraph.graph import add_messages


class ThreadData(BaseModel):
    """Thread-specific data"""
    thread_id: str = ""
    workspace_dir: str = ""
    uploads_dir: str = ""
    outputs_dir: str = ""


class Artifact(BaseModel):
    """Generated artifact"""
    path: str
    mime_type: str = "text/plain"


class Todo(BaseModel):
    """Todo item"""
    id: str
    content: str
    status: str = "pending"  # pending, in_progress, completed


class AgentState(BaseModel):
    """Main agent state"""
    
    # Messages (with reducer for accumulation)
    messages: Annotated[list[Any], add_messages] = Field(default_factory=list)
    
    # Thread data
    thread_id: Optional[str] = None
    thread_data: Optional[ThreadData] = None
    
    # Title
    title: Optional[str] = None
    
    # Artifacts (generated files)
    artifacts: list[Artifact] = Field(default_factory=list)
    
    # Todo list (for plan mode)
    todos: list[Todo] = Field(default_factory=list)
    
    # Uploaded files
    uploaded_files: list[str] = Field(default_factory=list)
    
    # Viewed images
    viewed_images: list[str] = Field(default_factory=list)
    
    # Sandbox ID
    sandbox_id: Optional[str] = None
    
    # Configurable options
    thinking_enabled: bool = False
    model_name: Optional[str] = None
    is_plan_mode: bool = False
    
    class Config:
        """Pydantic config"""
        arbitrary_types_allowed = True


def merge_artifacts(left: list[Artifact], right: list[Artifact]) -> list[Artifact]:
    """Merge artifacts, deduplicating by path"""
    seen = set()
    merged = []
    for artifact in left + right:
        if artifact.path not in seen:
            seen.add(artifact.path)
            merged.append(artifact)
    return merged


def merge_viewed_images(
    left: list[str], 
    right: list[str]
) -> list[str]:
    """Merge viewed images, keeping recent"""
    if not right:
        return left
    return right[-10:]  # Keep last 10
