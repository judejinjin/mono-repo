#!/usr/bin/env python3
"""
CloudWatch Logging Architecture Diagram Generator

This script generates comprehensive diagrams illustrating log aggregation,
retention policies, cross-account sharing, and compliance logging across
the Risk Management Platform infrastructure.

Generated Diagrams:
1. Log Aggregation & Collection Architecture - Centralized logging infrastructure and data flows
2. Log Retention & Lifecycle Management - Retention policies and automated lifecycle management
3. Cross-Account Log Sharing & Access - Multi-account logging architecture and access controls
4. Compliance Logging & Audit Trail - Compliance requirements and audit trail management

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

def create_log_aggregation_architecture():
    """Generate Log Aggregation & Collection Architecture diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(11, 14.5, 'Log Aggregation & Collection Architecture', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(11, 14, 'Centralized Logging Infrastructure & Data Flow Patterns', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # Log sources
    ax.text(11, 13.2, 'Log Sources & Collection Points', 
            fontsize=14, fontweight='bold', ha='center', color='#17a2b8')
    
    # Application log sources
    app_sources = [
        {'name': 'Risk API Services', 'type': 'Application Logs', 'volume': '~50GB/day', 'x': 3, 'y': 12, 'color': '#dc3545'},
        {'name': 'Web Applications', 'type': 'Access Logs', 'volume': '~25GB/day', 'x': 7, 'y': 12, 'color': '#fd7e14'},
        {'name': 'Database Systems', 'type': 'Query Logs', 'volume': '~15GB/day', 'x': 11, 'y': 12, 'color': '#28a745'},
        {'name': 'Infrastructure', 'type': 'System Logs', 'volume': '~10GB/day', 'x': 15, 'y': 12, 'color': '#6f42c1'},
        {'name': 'Security Systems', 'type': 'Audit Logs', 'volume': '~5GB/day', 'x': 19, 'y': 12, 'color': '#e83e8c'}
    ]
    
    for source in app_sources:
        # Source box
        source_box = FancyBboxPatch((source['x'] - 1.2, source['y']), 2.4, 1, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor=source['color'], alpha=0.3, 
                                   edgecolor=source['color'], linewidth=2)
        ax.add_patch(source_box)
        
        ax.text(source['x'], source['y'] + 0.7, source['name'], 
                fontsize=9, ha='center', fontweight='bold', color=source['color'])
        ax.text(source['x'], source['y'] + 0.5, source['type'], 
                fontsize=8, ha='center', color=source['color'])
        ax.text(source['x'], source['y'] + 0.3, source['volume'], 
                fontsize=8, ha='center', color='#666', fontweight='bold')
        ax.text(source['x'], source['y'] + 0.1, 'CloudWatch Logs', 
                fontsize=7, ha='center', color='#666', style='italic')
    
    # Log aggregation layer
    ax.text(11, 10.5, 'Log Aggregation & Processing Layer', 
            fontsize=14, fontweight='bold', ha='center', color='#ff9900')
    
    # CloudWatch Logs central hub
    cw_logs_box = FancyBboxPatch((8, 9), 6, 1.2, boxstyle="round,pad=0.1", 
                                facecolor='#ff9900', alpha=0.2, 
                                edgecolor='#ff9900', linewidth=3)
    ax.add_patch(cw_logs_box)
    ax.text(11, 9.9, 'Amazon CloudWatch Logs', 
            fontsize=12, fontweight='bold', ha='center', color='#ff9900')
    ax.text(11, 9.6, 'Central Log Aggregation Service', 
            fontsize=10, ha='center', color='#ff9900')
    ax.text(11, 9.3, 'Log Groups: 25+ | Log Streams: 500+ | Daily Volume: ~105GB', 
            fontsize=9, ha='center', color='#666')
    
    # Connection flows from sources to CloudWatch
    for source in app_sources:
        arrow = ConnectionPatch((source['x'], source['y']), (11, 10.2), 
                               "data", "data", arrowstyle="->", 
                               shrinkA=20, shrinkB=20, mutation_scale=12, 
                               fc=source['color'], ec=source['color'], 
                               linewidth=2, alpha=0.7)
        ax.add_artist(arrow)
    
    # Log processing and forwarding
    processing_services = [
        {'name': 'Kinesis Data Firehose', 'desc': 'Stream to S3/OpenSearch', 'x': 5, 'y': 7.5},
        {'name': 'Lambda Log Processor', 'desc': 'Transform & filter logs', 'x': 11, 'y': 7.5},
        {'name': 'OpenSearch Service', 'desc': 'Search & visualization', 'x': 17, 'y': 7.5}
    ]
    
    for service in processing_services:
        service_box = FancyBboxPatch((service['x'] - 1.5, service['y']), 3, 0.8, 
                                    boxstyle="round,pad=0.05", 
                                    facecolor='#28a745', alpha=0.2, 
                                    edgecolor='#28a745', linewidth=1.5)
        ax.add_patch(service_box)
        ax.text(service['x'], service['y'] + 0.5, service['name'], 
                fontsize=10, ha='center', fontweight='bold', color='#28a745')
        ax.text(service['x'], service['y'] + 0.25, service['desc'], 
                fontsize=8, ha='center', color='#28a745')
        
        # Arrow from CloudWatch to processing service
        arrow = ConnectionPatch((11, 9), (service['x'], service['y'] + 0.8), 
                               "data", "data", arrowstyle="->", 
                               shrinkA=10, shrinkB=10, mutation_scale=10, 
                               fc="#28a745", ec="#28a745", linewidth=1.5)
        ax.add_artist(arrow)
    
    # Storage and archival layer
    ax.text(11, 6.5, 'Log Storage & Long-term Archival', 
            fontsize=14, fontweight='bold', ha='center', color='#6f42c1')
    
    storage_tiers = [
        {'name': 'S3 Standard', 'desc': 'Active logs (30 days)', 'cost': '$0.023/GB', 'x': 4, 'y': 5.5},
        {'name': 'S3 Intelligent-Tiering', 'desc': 'Frequent access (90 days)', 'cost': '$0.0125/GB', 'x': 8, 'y': 5.5},
        {'name': 'S3 Standard-IA', 'desc': 'Compliance logs (1 year)', 'cost': '$0.0125/GB', 'x': 12, 'y': 5.5},
        {'name': 'S3 Glacier', 'desc': 'Long-term archive (7 years)', 'cost': '$0.004/GB', 'x': 16, 'y': 5.5}
    ]
    
    for i, tier in enumerate(storage_tiers):
        tier_box = FancyBboxPatch((tier['x'] - 1.2, tier['y']), 2.4, 1, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor='#6f42c1', alpha=0.2, 
                                 edgecolor='#6f42c1', linewidth=1.5)
        ax.add_patch(tier_box)
        ax.text(tier['x'], tier['y'] + 0.7, tier['name'], 
                fontsize=9, ha='center', fontweight='bold', color='#6f42c1')
        ax.text(tier['x'], tier['y'] + 0.5, tier['desc'], 
                fontsize=8, ha='center', color='#6f42c1')
        ax.text(tier['x'], tier['y'] + 0.3, tier['cost'], 
                fontsize=8, ha='center', color='#666', fontweight='bold')
        
        # Lifecycle transition arrow
        if i < len(storage_tiers) - 1:
            arrow = ConnectionPatch((tier['x'] + 1.2, tier['y'] + 0.5), 
                                   (storage_tiers[i+1]['x'] - 1.2, tier['y'] + 0.5), 
                                   "data", "data", arrowstyle="->", 
                                   shrinkA=2, shrinkB=2, mutation_scale=8, 
                                   fc="#6f42c1", ec="#6f42c1", linewidth=1)
            ax.add_artist(arrow)
    
    # Log formats and structure
    ax.text(11, 4.2, 'Standardized Log Formats & Structure', 
            fontsize=14, fontweight='bold', ha='center', color='#e83e8c')
    
    log_formats = [
        {
            'format': 'JSON Structured Logs',
            'example': '{"timestamp": "2024-01-01T12:00:00Z", "level": "INFO", "service": "risk-api"}',
            'use_case': 'Application logs, API responses, service communications'
        },
        {
            'format': 'Apache Common Log Format',
            'example': '10.0.1.100 - - [01/Jan/2024:12:00:00 +0000] "GET /api/risk HTTP/1.1" 200 1024',
            'use_case': 'Web server access logs, load balancer logs'
        },
        {
            'format': 'AWS CloudTrail Format',
            'example': '{"eventVersion": "1.05", "userIdentity": {"type": "IAMUser"}, "eventName": "AssumeRole"}',
            'use_case': 'AWS API calls, security events, compliance auditing'
        }
    ]
    
    for i, fmt in enumerate(log_formats):
        y_pos = 3.5 - i*0.8
        
        # Format box
        fmt_box = FancyBboxPatch((1, y_pos), 20, 0.7, boxstyle="round,pad=0.03", 
                                facecolor='#e83e8c', alpha=0.1, 
                                edgecolor='#e83e8c', linewidth=1)
        ax.add_patch(fmt_box)
        
        ax.text(2, y_pos + 0.55, fmt['format'], 
                fontsize=10, fontweight='bold', color='#e83e8c')
        ax.text(2, y_pos + 0.35, f"Example: {fmt['example'][:60]}...", 
                fontsize=8, color='#e83e8c', family='monospace')
        ax.text(2, y_pos + 0.15, f"Use Case: {fmt['use_case']}", 
                fontsize=8, color='#666', style='italic')
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/log_aggregation_architecture.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/log_aggregation_architecture.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ Log Aggregation & Collection Architecture diagram generated")

def create_log_retention_lifecycle():
    """Generate Log Retention & Lifecycle Management diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(10, 14.5, 'Log Retention & Lifecycle Management', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(10, 14, 'Automated Retention Policies & Storage Optimization', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # Retention timeline
    ax.text(10, 13.2, 'Log Retention Timeline & Storage Lifecycle', 
            fontsize=14, fontweight='bold', ha='center', color='#28a745')
    
    # Timeline visualization
    timeline_stages = [
        {'stage': 'Active', 'duration': '0-30 days', 'storage': 'CloudWatch Logs', 'cost': 'High', 'access': 'Real-time', 'x': 2},
        {'stage': 'Recent', 'duration': '30-90 days', 'storage': 'S3 Standard', 'cost': 'Medium', 'access': 'Fast', 'x': 6},
        {'stage': 'Archive', 'duration': '90 days-1 year', 'storage': 'S3 IA', 'cost': 'Low', 'access': 'Minutes', 'x': 10},
        {'stage': 'Cold', 'duration': '1-7 years', 'storage': 'S3 Glacier', 'cost': 'Very Low', 'access': 'Hours', 'x': 14},
        {'stage': 'Compliance', 'duration': '7+ years', 'storage': 'Glacier Deep', 'cost': 'Minimal', 'access': '12+ hours', 'x': 18}
    ]
    
    # Draw timeline
    timeline_y = 11.5
    for i, stage in enumerate(timeline_stages):
        # Stage box
        stage_color = ['#dc3545', '#fd7e14', '#ffc107', '#28a745', '#17a2b8'][i]
        stage_box = FancyBboxPatch((stage['x'] - 1.5, timeline_y), 3, 1.5, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor=stage_color, alpha=0.3, 
                                  edgecolor=stage_color, linewidth=2)
        ax.add_patch(stage_box)
        
        ax.text(stage['x'], timeline_y + 1.2, stage['stage'], 
                fontsize=10, ha='center', fontweight='bold', color=stage_color)
        ax.text(stage['x'], timeline_y + 1.0, stage['duration'], 
                fontsize=9, ha='center', color=stage_color)
        ax.text(stage['x'], timeline_y + 0.8, stage['storage'], 
                fontsize=8, ha='center', color=stage_color, fontweight='bold')
        ax.text(stage['x'], timeline_y + 0.6, f"Cost: {stage['cost']}", 
                fontsize=8, ha='center', color='#666')
        ax.text(stage['x'], timeline_y + 0.4, f"Access: {stage['access']}", 
                fontsize=8, ha='center', color='#666')
        
        # Arrow to next stage
        if i < len(timeline_stages) - 1:
            arrow = ConnectionPatch((stage['x'] + 1.5, timeline_y + 0.75), 
                                   (timeline_stages[i+1]['x'] - 1.5, timeline_y + 0.75), 
                                   "data", "data", arrowstyle="->", 
                                   shrinkA=2, shrinkB=2, mutation_scale=12, 
                                   fc="#28a745", ec="#28a745", linewidth=2)
            ax.add_artist(arrow)
    
    # Retention policies by log type
    ax.text(10, 9.5, 'Retention Policies by Log Type', 
            fontsize=14, fontweight='bold', ha='center', color='#6f42c1')
    
    retention_policies = [
        {
            'log_type': 'Application Logs',
            'active_period': '30 days',
            'archive_period': '1 year',
            'compliance_period': 'N/A',
            'rationale': 'Debugging, performance monitoring',
            'color': '#dc3545'
        },
        {
            'log_type': 'Access Logs',
            'active_period': '90 days',
            'archive_period': '2 years',
            'compliance_period': 'N/A',
            'rationale': 'Security analysis, traffic patterns',
            'color': '#fd7e14'
        },
        {
            'log_type': 'Security Logs',
            'active_period': '180 days',
            'archive_period': '3 years',
            'compliance_period': '7 years',
            'rationale': 'Incident response, compliance',
            'color': '#e83e8c'
        },
        {
            'log_type': 'Audit Logs',
            'active_period': '365 days',
            'archive_period': '5 years',
            'compliance_period': '10 years',
            'rationale': 'Regulatory compliance, legal',
            'color': '#17a2b8'
        },
        {
            'log_type': 'Database Logs',
            'active_period': '60 days',
            'archive_period': '1 year',
            'compliance_period': 'N/A',
            'rationale': 'Performance tuning, troubleshooting',
            'color': '#28a745'
        }
    ]
    
    for i, policy in enumerate(retention_policies):
        y_pos = 8.7 - i*0.8
        
        # Policy box
        policy_box = FancyBboxPatch((1, y_pos), 18, 0.7, boxstyle="round,pad=0.03", 
                                   facecolor=policy['color'], alpha=0.2, 
                                   edgecolor=policy['color'], linewidth=1.5)
        ax.add_patch(policy_box)
        
        ax.text(2, y_pos + 0.5, policy['log_type'], 
                fontsize=10, fontweight='bold', color=policy['color'])
        ax.text(2, y_pos + 0.25, f"Active: {policy['active_period']} | Archive: {policy['archive_period']} | Compliance: {policy['compliance_period']}", 
                fontsize=9, color=policy['color'])
        ax.text(12, y_pos + 0.35, f"Rationale: {policy['rationale']}", 
                fontsize=8, color='#666', style='italic')
    
    # Lifecycle automation
    ax.text(10, 4.5, 'Automated Lifecycle Management', 
            fontsize=14, fontweight='bold', ha='center', color='#ff9900')
    
    automation_features = [
        {
            'feature': 'S3 Lifecycle Policies',
            'description': 'Automated transition between storage classes based on age',
            'implementation': 'CloudFormation templates with lifecycle rules',
            'benefit': '60-80% cost reduction for long-term storage'
        },
        {
            'feature': 'CloudWatch Logs Retention',
            'description': 'Automatic log group retention policy enforcement',
            'implementation': 'Lambda function to set retention periods',
            'benefit': 'Consistent retention across all log groups'
        },
        {
            'feature': 'Compliance Monitoring',
            'description': 'Automated monitoring of retention policy compliance',
            'implementation': 'AWS Config rules with compliance dashboards',
            'benefit': 'Proactive compliance management and reporting'
        }
    ]
    
    for i, feature in enumerate(automation_features):
        y_pos = 3.8 - i*1
        
        # Feature box
        feature_box = FancyBboxPatch((1, y_pos), 18, 0.9, boxstyle="round,pad=0.05", 
                                    facecolor='#ff9900', alpha=0.1, 
                                    edgecolor='#ff9900', linewidth=1.5)
        ax.add_patch(feature_box)
        
        ax.text(2, y_pos + 0.7, feature['feature'], 
                fontsize=11, fontweight='bold', color='#ff9900')
        ax.text(2, y_pos + 0.5, feature['description'], 
                fontsize=9, color='#ff9900')
        ax.text(2, y_pos + 0.3, f"Implementation: {feature['implementation']}", 
                fontsize=8, color='#666')
        ax.text(2, y_pos + 0.1, f"Benefit: {feature['benefit']}", 
                fontsize=8, color='#666', style='italic', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/log_retention_lifecycle.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/log_retention_lifecycle.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ Log Retention & Lifecycle Management diagram generated")

def create_cross_account_sharing():
    """Generate Cross-Account Log Sharing & Access diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(11, 14.5, 'Cross-Account Log Sharing & Access', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(11, 14, 'Multi-Account Logging Architecture & Centralized Log Management', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # Account structure
    ax.text(11, 13.2, 'Multi-Account Logging Architecture', 
            fontsize=14, fontweight='bold', ha='center', color='#17a2b8')
    
    # AWS Accounts
    accounts = [
        {'name': 'Production Account', 'id': '111122223333', 'role': 'Log Producer', 'x': 4, 'y': 11.5, 'color': '#dc3545'},
        {'name': 'UAT Account', 'id': '444455556666', 'role': 'Log Producer', 'x': 8, 'y': 11.5, 'color': '#ffc107'},
        {'name': 'Development Account', 'id': '777788889999', 'role': 'Log Producer', 'x': 12, 'y': 11.5, 'color': '#28a745'},
        {'name': 'Security Account', 'id': '000011112222', 'role': 'Log Consumer', 'x': 16, 'y': 11.5, 'color': '#6f42c1'},
        {'name': 'Logging Account', 'id': '333344445555', 'role': 'Central Hub', 'x': 10, 'y': 9, 'color': '#17a2b8'}
    ]
    
    for account in accounts:
        # Account box
        if account['role'] == 'Central Hub':
            width, height = 4, 1.5
        else:
            width, height = 3, 1.2
            
        account_box = FancyBboxPatch((account['x'] - width/2, account['y']), width, height, 
                                    boxstyle="round,pad=0.05", 
                                    facecolor=account['color'], alpha=0.3, 
                                    edgecolor=account['color'], linewidth=2)
        ax.add_patch(account_box)
        
        ax.text(account['x'], account['y'] + height*0.7, account['name'], 
                fontsize=10, ha='center', fontweight='bold', color=account['color'])
        ax.text(account['x'], account['y'] + height*0.5, account['id'], 
                fontsize=9, ha='center', color=account['color'], family='monospace')
        ax.text(account['x'], account['y'] + height*0.3, account['role'], 
                fontsize=8, ha='center', color='#666', fontweight='bold')
        
        # Connection to central logging account
        if account['role'] != 'Central Hub':
            arrow = ConnectionPatch((account['x'], account['y']), (10, 10.5), 
                                   "data", "data", arrowstyle="->", 
                                   shrinkA=20, shrinkB=20, mutation_scale=12, 
                                   fc=account['color'], ec=account['color'], 
                                   linewidth=2, alpha=0.7)
            ax.add_artist(arrow)
    
    # Cross-account access patterns
    ax.text(11, 7.5, 'Cross-Account Access Patterns & Permissions', 
            fontsize=14, fontweight='bold', ha='center', color='#e83e8c')
    
    access_patterns = [
        {
            'pattern': 'Log Destination Sharing',
            'description': 'CloudWatch Logs destinations shared across accounts',
            'implementation': 'Cross-account IAM roles with AssumeRole permissions',
            'security': 'Least privilege access with MFA requirements'
        },
        {
            'pattern': 'S3 Cross-Account Access',
            'description': 'Centralized S3 bucket with cross-account write permissions',
            'implementation': 'Bucket policies with account-specific prefixes',
            'security': 'Server-side encryption with account-specific KMS keys'
        },
        {
            'pattern': 'Kinesis Data Streams',
            'description': 'Shared Kinesis streams for real-time log processing',
            'implementation': 'Cross-account Kinesis resource policies',
            'security': 'VPC endpoints for secure in-transit encryption'
        }
    ]
    
    for i, pattern in enumerate(access_patterns):
        y_pos = 6.8 - i*1.2
        
        # Pattern box
        pattern_box = FancyBboxPatch((1, y_pos), 20, 1, boxstyle="round,pad=0.05", 
                                    facecolor='#e83e8c', alpha=0.1, 
                                    edgecolor='#e83e8c', linewidth=1.5)
        ax.add_patch(pattern_box)
        
        ax.text(2, y_pos + 0.8, pattern['pattern'], 
                fontsize=11, fontweight='bold', color='#e83e8c')
        ax.text(2, y_pos + 0.6, pattern['description'], 
                fontsize=9, color='#e83e8c')
        ax.text(2, y_pos + 0.4, f"Implementation: {pattern['implementation']}", 
                fontsize=8, color='#666')
        ax.text(2, y_pos + 0.2, f"Security: {pattern['security']}", 
                fontsize=8, color='#666', style='italic')
    
    # Access control matrix
    ax.text(11, 3.5, 'Access Control Matrix & Permissions', 
            fontsize=14, fontweight='bold', ha='center', color='#28a745')
    
    access_matrix = [
        {'role': 'Security Team', 'read_access': 'All accounts', 'write_access': 'Security logs only', 'admin_access': 'Security account'},
        {'role': 'DevOps Team', 'read_access': 'Prod, UAT, Dev', 'write_access': 'Dev environment', 'admin_access': 'Logging account'},
        {'role': 'Compliance Team', 'read_access': 'All accounts', 'write_access': 'None', 'admin_access': 'Audit reports only'},
        {'role': 'Development Team', 'read_access': 'Dev account only', 'write_access': 'Dev logs only', 'admin_access': 'None'}
    ]
    
    for i, access in enumerate(access_matrix):
        y_pos = 2.8 - i*0.4
        
        # Access row
        access_box = FancyBboxPatch((1, y_pos), 20, 0.35, boxstyle="round,pad=0.02", 
                                   facecolor='#28a745', alpha=0.1, 
                                   edgecolor='#28a745', linewidth=1)
        ax.add_patch(access_box)
        
        ax.text(2, y_pos + 0.18, access['role'], 
                fontsize=9, fontweight='bold', color='#28a745')
        ax.text(7, y_pos + 0.18, f"Read: {access['read_access']}", 
                fontsize=8, color='#28a745')
        ax.text(12, y_pos + 0.18, f"Write: {access['write_access']}", 
                fontsize=8, color='#666')
        ax.text(17, y_pos + 0.18, f"Admin: {access['admin_access']}", 
                fontsize=8, color='#666')
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/cross_account_log_sharing.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/cross_account_log_sharing.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ Cross-Account Log Sharing & Access diagram generated")

def create_compliance_logging_audit():
    """Generate Compliance Logging & Audit Trail diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(10, 14.5, 'Compliance Logging & Audit Trail', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(10, 14, 'Regulatory Compliance & Comprehensive Audit Trail Management', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # Compliance frameworks
    ax.text(10, 13.2, 'Compliance Framework Coverage', 
            fontsize=14, fontweight='bold', ha='center', color='#dc3545')
    
    compliance_frameworks = [
        {
            'framework': 'SOC 2 Type II',
            'requirements': ['Access logging', 'Change management', 'Data encryption', 'Monitoring controls'],
            'retention': '3 years',
            'audit_frequency': 'Annual',
            'color': '#dc3545'
        },
        {
            'framework': 'PCI DSS',
            'requirements': ['Cardholder data access', 'Network monitoring', 'Vulnerability scans', 'Incident response'],
            'retention': '1 year',
            'audit_frequency': 'Quarterly',
            'color': '#fd7e14'
        },
        {
            'framework': 'GDPR',
            'requirements': ['Data processing logs', 'Consent tracking', 'Breach notifications', 'Right to erasure'],
            'retention': '6 years',
            'audit_frequency': 'Ongoing',
            'color': '#28a745'
        },
        {
            'framework': 'HIPAA',
            'requirements': ['PHI access logs', 'Audit controls', 'Authentication', 'Transmission security'],
            'retention': '6 years',
            'audit_frequency': 'Annual',
            'color': '#6f42c1'
        }
    ]
    
    for i, framework in enumerate(compliance_frameworks):
        y_pos = 12.3 - i*1.4
        
        # Framework box
        framework_box = FancyBboxPatch((1, y_pos), 18, 1.2, boxstyle="round,pad=0.05", 
                                      facecolor=framework['color'], alpha=0.2, 
                                      edgecolor=framework['color'], linewidth=2)
        ax.add_patch(framework_box)
        
        ax.text(2, y_pos + 0.9, framework['framework'], 
                fontsize=12, fontweight='bold', color=framework['color'])
        ax.text(2, y_pos + 0.6, f"Requirements: {', '.join(framework['requirements'][:2])}", 
                fontsize=9, color=framework['color'])
        ax.text(2, y_pos + 0.4, f"Additional: {', '.join(framework['requirements'][2:])}", 
                fontsize=9, color=framework['color'])
        ax.text(14, y_pos + 0.7, f"Retention: {framework['retention']}", 
                fontsize=9, color='#666', fontweight='bold')
        ax.text(14, y_pos + 0.5, f"Audit: {framework['audit_frequency']}", 
                fontsize=9, color='#666')
    
    # Audit trail components
    ax.text(10, 7.5, 'Comprehensive Audit Trail Components', 
            fontsize=14, fontweight='bold', ha='center', color='#17a2b8')
    
    audit_components = [
        {
            'component': 'AWS CloudTrail',
            'coverage': 'All AWS API calls and management events',
            'format': 'JSON with digital signatures for integrity',
            'storage': 'S3 with cross-region replication',
            'retention': '10 years (compliance requirement)'
        },
        {
            'component': 'Application Audit Logs',
            'coverage': 'User actions, data access, business transactions',
            'format': 'Structured JSON with correlation IDs',
            'storage': 'CloudWatch Logs → S3 lifecycle',
            'retention': '7 years (business requirement)'
        },
        {
            'component': 'Database Activity Streams',
            'coverage': 'All database queries and data modifications',
            'format': 'Real-time encrypted streams to Kinesis',
            'storage': 'Kinesis Data Firehose → S3',
            'retention': '5 years (regulatory requirement)'
        },
        {
            'component': 'Security Event Logs',
            'coverage': 'Authentication, authorization, security incidents',
            'format': 'SIEM-compatible with threat intelligence',
            'storage': 'Security-dedicated S3 bucket',
            'retention': '10 years (security policy)'
        }
    ]
    
    for i, component in enumerate(audit_components):
        y_pos = 6.7 - i*1.2
        
        # Component box
        comp_box = FancyBboxPatch((1, y_pos), 18, 1, boxstyle="round,pad=0.05", 
                                 facecolor='#17a2b8', alpha=0.1, 
                                 edgecolor='#17a2b8', linewidth=1.5)
        ax.add_patch(comp_box)
        
        ax.text(2, y_pos + 0.8, component['component'], 
                fontsize=11, fontweight='bold', color='#17a2b8')
        ax.text(2, y_pos + 0.6, f"Coverage: {component['coverage']}", 
                fontsize=9, color='#17a2b8')
        ax.text(2, y_pos + 0.4, f"Format: {component['format']}", 
                fontsize=8, color='#666')
        ax.text(11, y_pos + 0.6, f"Storage: {component['storage']}", 
                fontsize=8, color='#666')
        ax.text(11, y_pos + 0.4, f"Retention: {component['retention']}", 
                fontsize=8, color='#666', fontweight='bold')
    
    # Compliance monitoring and reporting
    compliance_box = FancyBboxPatch((1, 1), 18, 1.5, boxstyle="round,pad=0.1", 
                                   facecolor='#d4edda', edgecolor='#28a745', linewidth=2)
    ax.add_patch(compliance_box)
    ax.text(10, 2.2, 'Automated Compliance Monitoring & Reporting', 
            fontsize=12, fontweight='bold', ha='center', color='#28a745')
    
    compliance_features = [
        '• Real-time compliance dashboards with automated alerting for policy violations',
        '• Quarterly compliance reports generated automatically with evidence collection',
        '• Continuous monitoring of retention policies and automated lifecycle management',
        '• Integration with external audit tools and automated evidence export capabilities'
    ]
    
    for i, feature in enumerate(compliance_features[:2]):
        ax.text(2, 1.9 - i*0.15, feature, fontsize=9, color='#28a745')
    for i, feature in enumerate(compliance_features[2:]):
        ax.text(2, 1.6 - i*0.15, feature, fontsize=9, color='#28a745')
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/compliance_logging_audit.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/compliance_logging_audit.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ Compliance Logging & Audit Trail diagram generated")

def create_documentation():
    """Create comprehensive documentation for CloudWatch logging architecture"""
    doc_content = f"""# CloudWatch Logging Architecture Diagrams

*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

This document provides comprehensive analysis of the CloudWatch logging architecture diagrams for the Risk Management Platform infrastructure.

## Overview

The CloudWatch logging architecture diagrams illustrate the comprehensive logging framework including centralized log aggregation, automated lifecycle management, cross-account sharing, and regulatory compliance. These diagrams demonstrate enterprise-grade logging infrastructure with robust data retention, security controls, and audit capabilities.

## Generated Diagrams

### 1. Log Aggregation & Collection Architecture
**File**: `log_aggregation_architecture.png/.svg`

This diagram shows the complete log collection and aggregation infrastructure.

**Log Sources & Daily Volumes**:
- **Risk API Services**: Application logs (~50GB/day) with structured JSON formatting
- **Web Applications**: Access logs (~25GB/day) with Apache Common Log Format
- **Database Systems**: Query logs (~15GB/day) with performance metrics
- **Infrastructure**: System logs (~10GB/day) with CloudWatch agent
- **Security Systems**: Audit logs (~5GB/day) with security event correlation

**Central Aggregation**: Amazon CloudWatch Logs serving as the central hub with:
- **Log Groups**: 25+ organized by service and environment
- **Log Streams**: 500+ individual stream endpoints
- **Total Daily Volume**: ~105GB across all sources
- **Retention Management**: Automated retention policies per log type

**Log Processing Services**:
1. **Kinesis Data Firehose**: Real-time streaming to S3 and OpenSearch Service
2. **Lambda Log Processor**: Custom transformation and filtering logic
3. **OpenSearch Service**: Advanced search, visualization, and alerting capabilities

**Storage Tier Architecture**:
- **S3 Standard**: Active logs (30 days) at $0.023/GB for immediate access
- **S3 Intelligent-Tiering**: Frequent access logs (90 days) at $0.0125/GB with automatic optimization
- **S3 Standard-IA**: Compliance logs (1 year) at $0.0125/GB for infrequent access
- **S3 Glacier**: Long-term archive (7+ years) at $0.004/GB for compliance retention

**Standardized Log Formats**:
1. **JSON Structured Logs**: Application logs with timestamp, level, service metadata
2. **Apache Common Log Format**: Web server access logs with standardized fields
3. **AWS CloudTrail Format**: API calls with user identity and event details

### 2. Log Retention & Lifecycle Management
**File**: `log_retention_lifecycle.png/.svg`

Automated retention policies and storage optimization across the complete log lifecycle.

**Storage Lifecycle Stages**:
1. **Active (0-30 days)**: CloudWatch Logs with real-time access and high cost
2. **Recent (30-90 days)**: S3 Standard with fast access and medium cost
3. **Archive (90 days-1 year)**: S3 IA with minute-level access and low cost
4. **Cold (1-7 years)**: S3 Glacier with hour-level access and very low cost
5. **Compliance (7+ years)**: Glacier Deep Archive with 12+ hour access and minimal cost

**Retention Policies by Log Type**:

- **Application Logs**: 30 days active, 1 year archive for debugging and performance monitoring
- **Access Logs**: 90 days active, 2 years archive for security analysis and traffic patterns
- **Security Logs**: 180 days active, 3 years archive, 7 years compliance for incident response
- **Audit Logs**: 365 days active, 5 years archive, 10 years compliance for regulatory requirements
- **Database Logs**: 60 days active, 1 year archive for performance tuning and troubleshooting

**Automated Lifecycle Management**:
1. **S3 Lifecycle Policies**: CloudFormation templates with automated transitions achieving 60-80% cost reduction
2. **CloudWatch Logs Retention**: Lambda functions enforcing consistent retention across all log groups
3. **Compliance Monitoring**: AWS Config rules with dashboards for proactive compliance management

### 3. Cross-Account Log Sharing & Access
**File**: `cross_account_log_sharing.png/.svg`

Multi-account logging architecture with centralized management and controlled access.

**Account Structure**:
- **Production Account** (111122223333): Primary log producer with high-volume application logs
- **UAT Account** (444455556666): Testing environment log producer with validation workflows
- **Development Account** (777788889999): Development log producer with debug-level logging
- **Security Account** (000011112222): Log consumer with security analysis and incident response
- **Logging Account** (333344445555): Central hub for consolidated log management and long-term storage

**Cross-Account Access Patterns**:

1. **Log Destination Sharing**: CloudWatch Logs destinations with cross-account IAM roles and MFA requirements
2. **S3 Cross-Account Access**: Centralized bucket with account-specific prefixes and KMS encryption
3. **Kinesis Data Streams**: Shared streams with cross-account policies and VPC endpoint security

**Access Control Matrix**:
- **Security Team**: Read access to all accounts, write access to security logs, admin access to security account
- **DevOps Team**: Read access to Prod/UAT/Dev, write access to Dev environment, admin access to logging account
- **Compliance Team**: Read access to all accounts, no write access, audit report access only
- **Development Team**: Read access to Dev account only, write access to Dev logs only, no admin access

### 4. Compliance Logging & Audit Trail
**File**: `compliance_logging_audit.png/.svg`

Comprehensive compliance framework and audit trail management.

**Compliance Framework Coverage**:

1. **SOC 2 Type II**: Access logging, change management, data encryption, monitoring controls (3-year retention, annual audits)
2. **PCI DSS**: Cardholder data access, network monitoring, vulnerability scans, incident response (1-year retention, quarterly audits)
3. **GDPR**: Data processing logs, consent tracking, breach notifications, right to erasure (6-year retention, ongoing compliance)
4. **HIPAA**: PHI access logs, audit controls, authentication, transmission security (6-year retention, annual audits)

**Comprehensive Audit Trail Components**:

1. **AWS CloudTrail**: All AWS API calls with JSON format, digital signatures, S3 cross-region replication (10-year retention)
2. **Application Audit Logs**: User actions, data access, business transactions with structured JSON and correlation IDs (7-year retention)
3. **Database Activity Streams**: Real-time encrypted streams of all database queries via Kinesis Data Firehose (5-year retention)
4. **Security Event Logs**: Authentication, authorization, security incidents with SIEM compatibility (10-year retention)

**Automated Compliance Features**:
- Real-time compliance dashboards with automated policy violation alerting
- Quarterly compliance reports with automatic generation and evidence collection
- Continuous retention policy monitoring with automated lifecycle management
- External audit tool integration with automated evidence export capabilities

## Logging Infrastructure Framework

### Log Collection Strategy
Comprehensive log collection across all infrastructure tiers:

1. **Application-Level Logging**: Structured JSON logs with correlation IDs and contextual metadata
2. **Infrastructure Logging**: System metrics, performance data, and resource utilization
3. **Security Logging**: Authentication events, authorization decisions, and security incidents
4. **Compliance Logging**: Regulatory-required events with long-term retention and immutable storage

### Data Processing Pipeline
Advanced log processing and enrichment:

1. **Real-Time Processing**: Kinesis Data Streams for immediate log analysis and alerting
2. **Batch Processing**: Lambda functions for log transformation, filtering, and enrichment
3. **Search and Analytics**: OpenSearch Service for complex queries and visualization
4. **Machine Learning**: Automated anomaly detection and intelligent log analysis

### Storage Optimization
Cost-effective storage with performance optimization:

1. **Tiered Storage**: Automated lifecycle policies for optimal cost-performance balance
2. **Compression**: Intelligent compression algorithms reducing storage costs by 60-80%
3. **Deduplication**: Elimination of redundant log entries and data optimization
4. **Indexing**: Optimized indexing strategies for fast search and retrieval

### Security and Compliance
Enterprise-grade security and regulatory compliance:

1. **Encryption**: End-to-end encryption in transit and at rest with KMS key management
2. **Access Controls**: Role-based access with least privilege and multi-factor authentication
3. **Audit Trail**: Immutable audit logs with digital signatures and integrity validation
4. **Compliance Automation**: Automated compliance monitoring and reporting

## Operational Procedures

### Log Management
1. **Capacity Planning**: Proactive monitoring of log volume growth and storage requirements
2. **Performance Optimization**: Query optimization and index management for fast log retrieval
3. **Alert Management**: Intelligent alerting based on log patterns and anomaly detection
4. **Troubleshooting**: Rapid log analysis for incident response and root cause analysis

### Security Operations
1. **Threat Detection**: Real-time analysis of security logs for threat identification
2. **Incident Response**: Rapid log correlation and forensic analysis capabilities
3. **Compliance Monitoring**: Continuous validation of logging policies and retention requirements
4. **Audit Support**: Automated evidence collection and audit trail generation

### Cost Management
1. **Storage Optimization**: Regular analysis and optimization of storage tier utilization
2. **Lifecycle Management**: Automated policy enforcement for cost-effective data retention
3. **Usage Monitoring**: Tracking of log ingestion and storage costs across all accounts
4. **Budget Control**: Proactive monitoring and alerting for cost anomalies

## Best Practices Implementation

### Logging Standards
1. **Structured Logging**: Consistent JSON formatting across all applications and services
2. **Correlation IDs**: End-to-end request tracing with unique correlation identifiers
3. **Severity Levels**: Standardized log levels (ERROR, WARN, INFO, DEBUG) with appropriate usage
4. **Contextual Metadata**: Rich metadata including user context, session information, and business context

### Performance Best Practices
1. **Asynchronous Logging**: Non-blocking log operations to maintain application performance
2. **Batching**: Efficient batch processing for high-volume log ingestion
3. **Sampling**: Intelligent sampling for high-frequency events to manage volume
4. **Indexing Strategy**: Optimized index design for common query patterns

### Security Best Practices
1. **Data Sanitization**: Removal of sensitive information from log entries
2. **Access Logging**: Comprehensive logging of all data access and system operations
3. **Integrity Protection**: Digital signatures and checksums for log integrity validation
4. **Secure Transmission**: Encrypted log transmission with certificate-based authentication

### Compliance Best Practices
1. **Retention Policies**: Automated enforcement of regulatory retention requirements
2. **Immutable Storage**: Write-once-read-many storage for compliance and legal requirements
3. **Audit Readiness**: Continuous preparation for internal and external audits
4. **Evidence Management**: Automated collection and organization of compliance evidence

---

*This documentation is automatically updated when infrastructure diagrams are regenerated. For questions about logging architecture or compliance requirements, contact the Platform Engineering Team or Compliance Team.*
"""

    with open('../docs/cloudwatch_logging_architecture_implementation.md', 'w') as f:
        f.write(doc_content)
    
    print("📖 CloudWatch Logging Architecture documentation created")

def main():
    """Main function to generate all CloudWatch logging architecture diagrams"""
    print("🚀 Starting CloudWatch Logging Architecture diagram generation...")
    print("=" * 80)
    
    try:
        # Setup
        setup_directories()
        
        # Generate all diagrams
        create_log_aggregation_architecture()
        create_log_retention_lifecycle()
        create_cross_account_sharing()
        create_compliance_logging_audit()
        
        # Create documentation
        create_documentation()
        
        print("=" * 80)
        print("✅ CloudWatch Logging Architecture diagrams completed successfully!")
        print("\nGenerated Files:")
        print("📊 4 diagrams (PNG + SVG formats)")
        print("📖 1 comprehensive documentation file")
        print("\nAll files saved to:")
        print("- Diagrams: docs/architecture/")
        print("- Documentation: docs/cloudwatch_logging_architecture_implementation.md")
        
    except Exception as e:
        print(f"❌ Error generating diagrams: {str(e)}")
        raise

if __name__ == "__main__":
    main()