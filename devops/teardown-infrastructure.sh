#!/bin/bash

# Infrastructure Teardown Script
# Safely destroys AWS infrastructure to avoid ongoing charges

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/infrastructure/terraform"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}🔥 Infrastructure Teardown Script${NC}"
echo -e "${RED}===================================${NC}"
echo -e "${YELLOW}⚠️  This will DESTROY your AWS infrastructure!${NC}"
echo -e "${YELLOW}⚠️  Make sure you have backed up any important data!${NC}"

# Function to prompt for confirmation
confirm_destruction() {
    local environment=$1
    echo -e "\n${RED}Are you sure you want to destroy the ${environment} environment?${NC}"
    echo -e "${RED}This action cannot be undone!${NC}"
    read -p "Type 'yes' to confirm: " confirmation
    
    if [ "$confirmation" != "yes" ]; then
        echo -e "${GREEN}Teardown cancelled. Your infrastructure is safe.${NC}"
        exit 0
    fi
}

# Function to backup critical data
backup_data() {
    local environment=$1
    echo -e "\n${BLUE}💾 Creating backup before teardown...${NC}"
    
    BACKUP_DIR="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)_${environment}"
    mkdir -p "$BACKUP_DIR"
    
    cd "$TERRAFORM_DIR"
    
    # Backup Terraform state
    if [ -f "terraform.tfstate" ]; then
        cp terraform.tfstate "$BACKUP_DIR/terraform.tfstate.backup"
        echo -e "${GREEN}✅ Terraform state backed up${NC}"
    fi
    
    # Backup Terraform vars
    if [ -f "${environment}.tfvars" ]; then
        cp "${environment}.tfvars" "$BACKUP_DIR/${environment}.tfvars.backup"
        echo -e "${GREEN}✅ Terraform variables backed up${NC}"
    fi
    
    # Export Kubernetes resources (if cluster exists)
    if command -v kubectl >/dev/null 2>&1; then
        echo -e "${YELLOW}📦 Attempting to backup Kubernetes resources...${NC}"
        
        # Try to get cluster info
        if kubectl cluster-info >/dev/null 2>&1; then
            kubectl get all --all-namespaces -o yaml > "$BACKUP_DIR/k8s-resources.yaml" 2>/dev/null || true
            kubectl get configmaps --all-namespaces -o yaml > "$BACKUP_DIR/k8s-configmaps.yaml" 2>/dev/null || true
            kubectl get secrets --all-namespaces -o yaml > "$BACKUP_DIR/k8s-secrets.yaml" 2>/dev/null || true
            echo -e "${GREEN}✅ Kubernetes resources backed up${NC}"
        else
            echo -e "${YELLOW}⚠️  Kubernetes cluster not accessible for backup${NC}"
        fi
    fi
    
    echo -e "${GREEN}💾 Backup completed: $BACKUP_DIR${NC}"
}

# Function to pre-cleanup Kubernetes resources
cleanup_kubernetes() {
    echo -e "\n${BLUE}🧹 Cleaning up Kubernetes resources...${NC}"
    
    if command -v kubectl >/dev/null 2>&1; then
        if kubectl cluster-info >/dev/null 2>&1; then
            echo -e "${YELLOW}Removing Helm deployments...${NC}"
            
            # Remove Helm deployments
            if command -v helm >/dev/null 2>&1; then
                helm list -A | tail -n +2 | awk '{print $1, $2}' | while read -r release namespace; do
                    if [ -n "$release" ] && [ -n "$namespace" ]; then
                        echo "Uninstalling $release from $namespace..."
                        helm uninstall "$release" -n "$namespace" || true
                    fi
                done
            fi
            
            # Force delete stuck resources
            echo -e "${YELLOW}Removing persistent volumes...${NC}"
            kubectl delete pv --all --force --grace-period=0 || true
            
            echo -e "${YELLOW}Removing persistent volume claims...${NC}"
            kubectl delete pvc --all --all-namespaces --force --grace-period=0 || true
            
            # Delete load balancer services (to release ELBs)
            echo -e "${YELLOW}Removing load balancer services...${NC}"
            kubectl get services --all-namespaces -o json | \
                jq -r '.items[] | select(.spec.type=="LoadBalancer") | "\(.metadata.namespace) \(.metadata.name)"' | \
                while read -r namespace service; do
                    if [ -n "$namespace" ] && [ -n "$service" ]; then
                        kubectl delete service "$service" -n "$namespace" || true
                    fi
                done
            
            echo -e "${GREEN}✅ Kubernetes cleanup completed${NC}"
        else
            echo -e "${YELLOW}⚠️  Kubernetes cluster not accessible${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  kubectl not found${NC}"
    fi
}

