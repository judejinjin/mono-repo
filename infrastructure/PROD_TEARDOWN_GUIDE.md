# AWS Production Infrastructure Teardown Guide

This guide walks you through safely tearing down the Production VPC infrastructure.

## 🚨 **CRITICAL: Production Infrastructure Teardown**

### ⚠️ **EXTREME CAUTION REQUIRED**
Tearing down Production infrastructure will **PERMANENTLY AND IRREVERSIBLY DELETE**:
- **ALL PRODUCTION DATA** in databases, file systems, and applications
- **ALL CUSTOMER DATA** and business-critical information
- **ALL PRODUCTION APPLICATIONS** and services
- **ALL PRODUCTION CONFIGURATIONS** and customizations
- **YEARS OF OPERATIONAL DATA** and logs
- **THIS ACTION WILL CAUSE COMPLETE SERVICE OUTAGE**

## 🛑 **Production Teardown Prerequisites**

### **MANDATORY APPROVALS REQUIRED**
Before proceeding, you **MUST** have:
- [ ] **C-Level Executive Approval** (CEO, CTO, etc.)
- [ ] **Change Control Board Approval**
- [ ] **Security Team Sign-off**
- [ ] **Operations Team Confirmation**
- [ ] **Business Stakeholder Approval**
- [ ] **Legal/Compliance Team Approval** (if applicable)
- [ ] **Disaster Recovery Plan** activated if needed

### **MANDATORY DATA BACKUP VERIFICATION**
- [ ] **Complete Database Backup** verified and tested
- [ ] **Application Data Export** completed and validated
- [ ] **Configuration Backup** stored securely
- [ ] **Customer Data Export** completed (if required)
- [ ] **Compliance Data Retention** requirements met
- [ ] **Backup Restoration Test** successfully completed

### **MANDATORY COMMUNICATION PLAN**
- [ ] **Customer Notification** sent (maintenance window/migration)
- [ ] **Internal Teams Notified** (all stakeholders)
- [ ] **Support Team Prepared** for customer inquiries
- [ ] **Status Page Updated** with maintenance information
- [ ] **Escalation Procedures** activated

## 🗑️ Production Infrastructure Teardown Process

### **Phase 1: Service Degradation and Traffic Diversion** 🔄

#### **Step 1: Divert Production Traffic**
```bash
# Update DNS to point to disaster recovery site or maintenance page
aws route53 change-resource-record-sets --hosted-zone-id Z1PA6795UKMFR9 --change-batch '{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "api.yourcompany.com",
      "Type": "CNAME",
      "TTL": 60,
      "ResourceRecords": [{"Value": "maintenance.yourcompany.com"}]
    }
  }]
}'

# Scale down production applications gradually
kubectl --context=mono-repo-prod-eks-prod scale deployment --replicas=1 --all -n production
kubectl --context=mono-repo-prod-eks-prod scale deployment --replicas=0 --all -n production
```

#### **Step 2: Stop Data Ingestion**
```bash
# Stop Airflow DAGs
kubectl --context=mono-repo-prod-eks-prod exec -n airflow deployment/airflow-scheduler -- airflow dags pause --all

# Stop data processing jobs
kubectl --context=mono-repo-prod-eks-prod delete cronjobs --all -n production

# Verify no active connections to database
aws rds describe-db-instances --db-instance-identifier mono-repo-prod-db --query 'DBInstances[0].DBInstanceStatus'
```

#### **Step 3: Final Data Backup**
```bash
# Create final database snapshot
aws rds create-db-snapshot \
    --db-instance-identifier mono-repo-prod-db \
    --db-snapshot-identifier prod-final-snapshot-$(date +%Y%m%d-%H%M%S)

# Create final S3 backup
aws s3 sync s3://mono-repo-prod-data-bucket s3://mono-repo-prod-final-backup-$(date +%Y%m%d) --delete

# Export application configurations
kubectl --context=mono-repo-prod-eks-prod get all --all-namespaces -o yaml > prod-final-k8s-backup.yaml
```

### **Phase 2: Production Infrastructure Destruction** 💥

#### **Step 4: Destroy Production Applications**
```bash
cd infrastructure/terraform

# Destroy application-specific resources first
terraform destroy -target=module.applications -var-file="prod.tfvars" -auto-approve

# Wait for applications to fully terminate
sleep 300
```

