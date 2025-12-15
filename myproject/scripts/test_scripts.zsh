#!/bin/zsh

# Test script for start/stop functionality
echo "🧪 Testing Django start/stop scripts..."
echo ""

# Ensure no server is running initially
echo "1. Checking initial state..."
if lsof -i :8000 -sTCP:LISTEN -n -P >/dev/null 2>&1; then
    echo "❌ Port 8000 is already in use. Please stop any running servers first."
    exit 1
fi
echo "✅ Port 8000 is free"

# Test stop script when no server is running
echo ""
echo "2. Testing stop script with no server running..."
if ./scripts/stop_app.zsh; then
    echo "✅ Stop script handled no-server case correctly"
else
    echo "❌ Stop script failed when no server was running"
    exit 1
fi

# Test start script
echo ""
echo "3. Testing start script..."
./scripts/start_app.zsh &
START_PID=$!

# Wait for server to start
echo "   Waiting for server to start..."
sleep 5

# Check if server is responding
if curl -s --max-time 5 http://127.0.0.1:8000/ >/dev/null; then
    echo "✅ Server started successfully and is responding"
else
    echo "❌ Server failed to start or is not responding"
    kill $START_PID 2>/dev/null || true
    exit 1
fi

# Test stop script
echo ""
echo "4. Testing stop script with running server..."
if ./scripts/stop_app.zsh; then
    echo "✅ Stop script worked correctly"
else
    echo "❌ Stop script failed"
    exit 1
fi

# Verify server is stopped
echo "   Verifying server is stopped..."
sleep 2
if lsof -i :8000 -sTCP:LISTEN -n -P >/dev/null 2>&1; then
    echo "❌ Server is still running after stop command"
    exit 1
else
    echo "✅ Server stopped successfully"
fi

echo ""
echo "🎉 All tests passed! Start/stop scripts are working correctly."