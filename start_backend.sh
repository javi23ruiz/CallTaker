#!/bin/bash

# Start Backend Script for Camila Call Taker

echo "🚀 Starting Camila Call Taker Backend..."
echo "=================================="

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating it now..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Check if dependencies are installed
echo "📦 Checking dependencies..."
pip install -q -r requirements.txt
pip install -q -r backend/requirements.txt

echo "✅ Dependencies installed"
echo ""
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📖 API docs available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="

# Start the server
python backend/main.py

