#!/bin/bash
# Database Keep-Alive Startup Script
# This script runs the keep-alive service in the background

echo "🚀 Starting MongoDB Atlas Keep-Alive Service..."

# Navigate to backend directory
cd /app/backend

# Run keep-alive service in background
nohup python3 keep_alive.py > /var/log/keepalive.log 2>&1 &

# Get the process ID
KEEPALIVE_PID=$!
echo $KEEPALIVE_PID > /var/run/keepalive.pid

echo "✅ Keep-alive service started with PID: $KEEPALIVE_PID"
echo "📋 Log file: /var/log/keepalive.log"
echo "🛑 To stop: kill $KEEPALIVE_PID"

# Show initial log output
echo ""
echo "📊 Initial log output:"
sleep 2
tail -n 10 /var/log/keepalive.log