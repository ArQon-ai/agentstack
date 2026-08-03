# Blog Post: The Agent Engineer's Guide to Prompt Versioning
## Published: October 9, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to Prompt Versioning

*Treat prompts like code: version them, test them, deploy them safely.*

---

## The Problem

Prompts change frequently:
- Model updates
- Requirement changes
- A/B testing
- Bug fixes

Without versioning:
- Can't reproduce results
- Don't know what changed
- Can't rollback
- Can't compare

---

## Versioning Strategy

### 1. Store Prompts in Code

```python
# prompts/v1/research.py
RESEARCH_PROMPT = """You are a research assistant.

Task: Summarize the following text.

Requirements:
- 3 bullet points
- Each < 20 words
- Focus on key findings

Text: {text}
"""

# prompts/v2/research.py
RESEARCH_PROMPT = """You are a senior research analyst.

Task: Provide a structured summary.

Requirements:
- 3 key findings
- 1 implication
- 1 limitation
- Each < 30 words

Text: {text}
"""
```

### 2. Semantic Versioning

```
prompts/
├── v1.0.0/
│   ├── research.py       # Initial version
│   └── analysis.py
├── v1.1.0/
│   ├── research.py       # Added constraints
│   └── analysis.py
├── v2.0.0/
│   ├── research.py       # Major refactor
│   └── analysis.py       # New format
└── latest -> v2.0.0/     # Symlink
```

### 3. Prompt Registry

```python
class PromptRegistry:
    def __init__(self):
        self.prompts = {}
        self.versions = {}
    
    def register(self, name, version, prompt):
        if name not in self.prompts:
            self.prompts[name] = {}
        
        self.prompts[name][version] = prompt
        
        # Track version history
        if name not in self.versions:
            self.versions[name] = []
        self.versions[name].append(version)
    
    def get(self, name, version="latest"):
        if version == "latest":
            version = self.versions[name][-1]
        
        return self.prompts[name][version]
    
    def list_versions(self, name):
        return self.versions[name]
```

---

## Testing Prompts

### Regression Tests

```python
class PromptTestSuite:
    def __init__(self):
        self.test_cases = []
    
    def add_test(self, name, input_data, expected_patterns):
        self.test_cases.append({
            "name": name,
            "input": input_data,
            "expected": expected_patterns
        })
    
    async def run(self, prompt_version):
        results = []
        
        for test in self.test_cases:
            # Run prompt
            response = await self.run_prompt(
                prompt_version, 
                test["input"]
            )
            
            # Check expectations
            passed = all(
                pattern in response 
                for pattern in test["expected"]
            )
            
            results.append({
                "name": test["name"],
                "passed": passed,
                "response": response
            })
        
        return results
```

### Evaluation Metrics

```python
class PromptEvaluator:
    def __init__(self):
        self.metrics = {
            "accuracy": self.check_accuracy,
            "format": self.check_format,
            "length": self.check_length,
            "safety": self.check_safety
        }
    
    async def evaluate(self, response, criteria):
        scores = {}
        
        for metric_name, metric_fn in self.metrics.items():
            if metric_name in criteria:
                score = await metric_fn(response, criteria[metric_name])
                scores[metric_name] = score
        
        return scores
```

---

## Deployment

### Canary Deployment

```python
class PromptDeployer:
    def __init__(self):
        self.active_version = "v1.0.0"
        self.canary_version = None
        self.canary_percentage = 0
    
    def deploy_canary(self, version, percentage=10):
        self.canary_version = version
        self.canary_percentage = percentage
    
    def get_prompt(self, user_id):
        # Consistent hashing for canary
        user_hash = hash(user_id) % 100
        
        if user_hash < self.canary_percentage:
            return self.prompts[self.canary_version]
        
        return self.prompts[self.active_version]
    
    def promote_canary(self):
        self.active_version = self.canary_version
        self.canary_version = None
        self.canary_percentage = 0
```

### Rollback

```python
class PromptRollback:
    def __init__(self):
        self.history = []
    
    def deploy(self, version):
        self.history.append(version)
        self.active = version
    
    def rollback(self):
        if len(self.history) > 1:
            self.history.pop()  # Remove current
            self.active = self.history[-1]
            return self.active
        
        raise NoPreviousVersion("Cannot rollback further")
```

---

## Tracking

### Prompt Analytics

```python
class PromptAnalytics:
    def __init__(self):
        self.usage = defaultdict(lambda: defaultdict(int))
        self.performance = defaultdict(list)
    
    def track_usage(self, prompt_name, version):
        self.usage[prompt_name][version] += 1
    
    def track_performance(self, prompt_name, version, metrics):
        self.performance[(prompt_name, version)].append(metrics)
    
    def get_comparison(self, prompt_name, v1, v2):
        v1_perf = self.performance[(prompt_name, v1)]
        v2_perf = self.performance[(prompt_name, v2)]
        
        return {
            "v1_accuracy": np.mean([p["accuracy"] for p in v1_perf]),
            "v2_accuracy": np.mean([p["accuracy"] for p in v2_perf]),
            "v1_latency": np.mean([p["latency"] for p in v1_perf]),
            "v2_latency": np.mean([p["latency"] for p in v2_perf])
        }
```

---

## The Prompt Versioning Checklist

- [ ] Store prompts in code
- [ ] Use semantic versioning
- [ ] Create prompt registry
- [ ] Write regression tests
- [ ] Define evaluation metrics
- [ ] Implement canary deployment
- [ ] Enable rollback
- [ ] Track usage
- [ ] Compare performance
- [ ] Document changes

---

## Conclusion

Prompt versioning:
- Enables reproducibility
- Supports A/B testing
- Prevents regressions
- Enables rollback

Treat prompts like code.
Because they are.

---

*ArQon Agentics builds production-grade agent systems with versioned prompts. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
