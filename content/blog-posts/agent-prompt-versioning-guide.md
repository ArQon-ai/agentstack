# Blog Post: The Agent Engineer's Guide to Prompt Versioning
## Published: November 12, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to Prompt Versioning

*Version your prompts like you version your code.*

---

## Why Version Prompts?

### The Problem

- Prompts change frequently
- Hard to track what works
- Difficult to roll back
- No audit trail
- Team confusion

### The Solution

- Version control for prompts
- A/B testing
- Rollback capability
- Performance tracking
- Team collaboration

---

## Prompt Versioning System

### Version Storage

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PromptVersion:
    id: str
    name: str
    content: str
    version: int
    created_at: datetime
    created_by: str
    metrics: dict
    is_active: bool

class PromptRegistry:
    def __init__(self, db):
        self.db = db
    
    async def create_version(self, name: str, content: str, created_by: str) -> PromptVersion:
        # Get next version number
        versions = await self.get_versions(name)
        next_version = max([v.version for v in versions], default=0) + 1
        
        prompt = PromptVersion(
            id=str(uuid.uuid4()),
            name=name,
            content=content,
            version=next_version,
            created_at=datetime.now(),
            created_by=created_by,
            metrics={},
            is_active=False
        )
        
        await self.db.insert(prompt)
        return prompt
    
    async def activate_version(self, prompt_id: str):
        # Deactivate all versions of this prompt
        prompt = await self.db.get(prompt_id)
        await self.db.execute(
            "UPDATE prompts SET is_active = false WHERE name = $1",
            prompt.name
        )
        
        # Activate new version
        await self.db.execute(
            "UPDATE prompts SET is_active = true WHERE id = $1",
            prompt_id
        )
    
    async def get_active_version(self, name: str) -> PromptVersion:
        return await self.db.fetch_one(
            "SELECT * FROM prompts WHERE name = $1 AND is_active = true",
            name
        )
    
    async def get_versions(self, name: str) -> list[PromptVersion]:
        return await self.db.fetch(
            "SELECT * FROM prompts WHERE name = $1 ORDER BY version DESC",
            name
        )
```

### Git Integration

```python
class GitPromptStore:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
    
    def save_prompt(self, name: str, content: str, message: str):
        # Save to file
        file_path = f"{self.repo_path}/prompts/{name}.md"
        with open(file_path, "w") as f:
            f.write(content)
        
        # Git commit
        subprocess.run(["git", "add", file_path], cwd=self.repo_path)
        subprocess.run(["git", "commit", "-m", message], cwd=self.repo_path)
    
    def get_prompt(self, name: str, commit: str = None) -> str:
        file_path = f"prompts/{name}.md"
        
        if commit:
            result = subprocess.run(
                ["git", "show", f"{commit}:{file_path}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.stdout
        else:
            with open(f"{self.repo_path}/{file_path}") as f:
                return f.read()
```

---

## A/B Testing Prompts

```python
class PromptABTest:
    def __init__(self, registry: PromptRegistry):
        self.registry = registry
    
    async def run_experiment(self, prompt_name: str, versions: list[str]):
        # Create experiment
        experiment = {
            "name": f"{prompt_name}-ab-test",
            "variants": versions,
            "weights": [1.0 / len(versions)] * len(versions)
        }
        
        # Assign users to variants
        for user_id in await self.get_test_users():
            variant = self.assign_variant(experiment, user_id)
            prompt = await self.registry.get_version(prompt_name, variant)
            
            # Run prompt
            response = await self.run_prompt(prompt, user_id)
            
            # Track metrics
            await self.track_metrics(experiment["name"], variant, response)
    
    def assign_variant(self, experiment: dict, user_id: str) -> str:
        hash_val = int(hashlib.md5(
            f"{experiment['name']}:{user_id}".encode()
        ).hexdigest(), 16)
        
        index = hash_val % len(experiment["variants"])
        return experiment["variants"][index]
```

---

## Performance Tracking

```python
class PromptPerformanceTracker:
    def __init__(self):
        self.metrics = {}
    
    async def track(self, prompt_id: str, response: str, duration: float):
        if prompt_id not in self.metrics:
            self.metrics[prompt_id] = {
                "runs": 0,
                "total_latency": 0,
                "successes": 0,
                "failures": 0
            }
        
        self.metrics[prompt_id]["runs"] += 1
        self.metrics[prompt_id]["total_latency"] += duration
        
        # Check if response is valid
        if await self.is_valid(response):
            self.metrics[prompt_id]["successes"] += 1
        else:
            self.metrics[prompt_id]["failures"] += 1
    
    def get_stats(self, prompt_id: str) -> dict:
        m = self.metrics.get(prompt_id, {})
        runs = m.get("runs", 0)
        
        return {
            "runs": runs,
            "avg_latency": m.get("total_latency", 0) / max(runs, 1),
            "success_rate": m.get("successes", 0) / max(runs, 1),
            "failure_rate": m.get("failures", 0) / max(runs, 1)
        }
```

---

## The Prompt Versioning Checklist

- [ ] Store prompts in version control
- [ ] Track changes
- [ ] A/B test versions
- [ ] Measure performance
- [ ] Enable rollbacks
- [ ] Document changes
- [ ] Team access
- [ ] Review process
- [ ] Automated testing
- [ ] Performance monitoring

---

## Conclusion

Prompt versioning:
- Enables experimentation
- Supports collaboration
- Prevents regressions
- Improves quality

Version everything.
Test thoroughly.
Measure always.

---

*ArQon Agentics versions all prompts. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
