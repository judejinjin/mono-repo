#!/usr/bin/env python3
"""
Fixed Architecture Diagram Generator
Generates architecture diagrams using matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

def create_architecture_diagram(environment="dev"):
    """Create architecture diagram for the specified environment."""
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(18, 14))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 14)
    ax.set_aspect('equal')
    
    # Title
    ax.text(9, 13.5, f'AWS Infrastructure Architecture - {environment.upper()}', 
            fontsize=18, fontweight='bold', ha='center')
    
    # Define colors
    colors = {
        'aws_cloud': '#E8F4FD',
        'vpc': '#D4EDDA', 
        'public_subnet': '#FFF3CD',
        'private_subnet': '#F8D7DA',
        'eks_cluster': '#E2E3E5',
        'component': '#FFFFFF',
        'storage': '#FFE6CC',
        'ingress': '#D1ECF1',
        'api_gateway': '#D4EDDA',
        'load_balancer': '#E2E3E5'
    }
    
    # AWS Cloud boundary
    cloud_rect = patches.Rectangle((0.5, 0.5), 17, 12.5, linewidth=2, 
                                   edgecolor='blue', facecolor=colors['aws_cloud'], alpha=0.3)
    ax.add_patch(cloud_rect)
    ax.text(1, 12.7, 'AWS Cloud', fontsize=12, fontweight='bold', color='blue')
    
    # VPC
    vpc_rect = patches.Rectangle((1, 1), 16, 11, linewidth=2, 
                                edgecolor='green', facecolor=colors['vpc'], alpha=0.3)
    ax.add_patch(vpc_rect)
    ax.text(1.2, 11.7, f'VPC ({environment}_vpc)', fontsize=11, fontweight='bold', color='green')
    
    # Public Subnets
    pub_subnet1 = patches.Rectangle((2, 9), 6, 2.5, linewidth=1, 
                                   edgecolor='orange', facecolor=colors['public_subnet'], alpha=0.5)
    ax.add_patch(pub_subnet1)
    ax.text(2.2, 11.2, 'Public Subnet 1', fontsize=9, fontweight='bold')
    
    pub_subnet2 = patches.Rectangle((9, 9), 6, 2.5, linewidth=1, 
                                   edgecolor='orange', facecolor=colors['public_subnet'], alpha=0.5)
    ax.add_patch(pub_subnet2)
    ax.text(9.2, 11.2, 'Public Subnet 2', fontsize=9, fontweight='bold')
    
    # Private Subnets
    priv_subnet1 = patches.Rectangle((2, 5.5), 6, 3, linewidth=1, 
                                    edgecolor='red', facecolor=colors['private_subnet'], alpha=0.3)
    ax.add_patch(priv_subnet1)
    ax.text(2.2, 8.2, 'Private Subnet 1', fontsize=9, fontweight='bold')
    
    priv_subnet2 = patches.Rectangle((9, 5.5), 6, 3, linewidth=1, 
                                    edgecolor='red', facecolor=colors['private_subnet'], alpha=0.3)
    ax.add_patch(priv_subnet2)
    ax.text(9.2, 8.2, 'Private Subnet 2', fontsize=9, fontweight='bold')
    
    # Internet Gateway
    igw_rect = patches.Rectangle((8, 12), 2, 0.7, linewidth=1, 
                                edgecolor='blue', facecolor=colors['load_balancer'], alpha=0.8)
    ax.add_patch(igw_rect)
    ax.text(9, 12.35, 'Internet Gateway', fontsize=8, ha='center', va='center', fontweight='bold')
    
    # Application Load Balancer (for web traffic)
    alb_rect = patches.Rectangle((3, 9.5), 2.5, 0.8, linewidth=1, 
                                edgecolor='orange', facecolor=colors['load_balancer'], alpha=0.8)
    ax.add_patch(alb_rect)
    ax.text(4.25, 9.9, 'Application LB\n(Web Traffic)', fontsize=7, ha='center', va='center', fontweight='bold')
    
    # API Gateway (for external API access)
    api_gw_rect = patches.Rectangle((10.5, 9.5), 2.5, 0.8, linewidth=2, 
                                   edgecolor='darkgreen', facecolor=colors['api_gateway'], alpha=0.8)
    ax.add_patch(api_gw_rect)
    ax.text(11.75, 9.9, 'API Gateway\n(Airflow API)', fontsize=7, ha='center', va='center', fontweight='bold')
    
    # Network Load Balancer (for API Gateway)
    nlb_rect = patches.Rectangle((11, 8.5), 1.5, 0.6, linewidth=1, 
                                edgecolor='blue', facecolor=colors['load_balancer'], alpha=0.8)
    ax.add_patch(nlb_rect)
    ax.text(11.75, 8.8, 'Network LB', fontsize=7, ha='center', va='center', fontweight='bold')
    
    # EKS Cluster (spanning both private subnets)
    eks_rect = patches.Rectangle((2.5, 6), 12, 2, linewidth=2, 
                                edgecolor='purple', facecolor=colors['eks_cluster'], alpha=0.4)
    ax.add_patch(eks_rect)
    ax.text(8.5, 7.7, 'EKS Cluster', fontsize=11, ha='center', va='center', fontweight='bold', color='purple')
    
    # Ingress Controller (central routing)
    ingress_rect = patches.Rectangle((6, 6.8), 4, 0.6, linewidth=2, 
                                    edgecolor='darkblue', facecolor=colors['ingress'], alpha=0.9)
    ax.add_patch(ingress_rect)
    ax.text(8, 7.1, 'Ingress Controller (NGINX)', fontsize=8, ha='center', va='center', fontweight='bold')
    
    # Application components (as pods in EKS)
    components = [
        {'name': 'FastAPI', 'pos': (3, 6.2), 'size': (1.8, 0.5)},
        {'name': 'Web Apps', 'pos': (5.2, 6.2), 'size': (1.8, 0.5)},
        {'name': 'Dash', 'pos': (10.5, 6.2), 'size': (1.8, 0.5)},
        {'name': 'Airflow', 'pos': (12.7, 6.2), 'size': (1.8, 0.5)},
        {'name': 'Bamboo', 'pos': (7.4, 6.2), 'size': (1.8, 0.5)}
    ]
    
    # Add dev server only for dev environment
    if environment.lower() == 'dev':
        components.append({'name': 'Dev Server', 'pos': (13.5, 7), 'size': (1.3, 0.8)})
    
    for comp in components:
        comp_rect = patches.Rectangle(comp['pos'], comp['size'][0], comp['size'][1], 
                                     linewidth=1, edgecolor='black', 
                                     facecolor=colors['component'], alpha=0.9)
        ax.add_patch(comp_rect)
        ax.text(comp['pos'][0] + comp['size'][0]/2, comp['pos'][1] + comp['size'][1]/2, 
               comp['name'], ha='center', va='center', fontsize=7, fontweight='bold')
    
    # External storage (below VPC)
    storage_services = [
        {'name': 'RDS\nPostgreSQL', 'pos': (2, 3.5), 'size': (2.5, 1.2)},
        {'name': 'S3\nBucket', 'pos': (5.5, 3.5), 'size': (2.5, 1.2)},
        {'name': 'ElastiCache\nRedis', 'pos': (9, 3.5), 'size': (2.5, 1.2)},
        {'name': 'Snowflake\nData Warehouse', 'pos': (12.5, 3.5), 'size': (2.5, 1.2)}
    ]
    
    for storage in storage_services:
        storage_rect = patches.Rectangle(storage['pos'], storage['size'][0], storage['size'][1], 
                                        linewidth=1, edgecolor='darkorange', 
                                        facecolor=colors['storage'], alpha=0.7)
        ax.add_patch(storage_rect)
        ax.text(storage['pos'][0] + storage['size'][0]/2, storage['pos'][1] + storage['size'][1]/2, 
               storage['name'], ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Add connection arrows
    # Internet to IGW
    ax.annotate('', xy=(9, 12), xytext=(9, 11.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
    
    # ALB to Ingress Controller
    ax.annotate('', xy=(6, 7.1), xytext=(5.5, 9.5),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='orange'))
    
    # Ingress to FastAPI
    ax.annotate('', xy=(3.9, 6.7), xytext=(6.5, 7),
                arrowprops=dict(arrowstyle='->', lw=1, color='darkblue'))
    
    # Ingress to Web Apps
    ax.annotate('', xy=(6.1, 6.7), xytext=(7.5, 7),
                arrowprops=dict(arrowstyle='->', lw=1, color='darkblue'))
    
    # Ingress to Dash
    ax.annotate('', xy=(10.5, 6.7), xytext=(8.5, 7),
                arrowprops=dict(arrowstyle='->', lw=1, color='darkblue'))
    
    # API Gateway to NLB (via VPC Link)
    ax.annotate('VPC Link', xy=(11.75, 8.5), xytext=(11.75, 9.5),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='green', linestyle='--'),
                fontsize=7, ha='center', color='green', fontweight='bold')
    
    # NLB to Airflow (direct)
    ax.annotate('', xy=(13.6, 6.7), xytext=(11.75, 8.5),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))
    
    # Add traffic flow labels
    ax.text(4.25, 8.5, 'Web Traffic\n/api, /web, /dash', fontsize=7, ha='center', 
           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    ax.text(11.75, 7.5, 'API Traffic\n(External DAG\nTriggers)', fontsize=7, ha='center', 
           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    # Add legend
    legend_elements = [
        patches.Patch(color=colors['aws_cloud'], alpha=0.3, label='AWS Cloud'),
        patches.Patch(color=colors['vpc'], alpha=0.3, label='VPC'),
        patches.Patch(color=colors['public_subnet'], alpha=0.5, label='Public Subnet'),
        patches.Patch(color=colors['private_subnet'], alpha=0.3, label='Private Subnet'),
        patches.Patch(color=colors['eks_cluster'], alpha=0.4, label='EKS Cluster'),
        patches.Patch(color=colors['ingress'], alpha=0.9, label='Ingress Controller'),
        patches.Patch(color=colors['api_gateway'], alpha=0.8, label='API Gateway'),
        patches.Patch(color=colors['storage'], alpha=0.7, label='External Storage')
    ]
    
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.98), fontsize=8)
    
    # Environment info
    info_text = f"""
