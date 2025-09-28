# JupyterHub Configuration Template
# This file configures JupyterHub for the Risk Platform environment

import os
import sys
from oauthenticator.generic import GenericOAuthenticator
from kubespawner import KubeSpawner
from jupyter_client.localinterfaces import public_ips

# Basic JupyterHub configuration
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_port = 8000
c.JupyterHub.port = 8000

# Database configuration
c.JupyterHub.db_url = os.environ.get('JUPYTERHUB_DATABASE_URL', 'sqlite:///jupyterhub.sqlite')

# Security configuration
c.JupyterHub.cookie_secret = bytes.fromhex(os.environ.get('JUPYTERHUB_COOKIE_SECRET', ''))
c.JupyterHub.api_token = os.environ.get('JUPYTERHUB_API_TOKEN', '')
c.CryptKeeper.keys = [bytes.fromhex(os.environ.get('JUPYTERHUB_CRYPT_KEY', ''))]

# Risk Platform environment configuration
environment = "${environment}"
risk_api_url = "${risk_api_url}"
shared_storage_path = "${shared_storage_path}"
corporate_domain = "${corporate_domain}"

# Spawner configuration - KubeSpawner for Kubernetes deployment
c.JupyterHub.spawner_class = KubeSpawner

# Kubernetes spawner configuration
c.KubeSpawner.image = 'jupyter/datascience-notebook:python-3.11'
c.KubeSpawner.start_timeout = 300
c.KubeSpawner.http_timeout = 60

# Resource limits based on environment
if environment == 'prod':
    c.KubeSpawner.cpu_limit = 2.0
    c.KubeSpawner.mem_limit = '4G'
    c.KubeSpawner.cpu_guarantee = 0.5
    c.KubeSpawner.mem_guarantee = '1G'
else:
    c.KubeSpawner.cpu_limit = 1.0
    c.KubeSpawner.mem_limit = '2G'
    c.KubeSpawner.cpu_guarantee = 0.25
    c.KubeSpawner.mem_guarantee = '512M'

# Storage configuration - Persistent volumes for user data
c.KubeSpawner.pvc_name_template = 'jupyterhub-user-{username}'
c.KubeSpawner.volume_mounts = [
    {
        'name': 'volume-{username}',
        'mountPath': '/home/jovyan/work',
        'subPath': 'work'
    },
    {
        'name': 'shared-storage',
        'mountPath': shared_storage_path,
        'readOnly': False
    }
]

c.KubeSpawner.volumes = [
    {
        'name': 'volume-{username}',
        'persistentVolumeClaim': {
            'claimName': 'jupyterhub-user-{username}'
        }
    },
    {
        'name': 'shared-storage',
        'persistentVolumeClaim': {
            'claimName': 'jupyterhub-shared-pvc'
        }
    }
]

# PVC template for user storage
c.KubeSpawner.storage_pvc_ensure = True
c.KubeSpawner.storage_capacity = '5Gi'
c.KubeSpawner.storage_access_modes = ['ReadWriteOnce']
c.KubeSpawner.storage_class = 'gp2'

# Environment variables for notebook servers
c.KubeSpawner.environment = {
    'RISK_API_URL': risk_api_url,
    'ENVIRONMENT': environment,
    'CORPORATE_DOMAIN': corporate_domain,
    'SHARED_STORAGE': shared_storage_path
}

# Security context for spawned pods
c.KubeSpawner.security_context = {
    'runAsUser': 1000,
    'runAsGroup': 1000,
    'fsGroup': 1000
}

# Service account for spawned pods
c.KubeSpawner.service_account = 'jupyterhub-user-pods'

# Network configuration
c.KubeSpawner.extra_pod_config = {
    'restartPolicy': 'OnFailure'
}

# Culling configuration - automatically stop idle servers
c.JupyterHub.services = [
    {
        'name': 'idle-culler',
        'admin': True,
        'command': [
            sys.executable,
            '-m', 'jupyterhub_idle_culler',
            '--timeout=3600',  # 1 hour
            '--cull-every=300',  # Check every 5 minutes
            '--concurrency=10',
            '--max-age=86400'  # Max 24 hours
        ]
    }
]

# User profiles for different types of users
c.KubeSpawner.profile_list = [
    {
        'display_name': 'Business User Environment',
        'description': 'Standard environment for business users with pre-installed risk analysis tools',
        'default': True,
        'kubespawner_override': {
            'image': f'{os.environ.get("ECR_REGISTRY", "")}/jupyterhub-notebook:business-user-latest',
            'cpu_limit': 1.0,
            'mem_limit': '2G',
            'environment': {
                'USER_TYPE': 'business',
                'RISK_API_URL': risk_api_url,
                'ENVIRONMENT': environment
            }
        }
    },
    {
        'display_name': 'Data Scientist Environment',
        'description': 'Advanced environment for data scientists with ML libraries and GPU access',
        'kubespawner_override': {
            'image': f'{os.environ.get("ECR_REGISTRY", "")}/jupyterhub-notebook:data-scientist-latest',
            'cpu_limit': 2.0,
            'mem_limit': '4G',
            'extra_resource_limits': {
                'nvidia.com/gpu': '1'  # GPU access for ML workloads
            },
            'environment': {
                'USER_TYPE': 'data_scientist',
                'RISK_API_URL': risk_api_url,
                'ENVIRONMENT': environment,
                'CUDA_VISIBLE_DEVICES': 'all'
            }
        }
    },
    {
        'display_name': 'Admin Environment',
        'description': 'Administrative environment with full system access',
        'kubespawner_override': {
            'image': f'{os.environ.get("ECR_REGISTRY", "")}/jupyterhub-notebook:admin-latest',
            'cpu_limit': 2.0,
            'mem_limit': '4G',
            'environment': {
                'USER_TYPE': 'admin',
                'RISK_API_URL': risk_api_url,
                'ENVIRONMENT': environment,
                'ADMIN_ACCESS': 'true'
            }
        }
    }
]

