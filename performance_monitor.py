#!/usr/bin/env python3
"""
Performance monitoring and optimization module
Real-time performance tracking for high-concurrency operations
"""

import asyncio
import logging
import psutil
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    memory_usage: float  # MB
    cpu_usage: float     # Percentage
    active_connections: int
    response_time: float  # Seconds
    error_rate: float    # Percentage
    throughput: float    # Requests per second

@dataclass
class SystemHealth:
    """System health status"""
    status: str  # "healthy", "warning", "critical"
    metrics: PerformanceMetrics
    alerts: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

class PerformanceMonitor:
    """Real-time performance monitoring and optimization"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.request_times: deque = deque(maxlen=1000)
        self.error_counts: defaultdict = defaultdict(int)
        self.total_requests = 0
        self.start_time = time.time()
        self.last_health_check = datetime.now(timezone.utc)
        
        # Thresholds for alerts
        self.memory_threshold = 400  # MB
        self.cpu_threshold = 80      # Percentage
        self.response_time_threshold = 5.0  # Seconds
        self.error_rate_threshold = 10.0    # Percentage
        
        # Connection tracking
        self.active_connections = 0
        self.peak_connections = 0
        
    def record_request_start(self) -> float:
        """Record the start of a request"""
        self.active_connections += 1
        self.peak_connections = max(self.peak_connections, self.active_connections)
        return time.time()
    
    def record_request_end(self, start_time: float, success: bool = True):
        """Record the end of a request"""
        self.active_connections = max(0, self.active_connections - 1)
        self.total_requests += 1
        
        response_time = time.time() - start_time
        self.request_times.append(response_time)
        
        if not success:
            self.error_counts['total'] += 1
    
    def record_error(self, error_type: str):
        """Record an error"""
        self.error_counts[error_type] += 1
        self.error_counts['total'] += 1
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        # Memory usage
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        
        # CPU usage
        cpu_usage = process.cpu_percent()
        
        # Response time (average of last 100 requests)
        if self.request_times:
            response_time = sum(list(self.request_times)[-100:]) / min(100, len(self.request_times))
        else:
            response_time = 0.0
        
        # Error rate (last hour)
        error_rate = 0.0
        if self.total_requests > 0:
            error_rate = (self.error_counts['total'] / self.total_requests) * 100
        
        # Throughput (requests per second)
        uptime = time.time() - self.start_time
        throughput = self.total_requests / uptime if uptime > 0 else 0
        
        return PerformanceMetrics(
            timestamp=datetime.now(timezone.utc),
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            active_connections=self.active_connections,
            response_time=response_time,
            error_rate=error_rate,
            throughput=throughput
        )
    
    def update_metrics(self):
        """Update metrics history"""
        metrics = self.get_current_metrics()
        self.metrics_history.append(metrics)
        return metrics
    
    def get_health_status(self) -> SystemHealth:
        """Get current system health status"""
        metrics = self.get_current_metrics()
        alerts = []
        recommendations = []
        status = "healthy"
        
        # Check memory usage
        if metrics.memory_usage > self.memory_threshold:
            alerts.append(f"High memory usage: {metrics.memory_usage:.1f} MB")
            recommendations.append("Consider restarting the bot or optimizing memory usage")
            status = "warning" if status == "healthy" else status
        
        # Check CPU usage
        if metrics.cpu_usage > self.cpu_threshold:
            alerts.append(f"High CPU usage: {metrics.cpu_usage:.1f}%")
            recommendations.append("Reduce concurrent operations or optimize code")
            status = "warning" if status == "healthy" else status
        
        # Check response time
        if metrics.response_time > self.response_time_threshold:
            alerts.append(f"Slow response time: {metrics.response_time:.2f}s")
            recommendations.append("Optimize database queries and reduce processing time")
            status = "critical"
        
        # Check error rate
        if metrics.error_rate > self.error_rate_threshold:
            alerts.append(f"High error rate: {metrics.error_rate:.1f}%")
            recommendations.append("Investigate and fix recurring errors")
            status = "critical"
        
        # Check connection count
        if self.active_connections > 500:  # High connection threshold
            alerts.append(f"High connection count: {self.active_connections}")
            recommendations.append("Implement connection pooling and rate limiting")
            status = "warning" if status == "healthy" else status
        
        return SystemHealth(
            status=status,
            metrics=metrics,
            alerts=alerts,
            recommendations=recommendations
        )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance report"""
        if not self.metrics_history:
            self.update_metrics()
        
        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 data points
        
        # Calculate averages
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        
        # Calculate peaks
        peak_memory = max(m.memory_usage for m in recent_metrics)
        peak_cpu = max(m.cpu_usage for m in recent_metrics)
        peak_response_time = max(m.response_time for m in recent_metrics)
        
        uptime = time.time() - self.start_time
        
        return {
            'uptime_seconds': uptime,
            'total_requests': self.total_requests,
            'active_connections': self.active_connections,
            'peak_connections': self.peak_connections,
            'current_metrics': self.get_current_metrics().__dict__,
            'averages': {
                'memory_usage_mb': avg_memory,
                'cpu_usage_percent': avg_cpu,
                'response_time_seconds': avg_response_time
            },
            'peaks': {
                'memory_usage_mb': peak_memory,
                'cpu_usage_percent': peak_cpu,
                'response_time_seconds': peak_response_time
            },
            'error_counts': dict(self.error_counts),
            'health_status': self.get_health_status().__dict__
        }
    
    def optimize_performance(self) -> List[str]:
        """Get performance optimization suggestions"""
        suggestions = []
        health = self.get_health_status()
        
        if health.metrics.memory_usage > self.memory_threshold * 0.8:
            suggestions.extend([
                "Clear unnecessary data caches",
                "Implement data cleanup routines",
                "Consider using memory profiling tools"
            ])
        
        if health.metrics.response_time > self.response_time_threshold * 0.5:
            suggestions.extend([
                "Optimize database operations",
                "Implement query caching",
                "Use async operations where possible"
            ])
        
        if health.metrics.error_rate > self.error_rate_threshold * 0.5:
            suggestions.extend([
                "Improve error handling",
                "Add more robust retry mechanisms",
                "Implement graceful degradation"
            ])
        
        if self.active_connections > 100:
            suggestions.extend([
                "Implement connection pooling",
                "Add rate limiting",
                "Optimize concurrent request handling"
            ])
        
        return suggestions

