#!/bin/zsh

# Stop the Django application
# This script safely stops the Django development server

set -e  # Exit on any error

echo "🛑 Stopping Django application..."

# Find Django runserver processes
SERVER_PIDS=$(pgrep -f "python.*manage.py runserver" 2>/dev/null || true)

if [[ -z "$SERVER_PIDS" ]]; then
    echo "ℹ️  No Django development server processes found running"
    exit 0
fi

echo "📋 Found server process(es): $SERVER_PIDS"

# Kill the processes gracefully first
echo "🛡️  Sending SIGTERM to server processes..."
kill -TERM $SERVER_PIDS 2>/dev/null || true

# Wait a bit for graceful shutdown
sleep 3

# Check if processes are still running
REMAINING_PIDS=$(pgrep -f "python.*manage.py runserver" 2>/dev/null || true)
if [[ -n "$REMAINING_PIDS" ]]; then
    echo "⚠️  Processes still running, sending SIGKILL..."
    kill -KILL $REMAINING_PIDS 2>/dev/null || true
    sleep 2

    # Try one more time with a different approach
    STILL_RUNNING=$(pgrep -f "python.*manage.py runserver" 2>/dev/null || true)
    if [[ -n "$STILL_RUNNING" ]]; then
        echo "🔨 Using pkill as fallback..."
        pkill -9 -f "python.*manage.py runserver" 2>/dev/null || true
        sleep 1
    fi
fi

# Final check
FINAL_PIDS=$(pgrep -f "python.*manage.py runserver" 2>/dev/null || true)
if [[ -n "$FINAL_PIDS" ]]; then
    echo "❌ Failed to stop all server processes: $FINAL_PIDS"
    exit 1
fi

# Check if port 8000 is still in use
if lsof -i :8000 -sTCP:LISTEN -n -P >/dev/null 2>&1; then
    echo "⚠️  Port 8000 may still be in use by another process"
else
    echo "✅ Django development server stopped successfully"
fi