#!/bin/bash
# Bundle Python with dependencies for ProtoForge Desktop App

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ROOT_DIR="$(dirname "$PROJECT_DIR")"
VENV_DIR="$PROJECT_DIR/python-venv"

echo "🐍 Bundling Python environment for ProtoForge..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

echo "✅ Python: $(python3 --version)"
echo ""

# Remove old venv if exists
if [ -d "$VENV_DIR" ]; then
    echo "🗑️  Removing old virtual environment..."
    rm -rf "$VENV_DIR"
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv "$VENV_DIR"

# Activate and upgrade pip
source "$VENV_DIR/bin/activate"
pip install --upgrade pip

# Install dependencies
echo "📥 Installing ProtoForge dependencies..."
pip install -r "$ROOT_DIR/requirements.txt"

# Verify installations
echo ""
echo "✅ Installed packages:"
pip list

# Create a launcher script
echo ""
echo "📝 Creating launcher script..."
cat > "$PROJECT_DIR/start-backend.sh" << 'LAUNCHER'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/python-venv/bin/activate"
export PYTHONPATH="$SCRIPT_DIR/../backend"
export PROTOFORGE_APP_PATH="$SCRIPT_DIR/.."
cd "$SCRIPT_DIR/.."
python3 -m backend.src.gateway.app
LAUNCHER

chmod +x "$PROJECT_DIR/start-backend.sh"

echo ""
echo "✅ Python environment bundled successfully!"
echo ""
echo "📁 Location: $VENV_DIR"
echo "🚀 Launcher: $PROJECT_DIR/start-backend.sh"
echo ""
echo "⚠️  Note: This bundles Python for development testing."
echo "   For production .dmg, use PyInstaller or similar."
