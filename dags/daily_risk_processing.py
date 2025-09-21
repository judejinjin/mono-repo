"""
Daily risk processing DAG for Airflow.
Processes market data and calculates risk metrics daily.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from config import get_config

# DAG configuration
config = get_config()
default_args = config.get('airflow', {}).get('default_args', {})

dag = DAG(
    'daily_risk_processing',
    default_args=default_args,
    description='Daily risk processing and calculation',
    schedule_interval='0 6 * * 1-5',  # 6 AM on weekdays
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['risk', 'daily']
)


def process_market_data(**context):
    """Process daily market data."""
    import sys
    import os
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from libs.business.risk_management import MarketDataProcessor
    from scripts.market_data_processor import process_daily_market_data
    
    execution_date = context['ds']
    processor = MarketDataProcessor()
    
    success = processor.process_daily_prices(execution_date)
    if not success:
        raise Exception(f"Failed to process market data for {execution_date}")
    
    # Call additional processing script
    process_daily_market_data(execution_date)


def calculate_portfolio_risks(**context):
    """Calculate risk metrics for all portfolios."""
    import sys
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from libs.business.risk_management import RiskCalculator
    from libs.db import execute_query
    
    execution_date = context['ds']
    calculator = RiskCalculator()
    
    # Get all active portfolios
    portfolios = execute_query('riskdb', 'SELECT portfolio_id FROM portfolios WHERE active = true')
    
    for portfolio in portfolios:
        portfolio_id = portfolio['portfolio_id']
        risk_metrics = calculator.calculate_portfolio_risk(portfolio_id)
        
        # Store risk metrics in database
        # Implementation would go here
        print(f"Calculated risks for portfolio {portfolio_id}: {risk_metrics}")


def generate_risk_reports(**context):
    """Generate daily risk reports."""
    import sys
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from libs.business.analytics import ReportGenerator
    from scripts.report_generator import generate_daily_reports
    
    execution_date = context['ds']
    generator = ReportGenerator()
    
    # Generate risk report
    report = generator.generate_daily_risk_report(execution_date)
    
    # Call additional report generation script
    generate_daily_reports(execution_date, report)


# Define tasks
market_data_task = PythonOperator(
    task_id='process_market_data',
    python_callable=process_market_data,
    dag=dag
)

risk_calculation_task = PythonOperator(
    task_id='calculate_portfolio_risks',
    python_callable=calculate_portfolio_risks,
    dag=dag
)

report_generation_task = PythonOperator(
    task_id='generate_risk_reports',
    python_callable=generate_risk_reports,
    dag=dag
)

data_quality_check = BashOperator(
    task_id='data_quality_check',
    bash_command='python scripts/data_quality_check.py --date {{ ds }}',
    dag=dag
)

# Define task dependencies
market_data_task >> data_quality_check >> risk_calculation_task >> report_generation_task
