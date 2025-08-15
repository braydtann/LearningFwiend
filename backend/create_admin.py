#!/usr/bin/env python3
"""
Script to create a default admin user for the LMS system.
Run this script to create an initial admin user for testing.
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
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def create_admin_user():
    """Create Brayden T as the system administrator."""
    
    # Check if admin already exists
    existing_admin = await db.users.find_one({"email": "brayden.t@covesmart.com"})
    if existing_admin:
        print("❌ Admin user (Brayden T) already exists!")
        return
    
    # Admin user details
    admin_data = {
        "id": str(uuid.uuid4()),
        "email": "brayden.t@covesmart.com",
        "username": "brayden.t@covesmart.com",
        "full_name": "Brayden T",
        "role": "admin",
        "department": "Administration",
        "hashed_password": pwd_context.hash("Hawaii2020!"),
        "is_temporary_password": False,  # Not temporary - user specified
        "first_login_required": False,   # Don't force password change
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "password_updated_at": datetime.utcnow()
    }
    
    # Insert admin user
    await db.users.insert_one(admin_data)
    
    print("✅ System administrator (Brayden T) created successfully!")
    print("\n📋 Admin Credentials:")
    print("   Name: Brayden T")
    print("   Username: brayden.t@covesmart.com")
    print("   Email: brayden.t@covesmart.com")
    print("   Password: Hawaii2020!")
    print("\n✅ Admin can login immediately with these credentials!")
    
    # Also create some sample users
    sample_users = [
        {
            "id": str(uuid.uuid4()),
            "email": "instructor@learningfwiend.com",
            "username": "instructor",
            "full_name": "Jane Instructor",
            "role": "instructor",
            "department": "Computer Science",
            "hashed_password": pwd_context.hash("Instructor123!"),
            "is_temporary_password": True,
            "first_login_required": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "password_updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "student@learningfwiend.com",
            "username": "student",
            "full_name": "John Student",
            "role": "learner",
            "department": "Computer Science",
            "hashed_password": pwd_context.hash("Student123!"),
            "is_temporary_password": True,
            "first_login_required": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "password_updated_at": datetime.utcnow()
        }
    ]
    
    # Insert sample users
    await db.users.insert_many(sample_users)
    
    print("\n✅ Sample users created:")
    print("   Instructor - username: instructor, password: Instructor123!")
    print("   Student - username: student, password: Student123!")
    print("\n🔐 All users have temporary passwords and must change them on first login.")

async def main():
    try:
        await create_admin_user()
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())