#!/usr/bin/env python3
"""
IAM Security Diagrams Generator

This script creates comprehensive visual diagrams for IAM security architecture including:
1. IAM Roles & Policies Matrix
2. Permission Boundaries Flow
3. Security Groups Hierarchy
4. Cross-Account Access Patterns

Generated diagrams help understand the complete security model and access patterns.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Rectangle
import numpy as np
from pathlib import Path
import os
from datetime import datetime

# Set up matplotlib for better rendering
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = False

def create_fancy_box(ax, x, y, width, height, text, color, text_color='black', 
                     border_color='black', border_width=1, corner_radius=0.02):
    """Create a fancy rounded box with text"""
    # Create fancy box
    box = FancyBboxPatch((x, y), width, height,
                        boxstyle=f"round,pad=0.01,rounding_size={corner_radius}",
                        facecolor=color, edgecolor=border_color, linewidth=border_width,
                        alpha=0.8)
    ax.add_patch(box)
    
    # Add text
    ax.text(x + width/2, y + height/2, text, ha='center', va='center', 
            fontsize=9, color=text_color, weight='bold', wrap=True)

def create_arrow(ax, start_x, start_y, end_x, end_y, color='black', style='->', width=2):
    """Create an arrow between two points"""
    if style == '-->':
        style = '-|>'
    ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                arrowprops=dict(arrowstyle=style, color=color, lw=width))

def create_iam_roles_policies_matrix():
    """Create IAM Roles & Policies Matrix diagram"""
    print("Creating IAM Roles & Policies Matrix diagram...")
    
    # Create figure with high DPI for better quality
    fig, ax = plt.subplots(1, 1, figsize=(20, 16), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Title
    ax.text(50, 95, 'IAM Roles & Policies Matrix', fontsize=24, weight='bold', 
            ha='center', va='center')
    ax.text(50, 92, 'Complete Security Access Control Model', fontsize=14, 
            ha='center', va='center', style='italic')
    
    # Color scheme
    colors = {
        'admin': '#FF6B6B',      # Red for admin
        'security': '#4ECDC4',   # Teal for security
        'ops': '#45B7D1',        # Blue for operations
        'dev': '#96CEB4',        # Green for developers
        'business': '#FFEAA7',   # Yellow for business
        'service': '#DDA0DD',    # Plum for service accounts
        'policy': '#FFB6C1',     # Light pink for policies
        'boundary': '#FFA07A'    # Light salmon for boundaries
    }
    
    # Users Section (Left Side)
    ax.text(5, 85, 'USER GROUPS', fontsize=16, weight='bold', ha='left')
    
    user_groups = [
        ('Super Admins', 'admin', 'Full AWS access\nEmergency procedures'),
        ('Security Team', 'security', 'Security services\nCompliance monitoring'),
        ('DevOps Team', 'ops', 'Infrastructure management\nDeployment operations'),
        ('Developers', 'dev', 'Development resources\nLimited AWS access'),
        ('Business Users', 'business', 'Read-only access\nReporting & dashboards'),
        ('Service Accounts', 'service', 'Application services\nAutomated processes')
    ]
    
    y_pos = 78
    user_positions = {}
    for name, color_key, desc in user_groups:
        create_fancy_box(ax, 2, y_pos, 25, 8, f"{name}\n{desc}", 
                        colors[color_key], 'black', 'black', 2)
        user_positions[name] = (14.5, y_pos + 4)  # Center of box
        y_pos -= 12
    
    # Policies Section (Right Side)  
    ax.text(75, 85, 'IAM POLICIES', fontsize=16, weight='bold', ha='center')
    
    policies = [
        ('AdministratorAccess', 'admin', 'Full AWS access'),
        ('SecurityAudit', 'security', 'Security read access'),
        ('PowerUserAccess', 'ops', 'All except IAM'),
        ('ReadOnlyAccess', 'business', 'Read-only access'),
        ('Custom Policies', 'policy', 'Service-specific\nresource access'),
        ('Boundary Policies', 'boundary', 'Maximum permission\nlimits')
    ]
    
    y_pos = 78
    policy_positions = {}
    for name, color_key, desc in policies:
        create_fancy_box(ax, 70, y_pos, 25, 8, f"{name}\n{desc}", 
                        colors[color_key], 'black', 'black', 2)
        policy_positions[name] = (82.5, y_pos + 4)  # Center of box
        y_pos -= 12
    
    # Roles Section (Center)
    ax.text(50, 85, 'IAM ROLES', fontsize=16, weight='bold', ha='center')
    
    roles = [
        ('super-admin-role', 'admin'),
        ('security-admin-role', 'security'),
        ('platform-admin-role', 'ops'),
        ('database-admin-role', 'ops'),
        ('developer-role', 'dev'),
        ('business-read-role', 'business'),
        ('service-roles', 'service')
    ]
    
    y_pos = 78
    role_positions = {}
    for role, color_key in roles:
        create_fancy_box(ax, 40, y_pos, 20, 8, role, 
                        colors[color_key], 'black', 'black', 2)
        role_positions[role] = (50, y_pos + 4)  # Center of box
        y_pos -= 12
    
    # Permission Flow Arrows
    # Super Admin connections
    create_arrow(ax, user_positions['Super Admins'][0], user_positions['Super Admins'][1],
                role_positions['super-admin-role'][0] - 10, role_positions['super-admin-role'][1],
                '#FF6B6B', '->', 2)
    create_arrow(ax, role_positions['super-admin-role'][0] + 10, role_positions['super-admin-role'][1],
                policy_positions['AdministratorAccess'][0] - 12.5, policy_positions['AdministratorAccess'][1],
                '#FF6B6B', '->', 2)
    
    # Security Team connections
    create_arrow(ax, user_positions['Security Team'][0], user_positions['Security Team'][1],
                role_positions['security-admin-role'][0] - 10, role_positions['security-admin-role'][1],
                '#4ECDC4', '->', 2)
    create_arrow(ax, role_positions['security-admin-role'][0] + 10, role_positions['security-admin-role'][1],
                policy_positions['SecurityAudit'][0] - 12.5, policy_positions['SecurityAudit'][1],
                '#4ECDC4', '->', 2)
    
    # DevOps Team connections  
    create_arrow(ax, user_positions['DevOps Team'][0], user_positions['DevOps Team'][1],
                role_positions['platform-admin-role'][0] - 10, role_positions['platform-admin-role'][1],
                '#45B7D1', '->', 2)
    create_arrow(ax, role_positions['platform-admin-role'][0] + 10, role_positions['platform-admin-role'][1],
                policy_positions['PowerUserAccess'][0] - 12.5, policy_positions['PowerUserAccess'][1],
                '#45B7D1', '->', 2)
    
    # Developer connections
    create_arrow(ax, user_positions['Developers'][0], user_positions['Developers'][1],
                role_positions['developer-role'][0] - 10, role_positions['developer-role'][1],
                '#96CEB4', '->', 2)
    create_arrow(ax, role_positions['developer-role'][0] + 10, role_positions['developer-role'][1],
                policy_positions['Custom Policies'][0] - 12.5, policy_positions['Custom Policies'][1],
                '#96CEB4', '->', 2)
    
    # Business Users connections
    create_arrow(ax, user_positions['Business Users'][0], user_positions['Business Users'][1],
                role_positions['business-read-role'][0] - 10, role_positions['business-read-role'][1],
                '#FFEAA7', '->', 2)
    create_arrow(ax, role_positions['business-read-role'][0] + 10, role_positions['business-read-role'][1],
                policy_positions['ReadOnlyAccess'][0] - 12.5, policy_positions['ReadOnlyAccess'][1],
                '#FFEAA7', '->', 2)
    
    # Service Account connections
    create_arrow(ax, user_positions['Service Accounts'][0], user_positions['Service Accounts'][1],
                role_positions['service-roles'][0] - 10, role_positions['service-roles'][1],
                '#DDA0DD', '->', 2)
    create_arrow(ax, role_positions['service-roles'][0] + 10, role_positions['service-roles'][1],
                policy_positions['Custom Policies'][0] - 12.5, policy_positions['Custom Policies'][1],
                '#DDA0DD', '->', 2)
    
    # Permission Boundaries (connecting to all user groups)
    boundary_y = policy_positions['Boundary Policies'][1]
    for group_name, pos in user_positions.items():
        if group_name != 'Super Admins':  # Super admins don't have boundaries
            create_arrow(ax, pos[0] + 12.5, pos[1], 
                        policy_positions['Boundary Policies'][0] - 12.5, boundary_y,
                        '#FFA07A', '-|>', 1)
    
    # Legend
    ax.text(5, 8, 'LEGEND:', fontsize=14, weight='bold')
    ax.text(5, 5, '→ Direct Policy Attachment', fontsize=10)
    ax.text(5, 3, '--→ Permission Boundary', fontsize=10)
    ax.text(5, 1, 'Colors indicate security clearance level', fontsize=10, style='italic')
    
    # MFA Requirements Box
    create_fancy_box(ax, 75, 15, 22, 10, 
                    'MFA REQUIREMENTS\n\n• Admin roles: Required\n• Assume role: Required\n• Console access: Required\n• API access: Conditional',
                    '#FFE4E1', 'black', 'red', 2)
    
    # IP Restrictions Box  
    create_fancy_box(ax, 75, 3, 22, 10,
                    'IP RESTRICTIONS\n\n• Corporate networks only\n• VPN required for remote\n• Office IP ranges\n• Emergency access IPs',
                    '#E0FFFF', 'black', 'blue', 2)
    
    plt.tight_layout()
    return fig

def create_permission_boundaries_flow():
    """Create Permission Boundaries Flow diagram"""
    print("Creating Permission Boundaries Flow diagram...")
    
    fig, ax = plt.subplots(1, 1, figsize=(18, 14), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Title
    ax.text(50, 95, 'IAM Permission Boundaries Flow', fontsize=24, weight='bold', 
            ha='center', va='center')
    ax.text(50, 92, 'Maximum Permission Enforcement Model', fontsize=14, 
            ha='center', va='center', style='italic')
    
    # Color scheme
    colors = {
        'user': '#96CEB4',       # Green for users
        'boundary': '#FFA07A',   # Salmon for boundaries  
        'policy': '#FFB6C1',     # Pink for policies
        'effective': '#87CEEB',  # Sky blue for effective permissions
        'deny': '#FFB6B6',       # Light red for denials
        'allow': '#90EE90'       # Light green for allowed
    }
    
    # User Types Section
    ax.text(10, 85, 'USER TYPES', fontsize=16, weight='bold')
    
    user_types = [
        ('Developer', 'user', 'Development\nresources'),
        ('Operations', 'user', 'Infrastructure\nmanagement'), 
        ('Business', 'user', 'Read-only\naccess'),
        ('Security', 'user', 'Security\nservices'),
        ('Service Account', 'user', 'Application\nservices')
    ]
    
    y_pos = 78
    user_positions = {}
    for name, color_key, desc in user_types:
        create_fancy_box(ax, 5, y_pos, 18, 8, f"{name}\n{desc}", 
                        colors[color_key], 'black', 'black', 2)
        user_positions[name] = (14, y_pos + 4)
        y_pos -= 14
    
    # Permission Boundaries Section
    ax.text(40, 85, 'PERMISSION BOUNDARIES', fontsize=16, weight='bold')
    
    boundaries = [
        ('developer-boundary', 'boundary', 'EKS, Lambda, S3\nLogs, CloudWatch\nLimited IAM'),
        ('operations-boundary', 'boundary', 'EC2, EKS, RDS\nAll infrastructure\nLimited IAM'),
        ('business-boundary', 'boundary', 'Read-only access\nDashboards only\nNo write operations'),
        ('security-boundary', 'boundary', 'All security services\nIAM, KMS, Secrets\nAudit capabilities'),
        ('service-boundary', 'boundary', 'Service-specific\nApplication APIs\nNo user management')
    ]
    
    y_pos = 78
    boundary_positions = {}
    for name, color_key, desc in boundaries:
        create_fancy_box(ax, 30, y_pos, 25, 8, f"{name}\n{desc}", 
                        colors[color_key], 'black', 'black', 2)
        boundary_positions[name] = (42.5, y_pos + 4)
        y_pos -= 14
    
    # Effective Permissions Section
    ax.text(75, 85, 'EFFECTIVE PERMISSIONS', fontsize=16, weight='bold')
    
    effective_perms = [
        ('Allowed Actions', 'allow', 'Identity Policy\n∩\nBoundary Policy'),
        ('Denied Actions', 'deny', 'Exceeded boundary\nlimits'),
        ('Conditional Access', 'effective', 'MFA + IP\nrestrictions'),
        ('Resource Limits', 'effective', 'Environment\nscoped access'),
        ('Time Limits', 'effective', 'Session\nduration limits')
    ]
    
    y_pos = 78
    effective_positions = {}
    for name, color_key, desc in effective_perms:
        create_fancy_box(ax, 70, y_pos, 25, 8, f"{name}\n{desc}", 
                        colors[color_key], 'black', 'black', 2)
        effective_positions[name] = (82.5, y_pos + 4)
        y_pos -= 14
    
    # Flow Arrows
    # User to Boundary connections
    create_arrow(ax, user_positions['Developer'][0] + 9, user_positions['Developer'][1],
                boundary_positions['developer-boundary'][0] - 12.5, boundary_positions['developer-boundary'][1],
                '#96CEB4', '->', 2)
    
    create_arrow(ax, user_positions['Operations'][0] + 9, user_positions['Operations'][1],
                boundary_positions['operations-boundary'][0] - 12.5, boundary_positions['operations-boundary'][1],
                '#96CEB4', '->', 2)
    
    create_arrow(ax, user_positions['Business'][0] + 9, user_positions['Business'][1],
                boundary_positions['business-boundary'][0] - 12.5, boundary_positions['business-boundary'][1],
                '#96CEB4', '->', 2)
    
    create_arrow(ax, user_positions['Security'][0] + 9, user_positions['Security'][1],
                boundary_positions['security-boundary'][0] - 12.5, boundary_positions['security-boundary'][1],
                '#96CEB4', '->', 2)
    
    create_arrow(ax, user_positions['Service Account'][0] + 9, user_positions['Service Account'][1],
                boundary_positions['service-boundary'][0] - 12.5, boundary_positions['service-boundary'][1],
                '#96CEB4', '->', 2)
    
    # Boundary to Effective Permissions
    create_arrow(ax, boundary_positions['developer-boundary'][0] + 12.5, boundary_positions['developer-boundary'][1],
                effective_positions['Allowed Actions'][0] - 12.5, effective_positions['Allowed Actions'][1],
                '#FFA07A', '->', 2)
    
    create_arrow(ax, boundary_positions['operations-boundary'][0] + 12.5, boundary_positions['operations-boundary'][1],
                effective_positions['Conditional Access'][0] - 12.5, effective_positions['Conditional Access'][1],
                '#FFA07A', '->', 2)
    
    create_arrow(ax, boundary_positions['business-boundary'][0] + 12.5, boundary_positions['business-boundary'][1],
                effective_positions['Denied Actions'][0] - 12.5, effective_positions['Denied Actions'][1],
                '#FFA07A', '->', 2)
    
    # Policy Evaluation Logic Box
    create_fancy_box(ax, 25, 15, 50, 12,
                    'POLICY EVALUATION LOGIC\n\n1. Identity-based policies define intended permissions\n2. Permission boundaries define maximum allowed permissions\n3. Effective permissions = Identity Policy ∩ Permission Boundary\n4. Additional conditions: MFA, IP, Time, Resource tags',
                    '#F0F8FF', 'black', 'navy', 2)
    
    # Key Benefits Box
    create_fancy_box(ax, 5, 3, 40, 8,
                    'KEY BENEFITS\n\n• Prevent privilege escalation\n• Enforce security guardrails\n• Delegate permission management\n• Maintain compliance boundaries',
                    '#F0FFF0', 'black', 'darkgreen', 2)
    
    # Common Restrictions Box
    create_fancy_box(ax, 55, 3, 40, 8,
                    'COMMON RESTRICTIONS\n\n• No IAM user/role creation\n• No billing/cost management\n• Regional restrictions\n• Resource tagging requirements',
                    '#FFF0F0', 'black', 'darkred', 2)
    
    plt.tight_layout()
    return fig

def create_security_groups_hierarchy():
    """Create Security Groups Hierarchy diagram"""
    print("Creating Security Groups Hierarchy diagram...")
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Title
    ax.text(50, 95, 'Security Groups Hierarchy', fontsize=24, weight='bold', 
            ha='center', va='center')
    ax.text(50, 92, 'Permission Escalation & Access Levels', fontsize=14, 
            ha='center', va='center', style='italic')
    
    # Color scheme for hierarchy levels
    colors = {
        'level1': '#FFB6B6',  # Light red - Highest privilege
        'level2': '#FFD93D',  # Yellow - High privilege  
        'level3': '#6BCF7F',  # Green - Medium privilege
        'level4': '#4D96FF',  # Blue - Low privilege
        'level5': '#9B59B6'   # Purple - Service accounts
    }
    
    # Hierarchy Levels (Pyramid structure)
    levels = [
        # Level 1: Super Admin (Top)
        {
            'name': 'Super Administrators',
            'groups': ['super-admins'],
            'permissions': 'Full AWS Account Access\nEmergency Procedures\nBilling Management', 
            'y': 82, 'width': 30, 'color': 'level1'
        },
        # Level 2: Security & Platform Admin
        {
            'name': 'Administrative Teams', 
            'groups': ['security-admin', 'platform-admin', 'database-admin'],
            'permissions': 'Service Administration\nSecurity Management\nInfrastructure Control',
            'y': 68, 'width': 45, 'color': 'level2'
        },
        # Level 3: Operations & DevOps
        {
            'name': 'Operations Teams',
            'groups': ['devops-engineers', 'security-operations', 'monitoring-team'],
            'permissions': 'Infrastructure Management\nDeployment Operations\nMonitoring & Alerting',
            'y': 54, 'width': 60, 'color': 'level3'
        },
        # Level 4: Developers & Business
        {
            'name': 'Development & Business',
            'groups': ['developers', 'qa-team', 'business-users', 'support-team'],
            'permissions': 'Application Development\nTesting & QA\nBusiness Intelligence\nCustomer Support',
            'y': 40, 'width': 75, 'color': 'level4'
        },
        # Level 5: Service Accounts (Bottom)
        {
            'name': 'Service Accounts',
            'groups': ['application-services', 'monitoring-services', 'backup-services'],
            'permissions': 'Automated Processes\nApplication APIs\nScheduled Tasks\nSystem Operations',
            'y': 26, 'width': 90, 'color': 'level5'
        }
    ]
    
    # Draw hierarchy levels
    level_positions = {}
    for i, level in enumerate(levels):
        x = 50 - level['width']/2
        create_fancy_box(ax, x, level['y'], level['width'], 10, 
                        f"{level['name']}\n{level['permissions']}", 
                        colors[level['color']], 'black', 'black', 2)
        level_positions[level['name']] = (50, level['y'] + 5)
        
        # Add group details on the side
        group_text = ' | '.join(level['groups'])
        ax.text(95, level['y'] + 5, group_text, fontsize=8, ha='right', va='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='gray'))
    
    # Escalation Arrows
    for i in range(len(levels) - 1):
        start_y = levels[i+1]['y'] + 10
        end_y = levels[i]['y'] 
        create_arrow(ax, 50, start_y, 50, end_y, 'red', '->', 3)
        
        # Add escalation labels
        mid_y = (start_y + end_y) / 2
        ax.text(45, mid_y, f'Level {i+1}→{i+2}', fontsize=8, ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='yellow', alpha=0.7))
    
    # Access Control Matrix
    ax.text(5, 20, 'ACCESS CONTROL MATRIX', fontsize=14, weight='bold')
    
    services = ['IAM', 'EC2', 'EKS', 'RDS', 'S3', 'Lambda', 'CloudWatch', 'Billing']
    access_matrix = {
        'Super Admin': ['Full', 'Full', 'Full', 'Full', 'Full', 'Full', 'Full', 'Full'],
        'Security Admin': ['Full', 'Read', 'Read', 'Read', 'Read', 'Read', 'Full', 'None'],
        'Platform Admin': ['Limited', 'Full', 'Full', 'Full', 'Full', 'Full', 'Full', 'None'],
        'DevOps': ['None', 'Limited', 'Full', 'Limited', 'Limited', 'Full', 'Full', 'None'],
        'Developer': ['None', 'None', 'Limited', 'None', 'Limited', 'Full', 'Read', 'None'],
        'Business': ['None', 'None', 'None', 'None', 'Read', 'None', 'Read', 'Read'],
        'Service': ['None', 'None', 'API', 'API', 'API', 'API', 'Write', 'None']
    }
    
    # Draw matrix
    cell_width = 12
    cell_height = 2
    start_x = 5
    start_y = 16
    
    # Headers
    for i, service in enumerate(services):
        ax.text(start_x + (i+1) * cell_width + cell_width/2, start_y, service, 
                fontsize=8, ha='center', va='center', weight='bold')
    
    # Matrix rows
    row_colors = {'Full': '#FF6B6B', 'Limited': '#FFD93D', 'Read': '#4ECDC4', 
                  'Write': '#95E4D3', 'API': '#DDA0DD', 'None': '#D3D3D3'}
    
    y_offset = 0
    for role, permissions in access_matrix.items():
        y = start_y - 2 - y_offset
        ax.text(start_x + cell_width/2, y, role, fontsize=8, ha='center', va='center', weight='bold')
        
        for i, perm in enumerate(permissions):
            x = start_x + (i+1) * cell_width
            color = row_colors.get(perm, '#FFFFFF')
            rect = Rectangle((x, y-cell_height/2), cell_width, cell_height, 
                           facecolor=color, edgecolor='black', alpha=0.7)
            ax.add_patch(rect)
            ax.text(x + cell_width/2, y, perm, fontsize=7, ha='center', va='center', weight='bold')
        
        y_offset += 2.5
    
    # Legend
    ax.text(5, 2, 'LEGEND:', fontsize=12, weight='bold')
    legend_items = [('Full', '#FF6B6B'), ('Limited', '#FFD93D'), ('Read', '#4ECDC4'), 
                   ('Write', '#95E4D3'), ('API', '#DDA0DD'), ('None', '#D3D3D3')]
    
    for i, (label, color) in enumerate(legend_items):
        x = 15 + i * 12
        rect = Rectangle((x, 1), 2, 1, facecolor=color, edgecolor='black', alpha=0.7)
        ax.add_patch(rect)
        ax.text(x + 1, 1.5, label, fontsize=8, ha='center', va='center', weight='bold')
    
    plt.tight_layout()
    return fig

def create_cross_account_access():
    """Create Cross-Account Access Pattern diagram"""
    print("Creating Cross-Account Access Pattern diagram...")
    
    fig, ax = plt.subplots(1, 1, figsize=(18, 12), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Title
    ax.text(50, 95, 'Cross-Account Access Patterns', fontsize=24, weight='bold', 
            ha='center', va='center')
    ax.text(50, 92, 'Service Roles & Trust Relationships', fontsize=14, 
            ha='center', va='center', style='italic')
    
    # Color scheme
    colors = {
        'dev_account': '#96CEB4',      # Green
        'uat_account': '#FFD93D',      # Yellow  
        'prod_account': '#FF6B6B',     # Red
        'shared_account': '#4ECDC4',   # Teal
        'service_role': '#DDA0DD',     # Plum
        'trust': '#87CEEB'             # Sky blue
    }
    
    # AWS Accounts
    accounts = [
        ('Development Account', 'dev_account', '123456789012', 15, 75),
        ('UAT Account', 'uat_account', '123456789013', 45, 75), 
        ('Production Account', 'prod_account', '123456789014', 75, 75),
        ('Shared Services', 'shared_account', '123456789015', 30, 45),
        ('Security Account', 'shared_account', '123456789016', 60, 45)
    ]
    
    account_positions = {}
    for name, color_key, account_id, x, y in accounts:
        create_fancy_box(ax, x-10, y-5, 20, 10, f"{name}\n{account_id}", 
                        colors[color_key], 'black', 'black', 2)
        account_positions[name] = (x, y)
    
    # Service Roles within each account
    service_roles = [
        ('EKS Service Role', 'service_role', 15, 60),
        ('Lambda Execution Role', 'service_role', 15, 50),
        ('RDS Enhanced Monitoring', 'service_role', 15, 40),
        
        ('API Gateway Role', 'service_role', 45, 60), 
        ('Step Functions Role', 'service_role', 45, 50),
        ('CloudWatch Events Role', 'service_role', 45, 40),
        
        ('Production EKS Role', 'service_role', 75, 60),
        ('Backup Service Role', 'service_role', 75, 50),
        ('Monitoring Role', 'service_role', 75, 40),
        
        ('Central Logging Role', 'service_role', 30, 30),
        ('Cost Management Role', 'service_role', 30, 20),
        
        ('Security Audit Role', 'service_role', 60, 30),
        ('Compliance Role', 'service_role', 60, 20)
    ]
    
    role_positions = {}
    for name, color_key, x, y in service_roles:
        create_fancy_box(ax, x-8, y-2, 16, 4, name, 
                        colors[color_key], 'black', 'black', 1)
        role_positions[name] = (x, y)
    
    # Trust Relationships (Cross-account arrows)
    trust_relationships = [
        # Development to Shared Services
        ('Development Account', 'Shared Services', 'Central Logging\nAccess'),
        # UAT to Shared Services  
        ('UAT Account', 'Shared Services', 'Shared Resources\nAccess'),
        # Production to Security Account
        ('Production Account', 'Security Account', 'Security Audit\n& Compliance'),
        # All accounts to Security Account
        ('Development Account', 'Security Account', 'Security\nMonitoring'),
        ('UAT Account', 'Security Account', 'Security\nMonitoring'),
        # Shared Services to all accounts
        ('Shared Services', 'Development Account', 'Management\nOperations'),
        ('Shared Services', 'UAT Account', 'Management\nOperations'), 
        ('Shared Services', 'Production Account', 'Management\nOperations')
    ]
    
    for source, target, label in trust_relationships:
        start_pos = account_positions[source]
        end_pos = account_positions[target]
        
        # Calculate arrow position to avoid overlapping
        if start_pos[1] == end_pos[1]:  # Same height
            if start_pos[0] < end_pos[0]:  # Left to right
                start_x, start_y = start_pos[0] + 10, start_pos[1]
                end_x, end_y = end_pos[0] - 10, end_pos[1]
            else:  # Right to left
                start_x, start_y = start_pos[0] - 10, start_pos[1]  
                end_x, end_y = end_pos[0] + 10, end_pos[1]
        else:  # Different heights
            start_x, start_y = start_pos[0], start_pos[1] - 5
            end_x, end_y = end_pos[0], end_pos[1] + 5
        
        create_arrow(ax, start_x, start_y, end_x, end_y, colors['trust'], '->', 2)
        
        # Add label at midpoint
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        ax.text(mid_x, mid_y, label, fontsize=7, ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor='gray', alpha=0.8))
    
    # AssumeRole Policy Example
    create_fancy_box(ax, 5, 8, 40, 10,
                    'ASSUMEROLE POLICY EXAMPLE\n\n{\n  "Effect": "Allow",\n  "Principal": {\n    "AWS": "arn:aws:iam::123456789012:root"\n  },\n  "Action": "sts:AssumeRole",\n  "Condition": {\n    "StringEquals": {\n      "sts:ExternalId": "unique-external-id"\n    }\n  }\n}',
                    '#F0F8FF', 'black', 'navy', 2)
    
    # Security Best Practices
    create_fancy_box(ax, 55, 8, 40, 10,
                    'SECURITY BEST PRACTICES\n\n• Use External IDs for third-party access\n• Implement MFA for sensitive operations\n• Limit session duration\n• Use condition keys for additional security\n• Regular access reviews\n• Monitor CloudTrail for AssumeRole events',
                    '#F0FFF0', 'black', 'darkgreen', 2)
    
    plt.tight_layout()
    return fig

def create_documentation_summary():
    """Create comprehensive documentation summary"""
    return f"""# IAM Security Diagrams Documentation

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This document accompanies the visual IAM security diagrams created to illustrate the complete security model and access control patterns for the mono-repo infrastructure.

