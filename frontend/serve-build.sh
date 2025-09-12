#!/bin/bash
cd /app/frontend

# Build if build directory doesn't exist or if in production
if [ ! -d "build" ] || [ "$NODE_ENV" = "production" ]; then
    echo "Building React app for production..."
    npm run build
    if [ $? -ne 0 ]; then
        echo "Build failed!"
        exit 1
    fi
    echo "Build completed successfully"
fi

# Serve the built app
echo "Starting production server on port 3000..."
exec /app/frontend/node_modules/.bin/serve -s build -l 3000