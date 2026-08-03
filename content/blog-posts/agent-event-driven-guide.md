# Blog Post: The Agent Engineer's Guide to Event-Driven Architecture
## Published: November 14, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to Event-Driven Architecture

*Build agents that react to the world.*

---

## Why Event-Driven?

### The Problem with Polling

```python
# Bad: Polling
while True:
    if has_new_email():
        process_email()
    time.sleep(60)  # Waste resources
```

### The Solution: Events

```python
# Good: Event-driven
@on_event("new_email")
async def handle_email(event):
    await process_email(event.data)
```

---

## Event Architecture

### Event Bus

```python
from typing import Callable
import asyncio

class EventBus:
    def __init__(self):
        self.subscribers: dict[str, list[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    async def publish(self, event_type: str, data: dict):
        handlers = self.subscribers.get(event_type, [])
        
        # Run all handlers concurrently
        await asyncio.gather(*[
            handler(data) for handler in handlers
        ])
```

### Event Types

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    type: str
    data: dict
    timestamp: datetime
    source: str
    id: str

# Agent events
class AgentEvents:
    REQUEST_RECEIVED = "agent.request_received"
    RESPONSE_GENERATED = "agent.response_generated"
    TOOL_CALLED = "agent.tool_called"
    ERROR_OCCURRED = "agent.error_occurred"
    COST_TRACKED = "agent.cost_tracked"
```

---

## Event Handlers

### Logging Handler

```python
class LoggingHandler:
    def __init__(self, logger):
        self.logger = logger
    
    async def handle(self, event: Event):
        self.logger.info(
            f"Event: {event.type}",
            extra={
                "event_id": event.id,
                "source": event.source,
                "data": event.data
            }
        )
```

### Metrics Handler

```python
class MetricsHandler:
    def __init__(self, metrics):
        self.metrics = metrics
    
    async def handle(self, event: Event):
        if event.type == AgentEvents.RESPONSE_GENERATED:
            latency = event.data.get("latency_ms", 0)
            self.metrics.histogram("agent_latency").observe(latency / 1000)
        
        elif event.type == AgentEvents.COST_TRACKED:
            cost = event.data.get("cost", 0)
            self.metrics.counter("agent_cost").inc(cost)
```

### Alerting Handler

```python
class AlertingHandler:
    def __init__(self, alert_service):
        self.alert_service = alert_service
    
    async def handle(self, event: Event):
        if event.type == AgentEvents.ERROR_OCCURRED:
            error_count = await self.get_error_count(last_minutes=5)
            
            if error_count > 10:
                await self.alert_service.send_alert(
                    severity="high",
                    message=f"High error rate: {error_count} errors in 5 minutes"
                )
```

---

## Event Sourcing

```python
class EventStore:
    def __init__(self, db):
        self.db = db
    
    async def append(self, event: Event):
        await self.db.execute(
            """INSERT INTO events (id, type, data, timestamp, source)
               VALUES ($1, $2, $3, $4, $5)""",
            event.id,
            event.type,
            json.dumps(event.data),
            event.timestamp,
            event.source
        )
    
    async def get_events(self, entity_id: str) -> list[Event]:
        rows = await self.db.fetch(
            """SELECT * FROM events
               WHERE data->>'entity_id' = $1
               ORDER BY timestamp""",
            entity_id
        )
        
        return [self.row_to_event(row) for row in rows]
    
    async def replay(self, entity_id: str, handler: Callable):
        """Replay events to rebuild state"""
        events = await self.get_events(entity_id)
        
        for event in events:
            await handler(event)
```

---

## The Event-Driven Checklist

- [ ] Define event types
- [ ] Implement event bus
- [ ] Create handlers
- [ ] Add error handling
- [ ] Monitor events
- [ ] Store events
- [ ] Enable replay
- [ ] Test handlers
- [ ] Document events
- [ ] Scale horizontally

---

## Conclusion

Event-driven architecture:
- Decouples components
- Enables real-time
- Supports scaling
- Improves reliability

React to events.
Don't poll.
Build reactive agents.

---

*ArQon Agentics builds event-driven agents. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
