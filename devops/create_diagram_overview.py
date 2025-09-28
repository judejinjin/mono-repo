#!/usr/bin/env python3
"""
Generate a visual summary of all generated diagrams
Creates a simple overview showing what diagrams are available
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

def create_diagram_overview():
    """Create a visual overview of all generated diagrams"""
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    
    # Title
    ax.text(7, 9.5, 'Risk Platform with JupyterHub Integration - Diagram Overview', 
            fontsize=16, fontweight='bold', ha='center')
    ax.text(7, 9, 'Generated: September 28, 2025', 
            fontsize=12, ha='center', style='italic')
    
    # Define sections
    sections = [
        {
            'title': '🔬 JupyterHub Integration Diagrams',
            'diagrams': [
                'jupyterhub_architecture.png - Complete integration architecture',
                'jupyterhub_data_flow.png - Data flow through notebooks',
                'jupyterhub_security.png - Security boundaries & RBAC',
                'jupyterhub_deployment.png - Multi-environment deployment'
            ],
            'pos': (0.5, 6.5),
            'size': (6, 2),
            'color': '#E8E2F4'
        },
        {
            'title': '🏗️ Enhanced Platform Diagrams',
            'diagrams': [
                'enhanced_architecture_dev.png - Development environment',
                'enhanced_architecture_uat.png - UAT environment', 
                'enhanced_architecture_prod.png - Production environment'
            ],
            'pos': (7.5, 6.5),
            'size': (6, 2),
            'color': '#E8F4FD'
        },
        {
            'title': '📊 Core Platform Diagrams',
            'diagrams': [
                'architecture_dev/uat/prod.png - Base architecture',
                'cicd_flow_corporate.png - CI/CD pipeline',
                'risk_api_*.png - Risk API service diagrams',
                'dash_*.png - Analytics dashboard diagrams'
            ],
            'pos': (0.5, 4),
            'size': (6, 2),
            'color': '#F0F8E8'
        },
        {
            'title': '🛡️ Security & Operations',
            'diagrams': [
                'security_policy_*.png - Security policies',
                'alerting_notification_*.png - Monitoring setup',
                'cloudwatch_logging_*.png - Logging architecture',
                'budget_alerts_*.png - Cost monitoring'
            ],
            'pos': (7.5, 4),
            'size': (6, 2),
            'color': '#FFF2E6'
        }
    ]
    
    for section in sections:
        # Draw section box
        rect = patches.Rectangle(section['pos'], section['size'][0], section['size'][1], 
                               linewidth=2, edgecolor='darkblue', 
                               facecolor=section['color'], alpha=0.7)
        ax.add_patch(rect)
        
        # Add title
        ax.text(section['pos'][0] + section['size'][0]/2, 
               section['pos'][1] + section['size'][1] - 0.3, 
               section['title'], fontsize=11, fontweight='bold', ha='center')
        
        # Add diagram list
        for i, diagram in enumerate(section['diagrams']):
            ax.text(section['pos'][0] + 0.2, 
                   section['pos'][1] + section['size'][1] - 0.8 - (i * 0.3), 
                   f"• {diagram}", fontsize=9, va='top')
    
    # Key features section
    features_rect = patches.Rectangle((1, 1.5), 12, 2, linewidth=2,
                                    edgecolor='darkgreen', facecolor='lightgreen', alpha=0.3)
    ax.add_patch(features_rect)
    
    ax.text(7, 3.2, '🎯 Key Integration Points Visualized', 
            fontsize=12, fontweight='bold', ha='center')
    
    features = [
        '🔐 Corporate SSO → IAM Roles → JupyterHub → Risk Platform APIs',
        '📊 Market Data → Risk Engine → Notebooks → Analytics → Reports', 
        '🛡️ Multi-layer Security: Network Policies, RBAC, Encryption',
        '🚀 Multi-Environment: Dev/UAT/Prod with proper isolation',
        '⚙️ Operations: Monitoring, Backup, Cleanup, Maintenance'
    ]
    
    for i, feature in enumerate(features):
        ax.text(1.5, 2.8 - (i * 0.25), feature, fontsize=9)
    
    # Usage instructions
    usage_rect = patches.Rectangle((1, 0.2), 12, 1, linewidth=2,
                                 edgecolor='darkorange', facecolor='lightyellow', alpha=0.3)
    ax.add_patch(usage_rect)
    
    ax.text(7, 1, '📋 Quick Start Guide', 
            fontsize=12, fontweight='bold', ha='center')
    
    ax.text(1.5, 0.7, '👥 Business Users: Start with jupyterhub_architecture.png', fontsize=9)
    ax.text(1.5, 0.5, '👨‍💻 Data Scientists: Review jupyterhub_data_flow.png', fontsize=9) 
    ax.text(1.5, 0.3, '⚙️ Admins: Use all diagrams for operational understanding', fontsize=9)
    
    # Remove axes
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Save
    output_dir = Path("../docs/diagrams")
    plt.tight_layout(pad=0.5)
    plt.savefig(output_dir / 'DIAGRAM_OVERVIEW.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

if __name__ == "__main__":
    print("Generating diagram overview...")
    create_diagram_overview()
    print("✓ Created diagram overview: ../docs/diagrams/DIAGRAM_OVERVIEW.png")