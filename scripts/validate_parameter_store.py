#!/usr/bin/env python3
"""
Parameter Store Validation Tool
Validates configuration values in AWS Systems Manager Parameter Store.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from libs.cloud.parameter_store import ParameterStoreManager, ParameterStoreConfig
from config import get_environment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParameterStoreValidator:
    """Validates Parameter Store configuration."""
    
    def __init__(self, region_name: str = None):
        self.parameter_manager = ParameterStoreManager(region_name)
        self.region_name = region_name or os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        
        # Expected parameter structure for validation
        self.expected_structure = {
            'terraform': ['aws_account_id', 'aws_region', 'project_name', 'vpc_cidr'],
            'eks': ['cluster_name', 'node_group_min_size', 'node_group_max_size', 'node_group_desired_size'],
            'rds': ['db_name', 'username', 'password', 'instance_class', 'allocated_storage'],
            'fastapi': ['port', 'debug', 'workers', 'host'],
            'web': ['port', 'debug', 'build_env'],
            'dash': ['port', 'debug'],
            'airflow': ['webserver_port', 'executor', 'namespace'],
            'security': ['jwt_secret_key', 'encryption_key'],
            'monitoring': ['cloudwatch_log_group', 'metrics_namespace', 'log_level'],
            'ecr': ['registry_url', 'repository_prefix'],
            's3': ['bucket_prefix', 'terraform_state_bucket'],
        }
    
    def validate_environment_structure(self, environment: str) -> Dict[str, Any]:
        """
        Validate the parameter structure for an environment.
        
        Args:
            environment: Environment to validate
            
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Validating parameter structure for environment: {environment}")
        
        results = {
            'environment': environment,
            'apps': {},
            'summary': {
                'total_apps': 0,
                'valid_apps': 0,
                'total_parameters': 0,
                'found_parameters': 0,
                'missing_parameters': [],
                'extra_parameters': []
            }
        }
        
        for app_name, expected_params in self.expected_structure.items():
            app_results = self._validate_app_parameters(environment, app_name, expected_params)
            results['apps'][app_name] = app_results
            
            # Update summary
            results['summary']['total_apps'] += 1
            if app_results['is_valid']:
                results['summary']['valid_apps'] += 1
            
            results['summary']['total_parameters'] += len(expected_params)
            results['summary']['found_parameters'] += len(app_results['found_parameters'])
            results['summary']['missing_parameters'].extend(app_results['missing_parameters'])
            results['summary']['extra_parameters'].extend(app_results['extra_parameters'])
        
        return results
    
    def _validate_app_parameters(
        self, 
        environment: str, 
        app_name: str, 
        expected_params: List[str]
    ) -> Dict[str, Any]:
        """Validate parameters for a specific app."""
        logger.info(f"Validating {app_name} parameters...")
        
        # Get actual parameters
        actual_params = self.parameter_manager.get_environment_parameters(environment, app_name)
        
        found_params = list(actual_params.keys())
        missing_params = [param for param in expected_params if param not in found_params]
        extra_params = [param for param in found_params if param not in expected_params]
        
        is_valid = len(missing_params) == 0
        
        results = {
            'app_name': app_name,
            'is_valid': is_valid,
            'expected_parameters': expected_params,
            'found_parameters': found_params,
            'missing_parameters': missing_params,
            'extra_parameters': extra_params,
            'parameter_values': actual_params
        }
        
        if is_valid:
            logger.info(f"✅ {app_name}: All {len(expected_params)} parameters found")
        else:
            logger.warning(f"⚠️  {app_name}: {len(missing_params)} missing parameters")
            for param in missing_params:
                logger.warning(f"    Missing: {param}")
        
        if extra_params:
            logger.info(f"ℹ️  {app_name}: {len(extra_params)} extra parameters")
            for param in extra_params:
                logger.info(f"    Extra: {param}")
        
        return results
    
    def validate_parameter_values(self, environment: str) -> Dict[str, Any]:
        """
        Validate parameter values for correctness.
        
        Args:
            environment: Environment to validate
            
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Validating parameter values for environment: {environment}")
        
        validation_rules = {
            'fastapi': {
                'port': lambda x: x.isdigit() and 1000 <= int(x) <= 65535,
                'debug': lambda x: x.lower() in ['true', 'false'],
                'workers': lambda x: x.isdigit() and int(x) > 0
            },
            'web': {
                'port': lambda x: x.isdigit() and 1000 <= int(x) <= 65535,
                'debug': lambda x: x.lower() in ['true', 'false']
            },
            'dash': {
                'port': lambda x: x.isdigit() and 1000 <= int(x) <= 65535,
                'debug': lambda x: x.lower() in ['true', 'false']
            },
            'eks': {
                'node_group_min_size': lambda x: x.isdigit() and int(x) >= 1,
                'node_group_max_size': lambda x: x.isdigit() and int(x) >= 1,
                'node_group_desired_size': lambda x: x.isdigit() and int(x) >= 1
            },
            'rds': {
                'allocated_storage': lambda x: x.isdigit() and int(x) >= 20
            }
        }
        
        results = {
            'environment': environment,
            'validation_results': {},
            'summary': {
                'total_validations': 0,
                'passed_validations': 0,
                'failed_validations': []
            }
        }
        
        for app_name, rules in validation_rules.items():
            app_params = self.parameter_manager.get_environment_parameters(environment, app_name)
            app_results = {}
            
            for param_name, validation_func in rules.items():
                if param_name in app_params:
                    param_value = app_params[param_name]
                    is_valid = validation_func(param_value)
                    
                    app_results[param_name] = {
                        'value': param_value,
                        'is_valid': is_valid
                    }
                    
                    results['summary']['total_validations'] += 1
                    if is_valid:
                        results['summary']['passed_validations'] += 1
                        logger.info(f"✅ {app_name}.{param_name}: {param_value}")
                    else:
                        results['summary']['failed_validations'].append(f"{app_name}.{param_name}")
                        logger.error(f"❌ {app_name}.{param_name}: Invalid value '{param_value}'")
            
            if app_results:
                results['validation_results'][app_name] = app_results
        
        return results
    
    def test_parameter_access(self, environment: str) -> Dict[str, Any]:
        """
        Test parameter access and configuration loading.
        
        Args:
            environment: Environment to test
            
        Returns:
            Dictionary with test results
        """
        logger.info(f"Testing parameter access for environment: {environment}")
        
        results = {
            'environment': environment,
            'access_tests': {},
            'config_loading_test': None,
            'summary': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': []
            }
        }
        
        # Test direct parameter access
        test_apps = ['terraform', 'fastapi', 'security']
        
        for app_name in test_apps:
            try:
                app_params = self.parameter_manager.get_environment_parameters(environment, app_name)
                
                test_result = {
                    'success': True,
                    'parameter_count': len(app_params),
                    'sample_parameters': list(app_params.keys())[:3]  # Show first 3 params
                }
                
                results['access_tests'][app_name] = test_result
                results['summary']['total_tests'] += 1
                results['summary']['passed_tests'] += 1
                
                logger.info(f"✅ {app_name}: Retrieved {len(app_params)} parameters")
                
            except Exception as e:
                test_result = {
                    'success': False,
                    'error': str(e)
                }
                
                results['access_tests'][app_name] = test_result
                results['summary']['total_tests'] += 1
                results['summary']['failed_tests'].append(app_name)
                
                logger.error(f"❌ {app_name}: Failed to retrieve parameters - {e}")
        
        # Test config loading through ParameterStoreConfig
        try:
            param_config = ParameterStoreConfig(environment, self.region_name)
            
            # Test getting a specific parameter
            test_value = param_config.get('fastapi', 'port', 'default')
            
            config_test = {
                'success': True,
                'test_value': test_value,
                'cache_enabled': param_config.cache_parameters
            }
            
            results['config_loading_test'] = config_test
            results['summary']['total_tests'] += 1
            results['summary']['passed_tests'] += 1
            
            logger.info(f"✅ Config loading test passed (fastapi.port = {test_value})")
            
        except Exception as e:
            config_test = {
                'success': False,
                'error': str(e)
            }
            
            results['config_loading_test'] = config_test
            results['summary']['total_tests'] += 1
            results['summary']['failed_tests'].append('config_loading')
            
            logger.error(f"❌ Config loading test failed: {e}")
        
        return results
    
    def generate_validation_report(
        self,
        structure_results: Dict[str, Any],
        value_results: Dict[str, Any],
        access_results: Dict[str, Any]
    ) -> str:
        """Generate a comprehensive validation report."""
        report_lines = []
        report_lines.append("Parameter Store Validation Report")
        report_lines.append(f"Environment: {structure_results['environment']}")
        report_lines.append(f"Region: {self.region_name}")
        report_lines.append(f"Generated: {os.popen('date').read().strip()}")
        report_lines.append("=" * 60)
        
        # Structure validation summary
        structure_summary = structure_results['summary']
        report_lines.append(f"\n📋 Parameter Structure Validation:")
        report_lines.append(f"  Apps validated: {structure_summary['valid_apps']}/{structure_summary['total_apps']}")
        report_lines.append(f"  Parameters found: {structure_summary['found_parameters']}/{structure_summary['total_parameters']}")
        
        if structure_summary['missing_parameters']:
            report_lines.append(f"\n❌ Missing Parameters ({len(structure_summary['missing_parameters'])}):")
            for param in structure_summary['missing_parameters'][:10]:  # Show first 10
                report_lines.append(f"    {param}")
            if len(structure_summary['missing_parameters']) > 10:
                report_lines.append(f"    ... and {len(structure_summary['missing_parameters']) - 10} more")
        
        # Value validation summary
        value_summary = value_results['summary']
        report_lines.append(f"\n✓ Parameter Value Validation:")
        report_lines.append(f"  Validations passed: {value_summary['passed_validations']}/{value_summary['total_validations']}")
        
        if value_summary['failed_validations']:
            report_lines.append(f"\n❌ Failed Value Validations:")
            for param in value_summary['failed_validations']:
                report_lines.append(f"    {param}")
        
        # Access test summary
        access_summary = access_results['summary']
        report_lines.append(f"\n🔌 Parameter Access Tests:")
        report_lines.append(f"  Tests passed: {access_summary['passed_tests']}/{access_summary['total_tests']}")
        
        if access_summary['failed_tests']:
            report_lines.append(f"\n❌ Failed Access Tests:")
            for test in access_summary['failed_tests']:
                report_lines.append(f"    {test}")
        
        # Detailed app status
        report_lines.append(f"\n📊 Detailed App Status:")
        for app_name, app_results in structure_results['apps'].items():
            status = "✅" if app_results['is_valid'] else "❌"
            param_count = len(app_results['found_parameters'])
            expected_count = len(app_results['expected_parameters'])
            report_lines.append(f"  {status} {app_name}: {param_count}/{expected_count} parameters")
        
        # Recommendations
        report_lines.append(f"\n💡 Recommendations:")
        
        if structure_summary['missing_parameters']:
            report_lines.append("  - Run migration tool to populate missing parameters")
            report_lines.append("  - Check IAM permissions for Parameter Store access")
        
        if value_summary['failed_validations']:
            report_lines.append("  - Review and correct invalid parameter values")
            
        if access_summary['failed_tests']:
            report_lines.append("  - Verify AWS credentials and Parameter Store permissions")
            report_lines.append("  - Check network connectivity to AWS services")
        
        if (structure_summary['valid_apps'] == structure_summary['total_apps'] and
            value_summary['passed_validations'] == value_summary['total_validations'] and
            access_summary['passed_tests'] == access_summary['total_tests']):
            report_lines.append("  🎉 All validations passed! Parameter Store is ready for use.")
        
        return "\n".join(report_lines)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Validate AWS Parameter Store configuration')
    parser.add_argument('--environment', '-e',
                       default=get_environment(),
                       choices=['dev', 'uat', 'prod'],
                       help='Environment to validate (default: current environment)')
    parser.add_argument('--region', '-r',
                       default=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
                       help='AWS region (default: us-east-1)')
    parser.add_argument('--output', '-o',
                       type=Path,
                       help='Save validation report to file')
    parser.add_argument('--json',
                       action='store_true',
                       help='Output results in JSON format')
    parser.add_argument('--structure-only',
                       action='store_true',
                       help='Only validate parameter structure')
    parser.add_argument('--values-only',
                       action='store_true',
                       help='Only validate parameter values')
    parser.add_argument('--access-only',
                       action='store_true',
                       help='Only test parameter access')
    
    args = parser.parse_args()
    
    logger.info(f"Parameter Store Validation Tool")
    logger.info(f"Environment: {args.environment}")
    logger.info(f"Region: {args.region}")
    
    # Initialize validator
    validator = ParameterStoreValidator(args.region)
    
    # Determine which validations to run
    run_structure = not (args.values_only or args.access_only)
    run_values = not (args.structure_only or args.access_only)
    run_access = not (args.structure_only or args.values_only)
    
    results = {}
    
    # Run validations
    if run_structure:
        logger.info("🔍 Running parameter structure validation...")
        structure_results = validator.validate_environment_structure(args.environment)
        results['structure'] = structure_results
    
    if run_values:
        logger.info("🔍 Running parameter value validation...")
        value_results = validator.validate_parameter_values(args.environment)
        results['values'] = value_results
    
    if run_access:
        logger.info("🔍 Running parameter access tests...")
        access_results = validator.test_parameter_access(args.environment)
        results['access'] = access_results
    
    # Generate output
    if args.json:
        output = json.dumps(results, indent=2)
    else:
        # Generate text report
        structure_results = results.get('structure', {'summary': {'valid_apps': 0, 'total_apps': 0, 'found_parameters': 0, 'total_parameters': 0, 'missing_parameters': []}, 'apps': {}})
        value_results = results.get('values', {'summary': {'passed_validations': 0, 'total_validations': 0, 'failed_validations': []}, 'validation_results': {}})
        access_results = results.get('access', {'summary': {'passed_tests': 0, 'total_tests': 0, 'failed_tests': []}, 'access_tests': {}})
        
        output = validator.generate_validation_report(
            structure_results,
            value_results,
            access_results
        )
    
    # Output results
    if args.output:
        args.output.write_text(output)
        logger.info(f"📄 Validation report saved to: {args.output}")
    else:
        print("\n" + output)
    
    # Determine exit code
    exit_code = 0
    
    if 'structure' in results:
        structure_summary = results['structure']['summary']
        if structure_summary['valid_apps'] != structure_summary['total_apps']:
            exit_code = 1
    
    if 'values' in results:
        value_summary = results['values']['summary']
        if value_summary['passed_validations'] != value_summary['total_validations']:
            exit_code = 1
    
    if 'access' in results:
        access_summary = results['access']['summary']
        if access_summary['passed_tests'] != access_summary['total_tests']:
            exit_code = 1
    
    if exit_code == 0:
        logger.info("✅ All validations passed successfully")
    else:
        logger.error("❌ Some validations failed")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())