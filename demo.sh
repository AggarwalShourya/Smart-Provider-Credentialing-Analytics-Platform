#!/bin/bash
# Demo script for Smart Provider Credentialing Analytics Platform

echo "🏥 Smart Provider Credentialing Analytics Platform Demo"
echo "======================================================"
echo ""

echo "🚀 Starting Enhanced Dashboard..."
echo "Features included:"
echo "  📊 Interactive KPI Dashboard"
echo "  🤖 AI-Powered Insights"
echo "  📈 Advanced Analytics with Charts"
echo "  💬 Natural Language Query Interface"
echo "  📋 Comprehensive Reports & Exports"
echo ""

echo "📁 Sample data will be automatically loaded from:"
echo "  - Provider roster with errors"
echo "  - NY medical license database"
echo "  - CA medical license database"
echo "  - Mock NPI registry"
echo ""

echo "🔧 Available Tabs:"
echo "  🏠 Overview    - KPIs and AI insights"
echo "  📊 Analytics   - Interactive data exploration"
echo "  🤖 AI Assistant - Conversational analytics"
echo "  📋 Reports     - Standard and custom reports"
echo "  💬 Chat Query  - Natural language queries"
echo ""

echo "💡 Try these example queries:"
echo "  • What is our overall provider data quality score?"
echo "  • Show me providers with expired licenses"
echo "  • Which specialties have the most issues?"
echo "  • Generate compliance recommendations"
echo ""

echo "Starting Streamlit application..."
streamlit run ui/enhanced_app.py --server.port 8501 --server.headless false