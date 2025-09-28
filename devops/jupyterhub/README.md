# DevOps Automation for JupyterHub

This directory contains automation scripts for JupyterHub operations, monitoring, and maintenance.

## Scripts Overview

### Core Operations
- `monitor_jupyterhub.py` - Real-time monitoring and health checks
- `backup_jupyterhub.py` - Automated backup of user data and configurations
- `cleanup_sessions.py` - Automated cleanup of idle sessions and resources
- `user_management.py` - User provisioning and deprovisioning automation
- `generate_jupyterhub_diagrams.py` - Architecture and operational diagrams

### Monitoring & Alerts
- Real-time resource monitoring (CPU, Memory, Storage)
- User session tracking and analytics
- Performance metrics collection
- Automated alerting for resource thresholds
- Health check automation across all environments

### Maintenance Operations
- Automated session cleanup for idle users
- Storage optimization and cleanup
- Log rotation and archival
- Database maintenance and optimization
- User data backup and recovery

### User Management
- Automated user onboarding from corporate directory
- Role-based access provisioning
- Session limit enforcement
- Resource quota management
- Deprovisioning automation

## Usage

All scripts support environment-specific operations:
```bash
# Monitor production environment
python monitor_jupyterhub.py --environment prod

# Cleanup development environment
python cleanup_sessions.py --environment dev --dry-run

# Generate comprehensive diagrams
python generate_jupyterhub_diagrams.py --output-dir ../docs/diagrams/
```

## Configuration

Scripts read configuration from:
- Environment variables
- `../config/` directory
- Kubernetes secrets and configmaps
- AWS Parameter Store (for production)

## Integration

These scripts integrate with:
- Risk Platform monitoring systems
- Corporate identity management
- AWS CloudWatch and alerting
- Kubernetes cluster management
- Business intelligence dashboards