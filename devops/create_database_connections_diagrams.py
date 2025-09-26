#!/usr/bin/env python3
"""
Database Connections & Access Patterns Diagram Generator

This script generates comprehensive diagrams illustrating database architecture,
connection patterns, access controls, and data management across environments.

Generated Diagrams:
1. RDS Architecture & Connection Topology - Database infrastructure and connectivity
2. Database Access Control & Security - User management and permission matrices
3. Connection Pooling & Performance Optimization - Connection management patterns
4. Database Backup & Recovery Workflows - Backup strategies and disaster recovery

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

def create_rds_architecture_topology():
    """Generate RDS Architecture & Connection Topology diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(11, 14.5, 'RDS Architecture & Connection Topology', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(11, 14, 'Multi-Environment Database Infrastructure & Connectivity Patterns', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # Environment sections
    environments = [
        {'name': 'DEVELOPMENT', 'x': 1, 'y': 10, 'width': 6.5, 'height': 3.5, 'color': '#28a745'},
        {'name': 'UAT/STAGING', 'x': 8, 'y': 10, 'width': 6.5, 'height': 3.5, 'color': '#ffc107'},  
        {'name': 'PRODUCTION', 'x': 15, 'y': 10, 'width': 6.5, 'height': 3.5, 'color': '#dc3545'}
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
        
        # Database instances within environment
        if env['name'] == 'DEVELOPMENT':
            db_configs = [
                {'name': 'risk-dev-db', 'type': 'PostgreSQL 14', 'size': 'db.t3.medium', 'x': env['x'] + 0.5, 'y': env['y'] + 2},
                {'name': 'redis-dev', 'type': 'ElastiCache', 'size': 'cache.t3.micro', 'x': env['x'] + 3.5, 'y': env['y'] + 2}
            ]
        elif env['name'] == 'UAT/STAGING':
            db_configs = [
                {'name': 'risk-uat-db', 'type': 'PostgreSQL 14', 'size': 'db.t3.large', 'x': env['x'] + 0.5, 'y': env['y'] + 2},
                {'name': 'risk-uat-replica', 'type': 'Read Replica', 'size': 'db.t3.medium', 'x': env['x'] + 0.5, 'y': env['y'] + 1.2},
                {'name': 'redis-uat', 'type': 'ElastiCache', 'size': 'cache.t3.small', 'x': env['x'] + 3.5, 'y': env['y'] + 2}
            ]
        else:  # PRODUCTION
            db_configs = [
                {'name': 'risk-prod-primary', 'type': 'PostgreSQL 14', 'size': 'db.r5.xlarge', 'x': env['x'] + 0.5, 'y': env['y'] + 2.5},
                {'name': 'risk-prod-replica-1', 'type': 'Read Replica', 'size': 'db.r5.large', 'x': env['x'] + 3.5, 'y': env['y'] + 2.5},
                {'name': 'risk-prod-replica-2', 'type': 'Read Replica', 'size': 'db.r5.large', 'x': env['x'] + 3.5, 'y': env['y'] + 1.7},
                {'name': 'redis-prod-cluster', 'type': 'ElastiCache Cluster', 'size': 'cache.r6g.large', 'x': env['x'] + 0.5, 'y': env['y'] + 0.9}
            ]
        
        for db in db_configs:
            # Database instance box
            db_color = '#0066cc' if 'PostgreSQL' in db['type'] else '#dc3545' if 'Read Replica' in db['type'] else '#28a745'
            db_box = FancyBboxPatch((db['x'], db['y']), 2.5, 0.6, boxstyle="round,pad=0.05", 
                                   facecolor=db_color, alpha=0.2, edgecolor=db_color, linewidth=1.5)
            ax.add_patch(db_box)
            
            # Database details
            ax.text(db['x'] + 1.25, db['y'] + 0.45, db['name'], 
                    fontsize=9, ha='center', fontweight='bold', color=db_color)
            ax.text(db['x'] + 1.25, db['y'] + 0.25, db['type'], 
                    fontsize=8, ha='center', color=db_color)
            ax.text(db['x'] + 1.25, db['y'] + 0.1, db['size'], 
                    fontsize=7, ha='center', color='#666', style='italic')
    
    # Application layer connections
    ax.text(11, 9.2, 'Application Layer Connections', 
            fontsize=14, fontweight='bold', ha='center', color='#6f42c1')
    
    # Application services
    app_services = [
        {'name': 'Risk API Service', 'x': 3, 'y': 8, 'connections': ['Primary DB', 'Redis Cache']},
        {'name': 'Web Application', 'x': 8, 'y': 8, 'connections': ['Read Replica', 'Redis Cache']},
        {'name': 'Analytics Service', 'x': 13, 'y': 8, 'connections': ['Read Replica Only']},
        {'name': 'Batch Jobs', 'x': 18, 'y': 8, 'connections': ['Primary DB', 'Analytics DB']}
    ]
    
    for service in app_services:
        # Service box
        service_box = FancyBboxPatch((service['x'] - 1, service['y']), 2, 0.6, 
                                    boxstyle="round,pad=0.05", 
                                    facecolor='#6f42c1', alpha=0.2, 
                                    edgecolor='#6f42c1', linewidth=1.5)
        ax.add_patch(service_box)
        ax.text(service['x'], service['y'] + 0.3, service['name'], 
                fontsize=9, ha='center', fontweight='bold', color='#6f42c1')
        
        # Connection patterns
        connections_text = ', '.join(service['connections'])
        ax.text(service['x'], service['y'] - 0.2, connections_text, 
                fontsize=7, ha='center', color='#666', style='italic')
    
    # Connection security and patterns
    ax.text(11, 6.8, 'Connection Security & Patterns', 
            fontsize=14, fontweight='bold', ha='center', color='#e83e8c')
    
    # Security patterns
    security_patterns = [
        {
            'pattern': 'SSL/TLS Encryption',
            'description': 'All database connections encrypted in transit',
            'implementation': 'require_ssl=true, min_protocol_version=TLSv1.2'
        },
        {
            'pattern': 'VPC Security Groups',
            'description': 'Database access restricted to application subnets',
            'implementation': 'Port 5432 from app-sg only, no internet access'
        },
        {
            'pattern': 'IAM Database Authentication',
            'description': 'Token-based authentication for service accounts',
            'implementation': 'RDS IAM auth + temporary tokens (15 min TTL)'
        },
        {
            'pattern': 'Connection Pooling',
            'description': 'Efficient connection reuse and management',
            'implementation': 'PgBouncer proxy with transaction pooling'
        }
    ]
    
    for i, pattern in enumerate(security_patterns):
        y_pos = 6.3 - i*0.6
        
        # Pattern box
        pattern_box = FancyBboxPatch((1, y_pos), 20, 0.5, boxstyle="round,pad=0.05", 
                                    facecolor='#e83e8c', alpha=0.1, 
                                    edgecolor='#e83e8c', linewidth=1)
        ax.add_patch(pattern_box)
        
        ax.text(2, y_pos + 0.35, pattern['pattern'], 
                fontsize=10, fontweight='bold', color='#e83e8c')
        ax.text(2, y_pos + 0.15, pattern['description'], 
                fontsize=9, color='#e83e8c')
        ax.text(12, y_pos + 0.25, f"Implementation: {pattern['implementation']}", 
                fontsize=8, color='#666', style='italic')
    
    # Cross-environment replication
    ax.text(11, 2.8, 'Cross-Environment Replication & Backup', 
            fontsize=14, fontweight='bold', ha='center', color='#17a2b8')
    
    replication_flows = [
        {'source': 'PROD Primary', 'target': 'Cross-Region Replica (DR)', 'type': 'Async Replication', 'rto': '< 4 hours'},
        {'source': 'PROD Primary', 'target': 'Automated Backups', 'type': 'Point-in-Time Recovery', 'rto': '< 1 hour'},
        {'source': 'UAT Database', 'target': 'DEV Refresh', 'type': 'Weekly Data Refresh', 'rto': 'N/A'},
        {'source': 'All Environments', 'target': 'S3 Backup Archive', 'type': 'Daily Snapshots', 'rto': '< 24 hours'}
    ]
    
    for i, flow in enumerate(replication_flows):
        y_pos = 2.3 - i*0.3
        
        # Source
        ax.text(2, y_pos, flow['source'], fontsize=9, fontweight='bold', color='#17a2b8')
        
        # Arrow
        arrow = ConnectionPatch((5, y_pos + 0.05), (8, y_pos + 0.05), "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5, mutation_scale=15, 
                               fc="#17a2b8", ec="#17a2b8", linewidth=1.5)
        ax.add_artist(arrow)
        
        # Target and details
        ax.text(9, y_pos, flow['target'], fontsize=9, fontweight='bold', color='#17a2b8')
        ax.text(15, y_pos, f"{flow['type']} (RTO: {flow['rto']})", 
                fontsize=8, color='#666', style='italic')
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/rds_architecture_topology.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/rds_architecture_topology.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ RDS Architecture & Connection Topology diagram generated")

def create_database_access_control():
    """Generate Database Access Control & Security diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(10, 14.5, 'Database Access Control & Security', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(10, 14, 'User Management, Permissions & Security Framework', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # Database user roles hierarchy
    ax.text(5, 13, 'Database User Roles Hierarchy', fontsize=14, fontweight='bold', color='#dc3545')
    
    user_roles = [
        {
            'role': 'rds_superuser',
            'permissions': ['All database operations', 'User management', 'Schema changes'],
            'users': ['DBA Team', 'Emergency Access'],
            'access': 'Break-glass only',
            'color': '#dc3545',
            'y': 12.2
        },
        {
            'role': 'app_admin',
            'permissions': ['DDL operations', 'Index management', 'Performance tuning'],
            'users': ['DevOps Engineers', 'Senior Developers'],
            'access': 'Scheduled maintenance windows',
            'color': '#fd7e14',
            'y': 11.4
        },
        {
            'role': 'app_readwrite',
            'permissions': ['DML operations (CRUD)', 'Stored procedure execution'],
            'users': ['Application Services', 'API Services'],
            'access': '24/7 application access',
            'color': '#28a745',
            'y': 10.6
        },
        {
            'role': 'app_readonly',
            'permissions': ['SELECT queries only', 'View access', 'Reporting queries'],
            'users': ['Analytics Services', 'Reporting Tools', 'BI Applications'],
            'access': 'Read-only replica access',
            'color': '#17a2b8',
            'y': 9.8
        },
        {
            'role': 'app_backup',
            'permissions': ['Backup operations', 'Restore testing', 'Archive access'],
            'users': ['Backup Services', 'AWS Backup'],
            'access': 'Automated backup windows',
            'color': '#6f42c1',
            'y': 9.0
        }
    ]
    
    for role in user_roles:
        # Role box
        role_box = FancyBboxPatch((1, role['y']), 8, 0.6, boxstyle="round,pad=0.05", 
                                 facecolor=role['color'], alpha=0.2, 
                                 edgecolor=role['color'], linewidth=1.5)
        ax.add_patch(role_box)
        
        # Role details
        ax.text(1.5, role['y'] + 0.45, role['role'], 
                fontsize=10, fontweight='bold', color=role['color'])
        ax.text(1.5, role['y'] + 0.25, f"Users: {', '.join(role['users'])}", 
                fontsize=8, color=role['color'])
        ax.text(1.5, role['y'] + 0.05, f"Access: {role['access']}", 
                fontsize=8, color='#666', style='italic')
        
        # Permissions
        permissions_text = ' • '.join(role['permissions'])
        ax.text(9.5, role['y'] + 0.3, permissions_text, 
                fontsize=8, color=role['color'])
    
    # Authentication mechanisms
    ax.text(15, 13, 'Authentication Mechanisms', fontsize=14, fontweight='bold', color='#0066cc')
    
    auth_mechanisms = [
        {
            'method': 'IAM Database Authentication',
            'description': 'Token-based auth for service accounts',
            'pros': ['No password management', 'Temporary tokens', 'AWS integration'],
            'usage': 'Production services'
        },
        {
            'method': 'Username/Password',
            'description': 'Traditional database authentication',
            'pros': ['Simple setup', 'Wide compatibility', 'Emergency access'],
            'usage': 'Admin accounts, legacy apps'
        },
        {
            'method': 'Certificate Authentication',
            'description': 'SSL client certificates',
            'pros': ['Strong authentication', 'No shared secrets', 'Audit trail'],
            'usage': 'High-security environments'
        }
    ]
    
    for i, auth in enumerate(auth_mechanisms):
        y_pos = 12.2 - i*1.2
        
        # Auth method box
        auth_box = FancyBboxPatch((11, y_pos), 8, 1, boxstyle="round,pad=0.05", 
                                 facecolor='#0066cc', alpha=0.1, 
                                 edgecolor='#0066cc', linewidth=1)
        ax.add_patch(auth_box)
        
        ax.text(11.5, y_pos + 0.8, auth['method'], 
                fontsize=10, fontweight='bold', color='#0066cc')
        ax.text(11.5, y_pos + 0.6, auth['description'], 
                fontsize=9, color='#0066cc')
        ax.text(11.5, y_pos + 0.35, f"Pros: {', '.join(auth['pros'])}", 
                fontsize=8, color='#0066cc')
        ax.text(11.5, y_pos + 0.15, f"Usage: {auth['usage']}", 
                fontsize=8, color='#666', style='italic')
    
    # Connection security controls
    ax.text(10, 8.2, 'Connection Security Controls', 
            fontsize=14, fontweight='bold', ha='center', color='#e83e8c')
    
    security_controls = [
        {
            'control': 'Network Security',
            'measures': [
                'VPC Security Groups: Port 5432 from app subnets only',
                'No public internet access to databases',
                'Private subnet deployment with NAT gateway',
                'Network ACLs for additional layer of protection'
            ]
        },
        {
            'control': 'Encryption',
            'measures': [
                'Encryption at rest: AES-256 with KMS keys',
                'Encryption in transit: TLS 1.2+ required',
                'Database parameter groups enforce SSL',
                'Automated key rotation every 365 days'
            ]
        },
        {
            'control': 'Access Monitoring',
            'measures': [
                'CloudTrail logs all RDS API operations',
                'Database activity streams capture SQL queries',
                'CloudWatch metrics monitor connection counts',
                'Automated alerts for suspicious activity'
            ]
        }
    ]
    
    for i, control in enumerate(security_controls):
        y_start = 7.5 - i*2
        
        # Control header
        control_box = FancyBboxPatch((1, y_start), 18, 0.4, boxstyle="round,pad=0.05", 
                                    facecolor='#e83e8c', alpha=0.2, 
                                    edgecolor='#e83e8c', linewidth=1)
        ax.add_patch(control_box)
        ax.text(10, y_start + 0.2, control['control'], 
                fontsize=11, ha='center', fontweight='bold', color='#e83e8c')
        
        # Measures
        for j, measure in enumerate(control['measures']):
            ax.text(2, y_start - 0.3 - j*0.25, f"• {measure}", 
                    fontsize=9, color='#e83e8c')
    
    # Compliance and auditing
    compliance_box = FancyBboxPatch((1, 0.5), 18, 1.2, boxstyle="round,pad=0.1", 
                                   facecolor='#d4edda', edgecolor='#28a745', linewidth=2)
    ax.add_patch(compliance_box)
    ax.text(10, 1.4, 'Database Security Compliance & Auditing', 
            fontsize=12, fontweight='bold', ha='center', color='#28a745')
    
    compliance_items = [
        'SOC 2 Compliance: All database access logged and monitored',
        'PCI DSS Requirements: Encrypted storage and transmission of sensitive data',
        'Automated Compliance Checks: Daily validation of security configurations',
        'Access Reviews: Monthly review of database user permissions and access patterns'
    ]
    
    for i, item in enumerate(compliance_items[:2]):
        ax.text(2, 1.1 - i*0.15, f"• {item}", fontsize=9, color='#28a745')
    for i, item in enumerate(compliance_items[2:]):
        ax.text(11, 1.1 - i*0.15, f"• {item}", fontsize=9, color='#28a745')
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/database_access_control.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/database_access_control.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ Database Access Control & Security diagram generated")

def create_connection_pooling_optimization():
    """Generate Connection Pooling & Performance Optimization diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(10, 14.5, 'Connection Pooling & Performance Optimization', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(10, 14, 'Database Connection Management & Performance Strategies', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # Connection architecture flow
    ax.text(10, 13, 'Database Connection Architecture Flow', 
            fontsize=14, fontweight='bold', ha='center', color='#17a2b8')
    
    # Application layer
    app_services = [
        {'name': 'Risk API\n(10 instances)', 'x': 2, 'y': 11.5},
        {'name': 'Web App\n(5 instances)', 'x': 6, 'y': 11.5},
        {'name': 'Analytics\n(3 instances)', 'x': 10, 'y': 11.5},
        {'name': 'Batch Jobs\n(2 instances)', 'x': 14, 'y': 11.5}
    ]
    
    for service in app_services:
        service_box = FancyBboxPatch((service['x'] - 1, service['y']), 2, 0.8, 
                                    boxstyle="round,pad=0.05", 
                                    facecolor='#17a2b8', alpha=0.3, 
                                    edgecolor='#17a2b8', linewidth=1.5)
        ax.add_patch(service_box)
        ax.text(service['x'], service['y'] + 0.4, service['name'], 
                fontsize=9, ha='center', fontweight='bold', color='#17a2b8')
    
    # Connection pool layer
    ax.text(10, 10.5, 'PgBouncer Connection Pools', 
            fontsize=12, fontweight='bold', ha='center', color='#28a745')
    
    pool_configs = [
        {'name': 'Transaction Pool', 'connections': 'Max: 100\nActive: 25', 'x': 4, 'y': 9.5},
        {'name': 'Session Pool', 'connections': 'Max: 50\nActive: 15', 'x': 8, 'y': 9.5},
        {'name': 'Statement Pool', 'connections': 'Max: 200\nActive: 45', 'x': 12, 'y': 9.5}
    ]
    
    for pool in pool_configs:
        pool_box = FancyBboxPatch((pool['x'] - 1.5, pool['y']), 3, 0.8, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor='#28a745', alpha=0.3, 
                                 edgecolor='#28a745', linewidth=1.5)
        ax.add_patch(pool_box)
        ax.text(pool['x'], pool['y'] + 0.5, pool['name'], 
                fontsize=10, ha='center', fontweight='bold', color='#28a745')
        ax.text(pool['x'], pool['y'] + 0.2, pool['connections'], 
                fontsize=8, ha='center', color='#28a745')
    
    # Database layer
    ax.text(10, 8.5, 'PostgreSQL Database Cluster', 
            fontsize=12, fontweight='bold', ha='center', color='#dc3545')
    
    db_instances = [
        {'name': 'Primary\n(Write)', 'connections': 'Max: 100\nActive: 35', 'x': 6, 'y': 7.5},
        {'name': 'Replica 1\n(Read)', 'connections': 'Max: 100\nActive: 20', 'x': 10, 'y': 7.5},
        {'name': 'Replica 2\n(Read)', 'connections': 'Max: 100\nActive: 15', 'x': 14, 'y': 7.5}
    ]
    
    for db in db_instances:
        db_box = FancyBboxPatch((db['x'] - 1.5, db['y']), 3, 0.8, 
                               boxstyle="round,pad=0.05", 
                               facecolor='#dc3545', alpha=0.3, 
                               edgecolor='#dc3545', linewidth=1.5)
        ax.add_patch(db_box)
        ax.text(db['x'], db['y'] + 0.5, db['name'], 
                fontsize=10, ha='center', fontweight='bold', color='#dc3545')
        ax.text(db['x'], db['y'] + 0.2, db['connections'], 
                fontsize=8, ha='center', color='#dc3545')
    
    # Connection flow arrows
    # Apps to pools
    for service in app_services:
        for pool in pool_configs:
            if abs(service['x'] - pool['x']) <= 4:  # Connect nearby services
                arrow = ConnectionPatch((service['x'], service['y']), 
                                      (pool['x'], pool['y'] + 0.8), 
                                      "data", "data", arrowstyle="->", 
                                      shrinkA=5, shrinkB=5, mutation_scale=10, 
                                      fc="#666", ec="#666", alpha=0.5)
                ax.add_artist(arrow)
    
    # Pools to databases
    for pool in pool_configs:
        for db in db_instances:
            if (pool['name'] == 'Transaction Pool' and 'Primary' in db['name']) or \
               ('Pool' in pool['name'] and 'Replica' in db['name']):
                arrow = ConnectionPatch((pool['x'], pool['y']), 
                                      (db['x'], db['y'] + 0.8), 
                                      "data", "data", arrowstyle="->", 
                                      shrinkA=5, shrinkB=5, mutation_scale=10, 
                                      fc="#666", ec="#666", alpha=0.7)
                ax.add_artist(arrow)
    
    # Performance optimization strategies
    ax.text(10, 6.5, 'Performance Optimization Strategies', 
            fontsize=14, fontweight='bold', ha='center', color='#6f42c1')
    
    optimization_strategies = [
        {
            'category': 'Connection Management',
            'strategies': [
                'Connection pooling reduces overhead by 80%',
                'Idle connection timeout: 300 seconds',
                'Connection reuse prevents authentication overhead',
                'Pool size tuning based on workload patterns'
            ]
        },
        {
            'category': 'Query Optimization',
            'strategies': [
                'Read queries routed to read replicas automatically',
                'Query result caching with Redis (5-minute TTL)',
                'Prepared statements reduce parsing overhead',
                'Query performance monitoring with pg_stat_statements'
            ]
        },
        {
            'category': 'Resource Management',
            'strategies': [
                'Auto-scaling based on connection count and CPU',
                'Memory allocation optimized for workload',
                'Background maintenance during low-traffic hours',
                'Automated index maintenance and statistics updates'
            ]
        }
    ]
    
    for i, category in enumerate(optimization_strategies):
        y_start = 5.8 - i*1.5
        
        # Category header
        cat_box = FancyBboxPatch((1, y_start), 18, 0.4, boxstyle="round,pad=0.05", 
                                facecolor='#6f42c1', alpha=0.2, 
                                edgecolor='#6f42c1', linewidth=1)
        ax.add_patch(cat_box)
        ax.text(10, y_start + 0.2, category['category'], 
                fontsize=11, ha='center', fontweight='bold', color='#6f42c1')
        
        # Strategies
        for j, strategy in enumerate(category['strategies']):
            ax.text(2, y_start - 0.3 - j*0.2, f"• {strategy}", 
                    fontsize=9, color='#6f42c1')
    
    # Performance metrics and monitoring
    metrics_box = FancyBboxPatch((1, 0.5), 18, 1.2, boxstyle="round,pad=0.1", 
                                facecolor='#fff3cd', edgecolor='#856404', linewidth=2)
    ax.add_patch(metrics_box)
    ax.text(10, 1.4, 'Performance Metrics & Monitoring', 
            fontsize=12, fontweight='bold', ha='center', color='#856404')
    
    performance_metrics = [
        'Connection Pool Efficiency: 95% (target: 90%+)',
        'Average Query Response Time: 45ms (target: < 100ms)',
        'Database CPU Utilization: 65% average (target: < 80%)',
        'Connection Pool Utilization: 35% average (target: < 70%)'
    ]
    
    for i, metric in enumerate(performance_metrics[:2]):
        ax.text(2, 1.1 - i*0.15, f"✓ {metric}", fontsize=9, color='#856404', fontweight='bold')
    for i, metric in enumerate(performance_metrics[2:]):
        ax.text(11, 1.1 - i*0.15, f"✓ {metric}", fontsize=9, color='#856404', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/connection_pooling_optimization.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/connection_pooling_optimization.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ Connection Pooling & Performance Optimization diagram generated")

def create_database_backup_recovery():
    """Generate Database Backup & Recovery Workflows diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(11, 14.5, 'Database Backup & Recovery Workflows', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(11, 14, 'Backup Strategies, Disaster Recovery & Business Continuity', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # Backup strategy overview
    ax.text(11, 13, 'Multi-Tier Backup Strategy', 
            fontsize=14, fontweight='bold', ha='center', color='#dc3545')
    
    # Backup tiers
    backup_tiers = [
        {
            'tier': 'Real-Time Protection',
            'method': 'Synchronous Replication',
            'rpo': '0 seconds',
            'rto': '< 5 minutes',
            'description': 'Multi-AZ deployment with automatic failover',
            'color': '#dc3545',
            'x': 2, 'y': 11.5
        },
        {
            'tier': 'Point-in-Time Recovery',
            'method': 'Transaction Log Backups',
            'rpo': '< 5 minutes',
            'rto': '< 30 minutes',
            'description': 'Continuous backup of transaction logs',
            'color': '#fd7e14',
            'x': 7.5, 'y': 11.5
        },
        {
            'tier': 'Daily Snapshots',
            'method': 'Automated DB Snapshots',
            'rpo': '< 24 hours',
            'rto': '< 4 hours',
            'description': 'Daily automated snapshots retained for 7 days',
            'color': '#ffc107',
            'x': 13, 'y': 11.5
        },
        {
            'tier': 'Long-term Archive',
            'method': 'Manual Snapshots + S3',
            'rpo': '< 1 week',
            'rto': '< 24 hours',
            'description': 'Monthly snapshots for compliance retention',
            'color': '#28a745',
            'x': 18.5, 'y': 11.5
        }
    ]
    
    for tier in backup_tiers:
        # Tier box
        tier_box = FancyBboxPatch((tier['x'] - 2, tier['y']), 4, 1.5, 
                                 boxstyle="round,pad=0.1", 
                                 facecolor=tier['color'], alpha=0.2, 
                                 edgecolor=tier['color'], linewidth=2)
        ax.add_patch(tier_box)
        
        # Tier details
        ax.text(tier['x'], tier['y'] + 1.2, tier['tier'], 
                fontsize=10, ha='center', fontweight='bold', color=tier['color'])
        ax.text(tier['x'], tier['y'] + 0.95, tier['method'], 
                fontsize=9, ha='center', color=tier['color'])
        ax.text(tier['x'], tier['y'] + 0.7, f"RPO: {tier['rpo']}", 
                fontsize=8, ha='center', color=tier['color'], fontweight='bold')
        ax.text(tier['x'], tier['y'] + 0.5, f"RTO: {tier['rto']}", 
                fontsize=8, ha='center', color=tier['color'], fontweight='bold')
        ax.text(tier['x'], tier['y'] + 0.2, tier['description'], 
                fontsize=7, ha='center', color='#666', style='italic')
    
    # Recovery scenarios
    ax.text(11, 10, 'Disaster Recovery Scenarios', 
            fontsize=14, fontweight='bold', ha='center', color='#17a2b8')
    
    recovery_scenarios = [
        {
            'scenario': 'Primary AZ Failure',
            'detection': 'Automated health checks',
            'response': 'Automatic failover to standby AZ',
            'impact': 'RTO: 2-3 minutes, RPO: 0 seconds',
            'procedures': 'Fully automated, no manual intervention required'
        },
        {
            'scenario': 'Database Corruption',
            'detection': 'Application errors, data integrity checks',
            'response': 'Point-in-time recovery from transaction logs',
            'impact': 'RTO: 15-30 minutes, RPO: < 5 minutes',
            'procedures': 'Manual trigger, automated recovery process'
        },
        {
            'scenario': 'Regional Outage',
            'detection': 'Multi-region monitoring alerts',
            'response': 'Cross-region replica promotion',
            'impact': 'RTO: 2-4 hours, RPO: < 15 minutes',
            'procedures': 'Manual decision, semi-automated recovery'
        },
        {
            'scenario': 'Data Center Disaster',
            'detection': 'Complete communication loss',
            'response': 'Restore from archived snapshots',
            'impact': 'RTO: 8-24 hours, RPO: < 24 hours',
            'procedures': 'Manual recovery from cold backups'
        }
    ]
    
    for i, scenario in enumerate(recovery_scenarios):
        y_pos = 9.3 - i*1.2
        
        # Scenario box
        scenario_box = FancyBboxPatch((1, y_pos), 20, 1, boxstyle="round,pad=0.05", 
                                     facecolor='#17a2b8', alpha=0.1, 
                                     edgecolor='#17a2b8', linewidth=1)
        ax.add_patch(scenario_box)
        
        ax.text(2, y_pos + 0.8, scenario['scenario'], 
                fontsize=11, fontweight='bold', color='#17a2b8')
        ax.text(2, y_pos + 0.6, f"Detection: {scenario['detection']}", 
                fontsize=9, color='#17a2b8')
        ax.text(2, y_pos + 0.4, f"Response: {scenario['response']}", 
                fontsize=9, color='#17a2b8')
        ax.text(2, y_pos + 0.2, f"Impact: {scenario['impact']}", 
                fontsize=9, color='#17a2b8', fontweight='bold')
        ax.text(15, y_pos + 0.5, scenario['procedures'], 
                fontsize=9, color='#666', style='italic')
    
    # Backup and recovery workflow
    ax.text(11, 4.5, 'Automated Backup & Recovery Workflow', 
            fontsize=14, fontweight='bold', ha='center', color='#6f42c1')
    
    workflow_steps = [
        {'step': '1. Schedule', 'action': 'Automated triggers', 'time': 'Daily 2 AM UTC'},
        {'step': '2. Snapshot', 'action': 'Create DB snapshot', 'time': '10-15 minutes'},
        {'step': '3. Validate', 'action': 'Verify backup integrity', 'time': '5 minutes'},
        {'step': '4. Archive', 'action': 'Copy to S3 + Cross-region', 'time': '20-30 minutes'},
        {'step': '5. Cleanup', 'action': 'Remove old snapshots', 'time': '5 minutes'},
        {'step': '6. Report', 'action': 'Success/failure notification', 'time': '1 minute'}
    ]
    
    for i, step in enumerate(workflow_steps):
        x_pos = 1.5 + i * 3.3
        
        # Step box
        step_box = FancyBboxPatch((x_pos, 3.5), 3, 0.8, boxstyle="round,pad=0.05", 
                                 facecolor='#6f42c1', alpha=0.2, 
                                 edgecolor='#6f42c1', linewidth=1)
        ax.add_patch(step_box)
        
        ax.text(x_pos + 1.5, 4.15, step['step'], 
                fontsize=10, ha='center', fontweight='bold', color='#6f42c1')
        ax.text(x_pos + 1.5, 3.95, step['action'], 
                fontsize=8, ha='center', color='#6f42c1')
        ax.text(x_pos + 1.5, 3.75, step['time'], 
                fontsize=8, ha='center', color='#666', style='italic')
        
        # Arrow to next step
        if i < len(workflow_steps) - 1:
            arrow = ConnectionPatch((x_pos + 3, 3.9), (x_pos + 3.3, 3.9), "data", "data",
                                   arrowstyle="->", shrinkA=2, shrinkB=2, mutation_scale=10, 
                                   fc="#6f42c1", ec="#6f42c1")
            ax.add_artist(arrow)
    
    # Compliance and testing
    compliance_box = FancyBboxPatch((1, 1.5), 20, 1.5, boxstyle="round,pad=0.1", 
                                   facecolor='#d4edda', edgecolor='#28a745', linewidth=2)
    ax.add_patch(compliance_box)
    ax.text(11, 2.7, 'Backup Compliance & Recovery Testing', 
            fontsize=12, fontweight='bold', ha='center', color='#28a745')
    
    compliance_items = [
        'Retention Policy: 7 days automated, 90 days manual, 7 years compliance archive',
        'Recovery Testing: Monthly automated recovery tests in isolated environment',
        'Compliance Reporting: Quarterly backup and recovery capability reports',
        'Security: All backups encrypted at rest with KMS, access logged via CloudTrail'
    ]
    
    for i, item in enumerate(compliance_items[:2]):
        ax.text(2, 2.4 - i*0.2, f"• {item}", fontsize=9, color='#28a745')
    for i, item in enumerate(compliance_items[2:]):
        ax.text(2, 2.0 - i*0.2, f"• {item}", fontsize=9, color='#28a745')
    
    # Success metrics
    ax.text(11, 0.8, '✓ 99.99% backup success rate • ✓ 100% recovery test success • ✓ Zero data loss incidents', 
            fontsize=11, ha='center', fontweight='bold', color='#28a745',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#d4edda', edgecolor='#28a745'))
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/database_backup_recovery.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/database_backup_recovery.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ Database Backup & Recovery Workflows diagram generated")

def create_documentation():
    """Create comprehensive documentation for database connections and access patterns"""
    doc_content = f"""# Database Connections & Access Patterns Diagrams

*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

This document provides comprehensive analysis of the database connections and access patterns diagrams for the Risk Management Platform infrastructure.

## Overview

The database connections and access patterns diagrams illustrate the comprehensive data architecture, security framework, and performance optimization strategies implemented across all environments. These diagrams demonstrate enterprise-grade database management with multi-layered security controls, optimized connection patterns, and robust backup/recovery procedures.

## Generated Diagrams

### 1. RDS Architecture & Connection Topology
**File**: `rds_architecture_topology.png/.svg`

This diagram shows the complete database infrastructure and connectivity patterns across environments.

**Database Architecture by Environment**:

**Development Environment**:
- **Primary Database**: `risk-dev-db` (PostgreSQL 14, db.t3.medium)
- **Cache Layer**: `redis-dev` (ElastiCache, cache.t3.micro)
- **Usage Pattern**: Development and testing workloads

**UAT/Staging Environment**:
- **Primary Database**: `risk-uat-db` (PostgreSQL 14, db.t3.large)
- **Read Replica**: `risk-uat-replica` (PostgreSQL 14, db.t3.medium)
- **Cache Layer**: `redis-uat` (ElastiCache, cache.t3.small)
- **Usage Pattern**: User acceptance testing and staging validation

**Production Environment**:
- **Primary Database**: `risk-prod-primary` (PostgreSQL 14, db.r5.xlarge)
- **Read Replica 1**: `risk-prod-replica-1` (PostgreSQL 14, db.r5.large)
- **Read Replica 2**: `risk-prod-replica-2` (PostgreSQL 14, db.r5.large)
- **Cache Cluster**: `redis-prod-cluster` (ElastiCache Cluster, cache.r6g.large)
- **Usage Pattern**: Production workloads with high availability

**Application Layer Connections**:
- **Risk API Service**: Connects to primary database and Redis cache
- **Web Application**: Uses read replicas and cache for optimal performance
- **Analytics Service**: Read-replica only access for reporting workloads
- **Batch Jobs**: Direct primary database access for data processing

**Connection Security Patterns**:
- **SSL/TLS Encryption**: All connections encrypted with TLS 1.2+
- **VPC Security Groups**: Database access restricted to application subnets
- **IAM Database Authentication**: Token-based authentication for service accounts
- **Connection Pooling**: PgBouncer proxy for efficient connection management

### 2. Database Access Control & Security
**File**: `database_access_control.png/.svg`

Comprehensive security framework covering user management, authentication, and access controls.

**Database User Roles Hierarchy**:

1. **rds_superuser** (Break-glass only):
   - **Permissions**: All database operations, user management, schema changes
   - **Users**: DBA Team, Emergency Access accounts
   - **Access Pattern**: Emergency access only with full audit logging

2. **app_admin** (Maintenance windows):
   - **Permissions**: DDL operations, index management, performance tuning
   - **Users**: DevOps Engineers, Senior Developers
   - **Access Pattern**: Scheduled maintenance windows only

3. **app_readwrite** (24/7 application access):
   - **Permissions**: DML operations (CRUD), stored procedure execution
   - **Users**: Application Services, API Services
   - **Access Pattern**: Continuous application access with connection pooling

4. **app_readonly** (Read-replica access):
   - **Permissions**: SELECT queries only, view access, reporting queries
   - **Users**: Analytics Services, Reporting Tools, BI Applications
   - **Access Pattern**: Read-replica routing for performance optimization

5. **app_backup** (Automated backup windows):
   - **Permissions**: Backup operations, restore testing, archive access
   - **Users**: Backup Services, AWS Backup
   - **Access Pattern**: Automated backup and recovery operations

**Authentication Mechanisms**:

- **IAM Database Authentication**: Token-based authentication for service accounts with temporary tokens and AWS integration
- **Username/Password**: Traditional authentication for admin accounts and legacy applications
- **Certificate Authentication**: SSL client certificates for high-security environments

**Security Controls**:
- **Network Security**: VPC security groups, private subnets, no public access
- **Encryption**: AES-256 at rest with KMS keys, TLS 1.2+ in transit
- **Access Monitoring**: CloudTrail logging, database activity streams, automated alerts

### 3. Connection Pooling & Performance Optimization
**File**: `connection_pooling_optimization.png/.svg`

Advanced connection management and performance optimization strategies.

**Connection Architecture Flow**:
- **Application Layer**: 20 application instances across multiple services
- **Connection Pool Layer**: PgBouncer pools (Transaction, Session, Statement)
- **Database Layer**: PostgreSQL cluster with primary and read replicas

**PgBouncer Configuration**:
- **Transaction Pool**: Max 100 connections, optimized for short transactions
- **Session Pool**: Max 50 connections, for session-based applications
- **Statement Pool**: Max 200 connections, for high-throughput operations

**Performance Optimization Strategies**:

1. **Connection Management**:
   - Connection pooling reduces overhead by 80%
   - Idle connection timeout: 300 seconds
   - Pool size tuning based on workload patterns
   - Connection reuse prevents authentication overhead

2. **Query Optimization**:
   - Automatic read query routing to read replicas
   - Redis caching with 5-minute TTL for frequent queries
   - Prepared statements to reduce parsing overhead
   - Query performance monitoring with pg_stat_statements

3. **Resource Management**:
   - Auto-scaling based on connection count and CPU utilization
   - Memory allocation optimized for specific workloads
   - Background maintenance during low-traffic hours
   - Automated index maintenance and statistics updates

**Performance Metrics**:
- **Connection Pool Efficiency**: 95% (target: 90%+)
- **Average Query Response Time**: 45ms (target: < 100ms)
- **Database CPU Utilization**: 65% average (target: < 80%)
- **Connection Pool Utilization**: 35% average (target: < 70%)

### 4. Database Backup & Recovery Workflows
**File**: `database_backup_recovery.png/.svg`

Comprehensive backup strategy and disaster recovery procedures.

**Multi-Tier Backup Strategy**:

1. **Real-Time Protection** (RPO: 0 seconds, RTO: < 5 minutes):
   - **Method**: Synchronous replication with Multi-AZ deployment
   - **Use Case**: Primary protection against hardware failures
   - **Automation**: Fully automated failover

2. **Point-in-Time Recovery** (RPO: < 5 minutes, RTO: < 30 minutes):
   - **Method**: Continuous transaction log backups
   - **Use Case**: Recovery from data corruption or accidental changes
   - **Automation**: Manual trigger, automated recovery process

3. **Daily Snapshots** (RPO: < 24 hours, RTO: < 4 hours):
   - **Method**: Automated database snapshots retained for 7 days
   - **Use Case**: Daily backup protection and quick recovery
   - **Automation**: Fully automated with integrity validation

4. **Long-term Archive** (RPO: < 1 week, RTO: < 24 hours):
   - **Method**: Monthly snapshots with S3 archival
   - **Use Case**: Compliance retention and long-term recovery
   - **Automation**: Automated creation with manual validation

**Disaster Recovery Scenarios**:

- **Primary AZ Failure**: Automatic failover to standby AZ (2-3 minutes)
- **Database Corruption**: Point-in-time recovery from transaction logs (15-30 minutes)
- **Regional Outage**: Cross-region replica promotion (2-4 hours)
- **Data Center Disaster**: Restore from archived snapshots (8-24 hours)

**Automated Backup Workflow**:
1. **Schedule**: Daily automated triggers at 2 AM UTC
2. **Snapshot**: Create database snapshot (10-15 minutes)
3. **Validate**: Verify backup integrity (5 minutes)
4. **Archive**: Copy to S3 and cross-region (20-30 minutes)
5. **Cleanup**: Remove old snapshots per retention policy (5 minutes)
6. **Report**: Success/failure notifications (1 minute)

## Database Management Framework

### Performance Management
Advanced performance monitoring and optimization:

1. **Real-time Monitoring**: Continuous monitoring of connection counts, query performance, and resource utilization
2. **Automated Scaling**: Dynamic scaling based on workload patterns and performance metrics
3. **Query Optimization**: Automated query plan analysis and optimization recommendations
4. **Cache Management**: Intelligent caching strategies with Redis for frequently accessed data

### Security Framework
Multi-layered security approach:

1. **Network Security**: VPC isolation, security groups, private subnets
2. **Identity Management**: Role-based access control with least privilege principles
3. **Data Protection**: Encryption at rest and in transit with key management
4. **Audit and Compliance**: Comprehensive logging and monitoring for regulatory compliance

### High Availability Design
Enterprise-grade availability and reliability:

1. **Multi-AZ Deployment**: Automatic failover for primary database instances
2. **Read Replica Strategy**: Multiple read replicas for read scaling and availability
3. **Connection Resilience**: Connection pooling and automatic reconnection handling
4. **Health Monitoring**: Continuous health checks and automated recovery procedures

### Backup and Recovery Strategy
Comprehensive data protection:

1. **Multiple Recovery Points**: Various RPO/RTO options for different scenarios
2. **Automated Testing**: Regular recovery testing to validate backup integrity
3. **Cross-Region Protection**: Geographic distribution of backups for disaster recovery
4. **Compliance Retention**: Long-term retention policies for regulatory requirements

## Operational Procedures

### Database Maintenance
1. **Scheduled Maintenance**: Weekly maintenance windows during low-traffic periods
2. **Performance Tuning**: Monthly performance analysis and optimization
3. **Capacity Planning**: Quarterly capacity analysis and scaling recommendations
4. **Security Updates**: Automated security patching with minimal downtime

### Monitoring and Alerting
1. **Performance Monitoring**: Real-time monitoring of key performance indicators
2. **Security Monitoring**: Continuous monitoring of access patterns and security events
3. **Capacity Monitoring**: Proactive monitoring of storage, CPU, and memory utilization
4. **Backup Monitoring**: Automated validation and reporting of backup operations

### Incident Response
1. **Automated Detection**: Intelligent alerting for performance and availability issues
2. **Escalation Procedures**: Clear escalation paths for different types of incidents
3. **Recovery Procedures**: Documented procedures for various recovery scenarios
4. **Post-Incident Analysis**: Comprehensive analysis and improvement recommendations

## Best Practices Implementation

### Database Design Best Practices
1. **Normalized Schema**: Proper database normalization for data integrity
2. **Index Strategy**: Optimized indexing for query performance
3. **Partitioning**: Table partitioning for large datasets and improved performance
4. **Constraint Management**: Proper use of foreign keys and check constraints

### Security Best Practices
1. **Principle of Least Privilege**: Minimal required permissions for each role
2. **Defense in Depth**: Multiple layers of security controls
3. **Regular Access Reviews**: Quarterly review of user permissions and access patterns
4. **Audit Trail Maintenance**: Comprehensive logging of all database activities

### Performance Best Practices
1. **Connection Pool Optimization**: Proper sizing and configuration of connection pools
2. **Query Optimization**: Regular analysis and optimization of query performance
3. **Resource Monitoring**: Continuous monitoring and optimization of database resources
4. **Caching Strategies**: Intelligent use of caching to reduce database load

---

*This documentation is automatically updated when infrastructure diagrams are regenerated. For questions about database architecture or performance optimization, contact the Database Engineering Team.*
"""

    with open('../docs/database_connections_access_patterns_implementation.md', 'w') as f:
        f.write(doc_content)
    
    print("📖 Database Connections & Access Patterns documentation created")

def main():
    """Main function to generate all database connections and access patterns diagrams"""
    print("🚀 Starting Database Connections & Access Patterns diagram generation...")
    print("=" * 80)
    
    try:
        # Setup
        setup_directories()
        
        # Generate all diagrams
        create_rds_architecture_topology()
        create_database_access_control()
        create_connection_pooling_optimization()
        create_database_backup_recovery()
        
        # Create documentation
        create_documentation()
        
        print("=" * 80)
        print("✅ Database Connections & Access Patterns diagrams completed successfully!")
        print("\nGenerated Files:")
        print("📊 4 diagrams (PNG + SVG formats)")
        print("📖 1 comprehensive documentation file")
        print("\nAll files saved to:")
        print("- Diagrams: docs/architecture/")
        print("- Documentation: docs/database_connections_access_patterns_implementation.md")
        
    except Exception as e:
        print(f"❌ Error generating diagrams: {str(e)}")
        raise

if __name__ == "__main__":
    main()