#!/usr/bin/env python3
"""
Security Framework Architecture Diagrams Generator

This script creates comprehensive visual diagrams for the security framework:
1. Authentication and authorization architecture
2. RBAC (Role-Based Access Control) matrix
3. Security middleware and validation flow
4. Multi-factor authentication workflow
5. JWT token lifecycle and management

Generated diagrams help understand the complete security implementation.
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

def create_security_shield(ax, x, y, size, color):
    """Create a security shield icon"""
    # Shield shape
    shield_x = [x, x + size*0.2, x + size*0.5, x + size*0.8, x + size, 
                x + size*0.8, x + size*0.5, x + size*0.2, x]
    shield_y = [y + size*0.3, y + size*0.1, y, y + size*0.1, y + size*0.3,
                y + size*0.7, y + size, y + size*0.7, y + size*0.3]
    
    shield = patches.Polygon(list(zip(shield_x, shield_y)), closed=True, 
                           facecolor=color, edgecolor='darkblue', linewidth=2, alpha=0.8)
    ax.add_patch(shield)

def create_authentication_flow_diagram():
    """Create authentication and authorization flow diagram"""
    
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Title
    ax.text(9, 11.5, 'Security Framework: Authentication & Authorization Flow', 
            fontsize=18, fontweight='bold', ha='center')
    
    # Define colors
    colors = {
        'user': '#FF6B6B',
        'auth': '#4ECDC4',
        'jwt': '#45B7D1',
        'rbac': '#FFE66D',
        'middleware': '#FF8C94',
        'validation': '#C7ECEE',
        'secure': '#90EE90'
    }
    
    # User Layer
    create_fancy_box(ax, 1, 9.5, 3, 1.5, 'User\n(Web/API Client)', 
                    colors['user'], 'white', 'darkred', 2)
    
    # Security shields
    create_security_shield(ax, 0.5, 8.5, 0.8, colors['secure'])
    create_security_shield(ax, 4.5, 8.5, 0.8, colors['secure'])
    
    # Authentication Layer
    auth_components = [
        {'name': 'Login\nEndpoint', 'x': 6, 'y': 10, 'width': 2, 'height': 1},
        {'name': 'Password\nValidation', 'x': 8.5, 'y': 10, 'width': 2, 'height': 1},
        {'name': 'MFA\nVerification', 'x': 11, 'y': 10, 'width': 2, 'height': 1},
        {'name': 'JWT Token\nGeneration', 'x': 13.5, 'y': 10, 'width': 2, 'height': 1}
    ]
    
    for comp in auth_components:
        create_fancy_box(ax, comp['x'], comp['y'], comp['width'], comp['height'], 
                        comp['name'], colors['auth'], 'white', 'teal', 2)
    
    # JWT Management
    jwt_rect = Rectangle((6, 8), 9.5, 1.5, linewidth=2, 
                        edgecolor='darkblue', facecolor=colors['jwt'], alpha=0.3)
    ax.add_patch(jwt_rect)
    ax.text(6.2, 9.2, 'JWT Token Management', fontsize=11, fontweight='bold', color='darkblue')
    
    jwt_components = [
        {'name': 'Token\nIssuer', 'x': 6.5, 'y': 8.2, 'width': 1.8, 'height': 0.8},
        {'name': 'Token\nValidator', 'x': 8.5, 'y': 8.2, 'width': 1.8, 'height': 0.8},
        {'name': 'Refresh\nHandler', 'x': 10.5, 'y': 8.2, 'width': 1.8, 'height': 0.8},
        {'name': 'Blacklist\nManager', 'x': 12.5, 'y': 8.2, 'width': 1.8, 'height': 0.8}
    ]
    
    for comp in jwt_components:
        create_fancy_box(ax, comp['x'], comp['y'], comp['width'], comp['height'], 
                        comp['name'], colors['jwt'], 'white', 'darkblue', 2)
    
    # RBAC Layer
    rbac_rect = Rectangle((1, 5.5), 16, 1.8, linewidth=2, 
                         edgecolor='goldenrod', facecolor=colors['rbac'], alpha=0.3)
    ax.add_patch(rbac_rect)
    ax.text(1.2, 7, 'Role-Based Access Control (RBAC)', fontsize=11, fontweight='bold', color='goldenrod')
    
    rbac_components = [
        {'name': 'Role\nManager', 'x': 1.5, 'y': 5.8, 'width': 2, 'height': 1},
        {'name': 'Permission\nMatrix', 'x': 4, 'y': 5.8, 'width': 2, 'height': 1},
        {'name': 'Resource\nAccess', 'x': 6.5, 'y': 5.8, 'width': 2, 'height': 1},
        {'name': 'Audit\nLogger', 'x': 9, 'y': 5.8, 'width': 2, 'height': 1},
        {'name': 'Session\nManager', 'x': 11.5, 'y': 5.8, 'width': 2, 'height': 1},
        {'name': 'Policy\nEngine', 'x': 14, 'y': 5.8, 'width': 2.5, 'height': 1}
    ]
    
    for comp in rbac_components:
        create_fancy_box(ax, comp['x'], comp['y'], comp['width'], comp['height'], 
                        comp['name'], colors['rbac'], 'black', 'goldenrod', 2)
    
    # Middleware Layer
    middleware_components = [
        {'name': 'Security\nMiddleware', 'x': 2, 'y': 3.5, 'width': 2.5, 'height': 1.2},
        {'name': 'Input\nValidation', 'x': 5, 'y': 3.5, 'width': 2.5, 'height': 1.2},
        {'name': 'Rate\nLimiting', 'x': 8, 'y': 3.5, 'width': 2.5, 'height': 1.2},
        {'name': 'CORS\nHandler', 'x': 11, 'y': 3.5, 'width': 2.5, 'height': 1.2},
        {'name': 'Security\nHeaders', 'x': 14, 'y': 3.5, 'width': 2.5, 'height': 1.2}
    ]
    
    for comp in middleware_components:
        create_fancy_box(ax, comp['x'], comp['y'], comp['width'], comp['height'], 
                        comp['name'], colors['middleware'], 'white', 'darkmagenta', 2)
    
    # Protected Resources
    create_fancy_box(ax, 4, 1.5, 10, 1.5, 'Protected API Endpoints & Resources\n(Risk API, Admin Panel, Data Access)', 
                    colors['validation'], 'black', 'darkcyan', 2)
    
    # Flow arrows
    # User to Authentication
    create_arrow(ax, 4, 10.2, 6, 10.5, 'blue', '->', 3)
    ax.text(5, 10.7, 'Login\nRequest', ha='center', fontsize=8, color='blue')
    
    # Authentication flow
    for i in range(3):
        create_arrow(ax, 8 + i*2.5, 10.5, 8.5 + i*2.5, 10.5, 'green', '->', 2)
    
    # Auth to JWT
    create_arrow(ax, 10.5, 10, 10.5, 9.5, 'purple', '->', 2)
    
    # JWT to RBAC
    create_arrow(ax, 10.5, 8.2, 8.5, 7.3, 'orange', '->', 2)
    
    # RBAC to Middleware
    create_arrow(ax, 8.5, 5.8, 8.5, 4.7, 'red', '->', 2)
    
    # Middleware to Resources
    create_arrow(ax, 8.5, 3.5, 8.5, 3, 'darkgreen', '->', 3)
    
    plt.tight_layout()
    
    # Save diagram
    output_dir = Path("docs/architecture")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_dir / "security_authentication_flow.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / "security_authentication_flow.svg", format='svg', bbox_inches='tight')
    plt.close()

def create_rbac_matrix_diagram():
    """Create RBAC permission matrix diagram"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Title
    ax.text(8, 11.5, 'RBAC Permission Matrix & Role Hierarchy', 
            fontsize=18, fontweight='bold', ha='center')
    
    # Define roles and permissions
    roles = ['Super Admin', 'Risk Manager', 'Analyst', 'Viewer', 'API User']
    permissions = [
        'User Management', 'System Config', 'Risk Analysis', 'Portfolio Access',
        'Market Data', 'Reports View', 'Reports Create', 'API Access', 'Admin Panel'
    ]
    
    # Permission matrix (True/False for each role-permission combination)
    matrix = [
        [True, True, True, True, True, True, True, True, True],    # Super Admin
        [False, True, True, True, True, True, True, True, True],   # Risk Manager  
        [False, False, True, True, True, True, True, True, False], # Analyst
        [False, False, False, True, True, True, False, False, False], # Viewer
        [False, False, True, True, True, False, False, True, False]   # API User
    ]
    
    # Create role hierarchy visualization
    role_hierarchy_rect = Rectangle((1, 8.5), 6, 2.5, linewidth=2, 
                                  edgecolor='darkblue', facecolor='lightblue', alpha=0.3)
    ax.add_patch(role_hierarchy_rect)
    ax.text(1.2, 10.7, 'Role Hierarchy', fontsize=12, fontweight='bold', color='darkblue')
    
    # Draw role hierarchy
    hierarchy_levels = [
        {'role': 'Super Admin', 'x': 4, 'y': 10.2, 'width': 1.8, 'height': 0.5, 'color': '#FF6B6B'},
        {'role': 'Risk Manager', 'x': 2.5, 'y': 9.5, 'width': 1.8, 'height': 0.5, 'color': '#4ECDC4'},
        {'role': 'API User', 'x': 4.5, 'y': 9.5, 'width': 1.8, 'height': 0.5, 'color': '#4ECDC4'},
        {'role': 'Analyst', 'x': 2, 'y': 8.8, 'width': 1.8, 'height': 0.5, 'color': '#45B7D1'},
        {'role': 'Viewer', 'x': 4.5, 'y': 8.8, 'width': 1.8, 'height': 0.5, 'color': '#FFE66D'}
    ]
    
    for level in hierarchy_levels:
        create_fancy_box(ax, level['x'], level['y'], level['width'], level['height'], 
                        level['role'], level['color'], 'white', 'black', 2)
    
    # Draw hierarchy connections
    create_arrow(ax, 4.9, 10.2, 3.4, 9.8, 'darkblue', '->', 1)
    create_arrow(ax, 4.9, 10.2, 5.4, 9.8, 'darkblue', '->', 1)
    create_arrow(ax, 3.4, 9.5, 2.9, 9.1, 'darkblue', '->', 1)
    create_arrow(ax, 5.4, 9.5, 5.4, 9.1, 'darkblue', '->', 1)
    
    # Permission Matrix
    matrix_rect = Rectangle((9, 3), 6.5, 8, linewidth=2, 
                          edgecolor='darkgreen', facecolor='lightgreen', alpha=0.2)
    ax.add_patch(matrix_rect)
    ax.text(9.2, 10.7, 'Permission Matrix', fontsize=12, fontweight='bold', color='darkgreen')
    
    # Create matrix headers
    # Role headers (vertical)
    for i, role in enumerate(roles):
        create_fancy_box(ax, 9.2, 9.5 - i*1.2, 1.8, 0.8, role, '#FF8C94', 'white', 'darkred', 1)
    
    # Permission headers (horizontal) - rotated
    for j, perm in enumerate(permissions):
        if j < 5:  # First row of permissions
            ax.text(11.5 + j*0.8, 10.2, perm, rotation=45, ha='left', va='bottom', 
                   fontsize=8, fontweight='bold')
        else:  # Second row of permissions
            ax.text(11.5 + (j-5)*0.8, 9.7, perm, rotation=45, ha='left', va='bottom', 
                   fontsize=8, fontweight='bold')
    
    # Create matrix cells
    for i, role in enumerate(roles):
        for j, perm in enumerate(permissions):
            has_permission = matrix[i][j]
            cell_color = 'lightgreen' if has_permission else 'lightcoral'
            symbol = '✓' if has_permission else '✗'
            symbol_color = 'darkgreen' if has_permission else 'darkred'
            
            # Adjust positioning for two-row layout
            if j < 5:
                cell_x = 11.2 + j*0.8
                cell_y = 9.5 - i*1.2 + 0.3
            else:
                cell_x = 11.2 + (j-5)*0.8
                cell_y = 9.5 - i*1.2 - 0.1
            
            cell_rect = Rectangle((cell_x, cell_y), 0.6, 0.3, 
                                facecolor=cell_color, edgecolor='black', linewidth=1, alpha=0.8)
            ax.add_patch(cell_rect)
            ax.text(cell_x + 0.3, cell_y + 0.15, symbol, ha='center', va='center', 
                   fontsize=12, fontweight='bold', color=symbol_color)
    
    # Security Features
    security_features_rect = Rectangle((1, 3), 7, 4.5, linewidth=2, 
                                     edgecolor='purple', facecolor='lavender', alpha=0.3)
    ax.add_patch(security_features_rect)
    ax.text(1.2, 7.2, 'Security Features', fontsize=12, fontweight='bold', color='purple')
    
    features = [
        {'name': 'Multi-Factor\nAuthentication', 'x': 1.5, 'y': 6.2, 'width': 2, 'height': 0.8},
        {'name': 'Session\nManagement', 'x': 4, 'y': 6.2, 'width': 2, 'height': 0.8},
        {'name': 'Audit\nLogging', 'x': 6.2, 'y': 6.2, 'width': 1.5, 'height': 0.8},
        {'name': 'Password\nPolicy', 'x': 1.5, 'y': 5.2, 'width': 2, 'height': 0.8},
        {'name': 'Input\nValidation', 'x': 4, 'y': 5.2, 'width': 2, 'height': 0.8},
        {'name': 'Rate\nLimiting', 'x': 6.2, 'y': 5.2, 'width': 1.5, 'height': 0.8},
        {'name': 'CSRF\nProtection', 'x': 1.5, 'y': 4.2, 'width': 2, 'height': 0.8},
        {'name': 'XSS\nPrevention', 'x': 4, 'y': 4.2, 'width': 2, 'height': 0.8},
        {'name': 'Security\nHeaders', 'x': 6.2, 'y': 4.2, 'width': 1.5, 'height': 0.8},
        {'name': 'Encryption\n(AES-256)', 'x': 1.5, 'y': 3.2, 'width': 2, 'height': 0.8},
        {'name': 'Token\nBlacklist', 'x': 4, 'y': 3.2, 'width': 2, 'height': 0.8},
        {'name': 'IP\nWhitelisting', 'x': 6.2, 'y': 3.2, 'width': 1.5, 'height': 0.8}
    ]
    
    for feature in features:
        create_fancy_box(ax, feature['x'], feature['y'], feature['width'], feature['height'], 
                        feature['name'], '#E6E6FA', 'black', 'purple', 1)
    
    # Compliance & Standards
    compliance_text = (
        "SECURITY COMPLIANCE\n\n"
        "• OWASP Top 10 Protection\n"
        "• SOC 2 Type II Compliance\n"
        "• GDPR Data Protection\n"
        "• PCI DSS Standards\n"
        "• ISO 27001 Controls\n"
        "• Regular Security Audits\n"
        "• Penetration Testing\n"
        "• Vulnerability Scanning"
    )
    
    ax.text(1, 2.5, compliance_text, fontsize=9, va='top', ha='left', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    
    # Save diagram
    output_dir = Path("docs/architecture")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_dir / "security_rbac_matrix.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / "security_rbac_matrix.svg", format='svg', bbox_inches='tight')
    plt.close()

def create_mfa_workflow_diagram():
    """Create multi-factor authentication workflow diagram"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Title
    ax.text(8, 9.5, 'Multi-Factor Authentication (MFA) Workflow', 
            fontsize=18, fontweight='bold', ha='center')
    
    colors = {
        'user': '#FF6B6B', 
        'step': '#4ECDC4',
        'verification': '#45B7D1',
        'success': '#90EE90',
        'failure': '#FFB6C1'
    }
    
    # User
    create_fancy_box(ax, 1, 8, 2, 1, 'User', colors['user'], 'white', 'darkred', 2)
    
    # Step 1: Username/Password
    create_fancy_box(ax, 4.5, 8, 2.5, 1, 'Step 1:\nUsername/Password', 
                    colors['step'], 'white', 'teal', 2)
    
    # Step 2: MFA Challenge
    create_fancy_box(ax, 8, 8, 2.5, 1, 'Step 2:\nMFA Challenge', 
                    colors['step'], 'white', 'teal', 2)
    
    # Step 3: Token Validation
    create_fancy_box(ax, 11.5, 8, 2.5, 1, 'Step 3:\nToken Validation', 
                    colors['step'], 'white', 'teal', 2)
    
    # MFA Methods
    mfa_methods_rect = Rectangle((2, 5.5), 12, 1.8, linewidth=2, 
                               edgecolor='darkblue', facecolor=colors['verification'], alpha=0.3)
    ax.add_patch(mfa_methods_rect)
    ax.text(2.2, 7, 'MFA Methods', fontsize=11, fontweight='bold', color='darkblue')
    
    methods = [
        {'name': 'TOTP\n(Google Auth)', 'x': 2.5, 'y': 5.8, 'width': 2, 'height': 0.8},
        {'name': 'SMS\nToken', 'x': 5, 'y': 5.8, 'width': 2, 'height': 0.8},
        {'name': 'Email\nToken', 'x': 7.5, 'y': 5.8, 'width': 2, 'height': 0.8},
        {'name': 'Hardware\nToken', 'x': 10, 'y': 5.8, 'width': 2, 'height': 0.8},
        {'name': 'Backup\nCodes', 'x': 12.5, 'y': 5.8, 'width': 1.8, 'height': 0.8}
    ]
    
    for method in methods:
        create_fancy_box(ax, method['x'], method['y'], method['width'], method['height'], 
                        method['name'], colors['verification'], 'white', 'darkblue', 2)
    
    # Validation Process
    validation_steps = [
        {'name': 'Token\nGenerated', 'x': 2, 'y': 3.5, 'width': 2, 'height': 1},
        {'name': 'User\nInput', 'x': 4.5, 'y': 3.5, 'width': 2, 'height': 1},
        {'name': 'Server\nValidation', 'x': 7, 'y': 3.5, 'width': 2, 'height': 1},
        {'name': 'Time Window\nCheck', 'x': 9.5, 'y': 3.5, 'width': 2, 'height': 1},
        {'name': 'Access\nGranted', 'x': 12, 'y': 3.5, 'width': 2, 'height': 1}
    ]
    
    for step in validation_steps:
        create_fancy_box(ax, step['x'], step['y'], step['width'], step['height'], 
                        step['name'], colors['verification'], 'white', 'darkblue', 2)
    
    # Success/Failure outcomes
    create_fancy_box(ax, 4, 1.5, 3, 1, 'SUCCESS:\nJWT Token Issued', 
                    colors['success'], 'black', 'darkgreen', 2)
    create_fancy_box(ax, 9, 1.5, 3, 1, 'FAILURE:\nAccess Denied', 
                    colors['failure'], 'black', 'darkred', 2)
    
    # Flow arrows
    # Main flow
    create_arrow(ax, 3, 8.5, 4.5, 8.5, 'blue', '->', 3)
    create_arrow(ax, 7, 8.5, 8, 8.5, 'blue', '->', 3)
    create_arrow(ax, 10.5, 8.5, 11.5, 8.5, 'blue', '->', 3)
    
    # MFA methods to validation
    create_arrow(ax, 8, 7.3, 8, 4.5, 'green', '->', 2)
    
    # Validation process flow
    for i in range(4):
        create_arrow(ax, 4 + i*2.5, 4, 4.5 + i*2.5, 4, 'purple', '->', 2)
    
    # Outcomes
    create_arrow(ax, 10, 3.5, 6, 2.5, 'green', '->', 2)
    create_arrow(ax, 10, 3.5, 10, 2.5, 'red', '->', 2)
    
    # Security considerations
    security_text = (
        "SECURITY CONSIDERATIONS\n\n"
        "• Time-based token validation (30-60 seconds)\n"
        "• Rate limiting on MFA attempts\n"
        "• Backup codes for recovery\n"
        "• Audit logging of all attempts\n"
        "• Account lockout after failures\n"
        "• Secure token transmission\n"
        "• Device registration & trust\n"
        "• Emergency access procedures"
    )
    
    ax.text(0.5, 4.5, security_text, fontsize=9, va='top', ha='left', 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcyan', alpha=0.8))
    
    plt.tight_layout()
    
    # Save diagram
    output_dir = Path("docs/architecture")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(output_dir / "security_mfa_workflow.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / "security_mfa_workflow.svg", format='svg', bbox_inches='tight')
    plt.close()

def main():
    """Generate all security framework diagrams"""
    
    print("Generating Security Framework Architecture Diagrams...")
    
    try:
        # Create output directory
        output_dir = Path("docs/architecture")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("Creating authentication flow diagram...")
        create_authentication_flow_diagram()
        
        print("Creating RBAC matrix diagram...")
        create_rbac_matrix_diagram()
        
        print("Creating MFA workflow diagram...")
        create_mfa_workflow_diagram()
        
        print("\n" + "="*80)
        print("SECURITY FRAMEWORK DIAGRAMS GENERATED SUCCESSFULLY")
        print("="*80)
        print(f"Generated diagrams saved to: {output_dir.absolute()}")
        print("\nGenerated Files:")
        print("- security_authentication_flow.png/svg")
        print("- security_rbac_matrix.png/svg")
        print("- security_mfa_workflow.png/svg")
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"Error generating diagrams: {e}")
        raise

if __name__ == "__main__":
    main()