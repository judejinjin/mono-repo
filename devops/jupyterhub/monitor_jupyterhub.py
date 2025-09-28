#!/usr/bin/env python3
"""
JupyterHub Monitoring and Health Check System
Monitors JupyterHub infrastructure, user sessions, and resource utilization
"""

import asyncio
import logging
import json
import time
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import aiohttp
import yaml
import boto3
from kubernetes import client, config
import pandas as pd
import psutil
import os
import sys

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from config import get_config

class JupyterHubMonitor:
    """Comprehensive JupyterHub monitoring system"""
    
    def __init__(self, environment: str = 'dev'):
        self.environment = environment
        self.config = get_config(environment)
        self.setup_logging()
        self.setup_kubernetes()
        self.setup_cloudwatch()
        
        # Monitoring thresholds
        self.thresholds = {
            'cpu_utilization': 80.0,
            'memory_utilization': 85.0,
            'disk_utilization': 90.0,
            'active_sessions_limit': 100,
            'response_time_ms': 2000,
            'error_rate_percent': 5.0
        }
        
    def setup_logging(self):
        """Setup structured logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(f'jupyterhub-monitor-{self.environment}')
        
    def setup_kubernetes(self):
        """Initialize Kubernetes client"""
        try:
            if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount'):
                config.load_incluster_config()
            else:
                config.load_kube_config()
            
            self.k8s_apps = client.AppsV1Api()
            self.k8s_core = client.CoreV1Api()
            self.k8s_metrics = client.CustomObjectsApi()
        except Exception as e:
            self.logger.error(f"Failed to setup Kubernetes client: {e}")
            self.k8s_apps = None
            
    def setup_cloudwatch(self):
        """Initialize CloudWatch client for metrics"""
        if self.environment in ['prod', 'uat']:
            try:
                self.cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
            except Exception as e:
                self.logger.warning(f"Failed to setup CloudWatch: {e}")
                self.cloudwatch = None
        else:
            self.cloudwatch = None
            
    async def check_jupyterhub_health(self) -> Dict[str, Any]:
        """Check JupyterHub hub health status"""
        health_status = {
            'status': 'unknown',
            'response_time_ms': None,
            'active_users': 0,
            'active_sessions': 0,
            'errors': []
        }
        
        try:
            jupyterhub_url = f"http://jupyterhub-service.jupyterhub.svc.cluster.local:8000"
            api_token = os.getenv('JUPYTERHUB_API_TOKEN')
            
            if not api_token:
                self.logger.warning("No JupyterHub API token found")
                return health_status
                
            headers = {'Authorization': f'Bearer {api_token}'}
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                
                # Health check
                async with session.get(f"{jupyterhub_url}/hub/health", headers=headers) as resp:
                    response_time = (time.time() - start_time) * 1000
                    health_status['response_time_ms'] = response_time
                    
                    if resp.status == 200:
                        health_status['status'] = 'healthy'
                    else:
                        health_status['status'] = 'unhealthy'
                        health_status['errors'].append(f"Health check failed: {resp.status}")
                
                # Get user and session info
                try:
                    async with session.get(f"{jupyterhub_url}/hub/api/users", headers=headers) as resp:
                        if resp.status == 200:
                            users_data = await resp.json()
                            health_status['active_users'] = len(users_data)
                            
                            active_sessions = sum(1 for user in users_data.values() 
                                                if user.get('servers', {}))
                            health_status['active_sessions'] = active_sessions
                            
                except Exception as e:
                    health_status['errors'].append(f"Failed to get user info: {e}")
                    
        except Exception as e:
            health_status['status'] = 'error'
            health_status['errors'].append(f"Health check error: {e}")
            self.logger.error(f"JupyterHub health check failed: {e}")
            
        return health_status
        
    async def check_kubernetes_resources(self) -> Dict[str, Any]:
        """Monitor Kubernetes resources for JupyterHub"""
        k8s_status = {
            'deployments': {},
            'pods': {},
            'services': {},
            'resource_utilization': {},
            'errors': []
        }
        
        if not self.k8s_apps:
            k8s_status['errors'].append("Kubernetes client not available")
            return k8s_status
            
        try:
            namespace = 'jupyterhub'
            
            # Check deployments
            deployments = self.k8s_apps.list_namespaced_deployment(namespace)
            for deployment in deployments.items:
                name = deployment.metadata.name
                ready_replicas = deployment.status.ready_replicas or 0
                desired_replicas = deployment.spec.replicas or 0
                
                k8s_status['deployments'][name] = {
                    'ready_replicas': ready_replicas,
                    'desired_replicas': desired_replicas,
                    'available': ready_replicas == desired_replicas
                }
                
            # Check pods
            pods = self.k8s_core.list_namespaced_pod(namespace)
            for pod in pods.items:
                name = pod.metadata.name
                phase = pod.status.phase
                
                k8s_status['pods'][name] = {
                    'phase': phase,
                    'ready': phase == 'Running'
                }
                
            # Check services
            services = self.k8s_core.list_namespaced_service(namespace)
            for service in services.items:
                name = service.metadata.name
                k8s_status['services'][name] = {
                    'type': service.spec.type,
                    'cluster_ip': service.spec.cluster_ip
                }
                
        except Exception as e:
            k8s_status['errors'].append(f"Kubernetes monitoring error: {e}")
            self.logger.error(f"Kubernetes resource check failed: {e}")
            
        return k8s_status
        
    async def check_resource_utilization(self) -> Dict[str, Any]:
        """Monitor system resource utilization"""
        resources = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'network_io': dict(psutil.net_io_counters()._asdict()),
            'alerts': []
        }
        
        # Check against thresholds
        if resources['cpu_percent'] > self.thresholds['cpu_utilization']:
            resources['alerts'].append({
                'type': 'CPU_HIGH',
                'value': resources['cpu_percent'],
                'threshold': self.thresholds['cpu_utilization']
            })
            
        if resources['memory_percent'] > self.thresholds['memory_utilization']:
            resources['alerts'].append({
                'type': 'MEMORY_HIGH',
                'value': resources['memory_percent'],
                'threshold': self.thresholds['memory_utilization']
            })
            
        if resources['disk_percent'] > self.thresholds['disk_utilization']:
            resources['alerts'].append({
                'type': 'DISK_HIGH',
                'value': resources['disk_percent'],
                'threshold': self.thresholds['disk_utilization']
            })
            
        return resources
        
    async def check_storage_status(self) -> Dict[str, Any]:
        """Monitor EFS and persistent storage"""
        storage_status = {
            'efs_available': False,
            'pvc_status': {},
            'storage_utilization': {},
            'errors': []
        }
        
        try:
            if self.k8s_core:
                # Check PVCs
                namespace = 'jupyterhub'
                pvcs = self.k8s_core.list_namespaced_persistent_volume_claim(namespace)
                
                for pvc in pvcs.items:
                    name = pvc.metadata.name
                    phase = pvc.status.phase
                    storage_status['pvc_status'][name] = {
                        'phase': phase,
                        'bound': phase == 'Bound'
                    }
                    
        except Exception as e:
            storage_status['errors'].append(f"Storage check error: {e}")
            
        return storage_status
        
    def send_cloudwatch_metrics(self, metrics_data: Dict[str, Any]):
        """Send metrics to CloudWatch"""
        if not self.cloudwatch:
            return
            
        try:
            metric_data = []
            
            # JupyterHub health metrics
            if 'jupyterhub_health' in metrics_data:
                health = metrics_data['jupyterhub_health']
                
                metric_data.extend([
                    {
                        'MetricName': 'ActiveUsers',
                        'Value': health.get('active_users', 0),
                        'Unit': 'Count',
                        'Dimensions': [
                            {'Name': 'Environment', 'Value': self.environment},
                            {'Name': 'Service', 'Value': 'JupyterHub'}
                        ]
                    },
                    {
                        'MetricName': 'ActiveSessions',
                        'Value': health.get('active_sessions', 0),
                        'Unit': 'Count',
                        'Dimensions': [
                            {'Name': 'Environment', 'Value': self.environment},
                            {'Name': 'Service', 'Value': 'JupyterHub'}
                        ]
                    },
                    {
                        'MetricName': 'ResponseTime',
                        'Value': health.get('response_time_ms', 0),
                        'Unit': 'Milliseconds',
                        'Dimensions': [
                            {'Name': 'Environment', 'Value': self.environment},
                            {'Name': 'Service', 'Value': 'JupyterHub'}
                        ]
                    }
                ])
                
            # Resource utilization metrics
            if 'resource_utilization' in metrics_data:
                resources = metrics_data['resource_utilization']
                
                metric_data.extend([
                    {
                        'MetricName': 'CPUUtilization',
                        'Value': resources.get('cpu_percent', 0),
                        'Unit': 'Percent',
                        'Dimensions': [
                            {'Name': 'Environment', 'Value': self.environment},
                            {'Name': 'Service', 'Value': 'JupyterHub'}
                        ]
                    },
                    {
                        'MetricName': 'MemoryUtilization',
                        'Value': resources.get('memory_percent', 0),
                        'Unit': 'Percent',
                        'Dimensions': [
                            {'Name': 'Environment', 'Value': self.environment},
                            {'Name': 'Service', 'Value': 'JupyterHub'}
                        ]
                    }
                ])
                
            # Send metrics in batches
            if metric_data:
                for i in range(0, len(metric_data), 20):  # CloudWatch limit
                    batch = metric_data[i:i+20]
                    self.cloudwatch.put_metric_data(
                        Namespace='RiskPlatform/JupyterHub',
                        MetricData=batch
                    )
                    
        except Exception as e:
            self.logger.error(f"Failed to send CloudWatch metrics: {e}")
            
    async def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Execute complete monitoring cycle"""
        self.logger.info(f"Starting monitoring cycle for {self.environment}")
        
        monitoring_results = {
            'timestamp': datetime.now().isoformat(),
            'environment': self.environment,
            'jupyterhub_health': await self.check_jupyterhub_health(),
            'kubernetes_resources': await self.check_kubernetes_resources(),
            'resource_utilization': await self.check_resource_utilization(),
            'storage_status': await self.check_storage_status()
        }
        
        # Calculate overall health score
        health_score = self.calculate_health_score(monitoring_results)
        monitoring_results['health_score'] = health_score
        
        # Send metrics to CloudWatch
        self.send_cloudwatch_metrics(monitoring_results)
        
        # Log alerts
        self.log_alerts(monitoring_results)
        
        self.logger.info(f"Monitoring cycle completed. Health score: {health_score}%")
        
        return monitoring_results
        
    def calculate_health_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall health score (0-100)"""
        score = 100.0
        
        # JupyterHub health impact
        if results['jupyterhub_health']['status'] != 'healthy':
            score -= 30.0
            
        # Resource utilization impact
        resources = results['resource_utilization']
        if resources['cpu_percent'] > self.thresholds['cpu_utilization']:
            score -= 15.0
        if resources['memory_percent'] > self.thresholds['memory_utilization']:
            score -= 15.0
        if resources['disk_percent'] > self.thresholds['disk_utilization']:
            score -= 15.0
            
        # Kubernetes resources impact
        k8s = results['kubernetes_resources']
        for deployment, status in k8s['deployments'].items():
            if not status['available']:
                score -= 10.0
                
        # Storage impact
        storage = results['storage_status']
        if storage['errors']:
            score -= 10.0
            
        return max(0.0, score)
        
    def log_alerts(self, results: Dict[str, Any]):
        """Log and process alerts"""
        alerts = []
        
        # Collect all alerts
        alerts.extend(results['resource_utilization'].get('alerts', []))
        
        if results['jupyterhub_health']['status'] != 'healthy':
            alerts.append({
                'type': 'JUPYTERHUB_UNHEALTHY',
                'errors': results['jupyterhub_health']['errors']
            })
            
        # Log alerts
        for alert in alerts:
            self.logger.warning(f"ALERT: {alert}")
            
        # Send critical alerts to notification system
        if alerts and self.environment == 'prod':
            # Integration with alerting system would go here
            pass

async def main():
    """Main monitoring function"""
    parser = argparse.ArgumentParser(description='JupyterHub Monitoring System')
    parser.add_argument('--environment', choices=['dev', 'uat', 'prod'], 
                       default='dev', help='Environment to monitor')
    parser.add_argument('--continuous', action='store_true', 
                       help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=60, 
                       help='Monitoring interval in seconds')
    parser.add_argument('--output', type=str, 
                       help='Output file for monitoring results')
    
    args = parser.parse_args()
    
    monitor = JupyterHubMonitor(args.environment)
    
    if args.continuous:
        print(f"Starting continuous monitoring for {args.environment} environment...")
        while True:
            try:
                results = await monitor.run_monitoring_cycle()
                
                if args.output:
                    with open(args.output, 'w') as f:
                        json.dump(results, f, indent=2)
                        
                await asyncio.sleep(args.interval)
                
            except KeyboardInterrupt:
                print("Monitoring stopped by user")
                break
            except Exception as e:
                monitor.logger.error(f"Monitoring cycle failed: {e}")
                await asyncio.sleep(args.interval)
    else:
        results = await monitor.run_monitoring_cycle()
        print(json.dumps(results, indent=2))
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())