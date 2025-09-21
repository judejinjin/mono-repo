# Configuration Management Module

This module handles environment-specific configuration loading and management.

## Features
- Environment detection via ENV variable
- Hierarchical configuration loading
- Secrets management integration
- Database connection configuration
- Cloud service configuration

## Usage
```python
from config import get_config, get_db_config, get_cloud_config

# Get general configuration
config = get_config()

# Get database configuration
db_config = get_db_config('riskdb')

# Get cloud service configuration
cloud_config = get_cloud_config('s3')
```

## Environment Structure
- `dev`: Development environment
- `uat`: UAT environment
- `prod`: Production environment

Each environment has its own configuration file in the respective subdirectory.
