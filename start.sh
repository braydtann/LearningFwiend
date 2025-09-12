#!/bin/bash

# Startup script for production deployment
echo "Starting LMS application..."

# Build frontend if build directory doesn't exist
if [ ! -d "/app/frontend/build" ]; then
    echo "Building frontend for production..."
    cd /app/frontend
    npm run build
    if [ $? -ne 0 ]; then
        echo "Frontend build failed!"
        exit 1
    fi
    echo "Frontend build completed successfully"
fi

# Start backend
echo "Starting backend..."
cd /app/backend
uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Start frontend
echo "Starting frontend..."
cd /app/frontend
exec ./serve-build.sh &
FRONTEND_PID=$!

# Keep both processes running
wait $BACKEND_PID $FRONTEND_PID