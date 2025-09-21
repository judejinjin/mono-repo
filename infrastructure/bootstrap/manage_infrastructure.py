#!/usr/bin/env python3
"""
Multi-Environment Infrastructure Management Script
Provides unified interface for managing DEV, UAT, and PROD infrastructure deployments and teardowns.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to path for config imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def show_banner():
    """Display application banner."""
    print("🚀 Multi-Environment Infrastructure Manager")
    print("=" * 50)
    print("Environments: DEV | UAT | PROD")
    print("Operations: deploy | teardown | status")
    print()

def show_environment_status():
    """Show status of all environments."""
    print("📊 Environment Status Overview")
    print("-" * 30)
    
    bootstrap_dir = Path(__file__).parent
    environments = ["dev", "uat", "prod"]
    
    for env in environments:
        print(f"\n🏷️  {env.upper()} Environment:")
        
        # Check for tfvars file
        tfvars_file = bootstrap_dir / f"{env}.tfvars"
        if tfvars_file.exists():
            print(f"   ✅ Configuration: {tfvars_file.name}")
        else:
            print(f"   ❌ Configuration: {env}.tfvars (missing)")
        
        # Check for terraform state
        state_file = bootstrap_dir / "terraform.tfstate"
        if state_file.exists():
            # Check if state contains resources for this environment
            try:
                result = subprocess.run(
                    ["terraform", "output", "-json"],
                    cwd=bootstrap_dir,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    import json
                    outputs = json.loads(result.stdout)
                    if outputs:
                        print(f"   ✅ Bootstrap: Deployed")
                        
                        if 'terraform_state_bucket' in outputs:
                            bucket = outputs['terraform_state_bucket']['value']
                            print(f"      📦 S3 Bucket: {bucket}")
                        
                        if 'dynamodb_table_name' in outputs:
                            table = outputs['dynamodb_table_name']['value']
                            print(f"      🗄️  DynamoDB: {table}")
                        
                        ecr_repos = outputs.get('ecr_repository_urls', {}).get('value', {})
                        if ecr_repos:
                            print(f"      📦 ECR Repos: {len(ecr_repos)}")
                    else:
                        print(f"   ⚠️  Bootstrap: State exists but no outputs")
                else:
                    print(f"   ⚠️  Bootstrap: State exists but cannot read outputs")
            except Exception as e:
                print(f"   ⚠️  Bootstrap: State check failed ({e})")
        else:
            print(f"   ❌ Bootstrap: Not deployed")
        
        # Check for deployment/teardown logs
        deploy_log = bootstrap_dir / f"{env}-deployment-success.json"
        teardown_log = bootstrap_dir / f"{env}-teardown-log.json"
        
        if deploy_log.exists():
            print(f"   📜 Last Deploy: {deploy_log.stat().st_mtime}")
        
        if teardown_log.exists():
            print(f"   📜 Last Teardown: {teardown_log.stat().st_mtime}")

def deploy_environment(environment):
    """Deploy infrastructure for specified environment."""
    print(f"🚀 Deploying {environment.upper()} Environment")
    print("-" * 40)
    
    bootstrap_dir = Path(__file__).parent
    
    # Map environment to deployment script
    deploy_scripts = {
        "dev": "deploy_dev_bootstrap.py",
        "uat": "deploy_uat_bootstrap.py", 
        "prod": "deploy_prod_bootstrap.py"
    }
    
    script_name = deploy_scripts.get(environment)
    if not script_name:
        print(f"❌ Unknown environment: {environment}")
        return 1
    
    script_path = bootstrap_dir / script_name
    if not script_path.exists():
        print(f"❌ Deployment script not found: {script_name}")
        return 1
    
    # Execute deployment script
    print(f"🔧 Executing {script_name}...")
    result = subprocess.run([sys.executable, str(script_path)], cwd=bootstrap_dir)
    
    return result.returncode

def teardown_environment(environment):
    """Teardown infrastructure for specified environment."""
    print(f"🔥 Tearing down {environment.upper()} Environment")
    print("-" * 40)
    
    bootstrap_dir = Path(__file__).parent
    
    # Map environment to teardown script
    teardown_scripts = {
        "dev": "teardown_dev_bootstrap.py",
        "uat": "teardown_uat_bootstrap.py",
        "prod": "teardown_prod_bootstrap.py"
    }
    
    script_name = teardown_scripts.get(environment)
    if not script_name:
        print(f"❌ Unknown environment: {environment}")
        return 1
    
    script_path = bootstrap_dir / script_name
    if not script_path.exists():
        print(f"❌ Teardown script not found: {script_name}")
        return 1
    
    # Additional safety check for PROD
    if environment == "prod":
        print("🚨 PRODUCTION TEARDOWN INITIATED")
        print("⚠️  This will destroy PRODUCTION infrastructure!")
        
        response = input("❓ Are you absolutely sure? Type 'YES I AM SURE' to continue: ").strip()
        if response != "YES I AM SURE":
            print("❌ Production teardown cancelled")
            return 0
    
    # Execute teardown script
    print(f"🔧 Executing {script_name}...")
    result = subprocess.run([sys.executable, str(script_path)], cwd=bootstrap_dir)
    
    return result.returncode

def show_cost_estimates():
    """Show cost estimates for all environments."""
    print("💰 Infrastructure Cost Estimates")
    print("-" * 35)
    
    cost_estimates = {
        "dev": {
            "monthly": 120,
            "description": "Development environment - minimal resources"
        },
        "uat": {
            "monthly": 180,
            "description": "UAT environment - production-like but smaller"
        },
        "prod": {
            "monthly": 400,
            "description": "Production environment - full scale with HA"
        }
    }
    
    total_cost = 0
    
    for env, costs in cost_estimates.items():
        monthly = costs["monthly"]
        desc = costs["description"]
        total_cost += monthly
        
        print(f"\n🏷️  {env.upper()}: ~${monthly}/month")
        print(f"   {desc}")
    
    print(f"\n💸 Total Estimated Monthly Cost: ~${total_cost}")
    print("\n📝 Notes:")
    print("   • Costs are estimates based on typical usage")
    print("   • Actual costs may vary based on usage patterns")
    print("   • EKS clusters incur base charges (~$72/month each)")
    print("   • Data transfer and storage costs not included")
    print("   • Consider using spot instances for DEV/UAT to reduce costs")

def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-Environment Infrastructure Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_infrastructure.py status
  python manage_infrastructure.py deploy dev
  python manage_infrastructure.py deploy uat
  python manage_infrastructure.py deploy prod
  python manage_infrastructure.py teardown dev
  python manage_infrastructure.py teardown uat
  python manage_infrastructure.py teardown prod
  python manage_infrastructure.py costs
        """
    )
    
    parser.add_argument(
        "operation",
        choices=["deploy", "teardown", "status", "costs"],
        help="Operation to perform"
    )
    
    parser.add_argument(
        "environment",
        nargs="?",
        choices=["dev", "uat", "prod"],
        help="Environment to operate on (required for deploy/teardown)"
    )
    
    args = parser.parse_args()
    
    show_banner()
    
    # Handle operations that don't require environment
    if args.operation == "status":
        show_environment_status()
        return 0
    
    if args.operation == "costs":
        show_cost_estimates()
        return 0
    
    # Operations that require environment
    if not args.environment:
        print(f"❌ Environment required for {args.operation} operation")
        parser.print_help()
        return 1
    
    # Execute requested operation
    if args.operation == "deploy":
        return deploy_environment(args.environment)
    elif args.operation == "teardown":
        return teardown_environment(args.environment)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n❌ Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
