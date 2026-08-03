# Blog Post: The Agent Engineer's Guide to Load Testing
## Published: October 13, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to Load Testing

*Know your limits before users do.*

---

## Why Load Test Agents?

Agents have unique load characteristics:
- Variable latency (LLM-dependent)
- Token costs scale with load
- Context grows over time
- Rate limits from providers

Load testing reveals:
- Breaking points
- Cost at scale
- Latency degradation
- Resource bottlenecks

---

## Load Testing Framework

### Test Scenarios

```python
class LoadTestScenario:
    def __init__(self):
        self.scenarios = {
            "steady_state": {
                "description": "Normal traffic",
                "rps": 10,  # requests per second
                "duration": 300  # 5 minutes
            },
            "spike": {
                "description": "Traffic spike",
                "rps": 100,
                "duration": 60
            },
            "stress": {
                "description": "Maximum load",
                "rps": 500,
                "duration": 300
            },
            "endurance": {
                "description": "Sustained load",
                "rps": 50,
                "duration": 3600  # 1 hour
            }
        }
```

### Test Runner

```python
import asyncio
import aiohttp
from dataclasses import dataclass
from typing import List

@dataclass
class LoadTestResult:
    scenario: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_latency: float
    p50_latency: float
    p95_latency: float
    p99_latency: float
    rps: float
    errors: List[str]

class LoadTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = []
    
    async def run_scenario(self, scenario_name: str, config: dict):
        semaphore = asyncio.Semaphore(config["rps"])
        
        start_time = time.time()
        tasks = []
        
        for _ in range(config["rps"] * config["duration"]):
            task = self._make_request(semaphore)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        
        # Calculate metrics
        latencies = [r["latency"] for r in responses if isinstance(r, dict)]
        errors = [str(r) for r in responses if isinstance(r, Exception)]
        
        result = LoadTestResult(
            scenario=scenario_name,
            total_requests=len(responses),
            successful_requests=len([r for r in responses if isinstance(r, dict)]),
            failed_requests=len(errors),
            avg_latency=sum(latencies) / len(latencies) if latencies else 0,
            p50_latency=sorted(latencies)[len(latencies)//2] if latencies else 0,
            p95_latency=sorted(latencies)[int(len(latencies)*0.95)] if latencies else 0,
            p99_latency=sorted(latencies)[int(len(latencies)*0.99)] if latencies else 0,
            rps=len(responses) / (end_time - start_time),
            errors=errors[:10]  # First 10 errors
        )
        
        return result
    
    async def _make_request(self, semaphore: asyncio.Semaphore):
        async with semaphore:
            start = time.time()
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/agent/run",
                        json={"query": "Test query for load testing"}
                    ) as response:
                        await response.json()
                        
                        return {
                            "latency": time.time() - start,
                            "status": response.status
                        }
            except Exception as e:
                return e
```

---

## Measuring LLM-Specific Metrics

### Token Throughput

```python
class TokenMetrics:
    def __init__(self):
        self.tokens_per_second = Gauge("agent_tokens_per_second")
        self.cost_per_request = Gauge("agent_cost_per_request")
    
    async def track(self, response):
        if hasattr(response, "tokens"):
            self.tokens_per_second.set(
                response.tokens / response.latency
            )
        
        if hasattr(response, "cost"):
            self.cost_per_request.set(response.cost)
```

### Rate Limit Monitoring

```python
class RateLimitMonitor:
    def __init__(self):
        self.rate_limit_hits = Counter("agent_rate_limit_hits")
        self.backoff_time = Gauge("agent_backoff_seconds")
    
    async def handle_rate_limit(self, retry_after):
        self.rate_limit_hits.inc()
        self.backoff_time.set(retry_after)
        
        await asyncio.sleep(retry_after)
```

---

## Cost Projection

### Scaling Cost Calculator

```python
class CostProjector:
    def __init__(self, load_test_results):
        self.results = load_test_results
    
    def project_monthly_cost(self, target_rps):
        # Find closest test scenario
        closest = min(
            self.results,
            key=lambda r: abs(r.rps - target_rps)
        )
        
        # Calculate cost per request
        cost_per_request = closest.avg_cost
        
        # Project monthly
        requests_per_month = target_rps * 3600 * 24 * 30
        monthly_cost = requests_per_month * cost_per_request
        
        return {
            "target_rps": target_rps,
            "cost_per_request": cost_per_request,
            "monthly_requests": requests_per_month,
            "monthly_cost": monthly_cost,
            "confidence": self.calculate_confidence(closest, target_rps)
        }
```

---

## Bottleneck Identification

### Resource Monitoring

```python
class ResourceMonitor:
    def __init__(self):
        self.metrics = {
            "cpu": Gauge("agent_cpu_percent"),
            "memory": Gauge("agent_memory_percent"),
            "db_connections": Gauge("agent_db_connections"),
            "redis_connections": Gauge("agent_redis_connections")
        }
    
    async def sample(self):
        import psutil
        
        self.metrics["cpu"].set(psutil.cpu_percent())
        self.metrics["memory"].set(psutil.virtual_memory().percent)
        
        # DB connections
        db_stats = await self.db_pool.stats()
        self.metrics["db_connections"].set(db_stats["active"])
```

### Bottleneck Detection

```python
class BottleneckDetector:
    def __init__(self):
        self.thresholds = {
            "cpu": 80,
            "memory": 85,
            "db_connections": 90,
            "latency_p95": 5.0
        }
    
    def detect(self, metrics):
        bottlenecks = []
        
        for resource, threshold in self.thresholds.items():
            if metrics[resource] > threshold:
                bottlenecks.append({
                    "resource": resource,
                    "current": metrics[resource],
                    "threshold": threshold,
                    "severity": "critical" if metrics[resource] > threshold * 1.2 else "warning"
                })
        
        return bottlenecks
```

---

## The Load Testing Checklist

- [ ] Define test scenarios
- [ ] Set up monitoring
- [ ] Run baseline test
- [ ] Test at 2x expected load
- [ ] Test at 5x expected load
- [ ] Test sustained load
- [ ] Test traffic spikes
- [ ] Measure token throughput
- [ ] Calculate cost projections
- [ ] Identify bottlenecks
- [ ] Document limits
- [ ] Create scaling plan

---

## Conclusion

Load testing:
- Prevents surprises
- Controls costs
- Identifies limits
- Enables scaling

Test before you scale.
Measure before you optimize.

---

*ArQon Agentics builds agents that scale. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
