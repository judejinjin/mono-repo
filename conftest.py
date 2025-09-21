# Global test configuration for Python tests
import pytest
import asyncio
import os
import sys
from unittest.mock import Mock

# Configure pytest for async testing
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Mock AWS services for testing
@pytest.fixture
def mock_boto3_client():
    """Mock boto3 client for AWS services"""
    return Mock()

@pytest.fixture
def mock_redis_client():
    """Mock Redis client"""
    return Mock()

@pytest.fixture
def mock_database_session():
    """Mock database session"""
    return Mock()

# Test environment configuration
@pytest.fixture(autouse=True)
def test_environment():
    """Set up test environment variables"""
    os.environ.update({
        'ENVIRONMENT': 'test',
        'DATABASE_URL': 'sqlite:///:memory:',
        'REDIS_URL': 'redis://localhost:6379/15',
        'AWS_ACCESS_KEY_ID': 'test',
        'AWS_SECRET_ACCESS_KEY': 'test',
        'AWS_DEFAULT_REGION': 'us-east-1'
    })
    yield
    # Cleanup after tests
