"""
Comprehensive Testing Framework
Unit tests, integration tests, and test utilities for the Risk Management Platform
"""

import os
import sys
import pytest
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import tempfile
import shutil

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test configuration
TEST_CONFIG = {
    'environment': 'test',
    'database': {
        'url': 'sqlite:///:memory:',
        'echo': False
    },
    'snowflake': {
        'account': 'test_account',
        'user': 'test_user',
        'warehouse': 'TEST_WH',
        'database': 'TEST_DB'
    },
    'redis': {
        'host': 'localhost',
        'port': 6379,
        'db': 15  # Use test database
    }
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestFixtures:
    """Test data fixtures and utilities."""
    
    @staticmethod
    def get_sample_portfolio_positions() -> pd.DataFrame:
        """Get sample portfolio positions for testing."""
        return pd.DataFrame([
            {
                'position_id': 'POS_001',
                'symbol': 'AAPL',
                'quantity': 100,
                'unit_cost': 150.00,
                'market_value': 16500.00,
                'weight': 0.25,
                'sector': 'Technology',
                'currency': 'USD'
            },
            {
                'position_id': 'POS_002', 
                'symbol': 'MSFT',
                'quantity': 150,
                'unit_cost': 250.00,
                'market_value': 39000.00,
                'weight': 0.35,
                'sector': 'Technology',
                'currency': 'USD'
            },
            {
                'position_id': 'POS_003',
                'symbol': 'SPY',
                'quantity': 200,
                'unit_cost': 400.00,
                'market_value': 84000.00,
                'weight': 0.40,
                'sector': 'ETF',
                'currency': 'USD'
            }
        ])
    
    @staticmethod
    def get_sample_price_data() -> pd.DataFrame:
        """Get sample historical price data for testing."""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='B')  # Business days
        symbols = ['AAPL', 'MSFT', 'SPY']
        
        data = []
        for symbol in symbols:
            # Generate realistic price series with random walk
            np.random.seed(hash(symbol) % (2**32))  # Deterministic seed per symbol
            base_price = {'AAPL': 150, 'MSFT': 250, 'SPY': 400}[symbol]
            
            prices = [base_price]
            for _ in range(len(dates) - 1):
                change = np.random.normal(0.001, 0.02)  # Daily return
                new_price = prices[-1] * (1 + change)
                prices.append(max(new_price, 1.0))  # Prevent negative prices
            
            for i, (date, price) in enumerate(zip(dates, prices)):
                # Generate OHLC
                daily_vol = abs(np.random.normal(0, 0.01))
                high = price * (1 + daily_vol/2)
                low = price * (1 - daily_vol/2)
                open_price = prices[i-1] if i > 0 else price
                
                data.append({
                    'trading_date': date,
                    'symbol': symbol,
                    'open_price': round(open_price, 2),
                    'high_price': round(high, 2),
                    'low_price': round(low, 2),
                    'close_price': round(price, 2),
                    'adjusted_close': round(price, 2),
                    'volume': int(np.random.uniform(1000000, 10000000))
                })
        
        return pd.DataFrame(data)
    
    @staticmethod
    def get_sample_market_data() -> pd.DataFrame:
        """Get sample market index data (S&P 500)."""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='B')
        
        # Generate S&P 500 like data
        np.random.seed(12345)
        base_price = 4000
        prices = [base_price]
        
        for _ in range(len(dates) - 1):
            change = np.random.normal(0.0005, 0.015)  # Market return characteristics
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 100.0))
        
        data = []
        for date, price in zip(dates, prices):
            data.append({
                'trading_date': date,
                'symbol': '^GSPC',
                'close_price': round(price, 2)
            })
        
        return pd.DataFrame(data)
    
    @staticmethod
    def get_sample_portfolio_returns() -> pd.Series:
        """Get sample portfolio returns for testing."""
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='B')
        returns = np.random.normal(0.001, 0.015, len(dates))  # Daily returns
        return pd.Series(returns, index=dates)
    
    @staticmethod
    def create_temp_config_file() -> str:
        """Create temporary configuration file for testing."""
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, 'test_config.yaml')
        
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(TEST_CONFIG, f)
        
        return config_file


