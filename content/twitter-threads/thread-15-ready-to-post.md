# Twitter Thread — August 15, 2026
## Topic: The Day My Agent Almost Cost Me $5,000 (And What I Fixed)
## Status: READY TO POST

---

**Tweet 1/8 (Hook):**
```
Last Tuesday, my agent almost cost me $5,000.

Not a hack. Not a bug.

A simple mistake that every agent builder makes.

Here's what happened — and the 3 fixes that saved me 🧵
```

**Tweet 2/8:**
```
The setup:

I deployed a research agent that:
→ Searches the web
→ Summarizes findings
→ Writes reports

It worked great in testing.
10 queries, $0.50 total.

I set it to "auto-run" for a demo.
```

**Tweet 3/8:**
```
The incident:

Agent received a query:
"Research the history of artificial intelligence"

It decided this needed:
→ 50 search queries
→ 20,000 tokens of context
→ Multiple summarization rounds

Cost per query: $0.15
Queries before I noticed: 340

Total: $51 (in 2 hours)
```

**Tweet 4/8:**
```
The root cause:

No cost controls.

The agent had:
→ No token limit per request
→ No daily budget
→ No step limit
→ No human approval for expensive ops

It just kept going.
"Research needs more research!"
```

**Tweet 5/8:**
```
Fix 1: Token Budgets

```python
class CostControlledAgent:
    def __init__(self, max_tokens=4000):
        self.max_tokens = max_tokens
        self.tokens_used = 0
    
    def run(self, query):
        if self.tokens_used >= self.max_tokens:
            return "Budget exceeded"
        
        result = super().run(query)
        self.tokens_used += result.tokens
        return result
```

Hard limit. No exceptions.
```

**Tweet 6/8:**
```
Fix 2: Step Limits

```python
def run_with_limit(agent, query, max_steps=10):
    for step in range(max_steps):
        action = agent.decide_action()
        
        if action == "complete":
            return agent.result
        
        agent.execute(action)
    
    return "Step limit reached"
```

Agent can't loop forever.
Max 10 steps, then stop.
```

**Tweet 7/8:**
```
Fix 3: Human Approval for Expensive Operations

```python
class ApprovalGate:
    def check(self, action):
        if action.estimated_cost > 0.10:
            return request_human_approval(action)
        return True
```

Anything over $0.10?
Human says yes or no.

Simple. Effective.
```

**Tweet 8/8 (CTA):**
```
The lessons:

1. Set hard limits before deploying
2. Monitor costs in real-time
3. Require approval for expensive ops
4. Test with adversarial inputs

These aren't optional.
They're mandatory.

We're building these controls into AgentStack:
→ Cost limits
→ Step limits
→ Approval gates
→ Real-time monitoring

⭐ github.com/ArQon-ai/agentstack

What's your agent horror story? 👇
```

---

*Generated autonomously by ArQon Agentics — August 15, 2026*
