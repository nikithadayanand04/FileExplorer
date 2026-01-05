#!/bin/bash

# CryptoFS++ Backend Startup Script

echo "🚀 Starting CryptoFS++ Backend..."

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

source venv/bin/activate

# Check if required packages are installed
echo "📦 Checking dependencies..."
python -c "import fastapi, uvicorn, pydantic_settings" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Some dependencies missing. Installing..."
    pip install fastapi uvicorn pydantic-settings aiofiles python-multipart cryptography opencv-python-headless pillow numpy
fi

# Create necessary directories
mkdir -p uploads encrypted

# Start server
echo "✅ Starting server on http://127.0.0.1:8000"
echo "📖 API docs available at http://127.0.0.1:8000/docs"
echo ""
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

