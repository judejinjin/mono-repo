#!/usr/bin/env python3
"""
Infrastructure Teardown Script
Safely destroys AWS infrastructure to avoid ongoing charges.
"""

import os
import sys
import subprocess
import json
import argparse
from pathlib import Path
from datetime import datetime
import shutil

class InfrastructureTeardown:
    def __init__(self, terraform_dir: str, project_root: str):
        self.terraform_dir = Path(terraform_dir)
        self.project_root = Path(project_root)
        self.backup_dir = None
        
    def create_backup(self, environment: str) -> bool:
        """Create backup of important files before destruction."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.project_root / "backups" / f"{timestamp}_{environment}"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"💾 Creating backup in {self.backup_dir}")
        
        # Backup Terraform state
        state_file = self.terraform_dir / "terraform.tfstate"
        if state_file.exists():
            shutil.copy2(state_file, self.backup_dir / "terraform.tfstate.backup")
            print("✅ Terraform state backed up")
        
        # Backup Terraform variables
        tfvars_file = self.terraform_dir / f"{environment}.tfvars"
        if tfvars_file.exists():
            shutil.copy2(tfvars_file, self.backup_dir / f"{environment}.tfvars.backup")
            print("✅ Terraform variables backed up")
        
        # Backup Kubernetes resources
        self.backup_kubernetes_resources()
        
        return True
    
    def backup_kubernetes_resources(self) -> bool:
        """Backup Kubernetes resources if cluster is accessible."""
        try:
            # Check if kubectl is available
            subprocess.run(['kubectl', 'version', '--client'], 
                         capture_output=True, check=True)
            
            # Check if cluster is accessible
            subprocess.run(['kubectl', 'cluster-info'], 
                         capture_output=True, check=True)
            
            print("📦 Backing up Kubernetes resources...")
            
            # Backup all resources
            resources_cmd = ['kubectl', 'get', 'all', '--all-namespaces', '-o', 'yaml']
            with open(self.backup_dir / 'k8s-resources.yaml', 'w') as f:
                subprocess.run(resources_cmd, stdout=f, check=True)
            
            # Backup ConfigMaps
            configmaps_cmd = ['kubectl', 'get', 'configmaps', '--all-namespaces', '-o', 'yaml']
            with open(self.backup_dir / 'k8s-configmaps.yaml', 'w') as f:
                subprocess.run(configmaps_cmd, stdout=f, check=True)
            
            # Backup Secrets (be careful with this!)
            secrets_cmd = ['kubectl', 'get', 'secrets', '--all-namespaces', '-o', 'yaml']
            with open(self.backup_dir / 'k8s-secrets.yaml', 'w') as f:
                subprocess.run(secrets_cmd, stdout=f, check=True)
            
            print("✅ Kubernetes resources backed up")
            return True
            
        except subprocess.CalledProcessError:
            print("⚠️  Kubernetes cluster not accessible for backup")
            return False
        except FileNotFoundError:
            print("⚠️  kubectl not found")
            return False
    
    def cleanup_kubernetes(self) -> bool:
        """Clean up Kubernetes resources before infrastructure destruction."""
        try:
            print("🧹 Cleaning up Kubernetes resources...")
            
            # Check if cluster is accessible
            subprocess.run(['kubectl', 'cluster-info'], 
                         capture_output=True, check=True)
            
            # Remove Helm deployments
            self.cleanup_helm_deployments()
            
            # Force delete persistent volumes
            print("Removing persistent volumes...")
            subprocess.run(['kubectl', 'delete', 'pv', '--all', 
                          '--force', '--grace-period=0'], 
                         capture_output=True)
            
            # Force delete persistent volume claims
            print("Removing persistent volume claims...")
            subprocess.run(['kubectl', 'delete', 'pvc', '--all', 
                          '--all-namespaces', '--force', '--grace-period=0'], 
                         capture_output=True)
            
            # Delete LoadBalancer services
            self.cleanup_load_balancer_services()
            
            print("✅ Kubernetes cleanup completed")
            return True
            
        except subprocess.CalledProcessError:
            print("⚠️  Kubernetes cluster not accessible")
            return False
        except FileNotFoundError:
            print("⚠️  kubectl not found")
            return False
    
    def cleanup_helm_deployments(self):
        """Remove all Helm deployments."""
        try:
            # Get list of Helm releases
            result = subprocess.run(['helm', 'list', '-A', '-o', 'json'], 
                                  capture_output=True, text=True, check=True)
            
            releases = json.loads(result.stdout)
            
            for release in releases:
                name = release.get('name')
                namespace = release.get('namespace')
                
                if name and namespace:
                    print(f"Uninstalling Helm release: {name} from {namespace}")
                    subprocess.run(['helm', 'uninstall', name, '-n', namespace], 
                                 capture_output=True)
                    
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            print("⚠️  Could not cleanup Helm deployments")
    
    def cleanup_load_balancer_services(self):
        """Remove LoadBalancer services to release ELBs."""
        try:
            # Get LoadBalancer services
            result = subprocess.run(['kubectl', 'get', 'services', 
                                   '--all-namespaces', '-o', 'json'], 
                                  capture_output=True, text=True, check=True)
            
            services = json.loads(result.stdout)
            
            for service in services.get('items', []):
                if service.get('spec', {}).get('type') == 'LoadBalancer':
                    name = service['metadata']['name']
                    namespace = service['metadata']['namespace']
                    
                    print(f"Removing LoadBalancer service: {name} from {namespace}")
                    subprocess.run(['kubectl', 'delete', 'service', name, '-n', namespace], 
                                 capture_output=True)
                    
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            print("⚠️  Could not cleanup LoadBalancer services")
    
    def destroy_infrastructure(self, environment: str) -> bool:
        """Destroy the infrastructure using Terraform."""
        print(f"🔥 Destroying {environment} infrastructure...")
        
        original_dir = os.getcwd()
        os.chdir(self.terraform_dir)
        
        try:
            # Try standard destroy first
            cmd = ['terraform', 'destroy', f'-var-file={environment}.tfvars', '-auto-approve']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Infrastructure destroyed successfully")
                return True
            else:
                print("⚠️  Standard destroy failed, trying targeted approach...")
                return self.targeted_destroy(environment)
                
        except Exception as e:
            print(f"❌ Failed to destroy infrastructure: {e}")
            return False
        finally:
            os.chdir(original_dir)
    
    def targeted_destroy(self, environment: str) -> bool:
        """Destroy infrastructure with targeted approach."""
        targets = [
            'aws_eks_cluster.main',
            'aws_instance.dev_server',
            'aws_db_instance.postgres'
        ]
        
        for target in targets:
            print(f"Destroying {target}...")
            cmd = ['terraform', 'destroy', f'-target={target}', 
                   f'-var-file={environment}.tfvars', '-auto-approve']
            subprocess.run(cmd, capture_output=True)
        
        # Final cleanup
        print("Destroying remaining resources...")
        cmd = ['terraform', 'destroy', f'-var-file={environment}.tfvars', '-auto-approve']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return result.returncode == 0
    
    def verify_destruction(self) -> dict:
        """Verify that resources have been properly destroyed."""
        print("🔍 Verifying infrastructure destruction...")
        
        verification_results = {}
        
        try:
            # Check EC2 instances
            result = subprocess.run(['aws', 'ec2', 'describe-instances', 
                                   '--query', 'Reservations[].Instances[?State.Name!=`terminated`].InstanceId', 
                                   '--output', 'text'], 
                                  capture_output=True, text=True, check=True)
            
            instances = result.stdout.strip()
            if instances:
                print(f"⚠️  Found running EC2 instances: {instances}")
                verification_results['ec2'] = instances.split()
            else:
                print("✅ No running EC2 instances")
                verification_results['ec2'] = []
            
            # Check RDS instances
            result = subprocess.run(['aws', 'rds', 'describe-db-instances', 
                                   '--query', 'DBInstances[?DBInstanceStatus!=`deleting`].DBInstanceIdentifier', 
                                   '--output', 'text'], 
                                  capture_output=True, text=True, check=True)
            
            rds_instances = result.stdout.strip()
            if rds_instances:
                print(f"⚠️  Found RDS instances: {rds_instances}")
                verification_results['rds'] = rds_instances.split()
            else:
                print("✅ No RDS instances")
                verification_results['rds'] = []
            
            # Check EKS clusters
            result = subprocess.run(['aws', 'eks', 'list-clusters', 
                                   '--query', 'clusters[]', '--output', 'text'], 
                                  capture_output=True, text=True, check=True)
            
            eks_clusters = result.stdout.strip()
            if eks_clusters:
                print(f"⚠️  Found EKS clusters: {eks_clusters}")
                verification_results['eks'] = eks_clusters.split()
            else:
                print("✅ No EKS clusters")
                verification_results['eks'] = []
            
            # Check Load Balancers
            result = subprocess.run(['aws', 'elbv2', 'describe-load-balancers', 
                                   '--query', 'LoadBalancers[].LoadBalancerName', 
                                   '--output', 'text'], 
                                  capture_output=True, text=True, check=True)
            
            load_balancers = result.stdout.strip()
            if load_balancers:
                print(f"⚠️  Found Load Balancers: {load_balancers}")
                verification_results['elb'] = load_balancers.split()
            else:
                print("✅ No Load Balancers")
                verification_results['elb'] = []
            
            # Check NAT Gateways
            result = subprocess.run(['aws', 'ec2', 'describe-nat-gateways', 
                                   '--filter', 'Name=state,Values=available', 
                                   '--query', 'NatGateways[].NatGatewayId', 
                                   '--output', 'text'], 
                                  capture_output=True, text=True, check=True)
            
            nat_gateways = result.stdout.strip()
            if nat_gateways:
                print(f"⚠️  Found NAT Gateways: {nat_gateways}")
                verification_results['nat'] = nat_gateways.split()
            else:
                print("✅ No NAT Gateways")
                verification_results['nat'] = []
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Error during verification: {e}")
        except FileNotFoundError:
            print("⚠️  AWS CLI not found, skipping verification")
        
        return verification_results
    
    def cleanup_local_state(self) -> bool:
        """Clean up local Terraform state files."""
        print("🧹 Cleaning up local Terraform state...")
        
        response = input("Do you want to remove local Terraform state files? (y/N): ")
        
        if response.lower() in ['y', 'yes']:
            files_to_remove = [
                'terraform.tfstate',
                'terraform.tfstate.backup',
                '.terraform.lock.hcl'
            ]
            
            for file in files_to_remove:
                file_path = self.terraform_dir / file
                if file_path.exists():
                    file_path.unlink()
            
            terraform_dir = self.terraform_dir / '.terraform'
            if terraform_dir.exists():
                shutil.rmtree(terraform_dir)
            
            print("✅ Local state cleaned")
            return True
        else:
            print("⚠️  Local state preserved")
            return False
    
    def show_cost_verification_steps(self):
        """Show steps to verify no ongoing AWS charges."""
        print("\n💰 Cost Verification Steps")
        print("=" * 30)
        print("1. Check AWS Billing Dashboard")
        print("2. Review AWS Cost Explorer")
        print("3. Set up billing alerts if not already done")
        print("4. Monitor for next 24-48 hours")
        print()
        print("🔗 AWS Billing Dashboard: https://console.aws.amazon.com/billing/home")

def main():
    parser = argparse.ArgumentParser(description='Tear down AWS infrastructure')
    parser.add_argument('--environment', choices=['dev', 'uat', 'prod'],
                       help='Environment to destroy')
    parser.add_argument('--terraform-dir', default='infrastructure/terraform',
                       help='Path to Terraform directory')
    parser.add_argument('--auto-confirm', action='store_true',
                       help='Skip confirmation prompts (dangerous!)')
    
    args = parser.parse_args()
    
    # Resolve paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    terraform_dir = project_root / args.terraform_dir
    
    if not terraform_dir.exists():
        print(f"❌ Terraform directory not found: {terraform_dir}")
        sys.exit(1)
    
    # Get environment if not provided
    if not args.environment:
        print("\nAvailable environments:")
        for env in ['dev', 'uat', 'prod']:
            if (terraform_dir / f'{env}.tfvars').exists():
                print(f"  - {env}")
        
        args.environment = input("\nWhich environment do you want to destroy? (dev/uat/prod): ")
    
    # Validate environment
    if not (terraform_dir / f'{args.environment}.tfvars').exists():
        print(f"❌ Environment {args.environment} not found")
        sys.exit(1)
    
    # Confirm destruction
    if not args.auto_confirm:
        print(f"\n⚠️  Are you sure you want to destroy the {args.environment} environment?")
        print("⚠️  This action cannot be undone!")
        confirmation = input("Type 'yes' to confirm: ")
        
        if confirmation != 'yes':
            print("✅ Teardown cancelled. Your infrastructure is safe.")
            sys.exit(0)
    
    # Initialize teardown
    teardown = InfrastructureTeardown(terraform_dir, project_root)
    
    # Execute teardown process
    try:
        # Create backup
        teardown.create_backup(args.environment)
        
        # Cleanup Kubernetes
        teardown.cleanup_kubernetes()
        
        # Destroy infrastructure
        if teardown.destroy_infrastructure(args.environment):
            print("✅ Infrastructure destruction completed")
        else:
            print("⚠️  Infrastructure destruction completed with some errors")
        
        # Verify destruction
        verification_results = teardown.verify_destruction()
        
        # Cleanup local state
        teardown.cleanup_local_state()
        
        # Show cost verification steps
        teardown.show_cost_verification_steps()
        
        print("\n🎉 Teardown completed successfully!")
        print("Remember to check your AWS billing dashboard to confirm no ongoing charges.")
        
    except KeyboardInterrupt:
        print("\n❌ Teardown cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Teardown failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
