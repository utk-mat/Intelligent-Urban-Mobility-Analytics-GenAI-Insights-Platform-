# 🚀 Execution Guide - Step by Step Instructions

This guide provides detailed step-by-step instructions to execute the entire Urban Mobility Analytics & GenAI Insights Platform.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.9 or higher installed
- [ ] Kaggle account (for dataset access)
- [ ] OpenAI API key OR Google Gemini API key (for GenAI features)
- [ ] AWS account (optional, for cloud deployment)
- [ ] At least 10GB free disk space (for data processing)

---

## 🔧 Step 1: Environment Setup

### 1.1 Install Python Dependencies

```bash
# Navigate to project directory
cd /Users/utkarshbmathur/Blend_All_Projects/Capstone_Project

# Install all required packages
pip install -r requirements.txt
```

**Expected Output:** All packages should install successfully. If you encounter errors:
- For PySpark: Ensure Java 8+ is installed (`java -version`)
- For PostgreSQL: `psycopg2-binary` should work on most systems

### 1.2 Configure Kaggle Authentication

**Option A: Using Kaggle API Token (Recommended)**

1. Go to https://www.kaggle.com/account
2. Click "Create New API Token" - this downloads `kaggle.json`
3. Place the file in `~/.kaggle/kaggle.json` (create directory if needed)

```bash
mkdir -p ~/.kaggle
# Move your downloaded kaggle.json to ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

**Option B: Using Environment Variables**

```bash
export KAGGLE_USERNAME=your_username
export KAGGLE_KEY=your_api_key
```

### 1.3 Configure API Keys

Create a `.env` file in the project root:

```bash
# Create .env file
cat > .env << EOF
# GenAI API Keys (choose one or both)
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here

# AWS Credentials (optional, for cloud deployment)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///mobility_analytics.db
EOF
```

**Note:** You only need ONE of OPENAI_API_KEY or GEMINI_API_KEY for GenAI features.

---

## 📊 Step 2: Execute Tasks in Order

### Task 1: Data Ingestion & Cleaning

```bash
python 1_data_ingestion_cleaning.py
```

**What it does:**
- Downloads NYC Taxi Trip data from Kaggle
- Cleans missing values, invalid data
- Performs feature engineering
- Exports cleaned data to `data/cleaned/cleaned_taxi_data.csv`

**Expected Duration:** 5-15 minutes (depending on dataset size)

**Expected Output:**
```
✓ Loaded X records
✓ Data cleaning complete
✓ Feature engineering complete
✓ Cleaned data exported to: data/cleaned/cleaned_taxi_data.csv
```

**Troubleshooting:**
- If Kaggle download fails: Check your API credentials
- If memory error: Reduce `sample_size` parameter in the script (default: 100,000)

---

### Task 2: KPI Computation & Visualization

```bash
python 2_kpi_computation.py
```

**What it does:**
- Computes all core KPIs (revenue, distance, tips, etc.)
- Creates 5 visualizations:
  - Monthly revenue trends
  - Hourly demand heatmap
  - Fare & distance outliers
  - Tip distribution
  - Trips per hour
- Generates KPI report

**Expected Duration:** 2-5 minutes

**Expected Output:**
- Visualizations in `outputs/visualizations/`
- KPI report in `outputs/kpi_report.txt`

**Files Created:**
- `outputs/visualizations/monthly_revenue_trends.png`
- `outputs/visualizations/hourly_demand_heatmap.png`
- `outputs/visualizations/fare_distance_outliers.png`
- `outputs/visualizations/tip_distribution.png`
- `outputs/visualizations/trips_per_hour.png`
- `outputs/kpi_report.txt`

---

### Task 3: SQL Analytics

```bash
python 3_sql_analytics.py
```

**What it does:**
- Loads cleaned data into SQLite database
- Executes 8 analytical SQL queries
- Saves query results as CSV files

**Expected Duration:** 1-3 minutes

**Expected Output:**
- SQLite database: `mobility_analytics.db`
- Query results in `outputs/sql_results/`

**Files Created:**
- `outputs/sql_results/peak_demand_hours.csv`
- `outputs/sql_results/revenue_by_pickup_zone.csv`
- `outputs/sql_results/top_revenue_days.csv`
- `outputs/sql_results/avg_fare_by_weekday.csv`
- `outputs/sql_results/monthly_growth.csv`
- `outputs/sql_results/peak_vs_offpeak_analysis.csv`
- `outputs/sql_results/weekend_analysis.csv`
- `outputs/sql_results/revenue_per_mile_analysis.csv`

---

### Task 4: PySpark ETL

**Prerequisites:** Java 8+ must be installed

```bash
# Check Java installation
java -version

# Run PySpark ETL
python 4_pyspark_etl.py
```

**What it does:**
- Processes data at scale using Spark
- Computes KPIs using distributed processing
- Writes outputs to Parquet format
- Shows Spark execution plan (DAG)

**Expected Duration:** 5-10 minutes

**Expected Output:**
- Processed data in `data/processed/` (Parquet format)
- Spark execution plan displayed in console

**Files Created:**
- `data/processed/monthly_revenue.parquet`
- `data/processed/demand_by_zone.parquet`
- `data/processed/peak_hour_congestion.parquet`
- `data/processed/high_value_segments.parquet`
- `data/processed/processed_taxi_data.parquet`

**Troubleshooting:**
- If Java not found: Install Java 8+ and set JAVA_HOME
- If Spark fails: Try reducing data size or using `local[2]` instead of `local[*]`

---

### Task 5: GenAI Assistant

```bash
python 5_genai_assistant.py
```

**What it does:**
- Initializes GenAI assistant (OpenAI or Gemini)
- Loads context from previous tasks
- Answers natural language questions
- Generates executive summaries

**Expected Duration:** Interactive (runs until you exit)

**Usage:**
1. Script will test with example questions
2. Then enters interactive mode
3. Type questions like:
   - "What were the busiest pickup zones?"
   - "When is surge demand highest?"
   - "Why did revenue drop in February?"
4. Type `exit` to quit

**Example Session:**
```
Your question: What are the peak hours for trips?
[AI generates answer based on data]

