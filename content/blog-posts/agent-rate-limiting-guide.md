# Blog Post: The Agent Engineer's Guide to Rate Limiting
## Published: December 6, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to Rate Limiting

*Protect your agents. Control costs.*

---

## Why Rate Limit?

### Cost Control

- Prevent runaway costs
- Protect budget
- Enable scaling

### Fairness

- Prevent abuse
- Ensure availability
- Protect users

---

## Rate Limiting Strategies

### 1. Token Bucket

```python
class TokenBucket:
    def __init__(self, rate: int, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        now = time.time()
        elapsed = now - self.last_update
        
        # Add tokens
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate
        )
        self.last_update = now
        
        # Consume
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        return False
```

### 2. Sliding Window

```python
class SlidingWindow:
    def __init__(self, window: int, limit: int):
        self.window = window
        self.limit = limit
        self.requests = []
    
    def allow(self) -> bool:
        now = time.time()
        
        # Remove old requests
        self.requests = [
            req for req in self.requests
            if now - req < self.window
        ]
        
        # Check limit
        if len(self.requests) < self.limit:
            self.requests.append(now)
            return True
        
        return False
```

### 3. Per-User Limits

```python
class UserRateLimiter:
    def __init__(self):
        self.buckets: dict[str, TokenBucket] = {}
    
    def get_bucket(self, user_id: str) -> TokenBucket:
        if user_id not in self.buckets:
            self.buckets[user_id] = TokenBucket(
                rate=10,  # 10 requests/minute
                capacity=100  # burst
            )
        return self.buckets[user_id]
    
    def allow_request(self, user_id: str) -> bool:
        bucket = self.get_bucket(user_id)
        return bucket.consume()
```

---

## The Rate Limiting Checklist

- [ ] Define limits
- [ ] Choose algorithm
- [ ] Per-user tracking
- [ ] Global limits
- [ ] Burst handling
- [ ] Error responses
- [ ] Headers (X-RateLimit-*)
- [ ] Monitoring
- [ ] Alerts
- [ ] Documentation

---

## Conclusion

Rate limiting:
- Controls costs
- Prevents abuse
- Ensures fairness
- Requires planning

Limit everything.
Monitor always.
Scale safely.

---

*ArQon Agentics limits rates. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
