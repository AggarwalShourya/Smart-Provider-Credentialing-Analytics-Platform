"""
Enhanced Streamlit application with interactive dashboard and Gen AI integration
"""
import os, sys

# Ensure project root is importable (parent of this file)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import pandas as pd
from src.engine import ProviderDQEngine
from src.nlu import parse_intent
from src.visualizations import (
    create_quality_score_gauge, create_state_issues_map, create_issues_by_specialty_chart,
    create_license_expiration_timeline, create_data_quality_trends, create_duplicate_network_graph,
    create_compliance_dashboard, display_chart_with_fallback
)
from src.streamlit_charts import (
    create_basic_metrics_dashboard, create_enhanced_analytics_view,
    create_specialty_issues_chart, create_state_summary_chart
)
from src.ai_analytics import GenAIAnalytics, create_ai_chat_interface, display_ai_insights

# Page configuration (only if not already set)
try:
    st.set_page_config(
        page_title="Smart Provider Credentialing Analytics Platform", 
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://docs.streamlit.io',
            'Report a bug': None,
            'About': "Smart Provider Credentialing Analytics Platform with AI-powered insights"
        }
    )
except st.errors.StreamlitAPIException:
    # Page config already set, continue
    pass

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .alert-high {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 1rem;
        border-radius: 5px;
    }
    .alert-medium {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 1rem;
        border-radius: 5px;
    }
    .alert-low {
        background-color: #e8f5e8;
        border-left: 5px solid #4caf50;
        padding: 1rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="main-header">🏥 Smart Provider Credentialing Analytics Platform</h1>', unsafe_allow_html=True)
st.markdown("### AI-Powered Data Quality Analytics & Interactive Dashboard")

# Initialize session state
if "engine" not in st.session_state:
    st.session_state.engine = ProviderDQEngine()
if "loaded" not in st.session_state:
    st.session_state.loaded = False
if "ai_analytics" not in st.session_state:
    st.session_state.ai_analytics = GenAIAnalytics()

def save_temp(uploaded):
    """Save uploaded file to temporary location"""
    if not uploaded:
        return None
    os.makedirs("./tmp", exist_ok=True)
    path = os.path.abspath(os.path.join("tmp", uploaded.name))
    with open(path, "wb") as f:
        f.write(uploaded.read())
    return path

def load_data_sidebar():
    """Sidebar for data loading"""
    with st.sidebar:
        st.header("📁 Data Management")

        # Option A: Auto-load from local datasets folder
        st.subheader("🚀 Quick Start")
        default_dir = os.path.join(ROOT_DIR, "datasets")
        st.caption(f"Folder: {default_dir}")
        
        if st.button("🔄 Load Sample Data", type="primary"):
            try:
                roster_path = os.path.join(default_dir, "provider_roster_with_errors.csv")
                ny_path = os.path.join(default_dir, "ny_medical_license_database.csv")
                ca_path = os.path.join(default_dir, "ca_medical_license_database.csv")
                npi_path = os.path.join(default_dir, "mock_npi_registry.csv")

                missing = [p for p in [roster_path, ny_path, ca_path, npi_path] if not os.path.exists(p)]
                if missing:
                    st.error("❌ Missing files:\n" + "\n".join(missing))
                else:
                    with st.spinner("Loading data..."):
                        st.session_state.engine.load_files(roster_path, ny_path, ca_path, npi_path)
                        st.session_state.loaded = True
                    st.success("✅ Sample data loaded successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error loading data: {e}")

        st.markdown("---")

        # Option B: Upload files manually
        st.subheader("📤 Upload Custom Data")
        with st.expander("Upload CSV Files"):
            roster = st.file_uploader("Provider Roster (CSV)", type=["csv"], key="roster_upl")
            ny = st.file_uploader("NY License DB (CSV)", type=["csv"], key="ny_upl")
            ca = st.file_uploader("CA License DB (CSV)", type=["csv"], key="ca_upl")
            npi = st.file_uploader("Mock NPI Registry (CSV)", type=["csv"], key="npi_upl")
            
            if st.button("📊 Load Custom Data"):
                if roster is None:
                    st.error("❌ Please upload the provider roster file.")
                else:
                    try:
                        with st.spinner("Processing uploads..."):
                            r_path = save_temp(roster)
                            ny_path = save_temp(ny)
                            ca_path = save_temp(ca)
                            npi_path = save_temp(npi)
                            st.session_state.engine.load_files(r_path, ny_path, ca_path, npi_path)
                            st.session_state.loaded = True
                        st.success("✅ Custom data loaded successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error loading custom data: {e}")

def create_overview_dashboard():
    """Create the main overview dashboard"""
    if not st.session_state.loaded:
        st.info("📥 Please load data using the sidebar to get started.")
        return

    # Get data
    df = st.session_state.engine.aug
    dashboard_data = create_compliance_dashboard(df)
    
    # Key metrics row
    st.subheader("📊 Key Performance Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_providers = len(df)
        st.metric(
            label="👥 Total Providers", 
            value=f"{total_providers:,}",
            help="Total number of providers in the system"
        )
    
    with col2:
        expired_count = st.session_state.engine.count_expired()
        expired_pct = (expired_count / total_providers * 100) if total_providers > 0 else 0
        st.metric(
            label="⏰ Expired Licenses", 
            value=expired_count,
            delta=f"{expired_pct:.1f}%",
            delta_color="inverse",
            help="Number and percentage of providers with expired licenses"
        )
    
    with col3:
        quality_score = st.session_state.engine.get_quality_score()
        st.metric(
            label="🎯 Quality Score", 
            value=f"{quality_score:.1f}%",
            delta="Good" if quality_score > 80 else "Needs Improvement",
            delta_color="normal" if quality_score > 80 else "inverse",
            help="Overall data quality score (0-100%)"
        )
    
    with col4:
        missing_npi = int(st.session_state.engine.list_missing_npi().shape[0])
        missing_npi_pct = (missing_npi / total_providers * 100) if total_providers > 0 else 0
        st.metric(
            label="🆔 Missing NPI", 
            value=missing_npi,
            delta=f"{missing_npi_pct:.1f}%",
            delta_color="inverse",
            help="Providers missing National Provider Identifier"
        )
    
    with col5:
        phone_issues = int(st.session_state.engine.list_phone_issues().shape[0])
        phone_issues_pct = (phone_issues / total_providers * 100) if total_providers > 0 else 0
        st.metric(
            label="📞 Phone Issues", 
            value=phone_issues,
            delta=f"{phone_issues_pct:.1f}%",
            delta_color="inverse",
            help="Providers with phone number format issues"
        )

    # Charts row
    st.markdown("---")
    st.subheader("📈 Data Quality Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Quality score gauge
        gauge_fig = create_quality_score_gauge(quality_score)
        if gauge_fig:
            display_chart_with_fallback(gauge_fig, "Overall Quality Score")
        else:
            st.metric("Overall Quality Score", f"{quality_score:.1f}%")
    
    with col2:
        # Data quality trends
        trends_fig = create_data_quality_trends(df)
        display_chart_with_fallback(trends_fig, "Data Quality Issues Overview")

    # Second row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Issues by specialty
        specialty_fig = create_issues_by_specialty_chart(df)
        display_chart_with_fallback(specialty_fig, "Issues by Specialty", 
                                   fallback_data=st.session_state.engine.specialties_with_most_issues())
    
    with col2:
        # License expiration timeline
        timeline_fig = create_license_expiration_timeline(df)
        display_chart_with_fallback(timeline_fig, "License Expiration Timeline")

    # AI Insights Section
    st.markdown("---")
    display_ai_insights(df, dashboard_data)

def create_analytics_dashboard():
    """Create detailed analytics dashboard"""
    if not st.session_state.loaded:
        st.info("📥 Please load data first to view analytics.")
        return

    st.subheader("📊 Advanced Analytics Dashboard")
    
    df = st.session_state.engine.aug
    
    # Enhanced analytics view with native Streamlit charts
    create_enhanced_analytics_view(st.session_state.engine)
    
    # Filters section
    st.markdown("---")
    st.subheader("🔍 Interactive Data Explorer")
    
    with st.expander("Data Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'specialty' in df.columns:
                specialties = ['All'] + sorted(df['specialty'].dropna().unique().tolist())
                selected_specialty = st.selectbox("Filter by Specialty", specialties)
            else:
                selected_specialty = 'All'
        
        with col2:
            if 'address_state' in df.columns:
                states = ['All'] + sorted(df['address_state'].dropna().unique().tolist())
                selected_state = st.selectbox("Filter by State", states)
            else:
                selected_state = 'All'
        
        with col3:
            issue_types = st.multiselect(
                "Filter by Issue Type",
                ['license_expired', 'npi_missing', 'phone_issue', 'duplicate_suspect'],
                default=[]
            )
    
    # Apply filters
    filtered_df = df.copy()
    if selected_specialty != 'All' and 'specialty' in df.columns:
        filtered_df = filtered_df[filtered_df['specialty'] == selected_specialty]
    if selected_state != 'All' and 'address_state' in df.columns:
        filtered_df = filtered_df[filtered_df['address_state'] == selected_state]
    
    # Display filtered metrics
    st.markdown(f"**Showing {len(filtered_df):,} providers** (filtered from {len(df):,} total)")
    
    # Detailed tables
    st.subheader("📋 Detailed Data Views")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 All Data", "⏰ Expired Licenses", "🆔 Missing NPI", "📞 Phone Issues"])
    
    with tab1:
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="💾 Download Filtered Data",
            data=csv,
            file_name="provider_data_filtered.csv",
            mime="text/csv"
        )
    
    with tab2:
        expired_df = filtered_df[filtered_df.get('license_expired', False) == True]
        st.dataframe(expired_df, use_container_width=True, height=400)
        if not expired_df.empty:
            csv = expired_df.to_csv(index=False)
            st.download_button(
                label="💾 Download Expired Licenses",
                data=csv,
                file_name="expired_licenses.csv",
                mime="text/csv"
            )
    
    with tab3:
        missing_npi_df = filtered_df[filtered_df.get('npi_missing', False) == True]
        st.dataframe(missing_npi_df, use_container_width=True, height=400)
        if not missing_npi_df.empty:
            csv = missing_npi_df.to_csv(index=False)
            st.download_button(
                label="💾 Download Missing NPI",
                data=csv,
                file_name="missing_npi.csv",
                mime="text/csv"
            )
    
    with tab4:
        phone_issues_df = filtered_df[filtered_df.get('phone_issue', False) == True]
        st.dataframe(phone_issues_df, use_container_width=True, height=400)
        if not phone_issues_df.empty:
            csv = phone_issues_df.to_csv(index=False)
            st.download_button(
                label="💾 Download Phone Issues",
                data=csv,
                file_name="phone_issues.csv",
                mime="text/csv"
            )

def create_ai_assistant_page():
    """Create AI assistant page with enhanced chatbot"""
    st.subheader("🤖 AI-Powered Data Quality Assistant")
    
    if not st.session_state.loaded:
        st.info("📥 Please load data first to use the AI assistant.")
        return
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat interface
        create_ai_chat_interface()
        
        # Query examples
        st.subheader("💭 Example Queries")
        example_queries = [
            "What are the critical data quality issues in my provider network?",
            "Which states have the highest compliance risks?",
            "Recommend actions to improve our data quality score",
            "Show me providers with upcoming license expirations",
            "What specialties require immediate attention?",
            "Generate a compliance audit report"
        ]
        
        for query in example_queries:
            if st.button(f"💬 {query}", key=f"example_{hash(query)}"):
                # Process example query
                st.info(f"Processing: {query}")
    
    with col2:
        # Quick AI insights panel
        st.subheader("⚡ Quick Insights")
        
        if st.button("🧠 Generate AI Insights", type="primary"):
            df = st.session_state.engine.aug
            dashboard_data = create_compliance_dashboard(df)
            dashboard_data['total_providers'] = len(df)
            
            insights = st.session_state.ai_analytics.generate_insights(df, dashboard_data)
            summary = st.session_state.ai_analytics.generate_ai_summary(insights)
            
            st.markdown("### 📝 Executive Summary")
            st.markdown(summary)

def create_reports_page():
    """Create reports and exports page"""
    st.subheader("📊 Reports & Exports")
    
    if not st.session_state.loaded:
        st.info("📥 Please load data first to generate reports.")
        return
    
    # Report type selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Standard Reports")
        
        if st.button("📄 Compliance Report", type="primary"):
            compliance_report = st.session_state.engine.compliance_report_expired()
            st.dataframe(compliance_report, use_container_width=True)
            
            if not compliance_report.empty:
                csv = compliance_report.to_csv(index=False)
                st.download_button(
                    label="💾 Download Compliance Report",
                    data=csv,
                    file_name="compliance_report.csv",
                    mime="text/csv"
                )
        
        if st.button("📈 State Summary Report"):
            state_summary = st.session_state.engine.state_issue_summary()
            st.dataframe(state_summary, use_container_width=True)
            
            if not state_summary.empty:
                csv = state_summary.to_csv(index=False)
                st.download_button(
                    label="💾 Download State Summary",
                    data=csv,
                    file_name="state_summary.csv",
                    mime="text/csv"
                )
        
        if st.button("🏥 Specialty Analysis Report"):
            specialty_report = st.session_state.engine.specialties_with_most_issues()
            st.dataframe(specialty_report, use_container_width=True)
            
            if not specialty_report.empty:
                csv = specialty_report.to_csv(index=False)
                st.download_button(
                    label="💾 Download Specialty Report",
                    data=csv,
                    file_name="specialty_analysis.csv",
                    mime="text/csv"
                )
    
    with col2:
        st.subheader("🎯 Custom Reports")
        
        # Custom date range for expiration
        days_ahead = st.number_input("License expiration window (days)", min_value=1, max_value=365, value=60)
        
        if st.button("⏰ Expiration Window Report"):
            expiration_report = st.session_state.engine.filter_by_expiration_window(days_ahead)
            st.dataframe(expiration_report, use_container_width=True)
            
            if not expiration_report.empty:
                csv = expiration_report.to_csv(index=False)
                st.download_button(
                    label="💾 Download Expiration Report",
                    data=csv,
                    file_name=f"expiring_in_{days_ahead}_days.csv",
                    mime="text/csv"
                )

# Main navigation
def main():
    # Data loading sidebar
    load_data_sidebar()
    
    # Main navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Overview", 
        "📊 Analytics", 
        "🤖 AI Assistant", 
        "📋 Reports",
        "💬 Chat Query"
    ])
    
    with tab1:
        create_overview_dashboard()
    
    with tab2:
        create_analytics_dashboard()
    
    with tab3:
        create_ai_assistant_page()
    
    with tab4:
        create_reports_page()
    
    with tab5:
        # Original chatbot functionality
        st.subheader("💬 Natural Language Query Interface")
        st.markdown("Ask questions about your provider data in plain English:")
        
        # Example queries
        st.markdown("**Example queries:**")
        examples = [
            "How many providers have expired licenses in our network?",
            "Show me all providers with phone number formatting issues",
            "Which providers are missing NPI numbers?",
            "Find potential duplicate provider records",
            "What is our overall provider data quality score?",
            "Show me a summary of all data quality problems by state"
        ]
        
        for example in examples:
            st.markdown(f"• {example}")
        
        query = st.text_input("Your question:", placeholder="Type your question here...")
        
        if st.button("🔍 Ask", type="primary") and query:
            if not st.session_state.loaded:
                st.error("❌ Please load data first (sidebar).")
            else:
                try:
                    with st.spinner("Processing your query..."):
                        intent, params = parse_intent(query)
                        st.info(f"🎯 Detected intent: **{intent}** | Parameters: {params}")
                        
                        res = st.session_state.engine.run_query(intent, params)
                        
                        if isinstance(res, pd.DataFrame):
                            st.success(f"✅ Found {len(res)} results")
                            st.dataframe(res, use_container_width=True)
                            
                            # Download button
                            csv = res.to_csv(index=False).encode("utf-8")
                            st.download_button(
                                "💾 Download Results", 
                                data=csv, 
                                file_name=f"{intent}_results.csv", 
                                mime="text/csv"
                            )
                        else:
                            # Scalar result
                            st.success("✅ Query completed")
                            st.metric("Result", res)
                            
                except Exception as e:
                    st.error(f"❌ Error processing query: {e}")

if __name__ == "__main__":
    main()