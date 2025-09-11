#!/usr/bin/env python3
"""
Bootstrap script to create initial admin user in production deployment
"""
import requests
import json
from datetime import datetime
import uuid
from passlib.context import CryptContext

# Production backend URL
BACKEND_URL = "https://lms-chronology.emergent.host/api"

# Password hashing setup (same as backend)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    """Create the initial admin user directly via MongoDB or through a special endpoint"""
    
    admin_user_data = {
        "id": str(uuid.uuid4()),
        "email": "brayden.t@covesmart.com",
        "username": "brayden.t", 
        "full_name": "Brayden T - Admin",
        "role": "admin",
        "department": "Administration",
        "password_hash": pwd_context.hash("Hawaii2020!"),
        "is_active": True,
        "first_login_required": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    print("🔧 Creating admin user in production database...")
    print(f"📧 Email: {admin_user_data['email']}")
    print(f"🔑 Password: Hawaii2020!")
    print(f"👑 Role: {admin_user_data['role']}")
    
    # Test if we can connect to the backend first
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is accessible")
        else:
            print(f"⚠️ Backend returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Try to create user via API (this will likely fail due to auth requirement)
    try:
        create_response = requests.post(
            f"{BACKEND_URL}/auth/admin/create-user",
            json={
                "email": admin_user_data["email"],
                "username": admin_user_data["username"],
                "full_name": admin_user_data["full_name"],
                "password": "Hawaii2020!",
                "role": "admin",
                "department": admin_user_data["department"]
            },
            timeout=10
        )
        
        if create_response.status_code == 200:
            print("✅ Admin user created successfully via API!")
            return True
        else:
            print(f"⚠️ API creation failed: {create_response.status_code} - {create_response.text}")
    except Exception as e:
        print(f"⚠️ API creation failed: {e}")
    
    # Since API creation likely failed, provide instructions for manual creation
    print("\n" + "="*60)
    print("🔧 MANUAL ADMIN USER CREATION REQUIRED")
    print("="*60)
    print("Since the API requires authentication, you'll need to create the admin user manually.")
    print("\nOption 1: Database Direct Insert")
    print("If you have access to the MongoDB Atlas database, insert this document into the 'users' collection:")
    print("\n" + json.dumps(admin_user_data, indent=2, default=str))
    
    print("\nOption 2: Use Database Administration Tools")
    print("- Access your MongoDB Atlas dashboard")
    print("- Navigate to your database collections")
    print("- Insert the admin user document into the 'users' collection")
    
    print("\nOption 3: Contact Support")
    print("Contact Emergent support to help bootstrap the initial admin user")
    
    return False

if __name__ == "__main__":
    create_admin_user()