#!/usr/bin/env python3
"""
Terraform Workflow Diagram Generator
=====================================

This script creates comprehensive visual diagrams documenting the Terraform workflows
for building and maintaining infrastructure in the mono-repo project.

Created: September 25, 2025
Author: AI Assistant 
Purpose: Document Terraform infrastructure workflows and lifecycle management
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import matplotlib.patheffects as path_effects
from pathlib import Path
import numpy as np

# Configuration
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "architecture"
DIAGRAMS = [
    "terraform_deployment_workflow",
    "terraform_environment_lifecycle", 
    "terraform_state_management"
]

def setup_plot():
    """Setup matplotlib with corporate styling"""
    plt.style.use('default')
    plt.rcParams.update({
        'font.size': 10,
        'font.family': 'Arial',
        'axes.linewidth': 1.2,
        'figure.facecolor': 'white'
    })

def create_fancy_box(ax, x, y, width, height, text, color, text_color='black', 
                    box_style="round,pad=0.1", fontsize=10, fontweight='normal'):
    """Create a styled box with text"""
    # Create fancy box
    box = FancyBboxPatch((x, y), width, height,
                        boxstyle=box_style,
                        facecolor=color, 
                        edgecolor='black',
                        linewidth=1.5,
                        alpha=0.8)
    ax.add_patch(box)
    
    # Add text with shadow effect
    text_obj = ax.text(x + width/2, y + height/2, text, 
                      ha='center', va='center',
                      color=text_color,
                      fontsize=fontsize,
                      fontweight=fontweight,
                      wrap=True)
    text_obj.set_path_effects([path_effects.withStroke(linewidth=2, foreground='white')])
    
    return box

def add_arrow(ax, start, end, color='black', style='->', linewidth=2, alpha=0.8):
    """Add arrow between points"""
    arrow = patches.FancyArrowPatch(start, end,
                                   arrowstyle=style,
                                   color=color,
                                   linewidth=linewidth,
                                   alpha=alpha,
                                   mutation_scale=20)
    ax.add_patch(arrow)
    return arrow

def add_workflow_step(ax, x, y, step_num, title, description, color, arrow_to=None):
    """Add a workflow step box with optional arrow to next step"""
    # Step number circle
    circle = plt.Circle((x, y + 1), 0.3, color='darkblue', alpha=0.8)
    ax.add_patch(circle)
    ax.text(x, y + 1, str(step_num), ha='center', va='center', 
           color='white', fontweight='bold', fontsize=12)
    
    # Step content box
    create_fancy_box(ax, x-1.5, y-0.5, 3, 1, f"{title}\n{description}", 
                    color, fontsize=9, fontweight='bold')
    
    # Arrow to next step
    if arrow_to:
        add_arrow(ax, (x+1.5, y), (arrow_to[0]-1.5, arrow_to[1]), 'darkblue')

def create_deployment_workflow_diagram():
    """Create Terraform deployment workflow diagram"""
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    
    # Title
    ax.text(8, 11.5, 'Terraform Infrastructure Deployment Workflow', 
           ha='center', va='center', fontsize=16, fontweight='bold')
    ax.text(8, 11, 'Complete lifecycle from bootstrap to production deployment', 
           ha='center', va='center', fontsize=12, style='italic')

    # Environment Preparation Phase
    ax.text(2, 10.2, 'Phase 1: Environment Preparation', 
           ha='left', va='center', fontsize=14, fontweight='bold', color='darkgreen')
    
    # Step 1: AWS Credentials Setup
    add_workflow_step(ax, 2, 9, 1, "AWS Credentials", 
                     "python setup_aws_credentials.py\nConfigure .env file", 
                     'lightblue', (6, 9))
    
    # Step 2: Dependencies Installation
    add_workflow_step(ax, 6, 9, 2, "Install Dependencies", 
                     "pip install -r requirements/dev.txt\nTerraform & Python packages", 
                     'lightgreen', (10, 9))
    
    # Step 3: Environment Selection
    add_workflow_step(ax, 10, 9, 3, "Environment Selection", 
                     "Choose: dev.tfvars / uat.tfvars / prod.tfvars\nSet free_trial flag", 
                     'lightyellow', (14, 9))

    # Bootstrap Phase
    ax.text(2, 7.7, 'Phase 2: Bootstrap Infrastructure', 
           ha='left', va='center', fontsize=14, fontweight='bold', color='darkorange')
    
    # Bootstrap workflow steps
    add_workflow_step(ax, 2, 6.5, 4, "Deploy Bootstrap", 
                     "cd infrastructure/bootstrap\npython deploy_bootstrap.py", 
                     'peachpuff', (6, 6.5))
    
    add_workflow_step(ax, 6, 6.5, 5, "Create State Backend", 
                     "S3 bucket + DynamoDB table\nECR repositories", 
                     'lightcoral', (10, 6.5))
    
    add_workflow_step(ax, 10, 6.5, 6, "Update Backend Config", 
                     "python update_main_backend.py\nConfigure remote state", 
                     'lightsalmon', (14, 6.5))

    # Main Infrastructure Phase
    ax.text(2, 5.2, 'Phase 3: Main Infrastructure Deployment', 
           ha='left', va='center', fontsize=14, fontweight='bold', color='darkred')
    
    # Main deployment steps
    add_workflow_step(ax, 2, 4, 7, "Terraform Init", 
                     "cd infrastructure/terraform\nterraform init", 
                     'lavender', (6, 4))
    
    add_workflow_step(ax, 6, 4, 8, "Terraform Plan", 
                     "terraform plan -var-file=env.tfvars\nValidate resources", 
                     'lightsteelblue', (10, 4))
    
    add_workflow_step(ax, 10, 4, 9, "Terraform Apply", 
                     "terraform apply -var-file=env.tfvars\nDeploy infrastructure", 
                     'lightpink', (14, 4))

    # Validation Phase
    ax.text(2, 2.7, 'Phase 4: Validation & Monitoring', 
           ha='left', va='center', fontsize=14, fontweight='bold', color='purple')
    
    add_workflow_step(ax, 2, 1.5, 10, "Validate Deployment", 
                     "python validate_parameter_store.py\nTest resource access", 
                     'thistle', (6, 1.5))
    
    add_workflow_step(ax, 6, 1.5, 11, "Monitor Resources", 
                     "python cost_monitor.py\nCloudWatch dashboards", 
                     'plum', (10, 1.5))
    
    add_workflow_step(ax, 10, 1.5, 12, "Documentation", 
                     "Generate diagrams\nUpdate deployment guides", 
                     'mediumpurple', None)

    # Add environment boxes on the right
    create_fancy_box(ax, 14.5, 7, 1.3, 1.5, "DEV\nEnvironment\n\n• t3.micro\n• Single AZ\n• Free tier", 'lightblue')
    create_fancy_box(ax, 14.5, 5, 1.3, 1.5, "UAT\nEnvironment\n\n• t3.small\n• Multi AZ\n• Prod-like", 'lightyellow')  
    create_fancy_box(ax, 14.5, 3, 1.3, 1.5, "PROD\nEnvironment\n\n• t3.medium+\n• HA setup\n• Full scale", 'lightcoral')

    ax.set_aspect('equal')
    ax.axis('off')
    
    # Save diagram
    for ext in ['png', 'svg']:
        filename = f"{DIAGRAMS[0]}.{ext}"
        if ext == 'svg':
            fig.savefig(OUTPUT_DIR / filename, format='svg', bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
        else:
            fig.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
    
    plt.close()
    print(f"✅ Created Terraform deployment workflow diagram")

def create_environment_lifecycle_diagram():
    """Create environment lifecycle management diagram"""
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    
    # Title
    ax.text(8, 11.5, 'Terraform Environment Lifecycle Management', 
           ha='center', va='center', fontsize=16, fontweight='bold')
    ax.text(8, 11, 'Multi-environment deployment and management strategy', 
           ha='center', va='center', fontsize=12, style='italic')

    # Development Environment
    dev_x, dev_y = 2, 8.5
    create_fancy_box(ax, dev_x-0.5, dev_y, 3, 2, 
                    "DEV Environment\n(10.0.0.0/16)\n\n• Development server\n• t3.micro instances\n• Free tier optimized\n• Single AZ deployment", 
                    'lightblue', fontsize=10)
    
    # UAT Environment  
    uat_x, uat_y = 7, 8.5
    create_fancy_box(ax, uat_x-0.5, uat_y, 3, 2,
                    "UAT Environment\n(10.1.0.0/16)\n\n• User acceptance testing\n• t3.small instances\n• Multi-AZ setup\n• Production-like config",
                    'lightyellow', fontsize=10)
    
    # Production Environment
    prod_x, prod_y = 12, 8.5
    create_fancy_box(ax, prod_x-0.5, prod_y, 3, 2,
                    "PROD Environment\n(10.2.0.0/16)\n\n• Production workloads\n• t3.medium+ instances\n• High availability\n• Full monitoring",
                    'lightcoral', fontsize=10)

    # Resource Components (shared across environments)
    components = [
        ("VPC + Subnets", 2, 6.5, 'lightsteelblue'),
        ("EKS Cluster", 5, 6.5, 'lightgreen'),
        ("RDS Database", 8, 6.5, 'lightpink'),
        ("Load Balancer", 11, 6.5, 'lightsalmon'),
        ("Parameter Store", 14, 6.5, 'lavender')
    ]
    
    for comp_name, x, y, color in components:
        create_fancy_box(ax, x-0.7, y, 1.4, 0.8, comp_name, color, fontsize=9)
        
        # Arrows from each environment to components
        for env_x in [dev_x, uat_x, prod_x]:
            add_arrow(ax, (env_x, dev_y), (x, y+0.8), color='gray', alpha=0.5, linewidth=1)

    # Lifecycle operations
    ax.text(8, 5.5, 'Lifecycle Operations', 
           ha='center', va='center', fontsize=14, fontweight='bold', color='darkblue')

    # Operation boxes
    operations = [
        ("Deploy", 2, 4, "terraform apply\n-var-file=env.tfvars", 'lightgreen'),
        ("Update", 5, 4, "terraform plan\nterraform apply", 'lightyellow'), 
        ("Scale", 8, 4, "Update tfvars\nModify resources", 'lightblue'),
        ("Monitor", 11, 4, "CloudWatch\nCost monitoring", 'lightpink'),
        ("Teardown", 14, 4, "terraform destroy\n-var-file=env.tfvars", 'lightcoral')
    ]
    
    for op_name, x, y, description, color in operations:
        create_fancy_box(ax, x-0.8, y, 1.6, 1, f"{op_name}\n\n{description}", color, fontsize=9)

    # State Management Section
    ax.text(8, 2.8, 'Terraform State Management', 
           ha='center', va='center', fontsize=14, fontweight='bold', color='darkgreen')
    
    # State components
    create_fancy_box(ax, 1, 1.5, 4.5, 1, 
                    "Bootstrap Infrastructure\n• S3 bucket for remote state\n• DynamoDB for state locking\n• ECR repositories", 
                    'lightsteelblue', fontsize=10)
    
    create_fancy_box(ax, 6, 1.5, 4.5, 1,
                    "Remote State Backend\n• Versioned state files\n• Concurrent access protection\n• Encrypted storage", 
                    'lightgreen', fontsize=10)
    
    create_fancy_box(ax, 11, 1.5, 4.5, 1,
                    "State Validation\n• Drift detection\n• Resource validation\n• Backup procedures", 
                    'lightpink', fontsize=10)

    ax.set_aspect('equal')
    ax.axis('off')
    
    # Save diagram
    for ext in ['png', 'svg']:
        filename = f"{DIAGRAMS[1]}.{ext}"
        if ext == 'svg':
            fig.savefig(OUTPUT_DIR / filename, format='svg', bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
        else:
            fig.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
    
    plt.close()
    print(f"✅ Created Terraform environment lifecycle diagram")

def create_state_management_diagram():
    """Create Terraform state management workflow diagram"""
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    
    # Title
    ax.text(8, 11.5, 'Terraform State Management & Backend Configuration', 
           ha='center', va='center', fontsize=16, fontweight='bold')
    ax.text(8, 11, 'Remote state backend setup and management procedures', 
           ha='center', va='center', fontsize=12, style='italic')

    # Local State (Initial)
    create_fancy_box(ax, 1, 9, 3, 1.5, 
                    "Local State\n(Bootstrap Phase)\n\nterraform.tfstate\nStored locally", 
                    'lightgray', fontsize=10)
    
    # Arrow to bootstrap
    add_arrow(ax, (4, 9.7), (6, 9.7), 'darkblue')
    
    # Bootstrap Process
    create_fancy_box(ax, 6, 8.5, 4, 2.5, 
                    "Bootstrap Deployment\n\n1. Create S3 bucket\n2. Create DynamoDB table\n3. Create ECR repositories\n4. Generate backend config\n\npython deploy_bootstrap.py", 
                    'lightblue', fontsize=10)
    
    # Arrow to remote state
    add_arrow(ax, (10, 9.7), (12, 9.7), 'darkblue')
    
    # Remote State (Production)
    create_fancy_box(ax, 12, 9, 3, 1.5, 
                    "Remote State\n(Production)\n\nS3 + DynamoDB\nEncrypted & Versioned", 
                    'lightgreen', fontsize=10)

    # S3 State Backend Details
    ax.text(2, 7, 'S3 State Backend', 
           ha='left', va='center', fontsize=14, fontweight='bold', color='darkblue')
    
    s3_features = [
        ("Bucket Naming", 1, 6, "mono-repo-{env}-terraform-state-{random}", 'lightsteelblue'),
        ("Versioning", 5.5, 6, "Enabled for state history\nRollback capability", 'lightblue'),
        ("Encryption", 10, 6, "AES256 server-side\nBucket key enabled", 'lightcyan'),
        ("Access Control", 13.5, 6, "Public access blocked\nIAM permissions only", 'lightpink')
    ]
    
    for title, x, y, description, color in s3_features:
        create_fancy_box(ax, x-0.7, y-0.4, 1.4, 0.8, f"{title}\n{description}", color, fontsize=8)

    # DynamoDB Lock Table
    ax.text(2, 4.8, 'DynamoDB State Locking', 
           ha='left', va='center', fontsize=14, fontweight='bold', color='darkgreen')
    
    dynamodb_features = [
        ("Table Naming", 1, 4, "mono-repo-{env}-state-lock\nHash key: LockID", 'lightgreen'),
        ("Billing Mode", 5.5, 4, "Pay-per-request\nCost optimized", 'lightseagreen'),
        ("Concurrency", 10, 4, "Prevents simultaneous\nterraform operations", 'lightblue'),
        ("Reliability", 13.5, 4, "Highly available\nManaged service", 'lightcoral')
    ]
    
    for title, x, y, description, color in dynamodb_features:
        create_fancy_box(ax, x-0.7, y-0.4, 1.4, 0.8, f"{title}\n{description}", color, fontsize=8)

    # Backend Configuration Process
    ax.text(8, 2.8, 'Backend Configuration Workflow', 
           ha='center', va='center', fontsize=14, fontweight='bold', color='darkred')
    
    # Configuration steps
    config_steps = [
        (2, 1.8, "1. Generate Config", "python update_main_backend.py\nCreates backend.tf"),
        (5.5, 1.8, "2. Initialize Backend", "terraform init\nMigrate to remote state"),
        (9, 1.8, "3. Verify State", "terraform state list\nValidate migration"),
        (12.5, 1.8, "4. Remove Local", "rm terraform.tfstate*\nClean local files")
    ]
    
    for x, y, title, description in config_steps:
        create_fancy_box(ax, x-0.8, y-0.4, 1.6, 0.8, f"{title}\n{description}", 'lavender', fontsize=8)
        
        # Connect steps with arrows
        if x != 12.5:  # Don't add arrow from last step
            next_x = config_steps[config_steps.index((x, y, title, description)) + 1][0]
            add_arrow(ax, (x+0.8, y), (next_x-0.8, y), 'purple', linewidth=1.5)

    # Environment-specific backend configs
    create_fancy_box(ax, 0.5, 0.2, 5, 0.8, 
                    "DEV Backend\nbucket = mono-repo-dev-terraform-state-{id}\ntable = mono-repo-dev-state-lock", 
                    'lightblue', fontsize=8)
    
    create_fancy_box(ax, 5.5, 0.2, 5, 0.8,
                    "UAT Backend\nbucket = mono-repo-uat-terraform-state-{id}\ntable = mono-repo-uat-state-lock", 
                    'lightyellow', fontsize=8)
    
    create_fancy_box(ax, 11, 0.2, 5, 0.8,
                    "PROD Backend\nbucket = mono-repo-prod-terraform-state-{id}\ntable = mono-repo-prod-state-lock", 
                    'lightcoral', fontsize=8)

    ax.set_aspect('equal')
    ax.axis('off')
    
    # Save diagram
    for ext in ['png', 'svg']:
        filename = f"{DIAGRAMS[2]}.{ext}"
        if ext == 'svg':
            fig.savefig(OUTPUT_DIR / filename, format='svg', bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
        else:
            fig.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
    
    plt.close()
    print(f"✅ Created Terraform state management diagram")

def create_documentation_summary():
    """Create comprehensive documentation summary for Terraform workflows"""
    summary = f"""# Terraform Workflow Documentation

