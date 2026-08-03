# Blog Post: The Agent Engineer's Guide to API Design
## Published: October 31, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to API Design

*Design APIs that agents love to use.*

---

## API Principles

### 1. RESTful Design

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Models
class AgentRequest(BaseModel):
    query: str
    context: dict | None = None
    model: str = "gpt-4o"
    temperature: float = 0.7

class AgentResponse(BaseModel):
    id: str
    content: str
    model: str
    tokens_used: int
    cost: float
    latency_ms: int

# Endpoints
@app.post("/agents/{agent_id}/run", response_model=AgentResponse)
async def run_agent(agent_id: str, request: AgentRequest):
    agent = await get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    start = time.time()
    result = await agent.run(request.query, request.context)
    latency = int((time.time() - start) * 1000)
    
    return AgentResponse(
        id=str(uuid.uuid4()),
        content=result.content,
        model=request.model,
        tokens_used=result.tokens,
        cost=result.cost,
        latency_ms=latency
    )

@app.get("/agents/{agent_id}/runs/{run_id}")
async def get_run(agent_id: str, run_id: str):
    run = await get_run_by_id(run_id)
    if not run or run.agent_id != agent_id:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return run
```

### 2. Async Processing

```python
@app.post("/agents/{agent_id}/run/async")
async def run_agent_async(agent_id: str, request: AgentRequest):
    task_id = generate_task_id()
    
    # Queue task
    await task_queue.submit({
        "task_id": task_id,
        "agent_id": agent_id,
        "query": request.query,
        "context": request.context
    })
    
    return {"task_id": task_id, "status": "queued"}

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = await task_queue.get_status(task_id)
    
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.status == "completed" else None,
        "error": task.error if task.status == "failed" else None
    }
```

---

## Authentication

### API Keys

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    # Verify against database
    user = await get_user_by_api_key(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check rate limit
    allowed = await check_rate_limit(user.id)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return user

@app.post("/agents/{agent_id}/run")
async def run_agent(
    agent_id: str,
    request: AgentRequest,
    user: User = Depends(verify_api_key)
):
    # Process request
    pass
```

---

## Rate Limiting

```python
from fastapi import Request
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/agents/{agent_id}/run")
@limiter.limit("10/minute")
async def run_agent(request: Request, agent_id: str, body: AgentRequest):
    pass
```

---

## Error Responses

```python
class APIError(BaseModel):
    error: str
    message: str
    details: dict | None = None
    request_id: str

@app.exception_handler(AgentError)
async def agent_error_handler(request: Request, exc: AgentError):
    return JSONResponse(
        status_code=500,
        content=APIError(
            error="agent_error",
            message=str(exc),
            request_id=request.state.request_id
        ).dict()
    )
```

---

## Versioning

```python
# URL versioning
@app.post("/v1/agents/{agent_id}/run")
async def run_agent_v1(agent_id: str, request: V1AgentRequest):
    pass

@app.post("/v2/agents/{agent_id}/run")
async def run_agent_v2(agent_id: str, request: V2AgentRequest):
    pass
```

---

## The API Checklist

- [ ] RESTful endpoints
- [ ] Async support
- [ ] Authentication
- [ ] Rate limiting
- [ ] Error handling
- [ ] Input validation
- [ ] Output formatting
- [ ] Versioning
- [ ] Documentation
- [ ] Testing
- [ ] Monitoring
- [ ] Security

---

## Conclusion

API design:
- Is the interface
- Affects adoption
- Enables scaling
- Requires discipline

Design for developers.
Document thoroughly.
Version carefully.

---

*ArQon Agentics designs agent APIs for production. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
