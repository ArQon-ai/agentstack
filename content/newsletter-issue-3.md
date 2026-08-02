# Newsletter Issue #3 — The ArQon Agentics Dispatch
**Published:** August 14, 2026  
**Topic:** Multi-Agent Orchestration: When to Build a Team

---

*The weekly briefing for engineers building production-grade agentic systems.*

---

## This Week: The Multi-Agent Decision Framework

Everyone wants to build multi-agent systems. They're exciting, powerful, and complex.

But most teams should start with a single agent.

Here's when multi-agent makes sense — and when it doesn't.

---

## The Single Agent vs. Multi-Agent Decision

### Start with Single Agent If:

- Task is straightforward (fewer than 5 steps)
- Latency matters (< 2 second response time)
- Consistency is critical
- You're still finding product-market fit
- Team is small (< 3 engineers)

### Move to Multi-Agent If:

- Task requires multiple expertise domains
- Workflow has clear sequential dependencies
- Quality needs checks and balances
- Scale requires parallelization
- Single agent hits performance limits

---

## Pattern 1: The Specialist Team

```
[Orchestrator]
    ↓
[Researcher] → Facts
[Analyst] → Insights
[Writer] → Content
[Reviewer] → Quality
```

**Best for:** Content creation, report generation, research tasks

**Pros:**
- Clear separation of concerns
- Each agent can be optimized independently
- Easy to add/remove specialists

**Cons:**
- Sequential latency (sum of all agents)
- Orchestrator bottleneck
- Context passing overhead

---

## Pattern 2: The Parallel Squad

```
[Query]
    ↓
[Agent A] [Agent B] [Agent C]
    ↓
[Aggregator]
```

**Best for:** Batch processing, multi-dimensional analysis

**Pros:**
- Maximum parallelism
- Fault tolerant
- Scales horizontally

**Cons:**
- Requires combiner logic
- Can lose nuance
- More complex error handling

---

## Real Numbers: When Multi-Agent Pays Off

We tested both approaches on a document processing pipeline:

| Metric | Single Agent | Multi-Agent (3) | Delta |
|--------|-------------|-----------------|-------|
| Accuracy | 82% | 91% | +9pp |
| Latency | 3.2s | 8.5s | +166% |
| Cost | $0.08 | $0.24 | +200% |
| Failure Rate | 12% | 4% | -67% |

**Verdict:** Multi-agent improved quality but at significant cost. Worth it for high-stakes tasks, not for simple ones.

---

## This Week's Tool Drop

We've added multi-agent orchestration to AgentStack:

```python
from agentstack.core import Agent, Team

# Create specialist agents
researcher = Agent(name="researcher")
writer = Agent(name="writer")

# Form a team
team = Team(agents=[researcher, writer], pattern="sequential")

# Execute
result = team.run("Write a report on AI safety")
```

⭐ github.com/ArQon-ai/agentstack

---

## What's Coming Next Week

**Newsletter Issue #4:** Security and Safety for Agentic Systems

- Input validation patterns
- Output filtering
- Cost controls
- Hallucination detection
- Adversarial attack prevention

---

## The Dispatch

*The weekly briefing for engineers building production-grade agentic systems.*

→ Read past issues: substack.com/@arqonai1  
→ Follow us: @ArQon_ai86  
→ Open source: github.com/ArQon-ai/agentstack

---

*ArQon Agentics — We build. We document. We ship.*
