"""
AgentStack Core — Production-Ready Agent Runtime
Built by ArQon Agentics
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import json
import time
from enum import Enum


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETE = "complete"


@dataclass
class ToolCall:
    """Represents a tool call made by an agent."""
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Any] = None
    timestamp: float = field(default_factory=time.time)
    duration_ms: Optional[float] = None
    error: Optional[str] = None


@dataclass
class AgentStep:
    """A single step in an agent's execution."""
    thought: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    observation: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class AgentResult:
    """Result of an agent's execution."""
    output: str
    steps: List[AgentStep]
    tokens_used: int = 0
    cost_usd: float = 0.0
    duration_ms: float = 0.0
    status: AgentStatus = AgentStatus.COMPLETE
    error: Optional[str] = None


class Memory(ABC):
    """Abstract base class for agent memory systems."""
    
    @abstractmethod
    async def store(self, key: str, value: Any) -> None:
        """Store a value in memory."""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value from memory."""
        pass
    
    @abstractmethod
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memory for relevant context."""
        pass


class InMemoryMemory(Memory):
    """Simple in-memory storage for development/testing."""
    
    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._vectors: List[Dict[str, Any]] = []
    
    async def store(self, key: str, value: Any) -> None:
        self._store[key] = value
    
    async def retrieve(self, key: str) -> Optional[Any]:
        return self._store.get(key)
    
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        # Simple keyword search for demo
        results = []
        for key, value in self._store.items():
            if query.lower() in str(value).lower():
                results.append({"key": key, "value": value, "score": 1.0})
        return results[:limit]


class Tool(ABC):
    """Abstract base class for agent tools."""
    
    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass


