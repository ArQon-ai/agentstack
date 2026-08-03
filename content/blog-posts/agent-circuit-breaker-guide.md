# Blog Post: The Agent Engineer's Guide to Circuit Breakers
## Published: December 28, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to Circuit Breakers

*Fail fast. Recover gracefully.*

---

## Why Circuit Breakers?

### Problems

- Cascading failures
- Resource exhaustion
- Slow recovery
- Bad user experience

---

## Implementation

### 1. Simple Circuit Breaker

```python
from enum import Enum

class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.state = State.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
    
    async def call(self, func, *args, **kwargs):
        if self.state == State.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = State.HALF_OPEN
            else:
                raise CircuitBreakerOpen("Service unavailable")
        
        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        self.failure_count = 0
        self.state = State.CLOSED
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = State.OPEN
```

### 2. Agent Integration

```python
class ResilientAgent:
    def __init__(self):
        self.llm_breaker = CircuitBreaker(failure_threshold=3)
        self.tool_breaker = CircuitBreaker(failure_threshold=5)
    
    async def generate(self, query: str) -> str:
        return await self.llm_breaker.call(
            self.llm.generate, query
        )
    
    async def use_tool(self, tool_name: str, params: dict):
        return await self.tool_breaker.call(
            self.tools[tool_name].execute, params
        )
```

---

## The Circuit Breaker Checklist

- [ ] Failure threshold
- [ ] Timeout
- [ ] State management
- [ ] Fallback
- [ ] Monitoring
- [ ] Alerting
- [ ] Testing
- [ ] Documentation
- [ ] Integration
- [ ] Recovery

---

## Conclusion

Circuit breakers:
- Prevent cascades
- Enable recovery
- Require tuning
- Need monitoring

Break fast.
Recover gracefully.
Protect users.

---

*ArQon Agentics uses circuit breakers. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
