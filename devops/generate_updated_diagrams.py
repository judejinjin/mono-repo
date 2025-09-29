#!/usr/bin/env python3
"""
Generate All Updated Diagrams

This script generates all updated diagrams to reflect the latest implementations:
- Performance optimization diagrams
- Security framework diagrams  
- Updated architecture diagrams
- Enhanced monitoring diagrams

Run this script to update all architecture documentation.
"""

import sys
import subprocess
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_diagram_script(script_name, description):
    """Run a diagram generation script"""
    try:
        logger.info(f"Generating {description}...")
        
        script_path = Path(__file__).parent / script_name
        if not script_path.exists():
            logger.error(f"Script not found: {script_path}")
            return False
        
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            logger.info(f"✅ Successfully generated {description}")
            if result.stdout:
                logger.info(f"Output: {result.stdout}")
            return True
        else:
            logger.error(f"❌ Failed to generate {description}")
            logger.error(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Exception while generating {description}: {e}")
        return False

def main():
    """Generate all updated diagrams"""
    
    print("=" * 80)
    print("GENERATING ALL UPDATED ARCHITECTURE DIAGRAMS")
    print("=" * 80)
    print("")
    
    # List of diagram scripts to run
    diagram_scripts = [
        {
            'script': 'create_performance_optimization_diagrams.py',
            'description': 'Performance Optimization Diagrams'
        },
        {
            'script': 'create_security_framework_diagrams.py', 
            'description': 'Security Framework Diagrams'
        },
        {
            'script': 'create_updated_architecture_diagrams.py',
            'description': 'Updated Architecture Diagrams'
        },
        {
            'script': 'create_monitoring_stack_diagrams.py',
            'description': 'Enhanced Monitoring Stack Diagrams'
        },
        {
            'script': 'create_risk_api_diagrams.py',
            'description': 'Updated Risk API Diagrams'
        },
        {
            'script': 'create_web_apps_diagrams.py',
            'description': 'Web Applications Diagrams'
        }
    ]
    
    # Track results
    successful = []
    failed = []
    
    # Generate each diagram set
    for diagram in diagram_scripts:
        if run_diagram_script(diagram['script'], diagram['description']):
            successful.append(diagram['description'])
        else:
            failed.append(diagram['description'])
        print("")  # Add spacing between diagram generations
    
    # Summary
    print("=" * 80)
    print("DIAGRAM GENERATION SUMMARY")
    print("=" * 80)
    
    if successful:
        print(f"✅ Successfully Generated ({len(successful)}):")
        for desc in successful:
            print(f"   • {desc}")
        print("")
    
    if failed:
        print(f"❌ Failed to Generate ({len(failed)}):")
        for desc in failed:
            print(f"   • {desc}")
        print("")
    
    # Overall status
    total = len(diagram_scripts)
    success_rate = len(successful) / total * 100
    
    print(f"📊 Generation Statistics:")
    print(f"   • Total Scripts: {total}")
    print(f"   • Successful: {len(successful)}")
    print(f"   • Failed: {len(failed)}")
    print(f"   • Success Rate: {success_rate:.1f}%")
    print("")
    
    # Output location
    output_dir = Path("docs/architecture").absolute()
    print(f"📁 Diagrams saved to: {output_dir}")
    
    # List generated files
    if output_dir.exists():
        png_files = list(output_dir.glob("*.png"))
        svg_files = list(output_dir.glob("*.svg"))
        
        print(f"📈 Generated Files:")
        print(f"   • PNG files: {len(png_files)}")
        print(f"   • SVG files: {len(svg_files)}")
        
        # Show recent files (last 10)
        all_files = sorted(png_files + svg_files, key=lambda x: x.stat().st_mtime, reverse=True)
        if all_files:
            print(f"📋 Recent Files:")
            for file in all_files[:10]:
                print(f"   • {file.name}")
            if len(all_files) > 10:
                print(f"   • ... and {len(all_files) - 10} more files")
    
    print("")
    print("=" * 80)
    
    # Exit with appropriate code
    if failed:
        print("⚠️  Some diagrams failed to generate. Check logs above for details.")
        sys.exit(1)
    else:
        print("🎉 All diagrams generated successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()