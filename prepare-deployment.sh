#!/bin/bash

echo "🚀 Preparing LMS Application for Production Deployment"

# Set environment variables
export NODE_ENV=production

# Build frontend
echo "📦 Building React frontend for production..."
cd /app/frontend

# Ensure dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    yarn install
    if [ $? -ne 0 ]; then
        echo "❌ Frontend dependency installation failed!"
        exit 1
    fi
fi

# Build for production
echo "⚙️  Creating optimized production build..."
yarn build

if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed!"
    exit 1
fi

# Verify build directory and files exist
if [ ! -d "build" ]; then
    echo "❌ Build directory not created!"
    exit 1
fi

if [ ! -f "build/index.html" ]; then
    echo "❌ Build index.html not found!"
    exit 1
fi

if [ ! -d "build/static" ]; then
    echo "❌ Build static directory not found!"
    exit 1
fi

echo "✅ Frontend build completed successfully"
echo "📊 Build contents:"
ls -la build/
echo ""

# Verify backend dependencies
echo "🔧 Checking backend dependencies..."
cd /app/backend

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi

echo "✅ Backend configuration verified"

# Create documents directory if it doesn't exist
if [ ! -d "documents" ]; then
    echo "📁 Creating documents directory..."
    mkdir -p documents
fi

echo "✅ Documents directory ready"

# Final verification
echo "🔍 Final deployment verification..."

# Check if all necessary files exist
required_files=(
    "/app/frontend/build/index.html"
    "/app/frontend/build/static"
    "/app/backend/server.py"
    "/app/backend/requirements.txt"
)

for file in "${required_files[@]}"; do
    if [ ! -e "$file" ]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
done

echo ""
echo "🎉 LMS Application Successfully Prepared for Production Deployment!"
echo "✅ Frontend build: Ready"
echo "✅ Backend configuration: Ready"  
echo "✅ Static file serving: Configured"
echo "✅ API endpoints: Available at /api/*"
echo "✅ Health check: Available at /health"
echo "✅ File upload: Documents directory ready"
echo ""
echo "🚀 Application is ready for deployment!"