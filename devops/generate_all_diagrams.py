#!/usr/bin/env python3
"""
Master Diagram Generator
Generates all service architecture diagrams for the mono-repo project.
"""

import subprocess
import sys
from pathlib import Path
import os

def run_diagram_script(script_name):
    """Run a diagram generation script and capture output."""
    try:
        script_path = Path(__file__).parent / script_name
        print(f"\n{'='*60}")
        print(f"Running {script_name}...")
        print(f"{'='*60}")
        
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True, cwd=script_path.parent)
        
        if result.returncode == 0:
            print("✅ SUCCESS:")
            print(result.stdout)
        else:
            print("❌ ERROR:")
            print(result.stderr)
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ EXCEPTION running {script_name}: {e}")
        return False

def main():
    """Generate all service diagrams."""
    
    print("🚀 Starting Master Diagram Generation")
    print("="*80)
    
    # Ensure output directory exists
    output_dir = Path("../docs/architecture")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {output_dir.absolute()}")
    
    # List of diagram scripts to run
    diagram_scripts = [
        "create_risk_api_diagrams.py",
        "create_dash_diagrams.py", 
        "create_web_apps_diagrams.py",
        "create_airflow_diagrams.py"
    ]
    
    # Track results
    results = {}
    
    # Run each diagram script
    for script in diagram_scripts:
        service_name = script.replace("create_", "").replace("_diagrams.py", "")
        print(f"\n🎨 Generating {service_name.upper()} diagrams...")
        
        success = run_diagram_script(script)
        results[service_name] = success
        
        if success:
            print(f"✅ {service_name.upper()} diagrams completed successfully!")
        else:
            print(f"❌ {service_name.upper()} diagrams failed!")
    
    # Summary report
    print("\n" + "="*80)
    print("📊 DIAGRAM GENERATION SUMMARY")
    print("="*80)
    
    successful = []
    failed = []
    
    for service, success in results.items():
        if success:
            successful.append(service)
            print(f"✅ {service.upper()}: SUCCESS")
        else:
            failed.append(service)
            print(f"❌ {service.upper()}: FAILED")
    
    print(f"\n📈 Total Services: {len(results)}")
    print(f"✅ Successful: {len(successful)} ({', '.join(successful)})")
    print(f"❌ Failed: {len(failed)} ({', '.join(failed) if failed else 'None'})")
    
    # List generated files
    if output_dir.exists():
        # Count both PNG and SVG files
        all_diagram_files = list(output_dir.glob("*.png")) + list(output_dir.glob("*.svg"))
        if all_diagram_files:
            print(f"\n📸 Generated Diagram Files ({len(all_diagram_files)}):")
            for file in sorted(all_diagram_files):
                size_kb = file.stat().st_size // 1024
                format_type = "PNG" if file.suffix == ".png" else "SVG"
                print(f"   • {file.name} ({size_kb} KB, {format_type})")
        else:
            print("\n⚠️  No diagram files found in output directory")
    
    # Final status
    if len(failed) == 0:
        print("\n🎉 ALL DIAGRAMS GENERATED SUCCESSFULLY!")
        print("📁 Check the docs/architecture/ directory for all diagram files.")
    else:
        print("\n⚠️  Some diagrams failed to generate. Check error messages above.")
    
    print("="*80)

if __name__ == "__main__":
    main()