#### **Step 5: Destroy Production Data Layer**
```bash
# Destroy databases (IRREVERSIBLE!)
terraform destroy -target=module.rds -target=module.elasticache -var-file="prod.tfvars" -auto-approve

# Verify database destruction
aws rds describe-db-instances --query 'DBInstances[?contains(DBInstanceIdentifier, `prod`)]'
```

#### **Step 6: Destroy Production Computing Resources**
```bash
# Destroy EKS cluster and node groups
terraform destroy -target=module.eks -var-file="prod.tfvars" -auto-approve

# Destroy load balancers
terraform destroy -target=module.alb -target=module.nlb -var-file="prod.tfvars" -auto-approve

# Wait for ELBs to fully terminate
sleep 600
```

#### **Step 7: Destroy Production Networking**
```bash
# Destroy VPC and all networking components
terraform destroy -target=module.vpc -target=module.security_groups -var-file="prod.tfvars" -auto-approve
```

#### **Step 8: Destroy All Remaining Production Infrastructure**
```bash
# Final destruction of all remaining resources
terraform destroy -var-file="prod.tfvars" -auto-approve
```

### **Phase 3: Production Container Registry Cleanup** 📦

#### **Step 9: Production Container Image Cleanup**
```bash
echo "⚠️  DESTROYING ALL PRODUCTION CONTAINER IMAGES"
echo "This will delete all production application versions and deployment history!"
read -p "Type 'DESTROY-PROD-IMAGES' to confirm: " confirm

if [ "$confirm" = "DESTROY-PROD-IMAGES" ]; then
    # Delete all production container images
    for repo in $(aws ecr describe-repositories --query 'repositories[?contains(repositoryName, `mono-repo-prod`)].repositoryName' --output text --region us-east-1); do
        echo "Destroying production repository: $repo"
        
        # List all images for final confirmation
        aws ecr list-images --repository-name $repo --region us-east-1
        
        # Delete all images
        aws ecr batch-delete-image \
            --repository-name $repo \
            --image-ids $(aws ecr list-images --repository-name $repo --query 'imageIds[].imageDigest' --output text --region us-east-1 | tr '\t' '\n' | sed 's/^/imageDigest=/') \
            --region us-east-1 2>/dev/null || echo "No images in $repo"
    done
else
    echo "❌ Production image cleanup cancelled"
    exit 1
fi
```

### **Phase 4: Production Bootstrap Destruction** 🔧

#### **Step 10: Destroy Production Bootstrap Infrastructure**
```bash
cd infrastructure/bootstrap

echo "🚨 FINAL DESTRUCTION: Production Bootstrap Infrastructure"
echo "This will destroy the production Terraform state bucket and all infrastructure history!"
echo "⚠️  After this step, you will lose ALL ability to manage this infrastructure via Terraform!"

read -p "Type 'DESTROY-PROD-BOOTSTRAP' to confirm: " confirm

if [ "$confirm" = "DESTROY-PROD-BOOTSTRAP" ]; then
    # Final backup of Terraform state
    aws s3 sync s3://$(terraform output -raw terraform_state_bucket) ./prod-state-backup-$(date +%Y%m%d-%H%M%S)/
    
    # Destroy bootstrap infrastructure
    terraform destroy -var-file="prod.tfvars" -auto-approve
    
    echo "✅ Production bootstrap infrastructure destroyed"
else
    echo "❌ Production bootstrap destruction cancelled"
    exit 1
fi
```

### **Phase 5: Manual Production Cleanup** 🧹

#### **Step 11: Verify Complete Production Destruction**
```bash
echo "🔍 Verifying complete destruction of production infrastructure..."

# Check for any remaining production VPCs
PROD_VPCS=$(aws ec2 describe-vpcs --filters "Name=tag:Environment,Values=prod" --query 'Vpcs[].VpcId' --output text)
if [ ! -z "$PROD_VPCS" ]; then
    echo "❌ WARNING: Production VPCs still exist: $PROD_VPCS"
fi

# Check for any remaining production EKS clusters
PROD_CLUSTERS=$(aws eks list-clusters --query 'clusters[?contains(@, `prod`)]' --output text)
if [ ! -z "$PROD_CLUSTERS" ]; then
    echo "❌ WARNING: Production EKS clusters still exist: $PROD_CLUSTERS"
fi

# Check for any remaining production RDS instances
PROD_RDS=$(aws rds describe-db-instances --query 'DBInstances[?contains(DBInstanceIdentifier, `prod`)].DBInstanceIdentifier' --output text)
if [ ! -z "$PROD_RDS" ]; then
    echo "❌ WARNING: Production RDS instances still exist: $PROD_RDS"
fi

# Check for any remaining production S3 buckets
PROD_BUCKETS=$(aws s3 ls | grep -i prod)
if [ ! -z "$PROD_BUCKETS" ]; then
    echo "❌ WARNING: Production S3 buckets still exist:"
    echo "$PROD_BUCKETS"
fi

# Final comprehensive check
aws resourcegroups search-resources \
    --resource-query '{"Type":"TAG_FILTERS_1_0","Query":"{\"ResourceTypeFilters\":[\"AWS::AllSupported\"],\"TagFilters\":[{\"Key\":\"Environment\",\"Values\":[\"prod\"]}]}"}'
```

