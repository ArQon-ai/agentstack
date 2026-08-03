# Blog Post: The Agent Engineer's Guide to Feature Flags
## Published: November 8, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to Feature Flags

*Ship without fear. Test in production. Roll back instantly.*

---

## Why Feature Flags?

### The Problem

- **Deploy anxiety**: Will this break?
- **Long release cycles**: Test everything
- **No experimentation**: Can't A/B test
- **Hard rollbacks**: Re-deploy to revert

### The Solution

- Deploy code, release features separately
- Test with small user groups
- Roll back in seconds
- Experiment safely

---

## Feature Flag Implementation

### Basic Flag

```python
class FeatureFlag:
    def __init__(self, name: str, default: bool = False):
        self.name = name
        self.default = default
        self.overrides = {}
        self.rollout_percentage = 0
    
    def enable_for(self, user_id: str):
        self.overrides[user_id] = True
    
    def disable_for(self, user_id: str):
        self.overrides[user_id] = False
    
    def set_rollout(self, percentage: int):
        self.rollout_percentage = max(0, min(100, percentage))
    
    def is_enabled(self, user_id: str = None) -> bool:
        # Check explicit override
        if user_id in self.overrides:
            return self.overrides[user_id]
        
        # Check percentage rollout
        if user_id:
            return self._is_in_rollout(user_id)
        
        return self.default
    
    def _is_in_rollout(self, user_id: str) -> bool:
        # Deterministic based on user ID
        hash_val = int(hashlib.md5(
            f"{self.name}:{user_id}".encode()
        ).hexdigest(), 16)
        return hash_val % 100 < self.rollout_percentage
```

### Flag Manager

```python
class FeatureFlagManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.flags = {}
    
    def create_flag(self, name: str, default: bool = False) -> FeatureFlag:
        flag = FeatureFlag(name, default)
        self.flags[name] = flag
        return flag
    
    def get_flag(self, name: str) -> FeatureFlag:
        return self.flags.get(name)
    
    async def sync_from_redis(self):
        """Load flag states from Redis"""
        for name, flag in self.flags.items():
            state = await self.redis.get(f"flag:{name}")
            if state:
                data = json.loads(state)
                flag.default = data.get("default", False)
                flag.rollout_percentage = data.get("rollout", 0)
                flag.overrides = data.get("overrides", {})
    
    async def save_to_redis(self, name: str):
        """Save flag state to Redis"""
        flag = self.flags.get(name)
        if flag:
            await self.redis.set(f"flag:{name}", json.dumps({
                "default": flag.default,
                "rollout": flag.rollout_percentage,
                "overrides": flag.overrides
            }))
```

---

## Use Cases

### 1. Gradual Rollout

```python
# Create flag
new_model = flag_manager.create_flag("new-llm-model", default=False)

# Start with 1%
new_model.set_rollout(1)

# Monitor for errors
# If good, increase
new_model.set_rollout(10)
new_model.set_rollout(50)
new_model.set_rollout(100)

# Usage
async def handle_request(user_id: str, query: str):
    if new_model.is_enabled(user_id):
        return await agent_v2.run(query)
    else:
        return await agent_v1.run(query)
```

### 2. A/B Testing

```python
# Create experiment flag
experiment = flag_manager.create_flag("new-ui-experiment")
experiment.set_rollout(50)  # 50/50 split

# Track metrics
async def track_conversion(user_id: str, converted: bool):
    variant = "new" if experiment.is_enabled(user_id) else "old"
    
    await analytics.track("conversion", {
        "variant": variant,
        "converted": converted,
        "user_id": user_id
    })
```

### 3. Kill Switch

```python
# Create emergency flag
emergency_mode = flag_manager.create_flag("emergency-mode", default=False)

# In case of outage
async def handle_request(user_id: str, query: str):
    if emergency_mode.is_enabled():
        return {"error": "Service temporarily unavailable"}
    
    return await agent.run(query)

# Enable instantly in emergency
# No deploy needed
```

---

## Best Practices

### 1. Naming

```python
# Good: Descriptive
"new-llm-model"
"async-processing"
"enhanced-memory"

# Bad: Vague
"feature-1"
"test"
"new-thing"
```

### 2. Cleanup

```python
class FlagCleanup:
    async def remove_old_flags(self, max_age_days=30):
        """Remove flags that have been fully rolled out"""
        
        for name, flag in self.flags.items():
            if flag.rollout_percentage == 100:
                # Check if stable for 30 days
                state = await self.redis.get(f"flag:{name}:rolled_out_at")
                if state:
                    rolled_out = datetime.fromisoformat(state)
                    if datetime.now() - rolled_out > timedelta(days=max_age_days):
                        # Remove flag from code first
                        # Then remove from manager
                        del self.flags[name]
                        await self.redis.delete(f"flag:{name}")
```

### 3. Monitoring

```python
class FlagMonitor:
    async def track_flag_usage(self, flag_name: str, user_id: str):
        await self.redis.incr(f"flag:{flag_name}:impressions")
        
        if flag_manager.get_flag(flag_name).is_enabled(user_id):
            await self.redis.incr(f"flag:{flag_name}:enabled")
    
    async def get_flag_stats(self, flag_name: str) -> dict:
        impressions = int(await self.redis.get(f"flag:{flag_name}:impressions") or 0)
        enabled = int(await self.redis.get(f"flag:{flag_name}:enabled") or 0)
        
        return {
            "impressions": impressions,
            "enabled": enabled,
            "rate": enabled / max(impressions, 1)
        }
```

---

## The Feature Flag Checklist

- [ ] Implement flag system
- [ ] Add gradual rollout
- [ ] Create kill switches
- [ ] A/B test features
- [ ] Monitor flag usage
- [ ] Clean up old flags
- [ ] Document flags
- [ ] Test flag logic
- [ ] Alert on errors
- [ ] Train team

---

## Conclusion

Feature flags:
- Enable safe deploys
- Support experimentation
- Allow instant rollback
- Require discipline

Flag everything.
Release gradually.
Clean up regularly.

---

*ArQon Agentics uses feature flags in production. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
