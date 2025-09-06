"""
Gen-AI module for enhanced natural language processing and intelligent responses
"""
import os
from typing import Dict, Any, Tuple, Optional
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

# Load environment variables
load_dotenv()

# Try to import OpenAI, but make it optional
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

from .intents import INTENT_PATTERNS, extract_params


class GenAIProcessor:
    """Enhanced NLU processor with Gen-AI capabilities"""
    
    def __init__(self):
        self.openai_available = OPENAI_AVAILABLE
        self.client = None
        
        # Initialize OpenAI client if available and API key is provided
        if self.openai_available:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                try:
                    self.client = openai.OpenAI(api_key=api_key)
                except Exception as e:
                    st.warning(f"OpenAI initialization failed: {e}")
                    self.client = None
    
    def parse_intent_with_ai(self, text: str) -> Tuple[str, Dict]:
        """Parse intent using AI if available, fallback to rule-based"""
        # First try rule-based approach
        intent, params = self._rule_based_intent_parsing(text)
        
        # If OpenAI is available and we have a fallback intent, try to enhance it
        if self.client and intent == "overall_quality_score":  # This is our fallback
            try:
                enhanced_intent, enhanced_params = self._ai_intent_parsing(text)
                if enhanced_intent and enhanced_intent != "overall_quality_score":
                    return enhanced_intent, enhanced_params
            except Exception as e:
                st.warning(f"AI parsing failed, using rule-based: {e}")
        
        return intent, params
    
    def _rule_based_intent_parsing(self, text: str) -> Tuple[str, Dict]:
        """Original rule-based intent parsing"""
        for intent, patterns in INTENT_PATTERNS.items():
            for p in patterns:
                if p.search(text):
                    params = extract_params(intent, text)
                    return intent, params
        
        # Fallback logic
        t = text.lower()
        if "expired" in t and "license" in t and "how many" in t:
            return "expired_license_count", {}
        if "duplicate" in t:
            return "duplicate_records", {}
        if "quality score" in t:
            return "overall_quality_score", {}
        if "phone" in t and ("issue" in t or "format" in t):
            return "phone_format_issues", {}
        
        return "overall_quality_score", {}
    
    def _ai_intent_parsing(self, text: str) -> Tuple[str, Dict]:
        """AI-enhanced intent parsing using OpenAI"""
        if not self.client:
            return None, {}
        
        available_intents = list(INTENT_PATTERNS.keys())
        
        prompt = f"""
You are an expert in healthcare data quality analysis. Given a user query, identify the most appropriate intent from the following options:

Available intents:
- expired_license_count: Count expired licenses
- phone_format_issues: Find phone formatting problems  
- missing_npi: Find providers missing NPI numbers
- duplicate_records: Find duplicate provider records
- overall_quality_score: Get overall data quality score
- specialties_with_most_issues: Find specialties with most data quality issues
- state_issue_summary: Get summary of issues by state
- compliance_report_expired: Generate compliance report for expired licenses
- filter_by_expiration_window: Filter providers by license expiration within X days
- multi_state_single_license: Find providers in multiple states with single license
- export_update_list: Export list of providers needing updates

User query: "{text}"

Respond with ONLY the intent name that best matches the query. If no intent matches well, respond with "overall_quality_score".
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            predicted_intent = response.choices[0].message.content.strip()
            
            # Validate the predicted intent
            if predicted_intent in available_intents:
                # Extract parameters if needed
                params = extract_params(predicted_intent, text)
                return predicted_intent, params
            
        except Exception as e:
            st.warning(f"AI intent parsing error: {e}")
        
        return None, {}
    
    def generate_intelligent_response(self, intent: str, result: Any, query: str) -> str:
        """Generate intelligent natural language response using AI"""
        if not self.client:
            return self._generate_simple_response(intent, result)
        
        try:
            # Prepare context about the result
            if isinstance(result, pd.DataFrame):
                if result.empty:
                    result_context = "No data found"
                else:
                    result_context = f"Found {len(result)} records. Columns: {', '.join(result.columns[:5])}{'...' if len(result.columns) > 5 else ''}"
            elif isinstance(result, (int, float)):
                result_context = f"Result: {result}"
            else:
                result_context = f"Result: {str(result)[:200]}"
            
            prompt = f"""
You are a healthcare data quality expert assistant. A user asked: "{query}"

The system identified this as intent: {intent}
The query result: {result_context}

Generate a helpful, professional response that:
1. Directly answers the user's question
2. Provides context about what the data means
3. Suggests potential next steps or related insights
4. Keeps response under 150 words
5. Uses healthcare terminology appropriately

Response:
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.warning(f"AI response generation failed: {e}")
            return self._generate_simple_response(intent, result)
    
    def _generate_simple_response(self, intent: str, result: Any) -> str:
        """Generate simple rule-based response"""
        responses = {
            "expired_license_count": f"Found {result} providers with expired licenses.",
            "phone_format_issues": f"Found {len(result) if hasattr(result, '__len__') else result} providers with phone formatting issues.",
            "missing_npi": f"Found {len(result) if hasattr(result, '__len__') else result} providers missing NPI numbers.",
            "duplicate_records": f"Found {len(result) if hasattr(result, '__len__') else result} potential duplicate records.",
            "overall_quality_score": f"Overall data quality score is {result}%.",
            "specialties_with_most_issues": "Here are the medical specialties with the most data quality issues.",
            "state_issue_summary": "Here's a summary of data quality issues by state.",
            "compliance_report_expired": "Generated compliance report for expired licenses.",
            "filter_by_expiration_window": f"Found {len(result) if hasattr(result, '__len__') else result} providers with licenses expiring soon.",
            "multi_state_single_license": f"Found {len(result) if hasattr(result, '__len__') else result} providers practicing in multiple states with single licenses.",
            "export_update_list": f"Generated list of {len(result) if hasattr(result, '__len__') else result} providers requiring credential updates."
        }
        
        return responses.get(intent, "Query completed successfully.")
    
    def suggest_follow_up_questions(self, intent: str, result: Any) -> list:
        """Suggest relevant follow-up questions based on current query"""
        suggestions = {
            "expired_license_count": [
                "Show me the compliance report for expired licenses",
                "Which specialties have the most expired licenses?",
                "What is the trend of license expirations over time?"
            ],
            "phone_format_issues": [
                "Export the list of providers with phone issues",
                "Which states have the most phone formatting problems?",
                "What is our overall data quality score?"
            ],
            "missing_npi": [
                "Show providers missing both NPI and having other issues",
                "Which specialties are missing the most NPI numbers?",
                "Export update list for providers needing NPI numbers"
            ],
            "overall_quality_score": [
                "Show me a breakdown of issues by type",
                "Which specialties have the most data quality issues?",
                "What are the main data quality problems?"
            ]
        }
        
        return suggestions.get(intent, [
            "What is our overall data quality score?",
            "Show me issues by specialty",
            "Generate a compliance report"
        ])


# Global instance
genai_processor = GenAIProcessor()


def parse_intent(text: str) -> Tuple[str, Dict]:
    """Enhanced intent parsing with AI support"""
    return genai_processor.parse_intent_with_ai(text)


def generate_response(intent: str, result: Any, query: str) -> str:
    """Generate intelligent response"""
    return genai_processor.generate_intelligent_response(intent, result, query)


def get_follow_up_suggestions(intent: str, result: Any) -> list:
    """Get follow-up question suggestions"""
    return genai_processor.suggest_follow_up_questions(intent, result)