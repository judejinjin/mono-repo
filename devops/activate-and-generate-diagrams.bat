@echo off
REM Virtual Environment Activation and Diagram Generation Script
REM This script activates the Python virtual environment and generates Terraform diagrams

echo.
echo 🚀 Activating Python Virtual Environment and Generating Diagrams
echo ==================================================================

REM Check if virtual environment exists (look in parent directory)
if not exist "..\venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found in parent directory. Please run from project root.
    exit /b 1
)

REM Activate virtual environment from parent directory
echo ✅ Activating virtual environment...
call ..\venv\Scripts\activate.bat

REM Check if required packages are installed
echo ✅ Checking required packages...
python -c "import matplotlib.pyplot" 2>nul
if %errorlevel% neq 0 (
    echo 📦 Installing required packages...
    python -m pip install -r requirements-diagrams.txt
)

echo.
echo 🎨 Generating Architecture Diagrams...
echo =====================================

REM Generate visual diagrams with matplotlib
echo 📊 Creating visual diagrams...
python create_architecture_diagrams.py

REM Generate CI/CD flow diagram
echo 📊 Creating CI/CD flow diagram...
python create_cicd_flow_diagram.py

REM Generate detailed descriptions
echo 📄 Creating detailed descriptions...
python generate_terraform_diagrams.py --terraform-dir ..\infrastructure\terraform --output-dir ..\docs\architecture --environments dev uat prod

echo.
echo 🎉 Diagram generation complete!
echo 📁 Output directory: docs\architecture\
echo 🖼️  Visual diagrams: *.png and *.svg files
echo 📄 Documentation: *.md files
echo.
echo 💡 To view diagrams:
echo    - Open PNG/SVG files in your browser or image viewer
echo    - Read MD files for detailed architecture descriptions
echo.

REM Keep command prompt open
cmd /k
