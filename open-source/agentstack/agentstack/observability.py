"""
AgentStack Observability Module

Production-grade observability for agentic systems.
Provides tracing, metrics, logging, and evaluation tools.
"""

import time
import json
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class TraceStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentSpan:
    """A single operation within an agent trace."""
    span_id: str
    trace_id: str
    parent_id: Optional[str]
    name: str
    start_time: float
    end_time: Optional[float] = None
    status: TraceStatus = TraceStatus.RUNNING
    inputs: Dict[str, Any] = None
    outputs: Dict[str, Any] = None
    metrics: Dict[str, float] = None
    tags: List[str] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.inputs is None:
            self.inputs = {}
        if self.outputs is None:
            self.outputs = {}
        if self.metrics is None:
            self.metrics = {}
        if self.tags is None:
            self.tags = []
    
    def finish(self, outputs: Dict[str, Any] = None, error: str = None):
        """Mark the span as completed."""
        self.end_time = time.time()
        if outputs:
            self.outputs = outputs
        if error:
            self.error = error
            self.status = TraceStatus.FAILED
        else:
            self.status = TraceStatus.COMPLETED
    
    @property
    def duration_ms(self) -> float:
        """Get span duration in milliseconds."""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return (time.time() - self.start_time) * 1000
    
    def to_dict(self) -> Dict:
        """Convert span to dictionary."""
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "metrics": self.metrics,
            "tags": self.tags,
            "error": self.error
        }


class AgentTracer:
    """Traces agent execution with spans and context propagation."""
    
    def __init__(self, service_name: str = "agentstack"):
        self.service_name = service_name
        self._traces: Dict[str, List[AgentSpan]] = {}
        self._active_spans: Dict[str, AgentSpan] = {}
    
    def start_trace(self, trace_id: Optional[str] = None) -> str:
        """Start a new trace. Returns trace_id."""
        if trace_id is None:
            trace_id = str(uuid.uuid4())
        self._traces[trace_id] = []
        return trace_id
    
    def start_span(
        self,
        name: str,
        trace_id: str,
        parent_id: Optional[str] = None,
        inputs: Dict[str, Any] = None,
        tags: List[str] = None
    ) -> AgentSpan:
        """Start a new span within a trace."""
        span_id = str(uuid.uuid4())
        
        span = AgentSpan(
            span_id=span_id,
            trace_id=trace_id,
            parent_id=parent_id,
            name=name,
            start_time=time.time(),
            inputs=inputs or {},
            tags=tags or []
        )
        
        self._traces[trace_id].append(span)
        self._active_spans[span_id] = span
        
        return span
    
    def finish_span(
        self,
        span_id: str,
        outputs: Dict[str, Any] = None,
        error: str = None
    ):
        """Finish an active span."""
        if span_id in self._active_spans:
            span = self._active_spans[span_id]
            span.finish(outputs=outputs, error=error)
            del self._active_spans[span_id]
    
    def get_trace(self, trace_id: str) -> List[Dict]:
        """Get all spans for a trace."""
        if trace_id in self._traces:
            return [span.to_dict() for span in self._traces[trace_id]]
        return []
    
    def get_trace_summary(self, trace_id: str) -> Dict:
        """Get summary statistics for a trace."""
        spans = self._traces.get(trace_id, [])
        if not spans:
            return {}
        
        total_duration = sum(s.duration_ms for s in spans if s.end_time)
        errors = [s for s in spans if s.error]
        
        return {
            "trace_id": trace_id,
            "num_spans": len(spans),
            "total_duration_ms": total_duration,
            "num_errors": len(errors),
            "span_names": [s.name for s in spans],
            "status": "failed" if errors else "completed"
        }
    
    def export_trace(self, trace_id: str) -> str:
        """Export trace as JSON string."""
        trace_data = {
            "service": self.service_name,
            "trace_id": trace_id,
            "exported_at": datetime.now().isoformat(),
            "spans": self.get_trace(trace_id)
        }
        return json.dumps(trace_data, indent=2)


