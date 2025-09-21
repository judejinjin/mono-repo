"""
API-triggered DAG for on-demand risk calculations.
This DAG demonstrates how to create a DAG that can be triggered via Airflow REST API
with custom parameters and configuration.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from airflow.utils.trigger_rule import TriggerRule
from config import get_config
import json

# DAG configuration
config = get_config()
default_args = {
    'owner': 'risk-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'max_active_runs': 3,  # Allow multiple concurrent runs
}

dag = DAG(
    'api_triggered_risk_analysis',
    default_args=default_args,
    description='On-demand risk analysis triggered via API',
    schedule_interval=None,  # No schedule - API triggered only
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['risk', 'api', 'on-demand'],
    params={
        # Default parameters that can be overridden via API
        "portfolio_id": "default",
        "analysis_type": "full",
        "risk_horizon": 1,
        "confidence_level": 0.95,
        "include_stress_test": True,
        "notification_email": None
    }
)

def validate_api_params(**context):
    """Validate parameters passed via API trigger."""
    import sys
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Get parameters from DAG run configuration
    dag_run = context.get('dag_run')
    conf = dag_run.conf if dag_run else {}
    params = context['params']
    
    # Merge API parameters with defaults
    portfolio_id = conf.get('portfolio_id', params['portfolio_id'])
    analysis_type = conf.get('analysis_type', params['analysis_type'])
    risk_horizon = conf.get('risk_horizon', params['risk_horizon'])
    confidence_level = conf.get('confidence_level', params['confidence_level'])
    
    print(f"API Trigger Parameters:")
    print(f"  Portfolio ID: {portfolio_id}")
    print(f"  Analysis Type: {analysis_type}")
    print(f"  Risk Horizon: {risk_horizon} days")
    print(f"  Confidence Level: {confidence_level}")
    
    # Validation logic
    valid_analysis_types = ['full', 'var_only', 'stress_test', 'attribution']
    if analysis_type not in valid_analysis_types:
        raise ValueError(f"Invalid analysis_type: {analysis_type}. Must be one of {valid_analysis_types}")
    
    if not isinstance(risk_horizon, int) or risk_horizon < 1 or risk_horizon > 250:
        raise ValueError(f"Invalid risk_horizon: {risk_horizon}. Must be integer between 1 and 250")
    
    if not isinstance(confidence_level, (int, float)) or confidence_level <= 0 or confidence_level >= 1:
        raise ValueError(f"Invalid confidence_level: {confidence_level}. Must be between 0 and 1")
    
    # Store validated parameters for downstream tasks
    context['task_instance'].xcom_push(key='validated_params', value={
        'portfolio_id': portfolio_id,
        'analysis_type': analysis_type,
        'risk_horizon': risk_horizon,
        'confidence_level': confidence_level,
        'include_stress_test': conf.get('include_stress_test', params['include_stress_test']),
        'notification_email': conf.get('notification_email', params['notification_email'])
    })
    
    return "Parameters validated successfully"

def fetch_portfolio_data(**context):
    """Fetch portfolio data based on API parameters."""
    import sys
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from libs.business.risk_management import PortfolioManager
    
    # Get validated parameters
    ti = context['task_instance']
    params = ti.xcom_pull(key='validated_params', task_ids='validate_parameters')
    
    portfolio_id = params['portfolio_id']
    
    print(f"Fetching data for portfolio: {portfolio_id}")
    
    portfolio_manager = PortfolioManager()
    portfolio_data = portfolio_manager.get_portfolio_positions(portfolio_id)
    
    if not portfolio_data:
        raise ValueError(f"No data found for portfolio: {portfolio_id}")
    
    print(f"Found {len(portfolio_data)} positions in portfolio")
    
    # Store portfolio data for downstream tasks
    ti.xcom_push(key='portfolio_data', value=portfolio_data)
    
    return f"Successfully fetched data for portfolio {portfolio_id}"

def calculate_risk_metrics(**context):
    """Calculate risk metrics based on API parameters."""
    import sys
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from libs.business.risk_management import RiskCalculator
    
    # Get parameters and data from upstream tasks
    ti = context['task_instance']
    params = ti.xcom_pull(key='validated_params', task_ids='validate_parameters')
    portfolio_data = ti.xcom_pull(key='portfolio_data', task_ids='fetch_portfolio_data')
    
    analysis_type = params['analysis_type']
    risk_horizon = params['risk_horizon']
    confidence_level = params['confidence_level']
    
    print(f"Calculating {analysis_type} risk metrics...")
    
    risk_calculator = RiskCalculator()
    
    results = {}
    
    if analysis_type in ['full', 'var_only']:
        # Calculate VaR
        var_result = risk_calculator.calculate_var(
            portfolio_data, 
            horizon=risk_horizon, 
            confidence=confidence_level
        )
        results['var'] = var_result
        print(f"VaR ({confidence_level*100}%, {risk_horizon}d): ${var_result:,.2f}")
    
    if analysis_type in ['full', 'stress_test'] and params['include_stress_test']:
        # Calculate stress test scenarios
        stress_results = risk_calculator.stress_test_portfolio(portfolio_data)
        results['stress_test'] = stress_results
        print(f"Stress test completed: {len(stress_results)} scenarios")
    
    if analysis_type in ['full', 'attribution']:
        # Calculate risk attribution
        attribution = risk_calculator.calculate_risk_attribution(portfolio_data)
        results['attribution'] = attribution
        print(f"Risk attribution calculated for {len(attribution)} components")
    
    # Store results
    ti.xcom_push(key='risk_results', value=results)
    
    return f"Risk calculation completed: {analysis_type}"

def generate_report(**context):
    """Generate and optionally email risk report."""
    import sys
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from libs.business.analytics import ReportGenerator
    
    # Get data from upstream tasks
    ti = context['task_instance']
    params = ti.xcom_pull(key='validated_params', task_ids='validate_parameters')
    results = ti.xcom_pull(key='risk_results', task_ids='calculate_risk_metrics')
    
    portfolio_id = params['portfolio_id']
    notification_email = params['notification_email']
    
    print(f"Generating report for portfolio: {portfolio_id}")
    
    report_generator = ReportGenerator()
    
    # Generate report
    report_data = {
        'portfolio_id': portfolio_id,
        'analysis_type': params['analysis_type'],
        'timestamp': datetime.now().isoformat(),
        'parameters': params,
        'results': results
    }
    
    report_path = report_generator.generate_risk_report(report_data)
    print(f"Report generated: {report_path}")
    
    # Send email notification if requested
    if notification_email:
        try:
            from libs.cloud.notifications import EmailNotifier
            
            notifier = EmailNotifier()
            notifier.send_risk_report(
                to_email=notification_email,
                portfolio_id=portfolio_id,
                report_path=report_path,
                results_summary=results
            )
            print(f"Report sent to: {notification_email}")
        except Exception as e:
            print(f"Failed to send email notification: {e}")
            # Don't fail the task for email issues
    
    return f"Report generated and notification sent"

def cleanup_temp_data(**context):
    """Clean up temporary data and cache."""
    print("Cleaning up temporary data...")
    
    # Clean up any temporary files or cache
    # This runs regardless of upstream task status
    
    return "Cleanup completed"

# Define tasks
validate_task = PythonOperator(
    task_id='validate_parameters',
    python_callable=validate_api_params,
    dag=dag
)

fetch_data_task = PythonOperator(
    task_id='fetch_portfolio_data',
    python_callable=fetch_portfolio_data,
    dag=dag
)

risk_calculation_task = PythonOperator(
    task_id='calculate_risk_metrics',
    python_callable=calculate_risk_metrics,
    dag=dag
)

report_task = PythonOperator(
    task_id='generate_report',
    python_callable=generate_report,
    dag=dag
)

cleanup_task = PythonOperator(
    task_id='cleanup_temp_data',
    python_callable=cleanup_temp_data,
    trigger_rule=TriggerRule.ALL_DONE,  # Run regardless of upstream success/failure
    dag=dag
)

# Define task dependencies
validate_task >> fetch_data_task >> risk_calculation_task >> report_task >> cleanup_task
