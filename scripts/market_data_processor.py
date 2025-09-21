"""
Market data processing script for Airflow jobs.
Handles downloading and processing of market data from various sources.
"""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from libs.business.risk_management import MarketDataProcessor
from libs.db import execute_update, execute_query, get_session
from libs.cloud import upload_to_s3

logger = logging.getLogger(__name__)


def process_daily_market_data(date: str) -> bool:
    """
    Process daily market data for given date.
    
    Args:
        date: Date string in YYYY-MM-DD format
        
    Returns:
        bool: True if processing successful, False otherwise
    """
    logger.info(f"Starting market data processing for {date}")
    
    try:
        # Initialize processor
        processor = MarketDataProcessor()
        
        # Download market data from external sources
        market_data = download_market_data(date)
        
        # Validate data quality
        if not validate_market_data(market_data):
            raise ValueError("Market data validation failed")
        
        # Process and store data
        process_equity_data(market_data.get('equities', []))
        process_bond_data(market_data.get('bonds', []))
        process_fx_data(market_data.get('fx_rates', []))
        process_commodity_data(market_data.get('commodities', []))
        
        # Update processing status
        update_processing_status(date, 'completed')
        
        # Archive raw data to S3
        archive_market_data(date, market_data)
        
        # Load aggregated data to Snowflake for analytics
        load_data_to_snowflake(date, market_data)
        
        logger.info(f"Successfully processed market data for {date}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to process market data for {date}: {e}")
        update_processing_status(date, 'failed', str(e))
        return False


def download_market_data(date: str) -> Dict[str, List[Dict]]:
    """
    Download market data from external sources.
    
    Args:
        date: Date string in YYYY-MM-DD format
        
    Returns:
        Dict containing market data by asset class
    """
    logger.info(f"Downloading market data for {date}")
    
    # Mock implementation - in real scenario would connect to data vendors
    market_data = {
        'equities': [
            {'symbol': 'AAPL', 'price': 150.25, 'volume': 50000000, 'date': date},
            {'symbol': 'GOOGL', 'price': 2750.30, 'volume': 1200000, 'date': date},
            {'symbol': 'MSFT', 'price': 295.50, 'volume': 30000000, 'date': date},
        ],
        'bonds': [
            {'symbol': 'US10Y', 'yield': 4.25, 'price': 98.50, 'date': date},
            {'symbol': 'US2Y', 'yield': 4.75, 'price': 97.25, 'date': date},
        ],
        'fx_rates': [
            {'pair': 'EURUSD', 'rate': 1.0850, 'date': date},
            {'pair': 'USDJPY', 'rate': 148.25, 'date': date},
            {'pair': 'GBPUSD', 'rate': 1.2650, 'date': date},
        ],
        'commodities': [
            {'symbol': 'GOLD', 'price': 2020.50, 'unit': 'USD/oz', 'date': date},
            {'symbol': 'WTI', 'price': 78.25, 'unit': 'USD/bbl', 'date': date},
        ]
    }
    
    return market_data


def validate_market_data(market_data: Dict[str, List[Dict]]) -> bool:
    """
    Validate market data quality and completeness.
    
    Args:
        market_data: Market data dictionary
        
    Returns:
        bool: True if validation passes, False otherwise
    """
    logger.info("Validating market data quality")
    
    required_fields = {
        'equities': ['symbol', 'price', 'volume', 'date'],
        'bonds': ['symbol', 'yield', 'price', 'date'],
        'fx_rates': ['pair', 'rate', 'date'],
        'commodities': ['symbol', 'price', 'unit', 'date']
    }
    
    for asset_class, records in market_data.items():
        if asset_class not in required_fields:
            continue
            
        required = required_fields[asset_class]
        
        for record in records:
            # Check required fields
            for field in required:
                if field not in record or record[field] is None:
                    logger.error(f"Missing required field '{field}' in {asset_class}")
                    return False
            
            # Validate data types and ranges
            if asset_class == 'equities':
                if not isinstance(record['price'], (int, float)) or record['price'] <= 0:
                    logger.error(f"Invalid price for {record['symbol']}")
                    return False
                if not isinstance(record['volume'], int) or record['volume'] < 0:
                    logger.error(f"Invalid volume for {record['symbol']}")
                    return False
    
    logger.info("Market data validation passed")
    return True


