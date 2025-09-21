#!/usr/bin/env python3
"""
PROD Environment Bootstrap Deployment Script
Automates the creation of S3 bucket and DynamoDB table for PROD Terraform state management.
Includes additional safety checks and production-grade validations.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Add project root to path for config imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import setup_aws_environment, get_aws_credentials

def validate_production_readiness():
    """Validate production deployment prerequisites."""
    print("🔍 Validating production deployment prerequisites...")
    
    checks = []
    
    # Check for AWS credentials
    try:
        creds = get_aws_credentials()
        if creds.get('aws_access_key_id'):
            checks.append(("✅", "AWS credentials configured"))
        else:
            checks.append(("❌", "AWS credentials missing"))
    except Exception as e:
        checks.append(("❌", f"AWS credentials error: {e}"))
    
    # Check if running in appropriate environment
    current_user = os.environ.get('USERNAME', os.environ.get('USER', 'unknown'))
    if current_user in ['root', 'admin', 'administrator']:
        checks.append(("⚠️", f"Running as privileged user: {current_user}"))
    else:
        checks.append(("✅", f"Running as user: {current_user}"))
    
    # Check for terraform
    try:
        result = subprocess.run(['terraform', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0].strip()
            checks.append(("✅", f"Terraform available: {version}"))
        else:
            checks.append(("❌", "Terraform not available"))
    except Exception:
        checks.append(("❌", "Terraform not installed"))
    
    # Print validation results
    for status, message in checks:
        print(f"   {status} {message}")
    
    # Check if any critical validations failed
    failed_checks = [check for check in checks if check[0] == "❌"]
    if failed_checks:
        print(f"\n❌ {len(failed_checks)} critical validation(s) failed")
        return False
    
    warning_checks = [check for check in checks if check[0] == "⚠️"]
    if warning_checks:
        print(f"\n⚠️  {len(warning_checks)} warning(s) found")
        response = input("Continue with warnings? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            return False
    
    print("✅ All production validations passed")
    return True

def get_production_approval():
    """Get explicit approval for production deployment."""
    print("\n🚨 PRODUCTION ENVIRONMENT DEPLOYMENT")
    print("=" * 50)
    print("⚠️  You are about to deploy bootstrap infrastructure to PRODUCTION")
    print("⚠️  This will create AWS resources that may incur costs")
    print("⚠️  Ensure you have proper authorization and change management approval")
    print()
    
    # Get change ticket information
    change_ticket = input("📋 Change Ticket/Approval Number (required): ").strip()
    if not change_ticket:
        print("❌ Change ticket number required for production deployment")
        return False
    
    # Get authorized person
    authorized_by = input("👤 Authorized by (manager/team lead): ").strip()
    if not authorized_by:
        print("❌ Authorization person required for production deployment")
        return False
    
    # Get deployment window
    deployment_window = input("⏰ Approved deployment window (e.g., '2024-01-15 02:00-04:00 UTC'): ").strip()
    if not deployment_window:
        print("❌ Deployment window required for production deployment")
        return False
    
    # Final confirmation
    print(f"\n📋 Production Deployment Summary:")
    print(f"   Change Ticket: {change_ticket}")
    print(f"   Authorized by: {authorized_by}")
    print(f"   Deployment Window: {deployment_window}")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    
    response = input("\n❓ Confirm PRODUCTION bootstrap deployment? (type 'DEPLOY PROD' to confirm): ").strip()
    if response != "DEPLOY PROD":
        print("❌ Production deployment cancelled - incorrect confirmation")
        return False
    
    # Log deployment approval
    approval_log = {
        "timestamp": datetime.now().isoformat(),
        "change_ticket": change_ticket,
        "authorized_by": authorized_by,
        "deployment_window": deployment_window,
        "environment": "PRODUCTION",
        "operation": "bootstrap_deployment"
    }
    
    with open("prod-deployment-approval.json", "w") as f:
        json.dump(approval_log, f, indent=2)
    
    print("✅ Production deployment approved and logged")
    return True

def main():
    """Main PROD bootstrap deployment function."""
    print("🔧 PRODUCTION Environment Bootstrap Deployment")
    print("=" * 50)
    
    # Validate production readiness
    if not validate_production_readiness():
        print("❌ Production validation failed")
        return 1
    
    # Get production approval
    if not get_production_approval():
        print("❌ Production deployment not approved")
        return 1
    
    # Get bootstrap directory
    bootstrap_dir = Path(__file__).parent
    tfvars_file = "prod.tfvars"
    
    # Setup AWS environment
    setup_aws_environment()
    creds = get_aws_credentials()
    
    print(f"\n✅ AWS credentials configured for region: {creds.get('region_name')}")
    
    # Check if tfvars file exists
    if not (bootstrap_dir / tfvars_file).exists():
        print(f"❌ PROD configuration file not found: {tfvars_file}")
        return 1
    
    print(f"✅ PROD configuration file found: {tfvars_file}")
    
    # Run terraform init
    print("\n📦 Initializing Terraform for PRODUCTION...")
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
    print("\n📋 Planning PRODUCTION bootstrap deployment...")
    result = subprocess.run(
        ["terraform", "plan", f"-var-file={tfvars_file}", "-out=prod.tfplan"],
        cwd=bootstrap_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Terraform plan failed: {result.stderr}")
        return 1
    
    print("✅ PRODUCTION bootstrap plan created")
    print(result.stdout)
    
    # Additional production confirmation
    print("\n🚨 FINAL PRODUCTION CONFIRMATION")
    print("=" * 40)
    response = input("❓ Execute PRODUCTION bootstrap deployment now? (type 'EXECUTE' to confirm): ").strip()
    if response != "EXECUTE":
        print("❌ PRODUCTION bootstrap deployment cancelled")
        return 0
    
    # Run terraform apply
    print("\n🚀 Applying PRODUCTION bootstrap configuration...")
    result = subprocess.run(
        ["terraform", "apply", "prod.tfplan"],
        cwd=bootstrap_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Terraform apply failed: {result.stderr}")
        return 1
    
    print("✅ PRODUCTION bootstrap infrastructure created successfully!")
    print(result.stdout)
    
    # Get outputs
    print("\n📤 Getting PRODUCTION bootstrap outputs...")
    result = subprocess.run(
        ["terraform", "output", "-json"],
        cwd=bootstrap_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        outputs = json.loads(result.stdout)
        
        print("\n📋 PRODUCTION Bootstrap Resources Created:")
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
        with open(bootstrap_dir / "prod-outputs.json", "w") as f:
            json.dump(outputs, f, indent=2)
        
        print("\n🎉 Next steps for PRODUCTION:")
        print("   1. Update ../terraform/main.tf with PROD backend configuration")
        print("   2. Follow PROD_DEPLOYMENT_GUIDE.md for main infrastructure")
        print("   3. Ensure all security and compliance requirements are met")
        
        # Show backend configuration
        if 'backend_configuration' in outputs:
            backend = outputs['backend_configuration']['value']
            print(f"\n📝 PRODUCTION Backend Configuration:")
            print(f"   bucket         = \"{backend['bucket']}\"")
            print(f"   key            = \"{backend['key']}\"")
            print(f"   region         = \"{backend['region']}\"")
            print(f"   dynamodb_table = \"{backend['dynamodb_table']}\"")
        
        # Log successful deployment
        deployment_log = {
            "timestamp": datetime.now().isoformat(),
            "environment": "PRODUCTION",
            "operation": "bootstrap_deployment_success",
            "resources_created": list(outputs.keys()),
            "bucket_name": outputs.get('terraform_state_bucket', {}).get('value'),
            "dynamodb_table": outputs.get('dynamodb_table_name', {}).get('value')
        }
        
        with open("prod-deployment-success.json", "w") as f:
            json.dump(deployment_log, f, indent=2)
        
        print("\n✅ PRODUCTION bootstrap deployment completed and logged")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
