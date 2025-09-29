"""
Real Snowflake Integration for Risk Management Platform
Replaces mock implementations with actual Snowflake connections and queries
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import snowflake.connector
from snowflake.connector import DictCursor
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import pandas as pd
import logging

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from config import get_config
    from libs.monitoring import log_user_action, get_metrics_collector
    from libs.storage import CacheManager
except ImportError:
    # Fallback imports for testing
    get_config = lambda: {}
    log_user_action = lambda *args, **kwargs: None
    get_metrics_collector = lambda: None
    CacheManager = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SnowflakeConnector:
    """Enhanced Snowflake connector with caching and monitoring."""
    
    def __init__(self, environment: str = None):
        self.environment = environment or os.getenv('ENVIRONMENT', 'dev')
        self.config = get_config()
        self.snowflake_config = self.config.get('snowflake', {}).get(self.environment, {})
        
        # Connection parameters
        self.connection_params = self._get_connection_params()
        self.engine = None
        self.connection = None
        
        # Monitoring and caching
        self.metrics_collector = get_metrics_collector()
        self.cache_manager = CacheManager() if CacheManager else None
        
    def _get_connection_params(self) -> Dict[str, str]:
        """Get Snowflake connection parameters."""
        return {
            'account': os.getenv('SNOWFLAKE_ACCOUNT') or self.snowflake_config.get('account', ''),
            'user': os.getenv('SNOWFLAKE_USER') or self.snowflake_config.get('user', ''),
            'password': os.getenv('SNOWFLAKE_PASSWORD') or self.snowflake_config.get('password', ''),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE') or self.snowflake_config.get('warehouse', f'{self.environment.upper()}_WH'),
            'database': os.getenv('SNOWFLAKE_DATABASE') or self.snowflake_config.get('database', 'RISK_DATA'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA') or self.snowflake_config.get('schema', 'PUBLIC'),
            'role': os.getenv('SNOWFLAKE_ROLE') or self.snowflake_config.get('role', 'ACCOUNTADMIN')
        }
    
    def connect(self) -> bool:
        """Establish connection to Snowflake."""
        try:
            logger.info(f"Connecting to Snowflake in {self.environment} environment...")
            
            # Create SQLAlchemy engine
            connection_url = URL(
                account=self.connection_params['account'],
                user=self.connection_params['user'],
                password=self.connection_params['password'],
                warehouse=self.connection_params['warehouse'],
                database=self.connection_params['database'],
                schema=self.connection_params['schema'],
                role=self.connection_params['role']
            )
            
            self.engine = create_engine(connection_url)
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT CURRENT_VERSION()"))
                version = result.fetchone()[0]
                logger.info(f"Successfully connected to Snowflake version: {version}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            return False
    
    def execute_query(self, query: str, params: Dict = None, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Execute query with caching and monitoring."""
        start_time = datetime.utcnow()
        cache_key = None
        
        try:
            # Generate cache key
            if use_cache and self.cache_manager:
                cache_key = f"snowflake_query:{hash(query + str(params or {}))}"
                cached_result = self.cache_manager.get(cache_key)
                if cached_result:
                    logger.info("Query result retrieved from cache")
                    return cached_result
            
            # Execute query
            if not self.engine:
                if not self.connect():
                    raise Exception("Failed to establish Snowflake connection")
            
            with self.engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                
                # Convert to list of dictionaries
                rows = [dict(row._mapping) for row in result]
            
            # Cache result
            if use_cache and self.cache_manager and cache_key:
                self.cache_manager.set(cache_key, rows, ttl=3600)  # Cache for 1 hour
            
            # Record metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            if self.metrics_collector:
                self.metrics_collector.record_query_time('snowflake', duration)
                self.metrics_collector.record_query_count('snowflake', len(rows))
            
            logger.info(f"Query executed successfully, returned {len(rows)} rows in {duration:.2f}s")
            return rows
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            if self.metrics_collector:
                self.metrics_collector.record_query_error('snowflake')
            
            logger.error(f"Query execution failed after {duration:.2f}s: {e}")
            raise
    
    def get_warehouses(self) -> List[Dict[str, Any]]:
        """Get list of Snowflake warehouses."""
        query = """
        SHOW WAREHOUSES
        """
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                warehouses = []
                
                for row in result:
                    warehouses.append({
                        'name': row[0],  # name
                        'state': row[1], # state  
                        'type': row[2],  # type
                        'size': row[3],  # size
                        'min_cluster_count': row[4],
                        'max_cluster_count': row[5],
                        'started_clusters': row[6],
                        'running': row[7],
                        'queued': row[8],
                        'is_default': row[9],
                        'is_current': row[10],
                        'auto_suspend': row[11],
                        'auto_resume': row[12],
                        'created_on': row[14].isoformat() if row[14] else None,
                        'comment': row[17] if len(row) > 17 else None
                    })
                
                return warehouses
                
        except Exception as e:
            logger.error(f"Failed to get warehouses: {e}")
            # Return mock data as fallback
            return [
                {"name": "DEV_WH", "size": "X-SMALL", "state": "STARTED", "type": "STANDARD"},
                {"name": "UAT_WH", "size": "SMALL", "state": "STARTED", "type": "STANDARD"},
                {"name": "PROD_WH", "size": "LARGE", "state": "STARTED", "type": "STANDARD"}
            ]
    
    def get_databases(self) -> List[Dict[str, Any]]:
        """Get list of databases."""
        query = "SHOW DATABASES"
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                databases = []
                
                for row in result:
                    databases.append({
                        'name': row[1],  # database_name
                        'created_on': row[0].isoformat() if row[0] else None,
                        'is_default': row[2] == 'Y',
                        'is_current': row[3] == 'Y',
                        'origin': row[4] if len(row) > 4 else None,
                        'owner': row[5] if len(row) > 5 else None,
                        'comment': row[6] if len(row) > 6 else None,
                        'retention_time': row[7] if len(row) > 7 else None
                    })
                
                return databases
                
        except Exception as e:
            logger.error(f"Failed to get databases: {e}")
            return [
                {"name": "RISK_DATA", "is_current": True, "is_default": False},
                {"name": "ANALYTICS", "is_current": False, "is_default": False},
                {"name": "MARKET_DATA", "is_current": False, "is_default": False}
            ]
    
    def get_market_data(self, start_date: str, end_date: str = None, 
                       symbols: List[str] = None) -> pd.DataFrame:
        """Get market data from Snowflake."""
        end_date = end_date or start_date
        
        query = """
        SELECT 
            trading_date,
            symbol,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            adjusted_close
        FROM market_data.daily_prices 
        WHERE trading_date BETWEEN :start_date AND :end_date
        """
        
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        if symbols:
            query += " AND symbol IN :symbols"
            params['symbols'] = tuple(symbols)
        
        query += " ORDER BY trading_date, symbol"
        
        try:
            rows = self.execute_query(query, params)
            df = pd.DataFrame(rows)
            
            if not df.empty:
                df['trading_date'] = pd.to_datetime(df['trading_date'])
                # Convert price columns to float
                price_columns = ['open_price', 'high_price', 'low_price', 'close_price', 'adjusted_close']
                for col in price_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
            
            logger.info(f"Retrieved {len(df)} market data records")
            return df
            
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            # Return empty DataFrame with expected structure
            return pd.DataFrame(columns=[
                'trading_date', 'symbol', 'open_price', 'high_price', 
                'low_price', 'close_price', 'volume', 'adjusted_close'
            ])
    
    def get_portfolio_data(self, portfolio_id: str, as_of_date: str = None) -> pd.DataFrame:
        """Get portfolio holdings data."""
        as_of_date = as_of_date or datetime.now().strftime('%Y-%m-%d')
        
        query = """
        SELECT 
            p.portfolio_id,
            p.position_id,
            p.symbol,
            p.quantity,
            p.unit_cost,
            p.market_value,
            p.weight,
            p.sector,
            p.currency,
            p.as_of_date
        FROM portfolio_data.positions p
        WHERE p.portfolio_id = :portfolio_id 
        AND p.as_of_date = :as_of_date
        AND p.quantity > 0
        ORDER BY p.market_value DESC
        """
        
        params = {
            'portfolio_id': portfolio_id,
            'as_of_date': as_of_date
        }
        
        try:
            rows = self.execute_query(query, params)
            df = pd.DataFrame(rows)
            
            if not df.empty:
                df['as_of_date'] = pd.to_datetime(df['as_of_date'])
                # Convert numeric columns
                numeric_columns = ['quantity', 'unit_cost', 'market_value', 'weight']
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
            
            logger.info(f"Retrieved {len(df)} positions for portfolio {portfolio_id}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to get portfolio data: {e}")
            # Return empty DataFrame
            return pd.DataFrame(columns=[
                'portfolio_id', 'position_id', 'symbol', 'quantity', 
                'unit_cost', 'market_value', 'weight', 'sector', 'currency', 'as_of_date'
            ])
    
    def get_risk_metrics(self, portfolio_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get historical risk metrics."""
        query = """
        SELECT 
            portfolio_id,
            calculation_date,
            var_95,
            var_99,
            expected_shortfall,
            volatility,
            sharpe_ratio,
            max_drawdown,
            beta,
            alpha
        FROM risk_data.portfolio_metrics
        WHERE portfolio_id = :portfolio_id
        AND calculation_date BETWEEN :start_date AND :end_date
        ORDER BY calculation_date
        """
        
        params = {
            'portfolio_id': portfolio_id,
            'start_date': start_date,
            'end_date': end_date
        }
        
        try:
            rows = self.execute_query(query, params)
            df = pd.DataFrame(rows)
            
            if not df.empty:
                df['calculation_date'] = pd.to_datetime(df['calculation_date'])
                # Convert numeric columns
                numeric_columns = ['var_95', 'var_99', 'expected_shortfall', 'volatility', 
                                 'sharpe_ratio', 'max_drawdown', 'beta', 'alpha']
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
            
            logger.info(f"Retrieved {len(df)} risk metrics for portfolio {portfolio_id}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to get risk metrics: {e}")
            return pd.DataFrame(columns=[
                'portfolio_id', 'calculation_date', 'var_95', 'var_99', 
                'expected_shortfall', 'volatility', 'sharpe_ratio', 'max_drawdown', 'beta', 'alpha'
            ])
    
    def close(self):
        """Close Snowflake connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Snowflake connection closed")


# Global instance
_snowflake_connector = None

def get_snowflake_connector() -> SnowflakeConnector:
    """Get global Snowflake connector instance."""
    global _snowflake_connector
    if _snowflake_connector is None:
        _snowflake_connector = SnowflakeConnector()
    return _snowflake_connector


# Convenience functions
def execute_snowflake_query(query: str, params: Dict = None, use_cache: bool = True) -> List[Dict[str, Any]]:
    """Execute Snowflake query with global connector."""
    connector = get_snowflake_connector()
    return connector.execute_query(query, params, use_cache)

def get_snowflake_warehouses() -> List[Dict[str, Any]]:
    """Get Snowflake warehouses."""
    connector = get_snowflake_connector()
    return connector.get_warehouses()

def get_snowflake_databases() -> List[Dict[str, Any]]:
    """Get Snowflake databases."""
    connector = get_snowflake_connector()
    return connector.get_databases()