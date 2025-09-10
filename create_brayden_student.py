#!/usr/bin/env python3
"""
Script to create brayden.student user for testing
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import uuid

# Load environment variables
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def create_brayden_student():
    """Create brayden.student user."""
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": "brayden.student@learningfwiend.com"})
    if existing_user:
        print("❌ brayden.student user already exists!")
        print(f"   User ID: {existing_user['id']}")
        print(f"   Full Name: {existing_user['full_name']}")
        return existing_user
    
    # Student user details
    student_data = {
        "id": str(uuid.uuid4()),
        "email": "brayden.student@learningfwiend.com",
        "username": "brayden.student",
        "full_name": "Brayden Student",
        "role": "learner",
        "department": "Computer Science",
        "hashed_password": pwd_context.hash("Cove1234!"),
        "is_temporary_password": False,  # Not temporary
        "first_login_required": False,   # Don't force password change
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "password_updated_at": datetime.utcnow()
    }
    
    # Insert student user
    await db.users.insert_one(student_data)
    
    print("✅ brayden.student user created successfully!")
    print("\n📋 Student Credentials:")
    print("   Name: Brayden Student")
    print("   Username: brayden.student")
    print("   Email: brayden.student@learningfwiend.com")
    print("   Password: Cove1234!")
    print(f"   User ID: {student_data['id']}")
    
    return student_data

async def main():
    try:
        user = await create_brayden_student()
    except Exception as e:
        print(f"❌ Error creating student user: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())