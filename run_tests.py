"""
Test Runner Script
Comprehensive test execution with reporting and coverage
"""

#!/usr/def run_security_verification():
    """Run security requirements verification."""
    print("\\n" + "="*50)
    print("RUNNING SECURITY REQUIREMENTS VERIFICATION")
    print("="*50)
    
    security_script = PROJECT_ROOT / 'build' / 'verify_security_requirements.py'
    if not security_script.exists():
        print("⚠️  Security verification script not found")
        return {'success': False, 'reason': 'script_not_found'}
    
    # Run security verification with development tools check
    result = run_command([
        sys.executable, str(security_script), '--development'
    ])
    
    print(f"Security verification result: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
    if not result['success']:
        print("Security requirements verification failed!")
        print("Run the following to install missing security packages:")
        print("pip install -r build/requirements/dev.txt")
    
    return result


def run_linting():
    """Run code linting and style checks."""
    print("\\n" + "="*50)
    print("RUNNING LINTING AND STYLE CHECKS")
    print("="*50)nv python3

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import time
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.test_framework import TestRunner


def run_command(cmd: List[str], cwd: Optional[Path] = None) -> Dict[str, Any]:
    """Run command and return result."""
    cwd = cwd or PROJECT_ROOT
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        return {
            'command': ' '.join(cmd),
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
        
    except subprocess.TimeoutExpired:
        return {
            'command': ' '.join(cmd),
            'exit_code': -1,
            'stdout': '',
            'stderr': 'Command timed out after 5 minutes',
            'success': False
        }
    except Exception as e:
        return {
            'command': ' '.join(cmd),
            'exit_code': -1,
            'stdout': '',
            'stderr': str(e),
            'success': False
        }


def install_test_dependencies():
    """Install test dependencies."""
    print("Installing test dependencies...")
    
    test_requirements = [
        'pytest>=6.0.0',
        'pytest-cov>=2.12.0',
        'pytest-asyncio>=0.20.0',
        'pytest-benchmark>=3.4.1',
        'pytest-mock>=3.6.1',
        'pytest-xdist>=2.5.0',  # For parallel test execution
        'httpx>=0.24.0',  # For async HTTP testing
        'fastapi[all]>=0.100.0',
        'pandas>=1.5.0',
        'numpy>=1.21.0',
        'psutil>=5.9.0',  # For memory/performance monitoring
        'coverage>=6.0.0'
    ]
    
    # Install requirements
    for req in test_requirements:
        result = run_command([sys.executable, '-m', 'pip', 'install', req])
        if not result['success']:
            print(f"Warning: Failed to install {req}")
            print(f"Error: {result['stderr']}")


def run_linting():
    """Run code linting and style checks."""
    print("\n" + "="*50)
    print("RUNNING LINTING AND STYLE CHECKS")
    print("="*50)
    
    results = {}
    
    # Try to install linting tools
    linting_tools = ['flake8', 'black', 'isort', 'mypy']
    for tool in linting_tools:
        result = run_command([sys.executable, '-m', 'pip', 'install', tool])
        if not result['success']:
            print(f"Warning: Could not install {tool}")
    
    # Run flake8 (style checking)
    print("\nRunning flake8...")
    result = run_command([
        sys.executable, '-m', 'flake8', 
        'libs/', 'services/', 'tests/',
        '--max-line-length=100',
        '--ignore=E501,W503,E203',
        '--exclude=__pycache__,*.pyc,.git,build,dist'
    ])
    results['flake8'] = result
    print(f"Flake8 result: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
    
    # Run black (code formatting check)
    print("\nRunning black...")
    result = run_command([
        sys.executable, '-m', 'black', 
        '--check', '--diff', 
        'libs/', 'services/', 'tests/'
    ])
    results['black'] = result
    print(f"Black result: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
    
    # Run isort (import sorting check)
    print("\nRunning isort...")
    result = run_command([
        sys.executable, '-m', 'isort',
        '--check-only', '--diff',
        'libs/', 'services/', 'tests/'
    ])
    results['isort'] = result
    print(f"Isort result: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
    
    return results


def run_unit_tests():
    """Run unit tests with coverage."""
    print("\n" + "="*50)
    print("RUNNING UNIT TESTS")
    print("="*50)
    
    result = run_command([
        sys.executable, '-m', 'pytest',
        'tests/unit/',
        '-v',
        '--tb=short',
        '--cov=libs',
        '--cov=services', 
        '--cov-report=term-missing',
        '--cov-report=html:tests/coverage_html',
        '--cov-report=xml:tests/coverage.xml',
        '--junitxml=tests/junit_unit.xml',
        '-m', 'not slow'
    ])
    
    print(f"Unit tests result: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
    return result


def run_integration_tests():
    """Run integration tests."""
    print("\n" + "="*50)
    print("RUNNING INTEGRATION TESTS")
    print("="*50)
    
    result = run_command([
        sys.executable, '-m', 'pytest',
        'tests/integration/',
        '-v',
        '--tb=short',
        '--junitxml=tests/junit_integration.xml',
        '-m', 'not slow'
    ])
    
    print(f"Integration tests result: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
    return result


def run_performance_tests():
    """Run performance tests."""
    print("\n" + "="*50)
    print("RUNNING PERFORMANCE TESTS")
    print("="*50)
    
    result = run_command([
        sys.executable, '-m', 'pytest',
        'tests/performance/',
        '-v',
        '--tb=short',
        '--benchmark-only',
        '--benchmark-sort=mean',
        '--benchmark-columns=min,max,mean,stddev,median,ops,rounds',
        '--junitxml=tests/junit_performance.xml'
    ])
    
    print(f"Performance tests result: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
    return result


def run_specific_tests(test_path: str, markers: List[str] = None):
    """Run specific tests with optional markers."""
    print(f"\n" + "="*50)
    print(f"RUNNING SPECIFIC TESTS: {test_path}")
    print("="*50)
    
    cmd = [
        sys.executable, '-m', 'pytest',
        test_path,
        '-v',
        '--tb=short'
    ]
    
    if markers:
        for marker in markers:
            cmd.extend(['-m', marker])
    
    result = run_command(cmd)
    print(f"Specific tests result: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
    return result


def generate_test_report(results: Dict[str, Any]) -> str:
    """Generate comprehensive test report."""
    report_lines = [
        "# Risk Management Platform - Test Execution Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Environment: {os.getenv('ENVIRONMENT', 'unknown')}",
        "",
        "## Summary",
        ""
    ]
    
    total_suites = len(results)
    passed_suites = sum(1 for result in results.values() if result.get('success', False))
    success_rate = (passed_suites / total_suites * 100) if total_suites > 0 else 0
    
    report_lines.extend([
        f"- **Total Test Suites**: {total_suites}",
        f"- **Passed Suites**: {passed_suites}",
        f"- **Failed Suites**: {total_suites - passed_suites}",
        f"- **Success Rate**: {success_rate:.1f}%",
        f"- **Overall Status**: {'✅ PASSED' if passed_suites == total_suites else '❌ FAILED'}",
        ""
    ])
    
    # Add individual test suite results
    for suite_name, result in results.items():
        status = "✅ PASSED" if result.get('success', False) else "❌ FAILED"
        report_lines.extend([
            f"## {suite_name.replace('_', ' ').title()}",
            f"**Status**: {status}",
            f"**Exit Code**: {result.get('exit_code', 'Unknown')}",
            ""
        ])
        
        if result.get('stdout'):
            lines = result['stdout'].split('\n')
            # Show last 20 lines of output
            relevant_output = lines[-20:] if len(lines) > 20 else lines
            
            report_lines.extend([
                "### Output (Last 20 lines)",
                "```",
                *relevant_output,
                "```",
                ""
            ])
        
        if result.get('stderr') and result['stderr'].strip():
            report_lines.extend([
                "### Errors",
                "```",
                result['stderr'],
                "```",
                ""
            ])
    
    return '\n'.join(report_lines)


def create_test_directories():
    """Create necessary test directories."""
    test_dirs = [
        'tests/unit',
        'tests/integration', 
        'tests/performance',
        'tests/coverage_html',
        'tests/reports'
    ]
    
    for test_dir in test_dirs:
        Path(test_dir).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files
        init_file = Path(test_dir) / '__init__.py'
        if not init_file.exists() and 'coverage' not in test_dir and 'reports' not in test_dir:
            init_file.write_text('"""Test package."""\n')


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Risk Management Platform Test Runner')
    parser.add_argument('--test-type', 
                       choices=['all', 'unit', 'integration', 'performance', 'lint', 'specific'],
                       default='all',
                       help='Type of tests to run')
    parser.add_argument('--test-path', 
                       help='Specific test path (for --test-type specific)')
    parser.add_argument('--markers',
                       nargs='*',
                       help='Pytest markers to filter tests')
    parser.add_argument('--install-deps',
                       action='store_true',
                       help='Install test dependencies before running')
    parser.add_argument('--skip-lint',
                       action='store_true', 
                       help='Skip linting checks')
    parser.add_argument('--output-report',
                       help='Output file for test report')
    parser.add_argument('--parallel',
                       action='store_true',
                       help='Run tests in parallel using pytest-xdist')
    
    args = parser.parse_args()
    
    print("Risk Management Platform - Test Runner")
    print("="*50)
    
    # Create test directories
    create_test_directories()
    
    # Install dependencies if requested
    if args.install_deps:
        install_test_dependencies()
    
    # Track all results
    all_results = {}
    start_time = time.time()
    
    try:
        # Always run security verification first for comprehensive test runs
        if args.test_type == 'all':
            all_results['security_verification'] = run_security_verification()
        
        if args.test_type in ['all', 'lint'] and not args.skip_lint:
            lint_results = run_linting()
            all_results.update(lint_results)
        
        if args.test_type in ['all', 'unit']:
            all_results['unit_tests'] = run_unit_tests()
        
        if args.test_type in ['all', 'integration']:
            all_results['integration_tests'] = run_integration_tests()
        
        if args.test_type in ['all', 'performance']:
            all_results['performance_tests'] = run_performance_tests()
        
        if args.test_type == 'specific' and args.test_path:
            all_results['specific_tests'] = run_specific_tests(args.test_path, args.markers)
        
    except KeyboardInterrupt:
        print("\n\n❌ Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test execution failed with error: {e}")
        sys.exit(1)
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    # Generate and display report
    report = generate_test_report(all_results)
    print("\n" + "="*50)
    print("TEST EXECUTION REPORT")
    print("="*50)
    print(report)
    print(f"\nTotal execution time: {execution_time:.2f} seconds")
    
    # Save report if requested
    if args.output_report:
        report_file = Path(args.output_report)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(report)
        print(f"\nReport saved to: {report_file}")
    
    # Exit with appropriate code
    passed_suites = sum(1 for result in all_results.values() if result.get('success', False))
    total_suites = len(all_results)
    
    if passed_suites == total_suites and total_suites > 0:
        print("\n✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print(f"\n❌ SOME TESTS FAILED ({passed_suites}/{total_suites} passed)")
        sys.exit(1)


if __name__ == "__main__":
    main()