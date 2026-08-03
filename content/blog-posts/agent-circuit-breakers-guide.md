# Blog Post: The Agent Engineer's Guide to Circuit Breakers
## Published: February 26, 2027
## Category: Engineering

---

# The Agent Engineer's Guide to Circuit Breakers

*Fail fast. Recover smart.*

---

## Why Circuit Breakers?

### Benefits

- Fail fast
- Prevent cascading
- Auto-recover
- Graceful degradation

---

## Implementation

### 1. Circuit Breaker Pattern

```python
from enum import Enum
import asyncio
import time

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
    
    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.half_open_calls = 0
            else:
                raise CircuitBreakerOpen("Service temporarily unavailable")
        
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.half_open_max_calls:
                raise CircuitBreakerOpen("Too many half-open calls")
            self.half_open_calls += 1
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.half_open_calls = 0
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        return time.time() - self.last_failure_time >= self.recovery_timeout
```

### 2. LLM Circuit Breaker

```python
class LLMCircuitBreaker:
    def __init__(self):
        self.breakers = {
            "openai": CircuitBreaker(failure_threshold=3, recovery_timeout=30),
            "anthropic": CircuitBreaker(failure_threshold=3, recovery_timeout=30),
            "local": CircuitBreaker(failure_threshold=5, recovery_timeout=60)
        }
    
    async def generate(self, prompt: str, preferred: str = "openai") -> str:
        providers = [preferred] + [p for p in self.breakers if p != preferred]
        
        for provider in providers:
            breaker = self.breakers[provider]
            try:
                return await breaker.call(self._generate_with, provider, prompt)
            except CircuitBreakerOpen:
                continue
            except Exception:
                continue
        
        raise Exception("All providers unavailable")
    
    async def _generate_with(self, provider: str, prompt: str) -> str:
        # Implementation
        pass
```

---

## The Circuit Breaker Checklist

- [ ] Failure threshold
- [ ] Recovery timeout
- [ ] Half-open state
- [ ] Fallback strategy
- [ ] Metrics
- [ ] Alerting
- [ ] Testing
- [ ] Documentation
- [ ] Monitoring
- [ ] Tuning

---

## Conclusion

Circuit breakers:
- Prevent cascades
- Enable recovery
- Require tuning
- Need fallbacks

Fail fast.
Recover smart.
Stay resilient.

---

*ArQon Agentics uses circuit breakers. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
