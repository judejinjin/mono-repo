#!/bin/bash

# Virtual Environment Activation and Diagram Generation Script
# This script activates the Python virtual environment and generates Terraform diagrams

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo
echo -e "${BLUE}🚀 Activating Python Virtual Environment and Generating Diagrams${NC}"
echo -e "${BLUE}==================================================================${NC}"

# Check if virtual environment exists (look in parent directory)
if [ ! -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    echo -e "${RED}❌ Virtual environment not found in parent directory. Please run from project root.${NC}"
    echo -e "${YELLOW}To create a virtual environment:${NC}"
    echo -e "${YELLOW}cd $PROJECT_ROOT${NC}"
    echo -e "${YELLOW}python3 -m venv venv${NC}"
    echo -e "${YELLOW}source venv/bin/activate${NC}"
    echo -e "${YELLOW}pip install -r devops/requirements-diagrams.txt${NC}"
    exit 1
fi

# Activate virtual environment from parent directory
echo -e "${GREEN}✅ Activating virtual environment...${NC}"
source "$PROJECT_ROOT/venv/bin/activate"

# Check if required packages are installed
echo -e "${GREEN}✅ Checking required packages...${NC}"
if ! python -c "import matplotlib.pyplot" 2>/dev/null; then
    echo -e "${YELLOW}📦 Installing required packages...${NC}"
    python -m pip install -r requirements-diagrams.txt
fi

echo
echo -e "${BLUE}🎨 Generating Architecture Diagrams...${NC}"
echo -e "${BLUE}=====================================${NC}"

# Change to project root for correct relative paths
cd "$PROJECT_ROOT"

# Generate visual diagrams with matplotlib
echo -e "${YELLOW}📊 Creating architecture diagrams...${NC}"
python devops/create_architecture_diagrams.py

# Generate CI/CD flow diagram
echo -e "${YELLOW}📊 Creating CI/CD flow diagram...${NC}"
python devops/create_cicd_flow_diagram.py

# Generate Airflow diagrams
echo -e "${YELLOW}📊 Creating Airflow diagrams...${NC}"
python devops/create_airflow_diagrams.py

# Generate Dash analytics diagrams  
echo -e "${YELLOW}📊 Creating Dash analytics diagrams...${NC}"
python devops/create_dash_diagrams.py

# Generate Risk API diagrams
echo -e "${YELLOW}📊 Creating Risk API diagrams...${NC}"
python devops/create_risk_api_diagrams.py

# Generate Web Apps diagrams
echo -e "${YELLOW}📊 Creating Web Apps diagrams...${NC}"
python devops/create_web_apps_diagrams.py

# Generate detailed descriptions
echo -e "${YELLOW}📄 Creating detailed descriptions...${NC}"
python devops/generate_terraform_diagrams.py --terraform-dir infrastructure/terraform --output-dir docs/architecture --environments dev uat prod

echo
echo -e "${GREEN}🎉 Diagram generation complete!${NC}"
echo -e "${BLUE}📁 Output directory: docs/architecture/${NC}"
echo -e "${BLUE}🖼️  Visual diagrams: *.png and *.svg files${NC}"
echo -e "${BLUE}📄 Documentation: *.md files${NC}"
echo
echo -e "${YELLOW}💡 To view diagrams:${NC}"
echo -e "${YELLOW}   - Open PNG/SVG files in your browser or image viewer${NC}"
echo -e "${YELLOW}   - Read MD files for detailed architecture descriptions${NC}"
echo

# Keep shell active (equivalent to cmd /k)
echo -e "${GREEN}Virtual environment is still active. Type 'deactivate' to exit.${NC}"
exec "$SHELL"
