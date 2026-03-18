#!/bin/bash
# Complete build script for ProtoForge macOS .dmg
# Bundles Python dependencies for standalone app

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ROOT_DIR="$(dirname "$PROJECT_DIR")"
VENV_PATH="$PROJECT_DIR/bundled-venv"

echo "=========================================="
echo "🔨 Building ProtoForge Desktop App"
echo "=========================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found"
    exit 1
fi
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "✅ Node.js: $(node --version)"
echo "✅ Python: $(python3 --version)"
echo ""

# Clean previous build
echo "🧹 Cleaning previous build..."
rm -rf "$PROJECT_DIR/dist"
rm -rf "$PROJECT_DIR/bundled-venv"
rm -rf "$PROJECT_DIR/node_modules"
echo ""

# Install Node dependencies
echo "📦 Installing Node dependencies..."
cd "$PROJECT_DIR"
npm install
echo ""

# Generate icon
echo "🎨 Generating app icon..."
if [ -f "$PROJECT_DIR/../assets/logo.png" ]; then
    python3 -c "
from PIL import Image
import os, shutil

iconset_dir = '$PROJECT_DIR/build/icon.iconset'
if os.path.exists(iconset_dir): shutil.rmtree(iconset_dir)
os.makedirs(iconset_dir)

img = Image.open('$PROJECT_DIR/../assets/logo.png')
sizes = [(16,'icon_16x16.png'),(32,'icon_16x16@2x.png'),(32,'icon_32x32.png'),(64,'icon_32x32@2x.png'),(128,'icon_128x128.png'),(256,'icon_128x128@2x.png'),(256,'icon_256x256.png'),(512,'icon_256x256@2x.png'),(512,'icon_512x512.png'),(1024,'icon_512x512@2x.png')]
for size, fn in sizes:
    img.resize((size,size), Image.Resampling.LANCZOS).save(os.path.join(iconset_dir, fn))
"
    iconutil -c icns "$PROJECT_DIR/build/icon.iconset" -o "$PROJECT_DIR/build/icon.icns"
    rm -rf "$PROJECT_DIR/build/icon.iconset"
    echo "✅ Icon generated from logo.png"
fi
echo ""

# Create bundled Python venv
echo "🐍 Creating bundled Python environment..."
python3 -m venv "$VENV_PATH"
source "$VENV_PATH/bin/activate"
pip install --upgrade pip --quiet
echo "📥 Installing ProtoForge dependencies..."
pip install -r "$ROOT_DIR/requirements.txt" --quiet
echo "✅ Python environment created at: bundled-venv/"
echo ""

# Show installed packages
echo "📦 Bundled Python packages:"
pip list | grep -iE "fastapi|uvicorn|flask|langchain" | head -10
echo ""

# Deactivate venv
deactivate

# Build the app
echo "🚀 Building .dmg installer..."
npm run build:dmg

# Show result
echo ""
echo "=========================================="
echo "✅ Build Complete!"
echo "=========================================="
echo ""
echo "📁 Output:"
ls -lh "$PROJECT_DIR/dist/"*.dmg
echo ""
echo "📦 What's included:"
echo "   - Electron app with ProtoForge UI"
echo "   - Bundled Python 3 environment"
echo "   - All Python dependencies (FastAPI, LangChain, etc.)"
echo "   - Backend code and templates"
echo ""
echo "📥 Installation:"
echo "   1. Open the .dmg file"
echo "   2. Drag ProtoForge to Applications"
echo "   3. Launch from Applications"
echo ""
echo "⚠️  First launch (unsigned app):"
echo "   Right-click → Open, then click 'Open Anyway'"
echo "   Or run: xattr -rd com.apple.quarantine /Applications/ProtoForge.app"
echo ""
