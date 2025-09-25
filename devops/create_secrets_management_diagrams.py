#!/usr/bin/env python3
"""
Parameter Store and Secrets Management Diagrams Generator

This script creates comprehensive visual diagrams for secrets and configuration management including:
1. Parameter Store hierarchy and access patterns
2. Secrets Manager integration and lifecycle
3. Application secrets workflow and retrieval
4. Security and compliance controls for sensitive data

Generated diagrams help understand secrets management architecture and security patterns.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Rectangle, Circle, Ellipse
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

def create_secure_box(ax, x, y, width, height, text, security_level='high'):
    """Create a security-themed box with appropriate styling"""
    colors = {
        'high': '#FFB6B6',     # Light red for high security
        'medium': '#FFFACD',   # Light yellow for medium security
        'low': '#E0FFE0'       # Light green for low security
    }
    border_colors = {
        'high': 'darkred',
        'medium': 'darkorange', 
        'low': 'darkgreen'
    }
    
    create_fancy_box(ax, x, y, width, height, text, colors[security_level], 
                    'black', border_colors[security_level], 3)

def create_parameter_store_hierarchy():
    """Create Parameter Store hierarchy and access patterns diagram"""
    print("Creating Parameter Store hierarchy and access patterns diagram...")
    
    # Create figure with high DPI for better quality
    fig, ax = plt.subplots(1, 1, figsize=(20, 16), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Title
    ax.text(50, 95, 'AWS Parameter Store Hierarchy & Access Patterns', fontsize=24, weight='bold', 
            ha='center', va='center')
    ax.text(50, 92, 'Configuration Management and Secrets Organization', fontsize=14, 
            ha='center', va='center', style='italic')
    
    # Color scheme
    colors = {
        'parameter_store': '#87CEEB',  # Sky blue
        'env_config': '#98FB98',       # Pale green
        'app_config': '#DDA0DD',       # Plum
        'secrets': '#FFB6C1',          # Light pink
        'system': '#F0E68C'            # Khaki
    }
    
    # Parameter Store Service (Center)
    create_fancy_box(ax, 40, 75, 20, 10, 'AWS Systems Manager\nParameter Store\n\nHierarchical Configuration\nSecure Storage', 
                    colors['parameter_store'], 'black', 'black', 3)
    
    # Environment-based Parameter Organization (Left Side)
    ax.text(15, 85, 'ENVIRONMENT HIERARCHY', fontsize=16, weight='bold')
    
    environments = [
        ('Development', '/mono-repo/dev/', 5, 70),
        ('UAT', '/mono-repo/uat/', 5, 60), 
        ('Production', '/mono-repo/prod/', 5, 50)
    ]
    
    for env_name, path, x, y in environments:
        create_fancy_box(ax, x, y, 25, 8, f'{env_name} Environment\n{path}*', 
                        colors['env_config'], 'black', 'black', 2)
        
        # Connection to Parameter Store
        create_arrow(ax, x + 25, y + 4, 40, 80, colors['env_config'], '->', 2)
    
    # Application Parameter Categories (Right Side)  
    ax.text(80, 85, 'APPLICATION CATEGORIES', fontsize=16, weight='bold')
    
    app_categories = [
        ('Database Config', '/mono-repo/*/database/', 70, 70, 'medium'),
        ('API Keys', '/mono-repo/*/api/', 70, 62, 'high'),
        ('Feature Flags', '/mono-repo/*/features/', 70, 54, 'low'),
        ('Service URLs', '/mono-repo/*/services/', 70, 46, 'low')
    ]
    
    for cat_name, path, x, y, security in app_categories:
        create_secure_box(ax, x, y, 25, 6, f'{cat_name}\n{path}*', security)
        
        # Connection to Parameter Store
        create_arrow(ax, x, y + 3, 60, 80, colors['app_config'], '->', 2)
    
    # Parameter Types and Examples (Bottom Left)
    create_fancy_box(ax, 5, 25, 40, 18,
                    'PARAMETER TYPES & EXAMPLES\n\n' +
                    'String Parameters:\n' +
                    '• /mono-repo/prod/database/host\n' +
                    '• /mono-repo/prod/services/api-url\n' +
                    '• /mono-repo/*/features/risk-analysis-v2\n\n' +
                    'StringList Parameters:\n' +
                    '• /mono-repo/prod/allowed-origins\n' +
                    '• /mono-repo/*/notification-emails\n\n' +
                    'SecureString Parameters (KMS Encrypted):\n' +
                    '• /mono-repo/prod/database/password\n' +
                    '• /mono-repo/prod/api/external-service-key\n' +
                    '• /mono-repo/*/jwt/signing-key',
                    colors['system'], 'black', 'black', 2)
    
    # Access Patterns and Retrieval (Bottom Right)
    create_fancy_box(ax, 55, 25, 40, 18,
                    'ACCESS PATTERNS & RETRIEVAL\n\n' +
                    'Application Startup:\n' +
                    '• Bulk parameter retrieval by path\n' +
                    '• Environment-specific configuration\n' +
                    '• Cached values with TTL\n\n' +
                    'Runtime Configuration:\n' +
                    '• Feature flag updates\n' +
                    '• Dynamic service discovery\n' +
                    '• A/B testing parameters\n\n' +
                    'Security Considerations:\n' +
                    '• IAM policy-based access control\n' +
                    '• KMS encryption for sensitive data\n' +
                    '• CloudTrail audit logging\n' +
                    '• Parameter versioning',
                    colors['secrets'], 'black', 'darkred', 2)
    
    # Parameter Store Benefits (Bottom Center)
    create_fancy_box(ax, 25, 5, 50, 15,
                    'PARAMETER STORE BENEFITS\n\n' +
                    'Cost Effective: Standard parameters free (up to 10,000)\n' +
                    'Hierarchical Organization: Path-based parameter grouping\n' +
                    'Version Control: Parameter history and rollback capability\n' +
                    'Secure Storage: KMS integration for sensitive parameters\n' +
                    'Fine-grained Access: IAM policy-based parameter access\n' +
                    'CloudFormation Integration: Infrastructure as Code support\n' +
                    'Cross-Region Replication: Multi-region parameter availability',
                    '#F0F8FF', 'black', 'navy', 2)
    
    plt.tight_layout()
    return fig

def create_secrets_manager_integration():
    """Create Secrets Manager integration and lifecycle diagram"""
    print("Creating Secrets Manager integration and lifecycle diagram...")
    
    fig, ax = plt.subplots(1, 1, figsize=(18, 14), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Title
    ax.text(50, 95, 'AWS Secrets Manager Integration & Lifecycle', fontsize=24, weight='bold', 
            ha='center', va='center')
    ax.text(50, 92, 'Automated Secrets Rotation and Management', fontsize=14, 
            ha='center', va='center', style='italic')
    
    # Color scheme
    colors = {
        'secrets_manager': '#FF6B6B',  # Red for secrets
        'rotation': '#4ECDC4',         # Teal for rotation
        'application': '#45B7D1',      # Blue for applications
        'database': '#96CEB4',         # Green for database
        'monitoring': '#FFEAA7'        # Yellow for monitoring
    }
    
    # Secrets Manager Service (Center)
    create_fancy_box(ax, 40, 70, 20, 15, 'AWS Secrets Manager\n\nAutomated Rotation\nVersioned Secrets\nKMS Encryption\nFine-grained Access', 
                    colors['secrets_manager'], 'white', 'darkred', 3)
    
    # Database Secrets (Left)
    database_secrets = [
        ('RDS Master Password', 'PostgreSQL Admin', 10, 80),
        ('RDS Read Replica', 'Read-only Access', 10, 72),
        ('Application User', 'App Database User', 10, 64)
    ]
    
    for secret_name, desc, x, y in database_secrets:
        create_secure_box(ax, x, y, 20, 6, f'{secret_name}\n{desc}', 'high')
        create_arrow(ax, x + 20, y + 3, 40, 77, colors['database'], '->', 2)
    
    # Application Secrets (Right)
    app_secrets = [
        ('API Keys', 'External Service Keys', 70, 80),
        ('JWT Signing Key', 'Token Authentication', 70, 72),
        ('Encryption Keys', 'Data Encryption', 70, 64)
    ]
    
    for secret_name, desc, x, y in app_secrets:
        create_secure_box(ax, x, y, 20, 6, f'{secret_name}\n{desc}', 'high')
        create_arrow(ax, x, y + 3, 60, 77, colors['application'], '->', 2)
    
    # Rotation Process (Bottom)
    ax.text(50, 55, 'AUTOMATED ROTATION LIFECYCLE', fontsize=16, weight='bold', ha='center')
    
    # Rotation workflow steps
    rotation_steps = [
        ('Create New\nVersion', 15, 45, colors['rotation']),
        ('Test New\nSecret', 30, 45, colors['rotation']),
        ('Update\nApplications', 45, 45, colors['application']),
        ('Finalize\nRotation', 60, 45, colors['rotation']),
        ('Delete Old\nVersion', 75, 45, colors['rotation'])
    ]
    
    step_positions = []
    for step_name, x, y, color in rotation_steps:
        create_fancy_box(ax, x-5, y, 10, 6, step_name, color, 'black', 'black', 2)
        step_positions.append((x, y+3))
    
    # Draw rotation flow arrows
    for i in range(len(step_positions)-1):
        create_arrow(ax, step_positions[i][0]+5, step_positions[i][1], 
                    step_positions[i+1][0]-5, step_positions[i+1][1], 'purple', '->', 2)
    
    # Rotation Configuration
    create_fancy_box(ax, 5, 25, 40, 15,
                    'ROTATION CONFIGURATION\n\n' +
                    'Database Secrets:\n' +
                    '• Rotation Interval: 30 days\n' +
                    '• Lambda Function: Custom RDS rotator\n' +
                    '• Test Connection: Automated validation\n\n' +
                    'API Keys:\n' +
                    '• Rotation Interval: 90 days\n' +
                    '• Custom Lambda: Service-specific logic\n' +
                    '• Rollback: Automatic on failure\n\n' +
                    'Encryption Keys:\n' +
                    '• Rotation Interval: 365 days\n' +
                    '• Key Versioning: Multiple active versions',
                    colors['monitoring'], 'black', 'darkorange', 2)
    
    # Security & Compliance
    create_fancy_box(ax, 55, 25, 40, 15,
                    'SECURITY & COMPLIANCE\n\n' +
                    'Access Control:\n' +
                    '• IAM policies: Resource-based access\n' +
                    '• Resource policies: Cross-account access\n' +
                    '• VPC Endpoints: Private network access\n\n' +
                    'Audit & Monitoring:\n' +
                    '• CloudTrail: All API calls logged\n' +
                    '• CloudWatch: Rotation success/failure\n' +
                    '• Config Rules: Compliance validation\n\n' +
                    'Encryption:\n' +
                    '• KMS: Customer-managed keys\n' +
                    '• In-transit: TLS 1.2 minimum',
                    colors['secrets_manager'], 'white', 'darkred', 2)
    
    # Cost Optimization
    create_fancy_box(ax, 25, 5, 50, 15,
                    'COST OPTIMIZATION STRATEGIES\n\n' +
                    'Pricing Model: $0.40/secret/month + $0.05/10,000 API calls\n\n' +
                    'Optimization Techniques:\n' +
                    '• Consolidate related secrets into single secret with JSON values\n' +
                    '• Use Parameter Store for non-sensitive configuration\n' +
                    '• Implement client-side caching with appropriate TTL\n' +
                    '• Batch secret retrieval where possible\n' +
                    '• Monitor API call patterns and optimize retrieval frequency\n\n' +
                    'Current Usage: ~15 secrets × $0.40 = $6/month base cost',
                    '#F0FFF0', 'black', 'darkgreen', 2)
    
    plt.tight_layout()
    return fig

def create_application_secrets_workflow():
    """Create Application secrets workflow and retrieval diagram"""
    print("Creating Application secrets workflow and retrieval diagram...")
    
    fig, ax = plt.subplots(1, 1, figsize=(20, 14), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Title
    ax.text(50, 95, 'Application Secrets Workflow & Retrieval', fontsize=24, weight='bold', 
            ha='center', va='center')
    ax.text(50, 92, 'Runtime Secrets Management and Security Integration', fontsize=14, 
            ha='center', va='center', style='italic')
    
    # Color scheme
    colors = {
        'app': '#45B7D1',        # Blue for applications
        'secrets': '#FF6B6B',    # Red for secrets
        'cache': '#96CEB4',      # Green for caching
        'security': '#FFEAA7',   # Yellow for security
        'workflow': '#DDA0DD'    # Purple for workflow
    }
    
    # Application Services (Top)
    services = [
        ('Web App', 'React Frontend\nPort 3000', 10, 80),
        ('Risk API', 'FastAPI Backend\nPort 8000', 30, 80),
        ('Dash Analytics', 'Python Dashboard\nPort 8050', 50, 80),
        ('Airflow', 'Workflow Engine\nPort 8080', 70, 80)
    ]
    
    service_positions = {}
    for service_name, desc, x, y in services:
        create_fancy_box(ax, x, y, 15, 8, f'{service_name}\n{desc}', colors['app'], 'white', 'darkblue', 2)
        service_positions[service_name] = (x + 7.5, y)
    
    # Secrets Sources (Middle)
    ax.text(50, 65, 'SECRETS SOURCES', fontsize=16, weight='bold', ha='center')
    
    secrets_sources = [
        ('Parameter Store', 'Configuration\nNon-sensitive', 15, 55),
        ('Secrets Manager', 'Sensitive Data\nRotated Secrets', 45, 55),
        ('Environment Variables', 'Container Secrets\nRuntime Config', 75, 55)
    ]
    
    source_positions = {}
    for source_name, desc, x, y in secrets_sources:
        create_fancy_box(ax, x-7.5, y, 15, 8, f'{source_name}\n{desc}', colors['secrets'], 'white', 'darkred', 2)
        source_positions[source_name] = (x, y)
    
    # Draw connections from applications to secrets sources
    connections = [
        ('Web App', 'Parameter Store'),
        ('Web App', 'Environment Variables'),
        ('Risk API', 'Secrets Manager'),
        ('Risk API', 'Parameter Store'),
        ('Dash Analytics', 'Parameter Store'),
        ('Dash Analytics', 'Secrets Manager'),
        ('Airflow', 'Secrets Manager'),
        ('Airflow', 'Parameter Store')
    ]
    
    for app, source in connections:
        app_x, app_y = service_positions[app]
        source_x, source_y = source_positions[source]
        create_arrow(ax, app_x, app_y, source_x, source_y + 8, colors['workflow'], '->', 1.5)
    
    # Secrets Retrieval Workflow (Bottom Left)
    create_fancy_box(ax, 5, 30, 40, 20,
                    'SECRETS RETRIEVAL WORKFLOW\n\n' +
                    '1. Application Startup:\n' +
                    '   • Load environment-specific config\n' +
                    '   • Retrieve secrets via IAM role\n' +
                    '   • Initialize connection pools\n\n' +
                    '2. Runtime Access:\n' +
                    '   • Check local cache first\n' +
                    '   • Fetch if expired or missing\n' +
                    '   • Update cache with TTL\n\n' +
                    '3. Secrets Rotation:\n' +
                    '   • Receive rotation notification\n' +
                    '   • Refresh cached secrets\n' +
                    '   • Graceful connection refresh\n\n' +
                    '4. Error Handling:\n' +
                    '   • Retry with exponential backoff\n' +
                    '   • Use cached values if available\n' +
                    '   • Alert on persistent failures',
                    colors['workflow'], 'black', 'purple', 2)
    
    # Security Best Practices (Bottom Right)
    create_fancy_box(ax, 55, 30, 40, 20,
                    'SECURITY BEST PRACTICES\n\n' +
                    'Access Control:\n' +
                    '• IAM roles for service authentication\n' +
                    '• Principle of least privilege\n' +
                    '• Resource-based policies\n\n' +
                    'Data Protection:\n' +
                    '• Never log sensitive values\n' +
                    '• Memory-safe secret handling\n' +
                    '• Secure disposal of secret data\n\n' +
                    'Network Security:\n' +
                    '• VPC endpoints for AWS services\n' +
                    '• TLS encryption in transit\n' +
                    '• Private subnet deployment\n\n' +
                    'Monitoring:\n' +
                    '• CloudTrail for access logging\n' +
                    '• CloudWatch for performance\n' +
                    '• Custom metrics for secret usage',
                    colors['security'], 'black', 'darkorange', 2)
    
    # Caching Strategy (Bottom Center)
    create_fancy_box(ax, 25, 5, 50, 20,
                    'SECRETS CACHING STRATEGY\n\n' +
                    'Cache Tiers:\n' +
                    '• Application Memory: 5-15 minute TTL\n' +
                    '• Redis Cache: 30-60 minute TTL (optional)\n' +
                    '• AWS API: Always available fallback\n\n' +
                    'Cache Invalidation:\n' +
                    '• Time-based expiration\n' +
                    '• Manual invalidation via API\n' +
                    '• Rotation-triggered refresh\n\n' +
                    'Performance Benefits:\n' +
                    '• Reduced API calls (cost savings)\n' +
                    '• Lower latency (< 1ms vs 50ms)\n' +
                    '• Improved reliability\n\n' +
                    'Implementation:\n' +
                    '• Python: boto3 with local caching\n' +
                    '• Node.js: AWS SDK with TTL cache\n' +
                    '• Container: Init container pattern',
                    colors['cache'], 'black', 'darkgreen', 2)
    
    plt.tight_layout()
    return fig

def create_security_compliance_controls():
    """Create Security and compliance controls for sensitive data diagram"""
    print("Creating Security and compliance controls for sensitive data diagram...")
    
    fig, ax = plt.subplots(1, 1, figsize=(18, 16), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Title
    ax.text(50, 95, 'Security & Compliance Controls for Sensitive Data', fontsize=24, weight='bold', 
            ha='center', va='center')
    ax.text(50, 92, 'Comprehensive Data Protection and Regulatory Compliance', fontsize=14, 
            ha='center', va='center', style='italic')
    
    # Color scheme
    colors = {
        'encryption': '#FF6B6B',   # Red for encryption
        'access': '#45B7D1',       # Blue for access control
        'audit': '#96CEB4',        # Green for audit
        'compliance': '#FFEAA7',   # Yellow for compliance
        'monitoring': '#DDA0DD'    # Purple for monitoring
    }
    
    # Security Layers (Center - Layered Circles)
    ax.text(50, 85, 'DEFENSE IN DEPTH SECURITY MODEL', fontsize=16, weight='bold', ha='center')
    
    # Draw concentric security circles
    security_layers = [
        ('Data at Rest Encryption\n(KMS)', 50, 70, 20, colors['encryption']),
        ('Data in Transit\n(TLS 1.3)', 50, 70, 15, colors['encryption']),
        ('IAM Access Control\n(RBAC)', 50, 70, 10, colors['access']),
        ('Application Security\n(Auth)', 50, 70, 5, colors['access'])
    ]
    
    for layer_name, cx, cy, radius, color in security_layers:
        circle = Circle((cx, cy), radius, facecolor=color, alpha=0.3, edgecolor='black', linewidth=2)
        ax.add_patch(circle)
        
        # Add layer labels
        if radius == 20:
            ax.text(cx, cy + radius - 3, layer_name, ha='center', va='center', fontsize=10, weight='bold')
        elif radius == 15:
            ax.text(cx - radius + 5, cy, layer_name, ha='center', va='center', fontsize=10, weight='bold')
        elif radius == 10:
            ax.text(cx + radius - 5, cy, layer_name, ha='center', va='center', fontsize=10, weight='bold')
        else:
            ax.text(cx, cy, layer_name, ha='center', va='center', fontsize=10, weight='bold')
    
    # Encryption Controls (Left Side)
    create_fancy_box(ax, 5, 60, 35, 20,
                    'ENCRYPTION CONTROLS\n\n' +
                    'AWS KMS Integration:\n' +
                    '• Customer-managed keys (CMK)\n' +
                    '• Automatic key rotation (annual)\n' +
                    '• Cross-region key replication\n' +
                    '• Hardware Security Modules (HSM)\n\n' +
                    'Encryption at Rest:\n' +
                    '• Parameter Store: SecureString type\n' +
                    '• Secrets Manager: KMS encryption\n' +
                    '• RDS: Encrypted storage volumes\n' +
                    '• EKS: Secrets encryption\n\n' +
                    'Encryption in Transit:\n' +
                    '• TLS 1.3 minimum version\n' +
                    '• Certificate management (ACM)\n' +
                    '• VPC Endpoints: Private connectivity\n' +
                    '• Application-level encryption',
                    colors['encryption'], 'white', 'darkred', 3)
    
    # Access Control (Right Side)
    create_fancy_box(ax, 60, 60, 35, 20,
                    'ACCESS CONTROL FRAMEWORK\n\n' +
                    'IAM Policies:\n' +
                    '• Resource-based policies\n' +
                    '• Condition-based access\n' +
                    '• Time-based restrictions\n' +
                    '• IP address limitations\n\n' +
                    'Service Roles:\n' +
                    '• EKS Pod Identity (IRSA)\n' +
                    '• Lambda execution roles\n' +
                    '• EC2 instance profiles\n' +
                    '• Cross-account access\n\n' +
                    'Multi-Factor Authentication:\n' +
                    '• AWS Console access\n' +
                    '• CLI/API access\n' +
                    '• Administrative operations\n' +
                    '• Emergency access procedures',
                    colors['access'], 'white', 'darkblue', 3)
    
    # Audit and Monitoring (Left Bottom)
    create_fancy_box(ax, 5, 30, 40, 25,
                    'AUDIT & MONITORING CONTROLS\n\n' +
                    'CloudTrail Integration:\n' +
                    '• All API calls logged\n' +
                    '• Parameter/Secret access tracking\n' +
                    '• Cross-region log aggregation\n' +
                    '• Log file integrity validation\n\n' +
                    'CloudWatch Monitoring:\n' +
                    '• Failed access attempts\n' +
                    '• Unusual access patterns\n' +
                    '• Secret rotation failures\n' +
                    '• Performance metrics\n\n' +
                    'Security Hub Integration:\n' +
                    '• Compliance posture monitoring\n' +
                    '• Security finding aggregation\n' +
                    '• Custom security standards\n' +
                    '• Automated remediation\n\n' +
                    'GuardDuty Detection:\n' +
                    '• Anomalous API usage\n' +
                    '• Credential compromise detection\n' +
                    '• Machine learning-based alerts',
                    colors['audit'], 'black', 'darkgreen', 2)
    
    # Compliance Framework (Right Bottom)
    create_fancy_box(ax, 55, 30, 40, 25,
                    'COMPLIANCE FRAMEWORK\n\n' +
                    'Regulatory Standards:\n' +
                    '• SOC 2 Type II compliance\n' +
                    '• ISO 27001 information security\n' +
                    '• GDPR data protection\n' +
                    '• Industry-specific requirements\n\n' +
                    'Data Classification:\n' +
                    '• Public: Marketing content\n' +
                    '• Internal: Business data\n' +
                    '• Confidential: Customer data\n' +
                    '• Restricted: Financial/PII data\n\n' +
                    'Retention Policies:\n' +
                    '• Secret version history: 90 days\n' +
                    '• Audit logs: 7 years\n' +
                    '• Backup retention: 5 years\n' +
                    '• Legal hold procedures\n\n' +
                    'Privacy Controls:\n' +
                    '• Data anonymization\n' +
                    '• Right to deletion\n' +
                    '• Consent management\n' +
                    '• Cross-border data transfer',
                    colors['compliance'], 'black', 'darkorange', 2)
    
    # Incident Response (Bottom Center)
    create_fancy_box(ax, 25, 5, 50, 20,
                    'INCIDENT RESPONSE PROCEDURES\n\n' +
                    'Security Incident Types:\n' +
                    '• Unauthorized access attempts\n' +
                    '• Credential compromise\n' +
                    '• Data exfiltration attempts\n' +
                    '• Service disruption attacks\n\n' +
                    'Response Procedures:\n' +
                    '• Immediate containment (< 30 minutes)\n' +
                    '• Affected system isolation\n' +
                    '• Forensic data collection\n' +
                    '• Stakeholder notification\n\n' +
                    'Recovery Actions:\n' +
                    '• Secret rotation (emergency)\n' +
                    '• Access revocation\n' +
                    '• System remediation\n' +
                    '• Service restoration\n\n' +
                    'Post-Incident:\n' +
                    '• Root cause analysis\n' +
                    '• Security control improvements\n' +
                    '• Compliance reporting\n' +
                    '• Lessons learned documentation',
                    colors['monitoring'], 'black', 'purple', 2)
    
    plt.tight_layout()
    return fig

def create_documentation_summary():
    """Create comprehensive documentation summary"""
    return f"""# Parameter Store and Secrets Management Diagrams Documentation

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This document accompanies the visual diagrams created to illustrate the comprehensive secrets and configuration management architecture, including AWS Parameter Store, Secrets Manager integration, application workflows, and security compliance controls.