## Generated Diagrams

### 1. IAM Roles & Policies Matrix (`iam_roles_policies_matrix`)
**Purpose**: Complete security access control model showing relationships between users, roles, and policies

**Key Components**:
- **User Groups**: Super Admins, Security Team, DevOps Team, Developers, Business Users, Service Accounts
- **IAM Roles**: Environment-specific roles with appropriate privilege levels
- **Policy Attachments**: Direct policy assignments and managed policy usage
- **MFA Requirements**: Multi-factor authentication enforcement
- **IP Restrictions**: Corporate network access controls

**Security Features**:
- Role-based access control (RBAC)
- Principle of least privilege
- Separation of duties
- Administrative access controls

### 2. Permission Boundaries Flow (`permission_boundaries_flow`)
**Purpose**: Maximum permission enforcement model showing how boundaries limit effective permissions

**Flow Process**:
1. **Identity Policies**: Define intended permissions
2. **Permission Boundaries**: Set maximum allowed permissions
3. **Effective Permissions**: Intersection of identity and boundary policies
4. **Additional Conditions**: MFA, IP, time, and resource restrictions

**Boundary Types**:
- **Developer Boundary**: EKS, Lambda, S3, limited IAM
- **Operations Boundary**: Full infrastructure, limited IAM
- **Business Boundary**: Read-only access, no write operations
- **Security Boundary**: All security services, audit capabilities
- **Service Boundary**: Service-specific APIs, no user management

