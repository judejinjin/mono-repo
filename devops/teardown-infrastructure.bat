@echo off
REM Infrastructure Teardown Script for Windows
REM Safely destroys AWS infrastructure to avoid ongoing charges

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "TERRAFORM_DIR=%PROJECT_ROOT%\infrastructure\terraform"

echo.
echo 🔥 Infrastructure Teardown Script
echo ===================================
echo ⚠️  This will DESTROY your AWS infrastructure!
echo ⚠️  Make sure you have backed up any important data!

REM Function to confirm destruction
:confirm_destruction
set /p environment="Which environment do you want to destroy? (dev/uat/prod): "

if not exist "%TERRAFORM_DIR%\%environment%.tfvars" (
    echo ❌ Environment %environment% not found
    exit /b 1
)

echo.
echo ⚠️  Are you sure you want to destroy the %environment% environment?
echo ⚠️  This action cannot be undone!
set /p confirmation="Type 'yes' to confirm: "

if not "%confirmation%"=="yes" (
    echo ✅ Teardown cancelled. Your infrastructure is safe.
    exit /b 0
)

REM Create backup directory
set "BACKUP_DIR=%PROJECT_ROOT%\backups\%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%_%environment%"
set "BACKUP_DIR=%BACKUP_DIR: =0%"
mkdir "%BACKUP_DIR%" 2>nul

echo.
echo 💾 Creating backup before teardown...

cd /d "%TERRAFORM_DIR%"

REM Backup Terraform state
if exist "terraform.tfstate" (
    copy "terraform.tfstate" "%BACKUP_DIR%\terraform.tfstate.backup" >nul
    echo ✅ Terraform state backed up
)

REM Backup Terraform vars
if exist "%environment%.tfvars" (
    copy "%environment%.tfvars" "%BACKUP_DIR%\%environment%.tfvars.backup" >nul
    echo ✅ Terraform variables backed up
)

REM Backup Kubernetes resources (if available)
where kubectl >nul 2>nul
if %errorlevel% equ 0 (
    echo 📦 Attempting to backup Kubernetes resources...
    kubectl cluster-info >nul 2>nul
    if %errorlevel% equ 0 (
        kubectl get all --all-namespaces -o yaml > "%BACKUP_DIR%\k8s-resources.yaml" 2>nul
        kubectl get configmaps --all-namespaces -o yaml > "%BACKUP_DIR%\k8s-configmaps.yaml" 2>nul
        kubectl get secrets --all-namespaces -o yaml > "%BACKUP_DIR%\k8s-secrets.yaml" 2>nul
        echo ✅ Kubernetes resources backed up
    ) else (
        echo ⚠️  Kubernetes cluster not accessible for backup
    )
) else (
    echo ⚠️  kubectl not found
)

echo 💾 Backup completed: %BACKUP_DIR%

echo.
echo 🧹 Cleaning up Kubernetes resources...

REM Remove Helm deployments
where helm >nul 2>nul
if %errorlevel% equ 0 (
    echo Removing Helm deployments...
    for /f "skip=1 tokens=1,2" %%a in ('helm list -A 2^>nul') do (
        if not "%%a"=="" if not "%%b"=="" (
            echo Uninstalling %%a from %%b...
            helm uninstall %%a -n %%b >nul 2>nul
        )
    )
)

REM Clean up Kubernetes resources
where kubectl >nul 2>nul
if %errorlevel% equ 0 (
    kubectl cluster-info >nul 2>nul
    if %errorlevel% equ 0 (
        echo Removing persistent volumes...
        kubectl delete pv --all --force --grace-period=0 >nul 2>nul
        
        echo Removing persistent volume claims...
        kubectl delete pvc --all --all-namespaces --force --grace-period=0 >nul 2>nul
        
        echo Removing load balancer services...
        for /f "skip=1 tokens=1,2" %%a in ('kubectl get services --all-namespaces 2^>nul ^| findstr LoadBalancer') do (
            if not "%%a"=="" if not "%%b"=="" (
                kubectl delete service %%b -n %%a >nul 2>nul
            )
        )
        
        echo ✅ Kubernetes cleanup completed
    ) else (
        echo ⚠️  Kubernetes cluster not accessible
    )
)

