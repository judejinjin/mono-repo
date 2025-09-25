#!/usr/bin/env python3
"""
Main deployment script for the mono-repo project.
Handles deployment of infrastructure and applications to different environments.
"""

import os
import sys
import argparse
import subprocess
import logging
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import get_environment, get_config, setup_aws_environment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeploymentManager:
    """Manages deployment processes for different targets and environments."""
    
    def __init__(self, environment: str = None, branch: str = None):
        # Set up AWS environment from config/.env file
        setup_aws_environment()
        
        self.environment = environment or get_environment()
        self.config = get_config()
        self.project_root = PROJECT_ROOT
        self.deploy_dir = self.project_root / 'deploy'
        self.deploy_config = self._load_deploy_config()
        self.branch = branch or self.deploy_config.get('branch', self._get_branch_for_environment())
        
    def _get_branch_for_environment(self) -> str:
        """Get the appropriate branch for the current environment."""
        branch_mapping = {
            'dev': 'develop',
            'uat': 'uat', 
            'prod': 'master'
        }
        return branch_mapping.get(self.environment, 'master')
    
    def deploy_with_branch_build(self, components: List[str] = None) -> bool:
        """Deploy application with branch-specific build."""
        logger.info(f"Deploying with branch build - Environment: {self.environment}, Branch: {self.branch}")
        
        components = components or ['services', 'web', 'dash', 'airflow']
        
        # Step 1: Build Docker images for the specific branch
        if not self._build_branch_images(components):
            return False
        
        # Step 2: Push images to registry
        if not self._push_images(components):
            return False
        
        # Step 3: Deploy components
        success = True
        for component in components:
            if not self.deploy_component(component):
                success = False
                logger.error(f"Failed to deploy component: {component}")
        
        return success
    
    def _build_branch_images(self, components: List[str]) -> bool:
        """Build Docker images for specific branch."""
        logger.info(f"Building images for branch: {self.branch}")
        
        build_script = self.project_root / 'build' / 'build.py'
        
        # Mapping of components to Docker services
        service_mapping = {
            'services': ['risk-api', 'data-pipeline'],
            'web': ['base'],  # Assuming web uses base image
            'dash': ['base'],  # Assuming dash uses base image
            'airflow': ['airflow']
        }
        
        for component in components:
            services = service_mapping.get(component, [])
            for service in services:
                cmd = [
                    sys.executable, str(build_script),
                    '--environment', self.environment,
                    '--branch', self.branch,
                    '--docker-service', service
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"Failed to build {service}: {result.stderr}")
                    return False
                
                logger.info(f"✅ Successfully built {service}")
        
        return True
    
    def _push_images(self, components: List[str]) -> bool:
        """Push Docker images to registry."""
        logger.info("Pushing images to registry...")
        
        registry_url = self.deploy_config.get('registry', {}).get('url', 'jfrog.corporate.local')
        image_tag = self.deploy_config.get('image_tag', f'{self.environment}-{self.branch}')
        
        service_mapping = {
            'services': ['risk-api', 'data-pipeline'],
            'web': ['base'],
            'dash': ['base'],
            'airflow': ['airflow']
        }
        
        for component in components:
            services = service_mapping.get(component, [])
            for service in services:
                local_image = f'mono-repo/{service}:{self.environment}-{self.branch}'
                remote_image = f'{registry_url}/mono-repo/{service}:{image_tag}'
                
                # Tag for registry
                tag_cmd = ['docker', 'tag', local_image, remote_image]
                if subprocess.run(tag_cmd).returncode != 0:
                    logger.error(f"Failed to tag image: {service}")
                    return False
                
                # Push to registry
                push_cmd = ['docker', 'push', remote_image]
                if subprocess.run(push_cmd).returncode != 0:
                    logger.error(f"Failed to push image: {service}")
                    return False
                
                logger.info(f"✅ Pushed {remote_image}")
        
        return True

    def _load_deploy_config(self) -> Dict[str, Any]:
        """Load deployment configuration for current environment."""
        config_file = self.deploy_dir / 'configs' / f'{self.environment}.yaml'
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def deploy_infrastructure(self) -> bool:
        """Deploy infrastructure using Terraform."""
        logger.info(f"Deploying infrastructure for environment: {self.environment}")
        
        # First, setup environment configuration in Parameter Store
        if not self._setup_environment_config():
            logger.warning("Parameter Store setup failed, continuing with deployment")
        
        terraform_dir = self.project_root / 'infrastructure' / 'terraform'
        if not terraform_dir.exists():
            logger.error("Terraform directory not found")
            return False
        
        try:
            # Initialize Terraform
            if not self._run_terraform_command(['init'], terraform_dir):
                return False
            
            # Plan deployment
            if not self._run_terraform_command(['plan', f'-var-file={self.environment}.tfvars'], terraform_dir):
                return False
            
            # Apply deployment
            if not self._run_terraform_command(['apply', '-auto-approve', f'-var-file={self.environment}.tfvars'], terraform_dir):
                return False
            
            logger.info("Infrastructure deployment completed successfully")
            return True
        except Exception as e:
            logger.error(f"Infrastructure deployment failed: {e}")
            return False
    
    def deploy_applications(self) -> bool:
        """Deploy all applications."""
        logger.info(f"Deploying applications for environment: {self.environment}")
        
        applications = ['services', 'web', 'dash', 'airflow']
        success = True
        
        for app in applications:
            if not self.deploy_component(app):
                success = False
                logger.error(f"Failed to deploy application: {app}")
        
        return success
    
    def _setup_environment_config(self) -> bool:
        """Setup environment configuration in Parameter Store."""
        try:
            import subprocess
            setup_script = self.project_root / 'scripts' / 'setup_environment_config.py'
            
            cmd = [
                'python', str(setup_script),
                '--environment', self.environment,
                '--region', os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Environment configuration setup completed")
                return True
            else:
                logger.error(f"Environment configuration setup failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup environment configuration: {e}")
            return False
    
    def deploy_component(self, component: str) -> bool:
        """Deploy specific component."""
        logger.info(f"Deploying component: {component}")
        
        try:
            if component == 'services':
                return self._deploy_fastapi_services()
            elif component == 'web':
                return self._deploy_web_applications()
            elif component == 'dash':
                return self._deploy_dash_applications()
            elif component == 'airflow':
                return self._deploy_airflow()
            elif component == 'database':
                return self._deploy_database()
            else:
                logger.error(f"Unknown component: {component}")
                return False
        except Exception as e:
            logger.error(f"Error deploying {component}: {e}")
            return False
    
    def _deploy_fastapi_services(self) -> bool:
        """Deploy FastAPI services to Kubernetes."""
        logger.info("Deploying FastAPI services...")
        
        manifests_dir = self.deploy_dir / 'kubernetes' / 'services'
        if not manifests_dir.exists():
            logger.error("Kubernetes manifests for services not found")
            return False
        
        # Apply Kubernetes manifests
        for manifest_file in manifests_dir.glob('*.yaml'):
            if not self._apply_kubernetes_manifest(manifest_file):
                return False
        
        # Wait for deployment to be ready
        return self._wait_for_deployment('fastapi-service')
    
    def _deploy_web_applications(self) -> bool:
        """Deploy web applications."""
        logger.info("Deploying web applications...")
        
        # Build production assets first
        if not self._build_web_assets():
            return False
        
        manifests_dir = self.deploy_dir / 'kubernetes' / 'web'
        if not manifests_dir.exists():
            logger.error("Kubernetes manifests for web not found")
            return False
        
        # Apply Kubernetes manifests
        for manifest_file in manifests_dir.glob('*.yaml'):
            if not self._apply_kubernetes_manifest(manifest_file):
                return False
        
        return self._wait_for_deployment('web-app')
    
    def _deploy_dash_applications(self) -> bool:
        """Deploy Dash applications."""
        logger.info("Deploying Dash applications...")
        
        manifests_dir = self.deploy_dir / 'kubernetes' / 'dash'
        if not manifests_dir.exists():
            logger.error("Kubernetes manifests for dash not found")
            return False
        
        # Apply Kubernetes manifests
        for manifest_file in manifests_dir.glob('*.yaml'):
            if not self._apply_kubernetes_manifest(manifest_file):
                return False
        
        return self._wait_for_deployment('dash-app')
    
    def _deploy_airflow(self) -> bool:
        """Deploy Airflow components."""
        logger.info("Deploying Airflow...")
        
        # Deploy Airflow using Helm chart
        helm_values = self.deploy_dir / 'kubernetes' / 'airflow' / f'values-{self.environment}.yaml'
        if not helm_values.exists():
            logger.error(f"Helm values file not found: {helm_values}")
            return False
        
        cmd = [
            'helm', 'upgrade', '--install', 'airflow',
            'apache-airflow/airflow',
            '--namespace', f'airflow-{self.environment}',
            '--create-namespace',
            '--values', str(helm_values)
        ]
        
        return self._run_command(cmd)
    
    def _deploy_database(self) -> bool:
        """Run database migrations."""
        logger.info("Running database migrations...")
        
        # Run Alembic migrations
        cmd = [sys.executable, '-m', 'alembic', 'upgrade', 'head']
        return self._run_command(cmd, cwd=self.project_root)
    
    def _build_web_assets(self) -> bool:
        """Build web application assets."""
        web_dir = self.project_root / 'web'
        if not web_dir.exists():
            return True
        
        # Install dependencies and build
        commands = [
            ['npm', 'install'],
            ['npm', 'run', 'build']
        ]
        
        for cmd in commands:
            if not self._run_command(cmd, cwd=web_dir):
                return False
        
        return True
    
    def _run_terraform_command(self, args: List[str], cwd: Path) -> bool:
        """Run Terraform command."""
        cmd = ['terraform'] + args
        return self._run_command(cmd, cwd=cwd)
    
    def _apply_kubernetes_manifest(self, manifest_file: Path) -> bool:
        """Apply Kubernetes manifest."""
        # Substitute environment variables in manifest
        processed_manifest = self._process_manifest_template(manifest_file)
        
        cmd = ['kubectl', 'apply', '-f', '-']
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, text=True)
        process.communicate(input=processed_manifest)
        
        return process.returncode == 0
    
    def _process_manifest_template(self, manifest_file: Path) -> str:
        """Process Kubernetes manifest template with environment variables."""
        with open(manifest_file, 'r') as f:
            content = f.read()
        
        # Replace environment-specific values
        replacements = {
            '${ENVIRONMENT}': self.environment,
            '${NAMESPACE}': f'mono-repo-{self.environment}',
            '${IMAGE_TAG}': self.deploy_config.get('image_tag', 'latest'),
        }
        
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        return content
    
    def _wait_for_deployment(self, deployment_name: str) -> bool:
        """Wait for Kubernetes deployment to be ready."""
        cmd = [
            'kubectl', 'wait', '--for=condition=available',
            f'deployment/{deployment_name}',
            '--namespace', f'mono-repo-{self.environment}',
            '--timeout=300s'
        ]
        return self._run_command(cmd)
    
    def _run_command(self, cmd: List[str], cwd: Path = None, capture_output: bool = False) -> bool:
        """Run shell command and return success status."""
        try:
            logger.info(f"Running command: {' '.join(cmd)}")
            if capture_output:
                result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
            else:
                result = subprocess.run(cmd, cwd=cwd, check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(cmd)}")
            logger.error(f"Error: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Deploy mono-repo components')
    parser.add_argument('--target', 
                        choices=['infrastructure', 'applications', 'services', 'web', 'dash', 'airflow', 'database', 'build-and-deploy'],
                        required=True, help='Deployment target')
    parser.add_argument('--environment', choices=['dev', 'uat', 'prod'],
                        help='Target environment')
    parser.add_argument('--branch', 
                        help='Git branch to deploy (defaults to environment-appropriate branch)')
    parser.add_argument('--component', help='Specific component to deploy')
    parser.add_argument('--action', choices=['deploy', 'migrate', 'rollback'],
                        default='deploy', help='Deployment action')
    parser.add_argument('--components', nargs='+', 
                        choices=['services', 'web', 'dash', 'airflow'],
                        help='Multiple components to build and deploy')
    
    args = parser.parse_args()
    
    # Set environment variable if provided
    if args.environment:
        os.environ['ENV'] = args.environment
    
    deployment_manager = DeploymentManager(args.environment, args.branch)
    
    success = False
    
    if args.target == 'infrastructure':
        success = deployment_manager.deploy_infrastructure()
    elif args.target == 'applications':
        success = deployment_manager.deploy_applications()
    elif args.target == 'build-and-deploy':
        # New branch-aware build and deploy option
        components = args.components or ['services', 'web', 'dash', 'airflow']
        success = deployment_manager.deploy_with_branch_build(components)
    elif args.target in ['services', 'web', 'dash', 'airflow', 'database']:
        success = deployment_manager.deploy_component(args.target)
    
    if success:
        logger.info("Deployment completed successfully!")
        sys.exit(0)
    else:
        logger.error("Deployment failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
