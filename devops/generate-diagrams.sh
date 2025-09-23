#!/bin/bash

# Terraform Infrastructure Visualization Script
# This script generates architecture diagrams from Terraform infrastructure

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/infrastructure/terraform"
OUTPUT_DIR="$SCRIPT_DIR/docs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}🎨 Terraform Infrastructure Visualization Script${NC}"
echo -e "${BLUE}================================================${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to generate terraform graph
generate_terraform_graph() {
    echo -e "\n${YELLOW}📊 Generating Terraform dependency graphs...${NC}"
    
    cd "$TERRAFORM_DIR"
    
    # Basic dependency graph
    if terraform graph > /tmp/terraform_graph.dot 2>/dev/null; then
        if command_exists dot; then
            dot -Tpng /tmp/terraform_graph.dot > "$OUTPUT_DIR/terraform_dependencies.png"
            dot -Tsvg /tmp/terraform_graph.dot > "$OUTPUT_DIR/terraform_dependencies.svg"
            echo -e "${GREEN}✅ Terraform dependency graph generated${NC}"
        else
            echo -e "${RED}❌ Graphviz (dot) not found. Install with: sudo apt-get install graphviz${NC}"
            cp /tmp/terraform_graph.dot "$OUTPUT_DIR/terraform_dependencies.dot"
            echo -e "${YELLOW}⚠️  DOT file saved. Install Graphviz to generate images${NC}"
        fi
    else
        echo -e "${RED}❌ Failed to generate terraform graph. Ensure terraform is initialized.${NC}"
    fi
}

# Function to generate inframap diagram
generate_inframap() {
    echo -e "\n${YELLOW}🏗️  Generating Inframap AWS diagrams...${NC}"
    
    cd "$TERRAFORM_DIR"
    
    # Set dummy AWS credentials and static AMI for diagram generation
    echo -e "${BLUE}🔧 Setting environment variables for diagram mode...${NC}"
    export AWS_ACCESS_KEY_ID="dummy"
    export AWS_SECRET_ACCESS_KEY="dummy"
    export AWS_DEFAULT_REGION="us-east-1"
    export TF_VAR_diagram_mode=1
    export TF_VAR_dev_server_ami_id=${TF_VAR_static_ami_id:-ami-12345678}
    
    echo -e "${BLUE}📋 Environment variables set:${NC}"
    echo -e "  - TF_VAR_diagram_mode=$TF_VAR_diagram_mode"
    echo -e "  - TF_VAR_dev_server_ami_id=$TF_VAR_dev_server_ami_id"
    echo -e "  - AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION"
    
    if command_exists inframap; then
        echo -e "${BLUE}⏱️  Starting terraform plan (timeout: 120 seconds)...${NC}"
        # Generate from plan with verbose output to catch hanging - timeout is 120 seconds (2 minutes)
        if timeout 120 terraform plan -out=plan.out 2>&1 | tee /tmp/terraform_plan.log; then
            echo -e "${GREEN}✅ Terraform plan completed successfully${NC}"
            echo -e "${BLUE}🔍 Converting plan to JSON...${NC}"
            terraform show -json plan.out > plan.json
            echo -e "${GREEN}✅ Plan JSON generated${NC}"
            
            echo -e "${BLUE}🗺️  Generating inframap diagram from plan...${NC}"
            if inframap generate plan.json > /tmp/inframap.dot 2>&1; then
                echo -e "${GREEN}✅ Inframap DOT file generated${NC}"
                if command_exists dot; then
                    echo -e "${BLUE}🎨 Converting DOT to PNG/SVG...${NC}"
                    dot -Tpng /tmp/inframap.dot > "$OUTPUT_DIR/aws_infrastructure_plan.png"
                    dot -Tsvg /tmp/inframap.dot > "$OUTPUT_DIR/aws_infrastructure_plan.svg"
                    echo -e "${GREEN}✅ Inframap diagram generated from plan${NC}"
                else
                    cp /tmp/inframap.dot "$OUTPUT_DIR/aws_infrastructure_plan.dot"
                    echo -e "${YELLOW}⚠️  DOT file saved. Install Graphviz to generate images${NC}"
                fi
            else
                echo -e "${RED}❌ Failed to generate inframap diagram${NC}"
                echo -e "${YELLOW}📄 Checking inframap error output...${NC}"
                cat /tmp/inframap.dot || echo "No inframap output found"
            fi
            
            # Cleanup
            echo -e "${BLUE}🧹 Cleaning up temporary files...${NC}"
            rm -f plan.out plan.json
        else
            echo -e "${RED}❌ Failed to create terraform plan (timeout after 120s)${NC}"
            echo -e "${YELLOW}📄 Last 20 lines of terraform plan output:${NC}"
            tail -20 /tmp/terraform_plan.log || echo "No terraform plan log found"
        fi
    else
        echo -e "${RED}❌ Inframap not found. Install from: https://github.com/cycloidio/inframap${NC}"
    fi
}