## Generated Diagrams

### 1. Parameter Store Hierarchy & Access Patterns (`parameter_store_hierarchy`)
**Purpose**: Complete parameter organization and retrieval patterns for configuration management

**Hierarchical Organization**:
- **Environment-based**: `/mono-repo/dev/`, `/mono-repo/uat/`, `/mono-repo/prod/`
- **Application Categories**: Database config, API keys, feature flags, service URLs
- **Parameter Types**: String, StringList, SecureString (KMS encrypted)

**Access Patterns**:
- **Startup**: Bulk parameter retrieval by path
- **Runtime**: Dynamic configuration updates
- **Security**: IAM policy-based access control

### 2. Secrets Manager Integration & Lifecycle (`secrets_manager_integration`)
**Purpose**: Automated secrets rotation and secure secrets management

**Secrets Categories**:
- **Database Secrets**: RDS master password, read replica credentials
- **Application Secrets**: API keys, JWT signing keys, encryption keys
- **Rotation Lifecycle**: Create → Test → Update → Finalize → Delete

**Integration Features**:
- **Automated Rotation**: 30-90 day intervals
- **Lambda Functions**: Custom rotation logic
- **Version Management**: Multiple active secret versions

### 3. Application Secrets Workflow & Retrieval (`application_secrets_workflow`)
**Purpose**: Runtime secrets management and application integration patterns

