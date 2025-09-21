#!/usr/bin/env python3
"""
UAT Environment Bootstrap Deployment Script
Automates the creation of S3 bucket and DynamoDB table for UAT Terraform state management.
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

def main():
    """Main UAT bootstrap deployment function."""
    print("🔧 UAT Environment Bootstrap Deployment")
    print("=" * 50)
    
    # Get bootstrap directory
    bootstrap_dir = Path(__file__).parent
    tfvars_file = "uat.tfvars"
    
    # Setup AWS environment
    setup_aws_environment()
    creds = get_aws_credentials()
    
    if not creds.get('aws_access_key_id'):
        print("❌ AWS credentials not configured")
        print("   Please run: python setup_aws_credentials.py")
        return 1
    
    print(f"✅ AWS credentials found for region: {creds.get('region_name')}")
    
    # Check if tfvars file exists
    if not (bootstrap_dir / tfvars_file).exists():
        print(f"❌ UAT configuration file not found: {tfvars_file}")
        return 1
    
    print(f"✅ UAT configuration file found: {tfvars_file}")
    
    # Run terraform init
    print("\n📦 Initializing Terraform for UAT...")
    result = subprocess.run(
        ["terraform", "init"],
        cwd=bootstrap_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Terraform init failed: {result.stderr}")
        return 1
    
    print("✅ Terraform initialized successfully")
    
    # Run terraform plan
    print("\n📋 Planning UAT bootstrap deployment...")
    result = subprocess.run(
        ["terraform", "plan", f"-var-file={tfvars_file}", "-out=uat.tfplan"],
        cwd=bootstrap_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Terraform plan failed: {result.stderr}")
        return 1
    
    print("✅ UAT bootstrap plan created")
    print(result.stdout)
    
    # Ask for confirmation
    response = input("\n❓ Do you want to apply the UAT bootstrap? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ UAT bootstrap deployment cancelled")
        return 0
    
    # Run terraform apply
    print("\n🚀 Applying UAT bootstrap configuration...")
    result = subprocess.run(
        ["terraform", "apply", "uat.tfplan"],
        cwd=bootstrap_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Terraform apply failed: {result.stderr}")
        return 1
    
    print("✅ UAT bootstrap infrastructure created successfully!")
    print(result.stdout)
    
    # Get outputs
    print("\n📤 Getting UAT bootstrap outputs...")
    result = subprocess.run(
        ["terraform", "output", "-json"],
        cwd=bootstrap_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        outputs = json.loads(result.stdout)
        
        print("\n📋 UAT Bootstrap Resources Created:")
        if 'terraform_state_bucket' in outputs:
            bucket_name = outputs['terraform_state_bucket']['value']
            print(f"   📦 S3 State Bucket: {bucket_name}")
        
        if 'dynamodb_table_name' in outputs:
            table_name = outputs['dynamodb_table_name']['value']
            print(f"   🗄️  DynamoDB Lock Table: {table_name}")
        
        ecr_repos = outputs.get('ecr_repository_urls', {}).get('value', {})
        if ecr_repos:
            print(f"   📦 ECR Repositories: {len(ecr_repos)} created")
            for name, url in ecr_repos.items():
                print(f"      {name}: {url}")
        
        # Save outputs for later use
        with open(bootstrap_dir / "uat-outputs.json", "w") as f:
            json.dump(outputs, f, indent=2)
        
        print("\n🎉 Next steps for UAT:")
        print("   1. Update ../terraform/main.tf with UAT backend configuration")
        print("   2. Run UAT main infrastructure deployment:")
        print("      cd ../terraform")
        print("      terraform init")
        print("      terraform plan -var-file='uat.tfvars'")
        print("      terraform apply -var-file='uat.tfvars'")
        
        # Show backend configuration
        if 'backend_configuration' in outputs:
            backend = outputs['backend_configuration']['value']
            print(f"\n📝 UAT Backend Configuration:")
            print(f"   bucket         = \"{backend['bucket']}\"")
            print(f"   key            = \"{backend['key']}\"")
            print(f"   region         = \"{backend['region']}\"")
            print(f"   dynamodb_table = \"{backend['dynamodb_table']}\"")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
