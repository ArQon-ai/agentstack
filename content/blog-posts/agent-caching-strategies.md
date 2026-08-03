# Blog Post: The Agent Engineer's Guide to Caching Strategies
## Published: October 23, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to Caching Strategies

*Cache smarter. Reduce costs. Improve latency.*

---

## Why Cache Agents?

### Cost Reduction

LLM calls are expensive:
- GPT-4: $0.03/1K input tokens
- Claude 3.5: $0.003/1K input tokens
- Repeated queries = wasted money

### Latency Improvement

Cache hits:
- Redis: ~1ms
- LLM API: ~2-5s
- 1000x faster

### Rate Limit Protection

Provider limits:
- OpenAI: 60 RPM (tier 1)
- Cache reduces API calls

---

## Caching Strategies

### 1. Exact Match Cache

```python
class ExactMatchCache:
    def __init__(self, redis, ttl=3600):
        self.redis = redis
        self.ttl = ttl
    
    def _make_key(self, query, model, temperature):
        # Include all parameters that affect output
        key_data = f"{query}:{model}:{temperature}"
        return f"cache:exact:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    async def get(self, query, model="gpt-4", temperature=0.7):
        key = self._make_key(query, model, temperature)
        cached = await self.redis.get(key)
        
        if cached:
            return json.loads(cached)
        
        return None
    
    async def set(self, query, response, model="gpt-4", temperature=0.7):
        key = self._make_key(query, model, temperature)
        
        await self.redis.setex(
            key,
            self.ttl,
            json.dumps({
                "response": response,
                "cached_at": datetime.now().isoformat()
            })
        )
```

### 2. Semantic Cache

```python
class SemanticCache:
    def __init__(self, vector_store, embedder, threshold=0.95):
        self.vector_store = vector_store
        self.embedder = embedder
        self.threshold = threshold
    
    async def get(self, query):
        # Embed query
        query_embedding = await self.embedder.embed(query)
        
        # Search similar queries
        results = await self.vector_store.search(
            vector=query_embedding,
            top_k=3
        )
        
        for result in results:
            if result.score > self.threshold:
                return result.metadata["response"]
        
        return None
    
    async def set(self, query, response):
        embedding = await self.embedder.embed(query)
        
        await self.vector_store.upsert(
            id=f"cache:{hash(query)}",
            vector=embedding,
            metadata={
                "query": query,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
        )
```

### 3. Embedding Cache

```python
class EmbeddingCache:
    def __init__(self, redis):
        self.redis = redis
    
    async def get_embedding(self, text):
        key = f"embedding:{hashlib.md5(text.encode()).hexdigest()}"
        
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        # Generate embedding
        embedding = await self.embedder.embed(text)
        
        # Cache forever (embeddings don't change)
        await self.redis.set(key, json.dumps(embedding))
        
        return embedding
```

### 4. Multi-Tier Cache

```python
class MultiTierCache:
    def __init__(self, l1_cache, l2_cache, l3_cache):
        self.l1 = l1_cache  # In-memory (fastest)
        self.l2 = l2_cache  # Redis (fast)
        self.l3 = l3_cache  # Disk (persistent)
    
    async def get(self, key):
        # Try L1
        if value := self.l1.get(key):
            return value
        
        # Try L2
        if value := await self.l2.get(key):
            # Promote to L1
            self.l1.set(key, value)
            return value
        
        # Try L3
        if value := await self.l3.get(key):
            # Promote to L2 and L1
            await self.l2.set(key, value)
            self.l1.set(key, value)
            return value
        
        return None
    
    async def set(self, key, value):
        # Set in all tiers
        self.l1.set(key, value)
        await self.l2.set(key, value)
        await self.l3.set(key, value)
```

---

## Cache Invalidation

### Time-Based

```python
class TTLCache:
    def __init__(self, default_ttl=3600):
        self.default_ttl = default_ttl
        self.ttls = {}
    
    async def set(self, key, value, ttl=None):
        ttl = ttl or self.default_ttl
        
        await self.storage.set(key, value)
        self.ttls[key] = time.time() + ttl
    
    async def get(self, key):
        if key in self.ttls:
            if time.time() > self.ttls[key]:
                await self.delete(key)
                return None
        
        return await self.storage.get(key)
```

### Event-Based

```python
class EventInvalidator:
    def __init__(self, cache):
        self.cache = cache
        self.subscriptions = {}
    
    def subscribe(self, event_type, key_pattern):
        if event_type not in self.subscriptions:
            self.subscriptions[event_type] = []
        
        self.subscriptions[event_type].append(key_pattern)
    
    async def handle_event(self, event):
        event_type = event["type"]
        
        if event_type in self.subscriptions:
            for pattern in self.subscriptions[event_type]:
                # Invalidate matching keys
                keys = await self.cache.keys(pattern)
                for key in keys:
                    await self.cache.delete(key)
```

---

## Cache Metrics

### Hit Rate Monitoring

```python
class CacheMetrics:
    def __init__(self):
        self.hits = Counter("cache_hits", ["tier"])
        self.misses = Counter("cache_misses", ["tier"])
        self.latency = Histogram("cache_latency_seconds", ["tier", "operation"])
    
    def record_hit(self, tier):
        self.hits.labels(tier=tier).inc()
    
    def record_miss(self, tier):
        self.misses.labels(tier=tier).inc()
    
    def get_hit_rate(self, tier):
        hits = self.hits.labels(tier=tier)._value.get()
        misses = self.misses.labels(tier=tier)._value.get()
        
        total = hits + misses
        return hits / total if total > 0 else 0
```

### Cost Savings

```python
class CostSavingsTracker:
    def __init__(self):
        self.requests_saved = 0
        self.tokens_saved = 0
        self.cost_per_request = 0.05  # Average
    
    def record_cache_hit(self, tokens):
        self.requests_saved += 1
        self.tokens_saved += tokens
    
    def get_savings(self):
        return {
            "requests_saved": self.requests_saved,
            "tokens_saved": self.tokens_saved,
            "cost_saved": self.requests_saved * self.cost_per_request
        }
```

---

## The Caching Checklist

- [ ] Identify cacheable operations
- [ ] Choose cache tier (memory/redis/disk)
- [ ] Implement exact match cache
- [ ] Implement semantic cache
- [ ] Cache embeddings
- [ ] Set appropriate TTLs
- [ ] Add cache metrics
- [ ] Monitor hit rates
- [ ] Track cost savings
- [ ] Implement invalidation
- [ ] Test edge cases
- [ ] Document cache strategy

---

## Conclusion

Caching:
- Reduces costs by 30-50%
- Improves latency by 1000x
- Protects rate limits
- Requires strategy

Cache everything you can.
Measure the impact.

---

*ArQon Agentics builds agents with smart caching. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
