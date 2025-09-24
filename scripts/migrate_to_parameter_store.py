#!/usr/bin/env python3
"""
Parameter Store Migration Tool
Migrates configuration from config/.env files to AWS Systems Manager Parameter Store.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import re

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from libs.cloud.parameter_store import ParameterStoreManager
from config import get_environment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParameterStoreMigration:
    """Handles migration from config/.env files to Parameter Store."""
    
    def __init__(self, region_name: str = None):
        self.parameter_manager = ParameterStoreManager(region_name)
        self.project_root = PROJECT_ROOT
        
        # Define parameter mapping from config/.env names to Parameter Store structure
        self.parameter_mapping = {
            # AWS Configuration
            'AWS_ACCESS_KEY_ID': ('aws', 'access_key_id', True),  # (app, param, is_secure)
            'AWS_SECRET_ACCESS_KEY': ('aws', 'secret_access_key', True),
            'AWS_DEFAULT_REGION': ('aws', 'region', False),
            'AWS_REGION': ('aws', 'region', False),
            'AWS_PROFILE': ('aws', 'profile', False),
            'AWS_ACCOUNT_ID': ('terraform', 'aws_account_id', False),
            
            # Terraform Variables
            'TF_VAR_aws_region': ('terraform', 'aws_region', False),
            'TF_VAR_environment': ('terraform', 'environment', False),
            'TF_VAR_project_name': ('terraform', 'project_name', False),
            
            # EKS Configuration
            'EKS_CLUSTER_NAME': ('eks', 'cluster_name', False),
            
            # ECR Configuration
            'ECR_REGISTRY_URL': ('ecr', 'registry_url', False),
            'ECR_REPOSITORY_PREFIX': ('ecr', 'repository_prefix', False),
            
            # S3 Configuration
            'S3_BUCKET_PREFIX': ('s3', 'bucket_prefix', False),
            'TERRAFORM_STATE_BUCKET': ('s3', 'terraform_state_bucket', False),
            
            # RDS Configuration
            'RDS_DB_NAME': ('rds', 'db_name', False),
            'RDS_USERNAME': ('rds', 'username', False),
            'RDS_PASSWORD': ('rds', 'password', True),
            
            # Application Configuration
            'FASTAPI_PORT': ('fastapi', 'port', False),
            'WEB_PORT': ('web', 'port', False),
            'DASH_PORT': ('dash', 'port', False),
            'AIRFLOW_WEBSERVER_PORT': ('airflow', 'webserver_port', False),
            
            # Security
            'JWT_SECRET_KEY': ('security', 'jwt_secret_key', True),
            'ENCRYPTION_KEY': ('security', 'encryption_key', True),
            
            # Monitoring
            'CLOUDWATCH_LOG_GROUP': ('monitoring', 'cloudwatch_log_group', False),
            'METRICS_NAMESPACE': ('monitoring', 'metrics_namespace', False),
            
            # Environment Settings
            'ENVIRONMENT': ('app', 'environment', False),
            'LOG_LEVEL': ('monitoring', 'log_level', False),
        }
    
    def read_env_file(self, env_file_path: Path) -> Dict[str, str]:
        """Read and parse config/.env file."""
        env_vars = {}
        
        if not env_file_path.exists():
            logger.warning(f"Environment file not found: {env_file_path}")
            return env_vars
        
        with open(env_file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    env_vars[key] = value
                else:
                    logger.warning(f"Invalid line format at {env_file_path}:{line_num}: {line}")
        
        logger.info(f"Read {len(env_vars)} variables from {env_file_path}")
        return env_vars
    
    def migrate_environment(
        self, 
        environment: str, 
        env_vars: Dict[str, str],
        dry_run: bool = False
    ) -> Tuple[Dict[str, bool], List[str]]:
        """
        Migrate environment variables to Parameter Store.
        
        Args:
            environment: Target environment (dev, uat, prod)
            env_vars: Dictionary of environment variables
            dry_run: If True, only show what would be migrated
            
        Returns:
            Tuple of (migration results, unmapped variables)
        """
        results = {}
        unmapped_vars = []
        
        logger.info(f"Migrating {len(env_vars)} variables to environment: {environment}")
        
        for env_key, env_value in env_vars.items():
            if env_key in self.parameter_mapping:
                app_name, param_name, is_secure = self.parameter_mapping[env_key]
                full_param_name = f"/{environment}/{app_name}/{param_name}"
                param_type = 'SecureString' if is_secure else 'String'
                
                if dry_run:
                    logger.info(f"[DRY RUN] Would migrate: {env_key} -> {full_param_name} ({param_type})")
                    results[env_key] = True
                else:
                    success = self.parameter_manager.put_parameter(
                        name=full_param_name,
                        value=env_value,
                        parameter_type=param_type,
                        description=f"Migrated from .env: {env_key}",
                        overwrite=True
                    )
                    results[env_key] = success
                    
                    if success:
                        logger.info(f"✅ Migrated: {env_key} -> {full_param_name}")
                    else:
                        logger.error(f"❌ Failed to migrate: {env_key}")
            else:
                unmapped_vars.append(env_key)
                logger.warning(f"⚠️  Unmapped variable: {env_key} (value: {env_value[:20]}...)")
        
        return results, unmapped_vars
    
    def validate_migration(
        self, 
        environment: str, 
        original_env_vars: Dict[str, str]
    ) -> Dict[str, bool]:
        """
        Validate that migrated parameters can be retrieved correctly.
        
        Args:
            environment: Environment to validate
            original_env_vars: Original environment variables to validate against
            
        Returns:
            Dictionary of validation results
        """
        validation_results = {}
        
        logger.info(f"Validating migration for environment: {environment}")
        
        for env_key, original_value in original_env_vars.items():
            if env_key in self.parameter_mapping:
                app_name, param_name, is_secure = self.parameter_mapping[env_key]
                full_param_name = f"/{environment}/{app_name}/{param_name}"
                
                retrieved_value = self.parameter_manager.get_parameter(full_param_name, decrypt=True)
                
                if retrieved_value == original_value:
                    validation_results[env_key] = True
                    logger.info(f"✅ Validated: {env_key}")
                else:
                    validation_results[env_key] = False
                    logger.error(f"❌ Validation failed: {env_key} (expected: {original_value}, got: {retrieved_value})")
        
        success_count = sum(1 for result in validation_results.values() if result)
        total_count = len(validation_results)
        logger.info(f"Validation complete: {success_count}/{total_count} parameters validated successfully")
        
        return validation_results
    
    def generate_migration_report(
        self,
        environment: str,
        migration_results: Dict[str, bool],
        unmapped_vars: List[str],
        validation_results: Dict[str, bool] = None
    ) -> str:
        """Generate a migration report."""
        report_lines = []
        report_lines.append(f"Parameter Store Migration Report")
        report_lines.append(f"Environment: {environment}")
        report_lines.append(f"Generated: {os.popen('date').read().strip()}")
        report_lines.append("=" * 50)
        
        # Migration results
        successful_migrations = [k for k, v in migration_results.items() if v]
        failed_migrations = [k for k, v in migration_results.items() if not v]
        
        report_lines.append(f"\nMigration Results:")
        report_lines.append(f"  Successfully migrated: {len(successful_migrations)}")
        report_lines.append(f"  Failed migrations: {len(failed_migrations)}")
        report_lines.append(f"  Unmapped variables: {len(unmapped_vars)}")
        
        if failed_migrations:
            report_lines.append(f"\nFailed Migrations:")
            for var in failed_migrations:
                report_lines.append(f"  ❌ {var}")
        
        if unmapped_vars:
            report_lines.append(f"\nUnmapped Variables (need manual mapping):")
            for var in unmapped_vars:
                report_lines.append(f"  ⚠️  {var}")
        
        # Validation results
        if validation_results:
            successful_validations = [k for k, v in validation_results.items() if v]
            failed_validations = [k for k, v in validation_results.items() if not v]
            
            report_lines.append(f"\nValidation Results:")
            report_lines.append(f"  Successfully validated: {len(successful_validations)}")
            report_lines.append(f"  Failed validations: {len(failed_validations)}")
            
            if failed_validations:
                report_lines.append(f"\nFailed Validations:")
                for var in failed_validations:
                    report_lines.append(f"  ❌ {var}")
        
        # Parameter Store structure
        report_lines.append(f"\nParameter Store Structure:")
        apps = set()
        for env_key in successful_migrations:
            if env_key in self.parameter_mapping:
                app_name, _, _ = self.parameter_mapping[env_key]
                apps.add(app_name)
        
        for app in sorted(apps):
            report_lines.append(f"  /{environment}/{app}/")
            for env_key in successful_migrations:
                if env_key in self.parameter_mapping:
                    mapped_app, param_name, is_secure = self.parameter_mapping[env_key]
                    if mapped_app == app:
                        security_note = " (SecureString)" if is_secure else ""
                        report_lines.append(f"    {param_name}{security_note}")
        
        return "\n".join(report_lines)
    
    def cleanup_test_parameters(self, environment: str) -> bool:
        """Clean up test parameters created during validation."""
        test_param_name = f"/{environment}/test/migration_validation"
        return self.parameter_manager.delete_parameter(test_param_name)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Migrate config/.env configuration to AWS Parameter Store')
    parser.add_argument('--environment', '-e',
                       default=get_environment(),
                       choices=['dev', 'uat', 'prod'],
                       help='Target environment (default: current environment)')
    parser.add_argument('--env-file', '-f',
                       type=Path,
                       help='Path to .env file (default: config/.env)')
    parser.add_argument('--region', '-r',
                       default=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
                       help='AWS region (default: us-east-1)')
    parser.add_argument('--dry-run', '-d',
                       action='store_true',
                       help='Show what would be migrated without actually doing it')
    parser.add_argument('--validate', '-v',
                       action='store_true',
                       help='Validate migration after completion')
    parser.add_argument('--report', '-o',
                       type=Path,
                       help='Generate migration report to file')
    parser.add_argument('--force', 
                       action='store_true',
                       help='Force migration even if parameters already exist')
    
    args = parser.parse_args()
    
    # Default config/.env file path
    if not args.env_file:
        args.env_file = PROJECT_ROOT / 'config' / '.env'
    
    logger.info(f"Parameter Store Migration Tool")
    logger.info(f"Environment: {args.environment}")
    logger.info(f"Region: {args.region}")
    logger.info(f"Env file: {args.env_file}")
    logger.info(f"Dry run: {args.dry_run}")
    
    # Initialize migration tool
    migration_tool = ParameterStoreMigration(args.region)
    
    # Validate Parameter Store access
    if not args.dry_run:
        if not migration_tool.parameter_manager.validate_parameter_access(args.environment):
            logger.error("❌ Parameter Store access validation failed")
            return 1
        logger.info("✅ Parameter Store access validated")
    
    # Read config/.env file
    env_vars = migration_tool.read_env_file(args.env_file)
    if not env_vars:
        logger.error("❌ No environment variables found to migrate")
        return 1
    
    # Perform migration
    migration_results, unmapped_vars = migration_tool.migrate_environment(
        args.environment, 
        env_vars, 
        dry_run=args.dry_run
    )
    
    # Validate migration if requested
    validation_results = None
    if args.validate and not args.dry_run:
        validation_results = migration_tool.validate_migration(args.environment, env_vars)
    
    # Generate report
    report = migration_tool.generate_migration_report(
        args.environment,
        migration_results,
        unmapped_vars,
        validation_results
    )
    
    # Output report
    if args.report:
        args.report.write_text(report)
        logger.info(f"📄 Migration report saved to: {args.report}")
    else:
        print("\n" + report)
    
    # Summary
    success_count = sum(1 for result in migration_results.values() if result)
    total_count = len(migration_results)
    
    if args.dry_run:
        logger.info(f"🔍 Dry run complete: {success_count}/{total_count} parameters would be migrated")
    else:
        logger.info(f"🎉 Migration complete: {success_count}/{total_count} parameters migrated successfully")
        
        if unmapped_vars:
            logger.warning(f"⚠️  {len(unmapped_vars)} variables need manual mapping")
        
        if validation_results:
            validation_success = sum(1 for result in validation_results.values() if result)
            validation_total = len(validation_results)
            if validation_success == validation_total:
                logger.info(f"✅ All {validation_total} parameters validated successfully")
            else:
                logger.error(f"❌ Validation failed: {validation_success}/{validation_total} parameters validated")
    
    # Return appropriate exit code
    if success_count == total_count and (not validation_results or all(validation_results.values())):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())