# Blog Post: The Agent Engineer's Guide to Database Migrations
## Published: March 4, 2027
## Category: Engineering

---

# The Agent Engineer's Guide to Database Migrations

*Migrate safely. No data loss.*

---

## Why Database Migrations?

### Benefits

- Version control for schema
- Reproducible
- Reviewable
- Safe

---

## Implementation

### 1. Alembic (SQLAlchemy)

```python
# alembic/env.py
from alembic import context
from sqlalchemy import create_engine

config = context.config
engine = create_engine(config.get_main_option("sqlalchemy.url"))

# Generate migration
# alembic revision --autogenerate -m "add agent status"

# Generated migration
"""
revision = 'abc123'
down_revision = 'xyz789'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('agents', sa.Column('status', sa.String(), nullable=True))
    op.create_index('ix_agents_status', 'agents', ['status'])

def downgrade():
    op.drop_index('ix_agents_status', table_name='agents')
    op.drop_column('agents', 'status')
"""
```

### 2. Online Migrations

```python
class OnlineMigration:
    def __init__(self, db):
        self.db = db
    
    async def add_column_online(self, table: str, column: str, col_type):
        # Step 1: Add nullable column
        await self.db.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {col_type} NULL"
        )
        
        # Step 2: Backfill in batches
        batch_size = 1000
        offset = 0
        
        while True:
            rows = await self.db.fetch(
                f"SELECT id FROM {table} ORDER BY id LIMIT {batch_size} OFFSET {offset}"
            )
            
            if not rows:
                break
            
            for row in rows:
                await self.db.execute(
                    f"UPDATE {table} SET {column} = %s WHERE id = %s",
                    self.default_value(), row["id"]
                )
            
            offset += batch_size
            await asyncio.sleep(0.1)  # Throttle
        
        # Step 3: Make NOT NULL
        await self.db.execute(
            f"ALTER TABLE {table} ALTER COLUMN {column} SET NOT NULL"
        )
```

---

## The Database Migration Checklist

- [ ] Backward compatibility
- [ ] Forward compatibility
- [ ] Rollback plan
- [ ] Data backup
- [ ] Test on staging
- [ ] Monitor during deploy
- [ ] Performance impact
- [ ] Lock duration
- [ ] Documentation
- [ ] Team review

---

## Conclusion

Database migrations:
- Version schema
- Require safety
- Need planning
- Demand testing

Migrate safely.
No data loss.
No downtime.

---

*ArQon Agentics migrates carefully. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
