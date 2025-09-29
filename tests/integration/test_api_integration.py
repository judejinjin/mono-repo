"""
Integration Tests for the Enhanced Risk Management API
Tests end-to-end functionality with real implementations
"""

import sys
import pytest
import asyncio
from pathlib import Path
from typing import Dict, Any
import httpx
from fastapi.testclient import TestClient
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.test_framework import TestBase, MockSnowflakeConnector, MockMarketDataProvider, MockRiskEngine
from services.risk_api_enhanced import app


class TestRiskAPIIntegration(TestBase):
    """Integration tests for the enhanced Risk Management API."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = TestClient(app)
        
        # Mock the data sources for consistent testing
        import services.risk_api_enhanced as api_module
        api_module.snowflake_connector = cls.mock_snowflake
        api_module.market_data_provider = cls.mock_market_data
        api_module.risk_engine = cls.mock_risk_engine
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct information."""
        response = self.client.get("/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("service", data)
        self.assertIn("version", data)
        self.assertIn("features", data)
        self.assertEqual(data["service"], "Enhanced Risk Management API")
        self.assertEqual(data["version"], "2.0.0")
    
    def test_health_endpoints(self):
        """Test health check endpoints."""
        # Test basic health
        response = self.client.get("/health")
        self.assertIn(response.status_code, [200, 503])  # May fail if dependencies not available
        
        # Test liveness probe
        response = self.client.get("/health/liveness")
        self.assertEqual(response.status_code, 200)
        
        # Test readiness probe  
        response = self.client.get("/health/readiness")
        self.assertIn(response.status_code, [200, 503])
    
    def test_metrics_endpoint(self):
        """Test Prometheus metrics endpoint."""
        response = self.client.get("/metrics")
        
        # Should return metrics or graceful failure
        self.assertIn(response.status_code, [200, 503])
        
        if response.status_code == 200:
            self.assertIn("text/plain", response.headers.get("content-type", ""))
    
    def test_login_development_mode(self):
        """Test login in development mode."""
        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        
        response = self.client.post("/auth/login", json=login_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("access_token", data)
        self.assertIn("token_type", data)
        self.assertIn("user", data)
        self.assertEqual(data["token_type"], "bearer")
    
    def test_portfolio_risk_calculation(self):
        """Test portfolio risk calculation endpoint."""
        # First login to get token
        login_response = self.client.post("/auth/login", json={
            "username": "test_user", 
            "password": "test_password"
        })
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test risk calculation
        risk_request = {
            "portfolio_id": "TEST_PORTFOLIO",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31"
        }
        
        response = self.client.post(
            "/api/v1/risk/calculate",
            json=risk_request,
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Validate response structure
        required_fields = [
            "portfolio_id", "calculation_date", "var_95", "var_99",
            "expected_shortfall", "volatility", "sharpe_ratio", 
            "max_drawdown", "beta", "alpha"
        ]
        
        for field in required_fields:
            self.assertIn(field, data)
        
        # Validate data types and ranges
        self.assertEqual(data["portfolio_id"], "TEST_PORTFOLIO")
        self.assertIsInstance(data["var_95"], (int, float))
        self.assertGreaterEqual(data["var_95"], 0)
        self.assertGreaterEqual(data["var_99"], data["var_95"])
    
    def test_stress_testing(self):
        """Test stress testing endpoint."""
        # Login first
        login_response = self.client.post("/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test stress test
        stress_request = {
            "portfolio_id": "TEST_PORTFOLIO",
            "scenarios": {
                "market_crash": -0.30,
                "volatility_spike": 0.60
            }
        }
        
        response = self.client.post(
            "/api/v1/risk/stress-test",
            json=stress_request,
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("portfolio_id", data)
        self.assertIn("stress_test_results", data)
        self.assertIn("calculated_at", data)
        
        # Validate stress test results
        stress_results = data["stress_test_results"]
        self.assertIsInstance(stress_results, dict)
        
        for scenario in stress_request["scenarios"]:
            self.assertIn(scenario, stress_results)
    
    def test_market_data_endpoints(self):
        """Test market data endpoints."""
        # Login
        login_response = self.client.post("/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test historical data
        market_request = {
            "symbols": ["AAPL", "MSFT"],
            "start_date": "2023-01-01",
            "end_date": "2023-01-31"
        }
        
        response = self.client.post(
            "/api/v1/market-data/prices",
            json=market_request,
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("symbols", data)
        self.assertIn("data_points", data)
        self.assertIn("data", data)
        self.assertEqual(data["symbols"], ["AAPL", "MSFT"])
        
        # Test latest price
        response = self.client.get(
            "/api/v1/market-data/latest/AAPL",
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("symbol", data)
        self.assertIn("price", data)
        self.assertIn("change", data)
        self.assertEqual(data["symbol"], "AAPL")
    
    def test_snowflake_integration(self):
        """Test Snowflake integration endpoints."""
        # Login
        login_response = self.client.post("/auth/login", json={
            "username": "admin_user",
            "password": "admin_password"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test warehouse information
        response = self.client.get(
            "/api/v1/snowflake/warehouses",
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("warehouses", data)
        self.assertIsInstance(data["warehouses"], list)
        
        if data["warehouses"]:
            warehouse = data["warehouses"][0]
            self.assertIn("name", warehouse)
            self.assertIn("state", warehouse)
        
        # Test databases
        response = self.client.get(
            "/api/v1/snowflake/databases",
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("databases", data)
        self.assertIsInstance(data["databases"], list)
        
        # Test analytics query
        query_request = {
            "query": "SELECT 1 as test_column",
            "use_cache": False
        }
        
        response = self.client.post(
            "/api/v1/snowflake/query",
            json=query_request,
            headers=headers
        )
        
        # May succeed or fail depending on mock implementation
        self.assertIn(response.status_code, [200, 500, 503])
    
    def test_portfolio_management(self):
        """Test portfolio management endpoints.""" 
        # Login
        login_response = self.client.post("/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test portfolio list
        response = self.client.get(
            "/api/v1/portfolios",
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("portfolios", data)
        self.assertIn("count", data)
        self.assertIsInstance(data["portfolios"], list)
        self.assertGreaterEqual(data["count"], 0)
    
    def test_system_info(self):
        """Test system information endpoint."""
        response = self.client.get("/api/v1/system/info")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("service", data)
        self.assertIn("version", data) 
        self.assertIn("environment", data)
        self.assertIn("features", data)
        self.assertIn("data_sources", data)
        
        # Validate features
        features = data["features"]
        self.assertIsInstance(features, dict)
        
        expected_features = [
            "snowflake_integration", "market_data_provider", 
            "risk_engine", "prometheus_metrics", "health_checks"
        ]
        
        for feature in expected_features:
            self.assertIn(feature, features)
            self.assertIsInstance(features[feature], bool)
    
    def test_unauthorized_access(self):
        """Test that endpoints require authentication."""
        # Test without token
        response = self.client.post("/api/v1/risk/calculate", json={
            "portfolio_id": "TEST"
        })
        
        self.assertEqual(response.status_code, 403)  # Or 401 depending on implementation
        
        # Test with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.post("/api/v1/risk/calculate", json={
            "portfolio_id": "TEST"
        }, headers=headers)
        
        self.assertIn(response.status_code, [401, 403])
    
    def test_input_validation(self):
        """Test input validation."""
        # Login
        login_response = self.client.post("/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test missing required fields
        response = self.client.post(
            "/api/v1/risk/calculate",
            json={},  # Missing portfolio_id
            headers=headers
        )
        
        self.assertEqual(response.status_code, 422)  # Validation error
        
        # Test invalid date format
        response = self.client.post(
            "/api/v1/market-data/prices",
            json={
                "symbols": ["AAPL"],
                "start_date": "invalid-date"
            },
            headers=headers
        )
        
        # Should handle gracefully
        self.assertIn(response.status_code, [400, 422, 500])
    
    def test_error_handling(self):
        """Test error handling and responses.""" 
        # Login
        login_response = self.client.post("/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test non-existent portfolio
        response = self.client.post(
            "/api/v1/risk/calculate",
            json={"portfolio_id": "NON_EXISTENT_PORTFOLIO"},
            headers=headers
        )
        
        # Should handle gracefully (may return empty results or 404)
        self.assertIn(response.status_code, [200, 404, 500])
        
        if response.status_code == 200:
            # If successful, should have valid structure
            data = response.json()
            self.assertIn("portfolio_id", data)


@pytest.mark.asyncio
class TestAsyncRiskAPI:
    """Async integration tests."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup for each test method."""
        self.client = TestClient(app)
    
    async def test_concurrent_risk_calculations(self):
        """Test multiple concurrent risk calculations."""
        # Login
        login_response = self.client.post("/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create multiple concurrent requests
        portfolios = ["PORTFOLIO_1", "PORTFOLIO_2", "PORTFOLIO_3"]
        
        async with httpx.AsyncClient(app=app, base_url="http://test") as async_client:
            # Prepare concurrent requests
            tasks = []
            for portfolio in portfolios:
                request_data = {"portfolio_id": portfolio}
                task = async_client.post(
                    "/api/v1/risk/calculate",
                    json=request_data,
                    headers=headers
                )
                tasks.append(task)
            
            # Execute concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Validate responses
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    pytest.fail(f"Request {i} failed with exception: {response}")
                
                assert response.status_code == 200
                data = response.json()
                assert data["portfolio_id"] == portfolios[i]


if __name__ == "__main__":
    unittest.main()