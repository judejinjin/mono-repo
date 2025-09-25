#!/usr/bin/env python3
"""
Multi-Environment Security Isolation Diagram Generator

This script generates comprehensive diagrams illustrating the security isolation
between DEV, UAT, and PROD environments in AWS infrastructure.

Generated Diagrams:
1. Environment Isolation Architecture - Overall security boundaries
2. IAM Cross-Environment Access Patterns - Role-based environment access
3. Network Segmentation & Security Groups - Network-level isolation
4. Resource Tagging & Policy Enforcement - Compliance and governance

Author: Infrastructure Team
Date: 2024
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Rectangle, Circle
import numpy as np
import os
from datetime import datetime
import matplotlib.patheffects as path_effects

# Set up the style
plt.style.use('default')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'

def setup_directories():
    """Create necessary directories for output"""
    dirs = ['../docs/architecture', '../docs']
    for dir_path in dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    print("📁 Output directories ready")

def create_environment_isolation_architecture():
    """Generate Environment Isolation Architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(10, 14.5, 'Multi-Environment Security Isolation Architecture', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(10, 14, 'DEV / UAT / PROD Environment Separation & Security Controls', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # AWS Account boundary
    aws_account = FancyBboxPatch((0.5, 1), 19, 12, 
                                boxstyle="round,pad=0.1", 
                                facecolor='#f0f8ff', edgecolor='#4a90e2', linewidth=2)
    ax.add_patch(aws_account)
    ax.text(1, 12.5, 'AWS Account: Risk Management Platform', 
            fontsize=12, fontweight='bold', color='#4a90e2')
    
    # Environment boxes
    environments = [
        {'name': 'DEVELOPMENT', 'x': 1, 'y': 9, 'width': 5.5, 'height': 3, 'color': '#e8f5e8', 'border': '#2e7d2e'},
        {'name': 'UAT/STAGING', 'x': 7.25, 'y': 9, 'width': 5.5, 'height': 3, 'color': '#fff3cd', 'border': '#b8860b'},
        {'name': 'PRODUCTION', 'x': 13.5, 'y': 9, 'width': 5.5, 'height': 3, 'color': '#f8d7da', 'border': '#dc3545'}
    ]
    
    for env in environments:
        env_box = FancyBboxPatch((env['x'], env['y']), env['width'], env['height'],
                               boxstyle="round,pad=0.1", 
                               facecolor=env['color'], edgecolor=env['border'], linewidth=2)
        ax.add_patch(env_box)
        ax.text(env['x'] + env['width']/2, env['y'] + env['height'] - 0.3, env['name'], 
                fontsize=12, fontweight='bold', ha='center', color=env['border'])
    
    # VPC components for each environment
    vpc_configs = [
        {'env': 'DEV', 'x': 1.2, 'y': 9.2, 'width': 5.1, 'color': '#2e7d2e'},
        {'env': 'UAT', 'x': 7.45, 'y': 9.2, 'width': 5.1, 'color': '#b8860b'},
        {'env': 'PROD', 'x': 13.7, 'y': 9.2, 'width': 5.1, 'color': '#dc3545'}
    ]
    
    for i, vpc in enumerate(vpc_configs):
        # VPC
        vpc_box = Rectangle((vpc['x'], vpc['y'] + 1.8), vpc['width'], 1, 
                           facecolor='white', edgecolor=vpc['color'], linewidth=1.5, alpha=0.8)
        ax.add_patch(vpc_box)
        ax.text(vpc['x'] + vpc['width']/2, vpc['y'] + 2.3, f"VPC-{vpc['env']}", 
                fontsize=10, ha='center', fontweight='bold', color=vpc['color'])
        
        # Subnets
        subnet_width = vpc['width'] / 2 - 0.2
        # Private subnet
        priv_subnet = Rectangle((vpc['x'] + 0.1, vpc['y'] + 1), subnet_width, 0.6, 
                               facecolor='#ffeeee', edgecolor=vpc['color'], linewidth=1)
        ax.add_patch(priv_subnet)
        ax.text(vpc['x'] + 0.1 + subnet_width/2, vpc['y'] + 1.3, 'Private', 
                fontsize=8, ha='center', color=vpc['color'])
        
        # Public subnet
        pub_subnet = Rectangle((vpc['x'] + subnet_width + 0.3, vpc['y'] + 1), subnet_width, 0.6, 
                              facecolor='#eeffee', edgecolor=vpc['color'], linewidth=1)
        ax.add_patch(pub_subnet)
        ax.text(vpc['x'] + subnet_width + 0.3 + subnet_width/2, vpc['y'] + 1.3, 'Public', 
                fontsize=8, ha='center', color=vpc['color'])
        
        # Security Groups
        sg_box = Rectangle((vpc['x'] + 0.1, vpc['y'] + 0.2), vpc['width'] - 0.2, 0.6, 
                          facecolor='#f0f0f0', edgecolor=vpc['color'], linewidth=1, linestyle='--')
        ax.add_patch(sg_box)
        ax.text(vpc['x'] + vpc['width']/2, vpc['y'] + 0.5, f'Security Groups ({vpc["env"]})', 
                fontsize=8, ha='center', color=vpc['color'])
    
    # Central Management Services
    mgmt_box = FancyBboxPatch((7, 5.5), 6, 3, boxstyle="round,pad=0.1", 
                             facecolor='#e6f3ff', edgecolor='#0066cc', linewidth=2)
    ax.add_patch(mgmt_box)
    ax.text(10, 8, 'Centralized Management & Security', 
            fontsize=12, fontweight='bold', ha='center', color='#0066cc')
    
    # Management services
    services = [
        {'name': 'IAM Roles & Policies', 'x': 7.5, 'y': 7.3},
        {'name': 'CloudTrail (Audit)', 'x': 7.5, 'y': 6.9},
        {'name': 'Config Rules', 'x': 7.5, 'y': 6.5},
        {'name': 'Systems Manager', 'x': 10.5, 'y': 7.3},
        {'name': 'Parameter Store', 'x': 10.5, 'y': 6.9},
        {'name': 'Secrets Manager', 'x': 10.5, 'y': 6.5}
    ]
    
    for service in services:
        service_box = Rectangle((service['x'], service['y']), 2.3, 0.3, 
                               facecolor='white', edgecolor='#0066cc', linewidth=1)
        ax.add_patch(service_box)
        ax.text(service['x'] + 1.15, service['y'] + 0.15, service['name'], 
                fontsize=9, ha='center', color='#0066cc')
    
    # Cross-environment access controls
    ax.text(10, 5, 'Cross-Environment Access Controls', 
            fontsize=12, fontweight='bold', ha='center', color='#cc0066')
    
    # Access control rules
    rules = [
        '• DEV → UAT: Limited read access with approval',
        '• UAT → PROD: Deployment pipeline only',
        '• PROD → Others: No access (air-gapped)',
        '• Admin → All: Break-glass emergency access'
    ]
    
    for i, rule in enumerate(rules):
        ax.text(2, 4.3 - i*0.3, rule, fontsize=10, color='#cc0066')
    
    # Network isolation arrows
    # DEV to UAT
    arrow1 = ConnectionPatch((6.5, 10.5), (7.25, 10.5), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5, mutation_scale=20, 
                           fc="#ff6600", ec="#ff6600", linewidth=2)
    ax.add_artist(arrow1)
    ax.text(6.9, 10.7, 'Controlled\nAccess', fontsize=8, ha='center', color='#ff6600')
    
    # UAT to PROD
    arrow2 = ConnectionPatch((12.75, 10.5), (13.5, 10.5), "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5, mutation_scale=20, 
                           fc="#ff6600", ec="#ff6600", linewidth=2)
    ax.add_artist(arrow2)
    ax.text(13.1, 10.7, 'Pipeline\nOnly', fontsize=8, ha='center', color='#ff6600')
    
    # Legend
    legend_elements = [
        {'name': 'Development Environment', 'color': '#2e7d2e'},
        {'name': 'UAT/Staging Environment', 'color': '#b8860b'},
        {'name': 'Production Environment', 'color': '#dc3545'},
        {'name': 'Management Services', 'color': '#0066cc'},
        {'name': 'Access Controls', 'color': '#cc0066'}
    ]
    
    for i, item in enumerate(legend_elements):
        ax.add_patch(Rectangle((15, 3.5 - i*0.4), 0.3, 0.2, 
                              facecolor=item['color'], alpha=0.7))
        ax.text(15.5, 3.6 - i*0.4, item['name'], fontsize=9, va='center')
    
    # Compliance badges
    ax.text(1, 0.5, '🔒 SOC 2 Type II Compliant', fontsize=10, color='#0066cc')
    ax.text(6, 0.5, '🛡️ ISO 27001 Controls', fontsize=10, color='#0066cc')
    ax.text(11, 0.5, '⚖️ Regulatory Compliance', fontsize=10, color='#0066cc')
    
    # Save the diagram
    plt.tight_layout()
    plt.savefig('../docs/architecture/environment_isolation_architecture.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/environment_isolation_architecture.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ Environment Isolation Architecture diagram generated")

def create_iam_cross_environment_access():
    """Generate IAM Cross-Environment Access Patterns diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(10, 14.5, 'IAM Cross-Environment Access Patterns', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(10, 14, 'Role-Based Access Control & Environment Isolation', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # User groups section
    ax.text(2, 12.5, 'User Groups & Roles', fontsize=14, fontweight='bold', color='#0066cc')
    
    user_groups = [
        {'name': 'Developers', 'x': 1, 'y': 11, 'color': '#28a745', 'access': ['DEV-Full', 'UAT-Read']},
        {'name': 'QA Testers', 'x': 1, 'y': 10, 'color': '#ffc107', 'access': ['UAT-Full', 'DEV-Read']},
        {'name': 'DevOps Engineers', 'x': 1, 'y': 9, 'color': '#17a2b8', 'access': ['All-Deploy']},
        {'name': 'Platform Admins', 'x': 1, 'y': 8, 'color': '#dc3545', 'access': ['All-Admin']}
    ]
    
    for group in user_groups:
        # User group box
        group_box = FancyBboxPatch((group['x'], group['y']), 3, 0.7, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor=group['color'], alpha=0.2, 
                                  edgecolor=group['color'], linewidth=2)
        ax.add_patch(group_box)
        ax.text(group['x'] + 1.5, group['y'] + 0.35, group['name'], 
                fontsize=11, ha='center', fontweight='bold', color=group['color'])
    
    # Environment access matrix
    environments = ['DEVELOPMENT', 'UAT/STAGING', 'PRODUCTION']
    env_colors = ['#28a745', '#ffc107', '#dc3545']
    
    # Environment headers
    for i, (env, color) in enumerate(zip(environments, env_colors)):
        env_x = 6 + i * 4.5
        env_box = FancyBboxPatch((env_x, 12), 4, 1, boxstyle="round,pad=0.1", 
                                facecolor=color, alpha=0.2, edgecolor=color, linewidth=2)
        ax.add_patch(env_box)
        ax.text(env_x + 2, 12.5, env, fontsize=12, ha='center', fontweight='bold', color=color)
    
    # Access patterns matrix
    access_matrix = [
        # Developers
        [
            {'level': 'FULL ACCESS', 'desc': '• EC2, RDS, S3\n• CloudWatch\n• Parameter Store', 'color': '#28a745'},
            {'level': 'READ ONLY', 'desc': '• View resources\n• CloudWatch logs\n• Basic monitoring', 'color': '#6c757d'},
            {'level': 'NO ACCESS', 'desc': '• Blocked by policy\n• No permissions\n• Air-gapped', 'color': '#dc3545'}
        ],
        # QA Testers  
        [
            {'level': 'READ ONLY', 'desc': '• View test data\n• Access logs\n• Basic resources', 'color': '#6c757d'},
            {'level': 'FULL ACCESS', 'desc': '• Test execution\n• Data management\n• Environment control', 'color': '#ffc107'},
            {'level': 'NO ACCESS', 'desc': '• Blocked by policy\n• No permissions\n• Air-gapped', 'color': '#dc3545'}
        ],
        # DevOps Engineers
        [
            {'level': 'DEPLOY ONLY', 'desc': '• Pipeline execution\n• Infrastructure\n• Monitoring setup', 'color': '#17a2b8'},
            {'level': 'DEPLOY ONLY', 'desc': '• Pipeline execution\n• Infrastructure\n• Monitoring setup', 'color': '#17a2b8'},
            {'level': 'DEPLOY ONLY', 'desc': '• Pipeline execution\n• Infrastructure\n• Emergency access', 'color': '#17a2b8'}
        ],
        # Platform Admins
        [
            {'level': 'ADMIN ACCESS', 'desc': '• Full permissions\n• User management\n• Policy control', 'color': '#dc3545'},
            {'level': 'ADMIN ACCESS', 'desc': '• Full permissions\n• User management\n• Policy control', 'color': '#dc3545'},
            {'level': 'BREAK-GLASS', 'desc': '• Emergency only\n• Audit logged\n• Time-limited', 'color': '#fd7e14'}
        ]
    ]
    
    for row_idx, (group, access_row) in enumerate(zip(user_groups, access_matrix)):
        for col_idx, access in enumerate(access_row):
            cell_x = 6 + col_idx * 4.5
            cell_y = 11 - row_idx * 1
            
            # Access level box
            access_box = FancyBboxPatch((cell_x, cell_y - 0.8), 4, 0.6, 
                                       boxstyle="round,pad=0.05", 
                                       facecolor=access['color'], alpha=0.15, 
                                       edgecolor=access['color'], linewidth=1)
            ax.add_patch(access_box)
            
            # Access level text
            ax.text(cell_x + 2, cell_y - 0.3, access['level'], 
                    fontsize=10, ha='center', fontweight='bold', color=access['color'])
            ax.text(cell_x + 2, cell_y - 0.7, access['desc'], 
                    fontsize=8, ha='center', color=access['color'])
    
    # Role assumption patterns
    ax.text(2, 6.5, 'Cross-Environment Role Assumptions', fontsize=14, fontweight='bold', color='#6f42c1')
    
    # Role assumption flow
    role_flows = [
        {'from': 'Base Role', 'to': 'Dev-ReadWrite', 'condition': 'Developer + MFA', 'y': 5.8},
        {'from': 'Base Role', 'to': 'UAT-ReadOnly', 'condition': 'Developer + Approval', 'y': 5.4},
        {'from': 'Base Role', 'to': 'Prod-Emergency', 'condition': 'Admin + Break-Glass', 'y': 5.0},
        {'from': 'Pipeline Role', 'to': 'All-Deploy', 'condition': 'CI/CD + Automation', 'y': 4.6}
    ]
    
    for flow in role_flows:
        # From box
        from_box = Rectangle((1, flow['y']), 2.5, 0.25, 
                            facecolor='#e9ecef', edgecolor='#6f42c1', linewidth=1)
        ax.add_patch(from_box)
        ax.text(2.25, flow['y'] + 0.125, flow['from'], 
                fontsize=9, ha='center', color='#6f42c1')
        
        # Arrow
        arrow = ConnectionPatch((3.5, flow['y'] + 0.125), (6, flow['y'] + 0.125), "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5, mutation_scale=15, 
                               fc="#6f42c1", ec="#6f42c1", linewidth=1.5)
        ax.add_artist(arrow)
        
        # Condition
        ax.text(4.75, flow['y'] + 0.2, flow['condition'], 
                fontsize=8, ha='center', color='#6f42c1', style='italic')
        
        # To box
        to_box = Rectangle((6, flow['y']), 2.5, 0.25, 
                          facecolor='#d1ecf1', edgecolor='#6f42c1', linewidth=1)
        ax.add_patch(to_box)
        ax.text(7.25, flow['y'] + 0.125, flow['to'], 
                fontsize=9, ha='center', color='#6f42c1')
    
    # Policy enforcement mechanisms
    ax.text(11, 6.5, 'Policy Enforcement Mechanisms', fontsize=14, fontweight='bold', color='#e83e8c')
    
    mechanisms = [
        '🔐 Condition Keys: aws:RequestedRegion, aws:MultiFactorAuthPresent',
        '⏰ Time-Based Access: Business hours only for non-prod',  
        '🌐 IP Restrictions: Corporate network + VPN only',
        '📋 Resource Tags: Environment-specific tag enforcement',
        '🔄 Temporary Credentials: Session tokens with expiration',
        '📊 CloudTrail Logging: All cross-environment access logged'
    ]
    
    for i, mechanism in enumerate(mechanisms):
        ax.text(11, 5.9 - i*0.3, mechanism, fontsize=9, color='#e83e8c')
    
    # Compliance section
    compliance_box = FancyBboxPatch((1, 2), 18, 1.5, boxstyle="round,pad=0.1", 
                                   facecolor='#fff3cd', edgecolor='#856404', linewidth=2)
    ax.add_patch(compliance_box)
    ax.text(10, 3.2, 'Compliance & Security Controls', 
            fontsize=12, fontweight='bold', ha='center', color='#856404')
    
    compliance_items = [
        '• Principle of Least Privilege: Minimal required permissions only',
        '• Separation of Duties: No single user has full production access',
        '• Regular Access Reviews: Quarterly permission audits and cleanup',
        '• Automated Remediation: Policy violations automatically blocked'
    ]
    
    for i, item in enumerate(compliance_items[:2]):
        ax.text(2, 2.8 - i*0.2, item, fontsize=9, color='#856404')
    for i, item in enumerate(compliance_items[2:]):
        ax.text(11, 2.8 - i*0.2, item, fontsize=9, color='#856404')
    
    # Security boundaries
    ax.text(10, 0.8, '⚠️  CRITICAL: Production environment maintains strict air-gap isolation', 
            fontsize=11, ha='center', fontweight='bold', color='#dc3545',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#f8d7da', edgecolor='#dc3545'))
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/iam_cross_environment_access.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/iam_cross_environment_access.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ IAM Cross-Environment Access Patterns diagram generated")

def create_network_segmentation_security():
    """Generate Network Segmentation & Security Groups diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(11, 14.5, 'Network Segmentation & Security Groups', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(11, 14, 'Multi-Environment Network Isolation & Traffic Control', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # VPC sections for each environment
    vpcs = [
        {'name': 'DEV VPC (10.0.0.0/16)', 'x': 1, 'y': 10, 'width': 6, 'height': 3.5, 'color': '#28a745'},
        {'name': 'UAT VPC (10.1.0.0/16)', 'x': 8, 'y': 10, 'width': 6, 'height': 3.5, 'color': '#ffc107'},
        {'name': 'PROD VPC (10.2.0.0/16)', 'x': 15, 'y': 10, 'width': 6, 'height': 3.5, 'color': '#dc3545'}
    ]
    
    for vpc in vpcs:
        # VPC boundary
        vpc_box = FancyBboxPatch((vpc['x'], vpc['y']), vpc['width'], vpc['height'],
                                boxstyle="round,pad=0.1", 
                                facecolor=vpc['color'], alpha=0.1, 
                                edgecolor=vpc['color'], linewidth=2)
        ax.add_patch(vpc_box)
        ax.text(vpc['x'] + vpc['width']/2, vpc['y'] + vpc['height'] - 0.3, vpc['name'], 
                fontsize=11, fontweight='bold', ha='center', color=vpc['color'])
        
        # Subnets within VPC
        subnet_configs = [
            {'name': 'Public\n10.x.1.0/24', 'x': vpc['x'] + 0.2, 'y': vpc['y'] + 2, 'width': 2.5, 'height': 1.2, 'type': 'public'},
            {'name': 'Private App\n10.x.2.0/24', 'x': vpc['x'] + 3, 'y': vpc['y'] + 2, 'width': 2.5, 'height': 1.2, 'type': 'private'},
            {'name': 'Private DB\n10.x.3.0/24', 'x': vpc['x'] + 0.2, 'y': vpc['y'] + 0.3, 'width': 2.5, 'height': 1.2, 'type': 'database'},
            {'name': 'Management\n10.x.4.0/24', 'x': vpc['x'] + 3, 'y': vpc['y'] + 0.3, 'width': 2.5, 'height': 1.2, 'type': 'mgmt'}
        ]
        
        for subnet in subnet_configs:
            if subnet['type'] == 'public':
                color = '#e6ffe6'
                border = '#00cc00'
            elif subnet['type'] == 'private':
                color = '#fff0e6'  
                border = '#ff9900'
            elif subnet['type'] == 'database':
                color = '#ffe6e6'
                border = '#cc0000'
            else:  # management
                color = '#e6e6ff'
                border = '#0066cc'
            
            subnet_box = FancyBboxPatch((subnet['x'], subnet['y']), subnet['width'], subnet['height'],
                                       boxstyle="round,pad=0.05", 
                                       facecolor=color, edgecolor=border, linewidth=1)
            ax.add_patch(subnet_box)
            ax.text(subnet['x'] + subnet['width']/2, subnet['y'] + subnet['height']/2, subnet['name'], 
                    fontsize=9, ha='center', va='center', color=border, fontweight='bold')
    
    # Security Groups section
    ax.text(11, 9.2, 'Security Group Rules & Traffic Flow', 
            fontsize=14, fontweight='bold', ha='center', color='#6f42c1')
    
    # Security group rules matrix
    sg_rules = [
        {'name': 'ALB Security Group', 'inbound': 'Internet:443,80', 'outbound': 'App-SG:8080', 'y': 8.5},
        {'name': 'App Security Group', 'inbound': 'ALB-SG:8080', 'outbound': 'DB-SG:5432', 'y': 8.1},
        {'name': 'DB Security Group', 'inbound': 'App-SG:5432', 'outbound': 'None', 'y': 7.7},
        {'name': 'Mgmt Security Group', 'inbound': 'Corp-IP:22', 'outbound': 'All:443', 'y': 7.3}
    ]
    
    for rule in sg_rules:
        # Security group name
        sg_box = Rectangle((2, rule['y']), 3, 0.3, 
                          facecolor='#f8f9fa', edgecolor='#6f42c1', linewidth=1)
        ax.add_patch(sg_box)
        ax.text(3.5, rule['y'] + 0.15, rule['name'], 
                fontsize=9, ha='center', color='#6f42c1', fontweight='bold')
        
        # Inbound rules
        in_box = Rectangle((5.5, rule['y']), 3.5, 0.3, 
                          facecolor='#d4edda', edgecolor='#28a745', linewidth=1)
        ax.add_patch(in_box)
        ax.text(7.25, rule['y'] + 0.15, rule['inbound'], 
                fontsize=8, ha='center', color='#28a745')
        
        # Outbound rules
        out_box = Rectangle((9.5, rule['y']), 3.5, 0.3, 
                           facecolor='#fff3cd', edgecolor='#ffc107', linewidth=1)
        ax.add_patch(out_box)
        ax.text(11.25, rule['y'] + 0.15, rule['outbound'], 
                fontsize=8, ha='center', color='#ffc107')
        
        # Arrow between inbound and outbound
        arrow = ConnectionPatch((9, rule['y'] + 0.15), (9.5, rule['y'] + 0.15), "data", "data",
                               arrowstyle="->", shrinkA=2, shrinkB=2, mutation_scale=10, 
                               fc="#6f42c1", ec="#6f42c1")
        ax.add_artist(arrow)
    
    # Headers for security group rules
    ax.text(3.5, 8.9, 'Security Group', fontsize=10, ha='center', fontweight='bold', color='#6f42c1')
    ax.text(7.25, 8.9, 'Inbound Rules', fontsize=10, ha='center', fontweight='bold', color='#28a745')
    ax.text(11.25, 8.9, 'Outbound Rules', fontsize=10, ha='center', fontweight='bold', color='#ffc107')
    
    # Cross-environment networking
    ax.text(11, 6.5, 'Cross-Environment Network Controls', 
            fontsize=14, fontweight='bold', ha='center', color='#e83e8c')
    
    # VPC Peering connections (minimal)
    peering_configs = [
        {'from': 'DEV VPC', 'to': 'Shared Services', 'rules': 'DNS, Monitoring only', 'y': 6},
        {'from': 'UAT VPC', 'to': 'Shared Services', 'rules': 'DNS, Monitoring, Deploy', 'y': 5.6},
        {'from': 'PROD VPC', 'to': 'Shared Services', 'rules': 'DNS, Monitoring (isolated)', 'y': 5.2}
    ]
    
    for config in peering_configs:
        ax.text(2, config['y'], config['from'], fontsize=9, color='#e83e8c', fontweight='bold')
        
        # Connection arrow
        arrow = ConnectionPatch((5, config['y'] + 0.1), (8, config['y'] + 0.1), "data", "data",
                               arrowstyle="<->", shrinkA=5, shrinkB=5, mutation_scale=15, 
                               fc="#e83e8c", ec="#e83e8c", linewidth=1.5)
        ax.add_artist(arrow)
        
        ax.text(6.5, config['y'] + 0.2, config['rules'], fontsize=8, ha='center', color='#e83e8c', style='italic')
        ax.text(10, config['y'], config['to'], fontsize=9, color='#e83e8c', fontweight='bold')
    
    # Network ACL restrictions
    ax.text(16, 6.5, 'Network ACL Restrictions', 
            fontsize=12, fontweight='bold', color='#17a2b8')
    
    nacl_rules = [
        '• Block inter-environment traffic',
        '• Allow only specific service ports',
        '• Deny all by default policy',
        '• Emergency break-glass rules'
    ]
    
    for i, rule in enumerate(nacl_rules):
        ax.text(16, 6.1 - i*0.25, rule, fontsize=9, color='#17a2b8')
    
    # Traffic flow visualization
    ax.text(11, 4.5, 'Typical Traffic Flow Patterns', 
            fontsize=14, fontweight='bold', ha='center', color='#fd7e14')
    
    # Flow patterns
    flows = [
        {'name': '1. User Request', 'path': 'Internet → ALB → App Server → Database', 'security': 'HTTPS/TLS', 'y': 4},
        {'name': '2. Management', 'path': 'Corporate VPN → Bastion → Private Resources', 'security': 'SSH/RDP', 'y': 3.6},
        {'name': '3. Monitoring', 'path': 'All Resources → CloudWatch → Management VPC', 'security': 'AWS APIs', 'y': 3.2},
        {'name': '4. Deployment', 'path': 'CI/CD Pipeline → Target Environment → Validation', 'security': 'Signed/Encrypted', 'y': 2.8}
    ]
    
    for flow in flows:
        ax.text(2, flow['y'], flow['name'], fontsize=10, fontweight='bold', color='#fd7e14')
        ax.text(4, flow['y'], flow['path'], fontsize=9, color='#fd7e14')
        ax.text(16, flow['y'], f"Security: {flow['security']}", fontsize=9, color='#fd7e14', style='italic')
    
    # Security controls summary
    controls_box = FancyBboxPatch((1, 0.5), 20, 1.5, boxstyle="round,pad=0.1", 
                                 facecolor='#f8d7da', edgecolor='#dc3545', linewidth=2)
    ax.add_patch(controls_box)
    ax.text(11, 1.7, 'Network Security Controls Summary', 
            fontsize=12, fontweight='bold', ha='center', color='#dc3545')
    
    controls = [
        '🔒 Zero Trust: No implicit trust between environments',
        '🛡️ Defense in Depth: Multiple security layers (NACLs + Security Groups + WAF)',
        '📊 Traffic Monitoring: All flows logged and analyzed',
        '⚡ Automated Response: Suspicious activity automatically blocked'
    ]
    
    for i, control in enumerate(controls[:2]):
        ax.text(2, 1.3 - i*0.2, control, fontsize=9, color='#dc3545')
    for i, control in enumerate(controls[2:]):
        ax.text(12, 1.3 - i*0.2, control, fontsize=9, color='#dc3545')
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/network_segmentation_security.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/network_segmentation_security.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ Network Segmentation & Security Groups diagram generated")

def create_resource_tagging_governance():
    """Generate Resource Tagging & Policy Enforcement diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(10, 14.5, 'Resource Tagging & Policy Enforcement', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(10, 14, 'Compliance, Governance & Cost Management Through Tags', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # Mandatory tag schema
    ax.text(2, 13, 'Mandatory Tag Schema', fontsize=14, fontweight='bold', color='#0066cc')
    
    tag_schema = [
        {'tag': 'Environment', 'values': 'dev | uat | prod', 'purpose': 'Environment isolation'},
        {'tag': 'Project', 'values': 'risk-management', 'purpose': 'Resource grouping'},
        {'tag': 'Owner', 'values': 'team-name@company.com', 'purpose': 'Responsibility tracking'},
        {'tag': 'CostCenter', 'values': 'CC-XXXX', 'purpose': 'Billing allocation'},
        {'tag': 'DataClassification', 'values': 'public | internal | confidential', 'purpose': 'Data governance'},
        {'tag': 'Backup', 'values': 'required | optional | none', 'purpose': 'Backup policies'}
    ]
    
    for i, tag in enumerate(tag_schema):
        y_pos = 12.3 - i*0.3
        # Tag name
        tag_box = Rectangle((1.5, y_pos), 2, 0.2, 
                           facecolor='#e3f2fd', edgecolor='#0066cc', linewidth=1)
        ax.add_patch(tag_box)
        ax.text(2.5, y_pos + 0.1, tag['tag'], fontsize=9, ha='center', fontweight='bold', color='#0066cc')
        
        # Possible values
        values_box = Rectangle((3.7, y_pos), 4, 0.2, 
                              facecolor='#f3e5f5', edgecolor='#9c27b0', linewidth=1)
        ax.add_patch(values_box)
        ax.text(5.7, y_pos + 0.1, tag['values'], fontsize=8, ha='center', color='#9c27b0')
        
        # Purpose
        ax.text(8, y_pos + 0.1, tag['purpose'], fontsize=8, color='#666', style='italic')
    
    # Environment-specific tag enforcement
    ax.text(12, 13, 'Environment Tag Policies', fontsize=14, fontweight='bold', color='#28a745')
    
    env_policies = [
        {'env': 'DEVELOPMENT', 'color': '#28a745', 'rules': [
            '• Relaxed tagging requirements',
            '• Owner tag mandatory',
            '• Auto-cleanup after 30 days',
            '• Cost alerts at $500/month'
        ]},
        {'env': 'UAT/STAGING', 'color': '#ffc107', 'rules': [
            '• All mandatory tags required',
            '• DataClassification enforced',
            '• Backup tag mandatory',
            '• Cost alerts at $1000/month'
        ]},
        {'env': 'PRODUCTION', 'color': '#dc3545', 'rules': [
            '• Zero tolerance - all tags required',
            '• Compliance validation automated',
            '• Immutable tags (Project, Owner)',
            '• Real-time cost monitoring'
        ]}
    ]
    
    for i, env_policy in enumerate(env_policies):
        y_start = 12.5 - i*2.8
        
        # Environment header
        env_header = FancyBboxPatch((11.5, y_start), 7.5, 0.4, boxstyle="round,pad=0.05", 
                                   facecolor=env_policy['color'], alpha=0.2, 
                                   edgecolor=env_policy['color'], linewidth=2)
        ax.add_patch(env_header)
        ax.text(15.25, y_start + 0.2, env_policy['env'], fontsize=11, ha='center', 
                fontweight='bold', color=env_policy['color'])
        
        # Rules
        for j, rule in enumerate(env_policy['rules']):
            ax.text(12, y_start - 0.3 - j*0.25, rule, fontsize=9, color=env_policy['color'])
    
    # Tag-based access control
    ax.text(2, 10.2, 'Tag-Based Access Control (TBAC)', 
            fontsize=14, fontweight='bold', color='#6f42c1')
    
    tbac_examples = [
        {
            'role': 'DevTeam-Developer', 
            'condition': 'Environment=dev AND Owner=dev-team@company.com',
            'access': 'Full access to dev resources owned by dev team',
            'y': 9.7
        },
        {
            'role': 'QATeam-Tester', 
            'condition': 'Environment=uat AND Project=risk-management',
            'access': 'Read/write access to UAT risk management resources',
            'y': 9.3
        },
        {
            'role': 'ProdSupport-Engineer', 
            'condition': 'Environment=prod AND DataClassification!=confidential',
            'access': 'Limited production access excluding confidential data',
            'y': 8.9
        }
    ]
    
    for example in tbac_examples:
        # Role box
        role_box = Rectangle((1.5, example['y']), 2.5, 0.25, 
                            facecolor='#f3e5f5', edgecolor='#6f42c1', linewidth=1)
        ax.add_patch(role_box)
        ax.text(2.75, example['y'] + 0.125, example['role'], 
                fontsize=8, ha='center', fontweight='bold', color='#6f42c1')
        
        # Condition
        ax.text(4.2, example['y'] + 0.125, f"IF {example['condition']}", 
                fontsize=8, color='#6f42c1', style='italic')
        
        # Access description
        ax.text(1.5, example['y'] - 0.1, f"→ {example['access']}", 
                fontsize=8, color='#666')
    
    # Automated governance workflows
    ax.text(10, 8.2, 'Automated Governance Workflows', 
            fontsize=14, fontweight='bold', ha='center', color='#e83e8c')
    
    workflows = [
        {
            'trigger': 'Resource Created',
            'action': 'Tag Validation',
            'result': 'Block if mandatory tags missing',
            'x': 1, 'y': 7.5, 'color': '#28a745'
        },
        {
            'trigger': 'Cost Threshold',
            'action': 'Owner Notification', 
            'result': 'Alert sent to tagged owner',
            'x': 6, 'y': 7.5, 'color': '#ffc107'
        },
        {
            'trigger': 'Compliance Scan',
            'action': 'Policy Check',
            'result': 'Non-compliant resources flagged',
            'x': 11, 'y': 7.5, 'color': '#dc3545'
        },
        {
            'trigger': 'Backup Schedule',
            'action': 'Tag-Based Selection',
            'result': 'Auto-backup based on Backup tag',
            'x': 16, 'y': 7.5, 'color': '#17a2b8'
        }
    ]
    
    for workflow in workflows:
        # Workflow box
        workflow_box = FancyBboxPatch((workflow['x'], workflow['y']), 3.5, 1.5, 
                                     boxstyle="round,pad=0.1", 
                                     facecolor=workflow['color'], alpha=0.1, 
                                     edgecolor=workflow['color'], linewidth=2)
        ax.add_patch(workflow_box)
        
        # Workflow details
        ax.text(workflow['x'] + 1.75, workflow['y'] + 1.2, workflow['trigger'], 
                fontsize=9, ha='center', fontweight='bold', color=workflow['color'])
        ax.text(workflow['x'] + 1.75, workflow['y'] + 0.85, f"↓ {workflow['action']}", 
                fontsize=8, ha='center', color=workflow['color'])
        ax.text(workflow['x'] + 1.75, workflow['y'] + 0.3, workflow['result'], 
                fontsize=8, ha='center', color=workflow['color'], style='italic')
    
    # Cost allocation dashboard
    ax.text(10, 6.2, 'Cost Allocation Dashboard', 
            fontsize=14, fontweight='bold', ha='center', color='#fd7e14')
    
    # Sample cost breakdown
    cost_data = [
        {'category': 'Environment', 'dev': '$2,500', 'uat': '$1,800', 'prod': '$8,200'},
        {'category': 'Service', 'ec2': '$4,500', 'rds': '$3,200', 'other': '$4,800'},
        {'category': 'Team', 'dev-team': '$3,800', 'qa-team': '$2,100', 'platform': '$6,600'}
    ]
    
    # Cost table headers
    ax.text(3, 5.7, 'Cost Breakdown by Tags', fontsize=12, fontweight='bold', color='#fd7e14')
    headers = ['Category', 'Value 1', 'Value 2', 'Value 3']
    header_x = [2, 6, 10, 14]
    for i, header in enumerate(headers):
        header_box = Rectangle((header_x[i], 5.3), 3, 0.3, 
                              facecolor='#fff3cd', edgecolor='#fd7e14', linewidth=1)
        ax.add_patch(header_box)
        ax.text(header_x[i] + 1.5, 5.45, header, 
                fontsize=9, ha='center', fontweight='bold', color='#fd7e14')
    
    # Cost data rows
    for i, row in enumerate(cost_data):
        y_pos = 5 - i*0.4
        values = [row['category'], list(row.values())[1], list(row.values())[2], list(row.values())[3]]
        for j, value in enumerate(values):
            value_box = Rectangle((header_x[j], y_pos), 3, 0.3, 
                                 facecolor='#fff8e1', edgecolor='#fd7e14', linewidth=0.5)
            ax.add_patch(value_box)
            ax.text(header_x[j] + 1.5, y_pos + 0.15, value, 
                    fontsize=9, ha='center', color='#fd7e14')
    
    # Compliance reporting
    compliance_box = FancyBboxPatch((1, 2), 18, 1.5, boxstyle="round,pad=0.1", 
                                   facecolor='#d1ecf1', edgecolor='#0c5460', linewidth=2)
    ax.add_patch(compliance_box)
    ax.text(10, 3.2, 'Compliance Reporting & Auditing', 
            fontsize=12, fontweight='bold', ha='center', color='#0c5460')
    
    compliance_features = [
        '📊 Daily tag compliance reports with drift detection',
        '🔍 Automated remediation for tag policy violations',
        '📋 Quarterly access reviews based on resource ownership tags',
        '💰 Monthly cost allocation reports by business unit tags'
    ]
    
    for i, feature in enumerate(compliance_features[:2]):
        ax.text(2, 2.8 - i*0.2, feature, fontsize=9, color='#0c5460')
    for i, feature in enumerate(compliance_features[2:]):
        ax.text(11, 2.8 - i*0.2, feature, fontsize=9, color='#0c5460')
    
    # Best practices
    ax.text(10, 1.3, '🏆 Best Practices: Consistent tagging strategy enforced through automation', 
            fontsize=11, ha='center', fontweight='bold', color='#28a745',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#d4edda', edgecolor='#28a745'))
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/resource_tagging_governance.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/resource_tagging_governance.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ Resource Tagging & Policy Enforcement diagram generated")

def create_documentation():
    """Create comprehensive documentation for multi-environment security diagrams"""
    doc_content = f"""# Multi-Environment Security Isolation Diagrams

*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

This document provides comprehensive analysis of the multi-environment security isolation diagrams for the Risk Management Platform infrastructure.

## Overview

The multi-environment security diagrams illustrate the comprehensive security architecture that ensures proper isolation and access control across Development, UAT/Staging, and Production environments. These diagrams demonstrate defense-in-depth security principles with multiple layers of protection.

## Generated Diagrams

### 1. Environment Isolation Architecture
**File**: `environment_isolation_architecture.png/.svg`

This diagram provides a high-level view of how DEV, UAT, and PROD environments are isolated within the AWS infrastructure.

**Key Components**:
- **Environment Boundaries**: Clear separation of DEV, UAT, and PROD environments
- **VPC Isolation**: Each environment operates in its own VPC with distinct CIDR blocks
- **Centralized Management**: Shared services for IAM, monitoring, and compliance
- **Cross-Environment Controls**: Strict policies governing inter-environment access

**Security Features**:
- Air-gapped production environment
- Controlled access between non-production environments  
- Centralized audit logging and monitoring
- Compliance with SOC 2, ISO 27001, and regulatory requirements

### 2. IAM Cross-Environment Access Patterns
**File**: `iam_cross_environment_access.png/.svg`

Detailed visualization of role-based access control (RBAC) and how different user groups can access resources across environments.

**Access Matrix**:
- **Developers**: Full DEV access, read-only UAT access, no PROD access
- **QA Testers**: Read-only DEV access, full UAT access, no PROD access  
- **DevOps Engineers**: Deployment access to all environments via automation
- **Platform Admins**: Administrative access with break-glass for PROD

**Key Security Controls**:
- Principle of least privilege enforcement
- Multi-factor authentication requirements
- Time-based and IP-based access restrictions
- Comprehensive audit logging via CloudTrail

### 3. Network Segmentation & Security Groups
**File**: `network_segmentation_security.png/.svg`

Comprehensive network architecture showing how traffic is controlled and isolated between environments and within each environment.

**Network Architecture**:
- **VPC Segmentation**: Separate VPCs for each environment (10.0.0.0/16, 10.1.0.0/16, 10.2.0.0/16)
- **Subnet Strategy**: Public, private application, private database, and management subnets
- **Security Group Rules**: Layer-4 traffic control with specific port and protocol restrictions
- **Network ACLs**: Additional layer-3/4 controls for defense-in-depth

**Traffic Flow Patterns**:
1. **User Requests**: Internet → ALB → Application → Database
2. **Management Access**: Corporate VPN → Bastion → Private Resources
3. **Monitoring**: Resources → CloudWatch → Management VPC
4. **Deployment**: CI/CD Pipeline → Target Environment → Validation

### 4. Resource Tagging & Policy Enforcement
**File**: `resource_tagging_governance.png/.svg`

Governance framework using resource tags for access control, cost management, and compliance enforcement.

**Mandatory Tag Schema**:
- **Environment**: dev | uat | prod (environment isolation)
- **Project**: risk-management (resource grouping)
- **Owner**: team-name@company.com (responsibility tracking)
- **CostCenter**: CC-XXXX (billing allocation)
- **DataClassification**: public | internal | confidential (data governance)
- **Backup**: required | optional | none (backup policies)

**Tag-Based Access Control (TBAC)**:
- IAM policies that use tag conditions for resource access
- Environment-specific access based on tag values
- Data classification controls for sensitive information
- Cost center-based resource management

## Security Architecture Principles

### Defense in Depth
Multiple security layers provide comprehensive protection:

1. **Network Layer**: VPCs, subnets, security groups, NACLs
2. **Identity Layer**: IAM roles, policies, MFA, temporary credentials
3. **Application Layer**: Resource tagging, encryption, monitoring
4. **Data Layer**: Backup policies, data classification, access logging
5. **Management Layer**: Centralized governance, compliance validation

### Zero Trust Architecture
- No implicit trust between environments or services
- Every access request is authenticated and authorized
- Continuous monitoring and validation of access patterns
- Automated response to suspicious activities

### Compliance Framework
- **SOC 2 Type II**: Security, availability, and confidentiality controls
- **ISO 27001**: Information security management system
- **Regulatory Compliance**: Financial services and data protection requirements
- **Industry Standards**: AWS Well-Architected Framework security pillar

## Operational Procedures

### Access Management
1. **User Provisioning**: Role-based access assignment with environment restrictions
2. **Regular Reviews**: Quarterly access audits and cleanup procedures  
3. **Break-Glass Access**: Emergency procedures for critical production issues
4. **Automated Remediation**: Policy violations automatically blocked and reported

### Monitoring and Alerting
1. **Real-Time Monitoring**: CloudWatch metrics and logs for all environments
2. **Security Alerts**: Automated notifications for policy violations
3. **Cost Monitoring**: Tag-based cost allocation and budget alerts
4. **Compliance Dashboards**: Daily reports on governance and security posture

### Incident Response
1. **Automated Detection**: Security events trigger immediate response workflows
2. **Isolation Procedures**: Compromised resources can be quickly quarantined
3. **Forensic Capabilities**: Complete audit trail for security investigations
4. **Recovery Processes**: Environment-specific backup and restoration procedures

## Implementation Guidelines

### Environment Setup
1. Deploy VPCs with appropriate CIDR blocks for each environment
2. Configure security groups following principle of least privilege
3. Implement mandatory tagging policies through AWS Config
4. Set up centralized logging and monitoring infrastructure

### Access Control Implementation
1. Create environment-specific IAM roles and policies
2. Configure cross-environment access restrictions
3. Implement MFA requirements for sensitive operations
4. Set up break-glass procedures for emergency access

### Monitoring Configuration
1. Enable CloudTrail for all API activity logging
2. Configure CloudWatch alarms for security events
3. Set up cost allocation tags and budget monitoring
4. Implement compliance validation rules

## Security Validation

### Regular Security Assessments
- Monthly vulnerability scans across all environments
- Quarterly penetration testing of production systems
- Annual security architecture reviews and updates
- Continuous compliance monitoring and reporting

### Automated Security Testing
- Infrastructure as Code (IaC) security scanning
- Container and application security assessments
- Network segmentation validation testing
- Access control verification procedures

### Compliance Auditing
- Automated compliance checks against security baselines
- Regular audit log reviews and analysis
- Tag compliance monitoring and remediation
- Cost allocation accuracy verification

## Maintenance and Updates

### Regular Review Cycle
1. **Monthly**: Security group rules and access patterns
2. **Quarterly**: IAM policies and role assignments
3. **Semi-Annual**: Network architecture and segmentation
4. **Annual**: Complete security architecture review

### Change Management
- All security changes must be approved through formal change control
- Infrastructure changes deployed through automated pipelines
- Security policy updates require security team approval
- Emergency changes follow documented break-glass procedures

---

*This documentation is automatically updated when infrastructure diagrams are regenerated. For technical questions or clarifications, contact the Platform Security Team.*
"""

    with open('../docs/multi_environment_security_implementation.md', 'w') as f:
        f.write(doc_content)
    
    print("📖 Multi-Environment Security documentation created")

def main():
    """Main function to generate all multi-environment security diagrams"""
    print("🚀 Starting Multi-Environment Security Isolation diagram generation...")
    print("=" * 80)
    
    try:
        # Setup
        setup_directories()
        
        # Generate all diagrams
        create_environment_isolation_architecture()
        create_iam_cross_environment_access()
        create_network_segmentation_security()
        create_resource_tagging_governance()
        
        # Create documentation
        create_documentation()
        
        print("=" * 80)
        print("✅ Multi-Environment Security Isolation diagrams completed successfully!")
        print("\nGenerated Files:")
        print("📊 4 diagrams (PNG + SVG formats)")
        print("📖 1 comprehensive documentation file")
        print("\nAll files saved to:")
        print("- Diagrams: docs/architecture/")
        print("- Documentation: docs/multi_environment_security_implementation.md")
        
    except Exception as e:
        print(f"❌ Error generating diagrams: {{str(e)}}")
        raise

if __name__ == "__main__":
    main()