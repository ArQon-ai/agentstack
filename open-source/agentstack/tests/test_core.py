import pytest
import asyncio
from agentstack.core import Agent, Workflow, InMemoryMemory, WebSearchTool, AgentStatus


@pytest.mark.asyncio
async def test_agent_creation():
    """Test basic agent creation."""
    agent = Agent(name="test_agent", system_prompt="You are a test agent.")
    assert agent.name == "test_agent"
    assert agent.status == AgentStatus.IDLE


@pytest.mark.asyncio
async def test_agent_run():
    """Test agent execution."""
    agent = Agent(name="test_agent", system_prompt="You are a test agent.")
    result = await agent.run("Say hello")
    
    assert result.status == AgentStatus.COMPLETE
    assert len(result.steps) > 0
    assert result.duration_ms > 0


@pytest.mark.asyncio
async def test_agent_with_tools():
    """Test agent with tools."""
    agent = Agent(
        name="test_agent",
        tools=[WebSearchTool()],
        memory=InMemoryMemory()
    )
    
    schemas = agent.get_tool_schemas()
    assert len(schemas) == 1
    assert schemas[0]["name"] == "web_search"


@pytest.mark.asyncio
async def test_memory_operations():
    """Test memory store and retrieve."""
    memory = InMemoryMemory()
    
    await memory.store("key1", "value1")
    result = await memory.retrieve("key1")
    
    assert result == "value1"


@pytest.mark.asyncio
async def test_memory_search():
    """Test memory search functionality."""
    memory = InMemoryMemory()
    
    await memory.store("doc1", "This is about machine learning")
    await memory.store("doc2", "This is about web development")
    
    results = await memory.search("machine learning", limit=5)
    
    assert len(results) > 0
    assert any("machine learning" in str(r["value"]) for r in results)


@pytest.mark.asyncio
async def test_workflow_creation():
    """Test workflow with dependencies."""
    agent = Agent(name="test_agent")
    workflow = Workflow()
    
    step1 = workflow.add_step(agent, task="step 1", name="first")
    step2 = workflow.add_step(agent, task="step 2", name="second", depends_on=["first"])
    
    assert len(workflow.steps) == 2
    assert workflow.steps[1]["depends_on"] == ["first"]


@pytest.mark.asyncio
async def test_workflow_execution():
    """Test workflow execution."""
    agent = Agent(name="test_agent")
    workflow = Workflow()
    
    workflow.add_step(agent, task="task 1", name="step1")
    workflow.add_step(agent, task="task 2", name="step2", depends_on=["step1"])
    
    results = await workflow.run()
    
    assert "step1" in results
    assert "step2" in results
    assert results["step1"].status == AgentStatus.COMPLETE
    assert results["step2"].status == AgentStatus.COMPLETE


@pytest.mark.asyncio
async def test_agent_error_handling():
    """Test agent handles errors gracefully."""
    # Create an agent that will encounter an issue
    agent = Agent(name="test_agent", max_steps=1)
    
    # The simulation should still complete
    result = await agent.run("Test task")
    assert result.status == AgentStatus.COMPLETE


def test_tool_schema_validation():
    """Test tool schema generation."""
    tool = WebSearchTool()
    
    assert tool.name == "web_search"
    assert tool.description != ""
    assert "query" in tool.parameters


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
