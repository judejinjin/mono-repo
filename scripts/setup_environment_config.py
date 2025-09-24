#!/usr/bin/env python3
"""
Environment Configuration Setup Script
Populates AWS Parameter Store with environment-specific configuration values during deployment.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from libs.cloud.parameter_store import ParameterStoreManager
from config import get_config, get_environment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnvironmentConfigSetup:
    """Manages environment configuration setup in Parameter Store."""
    
    def __init__(self, environment: str, region_name: str = None):
        self.environment = environment
        self.parameter_manager = ParameterStoreManager(region_name)
        
    def populate_terraform_parameters(self) -> Dict[str, bool]:
        """Populate Terraform-related parameters."""
        # Get values from environment variables (legacy config/.env support)
        terraform_params = {
            'aws_account_id': os.getenv('AWS_ACCOUNT_ID', ''),
            'aws_region': os.getenv('TF_VAR_aws_region', os.getenv('AWS_DEFAULT_REGION', 'us-east-1')),
            'project_name': os.getenv('TF_VAR_project_name', f'mono-repo-{self.environment}'),
            'vpc_cidr': self._get_vpc_cidr_for_environment()
        }
        
        return self.parameter_manager.put_environment_parameters(
            self.environment,
            'terraform',
            terraform_params
        )
    
    def populate_eks_parameters(self) -> Dict[str, bool]:
        """Populate EKS-related parameters."""
        eks_params = {
            'cluster_name': os.getenv('EKS_CLUSTER_NAME', f'mono-repo-{self.environment}-eks-{self.environment}'),
            'node_group_min_size': self._get_node_group_size('min'),
            'node_group_max_size': self._get_node_group_size('max'),
            'node_group_desired_size': self._get_node_group_size('desired'),
            'kubernetes_version': '1.27'
        }
        
        return self.parameter_manager.put_environment_parameters(
            self.environment,
            'eks',
            eks_params
        )
    
    def populate_rds_parameters(self) -> Dict[str, bool]:
        """Populate RDS-related parameters."""
        rds_params = {
            'db_name': os.getenv('RDS_DB_NAME', f'monorepodb_{self.environment}'),
            'username': os.getenv('RDS_USERNAME', 'dbadmin'),
            'instance_class': self._get_rds_instance_class(),
            'allocated_storage': self._get_rds_storage(),
            'multi_az': str(self.environment == 'prod').lower(),
            'backup_retention_period': '7' if self.environment == 'dev' else '30'
        }
        
        # Secure parameters (will be stored as SecureString)
        secure_rds_params = ['password']
        rds_secure_params = {
            'password': os.getenv('RDS_PASSWORD', 'change_this_password_in_production')
        }
        
        # Store regular parameters
        results = self.parameter_manager.put_environment_parameters(
            self.environment,
            'rds',
            rds_params
        )
        
        # Store secure parameters
        secure_results = self.parameter_manager.put_environment_parameters(
            self.environment,
            'rds',
            rds_secure_params,
            secure_rds_params
        )
        
        results.update(secure_results)
        return results
    
    def populate_application_parameters(self) -> Dict[str, Dict[str, bool]]:
        """Populate application-specific parameters."""
        results = {}
        
        # FastAPI parameters
        fastapi_params = {
            'port': os.getenv('FASTAPI_PORT', '8000'),
            'host': '0.0.0.0',
            'debug': str(self.environment == 'dev').lower(),
            'workers': '1' if self.environment == 'dev' else '4',
            'reload': str(self.environment == 'dev').lower()
        }
        results['fastapi'] = self.parameter_manager.put_environment_parameters(
            self.environment, 'fastapi', fastapi_params
        )
        
        # Web application parameters
        web_params = {
            'port': os.getenv('WEB_PORT', '3000'),
            'debug': str(self.environment == 'dev').lower(),
            'build_env': self.environment
        }
        results['web'] = self.parameter_manager.put_environment_parameters(
            self.environment, 'web', web_params
        )
        
        # Dash application parameters
        dash_params = {
            'port': os.getenv('DASH_PORT', '8050'),
            'debug': str(self.environment == 'dev').lower(),
            'dev_tools_hot_reload': str(self.environment == 'dev').lower()
        }
        results['dash'] = self.parameter_manager.put_environment_parameters(
            self.environment, 'dash', dash_params
        )
        
        # Airflow parameters
        airflow_params = {
            'webserver_port': os.getenv('AIRFLOW_WEBSERVER_PORT', '8080'),
            'executor': 'KubernetesExecutor',
            'namespace': f'airflow-{self.environment}',
            'dag_dir': '/opt/airflow/dags'
        }
        results['airflow'] = self.parameter_manager.put_environment_parameters(
            self.environment, 'airflow', airflow_params
        )
        
        return results
    
    def populate_security_parameters(self) -> Dict[str, bool]:
        """Populate security-related parameters."""
        security_params = {
            'jwt_secret_key': os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key_here'),
            'encryption_key': os.getenv('ENCRYPTION_KEY', 'your_encryption_key_here')
        }
        
        # All security parameters are secure
        secure_parameters = list(security_params.keys())
        
        return self.parameter_manager.put_environment_parameters(
            self.environment,
            'security',
            security_params,
            secure_parameters
        )
    
    def populate_monitoring_parameters(self) -> Dict[str, bool]:
        """Populate monitoring-related parameters."""
        monitoring_params = {
            'cloudwatch_log_group': os.getenv('CLOUDWATCH_LOG_GROUP', f'/aws/eks/mono-repo-{self.environment}'),
            'metrics_namespace': os.getenv('METRICS_NAMESPACE', f'MonoRepo{self.environment.title()}'),
            'log_level': 'DEBUG' if self.environment == 'dev' else 'INFO'
        }
        
        return self.parameter_manager.put_environment_parameters(
            self.environment,
            'monitoring',
            monitoring_params
        )
    
    def populate_ecr_parameters(self) -> Dict[str, bool]:
        """Populate ECR-related parameters."""
        ecr_params = {
            'registry_url': os.getenv('ECR_REGISTRY_URL', f'ACCOUNT_ID.dkr.ecr.{os.getenv("AWS_DEFAULT_REGION", "us-east-1")}.amazonaws.com'),
            'repository_prefix': os.getenv('ECR_REPOSITORY_PREFIX', f'mono-repo-{self.environment}')
        }
        
        return self.parameter_manager.put_environment_parameters(
            self.environment,
            'ecr',
            ecr_params
        )
    
    def populate_s3_parameters(self) -> Dict[str, bool]:
        """Populate S3-related parameters."""
        s3_params = {
            'bucket_prefix': os.getenv('S3_BUCKET_PREFIX', f'mono-repo-{self.environment}-storage'),
            'terraform_state_bucket': os.getenv('TERRAFORM_STATE_BUCKET', f'mono-repo-{self.environment}-terraform-state')
        }
        
        return self.parameter_manager.put_environment_parameters(
            self.environment,
            's3',
            s3_params
        )
    
    def populate_aws_parameters(self) -> Dict[str, bool]:
        """Populate AWS credential parameters (if provided)."""
        # Note: In production, AWS credentials should be managed via IAM roles
        # This is primarily for development environments
        aws_params = {}
        
        if os.getenv('AWS_ACCESS_KEY_ID'):
            aws_params['access_key_id'] = os.getenv('AWS_ACCESS_KEY_ID')
        if os.getenv('AWS_SECRET_ACCESS_KEY'):
            aws_params['secret_access_key'] = os.getenv('AWS_SECRET_ACCESS_KEY')
        if os.getenv('AWS_REGION'):
            aws_params['region'] = os.getenv('AWS_REGION')
        if os.getenv('AWS_PROFILE'):
            aws_params['profile'] = os.getenv('AWS_PROFILE')
        
        if not aws_params:
            logger.info("No AWS credentials found in environment variables, skipping AWS parameters")
            return {}
        
        # AWS credentials should be stored as SecureString
        secure_parameters = ['access_key_id', 'secret_access_key'] if self.environment == 'dev' else []
        
        return self.parameter_manager.put_environment_parameters(
            self.environment,
            'aws',
            aws_params,
            secure_parameters
        )
    
    def populate_all_parameters(self) -> Dict[str, Any]:
        """Populate all environment parameters."""
        logger.info(f"Populating all parameters for environment: {self.environment}")
        
        results = {
            'terraform': self.populate_terraform_parameters(),
            'eks': self.populate_eks_parameters(),
            'rds': self.populate_rds_parameters(),
            'applications': self.populate_application_parameters(),
            'security': self.populate_security_parameters(),
            'monitoring': self.populate_monitoring_parameters(),
            'ecr': self.populate_ecr_parameters(),
            's3': self.populate_s3_parameters(),
            'aws': self.populate_aws_parameters()
        }
        
        # Summary
        total_success = 0
        total_attempted = 0
        
        for category, category_results in results.items():
            if isinstance(category_results, dict):
                if category == 'applications':
                    for app_name, app_results in category_results.items():
                        success_count = sum(1 for success in app_results.values() if success)
                        total_success += success_count
                        total_attempted += len(app_results)
                        logger.info(f"{category}.{app_name}: {success_count}/{len(app_results)} parameters set")
                else:
                    success_count = sum(1 for success in category_results.values() if success)
                    total_success += success_count
                    total_attempted += len(category_results)
                    logger.info(f"{category}: {success_count}/{len(category_results)} parameters set")
        
        logger.info(f"Total: {total_success}/{total_attempted} parameters set successfully")
        return results
    
    def validate_parameter_access(self) -> bool:
        """Validate that Parameter Store access is working."""
        return self.parameter_manager.validate_parameter_access(self.environment)
    
    def _get_vpc_cidr_for_environment(self) -> str:
        """Get VPC CIDR based on environment."""
        cidr_map = {
            'dev': '10.1.0.0/16',
            'uat': '10.3.0.0/16',
            'prod': '10.2.0.0/16'
        }
        return os.getenv('TF_VAR_vpc_cidr', cidr_map.get(self.environment, '10.1.0.0/16'))
    
    def _get_node_group_size(self, size_type: str) -> str:
        """Get EKS node group size based on environment and type."""
        size_map = {
            'dev': {'min': '1', 'max': '3', 'desired': '2'},
            'uat': {'min': '2', 'max': '5', 'desired': '3'},
            'prod': {'min': '3', 'max': '10', 'desired': '5'}
        }
        
        env_var_map = {
            'min': 'EKS_NODE_GROUP_MIN_SIZE',
            'max': 'EKS_NODE_GROUP_MAX_SIZE',
            'desired': 'EKS_NODE_GROUP_DESIRED_SIZE'
        }
        
        return os.getenv(
            env_var_map[size_type],
            size_map.get(self.environment, size_map['dev'])[size_type]
        )
    
    def _get_rds_instance_class(self) -> str:
        """Get RDS instance class based on environment."""
        class_map = {
            'dev': 'db.t3.micro',
            'uat': 'db.t3.small',
            'prod': 'db.r5.large'
        }
        return class_map.get(self.environment, 'db.t3.micro')
    
    def _get_rds_storage(self) -> str:
        """Get RDS allocated storage based on environment."""
        storage_map = {
            'dev': '20',
            'uat': '50',
            'prod': '100'
        }
        return storage_map.get(self.environment, '20')


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Setup environment configuration in Parameter Store')
    parser.add_argument('--environment', '-e', 
                       default=get_environment(),
                       choices=['dev', 'uat', 'prod'],
                       help='Environment to setup (default: current environment)')
    parser.add_argument('--region', '-r',
                       default=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
                       help='AWS region (default: us-east-1)')
    parser.add_argument('--validate-only', '-v',
                       action='store_true',
                       help='Only validate Parameter Store access')
    parser.add_argument('--category', '-c',
                       choices=['terraform', 'eks', 'rds', 'applications', 'security', 'monitoring', 'ecr', 's3', 'aws'],
                       help='Only populate specific category of parameters')
    
    args = parser.parse_args()
    
    logger.info(f"Setting up configuration for environment: {args.environment}")
    logger.info(f"AWS Region: {args.region}")
    
    # Initialize setup manager
    setup_manager = EnvironmentConfigSetup(args.environment, args.region)
    
    # Validate access first
    if not setup_manager.validate_parameter_access():
        logger.error("❌ Parameter Store access validation failed")
        return 1
    
    logger.info("✅ Parameter Store access validated")
    
    if args.validate_only:
        logger.info("Validation complete, exiting")
        return 0
    
    # Populate parameters
    if args.category:
        logger.info(f"Populating {args.category} parameters only")
        method_name = f"populate_{args.category}_parameters"
        if hasattr(setup_manager, method_name):
            results = getattr(setup_manager, method_name)()
            success_count = sum(1 for success in results.values() if success) if isinstance(results, dict) else 0
            total_count = len(results) if isinstance(results, dict) else 0
            logger.info(f"✅ {args.category}: {success_count}/{total_count} parameters set successfully")
        else:
            logger.error(f"❌ Unknown category: {args.category}")
            return 1
    else:
        results = setup_manager.populate_all_parameters()
    
    logger.info("🎉 Environment configuration setup complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())