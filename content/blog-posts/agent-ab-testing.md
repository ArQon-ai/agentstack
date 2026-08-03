# Blog Post: The Agent Engineer's Guide to A/B Testing
## Published: October 6, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to A/B Testing

*How to test agent changes without breaking production.*

---

## Why A/B Test Agents?

Traditional testing:
- Unit tests pass
- Integration tests pass
- Deploy to production
- Hope for the best

A/B testing:
- Test with real users
- Measure business metrics
- Compare variants
- Make data-driven decisions

---

## The Framework

### 1. Define Metrics

```python
class Metrics:
    def __init__(self):
        self.primary = "user_satisfaction"  # North star
        self.secondary = [
            "response_quality",
            "task_completion_rate",
            "error_rate",
            "latency",
            "cost_per_request"
        ]
        self.guardrail = [
            "error_rate < 5%",
            "latency_p95 < 5s",
            "cost_per_request < $0.05"
        ]
```

### 2. Split Traffic

```python
class TrafficSplitter:
    def __init__(self, split_ratio=0.5):
        self.split_ratio = split_ratio
    
    def assign_variant(self, user_id):
        # Consistent hashing for sticky variants
        hash_value = hash(user_id) % 100
        
        if hash_value < self.split_ratio * 100:
            return "control"
        return "treatment"
```

### 3. Run Experiment

```python
class ABTest:
    def __init__(self, control, treatment, metrics):
        self.control = control
        self.treatment = treatment
        self.metrics = metrics
        self.results = defaultdict(list)
    
    async def run(self, user_id, query):
        variant = self.assign_variant(user_id)
        agent = self.control if variant == "control" else self.treatment
        
        start = time.time()
        try:
            response = await agent.run(query)
            self.record_success(variant, response, time.time() - start)
        except Exception as e:
            self.record_failure(variant, e)
        
        return response
```

### 4. Analyze Results

```python
class ABAnalyzer:
    def analyze(self, results):
        control = results["control"]
        treatment = results["treatment"]
        
        analysis = {}
        
        for metric in self.metrics:
            control_mean = np.mean(control[metric])
            treatment_mean = np.mean(treatment[metric])
            
            # Statistical significance
            t_stat, p_value = ttest_ind(control[metric], treatment[metric])
            
            # Effect size
            lift = (treatment_mean - control_mean) / control_mean * 100
            
            analysis[metric] = {
                "control_mean": control_mean,
                "treatment_mean": treatment_mean,
                "lift": lift,
                "p_value": p_value,
                "significant": p_value < 0.05
            }
        
        return analysis
```

---

## What to Test

### Prompt Variations

```python
variants = {
    "control": "You are a helpful assistant.",
    "v2": "You are an expert agent engineer. Be concise.",
    "v3": "You are a helpful assistant. Think step by step."
}
```

### Model Comparisons

```python
variants = {
    "control": GPT4Agent(),
    "treatment": ClaudeAgent()
}
```

### Tool Configurations

```python
variants = {
    "control": {"retrieval_chunks": 3, "temperature": 0.7},
    "treatment": {"retrieval_chunks": 5, "temperature": 0.3}
}
```

### Response Formats

```python
variants = {
    "control": "plain_text",
    "treatment": "structured_json"
}
```

---

## Testing Best Practices

### 1. Start Small

```python
# Start with 10% traffic
splitter = TrafficSplitter(split_ratio=0.1)

# Monitor for 24 hours
# If no issues, increase to 50%
```

### 2. Set Guardrails

```python
class Guardrail:
    def check(self, results):
        if results["error_rate"] > 0.05:
            self.stop_experiment()
            self.rollback()
            return False
        
        if results["latency_p95"] > 5.0:
            self.stop_experiment()
            return False
        
        return True
```

### 3. Run Long Enough

```python
# Minimum sample size
def calculate_sample_size(baseline_rate, mde, power=0.8, alpha=0.05):
    from scipy.stats import norm
    
    z_alpha = norm.ppf(1 - alpha/2)
    z_beta = norm.ppf(power)
    
    p1 = baseline_rate
    p2 = baseline_rate * (1 + mde)
    
    n = (z_alpha * np.sqrt(2 * p1 * (1 - p1)) +
         z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    
    return int(n / (p2 - p1) ** 2)

# Example: 2% baseline, 10% relative improvement
sample_size = calculate_sample_size(0.02, 0.10)
print(f"Need {sample_size} users per variant")
```

### 4. Segment Analysis

```python
class SegmentAnalyzer:
    def analyze_by_segment(self, results):
        segments = {
            "new_users": results[results["user_age"] < 7],
            "power_users": results[results["requests"] > 100],
            "mobile": results[results["device"] == "mobile"],
            "desktop": results[results["device"] == "desktop"]
        }
        
        for segment_name, segment_data in segments.items():
            analysis = self.analyze(segment_data)
            print(f"{segment_name}: {analysis['lift']}% lift")
```

---

## Common Pitfalls

### 1. Multiple Changes

**Bad:** Test prompt + model + temperature at once
**Good:** Test one change at a time

### 2. Short Duration

**Bad:** 100 users, 2 hours
**Good:** 10,000 users, 2 weeks

### 3. Wrong Metrics

**Bad:** Click rate (gaming)
**Good:** Task completion (real value)

### 4. Novelty Effect

**Bad:** Measure day 1 only
**Good:** Measure over 2+ weeks

---

## The A/B Testing Checklist

- [ ] Define primary metric
- [ ] Choose secondary metrics
- [ ] Set guardrails
- [ ] Calculate sample size
- [ ] Implement consistent splitting
- [ ] Monitor in real-time
- [ ] Run for full duration
- [ ] Analyze segments
- [ ] Document learnings
- [ ] Roll out or rollback

---

## Conclusion

A/B testing agents:
- Reduces risk
- Measures real impact
- Builds confidence
- Drives improvement

Test everything.
Trust data.

---

*ArQon Agentics builds data-driven agent systems. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
