"""
Performance Monitoring and Benchmarking Tools
Real-time performance monitoring, load testing, and benchmark analysis
"""

import os
import sys
import asyncio
import time
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import json
import statistics
import threading
from contextlib import contextmanager
import psutil
import requests
import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sqlalchemy import create_engine, text
    from .optimization import (
        get_cache_manager, get_db_optimizer, get_performance_profiler,
        PerformanceMetrics
    )
    from libs.monitoring import get_metrics_collector
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Optional dependencies missing: {e}")
    plt = None
    sns = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LoadTestResult:
    """Load test result data structure."""
    test_name: str
    duration_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    min_response_time: float
    max_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    throughput_mb_per_sec: float
    cpu_usage_percent: float
    memory_usage_percent: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class BenchmarkResult:
    """Benchmark result for specific operation."""
    operation_name: str
    iterations: int
    total_time: float
    average_time: float
    min_time: float
    max_time: float
    std_deviation: float
    operations_per_second: float
    memory_usage_mb: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class PerformanceMonitor:
    """Real-time performance monitoring."""
    
    def __init__(self, monitoring_interval: float = 1.0):
        self.monitoring_interval = monitoring_interval
        self.is_monitoring = False
        self.monitoring_thread = None
        self.metrics_history = []
        self.alerts = []
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'response_time': 2.0,
            'error_rate': 5.0
        }
    
    def start_monitoring(self):
        """Start real-time performance monitoring."""
        if self.is_monitoring:
            logger.warning("Monitoring already started")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        profiler = get_performance_profiler()
        
        while self.is_monitoring:
            try:
                # Collect system metrics
                metrics = profiler.collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only recent metrics (last hour)
                cutoff_time = datetime.utcnow() - timedelta(hours=1)
                self.metrics_history = [
                    m for m in self.metrics_history 
                    if m.timestamp > cutoff_time
                ]
                
                # Check for alerts
                self._check_alerts(metrics)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(self.monitoring_interval)
    
    def _check_alerts(self, metrics: PerformanceMetrics):
        """Check metrics against alert thresholds."""
        alerts_triggered = []
        
        # CPU usage alert
        if metrics.cpu_usage_percent > self.alert_thresholds['cpu_usage']:
            alerts_triggered.append({
                'type': 'high_cpu_usage',
                'value': metrics.cpu_usage_percent,
                'threshold': self.alert_thresholds['cpu_usage'],
                'message': f"High CPU usage: {metrics.cpu_usage_percent:.1f}%"
            })
        
        # Memory usage alert
        if metrics.memory_usage_percent > self.alert_thresholds['memory_usage']:
            alerts_triggered.append({
                'type': 'high_memory_usage',
                'value': metrics.memory_usage_percent,
                'threshold': self.alert_thresholds['memory_usage'],
                'message': f"High memory usage: {metrics.memory_usage_percent:.1f}%"
            })
        
        # Response time alert
        if metrics.average_response_time > self.alert_thresholds['response_time']:
            alerts_triggered.append({
                'type': 'slow_response_time',
                'value': metrics.average_response_time,
                'threshold': self.alert_thresholds['response_time'],
                'message': f"Slow response time: {metrics.average_response_time:.3f}s"
            })
        
        # Add alerts with timestamp
        for alert in alerts_triggered:
            alert['timestamp'] = metrics.timestamp.isoformat()
            self.alerts.append(alert)
        
        # Keep only recent alerts (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get most recent performance metrics."""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_summary(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """Get performance metrics summary for specified duration."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=duration_minutes)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp > cutoff_time
        ]
        
        if not recent_metrics:
            return {'message': 'No metrics available for specified duration'}
        
        # Calculate averages and statistics
        cpu_values = [m.cpu_usage_percent for m in recent_metrics]
        memory_values = [m.memory_usage_percent for m in recent_metrics]
        response_times = [m.average_response_time for m in recent_metrics]
        
        return {
            'duration_minutes': duration_minutes,
            'metrics_count': len(recent_metrics),
            'cpu_usage': {
                'average': statistics.mean(cpu_values),
                'min': min(cpu_values),
                'max': max(cpu_values),
                'std_dev': statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0
            },
            'memory_usage': {
                'average': statistics.mean(memory_values),
                'min': min(memory_values),
                'max': max(memory_values),
                'std_dev': statistics.stdev(memory_values) if len(memory_values) > 1 else 0
            },
            'response_time': {
                'average': statistics.mean(response_times),
                'min': min(response_times),
                'max': max(response_times),
                'std_dev': statistics.stdev(response_times) if len(response_times) > 1 else 0
            },
            'alerts_count': len([a for a in self.alerts if datetime.fromisoformat(a['timestamp']) > cutoff_time])
        }
    
    def get_recent_alerts(self, duration_hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        cutoff_time = datetime.utcnow() - timedelta(hours=duration_hours)
        return [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]
    
    def set_alert_thresholds(self, thresholds: Dict[str, float]):
        """Update alert thresholds."""
        self.alert_thresholds.update(thresholds)
        logger.info(f"Alert thresholds updated: {self.alert_thresholds}")


class LoadTester:
    """Load testing framework."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Performance-LoadTester/1.0'})
    
    def run_load_test(self, 
                     endpoint: str,
                     concurrent_users: int = 10,
                     duration_seconds: int = 60,
                     ramp_up_seconds: int = 10,
                     method: str = 'GET',
                     payload: Dict[str, Any] = None,
                     headers: Dict[str, str] = None) -> LoadTestResult:
        """Run load test against specified endpoint."""
        
        logger.info(f"Starting load test: {concurrent_users} users, {duration_seconds}s duration")
        
        url = f"{self.base_url}{endpoint}"
        results = []
        start_time = time.time()
        
        # Track system metrics during test
        initial_cpu = psutil.cpu_percent()
        initial_memory = psutil.virtual_memory().percent
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            # Submit all requests
            futures = []
            
            for i in range(concurrent_users):
                # Stagger request starts for ramp-up
                delay = (i / concurrent_users) * ramp_up_seconds
                future = executor.submit(
                    self._run_user_requests,
                    url, duration_seconds, delay, method, payload, headers
                )
                futures.append(future)
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                try:
                    user_results = future.result()
                    results.extend(user_results)
                except Exception as e:
                    logger.error(f"User request failed: {e}")
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        # Calculate final system metrics
        final_cpu = psutil.cpu_percent()
        final_memory = psutil.virtual_memory().percent
        
        # Analyze results
        return self._analyze_load_test_results(
            f"Load test {endpoint}",
            results,
            actual_duration,
            (initial_cpu + final_cpu) / 2,
            (initial_memory + final_memory) / 2
        )
    
    def _run_user_requests(self, 
                          url: str, 
                          duration_seconds: int, 
                          delay: float,
                          method: str,
                          payload: Dict[str, Any],
                          headers: Dict[str, str]) -> List[Dict[str, Any]]:
        """Run requests for a single virtual user."""
        if delay > 0:
            time.sleep(delay)
        
        results = []
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            request_start = time.time()
            
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, headers=headers, timeout=30)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=payload, headers=headers, timeout=30)
                elif method.upper() == 'PUT':
                    response = self.session.put(url, json=payload, headers=headers, timeout=30)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                request_end = time.time()
                response_time = request_end - request_start
                
                results.append({
                    'timestamp': request_start,
                    'response_time': response_time,
                    'status_code': response.status_code,
                    'success': 200 <= response.status_code < 400,
                    'response_size': len(response.content)
                })
                
            except Exception as e:
                request_end = time.time()
                response_time = request_end - request_start
                
                results.append({
                    'timestamp': request_start,
                    'response_time': response_time,
                    'status_code': 0,
                    'success': False,
                    'error': str(e),
                    'response_size': 0
                })
            
            # Small delay between requests to simulate realistic usage
            time.sleep(0.1)
        
        return results
    
    def _analyze_load_test_results(self, 
                                  test_name: str,
                                  results: List[Dict[str, Any]],
                                  duration: float,
                                  avg_cpu: float,
                                  avg_memory: float) -> LoadTestResult:
        """Analyze load test results and generate summary."""
        
        if not results:
            return LoadTestResult(
                test_name=test_name,
                duration_seconds=duration,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                average_response_time=0.0,
                min_response_time=0.0,
                max_response_time=0.0,
                p50_response_time=0.0,
                p95_response_time=0.0,
                p99_response_time=0.0,
                requests_per_second=0.0,
                error_rate=0.0,
                throughput_mb_per_sec=0.0,
                cpu_usage_percent=avg_cpu,
                memory_usage_percent=avg_memory,
                timestamp=datetime.utcnow()
            )
        
        # Calculate statistics
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        response_times = [r['response_time'] for r in results]
        successful_response_times = [r['response_time'] for r in successful_results]
        
        total_data_bytes = sum(r['response_size'] for r in results)
        throughput_mb_per_sec = (total_data_bytes / 1024 / 1024) / duration
        
        # Calculate percentiles
        if successful_response_times:
            p50 = np.percentile(successful_response_times, 50)
            p95 = np.percentile(successful_response_times, 95)
            p99 = np.percentile(successful_response_times, 99)
            avg_response_time = statistics.mean(successful_response_times)
            min_response_time = min(successful_response_times)
            max_response_time = max(successful_response_times)
        else:
            p50 = p95 = p99 = avg_response_time = min_response_time = max_response_time = 0.0
        
        return LoadTestResult(
            test_name=test_name,
            duration_seconds=duration,
            total_requests=len(results),
            successful_requests=len(successful_results),
            failed_requests=len(failed_results),
            average_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p50_response_time=p50,
            p95_response_time=p95,
            p99_response_time=p99,
            requests_per_second=len(results) / duration,
            error_rate=(len(failed_results) / len(results)) * 100,
            throughput_mb_per_sec=throughput_mb_per_sec,
            cpu_usage_percent=avg_cpu,
            memory_usage_percent=avg_memory,
            timestamp=datetime.utcnow()
        )
    
    def run_stress_test(self, 
                       endpoint: str,
                       max_users: int = 100,
                       step_size: int = 10,
                       step_duration: int = 30) -> List[LoadTestResult]:
        """Run stress test with increasing load."""
        
        logger.info(f"Starting stress test: 0 to {max_users} users")
        results = []
        
        for users in range(step_size, max_users + 1, step_size):
            logger.info(f"Testing with {users} concurrent users")
            
            result = self.run_load_test(
                endpoint=endpoint,
                concurrent_users=users,
                duration_seconds=step_duration,
                ramp_up_seconds=5
            )
            
            results.append(result)
            
            # Brief pause between test steps
            time.sleep(5)
        
        return results


class BenchmarkSuite:
    """Performance benchmarking suite."""
    
    def __init__(self):
        self.benchmark_results = []
    
    def benchmark_function(self, 
                          func: Callable,
                          func_name: str = None,
                          iterations: int = 1000,
                          warmup_iterations: int = 100,
                          *args, **kwargs) -> BenchmarkResult:
        """Benchmark a function's performance."""
        
        func_name = func_name or func.__name__
        logger.info(f"Benchmarking {func_name} with {iterations} iterations")
        
        # Warmup
        for _ in range(warmup_iterations):
            try:
                func(*args, **kwargs)
            except Exception:
                pass  # Ignore errors during warmup
        
        # Actual benchmark
        times = []
        start_memory = psutil.Process().memory_info().rss
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                func(*args, **kwargs)
                end_time = time.perf_counter()
                times.append(end_time - start_time)
            except Exception as e:
                logger.warning(f"Benchmark iteration failed: {e}")
                times.append(float('inf'))  # Record failed attempt
        
        end_memory = psutil.Process().memory_info().rss
        memory_usage_mb = (end_memory - start_memory) / 1024 / 1024
        
        # Filter out failed attempts for statistics
        valid_times = [t for t in times if t != float('inf')]
        
        if not valid_times:
            logger.error(f"All benchmark iterations failed for {func_name}")
            return None
        
        # Calculate statistics
        total_time = sum(valid_times)
        average_time = statistics.mean(valid_times)
        min_time = min(valid_times)
        max_time = max(valid_times)
        std_deviation = statistics.stdev(valid_times) if len(valid_times) > 1 else 0.0
        ops_per_second = len(valid_times) / total_time if total_time > 0 else 0
        
        result = BenchmarkResult(
            operation_name=func_name,
            iterations=len(valid_times),
            total_time=total_time,
            average_time=average_time,
            min_time=min_time,
            max_time=max_time,
            std_deviation=std_deviation,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_usage_mb,
            timestamp=datetime.utcnow()
        )
        
        self.benchmark_results.append(result)
        return result
    
    async def benchmark_async_function(self,
                                     func: Callable,
                                     func_name: str = None,
                                     iterations: int = 1000,
                                     warmup_iterations: int = 100,
                                     *args, **kwargs) -> BenchmarkResult:
        """Benchmark an async function's performance."""
        
        func_name = func_name or func.__name__
        logger.info(f"Benchmarking async {func_name} with {iterations} iterations")
        
        # Warmup
        for _ in range(warmup_iterations):
            try:
                await func(*args, **kwargs)
            except Exception:
                pass
        
        # Actual benchmark
        times = []
        start_memory = psutil.Process().memory_info().rss
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                await func(*args, **kwargs)
                end_time = time.perf_counter()
                times.append(end_time - start_time)
            except Exception as e:
                logger.warning(f"Async benchmark iteration failed: {e}")
                times.append(float('inf'))
        
        end_memory = psutil.Process().memory_info().rss
        memory_usage_mb = (end_memory - start_memory) / 1024 / 1024
        
        # Filter out failed attempts
        valid_times = [t for t in times if t != float('inf')]
        
        if not valid_times:
            logger.error(f"All async benchmark iterations failed for {func_name}")
            return None
        
        # Calculate statistics
        total_time = sum(valid_times)
        average_time = statistics.mean(valid_times)
        min_time = min(valid_times)
        max_time = max(valid_times)
        std_deviation = statistics.stdev(valid_times) if len(valid_times) > 1 else 0.0
        ops_per_second = len(valid_times) / total_time if total_time > 0 else 0
        
        result = BenchmarkResult(
            operation_name=f"async_{func_name}",
            iterations=len(valid_times),
            total_time=total_time,
            average_time=average_time,
            min_time=min_time,
            max_time=max_time,
            std_deviation=std_deviation,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_usage_mb,
            timestamp=datetime.utcnow()
        )
        
        self.benchmark_results.append(result)
        return result
    
    def benchmark_database_operations(self, db_optimizer) -> List[BenchmarkResult]:
        """Benchmark common database operations."""
        results = []
        
        # Benchmark simple SELECT
        result = self.benchmark_function(
            lambda: db_optimizer.execute_query("SELECT 1 as test_column"),
            "simple_select",
            iterations=100
        )
        if result:
            results.append(result)
        
        # Benchmark parameterized query
        result = self.benchmark_function(
            lambda: db_optimizer.execute_query(
                "SELECT * FROM information_schema.tables WHERE table_name = :name",
                {"name": "test_table"}
            ),
            "parameterized_query",
            iterations=100
        )
        if result:
            results.append(result)
        
        return results
    
    def benchmark_cache_operations(self, cache_manager) -> List[BenchmarkResult]:
        """Benchmark cache operations."""
        results = []
        
        # Benchmark cache set
        result = self.benchmark_function(
            lambda: cache_manager.set("test_key", {"data": "test_value"}),
            "cache_set",
            iterations=1000
        )
        if result:
            results.append(result)
        
        # Benchmark cache get
        cache_manager.set("benchmark_key", {"data": "benchmark_value"})
        result = self.benchmark_function(
            lambda: cache_manager.get("benchmark_key"),
            "cache_get",
            iterations=1000
        )
        if result:
            results.append(result)
        
        return results
    
    def generate_benchmark_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report."""
        if not self.benchmark_results:
            return {'message': 'No benchmark results available'}
        
        # Sort results by operations per second (descending)
        sorted_results = sorted(
            self.benchmark_results,
            key=lambda x: x.operations_per_second,
            reverse=True
        )
        
        # Calculate summary statistics
        all_ops_per_sec = [r.operations_per_second for r in self.benchmark_results]
        all_avg_times = [r.average_time for r in self.benchmark_results]
        
        return {
            'summary': {
                'total_benchmarks': len(self.benchmark_results),
                'fastest_operation': sorted_results[0].operation_name if sorted_results else None,
                'slowest_operation': sorted_results[-1].operation_name if sorted_results else None,
                'average_ops_per_second': statistics.mean(all_ops_per_sec),
                'average_response_time': statistics.mean(all_avg_times)
            },
            'results': [result.to_dict() for result in sorted_results],
            'timestamp': datetime.utcnow().isoformat()
        }


class PerformanceReporter:
    """Generate performance reports and visualizations."""
    
    def __init__(self):
        self.reports = []
    
    def generate_performance_dashboard(self, 
                                     monitor: PerformanceMonitor,
                                     benchmark_suite: BenchmarkSuite,
                                     load_test_results: List[LoadTestResult] = None) -> Dict[str, Any]:
        """Generate comprehensive performance dashboard."""
        
        dashboard = {
            'timestamp': datetime.utcnow().isoformat(),
            'system_metrics': monitor.get_metrics_summary(60),
            'recent_alerts': monitor.get_recent_alerts(24),
            'benchmark_summary': benchmark_suite.generate_benchmark_report(),
        }
        
        if load_test_results:
            dashboard['load_test_results'] = [result.to_dict() for result in load_test_results]
        
        # Add performance recommendations
        dashboard['recommendations'] = self._generate_recommendations(dashboard)
        
        return dashboard
    
    def _generate_recommendations(self, dashboard: Dict[str, Any]) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        # Check system metrics
        system_metrics = dashboard.get('system_metrics', {})
        cpu_avg = system_metrics.get('cpu_usage', {}).get('average', 0)
        memory_avg = system_metrics.get('memory_usage', {}).get('average', 0)
        response_time_avg = system_metrics.get('response_time', {}).get('average', 0)
        
        if cpu_avg > 70:
            recommendations.append("High CPU usage detected. Consider optimizing CPU-intensive operations or scaling horizontally.")
        
        if memory_avg > 80:
            recommendations.append("High memory usage detected. Consider implementing memory optimization or increasing available memory.")
        
        if response_time_avg > 1.0:
            recommendations.append("Slow response times detected. Consider implementing caching or optimizing database queries.")
        
        # Check alerts
        alerts_count = len(dashboard.get('recent_alerts', []))
        if alerts_count > 10:
            recommendations.append(f"High number of alerts ({alerts_count}) in the last 24 hours. Review system performance.")
        
        # Check benchmark results
        benchmark_data = dashboard.get('benchmark_summary', {})
        if benchmark_data.get('summary', {}).get('average_response_time', 0) > 0.1:
            recommendations.append("Slow benchmark results detected. Consider optimizing critical operations.")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save performance report to file."""
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        filepath = PROJECT_ROOT / "reports" / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Performance report saved to {filepath}")
        return filepath


# Context managers for performance monitoring
@contextmanager
def performance_monitor():
    """Context manager for performance monitoring."""
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    try:
        yield monitor
    finally:
        monitor.stop_monitoring()


@contextmanager
def benchmark_suite():
    """Context manager for benchmark suite."""
    suite = BenchmarkSuite()
    try:
        yield suite
    finally:
        # Cleanup if needed
        pass


# Global instances
_performance_monitor = None
_load_tester = None
_benchmark_suite = None
_performance_reporter = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def get_load_tester() -> LoadTester:
    """Get global load tester instance."""
    global _load_tester
    if _load_tester is None:
        _load_tester = LoadTester()
    return _load_tester


def get_benchmark_suite() -> BenchmarkSuite:
    """Get global benchmark suite instance."""
    global _benchmark_suite
    if _benchmark_suite is None:
        _benchmark_suite = BenchmarkSuite()
    return _benchmark_suite


def get_performance_reporter() -> PerformanceReporter:
    """Get global performance reporter instance."""
    global _performance_reporter
    if _performance_reporter is None:
        _performance_reporter = PerformanceReporter()
    return _performance_reporter