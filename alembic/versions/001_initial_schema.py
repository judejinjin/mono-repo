"""Initial migration - create all tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('role', sa.String(length=50), nullable=False),
    sa.Column('department', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)

    # Create portfolios table
    op.create_table('portfolios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('portfolio_type', sa.String(length=100), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('risk_limit', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('benchmark', sa.String(length=100), nullable=True),
    sa.Column('manager_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['manager_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_portfolios_name'), 'portfolios', ['name'], unique=False)
    op.create_index(op.f('ix_portfolios_portfolio_type'), 'portfolios', ['portfolio_type'], unique=False)

    # Create positions table
    op.create_table('positions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('portfolio_id', sa.Integer(), nullable=False),
    sa.Column('instrument_id', sa.String(length=50), nullable=False),
    sa.Column('instrument_type', sa.String(length=50), nullable=False),
    sa.Column('quantity', sa.Numeric(precision=18, scale=8), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=15, scale=4), nullable=False),
    sa.Column('market_value', sa.Numeric(precision=18, scale=2), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('trade_date', sa.Date(), nullable=False),
    sa.Column('maturity_date', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_positions_instrument_id'), 'positions', ['instrument_id'], unique=False)
    op.create_index(op.f('ix_positions_instrument_type'), 'positions', ['instrument_type'], unique=False)
    op.create_index(op.f('ix_positions_portfolio_id'), 'positions', ['portfolio_id'], unique=False)

    # Create market_data table
    op.create_table('market_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('instrument_id', sa.String(length=50), nullable=False),
    sa.Column('data_source', sa.String(length=100), nullable=False),
    sa.Column('price', sa.Numeric(precision=15, scale=4), nullable=False),
    sa.Column('bid', sa.Numeric(precision=15, scale=4), nullable=True),
    sa.Column('ask', sa.Numeric(precision=15, scale=4), nullable=True),
    sa.Column('volume', sa.BigInteger(), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_market_data_instrument_id'), 'market_data', ['instrument_id'], unique=False)
    op.create_index(op.f('ix_market_data_timestamp'), 'market_data', ['timestamp'], unique=False)

    # Create risk_calculations table
    op.create_table('risk_calculations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('portfolio_id', sa.Integer(), nullable=False),
    sa.Column('calculation_type', sa.String(length=100), nullable=False),
    sa.Column('risk_measure', sa.String(length=100), nullable=False),
    sa.Column('value', sa.Numeric(precision=18, scale=6), nullable=False),
    sa.Column('confidence_level', sa.Numeric(precision=5, scale=4), nullable=True),
    sa.Column('time_horizon', sa.Integer(), nullable=True),
    sa.Column('parameters', sa.JSON(), nullable=True),
    sa.Column('calculation_date', sa.Date(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_risk_calculations_calculation_date'), 'risk_calculations', ['calculation_date'], unique=False)
    op.create_index(op.f('ix_risk_calculations_calculation_type'), 'risk_calculations', ['calculation_type'], unique=False)
    op.create_index(op.f('ix_risk_calculations_portfolio_id'), 'risk_calculations', ['portfolio_id'], unique=False)

    # Create jupyter_sessions table
    op.create_table('jupyter_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.String(length=100), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('notebook_path', sa.String(length=500), nullable=False),
    sa.Column('kernel_id', sa.String(length=100), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('last_activity', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('session_id')
    )
    op.create_index(op.f('ix_jupyter_sessions_user_id'), 'jupyter_sessions', ['user_id'], unique=False)

    # Create audit_logs table
    op.create_table('audit_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('action', sa.String(length=200), nullable=False),
    sa.Column('resource_type', sa.String(length=100), nullable=True),
    sa.Column('resource_id', sa.String(length=100), nullable=True),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('user_agent', sa.String(length=500), nullable=True),
    sa.Column('details', sa.JSON(), nullable=True),
    sa.Column('result', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)

    # Create cache_entries table
    op.create_table('cache_entries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=500), nullable=False),
    sa.Column('value', sa.LargeBinary(), nullable=False),
    sa.Column('expiry', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('accessed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    op.create_index(op.f('ix_cache_entries_expiry'), 'cache_entries', ['expiry'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_cache_entries_expiry'), table_name='cache_entries')
    op.drop_table('cache_entries')
    
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_table('audit_logs')
    
    op.drop_index(op.f('ix_jupyter_sessions_user_id'), table_name='jupyter_sessions')
    op.drop_table('jupyter_sessions')
    
    op.drop_index(op.f('ix_risk_calculations_portfolio_id'), table_name='risk_calculations')
    op.drop_index(op.f('ix_risk_calculations_calculation_type'), table_name='risk_calculations')
    op.drop_index(op.f('ix_risk_calculations_calculation_date'), table_name='risk_calculations')
    op.drop_table('risk_calculations')
    
    op.drop_index(op.f('ix_market_data_timestamp'), table_name='market_data')
    op.drop_index(op.f('ix_market_data_instrument_id'), table_name='market_data')
    op.drop_table('market_data')
    
    op.drop_index(op.f('ix_positions_portfolio_id'), table_name='positions')
    op.drop_index(op.f('ix_positions_instrument_type'), table_name='positions')
    op.drop_index(op.f('ix_positions_instrument_id'), table_name='positions')
    op.drop_table('positions')
    
    op.drop_index(op.f('ix_portfolios_portfolio_type'), table_name='portfolios')
    op.drop_index(op.f('ix_portfolios_name'), table_name='portfolios')
    op.drop_table('portfolios')
    
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')