#!/usr/bin/env python3
"""
CloudWatch and Monitoring Stack Diagrams Generator

This script creates comprehensive visual diagrams for monitoring and observability including:
1. CloudWatch metrics and dashboards architecture
2. Logging aggregation and analysis workflows
3. Alerting and notification systems
4. Performance monitoring and optimization

Generated diagrams help understand the complete observability stack and monitoring strategies.
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

def create_metric_box(ax, x, y, width, height, metric_name, value, unit, color):
    """Create a metric display box"""
    create_fancy_box(ax, x, y, width, height, 
                    f'{metric_name}\n{value} {unit}', 
                    color, 'black', 'black', 2)

def create_cloudwatch_metrics_dashboards():
    """Create CloudWatch metrics and dashboards architecture diagram"""
    print("Creating CloudWatch metrics and dashboards architecture diagram...")
    
    # Create figure with high DPI for better quality
    fig, ax = plt.subplots(1, 1, figsize=(20, 16), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Title
    ax.text(50, 95, 'CloudWatch Metrics & Dashboards Architecture', fontsize=24, weight='bold', 
            ha='center', va='center')
    ax.text(50, 92, 'Comprehensive Monitoring and Observability Platform', fontsize=14, 
            ha='center', va='center', style='italic')
    
    # Color scheme
    colors = {
        'cloudwatch': '#FF9900',      # Orange for CloudWatch
        'metrics': '#4A90E2',         # Blue for metrics
        'dashboards': '#50E3C2',      # Teal for dashboards
        'alarms': '#F5A623',          # Yellow for alarms
        'applications': '#7ED321',    # Green for applications
        'infrastructure': '#BD10E0'   # Purple for infrastructure
    }
    
    # CloudWatch Service (Center)
    create_fancy_box(ax, 40, 70, 20, 15, 'Amazon CloudWatch\n\nMetrics Collection\nDashboard Platform\nAlerting System\nLog Analysis', 
                    colors['cloudwatch'], 'white', 'darkorange', 3)
    
    # Metric Sources (Left Side)
    ax.text(15, 85, 'METRIC SOURCES', fontsize=16, weight='bold')
    
    metric_sources = [
        ('EKS Cluster', 'CPU, Memory, Pods\nNode utilization', 5, 75, colors['infrastructure']),
        ('ALB', 'Request count, Latency\nHTTP status codes', 5, 67, colors['infrastructure']),
        ('RDS PostgreSQL', 'Connections, CPU\nStorage, IOPS', 5, 59, colors['infrastructure']),
        ('Custom Apps', 'Business metrics\nError rates', 5, 51, colors['applications']),
        ('VPC Flow Logs', 'Network traffic\nSecurity events', 5, 43, colors['infrastructure'])
    ]
    
    for source_name, desc, x, y, color in metric_sources:
        create_fancy_box(ax, x, y, 25, 6, f'{source_name}\n{desc}', color, 'white', 'black', 2)
        create_arrow(ax, x + 25, y + 3, 40, 77, color, '->', 2)
    
    # Dashboards (Right Side)
    ax.text(75, 85, 'MONITORING DASHBOARDS', fontsize=16, weight='bold')
    
    dashboards = [
        ('Infrastructure', 'EKS, RDS, ALB\nSystem health', 70, 75),
        ('Application', 'API performance\nError tracking', 70, 67),
        ('Security', 'Access patterns\nThreat detection', 70, 59),
        ('Business', 'Risk metrics\nUser activity', 70, 51),
        ('Cost', 'Resource usage\nSpending trends', 70, 43)
    ]
    
    for dash_name, desc, x, y in dashboards:
        create_fancy_box(ax, x, y, 25, 6, f'{dash_name}\n{desc}', colors['dashboards'], 'black', 'black', 2)
        create_arrow(ax, 60, 77, x, y + 3, colors['dashboards'], '->', 2)
    
    # Key Metrics Display (Bottom Left)
    ax.text(15, 35, 'KEY PERFORMANCE INDICATORS', fontsize=14, weight='bold')
    
    kpi_metrics = [
        ('API Latency', '125ms', 'avg', 5, 30, colors['metrics']),
        ('Success Rate', '99.2%', '', 15, 30, colors['applications']),
        ('CPU Usage', '45%', 'avg', 25, 30, colors['infrastructure']),
        ('Memory Usage', '68%', 'avg', 35, 30, colors['infrastructure']),
        ('Error Rate', '0.8%', '', 5, 25, colors['alarms']),
        ('Throughput', '1,250', 'req/min', 15, 25, colors['metrics']),
        ('DB Connections', '15/100', '', 25, 25, colors['infrastructure']),
        ('Disk Usage', '72%', '', 35, 25, colors['infrastructure'])
    ]
    
    for metric, value, unit, x, y, color in kpi_metrics:
        create_metric_box(ax, x, y, 8, 3, metric, value, unit, color)
    
    # Dashboard Configuration (Bottom Right)
    create_fancy_box(ax, 50, 25, 45, 20,
                    'DASHBOARD CONFIGURATION\n\n' +
                    'Infrastructure Dashboard:\n' +
                    '• EKS cluster health and resource utilization\n' +
                    '• RDS performance metrics and connection pool\n' +
                    '• ALB request patterns and response times\n' +
                    '• VPC network traffic and security events\n\n' +
                    'Application Dashboard:\n' +
                    '• API endpoint performance and error rates\n' +
                    '• Web application user experience metrics\n' +
                    '• Background job processing status\n' +
                    '• Database query performance analysis\n\n' +
                    'Custom Widgets:\n' +
                    '• Real-time metric graphs with 1-minute resolution\n' +
                    '• Custom business logic metrics\n' +
                    '• Cost optimization recommendations\n' +
                    '• Capacity planning projections',
                    colors['dashboards'], 'black', 'darkcyan', 2)
    
    # Metric Collection Details
    create_fancy_box(ax, 5, 5, 40, 15,
                    'METRIC COLLECTION DETAILS\n\n' +
                    'Collection Methods:\n' +
                    '• AWS Service Integration: Native metric publishing\n' +
                    '• CloudWatch Agent: Custom metrics from EC2/EKS\n' +
                    '• StatsD Protocol: Application-level metrics\n' +
                    '• Custom API: Business-specific measurements\n\n' +
                    'Metric Types:\n' +
                    '• Count: Request volume, error occurrences\n' +
                    '• Gauge: CPU usage, memory consumption\n' +
                    '• Timer: Response times, processing duration\n' +
                    '• Histogram: Response time distribution\n\n' +
                    'Retention Policy:\n' +
                    '• 1-minute data: 15 days\n' +
                    '• 5-minute data: 63 days\n' +
                    '• 1-hour data: 455 days',
                    colors['metrics'], 'white', 'darkblue', 2)
    
    plt.tight_layout()
    return fig

def create_logging_aggregation_analysis():
    """Create Logging aggregation and analysis workflows diagram"""
    print("Creating Logging aggregation and analysis workflows diagram...")
    
    fig, ax = plt.subplots(1, 1, figsize=(18, 14), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Title
    ax.text(50, 95, 'Logging Aggregation & Analysis Workflows', fontsize=24, weight='bold', 
            ha='center', va='center')
    ax.text(50, 92, 'Centralized Log Management and Real-time Analysis', fontsize=14, 
            ha='center', va='center', style='italic')
    
    # Color scheme
    colors = {
        'cloudwatch_logs': '#FF6B35',  # Red-orange for CloudWatch Logs
        'log_groups': '#4A90E2',       # Blue for log groups
        'applications': '#7ED321',     # Green for applications
        'analysis': '#9013FE',         # Purple for analysis
        'alerts': '#FF4081'            # Pink for alerts
    }
    
    # Log Sources (Top)
    ax.text(50, 85, 'LOG SOURCES', fontsize=16, weight='bold', ha='center')
    
    log_sources = [
        ('EKS Pods', 'Application logs\nContainer stdout', 10, 75),
        ('ALB Access', 'HTTP requests\nAccess patterns', 25, 75),
        ('VPC Flow Logs', 'Network traffic\nSecurity events', 40, 75),
        ('RDS Logs', 'Query logs\nError logs', 55, 75),
        ('Lambda', 'Function execution\nError traces', 70, 75),
        ('CloudTrail', 'API calls\nAdmin actions', 85, 75)
    ]
    
    source_positions = {}
    for source_name, desc, x, y in log_sources:
        create_fancy_box(ax, x-5, y, 10, 6, f'{source_name}\n{desc}', colors['applications'], 'black', 'black', 2)
        source_positions[source_name] = (x, y)
    
    # CloudWatch Logs (Center)
    create_fancy_box(ax, 35, 55, 30, 12, 'Amazon CloudWatch Logs\n\nCentralized Log Aggregation\nReal-time Streaming\nLong-term Retention\nLog Insights Query Engine', 
                    colors['cloudwatch_logs'], 'white', 'darkred', 3)
    
    # Draw arrows from sources to CloudWatch Logs
    for source_name, (x, y) in source_positions.items():
        create_arrow(ax, x, y, 50, 67, colors['log_groups'], '->', 2)
    
    # Log Groups Organization (Left)
    create_fancy_box(ax, 5, 40, 25, 20,
                    'LOG GROUPS ORGANIZATION\n\n' +
                    'Application Logs:\n' +
                    '• /mono-repo/web-app\n' +
                    '• /mono-repo/risk-api\n' +
                    '• /mono-repo/dash-app\n' +
                    '• /mono-repo/airflow\n\n' +
                    'Infrastructure Logs:\n' +
                    '• /aws/elasticloadbalancing/\n' +
                    '• /aws/rds/instance\n' +
                    '• /aws/vpc/flowlogs\n\n' +
                    'System Logs:\n' +
                    '• /aws/lambda/functions\n' +
                    '• /aws/eks/cluster\n' +
                    '• /aws/cloudtrail',
                    colors['log_groups'], 'white', 'darkblue', 2)
    
    # Log Analysis & Insights (Right)
    create_fancy_box(ax, 70, 40, 25, 20,
                    'LOG ANALYSIS & INSIGHTS\n\n' +
                    'CloudWatch Insights:\n' +
                    '• SQL-like query language\n' +
                    '• Real-time log search\n' +
                    '• Pattern recognition\n' +
                    '• Custom visualizations\n\n' +
                    'Common Queries:\n' +
                    '• Error rate analysis\n' +
                    '• Performance bottlenecks\n' +
                    '• Security anomalies\n' +
                    '• User behavior patterns\n\n' +
                    'Automated Analysis:\n' +
                    '• Scheduled insights queries\n' +
                    '• Anomaly detection\n' +
                    '• Trend analysis',
                    colors['analysis'], 'white', 'purple', 2)
    
    # Log Processing Pipeline (Bottom)
    ax.text(50, 30, 'LOG PROCESSING PIPELINE', fontsize=16, weight='bold', ha='center')
    
    pipeline_steps = [
        ('Ingestion', 'Real-time\nStreaming', 15, 20, colors['applications']),
        ('Parsing', 'Structured\nExtraction', 30, 20, colors['log_groups']),
        ('Enrichment', 'Metadata\nAddition', 45, 20, colors['analysis']),
        ('Analysis', 'Pattern\nDetection', 60, 20, colors['analysis']),
        ('Alerting', 'Threshold\nNotification', 75, 20, colors['alerts'])
    ]
    
    step_positions = []
    for step_name, desc, x, y, color in pipeline_steps:
        create_fancy_box(ax, x-5, y, 10, 6, f'{step_name}\n{desc}', color, 'white', 'black', 2)
        step_positions.append((x, y+3))
    
    # Draw pipeline flow arrows
    for i in range(len(step_positions)-1):
        create_arrow(ax, step_positions[i][0]+5, step_positions[i][1], 
                    step_positions[i+1][0]-5, step_positions[i+1][1], 'darkgray', '->', 2)
    
    # Log Retention & Cost Optimization (Bottom)
    create_fancy_box(ax, 5, 5, 40, 10,
                    'RETENTION & COST OPTIMIZATION\n\n' +
                    'Retention Policies:\n' +
                    '• Application Logs: 30 days (frequently accessed)\n' +
                    '• System Logs: 90 days (compliance requirement)\n' +
                    '• Security Logs: 1 year (audit trail)\n' +
                    '• Archive to S3: Long-term storage (7 years)\n\n' +
                    'Cost Management:\n' +
                    '• Log filtering to reduce volume\n' +
                    '• Compression and deduplication\n' +
                    '• Automated lifecycle policies',
                    colors['cloudwatch_logs'], 'white', 'darkred', 2)
    
    create_fancy_box(ax, 55, 5, 40, 10,
                    'REAL-TIME LOG MONITORING\n\n' +
                    'Log Streaming:\n' +
                    '• Kinesis Data Streams integration\n' +
                    '• Real-time processing with Lambda\n' +
                    '• Custom alerting on log patterns\n' +
                    '• Integration with external SIEM tools\n\n' +
                    'Log Metrics:\n' +
                    '• Error rate from log patterns\n' +
                    '• Custom business metrics extraction\n' +
                    '• Performance indicators from logs',
                    colors['analysis'], 'white', 'purple', 2)
    
    plt.tight_layout()
    return fig

def create_alerting_notification_systems():
    """Create Alerting and notification systems diagram"""
    print("Creating Alerting and notification systems diagram...")
    
    fig, ax = plt.subplots(1, 1, figsize=(18, 12), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Title
    ax.text(50, 95, 'Alerting & Notification Systems', fontsize=24, weight='bold', 
            ha='center', va='center')
    ax.text(50, 92, 'Intelligent Alert Management and Multi-channel Notifications', fontsize=14, 
            ha='center', va='center', style='italic')
    
    # Color scheme
    colors = {
        'cloudwatch_alarms': '#E74C3C',  # Red for alarms
        'sns': '#3498DB',                # Blue for SNS
        'notification': '#2ECC71',       # Green for notifications
        'escalation': '#F39C12',         # Orange for escalation
        'automation': '#9B59B6'          # Purple for automation
    }
    
    # Alert Sources (Top)
    ax.text(50, 85, 'ALERT SOURCES & TRIGGERS', fontsize=16, weight='bold', ha='center')
    
    alert_sources = [
        ('CloudWatch\nMetrics', 'Threshold\nbreaches', 15, 75, colors['cloudwatch_alarms']),
        ('CloudWatch\nLogs', 'Error pattern\nmatching', 35, 75, colors['cloudwatch_alarms']),
        ('Custom\nMetrics', 'Business\nlogic alerts', 55, 75, colors['cloudwatch_alarms']),
        ('Health\nChecks', 'Service\navailability', 75, 75, colors['cloudwatch_alarms'])
    ]
    
    for source_name, desc, x, y, color in alert_sources:
        create_fancy_box(ax, x-7.5, y, 15, 6, f'{source_name}\n{desc}', color, 'white', 'darkred', 2)
    
    # SNS Topics (Center)
    create_fancy_box(ax, 35, 55, 30, 12, 'Amazon SNS Topics\n\nAlert Routing\nMessage Fanout\nSubscriber Management\nDelivery Retry Logic', 
                    colors['sns'], 'white', 'darkblue', 3)
    
    # Draw arrows from sources to SNS
    for source_name, desc, x, y, color in alert_sources:
        create_arrow(ax, x, y, 50, 67, color, '->', 2)
    
    # Notification Channels (Bottom)
    ax.text(50, 45, 'NOTIFICATION CHANNELS', fontsize=16, weight='bold', ha='center')
    
    notification_channels = [
        ('Email', 'team@company.com\nescalation@company.com', 10, 35, colors['notification']),
        ('Slack', '#alerts channel\n#incidents channel', 25, 35, colors['notification']),
        ('SMS', 'On-call engineer\nCritical alerts only', 40, 35, colors['notification']),
        ('PagerDuty', 'Incident management\nEscalation policies', 55, 35, colors['escalation']),
        ('Lambda', 'Auto-remediation\nCustom actions', 70, 35, colors['automation']),
        ('Webhook', 'External systems\nChatbots integration', 85, 35, colors['notification'])
    ]
    
    for channel_name, desc, x, y, color in notification_channels:
        create_fancy_box(ax, x-7.5, y, 15, 6, f'{channel_name}\n{desc}', color, 'white', 'black', 2)
        create_arrow(ax, 50, 55, x, y+6, colors['sns'], '->', 1.5)
    
    # Alert Severity Levels (Left Side)
    create_fancy_box(ax, 5, 60, 25, 20,
                    'ALERT SEVERITY LEVELS\n\n' +
                    'CRITICAL (P1):\n' +
                    '• Service completely down\n' +
                    '• Data corruption detected\n' +
                    '• Security breach identified\n' +
                    '→ Immediate notification\n\n' +
                    'HIGH (P2):\n' +
                    '• Performance degradation\n' +
                    '• Error rate spike\n' +
                    '• Resource exhaustion\n' +
                    '→ 5-minute notification\n\n' +
                    'MEDIUM (P3):\n' +
                    '• Capacity warnings\n' +
                    '• Configuration issues\n' +
                    '→ Business hours only\n\n' +
                    'LOW (P4):\n' +
                    '• Informational alerts\n' +
                    '→ Daily summary email',
                    colors['escalation'], 'black', 'darkorange', 2)
    
    # Alert Configuration (Right Side)
    create_fancy_box(ax, 70, 60, 25, 20,
                    'ALERT CONFIGURATION\n\n' +
                    'Threshold Settings:\n' +
                    '• CPU > 80% for 5 minutes\n' +
                    '• Memory > 90% for 3 minutes\n' +
                    '• Error rate > 5% for 2 minutes\n' +
                    '• Response time > 2s for 1 minute\n\n' +
                    'Smart Alerting:\n' +
                    '• Alert suppression during deploys\n' +
                    '• Anomaly detection algorithms\n' +
                    '• Composite alarms (multiple conditions)\n' +
                    '• Time-based alert schedules\n\n' +
                    'Alert Fatigue Prevention:\n' +
                    '• Alert grouping and correlation\n' +
                    '• Escalation policies with delays\n' +
                    '• Auto-resolution detection',
                    colors['cloudwatch_alarms'], 'white', 'darkred', 2)
    
    # Incident Response Workflow (Bottom)
    create_fancy_box(ax, 5, 10, 90, 15,
                    'INCIDENT RESPONSE WORKFLOW\n\n' +
                    'Alert Detection → Notification → Acknowledgment → Investigation → Remediation → Resolution → Post-mortem\n\n' +
                    'Automated Actions:\n' +
                    '• Auto-scaling trigger when CPU/memory thresholds exceeded\n' +
                    '• Restart unhealthy containers automatically\n' +
                    '• Circuit breaker activation for failing services\n' +
                    '• Backup system activation for critical failures\n\n' +
                    'Escalation Matrix:\n' +
                    '• Level 1: Development team (5 minutes response)\n' +
                    '• Level 2: Senior engineers (15 minutes response)\n' +
                    '• Level 3: Management/CTO (30 minutes response)\n' +
                    '• Emergency contacts for critical system failures\n\n' +
                    'SLA Targets: P1: 15 minutes, P2: 1 hour, P3: 4 hours, P4: Next business day',
                    colors['automation'], 'white', 'purple', 2)
    
    plt.tight_layout()
    return fig

def create_performance_monitoring_optimization():
    """Create Performance monitoring and optimization diagram"""
    print("Creating Performance monitoring and optimization diagram...")
    
    fig, ax = plt.subplots(1, 1, figsize=(20, 14), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Title
    ax.text(50, 95, 'Performance Monitoring & Optimization', fontsize=24, weight='bold', 
            ha='center', va='center')
    ax.text(50, 92, 'Comprehensive Performance Analysis and Continuous Optimization', fontsize=14, 
            ha='center', va='center', style='italic')
    
    # Color scheme
    colors = {
        'performance': '#E67E22',      # Orange for performance
        'optimization': '#27AE60',     # Green for optimization
        'analysis': '#8E44AD',         # Purple for analysis
        'monitoring': '#3498DB',       # Blue for monitoring
        'cost': '#F1C40F'              # Yellow for cost
    }
    
    # Performance Metrics Categories (Top)
    ax.text(50, 85, 'PERFORMANCE MONITORING CATEGORIES', fontsize=16, weight='bold', ha='center')
    
    metric_categories = [
        ('Application\nPerformance', 'Response time\nThroughput\nError rates', 15, 75, colors['performance']),
        ('Infrastructure\nMetrics', 'CPU, Memory\nDisk, Network', 35, 75, colors['monitoring']),
        ('Database\nPerformance', 'Query time\nConnections\nLocks', 55, 75, colors['performance']),
        ('User\nExperience', 'Page load\nInteraction\nSatisfaction', 75, 75, colors['analysis'])
    ]
    
    for category_name, desc, x, y, color in metric_categories:
        create_fancy_box(ax, x-7.5, y, 15, 8, f'{category_name}\n{desc}', color, 'white', 'black', 2)
    
    # Performance Dashboard (Center Left)
    create_fancy_box(ax, 5, 50, 40, 20,
                    'PERFORMANCE DASHBOARD METRICS\n\n' +
                    'API Performance:\n' +
                    '• Average Response Time: 125ms\n' +
                    '• 95th Percentile: 280ms\n' +
                    '• 99th Percentile: 450ms\n' +
                    '• Success Rate: 99.2%\n' +
                    '• Throughput: 1,250 req/min\n\n' +
                    'Resource Utilization:\n' +
                    '• CPU Usage: 45% average\n' +
                    '• Memory Usage: 68% average\n' +
                    '• Disk I/O: 120 IOPS\n' +
                    '• Network: 50 Mbps\n\n' +
                    'Database Performance:\n' +
                    '• Query Response: 15ms average\n' +
                    '• Active Connections: 15/100\n' +
                    '• Cache Hit Rate: 94%\n' +
                    '• Lock Wait Time: 2ms average',
                    colors['performance'], 'white', 'darkorange', 2)
    
    # Optimization Strategies (Center Right)
    create_fancy_box(ax, 55, 50, 40, 20,
                    'OPTIMIZATION STRATEGIES\n\n' +
                    'Application Optimization:\n' +
                    '• Code profiling and bottleneck identification\n' +
                    '• Database query optimization\n' +
                    '• Caching layer implementation\n' +
                    '• API response payload optimization\n' +
                    '• Asynchronous processing adoption\n\n' +
                    'Infrastructure Optimization:\n' +
                    '• Auto-scaling policy tuning\n' +
                    '• Resource right-sizing analysis\n' +
                    '• Load balancer optimization\n' +
                    '• Network latency reduction\n\n' +
                    'Cost Optimization:\n' +
                    '• Reserved instance planning\n' +
                    '• Spot instance utilization\n' +
                    '• Unused resource identification\n' +
                    '• Service consolidation opportunities',
                    colors['optimization'], 'white', 'darkgreen', 2)
    
    # Performance Analysis Tools (Bottom Left)
    create_fancy_box(ax, 5, 25, 40, 20,
                    'PERFORMANCE ANALYSIS TOOLS\n\n' +
                    'AWS Native Tools:\n' +
                    '• CloudWatch Insights: Log-based analysis\n' +
                    '• X-Ray: Distributed tracing\n' +
                    '• Application Insights: APM\n' +
                    '• Performance Insights: Database analysis\n\n' +
                    'Custom Monitoring:\n' +
                    '• Prometheus + Grafana: Metrics collection\n' +
                    '• ElasticSearch: Log analysis\n' +
                    '• Custom metrics via StatsD\n' +
                    '• Business metric tracking\n\n' +
                    'Performance Testing:\n' +
                    '• Load testing with JMeter/Locust\n' +
                    '• Stress testing for peak capacity\n' +
                    '• Regression testing in CI/CD\n' +
                    '• Synthetic monitoring and alerting',
                    colors['analysis'], 'white', 'purple', 2)
    
    # Cost & Capacity Planning (Bottom Right)
    create_fancy_box(ax, 55, 25, 40, 20,
                    'COST & CAPACITY PLANNING\n\n' +
                    'Current Resource Costs:\n' +
                    '• EKS Cluster: $180/month\n' +
                    '• RDS Database: $150/month\n' +
                    '• Load Balancer: $25/month\n' +
                    '• CloudWatch: $30/month\n' +
                    '• Total Infrastructure: $385/month\n\n' +
                    'Capacity Planning:\n' +
                    '• Growth projection: 20% quarterly\n' +
                    '• Peak traffic analysis\n' +
                    '• Resource scaling recommendations\n' +
                    '• Performance vs. cost trade-offs\n\n' +
                    'Optimization Opportunities:\n' +
                    '• Estimated savings: $75/month (19%)\n' +
                    '• Right-sizing recommendations\n' +
                    '• Reserved instance purchases\n' +
                    '• Automated cost optimization',
                    colors['cost'], 'black', 'darkorange', 2)
    
    # Key Performance Indicators (Bottom)
    create_fancy_box(ax, 25, 5, 50, 15,
                    'KEY PERFORMANCE INDICATORS (KPIs)\n\n' +
                    'Service Level Objectives (SLOs):\n' +
                    '• API Availability: 99.5% (target: 99.9%)\n' +
                    '• Response Time: 95th percentile < 300ms\n' +
                    '• Error Rate: < 1% of total requests\n' +
                    '• Database Uptime: 99.9% availability\n\n' +
                    'Business Impact Metrics:\n' +
                    '• User Satisfaction Score: 4.2/5.0\n' +
                    '• Feature Adoption Rate: 75%\n' +
                    '• Time to Value: 2.5 minutes average\n' +
                    '• Customer Retention: 94%\n\n' +
                    'Operational Excellence:\n' +
                    '• Mean Time to Recovery (MTTR): 8 minutes\n' +
                    '• Mean Time Between Failures (MTBF): 168 hours\n' +
                    '• Deployment Success Rate: 98.5%\n' +
                    '• Incident Response Time: 3.2 minutes average',
                    colors['monitoring'], 'white', 'darkblue', 2)
    
    plt.tight_layout()
    return fig

def create_documentation_summary():
    """Create comprehensive documentation summary"""
    return f"""# CloudWatch and Monitoring Stack Diagrams Documentation

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This document accompanies the visual diagrams created to illustrate the comprehensive monitoring and observability architecture, including CloudWatch metrics, logging systems, alerting mechanisms, and performance optimization strategies for the mono-repo infrastructure.