**Services Integration**:
- **Web App**: React frontend with environment configuration
- **Risk API**: FastAPI backend with database and API secrets
- **Dash Analytics**: Python dashboard with data source credentials
- **Airflow**: Workflow engine with service integrations

**Retrieval Workflow**:
- **Startup**: Load environment-specific configuration
- **Runtime**: Cached access with TTL
- **Rotation**: Automatic secret refresh

### 4. Security & Compliance Controls (`security_compliance_controls`)
**Purpose**: Comprehensive data protection and regulatory compliance

**Defense in Depth**:
1. **Data at Rest Encryption** (KMS)
2. **Data in Transit** (TLS 1.3)
3. **IAM Access Control** (RBAC)
4. **Application Security** (Authentication)

**Compliance Framework**:
- **SOC 2 Type II** compliance
- **ISO 27001** information security
- **GDPR** data protection
- **Custom** industry requirements

## Secrets Management Architecture

### Parameter Store Structure
```
/mono-repo/
├── dev/
│   ├── database/
│   │   ├── host              # String
│   │   ├── port              # String  
│   │   └── name              # String
│   ├── api/
│   │   ├── external-url      # String
│   │   └── rate-limit        # String
│   └── features/
│       ├── risk-analysis-v2  # String
│       └── dashboard-beta    # String
├── uat/
│   └── [same structure as dev]
└── prod/
    ├── database/
    │   ├── host              # String
    │   ├── port              # String
    │   ├── password          # SecureString (KMS)
    │   └── connection-string # SecureString (KMS)
    ├── api/
    │   ├── jwt-signing-key   # SecureString (KMS)
    │   └── external-api-key  # SecureString (KMS)
    └── services/
        ├── allowed-origins   # StringList
        └── notification-emails # StringList
```