#### **Step 12: Force Delete Remaining Production Resources**
```bash
# ONLY if resources remain after Terraform destroy
echo "🚨 EMERGENCY: Manual cleanup of remaining production resources"

# Force delete production S3 buckets
for bucket in $(aws s3 ls | grep mono-repo-prod | awk '{print $3}'); do
    echo "Force deleting production bucket: $bucket"
    aws s3 rm s3://$bucket --recursive
    aws s3 rb s3://$bucket --force
done

# Force delete production DynamoDB tables
for table in $(aws dynamodb list-tables --query 'TableNames[?contains(@, `prod`)]' --output text); do
    echo "Force deleting production table: $table"
    aws dynamodb delete-table --table-name $table
done

# Force delete production ECR repositories
for repo in $(aws ecr describe-repositories --query 'repositories[?contains(repositoryName, `prod`)].repositoryName' --output text); do
    echo "Force deleting production repository: $repo"
    aws ecr delete-repository --repository-name $repo --force
done
```

## 🔄 **Production Teardown Automation Script**

⚠️ **DO NOT USE WITHOUT PROPER APPROVALS**

```bash
#!/bin/bash
# infrastructure/teardown_production.sh - USE WITH EXTREME CAUTION

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}🚨 PRODUCTION INFRASTRUCTURE TEARDOWN${NC}"
echo -e "${RED}════════════════════════════════════════${NC}"
echo -e "${RED}THIS WILL DESTROY ALL PRODUCTION DATA AND SERVICES${NC}"
echo -e "${RED}THIS ACTION IS IRREVERSIBLE${NC}"
echo -e "${RED}COMPLETE SERVICE OUTAGE WILL OCCUR${NC}"
echo

# Multiple confirmation levels
echo -e "${YELLOW}Confirmation Level 1:${NC}"
read -p "Enter your full name: " user_name
read -p "Enter current date (YYYY-MM-DD): " current_date
read -p "Enter production environment name: " env_name

if [ "$env_name" != "production" ] && [ "$env_name" != "prod" ]; then
    echo "❌ Environment name verification failed"
    exit 1
fi

echo -e "${YELLOW}Confirmation Level 2:${NC}"
echo "By proceeding, $user_name confirms on $current_date that:"
echo "1. All required approvals have been obtained"
echo "2. All data has been backed up and verified"
echo "3. All stakeholders have been notified"
echo "4. This action is intentional and authorized"

read -p "Type 'I UNDERSTAND THE CONSEQUENCES' to continue: " confirm1
if [ "$confirm1" != "I UNDERSTAND THE CONSEQUENCES" ]; then
    echo "❌ Production teardown cancelled"
    exit 0
fi

echo -e "${YELLOW}Confirmation Level 3:${NC}"
read -p "Type 'DESTROY-PRODUCTION-INFRASTRUCTURE' to proceed: " confirm2
if [ "$confirm2" != "DESTROY-PRODUCTION-INFRASTRUCTURE" ]; then
    echo "❌ Production teardown cancelled"
    exit 0
fi

echo -e "${YELLOW}Final Confirmation:${NC}"
echo "This is your LAST CHANCE to cancel before irreversible destruction begins."
read -p "Type 'EXECUTE' to begin production teardown: " final_confirm
if [ "$final_confirm" != "EXECUTE" ]; then
    echo "❌ Production teardown cancelled"
    exit 0
fi

# Log the destruction attempt
echo "$(date): Production teardown initiated by $user_name" >> /var/log/production-teardown.log

echo "🚨 Beginning production infrastructure teardown..."

# Execute teardown phases
echo "Phase 1: Stopping applications..."
kubectl --context=mono-repo-prod-eks-prod scale deployment --replicas=0 --all -n production

echo "Phase 2: Creating final backups..."
aws rds create-db-snapshot --db-instance-identifier mono-repo-prod-db --db-snapshot-identifier prod-emergency-final-$(date +%Y%m%d-%H%M%S)

echo "Phase 3: Destroying infrastructure..."
cd infrastructure/terraform
terraform destroy -var-file="prod.tfvars" -auto-approve

echo "Phase 4: Destroying bootstrap..."
cd ../bootstrap
terraform destroy -var-file="prod.tfvars" -auto-approve

echo "✅ Production teardown completed"
echo "$(date): Production teardown completed by $user_name" >> /var/log/production-teardown.log
```

