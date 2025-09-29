"""
Database models for the risk platform.
Defines SQLAlchemy models for all entities.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

Base = declarative_base()

class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default='business_user')  # business_user, data_scientist, admin
    groups = Column(JSON, default=list)  # User groups for additional permissions
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True))
    
    # Profile information
    department = Column(String(100))
    phone = Column(String(20))
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="owner")
    risk_calculations = relationship("RiskCalculation", back_populates="user")
    jupyter_sessions = relationship("JupyterSession", back_populates="user")
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

class Portfolio(Base):
    """Portfolio model for risk management."""
    __tablename__ = 'portfolios'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # Portfolio metadata
    portfolio_type = Column(String(50), nullable=False)  # equity, fixed_income, mixed, etc.
    base_currency = Column(String(3), default='USD', nullable=False)  # ISO currency code
    total_value = Column(Float, default=0.0)
    
    # Risk settings
    risk_tolerance = Column(String(20), default='medium')  # low, medium, high
    benchmark = Column(String(50))  # Benchmark index
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    risk_calculations = relationship("RiskCalculation", back_populates="portfolio")
    
    def __repr__(self):
        return f"<Portfolio(name='{self.name}', owner='{self.owner.username if self.owner else None}')>"

class Holding(Base):
    """Individual holding within a portfolio."""
    __tablename__ = 'holdings'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String(36), ForeignKey('portfolios.id'), nullable=False)
    
    # Asset information
    symbol = Column(String(20), nullable=False)  # Stock symbol, bond ISIN, etc.
    asset_type = Column(String(50), nullable=False)  # stock, bond, derivative, etc.
    asset_name = Column(String(200))
    sector = Column(String(50))
    
    # Position information
    quantity = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    market_value = Column(Float, nullable=False)  # quantity * current_price
    cost_basis = Column(Float, default=0.0)  # Original purchase price
    
    # Weights and allocation
    weight_percent = Column(Float, default=0.0)  # Percentage of portfolio
    
    # Risk metrics
    beta = Column(Float)  # Beta vs benchmark
    volatility = Column(Float)  # Historical volatility
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    price_updated_at = Column(DateTime(timezone=True))
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    
    def __repr__(self):
        return f"<Holding(symbol='{self.symbol}', quantity={self.quantity}, value={self.market_value})>"

class RiskCalculation(Base):
    """Risk calculation results for portfolios."""
    __tablename__ = 'risk_calculations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String(36), ForeignKey('portfolios.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # Risk metrics
    var_95 = Column(Float)  # Value at Risk 95%
    var_99 = Column(Float)  # Value at Risk 99%
    expected_shortfall = Column(Float)  # Expected Shortfall (Conditional VaR)
    volatility = Column(Float)  # Portfolio volatility
    sharpe_ratio = Column(Float)  # Sharpe ratio
    max_drawdown = Column(Float)  # Maximum drawdown
    
    # Additional metrics
    beta = Column(Float)  # Portfolio beta
    alpha = Column(Float)  # Portfolio alpha
    tracking_error = Column(Float)  # Tracking error vs benchmark
    information_ratio = Column(Float)  # Information ratio
    
    # Calculation metadata
    calculation_date = Column(DateTime(timezone=True), nullable=False)
    data_start_date = Column(DateTime(timezone=True))  # Start of data period used
    data_end_date = Column(DateTime(timezone=True))    # End of data period used
    methodology = Column(String(50), default='historical')  # historical, monte_carlo, parametric
    confidence_level = Column(Float, default=0.95)
    time_horizon_days = Column(Integer, default=1)  # Risk horizon in days
    
    # Results metadata
    total_portfolio_value = Column(Float)  # Portfolio value at calculation time
    currency = Column(String(3), default='USD')
    status = Column(String(20), default='completed')  # pending, completed, failed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="risk_calculations")
    user = relationship("User", back_populates="risk_calculations")
    
    def __repr__(self):
        return f"<RiskCalculation(portfolio_id='{self.portfolio_id}', var_95={self.var_95})>"

class MarketData(Base):
    """Market data for assets."""
    __tablename__ = 'market_data'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(20), nullable=False, index=True)
    data_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Price data
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, default=0)
    
    # Adjusted data
    adjusted_close = Column(Float)
    dividend_amount = Column(Float, default=0.0)
    split_coefficient = Column(Float, default=1.0)
    
    # Calculated metrics
    returns_1d = Column(Float)  # 1-day return
    volatility_20d = Column(Float)  # 20-day rolling volatility
    
    # Data quality
    data_source = Column(String(50), default='external_api')  # external_api, manual, bloomberg, etc.
    is_valid = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<MarketData(symbol='{self.symbol}', date='{self.data_date}', price={self.close_price})>"

class JupyterSession(Base):
    """JupyterHub session tracking."""
    __tablename__ = 'jupyter_sessions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # Session information
    server_name = Column(String(100), nullable=False)
    notebook_path = Column(String(500))
    session_status = Column(String(20), default='active')  # active, stopped, failed
    
    # Resource usage
    cpu_limit = Column(String(10), default='1')  # e.g., '500m', '1', '2'
    memory_limit = Column(String(10), default='2Gi')  # e.g., '1Gi', '2Gi', '4Gi'
    
    # Session tracking
    started_at = Column(DateTime(timezone=True), nullable=False)
    last_activity = Column(DateTime(timezone=True))
    stopped_at = Column(DateTime(timezone=True))
    
    # Environment information
    image_name = Column(String(200))  # Docker image used
    kernel_name = Column(String(50), default='python3')
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="jupyter_sessions")
    
    def __repr__(self):
        return f"<JupyterSession(user='{self.user.username if self.user else None}', server='{self.server_name}')>"

class AuditLog(Base):
    """Audit log for tracking user actions."""
    __tablename__ = 'audit_logs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'))
    
    # Action information
    action = Column(String(100), nullable=False)  # login, logout, calculate_risk, etc.
    resource = Column(String(200))  # Resource affected (portfolio_id, etc.)
    resource_type = Column(String(50))  # portfolio, user, system, etc.
    
    # Request information
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    
    # Action details
    details = Column(JSON, default=dict)  # Additional action-specific data
    status = Column(String(20), default='success')  # success, failed, error
    error_message = Column(Text)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<AuditLog(action='{self.action}', user='{self.user.username if self.user else 'system'}')>"

# Index definitions for better query performance
from sqlalchemy import Index

# Composite indexes for common queries
Index('idx_portfolio_owner_active', Portfolio.owner_id, Portfolio.is_active)
Index('idx_holding_portfolio_symbol', Holding.portfolio_id, Holding.symbol)
Index('idx_market_data_symbol_date', MarketData.symbol, MarketData.data_date)
Index('idx_risk_calc_portfolio_date', RiskCalculation.portfolio_id, RiskCalculation.calculation_date)
Index('idx_audit_user_timestamp', AuditLog.user_id, AuditLog.timestamp)
Index('idx_jupyter_user_status', JupyterSession.user_id, JupyterSession.session_status)

# Helper function to create all tables
def create_tables(engine):
    """Create all database tables."""
    Base.metadata.create_all(engine)
    
def drop_tables(engine):
    """Drop all database tables."""
    Base.metadata.drop_all(engine)