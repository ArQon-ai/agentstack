# Chapter 5: Context Engineering — The Hidden Superpower

**The Agentic Engineer's Playbook**
*By ArQon Agentics*

---

## Overview

Prompt engineering gets all the attention. But context engineering is what separates toy agents from production systems.

This chapter covers how to manage, optimize, and engineer the context that flows through your agents.

---

## What is Context Engineering?

Context engineering is the practice of:
1. Selecting the right information to send to an LLM
2. Organizing it for maximum comprehension
3. Optimizing token usage without losing quality
4. Maintaining coherence across long interactions

It's the difference between:
- **Throwing everything at the model** and hoping for the best
- **Curating exactly what the model needs** to succeed

---

## The Context Budget

Every LLM call has a token limit. Think of this as your "context budget."

```
GPT-4 Turbo: 128K tokens (~96K words)
Claude 3.5: 200K tokens (~150K words)
Llama 3: 8K tokens (~6K words)
```

But just because you CAN send 128K tokens doesn't mean you SHOULD.

### Cost Reality Check

| Model | Input Cost (per 1K tokens) | 128K Context Cost |
|-------|---------------------------|-------------------|
| GPT-4 Turbo | $0.01 | $1.28 per call |
| Claude 3.5 Sonnet | $0.003 | $0.38 per call |
| GPT-4o | $0.005 | $0.64 per call |

Send 128K tokens on every request? $1.28 × 10,000 requests = **$12,800/day**.

---

## Context Architecture

Production agents need multiple context layers:

```
┌─────────────────────────────────────┐
│  Layer 1: System Context            │
│  (instructions, persona, rules)     │
│  ~500-1000 tokens                   │
├─────────────────────────────────────┤
│  Layer 2: Working Memory            │
│  (current task, recent actions)     │
│  ~1000-2000 tokens                  │
├─────────────────────────────────────┤
│  Layer 3: Retrieved Context         │
│  (documents, knowledge base)        │
│  ~2000-4000 tokens                  │
├─────────────────────────────────────┤
│  Layer 4: Conversation History      │
│  (previous messages)                │
│  ~1000-3000 tokens                  │
├─────────────────────────────────────┤
│  Layer 5: Tool Context              │
│  (tool descriptions, schemas)       │
│  ~500-1500 tokens                   │
└─────────────────────────────────────┘
```

**Total:** ~5,000-11,500 tokens per request.

But we can optimize each layer.

---

## Layer 1: System Context Optimization

### Dynamic System Prompts

Instead of static instructions, tailor the system prompt to the task:

```python
class DynamicSystemPrompt:
    def __init__(self, base_instructions):
        self.base = base_instructions
        self.templates = {
            "coding": "You are a senior software engineer...",
            "analysis": "You are a data analyst...",
            "writing": "You are a technical writer...",
        }
    
    def get_prompt(self, task_type, user_context):
        template = self.templates.get(task_type, self.base)
        
        return f"""{template}

User Context:
- Expertise: {user_context.expertise}
- Preferences: {user_context.preferences}
- Constraints: {user_context.constraints}

Current Task Type: {task_type}"""
```

**Result:** More relevant responses, fewer tokens wasted on irrelevant instructions.

---

## Layer 2: Working Memory

### The Sliding Window Pattern

```python
from collections import deque

class SlidingWindowMemory:
    def __init__(self, max_messages=10, max_tokens=2000):
        self.messages = deque(maxlen=max_messages)
        self.max_tokens = max_tokens
        self.current_tokens = 0
    
    def add(self, message):
        # Estimate tokens
        msg_tokens = self.estimate_tokens(message)
        
        # Remove old messages if needed
        while self.current_tokens + msg_tokens > self.max_tokens and self.messages:
            removed = self.messages.popleft()
            self.current_tokens -= self.estimate_tokens(removed)
        
        self.messages.append(message)
        self.current_tokens += msg_tokens
    
    def get_context(self):
        return list(self.messages)
```

### Summarization Fallback

When history gets too long, summarize instead of dropping:

```python
class SummarizingMemory:
    def __init__(self, llm, summary_interval=5):
        self.llm = llm
        self.recent = deque(maxlen=5)
        self.summaries = []
        self.message_count = 0
        self.summary_interval = summary_interval
    
    def add(self, message):
        self.recent.append(message)
        self.message_count += 1
        
        if self.message_count % self.summary_interval == 0:
            self._summarize()
    
    def _summarize(self):
        summary = self.llm.summarize(list(self.recent))
        self.summaries.append(summary)
        self.recent.clear()
    
    def get_context(self):
        return {
            "summaries": self.summaries[-3:],  # Last 3 summaries
            "recent": list(self.recent)
        }
```

**Result:** Maintain context coherence across 100+ messages using <2K tokens.

---

## Layer 3: Retrieved Context

### Relevance Scoring

```python
class RelevanceRetriever:
    def __init__(self, vector_db, min_score=0.75):
        self.db = vector_db
        self.min_score = min_score
    
    def retrieve(self, query, max_results=5):
        results = self.db.search(query, top_k=20)
        
        # Filter by relevance
        relevant = [r for r in results if r.score >= self.min_score]
        
        # If too few results, lower threshold
        if len(relevant) < 3:
            relevant = [r for r in results if r.score >= self.min_score * 0.8]
        
        return relevant[:max_results]
```

### Chunking Strategy