# Function to destroy infrastructure
destroy_infrastructure() {
    local environment=$1
    echo -e "\n${RED}🔥 Destroying ${environment} infrastructure...${NC}"
    
    cd "$TERRAFORM_DIR"
    
    # Destroy specific environment
    if [ -f "${environment}.tfvars" ]; then
        echo -e "${YELLOW}Destroying infrastructure for ${environment} environment...${NC}"
        
        # First, try to destroy without targeting (cleanest approach)
        terraform destroy -var-file="${environment}.tfvars" -auto-approve || {
            echo -e "${YELLOW}⚠️  Standard destroy failed, trying targeted approach...${NC}"
            
            # If that fails, try destroying in order (dependent resources first)
            echo -e "${YELLOW}Destroying EKS cluster...${NC}"
            terraform destroy -target=aws_eks_cluster.main -var-file="${environment}.tfvars" -auto-approve || true
            
            echo -e "${YELLOW}Destroying EC2 instances...${NC}"
            terraform destroy -target=aws_instance.dev_server -var-file="${environment}.tfvars" -auto-approve || true
            
            echo -e "${YELLOW}Destroying RDS instances...${NC}"
            terraform destroy -target=aws_db_instance.postgres -var-file="${environment}.tfvars" -auto-approve || true
            
            echo -e "${YELLOW}Destroying remaining resources...${NC}"
            terraform destroy -var-file="${environment}.tfvars" -auto-approve || true
        }
    else
        echo -e "${RED}❌ No tfvars file found for ${environment} environment${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Infrastructure destruction completed${NC}"
}

# Function to verify destruction
verify_destruction() {
    echo -e "\n${BLUE}🔍 Verifying infrastructure destruction...${NC}"
    
    if command -v aws >/dev/null 2>&1; then
        echo -e "${YELLOW}Checking for remaining resources...${NC}"
        
        # Check EC2 instances
        echo "Checking EC2 instances..."
        instances=$(aws ec2 describe-instances --query 'Reservations[].Instances[?State.Name!=`terminated`].InstanceId' --output text)
        if [ -n "$instances" ]; then
            echo -e "${RED}⚠️  Found running EC2 instances: $instances${NC}"
        else
            echo -e "${GREEN}✅ No running EC2 instances${NC}"
        fi
        
        # Check RDS instances
        echo "Checking RDS instances..."
        rds_instances=$(aws rds describe-db-instances --query 'DBInstances[?DBInstanceStatus!=`deleting`].DBInstanceIdentifier' --output text 2>/dev/null || echo "")
        if [ -n "$rds_instances" ]; then
            echo -e "${RED}⚠️  Found RDS instances: $rds_instances${NC}"
        else
            echo -e "${GREEN}✅ No RDS instances${NC}"
        fi
        
        # Check EKS clusters
        echo "Checking EKS clusters..."
        eks_clusters=$(aws eks list-clusters --query 'clusters[]' --output text 2>/dev/null || echo "")
        if [ -n "$eks_clusters" ]; then
            echo -e "${RED}⚠️  Found EKS clusters: $eks_clusters${NC}"
        else
            echo -e "${GREEN}✅ No EKS clusters${NC}"
        fi
        
        # Check Load Balancers
        echo "Checking Load Balancers..."
        load_balancers=$(aws elbv2 describe-load-balancers --query 'LoadBalancers[].LoadBalancerName' --output text 2>/dev/null || echo "")
        if [ -n "$load_balancers" ]; then
            echo -e "${RED}⚠️  Found Load Balancers: $load_balancers${NC}"
        else
            echo -e "${GREEN}✅ No Load Balancers${NC}"
        fi
        
        # Check NAT Gateways
        echo "Checking NAT Gateways..."
        nat_gateways=$(aws ec2 describe-nat-gateways --filter Name=state,Values=available --query 'NatGateways[].NatGatewayId' --output text 2>/dev/null || echo "")
        if [ -n "$nat_gateways" ]; then
            echo -e "${RED}⚠️  Found NAT Gateways: $nat_gateways${NC}"
        else
            echo -e "${GREEN}✅ No NAT Gateways${NC}"
        fi
        
    else
        echo -e "${YELLOW}⚠️  AWS CLI not found, skipping verification${NC}"
    fi
}

