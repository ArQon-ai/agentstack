# SEO Article: AI Agent Evaluation: Measuring Quality
**Target Keywords:** agent evaluation, LLM evaluation, agent quality  
**Published:** November 15, 2026

---

# AI Agent Evaluation: Measuring Quality

*You can't improve what you don't measure.*

---

## Evaluation Dimensions

### 1. Accuracy

```python
class AccuracyEvaluator:
    def evaluate(self, response: str, expected: str) -> float:
        # Exact match
        if response.strip() == expected.strip():
            return 1.0
        
        # Semantic similarity
        similarity = self.semantic_similarity(response, expected)
        
        return similarity
    
    def semantic_similarity(self, text1: str, text2: str) -> float:
        # Use embeddings
        emb1 = self.embedder.embed(text1)
        emb2 = self.embedder.embed(text2)
        
        # Cosine similarity
        return cosine_similarity(emb1, emb2)
```

### 2. Completeness

```python
class CompletenessEvaluator:
    def evaluate(self, response: str, requirements: list[str]) -> float:
        matched = 0
        
        for req in requirements:
            if self.covers_requirement(response, req):
                matched += 1
        
        return matched / len(requirements) if requirements else 0
    
    def covers_requirement(self, response: str, requirement: str) -> bool:
        # Check if response addresses requirement
        response_emb = self.embedder.embed(response)
        req_emb = self.embedder.embed(requirement)
        
        return cosine_similarity(response_emb, req_emb) > 0.7
```

### 3. Safety

```python
class SafetyEvaluator:
    def evaluate(self, response: str) -> dict:
        checks = {
            "toxicity": self.check_toxicity(response),
            "bias": self.check_bias(response),
            "privacy": self.check_privacy(response),
            "harmful": self.check_harmful(response)
        }
        
        return {
            "passed": all(checks.values()),
            "checks": checks
        }
    
    def check_toxicity(self, text: str) -> bool:
        score = self.toxicity_classifier.predict(text)
        return score < 0.5
```

---

## Automated Evaluation

### LLM-as-Judge

```python
class LLMJudge:
    def __init__(self, judge_model):
        self.judge = judge_model
    
    async def evaluate(self, query: str, response: str, criteria: list[str]) -> dict:
        prompt = f"""Evaluate this response based on the criteria.

Query: {query}

Response: {response}

Criteria:
{chr(10).join(f"- {c}" for c in criteria)}

Rate each criterion 1-5 and explain."""
        
        evaluation = await self.judge.generate(prompt)
        
        return self.parse_evaluation(evaluation)
```

### Human Evaluation

```python
class HumanEvaluation:
    def __init__(self, db):
        self.db = db
    
    async def submit_evaluation(self, response_id: str, ratings: dict, feedback: str):
        await self.db.execute(
            """INSERT INTO evaluations 
               (response_id, ratings, feedback, created_at)
               VALUES ($1, $2, $3, NOW())""",
            response_id,
            json.dumps(ratings),
            feedback
        )
    
    async def get_aggregate_scores(self) -> dict:
        rows = await self.db.fetch(
            """SELECT 
                 AVG(ratings->>'accuracy') as accuracy,
                 AVG(ratings->>'completeness') as completeness,
                 AVG(ratings->>'helpfulness') as helpfulness
               FROM evaluations"""
        )
        
        return dict(rows[0])
```

---

## Evaluation Framework

```python
class AgentEvaluator:
    def __init__(self):
        self.evaluators = {
            "accuracy": AccuracyEvaluator(),
            "completeness": CompletenessEvaluator(),
            "safety": SafetyEvaluator(),
            "latency": LatencyEvaluator(),
            "cost": CostEvaluator()
        }
    
    async def evaluate(self, query: str, response: str, context: dict) -> dict:
        results = {}
        
        for name, evaluator in self.evaluators.items():
            try:
                score = await evaluator.evaluate(response, context)
                results[name] = score
            except Exception as e:
                results[name] = {"error": str(e)}
        
        # Overall score
        overall = sum(
            r["score"] for r in results.values() 
            if isinstance(r, dict) and "score" in r
        ) / len(results)
        
        return {
            "overall": overall,
            "dimensions": results,
            "query": query,
            "response": response
        }
```

---

## The Evaluation Checklist

- [ ] Define evaluation criteria
- [ ] Choose metrics
- [ ] Build evaluators
- [ ] Run automated tests
- [ ] Collect human feedback
- [ ] Track over time
- [ ] Set thresholds
- [ ] Alert on regressions
- [ ] Iterate on prompts
- [ ] Document results

---

## Conclusion

Evaluation:
- Measures quality
- Drives improvement
- Prevents regressions
- Builds trust

Evaluate always.
Measure everything.
Improve continuously.

---

*ArQon Agentics evaluates every agent. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
