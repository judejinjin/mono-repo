#!/bin/bash
# Complete Infrastructure Teardown Script (Bash Version)
# Safely destroys all AWS infrastructure created by this project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="mono-repo-test"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Parse command line arguments
AUTO_APPROVE=false
KEEP_BOOTSTRAP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --auto-approve)
            AUTO_APPROVE=true
            shift
            ;;
        --keep-bootstrap)
            KEEP_BOOTSTRAP=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--auto-approve] [--keep-bootstrap]"
            echo "  --auto-approve    Skip confirmation prompts"
            echo "  --keep-bootstrap  Don't destroy bootstrap infrastructure"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

run_command() {
    local cmd="$1"
    local cwd="${2:-$PWD}"
    
    echo -e "${BLUE}🔧 Running: $cmd${NC}"
    
    if cd "$cwd" && eval "$cmd"; then
        return 0
    else
        local exit_code=$?
        log_error "Command failed with exit code $exit_code"
        return $exit_code
    fi
}

confirm_destruction() {
    if [ "$AUTO_APPROVE" = true ]; then
        return 0
    fi
    
    echo
    echo "============================================================"
    echo -e "${RED}⚠️  DANGER: COMPLETE INFRASTRUCTURE DESTRUCTION${NC}"
    echo "============================================================"
    echo "This will permanently destroy:"
    echo "  🏗️  All VPC and networking infrastructure"
    echo "  ☸️  EKS clusters and all applications" 
    echo "  📦 ECR repositories and container images"
    echo "  🗄️  S3 buckets and stored data"
    echo "  🔒 DynamoDB tables and state data"
    echo "  🔐 IAM roles and policies"
    echo
    echo -e "${RED}❌ THIS CANNOT BE UNDONE!${NC}"
    echo "============================================================"
    echo
    
    read -p "Type 'DESTROY' to confirm complete teardown: " confirm
    
    if [ "$confirm" = "DESTROY" ]; then
        return 0
    else
        log_error "Teardown cancelled by user"
        exit 0
    fi
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform not found. Please install Terraform first."
        return 1
    fi
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Please install AWS CLI first."
        return 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured or invalid"
        return 1
    fi
    
    log_success "All prerequisites met"
    return 0
}

check_existing_resources() {
    log_info "Checking for existing AWS resources..."
    
    # Check VPCs
    local vpcs=$(aws ec2 describe-vpcs --filters "Name=tag:Project,Values=$PROJECT_NAME" --query "Vpcs[].VpcId" --output text 2>/dev/null || echo "")
    if [ -n "$vpcs" ]; then
        log_info "Found VPCs: $vpcs"
    fi
    
    # Check EKS clusters
    local clusters=$(aws eks list-clusters --query "clusters" --output text 2>/dev/null | grep -o "[^ ]*$PROJECT_NAME[^ ]*" || echo "")
    if [ -n "$clusters" ]; then
        log_info "Found EKS clusters: $clusters"
    fi
    
    # Check S3 buckets
    local buckets=$(aws s3 ls 2>/dev/null | grep "$PROJECT_NAME" || echo "")
    if [ -n "$buckets" ]; then
        log_info "Found S3 buckets with project name"
    fi
    
    return 0
}

destroy_main_infrastructure() {
    echo
    echo "=================================================="
    echo "📍 Step 1: Destroying Main Infrastructure"  
    echo "=================================================="
    
    local terraform_dir="$PROJECT_ROOT/infrastructure/terraform"
    local tfvars_file="dev.tfvars"
    
    if [ ! -d "$terraform_dir" ]; then
        log_warning "Terraform directory not found: $terraform_dir"
        return 0
    fi
    
    if [ ! -f "$terraform_dir/$tfvars_file" ]; then
        log_warning "Terraform vars file not found: $tfvars_file"
        return 0
    fi
    
    if [ ! -d "$terraform_dir/.terraform" ]; then
        log_info "Terraform not initialized, nothing to destroy in main infrastructure"
        return 0
    fi
    
    log_info "Running terraform destroy for main infrastructure..."
    
    if run_command "terraform destroy -var-file='$tfvars_file' -auto-approve" "$terraform_dir"; then
        log_success "Main infrastructure destroyed successfully"
        return 0
    else
        log_error "Failed to destroy main infrastructure"
        log_warning "You may need to manually clean up resources in AWS Console"
        return 1
    fi
}

destroy_bootstrap_infrastructure() {
    if [ "$KEEP_BOOTSTRAP" = true ]; then
        log_info "Skipping bootstrap destruction (--keep-bootstrap specified)"
        return 0
    fi
    
    echo
    echo "=================================================="
    echo "📍 Step 2: Destroying Bootstrap Infrastructure"
    echo "=================================================="
    
    local bootstrap_dir="$PROJECT_ROOT/infrastructure/bootstrap"
    local tfvars_file="dev.tfvars"
    
    if [ ! -d "$bootstrap_dir" ]; then
        log_warning "Bootstrap directory not found: $bootstrap_dir"
        return 0
    fi
    
    if [ ! -f "$bootstrap_dir/$tfvars_file" ]; then
        log_warning "Bootstrap vars file not found: $tfvars_file"
        return 0
    fi
    
    if [ ! -d "$bootstrap_dir/.terraform" ]; then
        log_info "Bootstrap not initialized, nothing to destroy"
        return 0
    fi
    
    log_info "Running terraform destroy for bootstrap infrastructure..."
    
    if run_command "terraform destroy -var-file='$tfvars_file' -auto-approve" "$bootstrap_dir"; then
        log_success "Bootstrap infrastructure destroyed successfully"
        return 0
    else
        log_error "Failed to destroy bootstrap infrastructure"
        log_warning "You may need to manually delete S3 buckets and DynamoDB tables"
        return 1
    fi
}

