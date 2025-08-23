#!/usr/bin/env python3
"""
Create new admin and student test accounts for preview testing of Multiple Choice question type rebuild.
This ensures we have fresh accounts without any previous testing data conflicts.
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL for account creation
BACKEND_URL = "https://lms-evolution.emergent.host/api"

def create_test_accounts():
    """Create new admin and student accounts for Multiple Choice testing"""
    
    print("🚀 Creating new test accounts for Multiple Choice question type testing...")
    
    # Generate unique identifiers for this test session
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Test accounts to create
    accounts = [
        {
            "role": "admin", 
            "email": f"mc.admin.{timestamp}@preview.test",
            "password": "MCAdmin123!",
            "firstName": "MC Admin",
            "lastName": "Test Account",
            "description": "Admin account for Multiple Choice question type testing"
        },
        {
            "role": "learner",
            "email": f"mc.student.{timestamp}@preview.test", 
            "password": "MCStudent123!",
            "firstName": "MC Student",
            "lastName": "Test Account",
            "description": "Student account for Multiple Choice question type testing"
        }
    ]
    
    created_accounts = []
    
    for account in accounts:
        try:
            print(f"\n📝 Creating {account['role']} account: {account['email']}")
            
            # Create account payload
            account_data = {
                "email": account["email"],
                "password": account["password"],
                "firstName": account["firstName"],
                "lastName": account["lastName"],
                "role": account["role"],
                "firstLoginRequired": False  # Set to False so accounts are ready to use
            }
            
            # Make API request to create account
            response = requests.post(
                f"{BACKEND_URL}/auth/register",
                headers={"Content-Type": "application/json"},
                json=account_data,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ SUCCESS: {account['role']} account created successfully")
                print(f"   📧 Email: {account['email']}")
                print(f"   🔐 Password: {account['password']}")
                print(f"   🆔 User ID: {result.get('user', {}).get('id', 'N/A')}")
                
                created_accounts.append({
                    "role": account["role"],
                    "email": account["email"],
                    "password": account["password"],
                    "user_id": result.get('user', {}).get('id'),
                    "status": "created"
                })
                
            elif response.status_code == 400:
                # Account might already exist, try to verify credentials
                print(f"⚠️  Account may already exist, attempting to verify credentials...")
                
                login_response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    headers={"Content-Type": "application/json"},
                    json={
                        "email": account["email"],
                        "password": account["password"]
                    },
                    timeout=30
                )
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    print(f"✅ VERIFIED: Account exists and credentials work")
                    print(f"   📧 Email: {account['email']}")
                    print(f"   🔐 Password: {account['password']}")
                    print(f"   🆔 User ID: {login_result.get('user', {}).get('id', 'N/A')}")
                    
                    created_accounts.append({
                        "role": account["role"], 
                        "email": account["email"],
                        "password": account["password"],
                        "user_id": login_result.get('user', {}).get('id'),
                        "status": "verified_existing"
                    })
                else:
                    print(f"❌ FAILED: Cannot create or verify account")
                    print(f"   Status: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            else:
                print(f"❌ FAILED: Account creation failed")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ ERROR creating {account['role']} account: {str(e)}")
    
    # Summary
    print(f"\n📊 ACCOUNT CREATION SUMMARY:")
    print(f"{'='*60}")
    
    if created_accounts:
        print(f"✅ Successfully created/verified {len(created_accounts)} accounts:")
        
        for acc in created_accounts:
            print(f"\n🔹 {acc['role'].upper()} ACCOUNT:")
            print(f"   📧 Email: {acc['email']}")
            print(f"   🔐 Password: {acc['password']}")
            print(f"   🆔 ID: {acc['user_id']}")
            print(f"   📊 Status: {acc['status']}")
            
        print(f"\n🎯 READY FOR TESTING:")
        print(f"   • Use these accounts to test Multiple Choice question type rebuild")
        print(f"   • Admin account can create courses with Multiple Choice questions")
        print(f"   • Student account can take quizzes and test functionality")
        print(f"   • Both accounts are ready to use (no password change required)")
        
        # Write credentials to file for easy reference
        with open('/app/mc_test_credentials.txt', 'w') as f:
            f.write("MULTIPLE CHOICE TEST CREDENTIALS\n")
            f.write("="*50 + "\n\n")
            for acc in created_accounts:
                f.write(f"{acc['role'].upper()} ACCOUNT:\n")
                f.write(f"Email: {acc['email']}\n")
                f.write(f"Password: {acc['password']}\n")
                f.write(f"User ID: {acc['user_id']}\n")
                f.write(f"Status: {acc['status']}\n\n")
                
        print(f"   📄 Credentials saved to: /app/mc_test_credentials.txt")
        
    else:
        print("❌ No accounts were successfully created or verified")
        return False
        
    return True

if __name__ == "__main__":
    success = create_test_accounts()
    sys.exit(0 if success else 1)