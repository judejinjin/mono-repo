"""
Optimized Risk API Service with Performance Framework
Production-ready FastAPI service with caching, profiling, and monitoring
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import uvicorn
from contextlib import asynccontextmanager

# Performance optimization imports
import sys
from pathlib import Path
# Add performance optimization libs to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tests" / "performance_optimization" / "libs_performance"))
from libs_performance import (
    get_cache_manager, get_performance_profiler, get_async_task_manager,
    performance_monitor, cleanup_memory
)
from libs.security.authentication import verify_jwt_token, require_permissions
from libs.data.snowflake_client import get_snowflake_client  
from libs.data.market_data_client import get_market_data_provider
from libs.risk.calculations import get_risk_calculator
from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize performance components
cache_manager = get_cache_manager()
profiler = get_performance_profiler()
task_manager = get_async_task_manager()
config = get_config()

# Security
security = HTTPBearer()

# Data models
class PortfolioPosition(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)
    
    @validator('symbol')
    def validate_symbol(cls, v):
        return v.upper().strip()

class RiskAnalysisRequest(BaseModel):
    portfolio: List[PortfolioPosition]
    confidence_level: float = Field(0.95, ge=0.90, le=0.99)
    time_horizon_days: int = Field(1, ge=1, le=30)
    include_stress_testing: bool = True
    
    @validator('portfolio')
    def validate_portfolio_not_empty(cls, v):
        if not v:
            raise ValueError("Portfolio cannot be empty")
        return v

class MarketDataRequest(BaseModel):
    symbols: List[str] = Field(..., min_items=1, max_items=100)
    include_historical: bool = False
    days_history: int = Field(30, ge=1, le=365)
    
    @validator('symbols')
    def validate_symbols(cls, v):
        return [symbol.upper().strip() for symbol in v if symbol.strip()]

class RiskMetrics(BaseModel):
    var_95: float
    var_99: float
    expected_shortfall: float
    maximum_drawdown: float
    sharpe_ratio: float
    volatility: float
    beta: float
    correlation_matrix: Dict[str, Dict[str, float]]

class StressTestResult(BaseModel):
    scenario_name: str
    portfolio_impact: float
    probability: float
    description: str

class RiskAnalysisResponse(BaseModel):
    request_id: str
    timestamp: datetime
    portfolio_value: float
    risk_metrics: RiskMetrics
    stress_test_results: List[StressTestResult]
    confidence_level: float
    time_horizon_days: int
    computation_time_ms: float


# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management with performance monitoring."""
    logger.info("Starting Risk API Service with performance optimization...")
    
    # Start performance monitoring
    async with performance_monitor():
        # Initialize components
        try:
            # Test database connection
            snowflake_client = get_snowflake_client()
            if snowflake_client:
                await asyncio.to_thread(snowflake_client.test_connection)
            
            # Test market data connection
            market_data_provider = get_market_data_provider()
            if market_data_provider:
                test_price = await asyncio.to_thread(market_data_provider.get_current_price, "AAPL")
                logger.info(f"Market data connection verified: AAPL = ${test_price}")
            
            # Warm up cache
            cache_manager.set("service_status", {"status": "running", "startup": datetime.utcnow().isoformat()})
            
            logger.info("Risk API Service startup completed successfully")
            
        except Exception as e:
            logger.error(f"Service startup error: {e}")
        
        yield
        
        # Cleanup
        logger.info("Shutting down Risk API Service...")
        cleanup_memory()
        logger.info("Risk API Service shutdown completed")


# Create FastAPI app
app = FastAPI(
    title="Optimized Risk Analysis API",
    description="High-performance risk analysis service with caching and monitoring",
    version="2.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Dependency injection
async def get_authenticated_user(token: str = Depends(security)):
    """Authenticate user with performance profiling."""
    with profiler.profile_function("authenticate_user"):
        try:
            # Check cache first
            cache_key = f"auth_token:{hash(token.credentials)}"
            cached_user = cache_manager.get(cache_key)
            if cached_user:
                return cached_user
            
            # Verify token
            user_info = verify_jwt_token(token.credentials)
            if not user_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )
            
            # Cache for 5 minutes
            cache_manager.set(cache_key, user_info, ttl=300)
            return user_info
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )


