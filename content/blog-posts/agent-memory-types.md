# Blog Post: Agent Memory: Short-Term vs Long-Term vs External
## Published: September 4, 2026
## Category: Engineering

---

# Agent Memory: Short-Term vs Long-Term vs External

*How to give your agent a memory that actually works.*

---

## The Memory Problem

Agents without memory are stateless.
They forget everything between requests.

This is fine for simple tasks.
Terrible for conversations, workflows, and personalization.

---

## Type 1: Short-Term Memory (Conversation Context)

**What:** Recent messages in the current conversation.

**How it works:**
```python
class ShortTermMemory:
    def __init__(self, max_messages=10):
        self.messages = []
        self.max_messages = max_messages
    
    def add(self, role, content):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def get_context(self):
        return self.messages
```

**When to use:**
- Conversations
- Multi-turn tasks
- Context-dependent responses

**Limitations:**
- Limited by token budget
- Forgets older context
- No persistence

---

## Type 2: Long-Term Memory (User Profile)

**What:** Persistent information about the user.

**How it works:**
```python
class LongTermMemory:
    def __init__(self, db):
        self.db = db
    
    def remember(self, user_id, key, value):
        self.db.execute(
            "INSERT INTO user_memory (user_id, key, value) VALUES (?, ?, ?)",
            (user_id, key, json.dumps(value))
        )
    
    def recall(self, user_id, key):
        result = self.db.execute(
            "SELECT value FROM user_memory WHERE user_id = ? AND key = ?",
            (user_id, key)
        ).fetchone()
        return json.loads(result[0]) if result else None
```

**When to use:**
- User preferences
- Historical behavior
- Learned patterns
- Personalization

**Limitations:**
- Requires database
- Needs schema design
- Privacy concerns

---

## Type 3: External Memory (Knowledge Base)

**What:** Information from external sources.

**How it works:**
```python
class ExternalMemory:
    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    def retrieve(self, query, top_k=5):
        # Convert query to embedding
        embedding = self.embed(query)
        
        # Search vector store
        results = self.vector_store.search(embedding, top_k)
        
        return results
    
    def add_documents(self, documents):
        for doc in documents:
            embedding = self.embed(doc.content)
            self.vector_store.add(embedding, doc)
```

**When to use:**
- Product documentation
- Company knowledge
- Domain expertise
- FAQs

**Limitations:**
- Retrieval quality
- Context relevance
- Update latency

---

## Combining Memory Types

```python
class AgentWithMemory:
    def __init__(self, short_term, long_term, external):
        self.short_term = short_term
        self.long_term = long_term
        self.external = external
    
    def run(self, user_id, query):
        # Get all memory types
        conversation = self.short_term.get_context()
        user_profile = self.long_term.recall(user_id, "profile")
        knowledge = self.external.retrieve(query)
        
        # Assemble context
        context = {
            "conversation": conversation,
            "user": user_profile,
            "knowledge": knowledge
        }
        
        # Generate response
        response = self.llm.generate(query, context)
        
        # Update short-term memory
        self.short_term.add("user", query)
        self.short_term.add("assistant", response)
        
        return response
```

---

## Memory Management Best Practices

### 1. Prioritize Context

```python
def prioritize_context(conversation, user_profile, knowledge, max_tokens=4000):
    # Always include latest message
    context = [conversation[-1]]
    remaining = max_tokens - count_tokens(conversation[-1])
    
    # Add user profile (high priority)
    if user_profile and remaining > 0:
        context.insert(0, user_profile)
        remaining -= count_tokens(user_profile)
    
    # Add relevant knowledge
    for doc in knowledge:
        if remaining > count_tokens(doc):
            context.insert(-1, doc)
            remaining -= count_tokens(doc)
        else:
            break
    
    return context
```

### 2. Summarize Old Conversations

```python
class SummarizingMemory:
    def __init__(self, max_messages=20):
        self.messages = []
        self.summary = None
        self.max_messages = max_messages
    
    def add(self, message):
        self.messages.append(message)
        
        if len(self.messages) > self.max_messages:
            # Summarize older messages
            old_messages = self.messages[:-10]
            self.summary = self.llm.summarize(old_messages)
            self.messages = [self.summary] + self.messages[-10:]
```

### 3. Forgetting Strategy

```python
class ForgettingMemory:
    def __init__(self, db):
        self.db = db
    
    def cleanup_old_memories(self, days=30):
        self.db.execute(
            "DELETE FROM user_memory WHERE created_at < ?",
            (datetime.now() - timedelta(days=days),)
        )
    
    def decay_importance(self):
        # Reduce importance score over time
        self.db.execute(
            "UPDATE user_memory SET importance = importance * 0.9"
        )
```

---

## The Memory Checklist

- [ ] Short-term memory for conversations
- [ ] Long-term memory for user profiles
- [ ] External memory for knowledge
- [ ] Token budget management
- [ ] Context prioritization
- [ ] Conversation summarization
- [ ] Memory cleanup/forgetting
- [ ] Privacy compliance
- [ ] Performance optimization

---

## Conclusion

Good agent memory requires:
- Multiple memory types
- Smart context management
- Token optimization
- Privacy considerations

Build memory systems, not just prompts.

---

*ArQon Agentics builds agents with production-grade memory systems. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
