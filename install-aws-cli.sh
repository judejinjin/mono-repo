#!/bin/bash

# AWS CLI Installation Script for Linux (Ubuntu/Debian)
# This script installs AWS CLI v2 on Linux systems

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Installing AWS CLI...${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if AWS CLI is already installed
if command_exists aws; then
    current_version=$(aws --version 2>&1 | cut -d' ' -f1 | cut -d'/' -f2)
    echo -e "${YELLOW}AWS CLI is already installed: $current_version${NC}"
    echo -e "${YELLOW}Do you want to reinstall/update? (y/N)${NC}"
    read -p "> " reinstall
    if [[ ! "$reinstall" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Skipping installation${NC}"
        exit 0
    fi
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Download AWS CLI if not already present
if [ ! -f "awscliv2.zip" ]; then
    echo -e "${YELLOW}Downloading AWS CLI installer...${NC}"
    
    # Check if curl or wget is available
    if command_exists curl; then
        curl -sSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    elif command_exists wget; then
        wget -q "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -O "awscliv2.zip"
    else
        echo -e "${RED}❌ Neither curl nor wget found. Please install one of them first:${NC}"
        echo -e "${YELLOW}sudo apt-get install curl${NC}"
        echo -e "${YELLOW}# or${NC}"
        echo -e "${YELLOW}sudo apt-get install wget${NC}"
        exit 1
    fi
fi

# Check if unzip is available
if ! command_exists unzip; then
    echo -e "${RED}❌ unzip not found. Installing...${NC}"
    sudo apt-get update && sudo apt-get install -y unzip
fi

# Extract the installer
echo -e "${YELLOW}Extracting AWS CLI installer...${NC}"
unzip -q awscliv2.zip

# Install AWS CLI
echo -e "${YELLOW}Installing AWS CLI...${NC}"
sudo ./aws/install --update

# Clean up temporary files
cd /
rm -rf "$TEMP_DIR"

# Add AWS CLI to PATH for current session (usually not needed as it installs to /usr/local/bin)
export PATH="/usr/local/bin:$PATH"

# Check installation
echo -e "${YELLOW}Checking AWS CLI installation...${NC}"
if command_exists aws; then
    version=$(aws --version)
    echo -e "${GREEN}✅ AWS CLI successfully installed: $version${NC}"
else
    echo -e "${RED}❌ AWS CLI installation failed${NC}"
    echo -e "${YELLOW}You may need to add /usr/local/bin to your PATH or restart your terminal${NC}"
    exit 1
fi

echo
echo -e "${GREEN}🎉 Installation complete!${NC}"
echo
echo -e "${YELLOW}To configure AWS CLI, run:${NC}"
echo -e "${BLUE}aws configure${NC}"
echo
echo -e "${YELLOW}Or use the setup script:${NC}"
echo -e "${BLUE}python setup_aws_credentials.py${NC}"
echo