class MockSnowflakeConnector:
    """Mock Snowflake connector for testing."""
    
    def __init__(self):
        self.connected = True
        self.query_results = {}
    
    def connect(self) -> bool:
        return True
    
    def execute_query(self, query: str, params: Dict = None, use_cache: bool = True) -> List[Dict]:
        """Return predefined results based on query patterns."""
        if 'portfolio_data.positions' in query:
            return TestFixtures.get_sample_portfolio_positions().to_dict('records')
        elif 'market_data.daily_prices' in query:
            return TestFixtures.get_sample_price_data().to_dict('records')
        elif 'SHOW WAREHOUSES' in query.upper():
            return [
                {'name': 'TEST_WH', 'size': 'X-SMALL', 'state': 'STARTED'},
                {'name': 'DEV_WH', 'size': 'SMALL', 'state': 'SUSPENDED'}
            ]
        elif 'SHOW DATABASES' in query.upper():
            return [
                {'name': 'TEST_DB', 'is_current': True},
                {'name': 'RISK_DATA', 'is_current': False}
            ]
        else:
            return []
    
    def get_warehouses(self) -> List[Dict]:
        return [
            {'name': 'TEST_WH', 'size': 'X-SMALL', 'state': 'STARTED', 'type': 'STANDARD'}
        ]
    
    def get_databases(self) -> List[Dict]:
        return [
            {'name': 'TEST_DB', 'is_current': True, 'is_default': False}
        ]
    
    def get_market_data(self, start_date: str, end_date: str, symbols: List[str] = None) -> pd.DataFrame:
        sample_data = TestFixtures.get_sample_price_data()
        if symbols:
            sample_data = sample_data[sample_data['symbol'].isin(symbols)]
        return sample_data
    
    def get_portfolio_data(self, portfolio_id: str, as_of_date: str = None) -> pd.DataFrame:
        return TestFixtures.get_sample_portfolio_positions()


class MockMarketDataProvider:
    """Mock market data provider for testing."""
    
    def __init__(self):
        self.data_cache = {}
    
    def get_daily_prices(self, symbol: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        sample_data = TestFixtures.get_sample_price_data()
        return sample_data[sample_data['symbol'] == symbol].copy()
    
    def get_multiple_symbols(self, symbols: List[str], start_date: str, end_date: str = None) -> pd.DataFrame:
        sample_data = TestFixtures.get_sample_price_data()
        return sample_data[sample_data['symbol'].isin(symbols)].copy()
    
    def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        return {
            'symbol': symbol,
            'price': 150.25,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'change': 2.15,
            'change_percent': 1.45,
            'volume': 1500000
        }


class MockRiskEngine:
    """Mock risk calculation engine for testing."""
    
    def calculate_returns(self, prices: pd.Series, method: str = 'simple') -> pd.Series:
        if len(prices) < 2:
            return pd.Series(dtype=float)
        return prices.pct_change().dropna()
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        if len(returns) == 0:
            return 0.0
        return abs(np.percentile(returns, (1 - confidence_level) * 100))
    
    def calculate_volatility(self, returns: pd.Series, annualize: bool = True) -> float:
        if len(returns) == 0:
            return 0.0
        vol = returns.std()
        return vol * np.sqrt(252) if annualize else vol
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        if len(returns) == 0:
            return 0.0
        annual_return = returns.mean() * 252
        annual_vol = self.calculate_volatility(returns)
        return (annual_return - risk_free_rate) / annual_vol if annual_vol != 0 else 0.0
    
    def calculate_all_risk_metrics(self, portfolio_id: str, positions: pd.DataFrame, price_data: pd.DataFrame) -> Dict:
        """Return mock risk results."""
        from libs.risk.calculations import RiskResults
        
        return RiskResults(
            portfolio_id=portfolio_id,
            calculation_date=datetime.utcnow(),
            var_95=0.025,
            var_99=0.045,
            expected_shortfall=0.055,
            volatility=0.18,
            sharpe_ratio=1.35,
            max_drawdown=0.12,
            beta=1.05,
            alpha=0.02
        )


class TestBase(unittest.TestCase):
    """Base test class with common setup and utilities."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class."""
        cls.test_config = TEST_CONFIG.copy()
        cls.fixtures = TestFixtures()
        
        # Create mock objects
        cls.mock_snowflake = MockSnowflakeConnector()
        cls.mock_market_data = MockMarketDataProvider()
        cls.mock_risk_engine = MockRiskEngine()
        
        logger.info(f"Setting up test class: {cls.__name__}")
    
    def setUp(self):
        """Set up each test."""
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"Starting test: {self._testMethodName}")
    
    def tearDown(self):
        """Clean up after each test."""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        logger.info(f"Completed test: {self._testMethodName}")
    
    def assert_dataframe_not_empty(self, df: pd.DataFrame, msg: str = None):
        """Assert that DataFrame is not empty."""
        self.assertIsInstance(df, pd.DataFrame, msg or "Expected pandas DataFrame")
        self.assertGreater(len(df), 0, msg or "DataFrame should not be empty")
    
    def assert_valid_risk_metrics(self, metrics: Dict[str, Any]):
        """Assert that risk metrics are valid."""
        required_fields = ['var_95', 'var_99', 'volatility', 'sharpe_ratio']
        
        for field in required_fields:
            self.assertIn(field, metrics, f"Missing required field: {field}")
            self.assertIsInstance(metrics[field], (int, float), f"Field {field} should be numeric")
            self.assertGreaterEqual(metrics[field], 0, f"Field {field} should be non-negative")
    
    def create_test_portfolio(self) -> pd.DataFrame:
        """Create test portfolio for testing."""
        return self.fixtures.get_sample_portfolio_positions()
    
    def create_test_price_data(self) -> pd.DataFrame:
        """Create test price data for testing."""
        return self.fixtures.get_sample_price_data()