Your question: exit
Goodbye!
```

**Troubleshooting:**
- If API key error: Check your `.env` file
- If rate limit error: Wait a few minutes and try again

---

### Task 6: Cloud API (Optional)

**Option A: Run Locally**

```bash
python 6_cloud_api.py
```

This starts a FastAPI server on `http://localhost:8000`

**Test the API:**
```bash
# In another terminal
curl http://localhost:8000/
curl http://localhost:8000/monthly-revenue
curl http://localhost:8000/peak-hours
curl http://localhost:8000/kpis
```

**Access API Documentation:**
Open browser: http://localhost:8000/docs

**Option B: Deploy to AWS Lambda**

1. Install additional dependencies:
```bash
pip install mangum
```

2. Create Lambda deployment package (see AWS Lambda deployment guide)

3. Deploy using AWS CLI or Serverless Framework

**Option C: Deploy to Azure Functions**

1. Install Azure Functions Core Tools
2. Create function app
3. Deploy using Azure CLI

---

## 🎯 Quick Start (All Tasks)

Run all tasks sequentially:

```bash
# 1. Data Ingestion & Cleaning
python 1_data_ingestion_cleaning.py

# 2. KPI Computation
python 2_kpi_computation.py

# 3. SQL Analytics
python 3_sql_analytics.py

# 4. PySpark ETL
python 4_pyspark_etl.py

# 5. GenAI Assistant (interactive)
python 5_genai_assistant.py

# 6. Cloud API (in separate terminal)
python 6_cloud_api.py
```

---

## 📁 Expected Project Structure After Execution

```
Capstone_Project/
├── data/
│   ├── raw/
│   │   └── raw_taxi_data.csv
│   ├── cleaned/
│   │   └── cleaned_taxi_data.csv
│   └── processed/
│       ├── monthly_revenue.parquet
│       ├── demand_by_zone.parquet
│       └── ...
├── outputs/
│   ├── visualizations/
│   │   ├── monthly_revenue_trends.png
│   │   ├── hourly_demand_heatmap.png
│   │   └── ...
│   ├── sql_results/
│   │   ├── peak_demand_hours.csv
│   │   └── ...
│   ├── kpi_report.txt
│   └── sql_analytics_report.txt
├── mobility_analytics.db
└── [Python scripts]
```

---

## 🔍 Verification Checklist

After completing all tasks, verify:

- [ ] `data/cleaned/cleaned_taxi_data.csv` exists
- [ ] `outputs/visualizations/` contains 5 PNG files
- [ ] `outputs/sql_results/` contains 8 CSV files
- [ ] `data/processed/` contains Parquet files
- [ ] `mobility_analytics.db` exists
- [ ] GenAI assistant responds to questions
- [ ] API server runs on port 8000

---

## 🐛 Common Issues & Solutions

### Issue: Kaggle dataset download fails
**Solution:** 
- Verify Kaggle credentials
- Check internet connection
- Try manual download from Kaggle website

### Issue: Memory error during processing
**Solution:**
- Reduce `sample_size` in Task 1
- Process data in chunks
- Use PySpark for large datasets

### Issue: PySpark fails to start
**Solution:**
- Install Java 8+: `brew install openjdk@8` (Mac) or `apt-get install openjdk-8-jdk` (Linux)
- Set JAVA_HOME: `export JAVA_HOME=/path/to/java`

### Issue: GenAI API errors
**Solution:**
- Verify API key in `.env` file
- Check API quota/balance
- Try alternative API (Gemini if OpenAI fails)

### Issue: Database locked (SQLite)
**Solution:**
- Close any open database connections
- Delete `mobility_analytics.db` and rerun Task 3

---

## 📞 Next Steps

1. **Review Results:** Check all outputs in `outputs/` directory
2. **Explore Visualizations:** Open PNG files in `outputs/visualizations/`
3. **Analyze SQL Results:** Review CSV files in `outputs/sql_results/`
4. **Test GenAI:** Ask more questions in interactive mode
5. **API Testing:** Use API endpoints for integration

---

## 🎓 For GitHub Submission

Before pushing to GitHub:

1. **Create `.gitignore`:**
```bash
cat > .gitignore << EOF
.env
*.db
__pycache__/
*.pyc
data/raw/
data/cleaned/
data/processed/
outputs/
.DS_Store
*.log
EOF
```

2. **Document Execution:**
   - Take screenshots of each task execution
   - Save API responses
   - Document any customizations

3. **Create Architecture Diagram:**
   - Use tools like draw.io or Lucidchart
   - Show data flow from ingestion to API

---

## ✅ Success Criteria

You've successfully completed the project when:

✓ All 6 tasks execute without errors
✓ Visualizations are generated
✓ SQL queries return results
✓ PySpark processes data successfully
✓ GenAI assistant answers questions
✓ API serves endpoints correctly

**Congratulations! 🎉**





