#!/usr/bin/env python3
"""
AWS Cost Monitoring Script
Tracks AWS spending and identifies cost drivers for the mono-repo infrastructure.
"""

import boto3
import json
from datetime import datetime, timedelta
from decimal import Decimal
import argparse

class CostMonitor:
    def __init__(self, region='us-east-1'):
        """Initialize the cost monitor with AWS Cost Explorer client."""
        try:
            self.cost_explorer = boto3.client('ce', region_name=region)
            self.ec2 = boto3.client('ec2', region_name=region)
            self.rds = boto3.client('rds', region_name=region)
            self.eks = boto3.client('eks', region_name=region)
        except Exception as e:
            print(f"❌ Failed to initialize AWS clients: {e}")
            print("💡 Make sure AWS credentials are configured")
            exit(1)
    
    def get_cost_data(self, days_back=30):
        """Get cost data for the specified number of days."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        try:
            response = self.cost_explorer.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            return response
        except Exception as e:
            print(f"❌ Failed to get cost data: {e}")
            return None
    
    def get_current_month_costs(self):
        """Get current month costs by service."""
        now = datetime.now()
        start_of_month = now.replace(day=1).date()
        end_date = now.date()
        
        try:
            response = self.cost_explorer.get_cost_and_usage(
                TimePeriod={
                    'Start': start_of_month.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            return response
        except Exception as e:
            print(f"❌ Failed to get current month costs: {e}")
            return None
    
    def get_resource_inventory(self):
        """Get inventory of current resources."""
        inventory = {
            'ec2_instances': [],
            'rds_instances': [],
            'eks_clusters': [],
            'summary': {}
        }
        
        try:
            # EC2 instances
            ec2_response = self.ec2.describe_instances()
            for reservation in ec2_response['Reservations']:
                for instance in reservation['Instances']:
                    if instance['State']['Name'] != 'terminated':
                        inventory['ec2_instances'].append({
                            'id': instance['InstanceId'],
                            'type': instance['InstanceType'],
                            'state': instance['State']['Name'],
                            'launch_time': instance.get('LaunchTime', 'Unknown')
                        })
            
            # RDS instances
            rds_response = self.rds.describe_db_instances()
            for db in rds_response['DBInstances']:
                if db['DBInstanceStatus'] != 'deleting':
                    inventory['rds_instances'].append({
                        'id': db['DBInstanceIdentifier'],
                        'class': db['DBInstanceClass'],
                        'engine': db['Engine'],
                        'status': db['DBInstanceStatus']
                    })
            
            # EKS clusters
            eks_response = self.eks.list_clusters()
            for cluster_name in eks_response['clusters']:
                cluster_info = self.eks.describe_cluster(name=cluster_name)
                inventory['eks_clusters'].append({
                    'name': cluster_name,
                    'status': cluster_info['cluster']['status'],
                    'version': cluster_info['cluster']['version'],
                    'created': cluster_info['cluster'].get('createdAt', 'Unknown')
                })
            
            # Summary
            inventory['summary'] = {
                'ec2_count': len(inventory['ec2_instances']),
                'rds_count': len(inventory['rds_instances']),
                'eks_count': len(inventory['eks_clusters'])
            }
            
        except Exception as e:
            print(f"⚠️  Error getting resource inventory: {e}")
        
        return inventory
    
    def analyze_costs(self, cost_data):
        """Analyze and categorize costs."""
        if not cost_data:
            return None
        
        service_costs = {}
        total_cost = Decimal('0')
        
        for result in cost_data['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                cost = Decimal(group['Metrics']['BlendedCost']['Amount'])
                
                if service not in service_costs:
                    service_costs[service] = Decimal('0')
                
                service_costs[service] += cost
                total_cost += cost
        
        # Sort by cost descending
        sorted_costs = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_cost': total_cost,
            'service_costs': sorted_costs
        }
    
    def print_cost_report(self, analysis, title="Cost Analysis"):
        """Print formatted cost report."""
        print(f"\n💰 {title}")
        print("=" * (len(title) + 3))
        
        if not analysis:
            print("❌ No cost data available")
            return
        
        total = analysis['total_cost']
        print(f"📊 Total Cost: ${total:.2f}")
        
        if analysis['service_costs']:
            print("\n📋 Cost by Service:")
            for service, cost in analysis['service_costs'][:10]:  # Top 10
                percentage = (cost / total * 100) if total > 0 else 0
                print(f"  {service:<25} ${cost:>8.2f} ({percentage:>5.1f}%)")
        
        # Cost warnings
        if total > 50:
            print(f"\n⚠️  WARNING: Monthly cost is ${total:.2f}")
            print("   Consider running teardown script if testing is complete")
        elif total > 20:
            print(f"\n🔔 NOTICE: Monthly cost is ${total:.2f}")
            print("   Monitor closely to avoid unexpected charges")
        else:
            print(f"\n✅ Cost is within reasonable range: ${total:.2f}")
    
    def print_resource_report(self, inventory):
        """Print resource inventory report."""
        print("\n🏗️  Current Resource Inventory")
        print("=" * 29)
        
        summary = inventory['summary']
        print(f"📊 Summary: {summary['ec2_count']} EC2, {summary['rds_count']} RDS, {summary['eks_count']} EKS")
        
        # EC2 instances
        if inventory['ec2_instances']:
            print("\n💻 EC2 Instances:")
            for instance in inventory['ec2_instances']:
                print(f"  {instance['id']} - {instance['type']} ({instance['state']})")
        
        # RDS instances
        if inventory['rds_instances']:
            print("\n🗄️  RDS Instances:")
            for db in inventory['rds_instances']:
                print(f"  {db['id']} - {db['class']} {db['engine']} ({db['status']})")
        
        # EKS clusters
        if inventory['eks_clusters']:
            print("\n☸️  EKS Clusters:")
            for cluster in inventory['eks_clusters']:
                print(f"  {cluster['name']} - v{cluster['version']} ({cluster['status']})")
        
        if not any([inventory['ec2_instances'], inventory['rds_instances'], inventory['eks_clusters']]):
            print("✅ No major compute resources found")
    
    def get_cost_recommendations(self, inventory, analysis):
        """Provide cost optimization recommendations."""
        recommendations = []
        
        if not analysis:
            return recommendations
        
        total_cost = analysis['total_cost']
        
        # High cost warning
        if total_cost > 100:
            recommendations.append("🚨 HIGH COST ALERT: Consider immediate teardown")
        
        # Instance-specific recommendations
        if inventory['ec2_instances']:
            running_instances = [i for i in inventory['ec2_instances'] if i['state'] == 'running']
            if running_instances:
                recommendations.append(f"💻 {len(running_instances)} EC2 instances running - consider stopping if not needed")
        
        if inventory['rds_instances']:
            available_dbs = [i for i in inventory['rds_instances'] if i['status'] == 'available']
            if available_dbs:
                recommendations.append(f"🗄️  {len(available_dbs)} RDS instances available - consider stopping if not needed")
        
        if inventory['eks_clusters']:
            recommendations.append(f"☸️  {len(inventory['eks_clusters'])} EKS clusters - each costs ~$72/month just for control plane")
        
        # Service-specific recommendations
        for service, cost in analysis['service_costs']:
            if cost > 20:
                if service == 'Amazon Elastic Compute Cloud - Compute':
                    recommendations.append(f"💰 High EC2 costs (${cost:.2f}) - consider smaller instances")
                elif service == 'Amazon Relational Database Service':
                    recommendations.append(f"💰 High RDS costs (${cost:.2f}) - consider stopping when not testing")
                elif service == 'Amazon Elastic Kubernetes Service':
                    recommendations.append(f"💰 High EKS costs (${cost:.2f}) - each cluster costs $72/month")
        
        return recommendations
    
    def print_recommendations(self, recommendations):
        """Print cost optimization recommendations."""
        if not recommendations:
            print("\n✅ No specific cost optimization recommendations")
            return
        
        print("\n💡 Cost Optimization Recommendations")
        print("=" * 37)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        print("\n🔧 Available Actions:")
        print("   • Emergency stop: scripts/emergency-stop.sh")
        print("   • Full teardown: scripts/teardown-infrastructure.sh")
        print("   • Monitor costs: python scripts/cost_monitor.py")

def main():
    parser = argparse.ArgumentParser(description='Monitor AWS costs for mono-repo infrastructure')
    parser.add_argument('--days', type=int, default=30, help='Number of days to analyze')
    parser.add_argument('--current-month', action='store_true', help='Show current month costs only')
    parser.add_argument('--inventory-only', action='store_true', help='Show resource inventory only')
    
    args = parser.parse_args()
    
    print("🔍 AWS Cost Monitor for Mono-Repo Infrastructure")
    print("=" * 49)
    
    monitor = CostMonitor()
    
    # Get resource inventory
    inventory = monitor.get_resource_inventory()
    
    if args.inventory_only:
        monitor.print_resource_report(inventory)
        return
    
    # Get cost data
    if args.current_month:
        cost_data = monitor.get_current_month_costs()
        title = "Current Month Costs"
    else:
        cost_data = monitor.get_cost_data(args.days)
        title = f"Last {args.days} Days Costs"
    
    # Analyze costs
    analysis = monitor.analyze_costs(cost_data)
    
    # Print reports
    monitor.print_cost_report(analysis, title)
    monitor.print_resource_report(inventory)
    
    # Get and print recommendations
    recommendations = monitor.get_cost_recommendations(inventory, analysis)
    monitor.print_recommendations(recommendations)
    
    print("\n📊 Run this script regularly to monitor costs!")
    print("🔗 AWS Billing Dashboard: https://console.aws.amazon.com/billing/home")

if __name__ == '__main__':
    main()
