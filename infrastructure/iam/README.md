# IAM Infrastructure Management

This directory contains Terraform configurations for managing AWS IAM resources including roles, users, groups, and policies.

## 🔧 **Terraform IAM Capabilities**

Terraform can fully automate IAM management:

### ✅ **IAM Resources Supported:**
- **Roles** (`aws_iam_role`) - Service roles, cross-account roles, assume roles
- **Users** (`aws_iam_user`) - Individual user accounts with programmatic/console access
- **Groups** (`aws_iam_group`) - User collections for permission management
- **Policies** (`aws_iam_policy`) - Custom JSON permission policies
- **Policy Attachments** (`aws_iam_role_policy_attachment`) - Link policies to roles/users/groups
- **Instance Profiles** (`aws_iam_instance_profile`) - EC2 instance role binding
- **Access Keys** (`aws_iam_access_key`) - Programmatic access credentials
- **Login Profiles** (`aws_iam_user_login_profile`) - Console access passwords

### ✅ **Advanced Features:**
- **Policy Documents** with `data.aws_iam_policy_document`
- **Assume Role Policies** for service-to-service authentication
- **Cross-Account Access** with external ID validation
- **Conditional Access** based on IP, MFA, time, etc.
- **Permission Boundaries** for maximum privilege limits
- **Tags and Metadata** for resource organization

## 📁 **Directory Structure**

```
infrastructure/iam/
├── main.tf                    # Main IAM configuration
├── variables.tf               # Input variables
├── outputs.tf                 # Output values
├── roles/
│   ├── service-roles.tf       # EKS, Lambda, EC2 service roles
│   ├── application-roles.tf   # Application-specific roles
│   └── cross-account-roles.tf # Cross-account access roles
├── users/
│   ├── developers.tf          # Developer user accounts
│   ├── service-accounts.tf    # Service/system accounts
│   └── admin-users.tf         # Administrative users
├── groups/
│   ├── developer-groups.tf    # Development teams
│   ├── ops-groups.tf          # Operations teams
│   └── business-groups.tf     # Business user groups
├── policies/
│   ├── custom-policies.tf     # Custom permission policies
│   ├── boundary-policies.tf   # Permission boundary policies
│   └── policy-attachments.tf  # Policy-to-resource bindings
└── README.md                  # This documentation
```

## 🚀 **Usage**

### **Deploy IAM Infrastructure:**
```bash
cd infrastructure/iam
terraform init
terraform plan -var-file="../terraform/dev.tfvars"
terraform apply
```

### **Environment-Specific Deployment:**
```bash
# Development
terraform apply -var-file="../terraform/dev.tfvars"

# UAT
terraform apply -var-file="../terraform/uat.tfvars"

# Production
terraform apply -var-file="../terraform/prod.tfvars"
```

## 🔒 **Security Best Practices**

### **Implemented Security Controls:**
1. **Least Privilege Principle** - Minimal required permissions
2. **Permission Boundaries** - Maximum privilege limits
3. **Conditional Access** - IP, MFA, time-based restrictions
4. **Regular Access Reviews** - Automated policy validation
5. **Cross-Account Security** - External ID requirements
6. **Service Role Separation** - Dedicated roles per service
7. **Temporary Credentials** - AssumeRole for short-lived access

### **Policy Management:**
- **Custom Policies** for specific application needs
- **Managed Policies** for common permission sets
- **Inline Policies** for one-off requirements
- **Policy Versioning** with Terraform state management

## 🔧 **Integration Points**

### **With Main Infrastructure:**
- **EKS Cluster Roles** - Worker node and service account roles
- **RDS Access** - Database connection roles
- **S3 Permissions** - Bucket access policies
- **Secrets Manager** - Secret retrieval permissions
- **CloudWatch** - Logging and monitoring access

### **With CI/CD Pipeline:**
- **Bamboo Service Roles** - Deployment permissions
- **Docker Registry Access** - ECR push/pull permissions
- **Kubernetes Deployment** - EKS cluster access
- **Infrastructure Updates** - Terraform execution roles

## 📊 **Monitoring and Compliance**

### **CloudTrail Integration:**
- All IAM changes logged and auditable
- API call tracking for security analysis
- Compliance reporting capabilities

### **Access Analytics:**
- Last accessed information for permission optimization
- Unused permission identification
- Access pattern analysis for security insights

## 🎯 **Benefits**

1. **Infrastructure as Code** - Version-controlled IAM management
2. **Consistent Deployments** - Identical permissions across environments
3. **Automated Compliance** - Policy enforcement through code
4. **Drift Detection** - Terraform detects manual changes
5. **Collaborative Management** - Team-based IAM administration
6. **Disaster Recovery** - Rapid IAM reconstruction from code
