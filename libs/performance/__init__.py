"""
Performance Module Initialization
Provides easy access to all performance optimization components
"""

from .optimization import (
    # Core classes
    PerformanceMetrics, CacheManager, DatabaseOptimizer, 
    PerformanceProfiler, AsyncTaskManager,
    
    # Global instances
    get_cache_manager, get_db_optimizer, get_performance_profiler, get_task_manager,
    
    # Decorators
    cached, async_cached, profiled, async_profiled,
    
    # Utilities
    cleanup_memory, get_memory_usage
)

from .monitoring import (
    # Monitoring classes
    LoadTestResult, BenchmarkResult, PerformanceMonitor,
    LoadTester, BenchmarkSuite, PerformanceReporter,
    
    # Global instances
    get_performance_monitor, get_load_tester, 
    get_benchmark_suite, get_performance_reporter,
    
    # Context managers
    performance_monitor, benchmark_suite
)

__all__ = [
    # Core optimization
    'PerformanceMetrics', 'CacheManager', 'DatabaseOptimizer',
    'PerformanceProfiler', 'AsyncTaskManager',
    'get_cache_manager', 'get_db_optimizer', 'get_performance_profiler', 'get_task_manager',
    'cached', 'async_cached', 'profiled', 'async_profiled',
    'cleanup_memory', 'get_memory_usage',
    
    # Monitoring and benchmarking
    'LoadTestResult', 'BenchmarkResult', 'PerformanceMonitor',
    'LoadTester', 'BenchmarkSuite', 'PerformanceReporter',
    'get_performance_monitor', 'get_load_tester',
    'get_benchmark_suite', 'get_performance_reporter',
    'performance_monitor', 'benchmark_suite'
]