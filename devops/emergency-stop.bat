@echo off
REM Emergency Infrastructure Stop Script for Windows
REM Immediately stops all compute resources to minimize costs

echo.
echo 🚨 Emergency Infrastructure Stop
echo =================================
echo ⚠️  This will STOP (not destroy) all compute resources immediately

REM Check if AWS CLI is available
where aws >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ AWS CLI not found
    exit /b 1
)

echo.
echo 💰 Checking current resources...

REM Count current resources
for /f %%i in ('aws ec2 describe-instances --query "length(Reservations[].Instances[?State.Name!=`terminated`])" --output text 2^>nul') do set ec2_count=%%i
for /f %%i in ('aws rds describe-db-instances --query "length(DBInstances[?DBInstanceStatus!=`deleting`])" --output text 2^>nul') do set rds_count=%%i
for /f %%i in ('aws eks list-clusters --query "length(clusters[])" --output text 2^>nul') do set eks_count=%%i
for /f %%i in ('aws elbv2 describe-load-balancers --query "length(LoadBalancers[])" --output text 2^>nul') do set alb_count=%%i
for /f %%i in ('aws ec2 describe-nat-gateways --filter Name=state,Values=available --query "length(NatGateways[])" --output text 2^>nul') do set nat_count=%%i

echo EC2 Instances: %ec2_count%
echo RDS Instances: %rds_count%
echo EKS Clusters: %eks_count%
echo Load Balancers: %alb_count%
echo NAT Gateways: %nat_count%

echo.
echo ⚠️  This will immediately stop/delete compute resources
echo ⚠️  Data in databases and S3 will be preserved
set /p confirm="Continue? (y/N): "

if not "%confirm%"=="y" if not "%confirm%"=="Y" (
    echo ✅ Emergency stop cancelled
    exit /b 0
)

echo.
echo 🛑 Stopping EC2 instances...

REM Stop EC2 instances
for /f %%i in ('aws ec2 describe-instances --query "Reservations[].Instances[?State.Name==`running`].InstanceId" --output text 2^>nul') do (
    if not "%%i"=="" (
        echo Stopping EC2 instance: %%i
        aws ec2 stop-instances --instance-ids %%i >nul 2>nul
    )
)
echo ✅ EC2 instances stop initiated

echo.
echo 📉 Scaling down EKS node groups...

REM Scale down EKS node groups
for /f %%c in ('aws eks list-clusters --query "clusters[]" --output text 2^>nul') do (
    if not "%%c"=="" (
        echo Processing cluster: %%c
        for /f %%n in ('aws eks list-nodegroups --cluster-name %%c --query "nodegroups[]" --output text 2^>nul') do (
            if not "%%n"=="" (
                echo Scaling down node group: %%n
                aws eks update-nodegroup-config --cluster-name %%c --nodegroup-name %%n --scaling-config minSize=0,maxSize=0,desiredSize=0 >nul 2>nul
            )
        )
    )
)
echo ✅ EKS node groups scale-down initiated

echo.
echo 💾 Stopping RDS instances...

REM Stop RDS instances
for /f %%i in ('aws rds describe-db-instances --query "DBInstances[?DBInstanceStatus==`available`].DBInstanceIdentifier" --output text 2^>nul') do (
    if not "%%i"=="" (
        echo Stopping RDS instance: %%i
        aws rds stop-db-instance --db-instance-identifier %%i >nul 2>nul
    )
)
echo ✅ RDS instances stop initiated

echo.
echo ⚖️  Deleting load balancers...

REM Delete Application Load Balancers
for /f %%i in ('aws elbv2 describe-load-balancers --query "LoadBalancers[].LoadBalancerArn" --output text 2^>nul') do (
    if not "%%i"=="" (
        echo Deleting ALB: %%i
        aws elbv2 delete-load-balancer --load-balancer-arn %%i >nul 2>nul
    )
)

REM Delete Classic Load Balancers
for /f %%i in ('aws elb describe-load-balancers --query "LoadBalancerDescriptions[].LoadBalancerName" --output text 2^>nul') do (
    if not "%%i"=="" (
        echo Deleting CLB: %%i
        aws elb delete-load-balancer --load-balancer-name %%i >nul 2>nul
    )
)
echo ✅ Load Balancers deletion initiated

echo.
echo 🌐 Deleting NAT gateways...

REM Delete NAT gateways
for /f %%i in ('aws ec2 describe-nat-gateways --filter Name=state,Values=available --query "NatGateways[].NatGatewayId" --output text 2^>nul') do (
    if not "%%i"=="" (
        echo Deleting NAT Gateway: %%i
        aws ec2 delete-nat-gateway --nat-gateway-id %%i >nul 2>nul
    )
)
echo ✅ NAT Gateways deletion initiated

echo.
echo 🎉 Emergency stop completed!
echo Most compute costs should now be stopped.
echo.
echo 📋 What was preserved:
echo   - S3 buckets and data
echo   - RDS databases (stopped, not deleted)
echo   - EBS volumes
echo   - VPC and networking (except NAT gateways)
echo.
echo 💡 To fully clean up, run: scripts\teardown-infrastructure.bat

pause
