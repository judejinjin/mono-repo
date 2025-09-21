#!/usr/bin/env python3
"""
Update Main Terraform Backend Configuration
This script updates the main Terraform configuration to use the S3 backend created by bootstrap.
"""

import json
import sys
from pathlib import Path
import subprocess

def get_bootstrap_outputs():
    """Get outputs from the bootstrap Terraform configuration."""
    bootstrap_dir = Path(__file__).parent
    
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=bootstrap_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"❌ Failed to get bootstrap outputs: {e}")
        return None

def update_main_terraform(backend_config):
    """Update the main Terraform configuration with S3 backend."""
    main_tf_path = Path(__file__).parent.parent / "terraform" / "main.tf"
    
    if not main_tf_path.exists():
        print(f"❌ Main Terraform file not found: {main_tf_path}")
        return False
    
    # Read current main.tf
    with open(main_tf_path, 'r') as f:
        content = f.read()
    
    # Backend configuration to replace
    old_backend = '''  backend "s3" {
    bucket = "mono-repo-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "us-east-1"
    
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }'''
    
    new_backend = f'''  backend "s3" {{
    bucket = "{backend_config['bucket']}"
    key    = "{backend_config['key']}"
    region = "{backend_config['region']}"
    
    dynamodb_table = "{backend_config['dynamodb_table']}"
    encrypt        = {str(backend_config['encrypt']).lower()}
  }}'''
    
    if old_backend in content:
        updated_content = content.replace(old_backend, new_backend)
        
        # Write updated content
        with open(main_tf_path, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Updated main Terraform backend configuration in {main_tf_path}")
        return True
    else:
        print("⚠️  Could not find expected backend configuration in main.tf")
        print("   Please manually update the backend configuration:")
        print(f"   bucket = \"{backend_config['bucket']}\"")
        print(f"   dynamodb_table = \"{backend_config['dynamodb_table']}\"")
        return False

def main():
    """Main function to update Terraform backend configuration."""
    print("🔧 Updating Main Terraform Backend Configuration")
    print("=" * 55)
    
    # Get bootstrap outputs
    outputs = get_bootstrap_outputs()
    if not outputs:
        return 1
    
    backend_config = outputs.get('backend_configuration', {}).get('value', {})
    if not backend_config:
        print("❌ No backend configuration found in bootstrap outputs")
        return 1
    
    print("📋 Bootstrap outputs found:")
    print(f"   S3 Bucket: {backend_config['bucket']}")
    print(f"   DynamoDB Table: {backend_config['dynamodb_table']}")
    print(f"   Region: {backend_config['region']}")
    
    # Update main Terraform configuration
    if update_main_terraform(backend_config):
        print("\n🎉 Backend configuration updated successfully!")
        print("\nNext steps:")
        print("   1. cd ../terraform")
        print("   2. terraform init (to migrate to S3 backend)")
        print("   3. terraform plan -var-file=\"dev.tfvars\"")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
