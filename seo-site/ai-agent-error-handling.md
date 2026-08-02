# SEO Article: AI Agent Error Handling: Production Patterns
**Target Keywords:** agent error handling, LLM error patterns, agent failure recovery  
**Published:** September 13, 2026

---

# AI Agent Error Handling: Production Patterns

Agents fail. How you handle it determines whether you have a product or a liability.

---

## Error Types

### 1. LLM Errors

```python
class LLMError(Exception):
    pass

class RateLimitError(LLMError):
    pass

class TimeoutError(LLMError):
    pass

class ContextLengthError(LLMError):
    pass

class ContentFilterError(LLMError):
    pass
```

### 2. Tool Errors

```python
class ToolError(Exception):
    pass

class ToolNotFoundError(ToolError):
    pass

class ToolExecutionError(ToolError):
    pass

class ToolTimeoutError(ToolError):
    pass
```

### 3. System Errors

```python
class SystemError(Exception):
    pass

class DatabaseError(SystemError):
    pass

class CacheError(SystemError):
    pass

class ValidationError(SystemError):
    pass
```

---

## Error Handling Patterns

### Pattern 1: Retry with Backoff

```python
import time
import random

async def retry_with_backoff(func, max_retries=5, base_delay=1):
    for attempt in range(max_retries):
        try:
            return await func()
        except (RateLimitError, TimeoutError) as e:
            if attempt == max_retries - 1:
                raise e
            
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            await asyncio.sleep(delay)
```

### Pattern 2: Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure = None
        self.state = "CLOSED"
    
    async def call(self, func):
        if self.state == "OPEN":
            if time.time() - self.last_failure > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpen("Service unavailable")
        
        try:
            result = await func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
```

### Pattern 3: Fallback Chain

```python
class FallbackChain:
    def __init__(self, strategies):
        self.strategies = strategies
    
    async def execute(self, task):
        for strategy in self.strategies:
            try:
                return await strategy(task)
            except Exception as e:
                logger.warning(f"Strategy failed: {e}")
                continue
        
        raise AllStrategiesFailed("No strategy succeeded")

# Usage
chain = FallbackChain([
    lambda t: primary_model.generate(t),
    lambda t: fallback_model.generate(t),
    lambda t: cached_response(t),
    lambda t: default_response(t)
])
```

### Pattern 4: Graceful Degradation

```python
class GracefulAgent:
    async def run(self, query):
        try:
            # Full capability
            return await self.full_response(query)
        except ContextLengthError:
            # Reduce context
            return await self.reduced_context_response(query)
        except TimeoutError:
            # Simpler response
            return await self.simple_response(query)
        except Exception:
            # Minimal response
            return await self.minimal_response(query)
```

---

## Error Recovery

### Recovery Strategies

```python
class ErrorRecovery:
    def __init__(self):
        self.strategies = {
            RateLimitError: self.handle_rate_limit,
            TimeoutError: self.handle_timeout,
            ContextLengthError: self.handle_context_length,
            ToolExecutionError: self.handle_tool_error
        }
    
    async def recover(self, error, context):
        handler = self.strategies.get(type(error))
        if handler:
            return await handler(context)
        return await self.default_recovery(context)
    
    async def handle_rate_limit(self, context):
        await asyncio.sleep(60)
        return await context.retry()
    
    async def handle_timeout(self, context):
        context.use_faster_model()
        return await context.retry()
    
    async def handle_context_length(self, context):
        context.trim_context()
        return await context.retry()
```

---

## Monitoring Errors

### Error Metrics

```python
error_metrics = {
    "llm_errors": Counter("agent_llm_errors_total", ["type"]),
    "tool_errors": Counter("agent_tool_errors_total", ["tool", "error"]),
    "system_errors": Counter("agent_system_errors_total", ["component"]),
    "recovery_success": Counter("agent_recovery_success_total"),
    "recovery_failure": Counter("agent_recovery_failure_total")
}
```

### Alerting

```yaml
rules:
  - name: HighErrorRate
    condition: error_rate > 5%
    action: page_oncall
    
  - name: LLMFailing
    condition: llm_error_rate > 10%
    action: switch_provider
    
  - name: ToolBroken
    condition: tool_error_rate > 20%
    action: disable_tool
```

---

## The Error Handling Checklist

- [ ] All LLM errors caught
- [ ] All tool errors caught
- [ ] Retry with backoff
- [ ] Circuit breakers
- [ ] Fallback responses
- [ ] Graceful degradation
- [ ] Error logging
- [ ] Error metrics
- [ ] Alerting rules
- [ ] Recovery procedures
- [ ] User-friendly error messages
- [ ] Escalation paths

---

## Conclusion

Error handling is not optional.
It's core to production readiness.

Build for failure.
Plan for recovery.
Monitor everything.

---

*ArQon Agentics builds agents with production-grade error handling. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
