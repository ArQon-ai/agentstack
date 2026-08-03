# Blog Post: The Agent Engineer's Guide to Rate Limiting
## Published: February 2, 2027
## Category: Engineering

---

# The Agent Engineer's Guide to Rate Limiting

*Protect resources. Ensure fairness.*

---

## Why Rate Limiting?

### Benefits

- Prevent abuse
- Ensure fairness
- Control costs
- Maintain stability

---

## Implementation

### 1. Token Bucket

```python
import redis
import time

class TokenBucket:
    def __init__(self, redis_client, key: str, capacity: int, refill_rate: float):
        self.redis = redis_client
        self.key = key
        self.capacity = capacity
        self.refill_rate = refill_rate
    
    def is_allowed(self, tokens: int = 1) -> bool:
        pipe = self.redis.pipeline()
        now = time.time()
        
        # Get current state
        pipe.hmget(self.key, 'tokens', 'last_refill')
        result = pipe.execute()
        
        current_tokens = float(result[0][0] or self.capacity)
        last_refill = float(result[0][1] or now)
        
        # Calculate new tokens
        elapsed = now - last_refill
        new_tokens = min(
            self.capacity,
            current_tokens + elapsed * self.refill_rate
        )
        
        # Check and update
        if new_tokens >= tokens:
            pipe.hmset(self.key, {
                'tokens': new_tokens - tokens,
                'last_refill': now
            })
            pipe.execute()
            return True
        
        return False
```

### 2. Redis Rate Limiter

```python
class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def check_rate_limit(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        current = await self.redis.get(key)
        
        if current is None:
            await self.redis.setex(key, window, 1)
            return True, limit - 1
        
        current = int(current)
        if current >= limit:
            return False, 0
        
        await self.redis.incr(key)
        return True, limit - current - 1
```

---

## The Rate Limiting Checklist

- [ ] Algorithm choice
- [ ] Limit configuration
- [ ] Key design
- [ ] Headers
- [ ] Error handling
- [ ] Monitoring
- [ ] Testing
- [ ] Documentation
- [ ] Gradual rollout
- [ ] Customer communication

---

## Conclusion

Rate limiting:
- Protects resources
- Ensures fairness
- Controls costs
- Requires tuning

Limit requests.
Protect services.
Stay stable.

---

*ArQon Agentics limits rates. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
