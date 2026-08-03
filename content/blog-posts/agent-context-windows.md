# Blog Post: Agent Context Windows: Managing Token Limits in Production
## Published: October 2, 2026
## Category: Engineering

---

# Agent Context Windows: Managing Token Limits in Production

*Context limits are the silent killer of production agents. Here's how to manage them.*

---

## Understanding Token Limits

| Model | Context Window | Output Limit |
|-------|---------------|--------------|
| GPT-4 | 128K tokens | 4K tokens |
| GPT-4o | 128K tokens | 4K tokens |
| GPT-3.5 | 16K tokens | 4K tokens |
| Claude 3.5 | 200K tokens | 4K tokens |

**1 token ≈ 0.75 words (English)**

---

## The Context Problem

### Scenario

```
User asks a complex question.
Agent needs:
→ System prompt: 500 tokens
→ Conversation history: 8,000 tokens
→ Retrieved documents: 5,000 tokens
→ User query: 100 tokens

Total: 13,600 tokens

GPT-3.5 limit: 16,000 tokens
→ Barely fits
→ No room for response
→ Expensive
```

### The Cost

```python
# 13,600 tokens at GPT-4 rates
input_cost = (13600 / 1000) * 0.03  # $0.408 per request

# 100 requests/day
 daily_cost = 0.408 * 100  # $40.80/day
monthly_cost = 40.80 * 30  # $1,224/month
```

---

## Management Strategies

### 1. Sliding Window

```python
class SlidingWindowMemory:
    def __init__(self, max_tokens=12000):
        self.max_tokens = max_tokens
        self.messages = []
    
    def add(self, message):
        self.messages.append(message)
        self._trim()
    
    def _trim(self):
        while self.count_tokens() > self.max_tokens:
            # Remove oldest non-system message
            for i, msg in enumerate(self.messages):
                if msg.role != "system":
                    self.messages.pop(i)
                    break
    
    def count_tokens(self):
        return sum(len(msg.content.split()) * 1.3 for msg in self.messages)
```

### 2. Summarization

```python
class SummarizingMemory:
    def __init__(self, llm, summary_threshold=10):
        self.llm = llm
        self.messages = []
        self.summary = None
        self.threshold = summary_threshold
    
    def add(self, message):
        self.messages.append(message)
        
        if len(self.messages) > self.threshold:
            self._summarize()
    
    def _summarize(self):
        old_messages = self.messages[:-5]
        recent_messages = self.messages[-5:]
        
        # Summarize old messages
        prompt = f"Summarize this conversation: {old_messages}"
        self.summary = self.llm.generate(prompt)
        
        # Replace with summary
        self.messages = [
            {"role": "system", "content": f"Previous context: {self.summary}"}
        ] + recent_messages
```

### 3. Selective Context

```python
class SelectiveContext:
    def __init__(self, retriever):
        self.retriever = retriever
    
    def build_context(self, query, all_messages):
        # Always include system prompt
        context = [msg for msg in all_messages if msg.role == "system"]
        
        # Include recent messages
        context.extend(all_messages[-5:])
        
        # Retrieve relevant historical messages
        relevant = self.retriever.search(query, all_messages)
        context.extend(relevant)
        
        # Remove duplicates
        seen = set()
        unique_context = []
        for msg in context:
            if msg.id not in seen:
                seen.add(msg.id)
                unique_context.append(msg)
        
        return unique_context
```

### 4. Hierarchical Context

```python
class HierarchicalContext:
    def __init__(self):
        self.levels = {
            "system": [],      # Always included
            "session": [],     # Current session
            "topic": {},       # By topic
            "user": {}         # User preferences
        }
    
    def get_context(self, query):
        context = []
        
        # Level 1: System (always)
        context.extend(self.levels["system"])
        
        # Level 2: User preferences
        user_prefs = self.levels["user"].get(user_id, [])
        context.extend(user_prefs)
        
        # Level 3: Topic-specific
        topic = self.classify_topic(query)
        topic_context = self.levels["topic"].get(topic, [])
        context.extend(topic_context)
        
        # Level 4: Session
        context.extend(self.levels["session"][-3:])
        
        return context
```

---

## Token Counting

### Estimation

```python
def estimate_tokens(text):
    """Rough estimation: 1 token ≈ 0.75 words"""
    words = len(text.split())
    return int(words / 0.75)

def estimate_tokens_precise(text):
    """More accurate using tiktoken"""
    import tiktoken
    encoder = tiktoken.encoding_for_model("gpt-4")
    return len(encoder.encode(text))
```

### Budgeting

```python
class TokenBudget:
    def __init__(self, max_tokens=16000):
        self.max_tokens = max_tokens
        self.reserved = 4000  # For response
        self.available = max_tokens - reserved
    
    def allocate(self, system_prompt, history, context):
        used = 0
        
        # System prompt (priority 1)
        system_tokens = estimate_tokens(system_prompt)
        used += system_tokens
        
        # Recent history (priority 2)
        history_tokens = 0
        recent_history = []
        for msg in reversed(history):
            msg_tokens = estimate_tokens(msg.content)
            if used + msg_tokens > self.available:
                break
            recent_history.insert(0, msg)
            history_tokens += msg_tokens
            used += msg_tokens
        
        # Context (priority 3)
        context_tokens = 0
        relevant_context = []
        for doc in context:
            doc_tokens = estimate_tokens(doc.content)
            if used + doc_tokens > self.available:
                break
            relevant_context.append(doc)
            context_tokens += doc_tokens
            used += doc_tokens
        
        return {
            "system": system_prompt,
            "history": recent_history,
            "context": relevant_context,
            "total_used": used,
            "remaining": self.available - used
        }
```

---

## Optimization Techniques

### 1. Compression

```python
class ContextCompressor:
    def compress(self, text, target_tokens):
        current_tokens = estimate_tokens(text)
        
        if current_tokens <= target_tokens:
            return text
        
        # Remove less important parts
        sentences = text.split(". ")
        while estimate_tokens(". ".join(sentences)) > target_tokens:
            # Remove shortest sentence
            shortest = min(sentences, key=len)
            sentences.remove(shortest)
        
        return ". ".join(sentences)
```

### 2. Semantic Truncation

```python
class SemanticTruncator:
    def __init__(self, embedder):
        self.embedder = embedder
    
    def truncate(self, documents, query, max_tokens):
        # Embed query and documents
        query_embedding = self.embedder.embed(query)
        doc_embeddings = [self.embedder.embed(doc) for doc in documents]
        
        # Score by relevance
        scores = [
            cosine_similarity(query_embedding, doc_emb)
            for doc_emb in doc_embeddings
        ]
        
        # Sort by relevance
        scored_docs = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        
        # Take most relevant until budget
        result = []
        used_tokens = 0
        for doc, score in scored_docs:
            doc_tokens = estimate_tokens(doc)
            if used_tokens + doc_tokens > max_tokens:
                break
            result.append(doc)
            used_tokens += doc_tokens
        
        return result
```

---

## The Context Checklist

- [ ] Count tokens accurately
- [ ] Set context budget
- [ ] Implement sliding window
- [ ] Summarize old conversations
- [ ] Select relevant context
- [ ] Compress when needed
- [ ] Monitor token usage
- [ ] Alert on high usage
- [ ] Test with max context
- [ ] Optimize for cost

---

## Conclusion

Context management:
- Is critical for production
- Affects cost significantly
- Impacts response quality
- Requires ongoing optimization

Manage your context.
Control your costs.

---

*ArQon Agentics builds agents with smart context management. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
