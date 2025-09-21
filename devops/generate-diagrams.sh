#!/bin/bash

# Terraform Infrastructure Visualization Script
# This script generates architecture diagrams from Terraform infrastructure

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/infrastructure/terraform"
OUTPUT_DIR="$PROJECT_ROOT/docs/architecture"

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
    
    if command_exists inframap; then
        # Generate from plan
        if terraform plan -out=plan.out >/dev/null 2>&1; then
            terraform show -json plan.out > plan.json
            
            if inframap generate plan.json > /tmp/inframap.dot 2>/dev/null; then
                if command_exists dot; then
                    dot -Tpng /tmp/inframap.dot > "$OUTPUT_DIR/aws_infrastructure_plan.png"
                    dot -Tsvg /tmp/inframap.dot > "$OUTPUT_DIR/aws_infrastructure_plan.svg"
                    echo -e "${GREEN}✅ Inframap diagram generated from plan${NC}"
                else
                    cp /tmp/inframap.dot "$OUTPUT_DIR/aws_infrastructure_plan.dot"
                    echo -e "${YELLOW}⚠️  DOT file saved. Install Graphviz to generate images${NC}"
                fi
            else
                echo -e "${RED}❌ Failed to generate inframap diagram${NC}"
            fi
            
            # Cleanup
            rm -f plan.out plan.json
        else
            echo -e "${RED}❌ Failed to create terraform plan${NC}"
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
    
    # Set terraform workspace or use tfvars
    if [ -f "${env}.tfvars" ]; then
        # Generate plan for specific environment
        if terraform plan -var-file="${env}.tfvars" -out="${env}_plan.out" >/dev/null 2>&1; then
            terraform show -json "${env}_plan.out" > "${env}_plan.json"
            
            # Generate with inframap if available
            if command_exists inframap && command_exists dot; then
                inframap generate "${env}_plan.json" | dot -Tpng > "$OUTPUT_DIR/${env}_infrastructure.png"
                inframap generate "${env}_plan.json" | dot -Tsvg > "$OUTPUT_DIR/${env}_infrastructure.svg"
                echo -e "${GREEN}✅ ${env} environment diagram generated${NC}"
            fi
            
            # Cleanup
            rm -f "${env}_plan.out" "${env}_plan.json"
        else
            echo -e "${RED}❌ Failed to create plan for ${env} environment${NC}"
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

# Main execution
main() {
    check_prerequisites
    
    # Generate basic terraform graph
    generate_terraform_graph
    
    # Generate inframap diagrams
    generate_inframap
    
    # Generate environment-specific diagrams
    for env in dev uat prod; do
        generate_env_diagrams "$env"
    done
    
    # Generate summary
    generate_summary
    
    echo -e "\n${GREEN}🎉 Visualization generation complete!${NC}"
}

# Run main function
main "$@"
