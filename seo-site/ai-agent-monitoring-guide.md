# SEO Article: AI Agent Monitoring: Tools and Best Practices
**Target Keywords:** agent monitoring, LLM monitoring, agent observability  
**Published:** October 30, 2026

---

# AI Agent Monitoring: Tools and Best Practices

*You can't improve what you don't measure.*

---

## Key Metrics

### Performance Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Latency (p50) | Median response time | < 2s |
| Latency (p99) | 99th percentile | < 5s |
| Throughput | Requests per minute | > 100 |
| Error Rate | Failed requests / Total | < 1% |
| Uptime | Service availability | > 99.9% |

### Business Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Cost per Request | LLM cost / Requests | < $0.05 |
| Token Efficiency | Output tokens / Input tokens | > 0.5 |
| User Satisfaction | Positive feedback / Total | > 80% |
| Task Completion | Completed / Started | > 90% |

### LLM Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Token Usage | Tokens per request | < 2000 |
| Model Distribution | Usage by model | Track |
| Prompt Cache Hit | Cached / Total | > 30% |
| Retry Rate | Retries / Total | < 5% |

---

## Monitoring Stack

### Prometheus + Grafana

```python
from prometheus_client import Counter, Histogram, Gauge, Info

# Request metrics
requests_total = Counter("agent_requests_total", ["method", "endpoint", "status"])
request_duration = Histogram("agent_request_duration_seconds", ["endpoint"])

# LLM metrics
llm_tokens_total = Counter("llm_tokens_total", ["model", "type"])
llm_cost_total = Counter("llm_cost_total", ["model"])
llm_latency = Histogram("llm_latency_seconds", ["model"])

# Business metrics
active_sessions = Gauge("agent_active_sessions")
queue_size = Gauge("agent_queue_size")

# System metrics
memory_usage = Gauge("agent_memory_usage_bytes")
cpu_usage = Gauge("agent_cpu_usage_percent")
```

### Logging with Structured Logs

```python
import structlog

logger = structlog.get_logger()

# Request logging
logger.info(
    "agent_request",
    user_id=user_id,
    query=query[:100],
    model=model,
    tokens_input=tokens_in,
    tokens_output=tokens_out,
    cost=cost,
    latency_ms=latency,
    status="success"
)

# Error logging
logger.error(
    "agent_error",
    error_type=type(error).__name__,
    error_message=str(error),
    user_id=user_id,
    query=query[:100],
    traceback=traceback.format_exc()
)
```

---

## Alerting

### Alert Rules

```yaml
# prometheus/alerts.yml
groups:
- name: agent_alerts
  rules:
  - alert: HighErrorRate
    expr: rate(agent_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      
  - alert: HighLatency
    expr: histogram_quantile(0.99, rate(agent_request_duration_seconds_bucket[5m])) > 5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High latency detected"
      
  - alert: HighCost
    expr: rate(llm_cost_total[1h]) > 10
    for: 1h
    labels:
      severity: warning
    annotations:
      summary: "High LLM cost detected"
```

### On-Call Rotation

```python
class OnCallManager:
    def __init__(self, rotation):
        self.rotation = rotation
        self.current = 0
    
    def get_on_call(self):
        return self.rotation[self.current % len(self.rotation)]
    
    def rotate(self):
        self.current += 1
    
    async def alert(self, severity, message):
        on_call = self.get_on_call()
        
        if severity == "critical":
            await self.page(on_call, message)
        elif severity == "warning":
            await self.slack(on_call, message)
        else:
            await self.email(on_call, message)
```

---

## Distributed Tracing

### OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup
tracer_provider = TracerProvider()
otlp_exporter = OTLPSpanExporter(endpoint="otel-collector:4317")
tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer("agent")

# Usage
async def process_request(request):
    with tracer.start_as_current_span("process_request") as span:
        span.set_attribute("user.id", request.user_id)
        span.set_attribute("query.length", len(request.query))
        
        # Sub-span for LLM call
        with tracer.start_as_current_span("llm_call") as llm_span:
            response = await llm.generate(request.query)
            llm_span.set_attribute("tokens.used", response.tokens)
            llm_span.set_attribute("cost", response.cost)
        
        return response
```

---

## Dashboards

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Agent Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(agent_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Latency (p99)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, rate(agent_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(agent_requests_total{status=~\"5..\"}[5m]) / rate(agent_requests_total[5m])"
          }
        ]
      },
      {
        "title": "LLM Cost",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(llm_cost_total[1h])"
          }
        ]
      }
    ]
  }
}
```

---

## The Monitoring Checklist

- [ ] Metrics collection
- [ ] Structured logging
- [ ] Distributed tracing
- [ ] Alerting rules
- [ ] Dashboards
- [ ] On-call rotation
- [ ] Runbooks
- [ ] Post-mortems
- [ ] SLOs defined
- [ ] Error budgets

---

## Conclusion

Monitoring:
- Prevents outages
- Controls costs
- Improves quality
- Enables iteration

Instrument everything.
Alert on symptoms.
Measure what matters.

---

*ArQon Agentics monitors agents in production. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
