# Smart Provider Credentialing Analytics Platform

## 🚀 Enhanced with AI-Powered Insights and Interactive Dashboards

A comprehensive healthcare data quality analytics platform that combines advanced data validation, AI-powered natural language processing, and interactive visualizations to help healthcare organizations maintain high-quality provider credentialing data.

## ✨ New Features

### 🤖 Gen-AI Integration
- **Enhanced Natural Language Understanding**: Advanced AI-powered query processing using OpenAI
- **Intelligent Response Generation**: Context-aware responses that provide actionable insights
- **Smart Recommendations**: AI-generated follow-up questions and suggestions
- **Conversational Interface**: Natural language queries with intelligent parsing

### 📊 Interactive Dashboard & Visualizations
- **Real-time Quality Score Gauge**: Visual representation of overall data quality
- **Interactive Charts**: Dynamic charts for issues by type, specialties, and states
- **License Expiration Timeline**: Trend analysis of license expirations
- **Duplicate Analysis Visualizations**: Advanced duplicate detection insights
- **State-wise Analysis**: Geographic distribution of data quality issues
- **Specialty-based Insights**: Medical specialty performance analytics

### 🎯 Enhanced User Experience
- **Modern UI Design**: Clean, professional interface with intuitive navigation
- **Tabbed Dashboard**: Organized views for different types of analysis
- **One-click Sample Data**: Quick data loading for immediate testing
- **Export Capabilities**: Download results in CSV format
- **Responsive Design**: Works seamlessly across different screen sizes

## 🏗️ Architecture

### Core Components
- **Data Quality Engine** (`src/engine.py`): Core analytics and validation engine
- **Visualization Module** (`src/visualizations.py`): Interactive charts and graphs
- **Gen-AI Processor** (`src/genai.py`): AI-powered natural language processing
- **Enhanced Dashboard** (`ui/dashboard.py`): Modern Streamlit-based interface

### Data Processing Pipeline
1. **Data Ingestion**: Load provider data, license databases, and NPI registry
2. **Standardization**: Clean and normalize data formats
3. **Validation**: Apply business rules and cross-reference external data
4. **Quality Scoring**: Calculate composite data quality metrics
5. **AI Analysis**: Process natural language queries with AI
6. **Visualization**: Generate interactive charts and dashboards

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/amruth6002/Smart-Provider-Credentialing-Analytics-Platform.git
   cd Smart-Provider-Credentialing-Analytics-Platform
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Configure AI features:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key for enhanced AI features
   ```

4. Run the application:
   ```bash
   ./run.sh
   ```

5. Open your browser to `http://localhost:8501`

### Quick Demo with Sample Data
1. Start the application
2. Click "🚀 Load Sample Dataset" in the sidebar
3. Explore the interactive dashboard and charts
4. Try AI-powered queries like:
   - "How many providers have expired licenses?"
   - "Show me quality issues by specialty"
   - "What's our overall data quality score?"

## 📈 Features & Capabilities

### Data Quality Analytics
- ✅ License expiration tracking and compliance
- ✅ NPI number validation and missing data detection
- ✅ Phone number format validation
- ✅ Duplicate provider record detection
- ✅ Multi-state licensing analysis
- ✅ Specialty-based quality metrics

### Interactive Visualizations
- 📊 Quality score gauge with thresholds
- 📈 Issues distribution charts
- 🗺️ State-wise analysis
- 📅 License expiration timeline
- 🏥 Specialty performance analytics
- 🔍 Duplicate analysis insights

### AI-Powered Features
- 🤖 Natural language query processing
- 💡 Intelligent response generation
- 🎯 Smart follow-up suggestions
- 📝 Context-aware insights
- 🔄 Conversational interface

### Export & Reporting
- 📥 CSV data exports
- 📋 Compliance reports
- 📊 Custom filtered views
- 📈 Analytics summaries

## 🛠️ Configuration

### Environment Variables
Create a `.env` file (copy from `.env.example`) and configure:

```env
# Optional: Enable AI features
OPENAI_API_KEY=your_openai_api_key_here

# Other configurations
DEBUG=false
```

### Data Sources
The platform supports multiple data inputs:
- **Provider Roster**: Main provider database
- **License Databases**: State-specific license validation (NY, CA)
- **NPI Registry**: National Provider Identifier validation

## 🏥 Use Cases

### Healthcare Organizations
- Monitor provider credentialing compliance
- Identify data quality issues before audits
- Maintain accurate provider directories
- Track license expiration and renewals

### Data Quality Teams
- Automate data validation processes
- Generate compliance reports
- Identify systematic data issues
- Monitor quality metrics over time

### Administrative Staff
- Quick lookups for specific providers
- Generate update lists for providers
- Track multi-state licensing compliance
- Export data for external systems

## 🔧 Technical Stack

- **Backend**: Python, Pandas, DuckDB
- **Frontend**: Streamlit with custom CSS
- **Visualizations**: Plotly, Altair
- **AI/ML**: OpenAI API, Natural Language Processing
- **Data Processing**: Pandas, NumPy
- **APIs**: FastAPI (available separately)

## 📱 API Access

The platform also includes a REST API for programmatic access:

```bash
# Start API server
uvicorn src.api:app --host 0.0.0.0 --port 8000

# Example API calls
curl -X POST "http://localhost:8000/query" -F "text=How many expired licenses?"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information
4. For AI features, ensure your OpenAI API key is valid

## 🚀 Future Enhancements

- Real-time data streaming integration
- Advanced ML-based anomaly detection
- Mobile-responsive design
- Integration with EHR systems
- Automated report scheduling
- Advanced role-based access controls