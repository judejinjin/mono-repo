"""
Dash Application for Risk Management Dashboard
Provides interactive visualizations for risk metrics and portfolio analysis.
"""

import dash
from dash import dcc, html, Input, Output, callback, State
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path
import dash_bootstrap_components as dbc
import flask
from flask import session, request, redirect
from functools import wraps

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from libs.business.analytics import ReportGenerator
from libs.business.risk_management import RiskCalculator
from libs.auth import AuthManager
from libs.monitoring import log_user_action, log_auth_event, request_context
from config import get_config

# Authentication setup
auth_manager = AuthManager()

# Initialize Dash app with Bootstrap theme and custom server
server = flask.Flask(__name__)
server.secret_key = 'your-secret-key-change-in-production'  # Change this in production
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Risk Management Dashboard"

# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

# Flask routes for authentication
@server.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            user = auth_manager.authenticate_user(username, password)
            if user:
                session['user'] = {
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
                log_auth_event('login', user.username, result='success')
                log_user_action('dashboard_login', user.username)
                return redirect('/dashboard')
            else:
                log_auth_event('login_attempt', username, result='failure')
                return flask.render_template_string(LOGIN_TEMPLATE, error="Invalid credentials")
        except Exception as e:
            log_auth_event('login_error', username, result='error', details={'error': str(e)})
            return flask.render_template_string(LOGIN_TEMPLATE, error="Authentication failed")
    
    return flask.render_template_string(LOGIN_TEMPLATE)

@server.route('/logout')
def logout():
    user = session.get('user', {})
    if user:
        log_user_action('dashboard_logout', user.get('username'))
        log_auth_event('logout', user.get('username'), result='success')
    session.pop('user', None)
    return redirect('/login')

@server.route('/dashboard')
@require_auth
def dashboard():
    return app.index()

# Login page template
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Risk Management Dashboard - Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .login-container { max-width: 400px; margin: 100px auto; }
        .card { border: none; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-container">
            <div class="card">
                <div class="card-body p-5">
                    <h2 class="text-center mb-4">Risk Dashboard Login</h2>
                    {% if error %}
                        <div class="alert alert-danger">{{ error }}</div>
                    {% endif %}
                    <form method="post">
                        <div class="mb-3">
                            <label for="username" class="form-label">Username</label>
                            <input type="text" class="form-control" id="username" name="username" required>
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Login</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Check authentication for Dash callbacks
def get_current_user():
    """Get current authenticated user."""
    return session.get('user')

def require_permission(permission: str):
    """Check if current user has required permission."""
    user = get_current_user()
    if not user:
        return False
    
    # Mock permission check - in real implementation, use auth_manager
    role_permissions = {
        'admin': ['portfolio:read', 'portfolio:write', 'risk:read', 'risk:calculate', 'market_data:read', 'reports:generate'],
        'risk_manager': ['portfolio:read', 'risk:read', 'risk:calculate', 'market_data:read', 'reports:generate'],
        'analyst': ['portfolio:read', 'risk:read', 'market_data:read', 'reports:generate'],
        'viewer': ['portfolio:read', 'risk:read', 'market_data:read']
    }
    
    user_role = user.get('role', 'viewer')
    return permission in role_permissions.get(user_role, [])

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

# Function to create layout based on authentication
def create_layout():
    """Create dashboard layout with authentication check."""
    user = get_current_user()
    if not user:
        return html.Div([
            html.H1("Access Denied", className="text-center mt-5"),
            html.P("Please log in to access the Risk Management Dashboard.", className="text-center"),
            html.A("Login", href="/login", className="btn btn-primary")
        ], className="container mt-5")
    
    return html.Div([
        # Header with user info
        dbc.Navbar([
            dbc.NavbarBrand("Risk Management Dashboard", className="ms-2"),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink(f"Welcome, {user.get('first_name', user.get('username'))}", disabled=True)),
                dbc.NavItem(dbc.NavLink("Logout", href="/logout", external_link=True))
            ], className="ms-auto", navbar=True)
        ], color="primary", dark=True, className="mb-4"),
        
        # Main content
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
            ], className="col-md-6"),
            
            html.Div([
                html.H3("Date Range"),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=datetime.now() - timedelta(days=30),
                    end_date=datetime.now(),
                    display_format='YYYY-MM-DD',
                    className="date-picker"
                )
            ], className="col-md-6")
        ], className="row mb-4"),
        
        html.Div([
            html.Div([
                html.H3("Value at Risk (95%)"),
                dcc.Graph(id='var-chart')
            ], className="col-md-6"),
            
            html.Div([
                html.H3("Portfolio Volatility"),
                dcc.Graph(id='volatility-chart')
            ], className="col-md-6")
        ], className="row mb-4"),
        
        html.Div([
            html.Div([
                html.H3("Sharpe Ratio Trends"),
                dcc.Graph(id='sharpe-chart')
            ], className="col-md-12")
        ], className="row mb-4"),
        
        # Risk summary cards
        html.Div([
            html.Div([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Current VaR", className="card-title"),
                        html.H2(id="current-var", className="text-primary"),
                        html.P("95% Confidence Level", className="card-text")
                    ])
                ])
            ], className="col-md-3"),
            
            html.Div([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Volatility", className="card-title"),
                        html.H2(id="current-volatility", className="text-warning"),
                        html.P("Annualized", className="card-text")
                    ])
                ])
            ], className="col-md-3"),
            
            html.Div([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Sharpe Ratio", className="card-title"),
                        html.H2(id="current-sharpe", className="text-success"),
                        html.P("Risk-Adjusted Return", className="card-text")
                    ])
                ])
            ], className="col-md-3"),
            
            html.Div([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Status", className="card-title"),
                        html.H2("Active", className="text-info"),
                        html.P("Portfolio Status", className="card-text")
                    ])
                ])
            ], className="col-md-3")
        ], className="row")
