# Blog Post: Agent Testing in Production: Canary Releases and A/B Testing
## Published: September 25, 2026
## Category: Engineering

---

# Agent Testing in Production: Canary Releases and A/B Testing

*How to safely test agent changes with real users.*

---

## Why Test in Production?

Agent behavior is hard to predict:
- Prompt changes affect output quality
- Model updates change behavior
- Context affects reasoning
- User inputs are unpredictable

Staging can't catch everything.
Production testing is essential.

---

## Canary Releases

### Gradual Rollout

```python
class CanaryRelease:
    def __init__(self, rollout_percentage=5):
        self.rollout_percentage = rollout_percentage
    
    def should_use_new_version(self, user_id):
        # Hash user_id to get consistent assignment
        hash_value = hash(user_id) % 100
        return hash_value < self.rollout_percentage
    
    async def process(self, user_id, query):
        if self.should_use_new_version(user_id):
            return await new_agent.run(query)
        return await current_agent.run(query)
```

### Monitoring Canary

```python
class CanaryMonitor:
    def __init__(self):
        self.metrics = {
            "new_version": {"requests": 0, "errors": 0, "latency": []},
            "current_version": {"requests": 0, "errors": 0, "latency": []}
        }
    
    def record(self, version, success, latency):
        self.metrics[version]["requests"] += 1
        if not success:
            self.metrics[version]["errors"] += 1
        self.metrics[version]["latency"].append(latency)
    
    def should_promote(self):
        new = self.metrics["new_version"]
        current = self.metrics["current_version"]
        
        # Check error rate
        new_error_rate = new["errors"] / new["requests"]
        current_error_rate = current["errors"] / current["requests"]
        
        if new_error_rate > current_error_rate * 1.1:
            return False  # New version has more errors
        
        # Check latency
        new_latency = sum(new["latency"]) / len(new["latency"])
        current_latency = sum(current["latency"]) / len(current["latency"])
        
        if new_latency > current_latency * 1.2:
            return False  # New version is slower
        
        return True
```

---

## A/B Testing

### Variant Assignment

```python
class ABTest:
    def __init__(self, test_id, variants):
        self.test_id = test_id
        self.variants = variants
    
    def assign_variant(self, user_id):
        # Deterministic assignment
        hash_value = hash(f"{self.test_id}:{user_id}")
        variant_index = hash_value % len(self.variants)
        return self.variants[variant_index]
    
    async def run(self, user_id, query):
        variant = self.assign_variant(user_id)
        
        start_time = time.time()
        try:
            result = await variant["agent"].run(query)
            success = True
        except Exception:
            result = None
            success = False
        
        latency = time.time() - start_time
        
        # Log metrics
        self.log_metrics(variant["name"], success, latency, result)
        
        return result
```

### Success Metrics

```python
class ABTestMetrics:
    def __init__(self):
        self.metrics = defaultdict(lambda: {
            "conversions": 0,
            "engagement": [],
            "satisfaction": [],
            "revenue": []
        })
    
    def track_conversion(self, variant, user_id):
        self.metrics[variant]["conversions"] += 1
    
    def track_engagement(self, variant, duration):
        self.metrics[variant]["engagement"].append(duration)
    
    def track_satisfaction(self, variant, score):
        self.metrics[variant]["satisfaction"].append(score)
    
    def get_winner(self):
        results = {}
        for variant, metrics in self.metrics.items():
            results[variant] = {
                "conversion_rate": metrics["conversions"] / len(metrics["engagement"]),
                "avg_engagement": sum(metrics["engagement"]) / len(metrics["engagement"]),
                "avg_satisfaction": sum(metrics["satisfaction"]) / len(metrics["satisfaction"])
            }
        
        # Return variant with highest composite score
        return max(results, key=lambda v: (
            results[v]["conversion_rate"] * 0.4 +
            results[v]["avg_satisfaction"] * 0.4 +
            results[v]["avg_engagement"] * 0.2
        ))
```

---

## Feature Flags

### Conditional Features

```python
class FeatureFlags:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def is_enabled(self, feature, user_id=None):
        # Global flag
        global_flag = self.redis.get(f"feature:{feature}:global")
        if global_flag == "true":
            return True
        if global_flag == "false":
            return False
        
        # User-specific flag
        if user_id:
            user_flag = self.redis.get(f"feature:{feature}:user:{user_id}")
            if user_flag:
                return user_flag == "true"
        
        # Percentage rollout
        percentage = self.redis.get(f"feature:{feature}:percentage")
        if percentage:
            hash_value = hash(f"{feature}:{user_id}") % 100
            return hash_value < int(percentage)
        
        return False

# Usage
if feature_flags.is_enabled("new_model", user_id):
    response = new_model.generate(query)
else:
    response = current_model.generate(query)
```

---

## Shadow Testing

### Parallel Execution

```python
class ShadowTest:
    def __init__(self, current_agent, new_agent):
        self.current = current_agent
        self.new = new_agent
    
    async def run(self, query):
        # Run current agent (returns to user)
        current_result = await self.current.run(query)
        
        # Run new agent in background (doesn't return)
        asyncio.create_task(self.compare(query, current_result))
        
        return current_result
    
    async def compare(self, query, current_result):
        try:
            new_result = await self.new.run(query)
            
            # Log comparison
            similarity = self.calculate_similarity(current_result, new_result)
            
            logger.info(f"Shadow test: similarity={similarity}")
            
            if similarity < 0.8:
                logger.warning(f"Significant difference detected: {query}")
        except Exception as e:
            logger.error(f"Shadow test error: {e}")
```

---

## Rollback Strategy

### Automatic Rollback

```python
class AutoRollback:
    def __init__(self, error_threshold=0.05, latency_threshold=2.0):
        self.error_threshold = error_threshold
        self.latency_threshold = latency_threshold
        self.windows = deque(maxlen=100)
    
    def check_health(self, error_rate, avg_latency):
        self.windows.append({
            "error_rate": error_rate,
            "latency": avg_latency
        })
        
        if len(self.windows) < 10:
            return True  # Not enough data
        
        recent = list(self.windows)[-10:]
        avg_error = sum(w["error_rate"] for w in recent) / len(recent)
        avg_latency = sum(w["latency"] for w in recent) / len(recent)
        
        if avg_error > self.error_threshold:
            logger.error(f"Error rate too high: {avg_error}")
            return False
        
        if avg_latency > self.latency_threshold:
            logger.error(f"Latency too high: {avg_latency}")
            return False
        
        return True
```

---

## The Testing Checklist

- [ ] Canary release (5% → 25% → 50% → 100%)
- [ ] A/B testing framework
- [ ] Feature flags
- [ ] Shadow testing
- [ ] Automatic rollback
- [ ] Metrics comparison
- [ ] Error rate monitoring
- [ ] Latency monitoring
- [ ] User satisfaction tracking
- [ ] Manual override capability

---

## Conclusion

Production testing:
- Reduces risk
- Catches edge cases
- Validates improvements
- Protects users

Test in production.
But do it safely.

---

*ArQon Agentics builds agents with safe production testing. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
