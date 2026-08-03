# Blog Post: The Agent API: Design Patterns for Production
## Published: September 22, 2026
## Category: Engineering

---

# The Agent API: Design Patterns for Production

*How to design APIs that developers love and agents can use.*

---

## RESTful Agent API

### Basic Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

class AgentRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)
    user_id: str = Field(..., description="Unique user identifier")
    context: Optional[dict] = None
    model: Optional[str] = "gpt-4o"
    
class AgentResponse(BaseModel):
    response: str
    confidence: float = Field(..., ge=0, le=1)
    sources: List[str] = []
    tokens_used: int
    cost: float
    processing_time: float
    conversation_id: str

@app.post("/v1/agent", response_model=AgentResponse)
async def agent_endpoint(request: AgentRequest):
    try:
        result = await agent.process(
            query=request.query,
            user_id=request.user_id,
            context=request.context,
            model=request.model
        )
        return result
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise HTTPException(status_code=500, detail="Processing error")
```

---

## Streaming API

### Server-Sent Events

```python
from fastapi.responses import StreamingResponse

@app.post("/v1/agent/stream")
async def agent_stream(request: AgentRequest):
    async def generate():
        async for chunk in agent.astream(
            query=request.query,
            user_id=request.user_id
        ):
            yield f"data: {json.dumps(chunk)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

---

## Conversation Management

### Session-Based API

```python
@app.post("/v1/conversations")
async def create_conversation():
    conversation_id = generate_id()
    await storage.create_conversation(conversation_id)
    return {"conversation_id": conversation_id}

@app.post("/v1/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    request: AgentRequest
):
    # Get conversation history
    history = await storage.get_history(conversation_id)
    
    # Process with context
    result = await agent.process(
        query=request.query,
        history=history
    )
    
    # Store message
    await storage.add_message(conversation_id, result)
    
    return result

@app.get("/v1/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    return await storage.get_conversation(conversation_id)
```

---

## Tool Integration

### Tool Registration

```python
class Tool(BaseModel):
    name: str
    description: str
    parameters: dict
    required_permissions: List[str] = []

@app.post("/v1/tools")
async def register_tool(tool: Tool):
    agent.register_tool(tool)
    return {"status": "registered", "tool": tool.name}

@app.get("/v1/tools")
async def list_tools():
    return agent.available_tools()
```

---

## Rate Limiting

### Token Bucket

```python
from fastapi import Request, HTTPException
from redis import Redis

redis = Redis()

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    user_id = request.headers.get("X-User-ID")
    key = f"rate_limit:{user_id}"
    
    # Check limit
    current = redis.get(key)
    if current and int(current) > 100:  # 100 requests/hour
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Increment counter
    pipe = redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, 3600)
    pipe.execute()
    
    return await call_next(request)
```

---

## Authentication

### API Key

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.post("/v1/agent")
async def agent_endpoint(
    request: AgentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    api_key = credentials.credentials
    
    # Validate
    if not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check permissions
    user = get_user_from_key(api_key)
    if not user.can_access(request.model):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Process
    return await agent.process(request)
```

---

## Error Handling

### Structured Errors

```python
class AgentError(BaseModel):
    error_code: str
    message: str
    details: Optional[dict] = None
    request_id: str

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    error = AgentError(
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        request_id=get_request_id(),
        details={"type": type(exc).__name__}
    )
    return JSONResponse(
        status_code=500,
        content=error.dict()
    )

@app.post("/v1/agent")
async def agent_endpoint(request: AgentRequest):
    try:
        return await agent.process(request)
    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail=AgentError(
                error_code="RATE_LIMITED",
                message="Too many requests",
                request_id=get_request_id()
            ).dict()
        )
```

---

## The API Checklist

- [ ] RESTful endpoints
- [ ] Request/response schemas
- [ ] Validation
- [ ] Authentication
- [ ] Rate limiting
- [ ] Error handling
- [ ] Logging
- [ ] Documentation
- [ ] Versioning
- [ ] Health checks

---

## Conclusion

A good agent API:
- Is predictable
- Handles errors gracefully
- Is well-documented
- Is secure
- Is performant

Design for the developer.
Not for the demo.

---

*ArQon Agentics builds production-grade agent APIs. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
