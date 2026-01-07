#!/bin/bash

# Quick start script for the Streamlit frontend

echo "🚕 Starting Urban Mobility Analytics Frontend..."
echo ""

# Check if streamlit is installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the frontend
echo "✅ Starting Streamlit app..."
echo "📱 The app will open in your browser at http://localhost:8501"
echo ""

streamlit run frontend/app.py

