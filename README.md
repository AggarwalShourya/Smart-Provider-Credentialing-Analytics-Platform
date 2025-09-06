# 🏥 Smart Provider Credentialing Analytics Platform

An AI-powered, interactive dashboard for provider data quality analytics with comprehensive visualizations and intelligent insights.

## 🚀 Features

### 🤖 AI-Powered Analytics
- **Intelligent Insights Generation**: Automated analysis of data quality patterns
- **Smart Recommendations**: AI-generated actionable improvements
- **Risk Assessment**: Automated identification of high-risk areas
- **Compliance Monitoring**: Real-time compliance status tracking
- **Natural Language Processing**: Enhanced query understanding

### 📊 Interactive Dashboard
- **Multi-Tab Interface**: Organized navigation across different analytics views
- **Real-Time KPIs**: Live metrics with trend indicators
- **Interactive Visualizations**: Charts and graphs with filtering capabilities
- **Data Exploration Tools**: Advanced filtering and drill-down capabilities
- **Export Functionality**: CSV downloads for all data views

### 💬 Conversational Interface
- **AI Chat Assistant**: Natural language interaction for data queries
- **Intent Recognition**: Smart understanding of user questions
- **Contextual Responses**: Relevant insights based on query context
- **Example Queries**: Pre-built question templates

### 📋 Comprehensive Reporting
- **Standard Reports**: Compliance, state summary, specialty analysis
- **Custom Reports**: Configurable date ranges and parameters
- **Export Capabilities**: CSV downloads for all reports
- **Executive Summaries**: AI-generated high-level insights

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AggarwalShourya/Smart-Provider-Credentialing-Analytics-Platform.git
   cd Smart-Provider-Credentialing-Analytics-Platform
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the enhanced dashboard:**
   ```bash
   streamlit run ui/enhanced_app.py
   ```

   Or use the demo script:
   ```bash
   ./demo.sh
   ```

## 📱 Usage

### Quick Start
1. Open the application in your browser
2. Click "🔄 Load Sample Data" in the sidebar
3. Explore the different tabs:
   - **🏠 Overview**: View KPIs and AI insights
   - **📊 Analytics**: Interactive data exploration
   - **🤖 AI Assistant**: Chat with the AI
   - **📋 Reports**: Generate reports
   - **💬 Chat Query**: Natural language queries

### Sample Queries
Try these natural language questions:
- "What is our overall provider data quality score?"
- "Show me providers with expired licenses"
- "Which states have the most compliance issues?"
- "Generate recommendations for data quality improvement"
- "Find providers with phone number issues"

## 🔧 Architecture

### Core Components
- **`src/engine.py`**: Data quality engine with analytics capabilities
- **`src/ai_analytics.py`**: AI-powered insights and recommendations
- **`src/visualizations.py`**: Interactive charts with Plotly
- **`src/streamlit_charts.py`**: Native Streamlit visualizations
- **`ui/enhanced_app.py`**: Main dashboard application

### Data Processing Pipeline
1. **Data Ingestion**: CSV file loading and normalization
2. **Quality Analysis**: Rule-based validation and scoring
3. **AI Processing**: Insight generation and recommendations
4. **Visualization**: Interactive charts and dashboards
5. **Export**: CSV and report generation

## 📊 Data Quality Metrics

The platform analyzes multiple data quality dimensions:

- **License Compliance**: Expiration tracking and validation
- **NPI Verification**: National Provider Identifier validation
- **Contact Information**: Phone number format validation
- **Duplicate Detection**: Provider record deduplication
- **Geographic Analysis**: State-wise issue distribution
- **Specialty Analysis**: Medical specialty risk assessment

## 🤖 AI Capabilities

### Intelligent Analysis
- **Pattern Recognition**: Automated identification of data quality trends
- **Risk Scoring**: Predictive assessment of compliance risks
- **Anomaly Detection**: Identification of unusual data patterns
- **Recommendation Engine**: Actionable improvement suggestions

### Natural Language Understanding
- **Intent Classification**: Understanding user query intentions
- **Parameter Extraction**: Extracting relevant parameters from queries
- **Context Awareness**: Maintaining conversation context
- **Response Generation**: Creating relevant, helpful responses

## 🔒 Data Security

- **Local Processing**: All data processing occurs locally
- **No External Dependencies**: Core functionality works without internet
- **Configurable AI**: Optional AI features with API key configuration
- **Data Privacy**: No data transmitted to external services

## 📈 Performance Metrics

Example analysis from sample dataset (582 providers):
- **90.5%** expired licenses identified
- **48.5%** overall quality score
- **100%** phone formatting issues detected
- **31.8%** potential duplicates found

## 🔄 Development

### Project Structure
```
├── src/                    # Core analytics engine
│   ├── engine.py          # Main data quality engine
│   ├── ai_analytics.py    # AI-powered insights
│   ├── visualizations.py  # Interactive charts
│   └── streamlit_charts.py # Native visualizations
├── ui/                    # User interface
│   ├── app.py            # Original simple UI
│   └── enhanced_app.py   # Enhanced dashboard
├── datasets/             # Sample data files
└── requirements.txt      # Python dependencies
```

### Adding New Features
1. **New Analytics**: Add functions to `src/engine.py`
2. **AI Insights**: Extend `src/ai_analytics.py`
3. **Visualizations**: Add charts to `src/visualizations.py`
4. **UI Components**: Update `ui/enhanced_app.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Streamlit for the interactive dashboard
- Powered by Plotly for advanced visualizations
- Enhanced with AI capabilities for intelligent insights
- Sample data generated for demonstration purposes