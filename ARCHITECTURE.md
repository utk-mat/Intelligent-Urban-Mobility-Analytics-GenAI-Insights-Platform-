# 🏗️ System Architecture

## Overview

The Intelligent Urban Mobility Analytics & GenAI Insights Platform is an end-to-end data pipeline that transforms raw transportation data into actionable insights through multiple processing layers.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA INGESTION LAYER                            │
│                                                                         │
│  ┌──────────────┐                                                       │
│  │  Kaggle API  │ ────> Raw CSV Files                                  │
│  └──────────────┘                                                       │
│         │                                                                │
│         ▼                                                                │
│  ┌──────────────────────────────────────────────────────┐              │
│  │  MobilityDataAnalyzer (OOP)                          │              │
│  │  - load_data()                                        │              │
│  │  - clean_data()                                       │              │
│  │  - feature_engineering()                              │              │
│  │  - export_clean_data()                                │              │
│  └──────────────────────────────────────────────────────┘              │
│         │                                                                │
│         ▼                                                                │
│  Cleaned Data (CSV) ────> data/cleaned/cleaned_taxi_data.csv          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      ANALYTICS & PROCESSING LAYER                       │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │  KPI Computation │  │   SQL Analytics │  │  PySpark ETL     │     │
│  │                  │  │                  │  │                  │     │
│  │  - Revenue       │  │  - Peak Hours    │  │  - Distributed   │     │
│  │  - Distance      │  │  - Top Zones     │  │    Processing    │     │
│  │  - Tips          │  │  - Growth Trends  │  │  - Parquet       │     │
│  │  - Demand        │  │  - Weekday       │  │    Output        │     │
│  │                  │  │    Analysis      │  │  - DAG           │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│         │                       │                       │                │
│         ▼                       ▼                       ▼                │
│  Visualizations         SQLite DB          Processed Parquet            │
│  (PNG files)           (SQL queries)       (Scalable storage)           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        GENAI INSIGHTS LAYER                              │
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐              │
│  │  MobilityGenAIAssistant                               │              │
│  │                                                       │              │
│  │  Context Sources:                                    │              │
│  │  - Cleaned Data                                      │              │
│  │  - KPI Reports                                       │              │
│  │  - SQL Query Results                                 │              │
│  │                                                       │              │
│  │  Capabilities:                                       │              │
│  │  - Natural Language Q&A                              │              │
│  │  - Executive Summaries                               │              │
│  │  - Trend Explanations                                │              │
│  │                                                       │              │
│  │  LLM Integration:                                     │              │
│  │  - OpenAI GPT-4 / Gemini Pro                         │              │
│  │  - LangChain Prompt Orchestration                    │              │
│  └──────────────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API DEPLOYMENT LAYER                            │
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐              │
│  │  FastAPI Server (MobilityAnalyticsAPI)                │              │
│  │                                                       │              │
│  │  Endpoints:                                           │              │
│  │  - GET /monthly-revenue                               │              │
│  │  - GET /peak-hours                                    │              │
│  │  - GET /top-zones                                     │              │
│  │  - GET /kpis                                          │              │
│  │  - GET /demand-pattern                                │              │
│  └──────────────────────────────────────────────────────┘              │
│         │                                                                │
│         ▼                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │ AWS Lambda   │  │ Azure Func    │  │ Local Server  │                │
│  │ (Serverless) │  │ (Serverless)  │  │ (Development) │                │
│  └──────────────┘  └──────────────┘  └──────────────┘                │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Data Ingestion Flow
```
Kaggle Dataset → kagglehub → Raw CSV → MobilityDataAnalyzer → Cleaned CSV
```

### 2. Analytics Flow
```
Cleaned CSV → [KPI Analyzer | SQL Analytics | PySpark ETL] → Results/Outputs
```

### 3. Insights Flow
```
Results + Context → GenAI Assistant → Natural Language Insights
```

### 4. API Flow
```
Aggregated Data → FastAPI → REST Endpoints → Clients/Applications
```

## Component Details

