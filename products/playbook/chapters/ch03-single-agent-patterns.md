# Chapter 3: Single-Agent Design Patterns

**The Agentic Engineer's Playbook**
*By ArQon Agentics*

---

## Overview

Before you orchestrate multiple agents, you need to master single-agent design. This chapter covers the fundamental patterns for building reliable, production-grade individual agents.

Multi-agent systems are built on top of single-agent primitives. If your individual agents are unreliable, your multi-agent system will be chaos.

---

## The Single-Agent Architecture

Every production agent has the same core components:

```
┌─────────────────────────────────────────┐
│           Input Processor               │
│  (parse, validate, enrich user input)   │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Context Assembler               │
│  (retrieve, rank, format context)       │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│           Reasoning Engine              │
│  (LLM call with structured prompting)   │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         Output Validator                │
│  (validate, format, enrich output)      │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│          Memory Updater                 │
│  (update working, short, long-term)     │
└─────────────────────────────────────────┘
```

Let's break down each component.

---

## Pattern 1: The ReAct Agent

**ReAct** (Reasoning + Acting) is the most widely used single-agent pattern. It interleaves reasoning steps with action steps.

### How It Works

```python
class ReActAgent:
    def run(self, query):
        context = self.assemble_context(query)
        
        for step in range(self.max_steps):
            # Reason: What should I do next?
            reasoning = self.llm.generate(
                prompt=self.reasoning_prompt.format(
                    query=query,
                    context=context,
                    history=self.memory.get_recent()
                )
            )
            
            # Act: Execute the chosen action
            if reasoning.action == "tool_call":
                result = self.tools.execute(
                    reasoning.tool_name,
                    reasoning.parameters
                )
                context += f"\nTool result: {result}"
                
            elif reasoning.action == "answer":
                return self.format_output(reasoning.answer)
                
            elif reasoning.action == "clarify":
                return self.ask_clarification(reasoning.question)
            
            # Update memory
            self.memory.add_step(reasoning, result)
```

### When to Use
- Complex tasks requiring multiple steps
- Tasks with external tool dependencies
- Interactive problem-solving

### When NOT to Use
- Simple, single-step tasks (overkill)
- Real-time applications (too slow)
- Highly constrained environments (too flexible)

---

## Pattern 2: The Plan-and-Execute Agent

Instead of reasoning step-by-step, this agent plans the entire approach upfront, then executes.

### How It Works

```python
class PlanAndExecuteAgent:
    def run(self, query):
        # Phase 1: Planning
        plan = self.llm.generate(
            prompt=self.planning_prompt.format(query=query)
        )
        # Returns: [Step1, Step2, Step3, ...]
        
        # Phase 2: Execution
        results = []
        for step in plan.steps:
            result = self.execute_step(step)
            results.append(result)
            
            # Check if we need to replan
            if result.status == "failed":
                plan = self.replan(query, plan, results)
        
        # Phase 3: Synthesis
        return self.synthesize_results(results)
```

### When to Use
- Tasks with clear, sequential structure
- Batch processing
- Cost-sensitive applications (fewer LLM calls)

### When NOT to Use
- Highly dynamic environments
- Tasks requiring real-time adaptation
- Conversational interfaces

---

## Pattern 3: The Reflection Agent

This pattern adds a self-correction loop. After generating an output, the agent reflects on it and improves.

### How It Works

```python
class ReflectionAgent:
    def run(self, query):
        # Generate initial response
        draft = self.llm.generate(
            prompt=self.draft_prompt.format(query=query)
        )
        
        # Reflect on quality
        reflection = self.llm.generate(
            prompt=self.reflection_prompt.format(
                query=query,
                draft=draft
            )
        )
        
        # If issues found, improve
        if reflection.has_issues:
            improved = self.llm.generate(
                prompt=self.improvement_prompt.format(
                    query=query,
                    draft=draft,
                    reflection=reflection
                )
            )
            return improved
        
        return draft
```

### When to Use
- High-stakes outputs (code, medical, legal)
- Creative tasks (writing, design)
- Tasks where quality matters more than speed

### When NOT to Use
- Real-time applications
- Simple, low-stakes tasks
- Cost-sensitive applications

---

## Pattern 4: The Tool-Using Agent

The simplest pattern — an agent that has access to a set of tools and chooses which to use.

### How It Works

