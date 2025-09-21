#!/usr/bin/env python3
"""
Terraform Bootstrap Deployment Script
Automates the creation of S3 bucket and DynamoDB table for Terraform state management.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Add project root to path for config imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import setup_aws_environment, get_aws_credentials

def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result."""
    print(f"🔧 Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=check
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_terraform_installed():
    """Check if Terraform is installed and accessible."""
    try:
        result = subprocess.run(['terraform', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Terraform found: {result.stdout.split()[1]}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Terraform not found. Please install Terraform:")
    print("   https://www.terraform.io/downloads.html")
    return False

def check_aws_credentials():
    """Check if AWS credentials are configured."""
    setup_aws_environment()
    creds = get_aws_credentials()
    
    if not creds.get('aws_access_key_id') or not creds.get('aws_secret_access_key'):
        print("❌ AWS credentials not configured.")
        print("   Please run: python setup_aws_credentials.py")
        return False
    
    print(f"✅ AWS credentials found for region: {creds.get('region_name')}")
    return True

def terraform_init(bootstrap_dir):
    """Initialize Terraform in the bootstrap directory."""
    print("\n📦 Initializing Terraform...")
    result = run_command("terraform init", cwd=bootstrap_dir)
    return result.returncode == 0

def terraform_plan(bootstrap_dir, tfvars_file):
    """Run Terraform plan to preview changes."""
    print("\n📋 Planning Terraform deployment...")
    result = run_command(f"terraform plan -var-file=\"{tfvars_file}\"", cwd=bootstrap_dir)
    return result.returncode == 0

def terraform_apply(bootstrap_dir, tfvars_file, auto_approve=False):
    """Apply Terraform configuration."""
    print("\n🚀 Applying Terraform configuration...")
    command = f"terraform apply -var-file=\"{tfvars_file}\""
    if auto_approve:
        command += " -auto-approve"
    
    result = run_command(command, cwd=bootstrap_dir)
    return result.returncode == 0

def get_terraform_outputs(bootstrap_dir):
    """Get Terraform outputs as JSON."""
    print("\n📤 Getting Terraform outputs...")
    result = run_command("terraform output -json", cwd=bootstrap_dir, check=False)
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse Terraform outputs: {e}")
    
    return {}

def update_main_terraform_backend(outputs):
    """Update the main Terraform configuration with bootstrap outputs."""
    if not outputs:
        print("⚠️  No outputs available to update main Terraform configuration")
        return
    
    backend_config = outputs.get('backend_configuration', {}).get('value', {})
    if not backend_config:
        print("⚠️  No backend configuration in outputs")
        return
    
    print("\n📝 Backend configuration for main Terraform:")
    print("   Add this to your ../terraform/main.tf backend block:")
    print(f"   bucket         = \"{backend_config.get('bucket')}\"")
    print(f"   key            = \"{backend_config.get('key')}\"")
    print(f"   region         = \"{backend_config.get('region')}\"")
    print(f"   dynamodb_table = \"{backend_config.get('dynamodb_table')}\"")
    print(f"   encrypt        = {str(backend_config.get('encrypt', True)).lower()}")

def update_env_file(outputs):
    """Update .env file with ECR repository URLs."""
    ecr_repos = outputs.get('ecr_repository_urls', {}).get('value', {})
    if not ecr_repos:
        print("⚠️  No ECR repositories in outputs")
        return
    
    print("\n📝 ECR Repository URLs:")
    for name, url in ecr_repos.items():
        print(f"   {name}: {url}")
    
    # Optionally could update .env file automatically here
    print("\n💡 Consider adding these to your .env file for container deployments")

def main():
    """Main bootstrap deployment function."""
    print("🔧 Terraform Bootstrap Deployment")
    print("=" * 50)
    
    # Get bootstrap directory
    bootstrap_dir = Path(__file__).parent
    tfvars_file = "dev.tfvars"
    
    # Pre-flight checks
    print("\n🔍 Pre-flight checks...")
    
    if not check_terraform_installed():
        return 1
    
    if not check_aws_credentials():
        return 1
    
    if not (bootstrap_dir / tfvars_file).exists():
        print(f"❌ Configuration file not found: {tfvars_file}")
        return 1
    
    print("✅ All pre-flight checks passed!")
    
    # Terraform workflow
    if not terraform_init(bootstrap_dir):
        print("❌ Terraform initialization failed")
        return 1
    
    if not terraform_plan(bootstrap_dir, tfvars_file):
        print("❌ Terraform planning failed")
        return 1
    
    # Ask for confirmation unless auto-approve is requested
    auto_approve = "--auto-approve" in sys.argv or "-y" in sys.argv
    if not auto_approve:
        response = input("\n❓ Do you want to apply these changes? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Deployment cancelled by user")
            return 0
    
    if not terraform_apply(bootstrap_dir, tfvars_file, auto_approve=True):
        print("❌ Terraform apply failed")
        return 1
    
    # Get and display outputs
    outputs = get_terraform_outputs(bootstrap_dir)
    if outputs:
        print("\n✅ Bootstrap deployment completed successfully!")
        print("\n📋 Created Resources:")
        
        if 'terraform_state_bucket' in outputs:
            bucket_name = outputs['terraform_state_bucket']['value']
            print(f"   📦 S3 State Bucket: {bucket_name}")
        
        if 'dynamodb_table_name' in outputs:
            table_name = outputs['dynamodb_table_name']['value']
            print(f"   🗄️  DynamoDB Lock Table: {table_name}")
        
        ecr_count = len(outputs.get('ecr_repository_urls', {}).get('value', {}))
        if ecr_count > 0:
            print(f"   📦 ECR Repositories: {ecr_count} created")
        
        # Provide next steps
        update_main_terraform_backend(outputs)
        update_env_file(outputs)
        
        print("\n🎉 Next steps:")
        print("   1. Update ../terraform/main.tf with the backend configuration above")
        print("   2. Run the main infrastructure deployment:")
        print("      cd ../terraform && terraform init && terraform plan")
        
    else:
        print("⚠️  Bootstrap completed but no outputs available")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
