"""
Real Market Data Integration
Replaces mock market data with actual financial data sources
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import requests
import time
from dataclasses import dataclass
from enum import Enum

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from config import get_config
    from libs.monitoring import log_user_action, get_metrics_collector
    from libs.storage import CacheManager
    from libs.data.snowflake_client import get_snowflake_connector
except ImportError:
    # Fallback imports for testing
    get_config = lambda: {}
    log_user_action = lambda *args, **kwargs: None
    get_metrics_collector = lambda: None
    CacheManager = None
    get_snowflake_connector = lambda: None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Market data sources."""
    ALPHA_VANTAGE = "alpha_vantage"
    YAHOO_FINANCE = "yahoo_finance" 
    BLOOMBERG = "bloomberg"
    REFINITIV = "refinitiv"
    SNOWFLAKE = "snowflake"
    MOCK = "mock"


@dataclass
class MarketDataConfig:
    """Configuration for market data sources."""
    primary_source: DataSource
    fallback_sources: List[DataSource]
    cache_ttl: int = 3600  # 1 hour
    rate_limit_delay: float = 0.2  # seconds between API calls
    api_keys: Dict[str, str] = None


class MarketDataProvider:
    """Unified market data provider with multiple data sources."""
    
    def __init__(self, config: MarketDataConfig = None):
        self.config = config or self._get_default_config()
        self.cache_manager = CacheManager() if CacheManager else None
        self.metrics_collector = get_metrics_collector()
        self.snowflake_connector = get_snowflake_connector()
        
        # Rate limiting
        self._last_request_time = 0
        
    def _get_default_config(self) -> MarketDataConfig:
        """Get default market data configuration."""
        app_config = get_config()
        market_config = app_config.get('market_data', {})
        
        return MarketDataConfig(
            primary_source=DataSource(market_config.get('primary_source', 'alpha_vantage')),
            fallback_sources=[DataSource(s) for s in market_config.get('fallback_sources', ['yahoo_finance', 'mock'])],
            cache_ttl=market_config.get('cache_ttl', 3600),
            rate_limit_delay=market_config.get('rate_limit_delay', 0.2),
            api_keys={
                'alpha_vantage': os.getenv('ALPHA_VANTAGE_API_KEY') or market_config.get('alpha_vantage_key', ''),
                'bloomberg': os.getenv('BLOOMBERG_API_KEY') or market_config.get('bloomberg_key', ''),
                'refinitiv': os.getenv('REFINITIV_API_KEY') or market_config.get('refinitiv_key', '')
            }
        )
    
    def _rate_limit(self):
        """Apply rate limiting between API calls."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self.config.rate_limit_delay:
            sleep_time = self.config.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def _get_cache_key(self, data_type: str, symbol: str, start_date: str, end_date: str) -> str:
        """Generate cache key for market data."""
        return f"market_data:{data_type}:{symbol}:{start_date}:{end_date}"
    
    def get_daily_prices(self, symbol: str, start_date: str, end_date: str = None,
                        use_cache: bool = True) -> pd.DataFrame:
        """Get daily price data for a symbol."""
        end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        cache_key = self._get_cache_key('daily_prices', symbol, start_date, end_date)
        
        # Check cache first
        if use_cache and self.cache_manager:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data is not None:
                logger.info(f"Retrieved cached price data for {symbol}")
                return pd.DataFrame(cached_data)
        
        # Try data sources in order
        sources_to_try = [self.config.primary_source] + self.config.fallback_sources
        
        for source in sources_to_try:
            try:
                logger.info(f"Fetching {symbol} price data from {source.value}")
                
                if source == DataSource.SNOWFLAKE:
                    data = self._get_prices_from_snowflake(symbol, start_date, end_date)
                elif source == DataSource.ALPHA_VANTAGE:
                    data = self._get_prices_from_alpha_vantage(symbol, start_date, end_date)
                elif source == DataSource.YAHOO_FINANCE:
                    data = self._get_prices_from_yahoo(symbol, start_date, end_date)
                elif source == DataSource.BLOOMBERG:
                    data = self._get_prices_from_bloomberg(symbol, start_date, end_date)
                elif source == DataSource.REFINITIV:
                    data = self._get_prices_from_refinitiv(symbol, start_date, end_date)
                else:
                    data = self._get_mock_prices(symbol, start_date, end_date)
                
                if not data.empty:
                    # Cache the result
                    if use_cache and self.cache_manager:
                        self.cache_manager.set(cache_key, data.to_dict('records'), self.config.cache_ttl)
                    
                    # Record metrics
                    if self.metrics_collector:
                        self.metrics_collector.record_data_fetch('market_data', len(data))
                    
                    logger.info(f"Successfully retrieved {len(data)} price records for {symbol} from {source.value}")
                    return data
                
            except Exception as e:
                logger.warning(f"Failed to get data from {source.value}: {e}")
                continue
        
        # If all sources fail, return empty DataFrame
        logger.error(f"All data sources failed for {symbol}")
        return pd.DataFrame(columns=['trading_date', 'symbol', 'open_price', 'high_price', 
                                   'low_price', 'close_price', 'volume', 'adjusted_close'])
    
    def _get_prices_from_snowflake(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get prices from Snowflake database."""
        if not self.snowflake_connector:
            raise Exception("Snowflake connector not available")
        
        return self.snowflake_connector.get_market_data(start_date, end_date, [symbol])
    
    def _get_prices_from_alpha_vantage(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get prices from Alpha Vantage API."""
        api_key = self.config.api_keys.get('alpha_vantage')
        if not api_key:
            raise Exception("Alpha Vantage API key not configured")
        
        self._rate_limit()
        
        # Alpha Vantage daily adjusted endpoint
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': symbol,
            'outputsize': 'full',
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'Error Message' in data:
            raise Exception(f"Alpha Vantage error: {data['Error Message']}")
        
        if 'Note' in data:
            raise Exception(f"Alpha Vantage rate limit: {data['Note']}")
        
        time_series = data.get('Time Series (Daily)', {})
        if not time_series:
            raise Exception("No time series data returned from Alpha Vantage")
        
        # Convert to DataFrame
        records = []
        for date_str, values in time_series.items():
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Filter by date range
            if start_date and date_obj < datetime.strptime(start_date, '%Y-%m-%d'):
                continue
            if end_date and date_obj > datetime.strptime(end_date, '%Y-%m-%d'):
                continue
            
            records.append({
                'trading_date': date_obj,
                'symbol': symbol,
                'open_price': float(values['1. open']),
                'high_price': float(values['2. high']),
                'low_price': float(values['3. low']),
                'close_price': float(values['4. close']),
                'adjusted_close': float(values['5. adjusted close']),
                'volume': int(values['6. volume'])
            })
        
        df = pd.DataFrame(records)
        return df.sort_values('trading_date').reset_index(drop=True)
    
    def _get_prices_from_yahoo(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get prices from Yahoo Finance (using yfinance library if available)."""
        try:
            import yfinance as yf
        except ImportError:
            raise Exception("yfinance library not installed")
        
        self._rate_limit()
        
        # Download data
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date, auto_adjust=False)
        
        if data.empty:
            raise Exception(f"No data returned from Yahoo Finance for {symbol}")
        
        # Convert to standard format
        df = data.reset_index()
        df = df.rename(columns={
            'Date': 'trading_date',
            'Open': 'open_price',
            'High': 'high_price', 
            'Low': 'low_price',
            'Close': 'close_price',
            'Adj Close': 'adjusted_close',
            'Volume': 'volume'
        })
        
        df['symbol'] = symbol
        df = df[['trading_date', 'symbol', 'open_price', 'high_price', 
                'low_price', 'close_price', 'volume', 'adjusted_close']]
        
        return df
    
    def _get_prices_from_bloomberg(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get prices from Bloomberg API (placeholder - requires Bloomberg Terminal/API license)."""
        # This would require Bloomberg API setup
        raise Exception("Bloomberg API integration not implemented - requires Bloomberg Terminal license")
    
    def _get_prices_from_refinitiv(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get prices from Refinitiv API (placeholder)."""
        # This would require Refinitiv Eikon/Workspace API setup
        raise Exception("Refinitiv API integration not implemented - requires Refinitiv license")
    
    def _get_mock_prices(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Generate mock price data for testing."""
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Generate business days
        dates = pd.bdate_range(start_dt, end_dt)
        
        # Generate mock prices with random walk
        np.random.seed(hash(symbol) % (2**32))  # Deterministic seed based on symbol
        
        base_price = 100.0 + (hash(symbol) % 1000) / 10  # Base price varies by symbol
        returns = np.random.normal(0.001, 0.02, len(dates))  # Daily returns
        
        prices = [base_price]
        for return_val in returns[1:]:
            prices.append(prices[-1] * (1 + return_val))
        
        records = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            # Generate OHLC from close price
            daily_vol = abs(np.random.normal(0, 0.01))
            high_price = price * (1 + daily_vol/2)
            low_price = price * (1 - daily_vol/2)
            open_price = prices[i-1] if i > 0 else price
            
            records.append({
                'trading_date': date,
                'symbol': symbol,
                'open_price': round(open_price, 2),
                'high_price': round(high_price, 2),
                'low_price': round(low_price, 2),
                'close_price': round(price, 2),
                'adjusted_close': round(price, 2),  # Assume no adjustments for mock data
                'volume': int(np.random.uniform(100000, 10000000))
            })
        
        return pd.DataFrame(records)
    
    def get_multiple_symbols(self, symbols: List[str], start_date: str, 
                           end_date: str = None) -> pd.DataFrame:
        """Get price data for multiple symbols."""
        all_data = []
        
        for symbol in symbols:
            try:
                symbol_data = self.get_daily_prices(symbol, start_date, end_date)
                if not symbol_data.empty:
                    all_data.append(symbol_data)
            except Exception as e:
                logger.error(f"Failed to get data for {symbol}: {e}")
                continue
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        else:
            return pd.DataFrame(columns=['trading_date', 'symbol', 'open_price', 'high_price', 
                                       'low_price', 'close_price', 'volume', 'adjusted_close'])
    
    def get_index_data(self, index_symbol: str = "^GSPC", start_date: str = None, 
                      end_date: str = None) -> pd.DataFrame:
        """Get market index data (default S&P 500)."""
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        return self.get_daily_prices(index_symbol, start_date, end_date)
    
    def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """Get latest price for a symbol."""
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        data = self.get_daily_prices(symbol, yesterday, today)
        
        if data.empty:
            return {}
        
        latest_row = data.iloc[-1]
        return {
            'symbol': symbol,
            'price': latest_row['close_price'],
            'date': latest_row['trading_date'].strftime('%Y-%m-%d') if pd.notnull(latest_row['trading_date']) else today,
            'change': latest_row['close_price'] - latest_row['open_price'] if pd.notnull(latest_row['open_price']) else 0,
            'change_percent': ((latest_row['close_price'] - latest_row['open_price']) / latest_row['open_price'] * 100) 
                             if pd.notnull(latest_row['open_price']) and latest_row['open_price'] != 0 else 0,
            'volume': int(latest_row['volume']) if pd.notnull(latest_row['volume']) else 0
        }


# Global instance
_market_data_provider = None

def get_market_data_provider() -> MarketDataProvider:
    """Get global market data provider instance."""
    global _market_data_provider
    if _market_data_provider is None:
        _market_data_provider = MarketDataProvider()
    return _market_data_provider


# Convenience functions
def get_stock_prices(symbol: str, start_date: str, end_date: str = None) -> pd.DataFrame:
    """Get stock price data."""
    provider = get_market_data_provider()
    return provider.get_daily_prices(symbol, start_date, end_date)

def get_multiple_stock_prices(symbols: List[str], start_date: str, end_date: str = None) -> pd.DataFrame:
    """Get price data for multiple stocks."""
    provider = get_market_data_provider()
    return provider.get_multiple_symbols(symbols, start_date, end_date)

def get_market_index(start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """Get S&P 500 index data."""
    provider = get_market_data_provider()
    return provider.get_index_data("^GSPC", start_date, end_date)

def get_current_price(symbol: str) -> Dict[str, Any]:
    """Get current price for a symbol."""
    provider = get_market_data_provider()
    return provider.get_latest_price(symbol)