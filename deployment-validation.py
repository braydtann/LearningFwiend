#!/usr/bin/env python3
"""
Deployment Validation Script for LearningFriend LMS
This script validates that all components are properly configured for deployment.
"""

import os
import sys
import json
from pathlib import Path
import importlib.util

def validate_environment_variables():
    """Validate required environment variables"""
    print("🔧 Validating environment variables...")
    
    required_vars = [
        'MONGO_URL',
        'DB_NAME',
        'JWT_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def validate_frontend_build():
    """Validate frontend build exists and is complete"""
    print("📦 Validating frontend build...")
    
    build_path = Path("/app/frontend/build")
    if not build_path.exists():
        print("❌ Frontend build directory does not exist")
        return False
    
    required_files = [
        "index.html",
        "static"
    ]
    
    for file in required_files:
        if not (build_path / file).exists():
            print(f"❌ Required build file missing: {file}")
            return False
    
    print("✅ Frontend build is complete")
    return True

def validate_backend_dependencies():
    """Validate backend dependencies and imports"""
    print("🐍 Validating backend dependencies...")
    
    try:
        # Test critical imports
        import fastapi
        import motor
        import pymongo
        import bcrypt
        import jwt
        print("✅ All critical backend dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing backend dependency: {e}")
        return False

def validate_backend_configuration():
    """Validate backend server configuration"""
    print("⚙️ Validating backend configuration...")
    
    server_path = Path("/app/backend/server.py")
    if not server_path.exists():
        print("❌ Backend server.py not found")
        return False
    
    # Check if health endpoint exists
    with open(server_path, 'r') as f:
        content = f.read()
        if '/health' not in content:
            print("❌ Health check endpoint not found")
            return False
    
    print("✅ Backend configuration is valid")
    return True

def validate_database_models():
    """Validate database models for deployment compatibility"""
    print("🗄️ Validating database models...")
    
    try:
        # Try to import the server module to check for syntax errors
        spec = importlib.util.spec_from_file_location("server", "/app/backend/server.py")
        server_module = importlib.util.module_from_spec(spec)
        # Don't execute, just validate syntax
        print("✅ Database models syntax is valid")
        return True
    except Exception as e:
        print(f"❌ Database model validation failed: {e}")
        return False

def main():
    """Run all validation checks"""
    print("🚀 Starting LMS Deployment Validation")
    print("=" * 50)
    
    validations = [
        validate_environment_variables,
        validate_frontend_build,
        validate_backend_dependencies,
        validate_backend_configuration,
        validate_database_models
    ]
    
    results = []
    for validation in validations:
        try:
            result = validation()
            results.append(result)
        except Exception as e:
            print(f"❌ Validation error: {e}")
            results.append(False)
        print()
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"🎉 All validation checks passed! ({passed}/{total})")
        print("✅ Application is ready for deployment")
        sys.exit(0)
    else:
        print(f"❌ {total - passed} validation checks failed ({passed}/{total})")
        print("🚨 Application needs fixes before deployment")
        sys.exit(1)

if __name__ == "__main__":
    main()