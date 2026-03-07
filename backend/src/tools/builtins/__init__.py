"""
ProtoForge Built-in Tools
"""

import json
from typing import Any, Optional
from langchain_core.tools import BaseTool
from pydantic import Field


class PresentFilesTool(BaseTool):
    """Present generated files to user"""
    
    name: str = "present_files"
    description: str = """Make output files visible to the user.
Files must be in /mnt/user-data/outputs directory."""
    
    def _run(self, files: str) -> str:
        """Present files"""
        try:
            # Parse file list
            file_list = [f.strip() for f in files.split(",")]
            return json.dumps({"presented": file_list})
        except Exception as e:
            return f"Error: {str(e)}"


class AskClarificationTool(BaseTool):
    """Ask user for clarification"""
    
    name: str = "ask_clarification"
    description: str = """Ask the user for clarification when request is ambiguous.
Use this sparingly - only when truly needed."""
    
    def _run(self, question: str, options: Optional[str] = None) -> str:
        """Ask clarification"""
        response = {"question": question}
        if options:
            response["options"] = [o.strip() for o in options.split(",")]
        return json.dumps(response)


class ViewImageTool(BaseTool):
    """View an image"""
    
    name: str = "view_image"
    description: str = """View an image file and describe its contents.
Useful for understanding diagrams, screenshots, or visual designs."""
    
    def _run(self, path: str) -> str:
        """View image"""
        # Would load and describe image
        return f"Image at {path}: (would describe contents)"


class TaskTool(BaseTool):
    """Delegate to subagent"""
    
    name: str = "task"
    description: str = """Delegate a task to a subagent.
The subagent will execute in parallel and return results.
Useful for complex multi-step tasks."""
    
    def _run(
        self,
        description: str,
        prompt: str,
        subagent_type: str = "general-purpose",
        max_turns: int = 10
    ) -> str:
        """Submit task to subagent"""
        from src.subagents.executor import get_subagent_executor
        
        executor = get_subagent_executor()
        task_id = executor.submit(description, prompt, subagent_type)
        
        # Wait for result
        import time
        for _ in range(60):  # Wait up to 5 minutes
            task = executor.get_task(task_id)
            if task.status.value in ["completed", "failed", "timed_out"]:
                break
            time.sleep(5)
        
        task = executor.get_task(task_id)
        if task:
            if task.status.value == "completed":
                return task.result or "Task completed"
            else:
                return f"Task {task.status.value}: {task.error or 'No result'}"
        
        return "Task not found"


def get_builtin_tools() -> list[BaseTool]:
    """Get all built-in tools"""
    return [
        PresentFilesTool(),
        AskClarificationTool(),
        ViewImageTool(),
    ]


def get_subagent_tool() -> Optional[BaseTool]:
    """Get subagent tool"""
    return TaskTool()