class Agent:
    """
    Core agent class with memory, tools, and observability.
    
    Example:
        agent = Agent(
            name="researcher",
            system_prompt="You are a research assistant.",
            tools=[WebSearchTool(), DocumentReaderTool()],
            memory=InMemoryMemory()
        )
        result = await agent.run("Find recent papers on multi-agent systems")
    """
    
    def __init__(
        self,
        name: str,
        system_prompt: str = "",
        tools: Optional[List[Tool]] = None,
        memory: Optional[Memory] = None,
        max_steps: int = 10,
        model: str = "claude-sonnet-4"
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = {t.name: t for t in (tools or [])}
        self.memory = memory or InMemoryMemory()
        self.max_steps = max_steps
        self.model = model
        self.status = AgentStatus.IDLE
        self._history: List[AgentStep] = []
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get JSON schemas for all available tools."""
        schemas = []
        for name, tool in self.tools.items():
            schemas.append({
                "name": name,
                "description": tool.description,
                "parameters": tool.parameters
            })
        return schemas
    
    async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """
        Execute the agent on a given task.
        
        This is a simplified version. Production implementation would:
        - Call actual LLM API (OpenAI, Anthropic, etc.)
        - Parse tool calls from LLM response
        - Handle retries and error recovery
        - Track token usage and costs
        """
        start_time = time.time()
        self.status = AgentStatus.RUNNING
        self._history = []
        
        try:
            # Retrieve relevant context from memory
            memory_context = await self.memory.search(task, limit=3)
            
            # Build the full prompt
            prompt = self._build_prompt(task, memory_context, context)
            
            # In production, this would call the LLM
            # For now, simulate execution
            step = AgentStep(
                thought=f"Processing task: {task}",
                observation="Task processed successfully (simulated)"
            )
            self._history.append(step)
            
            # Store result in memory
            await self.memory.store(f"task_{int(time.time())}", {
                "task": task,
                "result": "Simulated result",
                "timestamp": time.time()
            })
            
            duration_ms = (time.time() - start_time) * 1000
            self.status = AgentStatus.COMPLETE
            
            return AgentResult(
                output="Simulated agent output. In production, this would be the LLM response.",
                steps=self._history,
                duration_ms=duration_ms
            )
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            return AgentResult(
                output="",
                steps=self._history,
                error=str(e),
                status=AgentStatus.ERROR
            )
    
    def _build_prompt(
        self,
        task: str,
        memory_context: List[Dict[str, Any]],
        extra_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build the full prompt for the LLM."""
        parts = [self.system_prompt, "\n\n"]
        
        # Add tool descriptions
        if self.tools:
            parts.append("Available tools:\n")
            for schema in self.get_tool_schemas():
                parts.append(f"- {schema['name']}: {schema['description']}\n")
            parts.append("\n")
        
        # Add memory context
        if memory_context:
            parts.append("Relevant context:\n")
            for item in memory_context:
                parts.append(f"- {item['key']}: {item['value']}\n")
            parts.append("\n")
        
        # Add extra context
        if extra_context:
            parts.append("Additional context:\n")
            parts.append(json.dumps(extra_context, indent=2))
            parts.append("\n\n")
        
        # Add the task
        parts.append(f"Task: {task}")
        
        return "".join(parts)


class Workflow:
    """
    Multi-agent workflow orchestrator.
    
    Example:
        workflow = Workflow()
        workflow.add_step(agent_a, task="research")
        workflow.add_step(agent_b, task="write", depends_on=["research"])
        results = await workflow.run()
    """
    
    def __init__(self):
        self.steps: List[Dict[str, Any]] = []
        self.results: Dict[str, AgentResult] = {}
    
    def add_step(
        self,
        agent: Agent,
        task: str,
        name: Optional[str] = None,
        depends_on: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a step to the workflow."""
        step_name = name or f"step_{len(self.steps)}"
        self.steps.append({
            "name": step_name,
            "agent": agent,
            "task": task,
            "depends_on": depends_on or [],
            "context": context or {}
        })
        return step_name
    
    async def run(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, AgentResult]:
        """Execute all workflow steps in dependency order."""
        completed = set()
        context = initial_context or {}
        
        while len(completed) < len(self.steps):
            # Find steps that are ready (all dependencies met)
            ready_steps = [
                s for s in self.steps
                if s["name"] not in completed
                and all(dep in completed for dep in s["depends_on"])
            ]
            
            if not ready_steps:
                raise ValueError("Circular dependency detected in workflow")
            
            # Execute ready steps (could be parallelized)
            for step in ready_steps:
                # Merge context from dependencies
                step_context = dict(context)
                for dep in step["depends_on"]:
                    if dep in self.results:
                        step_context[f"{dep}_output"] = self.results[dep].output
                
                step["context"].update(step_context)
                
                result = await step["agent"].run(step["task"], step["context"])
                self.results[step["name"]] = result
                completed.add(step["name"])
        
        return self.results


# Example tools for demonstration
class WebSearchTool(Tool):
    """Tool for searching the web."""
    name = "web_search"
    description = "Search the web for information"
    parameters = {
        "query": {
            "type": "string",
            "description": "Search query"
        }
    }
    
    async def execute(self, query: str) -> str:
        # In production, integrate with actual search API
        return f"Search results for: {query}"


class DocumentReaderTool(Tool):
    """Tool for reading documents."""
    name = "document_reader"
    description = "Read and summarize documents"
    parameters = {
        "url": {
            "type": "string",
            "description": "Document URL"
        }
    }
    
    async def execute(self, url: str) -> str:
        # In production, fetch and parse actual documents
        return f"Document content from: {url}"


if __name__ == "__main__":
    # Quick demo
    async def demo():
        agent = Agent(
            name="demo_agent",
            system_prompt="You are a helpful research assistant.",
            tools=[WebSearchTool(), DocumentReaderTool()],
            memory=InMemoryMemory()
        )
        
        result = await agent.run("Find recent news about AI agents")
        print(f"Status: {result.status.value}")
        print(f"Output: {result.output}")
        print(f"Duration: {result.duration_ms:.2f}ms")
    
    asyncio.run(demo())
