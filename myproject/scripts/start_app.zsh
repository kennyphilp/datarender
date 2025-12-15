#!/bin/zsh

# Start the Django application
# This script safely starts the Django development server

set -e  # Exit on any error

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/../.venv"

echo "🚀 Starting Django application..."

# Check if virtual environment exists
if [[ ! -d "$VENV_PATH" ]]; then
    echo "❌ Error: Virtual environment not found at $VENV_PATH"
    echo "   Please run: python3.12 -m venv .venv"
    exit 1
fi

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "📦 Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
fi

# Check if server is already running
if lsof -i :8000 -sTCP:LISTEN -n -P >/dev/null 2>&1; then
    echo "⚠️  Server appears to already be running on port 8000"
    echo "   Use './scripts/stop_app.zsh' to stop it first"
    exit 1
fi

# Change to project directory
cd "$PROJECT_ROOT"

# Verify manage.py exists
if [[ ! -f "manage.py" ]]; then
    echo "❌ Error: manage.py not found in $PROJECT_ROOT"
    exit 1
fi

echo "🔍 Running system checks..."
if ! python manage.py check >/dev/null 2>&1; then
    echo "❌ System check failed. Please fix the issues above."
    exit 1
fi

echo "🌐 Starting development server on http://127.0.0.1:8000"
echo "   Press Ctrl+C to stop the server"
echo ""

# Start the server
exec python manage.py runserver