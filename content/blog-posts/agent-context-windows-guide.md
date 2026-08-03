# Blog Post: The Agent Engineer's Guide to Context Windows
## Published: November 6, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to Context Windows

*Master context. Reduce costs. Improve responses.*

---

## Understanding Context Windows

### What is a Context Window?

The maximum amount of text an LLM can process in a single request:

| Model | Context Window | Cost |
|-------|---------------|------|
| GPT-4o | 128K tokens | $$ |
| GPT-4 | 8K tokens | $$$ |
| Claude 3.5 | 200K tokens | $$ |
| Claude 3 | 200K tokens | $$$ |

### Token Economics

```python
# Approximate token counts
text = "Hello, how are you?"
tokens = len(text.split()) * 1.3  # Rough estimate

# More accurate with tiktoken
import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4o")
tokens = len(encoder.encode(text))
```

---

## Context Management Strategies

### 1. Sliding Window

```python
class SlidingWindow:
    def __init__(self, max_tokens=4000):
        self.max_tokens = max_tokens
        self.messages = []
    
    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self._trim()
    
    def _trim(self):
        # Remove oldest messages until under limit
        while self._count_tokens() > self.max_tokens:
            if len(self.messages) > 2:
                self.messages.pop(1)  # Keep system message
            else:
                break
    
    def _count_tokens(self) -> int:
        encoder = tiktoken.encoding_for_model("gpt-4o")
        total = 0
        for msg in self.messages:
            total += len(encoder.encode(msg["content"]))
            total += 4  # Message overhead
        return total
```

### 2. Summarization

```python
class SummarizingMemory:
    def __init__(self, llm, max_tokens=2000):
        self.llm = llm
        self.max_tokens = max_tokens
        self.history = []
        self.summary = ""
    
    async def add_interaction(self, query: str, response: str):
        self.history.append({"query": query, "response": response})
        
        # Summarize if getting long
        if self._count_tokens() > self.max_tokens:
            await self._summarize()
    
    async def _summarize(self):
        # Summarize old interactions
        old_history = self.history[:-5]  # Keep last 5
        self.history = self.history[-5:]
        
        summary_prompt = f"""Summarize these interactions:
{json.dumps(old_history)}

Summary:"""
        
        new_summary = await self.llm.generate(summary_prompt)
        self.summary = f"{self.summary}\n{new_summary}"
    
    def get_context(self) -> str:
        context = f"Summary: {self.summary}\n\n"
        context += "Recent interactions:\n"
        for h in self.history:
            context += f"Q: {h['query']}\nA: {h['response']}\n\n"
        return context
```

### 3. Selective Context

```python
class SelectiveContext:
    def __init__(self, retriever):
        self.retriever = retriever
    
    async def build_context(self, query: str, max_tokens: int = 3000) -> str:
        # Retrieve relevant documents
        docs = await self.retriever.retrieve(query, top_k=5)
        
        # Build context from most relevant
        context = ""
        for doc in docs:
            doc_text = f"\n{doc.content}\n"
            if self._count_tokens(context + doc_text) > max_tokens:
                break
            context += doc_text
        
        return context
    
    def _count_tokens(self, text: str) -> int:
        encoder = tiktoken.encoding_for_model("gpt-4o")
        return len(encoder.encode(text))
```

---

## Optimizing Context Usage

### 1. Remove Redundancy

```python
class ContextOptimizer:
    def optimize(self, text: str) -> str:
        # Remove filler words
        fillers = ["very", "really", "quite", "rather", "fairly", "just"]
        for filler in fillers:
            text = text.replace(f" {filler} ", " ")
        
        # Remove duplicate sentences
        sentences = text.split(". ")
        unique = []
        for s in sentences:
            if s not in unique:
                unique.append(s)
        
        return ". ".join(unique)
```

### 2. Structured Context

```python
# Good: Structured
context = """## User Profile
- Role: Developer
- Experience: 5 years
- Tech stack: Python, React

## Current Task
Build an API endpoint for user authentication.

## Requirements
- JWT tokens
- Rate limiting
- Input validation"""

# Bad: Unstructured
context = "The user is a developer with 5 years experience who knows Python and React and wants to build an API endpoint for user authentication that needs JWT tokens and rate limiting and input validation..."
```

---

## The Context Checklist

- [ ] Understand token limits
- [ ] Count tokens accurately
- [ ] Implement sliding window
- [ ] Summarize old context
- [ ] Select relevant context
- [ ] Remove redundancy
- [ ] Structure context
- [ ] Monitor token usage
- [ ] Optimize costs
- [ ] Test edge cases

---

## Conclusion

Context windows:
- Are limited
- Cost money
- Affect quality
- Require management

Use wisely.
Count accurately.
Optimize continuously.

---

*ArQon Agentics optimizes agent context. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