cleanup_local_files() {
    echo
    echo "=================================================="
    echo "📍 Step 3: Cleaning Up Local Files"
    echo "=================================================="
    
    local dirs_to_clean=(
        "$PROJECT_ROOT/infrastructure/terraform"
        "$PROJECT_ROOT/infrastructure/bootstrap"
    )
    
    for dir in "${dirs_to_clean[@]}"; do
        if [ ! -d "$dir" ]; then
            continue
        fi
        
        local dir_name=$(basename "$dir")
        log_info "Cleaning $dir_name..."
        
        # Remove .terraform directory
        if [ -d "$dir/.terraform" ]; then
            rm -rf "$dir/.terraform" && log_success "Removed .terraform directory" || log_warning "Could not remove .terraform directory"
        fi
        
        # Remove lock file
        if [ -f "$dir/.terraform.lock.hcl" ]; then
            rm -f "$dir/.terraform.lock.hcl" && log_success "Removed .terraform.lock.hcl" || log_warning "Could not remove lock file"
        fi
        
        # Backup state files
        for state_file in "terraform.tfstate" "terraform.tfstate.backup"; do
            if [ -f "$dir/$state_file" ]; then
                mv "$dir/$state_file" "$dir/$state_file.teardown-backup" && log_success "Backed up $state_file" || log_warning "Could not backup $state_file"
            fi
        done
    done
}

verify_cleanup() {
    echo
    echo "=================================================="
    echo "📍 Step 4: Verifying Cleanup"
    echo "=================================================="
    
    log_info "Checking for remaining resources..."
    
    local remaining_resources=()
    
    # Check VPCs
    local vpcs=$(aws ec2 describe-vpcs --filters "Name=tag:Project,Values=$PROJECT_NAME" --query "Vpcs[].VpcId" --output text 2>/dev/null || echo "")
    if [ -n "$vpcs" ] && [ "$vpcs" != "None" ]; then
        remaining_resources+=("VPCs")
        log_warning "VPCs: $vpcs"
    else
        log_success "VPCs: None found"
    fi
    
    # Check S3 buckets
    local buckets=$(aws s3 ls 2>/dev/null | grep "$PROJECT_NAME" || echo "")
    if [ -n "$buckets" ]; then
        remaining_resources+=("S3 Buckets")
        log_warning "S3 Buckets found with project name"
    else
        log_success "S3 Buckets: None found"
    fi
    
    # Check DynamoDB tables
    local tables=$(aws dynamodb list-tables --query "TableNames[?contains(@, \`$PROJECT_NAME\`)]" --output text 2>/dev/null || echo "")
    if [ -n "$tables" ] && [ "$tables" != "None" ]; then
        remaining_resources+=("DynamoDB Tables")
        log_warning "DynamoDB Tables: $tables"
    else
        log_success "DynamoDB Tables: None found"
    fi
    
    # Check ECR repositories
    local repos=$(aws ecr describe-repositories --query "repositories[?contains(repositoryName, \`$PROJECT_NAME\`)].repositoryName" --output text 2>/dev/null || echo "")
    if [ -n "$repos" ] && [ "$repos" != "None" ]; then
        remaining_resources+=("ECR Repositories")
        log_warning "ECR Repositories: $repos"
    else
        log_success "ECR Repositories: None found"
    fi
    
    if [ ${#remaining_resources[@]} -gt 0 ]; then
        log_warning "Found remaining resources: ${remaining_resources[*]}"
        log_warning "You may need to manually delete these in AWS Console"
        return 1
    else
        log_success "All resources appear to be cleaned up!"
        return 0
    fi
}

main() {
    echo "🗑️ Complete Infrastructure Teardown"
    echo "=================================================="
    
    # Check prerequisites
    if ! check_prerequisites; then
        exit 1
    fi
    
    # Check existing resources
    check_existing_resources
    
    # Get confirmation
    confirm_destruction
    
    echo
    log_info "Starting teardown process..."
    
    local overall_success=true
    
    # Step 1: Destroy main infrastructure
    if ! destroy_main_infrastructure; then
        overall_success=false
    fi
    
    # Step 2: Destroy bootstrap infrastructure
    if ! destroy_bootstrap_infrastructure; then
        overall_success=false
    fi
    
    # Step 3: Clean up local files
    cleanup_local_files
    
    # Step 4: Verify cleanup
    if ! verify_cleanup; then
        overall_success=false
    fi
    
    echo
    if [ "$overall_success" = true ]; then
        echo "🎉 Teardown completed successfully!"
        echo
        echo "📋 Post-teardown checklist:"
        echo "   □ Check AWS Console to verify all resources are deleted"
        echo "   □ Monitor AWS billing for unexpected charges"
        echo "   □ Remove AWS credentials from .env file if no longer needed"
        echo "   □ Consider setting up billing alerts for future deployments"
        exit 0
    else
        log_warning "Teardown completed with some issues"
        log_warning "Please check AWS Console and manually delete any remaining resources"
        exit 1
    fi
}

# Run main function
main "$@"
