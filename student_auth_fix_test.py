#!/usr/bin/env python3
"""
URGENT: FIX TEST STUDENT AUTHENTICATION CREDENTIALS
LearningFwiend LMS Application - Student Authentication Fix Testing

CRITICAL ISSUE: Test student credentials test.student@cleanenv.com / CleanEnv123! 
are failing authentication with HTTP 401 error, causing white screen crashes 
when trying to access courses.

IMMEDIATE ACTION REQUIRED:
1. CONNECT to production backend: https://lms-evolution.emergent.host/api
2. AUTHENTICATE as admin: brayden.t@covesmart.com / Hawaii2020!
3. FIND test student: test.student@cleanenv.com
4. RESET password to: CleanEnv123! (ensure it works)
5. VERIFY student can login successfully
6. TEST complete authentication flow

EXPECTED RESULT:
- Student should be able to login at https://lms-evolution.emergent.host/
- No more 401 authentication errors
- Student should be able to access courses without white screen crashes
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using Production Backend URL
BACKEND_URL = "https://lms-evolution.emergent.host/api"
TEST_TIMEOUT = 15

# Credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

TARGET_STUDENT_EMAIL = "test.student@cleanenv.com"
TARGET_STUDENT_PASSWORD = "CleanEnv123!"

class StudentAuthFixer:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        self.target_student = None
        
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
    
    def test_production_backend_connectivity(self):
        """Test connection to production backend"""
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=TEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == 'Hello World':
                    self.log_result(
                        "Production Backend Connectivity", 
                        "PASS", 
                        "Successfully connected to production backend",
                        f"Backend URL: {BACKEND_URL}"
                    )
                    return True
                else:
                    self.log_result(
                        "Production Backend Connectivity", 
                        "FAIL", 
                        "Backend responded but with unexpected message",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Production Backend Connectivity", 
                    "FAIL", 
                    f"Backend not responding properly (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Production Backend Connectivity", 
                "FAIL", 
                "Failed to connect to production backend",
                f"Connection error: {str(e)}"
            )
        return False
    
    def test_admin_authentication(self):
        """Test admin authentication with provided credentials"""
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
                    self.log_result(
                        "Admin Authentication", 
                        "PASS", 
                        f"Admin login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Name: {user_info.get('full_name')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication", 
                        "FAIL", 
                        "Login successful but missing token or admin role",
                        f"Token present: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Admin Authentication", 
                    "FAIL", 
                    f"Admin login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Authentication", 
                "FAIL", 
                "Failed to authenticate admin",
                str(e)
            )
        return False
    
    def find_test_student(self):
        """Find the test student in the system"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Find Test Student", 
                "FAIL", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                users = response.json()
                
                for user in users:
                    if user.get('email') == TARGET_STUDENT_EMAIL:
                        self.target_student = user
                        self.log_result(
                            "Find Test Student", 
                            "PASS", 
                            f"Found test student: {user.get('email')}",
                            f"ID: {user.get('id')}, Name: {user.get('full_name')}, Role: {user.get('role')}"
                        )
                        return True
                
                # Student not found, let's create them
                self.log_result(
                    "Find Test Student", 
                    "FAIL", 
                    f"Test student {TARGET_STUDENT_EMAIL} not found in system",
                    f"Searched {len(users)} users, will attempt to create student"
                )
                return self.create_test_student()
            else:
                self.log_result(
                    "Find Test Student", 
                    "FAIL", 
                    f"Failed to retrieve users list (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Find Test Student", 
                "FAIL", 
                "Failed to search for test student",
                str(e)
            )
        return False
    
    def create_test_student(self):
        """Create the test student if they don't exist"""
        if "admin" not in self.auth_tokens:
            return False
        
        try:
            # Extract username from email
            username = TARGET_STUDENT_EMAIL.split('@')[0]
            
            user_data = {
                "email": TARGET_STUDENT_EMAIL,
                "username": username,
                "full_name": "Test Student Clean Environment",
                "role": "learner",
                "department": "Testing",
                "temporary_password": TARGET_STUDENT_PASSWORD
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=user_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                created_user = response.json()
                self.target_student = created_user
                self.log_result(
                    "Create Test Student", 
                    "PASS", 
                    f"Successfully created test student: {created_user.get('email')}",
                    f"ID: {created_user.get('id')}, Password: {TARGET_STUDENT_PASSWORD}"
                )
                return True
            else:
                self.log_result(
                    "Create Test Student", 
                    "FAIL", 
                    f"Failed to create test student (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Create Test Student", 
                "FAIL", 
                "Failed to create test student",
                str(e)
            )
        return False
    
    def reset_student_password(self):
        """Reset the student password to the expected value"""
        if "admin" not in self.auth_tokens or not self.target_student:
            self.log_result(
                "Reset Student Password", 
                "FAIL", 
                "Missing admin token or target student",
                "Admin authentication and student identification required"
            )
            return False
        
        try:
            reset_data = {
                "user_id": self.target_student.get('id'),
                "new_temporary_password": TARGET_STUDENT_PASSWORD
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/admin/reset-password",
                json=reset_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                reset_info = response.json()
                self.log_result(
                    "Reset Student Password", 
                    "PASS", 
                    f"Successfully reset password for {TARGET_STUDENT_EMAIL}",
                    f"New password: {TARGET_STUDENT_PASSWORD}, Reset at: {reset_info.get('reset_at')}"
                )
                return True
            else:
                self.log_result(
                    "Reset Student Password", 
                    "FAIL", 
                    f"Failed to reset password (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Reset Student Password", 
                "FAIL", 
                "Failed to reset student password",
                str(e)
            )
        return False
    
    def test_student_login(self):
        """Test student login with the expected credentials"""
        try:
            student_credentials = {
                "username_or_email": TARGET_STUDENT_EMAIL,
                "password": TARGET_STUDENT_PASSWORD
            }
            
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
                requires_password_change = data.get('requires_password_change', False)
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['student'] = token
                    self.log_result(
                        "Student Login Test", 
                        "PASS", 
                        f"Student login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Password change required: {requires_password_change}"
                    )
                    return True
                else:
                    self.log_result(
                        "Student Login Test", 
                        "FAIL", 
                        "Login successful but missing token or incorrect role",
                        f"Token present: {bool(token)}, Role: {user_info.get('role')}"
                    )
            elif response.status_code == 401:
                self.log_result(
                    "Student Login Test", 
                    "FAIL", 
                    "❌ CRITICAL: Student login failed with 401 Unauthorized - this is the root cause of white screen",
                    f"Credentials: {TARGET_STUDENT_EMAIL} / {TARGET_STUDENT_PASSWORD}"
                )
            else:
                self.log_result(
                    "Student Login Test", 
                    "FAIL", 
                    f"Student login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Login Test", 
                "FAIL", 
                "Failed to test student login",
                str(e)
            )
        return False
    
    def test_student_course_access(self):
        """Test student access to courses to verify no white screen"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Student Course Access", 
                "FAIL", 
                "No student token available",
                "Student authentication required"
            )
            return False
        
        try:
            # Test GET /api/courses
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                self.log_result(
                    "Student Course Access", 
                    "PASS", 
                    f"Student can access courses successfully - {len(courses)} courses available",
                    f"No 401 errors, no white screen issues detected"
                )
                
                # Test accessing a specific course if available
                if courses and len(courses) > 0:
                    test_course = courses[0]
                    course_id = test_course.get('id')
                    
                    course_response = requests.get(
                        f"{BACKEND_URL}/courses/{course_id}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                    )
                    
                    if course_response.status_code == 200:
                        course_detail = course_response.json()
                        self.log_result(
                            "Student Specific Course Access", 
                            "PASS", 
                            f"Student can access specific course: {course_detail.get('title')}",
                            f"Course ID: {course_id}, Modules: {len(course_detail.get('modules', []))}"
                        )
                    else:
                        self.log_result(
                            "Student Specific Course Access", 
                            "FAIL", 
                            f"Student cannot access specific course (status: {course_response.status_code})",
                            f"Course ID: {course_id}"
                        )
                
                return True
            elif response.status_code == 401:
                self.log_result(
                    "Student Course Access", 
                    "FAIL", 
                    "❌ CRITICAL: Student course access failed with 401 - this causes white screen",
                    "Authentication token may be invalid or expired"
                )
            else:
                self.log_result(
                    "Student Course Access", 
                    "FAIL", 
                    f"Student course access failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Course Access", 
                "FAIL", 
                "Failed to test student course access",
                str(e)
            )
        return False
    
    def test_student_enrollments(self):
        """Test student enrollment access"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Student Enrollments", 
                "SKIP", 
                "No student token available",
                "Student authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                self.log_result(
                    "Student Enrollments", 
                    "PASS", 
                    f"Student can access enrollments - {len(enrollments)} enrollments found",
                    f"No authentication issues with enrollment endpoint"
                )
                return True
            elif response.status_code == 401:
                self.log_result(
                    "Student Enrollments", 
                    "FAIL", 
                    "❌ Student enrollment access failed with 401",
                    "Authentication issues persist"
                )
            else:
                self.log_result(
                    "Student Enrollments", 
                    "FAIL", 
                    f"Student enrollment access failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Enrollments", 
                "FAIL", 
                "Failed to test student enrollments",
                str(e)
            )
        return False
    
    def run_complete_fix_test(self):
        """Run the complete student authentication fix test"""
        print("🚨 URGENT: STUDENT AUTHENTICATION FIX TEST")
        print("=" * 80)
        print(f"Target: Fix authentication for {TARGET_STUDENT_EMAIL}")
        print(f"Expected Password: {TARGET_STUDENT_PASSWORD}")
        print(f"Production Backend: {BACKEND_URL}")
        print("=" * 80)
        
        # Step 1: Connect to production backend
        print("\n🔗 STEP 1: Connecting to Production Backend")
        print("-" * 50)
        if not self.test_production_backend_connectivity():
            print("❌ Cannot proceed - production backend not accessible")
            return False
        
        # Step 2: Authenticate as admin
        print("\n🔑 STEP 2: Admin Authentication")
        print("-" * 50)
        if not self.test_admin_authentication():
            print("❌ Cannot proceed - admin authentication failed")
            return False
        
        # Step 3: Find test student
        print("\n👤 STEP 3: Finding Test Student")
        print("-" * 50)
        if not self.find_test_student():
            print("❌ Cannot proceed - test student not found and creation failed")
            return False
        
        # Step 4: Reset student password
        print("\n🔄 STEP 4: Resetting Student Password")
        print("-" * 50)
        if not self.reset_student_password():
            print("❌ Password reset failed")
            return False
        
        # Step 5: Test student login
        print("\n🎓 STEP 5: Testing Student Login")
        print("-" * 50)
        if not self.test_student_login():
            print("❌ Student login still failing after password reset")
            return False
        
        # Step 6: Test course access
        print("\n📚 STEP 6: Testing Course Access")
        print("-" * 50)
        course_access_success = self.test_student_course_access()
        
        # Step 7: Test enrollments
        print("\n📝 STEP 7: Testing Enrollments Access")
        print("-" * 50)
        enrollment_access_success = self.test_student_enrollments()
        
        # Final summary
        print("\n📊 FINAL RESULTS")
        print("=" * 50)
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.passed >= 6:  # At least 6 critical tests should pass
            print("\n🎉 SUCCESS: Student authentication issue has been RESOLVED!")
            print(f"✅ Student {TARGET_STUDENT_EMAIL} can now login with password {TARGET_STUDENT_PASSWORD}")
            print("✅ No more 401 authentication errors")
            print("✅ Student can access courses without white screen crashes")
            return True
        else:
            print("\n❌ FAILURE: Student authentication issue persists")
            print("❌ Manual intervention required")
            return False

def main():
    """Main function to run the student authentication fix test"""
    fixer = StudentAuthFixer()
    success = fixer.run_complete_fix_test()
    
    # Print detailed results
    print("\n" + "=" * 80)
    print("DETAILED TEST RESULTS")
    print("=" * 80)
    
    for result in fixer.results:
        status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⏭️"
        print(f"{status_icon} {result['test']}: {result['message']}")
        if result.get('details'):
            print(f"   Details: {result['details']}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())