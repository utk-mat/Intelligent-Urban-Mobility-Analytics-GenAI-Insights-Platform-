# Urban Mobility Analytics Frontend

## Overview
This Streamlit-based frontend provides a comprehensive interface for the Intelligent Urban Mobility Analytics & GenAI Insights Platform.

## Features

### 📊 Dashboard Overview
- Key Performance Indicators (KPIs) with real-time metrics
- Quick insights with interactive charts
- Data preview
- Detailed KPI report

### 📈 Visual Analytics
- Pre-generated visualizations from Task 2
- Interactive revenue analysis
- Time pattern analysis with heatmaps
- Geographic insights (if available)
- Custom analysis tools

### 🧮 SQL Insights
- View all SQL query results from Task 3
- Interactive data tables
- Custom visualizations for SQL results
- Multiple visualization types (bar, line, scatter, heatmap)

### ⚡ Spark Analytics
- View PySpark ETL results from Task 4
- Parquet data visualization
- Spark-processed metrics and aggregations

### 🤖 GenAI Chatbot
- Natural language query interface
- Ask questions about mobility data
- Generate monthly summaries
- Get insights and recommendations

## Installation

1. Install dependencies:
```bash
pip install -r ../requirements.txt
```

2. Ensure all tasks (1-4) have been executed to generate data:
```bash
# From project root
python 1_data_ingestion_cleaning.py
python 2_kpi_computation.py
python 3_sql_analytics.py
python 4_pyspark_etl.py
```

## Running the Frontend

From the project root directory:
```bash
streamlit run frontend/app.py
```

Or from the frontend directory:
```bash
cd frontend
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## Requirements

- Python 3.8+
- Streamlit 1.29.0+
- All dependencies from `requirements.txt`
- Data files from Tasks 1-4

## Troubleshooting

### GenAI Chatbot Not Working
- Check if the API key in `5_genai_assistant.py` is valid
- Verify API quota hasn't been exceeded
- Ensure `google-generativeai` package is installed

### Data Not Loading
- Ensure Task 1 has been executed to generate cleaned data
- Check that data files exist in `data/cleaned/`
- Verify file paths in the app configuration

### Visualizations Not Showing
- Run Task 2 to generate visualizations
- Check that `outputs/visualizations/` directory exists

### Spark Results Not Loading
- Ensure PyArrow is installed: `pip install pyarrow`
- Verify Task 4 has been executed
- Check that Parquet files exist in `data/processed/`

## Notes

- The frontend uses caching to improve performance
- Large datasets may take time to load initially
- Some features require specific data columns to be present