### 3. Security Groups Hierarchy (`security_groups_hierarchy`)
**Purpose**: Permission escalation and access levels across the organization

**Hierarchy Levels**:
- **Level 1**: Super Administrators (Full access)
- **Level 2**: Administrative Teams (Service administration)
- **Level 3**: Operations Teams (Infrastructure management)
- **Level 4**: Development & Business (Application development)
- **Level 5**: Service Accounts (Automated processes)

**Access Matrix**: Shows specific service permissions for each level

### 4. Cross-Account Access Patterns (`cross_account_access`)
**Purpose**: Service roles and trust relationships across AWS accounts

**Account Structure**:
- **Development Account**: Development resources and testing
- **UAT Account**: User acceptance testing environment
- **Production Account**: Production workloads
- **Shared Services Account**: Central logging and management
- **Security Account**: Security monitoring and compliance

**Trust Relationships**: Cross-account role assumptions with security controls

## Security Implementation

### Multi-Factor Authentication (MFA)
- Required for all administrative roles
- Console access requires MFA
- AssumeRole operations require MFA
- API access conditional on MFA

### IP Address Restrictions
- Corporate network access only
- VPN required for remote access
- Office IP range allowlists
- Emergency access IP controls

### Session Management
- Limited session duration
- Automatic session timeout
- Re-authentication requirements
- Session activity monitoring

