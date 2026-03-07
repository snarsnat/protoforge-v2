#!/bin/bash
# ProtoForge Setup Script

set -e

echo "⚡ ProtoForge Setup"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Copy config
if [ ! -f config.yaml ]; then
    echo "📝 Creating config.yaml..."
    cp config.example.yaml config.yaml
fi

if [ ! -f extensions_config.json ]; then
    echo "📝 Creating extensions_config.json..."
    cp extensions_config.example.json extensions_config.json
fi

# Create data directory
mkdir -p data/threads

echo "✅ Setup complete!"
echo ""
echo "To run ProtoForge:"
echo "  source .venv/bin/activate"
echo "  python -m src.gateway.app"
echo ""
echo "Then open http://localhost:8001"
