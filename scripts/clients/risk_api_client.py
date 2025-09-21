#!/usr/bin/env python3
"""
Risk API Client
Python client for interacting with the Risk Management API service.
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RiskMetrics:
    """Risk metrics data structure."""
    portfolio_id: str
    var_95: float
    var_99: float
    expected_shortfall: float
    volatility: float
    sharpe_ratio: float
    calculated_at: str


@dataclass
class Portfolio:
    """Portfolio data structure."""
    id: str
    name: str
    description: Optional[str] = None


class RiskAPIClient:
    """Client for interacting with the Risk Management API."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize the Risk API client.
        
        Args:
            base_url: Base URL of the Risk API (e.g., 'http://localhost:8000' or 'http://internal-alb.corporate.com/api')
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.exceptions.RequestException: On request failure
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {method} {url} - {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status.
        
        Returns:
            Health status information
        """
        logger.info("Checking API health...")
        return self._make_request("GET", "/health")
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get service information.
        
        Returns:
            Service information including version and status
        """
        logger.info("Getting service information...")
        return self._make_request("GET", "/")
    
    def calculate_risk_metrics(self, portfolio_id: str, calculation_date: Optional[str] = None) -> RiskMetrics:
        """
        Calculate risk metrics for a portfolio.
        
        Args:
            portfolio_id: Portfolio identifier
            calculation_date: Optional calculation date (ISO format)
            
        Returns:
            Risk metrics for the portfolio
        """
        logger.info(f"Calculating risk metrics for portfolio: {portfolio_id}")
        
        payload = {"portfolio_id": portfolio_id}
        if calculation_date:
            payload["calculation_date"] = calculation_date
            
        response = self._make_request(
            "POST", 
            "/api/v1/risk/calculate",
            json=payload
        )
        
        return RiskMetrics(**response)
    
    def list_portfolios(self) -> List[Portfolio]:
        """
        List all available portfolios.
        
        Returns:
            List of available portfolios
        """
        logger.info("Listing portfolios...")
        response = self._make_request("GET", "/api/v1/portfolios")
        
        return [Portfolio(**portfolio) for portfolio in response.get("portfolios", [])]
    
    def get_portfolio_risk(self, portfolio_id: str) -> RiskMetrics:
        """
        Get cached risk metrics for a portfolio.
        
        Args:
            portfolio_id: Portfolio identifier
            
        Returns:
            Cached risk metrics for the portfolio
        """
        logger.info(f"Getting portfolio risk for: {portfolio_id}")
        response = self._make_request("GET", f"/api/v1/portfolios/{portfolio_id}/risk")
        
        return RiskMetrics(**response)
    
    def process_market_data(self, date_str: str, asset_classes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process market data for a specific date.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            asset_classes: Optional list of asset classes to process
            
        Returns:
            Processing status and results
        """
        logger.info(f"Processing market data for date: {date_str}")
        
        payload = {"date": date_str}
        if asset_classes:
            payload["asset_classes"] = asset_classes
            
        return self._make_request(
            "POST",
            "/api/v1/market-data/process",
            json=payload
        )
    
    def get_market_data_status(self, date_str: str) -> Dict[str, Any]:
        """
        Get market data processing status for a date.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            Market data processing status
        """
        logger.info(f"Getting market data status for date: {date_str}")
        return self._make_request("GET", f"/api/v1/market-data/status/{date_str}")
    
    def generate_report(self, report_type: str, start_date: str, 
                       end_date: Optional[str] = None, 
                       parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a report.
        
        Args:
            report_type: Type of report to generate ('daily_risk', 'performance')
            start_date: Start date in YYYY-MM-DD format
            end_date: Optional end date in YYYY-MM-DD format
            parameters: Optional additional parameters
            
        Returns:
            Generated report data
        """
        logger.info(f"Generating {report_type} report from {start_date} to {end_date}")
        
        payload = {
            "report_type": report_type,
            "start_date": start_date
        }
        
        if end_date:
            payload["end_date"] = end_date
        if parameters:
            payload["parameters"] = parameters
            
        return self._make_request(
            "POST",
            "/api/v1/reports/generate",
            json=payload
        )
    
    def list_available_reports(self) -> List[Dict[str, Any]]:
        """
        List available report types.
        
        Returns:
            List of available report types with descriptions
        """
        logger.info("Listing available reports...")
        response = self._make_request("GET", "/api/v1/reports/list")
        return response.get("reports", [])
    
    def list_databases(self) -> List[Dict[str, Any]]:
        """
        List available databases.
        
        Returns:
            List of available databases
        """
        logger.info("Listing databases...")
        response = self._make_request("GET", "/api/v1/databases")
        return response.get("databases", [])
    
    def list_snowflake_warehouses(self) -> List[Dict[str, Any]]:
        """
        List available Snowflake warehouses.
        
        Returns:
            List of available Snowflake warehouses
        """
        logger.info("Listing Snowflake warehouses...")
        response = self._make_request("GET", "/api/v1/snowflake/warehouses")
        return response.get("warehouses", [])
    
    def execute_snowflake_query(self, query: str, warehouse: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a query on Snowflake.
        
        Args:
            query: SQL query to execute
            warehouse: Optional warehouse to use
            
        Returns:
            Query results
        """
        logger.info("Executing Snowflake query...")
        
        payload = {"query": query}
        if warehouse:
            payload["warehouse"] = warehouse
            
        return self._make_request(
            "POST",
            "/api/v1/analytics/snowflake-query",
            json=payload
        )
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get data summary and statistics.
        
        Returns:
            Data summary information
        """
        logger.info("Getting data summary...")
        return self._make_request("GET", "/api/v1/analytics/data-summary")
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get API configuration information.
        
        Returns:
            API configuration
        """
        logger.info("Getting API configuration...")
        return self._make_request("GET", "/api/v1/config")


def main():
    """
    Example usage of the Risk API Client.
    """
    # Example configuration for different environments
    configs = {
        "local": "http://localhost:8000",
        "corporate": "http://internal-alb.genai.corporate/api",
        "dev": "http://internal-alb.genai.corporate/api"  # Corporate intranet access
    }
    
    # Use corporate environment by default
    api_url = configs.get("corporate", "http://localhost:8000")
    
    try:
        # Initialize client
        client = RiskAPIClient(api_url)
        
        print("🚀 Risk API Client Example")
        print("=" * 40)
        
        # Health check
        health = client.health_check()
        print(f"✅ Health Check: {health['status']}")
        
        # Service info
        info = client.get_service_info()
        print(f"📊 Service: {info['service']} v{info['version']}")
        
        # List portfolios
        portfolios = client.list_portfolios()
        print(f"📁 Available Portfolios: {len(portfolios)}")
        for portfolio in portfolios[:3]:  # Show first 3
            print(f"   - {portfolio.id}: {portfolio.name}")
        
        # Calculate risk metrics for first portfolio (if available)
        if portfolios:
            portfolio_id = portfolios[0].id
            print(f"\n🧮 Calculating risk metrics for: {portfolio_id}")
            
            try:
                risk_metrics = client.calculate_risk_metrics(portfolio_id)
                print(f"   VaR 95%: {risk_metrics.var_95:.4f}")
                print(f"   VaR 99%: {risk_metrics.var_99:.4f}")
                print(f"   Expected Shortfall: {risk_metrics.expected_shortfall:.4f}")
                print(f"   Volatility: {risk_metrics.volatility:.4f}")
                print(f"   Sharpe Ratio: {risk_metrics.sharpe_ratio:.4f}")
            except Exception as e:
                print(f"   ⚠️ Risk calculation failed: {e}")
        
        # List available reports
        reports = client.list_available_reports()
        print(f"\n📋 Available Reports: {len(reports)}")
        for report in reports:
            print(f"   - {report['type']}: {report['name']}")
        
        # Generate daily risk report
        if reports:
            try:
                today = date.today().isoformat()
                report = client.generate_report("daily_risk", today)
                print(f"✅ Generated daily risk report for {today}")
            except Exception as e:
                print(f"⚠️ Report generation failed: {e}")
        
        # Get data summary
        try:
            summary = client.get_data_summary()
            print(f"\n📈 Data Summary: {summary.get('total_records', 'N/A')} records")
        except Exception as e:
            print(f"⚠️ Data summary failed: {e}")
        
        print("\n🎉 Risk API Client example completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
