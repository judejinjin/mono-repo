#!/usr/bin/env python3
"""
Risk API Client Usage Examples
Demonstrates how to use the Risk API Client in different scenarios.
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from risk_api_client import RiskAPIClient, RiskMetrics


def example_basic_usage():
    """Basic usage example."""
    print("📊 Basic Risk API Client Usage")
    print("-" * 40)
    
    # Initialize client for different environments
    environments = {
        "local": "http://localhost:8000",
        "dev": "http://internal-alb.genai.corporate/api",
        "corporate": "http://internal-alb.genai.corporate/api"
    }
    
    # Use corporate environment for production
    client = RiskAPIClient(environments["corporate"])
    
    try:
        # Health check
        health = client.health_check()
        print(f"✅ API Health: {health['status']}")
        
        # Get service information
        info = client.get_service_info()
        print(f"🔧 Service: {info['service']} v{info['version']}")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Make sure the Risk API service is running")


def example_risk_calculations():
    """Risk calculation examples."""
    print("\n🧮 Risk Calculations Example")
    print("-" * 40)
    
    client = RiskAPIClient("http://internal-alb.genai.corporate/api")
    
    try:
        # List available portfolios
        portfolios = client.list_portfolios()
        print(f"📁 Found {len(portfolios)} portfolios")
        
        # Calculate risk for each portfolio
        for portfolio in portfolios[:3]:  # Limit to first 3
            print(f"\n💼 Portfolio: {portfolio.name} ({portfolio.id})")
            
            try:
                # Calculate current risk metrics
                risk = client.calculate_risk_metrics(portfolio.id)
                
                print(f"   📈 Risk Metrics:")
                print(f"      VaR 95%: ${risk.var_95:,.2f}")
                print(f"      VaR 99%: ${risk.var_99:,.2f}")
                print(f"      Expected Shortfall: ${risk.expected_shortfall:,.2f}")
                print(f"      Volatility: {risk.volatility:.4f}")
                print(f"      Sharpe Ratio: {risk.sharpe_ratio:.4f}")
                print(f"      Calculated: {risk.calculated_at}")
                
                # Get cached risk metrics
                cached_risk = client.get_portfolio_risk(portfolio.id)
                print(f"   🗃️ Cached risk data available: {cached_risk.calculated_at}")
                
            except Exception as e:
                print(f"   ⚠️ Risk calculation failed: {e}")
                
    except Exception as e:
        print(f"❌ Failed to access portfolios: {e}")


def example_market_data():
    """Market data processing examples."""
    print("\n📊 Market Data Processing Example")
    print("-" * 40)
    
    client = RiskAPIClient("http://internal-alb.genai.corporate/api")
    
    try:
        # Get today's date
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Check market data status for yesterday
        status = client.get_market_data_status(yesterday.isoformat())
        print(f"📅 Market data status for {yesterday}: {status.get('status', 'Unknown')}")
        
        # Process market data for specific asset classes
        asset_classes = ["equities", "bonds", "commodities"]
        result = client.process_market_data(
            date_str=today.isoformat(),
            asset_classes=asset_classes
        )
        print(f"⚙️ Processing result: {result.get('status', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Market data operations failed: {e}")


def example_reports():
    """Report generation examples."""
    print("\n📋 Report Generation Example")
    print("-" * 40)
    
    client = RiskAPIClient("http://internal-alb.genai.corporate/api")
    
    try:
        # List available report types
        reports = client.list_available_reports()
        print("📊 Available Reports:")
        for report in reports:
            print(f"   - {report['type']}: {report['name']}")
            print(f"     {report['description']}")
        
        # Generate daily risk report
        today = date.today()
        daily_report = client.generate_report(
            report_type="daily_risk",
            start_date=today.isoformat()
        )
        print(f"\n📈 Daily Risk Report Generated:")
        print(f"   Status: {daily_report.get('status', 'Unknown')}")
        
        # Generate performance report for last week
        week_ago = today - timedelta(days=7)
        perf_report = client.generate_report(
            report_type="performance",
            start_date=week_ago.isoformat(),
            end_date=today.isoformat(),
            parameters={"include_benchmarks": True}
        )
        print(f"\n📊 Performance Report Generated:")
        print(f"   Status: {perf_report.get('status', 'Unknown')}")
        print(f"   Period: {week_ago} to {today}")
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")


def example_analytics():
    """Analytics and database examples."""
    print("\n🔬 Analytics & Database Example")  
    print("-" * 40)
    
    client = RiskAPIClient("http://internal-alb.genai.corporate/api")
    
    try:
        # List available databases
        databases = client.list_databases()
        print(f"🗄️ Available Databases: {len(databases)}")
        for db in databases:
            print(f"   - {db.get('name', 'Unknown')}: {db.get('type', 'Unknown')}")
        
        # List Snowflake warehouses
        warehouses = client.list_snowflake_warehouses()
        print(f"\n❄️ Snowflake Warehouses: {len(warehouses)}")
        for wh in warehouses:
            print(f"   - {wh.get('name', 'Unknown')}: {wh.get('size', 'Unknown')}")
        
        # Execute a simple query
        query_result = client.execute_snowflake_query(
            query="SELECT COUNT(*) as total_records FROM portfolio_data LIMIT 10",
            warehouse="COMPUTE_WH"
        )
        print(f"\n🔍 Query Result: {query_result.get('status', 'Unknown')}")
        
        # Get data summary
        summary = client.get_data_summary()
        print(f"\n📈 Data Summary:")
        print(f"   Total Records: {summary.get('total_records', 'N/A')}")
        print(f"   Last Updated: {summary.get('last_updated', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Analytics operations failed: {e}")


def example_configuration():
    """Configuration and system info examples."""
    print("\n⚙️ Configuration Example")
    print("-" * 40)
    
    client = RiskAPIClient("http://internal-alb.genai.corporate/api")
    
    try:
        # Get API configuration
        config = client.get_config()
        print("🔧 API Configuration:")
        for key, value in config.items():
            if not key.startswith('_'):  # Skip private fields
                print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ Configuration access failed: {e}")


def main():
    """Run all examples."""
    print("🚀 Risk API Client - Usage Examples")
    print("=" * 50)
    print("💡 Note: These examples assume the Risk API is running")
    print("   For corporate intranet access, ensure VPN connection is active")
    print()
    
    # Run all examples
    example_basic_usage()
    example_risk_calculations()
    example_market_data()
    example_reports()
    example_analytics()
    example_configuration()
    
    print("\n" + "=" * 50)
    print("🎉 All examples completed!")
    print("\n📚 Usage Tips:")
    print("   1. Modify the base_url for your environment")
    print("   2. Add error handling for production use")
    print("   3. Use environment variables for configuration")
    print("   4. Consider connection pooling for high-frequency calls")
    print("   5. Implement retry logic for network resilience")


if __name__ == "__main__":
    main()