### Secrets Manager Secrets
```
Database Secrets:
├── mono-repo/prod/rds/master-password
├── mono-repo/prod/rds/readonly-user
└── mono-repo/prod/rds/app-user

Application Secrets:
├── mono-repo/prod/api/jwt-signing-key
├── mono-repo/prod/api/external-service-key
└── mono-repo/prod/encryption/data-key

Service Secrets:
├── mono-repo/prod/airflow/fernet-key
├── mono-repo/prod/dash/session-key
└── mono-repo/prod/monitoring/api-key
```

## Security Implementation

### Encryption Strategy
```
KMS Key Management:
├── Customer Managed Keys (CMK)
│   ├── mono-repo-parameter-store-key
│   ├── mono-repo-secrets-manager-key
│   └── mono-repo-database-key
├── Automatic Key Rotation: Annual
├── Cross-Region Replication: Enabled
└── HSM Backing: FIPS 140-2 Level 3

SecureString Parameters:
├── Encryption: AES-256-GCM
├── Key Derivation: PBKDF2
└── Access Logging: CloudTrail
```

### Access Control Framework
```
IAM Policies:
├── ParameterStoreReadOnly
│   ├── GetParameter
│   ├── GetParameters
│   └── GetParametersByPath
├── SecretsManagerReadOnly
│   ├── GetSecretValue
│   ├── DescribeSecret
│   └── ListSecretVersionIds
└── SecretsManagerRotation
    ├── UpdateSecretVersionStage
    ├── PutSecretValue
    └── CreateNewVersion

Service Roles:
├── EKS Pod Identity (IRSA)
├── Lambda Execution Roles
├── EC2 Instance Profiles
└── Cross-Account Access
```

