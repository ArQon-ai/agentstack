# Blog Post: The Agent Engineer's Guide to Event Sourcing
## Published: January 25, 2027
## Category: Engineering

---

# The Agent Engineer's Guide to Event Sourcing

*Store events. Replay state.*

---

## Why Event Sourcing?

### Benefits

- Audit trail
- Temporal queries
- Replay capability
- Decoupled systems

---

## Implementation

### 1. Event Store

```python
class EventStore:
    def __init__(self, db):
        self.db = db
    
    async def append(self, stream_id: str, event: Event):
        await self.db.execute(
            "INSERT INTO events (stream_id, type, data, version) VALUES ($1, $2, $3, $4)",
            stream_id, event.type, json.dumps(event.data), event.version
        )
    
    async def get_events(self, stream_id: str) -> list[Event]:
        rows = await self.db.fetch(
            "SELECT * FROM events WHERE stream_id = $1 ORDER BY version",
            stream_id
        )
        return [Event.from_row(row) for row in rows]
```

### 2. Agent Events

```python
class AgentCreated(Event):
    def __init__(self, agent_id: str, name: str, model: str):
        super().__init__("agent.created", {
            "agent_id": agent_id,
            "name": name,
            "model": model
        })

class MessageSent(Event):
    def __init__(self, conversation_id: str, content: str):
        super().__init__("message.sent", {
            "conversation_id": conversation_id,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
```

---

## The Event Sourcing Checklist

- [ ] Event design
- [ ] Event store
- [ ] Projection
- [ ] Snapshot
- [ ] Replay
- [ ] Schema evolution
- [ ] Event versioning
- [ ] Testing
- [ ] Performance
- [ ] Documentation

---

## Conclusion

Event sourcing:
- Stores history
- Enables replay
- Supports audit
- Adds complexity

Store events.
Project state.
Replay history.

---

*ArQon Agentics uses event sourcing. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
