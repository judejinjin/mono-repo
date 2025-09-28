#!/usr/bin/env python3
"""
JupyterHub Session and Resource Cleanup System
Automatically cleans up idle sessions, manages resources, and optimizes storage
"""

import asyncio
import logging
import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import aiohttp
import yaml
from kubernetes import client, config
import boto3

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from config import get_config

class JupyterHubCleaner:
    """Comprehensive JupyterHub cleanup system"""
    
    def __init__(self, environment: str = 'dev'):
        self.environment = environment
        self.config = get_config(environment)
        self.setup_logging()
        self.setup_kubernetes()
        
        # Cleanup thresholds
        self.cleanup_config = {
            'idle_session_hours': 24,  # Hours before idle session cleanup
            'inactive_user_days': 30,  # Days before inactive user cleanup
            'log_retention_days': 7,   # Days to retain logs
            'temp_file_hours': 6,      # Hours before temp file cleanup
            'max_user_storage_gb': 10, # Max storage per user
            'max_concurrent_sessions': 5  # Max sessions per user
        }
        
    def setup_logging(self):
        """Setup structured logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(f'jupyterhub-cleaner-{self.environment}')
        
    def setup_kubernetes(self):
        """Initialize Kubernetes client"""
        try:
            if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount'):
                config.load_incluster_config()
            else:
                config.load_kube_config()
            
            self.k8s_core = client.CoreV1Api()
            self.k8s_apps = client.AppsV1Api()
            self.k8s_batch = client.BatchV1Api()
        except Exception as e:
            self.logger.error(f"Failed to setup Kubernetes client: {e}")
            self.k8s_core = None
            
    async def get_jupyterhub_users(self) -> List[Dict[str, Any]]:
        """Get all JupyterHub users and their session information"""
        users = []
        
        try:
            jupyterhub_url = f"http://jupyterhub-service.jupyterhub.svc.cluster.local:8000"
            api_token = os.getenv('JUPYTERHUB_API_TOKEN')
            
            if not api_token:
                self.logger.error("No JupyterHub API token found")
                return users
                
            headers = {'Authorization': f'Bearer {api_token}'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{jupyterhub_url}/hub/api/users", headers=headers) as resp:
                    if resp.status == 200:
                        users_data = await resp.json()
                        
                        for username, user_info in users_data.items():
                            user = {
                                'username': username,
                                'last_activity': user_info.get('last_activity'),
                                'servers': user_info.get('servers', {}),
                                'active_sessions': len(user_info.get('servers', {})),
                                'admin': user_info.get('admin', False)
                            }
                            users.append(user)
                            
                    else:
                        self.logger.error(f"Failed to get users: {resp.status}")
                        
        except Exception as e:
            self.logger.error(f"Error getting JupyterHub users: {e}")
            
        return users
        
    async def identify_idle_sessions(self, users: List[Dict[str, Any]], dry_run: bool = True) -> List[Dict[str, Any]]:
        """Identify idle user sessions that should be cleaned up"""
        idle_sessions = []
        cutoff_time = datetime.now() - timedelta(hours=self.cleanup_config['idle_session_hours'])
        
        for user in users:
            username = user['username']
            last_activity = user.get('last_activity')
            
            if not last_activity:
                continue
                
            try:
                # Parse last activity time
                if isinstance(last_activity, str):
                    last_activity_dt = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                else:
                    last_activity_dt = last_activity
                    
                # Check if session is idle
                if last_activity_dt < cutoff_time and user['active_sessions'] > 0:
                    idle_session = {
                        'username': username,
                        'last_activity': last_activity,
                        'idle_hours': (datetime.now() - last_activity_dt).total_seconds() / 3600,
                        'active_sessions': user['active_sessions'],
                        'servers': user['servers']
                    }
                    idle_sessions.append(idle_session)
                    
                    if not dry_run:
                        self.logger.info(f"Identified idle session for user {username}, "
                                       f"idle for {idle_session['idle_hours']:.1f} hours")
                        
            except Exception as e:
                self.logger.warning(f"Error processing user {username}: {e}")
                
        return idle_sessions
        
    async def cleanup_idle_sessions(self, idle_sessions: List[Dict[str, Any]], dry_run: bool = True) -> int:
        """Clean up identified idle sessions"""
        cleanup_count = 0
        
        try:
            jupyterhub_url = f"http://jupyterhub-service.jupyterhub.svc.cluster.local:8000"
            api_token = os.getenv('JUPYTERHUB_API_TOKEN')
            
            if not api_token:
                self.logger.error("No JupyterHub API token found")
                return 0
                
            headers = {'Authorization': f'Bearer {api_token}'}
            
            async with aiohttp.ClientSession() as session:
                for idle_session in idle_sessions:
                    username = idle_session['username']
                    
                    if dry_run:
                        self.logger.info(f"[DRY RUN] Would stop sessions for user {username}")
                        cleanup_count += 1
                        continue
                        
                    try:
                        # Stop all user servers
                        stop_url = f"{jupyterhub_url}/hub/api/users/{username}/servers"
                        async with session.delete(stop_url, headers=headers) as resp:
                            if resp.status in [200, 204]:
                                cleanup_count += 1
                                self.logger.info(f"Stopped idle sessions for user {username}")
                            else:
                                self.logger.warning(f"Failed to stop sessions for {username}: {resp.status}")
                                
                    except Exception as e:
                        self.logger.error(f"Error stopping sessions for {username}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error during session cleanup: {e}")
            
        return cleanup_count
        
    async def cleanup_kubernetes_resources(self, dry_run: bool = True) -> Dict[str, int]:
        """Clean up orphaned Kubernetes resources"""
        cleanup_stats = {
            'pods_cleaned': 0,
            'jobs_cleaned': 0,
            'pvcs_cleaned': 0
        }
        
        if not self.k8s_core:
            self.logger.warning("Kubernetes client not available")
            return cleanup_stats
            
        try:
            namespace = 'jupyterhub'
            
            # Clean up completed jobs
            jobs = self.k8s_batch.list_namespaced_job(namespace)
            for job in jobs.items:
                if job.status.succeeded or (job.status.failed and job.status.failed > 3):
                    if dry_run:
                        self.logger.info(f"[DRY RUN] Would delete job {job.metadata.name}")
                        cleanup_stats['jobs_cleaned'] += 1
                    else:
                        try:
                            self.k8s_batch.delete_namespaced_job(
                                name=job.metadata.name,
                                namespace=namespace,
                                body=client.V1DeleteOptions(propagation_policy='Foreground')
                            )
                            cleanup_stats['jobs_cleaned'] += 1
                            self.logger.info(f"Deleted completed job {job.metadata.name}")
                        except Exception as e:
                            self.logger.warning(f"Failed to delete job {job.metadata.name}: {e}")
                            
            # Clean up failed/orphaned pods
            pods = self.k8s_core.list_namespaced_pod(namespace)
            for pod in pods.items:
                # Clean up failed pods older than 1 hour
                if pod.status.phase in ['Failed', 'Succeeded']:
                    creation_time = pod.metadata.creation_timestamp
                    if (datetime.now(creation_time.tzinfo) - creation_time).total_seconds() > 3600:
                        if dry_run:
                            self.logger.info(f"[DRY RUN] Would delete pod {pod.metadata.name}")
                            cleanup_stats['pods_cleaned'] += 1
                        else:
                            try:
                                self.k8s_core.delete_namespaced_pod(
                                    name=pod.metadata.name,
                                    namespace=namespace
                                )
                                cleanup_stats['pods_cleaned'] += 1
                                self.logger.info(f"Deleted failed pod {pod.metadata.name}")
                            except Exception as e:
                                self.logger.warning(f"Failed to delete pod {pod.metadata.name}: {e}")
                                
        except Exception as e:
            self.logger.error(f"Error during Kubernetes cleanup: {e}")
            
        return cleanup_stats
        
    async def cleanup_storage(self, dry_run: bool = True) -> Dict[str, Any]:
        """Clean up storage and temporary files"""
        storage_stats = {
            'temp_files_cleaned': 0,
            'old_logs_cleaned': 0,
            'storage_freed_mb': 0
        }
        
        try:
            # This would typically involve running cleanup scripts on the EFS volumes
            # For now, we'll create a Kubernetes job to handle storage cleanup
            
            if not self.k8s_batch:
                self.logger.warning("Kubernetes batch client not available")
                return storage_stats
                
            cleanup_job_spec = {
                'apiVersion': 'batch/v1',
                'kind': 'Job',
                'metadata': {
                    'name': f'jupyterhub-storage-cleanup-{int(datetime.now().timestamp())}',
                    'namespace': 'jupyterhub'
                },
                'spec': {
                    'template': {
                        'spec': {
                            'containers': [{
                                'name': 'cleanup',
                                'image': 'alpine:latest',
                                'command': ['/bin/sh'],
                                'args': ['-c', f"""
                                    echo "Starting storage cleanup..."
                                    
                                    # Clean temp files older than {self.cleanup_config['temp_file_hours']} hours
                                    find /shared -name "*.tmp" -mtime +{self.cleanup_config['temp_file_hours']/24} -type f {'| wc -l' if dry_run else '-delete'}
                                    
                                    # Clean old log files
                                    find /shared -name "*.log" -mtime +{self.cleanup_config['log_retention_days']} -type f {'| wc -l' if dry_run else '-delete'}
                                    
                                    # Clean old checkpoint files
                                    find /shared -path "*/.ipynb_checkpoints/*" -mtime +1 -type f {'| wc -l' if dry_run else '-delete'}
                                    
                                    echo "Storage cleanup completed"
                                """],
                                'volumeMounts': [{
                                    'name': 'shared-storage',
                                    'mountPath': '/shared'
                                }]
                            }],
                            'volumes': [{
                                'name': 'shared-storage',
                                'persistentVolumeClaim': {
                                    'claimName': 'jupyterhub-shared-pvc'
                                }
                            }],
                            'restartPolicy': 'Never'
                        }
                    },
                    'backoffLimit': 2
                }
            }
            
            if dry_run:
                self.logger.info("[DRY RUN] Would create storage cleanup job")
                storage_stats['temp_files_cleaned'] = 10  # Mock data for dry run
                storage_stats['old_logs_cleaned'] = 5
                storage_stats['storage_freed_mb'] = 150
            else:
                # Create the cleanup job
                self.k8s_batch.create_namespaced_job(
                    namespace='jupyterhub',
                    body=cleanup_job_spec
                )
                self.logger.info("Created storage cleanup job")
                
        except Exception as e:
            self.logger.error(f"Error during storage cleanup: {e}")
            
        return storage_stats
        
    async def generate_cleanup_report(self, session_cleanup: int, k8s_cleanup: Dict[str, int], 
                                    storage_cleanup: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive cleanup report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'environment': self.environment,
            'session_cleanup': {
                'idle_sessions_cleaned': session_cleanup
            },
            'kubernetes_cleanup': k8s_cleanup,
            'storage_cleanup': storage_cleanup,
            'total_resources_freed': {
                'sessions': session_cleanup,
                'pods': k8s_cleanup.get('pods_cleaned', 0),
                'jobs': k8s_cleanup.get('jobs_cleaned', 0),
                'storage_mb': storage_cleanup.get('storage_freed_mb', 0)
            }
        }
        
        return report
        
    async def run_cleanup_cycle(self, dry_run: bool = True) -> Dict[str, Any]:
        """Execute complete cleanup cycle"""
        self.logger.info(f"Starting cleanup cycle for {self.environment} {'(DRY RUN)' if dry_run else ''}")
        
        # Get current users and sessions
        users = await self.get_jupyterhub_users()
        self.logger.info(f"Found {len(users)} users")
        
        # Identify idle sessions
        idle_sessions = await self.identify_idle_sessions(users, dry_run)
        self.logger.info(f"Found {len(idle_sessions)} idle sessions")
        
        # Cleanup idle sessions
        session_cleanup_count = await self.cleanup_idle_sessions(idle_sessions, dry_run)
        
        # Cleanup Kubernetes resources
        k8s_cleanup_stats = await self.cleanup_kubernetes_resources(dry_run)
        
        # Cleanup storage
        storage_cleanup_stats = await self.cleanup_storage(dry_run)
        
        # Generate report
        report = await self.generate_cleanup_report(
            session_cleanup_count, k8s_cleanup_stats, storage_cleanup_stats
        )
        
        self.logger.info(f"Cleanup cycle completed. Sessions: {session_cleanup_count}, "
                        f"Pods: {k8s_cleanup_stats['pods_cleaned']}, "
                        f"Jobs: {k8s_cleanup_stats['jobs_cleaned']}")
        
        return report

async def main():
    """Main cleanup function"""
    parser = argparse.ArgumentParser(description='JupyterHub Cleanup System')
    parser.add_argument('--environment', choices=['dev', 'uat', 'prod'], 
                       default='dev', help='Environment to clean')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Run in dry-run mode (default)')
    parser.add_argument('--execute', action='store_true',
                       help='Actually execute cleanup (overrides dry-run)')
    parser.add_argument('--output', type=str, 
                       help='Output file for cleanup report')
    
    args = parser.parse_args()
    
    # Determine if this is a dry run
    dry_run = not args.execute
    
    cleaner = JupyterHubCleaner(args.environment)
    
    report = await cleaner.run_cleanup_cycle(dry_run)
    
    print(json.dumps(report, indent=2))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())