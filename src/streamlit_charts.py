"""
Enhanced visualization functions that work without external plotting libraries
Uses Streamlit's built-in chart capabilities as fallbacks
"""
import pandas as pd
import streamlit as st
import numpy as np
from typing import Dict, Any

def create_basic_metrics_dashboard(df: pd.DataFrame) -> Dict[str, Any]:
    """Create basic metrics that can be displayed with Streamlit components"""
    metrics = {}
    
    # Total providers
    metrics['total_providers'] = len(df)
    
    # Issue type metrics
    issue_cols = ['license_expired', 'npi_missing', 'phone_issue', 'duplicate_suspect', 'license_state_mismatch']
    
    for col in issue_cols:
        if col in df.columns:
            count = df[col].sum() if df[col].dtype == 'bool' else len(df[df[col] == True])
            percentage = (count / len(df)) * 100 if len(df) > 0 else 0
            metrics[col] = {
                'count': int(count),
                'percentage': round(percentage, 1)
            }
    
    return metrics

def display_streamlit_bar_chart(df: pd.DataFrame, title: str, x_col: str, y_col: str):
    """Create a bar chart using Streamlit's built-in chart functionality"""
    st.subheader(title)
    
    # Prepare data for chart
    chart_data = df.set_index(x_col)[y_col]
    
    # Display as bar chart
    st.bar_chart(chart_data)
    
    # Also show as dataframe for reference
    with st.expander("View Data Table"):
        st.dataframe(df[[x_col, y_col]], use_container_width=True)

def display_streamlit_line_chart(df: pd.DataFrame, title: str, x_col: str, y_col: str):
    """Create a line chart using Streamlit's built-in chart functionality"""
    st.subheader(title)
    
    # Prepare data for chart
    chart_data = df.set_index(x_col)[y_col]
    
    # Display as line chart
    st.line_chart(chart_data)
    
    # Also show as dataframe for reference
    with st.expander("View Data Table"):
        st.dataframe(df[[x_col, y_col]], use_container_width=True)

def create_specialty_issues_chart(engine):
    """Create specialty issues visualization with fallback"""
    specialty_data = engine.specialties_with_most_issues()
    
    if not specialty_data.empty:
        # Top 10 specialties
        top_specialties = specialty_data.head(10)
        
        st.subheader("🏥 Top Specialties with Most Issues")
        
        # Create columns for better layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Use Streamlit's bar chart
            chart_data = top_specialties.set_index('specialty')['issues']
            st.bar_chart(chart_data)
        
        with col2:
            # Show metrics
            st.metric("Total Specialties", len(specialty_data))
            st.metric("Highest Issues", top_specialties.iloc[0]['issues'] if len(top_specialties) > 0 else 0)
            
        # Show detailed table
        with st.expander("View Detailed Data"):
            st.dataframe(specialty_data, use_container_width=True)
    else:
        st.info("No specialty data available for visualization")

def create_state_summary_chart(engine):
    """Create state summary visualization with fallback"""
    state_data = engine.state_issue_summary()
    
    if not state_data.empty:
        st.subheader("🗺️ Issues by State Summary")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # If state_data has the right columns, create a chart
            if 'state' in state_data.columns or 'address_state' in state_data.columns:
                state_col = 'state' if 'state' in state_data.columns else 'address_state'
                issue_cols = [col for col in state_data.columns if col != state_col]
                
                if issue_cols:
                    # Create a simple bar chart with total issues
                    state_data['total_issues'] = state_data[issue_cols].sum(axis=1)
                    chart_data = state_data.set_index(state_col)['total_issues']
                    st.bar_chart(chart_data)
        
        with col2:
            st.metric("States Analyzed", len(state_data))
            if 'total_issues' in state_data.columns or len([col for col in state_data.columns if 'issue' in col.lower()]) > 0:
                total_issues = state_data.select_dtypes(include=[np.number]).sum().sum()
                st.metric("Total Issues", int(total_issues))
        
        # Show detailed table
        with st.expander("View State Details"):
            st.dataframe(state_data, use_container_width=True)
    else:
        st.info("No state data available for visualization")

