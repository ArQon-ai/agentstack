# Blog Post: The Agent Engineer's Guide to Testing in Production
## Published: November 2, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to Testing in Production

*Test in prod safely. Ship with confidence.*

---

## Why Test in Production?

### The Problem with Staging

- Staging ≠ Production
- Data is different
- Load is different
- Users are different

### Benefits of Prod Testing

- Real data
- Real load
- Real users
- Real results

---

## Safe Production Testing

### 1. Feature Flags

```python
class FeatureFlag:
    def __init__(self, name, default=False):
        self.name = name
        self.default = default
        self.overrides = {}
    
    def is_enabled(self, user_id: str = None) -> bool:
        # Check user override
        if user_id and user_id in self.overrides:
            return self.overrides[user_id]
        
        # Check percentage rollout
        if user_id:
            return self._is_in_rollout(user_id)
        
        return self.default
    
    def _is_in_rollout(self, user_id: str) -> bool:
        # Deterministic based on user ID
        hash_val = int(hashlib.md5(f"{self.name}:{user_id}".encode()).hexdigest(), 16)
        return hash_val % 100 < self.rollout_percentage

# Usage
new_model = FeatureFlag("new-model", rollout_percentage=10)

async def handle_request(user_id: str, query: str):
    if new_model.is_enabled(user_id):
        return await agent_v2.run(query)
    else:
        return await agent_v1.run(query)
```

### 2. Canary Deployments

```python
class CanaryDeployment:
    def __init__(self, traffic_split=0.05):
        self.traffic_split = traffic_split
        self.metrics = {
            "v1": {"requests": 0, "errors": 0, "latency": []},
            "v2": {"requests": 0, "errors": 0, "latency": []}
        }
    
    async def route(self, request):
        # Route 5% to v2
        if random.random() < self.traffic_split:
            version = "v2"
        else:
            version = "v1"
        
        start = time.time()
        try:
            if version == "v2":
                response = await agent_v2.run(request)
            else:
                response = await agent_v1.run(request)
            
            self.metrics[version]["requests"] += 1
            self.metrics[version]["latency"].append(time.time() - start)
            
            return response
            
        except Exception as e:
            self.metrics[version]["errors"] += 1
            raise
    
    def should_promote(self) -> bool:
        # Promote if v2 error rate < v1 and latency similar
        v1_error_rate = self.metrics["v1"]["errors"] / max(self.metrics["v1"]["requests"], 1)
        v2_error_rate = self.metrics["v2"]["errors"] / max(self.metrics["v2"]["requests"], 1)
        
        return v2_error_rate <= v1_error_rate * 1.1
```

### 3. Shadow Traffic

```python
class ShadowTraffic:
    def __init__(self):
        self.shadow_results = []
    
    async def handle_with_shadow(self, request):
        # Send to production
        prod_response = await agent_v1.run(request)
        
        # Also send to new version (async, don't wait)
        asyncio.create_task(self._shadow_run(request, prod_response))
        
        return prod_response
    
    async def _shadow_run(self, request, prod_response):
        try:
            shadow_response = await agent_v2.run(request)
            
            # Compare responses
            similarity = self.compare_responses(prod_response, shadow_response)
            
            self.shadow_results.append({
                "request": request,
                "prod": prod_response,
                "shadow": shadow_response,
                "similarity": similarity
            })
            
        except Exception as e:
            logger.error(f"Shadow run failed: {e}")
```

---

## Monitoring Production Tests

### A/B Testing

```python
class ABTest:
    def __init__(self, name, variants):
        self.name = name
        self.variants = variants
        self.results = {v: {"conversions": 0, "total": 0} for v in variants}
    
    def get_variant(self, user_id: str) -> str:
        # Deterministic assignment
        hash_val = int(hashlib.md5(f"{self.name}:{user_id}".encode()).hexdigest(), 16)
        index = hash_val % len(self.variants)
        return self.variants[index]
    
    def track_conversion(self, user_id: str):
        variant = self.get_variant(user_id)
        self.results[variant]["conversions"] += 1
    
    def get_results(self):
        return {
            variant: {
                "conversion_rate": r["conversions"] / max(r["total"], 1),
                "total": r["total"]
            }
            for variant, r in self.results.items()
        }
```

---

## Rollback Strategy

```python
class SafeDeployer:
    def __init__(self):
        self.rollback_threshold = 0.05  # 5% error rate
    
    async def deploy(self, new_version):
        # Start with 1%
        await self.set_traffic_split(0.01)
        
        # Monitor for 10 minutes
        await asyncio.sleep(600)
        
        if await self.is_healthy():
            # Increase to 10%
            await self.set_traffic_split(0.10)
            await asyncio.sleep(600)
            
            if await self.is_healthy():
                # Full rollout
                await self.set_traffic_split(1.0)
            else:
                await self.rollback()
        else:
            await self.rollback()
    
    async def is_healthy(self) -> bool:
        metrics = await self.get_metrics()
        return metrics["error_rate"] < self.rollback_threshold
    
    async def rollback(self):
        logger.error("Rolling back deployment")
        await self.set_traffic_split(0.0)  # 0% to new version
```

---

## The Production Testing Checklist

- [ ] Feature flags implemented
- [ ] Canary deployment ready
- [ ] Shadow traffic configured
- [ ] A/B testing framework
- [ ] Rollback automated
- [ ] Metrics collected
- [ ] Alerts configured
- [ ] Runbook documented
- [ ] Team trained
- [ ] Test in staging first
- [ ] Gradual rollout
- [ ] Monitor continuously

---

## Conclusion

Production testing:
- Is necessary
- Can be safe
- Requires tooling
- Needs monitoring

Test in prod.
Do it safely.
Ship confidently.

---

*ArQon Agentics tests agents in production. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
