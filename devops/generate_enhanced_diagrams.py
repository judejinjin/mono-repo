#!/usr/bin/env python3
"""
Enhanced Architecture Diagram Generator with JupyterHub Integration
Updates existing diagrams to include JupyterHub components and creates new JupyterHub-specific diagrams
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
import subprocess
import sys
import os

def create_enhanced_architecture_diagram_with_jupyterhub(environment="dev"):
    """Create enhanced architecture diagram including JupyterHub components"""
    
    # Create figure and axis with simpler layout
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.set_aspect('equal')
    
    # Title
    ax.text(8, 11.5, f'Risk Platform with JupyterHub Integration - {environment.upper()}', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Define colors
    colors = {
        'aws_cloud': '#E8F4FD',
        'eks_cluster': '#E2E3E5',
        'jupyterhub': '#E8E2F4',
        'storage': '#F0F8E8',
        'users': '#E6F3FF',
        'security': '#FFF2E6'
    }
    
    # AWS Cloud boundary
    aws_rect = patches.Rectangle((0.5, 2), 15, 8.5, linewidth=2, 
                                edgecolor='blue', facecolor=colors['aws_cloud'], alpha=0.3)
    ax.add_patch(aws_rect)
    ax.text(0.7, 10.2, 'AWS Cloud', fontsize=12, fontweight='bold', color='blue')
    
    # Users section (above AWS cloud)
    users_rect = patches.Rectangle((1, 10.5), 3.5, 1, linewidth=2, 
                                  edgecolor='darkblue', facecolor=colors['users'], alpha=0.7)
    ax.add_patch(users_rect)
    ax.text(2.75, 11, 'Business Users\nData Scientists', fontsize=9, fontweight='bold', ha='center')
    
    # Authentication section
    auth_rect = patches.Rectangle((5.5, 10.5), 3, 1, linewidth=2,
                                 edgecolor='orange', facecolor=colors['security'], alpha=0.7)
    ax.add_patch(auth_rect)
    ax.text(7, 11, 'Corporate SSO\nIAM/RBAC', fontsize=9, fontweight='bold', ha='center')
    
    # Load Balancer
    alb_rect = patches.Rectangle((10, 10.5), 2.5, 1, linewidth=2, 
                                edgecolor='darkgreen', facecolor='lightgreen', alpha=0.7)
    ax.add_patch(alb_rect)
    ax.text(11.25, 11, 'Internal ALB', ha='center', va='center', fontsize=9, fontweight='bold')
    
    # EKS Cluster - Main Services
    eks_main_rect = patches.Rectangle((1, 7), 6, 2.5, linewidth=2, 
                                     edgecolor='darkgreen', facecolor=colors['eks_cluster'], alpha=0.5)
    ax.add_patch(eks_main_rect)
    ax.text(1.2, 9.2, 'EKS Cluster - Core Services', fontsize=10, fontweight='bold', color='darkgreen')
    
    # Core services (simplified)
    services = [
        {'name': 'Risk API', 'pos': (1.5, 8), 'size': (1.2, 0.8), 'color': 'lightgreen'},
        {'name': 'Web App', 'pos': (3, 8), 'size': (1.2, 0.8), 'color': 'lightblue'},
        {'name': 'Analytics', 'pos': (4.5, 8), 'size': (1.2, 0.8), 'color': 'lightcoral'},
        {'name': 'Airflow', 'pos': (1.5, 7.2), 'size': (1.2, 0.6), 'color': 'lightyellow'},
        {'name': 'Monitoring', 'pos': (3, 7.2), 'size': (1.2, 0.6), 'color': 'lightcyan'},
        {'name': 'API Gateway', 'pos': (4.5, 7.2), 'size': (1.2, 0.6), 'color': 'lightpink'}
    ]
    
    for svc in services:
        svc_rect = patches.Rectangle(svc['pos'], svc['size'][0], svc['size'][1], 
                                   linewidth=1, edgecolor='black', facecolor=svc['color'], alpha=0.8)
        ax.add_patch(svc_rect)
        ax.text(svc['pos'][0] + svc['size'][0]/2, svc['pos'][1] + svc['size'][1]/2, 
               svc['name'], ha='center', va='center', fontsize=8, fontweight='bold')
    
    # JupyterHub Cluster
    jupyter_rect = patches.Rectangle((8.5, 7), 6, 2.5, linewidth=2, 
                                    edgecolor='mediumpurple', facecolor=colors['jupyterhub'], alpha=0.5)
    ax.add_patch(jupyter_rect)
    ax.text(8.7, 9.2, 'JupyterHub Platform', fontsize=10, fontweight='bold', color='mediumpurple')
    
    # JupyterHub services (simplified)
    jupyter_services = [
        {'name': 'JHub Hub', 'pos': (9, 8), 'size': (1.2, 0.8), 'color': 'plum'},
        {'name': 'Mgmt API', 'pos': (10.5, 8), 'size': (1.2, 0.8), 'color': 'lavender'},
        {'name': 'Notebooks', 'pos': (12, 8), 'size': (1.2, 0.8), 'color': 'thistle'},
        {'name': 'Business', 'pos': (9, 7.2), 'size': (1.2, 0.6), 'color': 'lightpink'},
        {'name': 'Data Sci', 'pos': (10.5, 7.2), 'size': (1.2, 0.6), 'color': 'lightblue'},
        {'name': 'Shared', 'pos': (12, 7.2), 'size': (1.2, 0.6), 'color': 'lightgreen'}
    ]
    
    for jsvc in jupyter_services:
        jsvc_rect = patches.Rectangle(jsvc['pos'], jsvc['size'][0], jsvc['size'][1], 
                                     linewidth=1, edgecolor='black', facecolor=jsvc['color'], alpha=0.8)
        ax.add_patch(jsvc_rect)
        ax.text(jsvc['pos'][0] + jsvc['size'][0]/2, jsvc['pos'][1] + jsvc['size'][1]/2, 
               jsvc['name'], ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Storage Layer
    storage_rect = patches.Rectangle((1, 4.5), 13, 1.8, linewidth=2,
                                   edgecolor='darkgreen', facecolor=colors['storage'], alpha=0.5)
    ax.add_patch(storage_rect)
    ax.text(1.2, 6.1, 'Storage & Data Layer', fontsize=10, fontweight='bold', color='darkgreen')
    
    # Storage services (simplified)
    storage_services = [
        {'name': 'EFS\nShared', 'pos': (1.5, 4.8), 'size': (1.5, 1.2), 'color': 'lightgreen'},
        {'name': 'S3\nBackup', 'pos': (3.5, 4.8), 'size': (1.5, 1.2), 'color': 'lightblue'},
        {'name': 'ECR\nImages', 'pos': (5.5, 4.8), 'size': (1.5, 1.2), 'color': 'lightcoral'},
        {'name': 'RDS\nPostgreSQL', 'pos': (7.5, 4.8), 'size': (1.5, 1.2), 'color': 'lightyellow'},
        {'name': 'Redis\nCache', 'pos': (9.5, 4.8), 'size': (1.5, 1.2), 'color': 'lightcyan'},
        {'name': 'Secrets\nManager', 'pos': (11.5, 4.8), 'size': (1.5, 1.2), 'color': 'lightgray'}
    ]
    
    for storage in storage_services:
        storage_rect_svc = patches.Rectangle(storage['pos'], storage['size'][0], storage['size'][1], 
                                           linewidth=1, edgecolor='black', facecolor=storage['color'], alpha=0.8)
        ax.add_patch(storage_rect_svc)
        ax.text(storage['pos'][0] + storage['size'][0]/2, storage['pos'][1] + storage['size'][1]/2, 
               storage['name'], ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Data Sources
    data_rect = patches.Rectangle((1, 2.5), 13, 1.5, linewidth=2,
                                 edgecolor='darkblue', facecolor='lightblue', alpha=0.3)
    ax.add_patch(data_rect)
    ax.text(1.2, 3.8, 'Data Sources', fontsize=10, fontweight='bold', color='darkblue')
    
    # Data sources (simplified)
    data_sources = [
        {'name': 'Market\nData', 'pos': (2, 2.8), 'size': (1.8, 1), 'color': 'lightsteelblue'},
        {'name': 'Portfolio\nData', 'pos': (4.5, 2.8), 'size': (1.8, 1), 'color': 'lightcyan'},
        {'name': 'Risk\nModels', 'pos': (7, 2.8), 'size': (1.8, 1), 'color': 'lightblue'},
        {'name': 'External\nAPIs', 'pos': (9.5, 2.8), 'size': (1.8, 1), 'color': 'lightyellow'},
        {'name': 'Historical\nData', 'pos': (12, 2.8), 'size': (1.8, 1), 'color': 'lightgray'}
    ]
    
    for source in data_sources:
        source_rect = patches.Rectangle(source['pos'], source['size'][0], source['size'][1], 
                                      linewidth=1, edgecolor='black', facecolor=source['color'], alpha=0.8)
        ax.add_patch(source_rect)
        ax.text(source['pos'][0] + source['size'][0]/2, source['pos'][1] + source['size'][1]/2, 
               source['name'], ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Connection arrows (simplified)
    # Users to Auth
    ax.annotate('', xy=(5.5, 11), xytext=(4.5, 11),
                arrowprops=dict(arrowstyle='->', color='blue', lw=1.5))
    
    # Auth to ALB
    ax.annotate('', xy=(10, 11), xytext=(8.5, 11),
                arrowprops=dict(arrowstyle='->', color='blue', lw=1.5))
    
    # ALB to services (simplified - one arrow to each cluster)
    ax.annotate('', xy=(4, 9.5), xytext=(11, 10.5),
                arrowprops=dict(arrowstyle='->', color='green', lw=1.5))
    ax.annotate('', xy=(11.5, 9.5), xytext=(11.5, 10.5),
                arrowprops=dict(arrowstyle='->', color='purple', lw=1.5))
    
    # Services to Storage (simplified)
    ax.annotate('', xy=(7.5, 6.3), xytext=(4, 7),
                arrowprops=dict(arrowstyle='<->', color='darkgreen', lw=1))
    ax.annotate('', xy=(7.5, 6.3), xytext=(11.5, 7),
                arrowprops=dict(arrowstyle='<->', color='mediumpurple', lw=1))
    
    # Storage to Data Sources
    ax.annotate('', xy=(7.5, 4), xytext=(7.5, 4.5),
                arrowprops=dict(arrowstyle='<->', color='darkblue', lw=1))
    
    # Remove axis
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Save the diagram
    output_dir = Path("../docs/diagrams")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plt.tight_layout(pad=0.5)
    plt.savefig(output_dir / f'enhanced_architecture_with_jupyterhub_{environment}.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def generate_all_enhanced_diagrams():
    """Generate enhanced diagrams for all environments"""
    environments = ['dev', 'uat', 'prod']
    
    print("Generating enhanced architecture diagrams with JupyterHub...")
    
    for env in environments:
        try:
            create_enhanced_architecture_diagram_with_jupyterhub(env)
            print(f"✓ Generated enhanced architecture diagram for {env}")
        except Exception as e:
            print(f"✗ Failed to generate diagram for {env}: {e}")
    
    # Generate JupyterHub-specific diagrams
    try:
        jupyterhub_script = Path(__file__).parent / 'jupyterhub' / 'generate_jupyterhub_diagrams.py'
        if jupyterhub_script.exists():
            result = subprocess.run([sys.executable, str(jupyterhub_script)], 
                                  capture_output=True, text=True, cwd=str(jupyterhub_script.parent))
            if result.returncode == 0:
                print("✓ Generated JupyterHub-specific diagrams")
                
                # Move diagrams to main docs directory
                import shutil
                source_dir = jupyterhub_script.parent / 'jupyterhub_diagrams'
                target_dir = Path("../docs/diagrams/jupyterhub")
                
                if source_dir.exists():
                    if target_dir.exists():
                        shutil.rmtree(target_dir)
                    shutil.move(str(source_dir), str(target_dir))
                    print(f"✓ Moved JupyterHub diagrams to {target_dir}")
            else:
                print(f"⚠ Failed to generate JupyterHub diagrams: {result.stderr}")
        else:
            print("⚠ JupyterHub diagram script not found")
    except Exception as e:
        print(f"⚠ Error generating JupyterHub diagrams: {e}")

def main():
    """Main function"""
    print("Enhanced Architecture Diagram Generator with JupyterHub Integration")
    print("=" * 70)
    
    generate_all_enhanced_diagrams()
    
    print("\nAll enhanced diagrams generated successfully!")
    print("Output directory: ../docs/diagrams/")

if __name__ == "__main__":
    main()