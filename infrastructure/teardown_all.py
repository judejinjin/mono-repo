#!/bin/bash
"""
Complete Infrastructure Teardown Script
Safely destroys all AWS infrastructure created by this project.

Usage:
  python teardown_all.py [--auto-approve] [--keep-bootstrap]
  
Options:
  --auto-approve    Skip confirmation prompts
  --keep-bootstrap  Don't destroy bootstrap infrastructure (S3, DynamoDB)
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to path for config imports
PROJECT_ROOT = Path(__file__).parent.parent
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
        if result.stderr:
            print(result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if check:
            return e
        return e

def confirm_destruction(auto_approve=False):
    """Get user confirmation for infrastructure destruction."""
    if auto_approve:
        return True
    
    print("\n" + "=" * 60)
    print("⚠️  DANGER: COMPLETE INFRASTRUCTURE DESTRUCTION")
    print("=" * 60)
    print("This will permanently destroy:")
    print("  🏗️  All VPC and networking infrastructure")
    print("  ☸️  EKS clusters and all applications")
    print("  📦 ECR repositories and container images")
    print("  🗄️  S3 buckets and stored data")
    print("  🔒 DynamoDB tables and state data")
    print("  🔐 IAM roles and policies")
    print("\n❌ THIS CANNOT BE UNDONE!")
    print("=" * 60)
    
    response = input("\nType 'DESTROY' to confirm complete teardown: ").strip()
    return response == 'DESTROY'

def check_aws_resources():
    """Check for existing AWS resources before teardown."""
    print("\n🔍 Checking for existing AWS resources...")
    
    setup_aws_environment()
    creds = get_aws_credentials()
    
    if not creds.get('aws_access_key_id'):
        print("❌ AWS credentials not configured")
        return False
    
    print(f"✅ AWS credentials found for region: {creds.get('region_name')}")
    
    # Check for resources with project tag
    project_name = "mono-repo-test"  # from dev.tfvars
    
    try:
        # Check VPCs
        result = run_command(
            f'aws ec2 describe-vpcs --filters "Name=tag:Project,Values={project_name}" --query "Vpcs[].VpcId" --output text',
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"📍 Found VPCs: {result.stdout.strip()}")
        
        # Check EKS clusters
        result = run_command('aws eks list-clusters --query "clusters" --output text', check=False)
        if result.returncode == 0 and result.stdout.strip():
            clusters = [c for c in result.stdout.strip().split() if project_name in c]
            if clusters:
                print(f"☸️  Found EKS clusters: {', '.join(clusters)}")
        
        # Check S3 buckets
        result = run_command('aws s3 ls', check=False)
        if result.returncode == 0:
            buckets = [line for line in result.stdout.split('\n') if project_name in line]
            if buckets:
                print(f"📦 Found S3 buckets: {len(buckets)} buckets")
        
        return True
    
    except Exception as e:
        print(f"⚠️  Could not check existing resources: {e}")
        return True  # Continue anyway

def destroy_main_infrastructure():
    """Destroy the main Terraform infrastructure."""
    print("\n" + "="*50)
    print("📍 Step 1: Destroying Main Infrastructure")
    print("="*50)
    
    terraform_dir = PROJECT_ROOT / "infrastructure" / "terraform"
    tfvars_file = "dev.tfvars"
    
    if not terraform_dir.exists():
        print(f"⚠️  Terraform directory not found: {terraform_dir}")
        return True  # Not an error if doesn't exist
    
    if not (terraform_dir / tfvars_file).exists():
        print(f"⚠️  Terraform vars file not found: {tfvars_file}")
        return True
    
    # Check if Terraform is initialized
    if not (terraform_dir / ".terraform").exists():
        print("ℹ️  Terraform not initialized, nothing to destroy in main infrastructure")
        return True
    
    # Run terraform destroy
    print("🔧 Running terraform destroy for main infrastructure...")
    result = run_command(
        f'terraform destroy -var-file="{tfvars_file}" -auto-approve',
        cwd=terraform_dir,
        check=False
    )
    
    if result.returncode == 0:
        print("✅ Main infrastructure destroyed successfully")
        return True
    else:
        print("❌ Failed to destroy main infrastructure")
        print("   You may need to manually clean up resources in AWS Console")
        return False

def destroy_bootstrap_infrastructure(keep_bootstrap=False):
    """Destroy the bootstrap Terraform infrastructure."""
    if keep_bootstrap:
        print("\n📍 Skipping bootstrap destruction (--keep-bootstrap specified)")
        return True
    
    print("\n" + "="*50)
    print("📍 Step 2: Destroying Bootstrap Infrastructure")
    print("="*50)
    
    bootstrap_dir = PROJECT_ROOT / "infrastructure" / "bootstrap"
    tfvars_file = "dev.tfvars"
    
    if not bootstrap_dir.exists():
        print(f"⚠️  Bootstrap directory not found: {bootstrap_dir}")
        return True
    
    if not (bootstrap_dir / tfvars_file).exists():
        print(f"⚠️  Bootstrap vars file not found: {tfvars_file}")
        return True
    
    # Check if Terraform is initialized
    if not (bootstrap_dir / ".terraform").exists():
        print("ℹ️  Bootstrap not initialized, nothing to destroy")
        return True
    
    # Run terraform destroy
    print("🔧 Running terraform destroy for bootstrap infrastructure...")
    result = run_command(
        f'terraform destroy -var-file="{tfvars_file}" -auto-approve',
        cwd=bootstrap_dir,
        check=False
    )
    
    if result.returncode == 0:
        print("✅ Bootstrap infrastructure destroyed successfully")
        return True
    else:
        print("❌ Failed to destroy bootstrap infrastructure")
        print("   You may need to manually delete S3 buckets and DynamoDB tables")
        return False

def cleanup_local_files():
    """Clean up local Terraform files and cache."""
    print("\n" + "="*50)
    print("📍 Step 3: Cleaning Up Local Files")
    print("="*50)
    
    # Directories to clean
    dirs_to_clean = [
        PROJECT_ROOT / "infrastructure" / "terraform",
        PROJECT_ROOT / "infrastructure" / "bootstrap"
    ]
    
    for dir_path in dirs_to_clean:
        if not dir_path.exists():
            continue
        
        print(f"🧹 Cleaning {dir_path.name}...")
        
        # Remove .terraform directory
        terraform_dir = dir_path / ".terraform"
        if terraform_dir.exists():
            try:
                import shutil
                shutil.rmtree(terraform_dir)
                print(f"   ✅ Removed .terraform directory")
            except Exception as e:
                print(f"   ⚠️  Could not remove .terraform directory: {e}")
        
        # Remove lock file
        lock_file = dir_path / ".terraform.lock.hcl"
        if lock_file.exists():
            try:
                lock_file.unlink()
                print(f"   ✅ Removed .terraform.lock.hcl")
            except Exception as e:
                print(f"   ⚠️  Could not remove lock file: {e}")
        
        # Remove state files (backup only, keep if they exist)
        state_files = [
            "terraform.tfstate.backup",
            "terraform.tfstate"
        ]
        
        for state_file in state_files:
            file_path = dir_path / state_file
            if file_path.exists():
                try:
                    # Move to backup instead of deleting
                    backup_path = file_path.with_suffix(file_path.suffix + ".backup")
                    file_path.rename(backup_path)
                    print(f"   ✅ Backed up {state_file} to {backup_path.name}")
                except Exception as e:
                    print(f"   ⚠️  Could not backup {state_file}: {e}")

def verify_cleanup():
    """Verify that resources have been cleaned up."""
    print("\n" + "="*50)
    print("📍 Step 4: Verifying Cleanup")
    print("="*50)
    
    project_name = "mono-repo-test"
    
    print("🔍 Checking for remaining resources...")
    
    # Check for remaining resources
    checks = [
        ("VPCs", f'aws ec2 describe-vpcs --filters "Name=tag:Project,Values={project_name}" --query "Vpcs[].VpcId" --output text'),
        ("EKS Clusters", 'aws eks list-clusters --query "clusters[?contains(@, `mono-repo`)]" --output text'),
        ("S3 Buckets", f'aws s3 ls | grep {project_name}'),
        ("DynamoDB Tables", f'aws dynamodb list-tables --query "TableNames[?contains(@, `{project_name}`)]" --output text'),
        ("ECR Repositories", f'aws ecr describe-repositories --query "repositories[?contains(repositoryName, `{project_name}`)].repositoryName" --output text')
    ]
    
    remaining_resources = []
    
    for resource_type, command in checks:
        result = run_command(command, check=False)
        if result.returncode == 0 and result.stdout.strip():
            remaining_resources.append(resource_type)
            print(f"   ⚠️  {resource_type}: {result.stdout.strip()}")
        else:
            print(f"   ✅ {resource_type}: None found")
    
    if remaining_resources:
        print(f"\n⚠️  Found remaining resources: {', '.join(remaining_resources)}")
        print("   You may need to manually delete these in AWS Console")
        print("   Check the deployment guide for manual cleanup steps")
        return False
    else:
        print("\n✅ All resources appear to be cleaned up!")
        return True

def main():
    """Main teardown function."""
    parser = argparse.ArgumentParser(description="Complete infrastructure teardown")
    parser.add_argument('--auto-approve', action='store_true', help='Skip confirmation prompts')
    parser.add_argument('--keep-bootstrap', action='store_true', help="Don't destroy bootstrap infrastructure")
    
    args = parser.parse_args()
    
    print("🗑️ Complete Infrastructure Teardown")
    print("=" * 50)
    
    # Check AWS resources
    if not check_aws_resources():
        return 1
    
    # Get confirmation
    if not confirm_destruction(args.auto_approve):
        print("❌ Teardown cancelled by user")
        return 0
    
    print("\n🚀 Starting teardown process...")
    
    success = True
    
    # Step 1: Destroy main infrastructure
    if not destroy_main_infrastructure():
        success = False
    
    # Step 2: Destroy bootstrap infrastructure  
    if not destroy_bootstrap_infrastructure(args.keep_bootstrap):
        success = False
    
    # Step 3: Clean up local files
    cleanup_local_files()
    
    # Step 4: Verify cleanup
    verify_cleanup()
    
    if success:
        print("\n🎉 Teardown completed successfully!")
        print("\n📋 Post-teardown checklist:")
        print("   □ Check AWS Console to verify all resources are deleted")
        print("   □ Monitor AWS billing for unexpected charges")
        print("   □ Remove AWS credentials from .env file if no longer needed")
        print("   □ Consider setting up billing alerts for future deployments")
        return 0
    else:
        print("\n⚠️  Teardown completed with some issues")
        print("   Please check AWS Console and manually delete any remaining resources")
        return 1

if __name__ == "__main__":
    sys.exit(main())
