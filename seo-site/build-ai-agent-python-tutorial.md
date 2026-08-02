# SEO Article: Building AI Agents with Python: Complete Tutorial
**Target Keywords:** build AI agent Python, Python agent tutorial, AI agent development  
**Published:** September 5, 2026

---

# Building AI Agents with Python: Complete Tutorial

Build a production-ready agent from scratch in Python.

---

## Prerequisites

```bash
pip install fastapi uvicorn openai pydantic redis
```

---

## Step 1: Basic Agent

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
            model="gpt-4o",
            messages=self.history
        )
        
        answer = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": answer})
        
        return answer

# Usage
agent = Agent(api_key="your-key")
result = agent.run("What is the capital of France?")
print(result)  # Paris
```

---

## Step 2: Adding Tools

```python
class Tool:
    def __init__(self, name: str, func):
        self.name = name
        self.func = func
    
    def execute(self, **kwargs):
        return self.func(**kwargs)

class AgentWithTools:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.tools: Dict[str, Tool] = {}
    
    def add_tool(self, tool: Tool):
        self.tools[tool.name] = tool
    
    def run(self, query: str) -> str:
        # Determine which tool to use
        tool_name = self.select_tool(query)
        
        if tool_name in self.tools:
            result = self.tools[tool_name].execute(query=query)
            return f"Tool result: {result}"
        
        # Fallback to direct LLM
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": query}]
        )
        return response.choices[0].message.content
    
    def select_tool(self, query: str) -> str:
        # Simple keyword matching
        if "weather" in query.lower():
            return "weather"
        if "calculate" in query.lower():
            return "calculator"
        return "none"

# Usage
agent = AgentWithTools(api_key="your-key")
agent.add_tool(Tool("calculator", lambda **kwargs: eval(kwargs["query"].replace("calculate", ""))))

result = agent.run("calculate 2 + 2")
print(result)  # Tool result: 4
```

---

## Step 3: Adding Memory

```python
import redis
import json

class AgentWithMemory:
    def __init__(self, api_key: str, redis_url: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.memory = redis.from_url(redis_url)
    
    def run(self, user_id: str, query: str) -> str:
        # Get conversation history
        history_key = f"history:{user_id}"
        history = self.memory.get(history_key)
        
        if history:
            messages = json.loads(history)
        else:
            messages = []
        
        # Add user query
        messages.append({"role": "user", "content": query})
        
        # Get response
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        
        answer = response.choices[0].message.content
        
        # Update history
        messages.append({"role": "assistant", "content": answer})
        self.memory.setex(history_key, 3600, json.dumps(messages))
        
        return answer
```

---

## Step 4: FastAPI Deployment

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
agent = AgentWithMemory(api_key="your-key", redis_url="redis://localhost")

class QueryRequest(BaseModel):
    user_id: str
    query: str

@app.post("/chat")
async def chat(request: QueryRequest):
    try:
        response = agent.run(request.user_id, request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Step 5: Adding Cost Controls

```python
class CostControlledAgent:
    def __init__(self, api_key: str, max_daily_cost: float = 10.0):
        self.client = openai.OpenAI(api_key=api_key)
        self.max_daily_cost = max_daily_cost
        self.daily_cost = 0.0
    
    def run(self, query: str) -> str:
        # Check budget
        if self.daily_cost >= self.max_daily_cost:
            raise Exception("Daily budget exceeded")
        
        # Estimate cost
        estimated_cost = self.estimate_cost(query)
        
        if self.daily_cost + estimated_cost > self.max_daily_cost:
            raise Exception("Would exceed daily budget")
        
        # Run agent
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": query}]
        )
        
        # Track cost
        actual_cost = self.calculate_cost(response)
        self.daily_cost += actual_cost
        
        return response.choices[0].message.content
    
    def estimate_cost(self, query: str) -> float:
        tokens = len(query.split()) * 1.3
        return tokens * 0.00003  # GPT-4o rate
    
    def calculate_cost(self, response) -> float:
        tokens = response.usage.total_tokens
        return tokens * 0.00003
```

---

## Step 6: Testing

```python
import pytest

class TestAgent:
    def test_basic_query(self):
        agent = Agent(api_key="test-key")
        result = agent.run("What is 2+2?")
        assert "4" in result
    
    def test_memory(self):
        agent = AgentWithMemory(api_key="test-key", redis_url="redis://localhost")
        agent.run("user1", "My name is Alice")
        result = agent.run("user1", "What's my name?")
        assert "Alice" in result
    
    def test_cost_control(self):
        agent = CostControlledAgent(api_key="test-key", max_daily_cost=0.001)
        
        with pytest.raises(Exception):
            for _ in range(100):
                agent.run("Test query")
```

---

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Fly.io

```toml
app = "my-agent"

[build]
  dockerfile = "Dockerfile"

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80
```

---

## Next Steps

- Add more tools
- Implement RAG
- Add authentication
- Set up monitoring
- Write documentation
- Deploy to production

---

*ArQon Agentics provides production-grade agent frameworks. Get the complete code at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
