"""
Data visualization functions for Provider Data Quality Analytics
"""
import pandas as pd
import streamlit as st
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly not available. Using basic Streamlit charts.")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

def create_quality_score_gauge(score: float) -> any:
    """Create a gauge chart for overall data quality score"""
    if PLOTLY_AVAILABLE:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Data Quality Score"},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=300)
        return fig
    else:
        # Fallback to simple metric
        return None

def create_state_issues_map(df: pd.DataFrame) -> any:
    """Create a choropleth map showing issues by state"""
    if not PLOTLY_AVAILABLE or 'address_state' not in df.columns:
        return None
    
    # Aggregate issues by state
    issue_cols = ['license_expired', 'npi_missing', 'phone_issue', 'duplicate_suspect', 'license_state_mismatch']
    existing_cols = [col for col in issue_cols if col in df.columns]
    
    if not existing_cols:
        return None
        
    state_data = df.groupby('address_state').agg({
        **{col: 'sum' for col in existing_cols},
        'provider_id': 'count'
    }).reset_index()
    
    state_data['total_issues'] = state_data[existing_cols].sum(axis=1)
    state_data['issue_rate'] = state_data['total_issues'] / state_data['provider_id'] * 100
    
    fig = px.choropleth(
        state_data,
        locations='address_state',
        color='issue_rate',
        hover_name='address_state',
        hover_data=['total_issues', 'provider_id'],
        locationmode='USA-states',
        color_continuous_scale='Reds',
        title='Data Quality Issues by State (%)'
    )
    
    fig.update_layout(geo_scope='usa', height=500)
    return fig

def create_issues_by_specialty_chart(df: pd.DataFrame) -> any:
    """Create a bar chart showing issues by specialty"""
    if 'specialty' not in df.columns:
        return None
        
    issue_cols = ['license_expired', 'npi_missing', 'phone_issue', 'duplicate_suspect', 'license_state_mismatch']
    existing_cols = [col for col in issue_cols if col in df.columns]
    
    if not existing_cols:
        return None
    
    specialty_data = df.groupby('specialty').agg({
        **{col: 'sum' for col in existing_cols},
        'provider_id': 'count'
    }).reset_index()
    
    specialty_data['total_issues'] = specialty_data[existing_cols].sum(axis=1)
    specialty_data = specialty_data.sort_values('total_issues', ascending=True)
    
    if PLOTLY_AVAILABLE:
        fig = px.bar(
            specialty_data.tail(10),  # Top 10 specialties with most issues
            x='total_issues',
            y='specialty',
            orientation='h',
            title='Top 10 Specialties with Most Data Quality Issues',
            labels={'total_issues': 'Number of Issues', 'specialty': 'Specialty'}
        )
        fig.update_layout(height=500)
        return fig
    else:
        return specialty_data.tail(10)

def create_license_expiration_timeline(df: pd.DataFrame) -> any:
    """Create a timeline chart for license expirations"""
    if 'license_expiry' not in df.columns:
        return None
    
    # Convert license_expiry to datetime if it's not already
    try:
        df['license_expiry'] = pd.to_datetime(df['license_expiry'])
        
        # Filter for future expirations within next 2 years
        future_df = df[df['license_expiry'] > pd.Timestamp.now()]
        future_df = future_df[future_df['license_expiry'] < pd.Timestamp.now() + pd.DateOffset(years=2)]
        
        # Group by month
        monthly_expirations = future_df.groupby(
            future_df['license_expiry'].dt.to_period('M')
        ).size().reset_index()
        monthly_expirations['license_expiry'] = monthly_expirations['license_expiry'].dt.to_timestamp()
        monthly_expirations.columns = ['month', 'count']
        
        if PLOTLY_AVAILABLE:
            fig = px.line(
                monthly_expirations,
                x='month',
                y='count',
                title='License Expirations Timeline (Next 24 Months)',
                labels={'count': 'Number of Licenses Expiring', 'month': 'Month'}
            )
            fig.update_layout(height=400)
            return fig
        else:
            return monthly_expirations
            
    except Exception as e:
        st.error(f"Error processing license expiration data: {e}")
        return None

def create_data_quality_trends(df: pd.DataFrame) -> any:
    """Create a comprehensive data quality trends chart"""
    if not PLOTLY_AVAILABLE:
        return None
    
    issue_cols = ['license_expired', 'npi_missing', 'phone_issue', 'duplicate_suspect', 'license_state_mismatch']
    existing_cols = [col for col in issue_cols if col in df.columns]
    
    if not existing_cols:
        return None
    
    # Calculate percentages for each issue type
    issue_percentages = {}
    total_providers = len(df)
    
    for col in existing_cols:
        issue_percentages[col.replace('_', ' ').title()] = (df[col].sum() / total_providers) * 100
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(issue_percentages.keys()),
            y=list(issue_percentages.values()),
            marker_color=['red' if v > 10 else 'orange' if v > 5 else 'green' for v in issue_percentages.values()]
        )
    ])
    
    fig.update_layout(
        title='Data Quality Issues Overview (%)',
        xaxis_title='Issue Type',
        yaxis_title='Percentage of Providers',
        height=400
    )
    
    return fig

def create_duplicate_network_graph(dup_pairs: pd.DataFrame) -> any:
    """Create a network graph showing duplicate connections"""
    if not PLOTLY_AVAILABLE or dup_pairs is None or dup_pairs.empty:
        return None
    
    # Create a simple network visualization
    # For now, just show basic statistics
    num_duplicates = len(set(dup_pairs['idx_a']).union(set(dup_pairs['idx_b'])))
    num_pairs = len(dup_pairs)
    
    fig = go.Figure(data=[
        go.Bar(
            x=['Duplicate Pairs', 'Affected Providers'],
            y=[num_pairs, num_duplicates],
            marker_color=['red', 'orange']
        )
    ])
    
    fig.update_layout(
        title='Duplicate Detection Summary',
        yaxis_title='Count',
        height=300
    )
    
    return fig

def create_compliance_dashboard(df: pd.DataFrame) -> dict:
    """Create a comprehensive compliance dashboard"""
    dashboard_data = {}
    
    # Calculate key metrics
    total_providers = len(df)
    
    if 'license_expired' in df.columns:
        expired_licenses = df['license_expired'].sum()
        dashboard_data['expired_licenses'] = {
            'count': expired_licenses,
            'percentage': (expired_licenses / total_providers) * 100
        }
    
    if 'npi_missing' in df.columns:
        missing_npi = df['npi_missing'].sum()
        dashboard_data['missing_npi'] = {
            'count': missing_npi,
            'percentage': (missing_npi / total_providers) * 100
        }
    
    if 'phone_issue' in df.columns:
        phone_issues = df['phone_issue'].sum()
        dashboard_data['phone_issues'] = {
            'count': phone_issues,
            'percentage': (phone_issues / total_providers) * 100
        }
    
    if 'duplicate_suspect' in df.columns:
        duplicates = df['duplicate_suspect'].sum()
        dashboard_data['duplicates'] = {
            'count': duplicates,
            'percentage': (duplicates / total_providers) * 100
        }
    
    return dashboard_data

def display_chart_with_fallback(fig, title: str, fallback_data=None):
    """Display a chart with fallback to simpler visualization if needed"""
    if fig is not None and PLOTLY_AVAILABLE:
        st.plotly_chart(fig, use_container_width=True)
    elif fallback_data is not None and isinstance(fallback_data, pd.DataFrame):
        st.subheader(title)
        st.dataframe(fallback_data, use_container_width=True)
    else:
        st.warning(f"Could not generate visualization for: {title}")