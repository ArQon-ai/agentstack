# SEO Article: AI Agent Memory: Short-Term, Long-Term, and Beyond
**Target Keywords:** agent memory, LLM memory, agent state  
**Published:** November 7, 2026

---

# AI Agent Memory: Short-Term, Long-Term, and Beyond

*Give your agents perfect recall.*

---

## Types of Memory

### 1. Short-Term Memory (Working Memory)

```python
class ShortTermMemory:
    """In-session context"""
    
    def __init__(self, max_messages=10):
        self.messages = []
        self.max_messages = max_messages
    
    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        
        # Keep only recent messages
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def get_context(self) -> str:
        return "\n".join([
            f"{m['role']}: {m['content']}"
            for m in self.messages
        ])
```

### 2. Long-Term Memory

```python
class LongTermMemory:
    """Persistent storage"""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    async def store(self, key: str, value: str, metadata: dict = None):
        # Store in vector DB
        await self.vector_store.upsert(
            id=key,
            vector=await self.embed(value),
            metadata=metadata or {}
        )
    
    async def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        # Semantic search
        results = await self.vector_store.search(
            vector=await self.embed(query),
            top_k=top_k
        )
        return results
```

### 3. Episodic Memory

```python
class EpisodicMemory:
    """Event-based memory"""
    
    def __init__(self, db):
        self.db = db
    
    async def record_episode(self, event: str, outcome: str, success: bool):
        await self.db.execute(
            """INSERT INTO episodes (event, outcome, success, timestamp)
               VALUES ($1, $2, $3, NOW())""",
            event, outcome, success
        )
    
    async def get_similar_episodes(self, event: str) -> list[dict]:
        return await self.db.fetch(
            """SELECT * FROM episodes
               WHERE event ILIKE $1
               ORDER BY timestamp DESC
               LIMIT 10""",
            f"%{event}%"
        )
```

---

## Memory Management

### Forgetting Strategy

```python
class ForgettingMemory:
    def __init__(self, decay_rate=0.1):
        self.memories = {}
        self.decay_rate = decay_rate
    
    def add(self, key: str, value: str, importance: float = 1.0):
        self.memories[key] = {
            "value": value,
            "importance": importance,
            "last_accessed": time.time(),
            "access_count": 1
        }
    
    def retrieve(self, key: str) -> str | None:
        if key not in self.memories:
            return None
        
        memory = self.memories[key]
        memory["access_count"] += 1
        memory["last_accessed"] = time.time()
        
        return memory["value"]
    
    def decay(self):
        """Reduce importance of old memories"""
        now = time.time()
        
        for key, memory in list(self.memories.items()):
            age = now - memory["last_accessed"]
            memory["importance"] *= (1 - self.decay_rate) ** (age / 86400)
            
            # Remove if importance too low
            if memory["importance"] < 0.1:
                del self.memories[key]
```

### Memory Consolidation

```python
class MemoryConsolidator:
    def __init__(self, llm):
        self.llm = llm
    
    async def consolidate(self, memories: list[str]) -> str:
        prompt = f"""Summarize these memories into a concise summary:

Memories:
{chr(10).join(f"- {m}" for m in memories)}

Summary:"""
        
        return await self.llm.generate(prompt)
```

---

## Memory Storage Options

### Comparison

| Storage | Speed | Capacity | Cost | Use Case |
|---------|-------|----------|------|----------|
| In-Memory | Fastest | Limited | Free | Working memory |
| Redis | Fast | Medium | Low | Session cache |
| PostgreSQL | Medium | Large | Low | Structured data |
| Pinecone | Fast | Unlimited | Medium | Vector search |
| S3 | Slow | Unlimited | Low | Archive |

### Hybrid Approach

```python
class HybridMemory:
    def __init__(self):
        self.working = ShortTermMemory()
        self.cache = RedisCache()
        self.persistent = PostgreSQLStore()
        self.archive = S3Storage()
    
    async def store(self, key: str, value: str, importance: float):
        # Always store in working memory
        self.working.add(key, value)
        
        # Cache if recently used
        if importance > 0.5:
            await self.cache.set(key, value, ttl=3600)
        
        # Persist if important
        if importance > 0.8:
            await self.persistent.store(key, value)
    
    async def retrieve(self, key: str) -> str | None:
        # Check working memory
        if value := self.working.get(key):
            return value
        
        # Check cache
        if value := await self.cache.get(key):
            self.working.add(key, value)
            return value
        
        # Check persistent
        if value := await self.persistent.get(key):
            await self.cache.set(key, value)
            return value
        
        return None
```

---

## The Memory Checklist

- [ ] Choose memory types
- [ ] Implement short-term
- [ ] Implement long-term
- [ ] Add forgetting
- [ ] Consolidate memories
- [ ] Choose storage
- [ ] Implement hybrid
- [ ] Monitor memory usage
- [ ] Optimize retrieval
- [ ] Test edge cases

---

## Conclusion

Agent memory:
- Enables context
- Improves responses
- Requires management
- Needs strategy

Remember wisely.
Forget strategically.
Retrieve efficiently.

---

*ArQon Agentics builds agents with perfect memory. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
