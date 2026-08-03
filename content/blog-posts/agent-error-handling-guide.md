# Blog Post: The Agent Engineer's Guide to Error Handling
## Published: October 29, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to Error Handling

*Handle errors gracefully. Your users will thank you.*

---

## Types of Errors

### 1. LLM Errors

```python
class LLMError(Exception):
    """Base class for LLM errors"""
    pass

class RateLimitError(LLMError):
    """Hit rate limit"""
    pass

class TokenLimitError(LLMError):
    """Exceeded token limit"""
    pass

class InvalidResponseError(LLMError):
    """LLM returned invalid response"""
    pass

class LLMTimeoutError(LLMError):
    """LLM request timed out"""
    pass
```

### 2. Tool Errors

```python
class ToolError(Exception):
    """Base class for tool errors"""
    pass

class ToolNotFoundError(ToolError):
    """Tool doesn't exist"""
    pass

class ToolExecutionError(ToolError):
    """Tool execution failed"""
    pass

class ToolTimeoutError(ToolError):
    """Tool execution timed out"""
    pass

class ToolValidationError(ToolError):
    """Tool parameters invalid"""
    pass
```

### 3. Agent Errors

```python
class AgentError(Exception):
    """Base class for agent errors"""
    pass

class PlanError(AgentError):
    """Failed to create plan"""
    pass

class ExecutionError(AgentError):
    """Failed to execute step"""
    pass

class MemoryError(AgentError):
    """Memory operation failed"""
    pass

class ContextError(AgentError):
    """Context retrieval failed"""
    pass
```

---

## Error Handling Strategies

### Retry with Exponential Backoff

```python
import asyncio
from functools import wraps

def retry(max_attempts=3, backoff=2, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    
                    wait = backoff ** attempt
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
                    await asyncio.sleep(wait)
        return wrapper
    return decorator

# Usage
@retry(max_attempts=3, backoff=2, exceptions=(RateLimitError, LLMTimeoutError))
async def call_llm(prompt):
    return await llm_client.generate(prompt)
```

### Fallback Models

```python
class FallbackLLM:
    def __init__(self, primary, fallback):
        self.primary = primary
        self.fallback = fallback
    
    async def generate(self, prompt):
        try:
            return await self.primary.generate(prompt)
        except (RateLimitError, LLMTimeoutError) as e:
            logger.warning(f"Primary failed: {e}. Using fallback.")
            return await self.fallback.generate(prompt)
```

### Graceful Degradation

```python
class GracefulAgent:
    async def run(self, query):
        try:
            # Try full pipeline
            return await self.full_pipeline(query)
        except ToolError:
            # Degrade to simpler response
            logger.warning("Tools failed, using LLM only")
            return await self.llm_only(query)
        except LLMError:
            # Degrade to cached response
            logger.warning("LLM failed, using cache")
            return await self.cached_response(query)
        except Exception:
            # Ultimate fallback
            logger.error("Everything failed")
            return self.generic_response()
```

---

## Error Recovery

### Self-Healing

```python
class SelfHealingAgent:
    async def run(self, query):
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                return await self.execute(query)
            except PlanError:
                # Regenerate plan
                self.plan = await self.regenerate_plan(query)
            except ToolExecutionError as e:
                # Try alternative tool
                self.plan = await self.find_alternative(e.tool)
            except LLMError:
                # Switch model
                self.llm = self.get_backup_model()
        
        # If all attempts fail
        return self.error_response("Unable to complete request")
```

### Checkpoint Recovery

```python
class CheckpointAgent:
    def __init__(self):
        self.checkpoints = []
    
    async def execute_with_checkpoints(self, query):
        try:
            # Step 1: Plan
            plan = await self.plan(query)
            self.save_checkpoint("plan", plan)
            
            # Step 2: Execute
            results = []
            for i, step in enumerate(plan.steps):
                result = await self.execute_step(step)
                results.append(result)
                self.save_checkpoint(f"step_{i}", results)
            
            # Step 3: Respond
            return await self.generate_response(results)
            
        except Exception as e:
            # Restore from last checkpoint
            checkpoint = self.get_last_checkpoint()
            return await self.recover_from_checkpoint(checkpoint, e)
```

---

## User-Facing Errors

### Error Classification

```python
class ErrorClassifier:
    def classify(self, error: Exception) -> str:
        if isinstance(error, RateLimitError):
            return "temporary"  # User can retry
        elif isinstance(error, TokenLimitError):
            return "user_error"  # User needs to change input
        elif isinstance(error, ToolExecutionError):
            return "system_error"  # System issue, not user's fault
        else:
            return "unknown"
    
    def get_user_message(self, classification: str) -> str:
        messages = {
            "temporary": "Service temporarily unavailable. Please try again.",
            "user_error": "Your request was too long. Please try a shorter query.",
            "system_error": "Something went wrong on our end. We're working on it.",
            "unknown": "An unexpected error occurred. Please try again."
        }
        return messages.get(classification, messages["unknown"])
```

---

## Monitoring Errors

### Error Tracking

```python
class ErrorTracker:
    def __init__(self):
        self.errors = Counter("agent_errors_total", ["type", "severity"])
        self.error_rate = Gauge("agent_error_rate")
    
    async def track(self, error: Exception, context: dict = None):
        error_type = type(error).__name__
        severity = "high" if isinstance(error, AgentError) else "medium"
        
        self.errors.labels(type=error_type, severity=severity).inc()
        
        # Log with context
        logger.error(
            "agent_error",
            error=error_type,
            message=str(error),
            context=context,
            severity=severity
        )
        
        # Alert if high severity
        if severity == "high":
            await self.alert(error, context)
```

---

## The Error Handling Checklist

- [ ] Define error hierarchy
- [ ] Implement retries
- [ ] Add fallback models
- [ ] Graceful degradation
- [ ] Self-healing logic
- [ ] Checkpoint recovery
- [ ] User-friendly messages
- [ ] Error tracking
- [ ] Alerting
- [ ] Post-mortems
- [ ] Test error scenarios
- [ ] Document recovery procedures

---

## Conclusion

Error handling:
- Is not optional
- Requires planning
- Needs monitoring
- Enables reliability

Expect failures.
Handle gracefully.
Recover automatically.

---

*ArQon Agentics builds resilient agents. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
