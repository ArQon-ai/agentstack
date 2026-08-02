# Chapter 4: Multi-Agent Orchestration Patterns

**The Agentic Engineer's Playbook**
*By ArQon Agentics*

---

## Overview

Single agents can handle many tasks. But complex problems require multiple agents working together.

This chapter covers the patterns for orchestrating agent teams — when to use them, how to design them, and how to keep them from becoming chaos.

---

## When to Use Multiple Agents

Use multiple agents when:

1. **Tasks require different expertise** — A coding agent and a testing agent have different skills
2. **Workflows have sequential dependencies** — Research → Analysis → Writing → Review
3. **Quality requires checks and balances** — Writer + Editor + Fact-checker
4. **Scale requires parallelization** — 100 customer queries processed simultaneously
5. **Complexity requires decomposition** — Break big problems into smaller, manageable pieces

Don't use multiple agents when:
- The task is simple and sequential
- Latency is critical (coordination overhead)
- Consistency is more important than specialization

---

## Pattern 1: Sequential Pipeline

Agents pass work down a pipeline, each adding their expertise.

### Architecture

```
User Input
    ↓
[Research Agent] → Facts, context, sources
    ↓
[Analysis Agent] → Insights, patterns, conclusions
    ↓
[Writing Agent] → Draft content
    ↓
[Review Agent] → Edits, fact-checks, approvals
    ↓
Final Output
```

### Implementation

```python
from agentstack.core import Agent, Workflow

class SequentialPipeline(Workflow):
    def __init__(self):
        self.researcher = Agent(
            name="researcher",
            instructions="Gather facts and context"
        )
        self.analyst = Agent(
            name="analyst", 
            instructions="Analyze and derive insights"
        )
        self.writer = Agent(
            name="writer",
            instructions="Create draft content"
        )
        self.reviewer = Agent(
            name="reviewer",
            instructions="Review and improve"
        )
    
    def run(self, query):
        # Phase 1: Research
        research = self.researcher.run(query)
        
        # Phase 2: Analysis
        analysis = self.analyst.run(
            f"Analyze: {query}\nResearch: {research}"
        )
        
        # Phase 3: Writing
        draft = self.writer.run(
            f"Write about: {query}\nAnalysis: {analysis}"
        )
        
        # Phase 4: Review
        final = self.reviewer.run(
            f"Review: {draft}\nOriginal query: {query}"
        )
        
        return final
```

### When to Use
- Content creation workflows
- Data processing pipelines
- Multi-step analysis tasks

### Pros
- Simple to understand and debug
- Each step can be optimized independently
- Easy to add/remove stages

### Cons
- Latency adds up (sum of all agent times)
- No parallelization
- Early errors propagate

---

## Pattern 2: Parallel Map-Reduce

Agents work in parallel, then results are combined.

### Architecture

```
User Input
    ↓
[Split] → Task A | Task B | Task C
    ↓
[Agent A] [Agent B] [Agent C]
    ↓
[Combine] → Final Result
```

### Implementation

```python
import asyncio

class MapReduceWorkflow(Workflow):
    def __init__(self, num_workers=5):
        self.agents = [
            Agent(name=f"worker_{i}")
            for i in range(num_workers)
        ]
        self.combiner = Agent(name="combiner")
    
    async def run(self, tasks):
        # Map: Process in parallel
        async def process_task(agent, task):
            return await agent.run_async(task)
        
        results = await asyncio.gather(*[
            process_task(agent, task)
            for agent, task in zip(self.agents, tasks)
        ])
        
        # Reduce: Combine results
        combined = self.combiner.run(
            f"Combine these results: {results}"
        )
        
        return combined
```

### When to Use
- Batch processing
- Data analysis across multiple dimensions
- Survey/feedback processing

