#!/usr/bin/env python3
"""
UAT Environment Bootstrap Teardown Script
Safely destroys UAT bootstrap infrastructure (S3 bucket, DynamoDB table, ECR repositories).
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

def check_terraform_state():
    """Check if main infrastructure exists that depends on bootstrap."""
    print("\n🔍 Checking for dependent infrastructure...")
    
    # Check for main terraform state
    main_terraform_dir = Path(__file__).parent.parent / "terraform"
    
    if (main_terraform_dir / "terraform.tfstate").exists():
        print("⚠️  Main terraform state file found")
        print("   You may need to destroy main infrastructure first")
        return False
    
    if (main_terraform_dir / ".terraform").exists():
        print("⚠️  Main terraform workspace initialized")
        print("   Check if main infrastructure exists before destroying bootstrap")
        return False
    
    print("✅ No dependent infrastructure detected")
    return True

def backup_terraform_state():
    """Create backup of current terraform state."""
    bootstrap_dir = Path(__file__).parent
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Backup terraform state
    state_file = bootstrap_dir / "terraform.tfstate"
    if state_file.exists():
        backup_file = bootstrap_dir / f"terraform.tfstate.backup.{timestamp}"
        state_file.rename(backup_file)
        print(f"✅ State backed up to: {backup_file.name}")
        return backup_file
    
    return None

def get_resources_to_destroy():
    """Get list of resources that will be destroyed."""
    bootstrap_dir = Path(__file__).parent
    
    # Get current outputs to show what will be destroyed
    result = subprocess.run(
        ["terraform", "output", "-json"],
        cwd=bootstrap_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        outputs = json.loads(result.stdout)
        return outputs
    
    return {}

def main():
    """Main UAT bootstrap teardown function."""
    print("🔥 UAT Environment Bootstrap Teardown")
    print("=" * 50)
    
    # Get bootstrap directory
    bootstrap_dir = Path(__file__).parent
    tfvars_file = "uat.tfvars"
    
    # Setup AWS environment
    setup_aws_environment()
    creds = get_aws_credentials()
    
    if not creds.get('aws_access_key_id'):
        print("❌ AWS credentials not configured")
        return 1
    
    print(f"✅ AWS credentials found for region: {creds.get('region_name')}")
    
    # Check for terraform state
    if not (bootstrap_dir / "terraform.tfstate").exists():
        print("⚠️  No terraform state found - nothing to destroy")
        return 0
    
    # Check for dependent infrastructure
    if not check_terraform_state():
        response = input("\n❓ Continue with bootstrap teardown anyway? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ UAT bootstrap teardown cancelled")
            return 0
    
    # Get resources that will be destroyed
    resources = get_resources_to_destroy()
    if resources:
        print("\n📋 UAT Resources to be destroyed:")
        
        if 'terraform_state_bucket' in resources:
            bucket_name = resources['terraform_state_bucket']['value']
            print(f"   📦 S3 State Bucket: {bucket_name}")
        
        if 'dynamodb_table_name' in resources:
            table_name = resources['dynamodb_table_name']['value']
            print(f"   🗄️  DynamoDB Lock Table: {table_name}")
        
        ecr_repos = resources.get('ecr_repository_urls', {}).get('value', {})
        if ecr_repos:
            print(f"   📦 ECR Repositories: {len(ecr_repos)} repositories")
            for name, url in ecr_repos.items():
                print(f"      {name}: {url}")
    
    # Get confirmation
    print("\n⚠️  WARNING: This will permanently destroy UAT bootstrap infrastructure")
    print("⚠️  Ensure no important data or state is stored in these resources")
    
    response = input("\n❓ Do you want to proceed with UAT bootstrap teardown? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ UAT bootstrap teardown cancelled")
        return 0
    
    # Backup state before destruction
    backup_file = backup_terraform_state()
    
    # Run terraform destroy
    print("\n🔥 Destroying UAT bootstrap infrastructure...")
    
    destroy_command = ["terraform", "destroy", f"-var-file={tfvars_file}", "-auto-approve"]
    
    result = subprocess.run(
        destroy_command,
        cwd=bootstrap_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Terraform destroy failed: {result.stderr}")
        
        # Restore backup if destruction failed
        if backup_file and backup_file.exists():
            backup_file.rename(bootstrap_dir / "terraform.tfstate")
            print(f"✅ State restored from backup")
        
        return 1
    
    print("✅ UAT bootstrap infrastructure destroyed successfully!")
    print(result.stdout)
    
    # Clean up terraform files
    cleanup_files = [
        "uat.tfplan",
        ".terraform.lock.hcl",
        "uat-outputs.json",
        "terraform.tfstate.backup"
    ]
    
    for file in cleanup_files:
        file_path = bootstrap_dir / file
        if file_path.exists():
            file_path.unlink()
            print(f"🧹 Cleaned up: {file}")
    
    # Remove .terraform directory
    terraform_dir = bootstrap_dir / ".terraform"
    if terraform_dir.exists():
        import shutil
        shutil.rmtree(terraform_dir)
        print("🧹 Cleaned up: .terraform directory")
    
    # Log teardown completion
    teardown_log = {
        "timestamp": datetime.now().isoformat(),
        "environment": "UAT",
        "operation": "bootstrap_teardown_success",
        "resources_destroyed": list(resources.keys()) if resources else [],
        "backup_created": backup_file.name if backup_file else None
    }
    
    with open(bootstrap_dir / "uat-teardown-log.json", "w") as f:
        json.dump(teardown_log, f, indent=2)
    
    print("\n🎉 UAT bootstrap teardown completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Verify AWS resources have been destroyed in AWS Console")
    print("   2. Check for any remaining resources or costs")
    print("   3. Remove UAT backend configuration from main terraform if needed")
    print(f"   4. Teardown log saved to: uat-teardown-log.json")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
