# Chapter 6: Testing and Evaluation for Agentic Systems

**The Agentic Engineer's Playbook**
*By ArQon Agentics*

---

## Overview

Testing agents is harder than testing traditional software. Agents are non-deterministic, stateful, and context-dependent.

This chapter covers how to build reliable testing and evaluation frameworks for production agentic systems.

---

## Why Agent Testing is Different

| Aspect | Traditional Software | Agentic Systems |
|--------|---------------------|-----------------|
| Output | Deterministic | Probabilistic |
| State | Explicit | Implicit (context) |
| Errors | Binary (pass/fail) | Spectrum (quality) |
| Reproducibility | High | Low |
| Test Coverage | Line-based | Behavior-based |

Traditional unit tests don't work for agents. You need a new approach.

---

## The Three Layers of Agent Testing

### Layer 1: Unit Tests (Component Level)

Test individual components in isolation:

```python
class TestInputValidation:
    def test_valid_input(self):
        result = validator.validate({"query": "Hello"})
        assert result.is_valid
    
    def test_empty_input(self):
        result = validator.validate({"query": ""})
        assert not result.is_valid
        assert result.error == "empty_query"
    
    def test_sql_injection(self):
        result = validator.validate({"query": "'; DROP TABLE users; --"})
        assert not result.is_valid
        assert result.error == "malicious_input"

class TestContextRetrieval:
    def test_relevance_filtering(self):
        docs = retriever.retrieve("Python tutorial", min_score=0.8)
        assert all(d.score >= 0.8 for d in docs)
    
    def test_max_results(self):
        docs = retriever.retrieve("AI", max_results=5)
        assert len(docs) <= 5
```

### Layer 2: Integration Tests (Workflow Level)

Test agent workflows end-to-end:

```python
class TestAgentWorkflow:
    def test_successful_completion(self):
        result = agent.run("What's 2+2?")
        assert "4" in result.answer
        assert result.confidence == ConfidenceLevel.HIGH
    
    def test_tool_invocation(self):
        result = agent.run("What's the weather in Tokyo?")
        assert result.tools_used == ["weather_api"]
        assert "Tokyo" in result.answer
    
    def test_fallback_behavior(self):
        # When tool fails
        result = agent.run("What's the weather in [INVALID]?")
        assert result.confidence == ConfidenceLevel.LOW
        assert result.needs_human_review
```

### Layer 3: Evaluation Tests (Quality Level)

Test output quality using metrics:

```python
class TestOutputQuality:
    def test_factual_accuracy(self):
        result = agent.run("Capital of France?")
        assert "Paris" in result.answer
    
    def test_hallucination_rate(self):
        test_cases = load_test_cases("factual_queries.json")
        results = [agent.run(q) for q in test_cases]
        
        hallucinations = sum(1 for r in results if not verify_facts(r))
        rate = hallucinations / len(results)
        
        assert rate < 0.05  # Max 5% hallucination
    
    def test_response_format(self):
        result = agent.run("List 3 colors")
        assert is_valid_list_format(result.answer)
        assert len(parse_list(result.answer)) == 3
```

---

## Evaluation Metrics

### 1. Task Completion Rate

```python
def task_completion_rate(agent, test_cases):
    completed = 0
    
    for case in test_cases:
        result = agent.run(case.input)
        if case.success_criteria(result):
            completed += 1
    
    return completed / len(test_cases)
```

### 2. Semantic Similarity

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_similarity(prediction, expected):
    pred_embedding = model.encode(prediction)
    expected_embedding = model.encode(expected)
    
    similarity = cosine_similarity(
        [pred_embedding], 
        [expected_embedding]
    )[0][0]
    
    return similarity
```

### 3. Cost Efficiency

```python
def cost_efficiency(agent, test_cases):
    total_cost = 0
    successful = 0
    
    for case in test_cases:
        result = agent.run(case.input)
        total_cost += result.cost
        
        if case.success_criteria(result):
            successful += 1
    
    return successful / total_cost  # Tasks per dollar
```

### 4. Latency Distribution

```python
def latency_distribution(agent, test_cases):
    latencies = []
    
    for case in test_cases:
        start = time.time()
        agent.run(case.input)
        latencies.append(time.time() - start)
    
    return {
        "p50": np.percentile(latencies, 50),
        "p95": np.percentile(latencies, 95),
        "p99": np.percentile(latencies, 99),
        "max": max(latencies)
    }
