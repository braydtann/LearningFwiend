#!/usr/bin/env python3
"""
Script to reset user passwords to expected values for testing.
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def reset_user_passwords():
    """Reset all user passwords to expected values."""
    
    # Define expected passwords
    password_updates = [
        {
            "username": "admin",
            "password": "NewAdmin123!",
            "is_temporary": False,
            "first_login_required": False
        },
        {
            "username": "instructor", 
            "password": "Instructor123!",
            "is_temporary": True,
            "first_login_required": True
        },
        {
            "username": "student",
            "password": "Student123!",
            "is_temporary": True,
            "first_login_required": True
        }
    ]
    
    print("🔄 Resetting user passwords...")
    
    for user_info in password_updates:
        # Hash the password
        hashed_password = pwd_context.hash(user_info["password"])
        
        # Update user in database
        result = await db.users.update_one(
            {"username": user_info["username"]},
            {
                "$set": {
                    "hashed_password": hashed_password,
                    "is_temporary_password": user_info["is_temporary"],
                    "first_login_required": user_info["first_login_required"],
                    "password_updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"✅ Updated {user_info['username']} password")
            print(f"   Password: {user_info['password']}")
            print(f"   Temporary: {user_info['is_temporary']}")
            print(f"   First Login Required: {user_info['first_login_required']}")
        else:
            print(f"❌ Failed to update {user_info['username']} - user not found")
        print()
    
    print("📋 Final User Summary:")
    users = await db.users.find({"username": {"$in": ["admin", "instructor", "student"]}}).to_list(10)
    for user in users:
        print(f"- Username: {user['username']}")
        print(f"  Email: {user['email']}")
        print(f"  Role: {user['role']}")
        print(f"  First Login Required: {user['first_login_required']}")
        print(f"  Is Temporary Password: {user['is_temporary_password']}")
        print("---")

async def main():
    try:
        await reset_user_passwords()
        print("✅ Password reset completed successfully!")
    except Exception as e:
        print(f"❌ Error resetting passwords: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())