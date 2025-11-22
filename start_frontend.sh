#!/bin/bash

# Start Frontend Script for Camila Call Taker

echo "🚀 Starting Camila Call Taker Frontend..."
echo "=================================="

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env created. Please add your VITE_HEYGEN_API_KEY in frontend/.env"
        echo ""
        read -p "Press Enter to continue or Ctrl+C to exit and add your API key..."
    fi
fi

echo ""
echo "🌐 Starting development server on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="

# Start the dev server
npm run dev