def process_equity_data(equity_data: List[Dict]) -> None:
    """Process equity price data."""
    logger.info(f"Processing {len(equity_data)} equity records")
    
    for record in equity_data:
        query = """
        INSERT INTO market_data.equity_prices (symbol, price, volume, trade_date)
        VALUES (%(symbol)s, %(price)s, %(volume)s, %(date)s)
        ON CONFLICT (symbol, trade_date) 
        DO UPDATE SET price = EXCLUDED.price, volume = EXCLUDED.volume
        """
        execute_update('riskdb', query, record)


def process_bond_data(bond_data: List[Dict]) -> None:
    """Process bond price and yield data."""
    logger.info(f"Processing {len(bond_data)} bond records")
    
    for record in bond_data:
        query = """
        INSERT INTO market_data.bond_yields (symbol, yield_rate, price, trade_date)
        VALUES (%(symbol)s, %(yield)s, %(price)s, %(date)s)
        ON CONFLICT (symbol, trade_date)
        DO UPDATE SET yield_rate = EXCLUDED.yield_rate, price = EXCLUDED.price
        """
        execute_update('riskdb', query, record)


def process_fx_data(fx_data: List[Dict]) -> None:
    """Process foreign exchange rate data."""
    logger.info(f"Processing {len(fx_data)} FX records")
    
    for record in fx_data:
        query = """
        INSERT INTO market_data.fx_rates (currency_pair, rate, trade_date)
        VALUES (%(pair)s, %(rate)s, %(date)s)
        ON CONFLICT (currency_pair, trade_date)
        DO UPDATE SET rate = EXCLUDED.rate
        """
        execute_update('riskdb', query, record)


def process_commodity_data(commodity_data: List[Dict]) -> None:
    """Process commodity price data."""
    logger.info(f"Processing {len(commodity_data)} commodity records")
    
    for record in commodity_data:
        query = """
        INSERT INTO market_data.commodity_prices (symbol, price, unit, trade_date)
        VALUES (%(symbol)s, %(price)s, %(unit)s, %(date)s)
        ON CONFLICT (symbol, trade_date)
        DO UPDATE SET price = EXCLUDED.price, unit = EXCLUDED.unit
        """
        execute_update('riskdb', query, record)


def update_processing_status(date: str, status: str, error_message: str = None) -> None:
    """Update processing status in database."""
    query = """
    INSERT INTO processing_status (process_name, process_date, status, error_message, updated_at)
    VALUES ('market_data_processing', %(date)s, %(status)s, %(error_message)s, NOW())
    ON CONFLICT (process_name, process_date)
    DO UPDATE SET status = EXCLUDED.status, error_message = EXCLUDED.error_message, updated_at = NOW()
    """
    
    params = {
        'date': date,
        'status': status,
        'error_message': error_message
    }
    
    execute_update('riskdb', query, params)


def archive_market_data(date: str, market_data: Dict) -> None:
    """Archive market data to S3."""
    import json
    import tempfile
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(market_data, f, indent=2)
        temp_file = f.name
    
    # Upload to S3
    s3_key = f"market-data/raw/{date}/market_data.json"
    success = upload_to_s3(temp_file, s3_key)
    
    if success:
        logger.info(f"Archived market data to S3: {s3_key}")
    else:
        logger.error(f"Failed to archive market data to S3")
    
    # Clean up temporary file
    Path(temp_file).unlink()


def load_data_to_snowflake(date: str, market_data: Dict) -> None:
    """Load processed market data to Snowflake for analytics."""
    logger.info(f"Loading market data to Snowflake for {date}")
    
    try:
        with get_session('snowflakedb') as session:
            # Load equity data
            for record in market_data.get('equities', []):
                query = """
                INSERT INTO market_data.equity_prices_history 
                (symbol, price, volume, trade_date, processed_date)
                VALUES (%(symbol)s, %(price)s, %(volume)s, %(date)s, CURRENT_TIMESTAMP())
                """
                session.execute(query, record)
            
            # Load other asset classes similarly
            # This would be expanded for bonds, FX, commodities
            
            logger.info(f"Successfully loaded market data to Snowflake for {date}")
    except Exception as e:
        logger.error(f"Failed to load data to Snowflake: {e}")
        # Don't fail the entire process if Snowflake load fails
        pass


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Process daily market data')
    parser.add_argument('--date', required=True, help='Date in YYYY-MM-DD format')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    success = process_daily_market_data(args.date)
    sys.exit(0 if success else 1)