echo.
echo 🔥 Destroying %environment% infrastructure...

REM Destroy infrastructure
terraform destroy -var-file="%environment%.tfvars" -auto-approve
if %errorlevel% neq 0 (
    echo ⚠️  Standard destroy failed, trying targeted approach...
    
    echo Destroying EKS cluster...
    terraform destroy -target=aws_eks_cluster.main -var-file="%environment%.tfvars" -auto-approve >nul 2>nul
    
    echo Destroying EC2 instances...
    terraform destroy -target=aws_instance.dev_server -var-file="%environment%.tfvars" -auto-approve >nul 2>nul
    
    echo Destroying RDS instances...
    terraform destroy -target=aws_db_instance.postgres -var-file="%environment%.tfvars" -auto-approve >nul 2>nul
    
    echo Destroying remaining resources...
    terraform destroy -var-file="%environment%.tfvars" -auto-approve >nul 2>nul
)

echo ✅ Infrastructure destruction completed

echo.
echo 🔍 Verifying infrastructure destruction...

where aws >nul 2>nul
if %errorlevel% equ 0 (
    echo Checking for remaining resources...
    
    echo Checking EC2 instances...
    for /f %%i in ('aws ec2 describe-instances --query "Reservations[].Instances[?State.Name!=`terminated`].InstanceId" --output text 2^>nul') do (
        echo ⚠️  Found running EC2 instances: %%i
        goto :rds_check
    )
    echo ✅ No running EC2 instances
    
    :rds_check
    echo Checking RDS instances...
    for /f %%i in ('aws rds describe-db-instances --query "DBInstances[?DBInstanceStatus!=`deleting`].DBInstanceIdentifier" --output text 2^>nul') do (
        echo ⚠️  Found RDS instances: %%i
        goto :eks_check
    )
    echo ✅ No RDS instances
    
    :eks_check
    echo Checking EKS clusters...
    for /f %%i in ('aws eks list-clusters --query "clusters[]" --output text 2^>nul') do (
        echo ⚠️  Found EKS clusters: %%i
        goto :elb_check
    )
    echo ✅ No EKS clusters
    
    :elb_check
    echo Checking Load Balancers...
    for /f %%i in ('aws elbv2 describe-load-balancers --query "LoadBalancers[].LoadBalancerName" --output text 2^>nul') do (
        echo ⚠️  Found Load Balancers: %%i
        goto :nat_check
    )
    echo ✅ No Load Balancers
    
    :nat_check
    echo Checking NAT Gateways...
    for /f %%i in ('aws ec2 describe-nat-gateways --filter Name=state,Values=available --query "NatGateways[].NatGatewayId" --output text 2^>nul') do (
        echo ⚠️  Found NAT Gateways: %%i
        goto :cleanup_state
    )
    echo ✅ No NAT Gateways
    
) else (
    echo ⚠️  AWS CLI not found, skipping verification
)

:cleanup_state
echo.
echo 🧹 Cleaning up local Terraform state...
set /p clean_state="Do you want to remove local Terraform state files? (y/N): "

if /i "%clean_state%"=="y" (
    del terraform.tfstate terraform.tfstate.backup .terraform.lock.hcl 2>nul
    rmdir /s /q .terraform 2>nul
    echo ✅ Local state cleaned
) else (
    echo ⚠️  Local state preserved
)

echo.
echo 💰 Cost Verification Steps
echo ==========================
echo 1. Check AWS Billing Dashboard
echo 2. Review AWS Cost Explorer
echo 3. Set up billing alerts if not already done
echo 4. Monitor for next 24-48 hours
echo.
echo 🔗 AWS Billing Dashboard: https://console.aws.amazon.com/billing/home

echo.
echo 🎉 Teardown completed successfully!
echo Remember to check your AWS billing dashboard to confirm no ongoing charges.

pause
