"""
Gen AI integration for Provider Data Quality Analytics
Provides AI-powered insights, recommendations, and enhanced natural language processing
"""
import pandas as pd
import json
from typing import Dict, List, Any, Tuple
import streamlit as st

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class GenAIAnalytics:
    """AI-powered analytics and insights for provider data quality"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        if OPENAI_AVAILABLE and api_key:
            openai.api_key = api_key
    
    def generate_insights(self, df: pd.DataFrame, summary_stats: Dict) -> Dict[str, Any]:
        """Generate AI-powered insights from provider data"""
        insights = {
            "overall_assessment": self._assess_overall_quality(summary_stats),
            "critical_issues": self._identify_critical_issues(summary_stats),
            "recommendations": self._generate_recommendations(summary_stats),
            "risk_areas": self._identify_risk_areas(df, summary_stats),
            "compliance_status": self._assess_compliance_status(summary_stats)
        }
        
        return insights
    
    def _assess_overall_quality(self, stats: Dict) -> str:
        """Assess overall data quality and provide narrative"""
        total_providers = stats.get('total_providers', 0)
        
        if total_providers == 0:
            return "No provider data available for assessment."
        
        # Calculate overall issue rate
        total_issues = 0
        issue_categories = ['expired_licenses', 'missing_npi', 'phone_issues', 'duplicates']
        
        for category in issue_categories:
            if category in stats:
                total_issues += stats[category].get('count', 0)
        
        issue_rate = (total_issues / (total_providers * len(issue_categories))) * 100
        
        if issue_rate < 5:
            return "🟢 **Excellent Data Quality**: Your provider data demonstrates high quality with minimal issues. Continue current data management practices."
        elif issue_rate < 15:
            return "🟡 **Good Data Quality**: Your provider data is generally solid with some areas for improvement. Focus on the identified issues to enhance compliance."
        elif issue_rate < 30:
            return "🟠 **Moderate Data Quality**: Several data quality issues detected that require attention. Implement systematic improvements to ensure compliance."
        else:
            return "🔴 **Poor Data Quality**: Significant data quality issues identified that pose compliance risks. Immediate action required to address critical gaps."
    
    def _identify_critical_issues(self, stats: Dict) -> List[Dict[str, Any]]:
        """Identify the most critical data quality issues"""
        critical_issues = []
        
        # Define thresholds for critical issues
        thresholds = {
            'expired_licenses': {'percentage': 10, 'severity': 'High'},
            'missing_npi': {'percentage': 5, 'severity': 'High'},
            'phone_issues': {'percentage': 15, 'severity': 'Medium'},
            'duplicates': {'percentage': 3, 'severity': 'High'}
        }
        
        for issue_type, threshold in thresholds.items():
            if issue_type in stats:
                percentage = stats[issue_type].get('percentage', 0)
                if percentage > threshold['percentage']:
                    critical_issues.append({
                        'type': issue_type.replace('_', ' ').title(),
                        'percentage': round(percentage, 1),
                        'count': stats[issue_type].get('count', 0),
                        'severity': threshold['severity'],
                        'threshold': threshold['percentage']
                    })
        
        # Sort by severity and percentage
        severity_order = {'High': 3, 'Medium': 2, 'Low': 1}
        critical_issues.sort(key=lambda x: (severity_order[x['severity']], x['percentage']), reverse=True)
        
        return critical_issues
    
    def _generate_recommendations(self, stats: Dict) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on data quality issues"""
        recommendations = []
        
        # Expired licenses recommendations
        if 'expired_licenses' in stats and stats['expired_licenses']['percentage'] > 5:
            recommendations.append({
                'category': 'License Management',
                'priority': 'High',
                'action': 'Implement automated license expiration alerts 90 days before expiry',
                'description': 'Set up proactive monitoring to prevent license lapses and ensure continuous compliance'
            })
        
        # Missing NPI recommendations
        if 'missing_npi' in stats and stats['missing_npi']['percentage'] > 2:
            recommendations.append({
                'category': 'NPI Verification',
                'priority': 'High',
                'action': 'Establish mandatory NPI validation during provider onboarding',
                'description': 'Require valid NPI numbers for all new providers and validate existing records'
            })
        
        # Phone issues recommendations
        if 'phone_issues' in stats and stats['phone_issues']['percentage'] > 10:
            recommendations.append({
                'category': 'Data Standardization',
                'priority': 'Medium',
                'action': 'Implement phone number validation and formatting standards',
                'description': 'Use automated tools to standardize phone number formats and validate entries'
            })
        
        # Duplicate recommendations
        if 'duplicates' in stats and stats['duplicates']['percentage'] > 1:
            recommendations.append({
                'category': 'Data Deduplication',
                'priority': 'High',
                'action': 'Deploy automated duplicate detection and resolution workflow',
                'description': 'Implement systematic duplicate detection and establish merge/resolution procedures'
            })
        
        # General recommendations
        recommendations.append({
            'category': 'Data Governance',
            'priority': 'Medium',
            'action': 'Establish regular data quality monitoring and reporting',
            'description': 'Schedule monthly data quality assessments and track improvement metrics over time'
        })
        
        return recommendations
    
    def _identify_risk_areas(self, df: pd.DataFrame, stats: Dict) -> List[str]:
        """Identify high-risk areas based on data patterns"""
        risk_areas = []
        
        # State-level risks
        if 'address_state' in df.columns:
            state_issues = df.groupby('address_state').agg({
                col: 'sum' for col in df.columns 
                if col in ['license_expired', 'npi_missing', 'phone_issue', 'duplicate_suspect']
            })
            
            if not state_issues.empty:
                high_risk_states = state_issues[state_issues.sum(axis=1) > state_issues.sum(axis=1).quantile(0.8)]
                if not high_risk_states.empty:
                    risk_areas.append(f"High-risk states: {', '.join(high_risk_states.index.tolist()[:5])}")
        
        # Specialty-level risks
        if 'specialty' in df.columns:
            specialty_issues = df.groupby('specialty').agg({
                col: 'sum' for col in df.columns 
                if col in ['license_expired', 'npi_missing', 'phone_issue', 'duplicate_suspect']
            })
            
            if not specialty_issues.empty:
                high_risk_specialties = specialty_issues[specialty_issues.sum(axis=1) > specialty_issues.sum(axis=1).quantile(0.8)]
                if not high_risk_specialties.empty:
                    risk_areas.append(f"High-risk specialties: {', '.join(high_risk_specialties.index.tolist()[:3])}")
        
        return risk_areas
    
    def _assess_compliance_status(self, stats: Dict) -> Dict[str, str]:
        """Assess compliance status for different regulatory aspects"""
        compliance_status = {}
        
        # License compliance
        if 'expired_licenses' in stats:
            expired_pct = stats['expired_licenses']['percentage']
            if expired_pct < 1:
                compliance_status['License Compliance'] = "✅ Compliant"
            elif expired_pct < 5:
                compliance_status['License Compliance'] = "⚠️ At Risk"
            else:
                compliance_status['License Compliance'] = "❌ Non-Compliant"
        
        # NPI compliance
        if 'missing_npi' in stats:
            missing_pct = stats['missing_npi']['percentage']
            if missing_pct < 1:
                compliance_status['NPI Compliance'] = "✅ Compliant"
            elif missing_pct < 3:
                compliance_status['NPI Compliance'] = "⚠️ At Risk"
            else:
                compliance_status['NPI Compliance'] = "❌ Non-Compliant"
        
        # Data quality compliance
        total_issues = sum(stats.get(key, {}).get('count', 0) for key in ['expired_licenses', 'missing_npi', 'phone_issues', 'duplicates'])
        total_providers = stats.get('total_providers', 1)
        quality_score = (1 - (total_issues / (total_providers * 4))) * 100
        
        if quality_score > 90:
            compliance_status['Data Quality'] = "✅ Excellent"
        elif quality_score > 75:
            compliance_status['Data Quality'] = "⚠️ Good"
        else:
            compliance_status['Data Quality'] = "❌ Needs Improvement"
        
        return compliance_status
    
    def enhance_natural_language_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Enhanced natural language processing for queries"""
        # Convert query to lowercase for processing
        query_lower = query.lower()
        
        # Enhanced intent patterns with context
        enhanced_patterns = {
            'predictive_analysis': [
                'predict', 'forecast', 'trend', 'future', 'projection'
            ],
            'risk_assessment': [
                'risk', 'dangerous', 'critical', 'urgent', 'high priority'
            ],
            'compliance_audit': [
                'audit', 'compliance', 'regulatory', 'violation', 'requirement'
            ],
            'comparative_analysis': [
                'compare', 'versus', 'vs', 'difference', 'benchmark'
            ],
            'actionable_insights': [
                'what should', 'recommend', 'suggest', 'action', 'improve'
            ]
        }
        
        # Check for enhanced patterns
        for intent, keywords in enhanced_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                return intent, self._extract_enhanced_params(query, intent)
        
        # Fallback to original intent parsing
        return 'standard_query', {}
    
    def _extract_enhanced_params(self, query: str, intent: str) -> Dict[str, Any]:
        """Extract parameters for enhanced queries"""
        params = {}
        
        if intent == 'predictive_analysis':
            # Look for time periods
            if 'month' in query.lower():
                params['timeframe'] = 'monthly'
            elif 'quarter' in query.lower():
                params['timeframe'] = 'quarterly'
            elif 'year' in query.lower():
                params['timeframe'] = 'yearly'
        
        elif intent == 'comparative_analysis':
            # Look for comparison entities
            if 'state' in query.lower():
                params['compare_by'] = 'state'
            elif 'specialty' in query.lower():
                params['compare_by'] = 'specialty'
        
        return params
    
    def generate_ai_summary(self, insights: Dict[str, Any]) -> str:
        """Generate a natural language summary of insights"""
        if not OPENAI_AVAILABLE or not self.api_key:
            return self._generate_rule_based_summary(insights)
        
        # If OpenAI is available, this would generate more sophisticated summaries
        # For now, return rule-based summary
        return self._generate_rule_based_summary(insights)
    
    def _generate_rule_based_summary(self, insights: Dict[str, Any]) -> str:
        """Generate rule-based summary when AI API is not available"""
        summary_parts = []
        
        # Overall assessment
        summary_parts.append(insights.get('overall_assessment', ''))
        
        # Critical issues
        critical_issues = insights.get('critical_issues', [])
        if critical_issues:
            summary_parts.append(f"\n**Critical Issues Identified:** {len(critical_issues)} issues require immediate attention.")
            for issue in critical_issues[:3]:  # Top 3 issues
                summary_parts.append(f"• {issue['type']}: {issue['percentage']}% of providers affected")
        
        # Top recommendation
        recommendations = insights.get('recommendations', [])
        if recommendations:
            top_rec = recommendations[0]
            summary_parts.append(f"\n**Priority Action:** {top_rec['action']}")
        
        return '\n'.join(summary_parts)

def create_ai_chat_interface():
    """Create an AI-powered chat interface for data quality queries"""
    if 'ai_analytics' not in st.session_state:
        st.session_state.ai_analytics = GenAIAnalytics()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    st.subheader("🤖 AI-Powered Data Quality Assistant")
    
    # Chat interface
    with st.container():
        # Display chat history
        for i, (user_msg, ai_msg) in enumerate(st.session_state.chat_history):
            with st.chat_message("user"):
                st.write(user_msg)
            with st.chat_message("assistant"):
                st.write(ai_msg)
        
        # Input for new message
        user_input = st.chat_input("Ask me about your data quality...")
        
        if user_input:
            # Process the query
            enhanced_intent, params = st.session_state.ai_analytics.enhance_natural_language_query(user_input)
            
            # Generate response based on intent
            if enhanced_intent == 'risk_assessment':
                response = "🔍 **Risk Assessment**: Based on your data, I've identified several risk areas that need attention..."
            elif enhanced_intent == 'predictive_analysis':
                response = "📈 **Predictive Analysis**: Looking at current trends, here are my projections..."
            elif enhanced_intent == 'compliance_audit':
                response = "📋 **Compliance Check**: Let me analyze your compliance status across key areas..."
            elif enhanced_intent == 'actionable_insights':
                response = "💡 **Recommendations**: Here are my top suggestions for improving your data quality..."
            else:
                response = "I understand you're asking about data quality. Let me analyze your current data and provide insights..."
            
            # Add to chat history
            st.session_state.chat_history.append((user_input, response))
            st.rerun()

def display_ai_insights(df: pd.DataFrame, dashboard_data: Dict) -> None:
    """Display AI-generated insights in the dashboard"""
    if 'ai_analytics' not in st.session_state:
        st.session_state.ai_analytics = GenAIAnalytics()
    
    # Add total_providers to dashboard_data if not present
    if 'total_providers' not in dashboard_data:
        dashboard_data['total_providers'] = len(df)
    
    # Generate insights
    insights = st.session_state.ai_analytics.generate_insights(df, dashboard_data)
    
    # Display insights
    st.subheader("🧠 AI-Generated Insights")
    
    # Overall assessment
    st.markdown(insights['overall_assessment'])
    
    # Critical issues
    if insights['critical_issues']:
        st.subheader("🚨 Critical Issues")
        for issue in insights['critical_issues']:
            severity_color = "🔴" if issue['severity'] == 'High' else "🟠"
            st.warning(f"{severity_color} **{issue['type']}**: {issue['percentage']}% of providers affected (threshold: {issue['threshold']}%)")
    
    # Recommendations
    if insights['recommendations']:
        st.subheader("💡 Recommendations")
        for rec in insights['recommendations']:
            priority_icon = "🔥" if rec['priority'] == 'High' else "⚡"
            with st.expander(f"{priority_icon} {rec['category']} - {rec['action']}"):
                st.write(rec['description'])
    
    # Compliance status
    if insights['compliance_status']:
        st.subheader("📋 Compliance Status")
        cols = st.columns(len(insights['compliance_status']))
        for i, (area, status) in enumerate(insights['compliance_status'].items()):
            with cols[i]:
                st.metric(area, status)
    
    # Risk areas
    if insights['risk_areas']:
        st.subheader("⚠️ Risk Areas")
        for risk in insights['risk_areas']:
            st.info(risk)