# API Clients

This directory contains client libraries for interacting with various APIs used in the mono-repo project.

## Available Clients

### 🔧 Risk API Client (`risk_api_client.py`)
Client for the Risk Management API service with comprehensive endpoint coverage.

**Features:**
- Complete coverage of all 14 Risk API endpoints
- Risk calculations (VaR, Expected Shortfall, Volatility)
- Portfolio management operations
- Market data processing
- Report generation
- Snowflake analytics queries
- Health checks and service information

**Usage:**
```python
from scripts.clients.risk_api_client import RiskAPIClient

# Initialize client for corporate environment
client = RiskAPIClient("http://internal-alb.genai.corporate/api")

# Check API health
health = client.health_check()

# Calculate risk metrics
risk = client.calculate_risk_metrics("portfolio_123")
print(f"VaR 95%: ${risk.var_95:,.2f}")
```

### 🌊 Airflow API Client (`airflow_api_client.py`)
Client for interacting with Apache Airflow API for workflow management.

**Features:**
- DAG triggering and monitoring
- Task status checking
- Workflow execution management
- External API integration
- Corporate network compatibility

**Usage:**
```python
from scripts.clients.airflow_api_client import AirflowAPIClient

# Initialize client
client = AirflowAPIClient(
    base_url="https://airflow.corporate.com",
    api_key="your-api-key"
)

# Trigger a DAG
result = client.trigger_dag("daily_risk_processing")
```

## 📖 Examples

### Risk API Examples (`risk_api_client_examples.py`)
Comprehensive examples demonstrating all Risk API client capabilities:

- Basic usage and health checks
- Risk calculations for portfolios
- Market data processing workflows
- Report generation examples
- Analytics and Snowflake queries
- Configuration access patterns

**Run Examples:**
```bash
cd scripts/clients
python risk_api_client_examples.py
```

## 🔧 Installation

Required dependencies are included in the base requirements:
```bash
pip install -r build/requirements/base.txt
```

## 🏗️ Project Structure

```
scripts/clients/
├── __init__.py                     # Package initialization with exports
├── risk_api_client.py             # Risk Management API client
├── risk_api_client_examples.py    # Usage examples for Risk API
├── airflow_api_client.py          # Apache Airflow API client
└── README.md                      # This documentation
```

## 🌐 Environment Configuration

All clients are configured for corporate intranet access:

- **Development**: `http://localhost:8000` for local testing
- **Corporate**: `http://internal-alb.genai.corporate/api` for production
- **VPN Compatible**: Works with existing corporate infrastructure

## 🔗 Integration

These clients integrate seamlessly with:
- Corporate Bamboo CI/CD pipelines
- Kubernetes deployments
- Internal ALB routing
- AWS services and resources
- Corporate security policies

## 🎯 Best Practices

1. **Error Handling**: All clients include comprehensive error handling
2. **Timeouts**: Configurable timeout settings for network resilience
3. **Logging**: Structured logging for debugging and monitoring
4. **Corporate Standards**: Follows corporate API integration patterns
5. **Security**: Compatible with corporate security requirements
