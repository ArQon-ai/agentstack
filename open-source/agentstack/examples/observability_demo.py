"""
AgentStack Observability Quickstart

Shows how to use the tracing, metrics, and evaluation tools.
"""

from agentstack.observability import AgentTracer, AgentMetrics, AgentEvaluator, trace_operation, measure_metrics


# Initialize observability tools
tracer = AgentTracer(service_name="my-agent")
metrics = AgentMetrics()


def example_basic_tracing():
    """Example 1: Basic tracing of agent operations."""
    print("=== Example 1: Basic Tracing ===\n")
    
    # Start a new trace
    trace_id = tracer.start_trace()
    print(f"Started trace: {trace_id}")
    
    # Trace the context assembly phase
    span1 = tracer.start_span(
        name="context_assembly",
        trace_id=trace_id,
        inputs={"query": "What's the weather?", "user_id": "user_123"}
    )
    
    # Simulate work
    import time
    time.sleep(0.1)
    
    # Finish the span
    tracer.finish_span(
        span1.span_id,
        outputs={"context_size": 1500, "sources": ["weather_api", "location_db"]}
    )
    
    # Trace the reasoning phase
    span2 = tracer.start_span(
        name="llm_reasoning",
        trace_id=trace_id,
        parent_id=span1.span_id,
        inputs={"model": "gpt-4", "temperature": 0.7}
    )
    
    time.sleep(0.2)
    
    tracer.finish_span(
        span2.span_id,
        outputs={"tokens_used": 450, "confidence": 0.92}
    )
    
    # Get trace summary
    summary = tracer.get_trace_summary(trace_id)
    print(f"Trace Summary: {summary}\n")
    
    # Export full trace
    trace_json = tracer.export_trace(trace_id)
    print(f"Trace JSON (first 500 chars): {trace_json[:500]}...\n")


def example_metrics_collection():
    """Example 2: Collecting and reporting metrics."""
    print("=== Example 2: Metrics Collection ===\n")
    
    # Simulate agent operations
    for i in range(100):
        # Record request
        metrics.increment("agent_requests")
        
        # Record token usage
        metrics.histogram("tokens_per_request", 200 + i * 3)
        
        # Record latency
        metrics.histogram("request_latency_ms", 150 + i * 2)
        
        # Record cost
        metrics.histogram("cost_per_request", 0.01 + i * 0.001)
    
    # Get stats for latency
    latency_stats = metrics.get_stats("request_latency_ms")
    print(f"Latency Stats: {latency_stats}\n")
    
    # Get full report
    report = metrics.report()
    print(f"Total Requests: {report['counters']['agent_requests']}")
    print(f"Uptime: {report['uptime_seconds']:.2f} seconds\n")


def example_evaluation():
    """Example 3: Evaluating agent quality."""
    print("=== Example 3: Agent Evaluation ===\n")
    
    evaluator = AgentEvaluator()
    
    # Add test cases
    evaluator.add_test_case(
        input_data={"query": "What is 2+2?"},
        expected_output={"answer": "4", "confidence": "high"},
        name="math_basic"
    )
    
    evaluator.add_test_case(
        input_data={"query": "What is the capital of France?"},
        expected_output={"answer": "Paris", "confidence": "high"},
        name="geography"
    )
    
    evaluator.add_test_case(
        input_data={"query": "Invalid query"},
        expected_output={"answer": "I don't understand", "confidence": "low"},
        name="edge_case"
    )
    
    # Define a simple agent function
    def mock_agent(input_data):
        query = input_data["query"]
        if "2+2" in query:
            return {"answer": "4", "confidence": "high"}
        elif "France" in query:
            return {"answer": "Paris", "confidence": "high"}
        else:
            return {"answer": "I don't understand", "confidence": "low"}
    
    # Evaluate
    results = evaluator.evaluate(mock_agent)
    print(f"Accuracy: {results['accuracy']:.2%}")
    print(f"Passed: {results['passed']}/{results['total_cases']}")
    print(f"Avg Latency: {results['avg_latency_ms']:.2f}ms\n")
    
    # Print details
    for detail in results["details"]:
        status = "✅" if detail["correct"] else "❌"
        print(f"{status} {detail['name']}: {detail.get('latency_ms', 0):.2f}ms")


@trace_operation(tracer, "process_user_query")
def traced_process_query(query: str) -> str:
    """Example of using the trace decorator."""
    import time
    time.sleep(0.1)
    return f"Processed: {query}"


@measure_metrics(metrics, "query_processor")
def measured_process_query(query: str) -> str:
    """Example of using the metrics decorator."""
    import time
    time.sleep(0.05)
    return f"Processed: {query}"


def example_decorators():
    """Example 4: Using decorators for tracing and metrics."""
    print("=== Example 4: Decorators ===\n")
    
    # Use traced function
    trace_id = tracer.start_trace()
    result = traced_process_query("Hello, agent!")
    print(f"Traced result: {result}")
    
    # Use measured function
    result = measured_process_query("Hello, metrics!")
    print(f"Measured result: {result}\n")


if __name__ == "__main__":
    print("AgentStack Observability Quickstart\n")
    print("=" * 50 + "\n")
    
    example_basic_tracing()
    example_metrics_collection()
    example_evaluation()
    example_decorators()
    
    print("=" * 50)
    print("\n✅ Observability examples complete!")
    print("\nNext steps:")
    print("1. Integrate tracing into your agent workflows")
    print("2. Set up metrics dashboards (Prometheus/Grafana)")
    print("3. Build evaluation suites for your use cases")
    print("4. Export traces to your observability platform")