# Authentication configuration
# In production, configure corporate LDAP/SAML authentication
if environment == 'prod':
    # Corporate authentication (LDAP/SAML)
    c.JupyterHub.authenticator_class = GenericOAuthenticator
    c.GenericOAuthenticator.client_id = os.environ.get('OAUTH_CLIENT_ID', '')
    c.GenericOAuthenticator.client_secret = os.environ.get('OAUTH_CLIENT_SECRET', '')
    c.GenericOAuthenticator.oauth_callback_url = f'https://jupyterhub.{corporate_domain}/hub/oauth_callback'
    c.GenericOAuthenticator.authorize_url = os.environ.get('OAUTH_AUTHORIZE_URL', '')
    c.GenericOAuthenticator.token_url = os.environ.get('OAUTH_TOKEN_URL', '')
    c.GenericOAuthenticator.userdata_url = os.environ.get('OAUTH_USERDATA_URL', '')
    c.GenericOAuthenticator.username_key = 'username'
else:
    # Development authentication - dummy authenticator
    c.JupyterHub.authenticator_class = 'dummyauthenticator.DummyAuthenticator'
    c.DummyAuthenticator.password = 'password'

# Admin users configuration
c.Authenticator.admin_users = {
    'admin',
    'risk-admin',
    'platform-admin'
}

# Allowed users - in production, this would be managed via LDAP groups
c.Authenticator.allowed_users = {
    'business-user-1',
    'business-user-2',
    'data-scientist-1',
    'data-scientist-2',
    'risk-analyst-1',
    'risk-analyst-2'
}

# Logo and branding
c.JupyterHub.logo_file = '/etc/jupyterhub/logo.png'
c.JupyterHub.template_paths = ['/etc/jupyterhub/templates']

# Custom templates and styling
c.JupyterHub.extra_handlers = [
    (r'/custom/(.*)', 'tornado.web.StaticFileHandler', {'path': '/etc/jupyterhub/custom'})
]

# Hub configuration
c.JupyterHub.hub_connect_ip = '0.0.0.0'
c.JupyterHub.cleanup_servers = False

# Logging configuration
c.JupyterHub.log_level = 'INFO'
c.Application.log_level = 'INFO'

# Spawner logs
c.Spawner.debug = True if environment != 'prod' else False
c.LocalProcessSpawner.debug = True if environment != 'prod' else False

# Load balancer and proxy configuration
c.JupyterHub.bind_url = 'http://0.0.0.0:8000'
c.JupyterHub.hub_bind_url = 'http://0.0.0.0:8081'

# Proxy configuration
c.ConfigurableHTTPProxy.should_start = True
c.ConfigurableHTTPProxy.api_url = 'http://0.0.0.0:8001'

# Health check endpoint
c.JupyterHub.extra_handlers = c.JupyterHub.extra_handlers + [
    (r'/hub/health', 'jupyterhub.handlers.health.HealthCheckHandler')
]

# Statistics and monitoring
c.JupyterHub.statsd_host = os.environ.get('STATSD_HOST', '')
c.JupyterHub.statsd_port = int(os.environ.get('STATSD_PORT', '8125'))
c.JupyterHub.statsd_prefix = f'jupyterhub.{environment}'

# Concurrent spawn limit
c.JupyterHub.concurrent_spawn_limit = 10

# Active server limit per user
c.JupyterHub.active_server_limit = 2

# Allow named servers for different environments
c.JupyterHub.allow_named_servers = True
c.JupyterHub.named_server_limit_per_user = 3

# Notebook configuration
c.Spawner.default_url = '/lab'  # Use JupyterLab by default
c.Spawner.notebook_dir = '/home/jovyan'

# Custom configuration for Risk Platform integration
def pre_spawn_hook(spawner):
    """Pre-spawn hook to set up Risk Platform integration"""
    username = spawner.user.name
    
    # Set user-specific environment variables
    spawner.environment.update({
        'JUPYTERHUB_USER': username,
        'RISK_PLATFORM_USER_ID': username,
        'SHARED_NOTEBOOKS_PATH': f'{shared_storage_path}/notebooks',
        'SHARED_DATA_PATH': f'{shared_storage_path}/data',
        'SHARED_MODELS_PATH': f'{shared_storage_path}/models'
    })
    
    # Add user to specific groups based on username patterns
    if 'business' in username:
        spawner.environment['USER_ROLE'] = 'business_user'
    elif 'scientist' in username or 'analyst' in username:
        spawner.environment['USER_ROLE'] = 'data_scientist'
    elif 'admin' in username:
        spawner.environment['USER_ROLE'] = 'admin'
    else:
        spawner.environment['USER_ROLE'] = 'business_user'
    
    return spawner

c.Spawner.pre_spawn_hook = pre_spawn_hook

# Custom error pages
c.JupyterHub.template_vars = {
    'announcement': 'Welcome to Risk Platform JupyterHub',
    'custom_css': '''
        .navbar-brand {
            background-image: url('/custom/logo.png');
            background-size: contain;
            background-repeat: no-repeat;
        }
        .login-container {
            background-color: #f8f9fa;
        }
    '''
}

# Shutdown configuration
c.JupyterHub.cleanup_proxy = True
c.JupyterHub.cleanup_servers = False  # Keep user data