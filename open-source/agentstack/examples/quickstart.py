#!/usr/bin/env python3
"""
AgentStack Quickstart Example
Run this to see AgentStack in action.
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentstack.core import Agent, Workflow, WebSearchTool, DocumentReaderTool, InMemoryMemory


async def single_agent_demo():
    """Demonstrates a single agent with tools and memory."""
    print("=" * 60)
    print("SINGLE AGENT DEMO")
    print("=" * 60)
    
    agent = Agent(
        name="researcher",
        system_prompt="""You are a research assistant specializing in AI and machine learning.
You have access to web search and document reading tools.
Always cite your sources and provide structured summaries.""",
        tools=[WebSearchTool(), DocumentReaderTool()],
        memory=InMemoryMemory(),
        max_steps=5
    )
    
    result = await agent.run("What are the latest developments in multi-agent systems?")
    
    print(f"\nAgent: {agent.name}")
    print(f"Status: {result.status.value}")
    print(f"Output: {result.output}")
    print(f"Steps: {len(result.steps)}")
    print(f"Duration: {result.duration_ms:.2f}ms")
    print()


async def multi_agent_workflow_demo():
    """Demonstrates a multi-agent workflow with dependencies."""
    print("=" * 60)
    print("MULTI-AGENT WORKFLOW DEMO")
    print("=" * 60)
    
    # Create specialized agents
    researcher = Agent(
        name="researcher",
        system_prompt="Research specialist. Find and synthesize information.",
        tools=[WebSearchTool()],
        memory=InMemoryMemory()
    )
    
    writer = Agent(
        name="writer",
        system_prompt="Technical writer. Create clear, engaging content.",
        tools=[DocumentReaderTool()],
        memory=InMemoryMemory()
    )
    
    editor = Agent(
        name="editor",
        system_prompt="Editor. Review and improve content quality.",
        tools=[],
        memory=InMemoryMemory()
    )
    
    # Build workflow
    workflow = Workflow()
    
    workflow.add_step(
        researcher,
        task="Research the current state of vibe coding tools (Cursor, Claude Code, Windsurf)",
        name="research"
    )
    
    workflow.add_step(
        writer,
        task="Write a technical comparison article based on the research",
        name="write",
        depends_on=["research"]
    )
    
    workflow.add_step(
        editor,
        task="Review and improve the article",
        name="edit",
        depends_on=["write"]
    )
    
    # Execute
    results = await workflow.run()
    
    print("\nWorkflow Results:")
    for step_name, result in results.items():
        print(f"\n  Step: {step_name}")
        print(f"  Status: {result.status.value}")
        print(f"  Output: {result.output[:100]}...")
        print(f"  Duration: {result.duration_ms:.2f}ms")
    print()


async def memory_demo():
    """Demonstrates agent memory and context retrieval."""
    print("=" * 60)
    print("MEMORY & CONTEXT DEMO")
    print("=" * 60)
    
    memory = InMemoryMemory()
    
    # Store some knowledge
    await memory.store("mcp_definition", {
        "topic": "MCP",
        "content": "Model Context Protocol (MCP) is an open standard for connecting AI assistants to data sources and tools."
    })
    
    await memory.store("vibe_coding", {
        "topic": "Vibe Coding",
        "content": "Vibe coding is an approach where developers use AI to generate code through natural language prompts."
    })
    
    # Create agent with memory
    agent = Agent(
        name="context_aware",
        system_prompt="You answer questions using your knowledge base.",
        memory=memory
    )
    
    # Ask a question that should use memory
    result = await agent.run("What is MCP and how does it relate to vibe coding?")
    
    print(f"\nAgent: {agent.name}")
    print(f"Output: {result.output}")
    print()


async def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("AGENTSTACK QUICKSTART")
    print("=" * 60 + "\n")
    
    await single_agent_demo()
    await multi_agent_workflow_demo()
    await memory_demo()
    
    print("=" * 60)
    print("All demos complete! AgentStack is ready to use.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
