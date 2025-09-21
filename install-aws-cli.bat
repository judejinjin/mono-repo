@echo off
echo Installing AWS CLI...

REM Download AWS CLI if not already present
if not exist "AWSCLIV2.msi" (
    echo Downloading AWS CLI installer...
    powershell -Command "Invoke-WebRequest -Uri 'https://awscli.amazonaws.com/AWSCLIV2.msi' -OutFile 'AWSCLIV2.msi'"
)

REM Install AWS CLI
echo Installing AWS CLI...
msiexec /i AWSCLIV2.msi /quiet /norestart

REM Wait for installation to complete
timeout /t 30 /nobreak

REM Add AWS CLI to PATH for current session
set PATH=%PATH%;C:\Program Files\Amazon\AWSCLIV2

REM Check installation
echo Checking AWS CLI installation...
aws --version

if %errorlevel% neq 0 (
    echo AWS CLI installation may need a system restart or manual PATH update.
    echo Please restart your command prompt or add the following to your PATH:
    echo C:\Program Files\Amazon\AWSCLIV2
)

echo.
echo Installation complete! You may need to restart your command prompt.
echo.
echo To configure AWS CLI, run:
echo aws configure
echo.
pause