class PerformanceDecorator:
    """Decorator for performance monitoring"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            start_time = self.monitor.record_request_start()
            success = True
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                self.monitor.record_error(type(e).__name__)
                raise
            finally:
                self.monitor.record_request_end(start_time, success)
        
        return wrapper

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def monitor_performance(func):
    """Decorator for monitoring function performance"""
    decorator = PerformanceDecorator(performance_monitor)
    return decorator(func)

async def periodic_health_check(interval: int = 60):
    """Periodic health check task"""
    while True:
        try:
            health = performance_monitor.get_health_status()
            
            if health.status == "critical":
                logger.critical(f"System health critical: {health.alerts}")
            elif health.status == "warning":
                logger.warning(f"System health warning: {health.alerts}")
            else:
                logger.info("System health: OK")
            
            # Update metrics
            performance_monitor.update_metrics()
            
        except Exception as e:
            logger.error(f"Error in health check: {str(e)}")
        
        await asyncio.sleep(interval)

async def performance_cleanup_task(interval: int = 3600):
    """Periodic cleanup task to maintain performance"""
    while True:
        try:
            # Reset error counts periodically
            if len(performance_monitor.error_counts) > 100:
                # Keep only recent error types
                total_errors = performance_monitor.error_counts['total']
                performance_monitor.error_counts.clear()
                performance_monitor.error_counts['total'] = total_errors
            
            logger.info("Performance cleanup completed")
            
        except Exception as e:
            logger.error(f"Error in performance cleanup: {str(e)}")
        
        await asyncio.sleep(interval)
