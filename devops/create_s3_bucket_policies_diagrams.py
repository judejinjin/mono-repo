#!/usr/bin/env python3
"""
S3 Bucket Policies & Access Control Diagram Generator

This script generates comprehensive diagrams illustrating S3 storage architecture,
bucket policies, access controls, and data management patterns across environments.

Generated Diagrams:
1. S3 Storage Architecture & Organization - Bucket structure and organization
2. IAM & Bucket Policy Access Control - Permission matrices and policy enforcement
3. Data Lifecycle & Cross-Account Access - Data management and sharing patterns
4. S3 Security & Compliance Framework - Encryption, monitoring, and governance

Author: Infrastructure Team
Date: 2024
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Rectangle, Circle, Ellipse
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

def create_s3_storage_architecture():
    """Generate S3 Storage Architecture & Organization diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(11, 14.5, 'S3 Storage Architecture & Organization', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(11, 14, 'Multi-Environment Bucket Structure & Data Organization', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # AWS Account boundary
    aws_account = FancyBboxPatch((0.5, 1), 21, 12, 
                                boxstyle="round,pad=0.1", 
                                facecolor='#f0f8ff', edgecolor='#4a90e2', linewidth=2)
    ax.add_patch(aws_account)
    ax.text(1, 12.5, 'AWS Account: Risk Management Platform - S3 Storage', 
            fontsize=12, fontweight='bold', color='#4a90e2')
    
    # Environment sections
    environments = [
        {'name': 'DEVELOPMENT', 'x': 1, 'y': 9, 'width': 6.5, 'height': 3.5, 'color': '#28a745'},
        {'name': 'UAT/STAGING', 'x': 8, 'y': 9, 'width': 6.5, 'height': 3.5, 'color': '#ffc107'},
        {'name': 'PRODUCTION', 'x': 15, 'y': 9, 'width': 6.5, 'height': 3.5, 'color': '#dc3545'}
    ]
    
    for env in environments:
        # Environment boundary
        env_box = FancyBboxPatch((env['x'], env['y']), env['width'], env['height'],
                               boxstyle="round,pad=0.1", 
                               facecolor=env['color'], alpha=0.1, 
                               edgecolor=env['color'], linewidth=2)
        ax.add_patch(env_box)
        ax.text(env['x'] + env['width']/2, env['y'] + env['height'] - 0.3, env['name'], 
                fontsize=12, fontweight='bold', ha='center', color=env['color'])
        
        # Bucket types within each environment
        bucket_configs = [
            {'name': 'Application Data', 'prefix': 'app-data', 'x': env['x'] + 0.2, 'y': env['y'] + 2.5, 'width': 3, 'height': 0.7, 'type': 'app'},
            {'name': 'Static Assets', 'prefix': 'static-web', 'x': env['x'] + 3.4, 'y': env['y'] + 2.5, 'width': 2.9, 'height': 0.7, 'type': 'static'},
            {'name': 'Logs & Analytics', 'prefix': 'logs', 'x': env['x'] + 0.2, 'y': env['y'] + 1.6, 'width': 3, 'height': 0.7, 'type': 'logs'},
            {'name': 'Backups', 'prefix': 'backup', 'x': env['x'] + 3.4, 'y': env['y'] + 1.6, 'width': 2.9, 'height': 0.7, 'type': 'backup'},
            {'name': 'Documents', 'prefix': 'docs', 'x': env['x'] + 0.2, 'y': env['y'] + 0.7, 'width': 3, 'height': 0.7, 'type': 'docs'},
            {'name': 'ML Models', 'prefix': 'ml-models', 'x': env['x'] + 3.4, 'y': env['y'] + 0.7, 'width': 2.9, 'height': 0.7, 'type': 'ml'}
        ]
        
        env_short = env['name'].lower().split('/')[0][:4]
        
        for bucket in bucket_configs:
            if bucket['type'] == 'app':
                color = '#e6ffe6'
                border = '#00cc00'
            elif bucket['type'] == 'static':
                color = '#fff0e6'  
                border = '#ff9900'
            elif bucket['type'] == 'logs':
                color = '#e6e6ff'
                border = '#0066cc'
            elif bucket['type'] == 'backup':
                color = '#ffe6e6'
                border = '#cc0000'
            elif bucket['type'] == 'docs':
                color = '#f0e6ff'
                border = '#9900cc'
            else:  # ml
                color = '#e6fff0'
                border = '#00cc66'
            
            bucket_box = FancyBboxPatch((bucket['x'], bucket['y']), bucket['width'], bucket['height'],
                                       boxstyle="round,pad=0.05", 
                                       facecolor=color, edgecolor=border, linewidth=1.5)
            ax.add_patch(bucket_box)
            ax.text(bucket['x'] + bucket['width']/2, bucket['y'] + bucket['height']/2 + 0.1, bucket['name'], 
                    fontsize=9, ha='center', va='center', color=border, fontweight='bold')
            ax.text(bucket['x'] + bucket['width']/2, bucket['y'] + bucket['height']/2 - 0.15, 
                    f"rm-{env_short}-{bucket['prefix']}", 
                    fontsize=8, ha='center', va='center', color=border, style='italic')
    
    # Shared services section
    shared_box = FancyBboxPatch((1, 5.5), 20, 3, boxstyle="round,pad=0.1", 
                               facecolor='#f8f9fa', edgecolor='#6c757d', linewidth=2)
    ax.add_patch(shared_box)
    ax.text(11, 8.2, 'Shared S3 Services & Cross-Environment Resources', 
            fontsize=12, fontweight='bold', ha='center', color='#6c757d')
    
    # Shared buckets
    shared_buckets = [
        {'name': 'CloudTrail Logs', 'bucket': 'rm-shared-cloudtrail', 'x': 2, 'y': 7.5, 'desc': 'Audit logs from all environments'},
        {'name': 'Config Snapshots', 'bucket': 'rm-shared-config', 'x': 7.5, 'y': 7.5, 'desc': 'AWS Config compliance data'},
        {'name': 'Cross-Account Access', 'bucket': 'rm-shared-xaccount', 'x': 13, 'y': 7.5, 'desc': 'Partner/vendor data exchange'},
        {'name': 'Terraform State', 'bucket': 'rm-shared-tfstate', 'x': 18.5, 'y': 7.5, 'desc': 'Infrastructure state files'},
        {'name': 'Disaster Recovery', 'bucket': 'rm-shared-dr', 'x': 2, 'y': 6.3, 'desc': 'Cross-region backup storage'},
        {'name': 'Data Lake', 'bucket': 'rm-shared-datalake', 'x': 7.5, 'y': 6.3, 'desc': 'Analytics and ML datasets'},
        {'name': 'Compliance Archive', 'bucket': 'rm-shared-archive', 'x': 13, 'y': 6.3, 'desc': 'Long-term data retention'},
        {'name': 'Cost Reports', 'bucket': 'rm-shared-costreports', 'x': 18.5, 'y': 6.3, 'desc': 'Billing and usage analytics'}
    ]
    
    for bucket in shared_buckets:
        bucket_box = FancyBboxPatch((bucket['x'] - 1.5, bucket['y'] - 0.3), 3, 0.6,
                                   boxstyle="round,pad=0.05", 
                                   facecolor='#e9ecef', edgecolor='#6c757d', linewidth=1)
        ax.add_patch(bucket_box)
        ax.text(bucket['x'], bucket['y'], bucket['name'], 
                fontsize=9, ha='center', fontweight='bold', color='#6c757d')
        ax.text(bucket['x'], bucket['y'] - 0.15, bucket['bucket'], 
                fontsize=7, ha='center', color='#6c757d', style='italic')
        ax.text(bucket['x'], bucket['y'] - 0.4, bucket['desc'], 
                fontsize=7, ha='center', color='#666')
    
    # Bucket naming convention
    ax.text(11, 4.8, 'Bucket Naming Convention & Organization', 
            fontsize=14, fontweight='bold', ha='center', color='#e83e8c')
    
    naming_rules = [
        {'rule': 'Format', 'pattern': 'rm-{env}-{service}-{purpose}', 'example': 'rm-prod-app-data'},
        {'rule': 'Environment', 'pattern': 'dev | uat | prod | shared', 'example': 'Environment identifier'},
        {'rule': 'Service', 'pattern': 'app | api | web | ml | logs', 'example': 'Service or component'},
        {'rule': 'Purpose', 'pattern': 'data | backup | logs | static', 'example': 'Data type or usage'}
    ]
    
    for i, rule in enumerate(naming_rules):
        y_pos = 4.4 - i*0.25
        ax.text(3, y_pos, f"{rule['rule']}:", fontsize=10, fontweight='bold', color='#e83e8c')
        ax.text(6, y_pos, rule['pattern'], fontsize=9, color='#e83e8c', fontfamily='monospace')
        ax.text(14, y_pos, rule['example'], fontsize=9, color='#666', style='italic')
    
    # Storage classes and lifecycle
    ax.text(11, 3, 'Storage Classes & Lifecycle Management', 
            fontsize=14, fontweight='bold', ha='center', color='#17a2b8')
    
    storage_classes = [
        {'class': 'Standard', 'use_case': 'Active data, frequent access', 'retention': '< 30 days', 'cost': 'Higher'},
        {'class': 'Standard-IA', 'use_case': 'Infrequent access, backup', 'retention': '30-90 days', 'cost': 'Medium'},
        {'class': 'Glacier Flexible', 'use_case': 'Archive, compliance', 'retention': '90 days - 1 year', 'cost': 'Low'},
        {'class': 'Glacier Deep Archive', 'use_case': 'Long-term retention', 'retention': '> 1 year', 'cost': 'Lowest'}
    ]
    
    # Storage class headers
    headers = ['Storage Class', 'Use Case', 'Typical Retention', 'Cost']
    header_x = [2, 6, 12, 16]
    for i, header in enumerate(headers):
        header_box = Rectangle((header_x[i], 2.5), 3.5, 0.3, 
                              facecolor='#d1ecf1', edgecolor='#17a2b8', linewidth=1)
        ax.add_patch(header_box)
        ax.text(header_x[i] + 1.75, 2.65, header, 
                fontsize=9, ha='center', fontweight='bold', color='#17a2b8')
    
    # Storage class data
    for i, storage in enumerate(storage_classes):
        y_pos = 2.2 - i*0.3
        values = [storage['class'], storage['use_case'], storage['retention'], storage['cost']]
        for j, value in enumerate(values):
            value_box = Rectangle((header_x[j], y_pos), 3.5, 0.25, 
                                 facecolor='#f8f9fa', edgecolor='#17a2b8', linewidth=0.5)
            ax.add_patch(value_box)
            ax.text(header_x[j] + 1.75, y_pos + 0.125, value, 
                    fontsize=8, ha='center', color='#17a2b8')
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/s3_storage_architecture.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/s3_storage_architecture.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ S3 Storage Architecture & Organization diagram generated")

def create_iam_bucket_policy_access():
    """Generate IAM & Bucket Policy Access Control diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(11, 14.5, 'IAM & Bucket Policy Access Control', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(11, 14, 'S3 Permission Matrix & Policy Enforcement Framework', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # IAM Roles section
    ax.text(3, 13, 'IAM Roles & S3 Access Patterns', fontsize=14, fontweight='bold', color='#0066cc')
    
    iam_roles = [
        {'role': 'Developer-Role', 'dev': 'Full', 'uat': 'Read', 'prod': 'None', 'shared': 'Limited'},
        {'role': 'QA-Tester-Role', 'dev': 'Read', 'uat': 'Full', 'prod': 'None', 'shared': 'Limited'},
        {'role': 'DevOps-Role', 'dev': 'Full', 'uat': 'Full', 'prod': 'Deploy', 'shared': 'Admin'},
        {'role': 'App-Service-Role', 'dev': 'RW-App', 'uat': 'RW-App', 'prod': 'RW-App', 'shared': 'Read'},
        {'role': 'Analytics-Role', 'dev': 'None', 'uat': 'Read', 'prod': 'Read', 'shared': 'RW-Data'},
        {'role': 'Backup-Service', 'dev': 'Backup', 'uat': 'Backup', 'prod': 'Backup', 'shared': 'Archive'}
    ]
    
    # Access matrix headers
    ax.text(2, 12.3, 'IAM Role', fontsize=10, fontweight='bold', color='#0066cc')
    environments = ['DEV', 'UAT', 'PROD', 'SHARED']
    env_colors = ['#28a745', '#ffc107', '#dc3545', '#6c757d']
    
    for i, (env, color) in enumerate(zip(environments, env_colors)):
        ax.text(6 + i*3, 12.3, env, fontsize=10, fontweight='bold', ha='center', color=color)
    
    # Access matrix
    for i, role in enumerate(iam_roles):
        y_pos = 11.8 - i*0.4
        
        # Role name
        role_box = Rectangle((1, y_pos), 4, 0.3, 
                            facecolor='#e3f2fd', edgecolor='#0066cc', linewidth=1)
        ax.add_patch(role_box)
        ax.text(3, y_pos + 0.15, role['role'], 
                fontsize=9, ha='center', fontweight='bold', color='#0066cc')
        
        # Access levels
        access_levels = [role['dev'], role['uat'], role['prod'], role['shared']]
        for j, (access, color) in enumerate(zip(access_levels, env_colors)):
            access_box = Rectangle((5.5 + j*3, y_pos), 2.5, 0.3, 
                                  facecolor=color, alpha=0.2, edgecolor=color, linewidth=1)
            ax.add_patch(access_box)
            ax.text(6.75 + j*3, y_pos + 0.15, access, 
                    fontsize=9, ha='center', fontweight='bold', color=color)
    
    # Bucket policy examples
    ax.text(11, 9.5, 'Bucket Policy Examples', fontsize=14, fontweight='bold', ha='center', color='#6f42c1')
    
    # Policy 1: Environment isolation
    policy1_box = FancyBboxPatch((1, 8), 9, 1.2, boxstyle="round,pad=0.05", 
                                facecolor='#f3e5f5', edgecolor='#6f42c1', linewidth=1)
    ax.add_patch(policy1_box)
    ax.text(5.5, 8.9, 'Environment Isolation Policy', 
            fontsize=11, ha='center', fontweight='bold', color='#6f42c1')
    
    policy1_text = '''• Deny cross-environment access
• Allow only same-environment roles
• MFA required for production buckets
• IP restrictions for sensitive data'''
    ax.text(1.5, 8.4, policy1_text, fontsize=9, color='#6f42c1', va='center')
    
    # Policy 2: Application-specific access
    policy2_box = FancyBboxPatch((11.5, 8), 9, 1.2, boxstyle="round,pad=0.05", 
                                facecolor='#e8f5e8', edgecolor='#28a745', linewidth=1)
    ax.add_patch(policy2_box)
    ax.text(16, 8.9, 'Application-Specific Access Policy', 
            fontsize=11, ha='center', fontweight='bold', color='#28a745')
    
    policy2_text = '''• App services: Read/Write to app-data buckets
• Web services: Read-only static assets
• ML services: Read/Write to ml-models
• Log aggregation: Write-only to logs'''
    ax.text(12, 8.4, policy2_text, fontsize=9, color='#28a745', va='center')
    
    # Policy 3: Data classification
    policy3_box = FancyBboxPatch((1, 6.5), 9, 1.2, boxstyle="round,pad=0.05", 
                                facecolor='#fff3cd', edgecolor='#ffc107', linewidth=1)
    ax.add_patch(policy3_box)
    ax.text(5.5, 7.4, 'Data Classification Policy', 
            fontsize=11, ha='center', fontweight='bold', color='#ffc107')
    
    policy3_text = '''• Public: Read access with authentication
• Internal: Role-based access control
• Confidential: Encrypted + restricted access
• PII: Additional logging and monitoring'''
    ax.text(1.5, 6.9, policy3_text, fontsize=9, color='#ffc107', va='center')
    
    # Policy 4: Time-based and conditional
    policy4_box = FancyBboxPatch((11.5, 6.5), 9, 1.2, boxstyle="round,pad=0.05", 
                                facecolor='#f8d7da', edgecolor='#dc3545', linewidth=1)
    ax.add_patch(policy4_box)
    ax.text(16, 7.4, 'Conditional Access Policy', 
            fontsize=11, ha='center', fontweight='bold', color='#dc3545')
    
    policy4_text = '''• Time-based: Business hours for non-prod
• Source IP: Corporate network + VPN only
• MFA: Required for admin operations
• Request logging: All access attempts logged'''
    ax.text(12, 6.9, policy4_text, fontsize=9, color='#dc3545', va='center')
    
    # Access control mechanisms
    ax.text(11, 5.8, 'Access Control Mechanisms', 
            fontsize=14, fontweight='bold', ha='center', color='#e83e8c')
    
    mechanisms = [
        {'type': 'IAM Policies', 'desc': 'User/role-based permissions', 'scope': 'AWS account level', 'priority': '1st'},
        {'type': 'Bucket Policies', 'desc': 'Resource-based permissions', 'scope': 'Individual bucket level', 'priority': '2nd'},
        {'type': 'ACLs', 'desc': 'Object-level permissions', 'scope': 'Individual object level', 'priority': '3rd'},
        {'type': 'VPC Endpoints', 'desc': 'Network-based access control', 'scope': 'VPC/subnet level', 'priority': 'Overlay'}
    ]
    
    for i, mech in enumerate(mechanisms):
        y_pos = 5.3 - i*0.3
        
        # Mechanism type
        type_box = Rectangle((2, y_pos), 2.5, 0.25, 
                            facecolor='#ffe6f2', edgecolor='#e83e8c', linewidth=1)
        ax.add_patch(type_box)
        ax.text(3.25, y_pos + 0.125, mech['type'], 
                fontsize=9, ha='center', fontweight='bold', color='#e83e8c')
        
        # Description
        ax.text(5, y_pos + 0.125, mech['desc'], fontsize=9, color='#e83e8c')
        
        # Scope
        ax.text(12, y_pos + 0.125, mech['scope'], fontsize=9, color='#666', style='italic')
        
        # Priority
        priority_box = Rectangle((17, y_pos), 1.5, 0.25, 
                                facecolor='#e83e8c', alpha=0.2, edgecolor='#e83e8c', linewidth=1)
        ax.add_patch(priority_box)
        ax.text(17.75, y_pos + 0.125, mech['priority'], 
                fontsize=9, ha='center', fontweight='bold', color='#e83e8c')
    
    # Security best practices
    best_practices_box = FancyBboxPatch((1, 2), 20, 1.5, boxstyle="round,pad=0.1", 
                                       facecolor='#d4edda', edgecolor='#28a745', linewidth=2)
    ax.add_patch(best_practices_box)
    ax.text(11, 3.2, 'S3 Security Best Practices', 
            fontsize=12, fontweight='bold', ha='center', color='#28a745')
    
    best_practices = [
        '• Principle of Least Privilege: Grant minimum required permissions',
        '• Defense in Depth: Multiple layers of access control (IAM + Bucket Policy + ACL)',
        '• Regular Access Reviews: Quarterly audit of permissions and usage patterns',
        '• Encryption at Rest: All buckets encrypted with KMS keys, environment-specific keys'
    ]
    
    for i, practice in enumerate(best_practices[:2]):
        ax.text(2, 2.8 - i*0.2, practice, fontsize=9, color='#28a745')
    for i, practice in enumerate(best_practices[2:]):
        ax.text(11.5, 2.8 - i*0.2, practice, fontsize=9, color='#28a745')
    
    # Compliance note
    ax.text(11, 0.8, 'All S3 access policies comply with SOC 2, ISO 27001, and regulatory requirements', 
            fontsize=11, ha='center', fontweight='bold', color='#0066cc',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#e3f2fd', edgecolor='#0066cc'))
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/iam_bucket_policy_access.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/iam_bucket_policy_access.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ IAM & Bucket Policy Access Control diagram generated")

def create_data_lifecycle_cross_account():
    """Generate Data Lifecycle & Cross-Account Access diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(10, 14.5, 'Data Lifecycle & Cross-Account Access', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(10, 14, 'S3 Data Management, Archiving & Partner Integration', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # Data lifecycle workflow
    ax.text(10, 13, 'Data Lifecycle Management Workflow', 
            fontsize=14, fontweight='bold', ha='center', color='#17a2b8')
    
    # Lifecycle stages
    lifecycle_stages = [
        {'stage': 'Active Data', 'days': '0-30', 'class': 'Standard', 'cost': '$0.023/GB', 'color': '#28a745', 'x': 2, 'y': 11.5},
        {'stage': 'Infrequent Access', 'days': '31-90', 'class': 'Standard-IA', 'cost': '$0.0125/GB', 'color': '#ffc107', 'x': 6, 'y': 11.5},
        {'stage': 'Archive', 'days': '91-365', 'class': 'Glacier Flexible', 'cost': '$0.004/GB', 'color': '#fd7e14', 'x': 10, 'y': 11.5},
        {'stage': 'Deep Archive', 'days': '365+', 'class': 'Glacier Deep', 'cost': '$0.00099/GB', 'color': '#6f42c1', 'x': 14, 'y': 11.5},
        {'stage': 'Deletion', 'days': '7+ years', 'class': 'Deleted', 'cost': '$0/GB', 'color': '#dc3545', 'x': 18, 'y': 11.5}
    ]
    
    for i, stage in enumerate(lifecycle_stages):
        # Stage box
        stage_box = FancyBboxPatch((stage['x'] - 1.5, stage['y']), 3, 1.5, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=stage['color'], alpha=0.2, 
                                  edgecolor=stage['color'], linewidth=2)
        ax.add_patch(stage_box)
        
        # Stage details
        ax.text(stage['x'], stage['y'] + 1.2, stage['stage'], 
                fontsize=10, ha='center', fontweight='bold', color=stage['color'])
        ax.text(stage['x'], stage['y'] + 0.9, stage['days'], 
                fontsize=9, ha='center', color=stage['color'])
        ax.text(stage['x'], stage['y'] + 0.6, stage['class'], 
                fontsize=9, ha='center', color=stage['color'], style='italic')
        ax.text(stage['x'], stage['y'] + 0.3, stage['cost'], 
                fontsize=8, ha='center', color=stage['color'], fontweight='bold')
        
        # Arrow to next stage
        if i < len(lifecycle_stages) - 1:
            arrow = ConnectionPatch((stage['x'] + 1.5, stage['y'] + 0.75), 
                                  (lifecycle_stages[i+1]['x'] - 1.5, lifecycle_stages[i+1]['y'] + 0.75), 
                                  "data", "data", arrowstyle="->", shrinkA=5, shrinkB=5, 
                                  mutation_scale=15, fc="#666", ec="#666", linewidth=2)
            ax.add_artist(arrow)
    
    # Environment-specific lifecycle policies
    ax.text(10, 9.8, 'Environment-Specific Lifecycle Policies', 
            fontsize=14, fontweight='bold', ha='center', color='#e83e8c')
    
    env_policies = [
        {'env': 'DEVELOPMENT', 'policy': 'Aggressive cleanup: 30-day retention', 'details': '• Standard → IA: 7 days\n• IA → Delete: 30 days\n• Auto-cleanup enabled', 'color': '#28a745'},
        {'env': 'UAT/STAGING', 'policy': 'Moderate retention: 90-day lifecycle', 'details': '• Standard → IA: 30 days\n• IA → Glacier: 90 days\n• Archive → Delete: 1 year', 'color': '#ffc107'},
        {'env': 'PRODUCTION', 'policy': 'Long-term retention: 7-year compliance', 'details': '• Standard → IA: 30 days\n• IA → Glacier: 90 days\n• Deep Archive: 1 year\n• Retention: 7 years', 'color': '#dc3545'}
    ]
    
    for i, env_policy in enumerate(env_policies):
        x_pos = 2 + i * 6
        
        # Environment policy box
        policy_box = FancyBboxPatch((x_pos, 8.2), 5.5, 1.3, boxstyle="round,pad=0.1", 
                                   facecolor=env_policy['color'], alpha=0.1, 
                                   edgecolor=env_policy['color'], linewidth=2)
        ax.add_patch(policy_box)
        
        ax.text(x_pos + 2.75, 9.2, env_policy['env'], 
                fontsize=11, ha='center', fontweight='bold', color=env_policy['color'])
        ax.text(x_pos + 2.75, 8.9, env_policy['policy'], 
                fontsize=9, ha='center', color=env_policy['color'], style='italic')
        ax.text(x_pos + 0.3, 8.5, env_policy['details'], 
                fontsize=8, color=env_policy['color'], va='center')
    
    # Cross-account access patterns
    ax.text(10, 7.5, 'Cross-Account Access Patterns', 
            fontsize=14, fontweight='bold', ha='center', color='#6f42c1')
    
    # Cross-account scenarios
    cross_account_box = FancyBboxPatch((1, 5.5), 18, 1.8, boxstyle="round,pad=0.1", 
                                      facecolor='#f3e5f5', edgecolor='#6f42c1', linewidth=2)
    ax.add_patch(cross_account_box)
    
    scenarios = [
        {'name': 'Partner Data Exchange', 'access': 'External → rm-shared-xaccount', 'policy': 'Assume role with MFA + IP restriction'},
        {'name': 'Vendor Analytics', 'access': 'Vendor → rm-shared-datalake', 'policy': 'Time-limited STS tokens, read-only'},
        {'name': 'Disaster Recovery', 'access': 'DR Account → All buckets', 'policy': 'Cross-region replication, emergency access'},
        {'name': 'Audit & Compliance', 'access': 'Audit Account → CloudTrail logs', 'policy': 'Read-only, comprehensive logging'}
    ]
    
    for i, scenario in enumerate(scenarios):
        y_pos = 7 - i*0.25
        ax.text(2, y_pos, f"• {scenario['name']}", fontsize=9, fontweight='bold', color='#6f42c1')
        ax.text(6, y_pos, scenario['access'], fontsize=9, color='#6f42c1', fontfamily='monospace')
        ax.text(13, y_pos, scenario['policy'], fontsize=8, color='#666', style='italic')
    
    # Data replication and backup
    ax.text(10, 4.8, 'Data Replication & Backup Strategy', 
            fontsize=14, fontweight='bold', ha='center', color='#fd7e14')
    
    replication_strategies = [
        {'type': 'Cross-Region Replication (CRR)', 'scope': 'Production buckets', 'target': 'us-west-2 (DR)', 'rpo': '< 15 min'},
        {'type': 'Same-Region Replication (SRR)', 'scope': 'Critical data', 'target': 'Different storage class', 'rpo': '< 5 min'},
        {'type': 'Point-in-Time Recovery', 'scope': 'All application data', 'target': 'Versioned storage', 'rpo': '< 1 hour'},
        {'type': 'Cross-Account Backup', 'scope': 'Compliance data', 'target': 'Dedicated backup account', 'rpo': '< 24 hours'}
    ]
    
    # Replication table headers
    headers = ['Replication Type', 'Scope', 'Target', 'RPO']
    header_x = [2, 7, 12, 16]
    for i, header in enumerate(headers):
        header_box = Rectangle((header_x[i], 4.3), 3.5, 0.3, 
                              facecolor='#fff3cd', edgecolor='#fd7e14', linewidth=1)
        ax.add_patch(header_box)
        ax.text(header_x[i] + 1.75, 4.45, header, 
                fontsize=9, ha='center', fontweight='bold', color='#fd7e14')
    
    # Replication data
    for i, strategy in enumerate(replication_strategies):
        y_pos = 4 - i*0.3
        values = [strategy['type'], strategy['scope'], strategy['target'], strategy['rpo']]
        for j, value in enumerate(values):
            value_box = Rectangle((header_x[j], y_pos), 3.5, 0.25, 
                                 facecolor='#fff8e1', edgecolor='#fd7e14', linewidth=0.5)
            ax.add_patch(value_box)
            ax.text(header_x[j] + 1.75, y_pos + 0.125, value, 
                    fontsize=8, ha='center', color='#fd7e14')
    
    # Compliance and governance
    compliance_box = FancyBboxPatch((1, 1), 18, 1.5, boxstyle="round,pad=0.1", 
                                   facecolor='#d1ecf1', edgecolor='#0c5460', linewidth=2)
    ax.add_patch(compliance_box)
    ax.text(10, 2.2, 'Data Governance & Compliance Framework', 
            fontsize=12, fontweight='bold', ha='center', color='#0c5460')
    
    governance_items = [
        'Data Retention: Automated lifecycle policies ensure compliance with regulatory requirements',
        'Access Auditing: All cross-account and lifecycle operations logged via CloudTrail',
        'Encryption Management: Environment-specific KMS keys with automated rotation',
        'Cost Optimization: Intelligent tiering reduces storage costs by up to 70%'
    ]
    
    for i, item in enumerate(governance_items[:2]):
        ax.text(2, 1.8 - i*0.2, f"• {item}", fontsize=9, color='#0c5460')
    for i, item in enumerate(governance_items[2:]):
        ax.text(2, 1.4 - i*0.2, f"• {item}", fontsize=9, color='#0c5460')
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/data_lifecycle_cross_account.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/data_lifecycle_cross_account.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ Data Lifecycle & Cross-Account Access diagram generated")

def create_s3_security_compliance():
    """Generate S3 Security & Compliance Framework diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(10, 14.5, 'S3 Security & Compliance Framework', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(10, 14, 'Encryption, Monitoring, Governance & Regulatory Compliance', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # Encryption framework
    ax.text(5, 13, 'Encryption Framework', fontsize=14, fontweight='bold', color='#dc3545')
    
    encryption_layers = [
        {'layer': 'Data at Rest', 'method': 'S3-KMS', 'key': 'Environment-specific', 'rotation': 'Annual', 'y': 12.3},
        {'layer': 'Data in Transit', 'method': 'TLS 1.3', 'key': 'SSL/HTTPS only', 'rotation': 'Certificate renewal', 'y': 11.9},
        {'layer': 'Client-Side', 'method': 'Application', 'key': 'App-managed keys', 'rotation': 'Configurable', 'y': 11.5},
        {'layer': 'Cross-Region', 'method': 'KMS Cross-Region', 'key': 'Replicated keys', 'rotation': 'Synchronized', 'y': 11.1}
    ]
    
    for enc in encryption_layers:
        # Layer box
        layer_box = Rectangle((1, enc['y']), 2, 0.3, 
                             facecolor='#f8d7da', edgecolor='#dc3545', linewidth=1)
        ax.add_patch(layer_box)
        ax.text(2, enc['y'] + 0.15, enc['layer'], 
                fontsize=9, ha='center', fontweight='bold', color='#dc3545')
        
        # Method
        ax.text(3.5, enc['y'] + 0.15, enc['method'], fontsize=9, color='#dc3545')
        
        # Key management
        ax.text(6, enc['y'] + 0.15, enc['key'], fontsize=9, color='#dc3545', style='italic')
        
        # Rotation
        ax.text(8.5, enc['y'] + 0.15, enc['rotation'], fontsize=8, color='#666')
    
    # Monitoring and alerting
    ax.text(15, 13, 'Monitoring & Alerting', fontsize=14, fontweight='bold', color='#28a745')
    
    monitoring_components = [
        {'component': 'CloudTrail', 'monitors': 'API calls, access patterns', 'alerts': 'Unusual access'},
        {'component': 'CloudWatch', 'monitors': 'Metrics, logs, performance', 'alerts': 'Threshold breaches'},
        {'component': 'GuardDuty', 'monitors': 'Threat detection, anomalies', 'alerts': 'Security threats'},
        {'component': 'Macie', 'monitors': 'PII discovery, data classification', 'alerts': 'Sensitive data exposure'}
    ]
    
    for i, monitor in enumerate(monitoring_components):
        y_pos = 12.3 - i*0.4
        
        # Component box
        comp_box = Rectangle((11, y_pos), 2, 0.3, 
                            facecolor='#d4edda', edgecolor='#28a745', linewidth=1)
        ax.add_patch(comp_box)
        ax.text(12, y_pos + 0.15, monitor['component'], 
                fontsize=9, ha='center', fontweight='bold', color='#28a745')
        
        # What it monitors
        ax.text(13.5, y_pos + 0.15, monitor['monitors'], fontsize=8, color='#28a745')
        
        # Alert triggers
        ax.text(11, y_pos - 0.1, f"→ {monitor['alerts']}", fontsize=8, color='#666', style='italic')
    
    # Security controls matrix
    ax.text(10, 10.2, 'Security Controls Matrix', 
            fontsize=14, fontweight='bold', ha='center', color='#6f42c1')
    
    # Control categories
    control_categories = [
        {'category': 'Access Control', 'controls': ['IAM Policies', 'Bucket Policies', 'ACLs', 'MFA'], 'compliance': 'SOC 2, ISO 27001'},
        {'category': 'Data Protection', 'controls': ['Encryption at Rest', 'Encryption in Transit', 'Versioning', 'Cross-Region Replication'], 'compliance': 'GDPR, CCPA'},
        {'category': 'Monitoring', 'controls': ['CloudTrail Logging', 'CloudWatch Metrics', 'GuardDuty', 'Config Rules'], 'compliance': 'PCI DSS, HIPAA'},
        {'category': 'Governance', 'controls': ['Lifecycle Policies', 'Cost Controls', 'Tagging', 'Access Reviews'], 'compliance': 'SOX, Regulatory'}
    ]
    
    for i, category in enumerate(control_categories):
        y_start = 9.5 - i*1.8
        
        # Category header
        cat_box = FancyBboxPatch((1, y_start), 18, 0.4, boxstyle="round,pad=0.05", 
                                facecolor='#6f42c1', alpha=0.2, edgecolor='#6f42c1', linewidth=2)
        ax.add_patch(cat_box)
        ax.text(10, y_start + 0.2, category['category'], 
                fontsize=11, ha='center', fontweight='bold', color='#6f42c1')
        
        # Controls
        controls_per_row = 2
        for j, control in enumerate(category['controls']):
            row = j // controls_per_row
            col = j % controls_per_row
            x_pos = 2 + col * 8
            y_pos = y_start - 0.4 - row * 0.3
            
            control_box = Rectangle((x_pos, y_pos), 7, 0.25, 
                                   facecolor='#f8f9fa', edgecolor='#6f42c1', linewidth=1)
            ax.add_patch(control_box)
            ax.text(x_pos + 3.5, y_pos + 0.125, control, 
                    fontsize=9, ha='center', color='#6f42c1')
        
        # Compliance mapping
        ax.text(16, y_start - 0.7, f"Compliance: {category['compliance']}", 
                fontsize=8, color='#666', style='italic')
    
    # Incident response workflow
    ax.text(10, 2.5, 'Security Incident Response Workflow', 
            fontsize=14, fontweight='bold', ha='center', color='#fd7e14')
    
    incident_steps = [
        {'step': '1. Detection', 'action': 'Automated alerts', 'time': '< 5 min'},
        {'step': '2. Assessment', 'action': 'Impact analysis', 'time': '< 15 min'},
        {'step': '3. Containment', 'action': 'Block access', 'time': '< 30 min'},
        {'step': '4. Investigation', 'action': 'Forensic analysis', 'time': '< 2 hours'},
        {'step': '5. Recovery', 'action': 'Restore services', 'time': '< 4 hours'}
    ]
    
    for i, step in enumerate(incident_steps):
        x_pos = 1 + i * 3.8
        
        # Step box
        step_box = FancyBboxPatch((x_pos, 1.8), 3.5, 0.6, boxstyle="round,pad=0.05", 
                                 facecolor='#fd7e14', alpha=0.2, edgecolor='#fd7e14', linewidth=1)
        ax.add_patch(step_box)
        
        ax.text(x_pos + 1.75, 2.25, step['step'], 
                fontsize=9, ha='center', fontweight='bold', color='#fd7e14')
        ax.text(x_pos + 1.75, 2, step['action'], 
                fontsize=8, ha='center', color='#fd7e14')
        ax.text(x_pos + 1.75, 1.85, step['time'], 
                fontsize=8, ha='center', color='#fd7e14', style='italic')
        
        # Arrow to next step
        if i < len(incident_steps) - 1:
            arrow = ConnectionPatch((x_pos + 3.5, 2.1), (x_pos + 3.8, 2.1), "data", "data",
                                   arrowstyle="->", shrinkA=2, shrinkB=2, mutation_scale=10, 
                                   fc="#fd7e14", ec="#fd7e14")
            ax.add_artist(arrow)
    
    # Compliance summary
    compliance_box = FancyBboxPatch((1, 0.3), 18, 0.8, boxstyle="round,pad=0.1", 
                                   facecolor='#e3f2fd', edgecolor='#0066cc', linewidth=2)
    ax.add_patch(compliance_box)
    ax.text(10, 0.9, 'Regulatory Compliance Summary', 
            fontsize=12, fontweight='bold', ha='center', color='#0066cc')
    ax.text(10, 0.5, 'All S3 security controls designed to meet SOC 2 Type II, ISO 27001, GDPR, CCPA, PCI DSS, and HIPAA requirements', 
            fontsize=10, ha='center', color='#0066cc')
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/s3_security_compliance.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/s3_security_compliance.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ S3 Security & Compliance Framework diagram generated")

def create_documentation():
    """Create comprehensive documentation for S3 bucket policies and access control"""
    doc_content = f"""# S3 Bucket Policies & Access Control Diagrams

*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

This document provides comprehensive analysis of the S3 bucket policies and access control diagrams for the Risk Management Platform infrastructure.

## Overview

The S3 bucket policies and access control diagrams illustrate the comprehensive storage architecture, security framework, and data management strategies implemented across all environments. These diagrams demonstrate enterprise-grade storage security with multi-layered access controls and automated governance.

## Generated Diagrams

### 1. S3 Storage Architecture & Organization
**File**: `s3_storage_architecture.png/.svg`

This diagram shows the complete S3 bucket structure and organization strategy across environments.

**Bucket Organization Strategy**:
- **Environment Isolation**: Separate bucket sets for DEV, UAT, and PROD environments
- **Functional Separation**: Distinct buckets for applications, static assets, logs, backups, documents, and ML models
- **Shared Services**: Centralized buckets for cross-environment services like CloudTrail, Config, and disaster recovery
- **Naming Convention**: Consistent `rm-{{environment}}-{{service}}-{{purpose}}` pattern

**Storage Classes & Lifecycle**:
- **Standard**: Active data with frequent access (< 30 days)
- **Standard-IA**: Infrequent access and backup data (30-90 days)
- **Glacier Flexible**: Archive and compliance data (90 days - 1 year)
- **Glacier Deep Archive**: Long-term retention (> 1 year)

### 2. IAM & Bucket Policy Access Control
**File**: `iam_bucket_policy_access.png/.svg`

Comprehensive access control matrix showing how IAM roles and bucket policies work together to enforce security.

**Access Control Matrix**:
- **Developer Role**: Full DEV access, read-only UAT, no PROD access
- **QA Tester Role**: Read-only DEV, full UAT access, no PROD access
- **DevOps Role**: Deployment access to all environments via automation
- **Application Service Role**: Read/write access to application-specific buckets
- **Analytics Role**: Data lake access with read permissions to production analytics
- **Backup Service**: Automated backup access across all environments

**Policy Types**:
1. **Environment Isolation**: Cross-environment access restrictions with MFA requirements
2. **Application-Specific**: Service-based permissions for different application components
3. **Data Classification**: Access controls based on public, internal, and confidential data
4. **Conditional Access**: Time-based, IP-restricted, and MFA-required access patterns

### 3. Data Lifecycle & Cross-Account Access
**File**: `data_lifecycle_cross_account.png/.svg`

Automated data lifecycle management and cross-account sharing patterns for partner integration.

**Lifecycle Management**:
- **Development**: Aggressive 30-day retention with auto-cleanup
- **UAT/Staging**: Moderate 90-day lifecycle with archival policies
- **Production**: 7-year compliance retention with full lifecycle automation

**Cross-Account Patterns**:
- **Partner Data Exchange**: Secure external partner access via assumed roles
- **Vendor Analytics**: Time-limited access tokens for third-party analytics
- **Disaster Recovery**: Cross-region and cross-account replication strategies
- **Audit & Compliance**: Dedicated audit account access for compliance reviews

**Replication Strategy**:
- **Cross-Region Replication (CRR)**: Production data replicated to DR region
- **Same-Region Replication (SRR)**: Critical data replicated to different storage classes
- **Point-in-Time Recovery**: Versioned storage for application data recovery
- **Cross-Account Backup**: Compliance data backed up to dedicated backup accounts

### 4. S3 Security & Compliance Framework
**File**: `s3_security_compliance.png/.svg`

Complete security and compliance framework covering encryption, monitoring, and governance.

**Encryption Framework**:
- **Data at Rest**: S3-KMS encryption with environment-specific keys
- **Data in Transit**: TLS 1.3 encryption for all data transfers
- **Client-Side**: Application-managed encryption for sensitive workloads
- **Cross-Region**: KMS key replication for disaster recovery scenarios

**Monitoring & Alerting**:
- **CloudTrail**: API call logging and access pattern analysis
- **CloudWatch**: Performance metrics and threshold-based alerting
- **GuardDuty**: Threat detection and anomaly identification
- **Macie**: PII discovery and data classification automation

**Security Controls Matrix**:
1. **Access Control**: IAM policies, bucket policies, ACLs, and MFA requirements
2. **Data Protection**: Encryption, versioning, and cross-region replication
3. **Monitoring**: Comprehensive logging, metrics, and threat detection
4. **Governance**: Lifecycle policies, cost controls, tagging, and access reviews

## Security Architecture Implementation

### Multi-Layered Security Approach
The S3 security architecture implements defense-in-depth principles:

1. **Network Layer**: VPC endpoints and network-based access restrictions
2. **Identity Layer**: IAM policies with role-based access control
3. **Resource Layer**: Bucket policies with fine-grained permissions
4. **Object Layer**: ACLs and object-level security controls
5. **Data Layer**: Encryption at rest and in transit
6. **Monitoring Layer**: Comprehensive logging and threat detection

### Access Control Hierarchy
Security controls are evaluated in the following order:
1. **IAM Policies**: Account-level user and role permissions (highest priority)
2. **Bucket Policies**: Resource-based bucket-level permissions
3. **ACLs**: Legacy object-level permissions (lowest priority)
4. **VPC Endpoints**: Network-based access overlay controls

### Data Classification Framework
All S3 data is classified according to sensitivity levels:

- **Public**: Publicly accessible data with authentication requirements
- **Internal**: Company-internal data with role-based access controls
- **Confidential**: Sensitive data requiring encryption and restricted access
- **PII**: Personally identifiable information with additional logging and monitoring

## Operational Procedures

### Bucket Management
1. **Bucket Creation**: Automated via Infrastructure as Code (Terraform)
2. **Policy Assignment**: Environment-specific policies applied automatically
3. **Access Reviews**: Quarterly review of bucket permissions and usage
4. **Cost Optimization**: Automated lifecycle policies to manage storage costs

### Data Lifecycle Management
1. **Automated Transitions**: Data automatically moved between storage classes
2. **Retention Policies**: Environment-specific retention rules enforced
3. **Deletion Procedures**: Secure deletion with compliance verification
4. **Archive Management**: Long-term archival with retrieval procedures

### Security Monitoring
1. **Real-Time Alerts**: Immediate notification of security events
2. **Access Logging**: Comprehensive logging of all bucket access attempts
3. **Anomaly Detection**: Machine learning-based unusual activity detection
4. **Incident Response**: Automated containment and notification procedures

### Cross-Account Operations
1. **Partner Onboarding**: Secure process for granting external access
2. **Token Management**: Time-limited credentials with automatic rotation
3. **Audit Trail**: Complete logging of all cross-account activities
4. **Access Revocation**: Immediate capability to revoke external access

## Compliance and Governance

### Regulatory Compliance
The S3 architecture meets requirements for:

- **SOC 2 Type II**: Security, availability, and confidentiality controls
- **ISO 27001**: Information security management system requirements
- **GDPR**: Data protection and privacy requirements for EU data
- **CCPA**: California Consumer Privacy Act compliance for personal data
- **PCI DSS**: Payment card industry data security standards
- **HIPAA**: Healthcare data protection requirements (where applicable)

### Data Governance Framework
1. **Data Classification**: Automated classification based on content analysis
2. **Access Governance**: Role-based access with regular reviews
3. **Retention Management**: Automated retention policy enforcement
4. **Cost Governance**: Budget controls and cost allocation tracking

### Audit and Reporting
1. **Access Reports**: Daily reports on bucket access patterns
2. **Compliance Dashboards**: Real-time compliance posture visualization
3. **Cost Reports**: Monthly cost breakdowns by environment and service
4. **Security Reports**: Weekly security posture and threat analysis

## Best Practices Implementation

### Security Best Practices
1. **Principle of Least Privilege**: Minimum required permissions granted
2. **Defense in Depth**: Multiple security layers implemented
3. **Zero Trust**: No implicit trust between services or environments
4. **Continuous Monitoring**: Real-time security monitoring and alerting

### Performance Optimization
1. **Intelligent Tiering**: Automatic optimization of storage costs
2. **Transfer Acceleration**: Optimized data transfer for global access
3. **Multi-Part Uploads**: Efficient handling of large file uploads
4. **CloudFront Integration**: CDN integration for static asset delivery

### Cost Management
1. **Lifecycle Policies**: Automated storage class transitions
2. **Usage Monitoring**: Regular analysis of storage usage patterns
3. **Cost Alerts**: Proactive notifications for budget thresholds
4. **Resource Tagging**: Detailed cost allocation and tracking

## Disaster Recovery and Business Continuity

### Backup Strategy
1. **Cross-Region Replication**: Automated replication to disaster recovery regions
2. **Point-in-Time Recovery**: Versioning and deletion protection enabled
3. **Cross-Account Backup**: Critical data backed up to separate accounts
4. **Recovery Testing**: Regular testing of backup and recovery procedures

### High Availability
1. **Multi-AZ Design**: Data distributed across multiple availability zones
2. **Automatic Failover**: Seamless failover for critical applications
3. **Performance Monitoring**: Continuous monitoring of availability metrics
4. **Capacity Planning**: Proactive capacity management and scaling

---

*This documentation is automatically updated when infrastructure diagrams are regenerated. For technical questions or clarifications, contact the Platform Security Team.*
"""

    with open('../docs/s3_bucket_policies_implementation.md', 'w') as f:
        f.write(doc_content)
    
    print("📖 S3 Bucket Policies & Access Control documentation created")

def main():
    """Main function to generate all S3 bucket policies and access control diagrams"""
    print("🚀 Starting S3 Bucket Policies & Access Control diagram generation...")
    print("=" * 80)
    
    try:
        # Setup
        setup_directories()
        
        # Generate all diagrams
        create_s3_storage_architecture()
        create_iam_bucket_policy_access()
        create_data_lifecycle_cross_account()
        create_s3_security_compliance()
        
        # Create documentation
        create_documentation()
        
        print("=" * 80)
        print("✅ S3 Bucket Policies & Access Control diagrams completed successfully!")
        print("\nGenerated Files:")
        print("📊 4 diagrams (PNG + SVG formats)")
        print("📖 1 comprehensive documentation file")
        print("\nAll files saved to:")
        print("- Diagrams: docs/architecture/")
        print("- Documentation: docs/s3_bucket_policies_implementation.md")
        
    except Exception as e:
        print(f"❌ Error generating diagrams: {str(e)}")
        raise

if __name__ == "__main__":
    main()