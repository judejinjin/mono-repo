#!/bin/bash
# User data script for development server setup

set -e

# Update system
apt-get update
apt-get upgrade -y

# Install essential packages
apt-get install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    tree \
    unzip \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install Python 3.11+
add-apt-repository ppa:deadsnakes/ppa -y
apt-get update
apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    python3.11-distutils

# Set Python 3.11 as default
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
rm -rf aws awscliv2.zip

# Install Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list
apt-get update
apt-get install -y terraform

# Create development directory structure
mkdir -p /home/ubuntu/workspace
mkdir -p /home/ubuntu/.ssh

# Set up Python virtual environment
cd /home/ubuntu
python3.11 -m venv venv
chown -R ubuntu:ubuntu venv

# Install global Node.js packages
npm install -g \
    @vue/cli \
    create-react-app \
    typescript \
    ts-node \
    nodemon \
    pm2

# Set up environment variables
cat << 'EOF' >> /home/ubuntu/.bashrc
# Development environment setup
export ENVIRONMENT="${environment}"
export PATH="$PATH:/usr/local/bin"
export KUBECONFIG="/home/ubuntu/.kube/config"

# Python virtual environment
alias activate='source ~/venv/bin/activate'

# Useful aliases
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias gs='git status'
alias gd='git diff'
alias gc='git commit'
alias gp='git push'
alias gl='git pull'

# AWS and Kubernetes shortcuts
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get services'
alias kgd='kubectl get deployments'

echo "🚀 Development server ready! Environment: ${environment}"
echo "💡 Use 'activate' to enable Python virtual environment"
echo "🔧 Available tools: Python 3.11, Node.js 18, Docker, kubectl, AWS CLI, Terraform"
EOF

# Set ownership
chown -R ubuntu:ubuntu /home/ubuntu/

# Create kubectl config directory
mkdir -p /home/ubuntu/.kube
chown -R ubuntu:ubuntu /home/ubuntu/.kube

# Setup completion for kubectl
echo 'source <(kubectl completion bash)' >> /home/ubuntu/.bashrc
echo 'complete -F __start_kubectl k' >> /home/ubuntu/.bashrc

# Enable and start services
systemctl enable docker
systemctl start docker

# Log completion
echo "$(date): Development server setup completed" >> /var/log/user-data.log

# Final message
wall "Development server setup completed successfully!"
