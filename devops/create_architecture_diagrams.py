#!/usr/bin/env python3
"""
Fixed Architecture Diagram Generator
Generates architecture diagrams using matplotlib with corporate intranet components.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
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
    ax.text(9, 13.5, f'Corporate SDLC & Deployment Infrastructure - {environment.upper()}', 
            fontsize=18, fontweight='bold', ha='center')
    
    # Define colors
    colors = {
        'aws_cloud': '#E8F4FD',
        'vpc': '#D4EDDA', 
        'public_subnet': '#FFF3CD',
        'private_subnet': '#F8D7DA',
        'eks_cluster': '#E2E3E5',
        'rds': '#F8D7DA',
        'corporate_intranet': '#E6E6FA'
    }
    
    # Corporate Intranet boundary (outermost)
    corp_intranet_rect = patches.Rectangle((0.2, 0.2), 17.6, 13.3, linewidth=3, 
                                          edgecolor='purple', facecolor=colors['corporate_intranet'], alpha=0.2)
    ax.add_patch(corp_intranet_rect)
    ax.text(0.5, 13.2, 'Corporate Intranet', fontsize=14, fontweight='bold', color='purple')
    
    # AWS Cloud boundary (reduced height to make room for US-East-1 region at bottom)
    cloud_rect = patches.Rectangle((0.5, 2.5), 17, 9.5, linewidth=2, 
                                   edgecolor='blue', facecolor=colors['aws_cloud'], alpha=0.3)
    ax.add_patch(cloud_rect)
    ax.text(1, 11.7, 'AWS Cloud (VPC)', fontsize=12, fontweight='bold', color='blue')
    
    # Corporate intranet components (positioned at top - original pre-migration state)
    corporate_components = [
        {'name': 'On-Premise Dev Server', 'x': 2, 'y': 12.5, 'width': 1.5, 'height': 0.8, 'color': 'lightblue'},
        {'name': 'Bitbucket', 'x': 6, 'y': 12.5, 'width': 1.3, 'height': 0.8, 'color': 'lightgreen'},
        {'name': 'Bamboo', 'x': 10, 'y': 12.5, 'width': 1.3, 'height': 0.8, 'color': 'orange'}
    ]
    
    for comp in corporate_components:
        comp_rect = patches.Rectangle((comp['x'], comp['y']), comp['width'], comp['height'], 
                                     linewidth=2, edgecolor='darkgray', 
                                     facecolor=comp['color'], alpha=0.8)
        ax.add_patch(comp_rect)
        ax.text(comp['x'] + comp['width']/2, comp['y'] + comp['height']/2, 
               comp['name'], ha='center', va='center', fontsize=8, fontweight='bold')
    
    # VPC (within AWS Cloud)
    vpc_rect = patches.Rectangle((1, 3), 16, 8.5, linewidth=2, 
                                edgecolor='green', facecolor=colors['vpc'], alpha=0.3)
    ax.add_patch(vpc_rect)
    ax.text(1.2, 11.2, f'VPC ({environment}_vpc)', fontsize=11, fontweight='bold', color='green')
    
    # Management Subnets (formerly public)
    mgmt_subnet1 = patches.Rectangle((2, 9.5), 6, 1.8, linewidth=1, 
                                    edgecolor='orange', facecolor=colors['public_subnet'], alpha=0.5)
    ax.add_patch(mgmt_subnet1)
    ax.text(2.2, 10.9, 'Management Subnet 1', fontsize=9, fontweight='bold')
    
    mgmt_subnet2 = patches.Rectangle((9, 9.5), 6, 1.8, linewidth=1, 
                                    edgecolor='orange', facecolor=colors['public_subnet'], alpha=0.5)
    ax.add_patch(mgmt_subnet2)
    ax.text(9.2, 10.9, 'Management Subnet 2', fontsize=9, fontweight='bold')
    
    # Private Subnets
    priv_subnet1 = patches.Rectangle((2, 7), 6, 2.3, linewidth=1, 
                                    edgecolor='red', facecolor=colors['private_subnet'], alpha=0.3)
    ax.add_patch(priv_subnet1)
    ax.text(2.2, 9.1, 'Private Subnet 1', fontsize=9, fontweight='bold')
    
    priv_subnet2 = patches.Rectangle((9, 7), 6, 2.3, linewidth=1, 
                                    edgecolor='red', facecolor=colors['private_subnet'], alpha=0.3)
    ax.add_patch(priv_subnet2)
    ax.text(9.2, 9.1, 'Private Subnet 2', fontsize=9, fontweight='bold')
    
    # Corporate Network Gateway (VPN/Direct Connect)
    corp_gw_rect = patches.Rectangle((7.5, 11.2), 3, 0.5, linewidth=2, 
                                    edgecolor='darkblue', facecolor='lightcyan', alpha=0.7)
    ax.add_patch(corp_gw_rect)
    ax.text(9, 11.45, 'Corporate Gateway', ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Internal ALB (Application Load Balancer) - positioned in management subnets
    alb_rect = patches.Rectangle((7.5, 10.15), 3, 0.6, linewidth=2, 
                                edgecolor='darkgreen', facecolor='lightgreen', alpha=0.7)
    ax.add_patch(alb_rect)
    ax.text(9, 10.45, 'Internal ALB', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # EKS Cluster components (centered within private subnets)
    eks_components = [
        {'name': 'Risk API Service', 'x': 3, 'y': 8.1, 'width': 2, 'height': 0.7, 'color': 'lightcyan'},
        {'name': 'Web Application', 'x': 5.5, 'y': 8.1, 'width': 2, 'height': 0.7, 'color': 'lightcyan'},
        {'name': 'Dash Dashboard', 'x': 10, 'y': 8.1, 'width': 2, 'height': 0.7, 'color': 'lightcyan'},
        {'name': 'Airflow Scheduler', 'x': 12.5, 'y': 8.1, 'width': 2, 'height': 0.7, 'color': 'lightcyan'},
        {'name': 'Airflow Workers', 'x': 12.5, 'y': 7.3, 'width': 2, 'height': 0.6, 'color': 'lightcyan'}
    ]
    
    for comp in eks_components:
        comp_rect = patches.Rectangle((comp['x'], comp['y']), comp['width'], comp['height'], 
                                     linewidth=1, edgecolor='blue', 
                                     facecolor=comp['color'], alpha=0.8)
        ax.add_patch(comp_rect)
        ax.text(comp['x'] + comp['width']/2, comp['y'] + comp['height']/2, 
               comp['name'], ha='center', va='center', fontsize=8, fontweight='bold')
    
    # EKS Cluster boundary (adjusted for new positions)
    eks_rect = patches.Rectangle((2.5, 7.2), 12.5, 1.8, linewidth=2, 
                                edgecolor='blue', facecolor=colors['eks_cluster'], alpha=0.2)
    ax.add_patch(eks_rect)
    ax.text(2.7, 7.4, f'EKS Cluster ({environment})', fontsize=10, fontweight='bold', color='blue')
    
    # Internal ALB connections to EKS services (including Airflow REST API)
    alb_connections = [
        {'target': 'Risk API Service', 'target_x': 4, 'target_y': 8.1},
        {'target': 'Web Application', 'target_x': 6.5, 'target_y': 8.1},
        {'target': 'Dash Dashboard', 'target_x': 11, 'target_y': 8.1},
        {'target': 'Airflow Scheduler', 'target_x': 13.5, 'target_y': 8.1}
    ]
    
    alb_center_x = 9
    alb_center_y = 10.45
    
    for conn in alb_connections:
        # Draw arrow from ALB to each service
        ax.annotate('', xy=(conn['target_x'], conn['target_y'] + 0.7), 
                    xytext=(alb_center_x, alb_center_y),
                    arrowprops=dict(arrowstyle='->', color='darkgreen', lw=1.5, alpha=0.7))
    
    # Airflow Scheduler to Workers connection
    # Arrow from Airflow Scheduler to Airflow Workers
    ax.annotate('', xy=(13.5, 7.3 + 0.6), xytext=(13.5, 8.1),
                arrowprops=dict(arrowstyle='<->', color='blue', lw=1.5, alpha=0.8))
    
    # Database Subnets
    db_subnet1 = patches.Rectangle((2, 4.5), 6, 2.3, linewidth=1, 
                                  edgecolor='purple', facecolor='#F0E6FF', alpha=0.4)
    ax.add_patch(db_subnet1)
    ax.text(2.2, 6.5, 'Database Subnet 1', fontsize=9, fontweight='bold')
    
    db_subnet2 = patches.Rectangle((9, 4.5), 6, 2.3, linewidth=1, 
                                  edgecolor='purple', facecolor='#F0E6FF', alpha=0.4)
    ax.add_patch(db_subnet2)
    ax.text(9.2, 6.5, 'Database Subnet 2', fontsize=9, fontweight='bold')
    
    # Database components
    rds_rect = patches.Rectangle((3, 5.5), 4, 0.9, linewidth=2, 
                                edgecolor='darkred', facecolor=colors['rds'], alpha=0.8)
    ax.add_patch(rds_rect)
    ax.text(5, 5.95, f'RDS PostgreSQL ({environment}db)', ha='center', va='center', 
           fontsize=9, fontweight='bold')
    
    snowflake_rect = patches.Rectangle((10, 5.5), 4, 0.9, linewidth=2, 
                                      edgecolor='darkblue', facecolor='lightblue', alpha=0.8)
    ax.add_patch(snowflake_rect)
    ax.text(12, 5.95, f'Snowflake Data Warehouse', ha='center', va='center', 
           fontsize=9, fontweight='bold')
    
    # US-East-1 Region box (at bottom, outside VPC)
    us_east_1_rect = patches.Rectangle((0.5, 0.5), 17, 1.8, linewidth=2, 
                                      edgecolor='purple', facecolor='#F5F0FF', alpha=0.2)
    ax.add_patch(us_east_1_rect)
    ax.text(9, 2.1, 'US-East-1 Region (AWS Services)', ha='center', va='center', 
           fontsize=10, fontweight='bold', color='purple')
    
    # AWS Services in US-East-1 Region (at bottom, moved lower for better vertical alignment)
    ecr_rect = patches.Rectangle((7.75, 0.8), 1.5, 0.6, linewidth=2, 
                                edgecolor='orange', facecolor='lightyellow', alpha=0.8)
    ax.add_patch(ecr_rect)
    ax.text(8.5, 1.1, 'ECR', ha='center', va='center', fontsize=8, fontweight='bold')
    
    s3_rect = patches.Rectangle((9.75, 0.7), 1.5, 0.8, linewidth=2, 
                               edgecolor='green', facecolor='lightgreen', alpha=0.8)
    ax.add_patch(s3_rect)
    ax.text(10.5, 1.1, f'S3 Storage ({environment}-bucket)', ha='center', va='center', 
           fontsize=8, fontweight='bold')
    
    # VPC Endpoints (at VPC edge, perfectly aligned with services below)
    vpc_endpoint_ecr = patches.Rectangle((8, 2.8), 1, 0.4, linewidth=1, 
                                        edgecolor='gray', facecolor='lightgray', alpha=0.6)
    ax.add_patch(vpc_endpoint_ecr)
    ax.text(8.5, 3, 'ECR Endpoint', ha='center', va='center', fontsize=7)
    
    vpc_endpoint_s3 = patches.Rectangle((10, 2.8), 1, 0.4, linewidth=1, 
                                       edgecolor='gray', facecolor='lightgray', alpha=0.6)
    ax.add_patch(vpc_endpoint_s3)
    ax.text(10.5, 3, 'S3 Endpoint', ha='center', va='center', fontsize=7)
    
    # VPC Endpoint connections (perfectly vertical connections to bottom region)
    # ECR endpoint to ECR (perfectly vertical)
    ax.annotate('', xy=(8.5, 1.4), xytext=(8.5, 2.8),
                arrowprops=dict(arrowstyle='->', color='orange', lw=1.5, alpha=0.7, linestyle='--'))
    # S3 endpoint to S3 (perfectly vertical)
    ax.annotate('', xy=(10.5, 1.5), xytext=(10.5, 2.8),
                arrowprops=dict(arrowstyle='->', color='green', lw=1.5, alpha=0.7, linestyle='--'))
    
    # Legend (positioned in upper right corner)
    legend_elements = [
        {'color': colors['aws_cloud'], 'label': 'AWS Cloud'},
        {'color': colors['vpc'], 'label': 'VPC'},
        {'color': colors['public_subnet'], 'label': 'Management Subnet'}, 
        {'color': colors['private_subnet'], 'label': 'Private Subnet'},
        {'color': '#F0E6FF', 'label': 'Database Subnet'},
        {'color': colors['eks_cluster'], 'label': 'EKS Cluster'},
        {'color': colors['corporate_intranet'], 'label': 'Corporate Intranet'},
        {'color': 'lightblue', 'label': 'On-Premise Components'},
        {'color': 'lightgreen', 'label': 'Source Control'},
        {'color': 'orange', 'label': 'CI/CD Server'}
    ]
    
    legend_x = 15.5
    legend_y = 12.8
    
    # Legend background
    legend_bg = patches.Rectangle((legend_x - 0.2, legend_y - len(legend_elements) * 0.3 - 0.3), 
                                 3.5, len(legend_elements) * 0.3 + 0.5, 
                                 linewidth=1, edgecolor='black', facecolor='white', alpha=0.8)
    ax.add_patch(legend_bg)
    
    # Legend title
    ax.text(legend_x + 1.5, legend_y, 'Legend', fontsize=10, fontweight='bold', ha='center')
    
    # Legend items
    for i, item in enumerate(legend_elements):
        y_pos = legend_y - 0.4 - (i * 0.3)
        
        # Color box
        color_box = patches.Rectangle((legend_x, y_pos - 0.1), 0.3, 0.2, 
                                     facecolor=item['color'], edgecolor='black', alpha=0.8)
        ax.add_patch(color_box)
        
        # Label
        ax.text(legend_x + 0.4, y_pos, item['label'], fontsize=8, va='center')
    
    # Remove axes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    plt.tight_layout()
    return fig

def main():
    """Generate all architecture diagrams."""
    print("🎨 Generating Fixed Architecture Diagrams")
    print("=" * 50)
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "docs" / "architecture"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    environments = ["dev", "uat", "prod"]
    
    for env in environments:
        print(f"📊 Creating diagram for {env.upper()} environment...")
        
        # Create diagram
        fig = create_architecture_diagram(env)
        
        # Save as PNG and SVG
        png_path = output_dir / f"architecture_{env}.png"
        svg_path = output_dir / f"architecture_{env}.svg"
        
        fig.savefig(png_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        fig.savefig(svg_path, format='svg', bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        
        plt.close(fig)
        
        print(f"✅ Saved: {png_path}")
        print(f"✅ Saved: {svg_path}")
    
    print("\n🎉 All architecture diagrams generated successfully!")
    print(f"📁 Output location: {output_dir.absolute()}")

if __name__ == "__main__":
    main()
