#!/usr/bin/env python3
"""
PROD Environment Bootstrap Teardown Script
Safely destroys PROD bootstrap infrastructure with extensive safety checks and approvals.
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

def validate_production_teardown():
    """Validate production teardown prerequisites with extensive checks."""
    print("🔍 Validating production teardown prerequisites...")
    
    checks = []
    critical_issues = []
    
    # Check for AWS credentials
    try:
        creds = get_aws_credentials()
        if creds.get('aws_access_key_id'):
            checks.append(("✅", "AWS credentials configured"))
        else:
            checks.append(("❌", "AWS credentials missing"))
            critical_issues.append("AWS credentials required")
    except Exception as e:
        checks.append(("❌", f"AWS credentials error: {e}"))
        critical_issues.append("AWS credentials error")
    
    # Check current user
    current_user = os.environ.get('USERNAME', os.environ.get('USER', 'unknown'))
    checks.append(("ℹ️", f"Running as user: {current_user}"))
    
    # Check for terraform
    try:
        result = subprocess.run(['terraform', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0].strip()
            checks.append(("✅", f"Terraform available: {version}"))
        else:
            checks.append(("❌", "Terraform not available"))
            critical_issues.append("Terraform required")
    except Exception:
        checks.append(("❌", "Terraform not installed"))
        critical_issues.append("Terraform not installed")
    
    # Check for dependent infrastructure
    main_terraform_dir = Path(__file__).parent.parent / "terraform"
    if (main_terraform_dir / "terraform.tfstate").exists():
        checks.append(("⚠️", "Main terraform state exists - may have dependencies"))
    else:
        checks.append(("✅", "No main terraform state detected"))
    
    # Print validation results
    for status, message in checks:
        print(f"   {status} {message}")
    
    if critical_issues:
        print(f"\n❌ Critical issues found:")
        for issue in critical_issues:
            print(f"   • {issue}")
        return False
    
    print("✅ Production teardown validation passed")
    return True

def get_production_teardown_approval():
    """Get extensive approval for production teardown."""
    print("\n🚨 PRODUCTION ENVIRONMENT TEARDOWN")
    print("=" * 50)
    print("⚠️  YOU ARE ABOUT TO DESTROY PRODUCTION BOOTSTRAP INFRASTRUCTURE")
    print("⚠️  THIS ACTION IS IRREVERSIBLE AND WILL:")
    print("     • Delete the production S3 state bucket")
    print("     • Delete the production DynamoDB lock table")
    print("     • Delete all production ECR repositories and images")
    print("     • Make it impossible to manage existing production infrastructure")
    print("⚠️  ENSURE ALL PRODUCTION WORKLOADS ARE SAFELY MIGRATED OR TERMINATED")
    print()
    
    # Check for emergency teardown flag
    emergency_flag = os.environ.get('EMERGENCY_TEARDOWN')
    if emergency_flag == 'CONFIRMED':
        print("🚨 EMERGENCY TEARDOWN MODE DETECTED")
        print("   Proceeding with reduced approval requirements")
        return True
    
    # Get change ticket information
    change_ticket = input("📋 Change Ticket/Approval Number (required): ").strip()
    if not change_ticket:
        print("❌ Change ticket number required for production teardown")
        return False
    
    # Get executive approval
    executive_approval = input("👤 Executive Approval by (CTO/VP Engineering): ").strip()
    if not executive_approval:
        print("❌ Executive approval required for production teardown")
        return False
    
    # Get business justification
    business_justification = input("📝 Business Justification (required): ").strip()
    if not business_justification:
        print("❌ Business justification required for production teardown")
        return False
    
    # Get data backup confirmation
    data_backup_confirmed = input("💾 Confirm all critical data backed up (yes/no): ").strip().lower()
    if data_backup_confirmed != 'yes':
        print("❌ Data backup confirmation required for production teardown")
        return False
    
    # Get downtime window
    downtime_window = input("⏰ Approved downtime window (e.g., '2024-01-15 02:00-06:00 UTC'): ").strip()
    if not downtime_window:
        print("❌ Downtime window required for production teardown")
        return False
    
    # Get disaster recovery plan
    disaster_recovery = input("🆘 Disaster Recovery Plan Reference: ").strip()
    if not disaster_recovery:
        print("⚠️  No disaster recovery plan provided - proceeding without DR reference")
    
    # Summary and confirmation
    print(f"\n📋 Production Teardown Summary:")
    print(f"   Change Ticket: {change_ticket}")
    print(f"   Executive Approval: {executive_approval}")
    print(f"   Business Justification: {business_justification}")
    print(f"   Data Backup Confirmed: {data_backup_confirmed}")
    print(f"   Downtime Window: {downtime_window}")
    print(f"   Disaster Recovery: {disaster_recovery or 'Not specified'}")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    
    # Multi-stage confirmation
    print("\n🚨 PRODUCTION TEARDOWN CONFIRMATION REQUIRED")
    print("   Type exactly what is requested for each confirmation:")
    
    # First confirmation
    response1 = input("\n1️⃣ Type 'I UNDERSTAND THE RISKS' to continue: ").strip()
    if response1 != "I UNDERSTAND THE RISKS":
        print("❌ First confirmation failed")
        return False
    
    # Second confirmation
    response2 = input("2️⃣ Type 'DESTROY PRODUCTION BOOTSTRAP' to continue: ").strip()
    if response2 != "DESTROY PRODUCTION BOOTSTRAP":
        print("❌ Second confirmation failed")
        return False
    
    # Final confirmation with executive name
    response3 = input(f"3️⃣ Type 'APPROVED BY {executive_approval.upper()}' to confirm: ").strip()
    if response3 != f"APPROVED BY {executive_approval.upper()}":
        print("❌ Final confirmation failed")
        return False
    
    # Log approval
    approval_log = {
        "timestamp": datetime.now().isoformat(),
        "change_ticket": change_ticket,
        "executive_approval": executive_approval,
        "business_justification": business_justification,
        "data_backup_confirmed": data_backup_confirmed,
        "downtime_window": downtime_window,
        "disaster_recovery": disaster_recovery,
        "environment": "PRODUCTION",
        "operation": "bootstrap_teardown_approval",
        "user": os.environ.get('USERNAME', os.environ.get('USER', 'unknown')),
        "confirmations_completed": 3
    }
    
    with open("prod-teardown-approval.json", "w") as f:
        json.dump(approval_log, f, indent=2)
    
    print("\n✅ Production teardown approved and logged")
    return True

def create_production_backup():
    """Create comprehensive backup before teardown."""
    print("\n💾 Creating production backup...")
    
    bootstrap_dir = Path(__file__).parent
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = bootstrap_dir / f"prod-backup-{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    
    # Backup terraform state
    state_file = bootstrap_dir / "terraform.tfstate"
    if state_file.exists():
        backup_state = backup_dir / "terraform.tfstate"
        import shutil
        shutil.copy2(state_file, backup_state)
        print(f"✅ State backed up to: {backup_state}")
    
    # Backup terraform configuration
    tfvars_file = bootstrap_dir / "prod.tfvars"
    if tfvars_file.exists():
        backup_tfvars = backup_dir / "prod.tfvars"
        import shutil
        shutil.copy2(tfvars_file, backup_tfvars)
        print(f"✅ Configuration backed up to: {backup_tfvars}")
    
    # Export current outputs
    result = subprocess.run(
        ["terraform", "output", "-json"],
        cwd=bootstrap_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        outputs = json.loads(result.stdout)
        backup_outputs = backup_dir / "terraform-outputs.json"
        with open(backup_outputs, "w") as f:
            json.dump(outputs, f, indent=2)
        print(f"✅ Outputs backed up to: {backup_outputs}")
        return backup_dir, outputs
    
    return backup_dir, {}

def main():
    """Main PROD bootstrap teardown function."""
    print("🔥 PRODUCTION Environment Bootstrap Teardown")
    print("=" * 50)
    
    # Validate production teardown
    if not validate_production_teardown():
        print("❌ Production teardown validation failed")
        return 1
    
    # Get production approval
    if not get_production_teardown_approval():
        print("❌ Production teardown not approved")
        return 1
    
    # Get bootstrap directory
    bootstrap_dir = Path(__file__).parent
    tfvars_file = "prod.tfvars"
    
    # Setup AWS environment
    setup_aws_environment()
    creds = get_aws_credentials()
    
    print(f"\n✅ AWS credentials configured for region: {creds.get('region_name')}")
    
    # Check for terraform state
    if not (bootstrap_dir / "terraform.tfstate").exists():
        print("⚠️  No terraform state found - nothing to destroy")
        return 0
    
    # Create comprehensive backup
    backup_dir, resources = create_production_backup()
    
    # Show resources to be destroyed
    if resources:
        print("\n📋 PRODUCTION Resources to be DESTROYED:")
        
        if 'terraform_state_bucket' in resources:
            bucket_name = resources['terraform_state_bucket']['value']
            print(f"   📦 S3 State Bucket: {bucket_name} (ALL TERRAFORM STATE WILL BE LOST)")
        
        if 'dynamodb_table_name' in resources:
            table_name = resources['dynamodb_table_name']['value']
            print(f"   🗄️  DynamoDB Lock Table: {table_name}")
        
        ecr_repos = resources.get('ecr_repository_urls', {}).get('value', {})
        if ecr_repos:
            print(f"   📦 ECR Repositories: {len(ecr_repos)} repositories (ALL IMAGES WILL BE LOST)")
            for name, url in ecr_repos.items():
                print(f"      {name}: {url}")
    
    # Final warning and countdown
    print("\n🚨 FINAL WARNING: PRODUCTION TEARDOWN STARTING")
    print("⚠️  This is your last chance to abort!")
    
    for i in range(10, 0, -1):
        print(f"   Continuing in {i} seconds... (Ctrl+C to abort)")
        import time
        time.sleep(1)
    
    # Run terraform destroy
    print("\n🔥 Destroying PRODUCTION bootstrap infrastructure...")
    
    destroy_command = ["terraform", "destroy", f"-var-file={tfvars_file}", "-auto-approve"]
    
    result = subprocess.run(
        destroy_command,
        cwd=bootstrap_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Terraform destroy failed: {result.stderr}")
        print(f"💾 Backup available at: {backup_dir}")
        
        # Try to restore state from backup
        backup_state = backup_dir / "terraform.tfstate"
        if backup_state.exists():
            import shutil
            shutil.copy2(backup_state, bootstrap_dir / "terraform.tfstate")
            print("✅ State restored from backup")
        
        return 1
    
    print("✅ PRODUCTION bootstrap infrastructure destroyed!")
    print(result.stdout)
    
    # Clean up terraform files
    cleanup_files = [
        "prod.tfplan",
        ".terraform.lock.hcl",
        "prod-outputs.json",
        "terraform.tfstate.backup",
        "terraform.tfstate"
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
        "environment": "PRODUCTION",
        "operation": "bootstrap_teardown_success",
        "resources_destroyed": list(resources.keys()) if resources else [],
        "backup_location": str(backup_dir),
        "user": os.environ.get('USERNAME', os.environ.get('USER', 'unknown')),
        "aws_region": creds.get('region_name')
    }
    
    with open(bootstrap_dir / "prod-teardown-log.json", "w") as f:
        json.dump(teardown_log, f, indent=2)
    
    print("\n🎉 PRODUCTION bootstrap teardown completed!")
    print("\n📋 CRITICAL Next Steps:")
    print("   1. ✅ Verify ALL AWS resources destroyed in AWS Console")
    print("   2. ✅ Check for any remaining resources or unexpected costs")
    print("   3. ✅ Update monitoring/alerting to remove PROD infrastructure checks")
    print("   4. ✅ Notify stakeholders of teardown completion")
    print("   5. ✅ Archive production deployment documentation")
    print(f"   6. 💾 Backup preserved at: {backup_dir}")
    print(f"   7. 📊 Teardown log: prod-teardown-log.json")
    
    print("\n⚠️  IMPORTANT:")
    print("   • Production infrastructure can no longer be managed via Terraform")
    print("   • Any existing production resources are now orphaned")
    print("   • Re-deployment requires complete bootstrap recreation")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n❌ Production teardown interrupted by user")
        print("💾 Check for backup files before retrying")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during production teardown: {e}")
        print("💾 Check for backup files and terraform state")
        sys.exit(1)
