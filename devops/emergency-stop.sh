#!/bin/bash

# Emergency Infrastructure Stop Script
# Immediately stops all compute resources to minimize costs
# Use this if you need to quickly stop everything but don't want to fully destroy

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${RED}🚨 Emergency Infrastructure Stop${NC}"
echo -e "${RED}================================${NC}"
echo -e "${YELLOW}This will STOP (not destroy) all compute resources immediately${NC}"

# Function to stop EC2 instances
stop_ec2_instances() {
    echo -e "\n${BLUE}🛑 Stopping EC2 instances...${NC}"
    
    # Get running instances
    instances=$(aws ec2 describe-instances \
        --query 'Reservations[].Instances[?State.Name==`running`].InstanceId' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$instances" ]; then
        echo -e "${YELLOW}Found running instances: $instances${NC}"
        aws ec2 stop-instances --instance-ids $instances
        echo -e "${GREEN}✅ EC2 instances stop initiated${NC}"
    else
        echo -e "${GREEN}✅ No running EC2 instances${NC}"
    fi
}

# Function to scale down EKS node groups
scale_down_eks() {
    echo -e "\n${BLUE}📉 Scaling down EKS node groups...${NC}"
    
    # Get EKS clusters
    clusters=$(aws eks list-clusters --query 'clusters[]' --output text 2>/dev/null || echo "")
    
    if [ -n "$clusters" ]; then
        for cluster in $clusters; do
            echo -e "${YELLOW}Processing cluster: $cluster${NC}"
            
            # Get node groups
            nodegroups=$(aws eks list-nodegroups --cluster-name "$cluster" \
                --query 'nodegroups[]' --output text 2>/dev/null || echo "")
            
            for nodegroup in $nodegroups; do
                echo -e "${YELLOW}Scaling down node group: $nodegroup${NC}"
                aws eks update-nodegroup-config \
                    --cluster-name "$cluster" \
                    --nodegroup-name "$nodegroup" \
                    --scaling-config minSize=0,maxSize=0,desiredSize=0 \
                    2>/dev/null || echo "Failed to scale $nodegroup"
            done
        done
        echo -e "${GREEN}✅ EKS node groups scale-down initiated${NC}"
    else
        echo -e "${GREEN}✅ No EKS clusters found${NC}"
    fi
}

# Function to scale down RDS instances
stop_rds_instances() {
    echo -e "\n${BLUE}💾 Stopping RDS instances...${NC}"
    
    # Get RDS instances
    instances=$(aws rds describe-db-instances \
        --query 'DBInstances[?DBInstanceStatus==`available`].DBInstanceIdentifier' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$instances" ]; then
        for instance in $instances; do
            echo -e "${YELLOW}Stopping RDS instance: $instance${NC}"
            aws rds stop-db-instance --db-instance-identifier "$instance" \
                2>/dev/null || echo "Failed to stop $instance"
        done
        echo -e "${GREEN}✅ RDS instances stop initiated${NC}"
    else
        echo -e "${GREEN}✅ No running RDS instances${NC}"
    fi
}

# Function to delete load balancers (they cost money even when idle)
delete_load_balancers() {
    echo -e "\n${BLUE}⚖️  Deleting load balancers...${NC}"
    
    # Delete Application Load Balancers
    albs=$(aws elbv2 describe-load-balancers \
        --query 'LoadBalancers[].LoadBalancerArn' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$albs" ]; then
        for alb in $albs; do
            echo -e "${YELLOW}Deleting ALB: $alb${NC}"
            aws elbv2 delete-load-balancer --load-balancer-arn "$alb" \
                2>/dev/null || echo "Failed to delete $alb"
        done
        echo -e "${GREEN}✅ Application Load Balancers deletion initiated${NC}"
    else
        echo -e "${GREEN}✅ No Application Load Balancers found${NC}"
    fi
    
    # Delete Classic Load Balancers
    clbs=$(aws elb describe-load-balancers \
        --query 'LoadBalancerDescriptions[].LoadBalancerName' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$clbs" ]; then
        for clb in $clbs; do
            echo -e "${YELLOW}Deleting CLB: $clb${NC}"
            aws elb delete-load-balancer --load-balancer-name "$clb" \
                2>/dev/null || echo "Failed to delete $clb"
        done
        echo -e "${GREEN}✅ Classic Load Balancers deletion initiated${NC}"
    else
        echo -e "${GREEN}✅ No Classic Load Balancers found${NC}"
    fi
}

# Function to delete NAT gateways (expensive!)
delete_nat_gateways() {
    echo -e "\n${BLUE}🌐 Deleting NAT gateways...${NC}"
    
    nat_gateways=$(aws ec2 describe-nat-gateways \
        --filter Name=state,Values=available \
        --query 'NatGateways[].NatGatewayId' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$nat_gateways" ]; then
        for nat in $nat_gateways; do
            echo -e "${YELLOW}Deleting NAT Gateway: $nat${NC}"
            aws ec2 delete-nat-gateway --nat-gateway-id "$nat" \
                2>/dev/null || echo "Failed to delete $nat"
        done
        echo -e "${GREEN}✅ NAT Gateways deletion initiated${NC}"
    else
        echo -e "${GREEN}✅ No NAT Gateways found${NC}"
    fi
}

# Function to show current costs
show_current_costs() {
    echo -e "\n${BLUE}💰 Current Resource Status${NC}"
    echo -e "${BLUE}===========================${NC}"
    
    # Count resources
    ec2_count=$(aws ec2 describe-instances \
        --query 'length(Reservations[].Instances[?State.Name!=`terminated`])' \
        --output text 2>/dev/null || echo "0")
    
    rds_count=$(aws rds describe-db-instances \
        --query 'length(DBInstances[?DBInstanceStatus!=`deleting`])' \
        --output text 2>/dev/null || echo "0")
    
    eks_count=$(aws eks list-clusters \
        --query 'length(clusters[])' \
        --output text 2>/dev/null || echo "0")
    
    alb_count=$(aws elbv2 describe-load-balancers \
        --query 'length(LoadBalancers[])' \
        --output text 2>/dev/null || echo "0")
    
    nat_count=$(aws ec2 describe-nat-gateways \
        --filter Name=state,Values=available \
        --query 'length(NatGateways[])' \
        --output text 2>/dev/null || echo "0")
    
    echo "EC2 Instances: $ec2_count"
    echo "RDS Instances: $rds_count"
    echo "EKS Clusters: $eks_count"
    echo "Load Balancers: $alb_count"
    echo "NAT Gateways: $nat_count"
}

# Main execution
main() {
    # Check AWS CLI
    if ! command -v aws >/dev/null 2>&1; then
        echo -e "${RED}❌ AWS CLI not found${NC}"
        exit 1
    fi
    
    # Show current status
    show_current_costs
    
    # Confirm action
    echo -e "\n${YELLOW}⚠️  This will immediately stop/delete compute resources${NC}"
    echo -e "${YELLOW}⚠️  Data in databases and S3 will be preserved${NC}"
    read -p "Continue? (y/N): " confirm
    
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo -e "${GREEN}Emergency stop cancelled${NC}"
        exit 0
    fi
    
    # Execute emergency stops
    stop_ec2_instances
    scale_down_eks
    stop_rds_instances
    delete_load_balancers
    delete_nat_gateways
    
    echo -e "\n${GREEN}🎉 Emergency stop completed!${NC}"
    echo -e "${GREEN}Most compute costs should now be stopped.${NC}"
    echo -e "\n${YELLOW}📋 What was preserved:${NC}"
    echo -e "${YELLOW}  - S3 buckets and data${NC}"
    echo -e "${YELLOW}  - RDS databases (stopped, not deleted)${NC}"
    echo -e "${YELLOW}  - EBS volumes${NC}"
    echo -e "${YELLOW}  - VPC and networking (except NAT gateways)${NC}"
    echo -e "\n${BLUE}💡 To fully clean up, run: scripts/teardown-infrastructure.sh${NC}"
}

# Run main function
main "$@"
