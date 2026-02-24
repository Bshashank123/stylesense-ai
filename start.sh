#!/bin/bash

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║      ✦ StyleSense AI — Startup        ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check .env file
if [ ! -f ".env" ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Open .env and add your GEMINI_API_KEY before running again."
    echo "   Get your key at: https://aistudio.google.com/app/apikey"
    echo ""
    exit 1
fi

# Check if GEMINI_API_KEY is set
source .env 2>/dev/null
if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your_gemini_api_key_here" ]; then
    echo "❌ GEMINI_API_KEY is not set in .env"
    echo "   Get your key at: https://aistudio.google.com/app/apikey"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

echo ""
echo "✅ Dependencies installed"
echo "🚀 Starting StyleSense AI..."
echo ""
echo "   App:  http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""

# Start server
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
