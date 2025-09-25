# Branch-Per-Environment CI/CD Setup Guide

## Overview
This guide provides complete configuration for setting up branch-per-environment deployment using Bamboo CI/CD with Bitbucket Server in a corporate environment.

## Branch Strategy

- **Development Environment** → `develop` branch
- **UAT Environment** → `uat` branch  
- **Production Environment** → `master` branch

## Bamboo Plan Configuration

### 1. Create Three Bamboo Plans

#### Plan 1: Development Deployment
```yaml
Plan Name: mono-repo-dev-deployment
Branch: develop
Trigger: Push to develop branch
Environment: dev
```

#### Plan 2: UAT Deployment
```yaml
Plan Name: mono-repo-uat-deployment
Branch: uat
Trigger: Push to uat branch
Environment: uat
```

#### Plan 3: Production Deployment
```yaml
Plan Name: mono-repo-prod-deployment
Branch: master
Trigger: Manual trigger only (for safety)
Environment: prod
```

### 2. Bamboo Plan Stages

Each plan should have the following stages:

#### Stage 1: Build and Test
```bash
# Job: Build Branch-Specific Images
# Script:
#!/bin/bash
set -e

# Set environment variables
export ENV=${bamboo.planRepository.branch}
export BUILD_BRANCH=${bamboo.planRepository.branch}

# Map branch to environment
case ${BUILD_BRANCH} in
    "develop")
        ENV="dev"
        ;;
    "uat")
        ENV="uat"
        ;;
    "main"|"master")
        ENV="prod"
        ;;
    *)
        echo "Unknown branch: ${BUILD_BRANCH}"
        exit 1
        ;;
esac

echo "Building for environment: ${ENV}, branch: ${BUILD_BRANCH}"

# Activate virtual environment
source /mnt/c/GenAI/mono-repo/venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH=/mnt/c/GenAI/mono-repo/libs

# Run tests
python -m pytest --environment=${ENV}

# Build Docker images
python build/build.py --environment=${ENV} --branch=${BUILD_BRANCH} --docker-service=risk-api
python build/build.py --environment=${ENV} --branch=${BUILD_BRANCH} --docker-service=airflow
python build/build.py --environment=${ENV} --branch=${BUILD_BRANCH} --docker-service=data-pipeline
python build/build.py --environment=${ENV} --branch=${BUILD_BRANCH} --docker-service=base

echo "Build completed successfully"
```

#### Stage 2: Deploy to Environment
```bash
# Job: Deploy to Target Environment
# Script:
#!/bin/bash
set -e

# Set environment variables
export ENV=${bamboo.planRepository.branch}
export BUILD_BRANCH=${bamboo.planRepository.branch}

# Map branch to environment (same as above)
case ${BUILD_BRANCH} in
    "develop")
        ENV="dev"
        ;;
    "uat")
        ENV="uat"
        ;;
    "main"|"master")
        ENV="prod"
        ;;
esac

echo "Deploying to environment: ${ENV}, branch: ${BUILD_BRANCH}"

# Activate virtual environment
source /mnt/c/GenAI/mono-repo/venv/bin/activate
export PYTHONPATH=/mnt/c/GenAI/mono-repo/libs

# Deploy with branch-specific build and deploy
python deploy/deploy.py --target=build-and-deploy --environment=${ENV} --branch=${BUILD_BRANCH}

echo "Deployment completed successfully"
```

### 3. Bamboo Environment Variables