```python
class SmartChunker:
    def chunk_document(self, document, chunk_size=500, overlap=50):
        """Chunk document with semantic boundaries."""
        chunks = []
        
        # Split on semantic boundaries (paragraphs, sections)
        paragraphs = document.split('\n\n')
        
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_tokens = self.estimate_tokens(para)
            
            if current_size + para_tokens > chunk_size:
                # Save current chunk
                chunks.append('\n\n'.join(current_chunk))
                
                # Start new chunk with overlap
                overlap_text = '\n\n'.join(current_chunk[-2:])
                current_chunk = [overlap_text, para]
                current_size = self.estimate_tokens(overlap_text) + para_tokens
            else:
                current_chunk.append(para)
                current_size += para_tokens
        
        # Don't forget last chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
```

---

## Layer 4: Conversation History

### Differential Updates

For real-time agents, send only what changed:

```python
class DifferentialHistory:
    def __init__(self):
        self.last_sent = None
        self.last_hash = None
    
    def get_update(self, full_history):
        current_hash = hash(json.dumps(full_history, sort_keys=True))
        
        if current_hash == self.last_hash:
            return None  # No changes
        
        if self.last_sent is None:
            self.last_sent = full_history
            self.last_hash = current_hash
            return full_history
        
        # Compute diff
        diff = self._compute_diff(self.last_sent, full_history)
        
        self.last_sent = full_history
        self.last_hash = current_hash
        
        return diff
```

---

## Layer 5: Tool Context

### Dynamic Tool Selection

Don't send all tool descriptions. Send only relevant ones:

```python
class DynamicToolSelector:
    def __init__(self, tools, llm):
        self.tools = tools
        self.llm = llm
    
    def select_tools(self, query):
        # Use lightweight model to select tools
        tool_list = "\n".join([
            f"- {name}: {tool.description}"
            for name, tool in self.tools.items()
        ])
        
        selection = self.llm.generate(
            prompt=f"""Given this query, which tools are needed?

Query: {query}

Available tools:
{tool_list}

Respond with tool names only, comma-separated."""
        )
        
        selected_names = [t.strip() for t in selection.split(",")]
        return {
            name: self.tools[name]
            for name in selected_names
            if name in self.tools
        }
```

---

## Context Compression Techniques

### 1. Keyword Extraction

```python
from collections import Counter
import re

class KeywordCompressor:
    def compress(self, text, target_tokens=500):
        # Extract keywords
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = Counter(words).most_common(50)
        
        # Keep sentences with keywords
        sentences = text.split('.')
        compressed = []
        
        for sentence in sentences:
            if any(kw in sentence.lower() for kw, _ in keywords[:20]):
                compressed.append(sentence)
        
        result = '. '.join(compressed)
        
        # If still too long, truncate
        while self.estimate_tokens(result) > target_tokens:
            compressed.pop()
            result = '. '.join(compressed)
        
        return result
```

### 2. Structured Output Compression

```python
class StructuredCompressor:
    def compress_json(self, data, fields_to_keep=None):
        if fields_to_keep:
            return {
                k: v for k, v in data.items()
                if k in fields_to_keep
            }
        
        # Auto-select important fields
        important = []
        for key, value in data.items():
            if isinstance(value, (int, float, bool)):
                important.append(key)
            elif isinstance(value, str) and len(value) < 100:
                important.append(key)
        
        return {k: data[k] for k in important}
```

---

## Measuring Context Quality

How do you know if your context engineering is working?

### Metrics

1. **Token Efficiency**
   ```
   efficiency = task_success_rate / tokens_used
   ```

2. **Context Relevance**
   ```
   relevance = relevant_tokens / total_tokens
   ```

3. **Cache Hit Rate**
   ```
   cache_hits = cached_responses / total_requests
   ```

4. **Cost Per Task**
   ```
   cost_efficiency = tasks_completed / total_cost
   ```

### Evaluation Framework

```python
class ContextEvaluator:
    def evaluate(self, agent, test_cases):
        results = []
        
        for case in test_cases:
            # Run with full context
            full_result = agent.run(case.input, context=case.full_context)
            full_tokens = agent.last_token_count
            
            # Run with optimized context
            opt_result = agent.run(case.input, context=case.optimized_context)
            opt_tokens = agent.last_token_count
            
            results.append({
                "quality_delta": self.compare_quality(full_result, opt_result),
                "token_savings": 1 - (opt_tokens / full_tokens),
                "cost_savings": self.calculate_cost_diff(full_tokens, opt_tokens)
            })
        
        return results
```

---

## Context Engineering Checklist

Before deploying an agent:

- [ ] System prompt is dynamic and task-specific
- [ ] Working memory uses sliding window
- [ ] History is summarized when long
- [ ] Retrieved context is filtered by relevance
- [ ] Documents are chunked semantically
- [ ] Tool descriptions are dynamically selected
- [ ] Compression is applied to verbose outputs
- [ ] Differential updates are used for real-time
- [ ] Token budget is enforced per request
- [ ] Quality is measured with and without optimization

---

## The Bottom Line

Context engineering is not optional for production agents.

It's the difference between:
- An agent that costs $12,800/day and works
- An agent that costs $3,200/day and works BETTER

Master this, and you'll build agents that are cheaper, faster, and more reliable than your competition.

---

*This is Chapter 5 of The Agentic Engineer's Playbook. Get the full book at [arqonagentics.com](https://arqonagentics.com).*