This documentation accompanies the visual diagrams created for Terraform infrastructure management.

## Generated Diagrams

### 1. Terraform Deployment Workflow (`{DIAGRAMS[0]}`)
**Purpose**: Complete end-to-end deployment process from environment setup to production deployment

**Key Phases**:
- **Phase 1**: Environment Preparation (credentials, dependencies, environment selection)
- **Phase 2**: Bootstrap Infrastructure (S3 bucket, DynamoDB table, ECR repositories)  
- **Phase 3**: Main Infrastructure Deployment (terraform init/plan/apply)
- **Phase 4**: Validation & Monitoring (resource validation, cost monitoring, documentation)

**Environments Supported**:
- **DEV**: Free tier optimized (t3.micro, single AZ)
- **UAT**: Production-like (t3.small, multi-AZ) 
- **PROD**: Full scale (t3.medium+, high availability)

### 2. Environment Lifecycle Management (`{DIAGRAMS[1]}`)
**Purpose**: Multi-environment strategy and lifecycle operations

**Environment Strategy**:
- **Network Isolation**: Separate VPC CIDR ranges (10.0.x.x/16, 10.1.x.x/16, 10.2.x.x/16)
- **Resource Scaling**: Environment-appropriate instance sizing and configuration
- **Shared Components**: VPC, EKS, RDS, ALB, Parameter Store across all environments

