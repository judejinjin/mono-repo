"""
Unit Tests for Risk Calculation Engine
Tests for the real risk calculation implementations
"""

import sys
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.test_framework import TestBase, TestFixtures
from libs.risk.calculations import RiskCalculationEngine, RiskResults


class TestRiskCalculationEngine(TestBase):
    """Test cases for the Risk Calculation Engine."""
    
    def setUp(self):
        super().setUp()
        self.risk_engine = RiskCalculationEngine()
        self.sample_returns = pd.Series([0.01, -0.02, 0.005, -0.015, 0.025, 0.008, -0.012])
        self.sample_positions = self.fixtures.get_sample_portfolio_positions()
        self.sample_prices = self.fixtures.get_sample_price_data()
    
    def test_calculate_returns_simple(self):
        """Test simple return calculation."""
        prices = pd.Series([100, 102, 99, 101, 103])
        returns = self.risk_engine.calculate_returns(prices, method='simple')
        
        expected_returns = prices.pct_change().dropna()
        pd.testing.assert_series_equal(returns, expected_returns)
    
    def test_calculate_returns_log(self):
        """Test logarithmic return calculation."""
        prices = pd.Series([100, 102, 99, 101, 103])
        returns = self.risk_engine.calculate_returns(prices, method='log')
        
        expected_returns = np.log(prices / prices.shift(1)).dropna()
        pd.testing.assert_series_equal(returns, expected_returns)
    
    def test_calculate_returns_empty_series(self):
        """Test return calculation with empty series."""
        empty_series = pd.Series(dtype=float)
        returns = self.risk_engine.calculate_returns(empty_series)
        
        self.assertEqual(len(returns), 0)
        self.assertTrue(returns.empty)
    
    def test_calculate_var_95(self):
        """Test VaR calculation at 95% confidence level."""
        var_95 = self.risk_engine.calculate_var(self.sample_returns, 0.95)
        
        # VaR should be positive and reasonable
        self.assertGreater(var_95, 0)
        self.assertLess(var_95, 1)  # Should be less than 100%
        
        # Check that it's approximately the 5th percentile
        expected_var = abs(np.percentile(self.sample_returns, 5))
        self.assertAlmostEqual(var_95, expected_var, places=4)
    
    def test_calculate_var_99(self):
        """Test VaR calculation at 99% confidence level."""
        var_99 = self.risk_engine.calculate_var(self.sample_returns, 0.99)
        
        self.assertGreater(var_99, 0)
        self.assertLess(var_99, 1)
        
        # 99% VaR should be higher than 95% VaR
        var_95 = self.risk_engine.calculate_var(self.sample_returns, 0.95)
        self.assertGreaterEqual(var_99, var_95)
    
    def test_calculate_expected_shortfall(self):
        """Test Expected Shortfall calculation."""
        es = self.risk_engine.calculate_expected_shortfall(self.sample_returns, 0.95)
        
        self.assertGreater(es, 0)
        
        # Expected Shortfall should be higher than VaR
        var_95 = self.risk_engine.calculate_var(self.sample_returns, 0.95)
        self.assertGreaterEqual(es, var_95)
    
    def test_calculate_volatility_annualized(self):
        """Test annualized volatility calculation."""
        vol = self.risk_engine.calculate_volatility(self.sample_returns, annualize=True)
        
        self.assertGreater(vol, 0)
        
        # Check calculation
        expected_vol = self.sample_returns.std() * np.sqrt(252)
        self.assertAlmostEqual(vol, expected_vol, places=6)
    
    def test_calculate_volatility_daily(self):
        """Test daily volatility calculation."""
        vol_daily = self.risk_engine.calculate_volatility(self.sample_returns, annualize=False)
        vol_annual = self.risk_engine.calculate_volatility(self.sample_returns, annualize=True)
        
        # Annual volatility should be higher (by sqrt(252))
        self.assertAlmostEqual(vol_annual, vol_daily * np.sqrt(252), places=6)
    
    def test_calculate_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        sharpe = self.risk_engine.calculate_sharpe_ratio(self.sample_returns, risk_free_rate=0.02)
        
        # Sharpe ratio should be reasonable
        self.assertGreater(sharpe, -10)
        self.assertLess(sharpe, 10)
        
        # Test with zero volatility
        zero_returns = pd.Series([0.001] * 10)
        sharpe_zero_vol = self.risk_engine.calculate_sharpe_ratio(zero_returns, risk_free_rate=0.02)
        self.assertGreater(sharpe_zero_vol, 0)  # Should be positive since returns > risk-free rate
    
    def test_calculate_max_drawdown(self):
        """Test maximum drawdown calculation."""
        # Create returns with known drawdown
        returns_with_drawdown = pd.Series([0.1, -0.05, -0.1, -0.05, 0.15, 0.05])
        max_dd = self.risk_engine.calculate_max_drawdown(returns_with_drawdown)
        
        self.assertGreater(max_dd, 0)
        self.assertLessEqual(max_dd, 1)  # Cannot be more than 100%
    
    def test_calculate_beta(self):
        """Test beta calculation."""
        portfolio_returns = pd.Series([0.01, -0.02, 0.015, -0.01, 0.02])
        market_returns = pd.Series([0.008, -0.015, 0.012, -0.008, 0.018])
        
        beta = self.risk_engine.calculate_beta(portfolio_returns, market_returns)
        
        # Beta should be reasonable
        self.assertGreater(beta, -5)
        self.assertLess(beta, 5)
        
        # Test with identical series (beta should be 1)
        beta_identical = self.risk_engine.calculate_beta(market_returns, market_returns)
        self.assertAlmostEqual(beta_identical, 1.0, places=2)
    
    def test_calculate_alpha(self):
        """Test alpha calculation."""
        portfolio_returns = pd.Series([0.01, -0.02, 0.015, -0.01, 0.02])
        market_returns = pd.Series([0.008, -0.015, 0.012, -0.008, 0.018])
        
        alpha = self.risk_engine.calculate_alpha(portfolio_returns, market_returns)
        
        # Alpha should be reasonable
        self.assertGreater(alpha, -1)
        self.assertLess(alpha, 1)
    
    def test_calculate_tracking_error(self):
        """Test tracking error calculation."""
        portfolio_returns = pd.Series([0.01, -0.02, 0.015, -0.01, 0.02])
        benchmark_returns = pd.Series([0.008, -0.015, 0.012, -0.008, 0.018])
        
        tracking_error = self.risk_engine.calculate_tracking_error(portfolio_returns, benchmark_returns)
        
        self.assertGreaterEqual(tracking_error, 0)
        self.assertLess(tracking_error, 1)
        
        # Tracking error with identical series should be 0
        te_identical = self.risk_engine.calculate_tracking_error(benchmark_returns, benchmark_returns)
        self.assertAlmostEqual(te_identical, 0.0, places=6)
    
    def test_calculate_information_ratio(self):
        """Test information ratio calculation."""
        portfolio_returns = pd.Series([0.01, -0.02, 0.015, -0.01, 0.02])
        benchmark_returns = pd.Series([0.008, -0.015, 0.012, -0.008, 0.018])
        
        info_ratio = self.risk_engine.calculate_information_ratio(portfolio_returns, benchmark_returns)
        
        # Information ratio should be reasonable
        self.assertGreater(info_ratio, -10)
        self.assertLess(info_ratio, 10)
    
    def test_calculate_portfolio_returns(self):
        """Test portfolio return calculation."""
        # Use sample data
        portfolio_returns = self.risk_engine.calculate_portfolio_returns(
            self.sample_positions, 
            self.sample_prices
        )
        
        self.assertIsInstance(portfolio_returns, pd.Series)
        
        if len(portfolio_returns) > 0:
            # Returns should be reasonable
            self.assertGreater(portfolio_returns.abs().max(), 0)
            self.assertLess(portfolio_returns.abs().max(), 1)  # Less than 100% daily return
    
    def test_calculate_all_risk_metrics(self):
        """Test comprehensive risk metrics calculation."""
        results = self.risk_engine.calculate_all_risk_metrics(
            'TEST_PORTFOLIO',
            self.sample_positions,
            self.sample_prices
        )
        
        self.assertIsInstance(results, RiskResults)
        self.assertEqual(results.portfolio_id, 'TEST_PORTFOLIO')
        self.assertIsInstance(results.calculation_date, datetime)
        
        # Validate all risk metrics
        self.assertGreaterEqual(results.var_95, 0)
        self.assertGreaterEqual(results.var_99, results.var_95)
        self.assertGreaterEqual(results.expected_shortfall, results.var_95)
        self.assertGreaterEqual(results.volatility, 0)
        self.assertGreaterEqual(results.max_drawdown, 0)
        self.assertLessEqual(results.max_drawdown, 1)
    
    def test_stress_test(self):
        """Test stress testing functionality."""
        scenarios = {
            'market_crash': -0.20,
            'volatility_spike': 0.50,
            'interest_shock': -0.10
        }
        
        stress_results = self.risk_engine.stress_test(self.sample_returns, scenarios)
        
        self.assertIsInstance(stress_results, dict)
        self.assertEqual(len(stress_results), len(scenarios))
        
        for scenario_name in scenarios:
            self.assertIn(scenario_name, stress_results)
            result = stress_results[scenario_name]
            self.assertIn('var_95', result)
            self.assertIn('volatility', result)
            self.assertIn('shock_applied', result)
    
    def test_empty_data_handling(self):
        """Test handling of empty data."""
        empty_df = pd.DataFrame()
        empty_series = pd.Series(dtype=float)
        
        # Should not crash with empty data
        results = self.risk_engine.calculate_all_risk_metrics(
            'EMPTY_PORTFOLIO',
            empty_df,
            empty_df
        )
        
        self.assertIsInstance(results, RiskResults)
        self.assertEqual(results.var_95, 0.0)
        self.assertEqual(results.volatility, 0.0)
    
    def test_invalid_data_handling(self):
        """Test handling of invalid data."""
        # Test with NaN values
        invalid_returns = pd.Series([0.01, np.nan, 0.02, -0.01])
        
        # Should handle NaN values gracefully
        var_result = self.risk_engine.calculate_var(invalid_returns)
        self.assertGreaterEqual(var_result, 0)
        
        vol_result = self.risk_engine.calculate_volatility(invalid_returns)
        self.assertGreaterEqual(vol_result, 0)


class TestRiskResultsDataClass(TestBase):
    """Test the RiskResults data class."""
    
    def test_risk_results_creation(self):
        """Test RiskResults object creation."""
        results = RiskResults(
            portfolio_id='TEST_001',
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
        
        self.assertEqual(results.portfolio_id, 'TEST_001')
        self.assertAlmostEqual(results.var_95, 0.025)
        self.assertAlmostEqual(results.sharpe_ratio, 1.35)
    
    def test_risk_results_optional_fields(self):
        """Test optional fields in RiskResults."""
        results = RiskResults(
            portfolio_id='TEST_002',
            calculation_date=datetime.utcnow(),
            var_95=0.03,
            var_99=0.05,
            expected_shortfall=0.06,
            volatility=0.2,
            sharpe_ratio=1.2,
            max_drawdown=0.15,
            beta=0.95,
            alpha=-0.01,
            tracking_error=0.08,
            information_ratio=0.5
        )
        
        self.assertAlmostEqual(results.tracking_error, 0.08)
        self.assertAlmostEqual(results.information_ratio, 0.5)


if __name__ == "__main__":
    unittest.main()