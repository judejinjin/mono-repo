#!/usr/bin/env python3
"""
Generate comprehensive architecture diagrams for JupyterHub integration
Creates visual documentation showing JupyterHub integration with the Risk Platform
"""

import os
import sys
from pathlib import Path
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EKS, ECR
from diagrams.aws.storage import EFS, S3
from diagrams.aws.database import RDS
from diagrams.aws.security import IAM, SecretsManager
from diagrams.aws.network import ELB, VPC
from diagrams.aws.management import Cloudwatch, CloudwatchLogs
from diagrams.k8s.compute import Pod, Deployment, Job
from diagrams.k8s.network import Service, Ingress
from diagrams.k8s.storage import PV, PVC, StorageClass
from diagrams.k8s.rbac import ServiceAccount
from diagrams.onprem.client import Users, User
from diagrams.onprem.compute import Server
from diagrams.onprem.analytics import Superset
from diagrams.programming.framework import Fastapi
from diagrams.programming.language import Python
from diagrams.generic.compute import Rack

def create_jupyterhub_architecture_diagram():
    """Create comprehensive JupyterHub architecture diagram"""
    
    with Diagram("JupyterHub Integration with Risk Platform", show=False, 
                 filename="jupyterhub_architecture", direction="TB"):
        
        # Users
        with Cluster("Business Users"):
            business_users = Users("Business Users\n(Risk Analysts)")
            data_scientists = User("Data Scientists\n(Model Developers)")
            admins = User("Platform Admins")
        
        # Authentication
        with Cluster("Authentication & Authorization"):
            corporate_auth = Server("Corporate OAuth\n(SSO)")
            iam_roles = IAM("IAM Roles\n(Business/DS/Admin)")
        
        # JupyterHub Infrastructure
        with Cluster("JupyterHub Platform"):
            with Cluster("Kubernetes Cluster (EKS)"):
                with Cluster("JupyterHub Namespace"):
                    # JupyterHub Hub
                    hub_deployment = Deployment("JupyterHub Hub")
                    hub_service = Service("Hub Service")
                    
                    # Management API
                    mgmt_deployment = Deployment("Management API")
                    mgmt_service = Service("Management Service")
                    
                    # User Notebooks
                    user_pods = [
                        Pod("Business User\nNotebook"),
                        Pod("Data Scientist\nNotebook"), 
                        Pod("Shared Notebook")
                    ]
                    
                    # Service Account & RBAC
                    service_account = ServiceAccount("JupyterHub SA")
            
            # Load Balancer
            ingress = Ingress("ALB Ingress")
            
        # Storage
        with Cluster("Persistent Storage"):
            efs = EFS("EFS\n(Shared Storage)")
            pvc = PVC("Persistent Volume\nClaims")
            s3_backup = S3("S3 Backup\n(User Data)")
        
        # Container Registry
        with Cluster("Container Images"):
            ecr_management = ECR("ECR Management\nService Images")
            ecr_notebooks = ECR("ECR Notebook\nEnvironment Images")
        
        # Risk Platform Integration
        with Cluster("Risk Platform Services"):
            fastapi_service = Fastapi("Risk API\n(FastAPI)")
            risk_db = RDS("Risk Database\n(PostgreSQL)")
            dash_app = Python("Analytics Dashboard\n(Dash)")
        
        # Monitoring & Operations
        with Cluster("Monitoring & Operations"):
            cloudwatch = Cloudwatch("CloudWatch\nMetrics")
            logs = CloudwatchLogs("CloudWatch\nLogs")
            secrets = SecretsManager("Secrets Manager")
        
        # DevOps Automation
        with Cluster("DevOps Automation"):
            monitoring_job = Job("Monitoring\nScript")
            cleanup_job = Job("Cleanup\nScript")
            backup_job = Job("Backup\nScript")
        
        # Connections - User Access
        business_users >> Edge(label="SSO Login") >> corporate_auth
        data_scientists >> Edge(label="SSO Login") >> corporate_auth
        admins >> Edge(label="Admin Access") >> corporate_auth
        
        corporate_auth >> Edge(label="Validate") >> iam_roles
        iam_roles >> Edge(label="Authorized Access") >> ingress
        
        # JupyterHub Flow
        ingress >> hub_service >> hub_deployment
        hub_deployment >> Edge(label="Spawn") >> user_pods[0]  # Connect to first pod as representative
        hub_deployment >> Edge(label="API Calls") >> mgmt_service >> mgmt_deployment
        
        # Storage Connections
        user_pods[0] >> Edge(label="Mount") >> pvc  # Connect first pod as representative
        pvc >> Edge(label="EFS Mount") >> efs
        user_pods[0] >> Edge(label="Backup") >> s3_backup  # Connect first pod as representative
        
        # Container Images
        ecr_management >> Edge(label="Pull") >> mgmt_deployment
        ecr_notebooks >> Edge(label="Pull") >> user_pods
        
        # Risk Platform Integration
        user_pods[0] >> Edge(label="API Calls") >> fastapi_service  # Connect first pod as representative
        mgmt_deployment >> Edge(label="Health Checks") >> fastapi_service
        fastapi_service >> Edge(label="Data") >> risk_db
        user_pods[0] >> Edge(label="View Reports") >> dash_app  # Connect first pod as representative
        
        # Security & Configuration
        service_account >> Edge(label="RBAC") >> hub_deployment
        secrets >> Edge(label="Config") >> hub_deployment
        secrets >> Edge(label="Config") >> mgmt_deployment
        
        # Monitoring
        hub_deployment >> cloudwatch
        mgmt_deployment >> cloudwatch
        user_pods[0] >> cloudwatch  # Connect first pod as representative
        hub_deployment >> logs
        mgmt_deployment >> logs
        user_pods[0] >> logs  # Connect first pod as representative
        
        # DevOps Operations
        monitoring_job >> Edge(label="Monitor") >> hub_deployment
        monitoring_job >> Edge(label="Monitor") >> mgmt_deployment
        cleanup_job >> Edge(label="Cleanup") >> user_pods[0]  # Connect to first pod as representative
        backup_job >> Edge(label="Backup") >> efs