## Application Integration

### Secrets Retrieval Patterns
```python
# Parameter Store Access
import boto3

ssm = boto3.client('ssm')

# Get single parameter
response = ssm.get_parameter(
    Name='/mono-repo/prod/database/host'
)

# Get parameters by path
response = ssm.get_parameters_by_path(
    Path='/mono-repo/prod/',
    Recursive=True,
    WithDecryption=True
)

# Secrets Manager Access
secrets = boto3.client('secretsmanager')

# Get secret value
response = secrets.get_secret_value(
    SecretId='mono-repo/prod/rds/master-password'
)
```

### Caching Implementation
```python
# Local Cache with TTL
import time
from typing import Dict, Any, Optional

class SecretCache:
    def __init__(self, ttl: int = 900):  # 15 minutes
        self._cache: Dict[str, tuple] = {{}}
        self._ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return value
            del self._cache[key]
        return None
    
    def set(self, key: str, value: Any):
        self._cache[key] = (value, time.time())
```

## Monitoring & Compliance

### CloudTrail Events
```json
{{
    "eventSource": "ssm.amazonaws.com",
    "eventName": "GetParameter",
    "sourceIPAddress": "10.0.101.45",
    "userIdentity": {{
        "type": "AssumedRole",
        "principalId": "AROA...:risk-api-pod",
        "arn": "arn:aws:sts::123456789012:assumed-role/risk-api-role/risk-api-pod"
    }},
    "requestParameters": {{
        "name": "/mono-repo/prod/database/password",
        "withDecryption": true
    }}
}}
```

