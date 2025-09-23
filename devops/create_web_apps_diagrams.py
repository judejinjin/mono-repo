#!/usr/bin/env python3
"""
Web Applications Architecture Diagram Generator
Creates detailed diagrams showing React-based web applications infrastructure.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
from pathlib import Path

def create_web_apps_architecture_diagram():
    """Create comprehensive web applications architecture diagram."""
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 16))
    
    # Main architecture diagram
    ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=2, rowspan=2)
    ax1.set_xlim(0, 20)
    ax1.set_ylim(0, 16)
    ax1.set_aspect('equal')
    ax1.axis('off')
    
    # Application components
    ax2 = plt.subplot2grid((3, 2), (2, 0))
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 6)
    ax2.set_aspect('equal')
    ax2.axis('off')
    
    # Build & deployment flow
    ax3 = plt.subplot2grid((3, 2), (2, 1))
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 6)
    ax3.set_aspect('equal')
    ax3.axis('off')
    
    # Define colors
    colors = {
        'corporate_network': '#E6E6FA',
        'aws_cloud': '#E8F4FD',
        'vpc': '#D4EDDA',
        'eks': '#E2E3E5',
        'react': '#61DAFB',
        'nginx': '#269539',
        'vite': '#646CFF',
        'loadbalancer': '#45B7D1',
        'ecr': '#FFA07A',
        'cdn': '#FF6B35'
    }
    
    # Main Architecture Diagram
    ax1.text(10, 15.5, 'React Web Applications Architecture', 
             fontsize=20, fontweight='bold', ha='center')
    
    # Corporate Network boundary
    corp_rect = patches.Rectangle((0.5, 0.5), 19, 14.5, linewidth=3, 
                                  edgecolor='purple', facecolor=colors['corporate_network'], alpha=0.2)
    ax1.add_patch(corp_rect)
    ax1.text(1, 14.7, 'Corporate Intranet', fontsize=14, fontweight='bold', color='purple')
    
    # AWS Cloud boundary
    aws_rect = patches.Rectangle((1, 2), 18, 12, linewidth=2, 
                                 edgecolor='blue', facecolor=colors['aws_cloud'], alpha=0.3)
    ax1.add_patch(aws_rect)
    ax1.text(1.5, 13.5, 'AWS Cloud - US-East-1', fontsize=12, fontweight='bold', color='blue')
    
    # VPC boundary
    vpc_rect = patches.Rectangle((2, 3), 16, 10, linewidth=2, 
                                 edgecolor='green', facecolor=colors['vpc'], alpha=0.3)
    ax1.add_patch(vpc_rect)
    ax1.text(2.5, 12.5, 'VPC (10.0.0.0/16)', fontsize=11, fontweight='bold', color='green')
    
    # Load Balancer (ALB)
    alb_rect = FancyBboxPatch((3, 11), 3, 1.5, boxstyle="round,pad=0.1",
                              facecolor=colors['loadbalancer'], edgecolor='black', linewidth=2)
    ax1.add_patch(alb_rect)
    ax1.text(4.5, 11.75, 'Internal ALB\n/* → Web Apps', 
             fontsize=10, fontweight='bold', ha='center', va='center')
    
    # EKS Cluster
    eks_rect = patches.Rectangle((3, 6.5), 14, 4, linewidth=2, 
                                 edgecolor='darkblue', facecolor=colors['eks'], alpha=0.4)
    ax1.add_patch(eks_rect)
    ax1.text(3.5, 10, 'EKS Cluster', fontsize=12, fontweight='bold', color='darkblue')
    
    # Web Application Pods
    web_apps = [
        ('Dashboard', 'dev', 4, 8.5),
        ('Dashboard', 'uat', 7, 8.5), 
        ('Dashboard', 'prod', 10, 8.5),
        ('Admin', 'dev', 4, 7),
        ('Admin', 'uat', 7, 7),
        ('Admin', 'prod', 10, 7)
    ]
    
    for app_name, env, x_pos, y_pos in web_apps:
        color = colors['react'] if app_name == 'Dashboard' else '#FF6B6B'
        pod_rect = FancyBboxPatch((x_pos, y_pos), 2.5, 1, boxstyle="round,pad=0.1",
                                  facecolor=color, edgecolor='black', linewidth=1)
        ax1.add_patch(pod_rect)
        ax1.text(x_pos + 1.25, y_pos + 0.5, f'{app_name}\n{env.upper()}\nPort: 3000', 
                 fontsize=8, fontweight='bold', ha='center', va='center')
    
    # Nginx/Static Assets
    for i, env in enumerate(['dev', 'uat', 'prod']):
        x_pos = 13 + i * 1.5
        nginx_rect = FancyBboxPatch((x_pos, 8), 1.2, 1.5, boxstyle="round,pad=0.1",
                                    facecolor=colors['nginx'], edgecolor='black', linewidth=1)
        ax1.add_patch(nginx_rect)
        ax1.text(x_pos + 0.6, 8.75, f'Nginx\n{env.upper()}', 
                 fontsize=8, fontweight='bold', ha='center', va='center', color='white')
    
    # Build Tools & Registry
    build_tools = [
        (7, 11, 'ECR Repository\nweb-app images', colors['ecr']),
        (11, 11, 'Vite Build\nSystem', colors['vite']),
        (15, 11, 'CDN/CloudFront\n(Future)', colors['cdn'])
    ]
    
    for x, y, label, color in build_tools:
        rect = FancyBboxPatch((x-1, y-0.75), 2, 1.5, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax1.add_patch(rect)
        ax1.text(x, y, label, fontsize=9, fontweight='bold', ha='center', va='center')
    
    # External API Integration
    api_rect = FancyBboxPatch((3, 4.5), 6, 1.5, boxstyle="round,pad=0.1",
                              facecolor='lightcoral', edgecolor='black', linewidth=2)
    ax1.add_patch(api_rect)
    ax1.text(6, 5.25, 'API Integration Layer\nFastAPI + Airflow + Dash', 
             fontsize=10, fontweight='bold', ha='center', va='center', color='white')
    
    # Add arrows showing traffic flow
    # ALB to Web Apps
    ax1.annotate('', xy=(5.5, 8.5), xytext=(4.5, 11),
                arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    
    # Web Apps to API Layer
    ax1.annotate('', xy=(6, 6), xytext=(6, 7),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))  
    
    # Application Components (ax2)
    ax2.text(5, 5.5, 'Web Application Components', fontsize=14, fontweight='bold', ha='center')
    
    components = [
        (2, 4.5, 'React 18.2\nTypeScript', colors['react']),
        (5, 4.5, 'Vite Build\nTool', colors['vite']),
        (8, 4.5, 'Tailwind CSS\nStyling', '#06B6D4'),
        (2, 3, 'React Query\nState Mgmt', '#FF4154'),
        (5, 3, 'React Router\nNavigation', '#CA4245'),  
        (8, 3, 'Headless UI\nComponents', '#66E2FF')
    ]
    
    for x, y, label, color in components:
        rect = FancyBboxPatch((x-0.7, y-0.4), 1.4, 0.8, boxstyle="round,pad=0.05",
                              facecolor=color, edgecolor='black', alpha=0.8)
        ax2.add_patch(rect)
        ax2.text(x, y, label, fontsize=8, fontweight='bold', ha='center', va='center')
    
    # Feature list
    features = [
        '• Dashboard: Risk metrics & analytics',
        '• Admin: System management interface', 
        '• Responsive design (mobile-ready)',
        '• Real-time data integration',
        '• Form validation with Zod',
        '• Toast notifications'
    ]
    
    for i, feature in enumerate(features):
        ax2.text(0.2, 1.8 - i*0.25, feature, fontsize=9, va='center')
    
    # Build & Deployment Flow (ax3)
    ax3.text(5, 5.5, 'Build & Deployment Pipeline', fontsize=14, fontweight='bold', ha='center')
    
    pipeline_steps = [
        (1, 4.5, 'Code\nCommit', 'lightblue'),
        (3, 4.5, 'npm\nBuild', colors['vite']),
        (5, 4.5, 'Docker\nImage', 'orange'),
        (7, 4.5, 'ECR\nPush', colors['ecr']),
        (9, 4.5, 'K8s\nDeploy', 'lightgreen')
    ]
    
    for x, y, label, color in pipeline_steps:
        rect = FancyBboxPatch((x-0.4, y-0.3), 0.8, 0.6, boxstyle="round,pad=0.05",
                              facecolor=color, edgecolor='black')
        ax3.add_patch(rect)
        ax3.text(x, y, label, fontsize=8, fontweight='bold', ha='center', va='center')
        
        if x < 9:
            ax3.annotate('', xy=(x+0.6, y), xytext=(x+0.4, y),
                        arrowprops=dict(arrowstyle='->', lw=1.5, color='red'))
    
    # Build optimization features
    optimizations = [
        '• Code splitting with React.lazy()',
        '• Tree shaking & minification',
        '• Asset optimization',
        '• Chunk optimization',
        '• Source maps (dev/uat only)'
    ]
    
    for i, opt in enumerate(optimizations):
        ax3.text(0.2, 3.5 - i*0.3, opt, fontsize=9, va='center')
    
    plt.tight_layout()
    return fig

def create_web_apps_user_flow_diagram():
    """Create user interaction and application flow diagram."""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 12))
    
    # User Journey Flow (ax1)
    ax1.set_xlim(0, 18)
    ax1.set_ylim(0, 8)
    ax1.set_aspect('equal')
    ax1.axis('off')
    ax1.text(9, 7.5, 'User Journey & Application Flow', 
             fontsize=16, fontweight='bold', ha='center')
    
    # User types and entry points
    users = [
        (2, 6, 'Risk\nAnalyst', 'lightblue'),
        (6, 6, 'Portfolio\nManager', 'lightgreen'),
        (10, 6, 'System\nAdmin', 'orange'),
        (14, 6, 'Executive\nUser', 'lightcoral')
    ]
    
    for x, y, label, color in users:
        rect = FancyBboxPatch((x-0.8, y-0.5), 1.6, 1, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax1.add_patch(rect)
        ax1.text(x, y, label, fontsize=10, fontweight='bold', ha='center', va='center')
    
    # Application interfaces
    apps = [
        (4, 4, 'Dashboard\nApplication', '#61DAFB'),
        (8, 4, 'Dash Analytics\nCharts', '#FF9F43'),
        (12, 4, 'Admin\nPanel', '#FF6B6B')
    ]
    
    for x, y, label, color in apps:
        rect = FancyBboxPatch((x-1.2, y-0.6), 2.4, 1.2, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax1.add_patch(rect)
        ax1.text(x, y, label, fontsize=10, fontweight='bold', ha='center', va='center')
    
    # Data flow to backend
    backend_services = [
        (3, 2, 'FastAPI\nRisk Service'),
        (7, 2, 'Database\nQueries'),
        (11, 2, 'Real-time\nUpdates'),
        (15, 2, 'Report\nGeneration')
    ]
    
    for x, y, label in backend_services:
        rect = FancyBboxPatch((x-0.8, y-0.4), 1.6, 0.8, boxstyle="round,pad=0.05",
                              facecolor='lightgray', edgecolor='black')
        ax1.add_patch(rect)
        ax1.text(x, y, label, fontsize=9, fontweight='bold', ha='center', va='center')
    
    # Add connection arrows
    # Users to applications
    connections = [
        ((2, 5.5), (4, 4.6)),  # Risk Analyst -> Dashboard
        ((6, 5.5), (8, 4.6)),  # Portfolio Manager -> Dash
        ((10, 5.5), (12, 4.6)),  # Admin -> Admin Panel
        ((14, 5.5), (4, 4.6))   # Executive -> Dashboard
    ]
    
    for (x1, y1), (x2, y2) in connections:
        ax1.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))
    
    # Applications to backend
    ax1.annotate('', xy=(8, 2.8), xytext=(8, 3.4),
                arrowprops=dict(arrowstyle='<->', lw=2, color='red'))
    
    # Performance & Monitoring (ax2)
    ax2.set_xlim(0, 18)
    ax2.set_ylim(0, 6)
    ax2.axis('off')
    ax2.text(9, 5.5, 'Performance Monitoring & Metrics', 
             fontsize=16, fontweight='bold', ha='center')
    
    # Create performance charts
    x_vals = np.linspace(1, 17, 50)
    
    # Page load times
    load_times = 1000 + 500 * np.sin(x_vals/3) + np.random.normal(0, 100, 50)
    load_times = np.clip(load_times, 500, 2000)
    
    ax2_chart1 = plt.axes([0.05, 0.1, 0.25, 0.15])
    ax2_chart1.plot(x_vals, load_times, 'b-', linewidth=2)
    ax2_chart1.set_title('Page Load Time (ms)', fontsize=10)
    ax2_chart1.set_ylim(0, 2500)
    ax2_chart1.grid(True, alpha=0.3)
    
    # Bundle sizes
    bundle_sizes = [
        ('vendor.js', 450),
        ('app.js', 280),
        ('styles.css', 95),
        ('assets', 125)
    ]
    
    ax2_chart2 = plt.axes([0.35, 0.1, 0.25, 0.15])
    bars = ax2_chart2.bar([x[0] for x in bundle_sizes], [x[1] for x in bundle_sizes])
    ax2_chart2.set_title('Bundle Sizes (KB)', fontsize=10)
    ax2_chart2.set_ylabel('Size (KB)')
    plt.setp(ax2_chart2.get_xticklabels(), rotation=45, ha='right')
    
    # User engagement metrics
    engagement_data = ['Page Views: 15.2K/day', 'Avg Session: 12.5 min', 
                      'Bounce Rate: 23%', 'API Calls: 45K/day']
    
    for i, metric in enumerate(engagement_data):
        ax2.text(11, 4.5 - i*0.5, f'• {metric}', fontsize=11, va='center')
    
    # Performance targets
    targets = ['Target Load Time: < 2s', 'Bundle Size: < 1MB total', 
              'API Response: < 500ms', 'Uptime: > 99.9%']
    
    for i, target in enumerate(targets):
        ax2.text(14, 4.5 - i*0.5, f'• {target}', fontsize=11, va='center', color='darkgreen')
    
    plt.tight_layout()
    return fig

def create_web_apps_responsive_design_diagram():
    """Create responsive design and component architecture diagram."""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.set_aspect('equal')
    ax.axis('off')
    
    ax.text(8, 11.5, 'Web Applications Component Architecture & Responsive Design', 
            fontsize=16, fontweight='bold', ha='center')
    
    # Device breakpoints
    devices = [
        (2, 9.5, 'Mobile\n< 768px', '#FF6B6B', 0.8),
        (5, 9.5, 'Tablet\n768-1024px', '#4ECDC4', 1.2),
        (8, 9.5, 'Desktop\n> 1024px', '#45B7D1', 1.6),
        (11, 9.5, 'Large Screen\n> 1440px', '#96CEB4', 2.0)
    ]
    
    for x, y, label, color, scale in devices:
        width = 1.5 * scale
        height = 1.0 * scale
        rect = FancyBboxPatch((x-width/2, y-height/2), width, height, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, fontsize=9, fontweight='bold', ha='center', va='center')
    
    # Component hierarchy
    ax.text(8, 8, 'React Component Hierarchy', fontsize=14, fontweight='bold', ha='center')
    
    # Root components
    root_components = [
        (3, 7, 'App.tsx\n(Router)', '#61DAFB'),
        (8, 7, 'Layout\nComponent', '#61DAFB'),
        (13, 7, 'Theme\nProvider', '#61DAFB')
    ]
    
    for x, y, label, color in root_components:
        rect = FancyBboxPatch((x-0.8, y-0.4), 1.6, 0.8, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, fontsize=9, fontweight='bold', ha='center', va='center')
    
    # Page components
    page_components = [
        (2, 5.5, 'Dashboard\nPage', '#FFD93D'),
        (5, 5.5, 'Reports\nPage', '#FFD93D'),
        (8, 5.5, 'Settings\nPage', '#FFD93D'),
        (11, 5.5, 'Admin\nPage', '#FFD93D'),
        (14, 5.5, 'Profile\nPage', '#FFD93D')
    ]
    
    for x, y, label, color in page_components:
        rect = FancyBboxPatch((x-0.7, y-0.3), 1.4, 0.6, boxstyle="round,pad=0.05",
                              facecolor=color, edgecolor='black')
        ax.add_patch(rect)
        ax.text(x, y, label, fontsize=8, fontweight='bold', ha='center', va='center')
    
    # UI components
    ui_components = [
        (1, 4, 'Header', '#A8E6CF'),
        (3, 4, 'Sidebar', '#A8E6CF'),
        (5, 4, 'DataTable', '#A8E6CF'),
        (7, 4, 'Charts', '#A8E6CF'),
        (9, 4, 'Forms', '#A8E6CF'),
        (11, 4, 'Modals', '#A8E6CF'),
        (13, 4, 'Buttons', '#A8E6CF'),
        (15, 4, 'Footer', '#A8E6CF')
    ]
    
    for x, y, label, color in ui_components:
        rect = FancyBboxPatch((x-0.4, y-0.2), 0.8, 0.4, boxstyle="round,pad=0.02",
                              facecolor=color, edgecolor='black')
        ax.add_patch(rect)  
        ax.text(x, y, label, fontsize=7, fontweight='bold', ha='center', va='center')
    
    # State management layer
    ax.text(8, 3, 'State Management & Data Flow', fontsize=12, fontweight='bold', ha='center')
    
    state_components = [
        (3, 2, 'React Query\nCache', '#FF4154'),
        (6, 2, 'Context API\nGlobal State', '#61DAFB'),
        (9, 2, 'React Hook\nForm State', '#EC4899'),
        (12, 2, 'Local Component\nState', '#8B5CF6')
    ]
    
    for x, y, label, color in state_components:
        rect = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, boxstyle="round,pad=0.05",
                              facecolor=color, edgecolor='black')
        ax.add_patch(rect)
        ax.text(x, y, label, fontsize=8, fontweight='bold', ha='center', va='center', color='white')
    
    # API integration layer
    api_layer = FancyBboxPatch((2, 0.5), 12, 0.8, boxstyle="round,pad=0.1",
                               facecolor='lightcoral', edgecolor='black', linewidth=2)
    ax.add_patch(api_layer)
    ax.text(8, 0.9, 'API Integration Layer (Axios + React Query)', 
            fontsize=10, fontweight='bold', ha='center', va='center', color='white')
    
    # Add connection arrows
    # Layout to pages
    ax.annotate('', xy=(8, 6.3), xytext=(8, 6.6),
               arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))
    
    # Pages to components
    ax.annotate('', xy=(8, 4.5), xytext=(8, 5.2),
               arrowprops=dict(arrowstyle='->', lw=1.5, color='green'))
    
    # Components to state
    ax.annotate('', xy=(8, 2.8), xytext=(8, 3.8),
               arrowprops=dict(arrowstyle='<->', lw=1.5, color='red'))
    
    # State to API
    ax.annotate('', xy=(8, 1.3), xytext=(8, 1.7),
               arrowprops=dict(arrowstyle='<->', lw=2, color='purple'))
    
    plt.tight_layout()
    return fig

def main():
    """Generate all Web Applications diagrams."""
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "docs" / "architecture"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating Web Applications diagrams...")
    
    # Generate architecture diagram
    fig1 = create_web_apps_architecture_diagram()
    fig1.savefig(output_dir / "web_apps_architecture.png", dpi=300, bbox_inches='tight')
    fig1.savefig(output_dir / "web_apps_architecture.svg", format='svg', bbox_inches='tight')
    plt.close(fig1)
    print("Web apps architecture diagram saved (PNG + SVG)")
    
    # Generate user flow diagram
    fig2 = create_web_apps_user_flow_diagram()
    fig2.savefig(output_dir / "web_apps_user_flow.png", dpi=300, bbox_inches='tight')
    fig2.savefig(output_dir / "web_apps_user_flow.svg", format='svg', bbox_inches='tight')
    plt.close(fig2)
    print("Web apps user flow diagram saved (PNG + SVG)")
    
    # Generate component architecture diagram
    fig3 = create_web_apps_responsive_design_diagram()
    fig3.savefig(output_dir / "web_apps_component_architecture.png", dpi=300, bbox_inches='tight')
    fig3.savefig(output_dir / "web_apps_component_architecture.svg", format='svg', bbox_inches='tight')
    plt.close(fig3)
    print("Web apps component architecture diagram saved (PNG + SVG)")
    
    print("All Web Applications diagrams generated successfully!")

if __name__ == "__main__":
    main()
