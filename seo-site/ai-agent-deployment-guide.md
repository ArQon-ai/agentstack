# SEO Article: AI Agent Deployment: From Local to Production
**Target Keywords:** agent deployment, deploy AI agent, production deployment  
**Published:** September 19, 2026

---

# AI Agent Deployment: From Local to Production

Deploying agents requires more than just pushing code. Here's the complete guide.

---

## Deployment Checklist

Before deploying:

- [ ] Code tested locally
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Monitoring set up
- [ ] Error tracking configured
- [ ] SSL certificate
- [ ] Domain configured
- [ ] Backup strategy
- [ ] Rollback plan
- [ ] Documentation updated

---

## Local Development

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/agent
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Environment Setup

```bash
# .env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=...
LOG_LEVEL=INFO
```

---

## Staging Environment

### Why Staging Matters

- Test with production-like data
- Verify integrations
- Load testing
- Security validation
- Team review

### Staging Setup

```python
# config.py
import os

ENV = os.getenv("ENV", "development")

if ENV == "production":
    DEBUG = False
    LOG_LEVEL = "WARNING"
    DATABASE_URL = os.getenv("DATABASE_URL")
elif ENV == "staging":
    DEBUG = True
    LOG_LEVEL = "INFO"
    DATABASE_URL = os.getenv("STAGING_DATABASE_URL")
else:
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    DATABASE_URL = "postgresql://localhost/agent_dev"
```

---

## Production Deployment

### Platform Options

| Platform | Best For | Cost | Complexity |
|----------|----------|------|------------|
| Fly.io | Small-medium | $ | Low |
| Railway | Rapid deploy | $ | Low |
| Render | Simple hosting | $ | Low |
| AWS | Enterprise | $$ | High |
| GCP | ML workloads | $$ | High |
| Azure | Microsoft stack | $$ | Medium |

### Fly.io Deployment

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch
fly launch

# Deploy
fly deploy

# Scale
fly scale count 2
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## Database Migration

### Alembic Setup

```bash
pip install alembic
alembic init migrations
```

### Migration Script

```python
# migrations/versions/001_initial.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('conversations')
```

### Running Migrations

```bash
# Staging
alembic upgrade head

# Production (with backup)
fly ssh console
cd /app
pg_dump $DATABASE_URL > backup.sql
alembic upgrade head
```

---

## SSL and Security

### SSL Certificate

```bash
# Fly.io handles this automatically
# For custom domains:
fly certs create your-domain.com
```

### Security Headers

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.fly.dev"]
)
```

---

## Monitoring

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": check_database(),
        "redis": check_redis(),
        "version": "1.0.0"
    }
```

### Metrics

```python
from prometheus_client import Counter, Histogram

requests_total = Counter("agent_requests_total", "Total requests")
request_duration = Histogram("agent_request_duration_seconds", "Request duration")

@app.middleware("http")
async def metrics_middleware(request, call_next):
    requests_total.inc()
    with request_duration.time():
        response = await call_next(request)
    return response
```

---

## Rollback Strategy

### Blue-Green Deployment

```bash
# Deploy to green environment
fly deploy --app agent-green

# Test green
curl https://agent-green.fly.dev/health

# Switch traffic
fly deploy --app agent
```

### Database Rollback

```bash
# Before migration
pg_dump $DATABASE_URL > pre_migration_backup.sql

# If rollback needed
psql $DATABASE_URL < pre_migration_backup.sql
```

---

## The Deployment Checklist

- [ ] Tests passing
- [ ] Migrations tested
- [ ] Environment variables set
- [ ] SSL configured
- [ ] Monitoring active
- [ ] Alerts configured
- [ ] Backup verified
- [ ] Rollback tested
- [ ] Documentation updated
- [ ] Team notified

---

## Conclusion

Production deployment requires:
- Testing
- Staging
- Monitoring
- Rollback plans
- Security

Don't skip steps.
Your users will thank you.

---

*ArQon Agentics helps teams deploy production-grade agents. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
