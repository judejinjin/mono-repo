#!/usr/bin/env python3
"""
Risk API Service Architecture Diagram Generator
Creates detailed diagrams showing Risk API service infrastructure components.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
from pathlib import Path

def create_risk_api_diagram():
    """Create comprehensive Risk API service architecture diagram."""
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 16))
    
    # Main architecture diagram
    ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=2, rowspan=2)
    ax1.set_xlim(0, 20)
    ax1.set_ylim(0, 16)
    ax1.set_aspect('equal')
    ax1.axis('off')
    
    # Service flow diagram
    ax2 = plt.subplot2grid((3, 2), (2, 0))
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 6)
    ax2.set_aspect('equal')
    ax2.axis('off')
    
    # Component details
    ax3 = plt.subplot2grid((3, 2), (2, 1))
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 6)
    ax3.set_aspect('equal')
    ax3.axis('off')
    
    # Define colors
    colors = {
        'corporate_network': '#E6E6FA',
        'aws_cloud': '#E8F4FD',
        'vpc': '#D4EDDA',
        'eks': '#E2E3E5',
        'fastapi': '#FF6B6B',
        'database': '#4ECDC4',
        'loadbalancer': '#45B7D1',
        'ecr': '#FFA07A',
        'secrets': '#98D8C8',
        'iam': '#F7DC6F'
    }
    
    # Main Architecture Diagram
    ax1.text(10, 15.5, 'Risk API Service Architecture', 
             fontsize=20, fontweight='bold', ha='center')
    
    # Corporate Network boundary
    corp_rect = patches.Rectangle((0.5, 0.5), 19, 14.5, linewidth=3, 
                                  edgecolor='purple', facecolor=colors['corporate_network'], alpha=0.2)
    ax1.add_patch(corp_rect)
    ax1.text(1, 14.7, 'Corporate Intranet', fontsize=14, fontweight='bold', color='purple')
    
    # AWS Cloud boundary
    aws_rect = patches.Rectangle((1, 2), 18, 12, linewidth=2, 
                                 edgecolor='blue', facecolor=colors['aws_cloud'], alpha=0.3)
    ax1.add_patch(aws_rect)
    ax1.text(1.5, 13.5, 'AWS Cloud - US-East-1', fontsize=12, fontweight='bold', color='blue')
    
    # VPC boundary
    vpc_rect = patches.Rectangle((2, 3), 16, 10, linewidth=2, 
                                 edgecolor='green', facecolor=colors['vpc'], alpha=0.3)
    ax1.add_patch(vpc_rect)
    ax1.text(2.5, 12.5, 'VPC (10.0.0.0/16)', fontsize=11, fontweight='bold', color='green')
    
    # Load Balancer (ALB)
    alb_rect = FancyBboxPatch((3, 11), 3, 1.5, boxstyle="round,pad=0.1",
                              facecolor=colors['loadbalancer'], edgecolor='black', linewidth=2)
    ax1.add_patch(alb_rect)
    ax1.text(4.5, 11.75, 'Internal ALB\n/api/* → FastAPI', 
             fontsize=10, fontweight='bold', ha='center', va='center')
    
    # EKS Cluster
    eks_rect = patches.Rectangle((3, 7), 14, 3.5, linewidth=2, 
                                 edgecolor='darkblue', facecolor=colors['eks'], alpha=0.4)
    ax1.add_patch(eks_rect)
    ax1.text(3.5, 10.2, 'EKS Cluster', fontsize=12, fontweight='bold', color='darkblue')
    
    # FastAPI Service Pods
    for i, env in enumerate(['dev', 'uat', 'prod']):
        x_pos = 4 + i * 4
        pod_rect = FancyBboxPatch((x_pos, 8), 3, 1.5, boxstyle="round,pad=0.1",
                                  facecolor=colors['fastapi'], edgecolor='black', linewidth=1)
        ax1.add_patch(pod_rect)
        ax1.text(x_pos + 1.5, 8.75, f'FastAPI\n{env.upper()}\nPort: 8000', 
                 fontsize=9, fontweight='bold', ha='center', va='center', color='white')
    
    # Database Services
    db_y = 5
    # PostgreSQL RDS
    for i, env in enumerate(['dev', 'uat', 'prod']):
        x_pos = 4 + i * 4
        db_rect = FancyBboxPatch((x_pos, db_y), 3, 1.2, boxstyle="round,pad=0.1",
                                 facecolor=colors['database'], edgecolor='black', linewidth=1)
        ax1.add_patch(db_rect)
        ax1.text(x_pos + 1.5, db_y + 0.6, f'PostgreSQL\nRDS {env.upper()}', 
                 fontsize=9, fontweight='bold', ha='center', va='center')
    
    # US-East-1 Region box (AWS Services & External) 
    us_east_1_rect = patches.Rectangle((3, 0.5), 14, 1.8, linewidth=2, 
                                      edgecolor='purple', facecolor='#F5F0FF', alpha=0.3)
    ax1.add_patch(us_east_1_rect)
    ax1.text(10, 1.9, 'US-East-1 Region (AWS Services & External)', ha='center', va='center', 
           fontsize=10, fontweight='bold', color='purple')
    
    # Snowflake (External) - positioned beside ECR in region box
    snowflake_rect = FancyBboxPatch((11, 0.7), 3, 0.8, boxstyle="round,pad=0.1",
                                    facecolor='lightblue', edgecolor='black', linewidth=2)
    ax1.add_patch(snowflake_rect)
    ax1.text(12.5, 1.1, 'Snowflake\nAnalytics DB', 
             fontsize=9, fontweight='bold', ha='center', va='center')
    
    # ECR Repository - moved to US-East-1 region beside Snowflake
    ecr_rect = FancyBboxPatch((7.5, 0.7), 3, 0.8, boxstyle="round,pad=0.1",
                              facecolor=colors['ecr'], edgecolor='black', linewidth=2)
    ax1.add_patch(ecr_rect)
    ax1.text(9, 1.1, 'ECR Repository\nrisk-api images', 
             fontsize=9, fontweight='bold', ha='center', va='center')
    
    # VPC Endpoints for AWS service connectivity
    vpc_endpoint_ecr = patches.Rectangle((8, 2.8), 2, 0.4, linewidth=1, 
                                        edgecolor='gray', facecolor='lightgray', alpha=0.6)
    ax1.add_patch(vpc_endpoint_ecr)
    ax1.text(9, 3, 'ECR VPC Endpoint', ha='center', va='center', fontsize=8)
    
    # Secrets Manager - moved to fill ECR's former space
    secrets_rect = FancyBboxPatch((7, 11), 3, 1.5, boxstyle="round,pad=0.1",
                                  facecolor=colors['secrets'], edgecolor='black', linewidth=2)
    ax1.add_patch(secrets_rect)
    ax1.text(8.5, 11.75, 'Secrets Manager\nDB Credentials', 
             fontsize=10, fontweight='bold', ha='center', va='center')
    
    # IAM Role - repositioned
    iam_rect = FancyBboxPatch((11, 11), 3, 1.5, boxstyle="round,pad=0.1",
                              facecolor=colors['iam'], edgecolor='black', linewidth=2)
    ax1.add_patch(iam_rect)
    ax1.text(12.5, 11.75, 'IAM Role\nrisk-api-role', 
             fontsize=10, fontweight='bold', ha='center', va='center')
    
    # Add arrows showing data flow
    # ALB to FastAPI
    ax1.annotate('', xy=(5.5, 8), xytext=(4.5, 11),
                arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    
    # FastAPI to Database
    for i in range(3):
        x_pos = 5.5 + i * 4
        ax1.annotate('', xy=(x_pos, 6.2), xytext=(x_pos, 8),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))
    
    # ECR to VPC endpoint connection (container image deployment)
    ax1.annotate('', xy=(9, 2.8), xytext=(9, 1.5),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='orange', linestyle='dashed'))
    
    # VPC endpoint to FastAPI Apps (image pull)
    ax1.annotate('', xy=(6, 8), xytext=(9, 3.2),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='orange', linestyle='dashed'))
    ax1.text(7, 5.5, 'Image\nPull', fontsize=7, color='orange')
    
    # Snowflake analytics connection
    ax1.annotate('', xy=(10, 8), xytext=(12.5, 1.5),
                arrowprops=dict(arrowstyle='<->', lw=1.5, color='purple'))
    ax1.text(11.5, 4.5, 'Analytics\nData', fontsize=7, color='purple', rotation=60)
    
    # Service Flow Diagram (ax2)
    ax2.text(5, 5.5, 'API Request Flow', fontsize=14, fontweight='bold', ha='center')
    
    flow_components = [
        (1, 4, 'User'),
        (3, 4, 'ALB'),
        (5, 4, 'FastAPI'),
        (7, 4, 'Database'),
        (9, 4, 'Response')
    ]
    
    for i, (x, y, label) in enumerate(flow_components):
        color = ['lightgray', colors['loadbalancer'], colors['fastapi'], colors['database'], 'lightgreen'][i]
        rect = FancyBboxPatch((x-0.4, y-0.3), 0.8, 0.6, boxstyle="round,pad=0.05",
                              facecolor=color, edgecolor='black')
        ax2.add_patch(rect)
        ax2.text(x, y, label, fontsize=9, fontweight='bold', ha='center', va='center')
        
        if i < len(flow_components) - 1:
            ax2.annotate('', xy=(flow_components[i+1][0]-0.4, y), xytext=(x+0.4, y),
                        arrowprops=dict(arrowstyle='->', lw=1.5, color='red'))
    
    # Add step labels
    steps = ['1. HTTP Request', '2. Route /api/*', '3. Process', '4. Query Data', '5. JSON Response']
    for i, step in enumerate(steps):
        ax2.text(1 + i*2, 3, step, fontsize=8, ha='center', rotation=0)
    
    # Component Details (ax3)
    ax3.text(5, 5.5, 'API Endpoints & Features', fontsize=14, fontweight='bold', ha='center')
    
    endpoints = [
        'GET /health - Health check',
        'POST /api/v1/risk/calculate - Risk metrics',
        'GET /api/v1/market/data - Market data',
        'POST /api/v1/reports/generate - Reports',
        'GET / - Service info'
    ]
    
    for i, endpoint in enumerate(endpoints):
        ax3.text(0.2, 4.5 - i*0.6, f'• {endpoint}', fontsize=9, va='center')
    
    # Technical specs
    specs = [
        'Framework: FastAPI 0.104.1',
        'Runtime: Uvicorn ASGI',
        'Database: PostgreSQL + Snowflake',
        'Authentication: JWT (planned)',
        'Scaling: HPA enabled'
    ]
    
    ax3.text(5, 2.5, 'Technical Specifications:', fontsize=11, fontweight='bold')
    for i, spec in enumerate(specs):
        ax3.text(5, 2 - i*0.3, f'• {spec}', fontsize=9, va='center')
    
    plt.tight_layout()
    return fig

def create_risk_api_deployment_diagram():
    """Create Risk API deployment and scaling diagram."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    
    # Deployment Pipeline (ax1)
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.set_aspect('equal')
    ax1.axis('off')
    ax1.text(5, 9.5, 'Risk API Deployment Pipeline', fontsize=16, fontweight='bold', ha='center')
    
    pipeline_steps = [
        (2, 8, 'Code\nCommit', 'lightblue'),
        (2, 6.5, 'Build\nImage', 'orange'),
        (2, 5, 'Push\nECR', 'lightcoral'),
        (2, 3.5, 'Deploy\nK8s', 'lightgreen'),
        (2, 2, 'Health\nCheck', 'yellow')
    ]
    
    for x, y, label, color in pipeline_steps:
        rect = FancyBboxPatch((x-0.5, y-0.4), 1, 0.8, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black')
        ax1.add_patch(rect)
        ax1.text(x, y, label, fontsize=10, fontweight='bold', ha='center', va='center')
    
    # Add arrows between steps
    for i in range(len(pipeline_steps) - 1):
        y1 = pipeline_steps[i][1] - 0.4
        y2 = pipeline_steps[i+1][1] + 0.4
        ax1.annotate('', xy=(2, y2), xytext=(2, y1),
                    arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    
    # Environment progression
    envs = [
        (6, 7, 'DEV', 'lightblue', '1 replica'),
        (6, 5, 'UAT', 'orange', '1-2 replicas'),
        (6, 3, 'PROD', 'lightcoral', '2-5 replicas')
    ]
    
    for x, y, env, color, replicas in envs:
        rect = FancyBboxPatch((x-0.7, y-0.5), 1.4, 1, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black')
        ax1.add_patch(rect)
        ax1.text(x, y+0.2, env, fontsize=12, fontweight='bold', ha='center', va='center')
        ax1.text(x, y-0.2, replicas, fontsize=9, ha='center', va='center')
    
    # Scaling Diagram (ax2)
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_aspect('equal')
    ax2.axis('off')
    ax2.text(5, 9.5, 'Auto-Scaling Behavior', fontsize=16, fontweight='bold', ha='center')
    
    # CPU usage graph simulation
    x_vals = np.linspace(1, 9, 50)
    cpu_usage = 30 + 20 * np.sin(x_vals) + 10 * np.sin(2*x_vals) + np.random.normal(0, 3, 50)
    cpu_usage = np.clip(cpu_usage, 0, 100)
    
    ax2.plot(x_vals, 2 + cpu_usage/20, 'b-', linewidth=2, label='CPU Usage %')
    ax2.axhline(y=5.5, color='red', linestyle='--', label='Scale-up threshold (70%)')
    ax2.axhline(y=3.5, color='green', linestyle='--', label='Scale-down threshold (30%)')
    
    # Replica count simulation
    replica_count = []
    current_replicas = 2
    for cpu in cpu_usage:
        if cpu > 70 and current_replicas < 5:
            current_replicas += 1
        elif cpu < 30 and current_replicas > 2:
            current_replicas -= 1
        replica_count.append(current_replicas)
    
    ax2_twin = ax2.twinx()
    ax2_twin.plot(x_vals, replica_count, 'g-', linewidth=2, label='Pod Count')
    ax2_twin.set_ylim(0, 6)
    ax2_twin.set_ylabel('Pod Count', fontsize=12)
    
    ax2.set_xlabel('Time', fontsize=12)
    ax2.set_ylabel('CPU Usage %', fontsize=12)
    ax2.legend(loc='upper left')
    ax2_twin.legend(loc='upper right')
    
    plt.tight_layout()
    return fig

def main():
    """Generate all Risk API diagrams."""
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "docs" / "architecture"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating Risk API Service diagrams...")
    print(f"Output directory: {output_dir.absolute()}")
    
    # Generate architecture diagram
    fig1 = create_risk_api_diagram()
    fig1.savefig(output_dir / "risk_api_architecture.png", dpi=300, bbox_inches='tight')
    fig1.savefig(output_dir / "risk_api_architecture.svg", format='svg', bbox_inches='tight')
    plt.close(fig1)
    print("Risk API architecture diagram saved (PNG + SVG)")
    
    # Generate deployment diagram
    fig2 = create_risk_api_deployment_diagram()
    fig2.savefig(output_dir / "risk_api_deployment.png", dpi=300, bbox_inches='tight')
    fig2.savefig(output_dir / "risk_api_deployment.svg", format='svg', bbox_inches='tight')
    plt.close(fig2)
    print("Risk API deployment diagram saved (PNG + SVG)")
    
    print("All Risk API diagrams generated successfully!")

if __name__ == "__main__":
    main()
