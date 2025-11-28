"""
Metrics Collector for Personalized Learning Path Generator.

Collects and tracks metrics for:
- Learning path generation performance
- Agent usage statistics
- Student engagement metrics
- Quality scores
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class MetricPoint:
    """A single metric data point."""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Collects and aggregates metrics for the learning path generator.
    
    Tracks:
    - Request latency
    - Agent invocation counts
    - Tool usage statistics
    - Learning path quality scores
    - Error rates
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self._metrics: List[MetricPoint] = []
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._timers: Dict[str, float] = {}
        
    # ========================================================================
    # COUNTER METRICS
    # ========================================================================
    
    def increment_counter(self, name: str, value: int = 1, labels: Dict[str, str] = None):
        """
        Increment a counter metric.
        
        Args:
            name: Metric name
            value: Amount to increment by
            labels: Optional labels for the metric
        """
        key = self._make_key(name, labels)
        self._counters[key] += value
        self._record_metric(name, self._counters[key], labels)
        
    def get_counter(self, name: str, labels: Dict[str, str] = None) -> int:
        """Get current counter value."""
        key = self._make_key(name, labels)
        return self._counters.get(key, 0)
    
    # ========================================================================
    # GAUGE METRICS
    # ========================================================================
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """
        Set a gauge metric value.
        
        Args:
            name: Metric name
            value: Current value
            labels: Optional labels
        """
        key = self._make_key(name, labels)
        self._gauges[key] = value
        self._record_metric(name, value, labels)
        
    def get_gauge(self, name: str, labels: Dict[str, str] = None) -> Optional[float]:
        """Get current gauge value."""
        key = self._make_key(name, labels)
        return self._gauges.get(key)
    
    # ========================================================================
    # HISTOGRAM METRICS
    # ========================================================================
    
    def record_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """
        Record a value in a histogram.
        
        Args:
            name: Metric name
            value: Value to record
            labels: Optional labels
        """
        key = self._make_key(name, labels)
        self._histograms[key].append(value)
        self._record_metric(name, value, labels)
        
    def get_histogram_stats(self, name: str, labels: Dict[str, str] = None) -> Dict[str, float]:
        """Get histogram statistics."""
        key = self._make_key(name, labels)
        values = self._histograms.get(key, [])
        
        if not values:
            return {"count": 0, "min": 0, "max": 0, "avg": 0, "sum": 0}
            
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sum": sum(values),
        }
    
    # ========================================================================
    # TIMER METRICS
    # ========================================================================
    
    def start_timer(self, name: str):
        """Start a timer."""
        self._timers[name] = time.time()
        
    def stop_timer(self, name: str, labels: Dict[str, str] = None) -> float:
        """
        Stop a timer and record the duration.
        
        Returns:
            Duration in seconds
        """
        if name not in self._timers:
            return 0.0
            
        duration = time.time() - self._timers[name]
        self.record_histogram(f"{name}_duration_seconds", duration, labels)
        del self._timers[name]
        return duration
    
    # ========================================================================
    # LEARNING PATH SPECIFIC METRICS
    # ========================================================================
    
    def record_learning_path_generated(self, topic: str, complexity: str, duration_seconds: float):
        """Record a successful learning path generation."""
        self.increment_counter("learning_paths_generated", labels={"topic": topic, "complexity": complexity})
        self.record_histogram("learning_path_generation_time", duration_seconds, labels={"complexity": complexity})
        
    def record_agent_invocation(self, agent_name: str, success: bool):
        """Record an agent invocation."""
        status = "success" if success else "failure"
        self.increment_counter("agent_invocations", labels={"agent": agent_name, "status": status})
        
    def record_tool_usage(self, tool_name: str, duration_seconds: float):
        """Record tool usage."""
        self.increment_counter("tool_calls", labels={"tool": tool_name})
        self.record_histogram("tool_duration_seconds", duration_seconds, labels={"tool": tool_name})
        
    def record_quality_score(self, score: float, category: str):
        """Record a content quality score."""
        self.record_histogram("quality_scores", score, labels={"category": category})
        
    def record_student_engagement(self, session_id: str, engagement_score: float):
        """Record student engagement metric."""
        self.set_gauge("student_engagement", engagement_score, labels={"session": session_id})
        
    def record_approval_decision(self, approved: bool, wait_time_seconds: float):
        """Record teacher approval workflow metrics."""
        status = "approved" if approved else "rejected"
        self.increment_counter("approval_decisions", labels={"status": status})
        self.record_histogram("approval_wait_time", wait_time_seconds)
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all collected metrics.
        
        Returns:
            Dictionary containing all metric summaries
        """
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {
                key: self.get_histogram_stats(key.split(":", 1)[0])
                for key in self._histograms.keys()
            },
            "total_metric_points": len(self._metrics),
            "collection_period": {
                "start": self._metrics[0].timestamp.isoformat() if self._metrics else None,
                "end": self._metrics[-1].timestamp.isoformat() if self._metrics else None,
            },
        }
        
    def get_metrics_for_export(self) -> List[Dict[str, Any]]:
        """
        Get all metrics in export format.
        
        Returns:
            List of metric dictionaries ready for export
        """
        return [
            {
                "name": m.name,
                "value": m.value,
                "timestamp": m.timestamp.isoformat(),
                "labels": m.labels,
            }
            for m in self._metrics
        ]
        
    def reset(self):
        """Reset all collected metrics."""
        self._metrics.clear()
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._timers.clear()
    
    # ========================================================================
    # INTERNAL HELPERS
    # ========================================================================
    
    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """Create a unique key for a metric with labels."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}:{label_str}"
        
    def _record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a metric point."""
        self._metrics.append(MetricPoint(
            name=name,
            value=value,
            labels=labels or {},
        ))


# ============================================================================
# GLOBAL METRICS INSTANCE
# ============================================================================

# Global metrics collector for the application
metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return metrics

