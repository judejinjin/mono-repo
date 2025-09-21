#!/usr/bin/env python3
"""
Corporate CI/CD Flow Diagram Generator
Shows Bamboo-Bitbucket integration within corporate intranet
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

def create_cicd_flow_diagram():
    """Create CI/CD flow diagram showing Bamboo-Bitbucket integration."""
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Color scheme
    colors = {
        'corporate_network': 'lightblue',
        'aws_cloud': 'orange',
        'bitbucket': 'blue',
        'bamboo': 'green', 
        'vpn': 'purple',
        'eks': 'darkblue',
        'arrow': 'red'
    }
    
    # Set up the plot
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Title
    ax.text(8, 11.5, 'Original Corporate CI/CD Flow: Bitbucket → Bamboo → ECR → EKS', 
           fontsize=16, ha='center', va='center', fontweight='bold')
    
    # Corporate Network Box
    corp_network = patches.Rectangle((0.5, 6), 7, 5, linewidth=2, 
                                   edgecolor='blue', facecolor=colors['corporate_network'], alpha=0.3)
    ax.add_patch(corp_network)
    ax.text(0.7, 10.7, 'Corporate Intranet Network', fontsize=12, fontweight='bold')
    
    # AWS Cloud Box
    aws_cloud = patches.Rectangle((9, 1), 6.5, 10, linewidth=2, 
                                edgecolor='orange', facecolor=colors['aws_cloud'], alpha=0.3)
    ax.add_patch(aws_cloud)
    ax.text(9.2, 10.7, 'AWS Cloud (VPC)', fontsize=12, fontweight='bold')
    
    # Bitbucket Server
    bitbucket = patches.Rectangle((1, 8.5), 2.5, 1.5, linewidth=2, 
                                edgecolor='darkblue', facecolor=colors['bitbucket'], alpha=0.8)
    ax.add_patch(bitbucket)
    ax.text(2.25, 9.25, 'Bitbucket Server\n(Source Control)', fontsize=10, ha='center', va='center', 
           fontweight='bold', color='white')
    
    # Bamboo Server (larger to contain build steps)
    bamboo = patches.Rectangle((4, 6.5), 3.5, 4, linewidth=2, 
                             edgecolor='darkgreen', facecolor=colors['bamboo'], alpha=0.8)
    ax.add_patch(bamboo)
    ax.text(5.75, 10, 'Bamboo Server (CI/CD)', fontsize=11, ha='center', va='center', 
           fontweight='bold', color='white')
    
    # On-Premise Development Server
    dev_server = patches.Rectangle((1, 6.5), 2.5, 1.2, linewidth=1, 
                                 edgecolor='darkgray', facecolor='lightblue', alpha=0.8)
    ax.add_patch(dev_server)
    ax.text(2.25, 7.1, 'On-Premise\nDev Server', fontsize=9, ha='center', va='center', fontweight='bold')
    
    # VPN Connection
    vpn = patches.Rectangle((7.5, 7.5), 1.5, 2, linewidth=2, 
                          edgecolor='purple', facecolor=colors['vpn'], alpha=0.8)
    ax.add_patch(vpn)
    ax.text(8.25, 8.5, 'VPN\nGateway', fontsize=10, ha='center', va='center', 
           fontweight='bold', color='white')
    
    # Internal ALB (center-aligned in VPC)
    alb = patches.Rectangle((10.75, 8), 2.5, 1, linewidth=2, 
                          edgecolor='darkorange', facecolor='orange', alpha=0.8)
    ax.add_patch(alb)
    ax.text(12, 8.5, 'Internal ALB', fontsize=10, ha='center', va='center', fontweight='bold')
    
    # EKS Cluster (center-aligned in VPC)
    eks = patches.Rectangle((10, 5), 4, 2.5, linewidth=2, 
                          edgecolor='darkblue', facecolor=colors['eks'], alpha=0.4)
    ax.add_patch(eks)
    ax.text(12, 6.25, 'EKS Cluster', fontsize=12, ha='center', va='center', fontweight='bold')
    
    # Applications in EKS (adjusted for center-aligned EKS)
    apps = [
        {'name': 'FastAPI', 'pos': (10.3, 5.5), 'size': (0.8, 0.6)},
        {'name': 'WebApps', 'pos': (11.2, 5.5), 'size': (0.8, 0.6)},
        {'name': 'Dash', 'pos': (12.1, 5.5), 'size': (0.8, 0.6)},
        {'name': 'Airflow', 'pos': (13, 5.5), 'size': (0.8, 0.6)}
    ]
    
    for app in apps:
        app_rect = patches.Rectangle(app['pos'], app['size'][0], app['size'][1],
                                   linewidth=1, edgecolor='white', facecolor='lightblue', alpha=0.9)
        ax.add_patch(app_rect)
        ax.text(app['pos'][0] + app['size'][0]/2, app['pos'][1] + app['size'][1]/2, 
               app['name'], ha='center', va='center', fontsize=8, fontweight='bold')
    
    # ECR Repository (center-aligned in VPC)
    ecr = patches.Rectangle((11, 3), 2, 1, linewidth=2, 
                           edgecolor='orange', facecolor='lightyellow', alpha=0.8)
    ax.add_patch(ecr)
    ax.text(12, 3.5, 'ECR\n(Container Registry)', fontsize=9, ha='center', va='center', fontweight='bold')
    
    # Flow Arrows and Labels
    
    # 1. Developer commits code (vertical arrow to Bitbucket)
    ax.annotate('1. Push Code', xy=(2.25, 8.5), xytext=(2.25, 7.7),
                arrowprops=dict(arrowstyle='->', lw=2, color=colors['arrow']),
                fontsize=9, ha='center', color=colors['arrow'], fontweight='bold')
    
    # 2. Bitbucket triggers Bamboo
    ax.annotate('2. Webhook\nTrigger', xy=(4, 9.25), xytext=(3.5, 9.25),
                arrowprops=dict(arrowstyle='->', lw=2, color=colors['arrow']),
                fontsize=9, ha='center', color=colors['arrow'], fontweight='bold')
    
    # Steps 3-6 ordered top to bottom, center-aligned in Bamboo box (x=5.75 for center)
    
    # 3. Build & Test (top position)
    ax.text(5.75, 9.5, '3. Build & Test\n• Unit Tests\n• Integration Tests\n• Security Scans', 
           fontsize=10, ha='center', va='center', 
           bbox=dict(boxstyle="round,pad=0.4", facecolor='lightgreen', alpha=0.9), color='darkgreen')
    
    # 4. Push Images to ECR (second from top)
    ax.text(5.75, 8.7, '4. Push Images\nto ECR', fontsize=10, ha='center', va='center',
           bbox=dict(boxstyle="round,pad=0.4", facecolor='lightyellow', alpha=0.9), color='darkorange')
    ax.annotate('', xy=(11, 4), xytext=(6.3, 8.7),
                arrowprops=dict(arrowstyle='->', lw=2, color=colors['arrow'], linestyle='--'))
    
    # 5. Deploy Direct to EKS (third from top)
    ax.text(5.75, 7.9, '5. Deploy to\nEKS API', fontsize=10, ha='center', va='center',
           bbox=dict(boxstyle="round,pad=0.4", facecolor='lightcyan', alpha=0.9), color='darkgreen')
    ax.annotate('', xy=(10, 6.25), xytext=(6.3, 7.9),
                arrowprops=dict(arrowstyle='->', lw=2, color='darkgreen', linestyle=':'))
    
    # 6. Verify via ALB (bottom position)
    ax.text(5.75, 7.1, '6. Verify via\nALB Health', fontsize=10, ha='center', va='center',
           bbox=dict(boxstyle="round,pad=0.4", facecolor='lightblue', alpha=0.9), color='blue')
    ax.annotate('', xy=(11.25, 8), xytext=(6.3, 7.1),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='blue', linestyle='-.'))
    
    
    # CI/CD Stages (moved to avoid overlap)
    stages = [
        "Plan Configuration",
        "Source Checkout", 
        "Build Applications",
        "Run Tests",
        "Security Scans",
        "Build Containers",
        "Deploy to EKS (Direct API)",
        "Verify via ALB (Health Checks)"
    ]
    
    ax.text(1, 5.5, 'Bamboo CI/CD Pipeline Stages:', fontsize=10, fontweight='bold')
    for i, stage in enumerate(stages):
        ax.text(1, 5 - i*0.35, stage, fontsize=8, ha='left')
    
    # Deployment vs Access Paths (moved closer to pipeline stages)
    ax.text(5, 5.5, 'Container Path (Red):\nBamboo → VPN → ECR\n(Push Images)\n\nDeployment Path (Green):\nBamboo → VPN → EKS API\n(Bypasses ALB)\n\nAccess Path (Blue):\nUsers → VPN → ALB → Apps\n(Runtime access)', 
           fontsize=9, ha='left', va='top',
           bbox=dict(boxstyle="round,pad=0.5", facecolor='lightcyan', alpha=0.8))
    
    # Network Security Notes (moved closer to pipeline stages, below deployment/access paths)
    ax.text(5, 2.5, 'Security Features:\n• Corporate firewall protection\n• VPN encrypted tunnel\n• No internet exposure\n• Internal load balancer for access\n• Direct EKS API for deployment', 
           fontsize=9, ha='left', va='top',
           bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow', alpha=0.8))
    
    # Legend
    legend_elements = [
        patches.Patch(color=colors['corporate_network'], alpha=0.5, label='Corporate Network'),
        patches.Patch(color=colors['aws_cloud'], alpha=0.5, label='AWS Cloud'),
        patches.Patch(color=colors['bitbucket'], alpha=0.8, label='Bitbucket Server'),
        patches.Patch(color=colors['bamboo'], alpha=0.8, label='Bamboo CI/CD'),
        patches.Patch(color=colors['vpn'], alpha=0.8, label='VPN Connection'),
        patches.Patch(color=colors['eks'], alpha=0.6, label='EKS Applications')
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98), fontsize=9)
    
    plt.tight_layout()
    
    # Save the diagram
    output_dir = Path("docs/architecture")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as PNG and SVG
    png_path = output_dir / "cicd_flow_corporate.png"
    svg_path = output_dir / "cicd_flow_corporate.svg"
    
    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(svg_path, bbox_inches='tight', facecolor='white')
    
    print(f"✅ Generated: {png_path}")
    print(f"✅ Generated: {svg_path}")
    
    plt.close()

def main():
    """Generate the CI/CD flow diagram."""
    print("🎨 Generating Corporate CI/CD Flow Diagram")
    print("=" * 50)
    
    create_cicd_flow_diagram()
    
    print("📊 CI/CD Flow diagram generation completed!")

if __name__ == "__main__":
    main()