### Monitoring and Auditing
- CloudTrail logging for all IAM actions
- AssumeRole event monitoring
- Regular access reviews
- Compliance reporting

## Usage Instructions

### Role Assignment Process
1. Identify user's job function and required access level
2. Assign appropriate group membership
3. Configure MFA requirements
4. Set up IP restrictions
5. Test access permissions
6. Document role assignment

### Permission Boundary Application
1. Determine user type (developer, operations, business, etc.)
2. Apply appropriate boundary policy
3. Validate effective permissions
4. Test boundary enforcement
5. Monitor for boundary violations

### Cross-Account Access Setup
1. Define trust relationship requirements
2. Create cross-account roles
3. Configure external ID requirements
4. Set up conditional access
5. Test cross-account functionality
6. Monitor cross-account activity

## Best Practices

### Security
- Always use principle of least privilege
- Implement defense in depth
- Regular security reviews
- Automated compliance checking
- Incident response procedures

### Operational
- Standardized role naming conventions
- Documented permission rationale
- Regular access audits
- Automated provisioning
- Change management processes

### Compliance
- SOC 2 compliance alignment
- Regular audit trail reviews
- Data access logging
- Privacy controls
- Regulatory requirement mapping

## File Structure
```
docs/architecture/
├── iam_roles_policies_matrix.png         # Complete IAM model
├── iam_roles_policies_matrix.svg         # Vector format
├── permission_boundaries_flow.png        # Boundary enforcement
├── permission_boundaries_flow.svg        # Vector format
├── security_groups_hierarchy.png         # Access levels
├── security_groups_hierarchy.svg         # Vector format
├── cross_account_access.png              # Account relationships
└── cross_account_access.svg              # Vector format
```

