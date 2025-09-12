#!/usr/bin/env python3
"""
Debug enrollments to understand the data structure
"""

import requests
import json

# Configuration
BASE_URL = "https://fixfriend.preview.emergentagent.com/api"

# Credentials
admin_creds = {"username_or_email": "brayden.t@covesmart.com", "password": "Hawaii2020!"}
student_creds = {"username_or_email": "karlo.student@alder.com", "password": "StudentPermanent123!"}

def authenticate(credentials):
    response = requests.post(f"{BASE_URL}/auth/login", json=credentials, timeout=10)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def get_enrollments(token, user_type):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/enrollments", headers=headers, timeout=10)
    
    print(f"\n{user_type.upper()} ENROLLMENTS:")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        enrollments = response.json()
        print(f"Count: {len(enrollments)}")
        
        for i, enrollment in enumerate(enrollments):
            print(f"\nEnrollment {i+1}:")
            print(f"  ID: {enrollment.get('id')}")
            print(f"  Course ID: {enrollment.get('courseId')}")
            print(f"  User ID: {enrollment.get('userId')}")
            print(f"  Progress: {enrollment.get('progress', 0)}%")
            print(f"  Status: {enrollment.get('status')}")
            print(f"  Student Name: {enrollment.get('studentName')}")
            print(f"  Course Name: {enrollment.get('courseName')}")
            print(f"  Enrolled At: {enrollment.get('enrolledAt')}")
            print(f"  Completed At: {enrollment.get('completedAt')}")
    else:
        print(f"Error: {response.text}")

def main():
    print("🔍 DEBUGGING ENROLLMENTS DATA")
    print("=" * 50)
    
    # Authenticate both users
    admin_token = authenticate(admin_creds)
    student_token = authenticate(student_creds)
    
    if not admin_token:
        print("❌ Admin authentication failed")
        return
    
    if not student_token:
        print("❌ Student authentication failed")
        return
    
    print("✅ Both users authenticated successfully")
    
    # Get enrollments for both users
    get_enrollments(admin_token, "admin")
    get_enrollments(student_token, "student")

if __name__ == "__main__":
    main()