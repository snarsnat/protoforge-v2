#!/bin/bash
# Generate macOS .icns icon from PNG

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_DIR/build"
ASSETS_DIR="$PROJECT_DIR/../assets"

echo "🔨 Generating ProtoForge app icons..."

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "❌ ImageMagick not found. Install with: brew install imagemagick"
    exit 1
fi

# Create icon directory structure for icnsutil
ICONSET_DIR="$BUILD_DIR/icon.iconset"
mkdir -p "$ICONSET_DIR"

# Source image (use favicon or create from banner)
SOURCE_IMAGE=""

if [ -f "$ASSETS_DIR/icon-512.png" ]; then
    SOURCE_IMAGE="$ASSETS_DIR/icon-512.png"
elif [ -f "$PROJECT_DIR/../favicon.ico" ]; then
    # Convert favicon to PNG first
    convert "$PROJECT_DIR/../favicon.ico[0]" "$BUILD_DIR/source.png"
    SOURCE_IMAGE="$BUILD_DIR/source.png"
else
    echo "❌ No source image found. Please add icon-512.png to assets/ or favicon.ico to root"
    exit 1
fi

echo "📷 Using source image: $SOURCE_IMAGE"

# Generate all required icon sizes
echo "📐 Generating icon sizes..."

# macOS requires these sizes for .icns
convert "$SOURCE_IMAGE" -resize 16x16 "$ICONSET_DIR/icon_16x16.png"
convert "$SOURCE_IMAGE" -resize 32x32 "$ICONSET_DIR/icon_16x16@2x.png"
convert "$SOURCE_IMAGE" -resize 32x32 "$ICONSET_DIR/icon_32x32.png"
convert "$SOURCE_IMAGE" -resize 64x64 "$ICONSET_DIR/icon_32x32@2x.png"
convert "$SOURCE_IMAGE" -resize 128x128 "$ICONSET_DIR/icon_128x128.png"
convert "$SOURCE_IMAGE" -resize 256x256 "$ICONSET_DIR/icon_128x128@2x.png"
convert "$SOURCE_IMAGE" -resize 256x256 "$ICONSET_DIR/icon_256x256.png"
convert "$SOURCE_IMAGE" -resize 512x512 "$ICONSET_DIR/icon_256x256@2x.png"
convert "$SOURCE_IMAGE" -resize 512x512 "$ICONSET_DIR/icon_512x512.png"
convert "$SOURCE_IMAGE" -resize 1024x1024 "$ICONSET_DIR/icon_512x512@2x.png"

echo "✨ Generating .icns file..."

# Use iconutil to create .icns (macOS built-in)
if command -v iconutil &> /dev/null; then
    iconutil -c icns "$ICONSET_DIR" -o "$BUILD_DIR/icon.icns"
    echo "✅ Created icon.icns"
else
    echo "⚠️  iconutil not found. Creating placeholder..."
    # Create a simple placeholder
    cp "$SOURCE_IMAGE" "$BUILD_DIR/icon.png"
    echo "📝 Please manually convert to .icns or install Xcode command line tools"
fi

# Also create PNG version for Windows/Linux builds
convert "$SOURCE_IMAGE" -resize 512x512 "$BUILD_DIR/icon.png"

# Clean up
rm -rf "$ICONSET_DIR"
rm -f "$BUILD_DIR/source.png"

echo "🎉 Icon generation complete!"
echo "📁 Icons saved to: $BUILD_DIR/"