### CloudWatch Metrics
- **ParameterStore.GetParameter.Count**: API call volume
- **SecretsManager.GetSecretValue.Latency**: Retrieval performance
- **KMS.Decrypt.Count**: Decryption operations
- **Custom.SecretCacheHitRate**: Caching effectiveness

### Compliance Reporting
- **SOC 2**: Automated control testing
- **ISO 27001**: Security control validation
- **GDPR**: Data protection compliance
- **Audit Reports**: Quarterly compliance review

## Cost Optimization

### Pricing Structure
```
Parameter Store:
├── Standard Parameters: Free (up to 10,000)
├── Advanced Parameters: $0.05/parameter/month
└── API Calls: Free (standard tier)

Secrets Manager:
├── Secret Storage: $0.40/secret/month
├── API Calls: $0.05/10,000 requests
└── Rotation: No additional charge

Estimated Monthly Cost:
├── Parameter Store: $0 (using standard tier)
├── Secrets Manager: $6 (15 secrets × $0.40)
├── KMS: $1/key/month (3 keys = $3)
└── Total: ~$9/month
```

### Optimization Strategies
- **Consolidate Secrets**: JSON values in single secret
- **Cache Configuration**: Reduce API call frequency
- **Parameter Store First**: Use for non-sensitive config
- **Batch Retrieval**: GetParametersByPath for efficiency

