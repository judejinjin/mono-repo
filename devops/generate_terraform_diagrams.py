#!/usr/bin/env python3
"""
Terraform Architecture Diagram Generator
Generates professional architecture diagrams from Terraform infrastructure.
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional

class TerraformDiagramGenerator:
    def __init__(self, terraform_dir: str, output_dir: str):
        self.terraform_dir = Path(terraform_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required tools are available."""
        dependencies = {}
        
        tools = ['terraform', 'dot', 'inframap']
        for tool in tools:
            try:
                subprocess.run([tool, '--version'], 
                             capture_output=True, check=True)
                dependencies[tool] = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                dependencies[tool] = False
                
        return dependencies
    
    def generate_terraform_graph(self, format_type: str = 'svg') -> bool:
        """Generate basic Terraform dependency graph."""
        try:
            print("📊 Generating Terraform dependency graph...")
            
            # Change to terraform directory
            original_dir = os.getcwd()
            os.chdir(self.terraform_dir)
            
            # Generate graph
            result = subprocess.run(['terraform', 'graph'], 
                                  capture_output=True, text=True, check=True)
            
            # Save DOT file
            dot_file = self.output_dir / 'terraform_dependencies.dot'
            with open(dot_file, 'w') as f:
                f.write(result.stdout)
            
            # Generate image if Graphviz is available
            if format_type in ['png', 'svg']:
                output_file = self.output_dir / f'terraform_dependencies.{format_type}'
                subprocess.run(['dot', f'-T{format_type}', str(dot_file), 
                              '-o', str(output_file)], check=True)
                print(f"✅ Terraform graph generated: {output_file}")
            
            os.chdir(original_dir)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate Terraform graph: {e}")
            return False
        finally:
            os.chdir(original_dir)
    
    def generate_inframap_diagram(self, environment: Optional[str] = None, 
                                format_type: str = 'svg') -> bool:
        """Generate AWS infrastructure diagram using Inframap."""
        try:
            print(f"🏗️  Generating Inframap diagram for {environment or 'default'}...")
            
            original_dir = os.getcwd()
            os.chdir(self.terraform_dir)
            
            # Prepare plan command
            plan_cmd = ['terraform', 'plan', '-out=temp_plan.out']
            if environment and (self.terraform_dir / f'{environment}.tfvars').exists():
                plan_cmd.extend(['-var-file', f'{environment}.tfvars'])
            
            # Generate plan
            subprocess.run(plan_cmd, capture_output=True, check=True)
            
            # Convert plan to JSON
            subprocess.run(['terraform', 'show', '-json', 'temp_plan.out'], 
                         stdout=open('temp_plan.json', 'w'), check=True)
            
            # Generate inframap
            result = subprocess.run(['inframap', 'generate', 'temp_plan.json'], 
                                  capture_output=True, text=True, check=True)
            
            # Save DOT file
            suffix = f'_{environment}' if environment else ''
            dot_file = self.output_dir / f'aws_infrastructure{suffix}.dot'
            with open(dot_file, 'w') as f:
                f.write(result.stdout)
            
            # Generate image
            if format_type in ['png', 'svg']:
                output_file = self.output_dir / f'aws_infrastructure{suffix}.{format_type}'
                subprocess.run(['dot', f'-T{format_type}', str(dot_file), 
                              '-o', str(output_file)], check=True)
                print(f"✅ Inframap diagram generated: {output_file}")
            
            # Cleanup
            for temp_file in ['temp_plan.out', 'temp_plan.json']:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            os.chdir(original_dir)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate Inframap diagram: {e}")
            return False
        finally:
            os.chdir(original_dir)
    
    def generate_custom_diagram(self, environment: Optional[str] = None) -> bool:
        """Generate custom diagram using Python libraries."""
        try:
            print(f"🎨 Generating custom diagram for {environment or 'default'}...")
            
            # This is a placeholder for custom diagram generation
            # Could integrate with libraries like:
            # - diagrams (https://diagrams.mingrammer.com/)
            # - matplotlib for custom visualizations
            # - networkx for graph-based diagrams
            
            # For now, create a simple text-based architecture description
            arch_file = self.output_dir / f'architecture_{environment or "default"}.md'
            
            with open(arch_file, 'w') as f:
                f.write(f"# Infrastructure Architecture - {environment or 'Default'}\n\n")
                f.write("## Components\n\n")
                f.write("- VPC with public/private subnets\n")
                f.write("- EKS cluster for container orchestration\n")
                f.write("- RDS PostgreSQL for transactional data\n")
                f.write("- Snowflake for data warehousing\n")
                f.write("- S3 buckets for storage\n")
                f.write("- EC2 instances for development server\n")
                f.write("- IAM roles and policies\n")
                f.write("- Load balancers and security groups\n")
            
            print(f"✅ Architecture description generated: {arch_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate custom diagram: {e}")
            return False
    
    def generate_all_diagrams(self, environments: List[str], formats: List[str]):
        """Generate all types of diagrams for all environments."""
        dependencies = self.check_dependencies()
        
        print("🔍 Checking dependencies...")
        for tool, available in dependencies.items():
            status = "✅" if available else "❌"
            print(f"{status} {tool}")
        
        # Generate Terraform graph
        if dependencies['terraform'] and dependencies['dot']:
            for fmt in formats:
                self.generate_terraform_graph(fmt)
        
        # Generate Inframap diagrams
        if dependencies['inframap'] and dependencies['dot']:
            for env in environments:
                for fmt in formats:
                    self.generate_inframap_diagram(env, fmt)
        
        # Generate custom diagrams
        for env in environments:
            self.generate_custom_diagram(env)
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate a summary of all created diagrams."""
        print("\n📋 Generated Diagrams Summary")
        print("=" * 30)
        
        files = list(self.output_dir.glob('*'))
        for file in sorted(files):
            print(f"📄 {file.name}")
        
        print(f"\n📁 Output directory: {self.output_dir}")
        print("🌐 View SVG files in browser for best quality")

def main():
    parser = argparse.ArgumentParser(description='Generate Terraform architecture diagrams')
    parser.add_argument('--terraform-dir', default='infrastructure/terraform',
                       help='Path to Terraform directory')
    parser.add_argument('--output-dir', default='docs/architecture',
                       help='Output directory for diagrams')
    parser.add_argument('--environments', nargs='+', default=['dev', 'uat', 'prod'],
                       help='Environments to generate diagrams for')
    parser.add_argument('--formats', nargs='+', default=['svg', 'png'],
                       help='Output formats (svg, png)')
    
    args = parser.parse_args()
    
    # Resolve paths relative to script location
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    terraform_dir = project_root / args.terraform_dir
    output_dir = project_root / args.output_dir
    
    if not terraform_dir.exists():
        print(f"❌ Terraform directory not found: {terraform_dir}")
        sys.exit(1)
    
    generator = TerraformDiagramGenerator(terraform_dir, output_dir)
    generator.generate_all_diagrams(args.environments, args.formats)
    
    print("\n🎉 Diagram generation complete!")

if __name__ == '__main__':
    main()
