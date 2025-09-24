#!/usr/bin/env python3
"""
Dash Analytics Application Architecture Diagram Generator
Creates detailed diagrams showing Dash analytics service infrastructure components.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
from pathlib import Path

def create_dash_architecture_diagram():
    """Create comprehensive Dash analytics architecture diagram."""
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 16))
    
    # Main architecture diagram
    ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=2, rowspan=2)
    ax1.set_xlim(0, 20)
    ax1.set_ylim(0, 16)
    ax1.set_aspect('equal')
    ax1.axis('off')
    
    # Dashboard components
    ax2 = plt.subplot2grid((3, 2), (2, 0))
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 6)
    ax2.set_aspect('equal')
    ax2.axis('off')
    
    # Interactive features
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
        'dash': '#FF9F43',
        'plotly': '#1F77B4',
        'database': '#4ECDC4',
        'loadbalancer': '#45B7D1',
        'ecr': '#FFA07A',
        'analytics': '#9B59B6'
    }
    
    # Main Architecture Diagram
    ax1.text(10, 15.5, 'Dash Analytics Application Architecture', 
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
    ax1.text(4.5, 11.75, 'Internal ALB\n/dash/* → Dash App', 
             fontsize=10, fontweight='bold', ha='center', va='center')
    
    # EKS Cluster
    eks_rect = patches.Rectangle((3, 7), 14, 3.5, linewidth=2, 
                                 edgecolor='darkblue', facecolor=colors['eks'], alpha=0.4)
    ax1.add_patch(eks_rect)
    ax1.text(3.5, 10.2, 'EKS Cluster', fontsize=12, fontweight='bold', color='darkblue')
    
    # Dash Application Pods
    for i, env in enumerate(['dev', 'uat', 'prod']):
        x_pos = 4 + i * 4
        pod_rect = FancyBboxPatch((x_pos, 8), 3, 1.5, boxstyle="round,pad=0.1",
                                  facecolor=colors['dash'], edgecolor='black', linewidth=1)
        ax1.add_patch(pod_rect)
        ax1.text(x_pos + 1.5, 8.75, f'Dash App\n{env.upper()}\nPort: 8050', 
                 fontsize=9, fontweight='bold', ha='center', va='center', color='white')
    
    # Database Services
    db_y = 5
    # PostgreSQL RDS
    for i, env in enumerate(['dev', 'uat', 'prod']):
        x_pos = 4 + i * 4
        db_rect = FancyBboxPatch((x_pos, db_y), 3, 1.2, boxstyle="round,pad=0.1",
                                 facecolor=colors['database'], edgecolor='black', linewidth=1)
        ax1.add_patch(db_rect)
        ax1.text(x_pos + 1.5, db_y + 0.6, f'PostgreSQL\nRDS {env.upper()}', 
                 fontsize=9, fontweight='bold', ha='center', va='center')
    
    # Snowflake (External Analytics) - positioned beside ECR in US-East-1 region area  
    snowflake_rect = FancyBboxPatch((11, 0.7), 3, 0.8, boxstyle="round,pad=0.1",
                                    facecolor=colors['analytics'], edgecolor='black', linewidth=2)
    ax1.add_patch(snowflake_rect)
    ax1.text(12.5, 1.1, 'Snowflake\nData Warehouse', 
             fontsize=9, fontweight='bold', ha='center', va='center', color='white')
    
    # US-East-1 Region box (matches architecture diagram) - extended to fit ECR and Snowflake
    us_east_1_rect = patches.Rectangle((3, 0.5), 14, 1.8, linewidth=2, 
                                      edgecolor='purple', facecolor='#F5F0FF', alpha=0.3)
    ax1.add_patch(us_east_1_rect)
    ax1.text(10, 1.9, 'US-East-1 Region (AWS Services & External)', ha='center', va='center', 
           fontsize=10, fontweight='bold', color='purple')
    
    # ECR Repository - moved to US-East-1 region to match architecture diagram (y=0.8 area)
    ecr_rect = FancyBboxPatch((7.5, 0.7), 3, 0.8, boxstyle="round,pad=0.1",
                              facecolor=colors['ecr'], edgecolor='black', linewidth=2)
    ax1.add_patch(ecr_rect)
    ax1.text(9, 1.1, 'ECR Repository\ndash-app images', 
             fontsize=9, fontweight='bold', ha='center', va='center')
    
    # VPC Endpoint for ECR (matches architecture diagram pattern)
    vpc_endpoint_ecr = patches.Rectangle((8, 2.8), 2, 0.4, linewidth=1, 
                                        edgecolor='gray', facecolor='lightgray', alpha=0.6)
    ax1.add_patch(vpc_endpoint_ecr)
    ax1.text(9, 3, 'ECR VPC Endpoint', ha='center', va='center', fontsize=8)
    
    # Plotly/Dash Components - moved to fill ECR's former space
    dash_components_rect = FancyBboxPatch((7, 11), 3, 1.5, boxstyle="round,pad=0.1",
                                          facecolor=colors['plotly'], edgecolor='black', linewidth=2)
    ax1.add_patch(dash_components_rect)
    ax1.text(8.5, 11.75, 'Dash Framework\n+ Plotly Charts', 
             fontsize=10, fontweight='bold', ha='center', va='center', color='white')
    
    # Analytics Engine - repositioned 
    analytics_rect = FancyBboxPatch((11, 11), 3, 1.5, boxstyle="round,pad=0.1",
                                    facecolor=colors['analytics'], edgecolor='black', linewidth=2)
    ax1.add_patch(analytics_rect)
    ax1.text(12.5, 11.75, 'Analytics\nEngine', 
             fontsize=10, fontweight='bold', ha='center', va='center', color='white')
    
    # Add arrows showing data flow
    # ALB to Dash App
    ax1.annotate('', xy=(5.5, 8), xytext=(4.5, 11),
                arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    
    # Dash App to Database
    for i in range(3):
        x_pos = 5.5 + i * 4
        ax1.annotate('', xy=(x_pos, 6.2), xytext=(x_pos, 8),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))
    
    # ECR to VPC endpoint connection (container image deployment)
    ax1.annotate('', xy=(9, 2.8), xytext=(9, 1.5),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='orange', linestyle='dashed'))
    
    # VPC endpoint to Dash Apps (image pull)
    ax1.annotate('', xy=(6, 8), xytext=(9, 3.2),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='orange', linestyle='dashed'))
    ax1.text(7, 5.5, 'Image\nPull', fontsize=7, color='orange')
    
    # Snowflake to Analytics Engine (data connection) - updated for new position
    ax1.annotate('', xy=(12.5, 11), xytext=(12.5, 1.5),
                arrowprops=dict(arrowstyle='<->', lw=1.5, color='purple'))
    ax1.text(13, 6, 'Analytics\nData', fontsize=7, color='purple', rotation=90)
    
    # Dashboard Components (ax2)
    ax2.text(5, 5.5, 'Dashboard Components', fontsize=14, fontweight='bold', ha='center')
    
    components = [
        (2, 4.5, 'Portfolio\nDropdown', colors['dash']),
        (5, 4.5, 'Date Range\nPicker', colors['dash']),
        (8, 4.5, 'VaR Chart\nVisualization', colors['plotly']),
        (2, 3, 'Volatility\nChart', colors['plotly']),
        (5, 3, 'Sharpe Ratio\nChart', colors['plotly']),
        (8, 3, 'Risk Summary\nTable', colors['analytics'])
    ]
    
    for x, y, label, color in components:
        rect = FancyBboxPatch((x-0.6, y-0.4), 1.2, 0.8, boxstyle="round,pad=0.05",
                              facecolor=color, edgecolor='black', alpha=0.8)
        ax2.add_patch(rect)
        ax2.text(x, y, label, fontsize=8, fontweight='bold', ha='center', va='center')
    
    # Interactive Features (ax3)
    ax3.text(5, 5.5, 'Interactive Features', fontsize=14, fontweight='bold', ha='center')
    
    features = [
        'Real-time portfolio filtering',
        'Date range selection',
        'Interactive Plotly charts',
        'Hover tooltips & zoom',
        'Multi-portfolio comparison',
        'Export capabilities (planned)'
    ]
    
    for i, feature in enumerate(features):
        ax3.text(0.2, 4.8 - i*0.6, f'• {feature}', fontsize=10, va='center')
    
    # Portfolio types supported
    portfolios = [
        'EQUITY_GROWTH',
        'FIXED_INCOME', 
        'BALANCED',
        'EMERGING_MARKETS'
    ]
    
    ax3.text(5.5, 3.5, 'Supported Portfolios:', fontsize=11, fontweight='bold')
    for i, portfolio in enumerate(portfolios):
        ax3.text(5.5, 3 - i*0.4, f'• {portfolio}', fontsize=9, va='center')
    
    plt.tight_layout()
    return fig

def create_dash_interactive_flow_diagram():
    """Create Dash interactive flow and callback diagram."""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    
    # Callback Flow (ax1)
    ax1.set_xlim(0, 16)
    ax1.set_ylim(0, 8)
    ax1.set_aspect('equal')
    ax1.axis('off')
    ax1.text(8, 7.5, 'Dash Callback Flow & User Interactions', 
             fontsize=16, fontweight='bold', ha='center')
    
    # User interaction flow
    flow_components = [
        (2, 6, 'User\nSelection', 'lightblue', 'Input'),
        (5, 6, 'Dash\nCallback', '#FF9F43', 'Process'),
        (8, 6, 'Data\nQuery', '#4ECDC4', 'Database'),
        (11, 6, 'Chart\nUpdate', '#1F77B4', 'Visualization'),
        (14, 6, 'Browser\nRender', 'lightgreen', 'Output')
    ]
    
    for x, y, label, color, category in flow_components:
        rect = FancyBboxPatch((x-0.8, y-0.6), 1.6, 1.2, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax1.add_patch(rect)
        ax1.text(x, y+0.2, label, fontsize=10, fontweight='bold', ha='center', va='center')
        ax1.text(x, y-0.4, category, fontsize=8, ha='center', va='center', style='italic')
    
    # Add arrows between components
    for i in range(len(flow_components) - 1):
        x1 = flow_components[i][0] + 0.8
        x2 = flow_components[i+1][0] - 0.8
        ax1.annotate('', xy=(x2, 6), xytext=(x1, 6),
                    arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    
    # Show specific callbacks
    callbacks = [
        (2, 4, 'Portfolio\nDropdown', 'Input'),
        (5, 4, 'Date Range\nPicker', 'Input'),
        (8, 4, 'update_var_chart()', 'Callback'),
        (11, 4, 'update_volatility()', 'Callback'),
        (14, 4, 'update_summary()', 'Callback')
    ]
    
    for x, y, label, cb_type in callbacks:
        color = 'lightgray' if cb_type == 'Input' else '#FF6B6B'
        rect = FancyBboxPatch((x-0.7, y-0.4), 1.4, 0.8, boxstyle="round,pad=0.05",
                              facecolor=color, edgecolor='black')
        ax1.add_patch(rect)
        ax1.text(x, y, label, fontsize=9, fontweight='bold', ha='center', va='center')
    
    # Performance Metrics (ax2)
    ax2.set_xlim(0, 16)
    ax2.set_ylim(0, 8)
    ax2.axis('off')
    ax2.text(8, 7.5, 'Dashboard Performance & Analytics', 
             fontsize=16, fontweight='bold', ha='center')
    
    # Create sample performance chart
    x_vals = np.linspace(1, 15, 50)
    response_times = 200 + 100 * np.sin(x_vals/2) + np.random.normal(0, 20, 50)
    response_times = np.clip(response_times, 50, 500)
    
    ax2_chart = plt.axes([0.1, 0.1, 0.35, 0.25])
    ax2_chart.plot(x_vals, response_times, 'b-', linewidth=2)
    ax2_chart.set_title('Response Time (ms)', fontsize=12)
    ax2_chart.set_xlabel('Time')
    ax2_chart.set_ylabel('Response (ms)')
    ax2_chart.grid(True, alpha=0.3)
    
    # Resource usage chart
    cpu_usage = 20 + 30 * np.sin(x_vals/3) + np.random.normal(0, 5, 50)
    cpu_usage = np.clip(cpu_usage, 0, 100)
    
    ax2_cpu = plt.axes([0.55, 0.1, 0.35, 0.25])
    ax2_cpu.plot(x_vals, cpu_usage, 'g-', linewidth=2)
    ax2_cpu.set_title('CPU Usage (%)', fontsize=12)
    ax2_cpu.set_xlabel('Time')
    ax2_cpu.set_ylabel('CPU %')
    ax2_cpu.grid(True, alpha=0.3)
    
    # Performance metrics text
    metrics_text = [
        'Dashboard Features:',
        '• 4 Portfolio types supported',
        '• Real-time chart updates',
        '• Interactive date filtering',
        '• Multi-chart synchronization',
        '',
        'Performance Targets:',
        '• Chart render: < 500ms',
        '• Data query: < 200ms',
        '• Callback execution: < 100ms',
        '• Memory usage: < 1GB'
    ]
    
    for i, text in enumerate(metrics_text):
        style = 'bold' if text.endswith(':') else 'normal'
        ax2.text(1, 6 - i*0.4, text, fontsize=10, fontweight=style, va='center')
    
    plt.tight_layout()
    return fig

def create_dash_data_flow_diagram():
    """Create Dash data processing and visualization flow diagram."""
    
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)
    ax.set_aspect('equal')
    ax.axis('off')
    
    ax.text(9, 11.5, 'Dash Analytics Data Processing Flow', 
            fontsize=18, fontweight='bold', ha='center')
    
    # Data sources
    sources = [
        (2, 9, 'PostgreSQL\nRisk Data', '#4ECDC4'),
        (2, 7, 'Snowflake\nAnalytics', '#9B59B6'),
        (2, 5, 'Business Logic\nLibraries', '#F39C12')
    ]
    
    for x, y, label, color in sources:
        rect = FancyBboxPatch((x-0.8, y-0.6), 1.6, 1.2, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, fontsize=10, fontweight='bold', ha='center', va='center')
    
    # Data processing layer
    processing = [
        (6, 9, 'Risk\nCalculator', '#E74C3C'),
        (6, 7, 'Market Data\nProcessor', '#E74C3C'),
        (6, 5, 'Report\nGenerator', '#E74C3C')
    ]
    
    for x, y, label, color in processing:
        rect = FancyBboxPatch((x-0.8, y-0.6), 1.6, 1.2, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, fontsize=10, fontweight='bold', ha='center', va='center', color='white')
    
    # Visualization components
    viz_components = [
        (10, 9.5, 'VaR Chart\n(Time Series)', '#1F77B4'),
        (10, 8, 'Volatility Chart\n(Line Graph)', '#1F77B4'),
        (14, 9.5, 'Sharpe Ratio\n(Performance)', '#1F77B4'),
        (14, 8, 'Portfolio Comparison\n(Bar Chart)', '#1F77B4')
    ]
    
    for x, y, label, color in viz_components:
        rect = FancyBboxPatch((x-1, y-0.5), 2, 1, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, fontsize=9, fontweight='bold', ha='center', va='center', color='white')
    
    # Dashboard layout
    dashboard_rect = patches.Rectangle((9, 4), 8, 3, linewidth=2, 
                                       edgecolor='purple', facecolor='lavender', alpha=0.3)
    ax.add_patch(dashboard_rect)
    ax.text(13, 6.5, 'Interactive Dashboard Layout', fontsize=12, fontweight='bold', ha='center')
    
    # Dashboard components
    dash_components = [
        (10, 5.5, 'Controls\nPanel'),
        (12, 5.5, 'Chart\nGrid'),
        (14, 5.5, 'Summary\nTable'),
        (16, 5.5, 'Export\nOptions')
    ]
    
    for x, y, label in dash_components:
        rect = FancyBboxPatch((x-0.5, y-0.3), 1, 0.6, boxstyle="round,pad=0.05",
                              facecolor='#FF9F43', edgecolor='black')
        ax.add_patch(rect)
        ax.text(x, y, label, fontsize=8, fontweight='bold', ha='center', va='center')
    
    # User interaction layer
    ax.text(13, 2.5, 'User Interaction Layer', fontsize=12, fontweight='bold', ha='center')
    interactions = [
        (9, 1.5, 'Portfolio\nSelection'),
        (11, 1.5, 'Date Range\nFiltering'),
        (13, 1.5, 'Chart\nInteractions'),
        (15, 1.5, 'Data\nExport'),
        (17, 1.5, 'Real-time\nUpdates')
    ]
    
    for x, y, label in interactions:
        rect = FancyBboxPatch((x-0.6, y-0.4), 1.2, 0.8, boxstyle="round,pad=0.05",
                              facecolor='lightgreen', edgecolor='black')
        ax.add_patch(rect)
        ax.text(x, y, label, fontsize=8, fontweight='bold', ha='center', va='center')
    
    # Add data flow arrows
    # Sources to Processing
    for i in range(3):
        ax.annotate('', xy=(5.2, 9-i*2), xytext=(2.8, 9-i*2),
                   arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
    
    # Processing to Visualizations
    ax.annotate('', xy=(9, 9), xytext=(6.8, 9),
               arrowprops=dict(arrowstyle='->', lw=2, color='green'))
    ax.annotate('', xy=(9, 8.5), xytext=(6.8, 7),
               arrowprops=dict(arrowstyle='->', lw=2, color='green'))
    
    # Visualizations to Dashboard
    ax.annotate('', xy=(12, 7), xytext=(12, 8),
               arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    
    # Dashboard to User
    ax.annotate('', xy=(13, 4), xytext=(13, 2.3),
               arrowprops=dict(arrowstyle='<->', lw=2, color='purple'))
    
    plt.tight_layout()
    return fig

def main():
    """Generate all Dash Analytics diagrams."""
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "docs" / "architecture"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating Dash Analytics Application diagrams...")
    
    # Generate architecture diagram
    fig1 = create_dash_architecture_diagram()
    fig1.savefig(output_dir / "dash_analytics_architecture.png", dpi=300, bbox_inches='tight')
    fig1.savefig(output_dir / "dash_analytics_architecture.svg", format='svg', bbox_inches='tight')
    plt.close(fig1)
    print("Dash analytics architecture diagram saved (PNG + SVG)")
    
    # Generate interactive flow diagram
    fig2 = create_dash_interactive_flow_diagram()
    fig2.savefig(output_dir / "dash_interactive_flow.png", dpi=300, bbox_inches='tight')
    fig2.savefig(output_dir / "dash_interactive_flow.svg", format='svg', bbox_inches='tight')
    plt.close(fig2)
    print("Dash interactive flow diagram saved (PNG + SVG)")
    
    # Generate data flow diagram
    fig3 = create_dash_data_flow_diagram()
    fig3.savefig(output_dir / "dash_data_flow.png", dpi=300, bbox_inches='tight')
    fig3.savefig(output_dir / "dash_data_flow.svg", format='svg', bbox_inches='tight')
    plt.close(fig3)
    print("Dash data flow diagram saved (PNG + SVG)")
    
    print("All Dash Analytics diagrams generated successfully!")

if __name__ == "__main__":
    main()