```python
class ToolUsingAgent:
    def __init__(self, tools):
        self.tools = tools
        self.tool_descriptions = self.describe_tools(tools)
    
    def run(self, query):
        # Agent decides which tools to use
        tool_selection = self.llm.generate(
            prompt=self.tool_selection_prompt.format(
                query=query,
                available_tools=self.tool_descriptions
            )
        )
        
        # Execute selected tools
        results = []
        for tool_call in tool_selection.calls:
            result = self.tools[tool_call.name].execute(
                tool_call.parameters
            )
            results.append(result)
        
        # Synthesize results
        return self.llm.generate(
            prompt=self.synthesis_prompt.format(
                query=query,
                tool_results=results
            )
        )
```

### When to Use
- Tasks requiring specific capabilities (search, calculation, API calls)
- Extensible systems (easy to add new tools)
- Hybrid human-AI workflows

### When NOT to Use
- Tasks solvable by LLM alone (unnecessary complexity)
- Highly regulated environments (tool access controls needed)

---

## Pattern 5: The State Machine Agent

For deterministic workflows, model your agent as a state machine.

### How It Works

```python
class StateMachineAgent:
    def __init__(self):
        self.states = {
            'intake': self.handle_intake,
            'classify': self.handle_classification,
            'process': self.handle_processing,
            'validate': self.handle_validation,
            'complete': self.handle_completion
        }
        self.transitions = {
            'intake': {'next': 'classify'},
            'classify': {'urgent': 'process', 'standard': 'queue'},
            'process': {'success': 'validate', 'failure': 'escalate'},
            'validate': {'pass': 'complete', 'fail': 'process'},
        }
    
    def run(self, query):
        state = 'intake'
        context = {'query': query}
        
        while state != 'complete':
            handler = self.states[state]
            result = handler(context)
            
            transition = self.transitions[state].get(result.status)
            state = transition or 'escalate'
            
            context.update(result.context)
        
        return context['output']
```

### When to Use
- Regulatory/compliance workflows
- Standardized business processes
- Multi-step approvals

### When NOT to Use
- Exploratory tasks
- Creative work
- Highly variable inputs

---

## Choosing the Right Pattern

| Pattern | Complexity | Flexibility | Speed | Reliability |
|---------|-----------|-------------|-------|-------------|
| ReAct | High | High | Medium | Medium |
| Plan-and-Execute | Medium | Medium | Fast | High |
| Reflection | Medium | Low | Slow | Very High |
| Tool-Using | Low | High | Fast | Medium |
| State Machine | Low | Low | Fast | Very High |

**Decision Framework:**
1. Is the task deterministic? → State Machine
2. Is speed critical? → Plan-and-Execute or Tool-Using
3. Is quality critical? → Reflection or Plan-and-Execute
4. Is the environment dynamic? → ReAct
5. Are there many external dependencies? → Tool-Using

---

## Common Single-Agent Failure Modes

### 1. Infinite Loops
**Symptom:** Agent cycles between the same states indefinitely.

**Fix:**
- Step limits (max 10 iterations)
- State tracking (detect repeated states)
- Timeout mechanisms

### 2. Context Overflow
**Symptom:** Agent loses track of the original goal.

**Fix:**
- Goal restatement at each step
- Hierarchical context (summary + details)
- Context window management

### 3. Tool Over-Reliance
**Symptom:** Agent calls tools when LLM could answer directly.

**Fix:**
- Tool selection thresholds
- Cost-aware routing
- Simplification prompts

### 4. Hallucination in Reasoning
**Symptom:** Agent's reasoning is plausible but wrong.

**Fix:**
- Grounding in retrieved facts
- Reasoning validation steps
- Human-in-the-loop for critical decisions

---

## Implementation Checklist

Before deploying a single-agent system, verify:

- [ ] Agent has clear input/output contracts
- [ ] Context retrieval is tested and measured
- [ ] Memory system handles edge cases
- [ ] Tool execution has timeouts and fallbacks
- [ ] Output is validated against schema
- [ ] Failure modes are handled gracefully
- [ ] Logging captures full reasoning traces
- [ ] Cost is measured and budgeted
- [ ] Latency meets user expectations
- [ ] Security boundaries are enforced

---

## From Here

Single-agent patterns are the building blocks. In the next chapter, we'll combine them into **multi-agent orchestration** — the real power of agentic systems.

But remember: a multi-agent system is only as good as its individual agents. Master these patterns first.

---

*This is Chapter 3 of The Agentic Engineer's Playbook. Get the full book at [arqonagentics.com](https://arqonagentics.com).*
