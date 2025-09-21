"""
Snowflake-specific database utilities and helpers.
"""

import logging
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
from libs.db import get_session
from config import get_db_config

logger = logging.getLogger(__name__)


class SnowflakeManager:
    """Manages Snowflake-specific operations and utilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_warehouse_info(self) -> Dict[str, Any]:
        """Get information about available Snowflake warehouses."""
        try:
            with get_session('snowflakedb') as session:
                # Query Snowflake system tables for warehouse information
                query = """
                SELECT warehouse_name, warehouse_size, state, 
                       auto_suspend, auto_resume, comment
                FROM INFORMATION_SCHEMA.WAREHOUSES 
                WHERE warehouse_name LIKE '%WH'
                ORDER BY warehouse_name
                """
                result = session.execute(query)
                warehouses = [dict(row._mapping) for row in result]
                
                self.logger.info(f"Retrieved {len(warehouses)} warehouse(s)")
                return {"warehouses": warehouses}
        except Exception as e:
            self.logger.error(f"Failed to get warehouse info: {e}")
            return {"warehouses": []}
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about Snowflake databases and schemas."""
        try:
            with get_session('snowflakedb') as session:
                # Query for databases
                db_query = """
                SELECT database_name, created, comment
                FROM INFORMATION_SCHEMA.DATABASES 
                WHERE database_name NOT IN ('INFORMATION_SCHEMA', 'SNOWFLAKE')
                ORDER BY database_name
                """
                result = session.execute(db_query)
                databases = [dict(row._mapping) for row in result]
                
                # Query for schemas in current database
                schema_query = """
                SELECT schema_name, created, comment
                FROM INFORMATION_SCHEMA.SCHEMATA
                WHERE catalog_name = CURRENT_DATABASE()
                ORDER BY schema_name
                """
                result = session.execute(schema_query)
                schemas = [dict(row._mapping) for row in result]
                
                return {
                    "databases": databases,
                    "schemas": schemas
                }
        except Exception as e:
            self.logger.error(f"Failed to get database info: {e}")
            return {"databases": [], "schemas": []}
    
    def get_table_info(self, schema_name: str = "PUBLIC") -> List[Dict[str, Any]]:
        """Get information about tables in a specific schema."""
        try:
            with get_session('snowflakedb') as session:
                query = """
                SELECT table_name, table_type, created, 
                       row_count, bytes, comment
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE table_schema = %(schema_name)s
                ORDER BY table_name
                """
                result = session.execute(query, {"schema_name": schema_name})
                tables = [dict(row._mapping) for row in result]
                
                self.logger.info(f"Retrieved {len(tables)} table(s) from schema {schema_name}")
                return tables
        except Exception as e:
            self.logger.error(f"Failed to get table info for schema {schema_name}: {e}")
            return []
    
    def optimize_warehouse_usage(self) -> Dict[str, Any]:
        """Analyze and suggest warehouse usage optimizations."""
        try:
            with get_session('snowflakedb') as session:
                # Query warehouse usage over the last 24 hours
                usage_query = """
                SELECT warehouse_name, 
                       SUM(credits_used) as total_credits,
                       AVG(avg_running) as avg_running_queries,
                       COUNT(*) as query_count
                FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY 
                WHERE start_time >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
                GROUP BY warehouse_name
                ORDER BY total_credits DESC
                """
                result = session.execute(usage_query)
                usage_stats = [dict(row._mapping) for row in result]
                
                # Generate optimization suggestions
                suggestions = []
                for stat in usage_stats:
                    if stat['total_credits'] > 10:  # High usage threshold
                        if stat['avg_running_queries'] < 1:
                            suggestions.append({
                                "warehouse": stat['warehouse_name'],
                                "suggestion": "Consider reducing warehouse size or increasing auto-suspend time",
                                "reason": "Low query concurrency with high credit usage"
                            })
                
                return {
                    "usage_stats": usage_stats,
                    "optimization_suggestions": suggestions
                }
        except Exception as e:
            self.logger.error(f"Failed to analyze warehouse usage: {e}")
            return {"usage_stats": [], "optimization_suggestions": []}
    
    def execute_analytics_query(self, query: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a large analytics query with proper error handling and monitoring."""
        try:
            with get_session('snowflakedb') as session:
                self.logger.info(f"Executing analytics query: {query[:100]}...")
                
                # Set session parameters for large queries
                session.execute("ALTER SESSION SET QUERY_TAG = 'analytics_workload'")
                session.execute("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 3600")  # 1 hour
                
                result = session.execute(query, parameters or {})
                rows = [dict(row._mapping) for row in result]
                
                self.logger.info(f"Query completed successfully, returned {len(rows)} rows")
                
                return {
                    "status": "success",
                    "row_count": len(rows),
                    "data": rows,
                    "query_info": {
                        "query_tag": "analytics_workload",
                        "timeout_seconds": 3600
                    }
                }
        except Exception as e:
            self.logger.error(f"Analytics query failed: {e}")
            return {
                "status": "error",
                "error_message": str(e),
                "row_count": 0,
                "data": []
            }
    
    def load_data_from_s3(self, s3_path: str, table_name: str, file_format: str = "CSV") -> bool:
        """Load data from S3 into Snowflake table."""
        try:
            with get_session('snowflakedb') as session:
                # Create file format if it doesn't exist
                create_format_query = f"""
                CREATE FILE FORMAT IF NOT EXISTS {file_format}_FORMAT
                TYPE = '{file_format}'
                FIELD_DELIMITER = ','
                SKIP_HEADER = 1
                NULL_IF = ('NULL', 'null', '')
                EMPTY_FIELD_AS_NULL = TRUE
                """
                session.execute(create_format_query)
                
                # Load data using COPY INTO
                copy_query = f"""
                COPY INTO {table_name}
                FROM '{s3_path}'
                FILE_FORMAT = {file_format}_FORMAT
                ON_ERROR = 'CONTINUE'
                """
                result = session.execute(copy_query)
                
                # Get load statistics
                rows_loaded = result.fetchone()[0] if result.rowcount > 0 else 0
                
                self.logger.info(f"Successfully loaded {rows_loaded} rows into {table_name}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to load data from S3: {e}")
            return False


# Global Snowflake manager instance
_snowflake_manager = SnowflakeManager()

# Public API
def get_warehouse_info() -> Dict[str, Any]:
    """Get Snowflake warehouse information."""
    return _snowflake_manager.get_warehouse_info()

def get_database_info() -> Dict[str, Any]:
    """Get Snowflake database information."""
    return _snowflake_manager.get_database_info()

def get_table_info(schema_name: str = "PUBLIC") -> List[Dict[str, Any]]:
    """Get table information for a schema."""
    return _snowflake_manager.get_table_info(schema_name)

def optimize_warehouse_usage() -> Dict[str, Any]:
    """Get warehouse usage optimization suggestions."""
    return _snowflake_manager.optimize_warehouse_usage()

def execute_analytics_query(query: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
    """Execute analytics query on Snowflake."""
    return _snowflake_manager.execute_analytics_query(query, parameters)

def load_data_from_s3(s3_path: str, table_name: str, file_format: str = "CSV") -> bool:
    """Load data from S3 into Snowflake."""
    return _snowflake_manager.load_data_from_s3(s3_path, table_name, file_format)
