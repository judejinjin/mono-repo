#!/usr/bin/env python3
"""
Airflow API Client for triggering DAGs externally.
This script demonstrates how to trigger Airflow DAGs from outside the VPC.
"""

import requests
import json
import base64
from datetime import datetime
from typing import Dict, Any, Optional
import os

class AirflowAPIClient:
    """Client for interacting with Airflow REST API."""
    
    def __init__(self, airflow_url: str, username: str, password: str):
        """
        Initialize Airflow API client.
        
        Args:
            airflow_url: Base URL of Airflow webserver (e.g., https://airflow.example.com)
            username: Airflow username
            password: Airflow password
        """
        self.base_url = airflow_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1"
        
        # Create basic auth header
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }
        
    def test_connection(self) -> bool:
        """Test connection to Airflow API."""
        try:
            response = requests.get(
                f"{self.api_url}/health",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def get_dag_info(self, dag_id: str) -> Dict[str, Any]:
        """Get information about a specific DAG."""
        try:
            response = requests.get(
                f"{self.api_url}/dags/{dag_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get DAG info: {e}")
            return {}
    
    def trigger_dag(self, dag_id: str, conf: Optional[Dict[str, Any]] = None, 
                   dag_run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Trigger a DAG run with optional configuration.
        
        Args:
            dag_id: ID of the DAG to trigger
            conf: Configuration dictionary to pass to the DAG
            dag_run_id: Optional custom run ID
            
        Returns:
            Dictionary containing DAG run information
        """
        payload = {}
        
        if conf:
            payload['conf'] = conf
            
        if dag_run_id:
            payload['dag_run_id'] = dag_run_id
        else:
            # Generate unique run ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            payload['dag_run_id'] = f"api_trigger_{timestamp}"
        
        try:
            response = requests.post(
                f"{self.api_url}/dags/{dag_id}/dagRuns",
                headers=self.headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to trigger DAG: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return {}
    
    def get_dag_run_status(self, dag_id: str, dag_run_id: str) -> Dict[str, Any]:
        """Get status of a specific DAG run."""
        try:
            response = requests.get(
                f"{self.api_url}/dags/{dag_id}/dagRuns/{dag_run_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get DAG run status: {e}")
            return {}
    
    def get_task_instances(self, dag_id: str, dag_run_id: str) -> Dict[str, Any]:
        """Get task instances for a DAG run."""
        try:
            response = requests.get(
                f"{self.api_url}/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get task instances: {e}")
            return {}

def trigger_risk_analysis(client: AirflowAPIClient, portfolio_id: str, 
                         analysis_type: str = "full", **kwargs) -> str:
    """
    Trigger the API-based risk analysis DAG.
    
    Args:
        client: AirflowAPIClient instance
        portfolio_id: Portfolio ID to analyze
        analysis_type: Type of analysis ('full', 'var_only', 'stress_test', 'attribution')
        **kwargs: Additional parameters
        
    Returns:
        DAG run ID if successful
    """
    dag_id = "api_triggered_risk_analysis"
    
    # Prepare configuration
    conf = {
        "portfolio_id": portfolio_id,
        "analysis_type": analysis_type,
        "risk_horizon": kwargs.get("risk_horizon", 1),
        "confidence_level": kwargs.get("confidence_level", 0.95),
        "include_stress_test": kwargs.get("include_stress_test", True),
        "notification_email": kwargs.get("notification_email", None)
    }
    
    print(f"Triggering risk analysis for portfolio: {portfolio_id}")
    print(f"Configuration: {json.dumps(conf, indent=2)}")
    
    # Trigger the DAG
    result = client.trigger_dag(dag_id, conf=conf)
    
    if result:
        dag_run_id = result.get('dag_run_id')
        print(f"✅ DAG triggered successfully!")
        print(f"DAG Run ID: {dag_run_id}")
        print(f"State: {result.get('state')}")
        print(f"Execution Date: {result.get('execution_date')}")
        return dag_run_id
    else:
        print("❌ Failed to trigger DAG")
        return ""

def monitor_dag_run(client: AirflowAPIClient, dag_id: str, dag_run_id: str) -> None:
    """Monitor a DAG run and print status updates."""
    import time
    
    print(f"Monitoring DAG run: {dag_run_id}")
    
    while True:
        status = client.get_dag_run_status(dag_id, dag_run_id)
        
        if not status:
            print("❌ Failed to get DAG run status")
            break
            
        state = status.get('state')
        print(f"Current state: {state}")
        
        if state in ['success', 'failed']:
            print(f"✅ DAG run completed with state: {state}")
            
            # Get task details
            tasks = client.get_task_instances(dag_id, dag_run_id)
            if tasks and 'task_instances' in tasks:
                print("\nTask Status:")
                for task in tasks['task_instances']:
                    task_id = task.get('task_id')
                    task_state = task.get('state')
                    print(f"  {task_id}: {task_state}")
            break
        elif state == 'running':
            print("⏳ DAG is still running...")
            time.sleep(10)  # Wait 10 seconds before checking again
        else:
            print(f"🔄 DAG state: {state}")
            time.sleep(5)

def main():
    """Example usage of the Airflow API client."""
    
    # Configuration - these should come from environment variables or config file
    AIRFLOW_URL = os.getenv('AIRFLOW_URL', 'https://airflow.mono-repo.example.com')
    AIRFLOW_USERNAME = os.getenv('AIRFLOW_USERNAME', 'admin')
    AIRFLOW_PASSWORD = os.getenv('AIRFLOW_PASSWORD', 'admin')
    
    # Create client
    client = AirflowAPIClient(AIRFLOW_URL, AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
    
    # Test connection
    print("Testing connection to Airflow API...")
    if not client.test_connection():
        print("❌ Failed to connect to Airflow API")
        return
    
    print("✅ Connected to Airflow API successfully")
    
    # Example 1: Trigger full risk analysis
    print("\n" + "="*50)
    print("Example 1: Full Risk Analysis")
    print("="*50)
    
    dag_run_id = trigger_risk_analysis(
        client,
        portfolio_id="PORTFOLIO_001",
        analysis_type="full",
        risk_horizon=5,
        confidence_level=0.99,
        notification_email="risk-team@company.com"
    )
    
    if dag_run_id:
        # Monitor the DAG run
        monitor_dag_run(client, "api_triggered_risk_analysis", dag_run_id)
    
    # Example 2: Trigger VaR-only analysis
    print("\n" + "="*50)
    print("Example 2: VaR-Only Analysis")
    print("="*50)
    
    dag_run_id = trigger_risk_analysis(
        client,
        portfolio_id="PORTFOLIO_002",
        analysis_type="var_only",
        risk_horizon=1,
        confidence_level=0.95
    )
    
    print(f"VaR analysis triggered with run ID: {dag_run_id}")

if __name__ == "__main__":
    main()
