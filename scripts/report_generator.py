"""
Report generation script for Airflow jobs.
Generates various risk and analytics reports.
"""

import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from libs.business.analytics import ReportGenerator
from libs.cloud import upload_to_s3

logger = logging.getLogger(__name__)


def generate_daily_reports(date: str, risk_report: Dict[str, Any] = None) -> bool:
    """
    Generate all daily reports for given date.
    
    Args:
        date: Date string in YYYY-MM-DD format
        risk_report: Pre-generated risk report data
        
    Returns:
        bool: True if all reports generated successfully
    """
    logger.info(f"Starting report generation for {date}")
    
    try:
        generator = ReportGenerator()
        
        # Generate risk report if not provided
        if risk_report is None:
            risk_report = generator.generate_daily_risk_report(date)
        
        # Generate performance report (weekly)
        if datetime.strptime(date, '%Y-%m-%d').weekday() == 4:  # Friday
            performance_report = generate_weekly_performance_report(date, generator)
        else:
            performance_report = None
        
        # Export reports to various formats
        export_reports_to_json(date, risk_report, performance_report)
        export_reports_to_csv(date, risk_report)
        export_reports_to_pdf(date, risk_report)
        
        # Upload reports to S3
        upload_reports_to_s3(date, risk_report, performance_report)
        
        # Send email notifications
        send_report_notifications(date, risk_report)
        
        logger.info(f"Successfully generated all reports for {date}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to generate reports for {date}: {e}")
        return False


def generate_weekly_performance_report(date: str, generator: ReportGenerator) -> Dict[str, Any]:
    """Generate weekly performance report."""
    from datetime import datetime, timedelta
    
    end_date = datetime.strptime(date, '%Y-%m-%d')
    start_date = end_date - timedelta(days=6)  # 7 days including end date
    
    return generator.generate_performance_report(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )


def export_reports_to_json(date: str, risk_report: Dict, performance_report: Dict = None) -> None:
    """Export reports to JSON format."""
    import tempfile
    
    reports_dir = Path(tempfile.gettempdir()) / 'reports' / date
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Export risk report
    risk_file = reports_dir / 'daily_risk_report.json'
    with open(risk_file, 'w') as f:
        json.dump(risk_report, f, indent=2)
    
    # Export performance report if available
    if performance_report:
        perf_file = reports_dir / 'weekly_performance_report.json'
        with open(perf_file, 'w') as f:
            json.dump(performance_report, f, indent=2)
    
    logger.info(f"Exported reports to JSON in {reports_dir}")


def export_reports_to_csv(date: str, risk_report: Dict) -> None:
    """Export reports to CSV format."""
    import pandas as pd
    import tempfile
    
    reports_dir = Path(tempfile.gettempdir()) / 'reports' / date
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Export portfolio summary
    portfolio_data = risk_report.get('portfolio_summary', {})
    if portfolio_data:
        df = pd.DataFrame([portfolio_data])
        csv_file = reports_dir / 'portfolio_summary.csv'
        df.to_csv(csv_file, index=False)
    
    # Export risk metrics
    risk_metrics = risk_report.get('risk_metrics', {})
    if risk_metrics:
        df = pd.DataFrame([risk_metrics])
        csv_file = reports_dir / 'risk_metrics.csv'
        df.to_csv(csv_file, index=False)
    
    # Export top risks
    top_risks = risk_report.get('top_risks', [])
    if top_risks:
        df = pd.DataFrame(top_risks)
        csv_file = reports_dir / 'top_risks.csv'
        df.to_csv(csv_file, index=False)
    
    logger.info(f"Exported reports to CSV in {reports_dir}")


def export_reports_to_pdf(date: str, risk_report: Dict) -> None:
    """Export reports to PDF format."""
    # Mock implementation - in real scenario would use libraries like reportlab
    import tempfile
    
    reports_dir = Path(tempfile.gettempdir()) / 'reports' / date
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_file = reports_dir / 'daily_risk_report.pdf'
    
    # Create mock PDF content
    pdf_content = f"""
    Daily Risk Report - {date}
    
    Portfolio Summary:
    {json.dumps(risk_report.get('portfolio_summary', {}), indent=2)}
    
    Risk Metrics:
    {json.dumps(risk_report.get('risk_metrics', {}), indent=2)}
    
    Top Risks:
    {json.dumps(risk_report.get('top_risks', []), indent=2)}
    """
    
    with open(pdf_file, 'w') as f:
        f.write(pdf_content)
    
    logger.info(f"Exported report to PDF: {pdf_file}")


def upload_reports_to_s3(date: str, risk_report: Dict, performance_report: Dict = None) -> None:
    """Upload generated reports to S3."""
    import tempfile
    
    reports_dir = Path(tempfile.gettempdir()) / 'reports' / date
    
    # Upload all report files
    for report_file in reports_dir.glob('*'):
        s3_key = f"reports/{date}/{report_file.name}"
        success = upload_to_s3(str(report_file), s3_key)
        
        if success:
            logger.info(f"Uploaded report to S3: {s3_key}")
        else:
            logger.error(f"Failed to upload report: {report_file.name}")


def send_report_notifications(date: str, risk_report: Dict) -> None:
    """Send email notifications for generated reports."""
    # Mock implementation - in real scenario would integrate with email service
    
    risk_metrics = risk_report.get('risk_metrics', {})
    top_risks = risk_report.get('top_risks', [])
    
    # Check for alert conditions
    alerts = []
    
    # Check for portfolios above risk limit
    portfolios_above_limit = risk_metrics.get('portfolios_above_risk_limit', 0)
    if portfolios_above_limit > 0:
        alerts.append(f"{portfolios_above_limit} portfolios above risk limit")
    
    # Check for high risk exposures
    for risk in top_risks:
        if risk.get('impact') == 'High' and risk.get('exposure', 0) > 0.3:
            alerts.append(f"High {risk['risk_factor']} exposure: {risk['exposure']:.1%}")
    
    if alerts:
        logger.warning(f"Risk alerts for {date}: {'; '.join(alerts)}")
        # In real implementation, would send email to risk managers
    
    logger.info(f"Processed report notifications for {date}")


def generate_adhoc_report(report_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Generate ad-hoc reports based on type and parameters."""
    generator = ReportGenerator()
    
    if report_type == 'risk_summary':
        start_date = parameters.get('start_date')
        end_date = parameters.get('end_date')
        return generator.generate_performance_report(start_date, end_date)
    
    elif report_type == 'portfolio_analysis':
        portfolio_id = parameters.get('portfolio_id')
        # Mock implementation
        return {
            'portfolio_id': portfolio_id,
            'analysis_type': 'detailed',
            'generated_at': datetime.utcnow().isoformat()
        }
    
    else:
        raise ValueError(f"Unknown report type: {report_type}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate daily reports')
    parser.add_argument('--date', required=True, help='Date in YYYY-MM-DD format')
    parser.add_argument('--type', choices=['daily', 'weekly', 'adhoc'], default='daily',
                        help='Report type to generate')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if args.type == 'daily':
        success = generate_daily_reports(args.date)
    elif args.type == 'weekly':
        generator = ReportGenerator()
        report = generate_weekly_performance_report(args.date, generator)
        success = report is not None
    else:
        logger.error(f"Unsupported report type: {args.type}")
        success = False
    
    sys.exit(0 if success else 1)
