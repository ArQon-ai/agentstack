# Blog Post: Building Resilient Agents: Circuit Breakers, Retries, and Fallbacks
## Published: August 20, 2026
## Category: Engineering

---

# Building Resilient Agents: Circuit Breakers, Retries, and Fallbacks

*Production agents fail. The question is whether they fail gracefully.*

---

## Why Resilience Matters

In production, these things WILL happen:
- APIs go down
- Models timeout
- Context overflows
- Costs spike
- Networks fail

Your agent needs to handle ALL of them.

---

## Pattern 1: Circuit Breakers

Prevent cascade failures by stopping requests to failing services.

### The Pattern

```
CLOSED → Request succeeds → CLOSED
CLOSED → Request fails → Track failure
CLOSED → Failures exceed threshold → OPEN
OPEN → Block requests → Return fallback
OPEN → Timeout expires → HALF-OPEN
HALF-OPEN → Test request succeeds → CLOSED
HALF-OPEN → Test request fails → OPEN
```

### Implementation

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF-OPEN"
            else:
                raise CircuitBreakerOpen("Service unavailable")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
    
    def _should_attempt_reset(self):
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time > self.recovery_timeout
```

### Usage

```python
breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

@breaker.call
def search_web(query):
    return requests.get(f"https://api.search.com?q={query}")
```

---

## Pattern 2: Retries with Backoff

Automatically retry failed operations with increasing delays.

### Exponential Backoff

```python
import time
import random

def retry_with_backoff(func, max_retries=5, base_delay=1):
    for attempt in range(max_retries):
        try:
            return func()
        except TemporaryError as e:
            if attempt == max_retries - 1:
                raise e
            
            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
```

### When to Retry

**Retry:**
- Network timeouts
- Rate limits (with backoff)
- Temporary service unavailability

**Don't Retry:**
- Invalid input
- Authentication errors
- Resource not found
- Permanent errors

---

## Pattern 3: Fallbacks

Provide alternative responses when primary path fails.

### Fallback Chain

```python
class FallbackAgent:
    def __init__(self, primary, fallback, default_response="I can't help with that right now."):
        self.primary = primary
        self.fallback = fallback
        self.default = default_response
    
    def run(self, query):
        try:
            return self.primary.run(query)
        except Exception as e:
            logger.warning(f"Primary failed: {e}")
            
            try:
                return self.fallback.run(query)
            except Exception as e2:
                logger.error(f"Fallback failed: {e2}")
                return self.default
```

### Fallback Strategies

1. **Simpler Model**
   ```python
   # GPT-4 fails? Try GPT-3.5
   if model == "gpt-4":
       return agent.run_with_model(query, "gpt-3.5")
   ```

2. **Cached Response**
   ```python
   if result := cache.get(query):
       return result
   return "Let me get back to you on that."
   ```

3. **Human Escalation**
   ```python
   if confidence < 0.5:
       return create_support_ticket(query)
   ```

4. **Graceful Degradation**
   ```python
   # Can't do full analysis? Do summary instead
   if complexity > threshold:
       return agent.summarize(query)
   return agent.analyze(query)
   ```

---

## Pattern 4: Timeouts

Prevent operations from running forever.

```python
import signal

class Timeout:
    def __init__(self, seconds):
        self.seconds = seconds
    
    def __enter__(self):
        def handler(signum, frame):
            raise TimeoutError(f"Operation timed out after {self.seconds} seconds")
        
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(self.seconds)
    
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

# Usage
with Timeout(30):
    result = agent.run(query)
```

---

## Pattern 5: Bulkhead Isolation

Prevent failures in one component from affecting others.

```python
class Bulkhead:
    def __init__(self, max_concurrent=10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute(self, coro):
        async with self.semaphore:
            return await coro

# Usage
bulkhead = Bulkhead(max_concurrent=5)

async def process_request(query):
    return await bulkhead.execute(agent.run(query))
```

---

## The Resilience Checklist

Before deploying:

- [ ] Circuit breakers on external APIs
- [ ] Retry logic with backoff
- [ ] Fallback responses defined
- [ ] Timeouts on all operations
- [ ] Bulkhead isolation
- [ ] Graceful degradation paths
- [ ] Human escalation triggers
- [ ] Error logging and alerting
- [ ] Recovery procedures documented

---

## Conclusion

Resilience isn't an afterthought.
It's a core requirement.

Build it in from the start.
Test it regularly.
Monitor it continuously.

---

*ArQon Agentics builds resilient, production-grade agentic systems. Get the open-source framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
