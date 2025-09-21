"""
API Clients Package

This package contains client libraries for various APIs used in the mono-repo project.

Available Clients:
- AirflowAPIClient: Client for interacting with Apache Airflow API
- RiskAPIClient: Client for the Risk Management API service

Usage:
    from scripts.clients.risk_api_client import RiskAPIClient
    from scripts.clients.airflow_api_client import AirflowAPIClient
    
    # Risk API client
    risk_client = RiskAPIClient("http://internal-alb.genai.corporate/api")
    
    # Airflow API client  
    airflow_client = AirflowAPIClient("http://airflow.corporate.com")
"""

__version__ = "1.0.0"
__author__ = "GenAI Team"

# Import main client classes for easy access
try:
    from .risk_api_client import RiskAPIClient, RiskMetrics, Portfolio
    from .airflow_api_client import AirflowAPIClient
    
    __all__ = [
        'RiskAPIClient',
        'RiskMetrics', 
        'Portfolio',
        'AirflowAPIClient'
    ]
except ImportError:
    # Handle import errors gracefully during development
    __all__ = []