def create_data_quality_overview(metrics: Dict[str, Any]):
    """Create an overview of data quality using Streamlit components"""
    st.subheader("📊 Data Quality Overview")
    
    # Create issue distribution chart
    issue_data = []
    issue_labels = []
    
    for key, value in metrics.items():
        if isinstance(value, dict) and 'percentage' in value:
            issue_labels.append(key.replace('_', ' ').title())
            issue_data.append(value['percentage'])
    
    if issue_data:
        # Create a DataFrame for the chart
        chart_df = pd.DataFrame({
            'Issue Type': issue_labels,
            'Percentage': issue_data
        })
        
        # Display as bar chart
        st.bar_chart(chart_df.set_index('Issue Type')['Percentage'])
        
        # Color-coded alerts based on severity
        st.subheader("🚨 Issue Severity Analysis")
        col1, col2, col3 = st.columns(3)
        
        high_severity = sum(1 for p in issue_data if p > 20)
        medium_severity = sum(1 for p in issue_data if 5 < p <= 20)
        low_severity = sum(1 for p in issue_data if p <= 5)
        
        with col1:
            st.metric("🔴 High Severity", high_severity, help="Issues affecting >20% of providers")
        with col2:
            st.metric("🟡 Medium Severity", medium_severity, help="Issues affecting 5-20% of providers")
        with col3:
            st.metric("🟢 Low Severity", low_severity, help="Issues affecting <5% of providers")

def create_compliance_timeline_chart(engine):
    """Create a compliance timeline using available data"""
    try:
        # Get providers with upcoming expirations
        upcoming_expirations = engine.filter_by_expiration_window(365)  # Next 12 months
        
        if not upcoming_expirations.empty and 'license_expiration' in upcoming_expirations.columns:
            st.subheader("📅 License Expiration Timeline")
            
            # Convert to datetime
            upcoming_expirations['license_expiration'] = pd.to_datetime(upcoming_expirations['license_expiration'])
            
            # Group by month
            monthly_exp = upcoming_expirations.groupby(
                upcoming_expirations['license_expiration'].dt.to_period('M')
            ).size().reset_index()
            monthly_exp['month'] = monthly_exp['license_expiration'].dt.to_timestamp()
            monthly_exp.columns = ['period', 'count', 'month']
            
            # Create line chart
            chart_data = monthly_exp.set_index('month')['count']
            st.line_chart(chart_data)
            
            # Show summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                next_30_days = upcoming_expirations[
                    upcoming_expirations['license_expiration'] <= pd.Timestamp.now() + pd.DateOffset(days=30)
                ]
                st.metric("Expiring in 30 Days", len(next_30_days))
            
            with col2:
                next_90_days = upcoming_expirations[
                    upcoming_expirations['license_expiration'] <= pd.Timestamp.now() + pd.DateOffset(days=90)
                ]
                st.metric("Expiring in 90 Days", len(next_90_days))
            
            with col3:
                st.metric("Total in Next Year", len(upcoming_expirations))
        else:
            st.info("No license expiration data available for timeline")
    
    except Exception as e:
        st.error(f"Error creating timeline: {e}")

def create_enhanced_analytics_view(engine):
    """Create an enhanced analytics view using Streamlit's built-in capabilities"""
    if not hasattr(engine, 'aug') or engine.aug is None:
        st.error("No data loaded for analysis")
        return
    
    df = engine.aug
    metrics = create_basic_metrics_dashboard(df)
    
    # Overview metrics
    create_data_quality_overview(metrics)
    
    st.markdown("---")
    
    # Specialty analysis
    create_specialty_issues_chart(engine)
    
    st.markdown("---")
    
    # State analysis
    create_state_summary_chart(engine)
    
    st.markdown("---")
    
    # Timeline analysis
    create_compliance_timeline_chart(engine)
    
    return metrics