## Generated Diagrams

### 1. CloudWatch Metrics & Dashboards Architecture (`cloudwatch_metrics_dashboards`)
**Purpose**: Complete monitoring platform showing metrics collection, dashboard organization, and KPI visualization

**Metric Sources**:
- **EKS Cluster**: CPU, Memory, Pods, Node utilization
- **Application Load Balancer**: Request count, Latency, HTTP status codes  
- **RDS PostgreSQL**: Connections, CPU, Storage, IOPS
- **Custom Applications**: Business metrics, Error rates
- **VPC Flow Logs**: Network traffic, Security events

**Dashboard Categories**:
- **Infrastructure**: EKS, RDS, ALB system health
- **Application**: API performance, Error tracking
- **Security**: Access patterns, Threat detection
- **Business**: Risk metrics, User activity
- **Cost**: Resource usage, Spending trends

### 2. Logging Aggregation & Analysis Workflows (`logging_aggregation_analysis`)
**Purpose**: Centralized log management and real-time analysis capabilities

**Log Sources Integration**:
- **EKS Pods**: Application logs, Container stdout
- **ALB Access**: HTTP requests, Access patterns
- **VPC Flow Logs**: Network traffic, Security events
- **RDS Logs**: Query logs, Error logs
- **Lambda Functions**: Execution logs, Error traces
- **CloudTrail**: API calls, Administrative actions

