# AWS Credentials Setup for Personal Account Testing

This document explains how to configure AWS credentials for testing the VPC infrastructure in your personal AWS account.

## Quick Setup

### Option 1: Interactive Setup (Recommended)
Run the setup script to configure your credentials interactively:

```bash
python setup_aws_credentials.py
```

This script will:
- Prompt you for your AWS credentials
- Update the `.env` file with your credentials
- Test the configuration
- Verify AWS access (optional)

### Option 2: Manual Setup
Edit the `.env` file directly and replace the placeholder values:

```bash
# AWS Credentials for Personal Account Testing
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1

# Optional: For temporary credentials
#AWS_SESSION_TOKEN=your_session_token_here

# Optional: For AWS CLI profile
#AWS_PROFILE=your_profile_name
```

## Getting Your AWS Credentials

### From AWS Console:
1. Log into your AWS Console
2. Go to IAM → Users → Your User → Security credentials
3. Create a new Access Key if needed
4. Copy the Access Key ID and Secret Access Key

### From AWS CLI:
If you already have AWS CLI configured, you can view your credentials:

```bash
aws configure list
```

Or check your credentials file:
- Windows: `%USERPROFILE%\.aws\credentials`
- Linux/Mac: `~/.aws/credentials`

## Required AWS Permissions

For VPC infrastructure testing, your AWS user needs these permissions:

### Essential Services:
- **EC2**: Full access for VPC, subnets, security groups, instances
- **IAM**: Read access (for role verification)
- **S3**: Full access (for Terraform state and container images)
- **ECR**: Full access (for container registry)
- **EKS**: Full access (for Kubernetes cluster)

### Recommended Policy:
Attach these AWS managed policies to your user:
- `AmazonEC2FullAccess`
- `AmazonS3FullAccess`
- `AmazonEKSClusterPolicy`
- `AmazonEKSWorkerNodePolicy`
- `AmazonEKS_CNI_Policy`
- `AmazonEC2ContainerRegistryFullAccess`
- `IAMReadOnlyAccess`

## How It Works

### Automatic Loading
When you run build or deployment scripts, AWS credentials are automatically loaded:

```python
# In build.py and deploy.py
from config import setup_aws_environment

# Credentials loaded from .env file automatically
setup_aws_environment()
```

### Available Functions
The config module provides these AWS helper functions:

```python
from config import get_aws_credentials, get_boto3_session, setup_aws_environment

# Get credential dictionary
creds = get_aws_credentials()

# Get boto3 session with loaded credentials
session = get_boto3_session()
ec2 = session.client('ec2')

# Set up environment variables
setup_aws_environment()
```

## Testing Your Setup

### 1. Test Credential Loading
```bash
python -c "from config import get_aws_credentials; print(get_aws_credentials())"
```

### 2. Test AWS Access
```bash
python -c "from config import get_boto3_session; session = get_boto3_session(); print(session.client('s3').list_buckets())"
```

### 3. Run Build/Deploy Scripts
```bash
python build/build.py --help
python deploy/deploy.py --help
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | `wJalrXU...` |
| `AWS_REGION` | Primary AWS region | `us-east-1` |
| `AWS_DEFAULT_REGION` | Default region for AWS CLI | `us-east-1` |
| `AWS_SESSION_TOKEN` | For temporary credentials | Optional |
| `AWS_PROFILE` | AWS CLI profile name | Optional |

## Terraform Variables

The `.env` file also includes Terraform-specific variables:

```bash
# Terraform AWS Variables
TF_VAR_aws_region=us-east-1
TF_VAR_environment=dev
TF_VAR_project_name=mono-repo
TF_VAR_vpc_cidr=10.0.0.0/16
```

These are automatically used by Terraform when running infrastructure commands.

## Security Best Practices

### 1. Keep Credentials Secure
- Never commit `.env` file to version control
- Use temporary credentials when possible
- Rotate access keys regularly

### 2. Principle of Least Privilege
- Only grant permissions needed for testing
- Consider using temporary IAM roles
- Remove unused access keys

### 3. Monitor Usage
- Check AWS CloudTrail for API calls
- Set up billing alerts
- Use AWS Cost Explorer to monitor costs

## Troubleshooting

### Common Issues:

#### "Could not locate credentials"
- Check `.env` file exists and has correct values
- Verify credentials are not commented out
- Run `python setup_aws_credentials.py` to reconfigure

#### "Access Denied" errors
- Check IAM permissions for your user
- Verify credentials are valid (not expired)
- Check if MFA is required

#### "Region not found"
- Verify `AWS_REGION` is set correctly
- Use valid AWS region codes (e.g., `us-east-1`, `eu-west-1`)

#### Dependencies missing
```bash
# For development environment (includes all tools)
pip install -r build/requirements/dev.txt

# For UAT environment
pip install -r build/requirements/uat.txt

# For production environment
pip install -r build/requirements/prod.txt
```

### Debug Mode
Add debug logging to see credential loading:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from config import setup_aws_environment
setup_aws_environment()  # Will show debug info
```

## Next Steps

Once your credentials are configured:

1. **Test VPC Infrastructure**: Run Terraform commands to create VPC
2. **Build Container Images**: Use build.py to create ECR images  
3. **Deploy Applications**: Use deploy.py to deploy to EKS
4. **Monitor Resources**: Check AWS Console for created resources

For more information, see the main project documentation in the `docs/` directory.
