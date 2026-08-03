# SEO Article: AI Agent Hallucination: Detection and Prevention
**Target Keywords:** agent hallucination, LLM hallucination, AI accuracy  
**Published:** November 5, 2026

---

# AI Agent Hallucination: Detection and Prevention

*Don't let your agents make things up.*

---

## What is Hallucination?

### Types

1. **Factual Hallucination**
   - Inventing facts
   - Wrong dates
   - Non-existent references

2. **Source Hallucination**
   - Citing fake sources
   - Misattributing quotes
   - Inventing studies

3. **Logical Hallucination**
   - Contradicting itself
   - Invalid reasoning
   - False conclusions

---

## Detection Methods

### 1. Fact Checking

```python
class FactChecker:
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.search = WebSearch()
    
    async def check(self, claim: str) -> dict:
        # Search for evidence
        results = await self.search.query(claim)
        
        # Check against knowledge base
        kb_match = await self.knowledge_base.verify(claim)
        
        return {
            "claim": claim,
            "verified": kb_match or len(results) > 0,
            "sources": results[:3],
            "confidence": self.calculate_confidence(results)
        }
    
    async def check_response(self, response: str) -> list[dict]:
        # Extract claims
        claims = self.extract_claims(response)
        
        # Check each
        results = []
        for claim in claims:
            result = await self.check(claim)
            results.append(result)
        
        return results
```

### 2. Self-Consistency Check

```python
class ConsistencyChecker:
    async def verify(self, response: str, query: str) -> bool:
        # Ask the same question multiple times
        answers = []
        for _ in range(3):
            answer = await llm.generate(query)
            answers.append(answer)
        
        # Check consistency
        similarities = []
        for i in range(len(answers)):
            for j in range(i + 1, len(answers)):
                sim = self.semantic_similarity(answers[i], answers[j])
                similarities.append(sim)
        
        avg_similarity = sum(similarities) / len(similarities)
        return avg_similarity > 0.8
```

### 3. Source Verification

```python
class SourceVerifier:
    def __init__(self):
        self.trusted_domains = [
            "arxiv.org",
            "github.com",
            "wikipedia.org",
            ".edu"
        ]
    
    async def verify_sources(self, response: str) -> list[dict]:
        # Extract URLs
        urls = self.extract_urls(response)
        
        results = []
        for url in urls:
            try:
                # Check if URL exists
                page = await self.fetch(url)
                exists = page.status == 200
                
                # Check domain trust
                trusted = any(domain in url for domain in self.trusted_domains)
                
                results.append({
                    "url": url,
                    "exists": exists,
                    "trusted": trusted
                })
            except Exception:
                results.append({
                    "url": url,
                    "exists": False,
                    "trusted": False
                })
        
        return results
```

---

## Prevention Strategies

### 1. Retrieval-Augmented Generation (RAG)

```python
class RAGAgent:
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
    
    async def run(self, query: str) -> str:
        # Retrieve relevant documents
        docs = await self.retriever.retrieve(query, top_k=5)
        
        # Generate with context
        context = "\n\n".join([d.content for d in docs])
        
        prompt = f"""Answer based on the following context:

Context:
{context}

Question: {query}

Answer:"""
        
        response = await self.llm.generate(prompt)
        
        # Include citations
        return self.add_citations(response, docs)
```

### 2. Constrained Generation

```python
class ConstrainedAgent:
    async def run(self, query: str) -> str:
        prompt = f"""Answer the question using ONLY the provided information.
Do not make up facts.
Do not infer beyond the evidence.
If unsure, say "I don't know."

Question: {query}"""
        
        return await self.llm.generate(prompt)
```

### 3. Human-in-the-Loop

```python
class HITLAgent:
    async def run(self, query: str) -> str:
        # Generate response
        response = await self.llm.generate(query)
        
        # Check confidence
        confidence = await self.assess_confidence(response)
        
        if confidence < 0.7:
            # Flag for human review
            await self.queue_for_review(query, response)
            return "This response is being reviewed for accuracy."
        
        return response
```

---

## Monitoring Hallucinations

### Hallucination Rate

```python
class HallucinationMonitor:
    def __init__(self):
        self.total_responses = 0
        self.hallucinations = 0
    
    async def monitor(self, response: str, query: str):
        self.total_responses += 1
        
        # Check for hallucinations
        is_hallucination = await self.detect_hallucination(response, query)
        
        if is_hallucination:
            self.hallucinations += 1
            await self.alert(response, query)
        
        # Track rate
        rate = self.hallucinations / self.total_responses
        
        return {
            "hallucination_rate": rate,
            "total_checked": self.total_responses,
            "hallucinations_found": self.hallucinations
        }
```

---

## The Hallucination Checklist

- [ ] Implement fact checking
- [ ] Add self-consistency checks
- [ ] Verify sources
- [ ] Use RAG
- [ ] Constrain generation
- [ ] Add human review
- [ ] Monitor hallucination rate
- [ ] Track accuracy metrics
- [ ] Alert on high rates
- [ ] Document known issues
- [ ] Test edge cases
- [ ] Iterate on prompts

---

## Conclusion

Hallucination:
- Is a real problem
- Can be detected
- Can be prevented
- Requires vigilance

Verify everything.
Trust but confirm.
Monitor continuously.

---

*ArQon Agentics builds agents that tell the truth. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
