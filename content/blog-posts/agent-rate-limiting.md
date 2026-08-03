# Blog Post: The Agent Engineer's Guide to Rate Limiting
## Published: October 21, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to Rate Limiting

*Protect your agents. Protect your wallet. Protect your users.*

---

## Why Rate Limit?

### The Risks

1. **Cost Overruns**
   - Unlimited requests = unlimited bills
   - Burst traffic = surprise invoices
   - Abuse = financial damage

2. **Service Degradation**
   - Too many requests = slow responses
   - Resource exhaustion = downtime
   - Queue buildup = timeouts

3. **Provider Limits**
   - OpenAI: 60 RPM (tier 1)
   - Anthropic: 40 RPM (tier 1)
   - Exceeding = errors

---

## Rate Limiting Strategies

### 1. Token Bucket

```python
import time
from threading import Lock

class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate = rate  # tokens per second
        self.capacity = capacity  # max tokens
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = Lock()
    
    def consume(self, tokens=1):
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Add tokens based on elapsed time
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now
            
            # Check if we can consume
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def wait_time(self, tokens=1):
        with self.lock:
            if self.tokens >= tokens:
                return 0
            
            return (tokens - self.tokens) / self.rate
```

### 2. Sliding Window

```python
from collections import deque
import time

class SlidingWindow:
    def __init__(self, window_size, max_requests):
        self.window_size = window_size  # seconds
        self.max_requests = max_requests
        self.requests = deque()
        self.lock = Lock()
    
    def allow_request(self):
        with self.lock:
            now = time.time()
            
            # Remove old requests
            while self.requests and self.requests[0] < now - self.window_size:
                self.requests.popleft()
            
            # Check if we can allow
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    def get_window_stats(self):
        with self.lock:
            now = time.time()
            
            # Clean old requests
            while self.requests and self.requests[0] < now - self.window_size:
                self.requests.popleft()
            
            return {
                "current_requests": len(self.requests),
                "max_requests": self.max_requests,
                "window_size": self.window_size,
                "remaining": self.max_requests - len(self.requests)
            }
```

### 3. Fixed Window

```python
class FixedWindow:
    def __init__(self, window_size, max_requests):
        self.window_size = window_size
        self.max_requests = max_requests
        self.current_window = int(time.time() / window_size)
        self.current_count = 0
        self.lock = Lock()
    
    def allow_request(self):
        with self.lock:
            now = int(time.time() / self.window_size)
            
            # Reset if new window
            if now > self.current_window:
                self.current_window = now
                self.current_count = 0
            
            # Check limit
            if self.current_count < self.max_requests:
                self.current_count += 1
                return True
            
            return False
```

---

## Multi-Level Rate Limiting

### Per-User + Global

```python
class MultiLevelRateLimiter:
    def __init__(self, redis):
        self.redis = redis
        self.limits = {
            "user": {"rpm": 60, "rph": 1000},
            "global": {"rpm": 1000, "rph": 50000}
        }
    
    async def check(self, user_id):
        # Check user limit
        user_key = f"rate_limit:user:{user_id}"
        user_allowed = await self._check_limit(user_key, self.limits["user"])
        
        if not user_allowed:
            return False, "User rate limit exceeded"
        
        # Check global limit
        global_key = "rate_limit:global"
        global_allowed = await self._check_limit(global_key, self.limits["global"])
        
        if not global_allowed:
            return False, "Global rate limit exceeded"
        
        return True, None
    
    async def _check_limit(self, key, limits):
        pipe = self.redis.pipeline()
        
        # Check per-minute
        minute_key = f"{key}:minute:{int(time.time() / 60)}"
        pipe.incr(minute_key)
        pipe.expire(minute_key, 120)
        
        # Check per-hour
        hour_key = f"{key}:hour:{int(time.time() / 3600)}"
        pipe.incr(hour_key)
        pipe.expire(hour_key, 7200)
        
        results = await pipe.execute()
        minute_count = results[0]
        hour_count = results[2]
        
        return (minute_count <= limits["rpm"] and 
                hour_count <= limits["rph"])
```

---

## LLM-Specific Rate Limiting

### Token-Based Limits

```python
class TokenRateLimiter:
    def __init__(self, max_tokens_per_minute=100000):
        self.max_tokens = max_tokens_per_minute
        self.tokens_used = 0
        self.window_start = time.time()
    
    async def check_request(self, estimated_tokens):
        now = time.time()
        
        # Reset window
        if now - self.window_start > 60:
            self.tokens_used = 0
            self.window_start = now
        
        # Check if request fits
        if self.tokens_used + estimated_tokens > self.max_tokens:
            return False, f"Token limit exceeded. Used: {self.tokens_used}"
        
        self.tokens_used += estimated_tokens
        return True, None
```

### Cost-Based Limits

```python
class CostRateLimiter:
    def __init__(self, daily_budget=100):
        self.daily_budget = daily_budget
        self.daily_cost = 0
        self.last_reset = time.time()
    
    async def check_cost(self, estimated_cost):
        now = time.time()
        
        # Reset daily budget
        if now - self.last_reset > 86400:
            self.daily_cost = 0
            self.last_reset = now
        
        # Check budget
        if self.daily_cost + estimated_cost > self.daily_budget:
            return False, f"Daily budget exceeded. Spent: ${self.daily_cost}"
        
        self.daily_cost += estimated_cost
        return True, None
```

---

## Handling Rate Limit Exceeded

### Queue and Retry

```python
class QueuedRateLimiter:
    def __init__(self, limiter):
        self.limiter = limiter
        self.queue = asyncio.Queue()
        self.processing = False
    
    async def submit(self, request):
        await self.queue.put(request)
        
        if not self.processing:
            asyncio.create_task(self._process_queue())
    
    async def _process_queue(self):
        self.processing = True
        
        while not self.queue.empty():
            request = await self.queue.get()
            
            # Wait for rate limit
            while not self.limiter.allow_request():
                await asyncio.sleep(1)
            
            # Process request
            await self.process(request)
        
        self.processing = False
```

### Exponential Backoff

```python
class ExponentialBackoff:
    def __init__(self, base_delay=1, max_delay=60):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.attempts = 0
    
    def get_delay(self):
        delay = min(
            self.base_delay * (2 ** self.attempts),
            self.max_delay
        )
        self.attempts += 1
        return delay
    
    def reset(self):
        self.attempts = 0
```

---

## The Rate Limiting Checklist

- [ ] Define rate limits (per user, per global)
- [ ] Choose algorithm (token bucket, sliding window)
- [ ] Implement token-based limits
- [ ] Implement cost-based limits
- [ ] Add queue for exceeded limits
- [ ] Implement retry with backoff
- [ ] Monitor rate limit hits
- [ ] Alert on abuse
- [ ] Document limits
- [ ] Test edge cases

---

## Conclusion

Rate limiting:
- Controls costs
- Prevents abuse
- Ensures fairness
- Protects service

Limit everything.
Measure everything.
Protect everything.

---

*ArQon Agentics builds agents with production-grade rate limiting. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
