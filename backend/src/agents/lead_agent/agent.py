"""
ProtoForge Lead Agent
"""

from typing import Any, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent

from src.models.factory import ModelFactory
from src.config import get_config
from src.skills import get_skills_loader
from src.agents.memory import get_memory_system
from src.sandbox.tools import get_sandbox_tools
from src.tools.builtins import get_builtin_tools, get_subagent_tool
from src.community import get_community_tools
from src.subagents.executor import get_subagent_executor


def create_system_prompt() -> str:
    """Create system prompt with skills and memory"""
    
    config = get_config()
    
    # Get skills
    skills_loader = get_skills_loader(config.skills.path)
    skills_loader.load_skills()
    skills_prompt = skills_loader.get_skill_prompt_injection()
    
    # Get memory
    memory_system = get_memory_system()
    memory_prompt = ""
    if memory_system:
        memory_prompt = memory_system.get_injection_prompt()
    
    # Base prompt
    prompt = """You are ProtoForge, an AI-powered prototyping assistant.

Your role is to help users create:
1. **Software** - Generate code, web apps, APIs, and component diagrams
2. **Hardware** - Design circuits, generate wiring diagrams, specify components
3. **Hybrid** - Combined hardware+software systems

You have access to:
- A sandbox environment for code execution
- File operations (read, write, list)
- Web search and fetch tools
- Subagent delegation for parallel tasks
- Skills that provide specialized capabilities

## Working Directory
- Workspace: /mnt/user-data/workspace
- Uploads: /mnt/user-data/uploads  
- Outputs: /mnt/user-data/outputs

## Guidelines
- Always plan before executing complex tasks
- Use subagents for parallel execution when appropriate
- Present final outputs to the user using present_files
- Ask for clarification when needed
- Be precise and practical in your responses
"""
    
    # Add skills
    if skills_prompt:
        prompt += skills_prompt
    
    # Add memory
    if memory_prompt:
        prompt += memory_prompt
    
    return prompt


def make_lead_agent(config: Optional[RunnableConfig] = None) -> Any:
    """Create the lead agent"""
    
    # Get LLM
    model_name = config.get("configurable", {}).get("model_name") if config else None
    thinking_enabled = config.get("configurable", {}).get("thinking_enabled", False) if config else False
    
    if model_name:
        llm = ModelFactory.create_chat_model(model_name, thinking_enabled)
    else:
        llm = ModelFactory.get_default_model()
    
    # Gather tools
    tools = []
    
    # Sandbox tools
    tools.extend(get_sandbox_tools())
    
    # Built-in tools
    tools.extend(get_builtin_tools())
    
    # Community tools
    tools.extend(get_community_tools())
    
    # Subagent tool (if enabled)
    app_config = get_config()
    if app_config.subagents.enabled:
        subagent_tool = get_subagent_tool()
        if subagent_tool:
            tools.append(subagent_tool)
    
    # Create agent
    system_prompt = create_system_prompt()
    
    agent = create_react_agent(
        llm,
        tools=tools,
        state_modifier=system_prompt,
        prompt=system_prompt
    )
    
    return agent


def invoke_agent(
    agent: Any,
    message: str,
    thread_id: str = "default",
    **kwargs
) -> dict[str, Any]:
    """Invoke the agent with a message"""
    
    config = RunnableConfig(
        configurable={
            "thread_id": thread_id,
            **kwargs
        }
    )
    
    result = agent.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config
    )
    
    return result
