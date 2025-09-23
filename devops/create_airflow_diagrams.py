#!/usr/bin/env python3
"""
Apache Airflow Architecture Diagram Generator
Creates comprehensive diagrams showing Airflow infrastructure and workflow architecture.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Circle
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.dates as mdates

def create_airflow_architecture_diagram():
    """Create comprehensive Airflow architecture diagram."""
    
    # Create figure with subplots
    fig = plt.figure(figsize=(22, 16))
    
    # Main architecture diagram
    ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=2, rowspan=2)
    ax1.set_xlim(0, 22)
    ax1.set_ylim(0, 16)
    ax1.set_aspect('equal')
    ax1.axis('off')
    
    # Executor details
    ax2 = plt.subplot2grid((3, 2), (2, 0))
    ax2.set_xlim(0, 11)
    ax2.set_ylim(0, 6)
    ax2.set_aspect('equal')
    ax2.axis('off')
    
    # DAG workflow visualization
    ax3 = plt.subplot2grid((3, 2), (2, 1))
    ax3.set_xlim(0, 11)
    ax3.set_ylim(0, 6)
    ax3.set_aspect('equal')
    ax3.axis('off')
    
    # Define colors
    colors = {
        'corporate_network': '#E6E6FA',
        'aws_cloud': '#E8F4FD',
        'vpc': '#D4EDDA',
        'eks': '#E2E3E5',
        'airflow': '#E2F4FF',
        'postgres': '#336791',
        'redis': '#DC382D',
        'k8s_executor': '#3498DB',
        'git': '#F05032',
        'celery': '#37B24D',
        'scheduler': '#FF6B35',
        'webserver': '#4C6EF5',
        's3': '#569A31'
    }
    
    # Main Architecture Diagram
    ax1.text(11, 15.5, 'Apache Airflow Self-Managed Architecture on EKS', 
             fontsize=20, fontweight='bold', ha='center')
    
    # Corporate Network boundary
    corp_rect = patches.Rectangle((0.5, 0.5), 21, 14.5, linewidth=3, 
                                  edgecolor='purple', facecolor=colors['corporate_network'], alpha=0.2)
    ax1.add_patch(corp_rect)
    ax1.text(1, 14.7, 'Corporate Intranet Only', fontsize=14, fontweight='bold', color='purple')
    
    # AWS Cloud boundary
    aws_rect = patches.Rectangle((1, 2), 20, 12, linewidth=2, 
                                 edgecolor='blue', facecolor=colors['aws_cloud'], alpha=0.3)
    ax1.add_patch(aws_rect)
    ax1.text(1.5, 13.5, 'AWS Cloud - US-East-1', fontsize=12, fontweight='bold', color='blue')
    
    # VPC boundary
    vpc_rect = patches.Rectangle((2, 3), 18, 10, linewidth=2, 
                                 edgecolor='green', facecolor=colors['vpc'], alpha=0.3)
    ax1.add_patch(vpc_rect)
    ax1.text(2.5, 12.5, 'VPC (10.0.0.0/16)', fontsize=11, fontweight='bold', color='green')
    
    # Load Balancer (ALB) 
    alb_rect = FancyBboxPatch((9, 11), 4, 1.5, boxstyle="round,pad=0.1",
                              facecolor='#45B7D1', edgecolor='black', linewidth=2)
    ax1.add_patch(alb_rect)
    ax1.text(11, 11.75, 'Internal ALB\n/airflow → Webserver', 
             fontsize=10, fontweight='bold', ha='center', va='center')
    
    # EKS Cluster
    eks_rect = patches.Rectangle((3, 5.5), 16, 5, linewidth=2, 
                                 edgecolor='darkblue', facecolor=colors['eks'], alpha=0.4)
    ax1.add_patch(eks_rect)
    ax1.text(3.5, 10, 'EKS Cluster (airflow-cluster)', fontsize=12, fontweight='bold', color='darkblue')
    
    # Airflow Components within EKS
    # Airflow Webserver
    webserver_rect = FancyBboxPatch((4, 8.5), 3, 1.5, boxstyle="round,pad=0.1",
                                    facecolor=colors['webserver'], edgecolor='black', linewidth=2)
    ax1.add_patch(webserver_rect)
    ax1.text(5.5, 9.25, 'Airflow Webserver\nPort: 8080\nReplicas: 2', 
             fontsize=9, fontweight='bold', ha='center', va='center', color='white')
    
    # Airflow Scheduler
    scheduler_rect = FancyBboxPatch((8, 8.5), 3, 1.5, boxstyle="round,pad=0.1",
                                    facecolor=colors['scheduler'], edgecolor='black', linewidth=2)
    ax1.add_patch(scheduler_rect)
    ax1.text(9.5, 9.25, 'Airflow Scheduler\nDAG Parsing\nReplicas: 2', 
             fontsize=9, fontweight='bold', ha='center', va='center', color='white')
    
    # KubernetesExecutor Pods
    k8s_executor_rect = FancyBboxPatch((12, 8.5), 3.5, 1.5, boxstyle="round,pad=0.1",
                                       facecolor=colors['k8s_executor'], edgecolor='black', linewidth=2)
    ax1.add_patch(k8s_executor_rect)
    ax1.text(13.75, 9.25, 'KubernetesExecutor\nTask Pods\nAuto-scaling', 
             fontsize=9, fontweight='bold', ha='center', va='center', color='white')
    
    # Worker Pods (dynamically created)
    worker_pods = [
        (16.5, 8.5, 'Worker\nPod 1'),
        (16.5, 7, 'Worker\nPod 2'),
        (16.5, 5.5, 'Worker\nPod N')
    ]
    
    for x, y, label in worker_pods:
        pod_rect = FancyBboxPatch((x-0.4, y-0.3), 0.8, 0.6, boxstyle="round,pad=0.05",
                                  facecolor='lightblue', edgecolor='black')
        ax1.add_patch(pod_rect)
        ax1.text(x, y, label, fontsize=7, fontweight='bold', ha='center', va='center')
    
    # Git-Sync sidecar
    git_sync_rect = FancyBboxPatch((4, 6.5), 2.5, 1, boxstyle="round,pad=0.1",
                                   facecolor=colors['git'], edgecolor='black', linewidth=2)
    ax1.add_patch(git_sync_rect)
    ax1.text(5.25, 7, 'Git-Sync\nDAG Repo', 
             fontsize=9, fontweight='bold', ha='center', va='center', color='white')
    
    # Shared DAG Volume
    dag_volume_rect = FancyBboxPatch((8, 6.5), 3, 1, boxstyle="round,pad=0.1",
                                     facecolor='lightyellow', edgecolor='black', linewidth=2)
    ax1.add_patch(dag_volume_rect)
    ax1.text(9.5, 7, 'Shared DAG\nVolume (PVC)', 
             fontsize=9, fontweight='bold', ha='center', va='center')
    
    # External PostgreSQL Database
    postgres_rect = FancyBboxPatch((3, 4), 4, 1.5, boxstyle="round,pad=0.1",
                                   facecolor=colors['postgres'], edgecolor='black', linewidth=2)
    ax1.add_patch(postgres_rect)
    ax1.text(5, 4.75, 'RDS PostgreSQL 14.9\nairflow-metadata-db\nMulti-AZ: Yes', 
             fontsize=10, fontweight='bold', ha='center', va='center', color='white')
    
    # Redis (if using CeleryExecutor alternative)
    redis_rect = FancyBboxPatch((8, 4), 3, 1.5, boxstyle="round,pad=0.1",
                                facecolor=colors['redis'], edgecolor='black', linewidth=2)
    ax1.add_patch(redis_rect)
    ax1.text(9.5, 4.75, 'ElastiCache Redis\n(Optional)\nFor CeleryExecutor', 
             fontsize=10, fontweight='bold', ha='center', va='center', color='white')
    
    # S3 Storage
    s3_rect = FancyBboxPatch((15, 4), 4, 1.5, boxstyle="round,pad=0.1",
                             facecolor=colors['s3'], edgecolor='black', linewidth=2)
    ax1.add_patch(s3_rect)
    ax3.text(17, 4.75, 'S3 Storage\nLogs & Artifacts\nData Lake', 
             fontsize=10, fontweight='bold', ha='center', va='center', color='white')
    
    # Add connection arrows
    # ALB to Webserver
    ax1.annotate('', xy=(5.5, 10), xytext=(11, 11),
                arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    
    # Scheduler to Database
    ax1.annotate('', xy=(5, 5.5), xytext=(9.5, 8.5),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))
    
    # Webserver to Database
    ax1.annotate('', xy=(5, 5.5), xytext=(5.5, 8.5),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))
    
    # Git-Sync to DAG Volume
    ax1.annotate('', xy=(8, 7), xytext=(6.5, 7),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='green'))
    
    # Scheduler to KubernetesExecutor
    ax1.annotate('', xy=(12, 9.25), xytext=(11, 9.25),
                arrowprops=dict(arrowstyle='->', lw=2, color='orange'))
    
    # KubernetesExecutor details (ax2)
    ax2.text(5.5, 5.5, 'KubernetesExecutor Configuration', fontsize=14, fontweight='bold', ha='center')
    
    # Executor flow
    executor_components = [
        (2, 4.5, 'Task\nSubmission', 'lightblue'),
        (4.5, 4.5, 'Pod\nCreation', colors['k8s_executor']),
        (7, 4.5, 'Task\nExecution', 'lightgreen'),
        (9.5, 4.5, 'Pod\nCleanup', 'orange')
    ]
    
    for x, y, label, color in executor_components:
        rect = FancyBboxPatch((x-0.6, y-0.4), 1.2, 0.8, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax2.add_patch(rect)
        ax2.text(x, y, label, fontsize=9, fontweight='bold', ha='center', va='center')
        
        if x < 9.5:
            ax2.annotate('', xy=(x+0.8, y), xytext=(x+0.6, y),
                        arrowprops=dict(arrowstyle='->', lw=1.5, color='red'))
    
    # Configuration details
    config_details = [
        '• Namespace: airflow',
        '• Worker Image: apache/airflow:2.7.0',
        '• Resource Requests: 100m CPU, 128Mi RAM',
        '• Resource Limits: 1000m CPU, 1Gi RAM',
        '• Pod Template: Custom security context',
        '• Annotations: IAM roles for service accounts'
    ]
    
    for i, detail in enumerate(config_details):
        ax2.text(0.5, 3.5 - i*0.4, detail, fontsize=9, va='center')
    
    # DAG Workflow visualization (ax3)
    ax3.text(5.5, 5.5, 'Sample DAG Workflow', fontsize=14, fontweight='bold', ha='center')
    
    # DAG tasks
    dag_tasks = [
        (1.5, 4, 'Start', 'lightgreen'),
        (3.5, 4.5, 'Extract\nData', 'lightblue'),
        (3.5, 3.5, 'Validate\nData', 'lightblue'),
        (6, 4, 'Transform\nData', 'orange'),
        (8.5, 4, 'Load to\nDatabase', 'yellow'),
        (10.5, 4, 'End', 'lightcoral')
    ]
    
    for x, y, label, color in dag_tasks:
        rect = FancyBboxPatch((x-0.5, y-0.3), 1, 0.6, boxstyle="round,pad=0.05",
                              facecolor=color, edgecolor='black')
        ax3.add_patch(rect)
        ax3.text(x, y, label, fontsize=8, fontweight='bold', ha='center', va='center')
    
    # Task dependencies
    dependencies = [
        ((2, 4), (3, 4.5)),     # Start -> Extract
        ((2, 4), (3, 3.5)),     # Start -> Validate  
        ((4, 4.5), (5.5, 4)),   # Extract -> Transform
        ((4, 3.5), (5.5, 4)),   # Validate -> Transform
        ((6.5, 4), (8, 4)),     # Transform -> Load
        ((9, 4), (10, 4))       # Load -> End
    ]
    
    for (x1, y1), (x2, y2) in dependencies:
        ax3.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='darkblue'))
    
    # DAG execution timeline
    timeline_y = 2.5
    ax3.text(5.5, 3, 'Execution Timeline (Hourly Schedule)', fontsize=10, fontweight='bold', ha='center')
    
    # Timeline bars
    timeline_tasks = [
        (1.5, timeline_y, 0.2, 'Start'),
        (2.5, timeline_y, 1.0, 'Extract'),
        (4, timeline_y, 0.5, 'Validate'),
        (5, timeline_y, 1.5, 'Transform'),
        (7, timeline_y, 2.0, 'Load'),
        (9.5, timeline_y, 0.2, 'End')
    ]
    
    for x, y, duration, label in timeline_tasks:
        rect = patches.Rectangle((x, y-0.1), duration, 0.2, 
                                facecolor='skyblue', edgecolor='black')
        ax3.add_patch(rect)
        ax3.text(x + duration/2, y, label, fontsize=7, ha='center', va='center')
    
    # Time markers
    for i in range(11):
        ax3.axvline(x=i+1, ymin=0.35, ymax=0.45, color='gray', linestyle='--', alpha=0.5)
        ax3.text(i+1, 1.8, f'{i}h', fontsize=7, ha='center')
    
    plt.tight_layout()
    return fig

def create_airflow_dag_management_diagram():
    """Create DAG management and deployment workflow diagram."""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 12))
    
    # DAG Development & Deployment Flow (ax1)
    ax1.set_xlim(0, 18)
    ax1.set_ylim(0, 8)
    ax1.set_aspect('equal')
    ax1.axis('off')
    ax1.text(9, 7.5, 'DAG Development & Deployment Pipeline', 
             fontsize=16, fontweight='bold', ha='center')
    
    # Development workflow
    dev_stages = [
        (2, 6, 'Developer\nLocal IDE', 'lightblue'),
        (5, 6, 'Git Repository\n(GitLab/GitHub)', '#F05032'),
        (8, 6, 'CI/CD Pipeline\n(Testing)', 'orange'),
        (11, 6, 'Staging\nEnvironment', 'yellow'),
        (14, 6, 'Production\nDeployment', 'lightgreen'),
        (17, 6, 'Airflow UI\nMonitoring', '#4C6EF5')
    ]
    
    for x, y, label, color in dev_stages:
        rect = FancyBboxPatch((x-0.8, y-0.6), 1.6, 1.2, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax1.add_patch(rect)
        ax1.text(x, y, label, fontsize=9, fontweight='bold', ha='center', va='center')
        
        if x < 17:
            ax1.annotate('', xy=(x+1.2, y), xytext=(x+0.8, y),
                        arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
    
    # Git-Sync process
    git_sync_process = [
        (3, 4, 'Git-Sync\nSidecar', '#F05032'),
        (6, 4, 'DAG Files\nSync', 'lightgray'),
        (9, 4, 'Shared Volume\n(PVC)', 'lightyellow'),
        (12, 4, 'Scheduler\nDAG Loading', '#FF6B35'),
        (15, 4, 'DAG Parsing\n& Validation', 'lightcoral')
    ]
    
    for x, y, label, color in git_sync_process:
        rect = FancyBboxPatch((x-0.7, y-0.4), 1.4, 0.8, boxstyle="round,pad=0.05",
                              facecolor=color, edgecolor='black')
        ax1.add_patch(rect)
        ax1.text(x, y, label, fontsize=8, fontweight='bold', ha='center', va='center')
        
        if x < 15:
            ax1.annotate('', xy=(x+1.1, y), xytext=(x+0.7, y),
                        arrowprops=dict(arrowstyle='->', lw=1.5, color='green'))
    
    # Quality gates
    quality_gates = [
        '1. Pre-commit hooks (black, flake8)',
        '2. Unit tests for DAG validation',
        '3. Integration tests in staging',
        '4. Performance benchmarks',
        '5. Security scan (Bandit)',
        '6. DAG integrity checks'
    ]
    
    ax1.text(1, 2.5, 'Quality Gates:', fontsize=12, fontweight='bold')
    for i, gate in enumerate(quality_gates):
        ax1.text(1.5, 2 - i*0.25, gate, fontsize=9, va='center')
    
    # DAG Monitoring & Operations (ax2)
    ax2.set_xlim(0, 18)
    ax2.set_ylim(0, 6)
    ax2.axis('off')
    ax2.text(9, 5.5, 'DAG Monitoring & Operational Metrics', 
             fontsize=16, fontweight='bold', ha='center')
    
    # Create monitoring dashboard mockup
    monitoring_panels = [
        (3, 4, 'Task Success\nRate: 98.5%', 'lightgreen'),
        (6, 4, 'Avg Execution\nTime: 12.3 min', 'lightblue'),
        (9, 4, 'Failed Tasks\nLast 24h: 3', 'lightcoral'),
        (12, 4, 'Active DAGs\nCount: 47', 'lightyellow'),
        (15, 4, 'Resource Usage\nCPU: 65%', 'orange')
    ]
    
    for x, y, label, color in monitoring_panels:
        rect = FancyBboxPatch((x-1, y-0.5), 2, 1, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax2.add_patch(rect)
        ax2.text(x, y, label, fontsize=9, fontweight='bold', ha='center', va='center')
    
    # Alert configuration
    alerts = [
        '• Task failure → Slack notification',
        '• DAG timeout → Email alert',
        '• Resource threshold → PagerDuty',
        '• SLA miss → Dashboard warning',
        '• Data quality → Data team alert'
    ]
    
    ax2.text(1, 2.5, 'Alert Configuration:', fontsize=12, fontweight='bold')
    for i, alert in enumerate(alerts):
        ax2.text(1.5, 2 - i*0.3, alert, fontsize=9, va='center')
    
    # Performance metrics chart
    ax2_chart = plt.axes([0.55, 0.05, 0.4, 0.15])
    
    # Generate sample performance data
    days = np.arange(1, 31)
    success_rate = 95 + 3 * np.sin(days/5) + np.random.normal(0, 1, 30)
    success_rate = np.clip(success_rate, 90, 100)
    
    ax2_chart.plot(days, success_rate, 'g-', linewidth=2, label='Success Rate %')
    ax2_chart.set_ylim(88, 102)
    ax2_chart.set_xlabel('Days')
    ax2_chart.set_ylabel('Success Rate (%)')
    ax2_chart.set_title('30-Day DAG Success Rate Trend')
    ax2_chart.grid(True, alpha=0.3)
    ax2_chart.legend()
    
    plt.tight_layout()
    return fig

def create_airflow_scaling_monitoring_diagram():
    """Create Airflow scaling strategies and monitoring architecture diagram."""
    
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)
    ax.set_aspect('equal')
    ax.axis('off')
    
    ax.text(9, 11.5, 'Airflow Scaling & Monitoring Architecture', 
            fontsize=18, fontweight='bold', ha='center')
    
    # Horizontal Pod Autoscaler section
    ax.text(4.5, 10.5, 'Horizontal Pod Autoscaler (HPA)', fontsize=14, fontweight='bold', ha='center')
    
    hpa_components = [
        (2, 9.5, 'Metrics\nServer', 'lightblue'),
        (4.5, 9.5, 'HPA\nController', 'orange'),
        (7, 9.5, 'Airflow\nPods', 'lightgreen')
    ]
    
    for x, y, label, color in hpa_components:
        rect = FancyBboxPatch((x-0.6, y-0.4), 1.2, 0.8, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, fontsize=9, fontweight='bold', ha='center', va='center')
    
    # HPA arrows
    ax.annotate('', xy=(3.9, 9.5), xytext=(2.6, 9.5),
               arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
    ax.annotate('', xy=(6.4, 9.5), xytext=(5.1, 9.5),
               arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
    
    # Scaling metrics
    scaling_metrics = [
        '• CPU Utilization > 70%',
        '• Memory Usage > 80%',
        '• Queue Depth > 50 tasks',
        '• Task Wait Time > 5 minutes'
    ]
    
    ax.text(1, 8.5, 'Scaling Triggers:', fontsize=12, fontweight='bold')
    for i, metric in enumerate(scaling_metrics):
        ax.text(1.5, 8 - i*0.3, metric, fontsize=10, va='center')
    
    # KubernetesExecutor Auto-scaling
    ax.text(13.5, 10.5, 'KubernetesExecutor Auto-scaling', fontsize=14, fontweight='bold', ha='center')
    
    # Task queue visualization
    queue_rect = FancyBboxPatch((11, 9), 2, 1, boxstyle="round,pad=0.1",
                                facecolor='lightyellow', edgecolor='black', linewidth=2)
    ax.add_patch(queue_rect)
    ax.text(12, 9.5, 'Task Queue\n(Queued: 15)', fontsize=9, fontweight='bold', ha='center', va='center')
    
    # Dynamic worker pods
    worker_positions = [(14, 9.5), (15.5, 9.5), (17, 9.5), (14, 8.5), (15.5, 8.5)]
    for i, (x, y) in enumerate(worker_positions):
        if i < 3:  # Active pods
            color = 'lightgreen'
            status = 'Active'
        else:  # Pending pods
            color = 'lightcoral'
            status = 'Pending'
        
        pod_circle = Circle((x, y), 0.3, facecolor=color, edgecolor='black')
        ax.add_patch(pod_circle)
        ax.text(x, y-0.6, f'Pod {i+1}\n{status}', fontsize=7, ha='center', va='center')
    
    # Queue to pods arrow
    ax.annotate('', xy=(13.7, 9.5), xytext=(13, 9.5),
               arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    
    # Monitoring & Observability
    ax.text(9, 7, 'Monitoring & Observability Stack', fontsize=14, fontweight='bold', ha='center')
    
    # Monitoring components
    monitoring_components = [
        (3, 5.5, 'Prometheus\nMetrics', '#E6522C'),
        (6, 5.5, 'Grafana\nDashboards', '#F46800'),
        (9, 5.5, 'ELK Stack\nLogs', '#005571'),
        (12, 5.5, 'CloudWatch\nAWS Metrics', '#FF9900'),
        (15, 5.5, 'PagerDuty\nAlerts', '#06AC38')
    ]
    
    for x, y, label, color in monitoring_components:
        rect = FancyBboxPatch((x-0.8, y-0.5), 1.6, 1, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, fontsize=9, fontweight='bold', ha='center', va='center', color='white')
    
    # Data flow arrows between monitoring components
    monitoring_connections = [
        ((3.8, 5.5), (5.2, 5.5)),   # Prometheus -> Grafana
        ((6.8, 5.5), (8.2, 5.5)),   # Grafana -> ELK
        ((9.8, 5.5), (11.2, 5.5)),  # ELK -> CloudWatch
        ((12.8, 5.5), (14.2, 5.5))  # CloudWatch -> PagerDuty
    ]
    
    for (x1, y1), (x2, y2) in monitoring_connections:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', lw=1.5, color='purple'))
    
    # Key metrics being monitored
    key_metrics = [
        '• DAG Success/Failure Rates',
        '• Task Execution Duration',
        '• Resource Utilization (CPU/Memory)',
        '• Queue Depth & Wait Times',
        '• Database Connection Pool',
        '• Pod Creation/Termination Events',
        '• Storage I/O Performance',
        '• Network Latency & Throughput'
    ]
    
    ax.text(1, 4, 'Key Metrics Monitored:', fontsize=12, fontweight='bold')
    for i, metric in enumerate(key_metrics):
        ax.text(1.5, 3.5 - i*0.25, metric, fontsize=9, va='center')
    
    # SLA and Performance Targets
    sla_targets = [
        '• Task Success Rate: > 99%',
        '• P95 Task Duration: < 30 min',
        '• System Availability: > 99.9%',
        '• Alert Response: < 5 min',
        '• Recovery Time: < 15 min'
    ]
    
    ax.text(11, 4, 'SLA Targets:', fontsize=12, fontweight='bold')
    for i, target in enumerate(sla_targets):
        ax.text(11.5, 3.5 - i*0.25, target, fontsize=9, va='center')
    
    # Automated remediation workflows
    remediation_rect = FancyBboxPatch((6, 1), 6, 1.5, boxstyle="round,pad=0.1",
                                      facecolor='lightsteelblue', edgecolor='black', linewidth=2)
    ax.add_patch(remediation_rect)
    ax.text(9, 1.75, 'Automated Remediation\n• Pod restart on failure\n• Resource scaling\n• Alert escalation', 
            fontsize=10, fontweight='bold', ha='center', va='center')
    
    plt.tight_layout()
    return fig

def main():
    """Generate all Airflow diagrams."""
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "docs" / "architecture"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating Airflow diagrams...")
    
    # Generate architecture diagram
    fig1 = create_airflow_architecture_diagram()
    fig1.savefig(output_dir / "airflow_architecture.png", dpi=300, bbox_inches='tight')
    fig1.savefig(output_dir / "airflow_architecture.svg", format='svg', bbox_inches='tight')
    plt.close(fig1)
    print("Airflow architecture diagram saved (PNG + SVG)")
    
    # Generate DAG management diagram
    fig2 = create_airflow_dag_management_diagram()
    fig2.savefig(output_dir / "airflow_dag_management.png", dpi=300, bbox_inches='tight')
    fig2.savefig(output_dir / "airflow_dag_management.svg", format='svg', bbox_inches='tight')
    plt.close(fig2)
    print("Airflow DAG management diagram saved (PNG + SVG)")
    
    # Generate scaling and monitoring diagram
    fig3 = create_airflow_scaling_monitoring_diagram()
    fig3.savefig(output_dir / "airflow_scaling_monitoring.png", dpi=300, bbox_inches='tight')
    fig3.savefig(output_dir / "airflow_scaling_monitoring.svg", format='svg', bbox_inches='tight')
    plt.close(fig3)
    print("Airflow scaling & monitoring diagram saved (PNG + SVG)")
    
    print("All Airflow diagrams generated successfully!")

if __name__ == "__main__":
    main()