Environment: {environment.upper()}
Region: us-east-1
AZs: 2
VPC CIDR: 10.{['0', '1', '2'][['dev', 'uat', 'prod'].index(environment)]}.0.0/16
    """
    ax.text(16.5, 3, info_text, fontsize=8, va='top', ha='right',
           bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.9))
    
    # Remove axes
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Save the diagram
    output_dir = Path("docs/architecture")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    png_file = output_dir / f"architecture_{environment}.png"
    svg_file = output_dir / f"architecture_{environment}.svg"
    
    plt.savefig(png_file, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.savefig(svg_file, format='svg', bbox_inches='tight', facecolor='white', edgecolor='none')
    
    print(f"✅ Generated: {png_file}")
    print(f"✅ Generated: {svg_file}")
    
    plt.close()

def main():
    """Generate architecture diagrams for all environments."""
    environments = ['dev', 'uat', 'prod']
    
    print("🎨 Generating Fixed Architecture Diagrams")
    print("=" * 50)
    
    for env in environments:
        print(f"\n📊 Creating diagram for {env.upper()} environment...")
        try:
            create_architecture_diagram(env)
        except Exception as e:
            print(f"❌ Error creating {env} diagram: {e}")
    
    print(f"\n🎉 Diagram generation completed!")
    print(f"📁 Output directory: docs/architecture/")

if __name__ == "__main__":
    main()
