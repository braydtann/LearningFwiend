#!/bin/bash

echo "🏗️  Building LMS Application for Production"

# Build frontend
echo "📦 Building React frontend..."
cd /app/frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    npm install
fi

# Build for production
echo "⚙️  Building production bundle..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed!"
    exit 1
fi

echo "✅ Frontend build completed successfully"

# Verify build directory exists
if [ ! -d "build" ]; then
    echo "❌ Build directory not created!"
    exit 1
fi

echo "📊 Build summary:"
ls -la build/
echo ""
echo "🎉 Application build completed successfully!"
echo "🚀 Ready for deployment"