async def require_risk_analysis_permission(user: dict = Depends(get_authenticated_user)):
    """Require risk analysis permission."""
    if not require_permissions(user, ["risk:read", "risk:analyze"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for risk analysis"
        )
    return user


# Health and monitoring endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "2.0.0",
        "cache_status": "connected" if cache_manager.ping() else "disconnected"
    }

@app.get("/metrics")
async def get_metrics():
    """Performance metrics endpoint."""
    with profiler.profile_function("get_metrics"):
        cache_stats = cache_manager.get_stats()
        system_metrics = profiler.collect_system_metrics()
        
        return {
            "cache_statistics": cache_stats,
            "system_metrics": system_metrics.to_dict(),
            "memory_usage": profiler.get_memory_usage(),
            "timestamp": datetime.utcnow()
        }

@app.get("/status")
async def get_service_status():
    """Detailed service status."""
    with profiler.profile_function("get_service_status"):
        try:
            # Check all service dependencies
            status_checks = {}
            
            # Check cache
            status_checks["cache"] = cache_manager.ping()
            
            # Check database
            try:
                snowflake_client = get_snowflake_client()
                status_checks["database"] = snowflake_client.test_connection() if snowflake_client else False
            except Exception:
                status_checks["database"] = False
            
            # Check market data
            try:
                market_data_provider = get_market_data_provider()
                test_price = market_data_provider.get_current_price("AAPL") if market_data_provider else None
                status_checks["market_data"] = test_price is not None
            except Exception:
                status_checks["market_data"] = False
            
            overall_status = "healthy" if all(status_checks.values()) else "degraded"
            
            return {
                "overall_status": overall_status,
                "components": status_checks,
                "timestamp": datetime.utcnow(),
                "uptime_seconds": (datetime.utcnow() - datetime.utcnow().replace(hour=0, minute=0, second=0)).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return {
                "overall_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow()
            }


# Market data endpoints
@app.post("/api/v1/market-data")
async def get_market_data(
    request: MarketDataRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_authenticated_user)
):
    """Get market data with caching."""
    with profiler.profile_function("get_market_data"):
        try:
            # Check cache first
            cache_key = f"market_data:{hash(tuple(sorted(request.symbols)))}:{request.include_historical}:{request.days_history}"
            cached_data = cache_manager.get(cache_key)
            if cached_data:
                logger.info(f"Returning cached market data for {len(request.symbols)} symbols")
                return cached_data
            
            market_data_provider = get_market_data_provider()
            if not market_data_provider:
                raise HTTPException(status_code=503, detail="Market data service unavailable")
            
            # Get current prices
            current_prices = {}
            for symbol in request.symbols:
                try:
                    price = await asyncio.to_thread(market_data_provider.get_current_price, symbol)
                    current_prices[symbol] = price
                except Exception as e:
                    logger.warning(f"Failed to get price for {symbol}: {e}")
                    current_prices[symbol] = None
            
            result = {
                "symbols": request.symbols,
                "current_prices": current_prices,
                "timestamp": datetime.utcnow(),
                "include_historical": request.include_historical
            }
            
            # Get historical data if requested
            if request.include_historical:
                historical_data = {}
                for symbol in request.symbols:
                    try:
                        history = await asyncio.to_thread(
                            market_data_provider.get_historical_prices,
                            symbol,
                            request.days_history
                        )
                        historical_data[symbol] = history
                    except Exception as e:
                        logger.warning(f"Failed to get historical data for {symbol}: {e}")
                        historical_data[symbol] = []
                
                result["historical_data"] = historical_data
            
            # Cache for 1 minute (market data changes frequently)
            cache_manager.set(cache_key, result, ttl=60)
            
            # Schedule background cache refresh
            background_tasks.add_task(schedule_market_data_refresh, request.symbols)
            
            return result
            
        except Exception as e:
            logger.error(f"Market data error: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve market data: {str(e)}")


