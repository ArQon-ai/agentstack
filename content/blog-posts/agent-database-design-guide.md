# Blog Post: The Agent Engineer's Guide to Database Design
## Published: October 27, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to Database Design

*Design databases that scale with your agents.*

---

## Schema Design

### Core Tables

```sql
-- Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    tokens_used INTEGER,
    model VARCHAR(50),
    cost DECIMAL(10, 6),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agents
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    system_prompt TEXT,
    model VARCHAR(50) DEFAULT 'gpt-4o',
    temperature DECIMAL(3, 2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 2000,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent Runs
CREATE TABLE agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id),
    conversation_id UUID REFERENCES conversations(id),
    input TEXT NOT NULL,
    output TEXT,
    tokens_input INTEGER,
    tokens_output INTEGER,
    cost DECIMAL(10, 6),
    latency_ms INTEGER,
    status VARCHAR(20) DEFAULT 'running',
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
```

### Indexes

```sql
-- For conversation lookups
CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at);

-- For user history
CREATE INDEX idx_conversations_user ON conversations(user_id, updated_at DESC);

-- For cost tracking
CREATE INDEX idx_agent_runs_cost ON agent_runs(agent_id, created_at) 
WHERE cost IS NOT NULL;

-- For monitoring
CREATE INDEX idx_agent_runs_status ON agent_runs(status, created_at) 
WHERE status != 'completed';

-- For token usage
CREATE INDEX idx_messages_tokens ON messages(conversation_id, tokens_used) 
WHERE tokens_used > 0;
```

---

## Query Patterns

### Conversation History

```python
async def get_conversation_history(
    conversation_id: UUID,
    limit: int = 50
) -> list[Message]:
    query = """
    SELECT * FROM messages
    WHERE conversation_id = $1
    ORDER BY created_at DESC
    LIMIT $2
    """
    
    rows = await db.fetch(query, conversation_id, limit)
    return [Message.from_row(row) for row in reversed(rows)]
```

### Cost Analysis

```python
async def get_cost_breakdown(
    start_date: datetime,
    end_date: datetime
) -> dict:
    query = """
    SELECT 
        DATE(created_at) as date,
        agent_id,
        COUNT(*) as runs,
        SUM(tokens_input) as tokens_in,
        SUM(tokens_output) as tokens_out,
        SUM(cost) as total_cost
    FROM agent_runs
    WHERE created_at BETWEEN $1 AND $2
    GROUP BY DATE(created_at), agent_id
    ORDER BY date DESC
    """
    
    rows = await db.fetch(query, start_date, end_date)
    
    return {
        "daily": [dict(row) for row in rows],
        "total_cost": sum(r["total_cost"] for r in rows),
        "total_runs": sum(r["runs"] for r in rows)
    }
```

---

## Data Retention

### Archiving Strategy

```python
class DataArchiver:
    def __init__(self, db, archive_storage):
        self.db = db
        self.archive = archive_storage
    
    async def archive_old_conversations(self, days: int = 90):
        cutoff = datetime.now() - timedelta(days=days)
        
        # Find old conversations
        old_conversations = await self.db.fetch(
            """
            SELECT id FROM conversations
            WHERE updated_at < $1
            AND status = 'archived'
            """,
            cutoff
        )
        
        for conv in old_conversations:
            # Archive messages
            messages = await self.db.fetch(
                "SELECT * FROM messages WHERE conversation_id = $1",
                conv["id"]
            )
            
            await self.archive.store(
                f"conversations/{conv['id']}.json",
                json.dumps([dict(m) for m in messages])
            )
            
            # Delete from main DB
            await self.db.execute(
                "DELETE FROM messages WHERE conversation_id = $1",
                conv["id"]
            )
            
            await self.db.execute(
                "DELETE FROM conversations WHERE id = $1",
                conv["id"]
            )
```

---

## Connection Pooling

```python
from asyncpg import create_pool

class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None
    
    async def connect(self):
        self.pool = await create_pool(
            self.dsn,
            min_size=10,
            max_size=20,
            command_timeout=60,
            server_settings={
                'jit': 'off'
            }
        )
    
    async def fetch(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def execute(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
```

---

## The Database Checklist

- [ ] Schema designed for queries
- [ ] Indexes on common lookups
- [ ] Foreign key constraints
- [ ] Connection pooling
- [ ] Query timeout
- [ ] Data retention policy
- [ ] Backup strategy
- [ ] Monitoring slow queries
- [ ] Migration plan
- [ ] Read replicas (if needed)

---

## Conclusion

Database design:
- Affects performance
- Determines scalability
- Enables analytics
- Requires planning

Design for queries.
Index for performance.
Archive for cost.

---

*ArQon Agentics designs agent databases for scale. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
