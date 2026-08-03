# Blog Post: The Agent Engineer's Guide to Error Budgets
## Published: October 11, 2026
## Category: Engineering

---

# The Agent Engineer's Guide to Error Budgets

*Error budgets align engineering and business. Here's how to implement them.*

---

## What is an Error Budget?

### Definition

An error budget is the acceptable amount of unreliability in a service.

**Formula:**
```
Error Budget = 1 - SLO

Example:
SLO = 99.9% uptime
Error Budget = 0.1% = 43.8 minutes/month
```

### Why It Matters

- Aligns teams on reliability
- Enables risk-taking
- Prevents perfectionism
- Drives prioritization

---

## Defining SLOs for Agents

### Service Level Objectives

```python
class AgentSLOs:
    def __init__(self):
        self.objectives = {
            "availability": {
                "target": 0.999,  # 99.9%
                "measurement": "uptime",
                "window": "30d"
            },
            "latency": {
                "target": 0.95,   # 95% under threshold
                "threshold": 3.0,  # 3 seconds
                "measurement": "p95",
                "window": "7d"
            },
            "accuracy": {
                "target": 0.85,   # 85% correct
                "measurement": "human_eval",
                "window": "7d"
            },
            "cost": {
                "target": 0.90,   # 90% under budget
                "threshold": 1000,  # $1000/month
                "measurement": "monthly_spend",
                "window": "30d"
            }
        }
```

### Measuring SLOs

```python
class SLOMonitor:
    def __init__(self, slos):
        self.slos = slos
        self.measurements = defaultdict(list)
    
    def record(self, metric, value):
        self.measurements[metric].append({
            "value": value,
            "timestamp": datetime.now()
        })
    
    def check_slo(self, metric):
        slo = self.slos[metric]
        measurements = self.measurements[metric]
        
        if slo["measurement"] == "uptime":
            uptime = self.calculate_uptime(measurements)
            return uptime >= slo["target"]
        
        elif slo["measurement"] == "p95":
            p95 = np.percentile([m["value"] for m in measurements], 95)
            return p95 <= slo["threshold"]
        
        elif slo["measurement"] == "human_eval":
            accuracy = np.mean([m["value"] for m in measurements])
            return accuracy >= slo["target"]
```

---

## Error Budget Policy

### The Policy

```python
class ErrorBudgetPolicy:
    def __init__(self, slo):
        self.slo = slo
        self.budget = 1 - slo.target
        self.consumed = 0
    
    def consume(self, error_rate):
        self.consumed += error_rate
        
        if self.consumed > self.budget:
            return self.get_action()
        
        return {"action": "continue", "remaining": self.budget - self.consumed}
    
    def get_action(self):
        consumption_rate = self.consumed / self.budget
        
        if consumption_rate > 2.0:
            return {
                "action": "freeze",
                "message": "Error budget exhausted. Freeze releases."
            }
        elif consumption_rate > 1.0:
            return {
                "action": "slow_down",
                "message": "Error budget exceeded. Slow down releases."
            }
        elif consumption_rate > 0.5:
            return {
                "action": "caution",
                "message": "50% budget consumed. Proceed with caution."
            }
        
        return {"action": "continue", "remaining": self.budget - self.consumed}
```

### Actions

```python
class ErrorBudgetActions:
    def freeze_releases(self):
        """Stop all non-critical releases"""
        self.deployment_queue.pause()
        self.alert_team("Release freeze: Error budget exhausted")
    
    def slow_down(self):
        """Reduce release velocity"""
        self.deployment_queue.throttle(rate=0.5)
        self.require_additional_review()
    
    def increase_testing(self):
        """Require more testing"""
        self.coverage_threshold = 0.95
        self.require_load_test = True
    
    def prioritize_reliability(self):
        """Focus on reliability work"""
        self.backlog.prioritize("reliability")
        self.allocate_engineers("reliability", count=2)
```

---

## Implementation

### Tracking Error Budget

```python
class ErrorBudgetTracker:
    def __init__(self):
        self.windows = {
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90)
        }
    
    def calculate_consumption(self, metric, window="30d"):
        end = datetime.now()
        start = end - self.windows[window]
        
        errors = self.get_errors(metric, start, end)
        total = self.get_total(metric, start, end)
        
        if total == 0:
            return 0
        
        return errors / total
    
    def get_status(self, metric, window="30d"):
        consumption = self.calculate_consumption(metric, window)
        budget = 1 - self.slos[metric].target
        
        percentage = consumption / budget
        
        if percentage > 1.0:
            return "exhausted", percentage
        elif percentage > 0.75:
            return "critical", percentage
        elif percentage > 0.5:
            return "warning", percentage
        else:
            return "healthy", percentage
```

### Dashboard

```python
class ErrorBudgetDashboard:
    def generate(self):
        metrics = ["availability", "latency", "accuracy", "cost"]
        
        dashboard = {}
        for metric in metrics:
            status, percentage = self.tracker.get_status(metric)
            
            dashboard[metric] = {
                "status": status,
                "consumed": f"{percentage*100:.1f}%",
                "budget": f"{(1-self.slos[metric].target)*100:.1f}%",
                "action": self.get_recommended_action(status)
            }
        
        return dashboard
```

---

## Communication

### Weekly Report

```
Error Budget Report — Week of Oct 1-7

Availability:
  Status: ⚠️ Warning (65% consumed)
  Budget: 0.1% (43.8 min/month)
  Consumed: 28.5 minutes
  Action: Proceed with caution

Latency:
  Status: ✅ Healthy (23% consumed)
  Budget: 5% over 3s
  Consumed: 1.15%
  Action: None

Accuracy:
  Status: ✅ Healthy (12% consumed)
  Budget: 15% error rate
  Consumed: 1.8%
  Action: None
```

### Incident Response

```python
class IncidentResponse:
    def handle_incident(self, incident):
        # Calculate impact
        error_duration = incident.duration
        total_window = 30 * 24 * 60  # 30 days in minutes
        
        impact = error_duration / total_window
        
        # Consume budget
        result = self.budget.consume(impact)
        
        if result["action"] != "continue":
            self.execute_action(result["action"])
        
        # Post-incident review
        self.schedule_post_mortem(incident)
```

---

## The Error Budget Checklist

- [ ] Define SLOs
- [ ] Calculate budgets
- [ ] Set up monitoring
- [ ] Create dashboard
- [ ] Define actions
- [ ] Communicate policy
- [ ] Track consumption
- [ ] Alert on thresholds
- [ ] Review weekly
- [ ] Adjust quarterly

---

## Conclusion

Error budgets:
- Align teams
- Enable velocity
- Prevent burnout
- Drive decisions

Define them.
Measure them.
Respect them.

---

*ArQon Agentics builds reliable agent systems with error budgets. Get the framework at [github.com/ArQon-ai/agentstack](https://github.com/ArQon-ai/agentstack).*