### 1. Data Ingestion & Cleaning (Task 1)
- **Technology:** Python, Pandas, OOP
- **Input:** Kaggle NYC Taxi Trip Data
- **Output:** Cleaned CSV with engineered features
- **Key Features:**
  - Missing value handling
  - Data type conversion
  - Feature engineering (hour, day, month, quarter)
  - Outlier removal

### 2. KPI Computation (Task 2)
- **Technology:** Pandas, Matplotlib, Seaborn
- **Input:** Cleaned CSV
- **Output:** Visualizations + KPI Report
- **KPIs Computed:**
  - Total & Monthly Revenue
  - Average Trip Distance
  - Average Fare per Trip
  - Tip Percentage
  - Trips per Hour
  - Revenue per Mile
  - Peak vs Off-Peak Utilization

### 3. SQL Analytics (Task 3)
- **Technology:** SQLite/PostgreSQL, SQLAlchemy
- **Input:** Cleaned CSV
- **Output:** SQL Query Results (CSV)
- **Queries:**
  - Peak demand hours
  - Revenue by zone
  - Top revenue days
  - Monthly growth trends
  - Weekend analysis

### 4. PySpark ETL (Task 4)
- **Technology:** PySpark, Parquet
- **Input:** Cleaned CSV
- **Output:** Processed Parquet files
- **Capabilities:**
  - Distributed processing
  - Scalable to 100GB+
  - Performance optimization
  - DAG visualization

### 5. GenAI Assistant (Task 5)
- **Technology:** LangChain, OpenAI/Gemini API
- **Input:** KPI Reports + SQL Results + Data Context
- **Output:** Natural Language Insights
- **Features:**
  - Question answering
  - Executive summaries
  - Trend explanations
  - Interactive mode

### 6. Cloud API (Task 6)
- **Technology:** FastAPI, AWS Lambda/Azure Functions
- **Input:** Aggregated KPIs
- **Output:** REST API Endpoints
- **Deployment Options:**
  - Local development
  - AWS Lambda (serverless)
  - Azure Functions (serverless)

## Scalability Strategy

### For 100GB+ Datasets

1. **Storage:**
   - S3 / Azure Blob Storage (Parquet format)
   - Partitioned by date/month

2. **Processing:**
   - PySpark on Databricks/EMR
   - Distributed computing clusters

3. **Indexing:**
   - Vector DB (FAISS/Pinecone) for semantic search
   - Elasticsearch for structured queries

4. **Retrieval:**
   - RAG (Retrieval-Augmented Generation) over aggregated metrics
   - Pre-computed aggregations for fast queries

## Technology Stack Summary

| Layer | Technologies |
|-------|-------------|
| Data Ingestion | Python, Pandas, kagglehub |
| Data Cleaning | Python OOP, NumPy |
| Analytics | Pandas, SQL, PySpark |
| Visualization | Matplotlib, Seaborn |
| GenAI | LangChain, OpenAI API, Gemini API |
| API | FastAPI, uvicorn |
| Cloud | AWS Lambda, Azure Functions, S3 |
| Database | SQLite, PostgreSQL (optional) |
| Storage | CSV, Parquet |

## Performance Characteristics

- **Data Ingestion:** ~5-15 min for 100K records
- **KPI Computation:** ~2-5 min
- **SQL Analytics:** ~1-3 min
- **PySpark ETL:** ~5-10 min (scales with cluster size)
- **GenAI Response:** ~2-5 seconds per query
- **API Latency:** <100ms for cached queries

## Security Considerations

1. **API Keys:** Stored in `.env` (not committed to Git)
2. **Data Privacy:** No PII in processed data
3. **API Authentication:** Add API keys/tokens for production
4. **Cloud Security:** Use IAM roles, VPC for AWS/Azure

## Future Enhancements

1. **Real-time Processing:** Kafka + Spark Streaming
2. **Advanced ML:** Predictive demand modeling
3. **Dashboard:** Interactive web dashboard (Streamlit/Dash)
4. **Monitoring:** Prometheus + Grafana
5. **CI/CD:** GitHub Actions for automated deployment





