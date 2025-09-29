"""
Real Risk Calculation Engine
Replaces mock implementations with actual financial risk calculations
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import warnings

try:
    from libs.data.snowflake_client import get_snowflake_connector
    from libs.monitoring import log_user_action, get_metrics_collector
except ImportError:
    # Fallback for testing
    get_snowflake_connector = None
    log_user_action = lambda *args, **kwargs: None
    get_metrics_collector = lambda: None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=RuntimeWarning)


class RiskMetric(Enum):
    """Risk metric types."""
    VAR_95 = "var_95"
    VAR_99 = "var_99" 
    EXPECTED_SHORTFALL = "expected_shortfall"
    VOLATILITY = "volatility"
    SHARPE_RATIO = "sharpe_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    BETA = "beta"
    ALPHA = "alpha"
    TRACKING_ERROR = "tracking_error"
    INFORMATION_RATIO = "information_ratio"


@dataclass
class RiskResults:
    """Container for risk calculation results."""
    portfolio_id: str
    calculation_date: datetime
    var_95: float
    var_99: float
    expected_shortfall: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    beta: float
    alpha: float
    tracking_error: float = None
    information_ratio: float = None
    metrics_metadata: Dict[str, Any] = None


class RiskCalculationEngine:
    """Advanced risk calculation engine with real financial models."""
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
        self.metrics_collector = get_metrics_collector()
        
    def calculate_returns(self, prices: pd.Series, method: str = 'simple') -> pd.Series:
        """Calculate returns from price series."""
        if len(prices) < 2:
            return pd.Series(dtype=float)
        
        if method == 'simple':
            returns = prices.pct_change().dropna()
        elif method == 'log':
            returns = np.log(prices / prices.shift(1)).dropna()
        else:
            raise ValueError(f"Unknown return calculation method: {method}")
        
        return returns
    
    def calculate_portfolio_returns(self, positions: pd.DataFrame, 
                                  price_data: pd.DataFrame) -> pd.Series:
        """Calculate portfolio returns based on positions and price data."""
        try:
            # Ensure we have required columns
            required_pos_cols = ['symbol', 'quantity', 'weight']
            required_price_cols = ['symbol', 'trading_date', 'close_price']
            
            if not all(col in positions.columns for col in required_pos_cols):
                raise ValueError(f"Position data missing required columns: {required_pos_cols}")
            
            if not all(col in price_data.columns for col in required_price_cols):
                raise ValueError(f"Price data missing required columns: {required_price_cols}")
            
            # Pivot price data to have symbols as columns
            price_pivot = price_data.pivot(index='trading_date', columns='symbol', values='close_price')
            price_pivot = price_pivot.sort_index()
            
            # Calculate individual asset returns
            asset_returns = price_pivot.pct_change().dropna()
            
            # Get weights for assets in our portfolio
            weights = positions.set_index('symbol')['weight'].to_dict()
            
            # Calculate portfolio returns
            portfolio_returns = pd.Series(index=asset_returns.index, dtype=float)
            
            for date, returns_row in asset_returns.iterrows():
                weighted_return = 0.0
                total_weight = 0.0
                
                for symbol, return_val in returns_row.items():
                    if symbol in weights and not pd.isna(return_val):
                        weight = weights[symbol]
                        weighted_return += weight * return_val
                        total_weight += weight
                
                # Normalize if total weight != 1
                if total_weight > 0:
                    portfolio_returns.loc[date] = weighted_return / total_weight if total_weight != 1 else weighted_return
                else:
                    portfolio_returns.loc[date] = 0.0
            
            return portfolio_returns.dropna()
            
        except Exception as e:
            logger.error(f"Error calculating portfolio returns: {e}")
            return pd.Series(dtype=float)
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk using historical simulation."""
        if len(returns) == 0:
            return 0.0
        
        try:
            # Sort returns in ascending order
            sorted_returns = returns.sort_values()
            
            # Calculate percentile
            percentile = (1 - confidence_level) * 100
            var_value = np.percentile(sorted_returns, percentile)
            
            # VaR is typically reported as a positive number
            return abs(var_value)
            
        except Exception as e:
            logger.error(f"Error calculating VaR: {e}")
            return 0.0
    
    def calculate_expected_shortfall(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Expected Shortfall (Conditional VaR)."""
        if len(returns) == 0:
            return 0.0
        
        try:
            var_value = self.calculate_var(returns, confidence_level)
            
            # Get returns worse than VaR
            tail_returns = returns[returns <= -var_value]
            
            if len(tail_returns) == 0:
                return var_value
            
            # Expected Shortfall is the mean of tail losses
            expected_shortfall = abs(tail_returns.mean())
            
            return expected_shortfall
            
        except Exception as e:
            logger.error(f"Error calculating Expected Shortfall: {e}")
            return 0.0
    
    def calculate_volatility(self, returns: pd.Series, annualize: bool = True) -> float:
        """Calculate volatility (standard deviation of returns)."""
        if len(returns) == 0:
            return 0.0
        
        try:
            vol = returns.std()
            
            # Annualize assuming 252 trading days
            if annualize:
                vol = vol * np.sqrt(252)
            
            return vol
            
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return 0.0
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = None) -> float:
        """Calculate Sharpe ratio."""
        if len(returns) == 0:
            return 0.0
        
        try:
            risk_free = risk_free_rate or self.risk_free_rate
            
            # Annualize returns
            annual_return = returns.mean() * 252
            annual_volatility = self.calculate_volatility(returns, annualize=True)
            
            if annual_volatility == 0:
                return 0.0
            
            sharpe = (annual_return - risk_free) / annual_volatility
            
            return sharpe
            
        except Exception as e:
            logger.error(f"Error calculating Sharpe ratio: {e}")
            return 0.0
    
    def calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown."""
        if len(returns) == 0:
            return 0.0
        
        try:
            # Calculate cumulative returns
            cumulative_returns = (1 + returns).cumprod()
            
            # Calculate running maximum
            running_max = cumulative_returns.expanding().max()
            
            # Calculate drawdown
            drawdown = (cumulative_returns - running_max) / running_max
            
            # Maximum drawdown is the minimum (most negative) drawdown
            max_dd = abs(drawdown.min())
            
            return max_dd
            
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {e}")
            return 0.0
    
    def calculate_beta(self, portfolio_returns: pd.Series, 
                      market_returns: pd.Series) -> float:
        """Calculate portfolio beta relative to market."""
        if len(portfolio_returns) == 0 or len(market_returns) == 0:
            return 1.0  # Default beta
        
        try:
            # Align the series by date
            aligned_data = pd.DataFrame({
                'portfolio': portfolio_returns,
                'market': market_returns
            }).dropna()
            
            if len(aligned_data) < 2:
                return 1.0
            
            # Calculate covariance and variance
            covariance = np.cov(aligned_data['portfolio'], aligned_data['market'])[0, 1]
            market_variance = np.var(aligned_data['market'])
            
            if market_variance == 0:
                return 1.0
            
            beta = covariance / market_variance
            
            return beta
            
        except Exception as e:
            logger.error(f"Error calculating beta: {e}")
            return 1.0
    
    def calculate_alpha(self, portfolio_returns: pd.Series, 
                       market_returns: pd.Series, beta: float = None) -> float:
        """Calculate portfolio alpha."""
        if len(portfolio_returns) == 0 or len(market_returns) == 0:
            return 0.0
        
        try:
            # Calculate beta if not provided
            if beta is None:
                beta = self.calculate_beta(portfolio_returns, market_returns)
            
            # Annualize returns
            portfolio_annual_return = portfolio_returns.mean() * 252
            market_annual_return = market_returns.mean() * 252
            
            # Alpha = Portfolio Return - (Risk Free Rate + Beta * (Market Return - Risk Free Rate))
            alpha = portfolio_annual_return - (self.risk_free_rate + beta * (market_annual_return - self.risk_free_rate))
            
            return alpha
            
        except Exception as e:
            logger.error(f"Error calculating alpha: {e}")
            return 0.0
    
    def calculate_tracking_error(self, portfolio_returns: pd.Series, 
                               benchmark_returns: pd.Series) -> float:
        """Calculate tracking error relative to benchmark."""
        if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
            return 0.0
        
        try:
            # Align the series
            aligned_data = pd.DataFrame({
                'portfolio': portfolio_returns,
                'benchmark': benchmark_returns
            }).dropna()
            
            if len(aligned_data) < 2:
                return 0.0
            
            # Calculate excess returns
            excess_returns = aligned_data['portfolio'] - aligned_data['benchmark']
            
            # Tracking error is annualized standard deviation of excess returns
            tracking_error = excess_returns.std() * np.sqrt(252)
            
            return tracking_error
            
        except Exception as e:
            logger.error(f"Error calculating tracking error: {e}")
            return 0.0
    
    def calculate_information_ratio(self, portfolio_returns: pd.Series,
                                  benchmark_returns: pd.Series) -> float:
        """Calculate information ratio."""
        if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
            return 0.0
        
        try:
            # Align the series
            aligned_data = pd.DataFrame({
                'portfolio': portfolio_returns,
                'benchmark': benchmark_returns
            }).dropna()
            
            if len(aligned_data) < 2:
                return 0.0
            
            # Calculate excess returns
            excess_returns = aligned_data['portfolio'] - aligned_data['benchmark']
            
            # Information ratio = mean excess return / tracking error
            mean_excess_return = excess_returns.mean() * 252  # Annualize
            tracking_error = self.calculate_tracking_error(portfolio_returns, benchmark_returns)
            
            if tracking_error == 0:
                return 0.0
            
            info_ratio = mean_excess_return / tracking_error
            
            return info_ratio
            
        except Exception as e:
            logger.error(f"Error calculating information ratio: {e}")
            return 0.0
    
    def calculate_all_risk_metrics(self, portfolio_id: str, positions: pd.DataFrame,
                                 price_data: pd.DataFrame, 
                                 market_data: pd.DataFrame = None) -> RiskResults:
        """Calculate all risk metrics for a portfolio."""
        start_time = datetime.utcnow()
        
        try:
            # Calculate portfolio returns
            portfolio_returns = self.calculate_portfolio_returns(positions, price_data)
            
            if len(portfolio_returns) == 0:
                logger.warning(f"No portfolio returns calculated for {portfolio_id}")
                return self._create_empty_results(portfolio_id)
            
            # Calculate basic risk metrics
            var_95 = self.calculate_var(portfolio_returns, 0.95)
            var_99 = self.calculate_var(portfolio_returns, 0.99)
            expected_shortfall = self.calculate_expected_shortfall(portfolio_returns, 0.95)
            volatility = self.calculate_volatility(portfolio_returns)
            sharpe_ratio = self.calculate_sharpe_ratio(portfolio_returns)
            max_drawdown = self.calculate_max_drawdown(portfolio_returns)
            
            # Calculate market-relative metrics if market data available
            beta = 1.0
            alpha = 0.0
            tracking_error = None
            information_ratio = None
            
            if market_data is not None and len(market_data) > 0:
                market_returns = self.calculate_returns(market_data['close_price'])
                if len(market_returns) > 0:
                    beta = self.calculate_beta(portfolio_returns, market_returns)
                    alpha = self.calculate_alpha(portfolio_returns, market_returns, beta)
                    tracking_error = self.calculate_tracking_error(portfolio_returns, market_returns)
                    information_ratio = self.calculate_information_ratio(portfolio_returns, market_returns)
            
            # Create results
            results = RiskResults(
                portfolio_id=portfolio_id,
                calculation_date=datetime.utcnow(),
                var_95=var_95,
                var_99=var_99,
                expected_shortfall=expected_shortfall,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                beta=beta,
                alpha=alpha,
                tracking_error=tracking_error,
                information_ratio=information_ratio,
                metrics_metadata={
                    'calculation_duration': (datetime.utcnow() - start_time).total_seconds(),
                    'return_observations': len(portfolio_returns),
                    'start_date': portfolio_returns.index.min().isoformat() if len(portfolio_returns) > 0 else None,
                    'end_date': portfolio_returns.index.max().isoformat() if len(portfolio_returns) > 0 else None
                }
            )
            
            # Record metrics
            if self.metrics_collector:
                duration = (datetime.utcnow() - start_time).total_seconds()
                self.metrics_collector.record_calculation_time('risk_metrics', duration)
                self.metrics_collector.record_calculation_count('risk_metrics')
            
            logger.info(f"Risk metrics calculated for portfolio {portfolio_id}: "
                       f"VaR95={var_95:.4f}, Vol={volatility:.4f}, Sharpe={sharpe_ratio:.4f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics for portfolio {portfolio_id}: {e}")
            return self._create_empty_results(portfolio_id)
    
    def _create_empty_results(self, portfolio_id: str) -> RiskResults:
        """Create empty risk results."""
        return RiskResults(
            portfolio_id=portfolio_id,
            calculation_date=datetime.utcnow(),
            var_95=0.0,
            var_99=0.0,
            expected_shortfall=0.0,
            volatility=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            beta=1.0,
            alpha=0.0
        )
    
    def stress_test(self, portfolio_returns: pd.Series, 
                   scenarios: Dict[str, float]) -> Dict[str, float]:
        """Perform stress testing on portfolio."""
        results = {}
        
        for scenario_name, shock in scenarios.items():
            try:
                # Apply shock to returns
                shocked_returns = portfolio_returns * (1 + shock)
                
                # Calculate metrics under stress
                stressed_var = self.calculate_var(shocked_returns, 0.95)
                stressed_vol = self.calculate_volatility(shocked_returns)
                
                results[scenario_name] = {
                    'var_95': stressed_var,
                    'volatility': stressed_vol,
                    'max_drawdown': self.calculate_max_drawdown(shocked_returns),
                    'shock_applied': shock
                }
                
            except Exception as e:
                logger.error(f"Error in stress test scenario {scenario_name}: {e}")
                results[scenario_name] = {
                    'var_95': 0.0,
                    'volatility': 0.0,
                    'max_drawdown': 0.0,
                    'shock_applied': shock,
                    'error': str(e)
                }
        
        return results


# Global instance
_risk_engine = None

def get_risk_engine() -> RiskCalculationEngine:
    """Get global risk calculation engine."""
    global _risk_engine
    if _risk_engine is None:
        _risk_engine = RiskCalculationEngine()
    return _risk_engine


# Convenience functions
def calculate_portfolio_risk(portfolio_id: str, positions: pd.DataFrame, 
                           price_data: pd.DataFrame) -> RiskResults:
    """Calculate portfolio risk metrics."""
    engine = get_risk_engine()
    return engine.calculate_all_risk_metrics(portfolio_id, positions, price_data)


def perform_stress_test(portfolio_returns: pd.Series, 
                       scenarios: Dict[str, float] = None) -> Dict[str, float]:
    """Perform stress testing."""
    if scenarios is None:
        scenarios = {
            'market_crash': -0.20,  # 20% market drop
            'high_volatility': 0.50,  # 50% volatility increase
            'interest_rate_shock': -0.10,  # 10% interest rate shock
            'currency_crisis': -0.15,  # 15% currency shock
        }
    
    engine = get_risk_engine()
    return engine.stress_test(portfolio_returns, scenarios)