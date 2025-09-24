# Free Trial Flag Implementation Summary

## Overview

The mono-repo infrastructure now includes a `free_trial` boolean flag that automatically configures AWS resources to be compliant with AWS Free Tier limits. This enables cost-effective deployment for personal AWS accounts and trial environments.

## Implementation Details

### 1. Terraform Variable
- **Location**: `infrastructure/terraform/variables.tf`
- **Variable**: `free_trial` (boolean, default: false)
- **Purpose**: Controls conditional resource sizing throughout the infrastructure

### 2. Conditional Logic
- **Location**: `infrastructure/terraform/main.tf` (locals block)
- **Mechanism**: Uses Terraform conditional expressions to select appropriate resource sizes
- **Pattern**: `var.free_trial ? free_tier_value : production_value`

### 3. Affected Resources

#### EKS Cluster
- **Node Instance Types**: t3.micro (free) vs t3.medium+ (production)
- **Node Capacity**: 1 desired, 2 max (free) vs 2+ desired, 5+ max (production)
- **Disk Size**: 20GB (free) vs 50GB+ (production)
- **Cluster Logging**: Disabled (free) vs Enabled (production)

#### RDS Database
- **Instance Class**: db.t3.micro (free) vs db.t3.small+ (production)
- **Storage**: 20GB allocated, 100GB max (free) vs 100GB allocated, 1000GB max (production)
- **Multi-AZ**: Single AZ (free) vs Multi-AZ (production)
- **Enhanced Monitoring**: Disabled (free) vs Enabled (production)
- **Performance Insights**: Disabled (free) vs Enabled (production)

#### Dev Server
- **Instance Type**: t3.micro (free) vs t3.medium+ (production)
- **Disk Size**: 20GB (free) vs 50GB (production)

#### Monitoring & Logging
- **VPC Flow Logs**: Disabled (free) vs Enabled (production)
- **Detailed Monitoring**: Disabled (free) vs Enabled (production)
- **CloudWatch Costs**: Minimized (free) vs Full monitoring (production)

### 4. Environment Configuration

#### Development Environment (Free Trial)
```hcl
# infrastructure/terraform/dev.tfvars
free_trial = true
```

#### Production Environment
```hcl
# infrastructure/terraform/prod.tfvars
free_trial = false
```

#### UAT Environment
```hcl
# infrastructure/terraform/uat.tfvars
free_trial = false
```

### 5. Free Trial Template
- **Location**: `infrastructure/terraform/free_trial.tfvars.example`
- **Purpose**: Complete example configuration for AWS Free Tier deployment
- **Usage**: Copy to create new free trial environments

## Cost Benefits

### AWS Free Tier Compliance
1. **EC2 Instances**: 750 hours/month of t3.micro instances
2. **RDS Database**: 20GB storage, single AZ deployment
3. **CloudWatch**: Minimal logging to stay within free limits
4. **VPC**: Basic networking without flow logs

### Estimated Monthly Costs
- **Free Trial Mode**: $0-5/month (within AWS Free Tier)
- **Production Mode**: $150-300/month (depending on usage)

## Usage Instructions

### For AWS Free Trial Accounts
1. Set `free_trial = true` in your .tfvars file
2. Deploy infrastructure normally
3. All resources automatically sized for free tier

### For Production Accounts
1. Set `free_trial = false` in your .tfvars file
2. Deploy with full resource sizing
3. Enhanced monitoring and multi-AZ enabled

### Switching Modes
- **Free to Production**: Change flag to `false`, run `terraform plan` and `apply`
- **Production to Free**: Change flag to `true`, **WARNING**: This will downsize resources

## File Modifications

### Created Files
- `infrastructure/terraform/eks.tf` - EKS cluster with free trial optimizations
- `infrastructure/terraform/rds.tf` - RDS database with free trial optimizations
- `infrastructure/terraform/free_trial.tfvars.example` - Complete free trial configuration

### Modified Files
- `infrastructure/terraform/variables.tf` - Added free_trial variable
- `infrastructure/terraform/main.tf` - Added conditional logic in locals
- `infrastructure/terraform/dev_server.tf` - Added conditional instance sizing
- `infrastructure/terraform/vpc.tf` - Added conditional VPC flow logs
- `infrastructure/terraform/dev.tfvars` - Set free_trial = true
- `infrastructure/terraform/prod.tfvars` - Set free_trial = false
- `infrastructure/terraform/uat.tfvars` - Set free_trial = false
- `AWS_trial_steps.md` - Updated with free trial information

## Benefits

1. **Cost Control**: Automatic compliance with AWS Free Tier limits
2. **Flexibility**: Single codebase supports both free trial and production
3. **Safety**: Prevents accidental deployment of expensive resources
4. **Transparency**: Clear documentation of cost optimizations
5. **Scalability**: Easy transition from trial to production

## Monitoring

### Cost Alerts
- Set up AWS Budget alerts for $50/month threshold
- Monitor usage through AWS Cost Explorer
- Track free tier usage in AWS Free Tier dashboard

### Resource Monitoring
- EKS node utilization
- RDS storage usage
- CloudWatch logs volume (if enabled)

## Best Practices

1. **Always set free_trial = true** for personal AWS accounts
2. **Review terraform plan** carefully before applying
3. **Monitor AWS costs** regularly during trial period
4. **Test applications** with free tier resource constraints
5. **Plan transition** to production sizing when ready

## Troubleshooting

### Common Issues
1. **Resource limits**: Free tier has strict limits on instance hours
2. **Performance**: t3.micro instances may be slower for development
3. **Storage**: 20GB database storage may fill up with test data

### Solutions
1. **Monitor usage**: Use AWS Free Tier dashboard
2. **Optimize applications**: Design for resource constraints
3. **Clean up data**: Regularly remove test data
4. **Scale when ready**: Switch free_trial to false for more resources

## Next Steps

1. Test deployment with free_trial = true
2. Validate application performance on free tier resources
3. Monitor costs and usage patterns
4. Plan production deployment strategy
5. Create cost monitoring dashboards