## Operational Procedures

### Secret Rotation Process
```
1. Pre-rotation:
   ├── Validate rotation schedule
   ├── Check application health
   └── Prepare rollback plan

2. Rotation Execution:
   ├── Create new secret version
   ├── Test new credentials
   ├── Update application references
   └── Finalize rotation

3. Post-rotation:
   ├── Verify application functionality
   ├── Monitor error rates
   └── Clean up old versions
```

### Emergency Procedures
- **Credential Compromise**: Immediate rotation
- **Access Revocation**: IAM policy updates
- **Service Recovery**: Cached credential fallback
- **Incident Documentation**: Complete audit trail

## Troubleshooting Guide

### Common Issues
```
Issue: Access Denied
├── Check: IAM policy permissions
├── Check: Resource-based policies
├── Check: KMS key permissions
└── Verify: Service role assumption

Issue: Rotation Failures
├── Check: Lambda function logs
├── Check: Network connectivity
├── Check: Database permissions
└── Verify: Secret format

Issue: Performance Problems
├── Check: Cache hit rates
├── Check: API call patterns
├── Check: Network latency
└── Optimize: Batch retrieval
```

## File Structure
```
docs/architecture/
├── parameter_store_hierarchy.png               # Parameter organization
├── parameter_store_hierarchy.svg               # Vector format
├── secrets_manager_integration.png             # Secrets lifecycle
├── secrets_manager_integration.svg             # Vector format
├── application_secrets_workflow.png            # App integration
├── application_secrets_workflow.svg            # Vector format
├── security_compliance_controls.png            # Security framework
└── security_compliance_controls.svg            # Vector format
```

