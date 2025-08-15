#!/usr/bin/env python3
"""
Initialize database with default users for testing
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import uuid
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

async def init_users():
    """Initialize database with default users"""
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'test_database')]
    
    # Default users to create
    default_users = [
        {
            "id": str(uuid.uuid4()),
            "email": "admin@learningfwiend.com",
            "username": "admin",
            "full_name": "System Administrator",
            "role": "admin",
            "department": None,
            "hashed_password": hash_password("NewAdmin123!"),
            "is_temporary_password": True,
            "first_login_required": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "password_updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "instructor@learningfwiend.com",
            "username": "instructor",
            "full_name": "Test Instructor",
            "role": "instructor",
            "department": "Technology",
            "hashed_password": hash_password("Instructor123!"),
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
            "full_name": "Test Student",
            "role": "learner",
            "department": "General",
            "hashed_password": hash_password("Student123!"),
            "is_temporary_password": True,
            "first_login_required": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "password_updated_at": datetime.utcnow()
        }
    ]
    
    print("Initializing database with default users...")
    
    for user in default_users:
        # Check if user already exists
        existing_user = await db.users.find_one({
            "$or": [
                {"username": user["username"]},
                {"email": user["email"]}
            ]
        })
        
        if existing_user:
            print(f"User {user['username']} already exists, skipping...")
        else:
            await db.users.insert_one(user)
            print(f"Created user: {user['username']} ({user['role']})")
    
    # Create some default categories
    default_categories = [
        {
            "id": str(uuid.uuid4()),
            "name": "Technology",
            "description": "Technology and programming courses",
            "courseCount": 0,
            "isActive": True,
            "createdBy": default_users[0]["id"],  # Admin
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Business",
            "description": "Business and management courses",
            "courseCount": 0,
            "isActive": True,
            "createdBy": default_users[0]["id"],  # Admin
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Design",
            "description": "Design and creative courses",
            "courseCount": 0,
            "isActive": True,
            "createdBy": default_users[0]["id"],  # Admin
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Marketing",
            "description": "Marketing and sales courses",
            "courseCount": 0,
            "isActive": True,
            "createdBy": default_users[0]["id"],  # Admin
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    print("Creating default categories...")
    for category in default_categories:
        existing_category = await db.categories.find_one({"name": category["name"]})
        if existing_category:
            print(f"Category {category['name']} already exists, skipping...")
        else:
            await db.categories.insert_one(category)
            print(f"Created category: {category['name']}")
    
    print("Database initialization complete!")
    client.close()

if __name__ == "__main__":
    asyncio.run(init_users())