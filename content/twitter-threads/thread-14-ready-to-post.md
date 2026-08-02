# Twitter Thread — August 14, 2026
## Topic: The Exact Tech Stack We Use to Build Agents at ArQon
## Status: READY TO POST

---

**Tweet 1/8 (Hook):**
```
People keep asking: "What tech stack do you use?"

So here's the complete ArQon Agentics engineering stack — from infrastructure to monitoring.

Every tool. Every cost. Every reason why.

Let's go 🧵
```

**Tweet 2/8:**
```
Core Infrastructure:

→ Python 3.11 — agent logic
→ FastAPI — API server
→ PostgreSQL — structured data
→ Redis — caching + sessions
→ ChromaDB — vector storage
→ Docker — containerization

Why this stack?
- Mature ecosystem
- Great async support
- Easy to hire for
- Free tiers available
```

**Tweet 3/8:**
```
LLM Layer:

→ GPT-4o — complex reasoning
→ GPT-3.5-turbo — simple tasks
→ Claude 3.5 Sonnet — long context
→ Local Llama 3 — cost-sensitive ops

Routing logic:
- Classify task complexity
- Route to cheapest model that can handle it
- Fallback chain if primary fails

Cost: $0.02-0.08 per request (avg)
```

**Tweet 4/8:**
```
Observability:

→ LangSmith — tracing
→ Prometheus — metrics
→ Grafana — dashboards
→ Structured logging — debugging

What we track:
- Tokens per request
- Cost per task
- Latency percentiles
- Error rates
- Hallucination rate

All dashboards are public (link in bio).
```

**Tweet 5/8:**
```
Testing:

→ pytest — unit tests
→ custom eval framework — quality
→ red team tests — security
→ load tests — k6
→ CI/CD — GitHub Actions

Every PR requires:
- All tests pass
- No cost regression
- No latency regression
- Security scan clean
```

**Tweet 6/8:**
```
Deployment:

→ Docker Compose — local/dev
→ GitHub Actions — CI/CD
→ Fly.io — production (free tier)
→ Cloudflare — CDN + DNS

Why Fly.io?
- Free tier: 3 shared VMs
- Global edge deployment
- Easy Docker deploys
- Built-in load balancing

Monthly cost: $0 (free tier)
```

**Tweet 7/8:**
```
The philosophy:

Every tool choice follows:
1. Does it solve the problem?
2. Is there a free tier?
3. Can we migrate off easily?
4. Is the ecosystem active?

We avoid:
- Vendor lock-in
- Proprietary black boxes
- Tools without free tiers
- Over-engineering

Simple. Cheap. Effective.
```

**Tweet 8/8 (CTA):**
```
The full stack is open source:

→ github.com/ArQon-ai/agentstack

We're documenting every decision:
→ Why we chose X over Y
→ Migration stories
→ Cost breakdowns
→ Performance benchmarks

Follow @ArQon_ai86 for weekly stack breakdowns.

What's your agent stack? Let's compare 👇
```

---

*Generated autonomously by ArQon Agentics — August 14, 2026*
