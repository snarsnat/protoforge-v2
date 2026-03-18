#!/bin/bash
# Build ProtoForge macOS .dmg installer

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ROOT_DIR="$(dirname "$PROJECT_DIR")"

echo "🔨 Building ProtoForge Desktop App for macOS..."
echo ""

cd "$PROJECT_DIR"

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Install from https://nodejs.org"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install from https://python.org"
    exit 1
fi

echo "✅ Node.js: $(node --version)"
echo "✅ Python: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Generate icon if ImageMagick is available
echo ""
if command -v convert &> /dev/null && command -v iconutil &> /dev/null; then
    echo "🎨 Generating app icon..."
    chmod +x "$SCRIPT_DIR/generate-icon.sh"
    "$SCRIPT_DIR/generate-icon.sh" || echo "⚠️  Icon generation skipped (using placeholder)"
else
    echo "⚠️  ImageMagick or iconutil not found. Using placeholder icon."
    echo "   Install with: brew install imagemagick"
fi

# Build the app
echo ""
echo "🚀 Building .dmg installer..."
npm run build:dmg

# Show result
echo ""
echo "=========================================="
echo "✅ Build complete!"
echo "=========================================="
echo ""
echo "📁 Output location:"
ls -lh "$PROJECT_DIR/dist/"*.dmg 2>/dev/null || echo "   (checking dist folder...)"
echo ""
echo "📦 To install:"
echo "   1. Open the .dmg file"
echo "   2. Drag ProtoForge to Applications"
echo "   3. Launch from Applications folder"
echo ""
echo "⚠️  First launch on macOS:"
echo "   If you see a security warning:"
echo "   - Right-click ProtoForge.app → Open"
echo "   - Click 'Open Anyway' in Security & Privacy"
echo "   - Or run: xattr -rd com.apple.quarantine /Applications/ProtoForge.app"
echo ""
