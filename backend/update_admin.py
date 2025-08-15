#!/usr/bin/env python3
"""
Script to update the system administrator.
This script will:
1. Remove the existing admin user
2. Create Brayden T as the new system administrator
3. Set up his credentials with the specified password
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

async def update_system_admin():
    """Remove old admin and create Brayden as new system administrator."""
    
    print("🔄 Updating system administrator...")
    
    # Step 1: Remove existing admin users
    print("\n1️⃣ Removing existing admin users...")
    result = await db.users.delete_many({"role": "admin"})
    if result.deleted_count > 0:
        print(f"   ✅ Removed {result.deleted_count} existing admin user(s)")
    else:
        print("   ℹ️ No existing admin users found")
    
    # Step 2: Create Brayden as new admin
    print("\n2️⃣ Creating Brayden T as new system administrator...")
    
    # New admin user details
    admin_data = {
        "id": str(uuid.uuid4()),
        "email": "brayden.t@covesmart.com",
        "username": "brayden.t@covesmart.com",  # Using email as username
        "full_name": "Brayden T",
        "role": "admin",
        "department": "Administration",
        "hashed_password": pwd_context.hash("Hawaii2020!"),
        "is_temporary_password": False,  # Not temporary since it's user-specified
        "first_login_required": False,   # Don't force password change
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "password_updated_at": datetime.utcnow()
    }
    
    # Insert new admin user
    await db.users.insert_one(admin_data)
    
    print("   ✅ New admin user created successfully!")
    
    # Step 3: Display new admin credentials
    print("\n🎉 System Administrator Updated Successfully!")
    print("\n" + "="*50)
    print("📋 NEW ADMIN CREDENTIALS")
    print("="*50)
    print(f"   Name: {admin_data['full_name']}")
    print(f"   Email: {admin_data['email']}")
    print(f"   Username: {admin_data['username']}")
    print(f"   Password: Hawaii2020!")
    print("="*50)
    print("\n✅ Brayden can now login with these credentials")
    print("🔐 Password is permanent (no forced change required)")
    
    # Optional: Display other users for reference
    print("\n📊 Checking other users in system...")
    other_users = await db.users.find({"role": {"$ne": "admin"}}).to_list(length=None)
    
    if other_users:
        print(f"   Found {len(other_users)} other users:")
        for user in other_users:
            print(f"   - {user.get('full_name', 'Unknown')} ({user.get('email')}) - {user.get('role')}")
    else:
        print("   No other users found in the system")

async def main():
    try:
        await update_system_admin()
    except Exception as e:
        print(f"❌ Error updating admin user: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())