class AgentMetrics:
    """Collects and reports metrics for agent systems."""
    
    def __init__(self):
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = {}
        self._start_time = time.time()
    
    def increment(self, metric_name: str, value: int = 1):
        """Increment a counter metric."""
        self._counters[metric_name] = self._counters.get(metric_name, 0) + value
    
    def gauge(self, metric_name: str, value: float):
        """Set a gauge metric."""
        self._gauges[metric_name] = value
    
    def histogram(self, metric_name: str, value: float):
        """Record a value in a histogram."""
        if metric_name not in self._histograms:
            self._histograms[metric_name] = []
        self._histograms[metric_name].append(value)
    
    def get_stats(self, metric_name: str) -> Dict:
        """Get statistics for a histogram metric."""
        values = self._histograms.get(metric_name, [])
        if not values:
            return {}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        return {
            "count": n,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "mean": sum(values) / n,
            "p50": sorted_values[n // 2],
            "p95": sorted_values[int(n * 0.95)],
            "p99": sorted_values[int(n * 0.99)]
        }
    
    def report(self) -> Dict:
        """Generate full metrics report."""
        report = {
            "counters": self._counters,
            "gauges": self._gauges,
            "histograms": {},
            "uptime_seconds": time.time() - self._start_time
        }
        
        for name in self._histograms:
            report["histograms"][name] = self.get_stats(name)
        
        return report


class AgentEvaluator:
    """Evaluates agent output quality."""
    
    def __init__(self):
        self._test_cases: List[Dict] = []
    
    def add_test_case(self, input_data: Dict, expected_output: Dict, name: str = None):
        """Add a test case for evaluation."""
        self._test_cases.append({
            "name": name or f"test_{len(self._test_cases)}",
            "input": input_data,
            "expected": expected_output
        })
    
    def evaluate(self, agent_fn, test_cases: List[Dict] = None) -> Dict:
        """Evaluate an agent function against test cases."""
        cases = test_cases or self._test_cases
        results = []
        
        for case in cases:
            start = time.time()
            try:
                output = agent_fn(case["input"])
                latency = (time.time() - start) * 1000
                
                # Simple exact match for now
                # In production, use semantic similarity
                correct = output == case["expected"]
                
                results.append({
                    "name": case["name"],
                    "correct": correct,
                    "latency_ms": latency,
                    "input": case["input"],
                    "expected": case["expected"],
                    "actual": output
                })
            except Exception as e:
                results.append({
                    "name": case["name"],
                    "correct": False,
                    "error": str(e),
                    "input": case["input"]
                })
        
        correct_count = sum(1 for r in results if r.get("correct"))
        total = len(results)
        
        return {
            "accuracy": correct_count / total if total > 0 else 0,
            "total_cases": total,
            "passed": correct_count,
            "failed": total - correct_count,
            "avg_latency_ms": sum(r.get("latency_ms", 0) for r in results) / total if total > 0 else 0,
            "details": results
        }


# Convenience decorators
def trace_operation(tracer: AgentTracer, operation_name: str):
    """Decorator to trace a function execution."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get trace_id from kwargs or create new
            trace_id = kwargs.pop('trace_id', None) or tracer.start_trace()
            
            span = tracer.start_span(
                name=operation_name,
                trace_id=trace_id,
                inputs={"args": str(args), "kwargs": str(kwargs)}
            )
            
            try:
                result = func(*args, **kwargs)
                tracer.finish_span(span.span_id, outputs={"result": str(result)})
                return result
            except Exception as e:
                tracer.finish_span(span.span_id, error=str(e))
                raise
        
        return wrapper
    return decorator


def measure_metrics(metrics: AgentMetrics, metric_name: str):
    """Decorator to measure function execution metrics."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            metrics.increment(f"{metric_name}_calls")
            
            try:
                result = func(*args, **kwargs)
                metrics.increment(f"{metric_name}_success")
                return result
            except Exception:
                metrics.increment(f"{metric_name}_errors")
                raise
            finally:
                duration = (time.time() - start) * 1000
                metrics.histogram(f"{metric_name}_duration_ms", duration)
        
        return wrapper
    return decorator
