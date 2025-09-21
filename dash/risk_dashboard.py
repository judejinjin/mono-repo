"""
Dash Application for Risk Management Dashboard
Provides interactive visualizations for risk metrics and portfolio analysis.
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from libs.business.analytics import ReportGenerator
from libs.business.risk_management import RiskCalculator
from config import get_config

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Risk Management Dashboard"

# Get configuration
config = get_config()
dash_config = config.get('dash', {})

# Sample data generation
def generate_sample_data():
    """Generate sample data for dashboard."""
    dates = pd.date_range(start='2025-01-01', end='2025-09-01', freq='D')
    
    # Portfolio risk data
    portfolios = ['EQUITY_GROWTH', 'FIXED_INCOME', 'BALANCED', 'EMERGING_MARKETS']
    
    risk_data = []
    for portfolio in portfolios:
        for date in dates:
            risk_data.append({
                'date': date,
                'portfolio': portfolio,
                'var_95': -0.02 - (hash(f"{portfolio}{date}") % 100) / 10000,
                'volatility': 0.10 + (hash(f"{portfolio}{date}") % 50) / 1000,
                'sharpe_ratio': 0.5 + (hash(f"{portfolio}{date}") % 100) / 200
            })
    
    return pd.DataFrame(risk_data)

# Generate sample data
df_risk = generate_sample_data()

# Layout
app.layout = html.Div([
    html.Div([
        html.H1("Risk Management Dashboard", className="header-title"),
        html.P("Real-time portfolio risk monitoring and analysis", className="header-subtitle")
    ], className="header"),
    
    html.Div([
        html.Div([
            html.H3("Portfolio Selection"),
            dcc.Dropdown(
                id='portfolio-dropdown',
                options=[
                    {'label': 'Equity Growth Portfolio', 'value': 'EQUITY_GROWTH'},
                    {'label': 'Fixed Income Portfolio', 'value': 'FIXED_INCOME'},
                    {'label': 'Balanced Portfolio', 'value': 'BALANCED'},
                    {'label': 'Emerging Markets Portfolio', 'value': 'EMERGING_MARKETS'}
                ],
                value='EQUITY_GROWTH',
                className="dropdown"
            )
        ], className="control-panel"),
        
        html.Div([
            html.H3("Date Range"),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=datetime.now() - timedelta(days=30),
                end_date=datetime.now(),
                display_format='YYYY-MM-DD',
                className="date-picker"
            )
        ], className="control-panel")
    ], className="controls-row"),
    
    html.Div([
        html.Div([
            html.H3("Value at Risk (95%)"),
            dcc.Graph(id='var-chart')
        ], className="chart-container"),
        
        html.Div([
            html.H3("Portfolio Volatility"),
            dcc.Graph(id='volatility-chart')
        ], className="chart-container")
    ], className="charts-row"),
    
    html.Div([
        html.Div([
            html.H3("Sharpe Ratio"),
            dcc.Graph(id='sharpe-chart')
        ], className="chart-container"),
        
        html.Div([
            html.H3("Risk Summary"),
            html.Div(id='risk-summary-table')
        ], className="chart-container")
    ], className="charts-row"),
    
    html.Div([
        html.H3("Portfolio Comparison"),
        dcc.Graph(id='comparison-chart')
    ], className="full-width-chart")
    
], className="dashboard-container")

# Callbacks
@callback(
    Output('var-chart', 'figure'),
    [Input('portfolio-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_var_chart(portfolio, start_date, end_date):
    """Update VaR chart based on selected portfolio and date range."""
    filtered_df = df_risk[
        (df_risk['portfolio'] == portfolio) &
        (df_risk['date'] >= start_date) &
        (df_risk['date'] <= end_date)
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered_df['date'],
        y=filtered_df['var_95'],
        mode='lines+markers',
        name='VaR 95%',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title=f"Value at Risk - {portfolio}",
        xaxis_title="Date",
        yaxis_title="VaR (95%)",
        yaxis_tickformat='.2%',
        template="plotly_white"
    )
    
    return fig

@callback(
    Output('volatility-chart', 'figure'),
    [Input('portfolio-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_volatility_chart(portfolio, start_date, end_date):
    """Update volatility chart."""
    filtered_df = df_risk[
        (df_risk['portfolio'] == portfolio) &
        (df_risk['date'] >= start_date) &
        (df_risk['date'] <= end_date)
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered_df['date'],
        y=filtered_df['volatility'],
        mode='lines+markers',
        name='Volatility',
        line=dict(color='blue', width=2)
    ))
    
    fig.update_layout(
        title=f"Portfolio Volatility - {portfolio}",
        xaxis_title="Date",
        yaxis_title="Volatility",
        yaxis_tickformat='.2%',
        template="plotly_white"
    )
    
    return fig

@callback(
    Output('sharpe-chart', 'figure'),
    [Input('portfolio-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_sharpe_chart(portfolio, start_date, end_date):
    """Update Sharpe ratio chart."""
    filtered_df = df_risk[
        (df_risk['portfolio'] == portfolio) &
        (df_risk['date'] >= start_date) &
        (df_risk['date'] <= end_date)
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered_df['date'],
        y=filtered_df['sharpe_ratio'],
        mode='lines+markers',
        name='Sharpe Ratio',
        line=dict(color='green', width=2)
    ))
    
    fig.update_layout(
        title=f"Sharpe Ratio - {portfolio}",
        xaxis_title="Date",
        yaxis_title="Sharpe Ratio",
        template="plotly_white"
    )
    
    return fig

@callback(
    Output('comparison-chart', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_comparison_chart(start_date, end_date):
    """Update portfolio comparison chart."""
    filtered_df = df_risk[
        (df_risk['date'] >= start_date) &
        (df_risk['date'] <= end_date)
    ]
    
    # Calculate average metrics by portfolio
    avg_metrics = filtered_df.groupby('portfolio').agg({
        'var_95': 'mean',
        'volatility': 'mean',
        'sharpe_ratio': 'mean'
    }).reset_index()
    
    fig = go.Figure()
    
    # Add VaR bars
    fig.add_trace(go.Bar(
        name='VaR 95%',
        x=avg_metrics['portfolio'],
        y=avg_metrics['var_95'],
        yaxis='y',
        offsetgroup=1
    ))
    
    # Add volatility bars (on secondary y-axis)
    fig.add_trace(go.Bar(
        name='Volatility',
        x=avg_metrics['portfolio'],
        y=avg_metrics['volatility'],
        yaxis='y2',
        offsetgroup=2
    ))
    
    fig.update_layout(
        title="Portfolio Risk Comparison",
        xaxis_title="Portfolio",
        yaxis=dict(
            title="VaR 95%",
            tickformat='.2%',
            side="left"
        ),
        yaxis2=dict(
            title="Volatility",
            tickformat='.2%',
            overlaying="y",
            side="right"
        ),
        template="plotly_white",
        barmode='group'
    )
    
    return fig

@callback(
    Output('risk-summary-table', 'children'),
    [Input('portfolio-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_risk_summary(portfolio, start_date, end_date):
    """Update risk summary table."""
    filtered_df = df_risk[
        (df_risk['portfolio'] == portfolio) &
        (df_risk['date'] >= start_date) &
        (df_risk['date'] <= end_date)
    ]
    
    # Calculate summary statistics
    summary_stats = {
        'Average VaR 95%': f"{filtered_df['var_95'].mean():.2%}",
        'Max VaR 95%': f"{filtered_df['var_95'].min():.2%}",  # Min because VaR is negative
        'Average Volatility': f"{filtered_df['volatility'].mean():.2%}",
        'Max Volatility': f"{filtered_df['volatility'].max():.2%}",
        'Average Sharpe Ratio': f"{filtered_df['sharpe_ratio'].mean():.2f}",
        'Max Sharpe Ratio': f"{filtered_df['sharpe_ratio'].max():.2f}"
    }
    
    table_rows = []
    for metric, value in summary_stats.items():
        table_rows.append(
            html.Tr([
                html.Td(metric, className="metric-name"),
                html.Td(value, className="metric-value")
            ])
        )
    
    return html.Table([
        html.Thead([
            html.Tr([
                html.Th("Metric"),
                html.Th("Value")
            ])
        ]),
        html.Tbody(table_rows)
    ], className="summary-table")

# CSS Styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .dashboard-container {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            .header {
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 5px;
            }
            .header-title {
                margin: 0;
                font-size: 2.5em;
            }
            .header-subtitle {
                margin: 10px 0 0 0;
                font-size: 1.2em;
                opacity: 0.8;
            }
            .controls-row {
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
            }
            .control-panel {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                flex: 1;
            }
            .charts-row {
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
            }
            .chart-container {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                flex: 1;
            }
            .full-width-chart {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 20px;
            }
            .summary-table {
                width: 100%;
                border-collapse: collapse;
            }
            .summary-table th, .summary-table td {
                border: 1px solid #dee2e6;
                padding: 8px;
                text-align: left;
            }
            .summary-table th {
                background-color: #f8f9fa;
                font-weight: bold;
            }
            .metric-value {
                font-weight: bold;
                color: #2c3e50;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server(
        debug=dash_config.get('debug', False),
        host=dash_config.get('host', '0.0.0.0'),
        port=dash_config.get('port', 8050)
    )