# Pytest fixtures for async testing
@pytest.fixture
def test_config():
    """Test configuration fixture."""
    return TEST_CONFIG.copy()

@pytest.fixture
def sample_portfolio():
    """Sample portfolio fixture."""
    return TestFixtures.get_sample_portfolio_positions()

@pytest.fixture
def sample_price_data():
    """Sample price data fixture."""
    return TestFixtures.get_sample_price_data()

@pytest.fixture
def mock_snowflake():
    """Mock Snowflake connector fixture."""
    return MockSnowflakeConnector()

@pytest.fixture
def mock_market_data():
    """Mock market data provider fixture.""" 
    return MockMarketDataProvider()

@pytest.fixture
def mock_risk_engine():
    """Mock risk engine fixture."""
    return MockRiskEngine()

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


class TestRunner:
    """Test runner with enhanced reporting and coverage."""
    
    def __init__(self, test_directory: str = None):
        self.test_directory = test_directory or str(PROJECT_ROOT / 'tests')
        self.results = {}
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests with coverage."""
        logger.info("Running unit tests...")
        
        try:
            # Run with pytest for better output
            import subprocess
            result = subprocess.run([
                'python', '-m', 'pytest', 
                os.path.join(self.test_directory, 'unit'),
                '-v', '--tb=short', '--cov=libs', '--cov=services',
                '--cov-report=term', '--cov-report=html'
            ], capture_output=True, text=True, cwd=str(PROJECT_ROOT))
            
            self.results['unit_tests'] = {
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'passed': result.returncode == 0
            }
            
        except Exception as e:
            self.results['unit_tests'] = {
                'exit_code': 1,
                'error': str(e),
                'passed': False
            }
        
        return self.results['unit_tests']
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        logger.info("Running integration tests...")
        
        try:
            import subprocess
            result = subprocess.run([
                'python', '-m', 'pytest',
                os.path.join(self.test_directory, 'integration'),
                '-v', '--tb=short'
            ], capture_output=True, text=True, cwd=str(PROJECT_ROOT))
            
            self.results['integration_tests'] = {
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'passed': result.returncode == 0
            }
            
        except Exception as e:
            self.results['integration_tests'] = {
                'exit_code': 1,
                'error': str(e),
                'passed': False
            }
        
        return self.results['integration_tests']
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests."""
        logger.info("Running performance tests...")
        
        try:
            import subprocess
            result = subprocess.run([
                'python', '-m', 'pytest',
                os.path.join(self.test_directory, 'performance'),
                '-v', '--tb=short', '--benchmark-only'
            ], capture_output=True, text=True, cwd=str(PROJECT_ROOT))
            
            self.results['performance_tests'] = {
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'passed': result.returncode == 0
            }
            
        except Exception as e:
            self.results['performance_tests'] = {
                'exit_code': 1,
                'error': str(e),
                'passed': False
            }
        
        return self.results['performance_tests']
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites."""
        logger.info("Running all tests...")
        
        all_results = {
            'unit_tests': self.run_unit_tests(),
            'integration_tests': self.run_integration_tests(),
            'performance_tests': self.run_performance_tests(),
            'summary': {}
        }
        
        # Calculate summary
        total_passed = sum(1 for result in all_results.values() 
                          if isinstance(result, dict) and result.get('passed', False))
        total_suites = 3
        
        all_results['summary'] = {
            'total_suites': total_suites,
            'passed_suites': total_passed,
            'success_rate': (total_passed / total_suites) * 100,
            'overall_passed': total_passed == total_suites
        }
        
        return all_results
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report."""
        if not self.results:
            self.run_all_tests()
        
        report_lines = [
            "# Risk Management Platform - Test Report",
            f"Generated: {datetime.utcnow().isoformat()}",
            "",
            "## Summary",
            f"- Total Test Suites: {self.results.get('summary', {}).get('total_suites', 0)}",
            f"- Passed Suites: {self.results.get('summary', {}).get('passed_suites', 0)}",
            f"- Success Rate: {self.results.get('summary', {}).get('success_rate', 0):.1f}%",
            f"- Overall Status: {'✅ PASSED' if self.results.get('summary', {}).get('overall_passed') else '❌ FAILED'}",
            ""
        ]
        
        for test_type, result in self.results.items():
            if test_type == 'summary':
                continue
                
            status = "✅ PASSED" if result.get('passed') else "❌ FAILED"
            report_lines.extend([
                f"## {test_type.replace('_', ' ').title()}",
                f"Status: {status}",
                f"Exit Code: {result.get('exit_code', 'Unknown')}",
                ""
            ])
            
            if result.get('stdout'):
                report_lines.extend([
                    "### Output",
                    "```",
                    result['stdout'],
                    "```",
                    ""
                ])
            
            if result.get('stderr'):
                report_lines.extend([
                    "### Errors", 
                    "```",
                    result['stderr'],
                    "```",
                    ""
                ])
        
        return '\n'.join(report_lines)