### Pros
- Maximum parallelism
- Scales with workers
- Fault tolerant (one failure doesn't stop others)

### Cons
- Requires combiner logic
- Can lose nuance in combination
- More complex error handling

---

## Pattern 3: Hierarchical Team

A manager agent coordinates specialist agents.

### Architecture

```
        [Manager Agent]
       /       |       \
      ↓        ↓        ↓
[Specialist A] [Specialist B] [Specialist C]
      ↓        ↓        ↓
       \       |       /
        ↓      ↓      ↓
      [Integration]
```

### Implementation

```python
class HierarchicalTeam(Workflow):
    def __init__(self):
        self.manager = Agent(
            name="manager",
            instructions="""
            You are a project manager. Break down tasks,
            assign to specialists, and integrate results.
            """
        )
        
        self.specialists = {
            "frontend": Agent(name="frontend_dev"),
            "backend": Agent(name="backend_dev"),
            "design": Agent(name="designer"),
            "qa": Agent(name="qa_engineer")
        }
        
        self.integrator = Agent(name="integrator")
    
    def run(self, project_description):
        # Manager creates plan
        plan = self.manager.run(
            f"Plan this project: {project_description}"
        )
        
        # Execute specialist tasks
        results = {}
        for task in plan.tasks:
            specialist = self.specialists[task.specialist]
            results[task.id] = specialist.run(task.description)
        
        # Integrate results
        final = self.integrator.run(
            f"Integrate: {results}"
        )
        
        return final
```

### When to Use
- Software development
- Complex project management
- Multi-disciplinary tasks

### Pros
- Clear ownership
- Scalable (add specialists)
- Natural delegation

### Cons
- Manager bottleneck
- Single point of failure
- Coordination overhead

---

## Pattern 4: Debate & Consensus

Multiple agents debate, then reach consensus.

### Architecture

```
User Input
    ↓
[Agent A: Position X]
[Agent B: Position Y]
[Agent C: Position Z]
    ↓
[Debate Rounds]
    ↓
[Consensus Agent] → Final Answer
```

### Implementation

```python
class DebateWorkflow(Workflow):
    def __init__(self, num_rounds=3):
        self.agents = [
            Agent(name="agent_a", stance="optimistic"),
            Agent(name="agent_b", stance="pessimistic"),
            Agent(name="agent_c", stance="neutral")
        ]
        self.consensus = Agent(name="consensus")
        self.num_rounds = num_rounds
    
    def run(self, question):
        # Initial positions
        positions = {
            agent.name: agent.run(f"Your position on: {question}")
            for agent in self.agents
        }
        
        # Debate rounds
        for round in range(self.num_rounds):
            new_positions = {}
            for agent in self.agents:
                # Each agent responds to others
                context = f"Round {round}. Others say: {positions}"
                new_positions[agent.name] = agent.run(context)
            positions = new_positions
        
        # Reach consensus
        final = self.consensus.run(
            f"Reach consensus from: {positions}"
        )
        
        return final
```

### When to Use
- High-stakes decisions
- Complex ethical questions
- Strategy development

### Pros
- Multiple perspectives
- Reduced bias
- Better reasoning

### Cons
- Expensive (multiple agents × rounds)
- Slow
- May not reach consensus

---

## Pattern 5: Market/Economy of Agents

Agents bid on tasks, optimizing for cost and quality.

### Architecture

```
Task Market
    ↓
[Agent A bids: $0.50, 95% accuracy]
[Agent B bids: $0.30, 85% accuracy]
[Agent C bids: $0.80, 99% accuracy]
    ↓
[Router selects based on budget/quality]
    ↓
Execute → Evaluate → Pay
```

### Implementation

```python
class AgentMarket(Workflow):
    def __init__(self):
        self.agents = [
            Agent(name="cheap", cost=0.10, quality=0.80),
            Agent(name="balanced", cost=0.50, quality=0.90),
            Agent(name="premium", cost=2.00, quality=0.99)
        ]
    
    def run(self, task, budget=1.00, min_quality=0.85):
        # Get bids
        bids = []
        for agent in self.agents:
            bid = agent.bid(task)
            bids.append({
                "agent": agent,
                "cost": bid.cost,
                "quality": bid.quality
            })
        
        # Select best agent within budget
        valid_bids = [
            b for b in bids
            if b["cost"] <= budget and b["quality"] >= min_quality
        ]
        
        if not valid_bids:
            raise ValueError("No valid bids")
        
        # Optimize: best quality per dollar
        selected = max(valid_bids, key=lambda b: b["quality"] / b["cost"])
        
        # Execute
        result = selected["agent"].run(task)
        
        return result
```

### When to Use
- Cost-sensitive applications
- Variable quality requirements
- Large-scale operations

### Pros
- Cost optimization
- Quality guarantees
- Natural load balancing

### Cons
- Complex bidding logic
- Requires evaluation framework
- Market dynamics can be unstable

---

## Shared Infrastructure for Multi-Agent Systems

Every multi-agent system needs:

### 1. Shared Context Store
```python
class SharedContext:
    def __init__(self):
        self.store = {}
    
    def write(self, agent_id, key, value):
        self.store[f"{agent_id}:{key}"] = {
            "value": value,
            "timestamp": time.time()
        }
    
    def read(self, pattern):
        # Read with pattern matching
        return {
            k: v for k, v in self.store.items()
            if pattern in k
        }
```

### 2. Message Bus
```python
class MessageBus:
    def __init__(self):
        self.subscribers = {}
    
    def subscribe(self, topic, agent):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(agent)
    
    def publish(self, topic, message):
        for agent in self.subscribers.get(topic, []):
            agent.receive(message)
```

### 3. Conflict Resolution
```python
class ConflictResolver:
    def resolve(self, agent_outputs):
        # Voting
        votes = {}
        for output in agent_outputs:
            votes[output] = votes.get(output, 0) + 1
        
        # Return majority
        return max(votes, key=votes.get)
```

---

## Common Multi-Agent Failure Modes

### 1. Coordination Breakdown
**Symptom:** Agents wait for each other indefinitely.

**Fix:** Timeouts, heartbeat checks, circuit breakers.

### 2. Context Inconsistency
**Symptom:** Different agents have different versions of shared state.

**Fix:** Versioned context store, atomic updates, conflict resolution.

### 3. Cascading Failures
**Symptom:** One failed agent brings down the whole system.

**Fix:** Isolation, fallbacks, graceful degradation.

### 4. Cost Explosion
**Symptom:** Multi-agent systems cost 10x more than expected.

**Fix:** Budgets per workflow, cost-aware routing, caching.

---

## Decision Framework

Choose your pattern based on:

| Factor | Pipeline | Map-Reduce | Hierarchical | Debate | Market |
|--------|----------|------------|--------------|--------|--------|
| Latency | Medium | Low | Medium | High | Medium |
| Cost | Medium | Medium | Medium | High | Variable |
| Quality | Medium | Medium | High | Very High | Variable |
| Scalability | Low | High | Medium | Low | High |
| Complexity | Low | Medium | Medium | High | High |

---

*This is Chapter 4 of The Agentic Engineer's Playbook. Get the full book at [arqonagentics.com](https://arqonagentics.com).*