Created: {datetime.now().strftime('%B %d, %Y')}
Generated by: create_secrets_management_diagrams.py
"""

def main():
    """Main function to generate all parameter store and secrets management diagrams"""
    print("🔐 Starting Parameter Store and Secrets Management Diagrams generation...")
    
    # Create output directory
    output_dir = Path("../docs/architecture")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate diagrams
    diagrams = [
        ("parameter_store_hierarchy", create_parameter_store_hierarchy()),
        ("secrets_manager_integration", create_secrets_manager_integration()),
        ("application_secrets_workflow", create_application_secrets_workflow()),
        ("security_compliance_controls", create_security_compliance_controls())
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
    doc_path = Path("../docs/PARAMETER_STORE_SECRETS_MANAGEMENT_DOCUMENTATION.md")
    with open(doc_path, 'w') as f:
        f.write(doc_content)
    
    print(f"✅ Created comprehensive Parameter Store and Secrets Management documentation")
    
    print(f"\n✅ All Parameter Store and Secrets Management diagrams generated successfully!")
    print(f"📊 Generated {len(diagrams)} diagrams (PNG + SVG formats)")
    print(f"📖 Created comprehensive documentation")
    print(f"🔧 View diagrams in: {output_dir.resolve()}")

if __name__ == "__main__":
    main()