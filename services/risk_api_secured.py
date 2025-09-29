"""
Secured Risk API Service
Integration of security framework with enhanced API functionality
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, Request, Response, status
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import logging

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from config import get_config
    from libs.monitoring import get_metrics_collector
    from libs.security.security_framework import User, Role, Permission
    from libs.security.middleware import (
        configure_security, get_current_user, require_permission, require_role
    )
    from libs.security.authentication import get_auth_service
    from libs.data.snowflake_client import get_snowflake_client
    from libs.data.market_data_client import get_market_data_provider
    from libs.risk.calculations import get_risk_calculator
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback imports for development
    get_config = lambda: {}
    get_metrics_collector = lambda: None
    get_snowflake_client = lambda: None
    get_market_data_provider = lambda: None
    get_risk_calculator = lambda: None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with security configuration
app = FastAPI(
    title="Secured Risk Management API",
    description="Enterprise-grade risk management API with comprehensive security",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure security middleware and authentication
security_config = {
    'whitelist_enabled': get_config().get('security_whitelist_enabled', False)
}
security_manager = configure_security(app, security_config)

# Initialize services
auth_service = get_auth_service()
metrics_collector = get_metrics_collector()


# Pydantic models for request/response validation
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8)
    totp_token: Optional[str] = Field(None, regex=r'^\d{6}$')
    backup_code: Optional[str] = Field(None, min_length=8, max_length=8)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric with optional underscores/hyphens')
        return v


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=12)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric with optional underscores/hyphens')
        return v


class PasswordResetRequest(BaseModel):
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


class PasswordResetConfirm(BaseModel):
    token: str = Field(..., min_length=32)
    new_password: str = Field(..., min_length=12)


class PortfolioAnalysisRequest(BaseModel):
    portfolio_id: str = Field(..., regex=r'^[A-Z0-9_-]{3,20}$')
    start_date: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}$')
    end_date: Optional[str] = Field(None, regex=r'^\d{4}-\d{2}-\d{2}$')
    risk_metrics: Optional[List[str]] = Field(default=['var', 'volatility', 'sharpe'])
    confidence_level: Optional[float] = Field(default=0.95, ge=0.01, le=0.99)
    
    @validator('risk_metrics')
    def validate_risk_metrics(cls, v):
        allowed_metrics = ['var', 'volatility', 'sharpe', 'beta', 'alpha', 'max_drawdown', 'sortino']
        for metric in v:
            if metric not in allowed_metrics:
                raise ValueError(f'Invalid risk metric: {metric}')
        return v


class StressTestRequest(BaseModel):
    portfolio_id: str = Field(..., regex=r'^[A-Z0-9_-]{3,20}$')
    scenario_type: str = Field(..., regex=r'^(market_crash|interest_rate|volatility|custom)$')
    stress_factor: Optional[float] = Field(default=1.0, ge=0.1, le=10.0)
    custom_shocks: Optional[Dict[str, float]] = None


class MarketDataRequest(BaseModel):
    symbols: List[str] = Field(..., min_items=1, max_items=100)
    start_date: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}$')
    end_date: Optional[str] = Field(None, regex=r'^\d{4}-\d{2}-\d{2}$')
    data_source: Optional[str] = Field(default='auto', regex=r'^(auto|alpha_vantage|yahoo|bloomberg)$')
    
    @validator('symbols')
    def validate_symbols(cls, v):
        for symbol in v:
            if not symbol.replace('.', '').replace('-', '').isalnum():
                raise ValueError(f'Invalid symbol format: {symbol}')
        return v


# Authentication endpoints
@app.post("/auth/login", tags=["Authentication"])
async def login(request: LoginRequest, req: Request):
    """Authenticate user and return access token."""
    client_ip = req.client.host if req.client else '127.0.0.1'
    user_agent = req.headers.get('user-agent', '')
    
    result = auth_service.authenticate(
        username=request.username,
        password=request.password,
        ip_address=client_ip,
        user_agent=user_agent,
        totp_token=request.totp_token,
        backup_code=request.backup_code
    )
    
    if metrics_collector:
        if result['success']:
            metrics_collector.record_request('auth_login_success', 'auth')
        else:
            metrics_collector.record_error('auth_login_failed', 'auth')
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result['error']
        )
    
    return {
        'access_token': result['access_token'],
        'refresh_token': result['refresh_token'],
        'token_type': result['token_type'],
        'user': result['user'],
        'mfa_enabled': result['mfa_enabled']
    }


@app.post("/auth/register", tags=["Authentication"])
async def register(request: RegisterRequest):
    """Register new user account."""
    result = auth_service.register_user(
        username=request.username,
        email=request.email,
        password=request.password,
        first_name=request.first_name or "",
        last_name=request.last_name or "",
        role=Role.VIEWER  # Default role for new users
    )
    
    if metrics_collector:
        if result['success']:
            metrics_collector.record_request('user_registration_success', 'auth')
        else:
            metrics_collector.record_error('user_registration_failed', 'auth')
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result['error']
        )
    
    return {
        'message': 'User registered successfully',
        'user_id': result['user_id'],
        'verification_required': result['verification_required']
    }


@app.post("/auth/password-reset", tags=["Authentication"])
async def request_password_reset(request: PasswordResetRequest):
    """Request password reset email."""
    result = auth_service.request_password_reset(request.email)
    
    if metrics_collector:
        metrics_collector.record_request('password_reset_request', 'auth')
    
    return {'message': result['message']}


@app.post("/auth/password-reset/confirm", tags=["Authentication"])
async def confirm_password_reset(request: PasswordResetConfirm):
    """Confirm password reset with token."""
    result = auth_service.reset_password(request.token, request.new_password)
    
    if metrics_collector:
        if result['success']:
            metrics_collector.record_request('password_reset_success', 'auth')
        else:
            metrics_collector.record_error('password_reset_failed', 'auth')
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result['error']
        )
    
    return {'message': result['message']}


@app.post("/auth/mfa/setup", tags=["Authentication"])
async def setup_mfa(user: User = Depends(get_current_user)):
    """Setup multi-factor authentication."""
    result = auth_service.setup_mfa(user.user_id)
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result['error']
        )
    
    return {
        'secret': result['secret'],
        'qr_code': result['qr_code'],
        'backup_codes': result['backup_codes']
    }


@app.post("/auth/mfa/enable", tags=["Authentication"])
async def enable_mfa(totp_token: str, user: User = Depends(get_current_user)):
    """Enable MFA after verification."""
    result = auth_service.enable_mfa(user.user_id, totp_token)
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result['error']
        )
    
    return {'message': result['message']}


# Portfolio endpoints with security
@app.get("/portfolios", tags=["Portfolio"])
async def get_portfolios(
    user: User = Depends(require_permission(Permission.PORTFOLIO_READ))
):
    """Get user's portfolios."""
    try:
        snowflake_client = get_snowflake_client()
        if not snowflake_client:
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        portfolios = snowflake_client.get_user_portfolios(user.user_id)
        
        if metrics_collector:
            metrics_collector.record_request('get_portfolios', 'portfolio')
        
        return {
            'portfolios': portfolios,
            'count': len(portfolios)
        }
        
    except Exception as e:
        logger.error(f"Error fetching portfolios: {e}")
        if metrics_collector:
            metrics_collector.record_error('get_portfolios_failed', 'portfolio')
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/portfolios/{portfolio_id}/analysis", tags=["Risk Analysis"])
async def analyze_portfolio(
    portfolio_id: str,
    request: PortfolioAnalysisRequest,
    user: User = Depends(require_permission(Permission.RISK_CALCULATE))
):
    """Perform comprehensive portfolio risk analysis."""
    try:
        # Validate portfolio access
        snowflake_client = get_snowflake_client()
        if not snowflake_client:
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        # Check if user has access to portfolio
        portfolio = snowflake_client.get_portfolio_by_id(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # For security, check portfolio ownership or permission
        if portfolio.get('user_id') != user.user_id and not user.has_permission(Permission.ADMIN_READ):
            raise HTTPException(status_code=403, detail="Access denied to portfolio")
        
        # Get portfolio holdings
        holdings = snowflake_client.get_portfolio_holdings(portfolio_id)
        
        # Get market data for analysis period
        market_data_provider = get_market_data_provider()
        symbols = [holding['symbol'] for holding in holdings]
        
        market_data = market_data_provider.get_price_history(
            symbols=symbols,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        # Calculate risk metrics
        risk_calculator = get_risk_calculator()
        
        analysis_results = {}
        
        for metric in request.risk_metrics:
            if metric == 'var':
                var_result = risk_calculator.calculate_portfolio_var(
                    holdings, market_data, confidence_level=request.confidence_level
                )
                analysis_results['var'] = var_result
                
            elif metric == 'volatility':
                volatility = risk_calculator.calculate_portfolio_volatility(holdings, market_data)
                analysis_results['volatility'] = volatility
                
            elif metric == 'sharpe':
                sharpe = risk_calculator.calculate_sharpe_ratio(holdings, market_data)
                analysis_results['sharpe_ratio'] = sharpe
                
            elif metric == 'beta':
                beta = risk_calculator.calculate_portfolio_beta(holdings, market_data)
                analysis_results['beta'] = beta
                
            elif metric == 'alpha':
                alpha = risk_calculator.calculate_alpha(holdings, market_data)
                analysis_results['alpha'] = alpha
        
        if metrics_collector:
            metrics_collector.record_request('portfolio_analysis', 'risk')
            metrics_collector.record_business_metric('risk_calculations_performed', len(request.risk_metrics))
        
        return {
            'portfolio_id': portfolio_id,
            'analysis_date': datetime.utcnow().isoformat(),
            'period': {
                'start_date': request.start_date,
                'end_date': request.end_date
            },
            'risk_metrics': analysis_results,
            'metadata': {
                'holdings_count': len(holdings),
                'confidence_level': request.confidence_level,
                'calculated_by': user.username
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio analysis failed: {e}")
        if metrics_collector:
            metrics_collector.record_error('portfolio_analysis_failed', 'risk')
        raise HTTPException(status_code=500, detail="Analysis failed")


@app.post("/stress-test", tags=["Risk Analysis"])
async def perform_stress_test(
    request: StressTestRequest,
    user: User = Depends(require_permission(Permission.RISK_STRESS_TEST))
):
    """Perform stress testing on portfolio."""
    try:
        snowflake_client = get_snowflake_client()
        risk_calculator = get_risk_calculator()
        
        # Get portfolio and validate access
        portfolio = snowflake_client.get_portfolio_by_id(request.portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        if portfolio.get('user_id') != user.user_id and not user.has_permission(Permission.ADMIN_READ):
            raise HTTPException(status_code=403, detail="Access denied to portfolio")
        
        holdings = snowflake_client.get_portfolio_holdings(request.portfolio_id)
        
        # Perform stress test based on scenario type
        if request.scenario_type == 'market_crash':
            results = risk_calculator.stress_test_market_crash(
                holdings, stress_factor=request.stress_factor
            )
        elif request.scenario_type == 'interest_rate':
            results = risk_calculator.stress_test_interest_rate(
                holdings, stress_factor=request.stress_factor
            )
        elif request.scenario_type == 'volatility':
            results = risk_calculator.stress_test_volatility_spike(
                holdings, stress_factor=request.stress_factor
            )
        elif request.scenario_type == 'custom' and request.custom_shocks:
            results = risk_calculator.stress_test_custom(
                holdings, request.custom_shocks
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid scenario type")
        
        if metrics_collector:
            metrics_collector.record_request('stress_test', 'risk')
            metrics_collector.record_business_metric('stress_tests_performed', 1)
        
        return {
            'portfolio_id': request.portfolio_id,
            'scenario_type': request.scenario_type,
            'test_date': datetime.utcnow().isoformat(),
            'results': results,
            'metadata': {
                'stress_factor': request.stress_factor,
                'performed_by': user.username
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stress test failed: {e}")
        if metrics_collector:
            metrics_collector.record_error('stress_test_failed', 'risk')
        raise HTTPException(status_code=500, detail="Stress test failed")


@app.post("/market-data", tags=["Market Data"])
async def get_market_data(
    request: MarketDataRequest,
    user: User = Depends(require_permission(Permission.MARKET_DATA_READ))
):
    """Fetch market data for specified symbols."""
    try:
        market_data_provider = get_market_data_provider()
        
        data = market_data_provider.get_price_history(
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            preferred_source=request.data_source if request.data_source != 'auto' else None
        )
        
        if metrics_collector:
            metrics_collector.record_request('market_data_fetch', 'data')
            metrics_collector.record_business_metric('market_data_symbols_fetched', len(request.symbols))
        
        return {
            'symbols': request.symbols,
            'period': {
                'start_date': request.start_date,
                'end_date': request.end_date
            },
            'data': data,
            'metadata': {
                'symbols_count': len(request.symbols),
                'data_source': request.data_source,
                'fetched_by': user.username,
                'fetch_time': datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Market data fetch failed: {e}")
        if metrics_collector:
            metrics_collector.record_error('market_data_fetch_failed', 'data')
        raise HTTPException(status_code=500, detail="Market data fetch failed")


# Admin endpoints
@app.get("/admin/users", tags=["Administration"])
async def get_users(
    user: User = Depends(require_permission(Permission.ADMIN_USERS))
):
    """Get all users (admin only)."""
    try:
        stats = auth_service.get_authentication_stats()
        
        return {
            'statistics': stats,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Admin users fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user data")


@app.get("/admin/security-status", tags=["Administration"])
async def get_security_status(
    user: User = Depends(require_permission(Permission.ADMIN_SYSTEM))
):
    """Get security system status (admin only)."""
    try:
        return security_manager.get_security_status()
        
    except Exception as e:
        logger.error(f"Security status fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch security status")


# Health and monitoring endpoints
@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Health check endpoint (no authentication required)."""
    try:
        # Basic health checks
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'authentication': True,
                'database': bool(get_snowflake_client()),
                'market_data': bool(get_market_data_provider()),
                'risk_engine': bool(get_risk_calculator())
            }
        }
        
        # Check if all services are healthy
        all_healthy = all(health_status['services'].values())
        health_status['status'] = 'healthy' if all_healthy else 'degraded'
        
        if metrics_collector:
            metrics_collector.record_request('health_check', 'monitoring')
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }


@app.get("/metrics", tags=["Monitoring"])
async def get_metrics(
    user: User = Depends(require_permission(Permission.ADMIN_READ))
):
    """Get system metrics (admin only)."""
    try:
        if not metrics_collector:
            raise HTTPException(status_code=503, detail="Metrics service unavailable")
        
        return metrics_collector.get_all_metrics()
        
    except Exception as e:
        logger.error(f"Metrics fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")


# User profile endpoints
@app.get("/profile", tags=["User"])
async def get_profile(user: User = Depends(get_current_user)):
    """Get current user profile."""
    return user.to_dict()


@app.get("/profile/permissions", tags=["User"])
async def get_user_permissions(user: User = Depends(get_current_user)):
    """Get current user permissions."""
    return {
        'user_id': user.user_id,
        'role': user.role.value,
        'permissions': [p.value for p in user.permissions],
        'mfa_enabled': user.mfa_enabled
    }


if __name__ == "__main__":
    import uvicorn
    
    # Configure for secure deployment
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_keyfile=os.getenv('SSL_KEY_FILE'),
        ssl_certfile=os.getenv('SSL_CERT_FILE'),
        log_level="info"
    )