# SEO Article: AI Agent Monitoring: Metrics That Matter in Production
**Target Keywords:** agent monitoring, LLM observability, agent metrics  
**Published:** October 7, 2026

---

# AI Agent Monitoring: Metrics That Matter in Production

Build visibility before you need it.

---

## The Three Pillars

### 1. Business Metrics

Measure value delivered:

| Metric | Description | Target |
|--------|-------------|--------|
| Requests/min | Throughput | Baseline + growth |
| Active Users | Engagement | Growing |
| Task Completion | Success rate | > 90% |
| User Satisfaction | Rating | > 4.0/5 |
| Retention | Return rate | > 60% |

### 2. Technical Metrics

Measure system health:

| Metric | Description | Alert |
|--------|-------------|-------|
| Latency p50 | Median response | > 2s |
| Latency p95 | 95th percentile | > 5s |
| Latency p99 | 99th percentile | > 10s |
| Error Rate | Failed requests | > 5% |
| Token Usage | Tokens/request | > 2x baseline |
| Cost/hour | Burn rate | > budget |

### 3. Quality Metrics

Measure output quality:

| Metric | Description | Target |
|--------|-------------|--------|
| Response Accuracy | Correct answers | > 85% |
| Hallucination Rate | False info | < 5% |
| Context Relevance | Retrieved context | > 80% |
| User Feedback | Explicit rating | > 4.0 |
| Escalation Rate | Human handoff | < 10% |

---

## Implementation

### Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge

class AgentMetrics:
    def __init__(self):
        # Counters
        self.requests = Counter('agent_requests_total', 'Total requests')
        self.errors = Counter('agent_errors_total', 'Errors', ['type'])
        self.tokens = Counter('agent_tokens_total', 'Tokens', ['model', 'type'])
        
        # Histograms
        self.latency = Histogram('agent_latency_seconds', 'Latency')
        self.tokens_per_request = Histogram('agent_tokens_per_request', 'Tokens per request')
        
        # Gauges
        self.active_users = Gauge('agent_active_users', 'Active users')
        self.cost_per_hour = Gauge('agent_cost_per_hour', 'Cost per hour')
```

### Instrumentation

```python
import time
from functools import wraps

def instrumented(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        start = time.time()
        
        try:
            result = await func(self, *args, **kwargs)
            
            # Record success
            self.metrics.requests.inc()
            self.metrics.latency.observe(time.time() - start)
            
            if hasattr(result, 'tokens'):
                self.metrics.tokens.labels(model=result.model, type='output').inc(result.tokens)
            
            return result
            
        except Exception as e:
            # Record failure
            self.metrics.errors.labels(type=type(e).__name__).inc()
            raise
    
    return wrapper
```

### Dashboard

```python
# Grafana dashboard configuration
dashboard = {
    "title": "Agent Monitoring",
    "panels": [
        {
            "title": "Requests/min",
            "type": "stat",
            "targets": [{
                "expr": "rate(agent_requests_total[1m])"
            }]
        },
        {
            "title": "Latency p95",
            "type": "graph",
            "targets": [{
                "expr": "histogram_quantile(0.95, rate(agent_latency_seconds_bucket[5m]))"
            }]
        },
        {
            "title": "Error Rate %",
            "type": "stat",
            "targets": [{
                "expr": "rate(agent_errors_total[5m]) / rate(agent_requests_total[5m]) * 100"
            }]
        },
        {
            "title": "Cost/hour",
            "type": "graph",
            "targets": [{
                "expr": "rate(agent_cost_total[1h])"
            }]
        }
    ]
}
```

---

## Alerting

### Critical Alerts

```yaml
groups:
  - name: agent_critical
    rules:
      - alert: AgentDown
        expr: up{job="agent"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Agent is down"
          
      - alert: HighErrorRate
        expr: rate(agent_errors_total[5m]) / rate(agent_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Error rate above 5%"
```

### Warning Alerts

```yaml
  - name: agent_warning
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(agent_latency_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "p95 latency above 5s"
          
      - alert: HighCost
        expr: rate(agent_cost_total[1h]) > 100
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Cost above $100/hour"
```

---

## Log Analysis

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

async def process_request(self, query):
    logger.info(
        "agent_request",
        user_id=user_id,
        query=query[:100],  # Truncate for privacy
        model="gpt-4o",
        timestamp=datetime.now().isoformat()
    )
    
    try:
        response = await self.agent.run(query)
        
        logger.info(
            "agent_response",
            user_id=user_id,
            latency_ms=int(response.latency * 1000),
            tokens=response.tokens,
            cost=response.cost,
            status="success"
        )
        
        return response
        
    except Exception as e:
        logger.error(
            "agent_error",
            user_id=user_id,
            error_type=type(e).__name__,
            error_message=str(e),
            query=query[:100]
        )
        raise
```

---

## Distributed Tracing

### OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Usage
async def process_request(self, query):
    with tracer.start_as_current_span("agent_request") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("query_length", len(query))
        
        with tracer.start_span("retrieval"):
            context = await self.retrieve(query)
            span.set_attribute("context_chunks", len(context))
        
        with tracer.start_span("generation"):
            response = await self.generate(query, context)
            span.set_attribute("response_length", len(response))
            span.set_attribute("tokens", response.tokens)
        
        return response
```

---

## The Monitoring Checklist

- [ ] Metrics collection
- [ ] Structured logging
- [ ] Distributed tracing
- [ ] Dashboard creation
- [ ] Alert configuration
- [ ] Error tracking
- [ ] Performance monitoring
- [ ] Cost tracking
- [ ] User analytics
- [ ] Quality metrics
- [ ] On-call rotation
- [ ] Incident response

---

## Conclusion

Monitoring:
- Prevents surprises
- Enables optimization
- Builds trust
- Drives improvement

Instrument everything.
Alert early.
Fix fast.

---

*ArQon Agentics builds observable agent systems. Get the open-source framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
