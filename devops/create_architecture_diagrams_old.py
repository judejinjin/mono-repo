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
    ax.text(9, 13.5, f'Corporate Intranet Architecture - {environment.upper()}', 
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
    
    # Corporate Intranet boundary (outer boundary)
    intranet_rect = patches.Rectangle((0.2, 0.2), 17.6, 13.3, linewidth=3, 
                                     edgecolor='purple', facecolor='lavender', alpha=0.2)
    ax.add_patch(intranet_rect)
    ax.text(0.5, 13.2, 'Corporate Intranet', fontsize=12, fontweight='bold', color='purple')
    
    # AWS Cloud boundary 
    cloud_rect = patches.Rectangle((0.5, 0.5), 17, 11.5, linewidth=2, 
                                   edgecolor='blue', facecolor=colors['aws_cloud'], alpha=0.3)
    ax.add_patch(cloud_rect)
    ax.text(1, 11.7, 'AWS Cloud (VPC)', fontsize=12, fontweight='bold', color='blue')
    
    # Corporate Intranet Components (outside AWS VPC but inside Corporate Intranet)
    corporate_components = [
            # Corporate intranet components (positioned at top)
    corporate_components = [
        {'name': 'On-Premise
Dev Server', 'x': 2, 'y': 12.5, 'width': 1.5, 'height': 0.8, 'color': 'lightblue'},
        {'name': 'Bitbucket', 'x': 6, 'y': 12.5, 'width': 1.3, 'height': 0.8, 'color': 'lightgreen'},
        {'name': 'Bamboo', 'x': 10, 'y': 12.5, 'width': 1.3, 'height': 0.8, 'color': 'orange'}
    ],
        {'name': 'Bitbucket Server\n(Source Control)', 'pos': (4.5, 12.2), 'size': (2.5, 0.8), 'color': 'lightgreen'},
        {'name': 'Bamboo Server\n(CI/CD)', 'pos': (14.5, 12.2), 'size': (2.5, 0.8), 'color': 'lightyellow'}
    ]
    
    for corp_comp in corporate_components:
        corp_rect = patches.Rectangle(corp_comp['pos'], corp_comp['size'][0], corp_comp['size'][1], 
                                     linewidth=2, edgecolor='darkgray', 
                                     facecolor=corp_comp['color'], alpha=0.8)
        ax.add_patch(corp_rect)
        ax.text(corp_comp['pos'][0] + corp_comp['size'][0]/2, corp_comp['pos'][1] + corp_comp['size'][1]/2, 
               corp_comp['name'], ha='center', va='center', fontsize=8, fontweight='bold')
    
    # VPC (within AWS Cloud)
    vpc_rect = patches.Rectangle((1, 1), 16, 10.5, linewidth=2, 
                                edgecolor='green', facecolor=colors['vpc'], alpha=0.3)
    ax.add_patch(vpc_rect)
    ax.text(1.2, 11.2, f'VPC ({environment}_vpc)', fontsize=11, fontweight='bold', color='green')
    
    # Management Subnets (formerly public)
    mgmt_subnet1 = patches.Rectangle((2, 8.5), 6, 2, linewidth=1, 
                                    edgecolor='orange', facecolor=colors['public_subnet'], alpha=0.5)
    ax.add_patch(mgmt_subnet1)
    ax.text(2.2, 10.2, 'Management Subnet 1', fontsize=9, fontweight='bold')
    
    mgmt_subnet2 = patches.Rectangle((9, 8.5), 6, 2, linewidth=1, 
                                    edgecolor='orange', facecolor=colors['public_subnet'], alpha=0.5)
    ax.add_patch(mgmt_subnet2)
    ax.text(9.2, 10.2, 'Management Subnet 2', fontsize=9, fontweight='bold')
    
    # Private Subnets
    priv_subnet1 = patches.Rectangle((2, 5.5), 6, 2.8, linewidth=1, 
                                    edgecolor='red', facecolor=colors['private_subnet'], alpha=0.3)
    ax.add_patch(priv_subnet1)
    ax.text(2.2, 7.8, 'Private Subnet 1', fontsize=9, fontweight='bold')
    
    priv_subnet2 = patches.Rectangle((9, 5.5), 6, 2.8, linewidth=1, 
                                    edgecolor='red', facecolor=colors['private_subnet'], alpha=0.3)
    ax.add_patch(priv_subnet2)
    ax.text(9.2, 7.8, 'Private Subnet 2', fontsize=9, fontweight='bold')
    
    # Corporate Network Gateway (VPN/Direct Connect)
    corp_gw_rect = patches.Rectangle((7.5, 11.2), 3, 0.5, linewidth=2, 
                                    edgecolor='purple', facecolor='mediumpurple', alpha=0.8)
    ax.add_patch(corp_gw_rect)
    ax.text(9, 11.45, 'Corporate Gateway\n(VPN/Direct Connect)', fontsize=7, ha='center', va='center', fontweight='bold')
    
    # Internal Application Load Balancer (deployed in Management Subnets)
    alb_rect = patches.Rectangle((4.5, 9.2), 5, 0.6, linewidth=2, 
                                edgecolor='darkblue', facecolor=colors['load_balancer'], alpha=0.8)
    ax.add_patch(alb_rect)
    ax.text(7, 9.5, 'Internal Application LB\n(Management Subnets)', fontsize=8, ha='center', va='center', fontweight='bold')
    
    # Remove API Gateway - not needed for intranet
    # Network Load Balancer also removed - single ALB handles all traffic
    
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
        {'name': 'Dash', 'pos': (7.5, 6.2), 'size': (1.8, 0.5)},
        {'name': 'Airflow', 'pos': (9.8, 6.2), 'size': (1.8, 0.5)},
        {'name': 'ECR', 'pos': (12.1, 6.2), 'size': (1.8, 0.5)}
        # Dev Server, Bamboo, and Bitbucket moved to Corporate Intranet
    ]
    
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
    # Corporate Network to Gateway
    ax.annotate('', xy=(9, 12), xytext=(9, 11.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='purple'))
    
    # Corporate Gateway to Internal ALB (Management Subnets)
    ax.annotate('', xy=(7, 10.8), xytext=(9, 12),
                arrowprops=dict(arrowstyle='->', lw=2, color='purple'))
    
    # Internal ALB (Management Subnets) to Ingress Controller (Private Subnets)
    ax.annotate('', xy=(6, 7.1), xytext=(7, 10),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='darkblue'))
    
    # Ingress to FastAPI
    ax.annotate('', xy=(3.9, 6.7), xytext=(6.5, 7),
                arrowprops=dict(arrowstyle='->', lw=1, color='darkblue'))
    
    # Ingress to Web Apps
    ax.annotate('', xy=(6.1, 6.7), xytext=(7.5, 7),
                arrowprops=dict(arrowstyle='->', lw=1, color='darkblue'))
    
    # Ingress to Dash
    ax.annotate('', xy=(10.5, 6.7), xytext=(8.5, 7),
                arrowprops=dict(arrowstyle='->', lw=1, color='darkblue'))
    
    # Internal ALB to Airflow (direct path-based routing from Management Subnets)
    ax.annotate('', xy=(13.6, 6.7), xytext=(8, 10),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='darkblue', linestyle='--'))
    
    # Add traffic flow labels
    ax.text(6, 8.5, 'Corporate Intranet Traffic\n/api, /web, /dash, /airflow', fontsize=7, ha='center', 
           bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.8))
    
    ax.text(10.5, 8, 'Airflow API\n(Internal DAG\nTriggers)', fontsize=7, ha='center', 
           bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcyan', alpha=0.8))
    
    # Add legend
    legend_elements = [
        patches.Patch(color='lavender', alpha=0.2, label='Corporate Intranet'),
        patches.Patch(color=colors['aws_cloud'], alpha=0.3, label='AWS Cloud'),
        patches.Patch(color=colors['vpc'], alpha=0.3, label='VPC'),
        patches.Patch(color=colors['public_subnet'], alpha=0.5, label='Management Subnet'),
        patches.Patch(color=colors['private_subnet'], alpha=0.3, label='Private Subnet'),
        patches.Patch(color=colors['eks_cluster'], alpha=0.4, label='EKS Cluster'),
        patches.Patch(color='lightblue', alpha=0.8, label='On-Premise Components'),
        patches.Patch(color=colors['storage'], alpha=0.7, label='External Storage')
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98), fontsize=8)
    
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
    output_dir = Path("../docs/architecture")
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
    print(f"📁 Output directory: ../docs/architecture/")

if __name__ == "__main__":
    main()
