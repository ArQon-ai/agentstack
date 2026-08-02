# AgentStack

> A production-ready starter kit for building agentic systems at scale.

[![GitHub stars](https://img.shields.io/github/stars/arqon-agentics/agentstack?style=social)](https://github.com/arqon-agentics/agentstack)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is AgentStack?

AgentStack is an opinionated starter kit for building production-grade agentic systems. It bridges the gap between "vibe coding" a prototype and running agents reliably in production.

Built by [ArQon Agentics](https://arqonagentics.com).

## Features

- ⚡ **Agent Orchestration** — Multi-agent workflows with inter-agent communication
- 🧠 **Context Engineering** — Shared memory, context window management, semantic retrieval
- 🔧 **MCP Server Integration** — Pre-built connectors for common tools and APIs
- 📊 **Observability** — Reasoning traces, tool call logging, cost tracking
- 🛡️ **Governance** — Agent permissions, audit trails, human-in-the-loop gates
- 🚀 **One-Command Deploy** — Docker Compose, Kubernetes, or Vercel

## Quick Start

```bash
# Clone the starter kit
git clone https://github.com/arqon-agentics/agentstack.git
cd agentstack

# Copy environment template
cp .env.example .env

# Start the stack
docker-compose up -d

# Run your first agent
python -m agentstack.examples.quickstart
```

## Architecture

```
┌─────────────────────────────────────────┐
│           Agent Control Plane            │
│  (Governance, Audit, Human-in-the-Loop)  │
└─────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌────────┐    ┌────────┐    ┌────────┐
│ Agent  │    │ Agent  │    │ Agent  │
│   A    │◄──►│   B    │◄──►│   C    │
└────────┘    └────────┘    └────────┘
    │               │               │
    └───────────────┼───────────────┘
                    ▼
┌─────────────────────────────────────────┐
│      Shared Memory & Context Store       │
│   (Vector DB, Key-Value, Session State)  │
└─────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌────────┐    ┌────────┐    ┌────────┐
│  MCP   │    │  MCP   │    │  MCP   │
│ Server │    │ Server │    │ Server │
│   #1   │    │   #2   │    │   #3   │
└────────┘    └────────┘    └────────┘
```

## Components

### Agent Runtime
- FastAPI-based agent server
- Async task processing with Celery
- Configurable agent pools and scaling

### Memory & Context
- Redis for session state
- Qdrant/Pinecone for vector storage
- Context window optimization

### MCP Integration
- Pre-built MCP servers for:
  - File system operations
  - Database queries
  - REST API calls
  - GitHub operations
  - Slack notifications

### Observability
- OpenTelemetry tracing
- Prometheus metrics
- Grafana dashboards
- Cost tracking per agent/task

## Directory Structure

```
agentstack/
├── agents/              # Agent definitions and configurations
├── mcp/                 # MCP server implementations
├── memory/              # Context and memory management
├── orchestration/       # Multi-agent workflow engine
├── observability/       # Tracing, metrics, logging
├── governance/          # Permissions, audit, policies
├── deployments/         # Docker, K8s, Terraform configs
├── examples/            # Example agents and workflows
└── tests/               # Test suites
```

## Examples

### Simple Agent
```python
from agentstack import Agent, Memory

agent = Agent(
    name="researcher",
    model="claude-sonnet-4",
    tools=["web_search", "document_reader"],
    memory=Memory.vector_store()
)

result = agent.run("Find the latest papers on multi-agent systems")
```

### Multi-Agent Workflow
```python
from agentstack import Workflow, Agent

workflow = Workflow()

# Define agents
researcher = Agent(name="researcher", tools=["web_search"])
writer = Agent(name="writer", tools=["document_writer"])
reviewer = Agent(name="reviewer", tools=["grammar_check"])

# Define flow
workflow.add_step(researcher, task="research_topic")
workflow.add_step(writer, task="write_article", depends_on=["researcher"])
workflow.add_step(reviewer, task="review_article", depends_on=["writer"])

# Execute
results = workflow.run(topic="Agentic Engineering in 2026")
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture Guide](docs/architecture.md)
- [MCP Server Development](docs/mcp-servers.md)
- [Observability Setup](docs/observability.md)
- [Governance & Policies](docs/governance.md)
- [Deployment Guide](docs/deployment.md)

## Roadmap

- [x] Core agent runtime
- [x] MCP server framework
- [x] Memory and context management
- [x] Basic observability
- [ ] Advanced multi-agent orchestration
- [ ] Web UI for agent management
- [ ] Managed cloud offering
- [ ] Enterprise SSO and RBAC

## Contributing

We build in the open. Contributions welcome!

1. Fork the repo
2. Create a feature branch
3. Write tests
4. Submit a PR

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License — see [LICENSE](LICENSE) for details.

## About ArQon Agentics

AgentStack is built by [ArQon Agentics](https://arqonagentics.com), a collective of platform engineers and vibe coders shipping the future of agentic infrastructure.

- 🌐 [Website](https://arqonagentics.com)
- 🐦 [Twitter](https://twitter.com/ArQon_ai86)
- 📧 [Newsletter](https://arqonai.substack.com)

---

*Built with ⚡ and way too much caffeine.*
