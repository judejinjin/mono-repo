#!/usr/bin/env python3
"""
Emergency Access & Break-Glass Procedures Diagram Generator

This script generates comprehensive diagrams illustrating emergency access procedures,
break-glass scenarios, incident response workflows, and security controls for
emergency situations across the Risk Management Platform infrastructure.

Generated Diagrams:
1. Emergency Access Control Matrix - Emergency roles, permissions, and activation procedures
2. Break-Glass Activation Workflow - Step-by-step emergency access activation process
3. Incident Response & Escalation - Emergency response procedures and communication flows
4. Post-Incident Recovery & Audit - Recovery procedures and compliance auditing

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

def create_emergency_access_control_matrix():
    """Generate Emergency Access Control Matrix diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(11, 14.5, 'Emergency Access Control Matrix', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(11, 14, 'Emergency Roles, Permissions & Break-Glass Activation Procedures', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # Emergency access levels
    ax.text(11, 13.2, 'Emergency Access Levels & Activation Criteria', 
            fontsize=14, fontweight='bold', ha='center', color='#dc3545')
    
    emergency_levels = [
        {
            'level': 'CRITICAL (Level 1)',
            'description': 'Service completely down, data loss imminent',
            'activation_criteria': 'Production outage affecting all users',
            'max_duration': '4 hours',
            'approver': 'CTO or designated alternate',
            'color': '#dc3545',
            'y': 12.3
        },
        {
            'level': 'HIGH (Level 2)', 
            'description': 'Major service degradation, security incident',
            'activation_criteria': 'Significant performance impact or breach',
            'max_duration': '2 hours',
            'approver': 'Engineering Director + Security Lead',
            'color': '#fd7e14',
            'y': 11.7
        },
        {
            'level': 'MODERATE (Level 3)',
            'description': 'Minor service issues, configuration emergency',
            'activation_criteria': 'Limited user impact, urgent fixes needed',
            'max_duration': '1 hour',
            'approver': 'Senior Engineering Manager',
            'color': '#ffc107',
            'y': 11.1
        },
        {
            'level': 'LOW (Level 4)',
            'description': 'Preventive maintenance, planned emergency access',
            'activation_criteria': 'Scheduled maintenance requiring elevated access',
            'max_duration': '30 minutes',
            'approver': 'Team Lead + Security Review',
            'color': '#28a745',
            'y': 10.5
        }
    ]
    
    for level in emergency_levels:
        # Level box
        level_box = FancyBboxPatch((1, level['y']), 20, 0.5, boxstyle="round,pad=0.05", 
                                  facecolor=level['color'], alpha=0.2, 
                                  edgecolor=level['color'], linewidth=1.5)
        ax.add_patch(level_box)
        
        # Level details
        ax.text(2, level['y'] + 0.35, level['level'], 
                fontsize=10, fontweight='bold', color=level['color'])
        ax.text(2, level['y'] + 0.15, level['description'], 
                fontsize=9, color=level['color'])
        ax.text(10, level['y'] + 0.25, f"Criteria: {level['activation_criteria']}", 
                fontsize=8, color='#666')
        ax.text(10, level['y'] + 0.05, f"Max Duration: {level['max_duration']} | Approver: {level['approver']}", 
                fontsize=8, color='#666', style='italic')
    
    # Emergency roles and permissions
    ax.text(11, 9.7, 'Emergency Roles & Permissions Matrix', 
            fontsize=14, fontweight='bold', ha='center', color='#0066cc')
    
    emergency_roles = [
        {
            'role': 'Emergency SysAdmin',
            'permissions': ['Full AWS root access', 'Database admin rights', 'Network configuration'],
            'activation': 'Level 1-2 incidents only',
            'personnel': 'Senior DevOps Engineers (3 designated)',
            'mfa': 'Hardware token + biometric',
            'monitoring': 'All actions logged + real-time alerts',
            'color': '#dc3545'
        },
        {
            'role': 'Emergency Security Lead',
            'permissions': ['IAM policy changes', 'Security group modifications', 'Certificate management'],
            'activation': 'Level 1-3 security incidents',
            'personnel': 'Security Team Leads (2 designated)',
            'mfa': 'Hardware token + phone verification',
            'monitoring': 'Security event correlation + SIEM alerts',
            'color': '#fd7e14'
        },
        {
            'role': 'Emergency Database Admin',
            'permissions': ['Database recovery', 'Backup restoration', 'Performance tuning'],
            'activation': 'Level 1-3 data incidents',
            'personnel': 'Database Engineers (2 designated)',
            'mfa': 'Software token + manager approval',
            'monitoring': 'Database activity streams + audit logs',
            'color': '#ffc107'
        },
        {
            'role': 'Emergency Network Admin',
            'permissions': ['VPC modifications', 'Route table changes', 'Load balancer config'],
            'activation': 'Level 2-4 network incidents',
            'personnel': 'Network Engineers (2 designated)',
            'mfa': 'Software token + peer review',
            'monitoring': 'Network flow logs + change tracking',
            'color': '#28a745'
        }
    ]
    
    for i, role in enumerate(emergency_roles):
        y_pos = 8.8 - i*1.8
        
        # Role header box
        role_box = FancyBboxPatch((1, y_pos), 20, 0.4, boxstyle="round,pad=0.05", 
                                 facecolor=role['color'], alpha=0.3, 
                                 edgecolor=role['color'], linewidth=1.5)
        ax.add_patch(role_box)
        ax.text(11, y_pos + 0.2, role['role'], 
                fontsize=12, ha='center', fontweight='bold', color=role['color'])
        
        # Role details
        ax.text(2, y_pos - 0.2, f"Permissions: {', '.join(role['permissions'])}", 
                fontsize=9, color=role['color'])
        ax.text(2, y_pos - 0.4, f"Personnel: {role['personnel']}", 
                fontsize=9, color=role['color'])
        ax.text(2, y_pos - 0.6, f"Activation: {role['activation']}", 
                fontsize=9, color='#666')
        ax.text(2, y_pos - 0.8, f"MFA: {role['mfa']}", 
                fontsize=9, color='#666')
        ax.text(2, y_pos - 1.0, f"Monitoring: {role['monitoring']}", 
                fontsize=9, color='#666', style='italic')
    
    # Break-glass activation requirements
    activation_box = FancyBboxPatch((1, 0.5), 20, 1.5, boxstyle="round,pad=0.1", 
                                   facecolor='#f8d7da', edgecolor='#dc3545', linewidth=2)
    ax.add_patch(activation_box)
    ax.text(11, 1.7, 'Break-Glass Activation Requirements', 
            fontsize=12, fontweight='bold', ha='center', color='#dc3545')
    
    activation_requirements = [
        '✓ Incident ticket created with severity classification and business impact assessment',
        '✓ Manager approval obtained through secure approval workflow (Slack + email confirmation)',  
        '✓ Multi-factor authentication completed using hardware tokens and biometric verification',
        '✓ Emergency access session recorded with full audit trail and real-time monitoring enabled'
    ]
    
    for i, req in enumerate(activation_requirements[:2]):
        ax.text(2, 1.4 - i*0.15, req, fontsize=9, color='#dc3545')
    for i, req in enumerate(activation_requirements[2:]):
        ax.text(2, 1.1 - i*0.15, req, fontsize=9, color='#dc3545')
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/emergency_access_control_matrix.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/emergency_access_control_matrix.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ Emergency Access Control Matrix diagram generated")

def create_break_glass_activation_workflow():
    """Generate Break-Glass Activation Workflow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(10, 14.5, 'Break-Glass Activation Workflow', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(10, 14, 'Step-by-Step Emergency Access Activation & Monitoring Process', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # Workflow phases
    ax.text(10, 13.2, 'Emergency Access Activation Timeline', 
            fontsize=14, fontweight='bold', ha='center', color='#17a2b8')
    
    # Phase timeline
    phases = [
        {'name': 'DETECTION', 'duration': '0-5 min', 'color': '#dc3545', 'x': 2},
        {'name': 'ACTIVATION', 'duration': '5-15 min', 'color': '#fd7e14', 'x': 6},
        {'name': 'ACCESS', 'duration': '15-240 min', 'color': '#ffc107', 'x': 10},
        {'name': 'RECOVERY', 'duration': '240+ min', 'color': '#28a745', 'x': 14},
        {'name': 'AUDIT', 'duration': '24-48 hrs', 'color': '#6f42c1', 'x': 18}
    ]
    
    # Draw timeline
    timeline_y = 12.5
    for i, phase in enumerate(phases):
        # Phase box
        phase_box = FancyBboxPatch((phase['x'] - 1.5, timeline_y), 3, 0.6, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor=phase['color'], alpha=0.3, 
                                  edgecolor=phase['color'], linewidth=2)
        ax.add_patch(phase_box)
        ax.text(phase['x'], timeline_y + 0.4, phase['name'], 
                fontsize=10, ha='center', fontweight='bold', color=phase['color'])
        ax.text(phase['x'], timeline_y + 0.15, phase['duration'], 
                fontsize=8, ha='center', color=phase['color'])
        
        # Arrow to next phase
        if i < len(phases) - 1:
            arrow = ConnectionPatch((phase['x'] + 1.5, timeline_y + 0.3), 
                                   (phases[i+1]['x'] - 1.5, timeline_y + 0.3), 
                                   "data", "data", arrowstyle="->", 
                                   shrinkA=2, shrinkB=2, mutation_scale=15, 
                                   fc="#17a2b8", ec="#17a2b8", linewidth=2)
            ax.add_artist(arrow)
    
    # Detailed workflow steps
    ax.text(10, 11.5, 'Detailed Activation Steps & Controls', 
            fontsize=14, fontweight='bold', ha='center', color='#e83e8c')
    
    workflow_steps = [
        {
            'step': '1. INCIDENT DETECTION',
            'actions': [
                'Monitoring alerts triggered (CloudWatch, Grafana, PagerDuty)',
                'On-call engineer receives notification with severity assessment',
                'Initial incident triage and impact assessment completed',
                'Emergency access need determined based on incident severity'
            ],
            'timeframe': '0-5 minutes',
            'stakeholders': 'On-call Engineer, Monitoring Systems',
            'color': '#dc3545'
        },
        {
            'step': '2. APPROVAL PROCESS',
            'actions': [
                'Incident ticket created with detailed justification and business impact',
                'Manager notification sent via Slack and SMS with approval request',
                'Security team notified for high-severity incidents (Level 1-2)',
                'Approval received and documented in incident management system'
            ],
            'timeframe': '5-15 minutes',
            'stakeholders': 'Engineering Manager, Security Lead, CTO (Level 1)',
            'color': '#fd7e14'
        },
        {
            'step': '3. ACCESS ACTIVATION',
            'actions': [
                'Multi-factor authentication completed with hardware token',
                'Emergency role assumed with time-limited session (max 4 hours)',
                'Access session initiated with full audit logging enabled',
                'Real-time monitoring and alerting activated for all actions'
            ],
            'timeframe': '15 minutes - 4 hours',
            'stakeholders': 'Emergency Personnel, Security Monitoring',
            'color': '#ffc107'
        },
        {
            'step': '4. INCIDENT RESOLUTION',
            'actions': [
                'Problem resolution with minimal required changes documented',
                'Regular status updates provided to stakeholders and management',
                'Emergency session terminated immediately upon resolution',
                'Service restoration validated and monitoring confirmed normal'
            ],
            'timeframe': '4+ hours (varies)',
            'stakeholders': 'Emergency Personnel, Service Owners, Management',
            'color': '#28a745'
        },
        {
            'step': '5. POST-INCIDENT AUDIT',
            'actions': [
                'Complete audit trail review and compliance validation',
                'Post-incident review meeting scheduled within 24 hours',
                'Root cause analysis completed and preventive measures identified',
                'Process improvements documented and implemented'
            ],
            'timeframe': '24-48 hours',
            'stakeholders': 'Security Team, Management, Compliance',
            'color': '#6f42c1'
        }
    ]
    
    for i, step in enumerate(workflow_steps):
        y_start = 10.7 - i*2
        
        # Step header
        step_box = FancyBboxPatch((1, y_start), 18, 0.4, boxstyle="round,pad=0.05", 
                                 facecolor=step['color'], alpha=0.2, 
                                 edgecolor=step['color'], linewidth=1.5)
        ax.add_patch(step_box)
        ax.text(2, y_start + 0.2, step['step'], 
                fontsize=11, fontweight='bold', color=step['color'])
        ax.text(15, y_start + 0.2, f"⏱️ {step['timeframe']}", 
                fontsize=9, color=step['color'], style='italic')
        
        # Actions
        for j, action in enumerate(step['actions']):
            ax.text(2.5, y_start - 0.2 - j*0.18, f"• {action}", 
                    fontsize=8, color=step['color'])
        
        # Stakeholders
        ax.text(2, y_start - 1.1, f"👥 Stakeholders: {step['stakeholders']}", 
                fontsize=8, color='#666', style='italic')
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/break_glass_activation_workflow.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/break_glass_activation_workflow.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ Break-Glass Activation Workflow diagram generated")

def create_incident_response_escalation():
    """Generate Incident Response & Escalation diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(11, 14.5, 'Incident Response & Escalation Framework', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(11, 14, 'Emergency Response Procedures & Communication Flows', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # Escalation matrix
    ax.text(11, 13.2, 'Incident Severity & Escalation Matrix', 
            fontsize=14, fontweight='bold', ha='center', color='#dc3545')
    
    severity_levels = [
        {
            'severity': 'CRITICAL (P0)',
            'description': 'Complete service outage, data loss, security breach',
            'response_time': '5 minutes',
            'escalation': 'Immediate: CTO + Security Lead + On-call Team',
            'communication': 'All stakeholders, customer notification',
            'sla': '4 hours to resolution',
            'color': '#dc3545'
        },
        {
            'severity': 'HIGH (P1)',
            'description': 'Major functionality impaired, significant user impact',
            'response_time': '15 minutes',
            'escalation': 'Engineering Director + Service Owner + Security Review',
            'communication': 'Management team, affected service owners',
            'sla': '8 hours to resolution',
            'color': '#fd7e14'
        },
        {
            'severity': 'MEDIUM (P2)',
            'description': 'Minor functionality issues, limited user impact',
            'response_time': '30 minutes',
            'escalation': 'Senior Engineer + Team Lead + Service Owner',
            'communication': 'Engineering team, service stakeholders',
            'sla': '24 hours to resolution',
            'color': '#ffc107'
        },
        {
            'severity': 'LOW (P3)',
            'description': 'Cosmetic issues, no user impact, scheduled fixes',
            'response_time': '2 hours',
            'escalation': 'Regular team assignment, no emergency escalation',
            'communication': 'Development team only',
            'sla': '72 hours to resolution',
            'color': '#28a745'
        }
    ]
    
    for i, level in enumerate(severity_levels):
        y_pos = 12.3 - i*0.8
        
        # Severity box
        severity_box = FancyBboxPatch((1, y_pos), 20, 0.7, boxstyle="round,pad=0.05", 
                                     facecolor=level['color'], alpha=0.2, 
                                     edgecolor=level['color'], linewidth=1.5)
        ax.add_patch(severity_box)
        
        ax.text(2, y_pos + 0.5, level['severity'], 
                fontsize=10, fontweight='bold', color=level['color'])
        ax.text(2, y_pos + 0.3, level['description'], 
                fontsize=9, color=level['color'])
        ax.text(12, y_pos + 0.5, f"Response: {level['response_time']} | SLA: {level['sla']}", 
                fontsize=8, color=level['color'], fontweight='bold')
        ax.text(12, y_pos + 0.3, f"Escalation: {level['escalation']}", 
                fontsize=8, color='#666')
        ax.text(12, y_pos + 0.1, f"Communication: {level['communication']}", 
                fontsize=8, color='#666', style='italic')
    
    # Communication channels and protocols
    ax.text(11, 8.8, 'Emergency Communication Channels & Protocols', 
            fontsize=14, fontweight='bold', ha='center', color='#17a2b8')
    
    # Primary communication channels
    comm_channels = [
        {
            'channel': 'Slack Channels',
            'primary': '#incident-response',
            'secondary': '#security-alerts, #engineering-emergency',
            'usage': 'Real-time coordination and status updates',
            'automation': 'PagerDuty integration, alert routing'
        },
        {
            'channel': 'Phone/SMS',
            'primary': 'On-call rotation (PagerDuty)',
            'secondary': 'Management escalation tree',
            'usage': 'Critical alerts and out-of-band communication',
            'automation': 'Automated escalation after 10 minutes'
        },
        {
            'channel': 'Email Groups',
            'primary': 'engineering-emergency@company.com',
            'secondary': 'security-team@company.com, leadership@company.com',
            'usage': 'Formal notifications and audit trail',
            'automation': 'Incident summary and resolution reports'
        },
        {
            'channel': 'Status Page',
            'primary': 'External customer communication',
            'secondary': 'Internal stakeholder updates',
            'usage': 'Public incident status and updates',
            'automation': 'Auto-update from incident management system'
        }
    ]
    
    for i, channel in enumerate(comm_channels):
        y_pos = 8.2 - i*0.9
        
        # Channel box
        channel_box = FancyBboxPatch((1, y_pos), 20, 0.8, boxstyle="round,pad=0.05", 
                                    facecolor='#17a2b8', alpha=0.1, 
                                    edgecolor='#17a2b8', linewidth=1)
        ax.add_patch(channel_box)
        
        ax.text(2, y_pos + 0.6, channel['channel'], 
                fontsize=11, fontweight='bold', color='#17a2b8')
        ax.text(2, y_pos + 0.4, f"Primary: {channel['primary']}", 
                fontsize=9, color='#17a2b8')
        ax.text(2, y_pos + 0.2, f"Secondary: {channel['secondary']}", 
                fontsize=9, color='#17a2b8')
        ax.text(12, y_pos + 0.4, f"Usage: {channel['usage']}", 
                fontsize=9, color='#666')
        ax.text(12, y_pos + 0.2, f"Automation: {channel['automation']}", 
                fontsize=9, color='#666', style='italic')
    
    # Decision tree for emergency access
    ax.text(11, 4.8, 'Emergency Access Decision Tree', 
            fontsize=14, fontweight='bold', ha='center', color='#6f42c1')
    
    # Decision flow
    decision_nodes = [
        {'text': 'Service\nOutage?', 'x': 3, 'y': 4, 'color': '#dc3545'},
        {'text': 'Security\nIncident?', 'x': 7, 'y': 4, 'color': '#fd7e14'},
        {'text': 'Data at\nRisk?', 'x': 11, 'y': 4, 'color': '#ffc107'},
        {'text': 'Business\nImpact?', 'x': 15, 'y': 4, 'color': '#28a745'},
        {'text': 'Emergency\nAccess', 'x': 19, 'y': 4, 'color': '#6f42c1'}
    ]
    
    for i, node in enumerate(decision_nodes):
        # Node circle
        node_circle = Circle((node['x'], node['y']), 0.8, facecolor=node['color'], 
                           alpha=0.3, edgecolor=node['color'], linewidth=2)
        ax.add_patch(node_circle)
        ax.text(node['x'], node['y'], node['text'], 
                ha='center', va='center', fontsize=9, fontweight='bold', color=node['color'])
        
        # Arrow to next node
        if i < len(decision_nodes) - 1:
            arrow = ConnectionPatch((node['x'] + 0.8, node['y']), 
                                   (decision_nodes[i+1]['x'] - 0.8, node['y']), 
                                   "data", "data", arrowstyle="->", 
                                   shrinkA=5, shrinkB=5, mutation_scale=15, 
                                   fc="#6f42c1", ec="#6f42c1", linewidth=2)
            ax.add_artist(arrow)
    
    # Yes/No paths
    ax.text(3, 3.2, 'YES', ha='center', fontsize=8, color='#28a745', fontweight='bold')
    ax.text(3, 2.8, '↓', ha='center', fontsize=16, color='#28a745')
    ax.text(3, 2.5, 'Level 1\nActivation', ha='center', fontsize=8, color='#dc3545', fontweight='bold')
    
    ax.text(3, 4.8, 'NO → Continue', ha='center', fontsize=8, color='#666', style='italic')
    
    # Post-incident procedures
    post_incident_box = FancyBboxPatch((1, 0.5), 20, 1.5, boxstyle="round,pad=0.1", 
                                      facecolor='#e7f3ff', edgecolor='#0066cc', linewidth=2)
    ax.add_patch(post_incident_box)
    ax.text(11, 1.7, 'Post-Incident Procedures & Compliance', 
            fontsize=12, fontweight='bold', ha='center', color='#0066cc')
    
    post_procedures = [
        '📋 Incident post-mortem scheduled within 24 hours with all stakeholders',
        '🔍 Root cause analysis completed and documented with preventive measures',
        '📊 Compliance review of emergency access usage and audit trail validation',
        '📈 Process improvement recommendations implemented and team training updated'
    ]
    
    for i, procedure in enumerate(post_procedures[:2]):
        ax.text(2, 1.4 - i*0.15, procedure, fontsize=9, color='#0066cc')
    for i, procedure in enumerate(post_procedures[2:]):
        ax.text(2, 1.1 - i*0.15, procedure, fontsize=9, color='#0066cc')
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/incident_response_escalation.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/incident_response_escalation.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ Incident Response & Escalation diagram generated")

def create_post_incident_recovery_audit():
    """Generate Post-Incident Recovery & Audit diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 15)
    ax.axis('off')
    
    # Title
    ax.text(10, 14.5, 'Post-Incident Recovery & Audit', 
            fontsize=20, fontweight='bold', ha='center')
    ax.text(10, 14, 'Recovery Procedures, Audit Trail & Compliance Validation', 
            fontsize=14, ha='center', style='italic', color='#555')
    
    # Recovery timeline
    ax.text(10, 13.2, 'Post-Incident Recovery Timeline', 
            fontsize=14, fontweight='bold', ha='center', color='#28a745')
    
    recovery_phases = [
        {'name': 'IMMEDIATE', 'duration': '0-2 hrs', 'tasks': 'Access termination, initial assessment', 'color': '#dc3545'},
        {'name': 'SHORT-TERM', 'duration': '2-24 hrs', 'tasks': 'Post-mortem, audit review, documentation', 'color': '#fd7e14'},
        {'name': 'MEDIUM-TERM', 'duration': '1-7 days', 'tasks': 'Process improvements, team training', 'color': '#ffc107'},
        {'name': 'LONG-TERM', 'duration': '1-4 weeks', 'tasks': 'System enhancements, compliance reporting', 'color': '#28a745'}
    ]
    
    for i, phase in enumerate(recovery_phases):
        x_pos = 2 + i * 4.5
        
        # Phase box
        phase_box = FancyBboxPatch((x_pos - 1.5, 12.2), 3, 0.8, 
                                  boxstyle="round,pad=0.05", 
                                  facecolor=phase['color'], alpha=0.3, 
                                  edgecolor=phase['color'], linewidth=2)
        ax.add_patch(phase_box)
        ax.text(x_pos, 12.8, phase['name'], 
                fontsize=10, ha='center', fontweight='bold', color=phase['color'])
        ax.text(x_pos, 12.6, phase['duration'], 
                fontsize=8, ha='center', color=phase['color'])
        ax.text(x_pos, 12.35, phase['tasks'], 
                fontsize=7, ha='center', color='#666', style='italic')
        
        # Arrow to next phase
        if i < len(recovery_phases) - 1:
            arrow = ConnectionPatch((x_pos + 1.5, 12.6), (x_pos + 3, 12.6), 
                                   "data", "data", arrowstyle="->", 
                                   shrinkA=2, shrinkB=2, mutation_scale=12, 
                                   fc="#28a745", ec="#28a745")
            ax.add_artist(arrow)
    
    # Audit trail components
    ax.text(10, 11.5, 'Comprehensive Audit Trail Components', 
            fontsize=14, fontweight='bold', ha='center', color='#17a2b8')
    
    audit_components = [
        {
            'component': 'Access Logs & Authentication',
            'details': [
                'Complete MFA authentication records with timestamps',
                'Session duration and all commands/actions executed',
                'IP address, user agent, and location information',
                'Failed authentication attempts and security warnings'
            ],
            'retention': '7 years (compliance)',
            'format': 'CloudTrail + Custom audit logs'
        },
        {
            'component': 'System Changes & Modifications',
            'details': [
                'All configuration changes with before/after states',
                'Database queries executed and data accessed',
                'Infrastructure modifications and service restarts',
                'Security policy changes and permission modifications'
            ],
            'retention': '5 years (operational)',
            'format': 'Config snapshots + Change logs'
        },
        {
            'component': 'Communication & Approvals',
            'details': [
                'Approval workflow records and manager confirmations',
                'Slack conversations and incident communications',
                'Email notifications and escalation records',
                'Status page updates and customer communications'
            ],
            'retention': '3 years (business)',
            'format': 'Incident management system'
        }
    ]
    
    for i, component in enumerate(audit_components):
        y_start = 10.8 - i*2.5
        
        # Component header
        comp_box = FancyBboxPatch((1, y_start), 18, 0.4, boxstyle="round,pad=0.05", 
                                 facecolor='#17a2b8', alpha=0.2, 
                                 edgecolor='#17a2b8', linewidth=1.5)
        ax.add_patch(comp_box)
        ax.text(10, y_start + 0.2, component['component'], 
                fontsize=11, ha='center', fontweight='bold', color='#17a2b8')
        
        # Details
        for j, detail in enumerate(component['details']):
            ax.text(2, y_start - 0.3 - j*0.2, f"• {detail}", 
                    fontsize=9, color='#17a2b8')
        
        # Metadata
        ax.text(2, y_start - 1.5, f"📅 Retention: {component['retention']} | 💾 Format: {component['format']}", 
                fontsize=8, color='#666', style='italic')
    
    # Compliance and reporting
    ax.text(10, 3.5, 'Compliance Validation & Reporting', 
            fontsize=14, fontweight='bold', ha='center', color='#6f42c1')
    
    compliance_areas = [
        {
            'area': 'SOC 2 Type II Compliance',
            'requirements': 'Access controls, change management, monitoring',
            'evidence': 'Audit logs, approval workflows, security reviews',
            'frequency': 'Annual audit with quarterly reviews'
        },
        {
            'area': 'PCI DSS Compliance',
            'requirements': 'Data access logging, encryption, access restrictions',
            'evidence': 'Database access logs, encryption validation, network controls',
            'frequency': 'Quarterly scans with annual assessment'
        },
        {
            'area': 'Internal Security Policy',
            'requirements': 'Emergency access procedures, approval processes',
            'evidence': 'Process documentation, training records, incident reports',
            'frequency': 'Monthly reviews with annual policy updates'
        }
    ]
    
    for i, area in enumerate(compliance_areas):
        y_pos = 2.8 - i*0.6
        
        # Compliance box
        comp_box = FancyBboxPatch((1, y_pos), 18, 0.5, boxstyle="round,pad=0.05", 
                                 facecolor='#6f42c1', alpha=0.1, 
                                 edgecolor='#6f42c1', linewidth=1)
        ax.add_patch(comp_box)
        
        ax.text(2, y_pos + 0.35, area['area'], 
                fontsize=10, fontweight='bold', color='#6f42c1')
        ax.text(2, y_pos + 0.15, f"Requirements: {area['requirements']}", 
                fontsize=8, color='#6f42c1')
        ax.text(12, y_pos + 0.25, f"Evidence: {area['evidence']}", 
                fontsize=8, color='#666')
        ax.text(12, y_pos + 0.05, f"Frequency: {area['frequency']}", 
                fontsize=8, color='#666', style='italic')
    
    plt.tight_layout()
    plt.savefig('../docs/architecture/post_incident_recovery_audit.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/architecture/post_incident_recovery_audit.svg', format='svg', bbox_inches='tight')
    plt.close()
    
    print("✅ Post-Incident Recovery & Audit diagram generated")

def create_documentation():
    """Create comprehensive documentation for emergency access and break-glass procedures"""
    doc_content = f"""# Emergency Access & Break-Glass Procedures Diagrams

*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

This document provides comprehensive analysis of the emergency access and break-glass procedure diagrams for the Risk Management Platform infrastructure.

## Overview

The emergency access and break-glass procedure diagrams illustrate the comprehensive framework for handling emergency situations, security incidents, and critical system outages. These diagrams demonstrate enterprise-grade emergency response procedures with multi-layered approval processes, comprehensive audit trails, and robust compliance validation.

## Generated Diagrams

### 1. Emergency Access Control Matrix
**File**: `emergency_access_control_matrix.png/.svg`

This diagram shows the complete emergency access control framework including roles, permissions, and activation procedures.

**Emergency Access Levels**:

1. **CRITICAL (Level 1)** - Service completely down, data loss imminent:
   - **Activation Criteria**: Production outage affecting all users
   - **Max Duration**: 4 hours
   - **Approver**: CTO or designated alternate
   - **Use Case**: Complete service outages, critical security breaches

2. **HIGH (Level 2)** - Major service degradation, security incident:
   - **Activation Criteria**: Significant performance impact or breach
   - **Max Duration**: 2 hours
   - **Approver**: Engineering Director + Security Lead
   - **Use Case**: Major functionality impairment, security incidents

3. **MODERATE (Level 3)** - Minor service issues, configuration emergency:
   - **Activation Criteria**: Limited user impact, urgent fixes needed
   - **Max Duration**: 1 hour
   - **Approver**: Senior Engineering Manager
   - **Use Case**: Configuration emergencies, minor service issues

4. **LOW (Level 4)** - Preventive maintenance, planned emergency access:
   - **Activation Criteria**: Scheduled maintenance requiring elevated access
   - **Max Duration**: 30 minutes
   - **Approver**: Team Lead + Security Review
   - **Use Case**: Planned maintenance, preventive emergency access

**Emergency Roles & Permissions**:

- **Emergency SysAdmin**: Full AWS root access, database admin rights, network configuration
  - Personnel: 3 designated Senior DevOps Engineers
  - MFA: Hardware token + biometric verification
  - Activation: Level 1-2 incidents only
  - Monitoring: All actions logged with real-time alerts

- **Emergency Security Lead**: IAM policy changes, security group modifications, certificate management
  - Personnel: 2 designated Security Team Leads
  - MFA: Hardware token + phone verification
  - Activation: Level 1-3 security incidents
  - Monitoring: Security event correlation + SIEM alerts

- **Emergency Database Admin**: Database recovery, backup restoration, performance tuning
  - Personnel: 2 designated Database Engineers
  - MFA: Software token + manager approval
  - Activation: Level 1-3 data incidents
  - Monitoring: Database activity streams + audit logs

- **Emergency Network Admin**: VPC modifications, route table changes, load balancer config
  - Personnel: 2 designated Network Engineers
  - MFA: Software token + peer review
  - Activation: Level 2-4 network incidents
  - Monitoring: Network flow logs + change tracking

### 2. Break-Glass Activation Workflow
**File**: `break_glass_activation_workflow.png/.svg`

Step-by-step emergency access activation process with detailed timeline and controls.

**Activation Timeline**:
- **DETECTION** (0-5 min): Monitoring alerts and initial triage
- **ACTIVATION** (5-15 min): Approval process and access granting
- **ACCESS** (15-240 min): Emergency actions with full monitoring
- **RECOVERY** (240+ min): Service restoration and validation
- **AUDIT** (24-48 hrs): Post-incident review and compliance

**Detailed Workflow Steps**:

1. **INCIDENT DETECTION** (0-5 minutes):
   - Monitoring alerts triggered (CloudWatch, Grafana, PagerDuty)
   - On-call engineer receives notification with severity assessment
   - Initial incident triage and impact assessment completed
   - Emergency access need determined based on incident severity

2. **APPROVAL PROCESS** (5-15 minutes):
   - Incident ticket created with detailed justification and business impact
   - Manager notification sent via Slack and SMS with approval request
   - Security team notified for high-severity incidents (Level 1-2)
   - Approval received and documented in incident management system

3. **ACCESS ACTIVATION** (15 minutes - 4 hours):
   - Multi-factor authentication completed with hardware token
   - Emergency role assumed with time-limited session (max 4 hours)
   - Access session initiated with full audit logging enabled
   - Real-time monitoring and alerting activated for all actions

4. **INCIDENT RESOLUTION** (4+ hours):
   - Problem resolution with minimal required changes documented
   - Regular status updates provided to stakeholders and management
   - Emergency session terminated immediately upon resolution
   - Service restoration validated and monitoring confirmed normal

5. **POST-INCIDENT AUDIT** (24-48 hours):
   - Complete audit trail review and compliance validation
   - Post-incident review meeting scheduled within 24 hours
   - Root cause analysis completed and preventive measures identified
   - Process improvements documented and implemented

### 3. Incident Response & Escalation Framework
**File**: `incident_response_escalation.png/.svg`

Comprehensive incident response procedures and communication flows.

**Incident Severity Levels**:

- **CRITICAL (P0)**: Complete service outage, data loss, security breach
  - Response Time: 5 minutes
  - Escalation: Immediate CTO + Security Lead + On-call Team
  - SLA: 4 hours to resolution
  - Communication: All stakeholders, customer notification

- **HIGH (P1)**: Major functionality impaired, significant user impact
  - Response Time: 15 minutes
  - Escalation: Engineering Director + Service Owner + Security Review
  - SLA: 8 hours to resolution
  - Communication: Management team, affected service owners

- **MEDIUM (P2)**: Minor functionality issues, limited user impact
  - Response Time: 30 minutes
  - Escalation: Senior Engineer + Team Lead + Service Owner
  - SLA: 24 hours to resolution
  - Communication: Engineering team, service stakeholders

- **LOW (P3)**: Cosmetic issues, no user impact, scheduled fixes
  - Response Time: 2 hours
  - Escalation: Regular team assignment, no emergency escalation
  - SLA: 72 hours to resolution
  - Communication: Development team only

**Communication Channels**:

1. **Slack Channels**: Real-time coordination (#incident-response, #security-alerts)
   - PagerDuty integration and automated alert routing
   - Real-time status updates and team coordination

2. **Phone/SMS**: Critical alerts and out-of-band communication
   - On-call rotation through PagerDuty
   - Management escalation tree with automated escalation

3. **Email Groups**: Formal notifications and audit trail
   - engineering-emergency@company.com for incident notifications
   - Automated incident summary and resolution reports

4. **Status Page**: Public incident status and customer communication
   - External customer communication with real-time updates
   - Auto-update from incident management system

### 4. Post-Incident Recovery & Audit
**File**: `post_incident_recovery_audit.png/.svg`

Recovery procedures, audit trail validation, and compliance reporting.

**Recovery Timeline**:

- **IMMEDIATE** (0-2 hours): Access termination and initial assessment
  - Emergency access immediately terminated upon resolution
  - Initial incident summary and impact assessment completed
  - Key stakeholders notified of resolution status

- **SHORT-TERM** (2-24 hours): Post-mortem and audit review
  - Post-incident review meeting scheduled and conducted
  - Complete audit trail review and validation
  - Initial process improvement recommendations identified

- **MEDIUM-TERM** (1-7 days): Process improvements and team training
  - Root cause analysis completed with detailed findings
  - Process improvements implemented and documented
  - Team training updated based on lessons learned

- **LONG-TERM** (1-4 weeks): System enhancements and compliance reporting
  - System enhancements implemented to prevent recurrence
  - Comprehensive compliance reporting completed
  - External audit evidence prepared and documented

**Audit Trail Components**:

1. **Access Logs & Authentication**:
   - Complete MFA authentication records with timestamps
   - Session duration and all commands/actions executed
   - IP address, user agent, and location information
   - Failed authentication attempts and security warnings
   - **Retention**: 7 years (compliance)
   - **Format**: CloudTrail + Custom audit logs

2. **System Changes & Modifications**:
   - All configuration changes with before/after states
   - Database queries executed and data accessed
   - Infrastructure modifications and service restarts
   - Security policy changes and permission modifications
   - **Retention**: 5 years (operational)
   - **Format**: Config snapshots + Change logs

3. **Communication & Approvals**:
   - Approval workflow records and manager confirmations
   - Slack conversations and incident communications
   - Email notifications and escalation records
   - Status page updates and customer communications
   - **Retention**: 3 years (business)
   - **Format**: Incident management system

## Emergency Access Framework

### Security Controls
Multi-layered security framework for emergency access:

1. **Authentication Controls**: Multi-factor authentication with hardware tokens and biometric verification
2. **Authorization Controls**: Role-based access with time-limited sessions and minimal required permissions
3. **Monitoring Controls**: Real-time monitoring, audit logging, and automated alerting for all emergency actions
4. **Approval Controls**: Multi-level approval workflows with documented justification and business impact assessment

### Risk Management
Comprehensive risk management approach:

1. **Risk Assessment**: Regular assessment of emergency access risks and mitigation strategies
2. **Risk Monitoring**: Continuous monitoring of emergency access usage patterns and anomaly detection
3. **Risk Mitigation**: Automated controls to minimize risk exposure during emergency access sessions
4. **Risk Reporting**: Regular reporting on emergency access usage and risk metrics

### Compliance Framework
Enterprise-grade compliance validation:

1. **SOC 2 Type II Compliance**: Access controls, change management, and monitoring requirements
2. **PCI DSS Compliance**: Data access logging, encryption, and access restriction requirements
3. **Internal Security Policy**: Emergency access procedures and approval process compliance
4. **Regulatory Reporting**: Quarterly and annual compliance reporting with external audit support

### Business Continuity
Ensuring business continuity during emergencies:

1. **Service Restoration**: Prioritized approach to service restoration with minimal business impact
2. **Communication Management**: Clear communication channels and stakeholder notification procedures
3. **Decision Making**: Defined decision-making authority and escalation procedures for different scenarios
4. **Recovery Validation**: Comprehensive validation of service recovery and system stability

## Operational Procedures

### Emergency Access Management
1. **Access Provisioning**: Automated provisioning of emergency roles with time-limited sessions
2. **Session Monitoring**: Real-time monitoring of all emergency access sessions with automated alerts
3. **Access Termination**: Immediate termination of emergency access upon incident resolution
4. **Usage Reporting**: Regular reporting on emergency access usage patterns and trends

### Incident Management Integration
1. **Incident Detection**: Integration with monitoring systems for automated incident detection
2. **Response Coordination**: Centralized incident response coordination through dedicated tools
3. **Status Communication**: Automated status updates and stakeholder communication
4. **Resolution Tracking**: Complete tracking of incident resolution progress and outcomes

### Audit and Compliance
1. **Audit Trail Management**: Comprehensive audit trail collection and retention
2. **Compliance Validation**: Regular validation of compliance with security policies and regulations
3. **External Audits**: Support for external audits with complete documentation and evidence
4. **Process Improvement**: Continuous improvement based on audit findings and industry best practices

## Best Practices Implementation

### Emergency Access Security
1. **Principle of Least Privilege**: Emergency roles granted minimal required permissions
2. **Time-Limited Access**: All emergency sessions automatically expire after defined time limits
3. **Multi-Factor Authentication**: Strong authentication required for all emergency access
4. **Continuous Monitoring**: Real-time monitoring and alerting for all emergency actions

### Incident Response Excellence
1. **Rapid Response**: Clear procedures for rapid incident detection and response initiation
2. **Effective Communication**: Comprehensive communication strategies for all stakeholder groups
3. **Coordinated Resolution**: Well-coordinated resolution efforts with clear roles and responsibilities
4. **Learning Culture**: Post-incident learning and continuous improvement mindset

### Compliance and Governance
1. **Regulatory Compliance**: Full compliance with applicable security regulations and standards
2. **Policy Adherence**: Strict adherence to internal security policies and procedures
3. **Audit Readiness**: Continuous audit readiness with complete documentation and evidence
4. **Risk Management**: Proactive risk management with regular assessment and mitigation

---

*This documentation is automatically updated when infrastructure diagrams are regenerated. For questions about emergency access procedures or incident response, contact the Security Team or Infrastructure Engineering Team.*
"""

    with open('../docs/emergency_access_break_glass_implementation.md', 'w') as f:
        f.write(doc_content)
    
    print("📖 Emergency Access & Break-Glass Procedures documentation created")

def main():
    """Main function to generate all emergency access and break-glass procedure diagrams"""
    print("🚀 Starting Emergency Access & Break-Glass Procedures diagram generation...")
    print("=" * 80)
    
    try:
        # Setup
        setup_directories()
        
        # Generate all diagrams
        create_emergency_access_control_matrix()
        create_break_glass_activation_workflow()
        create_incident_response_escalation()
        create_post_incident_recovery_audit()
        
        # Create documentation
        create_documentation()
        
        print("=" * 80)
        print("✅ Emergency Access & Break-Glass Procedures diagrams completed successfully!")
        print("\nGenerated Files:")
        print("📊 4 diagrams (PNG + SVG formats)")
        print("📖 1 comprehensive documentation file")
        print("\nAll files saved to:")
        print("- Diagrams: docs/architecture/")
        print("- Documentation: docs/emergency_access_break_glass_implementation.md")
        
    except Exception as e:
        print(f"❌ Error generating diagrams: {str(e)}")
        raise

if __name__ == "__main__":
    main()