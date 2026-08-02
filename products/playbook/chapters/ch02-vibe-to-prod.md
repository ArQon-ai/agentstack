# From Vibe Coding to Production: The 48-Hour Playbook

You just vibe-coded an amazing prototype. Cursor composed 10 files in 20 minutes. It works on your machine. You're feeling unstoppable.

Now you need to ship it to production. And that's where things get interesting.

## The Vibe Coding → Production Gap

Vibe coding is incredible for:
- ✅ Rapid prototyping
- ✅ Exploring ideas
- ✅ Learning new technologies
- ✅ Building MVPs

Vibe coding is terrible for:
- ❌ Security hardening
- ❌ Error handling
- ❌ Observability
- ❌ Scalability
- ❌ Maintainability

The gap between "it works" and "it's production-ready" is where most vibe-coded projects die.

## The 48-Hour Production Playbook

Here's how we take a vibe-coded prototype to production in 48 hours.

### Hour 0-4: Audit

**What to do:** Understand what you actually built.

1. **Read every file** — Yes, all of them. You need to understand the codebase.
2. **Map dependencies** — What packages does it use? Are they secure?
3. **Identify secrets** — API keys, database URLs, passwords hardcoded anywhere?
4. **Document the architecture** — Draw a simple diagram. What talks to what?

**Tools:**
- `npm audit` or `pip audit` for dependency checks
- `grep -r "API_KEY\|SECRET\|PASSWORD" .` for secrets
- Excalidraw for architecture diagrams

**Output:** A document listing every file, dependency, secret, and architectural decision.

---

### Hour 4-12: Harden

**What to do:** Fix the things that will break in production.

1. **Input validation** — Every API endpoint, every user input. Sanitize everything.
2. **Error handling** — Wrap every external call in try/catch. Handle timeouts.
3. **Rate limiting** — Prevent abuse. Set sensible limits.
4. **Authentication** — If users are involved, add auth. Don't ship without it.
5. **Database security** — Parameterized queries only. No SQL injection.

**Checklist:**
- [ ] All inputs validated
- [ ] All errors handled gracefully
- [ ] Rate limiting implemented
- [ ] Authentication added (if needed)
- [ ] No hardcoded secrets
- [ ] HTTPS enforced
- [ ] CORS configured correctly

---

### Hour 12-24: Observe

**What to do:** Add observability so you know when things break.

1. **Logging** — Structured logs, not print statements. Include correlation IDs.
2. **Metrics** — Track response times, error rates, throughput.
3. **Health checks** — Simple endpoints that verify the system is alive.
4. **Alerting** — Get notified when error rate exceeds threshold.

**Tools:**
- Prometheus + Grafana for metrics
- Winston/Pino (Node.js) or structlog (Python) for logging
- PagerDuty or Opsgenie for alerting

**Output:** Dashboard showing system health, alert rules configured.

---

### Hour 24-36: Deploy

**What to do:** Get it running in a production environment.

1. **Containerize** — Dockerfile, docker-compose for local testing.
2. **Choose hosting** — Vercel/Netlify for frontend, Railway/Render/Fly.io for backend.
3. **Environment config** — Separate dev/staging/prod configs.
4. **Database** — Managed database (Supabase, PlanetScale, RDS).
5. **CI/CD** — GitHub Actions to deploy on push to main.

**Free tier stack:**
- Frontend: Vercel (free)
- Backend: Railway or Render (free tier)
- Database: Supabase (free tier)
- Storage: Cloudflare R2 (free)
- Monitoring: Datadog free tier or self-hosted

---

### Hour 36-48: Validate

**What to do:** Prove it works in production.

1. **Smoke tests** — Automated tests that verify core functionality.
2. **Load test** — Can it handle 10x your expected traffic?
3. **Chaos test** — Kill a dependency. Does it fail gracefully?
4. **User acceptance** — Have someone else try to break it.

**Tools:**
- k6 for load testing
- Artillery for API load testing
- Postman/Newman for smoke tests

---

## Common Vibe Coding Production Issues

### Issue 1: "It works on my machine"

**Cause:** Hardcoded paths, local-only dependencies, missing environment variables.

**Fix:** Use environment variables for all configuration. Containerize early.

### Issue 2: "The AI wrote insecure code"

**Cause:** AI tools optimize for functionality, not security.

**Fix:** Run security scanners (Snyk, CodeQL, Bandit). Manual review of auth and input handling.

### Issue 3: "I don't understand my own codebase"

**Cause:** AI generated 10K lines you never read.

**Fix:** Spend the first 4 hours reading and documenting. Generate architecture diagrams.

### Issue 4: "No tests"

**Cause:** Vibe coding skips testing.

**Fix:** Add smoke tests at minimum. Use AI to generate tests from your code.

### Issue 5: "Database will explode"

**Cause:** No indexing, no connection pooling, no query optimization.

**Fix:** Add indexes, connection pooling, query timeouts. Use a managed database.

---

## The Mindset Shift

Vibe coding is about speed. Production is about reliability.

The best developers combine both:
- **Day 1-2:** Vibe code the prototype
- **Day 3-4:** Harden and observe
- **Day 5:** Deploy and validate

Then iterate.

## Tools We Use

For the vibe coding phase:
- Cursor or Claude Code
- Bolt for web app prototypes
- GitHub Copilot for quick fixes

For the production phase:
- AgentStack for agent infrastructure
- Docker for containerization
- Vercel/Railway for hosting
- Prometheus/Grafana for monitoring
- Snyk for security scanning

## Case Study: From Vibe to Production

We recently took a vibe-coded customer support dashboard from prototype to production:

**Prototype (Day 1):**
- Built with Cursor in 4 hours
- 15 files, 2,000 lines of code
- Worked locally, looked great

**Production (Days 2-4):**
- Added auth (Clerk)
- Added rate limiting
- Added structured logging
- Containerized with Docker
- Deployed to Railway
- Added monitoring

**Result:** Live in production, handling 500+ requests/day, zero downtime.

**Time from vibe to production:** 48 hours.

---

## Your Turn

You have a vibe-coded prototype. Now what?

1. Set a timer for 48 hours
2. Follow this playbook
3. Ship it

The world doesn't need more prototypes. It needs more shipped products.

---

*This is Chapter 2 of The Agentic Engineer's Playbook. Get the full book at [synapsevibe.com](https://synapsevibe.com).*
