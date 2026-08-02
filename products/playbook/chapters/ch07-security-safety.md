# Playbook Chapter 7: Security and Safety for Agentic Systems

**The Agentic Engineer's Playbook**
*By ArQon Agentics*

---

## Overview

Agents have unique security challenges. They execute code, access APIs, and make autonomous decisions. This chapter covers how to secure them.

---

## The Agent Security Model

Traditional security: **Defend the perimeter**
Agent security: **Defend every decision**

Agents need:
- Input validation
- Output filtering
- Tool access controls
- Cost limits
- Audit logging
- Human oversight

---

## Threat Model

### High Risk
1. **Prompt Injection** — User manipulates agent behavior
2. **Data Exfiltration** — Agent leaks sensitive data
3. **Unauthorized Tool Access** — Agent uses tools it shouldn't
4. **Runaway Costs** — Infinite loops burning tokens
5. **Supply Chain** — Compromised dependencies

### Medium Risk
6. **Hallucination** — Agent generates false information
7. **Bias Amplification** — Agent reinforces harmful biases
8. **Privacy Violations** — Agent mishandles PII

### Low Risk
9. **Performance Degradation** — Slow responses
10. **Availability Issues** — Service outages

---

## Defense in Depth

### Layer 1: Input Validation

```python
from pydantic import BaseModel, validator
import re

class ValidatedInput(BaseModel):
    query: str
    user_id: str
    session_id: str
    
    @validator('query')
    def check_length(cls, v):
        if len(v) > 10000:
            raise ValueError("Query too long")
        return v
    
    @validator('query')
    def check_injection(cls, v):
        dangerous = [
            r'ignore previous',
            r'system prompt',
            r'you are now',
            r'new instructions',
        ]
        for pattern in dangerous:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Potential injection attempt")
        return v
```

### Layer 2: Output Filtering

```python
class OutputFilter:
    def __init__(self):
        self.blocked_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card
            r'sk-[a-zA-Z0-9]{48}',  # API keys
        ]
    
    def filter(self, output):
        filtered = output
        detections = []
        
        for pattern in self.blocked_patterns:
            matches = re.finditer(pattern, output)
            for match in matches:
                detections.append({
                    "type": "sensitive_data",
                    "matched": match.group()
                })
                filtered = filtered.replace(match.group(), "[REDACTED]")
        
        return {
            "output": filtered,
            "detections": detections,
            "safe": len(detections) == 0
        }
```

### Layer 3: Tool Controls

```python
class ToolController:
    def __init__(self):
        self.permissions = {
            "user": ["read", "search"],
            "admin": ["read", "write", "delete", "admin"]
        }
    
    def can_execute(self, tool, user_role):
        required_perm = tool.required_permission
        return required_perm in self.permissions.get(user_role, [])
    
    def execute(self, tool, params, user_role):
        if not self.can_execute(tool, user_role):
            raise PermissionError(f"Role {user_role} cannot use {tool.name}")
        
        # Log the action
        audit_log.record({
            "tool": tool.name,
            "user": user_role,
            "params": params,
            "timestamp": datetime.now()
        })
        
        return tool.run(params)
```

### Layer 4: Cost Controls

```python
class CostGuard:
    def __init__(self, max_daily_cost=100.0):
        self.max_daily = max_daily_cost
        self.spent_today = 0.0
        self.reset_time = time.time()
    
    def check_budget(self, estimated_cost):
        # Reset daily counter
        if time.time() - self.reset_time > 86400:
            self.spent_today = 0.0
            self.reset_time = time.time()
        
        if self.spent_today + estimated_cost > self.max_daily:
            raise BudgetExceeded(
                f"Daily budget exceeded: ${self.spent_today:.2f}"
            )
        
        return True
    
    def record_cost(self, actual_cost):
        self.spent_today += actual_cost
```

---

## Human-in-the-Loop

For high-stakes actions, require human approval:

```python
class HumanApproval:
    def __init__(self, approval_threshold="high_impact"):
        self.threshold = approval_threshold
    
    def requires_approval(self, action):
        high_impact_tools = ["delete", "modify", "transfer", "grant_access"]
        return action.tool in high_impact_tools
    
    def request_approval(self, action):
        if not self.requires_approval(action):
            return True
        
        # Send to human for approval
        approval_request = {
            "action": action.name,
            "details": action.details,
            "requested_by": action.user_id,
            "timestamp": datetime.now()
        }
        
        # Wait for human response (async)
        return await approval_queue.submit(approval_request)
```

---

## Incident Response

When something goes wrong:

1. **Detect** — Monitoring alerts
2. **Contain** — Stop the agent, revoke access
3. **Investigate** — Review audit logs
4. **Remediate** — Fix the vulnerability
5. **Learn** — Update safeguards

```python
class IncidentResponse:
    def handle_incident(self, incident):
        # 1. Contain
        self.agent_registry.stop(incident.agent_id)
        self.access_control.revoke(incident.user_id)
        
        # 2. Investigate
        logs = self.audit_log.query(
            agent_id=incident.agent_id,
            time_range=incident.time_range
        )
        
        # 3. Alert
        self.alerting.send({
            "severity": incident.severity,
            "details": incident.details,
            "logs": logs
        })
        
        # 4. Document
        self.incident_tracker.create({
            "incident": incident,
            "logs": logs,
            "response": "contained"
        })
```

---

## Security Checklist

Before deploying:

- [ ] Input validation on all entry points
- [ ] Output filtering for sensitive data
- [ ] Tool access controls by role
- [ ] Rate limiting per user
- [ ] Cost budgets enforced
- [ ] Audit logging enabled
- [ ] Circuit breakers on external APIs
- [ ] Timeouts on all operations
- [ ] Human approval for destructive actions
- [ ] Incident response plan documented
- [ ] Regular security audits scheduled
- [ ] Penetration testing completed

---

*This is Chapter 7 of The Agentic Engineer's Playbook. Get the full book at [arqonagentics.com](https://arqonagentics.com).*