# Function to generate environment-specific diagrams
generate_env_diagrams() {
    local env=$1
    echo -e "\n${YELLOW}🌍 Generating diagrams for environment: $env${NC}"
    
    cd "$TERRAFORM_DIR"
    
    # Set dummy AWS credentials for diagram generation
    export AWS_ACCESS_KEY_ID="dummy"
    export AWS_SECRET_ACCESS_KEY="dummy" 
    export AWS_DEFAULT_REGION="us-east-1"
    
    # Set terraform workspace or use tfvars
    if [ -f "${env}.tfvars" ]; then
        echo -e "${BLUE}📋 Using ${env}.tfvars for environment-specific variables${NC}"
        # Generate plan for specific environment with timeout
        # Set environment variables for diagram mode
        export TF_VAR_diagram_mode=1
        export TF_VAR_static_ami_id=${TF_VAR_static_ami_id:-ami-12345678}
        export TF_VAR_dev_server_ami_id=${TF_VAR_static_ami_id:-ami-12345678}
        
        echo -e "${BLUE}⏱️  Starting terraform plan for $env environment (timeout: 120 seconds)...${NC}"
        echo -e "${BLUE}📋 Using diagram mode variables for $env:${NC}"
        echo -e "  - TF_VAR_diagram_mode=$TF_VAR_diagram_mode"
        echo -e "  - TF_VAR_dev_server_ami_id=$TF_VAR_dev_server_ami_id"
        
        if timeout 120 terraform plan -var-file="${env}.tfvars" -out="${env}_plan.out" 2>&1 | tee /tmp/terraform_${env}_plan.log; then
            echo -e "${GREEN}✅ Terraform plan for $env completed${NC}"
            terraform show -json "${env}_plan.out" > "${env}_plan.json"
            
            # Generate with inframap if available
            if command_exists inframap && command_exists dot; then
                echo -e "${BLUE}🗺️  Generating inframap for $env environment...${NC}"
                # Try HCL approach first (more reliable)
                if inframap generate --hcl . > /tmp/${env}_inframap.dot 2>&1; then
                    echo -e "${GREEN}✅ Inframap DOT generated from HCL${NC}"
                    dot -Tpng /tmp/${env}_inframap.dot > "$OUTPUT_DIR/${env}_infrastructure.png"
                    dot -Tsvg /tmp/${env}_inframap.dot > "$OUTPUT_DIR/${env}_infrastructure.svg"
                    echo -e "${GREEN}✅ ${env} environment diagram generated${NC}"
                else
                    echo -e "${YELLOW}⚠️  HCL approach failed, trying plan JSON...${NC}"
                    # Fallback to plan JSON approach
                    if inframap generate "${env}_plan.json" > /tmp/${env}_inframap.dot 2>&1; then
                        echo -e "${GREEN}✅ Inframap DOT generated from plan JSON${NC}"
                        dot -Tpng /tmp/${env}_inframap.dot > "$OUTPUT_DIR/${env}_infrastructure.png"
                        dot -Tsvg /tmp/${env}_inframap.dot > "$OUTPUT_DIR/${env}_infrastructure.svg"
                        echo -e "${GREEN}✅ ${env} environment diagram generated${NC}"
                    else
                        echo -e "${RED}❌ Both HCL and plan JSON approaches failed${NC}"
                        echo -e "${YELLOW}📄 Inframap error output:${NC}"
                        cat /tmp/${env}_inframap.dot 2>/dev/null || echo "No inframap output found"
                    fi
                fi
            fi
            
            # Cleanup
            rm -f "${env}_plan.out" "${env}_plan.json"
        else
            echo -e "${RED}❌ Failed to create plan for ${env} environment (timeout after 120s)${NC}"
            echo -e "${YELLOW}📄 Last 20 lines of terraform plan output for ${env}:${NC}"
            tail -20 /tmp/terraform_${env}_plan.log || echo "No terraform plan log found for ${env}"
        fi
    else
        echo -e "${YELLOW}⚠️  No tfvars file found for ${env} environment${NC}"
    fi
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "\n${YELLOW}🔍 Checking prerequisites...${NC}"
    
    if ! command_exists terraform; then
        echo -e "${RED}❌ Terraform not found${NC}"
        exit 1
    fi
    
    if ! command_exists dot; then
        echo -e "${YELLOW}⚠️  Graphviz not found. Install with:${NC}"
        echo -e "${YELLOW}   Ubuntu/Debian: sudo apt-get install graphviz${NC}"
        echo -e "${YELLOW}   macOS: brew install graphviz${NC}"
        echo -e "${YELLOW}   Windows: choco install graphviz${NC}"
    fi
    
    if ! command_exists inframap; then
        echo -e "${YELLOW}⚠️  Inframap not found. Install from:${NC}"
        echo -e "${YELLOW}   https://github.com/cycloidio/inframap/releases${NC}"
    fi
    
    echo -e "${GREEN}✅ Prerequisites check complete${NC}"
}