def create_jupyterhub_data_flow_diagram():
    """Create JupyterHub data flow diagram"""
    
    with Diagram("JupyterHub Data Flow", show=False, 
                 filename="jupyterhub_data_flow", direction="LR"):
        
        # Data Sources
        with Cluster("Data Sources"):
            market_data = Server("Market Data\nFeeds")
            portfolio_data = Server("Portfolio\nData")
            risk_models = Server("Risk Models")
        
        # Risk Platform
        with Cluster("Risk Platform"):
            risk_api = Fastapi("Risk API")
            risk_db = RDS("Risk Database")
            analytics = Python("Analytics Engine")
        
        # JupyterHub
        with Cluster("JupyterHub Environment"):
            notebook = Rack("User Notebooks")
            shared_storage = EFS("Shared Data")
        
        # Outputs
        with Cluster("Outputs"):
            reports = Server("Risk Reports")
            dashboards = Server("Dashboards")
            models = Server("ML Models")
        
        # Data Flow
        [market_data, portfolio_data, risk_models] >> risk_api
        risk_api >> risk_db
        risk_db >> analytics
        
        analytics >> Edge(label="API") >> notebook
        notebook >> Edge(label="Results") >> shared_storage
        notebook >> Edge(label="Export") >> [reports, dashboards, models]
        
        shared_storage >> Edge(label="Collaboration") >> notebook