Set these variables in Bamboo Global Variables or Plan Variables:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=${bamboo.AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${bamboo.AWS_SECRET_ACCESS_KEY}
AWS_DEFAULT_REGION=${bamboo.AWS_DEFAULT_REGION}

# JFrog Container Registry
JFROG_DOCKER_CONFIG_JSON=${bamboo.JFROG_DOCKER_CONFIG_JSON}
JFROG_USERNAME=${bamboo.JFROG_USERNAME}
JFROG_PASSWORD=${bamboo.JFROG_PASSWORD}

# Project Configuration
PYTHONPATH=/mnt/c/GenAI/mono-repo/libs
PROJECT_ROOT=/mnt/c/GenAI/mono-repo
```

### 4. Bamboo Repository Configuration

#### For each plan, configure the repository:

```yaml
Repository Type: Bitbucket Server
Repository URL: https://bitbucket.corporate.com/projects/GENAI/repos/mono-repo
Branch: 
  - develop (for dev plan)
  - uat (for uat plan)  
  - master (for prod plan)

Authentication: SSH Key or Username/Password
SSH Key: [Corporate SSH key for Bamboo]
```

### 5. Plan Triggers

#### Development Plan Triggers:
```yaml
Repository Polling:
  - Enable: Yes
  - Repository: mono-repo
  - Branch: develop
  - Polling Frequency: 30 seconds

Webhook Trigger (Optional):
  - Enable: Yes
  - Repository: Bitbucket Server
  - Branch Pattern: develop
```

#### UAT Plan Triggers:
```yaml
Repository Polling:
  - Enable: Yes
  - Repository: mono-repo
  - Branch: uat
  - Polling Frequency: 60 seconds
```

#### Production Plan Triggers:
```yaml
Manual Trigger Only:
  - Repository Polling: Disabled
  - Webhook: Disabled
  - Manual Deployment: Enabled
```

## Bitbucket Configuration

### 1. Branch Permissions

Configure branch permissions in Bitbucket:

```yaml
Branch Permissions:
  - Branch: develop
    - Type: Branch
    - Users: All developers
    - Write access: Yes
    
  - Branch: uat
    - Type: Branch  
    - Users: QA Team, Senior Developers
    - Write access: Yes
    - Requires pull request: Yes
    
  - Branch: master
    - Type: Branch
    - Users: DevOps Team, Tech Leads
    - Write access: Yes
    - Requires pull request: Yes
    - Requires 2 approvals: Yes
```

### 2. Pull Request Configuration

#### UAT Branch Pull Requests:
```yaml
Source: develop
Target: uat
Required Reviewers: 1
Required Build Success: Yes
Auto-merge: No
```

#### Production Branch Pull Requests:
```yaml
Source: uat
Target: master
Required Reviewers: 2 (DevOps + Tech Lead)
Required Build Success: Yes
Required Manual Testing Sign-off: Yes
Auto-merge: No
```

### 3. Webhook Configuration

Configure webhooks to trigger Bamboo builds:

```yaml
Webhook URL: https://bamboo.corporate.com/chain/admin/ajax/triggerManualBuild.action
Events: 
  - Push
  - Pull Request Merged
Branches:
  - develop
  - uat
  - master
```

## Deployment Workflow

### Development Deployment:
1. Developer commits to `develop` branch
2. Bamboo automatically triggers build
3. Docker images built with `develop` branch code
4. Deployed to DEV environment
5. PYTHONPATH set to `/mnt/c/GenAI/mono-repo/libs` in all containers

### UAT Deployment:
1. Create PR from `develop` to `uat`
2. After PR approval and merge
3. Bamboo triggers UAT build automatically
4. Docker images built with `uat` branch code
5. Deployed to UAT environment
6. PYTHONPATH set to `/mnt/c/GenAI/mono-repo/libs` in all containers

### Production Deployment:
1. Create PR from `uat` to `master`
2. Requires 2 approvals + manual testing sign-off
3. After PR merge, manual Bamboo build trigger
4. Docker images built with `master` branch code
5. Deployed to PROD environment
6. PYTHONPATH set to `/mnt/c/GenAI/mono-repo/libs` in all containers

## Example Commands

### Build for specific environment and branch:
```bash
# Development
python build/build.py --environment=dev --branch=develop --docker-service=risk-api

# UAT
python build/build.py --environment=uat --branch=uat --docker-service=airflow

# Production
python build/build.py --environment=prod --branch=master --docker-service=data-pipeline
```

### Deploy with branch-specific build:
```bash
# Development
python deploy/deploy.py --target=build-and-deploy --environment=dev --branch=develop

# UAT
python deploy/deploy.py --target=build-and-deploy --environment=uat --branch=uat

# Production
python deploy/deploy.py --target=build-and-deploy --environment=prod --branch=master
```

## Container Configuration Summary

All containers now use:
- **Virtual Environment**: `/app/venv/` (for Airflow: `/opt/airflow/venv/`)
- **PYTHONPATH**: `/app/libs` (for Airflow: `/opt/airflow/libs`)
- **Branch-specific code**: Git checkout during Docker build
- **Environment-specific images**: Tags include branch name (e.g., `dev-develop`, `uat-uat`, `prod-master`)

## Verification Steps

### 1. Test Branch Deployment:
```bash
# Test development deployment
devops/test-deployment.sh dev develop

# Test UAT deployment  
devops/test-deployment.sh uat uat

# Test production deployment
devops/test-deployment.sh prod master
```

### 2. Verify Container Configuration:
```bash
# Check PYTHONPATH in running containers
kubectl exec -it <pod-name> -- echo $PYTHONPATH

# Verify virtual environment
kubectl exec -it <pod-name> -- which python

# Check git branch in container
kubectl exec -it <pod-name> -- cat /app/.git/HEAD
```

## Troubleshooting

### Common Issues:

1. **Build fails with module import errors**:
   - Check PYTHONPATH is set to `/mnt/c/GenAI/mono-repo/libs`
   - Verify virtual environment is activated

2. **Docker image build fails**:
   - Verify BUILD_BRANCH argument is passed correctly
   - Check git checkout logic in Dockerfile

3. **Deployment to wrong environment**:
   - Verify branch-to-environment mapping in scripts
   - Check deployment configuration files have correct branch specified

## Security Considerations

1. **SSH Keys**: Use dedicated SSH keys for Bamboo-Bitbucket communication
2. **AWS Credentials**: Store as encrypted Bamboo variables
3. **Container Registry**: Use service accounts with minimal required permissions
4. **Branch Protection**: Enforce branch protection rules in Bitbucket
5. **Manual Approval**: Require manual approval for production deployments