Created: {datetime.now().strftime('%B %d, %Y')}
Generated by: create_iam_security_diagrams.py
"""

def main():
    """Main function to generate all IAM security diagrams"""
    print("🔐 Starting IAM Security Diagrams generation...")
    
    # Create output directory
    output_dir = Path("../docs/architecture")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate diagrams
    diagrams = [
        ("iam_roles_policies_matrix", create_iam_roles_policies_matrix()),
        ("permission_boundaries_flow", create_permission_boundaries_flow()), 
        ("security_groups_hierarchy", create_security_groups_hierarchy()),
        ("cross_account_access", create_cross_account_access())
    ]
    
    # Save diagrams in both PNG and SVG formats
    for name, fig in diagrams:
        # Save PNG
        png_path = output_dir / f"{name}.png"
        fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        
        # Save SVG
        svg_path = output_dir / f"{name}.svg"
        fig.savefig(svg_path, format='svg', bbox_inches='tight', facecolor='white', edgecolor='none')
        
        plt.close(fig)
        print(f"✅ Created {name} diagram")
    
    # Create documentation
    doc_content = create_documentation_summary()
    doc_path = Path("../docs/IAM_SECURITY_DIAGRAMS_DOCUMENTATION.md")
    with open(doc_path, 'w') as f:
        f.write(doc_content)
    
    print(f"✅ Created comprehensive IAM security documentation")
    
    print(f"\n✅ All IAM security diagrams generated successfully!")
    print(f"📊 Generated {len(diagrams)} diagrams (PNG + SVG formats)")
    print(f"📖 Created comprehensive documentation")
    print(f"🔧 View diagrams in: {output_dir.resolve()}")

if __name__ == "__main__":
    main()