# Function to generate summary
generate_summary() {
    echo -e "\n${BLUE}📋 Generated Diagrams Summary${NC}"
    echo -e "${BLUE}==============================${NC}"
    
    if [ -d "$OUTPUT_DIR" ]; then
        find "$OUTPUT_DIR" -name "*.png" -o -name "*.svg" -o -name "*.dot" | while read -r file; do
            echo -e "${GREEN}📄 $(basename "$file")${NC}"
        done
    fi
    
    echo -e "\n${BLUE}📁 Output directory: $OUTPUT_DIR${NC}"
    echo -e "${BLUE}🌐 View SVG files in browser for best quality${NC}"
}

# Function to setup terraform for diagram generation
setup_terraform_for_diagrams() {
    cd "$TERRAFORM_DIR"
    
    # Temporarily handle duplicate files
    if [ -f "intranet_load_balancer.tf.duplicate" ]; then
        echo -e "${YELLOW}ℹ️  Using cleaned terraform configuration for diagram generation${NC}"
    fi
    
    # Set dummy AWS credentials 
    export AWS_ACCESS_KEY_ID="dummy"
    export AWS_SECRET_ACCESS_KEY="dummy"
    export AWS_DEFAULT_REGION="us-east-1"
}

# Main execution
main() {
    local target_env="$1"
    
    setup_terraform_for_diagrams
    check_prerequisites
    
    # Generate basic terraform graph
    generate_terraform_graph
    
    # Generate inframap diagrams (only for main plan, not environment-specific)
    if [ -z "$target_env" ]; then
        generate_inframap
        
        # Generate environment-specific diagrams for all environments
        for env in dev uat prod; do
            generate_env_diagrams "$env"
        done
    else
        echo -e "${BLUE}🎯 Targeting specific environment: $target_env${NC}"
        # Only generate for the specified environment
        generate_env_diagrams "$target_env"
    fi
    
    # Generate summary
    generate_summary
    
    echo -e "\n${GREEN}🎉 Visualization generation complete!${NC}"
}

# Show usage if invalid arguments
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [ENVIRONMENT]"
    echo "  ENVIRONMENT: dev, uat, prod (optional - if not specified, generates all)"
    echo "  --help, -h: Show this help message"
    exit 0
fi

# Validate environment argument if provided
if [ -n "$1" ] && [[ ! "$1" =~ ^(dev|uat|prod)$ ]]; then
    echo -e "${RED}❌ Invalid environment: $1${NC}"
    echo -e "${YELLOW}Valid environments: dev, uat, prod${NC}"
    echo -e "${YELLOW}Usage: $0 [dev|uat|prod]${NC}"
    exit 1
fi

# Run main function
main "$@"
