#!/usr/bin/env python3
"""
PRODUCTION ENVIRONMENT VERIFICATION - LearningFriend LMS
Verify the clean production environment and create test student
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# PRODUCTION Configuration
BACKEND_URL = "https://lms-evolution.emergent.host/api"
TEST_TIMEOUT = 30

# Admin credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class ProductionVerificationTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        
    def log_result(self, test_name, status, message, details=None):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.results.append(result)
        
        if status == 'PASS':
            self.passed += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.failed += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate admin"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'admin':
                    self.auth_tokens['admin'] = token
                    return True
        except Exception as e:
            print(f"❌ Admin authentication failed: {str(e)}")
        return False
    
    def create_test_student(self):
        """Create a test student for the clean environment"""
        print(f"\n👤 CREATING TEST STUDENT FOR CLEAN ENVIRONMENT")
        print("=" * 80)
        
        if not self.authenticate_admin():
            self.log_result(
                "Create Test Student", 
                "FAIL", 
                "Admin authentication failed",
                "Cannot create student without admin access"
            )
            return False
        
        student_data = {
            "email": "test.student@cleanenv.com",
            "username": "test.student.clean",
            "full_name": "Test Student - Clean Environment",
            "role": "learner",
            "department": "Testing",
            "temporary_password": "CleanEnv123!"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=student_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                created_student = response.json()
                
                self.log_result(
                    "Create Test Student", 
                    "PASS", 
                    f"✅ Successfully created test student in clean production environment",
                    f"Student: {created_student.get('full_name')} ({created_student.get('email')})"
                )
                return created_student
            else:
                self.log_result(
                    "Create Test Student", 
                    "FAIL", 
                    f"Failed to create test student (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Create Test Student", 
                "FAIL", 
                "Error creating test student",
                str(e)
            )
        return False
    
    def test_student_login(self):
        """Test student login with the created account"""
        print(f"\n🔑 TESTING STUDENT LOGIN")
        print("=" * 80)
        
        student_credentials = {
            "username_or_email": "test.student@cleanenv.com",
            "password": "CleanEnv123!"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=student_credentials,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['student'] = token
                    
                    self.log_result(
                        "Test Student Login", 
                        "PASS", 
                        f"✅ Student login successful in clean production environment",
                        f"Student: {user_info.get('full_name')} - Token received"
                    )
                    return True
                else:
                    self.log_result(
                        "Test Student Login", 
                        "FAIL", 
                        "Login succeeded but invalid token or role",
                        f"Role: {user_info.get('role')}, Token present: {bool(token)}"
                    )
            else:
                self.log_result(
                    "Test Student Login", 
                    "FAIL", 
                    f"Student login failed (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Test Student Login", 
                "FAIL", 
                "Error during student login",
                str(e)
            )
        return False
    
    def verify_clean_environment(self):
        """Verify the production environment is clean"""
        print(f"\n🔍 VERIFYING CLEAN PRODUCTION ENVIRONMENT")
        print("=" * 80)
        
        if "student" not in self.auth_tokens:
            self.log_result(
                "Verify Clean Environment", 
                "FAIL", 
                "No student token available for verification",
                "Student authentication required"
            )
            return False
        
        try:
            # Check courses available to student
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if courses_response.status_code == 200:
                courses = courses_response.json()
                
                # Check enrollments
                enrollments_response = requests.get(
                    f"{BACKEND_URL}/enrollments",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                )
                
                if enrollments_response.status_code == 200:
                    enrollments = enrollments_response.json()
                    
                    print(f"📊 CLEAN ENVIRONMENT STATUS:")
                    print(f"   📚 Available Courses: {len(courses)}")
                    print(f"   📝 Student Enrollments: {len(enrollments)}")
                    
                    # Show available courses
                    if courses:
                        print(f"   📖 Courses in clean environment:")
                        for course in courses:
                            print(f"      - {course.get('title', 'Unknown')} (ID: {course.get('id')})")
                    
                    self.log_result(
                        "Verify Clean Environment", 
                        "PASS", 
                        f"✅ Clean production environment verified successfully",
                        f"Found {len(courses)} fresh courses, {len(enrollments)} enrollments - environment is clean and ready"
                    )
                    return True
                else:
                    self.log_result(
                        "Verify Clean Environment", 
                        "FAIL", 
                        f"Failed to get enrollments (status: {enrollments_response.status_code})",
                        f"Response: {enrollments_response.text}"
                    )
            else:
                self.log_result(
                    "Verify Clean Environment", 
                    "FAIL", 
                    f"Failed to get courses (status: {courses_response.status_code})",
                    f"Response: {courses_response.text}"
                )
        except Exception as e:
            self.log_result(
                "Verify Clean Environment", 
                "FAIL", 
                "Error verifying clean environment",
                str(e)
            )
        return False
    
    def run_verification(self):
        """Run complete production environment verification"""
        print("🔍 PRODUCTION ENVIRONMENT VERIFICATION - LearningFriend LMS")
        print("=" * 80)
        print("Verifying clean production environment and creating test student")
        print(f"Production Backend: {BACKEND_URL}")
        print("=" * 80)
        
        # Step 1: Create test student
        test_student = self.create_test_student()
        
        # Step 2: Test student login
        student_login_success = False
        if test_student:
            student_login_success = self.test_student_login()
        
        # Step 3: Verify clean environment
        clean_verified = False
        if student_login_success:
            clean_verified = self.verify_clean_environment()
        
        # Final summary
        print(f"\n📊 PRODUCTION VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"✅ Test Student Created: {'SUCCESS' if test_student else 'FAILED'}")
        print(f"✅ Student Login: {'SUCCESS' if student_login_success else 'FAILED'}")
        print(f"✅ Clean Environment Verified: {'SUCCESS' if clean_verified else 'FAILED'}")
        
        if test_student and student_login_success and clean_verified:
            print(f"\n🎉 PRODUCTION ENVIRONMENT VERIFICATION SUCCESSFUL!")
            print(f"   🌐 Production site: https://lms-evolution.emergent.host/")
            print(f"   👤 Test Student: test.student@cleanenv.com / CleanEnv123!")
            print(f"   🔑 Admin: brayden.t@covesmart.com / Hawaii2020!")
            return True
        else:
            print(f"\n❌ PRODUCTION ENVIRONMENT VERIFICATION INCOMPLETE!")
            return False

def main():
    """Main execution function"""
    tester = ProductionVerificationTester()
    
    print("🔍 STARTING PRODUCTION ENVIRONMENT VERIFICATION")
    print("=" * 80)
    
    success = tester.run_verification()
    
    print(f"\n📈 FINAL RESULTS:")
    print(f"   ✅ Tests Passed: {tester.passed}")
    print(f"   ❌ Tests Failed: {tester.failed}")
    print(f"   📊 Success Rate: {(tester.passed / (tester.passed + tester.failed) * 100):.1f}%" if (tester.passed + tester.failed) > 0 else "0.0%")
    
    if success:
        print(f"\n🎉 PRODUCTION VERIFICATION SUCCESSFUL!")
        return 0
    else:
        print(f"\n❌ PRODUCTION VERIFICATION FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())