# Set app layout
app.layout = create_layout
    
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

# Callbacks with authentication
@callback(
    Output('var-chart', 'figure'),
    [Input('portfolio-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_var_chart(portfolio, start_date, end_date):
    """Update VaR chart with authentication check."""
    user = get_current_user()
    if not user or not require_permission('risk:read'):
        return go.Figure().add_annotation(text="Access Denied", xref="paper", yref="paper", 
                                        x=0.5, y=0.5, showarrow=False)
    
    with request_context(user_id=user.get('username')):
        log_user_action('view_var_chart', user.get('username'), 
                       details={'portfolio': portfolio, 'date_range': f"{start_date}_{end_date}"})
        
        # Filter data
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
            hovermode='x'
        )
        
        return fig
        return fig

@callback(
    Output('volatility-chart', 'figure'),
    [Input('portfolio-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_volatility_chart(portfolio, start_date, end_date):
    """Update volatility chart with authentication check."""
    user = get_current_user()
    if not user or not require_permission('risk:read'):
        return go.Figure().add_annotation(text="Access Denied", xref="paper", yref="paper", 
                                        x=0.5, y=0.5, showarrow=False)
    
    with request_context(user_id=user.get('username')):
        log_user_action('view_volatility_chart', user.get('username'), 
                       details={'portfolio': portfolio, 'date_range': f"{start_date}_{end_date}"})
        
        # Filter data
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
    """Update Sharpe ratio chart with authentication check."""
    user = get_current_user()
    if not user or not require_permission('risk:read'):
        return go.Figure().add_annotation(text="Access Denied", xref="paper", yref="paper", 
                                        x=0.5, y=0.5, showarrow=False)
    
    with request_context(user_id=user.get('username')):
        log_user_action('view_sharpe_chart', user.get('username'), 
                       details={'portfolio': portfolio, 'date_range': f"{start_date}_{end_date}"})
        
        # Filter data
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
