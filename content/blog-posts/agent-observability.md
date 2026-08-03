# Blog Post: Agent Observability: Monitoring What Matters
## Published: September 30, 2026
## Category: Engineering

---

# Agent Observability: Monitoring What Matters

*You can't improve what you can't see. Here's how to instrument your agents.*

---

## The Observability Stack

### Metrics

Quantitative measurements:
- Request volume
- Latency percentiles
- Error rates
- Token usage
- Cost per request

### Logs

Structured event records:
- User queries
- Agent reasoning
- Tool calls
- Error traces
- Performance data

### Traces

End-to-end request flow:
- Request path
- Service dependencies
- Timing breakdown
- Error propagation

---

## Key Metrics

### Business Metrics

```python
business_metrics = {
    "requests_per_minute": Gauge("agent_rpm"),
    "active_users": Gauge("agent_active_users"),
    "conversations_per_user": Histogram("agent_conv_per_user"),
    "retention_rate": Gauge("agent_retention"),
    "user_satisfaction": Gauge("agent_satisfaction")
}
```

### Technical Metrics

```python
technical_metrics = {
    "latency_p50": Histogram("agent_latency", ["model"]),
    "latency_p95": Histogram("agent_latency", ["model"]),
    "latency_p99": Histogram("agent_latency", ["model"]),
    "error_rate": Counter("agent_errors", ["type"]),
    "token_usage": Counter("agent_tokens", ["model", "type"]),
    "cost_per_request": Gauge("agent_cost")
}
```

### Quality Metrics

```python
quality_metrics = {
    "response_accuracy": Gauge("agent_accuracy"),
    "hallucination_rate": Gauge("agent_hallucinations"),
    "context_relevance": Gauge("agent_relevance"),
    "user_feedback_score": Gauge("agent_feedback"),
    "human_escalation_rate": Gauge("agent_escalations")
}
```

---

## Logging

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

async def process_request(self, query):
    logger.info(
        "agent_request",
        user_id=user_id,
        query=query,
        model="gpt-4o",
        timestamp=datetime.now()
    )
    
    try:
        response = await self.agent.run(query)
        
        logger.info(
            "agent_response",
            user_id=user_id,
            response_length=len(response),
            tokens_used=response.tokens,
            cost=response.cost,
            latency=response.latency
        )
        
        return response
    except Exception as e:
        logger.error(
            "agent_error",
            user_id=user_id,
            error_type=type(e).__name__,
            error_message=str(e),
            query=query
        )
        raise
```

### Log Levels

```python
# DEBUG: Detailed debugging
logger.debug("tool_called", tool=tool_name, params=params)

# INFO: Normal operations
logger.info("request_processed", latency=latency)

# WARNING: Unexpected but handled
logger.warning("high_latency", latency=latency, threshold=threshold)

# ERROR: Failed operations
logger.error("request_failed", error=error, query=query)

# CRITICAL: System failure
logger.critical("service_down", reason=reason)
```

---

## Tracing

### OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

exporter = OTLPSpanExporter(endpoint="localhost:4317")
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Usage
async def process_request(self, query):
    with tracer.start_as_current_span("agent_request") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("query", query)
        
        with tracer.start_span("retrieval"):
            context = await self.retrieve(query)
        
        with tracer.start_span("generation"):
            response = await self.generate(query, context)
        
        span.set_attribute("latency", response.latency)
        span.set_attribute("tokens", response.tokens)
        
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
        "title": "Requests/min",
        "targets": [{"expr": "rate(agent_requests_total[1m])"}]
      },
      {
        "title": "Latency p95",
        "targets": [{"expr": "histogram_quantile(0.95, rate(agent_latency_bucket[5m]))"}]
      },
      {
        "title": "Error Rate",
        "targets": [{"expr": "rate(agent_errors_total[5m]) / rate(agent_requests_total[5m])"}]
      },
      {
        "title": "Cost/hour",
        "targets": [{"expr": "rate(agent_cost_total[1h])"}]
      }
    ]
  }
}
```

---

## Alerting

### Alert Rules

```yaml
groups:
  - name: agent_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(agent_errors_total[5m]) / rate(agent_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(agent_latency_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          
      - alert: HighCost
        expr: rate(agent_cost_total[1h]) > 100
        for: 10m
        labels:
          severity: info
        annotations:
          summary: "High cost detected"
```

---

## The Observability Checklist

- [ ] Metrics collection
- [ ] Structured logging
- [ ] Distributed tracing
- [ ] Dashboards
- [ ] Alerting
- [ ] Error tracking
- [ ] Performance monitoring
- [ ] Cost tracking
- [ ] User analytics
- [ ] Quality metrics

---

## Conclusion

Observability:
- Enables debugging
- Prevents issues
- Optimizes costs
- Improves quality

Instrument everything.
Monitor continuously.
Alert proactively.

---

*ArQon Agentics builds agents with production-grade observability. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
