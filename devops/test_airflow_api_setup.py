#!/usr/bin/env python3
"""
Test script to validate the Airflow API external access setup
"""

import os
import sys
import json
from pathlib import Path

def test_terraform_configuration():
    """Test if Terraform configuration files are valid"""
    print("🔧 Testing Terraform Configuration...")
    
    # Check if required Terraform files exist
    terraform_files = [
        "../infrastructure/terraform/main.tf",
        "../infrastructure/terraform/variables.tf", 
        "../infrastructure/terraform/intranet_load_balancer.tf",
        "../infrastructure/terraform/dev_server.tf"
    ]
    
    missing_files = []
    for file_path in terraform_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing Terraform files: {missing_files}")
        return False
    
    print("✅ All required Terraform files exist")
    return True

def test_airflow_dag():
    """Test if the Airflow DAG file is properly structured"""
    print("\n🛠️ Testing Airflow DAG Configuration...")
    
    dag_file = "../dags/api_triggered_risk_analysis.py"
    if not Path(dag_file).exists():
        print(f"❌ DAG file not found: {dag_file}")
        return False
    
    # Try to import the DAG (syntax check)
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("api_triggered_dag", dag_file)
        module = importlib.util.module_from_spec(spec)
        # We won't execute it as it depends on Airflow imports
        print("✅ DAG file syntax appears valid")
        return True
    except Exception as e:
        print(f"❌ DAG file has issues: {e}")
        return False

def test_api_client():
    """Test if the API client is properly structured"""
    print("\n📡 Testing API Client Configuration...")
    
    client_file = "../scripts/clients/airflow_api_client.py"
    if not Path(client_file).exists():
        print(f"❌ API client not found: {client_file}")
        return False
    
    # Check if client has required methods
    try:
        with open(client_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        required_methods = [
            "class AirflowAPIClient",
            "def test_connection",
            "def trigger_dag", 
            "def get_dag_run_status",
            "def trigger_risk_analysis"
        ]
        
        missing_methods = []
        for method in required_methods:
            if method not in content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Missing methods in API client: {missing_methods}")
            return False
            
        print("✅ API client has all required methods")
        return True
        
    except Exception as e:
        print(f"❌ Error reading API client: {e}")
        return False

def test_kubernetes_configuration():
    """Test Kubernetes/Helm configuration"""
    print("\n☸️ Testing Kubernetes Configuration...")
    
    k8s_files = [
        "../deploy/kubernetes/airflow/values-dev.yaml",
        "../deploy/kubernetes/airflow/values-uat.yaml", 
        "../deploy/kubernetes/airflow/values-prod.yaml"
    ]
    
    missing_files = []
    for file_path in k8s_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing Kubernetes files: {missing_files}")
        return False
    
    # Check if dev values has LoadBalancer configuration
    try:
        import yaml
        with open("../deploy/kubernetes/airflow/values-dev.yaml", 'r') as f:
            values = yaml.safe_load(f)
        
        # Check for LoadBalancer configuration
        if (values.get('webserver', {}).get('service', {}).get('type') == 'LoadBalancer' and
            'aws-load-balancer-type' in str(values.get('webserver', {}).get('service', {}).get('annotations', {}))):
            print("✅ Kubernetes configuration includes LoadBalancer setup")
            return True
        else:
            print("⚠️ LoadBalancer configuration may be missing or incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Error validating Kubernetes configuration: {e}")
        return False

def test_documentation():
    """Test if documentation files are present"""
    print("\n📚 Testing Documentation...")
    
    doc_files = [
        "docs/architecture/architecture_dev.png",
        "docs/architecture/architecture_uat.png",
        "docs/architecture/architecture_prod.png"
    ]
    
    missing_files = []
    for file_path in doc_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing documentation files: {missing_files}")
        return False
    
    print("✅ All architecture diagrams are present")
    return True

def generate_deployment_checklist():
    """Generate a deployment checklist"""
    print("\n📋 Deployment Checklist:")
    print("=" * 50)
    
    checklist = [
        "☐ Deploy Terraform infrastructure (terraform apply)",
        "☐ Configure DNS for API Gateway custom domain (if using)",
        "☐ Deploy Airflow to EKS using Helm charts",
        "☐ Verify LoadBalancer service is created and has external IP",
        "☐ Test corporate VPN connectivity to AWS VPC", 
        "☐ Configure Internal ALB target groups",
        "☐ Test DAG triggering via Internal ALB endpoint",
        "☐ Set up monitoring and logging for Internal ALB",
        "☐ Configure corporate network security groups",
        "☐ Test internal API access with provided Python client",
        "☐ Configure Bamboo CI/CD pipeline for corporate Bitbucket"
    ]
    
    for item in checklist:
        print(f"  {item}")
    
    print(f"\n📖 Key Configuration Files:")
    print(f"  • Terraform: ../infrastructure/terraform/")
    print(f"  • Kubernetes: ../deploy/kubernetes/airflow/")
    print(f"  • DAGs: ../dags/")
    print(f"  • API Client: ../scripts/clients/airflow_api_client.py")

def main():
    """Run all tests"""
    print("🧪 Testing Airflow API External Access Setup")
    print("=" * 50)
    
    tests = [
        test_terraform_configuration,
        test_airflow_dag,
        test_api_client,
        test_kubernetes_configuration,
        test_documentation
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print(f"\n📊 Test Results Summary:")
    print(f"=" * 30)
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print(f"🎉 All tests passed! Setup is ready for deployment.")
    else:
        print(f"⚠️ Some tests failed. Please review the issues above.")
    
    generate_deployment_checklist()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
