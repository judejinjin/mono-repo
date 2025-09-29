"""
Performance Tests and Benchmarks
Tests for performance characteristics of the Risk Management Platform
"""

import sys
import pytest
import time
import threading
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import statistics

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.test_framework import TestBase, TestFixtures, MockRiskEngine, MockMarketDataProvider
from libs.risk.calculations import RiskCalculationEngine
from libs.data.market_data_client import MarketDataProvider
from libs.monitoring.prometheus_metrics import PrometheusMetricsCollector


class PerformanceTestBase(TestBase):
    """Base class for performance tests."""
    
    def setUp(self):
        super().setUp()
        self.performance_results = {}
        
    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function."""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        return result, execution_time
    
    def measure_memory_usage(self, func, *args, **kwargs):
        """Measure memory usage of a function."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss
            
            result = func(*args, **kwargs)
            
            memory_after = process.memory_info().rss
            memory_diff = memory_after - memory_before
            
            return result, memory_diff
        except ImportError:
            # Fallback if psutil not available
            return func(*args, **kwargs), 0
    
    def run_benchmark(self, func, iterations: int = 100, *args, **kwargs) -> Dict[str, Any]:
        """Run benchmark for a function multiple iterations."""
        times = []
        
        # Warmup
        for _ in range(min(10, iterations // 10)):
            func(*args, **kwargs)
        
        # Actual benchmark
        for _ in range(iterations):
            _, execution_time = self.measure_time(func, *args, **kwargs)
            times.append(execution_time)
        
        return {
            'iterations': iterations,
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'total_time': sum(times),
            'times': times
        }


class TestRiskCalculationPerformance(PerformanceTestBase):
    """Performance tests for risk calculation engine."""
    
    def setUp(self):
        super().setUp()
        self.risk_engine = RiskCalculationEngine()
        self.large_portfolio = self.create_large_portfolio()
        self.large_price_data = self.create_large_price_dataset()
    
    def create_large_portfolio(self, num_positions: int = 100) -> pd.DataFrame:
        """Create large portfolio for performance testing.""" 
        positions = []
        symbols = [f'STOCK_{i:03d}' for i in range(num_positions)]
        
        np.random.seed(42)
        weights = np.random.dirichlet(np.ones(num_positions))  # Random weights that sum to 1
        
        for i, (symbol, weight) in enumerate(zip(symbols, weights)):
            positions.append({
                'position_id': f'POS_{i:03d}',
                'symbol': symbol,
                'quantity': np.random.uniform(10, 1000),
                'unit_cost': np.random.uniform(10, 500),
                'market_value': weight * 10000000,  # $10M portfolio
                'weight': weight,
                'sector': np.random.choice(['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer']),
                'currency': 'USD'
            })
        
        return pd.DataFrame(positions)
    
    def create_large_price_dataset(self, num_symbols: int = 100, num_days: int = 252) -> pd.DataFrame:
        """Create large price dataset for performance testing."""
        symbols = [f'STOCK_{i:03d}' for i in range(num_symbols)]
        dates = pd.date_range(start='2023-01-01', periods=num_days, freq='B')
        
        data = []
        
        for symbol in symbols:
            np.random.seed(hash(symbol) % (2**32))
            base_price = np.random.uniform(50, 500)
            
            prices = [base_price]
            for _ in range(num_days - 1):
                change = np.random.normal(0.001, 0.02)
                new_price = max(prices[-1] * (1 + change), 1.0)
                prices.append(new_price)
            
            for date, price in zip(dates, prices):
                daily_vol = abs(np.random.normal(0, 0.01))
                
                data.append({
                    'trading_date': date,
                    'symbol': symbol,
                    'open_price': price * (1 + np.random.uniform(-0.01, 0.01)),
                    'high_price': price * (1 + daily_vol/2),
                    'low_price': price * (1 - daily_vol/2),
                    'close_price': price,
                    'adjusted_close': price,
                    'volume': int(np.random.uniform(100000, 10000000))
                })
        
        return pd.DataFrame(data)
    
    @pytest.mark.benchmark
    def test_var_calculation_performance(self):
        """Benchmark VaR calculation performance."""
        # Generate large return series
        large_returns = pd.Series(np.random.normal(0.001, 0.02, 10000))
        
        benchmark_results = self.run_benchmark(
            self.risk_engine.calculate_var,
            iterations=1000,
            returns=large_returns,
            confidence_level=0.95
        )
        
        self.performance_results['var_calculation'] = benchmark_results
        
        # Performance assertions
        self.assertLess(benchmark_results['mean'], 0.01, "VaR calculation should be under 10ms on average")
        self.assertLess(benchmark_results['max'], 0.1, "VaR calculation should never exceed 100ms")
        
        print(f"VaR Calculation Performance:")
        print(f"  Mean: {benchmark_results['mean']*1000:.2f}ms")
        print(f"  Median: {benchmark_results['median']*1000:.2f}ms")
        print(f"  Max: {benchmark_results['max']*1000:.2f}ms")
    
    @pytest.mark.benchmark
    def test_portfolio_returns_calculation_performance(self):
        """Benchmark portfolio returns calculation."""
        benchmark_results = self.run_benchmark(
            self.risk_engine.calculate_portfolio_returns,
            iterations=10,
            positions=self.large_portfolio,
            price_data=self.large_price_data
        )
        
        self.performance_results['portfolio_returns'] = benchmark_results
        
        # Performance assertions for large portfolio
        self.assertLess(benchmark_results['mean'], 5.0, "Portfolio returns calculation should be under 5 seconds")
        
        print(f"Portfolio Returns Calculation Performance (100 assets, 252 days):")
        print(f"  Mean: {benchmark_results['mean']:.3f}s")
        print(f"  Median: {benchmark_results['median']:.3f}s")
    
    @pytest.mark.benchmark
    def test_comprehensive_risk_metrics_performance(self):
        """Benchmark comprehensive risk metrics calculation."""
        benchmark_results = self.run_benchmark(
            self.risk_engine.calculate_all_risk_metrics,
            iterations=5,
            portfolio_id='LARGE_PORTFOLIO',
            positions=self.large_portfolio,
            price_data=self.large_price_data
        )
        
        self.performance_results['comprehensive_risk_metrics'] = benchmark_results
        
        # Performance assertions
        self.assertLess(benchmark_results['mean'], 10.0, "Comprehensive risk calculation should be under 10 seconds")
        
        print(f"Comprehensive Risk Metrics Performance:")
        print(f"  Mean: {benchmark_results['mean']:.3f}s")
        print(f"  Median: {benchmark_results['median']:.3f}s")
    
    @pytest.mark.benchmark 
    def test_concurrent_risk_calculations(self):
        """Test performance under concurrent load."""
        def calculate_risk_for_portfolio(portfolio_subset):
            return self.risk_engine.calculate_all_risk_metrics(
                f'PORTFOLIO_{id(portfolio_subset)}',
                portfolio_subset,
                self.large_price_data
            )
        
        # Create multiple portfolio subsets
        portfolio_subsets = []
        subset_size = len(self.large_portfolio) // 4
        
        for i in range(4):
            start_idx = i * subset_size
            end_idx = min((i + 1) * subset_size, len(self.large_portfolio))
            subset = self.large_portfolio.iloc[start_idx:end_idx].copy()
            portfolio_subsets.append(subset)
        
        # Test sequential execution
        start_time = time.perf_counter()
        sequential_results = []
        for subset in portfolio_subsets:
            result = calculate_risk_for_portfolio(subset)
            sequential_results.append(result)
        sequential_time = time.perf_counter() - start_time
        
        # Test concurrent execution
        start_time = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            concurrent_results = list(executor.map(calculate_risk_for_portfolio, portfolio_subsets))
        concurrent_time = time.perf_counter() - start_time
        
        speedup = sequential_time / concurrent_time if concurrent_time > 0 else 0
        
        print(f"Concurrent Risk Calculation Performance:")
        print(f"  Sequential time: {sequential_time:.3f}s")
        print(f"  Concurrent time: {concurrent_time:.3f}s")
        print(f"  Speedup: {speedup:.2f}x")
        
        # Should have some speedup from parallelization
        self.assertGreater(speedup, 1.1, "Concurrent execution should be at least 10% faster")
        
        # Validate results are equivalent
        self.assertEqual(len(sequential_results), len(concurrent_results))
        for seq_result, conc_result in zip(sequential_results, concurrent_results):
            self.assertAlmostEqual(seq_result.var_95, conc_result.var_95, places=6)


class TestMarketDataPerformance(PerformanceTestBase):
    """Performance tests for market data operations."""
    
    def setUp(self):
        super().setUp()
        self.mock_provider = MockMarketDataProvider()
    
    @pytest.mark.benchmark
    def test_single_symbol_fetch_performance(self):
        """Benchmark single symbol data fetch."""
        benchmark_results = self.run_benchmark(
            self.mock_provider.get_daily_prices,
            iterations=100,
            symbol='AAPL',
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        
        self.performance_results['single_symbol_fetch'] = benchmark_results
        
        # Performance assertions
        self.assertLess(benchmark_results['mean'], 0.1, "Single symbol fetch should be under 100ms")
        
        print(f"Single Symbol Fetch Performance:")
        print(f"  Mean: {benchmark_results['mean']*1000:.2f}ms")
    
    @pytest.mark.benchmark
    def test_multiple_symbols_fetch_performance(self):
        """Benchmark multiple symbols data fetch.""" 
        symbols = [f'STOCK_{i:03d}' for i in range(50)]
        
        benchmark_results = self.run_benchmark(
            self.mock_provider.get_multiple_symbols,
            iterations=10,
            symbols=symbols,
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        
        self.performance_results['multiple_symbols_fetch'] = benchmark_results
        
        print(f"Multiple Symbols Fetch Performance (50 symbols):")
        print(f"  Mean: {benchmark_results['mean']:.3f}s")
        print(f"  Throughput: {50/benchmark_results['mean']:.1f} symbols/second")


class TestPrometheusMetricsPerformance(PerformanceTestBase):
    """Performance tests for Prometheus metrics collection."""
    
    def setUp(self):
        super().setUp()
        self.metrics_collector = PrometheusMetricsCollector('test_service')
    
    @pytest.mark.benchmark
    def test_metrics_collection_performance(self):
        """Benchmark metrics collection operations."""
        def record_multiple_metrics():
            for i in range(100):
                self.metrics_collector.record_http_request('GET', f'/endpoint_{i%10}', 200, 0.1)
                self.metrics_collector.record_database_query('postgres', 'select', 0.05)
                self.metrics_collector.record_user_action(f'action_{i%5}', 'user')
        
        benchmark_results = self.run_benchmark(
            record_multiple_metrics,
            iterations=10
        )
        
        self.performance_results['metrics_collection'] = benchmark_results
        
        # Performance assertions
        self.assertLess(benchmark_results['mean'], 1.0, "Metrics collection should be under 1 second for 300 operations")
        
        print(f"Metrics Collection Performance (300 operations):")
        print(f"  Mean: {benchmark_results['mean']:.3f}s")
        print(f"  Throughput: {300/benchmark_results['mean']:.0f} operations/second")
    
    @pytest.mark.benchmark
    def test_metrics_export_performance(self):
        """Benchmark metrics export performance."""
        # Pre-populate some metrics
        for i in range(1000):
            self.metrics_collector.record_http_request('GET', '/test', 200, 0.1)
        
        benchmark_results = self.run_benchmark(
            self.metrics_collector.get_metrics,
            iterations=100
        )
        
        self.performance_results['metrics_export'] = benchmark_results
        
        print(f"Metrics Export Performance:")
        print(f"  Mean: {benchmark_results['mean']*1000:.2f}ms")


class TestMemoryUsagePerformance(PerformanceTestBase):
    """Memory usage performance tests."""
    
    @pytest.mark.benchmark
    def test_large_dataset_memory_usage(self):
        """Test memory usage with large datasets."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create large dataset
            large_data = []
            for i in range(100000):
                large_data.append({
                    'symbol': f'STOCK_{i}',
                    'price': np.random.uniform(10, 1000),
                    'volume': np.random.randint(1000, 1000000),
                    'date': datetime.now() - timedelta(days=i)
                })
            
            df = pd.DataFrame(large_data)
            
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_usage = peak_memory - initial_memory
            
            print(f"Large Dataset Memory Usage:")
            print(f"  Dataset size: {len(df):,} rows")
            print(f"  Memory usage: {memory_usage:.1f} MB")
            print(f"  Memory per row: {memory_usage*1024/len(df):.2f} KB")
            
            # Cleanup
            del df, large_data
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_freed = peak_memory - final_memory
            
            print(f"  Memory freed: {memory_freed:.1f} MB")
            
            # Memory usage should be reasonable
            self.assertLess(memory_usage, 500, "Memory usage should be under 500MB for 100k records")
            
        except ImportError:
            self.skipTest("psutil not available for memory testing")


class TestLoadStressTest(PerformanceTestBase):
    """Load and stress testing."""
    
    def setUp(self):
        super().setUp()
        self.risk_engine = RiskCalculationEngine()
    
    @pytest.mark.benchmark
    def test_sustained_load(self):
        """Test performance under sustained load."""
        def sustained_calculation():
            portfolio = TestFixtures.get_sample_portfolio_positions()
            price_data = TestFixtures.get_sample_price_data()
            
            results = []
            start_time = time.perf_counter()
            
            # Run for 10 seconds
            while time.perf_counter() - start_time < 10:
                result = self.risk_engine.calculate_all_risk_metrics(
                    'LOAD_TEST_PORTFOLIO',
                    portfolio,
                    price_data
                )
                results.append(result)
            
            return results
        
        results = sustained_calculation()
        
        print(f"Sustained Load Test (10 seconds):")
        print(f"  Total calculations: {len(results)}")
        print(f"  Calculations per second: {len(results)/10:.1f}")
        
        # Should handle at least 1 calculation per second
        self.assertGreaterEqual(len(results), 10, "Should handle at least 1 calculation per second")
    
    @pytest.mark.benchmark
    def test_peak_load(self):
        """Test performance under peak load conditions."""
        def peak_load_worker():
            portfolio = TestFixtures.get_sample_portfolio_positions()
            price_data = TestFixtures.get_sample_price_data()
            
            return self.risk_engine.calculate_all_risk_metrics(
                'PEAK_TEST_PORTFOLIO',
                portfolio,
                price_data
            )
        
        # Simulate peak load with multiple concurrent workers
        num_workers = 10
        start_time = time.perf_counter()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(peak_load_worker) for _ in range(num_workers)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        print(f"Peak Load Test ({num_workers} concurrent workers):")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Average time per calculation: {total_time/num_workers:.3f}s")
        print(f"  Successful calculations: {len(results)}")
        
        # All calculations should complete successfully
        self.assertEqual(len(results), num_workers, "All peak load calculations should complete")
        
        # Should complete within reasonable time
        self.assertLess(total_time, 30, "Peak load should complete within 30 seconds")


if __name__ == "__main__":
    # Run performance tests
    import unittest
    unittest.main()