**Lifecycle Operations**:
- **Deploy**: Fresh environment deployment
- **Update**: Resource modifications and updates
- **Scale**: Resource sizing and capacity changes
- **Monitor**: CloudWatch and cost monitoring
- **Teardown**: Safe infrastructure removal

### 3. State Management & Backend (`{DIAGRAMS[2]}`)
**Purpose**: Terraform remote state backend configuration and management

**Backend Components**:
- **S3 State Storage**: Versioned, encrypted state files
- **DynamoDB Locking**: Concurrent access prevention
- **Environment Isolation**: Separate backends per environment

**Configuration Process**:
1. **Bootstrap Phase**: Create S3 bucket and DynamoDB table
2. **Backend Migration**: Move from local to remote state
3. **State Validation**: Verify successful migration
4. **Local Cleanup**: Remove local state files

## Usage Instructions

### Initial Deployment
```bash
# 1. Setup environment
python setup_aws_credentials.py

# 2. Deploy bootstrap infrastructure
cd infrastructure/bootstrap
python deploy_bootstrap.py --environment=dev

# 3. Deploy main infrastructure
cd ../terraform
terraform init
terraform plan -var-file="dev.tfvars"
terraform apply -var-file="dev.tfvars"
```

### Environment Management
```bash
# Update infrastructure
terraform plan -var-file="env.tfvars"
terraform apply -var-file="env.tfvars"

# Monitor costs
python devops/cost_monitor.py

# Validate deployment
python scripts/validate_parameter_store.py --environment=dev
```