## 💰 **Production Cost Impact After Teardown**

### **Immediate Cost Savings (Monthly):**
- **EKS Cluster**: +$73/month saved
- **EKS Node Groups**: +$500-2000/month saved
- **RDS Multi-AZ**: +$200-1000/month saved
- **Load Balancers**: +$25-50/month saved
- **ElastiCache**: +$100-500/month saved
- **CloudWatch**: +$50-200/month saved
- **Security Services**: +$100-300/month saved

**Total Monthly Savings**: $1,055-4,145/month

### **Post-Teardown Cost Verification:**
```bash
# Wait 24-48 hours, then verify no charges
aws ce get-cost-and-usage \
    --time-period Start=2025-09-22,End=2025-09-25 \
    --granularity DAILY \
    --metrics BlendedCost \
    --group-by Type=DIMENSION,Key=SERVICE

# Set up billing alerts for any unexpected charges
aws budgets create-budget --account-id YOUR_ACCOUNT_ID --budget '{
  "BudgetName": "Post-Production-Teardown-Alert",
  "BudgetLimit": {"Amount": "10", "Unit": "USD"},
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}'
```

## 🆘 **Production Emergency Procedures**

### **If Teardown Fails Midway:**
1. **STOP IMMEDIATELY** - Do not continue
2. **Assess Current State** - Determine what's running/destroyed
3. **Contact AWS Support** - Open emergency support case
4. **Implement Emergency Recovery** - From backups if needed
5. **Document Everything** - For post-incident analysis

### **If Data Loss Occurs:**
1. **Immediate Escalation** - Notify all stakeholders
2. **Activate DR Plan** - Switch to disaster recovery site
3. **Begin Data Recovery** - From backups/snapshots
4. **Customer Communication** - Transparent status updates
5. **Incident Commander** - Assign single point of accountability

## 📋 **Post-Teardown Checklist**

After production teardown is complete:

- [ ] **Verify Complete Destruction**: All AWS resources deleted
- [ ] **Confirm Cost Reduction**: AWS billing reflects teardown
- [ ] **Update DNS**: Remove all production DNS entries
- [ ] **Revoke Access**: Remove all production access credentials
- [ ] **Update Documentation**: Mark production environment as decommissioned
- [ ] **Asset Tracking**: Update inventory and asset management systems
- [ ] **Compliance Reporting**: Submit required decommission reports
- [ ] **Stakeholder Notification**: Confirm completion to all parties
- [ ] **Lessons Learned**: Document process improvements
- [ ] **Archive Backups**: Store final backups per retention policy

## 🔄 **Production Environment Recreation**

If you need to recreate production (e.g., for migration):

```bash
# This should be a separate, carefully planned process
# NOT part of the teardown procedure

echo "Production recreation requires:"
echo "1. New deployment planning process"
echo "2. Infrastructure as Code review"
echo "3. Security and compliance validation"
echo "4. Data migration strategy"
echo "5. Rollback plan preparation"
echo "6. Stakeholder approval for new deployment"
```

---

## ⚠️ **FINAL WARNING**

**Production teardown is an IRREVERSIBLE action that will:**
- Destroy all customer data and business operations
- Cause complete service outage
- Potentially violate SLAs and compliance requirements
- Result in significant business impact and costs

**Only proceed if you have:**
- ✅ Complete executive approval
- ✅ Verified data backups
- ✅ Alternative service provision
- ✅ Full understanding of consequences

**Remember: It's much easier to scale down than to destroy and rebuild.**

Consider alternatives like:
- Scaling down resources instead of destroying
- Moving to cheaper instance types
- Implementing auto-scaling policies
- Pausing non-critical services

🚨 **PROCEED ONLY WITH ABSOLUTE CERTAINTY** 🚨
