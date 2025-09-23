@echo off
REM Terraform Infrastructure Visualization Script for Windows
REM This script generates architecture diagrams from Terraform infrastructure

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "TERRAFORM_DIR=%PROJECT_ROOT%\infrastructure\terraform"
set "OUTPUT_DIR=%SCRIPT_DIR%docs"

echo.
echo 🎨 Terraform Infrastructure Visualization Script
echo ================================================

REM Create output directory
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Function to check if command exists
where terraform >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Terraform not found
    exit /b 1
)

where dot >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Graphviz not found. Install with: choco install graphviz
    set "GRAPHVIZ_AVAILABLE=false"
) else (
    set "GRAPHVIZ_AVAILABLE=true"
)

where inframap >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Inframap not found. Download from: https://github.com/cycloidio/inframap/releases
    set "INFRAMAP_AVAILABLE=false"
) else (
    set "INFRAMAP_AVAILABLE=true"
)

echo.
echo 📊 Generating Terraform dependency graphs...

cd /d "%TERRAFORM_DIR%"

REM Generate basic dependency graph
terraform graph > "%TEMP%\terraform_graph.dot" 2>nul
if %errorlevel% equ 0 (
    if "%GRAPHVIZ_AVAILABLE%"=="true" (
        dot -Tpng "%TEMP%\terraform_graph.dot" > "%OUTPUT_DIR%\terraform_dependencies.png"
        dot -Tsvg "%TEMP%\terraform_graph.dot" > "%OUTPUT_DIR%\terraform_dependencies.svg"
        echo ✅ Terraform dependency graph generated
    ) else (
        copy "%TEMP%\terraform_graph.dot" "%OUTPUT_DIR%\terraform_dependencies.dot" >nul
        echo ⚠️  DOT file saved. Install Graphviz to generate images
    )
) else (
    echo ❌ Failed to generate terraform graph. Ensure terraform is initialized.
)

echo.
echo 🏗️  Generating Inframap AWS diagrams...

if "%INFRAMAP_AVAILABLE%"=="true" (
    REM Generate from plan
    terraform plan -out=plan.out >nul 2>nul
    if %errorlevel% equ 0 (
        terraform show -json plan.out > plan.json
        
        inframap generate plan.json > "%TEMP%\inframap.dot" 2>nul
        if %errorlevel% equ 0 (
            if "%GRAPHVIZ_AVAILABLE%"=="true" (
                dot -Tpng "%TEMP%\inframap.dot" > "%OUTPUT_DIR%\aws_infrastructure_plan.png"
                dot -Tsvg "%TEMP%\inframap.dot" > "%OUTPUT_DIR%\aws_infrastructure_plan.svg"
                echo ✅ Inframap diagram generated from plan
            ) else (
                copy "%TEMP%\inframap.dot" "%OUTPUT_DIR%\aws_infrastructure_plan.dot" >nul
                echo ⚠️  DOT file saved. Install Graphviz to generate images
            )
        ) else (
            echo ❌ Failed to generate inframap diagram
        )
        
        REM Cleanup
        del plan.out plan.json 2>nul
    ) else (
        echo ❌ Failed to create terraform plan
    )
)

echo.
echo 🌍 Generating environment-specific diagrams...

for %%e in (dev uat prod) do (
    echo Processing %%e environment...
    
    if exist "%%e.tfvars" (
        terraform plan -var-file="%%e.tfvars" -out="%%e_plan.out" >nul 2>nul
        if !errorlevel! equ 0 (
            terraform show -json "%%e_plan.out" > "%%e_plan.json"
            
            if "%INFRAMAP_AVAILABLE%"=="true" if "%GRAPHVIZ_AVAILABLE%"=="true" (
                inframap generate "%%e_plan.json" | dot -Tpng > "%OUTPUT_DIR%\%%e_infrastructure.png"
                inframap generate "%%e_plan.json" | dot -Tsvg > "%OUTPUT_DIR%\%%e_infrastructure.svg"
                echo ✅ %%e environment diagram generated
            )
            
            del "%%e_plan.out" "%%e_plan.json" 2>nul
        ) else (
            echo ❌ Failed to create plan for %%e environment
        )
    ) else (
        echo ⚠️  No tfvars file found for %%e environment
    )
)

echo.
echo 📋 Generated Diagrams Summary
echo ==============================

if exist "%OUTPUT_DIR%" (
    for %%f in ("%OUTPUT_DIR%\*.png" "%OUTPUT_DIR%\*.svg" "%OUTPUT_DIR%\*.dot") do (
        echo 📄 %%~nxf
    )
)

echo.
echo 📁 Output directory: %OUTPUT_DIR%
echo 🌐 View SVG files in browser for best quality
echo.
echo 🎉 Visualization generation complete!

pause