# Test discovery and execution utilities
def discover_tests(directory: str = None) -> List[str]:
    """Discover all test files in the project."""
    test_dir = Path(directory) if directory else PROJECT_ROOT / 'tests'
    if not test_dir.exists():
        return []
    
    test_files = []
    for pattern in ['test_*.py', '*_test.py']:
        test_files.extend(test_dir.rglob(pattern))
    
    return [str(f) for f in test_files]


def run_specific_test(test_file: str, test_method: str = None) -> Dict[str, Any]:
    """Run a specific test file or method."""
    try:
        import subprocess
        
        cmd = ['python', '-m', 'pytest', test_file, '-v']
        if test_method:
            cmd.append(f'::{test_method}')
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))
        
        return {
            'test_file': test_file,
            'test_method': test_method,
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'passed': result.returncode == 0
        }
        
    except Exception as e:
        return {
            'test_file': test_file,
            'test_method': test_method,
            'exit_code': 1,
            'error': str(e),
            'passed': False
        }


if __name__ == "__main__":
    # Run tests when executed directly
    runner = TestRunner()
    results = runner.run_all_tests()
    
    print(runner.generate_test_report())
    
    # Exit with appropriate code
    exit_code = 0 if results.get('summary', {}).get('overall_passed') else 1
    sys.exit(exit_code)