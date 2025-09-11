#!/usr/bin/env python3
"""
Script to create initial admin user using bootstrap endpoint
"""
import requests
import json

def create_admin_via_bootstrap():
    """Create admin user using the bootstrap endpoint"""
    
    # Production backend URL
    BACKEND_URL = "https://lms-chronology.emergent.host/api"
    
    # Admin user credentials
    admin_data = {
        "email": "brayden.t@covesmart.com",
        "password": "Hawaii2020!",
        "full_name": "Brayden T - Admin",
        "username": "brayden.t"
    }
    
    print("🔧 Creating initial admin user via bootstrap endpoint...")
    print(f"📧 Email: {admin_data['email']}")
    print(f"👤 Username: {admin_data['username']}")
    print(f"👑 Role: admin (automatic)")
    print()
    
    try:
        # Call the bootstrap endpoint
        response = requests.post(
            f"{BACKEND_URL}/auth/bootstrap",
            json=admin_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Admin user created successfully!")
            print(f"📧 Admin Email: {result.get('admin_email')}")
            print(f"👤 Admin Username: {result.get('admin_username')}")
            print(f"📝 Message: {result.get('message')}")
            print(f"ℹ️  Note: {result.get('note')}")
            print()
            print("🎉 You can now login to your application with:")
            print(f"   Email: brayden.t@covesmart.com")
            print(f"   Password: Hawaii2020!")
            print()
            print(f"🌐 Login at: https://lms-chronology.emergent.host")
            return True
            
        elif response.status_code == 403:
            error_data = response.json()
            if "already exist" in error_data.get('detail', ''):
                print("ℹ️  Admin user already exists!")
                print("   You can login with your existing credentials:")
                print(f"   Email: brayden.t@covesmart.com")
                print(f"   Password: Hawaii2020!")
                print(f"🌐 Login at: https://lms-chronology.emergent.host")
                return True
            else:
                print(f"❌ Bootstrap endpoint disabled: {error_data.get('detail')}")
                return False
                
        else:
            print(f"❌ Failed to create admin user:")
            print(f"   Status Code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.ConnectionError:
        print("❌ Cannot connect to the backend.")
        print("   Make sure your application is deployed and running.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    create_admin_via_bootstrap()