"""
Database abstraction layer for the mono-repo project.
Provides unified database access across different environments.
"""

import logging
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from config import get_db_config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self):
        self._engines = {}
        self._session_factories = {}
    
    def _create_engine(self, db_name: str):
        """Create database engine for given database."""
        config = get_db_config(db_name)
        
        # Build connection URL
        engine_type = config['engine']
        
        if engine_type == 'postgresql':
            username = config.get('username')
            password = config.get('password')
            host = config['host']
            port = config['port']
            database = config['database']
            url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            
        elif engine_type == 'snowflake':
            username = config.get('username')
            password = config.get('password')
            account = config['account']
            warehouse = config['warehouse']
            database = config['database']
            schema = config.get('schema', 'PUBLIC')
            url = f"snowflake://{username}:{password}@{account}/{database}/{schema}?warehouse={warehouse}"
            
        else:
            raise ValueError(f"Unsupported database engine: {engine_type}")
        
        # Create engine with connection pooling
        engine = create_engine(
            url,
            poolclass=QueuePool,
            pool_size=config.get('pool_size', 10),
            max_overflow=config.get('max_overflow', 20),
            pool_timeout=config.get('pool_timeout', 30),
            pool_recycle=3600,  # Recycle connections every hour
            echo=config.get('echo', False)
        )
        
        return engine
    
    def get_engine(self, db_name: str):
        """Get database engine for given database."""
        if db_name not in self._engines:
            self._engines[db_name] = self._create_engine(db_name)
        return self._engines[db_name]
    
    def get_session_factory(self, db_name: str):
        """Get session factory for given database."""
        if db_name not in self._session_factories:
            engine = self.get_engine(db_name)
            self._session_factories[db_name] = sessionmaker(bind=engine)
        return self._session_factories[db_name]
    
    @contextmanager
    def get_session(self, db_name: str):
        """Get database session with automatic cleanup."""
        session_factory = self.get_session_factory(db_name)
        session = session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def execute_query(self, db_name: str, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute raw SQL query and return results."""
        with self.get_session(db_name) as session:
            result = session.execute(text(query), params or {})
            return [dict(row._mapping) for row in result]
    
    def execute_update(self, db_name: str, query: str, params: Optional[Dict] = None) -> int:
        """Execute update/insert/delete query and return affected rows."""
        with self.get_session(db_name) as session:
            result = session.execute(text(query), params or {})
            return result.rowcount


# Global database manager instance
_db_manager = DatabaseManager()

# Public API
def get_engine(db_name: str):
    """Get database engine."""
    return _db_manager.get_engine(db_name)

def get_session_factory(db_name: str):
    """Get session factory."""
    return _db_manager.get_session_factory(db_name)

@contextmanager
def get_session(db_name: str):
    """Get database session context manager."""
    with _db_manager.get_session(db_name) as session:
        yield session

def execute_query(db_name: str, query: str, params: Optional[Dict] = None) -> List[Dict]:
    """Execute query and return results."""
    return _db_manager.execute_query(db_name, query, params)

def execute_update(db_name: str, query: str, params: Optional[Dict] = None) -> int:
    """Execute update query."""
    return _db_manager.execute_update(db_name, query, params)


# Convenience functions for specific databases
def get_riskdb_session():
    """Get Risk database session."""
    return get_session('riskdb')

def get_analyticsdb_session():
    """Get Analytics database session."""
    return get_session('analyticsdb')

def get_snowflakedb_session():
    """Get Snowflake database session."""
    return get_session('snowflakedb')