# Function to clean up local state
cleanup_local_state() {
    echo -e "\n${BLUE}🧹 Cleaning up local Terraform state...${NC}"
    
    cd "$TERRAFORM_DIR"
    
    # Ask if user wants to clean state
    read -p "Do you want to remove local Terraform state files? (y/N): " clean_state
    if [ "$clean_state" = "y" ] || [ "$clean_state" = "Y" ]; then
        rm -f terraform.tfstate terraform.tfstate.backup .terraform.lock.hcl
        rm -rf .terraform/
        echo -e "${GREEN}✅ Local state cleaned${NC}"
    else
        echo -e "${YELLOW}⚠️  Local state preserved${NC}"
    fi
}

# Function to show cost verification steps
show_cost_verification() {
    echo -e "\n${BLUE}💰 Cost Verification Steps${NC}"
    echo -e "${BLUE}==========================${NC}"
    echo -e "${YELLOW}1. Check AWS Billing Dashboard${NC}"
    echo -e "${YELLOW}2. Review AWS Cost Explorer${NC}"
    echo -e "${YELLOW}3. Set up billing alerts if not already done${NC}"
    echo -e "${YELLOW}4. Monitor for next 24-48 hours${NC}"
    echo ""
    echo -e "${GREEN}🔗 AWS Billing Dashboard: https://console.aws.amazon.com/billing/home${NC}"
}

# Main execution
main() {
    # Check if terraform is available
    if ! command -v terraform >/dev/null 2>&1; then
        echo -e "${RED}❌ Terraform not found${NC}"
        exit 1
    fi
    
    # Get environment from user
    if [ $# -eq 0 ]; then
        echo -e "\n${BLUE}Available environments:${NC}"
        for env in dev uat prod; do
            if [ -f "$TERRAFORM_DIR/${env}.tfvars" ]; then
                echo -e "${GREEN}  - $env${NC}"
            fi
        done
        echo ""
        read -p "Which environment do you want to destroy? (dev/uat/prod): " environment
    else
        environment=$1
    fi
    
    # Validate environment
    if [ ! -f "$TERRAFORM_DIR/${environment}.tfvars" ]; then
        echo -e "${RED}❌ Environment ${environment} not found${NC}"
        exit 1
    fi
    
    # Confirm destruction
    confirm_destruction "$environment"
    
    # Create backup
    backup_data "$environment"
    
    # Pre-cleanup Kubernetes
    cleanup_kubernetes
    
    # Destroy infrastructure
    destroy_infrastructure "$environment"
    
    # Verify destruction
    verify_destruction
    
    # Clean up local state
    cleanup_local_state
    
    # Show cost verification steps
    show_cost_verification
    
    echo -e "\n${GREEN}🎉 Teardown completed successfully!${NC}"
    echo -e "${GREEN}Remember to check your AWS billing dashboard to confirm no ongoing charges.${NC}"
}

# Run main function
main "$@"