```

---

## Building a Test Suite

### Directory Structure

```
tests/
├── unit/
│   ├── test_input_validation.py
│   ├── test_context_retrieval.py
│   ├── test_output_formatting.py
│   └── test_tool_execution.py
├── integration/
│   ├── test_single_agent.py
│   ├── test_multi_agent.py
│   └── test_error_handling.py
├── evaluation/
│   ├── test_factual_accuracy.py
│   ├── test_hallucination.py
│   ├── test_cost_efficiency.py
│   └── test_user_satisfaction.py
├── fixtures/
│   ├── test_queries.json
│   ├── expected_outputs.json
│   └── test_documents/
└── conftest.py
```

### conftest.py

```python
import pytest
from agentstack.core import Agent

@pytest.fixture
def agent():
    return Agent(
        name="test_agent",
        model="gpt-4o",
        tools=["calculator", "search"]
    )

@pytest.fixture
def test_queries():
    return load_json("tests/fixtures/test_queries.json")

@pytest.fixture
def mock_tools():
    return {
        "calculator": MockCalculator(),
        "search": MockSearchEngine()
    }
```

---

## Continuous Evaluation

Agents degrade over time. Set up continuous evaluation:

```python
class ContinuousEvaluator:
    def __init__(self, agent, test_suite):
        self.agent = agent
        self.test_suite = test_suite
        self.baseline_scores = {}
    
    def run_evaluation(self):
        current_scores = {}
        
        for test in self.test_suite:
            score = test.run(self.agent)
            current_scores[test.name] = score
        
        return current_scores
    
    def check_regression(self, current_scores):
        regressions = []
        
        for name, score in current_scores.items():
            baseline = self.baseline_scores.get(name, 0)
            
            if score < baseline * 0.95:  # 5% regression threshold
                regressions.append({
                    "test": name,
                    "baseline": baseline,
                    "current": score,
                    "drop": (baseline - score) / baseline
                })
        
        return regressions
    
    def update_baseline(self, scores):
        self.baseline_scores = scores
```

### CI/CD Integration

```yaml
# .github/workflows/evaluate.yml
name: Agent Evaluation

on: [push, pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Unit Tests
        run: pytest tests/unit/
      
      - name: Run Integration Tests
        run: pytest tests/integration/
      
      - name: Run Evaluation Suite
        run: python scripts/evaluate.py
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      
      - name: Check for Regressions
        run: python scripts/check_regressions.py
```

---

## Human-in-the-Loop Evaluation

Automated metrics aren't enough. You need human judgment:

### A/B Testing Framework

```python
class ABTest:
    def __init__(self, agent_a, agent_b, evaluator_pool):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.evaluators = evaluator_pool
    
    def run_test(self, queries, sample_size=100):
        results = []
        
        for query in queries[:sample_size]:
            # Randomize order to avoid bias
            order = random.choice(["AB", "BA"])
            
            if order == "AB":
                response_a = self.agent_a.run(query)
                response_b = self.agent_b.run(query)
            else:
                response_b = self.agent_b.run(query)
                response_a = self.agent_a.run(query)
            
            results.append({
                "query": query,
                "response_a": response_a,
                "response_b": response_b,
                "order": order
            })
        
        return results
    
    def collect_human_judgments(self, results):
        for result in results:
            # Send to human evaluators
            judgment = self.evaluators.evaluate(
                result["query"],
                result["response_a"],
                result["response_b"]
            )
            result["judgment"] = judgment
```

---

## The Evaluation Checklist

Before shipping a new agent version:

- [ ] Unit tests pass (100%)
- [ ] Integration tests pass (100%)
- [ ] Task completion rate > 90%
- [ ] Hallucination rate < 5%
- [ ] P95 latency < 5 seconds
- [ ] Cost per task within budget
- [ ] No regressions from baseline
- [ ] Human evaluation sample completed
- [ ] Edge cases tested
- [ ] Error handling verified

---

## From Here

Testing agents is an ongoing process, not a one-time task. Set up:

1. **Automated test suite** that runs on every commit
2. **Continuous evaluation** that monitors production quality
3. **Human evaluation pipeline** for subjective quality
4. **Regression detection** that alerts on quality drops

In the next chapter, we'll cover **security and safety** — how to protect your agents from attacks and misuse.

---

*This is Chapter 6 of The Agentic Engineer's Playbook. Get the full book at [arqonagentics.com](https://arqonagentics.com).*