### Teardown Procedures
```bash
# Safe teardown with backups
terraform destroy -var-file="env.tfvars"

# Emergency stop (preserves data)
./devops/emergency-stop.sh

# Complete teardown (includes bootstrap)
python infrastructure/teardown_all.py --environment=dev
```

## Security & Best Practices

### State Security
- Remote state stored in encrypted S3 buckets
- State locking prevents concurrent modifications
- IAM permissions control state access
- State file versioning enables rollback

### Environment Isolation
- Separate AWS accounts recommended for PROD
- Network isolation via VPC CIDR ranges
- Environment-specific IAM roles and policies
- Parameter Store namespacing by environment

### Cost Management
- Free tier optimization for development
- Resource tagging for cost allocation
- Automated cost monitoring and alerts
- Environment-appropriate resource sizing

### Operational Security
- Multi-step deployment validation
- Backup procedures before infrastructure changes  
- Emergency procedures for rapid response
- Comprehensive audit trails via CloudTrail

## File Structure
```
infrastructure/
├── bootstrap/              # Bootstrap infrastructure
│   ├── deploy_bootstrap.py  # Automated bootstrap deployment
│   └── main.tf             # S3/DynamoDB/ECR resources
├── terraform/              # Main infrastructure  
│   ├── main.tf             # Core Terraform configuration
│   ├── vpc.tf              # Network infrastructure
│   ├── eks.tf              # Kubernetes cluster
│   ├── rds.tf              # Database infrastructure
│   └── modules/            # Reusable Terraform modules
└── guides/                 # Deployment documentation
    ├── DEPLOYMENT_GUIDE.md      # Development deployment
    ├── UAT_DEPLOYMENT_GUIDE.md  # UAT deployment
    └── PROD_DEPLOYMENT_GUIDE.md # Production deployment
```

Created: September 25, 2025
Generated by: create_terraform_workflow_diagram.py
"""

    doc_file = OUTPUT_DIR / "TERRAFORM_WORKFLOW_DOCUMENTATION.md"
    doc_file.write_text(summary, encoding='utf-8')
    print(f"✅ Created comprehensive Terraform workflow documentation")

def main():
    """Main execution function"""
    print("🚀 Generating Terraform Workflow Diagrams...")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Setup matplotlib
    setup_plot()
    
    # Generate diagrams
    create_deployment_workflow_diagram()
    create_environment_lifecycle_diagram() 
    create_state_management_diagram()
    
    # Create documentation
    create_documentation_summary()
    
    print("\n✅ All Terraform workflow diagrams generated successfully!")
    print(f"📊 Generated {len(DIAGRAMS)} diagrams (PNG + SVG formats)")
    print(f"📖 Created comprehensive documentation")
    print(f"🔧 View diagrams in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()