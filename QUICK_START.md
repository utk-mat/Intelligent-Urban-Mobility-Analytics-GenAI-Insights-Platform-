# ⚡ Quick Start Guide

## What You Need to Do (5 Steps)

### 1️⃣ Install Dependencies
```bash
cd /Users/utkarshbmathur/Blend_All_Projects/Capstone_Project
pip install -r requirements.txt
```

### 2️⃣ Set Up Kaggle
1. Go to https://www.kaggle.com/account
2. Click "Create New API Token"
3. Save `kaggle.json` to `~/.kaggle/kaggle.json`
```bash
mkdir -p ~/.kaggle
# Move your kaggle.json file here
chmod 600 ~/.kaggle/kaggle.json
```

### 3️⃣ Create .env File
Create a file named `.env` in the project root:
```bash
cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
# OR
GEMINI_API_KEY=your-gemini-key-here
EOF
```

**Note:** You only need ONE API key (OpenAI OR Gemini)

### 4️⃣ Run Everything
```bash
python run_all.py
```

This will automatically run all 5 main tasks in sequence.

### 5️⃣ Start the API (Optional)
In a new terminal:
```bash
python 6_cloud_api.py
```

Then visit http://localhost:8000/docs to see the API documentation.

---

## Expected Outputs

After running, you'll have:

✅ **Cleaned Data:** `data/cleaned/cleaned_taxi_data.csv`

✅ **Visualizations:** 5 PNG files in `outputs/visualizations/`
- Monthly revenue trends
- Hourly demand heatmap
- Fare & distance analysis
- Tip distribution
- Trips per hour

✅ **SQL Results:** 8 CSV files in `outputs/sql_results/`

✅ **Processed Data:** Parquet files in `data/processed/`

✅ **Database:** `mobility_analytics.db`

---

## Troubleshooting

**Problem:** Kaggle download fails
```bash
# Verify credentials
cat ~/.kaggle/kaggle.json
```

**Problem:** PySpark fails
```bash
# Install Java
brew install openjdk@8  # Mac
# or
sudo apt-get install openjdk-8-jdk  # Linux

# Verify
java -version
```

**Problem:** GenAI API error
- Check your `.env` file has the correct API key
- Verify you have API credits/quota

**Problem:** Memory error
- Edit `1_data_ingestion_cleaning.py` and reduce `sample_size=100000` to a smaller number

---

## Next Steps

1. **Review Results:** Check `outputs/` directory
2. **Explore Visualizations:** Open PNG files
3. **Test GenAI:** Run `python 5_genai_assistant.py` and ask questions
4. **Use API:** Start `python 6_cloud_api.py` and test endpoints

---

## Full Documentation

- **Detailed Guide:** [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Main README:** [README.md](README.md)

---

**That's it! You're ready to go! 🚀**