# Risk analysis endpoints
@app.post("/api/v1/risk-analysis", response_model=RiskAnalysisResponse)
async def analyze_portfolio_risk(
    request: RiskAnalysisRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(require_risk_analysis_permission)
):
    """Analyze portfolio risk with comprehensive caching and optimization."""
    request_id = f"risk_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(str(request.portfolio))}"
    
    with profiler.profile_function("analyze_portfolio_risk"):
        start_time = datetime.utcnow()
        
        try:
            # Check cache first
            cache_key = f"risk_analysis:{hash(str(request.portfolio))}:{request.confidence_level}:{request.time_horizon_days}"
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached risk analysis for portfolio with {len(request.portfolio)} positions")
                cached_result["request_id"] = request_id  # Update request ID
                return cached_result
            
            # Get risk calculator
            risk_calculator = get_risk_calculator()
            if not risk_calculator:
                raise HTTPException(status_code=503, detail="Risk calculation service unavailable")
            
            # Extract symbols and get market data
            symbols = list(set(pos.symbol for pos in request.portfolio))
            market_data_provider = get_market_data_provider()
            
            if not market_data_provider:
                raise HTTPException(status_code=503, detail="Market data service unavailable")
            
            # Get current prices and historical data
            current_prices = {}
            historical_prices = {}
            
            for symbol in symbols:
                try:
                    # Current price
                    current_price = await asyncio.to_thread(market_data_provider.get_current_price, symbol)
                    current_prices[symbol] = current_price
                    
                    # Historical prices (for volatility calculation)
                    historical_data = await asyncio.to_thread(
                        market_data_provider.get_historical_prices,
                        symbol,
                        max(30, request.time_horizon_days * 5)  # Get enough history
                    )
                    historical_prices[symbol] = historical_data
                    
                except Exception as e:
                    logger.error(f"Failed to get data for {symbol}: {e}")
                    raise HTTPException(status_code=400, detail=f"Failed to get market data for {symbol}")
            
            # Calculate portfolio value
            portfolio_value = sum(pos.quantity * current_prices[pos.symbol] for pos in request.portfolio)
            
            # Prepare portfolio data for risk calculations
            portfolio_data = [
                {
                    "symbol": pos.symbol,
                    "quantity": pos.quantity,
                    "price": current_prices[pos.symbol],
                    "weight": (pos.quantity * current_prices[pos.symbol]) / portfolio_value
                }
                for pos in request.portfolio
            ]
            
            # Calculate risk metrics
            var_95 = await asyncio.to_thread(
                risk_calculator.calculate_portfolio_var,
                portfolio_data,
                historical_prices,
                confidence_level=0.95,
                time_horizon=request.time_horizon_days
            )
            
            var_99 = await asyncio.to_thread(
                risk_calculator.calculate_portfolio_var,
                portfolio_data,
                historical_prices,
                confidence_level=0.99,
                time_horizon=request.time_horizon_days
            )
            
            expected_shortfall = await asyncio.to_thread(
                risk_calculator.calculate_expected_shortfall,
                portfolio_data,
                historical_prices,
                confidence_level=request.confidence_level
            )
            
            maximum_drawdown = await asyncio.to_thread(
                risk_calculator.calculate_maximum_drawdown,
                portfolio_data,
                historical_prices
            )
            
            sharpe_ratio = await asyncio.to_thread(
                risk_calculator.calculate_sharpe_ratio,
                portfolio_data,
                historical_prices
            )
            
            volatility = await asyncio.to_thread(
                risk_calculator.calculate_portfolio_volatility,
                portfolio_data,
                historical_prices
            )
            
            beta = await asyncio.to_thread(
                risk_calculator.calculate_portfolio_beta,
                portfolio_data,
                historical_prices
            )
            
            correlation_matrix = await asyncio.to_thread(
                risk_calculator.calculate_correlation_matrix,
                historical_prices
            )
            
            # Risk metrics
            risk_metrics = RiskMetrics(
                var_95=var_95,
                var_99=var_99,
                expected_shortfall=expected_shortfall,
                maximum_drawdown=maximum_drawdown,
                sharpe_ratio=sharpe_ratio,
                volatility=volatility,
                beta=beta,
                correlation_matrix=correlation_matrix
            )
            
            # Stress testing
            stress_test_results = []
            if request.include_stress_testing:
                stress_scenarios = [
                    ("Market Crash", -0.20, 0.05, "20% market decline scenario"),
                    ("Interest Rate Shock", -0.10, 0.15, "Significant interest rate increase"),
                    ("Volatility Spike", -0.15, 0.10, "Market volatility increases by 50%"),
                    ("Sector Rotation", -0.08, 0.20, "Major sector rotation event"),
                ]
                
                for scenario_name, impact, probability, description in stress_scenarios:
                    portfolio_impact = portfolio_value * impact
                    stress_test_results.append(
                        StressTestResult(
                            scenario_name=scenario_name,
                            portfolio_impact=portfolio_impact,
                            probability=probability,
                            description=description
                        )
                    )
            
            # Calculate computation time
            computation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Create response
            response = RiskAnalysisResponse(
                request_id=request_id,
                timestamp=datetime.utcnow(),
                portfolio_value=portfolio_value,
                risk_metrics=risk_metrics,
                stress_test_results=stress_test_results,
                confidence_level=request.confidence_level,
                time_horizon_days=request.time_horizon_days,
                computation_time_ms=computation_time
            )
            
            # Cache result for 5 minutes
            cache_manager.set(cache_key, response.dict(), ttl=300)
            
            # Schedule background risk monitoring
            background_tasks.add_task(schedule_risk_monitoring, portfolio_data, user["user_id"])
            
            logger.info(f"Risk analysis completed in {computation_time:.2f}ms for portfolio value ${portfolio_value:,.2f}")
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Risk analysis error: {e}")
            raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")


