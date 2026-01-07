# Intelligent Urban Mobility Analytics & GenAI Insights Platform

An end-to-end analytics and GenAI system for urban transportation data that performs scalable data cleaning, KPI computation, SQL analytics, PySpark ETL, GenAI-powered insights, and cloud-based API deployment.

## 🎯 Project Overview

This platform transforms raw NYC taxi trip data into actionable insights through:
- **Data Cleaning & Feature Engineering** (OOP-based)
- **KPI Computation & Visualization**
- **SQL Analytics Layer**
- **Scalable PySpark ETL**
- **GenAI-Powered Insights Assistant**
- **Interactive Streamlit Frontend** 🆕
- **Cloud API Deployment** (Optional)

## 📋 Prerequisites

1. **Python 3.9+**
2. **Kaggle Account** (for dataset access)
3. **OpenAI API Key** or **Google Gemini API Key** (for GenAI features)
4. **AWS Account** (optional, for cloud deployment)

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up Kaggle credentials (see Step 3 below)

# 3. Create .env file with API keys (see Step 2 below)

# 4. Run all tasks automatically
python run_all.py

# OR run tasks individually (see detailed instructions below)
```

## 🚀 Setup Instructions

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** For PySpark, ensure Java 8+ is installed:
```bash
# Mac
brew install openjdk@8

# Linux
sudo apt-get install openjdk-8-jdk

# Verify
java -version
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```env
# GenAI API Keys (choose one or both)
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# AWS Credentials (for cloud deployment)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///mobility_analytics.db
```

### Step 3: Authenticate Kaggle

1. Go to https://www.kaggle.com/account
2. Create API Token (download `kaggle.json`)
3. Place it in `~/.kaggle/kaggle.json` or set `KAGGLE_USERNAME` and `KAGGLE_KEY` environment variables

### Step 4: Run the Pipeline

**Option A: Run All Tasks Automatically**
```bash
python run_all.py
```

**Option B: Run Tasks Individually**
```bash
# 1. Data Ingestion & Cleaning
python 1_data_ingestion_cleaning.py

# 2. KPI Computation & Analysis
python 2_kpi_computation.py

# 3. SQL Analytics
python 3_sql_analytics.py

# 4. PySpark ETL
python 4_pyspark_etl.py

# 5. GenAI Assistant (Interactive)
python 5_genai_assistant.py

# 6. Cloud API (Optional - runs locally)
python 6_cloud_api.py
```

**Option C: Launch Interactive Frontend** 🆕
```bash
# After running tasks 1-4, launch the Streamlit frontend
streamlit run frontend/app.py

# Or use the quick start script
./run_frontend.sh
```

**📖 For detailed step-by-step instructions, see [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md)**

## 📁 Project Structure

```
Capstone_Project/
├── requirements.txt
├── README.md
├── .env.example
├── run_frontend.sh       # Quick start script for frontend
├── 1_data_ingestion_cleaning.py
├── 2_kpi_computation.py
├── 3_sql_analytics.py
├── 4_pyspark_etl.py
├── 5_genai_assistant.py
├── 6_cloud_api.py
├── frontend/             # Streamlit frontend 🆕
│   ├── app.py           # Main Streamlit application
│   └── README.md        # Frontend documentation
├── data/
│   ├── raw/              # Raw CSV files
│   ├── cleaned/          # Cleaned data
│   └── processed/        # Processed outputs
├── outputs/
│   ├── visualizations/   # Charts and graphs
│   ├── sql_results/      # SQL query outputs
│   └── reports/          # Generated reports
└── notebooks/
    └── exploratory_analysis.ipynb
```

## 🔧 Key Components

### 1. Data Ingestion & Cleaning
- OOP-based `MobilityDataAnalyzer` class
- Handles missing values, invalid data
- Feature engineering (hour, day, month, quarter)

### 2. KPI Computation
- Total & Monthly Revenue
- Average Trip Distance & Fare
- Tip Percentage
- Demand Patterns
- Peak vs Off-Peak Utilization

### 3. SQL Analytics
- Peak demand hours
- Revenue by zone
- Top revenue days
- Monthly growth trends

### 4. PySpark ETL
- Scalable processing for large datasets
- Parquet output format
- Performance optimization

### 5. GenAI Assistant
- Natural language queries
- Executive summaries
- Trend explanations

### 6. Interactive Frontend 🆕
- **Dashboard Overview**: Real-time KPIs and metrics
- **Visual Analytics**: Interactive charts and visualizations
- **SQL Insights**: Browse SQL query results with custom visualizations
- **Spark Analytics**: View PySpark ETL outputs
- **GenAI Chatbot**: Natural language interface for data queries
- Features: Date filters, peak hour analysis, geographic insights, custom analysis tools

### 7. Cloud API
- Serverless deployment
- RESTful endpoints
- Scheduled execution

## 📊 Dataset

**NYC Yellow Taxi Trip Data**
- Source: [Kaggle Dataset](https://www.kaggle.com/datasets/elemento/nyc-yellow-taxi-trip-data)
- Automatically downloaded via `kagglehub`

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

This is a capstone project. For questions or improvements, please open an issue.

