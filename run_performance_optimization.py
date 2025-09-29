#!/usr/bin/env python3
"""
Performance Optimization Runner
Comprehensive performance testing, monitoring, and optimization
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from libs.performance import (
        get_cache_manager, get_db_optimizer, get_performance_profiler,
        get_performance_monitor, get_load_tester, get_benchmark_suite,
        get_performance_reporter, performance_monitor, benchmark_suite,
        cleanup_memory, get_memory_usage
    )
    from libs.data.snowflake_client import get_snowflake_client
    from libs.data.market_data_client import get_market_data_provider
    from libs.risk.calculations import get_risk_calculator
    from config import get_config
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements-performance.txt")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceOptimizationRunner:
    """Main runner for performance optimization tasks."""
    
    def __init__(self):
        self.config = get_config()
        self.results = {}
    
    def run_cache_performance_tests(self):
        """Test cache performance and optimization."""
        logger.info("Running cache performance tests...")
        
        cache_manager = get_cache_manager()
        benchmark_suite = get_benchmark_suite()
        
        # Benchmark cache operations
        cache_results = benchmark_suite.benchmark_cache_operations(cache_manager)
        
        # Test cache hit rates with different data sizes
        test_data_sizes = [1, 10, 100, 1000, 10000]  # Number of items
        
        for size in test_data_sizes:
            # Populate cache
            for i in range(size):
                key = f"test_key_{i}"
                value = {"data": f"test_value_{i}", "index": i}
                cache_manager.set(key, value)
            
            # Test retrieval performance
            result = benchmark_suite.benchmark_function(
                lambda: cache_manager.get(f"test_key_{size//2}"),
                f"cache_get_{size}_items",
                iterations=1000
            )
            
            if result:
                cache_results.append(result)
        
        # Get cache statistics
        cache_stats = cache_manager.get_stats()
        
        self.results['cache_performance'] = {
            'benchmark_results': [r.to_dict() for r in cache_results if r],
            'cache_statistics': cache_stats,
            'recommendations': self._generate_cache_recommendations(cache_stats, cache_results)
        }
        
        logger.info(f"Cache performance tests completed. Hit rate: {cache_stats.get('hit_rate_percent', 0):.2f}%")
    
    def run_database_performance_tests(self):
        """Test database performance and optimization."""
        logger.info("Running database performance tests...")
        
        db_optimizer = get_db_optimizer()
        benchmark_suite = get_benchmark_suite()
        
        # Benchmark basic database operations
        db_results = benchmark_suite.benchmark_database_operations(db_optimizer)
        
        # Test different query patterns
        test_queries = [
            ("simple_select", "SELECT 1 as test_value"),
            ("system_info", "SELECT version()"),
            ("table_list", "SELECT table_name FROM information_schema.tables LIMIT 10"),
        ]
        
        for query_name, query in test_queries:
            result = benchmark_suite.benchmark_function(
                lambda q=query: db_optimizer.execute_query(q),
                f"query_{query_name}",
                iterations=100
            )
            if result:
                db_results.append(result)
        
        # Analyze query performance
        query_analysis = db_optimizer.analyze_query_performance()
        pool_stats = db_optimizer.get_connection_pool_stats()
        
        self.results['database_performance'] = {
            'benchmark_results': [r.to_dict() for r in db_results if r],
            'query_analysis': query_analysis,
            'connection_pool_stats': pool_stats,
            'recommendations': self._generate_database_recommendations(query_analysis, pool_stats)
        }
        
        logger.info("Database performance tests completed")
    
    def run_system_performance_tests(self):
        """Test overall system performance."""
        logger.info("Running system performance tests...")
        
        profiler = get_performance_profiler()
        
        # Test different computational workloads
        workloads = [
            ("cpu_intensive", self._cpu_intensive_task, 100),
            ("memory_intensive", self._memory_intensive_task, 50),
            ("io_intensive", self._io_intensive_task, 20),
        ]
        
        benchmark_suite = get_benchmark_suite()
        system_results = []
        
        for workload_name, workload_func, iterations in workloads:
            result = benchmark_suite.benchmark_function(
                workload_func,
                workload_name,
                iterations=iterations
            )
            if result:
                system_results.append(result)
        
        # Collect system metrics
        system_metrics = profiler.collect_system_metrics()
        memory_usage = get_memory_usage()
        
        self.results['system_performance'] = {
            'benchmark_results': [r.to_dict() for r in system_results],
            'current_metrics': system_metrics.to_dict(),
            'memory_usage': memory_usage,
            'recommendations': self._generate_system_recommendations(system_metrics, memory_usage)
        }
        
        logger.info("System performance tests completed")
    
    def run_api_load_tests(self, base_url: str = "http://localhost:8000"):
        """Run API load tests."""
        logger.info(f"Running API load tests against {base_url}...")
        
        load_tester = get_load_tester()
        load_tester.base_url = base_url
        
        # Test different endpoints with varying loads
        test_scenarios = [
            ("/health", "GET", 50, 30, None),
            ("/metrics", "GET", 20, 60, None),
            # Add more endpoints as needed
        ]
        
        load_test_results = []
        
        for endpoint, method, users, duration, payload in test_scenarios:
            try:
                result = load_tester.run_load_test(
                    endpoint=endpoint,
                    concurrent_users=users,
                    duration_seconds=duration,
                    method=method,
                    payload=payload
                )
                load_test_results.append(result)
                
                logger.info(f"Load test {endpoint}: {result.requests_per_second:.2f} RPS, "
                           f"{result.error_rate:.2f}% error rate")
                
            except Exception as e:
                logger.error(f"Load test failed for {endpoint}: {e}")
        
        self.results['load_test_results'] = [r.to_dict() for r in load_test_results]
        
        logger.info("API load tests completed")
    
    def run_real_component_benchmarks(self):
        """Benchmark real application components."""
        logger.info("Running real component benchmarks...")
        
        benchmark_suite = get_benchmark_suite()
        component_results = []
        
        # Test Snowflake client (if available)
        try:
            snowflake_client = get_snowflake_client()
            if snowflake_client:
                result = benchmark_suite.benchmark_function(
                    lambda: snowflake_client.test_connection(),
                    "snowflake_connection_test",
                    iterations=10  # Fewer iterations for external service
                )
                if result:
                    component_results.append(result)
        except Exception as e:
            logger.warning(f"Snowflake benchmark skipped: {e}")
        
        # Test market data provider (if available)
        try:
            market_data_provider = get_market_data_provider()
            if market_data_provider:
                result = benchmark_suite.benchmark_function(
                    lambda: market_data_provider.get_current_price("AAPL"),
                    "market_data_single_price",
                    iterations=10
                )
                if result:
                    component_results.append(result)
        except Exception as e:
            logger.warning(f"Market data benchmark skipped: {e}")
        
        # Test risk calculator
        try:
            risk_calculator = get_risk_calculator()
            if risk_calculator:
                # Create sample data for risk calculation
                sample_portfolio = [
                    {"symbol": "AAPL", "quantity": 100, "price": 150.0},
                    {"symbol": "GOOGL", "quantity": 50, "price": 2500.0}
                ]
                
                sample_prices = {
                    "AAPL": [150.0, 152.0, 148.0, 151.0, 149.0],
                    "GOOGL": [2500.0, 2520.0, 2480.0, 2510.0, 2490.0]
                }
                
                result = benchmark_suite.benchmark_function(
                    lambda: risk_calculator.calculate_portfolio_var(sample_portfolio, sample_prices),
                    "risk_calculation_var",
                    iterations=100
                )
                if result:
                    component_results.append(result)
        except Exception as e:
            logger.warning(f"Risk calculation benchmark skipped: {e}")
        
        self.results['component_benchmarks'] = [r.to_dict() for r in component_results]
        
        logger.info("Real component benchmarks completed")
    
    async def run_async_performance_tests(self):
        """Run async performance tests."""
        logger.info("Running async performance tests...")
        
        benchmark_suite = get_benchmark_suite()
        
        # Test async operations
        async_results = []
        
        # Async sleep test (simulates I/O)
        result = await benchmark_suite.benchmark_async_function(
            self._async_io_simulation,
            "async_io_simulation",
            iterations=100
        )
        if result:
            async_results.append(result)
        
        # Concurrent async operations
        result = await benchmark_suite.benchmark_async_function(
            self._concurrent_async_operations,
            "concurrent_async_ops",
            iterations=50
        )
        if result:
            async_results.append(result)
        
        self.results['async_performance'] = [r.to_dict() for r in async_results]
        
        logger.info("Async performance tests completed")
    
    def run_monitoring_test(self, duration_minutes: int = 5):
        """Run performance monitoring test."""
        logger.info(f"Running performance monitoring for {duration_minutes} minutes...")
        
        with performance_monitor() as monitor:
            # Let monitoring run for specified duration
            import time
            
            # Simulate some workload during monitoring
            start_time = time.time()
            iteration = 0
            
            while time.time() - start_time < (duration_minutes * 60):
                # Simulate varying workload
                if iteration % 10 == 0:
                    self._cpu_intensive_task()
                elif iteration % 15 == 0:
                    self._memory_intensive_task()
                
                time.sleep(1)
                iteration += 1
            
            # Get monitoring results
            metrics_summary = monitor.get_metrics_summary(duration_minutes)
            recent_alerts = monitor.get_recent_alerts(1)  # Last hour
            
            self.results['monitoring_results'] = {
                'metrics_summary': metrics_summary,
                'alerts': recent_alerts
            }
        
        logger.info("Performance monitoring test completed")
    
    def generate_optimization_report(self):
        """Generate comprehensive optimization report."""
        logger.info("Generating optimization report...")
        
        reporter = get_performance_reporter()
        
        # Create dashboard with all results
        dashboard = {
            'timestamp': datetime.utcnow().isoformat(),
            'test_results': self.results,
            'system_info': {
                'memory_usage': get_memory_usage(),
                'python_version': sys.version,
                'platform': sys.platform
            }
        }
        
        # Add overall recommendations
        dashboard['overall_recommendations'] = self._generate_overall_recommendations()
        
        # Save report
        report_file = reporter.save_report(dashboard)
        
        # Print summary
        self._print_performance_summary()
        
        logger.info(f"Optimization report saved to: {report_file}")
        return dashboard
    
    def _cpu_intensive_task(self):
        """CPU-intensive benchmark task."""
        total = 0
        for i in range(10000):
            total += i ** 2
        return total
    
    def _memory_intensive_task(self):
        """Memory-intensive benchmark task."""
        data = []
        for i in range(1000):
            data.append([j for j in range(100)])
        return len(data)
    
    def _io_intensive_task(self):
        """I/O-intensive benchmark task."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            # Write data
            for i in range(100):
                tmp.write(f"Line {i}\n".encode())
            tmp_path = tmp.name
        
        # Read data back
        with open(tmp_path, 'r') as f:
            lines = f.readlines()
        
        # Cleanup
        os.unlink(tmp_path)
        return len(lines)
    
    async def _async_io_simulation(self):
        """Simulate async I/O operation."""
        await asyncio.sleep(0.01)  # 10ms simulated I/O
        return "completed"
    
    async def _concurrent_async_operations(self):
        """Test concurrent async operations."""
        tasks = [self._async_io_simulation() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        return len(results)
    
    def _generate_cache_recommendations(self, cache_stats, cache_results):
        """Generate cache-specific recommendations."""
        recommendations = []
        
        hit_rate = cache_stats.get('hit_rate_percent', 0)
        if hit_rate < 80:
            recommendations.append(f"Cache hit rate is low ({hit_rate:.1f}%). Consider increasing TTL or cache size.")
        
        if cache_results:
            slowest_cache_op = max(cache_results, key=lambda x: x.average_time if x else 0)
            if slowest_cache_op and slowest_cache_op.average_time > 0.01:  # 10ms
                recommendations.append(f"Cache operation '{slowest_cache_op.operation_name}' is slow. Consider optimization.")
        
        return recommendations
    
    def _generate_database_recommendations(self, query_analysis, pool_stats):
        """Generate database-specific recommendations."""
        recommendations = []
        
        if query_analysis.get('slow_queries_count', 0) > 0:
            recommendations.append("Slow queries detected. Consider adding indexes or optimizing query structure.")
        
        if pool_stats.get('checked_out_connections', 0) > pool_stats.get('pool_size', 0) * 0.8:
            recommendations.append("High database connection usage. Consider increasing pool size.")
        
        avg_time = query_analysis.get('average_execution_time', 0)
        if avg_time > 0.1:  # 100ms
            recommendations.append(f"Average query time is high ({avg_time:.3f}s). Consider query optimization.")
        
        return recommendations
    
    def _generate_system_recommendations(self, system_metrics, memory_usage):
        """Generate system-specific recommendations."""
        recommendations = []
        
        if system_metrics.cpu_usage_percent > 80:
            recommendations.append("High CPU usage. Consider optimizing CPU-intensive operations.")
        
        if system_metrics.memory_usage_percent > 85:
            recommendations.append("High memory usage. Consider memory optimization or garbage collection.")
        
        if memory_usage['process_memory_percent'] > 50:
            recommendations.append("Process using significant memory. Monitor for memory leaks.")
        
        return recommendations
    
    def _generate_overall_recommendations(self):
        """Generate overall optimization recommendations."""
        recommendations = []
        
        # Collect all sub-recommendations
        for category, data in self.results.items():
            if isinstance(data, dict) and 'recommendations' in data:
                recommendations.extend(data['recommendations'])
        
        # Add general recommendations
        recommendations.extend([
            "Consider implementing Redis caching for frequently accessed data",
            "Use database connection pooling for better resource utilization",
            "Implement async processing for I/O-bound operations",
            "Monitor and profile application regularly",
            "Use CDN for static assets in production"
        ])
        
        return list(set(recommendations))  # Remove duplicates
    
    def _print_performance_summary(self):
        """Print performance test summary."""
        print("\n" + "="*80)
        print("PERFORMANCE OPTIMIZATION SUMMARY")
        print("="*80)
        
        # Cache performance
        if 'cache_performance' in self.results:
            cache_stats = self.results['cache_performance']['cache_statistics']
            print(f"\nCache Performance:")
            print(f"  Hit Rate: {cache_stats.get('hit_rate_percent', 0):.2f}%")
            print(f"  Total Requests: {cache_stats.get('total_requests', 0)}")
        
        # Database performance
        if 'database_performance' in self.results:
            query_analysis = self.results['database_performance']['query_analysis']
            print(f"\nDatabase Performance:")
            print(f"  Average Query Time: {query_analysis.get('average_execution_time', 0):.3f}s")
            print(f"  Slow Queries: {query_analysis.get('slow_queries_count', 0)}")
        
        # System performance
        if 'system_performance' in self.results:
            metrics = self.results['system_performance']['current_metrics']
            print(f"\nSystem Performance:")
            print(f"  CPU Usage: {metrics.get('cpu_usage_percent', 0):.1f}%")
            print(f"  Memory Usage: {metrics.get('memory_usage_percent', 0):.1f}%")
        
        # Load test results
        if 'load_test_results' in self.results:
            print(f"\nLoad Test Results:")
            for result in self.results['load_test_results']:
                print(f"  {result['test_name']}: {result['requests_per_second']:.2f} RPS, "
                      f"{result['error_rate']:.2f}% errors")
        
        print("\n" + "="*80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Performance Optimization Runner")
    parser.add_argument("--cache", action="store_true", help="Run cache performance tests")
    parser.add_argument("--database", action="store_true", help="Run database performance tests")
    parser.add_argument("--system", action="store_true", help="Run system performance tests")
    parser.add_argument("--load-test", help="Run API load tests (specify base URL)")
    parser.add_argument("--components", action="store_true", help="Benchmark real components")
    parser.add_argument("--async", action="store_true", help="Run async performance tests")
    parser.add_argument("--monitor", type=int, metavar="MINUTES", help="Run monitoring test for N minutes")
    parser.add_argument("--all", action="store_true", help="Run all performance tests")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup memory after tests")
    
    args = parser.parse_args()
    
    if not any([args.cache, args.database, args.system, args.load_test, 
                args.components, args.async, args.monitor, args.all]):
        parser.print_help()
        return
    
    runner = PerformanceOptimizationRunner()
    
    try:
        if args.all or args.cache:
            runner.run_cache_performance_tests()
        
        if args.all or args.database:
            runner.run_database_performance_tests()
        
        if args.all or args.system:
            runner.run_system_performance_tests()
        
        if args.load_test or args.all:
            base_url = args.load_test if args.load_test else "http://localhost:8000"
            runner.run_api_load_tests(base_url)
        
        if args.all or args.components:
            runner.run_real_component_benchmarks()
        
        if args.all or args.async:
            asyncio.run(runner.run_async_performance_tests())
        
        if args.monitor or args.all:
            duration = args.monitor if args.monitor else 2  # Default 2 minutes for --all
            runner.run_monitoring_test(duration)
        
        # Generate final report
        report = runner.generate_optimization_report()
        
        if args.cleanup:
            cleanup_memory()
            logger.info("Memory cleanup completed")
        
        logger.info("Performance optimization completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Performance testing interrupted by user")
    except Exception as e:
        logger.error(f"Performance testing failed: {e}")
        raise


if __name__ == "__main__":
    main()