def create_jupyterhub_security_diagram():
    """Create JupyterHub security boundaries diagram"""
    
    with Diagram("JupyterHub Security Architecture", show=False, 
                 filename="jupyterhub_security", direction="TB"):
        
        # External Layer
        with Cluster("External Access"):
            users = Users("Corporate Users")
            internet = Server("Internet")
        
        # Security Perimeter
        with Cluster("Security Perimeter"):
            waf = Server("WAF")
            alb = ELB("Application Load Balancer")
        
        # Authentication Layer
        with Cluster("Authentication Layer"):
            oauth = Server("Corporate OAuth")
            iam = IAM("AWS IAM")
        
        # Kubernetes Security
        with Cluster("Kubernetes Security"):
            with Cluster("Network Policies"):
                network_policy = Server("Network Policies")
            
            with Cluster("RBAC"):
                rbac = ServiceAccount("Service Accounts\n& RBAC")
                
            with Cluster("Pod Security"):
                pod_security = Server("Pod Security\nContexts")
        
        # Application Layer
        with Cluster("Application Security"):
            hub_security = Rack("JupyterHub\nAuthentication")
            api_security = Fastapi("API Security\n(JWT Tokens)")
        
        # Data Layer
        with Cluster("Data Security"):
            encryption = Server("Encryption\nat Rest")
            secrets = SecretsManager("Secrets\nManagement")
            vpc = VPC("VPC\nIsolation")
        
        # Security Flow
        users >> waf >> alb
        alb >> oauth >> iam
        iam >> rbac >> hub_security
        hub_security >> api_security
        
        # Security Controls
        [network_policy, pod_security] >> hub_security
        secrets >> [hub_security, api_security]
        vpc >> [encryption, secrets]

def create_jupyterhub_deployment_diagram():
    """Create JupyterHub deployment architecture diagram"""
    
    with Diagram("JupyterHub Multi-Environment Deployment", show=False, 
                 filename="jupyterhub_deployment", direction="TB"):
        
        # Source Code
        with Cluster("Source Code"):
            repo = Server("Git Repository\n(mono-repo)")
        
        # CI/CD Pipeline
        with Cluster("CI/CD Pipeline"):
            build = Server("Build System\n(Docker)")
            ecr = ECR("ECR Registry")
            deploy = Server("Deployment\n(Kubectl)")
        
        # Environments
        with Cluster("Development Environment"):
            dev_eks = EKS("EKS Cluster (Dev)")
            dev_hub = Rack("JupyterHub (Dev)")
            dev_storage = EFS("EFS (Dev)")
        
        with Cluster("UAT Environment"):
            uat_eks = EKS("EKS Cluster (UAT)")
            uat_hub = Rack("JupyterHub (UAT)")
            uat_storage = EFS("EFS (UAT)")
        
        with Cluster("Production Environment"):
            prod_eks = EKS("EKS Cluster (Prod)")
            prod_hub = Rack("JupyterHub (Prod)")
            prod_storage = EFS("EFS (Prod)")
        
        # Deployment Flow
        repo >> build >> ecr
        ecr >> deploy
        
        deploy >> Edge(label="Deploy") >> [dev_hub, uat_hub, prod_hub]
        
        # Environment Connections
        dev_hub >> dev_storage
        uat_hub >> uat_storage
        prod_hub >> prod_storage

def main():
    """Generate all JupyterHub diagrams"""
    
    # Create output directory
    output_dir = Path("jupyterhub_diagrams")
    output_dir.mkdir(exist_ok=True)
    
    # Change to output directory
    os.chdir(output_dir)
    
    print("Generating JupyterHub architecture diagrams...")
    
    try:
        create_jupyterhub_architecture_diagram()
        print("✓ Created JupyterHub architecture diagram")
        
        create_jupyterhub_data_flow_diagram()
        print("✓ Created JupyterHub data flow diagram")
        
        create_jupyterhub_security_diagram()
        print("✓ Created JupyterHub security diagram")
        
        create_jupyterhub_deployment_diagram()
        print("✓ Created JupyterHub deployment diagram")
        
        print(f"\nAll diagrams generated in: {output_dir.absolute()}")
        
    except Exception as e:
        print(f"Error generating diagrams: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()