@app.get("/api/v1/risk-analysis/{request_id}")
async def get_risk_analysis_result(
    request_id: str,
    user: dict = Depends(require_risk_analysis_permission)
):
    """Get cached risk analysis result."""
    with profiler.profile_function("get_risk_analysis_result"):
        cache_key = f"risk_result:{request_id}"
        result = cache_manager.get(cache_key)
        
        if not result:
            raise HTTPException(status_code=404, detail="Risk analysis result not found")
        
        return result


# Background tasks
async def schedule_market_data_refresh(symbols: List[str]):
    """Background task to refresh market data cache."""
    try:
        logger.info(f"Refreshing market data cache for {len(symbols)} symbols")
        market_data_provider = get_market_data_provider()
        
        if market_data_provider:
            for symbol in symbols:
                try:
                    price = await asyncio.to_thread(market_data_provider.get_current_price, symbol)
                    cache_key = f"current_price:{symbol}"
                    cache_manager.set(cache_key, price, ttl=60)
                except Exception as e:
                    logger.warning(f"Failed to refresh price for {symbol}: {e}")
        
    except Exception as e:
        logger.error(f"Market data refresh error: {e}")


async def schedule_risk_monitoring(portfolio_data: List[Dict], user_id: str):
    """Background task to monitor portfolio risk."""
    try:
        logger.info(f"Starting risk monitoring for user {user_id}")
        
        # Add to background monitoring queue
        await task_manager.add_task(
            "risk_monitoring",
            monitor_portfolio_risk,
            portfolio_data,
            user_id
        )
        
    except Exception as e:
        logger.error(f"Risk monitoring schedule error: {e}")


async def monitor_portfolio_risk(portfolio_data: List[Dict], user_id: str):
    """Monitor portfolio risk in background."""
    try:
        # This would implement ongoing risk monitoring
        # For now, just log the monitoring activity
        logger.info(f"Monitoring portfolio risk for user {user_id} with {len(portfolio_data)} positions")
        
        # In a real implementation, this would:
        # 1. Continuously monitor market conditions
        # 2. Alert on significant risk changes
        # 3. Generate periodic risk reports
        # 4. Update risk metrics in real-time
        
    except Exception as e:
        logger.error(f"Portfolio risk monitoring error: {e}")


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with logging."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.utcnow().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "timestamp": datetime.utcnow().isoformat()}
    )


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "services.risk_api_optimized:app",
        host="0.0.0.0",
        port=8001,  # Different port from regular risk API
        reload=False,  # Disable in production
        log_level="info",
        access_log=True
    )