**Log Processing Pipeline**:
1. **Ingestion**: Real-time streaming
2. **Parsing**: Structured extraction
3. **Enrichment**: Metadata addition
4. **Analysis**: Pattern detection
5. **Alerting**: Threshold notifications

### 3. Alerting & Notification Systems (`alerting_notification_systems`)
**Purpose**: Intelligent alert management and multi-channel notifications

**Alert Sources**:
- **CloudWatch Metrics**: Threshold breaches
- **CloudWatch Logs**: Error pattern matching
- **Custom Metrics**: Business logic alerts
- **Health Checks**: Service availability monitoring

**Notification Channels**:
- **Email**: Team and escalation distribution lists
- **Slack**: Real-time team notifications (#alerts, #incidents)
- **SMS**: Critical alerts for on-call engineers
- **PagerDuty**: Incident management with escalation policies
- **Lambda**: Auto-remediation and custom actions
- **Webhooks**: External systems and chatbot integration

### 4. Performance Monitoring & Optimization (`performance_monitoring_optimization`)
**Purpose**: Comprehensive performance analysis and continuous optimization

**Monitoring Categories**:
- **Application Performance**: Response time, Throughput, Error rates
- **Infrastructure Metrics**: CPU, Memory, Disk, Network utilization
- **Database Performance**: Query time, Connections, Lock analysis
- **User Experience**: Page load times, Interaction metrics

**Optimization Strategies**:
- **Application**: Code profiling, Database optimization, Caching
- **Infrastructure**: Auto-scaling, Resource right-sizing, Load balancing
- **Cost**: Reserved instances, Spot utilization, Resource consolidation

## Monitoring Architecture Implementation

### CloudWatch Metrics Structure
```
Metric Namespaces:
├── AWS/EKS
│   ├── cluster_failed_request_count
│   ├── cluster_service_number_of_running_pods
│   └── node_cpu_utilization
├── AWS/ApplicationELB
│   ├── RequestCount
│   ├── TargetResponseTime
│   └── HTTPCode_Target_2XX_Count
├── AWS/RDS
│   ├── CPUUtilization
│   ├── DatabaseConnections
│   └── ReadLatency
└── MonoRepo/Application
    ├── api_response_time
    ├── business_metric_risk_processed
    └── user_session_count
```

### Log Groups Organization
```
/aws/eks/mono-repo-cluster/
├── application-logs/
│   ├── web-app/
│   ├── risk-api/
│   ├── dash-analytics/
│   └── airflow/
├── system-logs/
│   ├── kube-apiserver-audit
│   ├── kube-controller-manager
│   └── kube-scheduler
└── security-logs/
    ├── cluster-autoscaler
    └── aws-load-balancer-controller

/aws/rds/instance/mono-repo-db/
├── error
├── general
├── slow-query
└── postgresql

/aws/elasticloadbalancing/app/mono-repo-alb/
└── access-logs

/aws/lambda/
├── log-processor
├── alert-handler
└── auto-remediation
```

## Alerting Configuration

### Alert Severity Matrix
```
CRITICAL (P1) - Immediate Response:
├── Service Unavailable (HTTP 5xx > 50%)
├── Database Connection Failure
├── EKS Cluster Failure  
├── Security Breach Detection
└── Data Corruption Alerts

HIGH (P2) - 5 Minute Response:
├── High Error Rate (HTTP 4xx/5xx > 5%)
├── Response Time Degradation (> 2 seconds)
├── Resource Exhaustion (CPU > 90%, Memory > 95%)
├── Failed Deployment Detection
└── Authentication Failures Spike

MEDIUM (P3) - Business Hours Response:
├── Performance Warning (Response time > 1 second)
├── Resource Warning (CPU > 80%, Memory > 85%)
├── Capacity Planning Alerts
├── SSL Certificate Expiration
└── Configuration Drift Detection

LOW (P4) - Daily Summary:
├── Informational Metrics
├── Usage Pattern Changes
├── Cost Optimization Opportunities
└── Maintenance Reminders
```

### SNS Topics Configuration
```
mono-repo-critical-alerts:
├── Subscribers: PagerDuty, SMS (On-call), Slack (#incidents)
├── Delivery Policy: Immediate retry
└── Dead Letter Queue: Enabled

mono-repo-high-alerts:
├── Subscribers: Email (Team), Slack (#alerts)
├── Delivery Policy: 5-minute delay retry
└── Filter Policy: Business hours preference

mono-repo-info-alerts:
├── Subscribers: Email (Daily digest)
├── Delivery Policy: Best effort
└── Batch Processing: Enabled
```

## Performance Monitoring Implementation

### Key Performance Indicators
```python
# CloudWatch Custom Metrics
import boto3

cloudwatch = boto3.client('cloudwatch')

# API Performance Metrics
def publish_api_metrics(response_time, status_code, endpoint):
    cloudwatch.put_metric_data(
        Namespace='MonoRepo/API',
        MetricData=[
            {{
                'MetricName': 'ResponseTime',
                'Dimensions': [
                    {{'Name': 'Endpoint', 'Value': endpoint}},
                    {{'Name': 'StatusCode', 'Value': str(status_code)}}
                ],
                'Value': response_time,
                'Unit': 'Milliseconds'
            }}
        ]
    )

# Business Metrics
def publish_business_metrics(metric_name, value, unit='Count'):
    cloudwatch.put_metric_data(
        Namespace='MonoRepo/Business',
        MetricData=[
            {{
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow()
            }}
        ]
    )
```

### Performance Analysis Queries
```sql
-- CloudWatch Logs Insights Queries

-- API Error Analysis
fields @timestamp, @message, status_code, response_time
| filter status_code >= 400
| stats count() by status_code, bin(5m)
| sort @timestamp desc

-- Slow Query Analysis  
fields @timestamp, query, duration
| filter duration > 1000
| stats avg(duration), max(duration), count() by query
| sort avg_duration desc

-- User Activity Patterns
fields @timestamp, user_id, action, endpoint
| stats count() as requests by user_id, endpoint
| sort requests desc
| limit 100
```

## Cost Optimization Analysis

### Current Infrastructure Costs
```
Monthly AWS Costs (Estimated):
├── EKS Cluster Control Plane: $73/month
├── EKS Worker Nodes (t3.medium): $87/month  
├── RDS PostgreSQL (db.t3.micro): $13/month
├── Application Load Balancer: $23/month
├── CloudWatch: $15/month (logs + metrics)
├── VPC NAT Gateway: $32/month
├── Parameter Store: $0 (standard tier)
├── Secrets Manager: $6/month (15 secrets)
└── Total: ~$249/month

Optimization Opportunities:
├── Reserved Instances: -$25/month (10% savings)
├── Spot Instances: -$30/month (worker nodes)
├── Log Retention Optimization: -$8/month
├── Unused Resources Cleanup: -$12/month
└── Potential Savings: $75/month (30%)
```

### Capacity Planning
```
Current Usage vs. Capacity:
├── CPU Utilization: 45% average (55% headroom)
├── Memory Utilization: 68% average (32% headroom)
├── Database Connections: 15/100 (85% available)
├── Storage: 25GB/100GB allocated (75% free)

Growth Projections:
├── Traffic Growth: 20% quarterly
├── Data Growth: 15% quarterly  
├── User Growth: 25% quarterly
├── Scaling Timeline: 6-month capacity available

Scaling Recommendations:
├── Horizontal Pod Autoscaler: 2-10 replicas
├── Cluster Autoscaler: 1-5 nodes
├── Database Scaling: Read replicas at 80% CPU
└── Cost Impact: Linear scaling with usage
```

## Operational Procedures

### Monitoring Runbook
```
Daily Operations:
├── Review overnight alerts and incidents
├── Check performance dashboard for anomalies
├── Validate backup and monitoring system health
├── Update capacity planning projections
└── Review cost optimization opportunities

Weekly Operations:
├── Performance trend analysis
├── Alert threshold tuning
├── Log retention policy review
├── Monitoring system updates
└── Incident post-mortem reviews

Monthly Operations:
├── Comprehensive performance report
├── Cost optimization review
├── Monitoring tool evaluation
├── Capacity planning updates
└── SLO/SLA compliance review
```

### Incident Response Workflow
```
Alert Detection:
├── CloudWatch alarm triggered
├── SNS notification sent
├── PagerDuty incident created
└── Slack notification posted

Initial Response (< 5 minutes):
├── Acknowledge alert in PagerDuty
├── Check service dashboard
├── Identify affected services
└── Begin triage process

Investigation (< 15 minutes):
├── Review recent deployments
├── Check error logs and metrics
├── Identify root cause
└── Determine remediation steps

Remediation:
├── Apply immediate fixes
├── Monitor system recovery
├── Communicate status updates
└── Document resolution steps

Post-Incident:
├── Conduct post-mortem review
├── Update monitoring and alerts
├── Implement preventive measures
└── Update runbook procedures
```

## Integration Examples

### CloudWatch Dashboard JSON
```json
{{
    "widgets": [
        {{
            "type": "metric",
            "properties": {{
                "metrics": [
                    ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", "mono-repo-alb"],
                    ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "mono-repo-alb"]
                ],
                "period": 300,
                "stat": "Average",
                "region": "us-east-1",
                "title": "ALB Performance"
            }}
        }}
    ]
}}
```

### Custom Alert Handler Lambda
```python
import json
import boto3

def lambda_handler(event, context):
    # Parse SNS message
    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    # Extract alert details
    alarm_name = message['AlarmName']
    new_state = message['NewStateValue']
    reason = message['NewStateReason']
    
    # Auto-remediation logic
    if alarm_name == 'HighCPUUtilization':
        trigger_auto_scaling(alarm_name)
    elif alarm_name == 'DatabaseConnectionHigh':
        restart_connection_pool()
    
    # Send to incident management
    create_incident(alarm_name, new_state, reason)
    
    return {{'statusCode': 200}}
```

## File Structure
```
docs/architecture/
├── cloudwatch_metrics_dashboards.png           # Metrics and dashboards
├── cloudwatch_metrics_dashboards.svg           # Vector format
├── logging_aggregation_analysis.png            # Log management
├── logging_aggregation_analysis.svg            # Vector format  
├── alerting_notification_systems.png           # Alert management
├── alerting_notification_systems.svg           # Vector format
├── performance_monitoring_optimization.png     # Performance analysis
└── performance_monitoring_optimization.svg     # Vector format
```

Created: {datetime.now().strftime('%B %d, %Y')}
Generated by: create_monitoring_stack_diagrams.py
"""

def main():
    """Main function to generate all CloudWatch and monitoring stack diagrams"""
    print("📊 Starting CloudWatch and Monitoring Stack Diagrams generation...")
    
    # Create output directory
    output_dir = Path("../docs/architecture")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate diagrams
    diagrams = [
        ("cloudwatch_metrics_dashboards", create_cloudwatch_metrics_dashboards()),
        ("logging_aggregation_analysis", create_logging_aggregation_analysis()),
        ("alerting_notification_systems", create_alerting_notification_systems()),
        ("performance_monitoring_optimization", create_performance_monitoring_optimization())
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
    doc_path = Path("../docs/CLOUDWATCH_MONITORING_STACK_DOCUMENTATION.md")
    with open(doc_path, 'w') as f:
        f.write(doc_content)
    
    print(f"✅ Created comprehensive CloudWatch and Monitoring Stack documentation")
    
    print(f"\n✅ All CloudWatch and Monitoring Stack diagrams generated successfully!")
    print(f"📊 Generated {len(diagrams)} diagrams (PNG + SVG formats)")
    print(f"📖 Created comprehensive documentation")
    print(f"🔧 View diagrams in: {output_dir.resolve()}")

if __name__ == "__main__":
    main()