# Blog Post: Building Your First Agent: A Step-by-Step Guide
## Published: September 12, 2026
## Category: Tutorial

---

# Building Your First Agent: A Step-by-Step Guide

*From zero to deployed agent in one afternoon.*

---

## Prerequisites

- Python 3.10+
- OpenAI API key
- 2-3 hours

---

## Step 1: Setup (10 minutes)

```bash
mkdir my-first-agent
cd my-first-agent
python -m venv venv
source venv/bin/activate
pip install openai fastapi uvicorn
```

---

## Step 2: Basic Agent (20 minutes)

Create `agent.py`:

```python
import openai
from typing import List, Dict

class Agent:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.history: List[Dict] = []
    
    def run(self, query: str) -> str:
        self.history.append({"role": "user", "content": query})
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.history
        )
        
        answer = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": answer})
        
        return answer

# Test
if __name__ == "__main__":
    agent = Agent(api_key="your-key")
    print(agent.run("Hello! What can you do?"))
```

---

## Step 3: Add Tools (30 minutes)

Create `tools.py`:

```python
import requests
from typing import Dict, Any

class Tool:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, **kwargs) -> Any:
        raise NotImplementedError

class WeatherTool(Tool):
    def __init__(self):
        super().__init__("weather", "Get weather for a location")
    
    def execute(self, location: str) -> str:
        # Simplified - use real weather API
        return f"Weather in {location}: 72°F, Sunny"

class CalculatorTool(Tool):
    def __init__(self):
        super().__init__("calculator", "Perform calculations")
    
    def execute(self, expression: str) -> str:
        try:
            result = eval(expression)
            return f"Result: {result}"
        except:
            return "Invalid expression"
```

---

## Step 4: Agent with Tools (30 minutes)

Update `agent.py`:

```python
from tools import Tool

class AgentWithTools:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.tools: Dict[str, Tool] = {}
    
    def add_tool(self, tool: Tool):
        self.tools[tool.name] = tool
    
    def run(self, query: str) -> str:
        # Simple keyword matching for demo
        if "weather" in query.lower():
            location = query.split("in")[-1].strip()
            return self.tools["weather"].execute(location=location)
        
        if "calculate" in query.lower():
            expression = query.split("calculate")[-1].strip()
            return self.tools["calculator"].execute(expression=expression)
        
        # Default to LLM
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": query}]
        )
        return response.choices[0].message.content
```

---

## Step 5: Deploy (30 minutes)

Create `main.py`:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from agent import AgentWithTools
from tools import WeatherTool, CalculatorTool

app = FastAPI()
agent = AgentWithTools(api_key="your-key")
agent.add_tool(WeatherTool())
agent.add_tool(CalculatorTool())

class QueryRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat(request: QueryRequest):
    response = agent.run(request.query)
    return {"response": response}

@app.get("/health")
async def health():
    return {"status": "ok"}
```

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Deploy to Fly.io:

```bash
fly launch
fly deploy
```

---

## Step 6: Test (10 minutes)

```bash
curl -X POST https://your-app.fly.dev/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in New York?"}'
```

---

## Next Steps

- Add more tools
- Implement memory
- Add authentication
- Set up monitoring
- Write tests
- Optimize costs

---

## Resources

- **Full code:** github.com/ArQon-ai/agentstack/examples/first-agent
- **Documentation:** github.com/ArQon-ai/agentstack/tree/main/docs
- **Community:** Join The Dispatch

---

*ArQon Agentics helps builders create their first production agent. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
