"""
FastAPI Risk Management Service
Provides REST API endpoints for risk management operations.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from libs.business.risk_management import RiskCalculator, MarketDataProcessor
from libs.business.analytics import ReportGenerator
from libs.db import get_session, execute_query
from sqlalchemy import text
from config import get_config

# Initialize FastAPI app
app = FastAPI(
    title="Risk Management API",
    description="API for risk calculations and market data processing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class RiskMetricsRequest(BaseModel):
    portfolio_id: str
    calculation_date: Optional[str] = None

class RiskMetricsResponse(BaseModel):
    portfolio_id: str
    var_95: float
    var_99: float
    expected_shortfall: float
    volatility: float
    sharpe_ratio: float
    calculated_at: str

class MarketDataRequest(BaseModel):
    date: str
    asset_classes: Optional[List[str]] = None

class ReportRequest(BaseModel):
    report_type: str
    start_date: str
    end_date: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

# Dependency injection
def get_risk_calculator():
    return RiskCalculator()

def get_market_processor():
    return MarketDataProcessor()

def get_report_generator():
    return ReportGenerator()

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Risk Management API",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/v1/risk/calculate", response_model=RiskMetricsResponse)
async def calculate_risk_metrics(
    request: RiskMetricsRequest,
    calculator: RiskCalculator = Depends(get_risk_calculator)
):
    """Calculate risk metrics for a portfolio."""
    try:
        risk_metrics = calculator.calculate_portfolio_risk(request.portfolio_id)
        return RiskMetricsResponse(**risk_metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk calculation failed: {str(e)}")

@app.get("/api/v1/portfolios")
async def get_portfolios():
    """Get list of all portfolios."""
    # Mock implementation
    portfolios = [
        {"portfolio_id": "EQUITY_GROWTH", "name": "Equity Growth Portfolio", "active": True},
        {"portfolio_id": "FIXED_INCOME", "name": "Fixed Income Portfolio", "active": True},
        {"portfolio_id": "BALANCED", "name": "Balanced Portfolio", "active": True},
        {"portfolio_id": "EMERGING_MARKETS", "name": "Emerging Markets Portfolio", "active": True},
    ]
    return {"portfolios": portfolios}

@app.get("/api/v1/portfolios/{portfolio_id}/risk")
async def get_portfolio_risk(
    portfolio_id: str,
    calculator: RiskCalculator = Depends(get_risk_calculator)
):
    """Get current risk metrics for a specific portfolio."""
    try:
        risk_metrics = calculator.calculate_portfolio_risk(portfolio_id)
        return risk_metrics
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Portfolio not found: {portfolio_id}")

@app.post("/api/v1/market-data/process")
async def process_market_data(
    request: MarketDataRequest,
    processor: MarketDataProcessor = Depends(get_market_processor)
):
    """Process market data for a specific date."""
    try:
        success = processor.process_daily_prices(request.date)
        if success:
            return {"status": "success", "date": request.date, "message": "Market data processed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Market data processing failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/api/v1/market-data/status/{date}")
async def get_market_data_status(date: str):
    """Get market data processing status for a date."""
    # Mock implementation
    return {
        "date": date,
        "status": "completed",
        "processed_at": datetime.utcnow().isoformat(),
        "records_processed": 1250
    }

@app.post("/api/v1/reports/generate")
async def generate_report(
    request: ReportRequest,
    generator: ReportGenerator = Depends(get_report_generator)
):
    """Generate a report."""
    try:
        if request.report_type == "daily_risk":
            report = generator.generate_daily_risk_report(request.start_date)
        elif request.report_type == "performance":
            end_date = request.end_date or request.start_date
            report = generator.generate_performance_report(request.start_date, end_date)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown report type: {request.report_type}")
        
        return {"status": "success", "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.get("/api/v1/reports/list")
async def list_reports():
    """List available reports."""
    reports = [
        {
            "type": "daily_risk",
            "name": "Daily Risk Report",
            "description": "Daily portfolio risk metrics and summary"
        },
        {
            "type": "performance",
            "name": "Performance Report",
            "description": "Portfolio performance analysis over a period"
        }
    ]
    return {"reports": reports}

@app.get("/api/v1/databases")
async def get_databases():
    """Get list of available databases."""
    databases = [
        {"name": "riskdb", "type": "postgresql", "description": "Risk management data"},
        {"name": "analyticsdb", "type": "postgresql", "description": "Analytics and reporting data"},
        {"name": "snowflakedb", "type": "snowflake", "description": "Data warehouse for large-scale analytics"}
    ]
    return {"databases": databases}

@app.get("/api/v1/snowflake/warehouses")
async def get_snowflake_warehouses():
    """Get Snowflake warehouse information."""
    try:
        # Mock implementation - in production would query Snowflake system tables
        warehouses = [
            {"name": "DEV_WH", "size": "X-SMALL", "state": "STARTED"},
            {"name": "UAT_WH", "size": "SMALL", "state": "STARTED"},
            {"name": "PROD_WH", "size": "LARGE", "state": "STARTED"}
        ]
        return {"warehouses": warehouses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve warehouses: {str(e)}")

@app.post("/api/v1/analytics/snowflake-query")
async def execute_snowflake_query(query_request: dict):
    """Execute analytics query on Snowflake."""
    try:
        query = query_request.get('query')
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Use Snowflake for analytics queries
        with get_session('snowflakedb') as session:
            result = session.execute(text(query))
            rows = [dict(row._mapping) for row in result]
        
        return {
            "status": "success",
            "row_count": len(rows),
            "data": rows[:100],  # Limit to first 100 rows for API response
            "truncated": len(rows) > 100
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

@app.get("/api/v1/analytics/data-summary")
async def get_data_summary():
    """Get summary of data available in analytics databases."""
    try:
        # Query both PostgreSQL and Snowflake for data summary
        summary = {
            "postgresql": {
                "total_portfolios": 25,
                "total_trades_today": 1250,
                "last_update": "2025-09-01T10:30:00Z"
            },
            "snowflake": {
                "total_historical_records": 50000000,
                "data_retention_days": 2555,  # 7 years
                "warehouse_usage_credits": 125.5,
                "last_data_load": "2025-09-01T06:00:00Z"
            }
        }
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get data summary: {str(e)}")

@app.get("/api/v1/config")
async def get_api_config():
    """Get API configuration information."""
    config = get_config()
    api_config = config.get('fastapi', {})
    
    return {
        "environment": config.get('app', {}).get('environment', 'unknown'),
        "debug": config.get('app', {}).get('debug', False),
        "version": "1.0.0",
        "host": api_config.get('host', '0.0.0.0'),
        "port": api_config.get('port', 8000)
    }

if __name__ == "__main__":
    import uvicorn
    
    config = get_config()
    fastapi_config = config.get('fastapi', {})
    
    uvicorn.run(
        "main:app",
        host=fastapi_config.get('host', '0.0.0.0'),
        port=fastapi_config.get('port', 8000),
        reload=fastapi_config.get('reload', False),
        workers=fastapi_config.get('workers', 1)
    )
