#!/usr/bin/env python3
"""
URGENT AUTHENTICATION TESTING - REMOTE BACKEND USER ACCOUNTS
LearningFwiend LMS Application - Remote Backend Authentication Testing

OBJECTIVE: Test authentication on the remote backend (https://lms-evolution.emergent.host/api) 
to identify available user accounts for testing.

KNOWN WORKING CREDENTIALS:
- Admin: brayden.t@covesmart.com / Hawaii2020! ✅ (confirmed working)

NEED TO TEST:
1. Test various student account credentials that might exist on this backend
2. If needed, create a test student account using admin credentials
3. Verify quiz functionality works with these accounts

PRIORITY: Get working student credentials so user can test quiz functionality
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using remote backend URL from frontend/.env
BACKEND_URL = "https://lms-evolution.emergent.host/api"
TEST_TIMEOUT = 15

# Known working admin credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

# Potential student credentials to test
POTENTIAL_STUDENT_CREDENTIALS = [
    {"username_or_email": "karlo.student@alder.com", "password": "StudentPermanent123!"},
    {"username_or_email": "brayden.student@learningfwiend.com", "password": "StudentTest123!"},
    {"username_or_email": "test.student@cleanenv.com", "password": "CleanEnv123!"},
    {"username_or_email": "enrollment.test.student@learningfwiend.com", "password": "CleanEnv123!"},
    {"username_or_email": "student@example.com", "password": "Student123!"},
    {"username_or_email": "learner@test.com", "password": "Learner123!"},
    {"username_or_email": "demo.student@lms.com", "password": "Demo123!"},
]

class UrgentAuthTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        self.working_credentials = []
        
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
    
    def test_authentication(self, credentials, user_type="user"):
        """Test authentication with given credentials"""
        test_name = f"Authentication Test - {credentials['username_or_email']}"
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=credentials,
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token:
                    self.auth_tokens[user_type] = token
                    self.working_credentials.append({
                        'credentials': credentials,
                        'user_info': user_info,
                        'token': token
                    })
                    
                    self.log_result(
                        test_name, 
                        'PASS', 
                        f"Authentication successful - Role: {user_info.get('role', 'unknown')}, Name: {user_info.get('full_name', 'unknown')}",
                        {
                            'user_id': user_info.get('id'),
                            'role': user_info.get('role'),
                            'email': user_info.get('email'),
                            'requires_password_change': data.get('requires_password_change', False)
                        }
                    )
                    return True
                else:
                    self.log_result(test_name, 'FAIL', "No access token in response", response.json())
                    return False
            else:
                self.log_result(
                    test_name, 
                    'FAIL', 
                    f"Authentication failed - Status: {response.status_code}",
                    response.text[:200] if response.text else "No response body"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(test_name, 'FAIL', f"Request failed: {str(e)}")
            return False
    
    def create_test_student_account(self, admin_token):
        """Create a test student account using admin credentials"""
        test_name = "Create Test Student Account"
        
        # Generate unique test student credentials
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        test_student_data = {
            "email": f"test.student.{timestamp}@urgenttest.com",
            "username": f"teststudent{timestamp}",
            "full_name": f"Test Student {timestamp}",
            "role": "learner",
            "department": "Testing",
            "temporary_password": "TestStudent123!"
        }
        
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=test_student_data,
                headers=headers,
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Test login with the new student account
                new_credentials = {
                    "username_or_email": test_student_data["email"],
                    "password": test_student_data["temporary_password"]
                }
                
                login_success = self.test_authentication(new_credentials, "new_student")
                
                if login_success:
                    self.log_result(
                        test_name, 
                        'PASS', 
                        f"Successfully created and authenticated test student: {test_student_data['email']}",
                        {
                            'email': test_student_data['email'],
                            'username': test_student_data['username'],
                            'password': test_student_data['temporary_password'],
                            'user_id': user_data.get('id')
                        }
                    )
                    return new_credentials
                else:
                    self.log_result(test_name, 'FAIL', "Created student account but login failed")
                    return None
            else:
                self.log_result(
                    test_name, 
                    'FAIL', 
                    f"Failed to create student account - Status: {response.status_code}",
                    response.text[:200] if response.text else "No response body"
                )
                return None
                
        except requests.exceptions.RequestException as e:
            self.log_result(test_name, 'FAIL', f"Request failed: {str(e)}")
            return None
    
    def test_quiz_access(self, token, user_type):
        """Test basic quiz functionality access"""
        test_name = f"Quiz Access Test - {user_type}"
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test getting courses (needed for quiz access)
            response = requests.get(
                f"{BACKEND_URL}/courses",
                headers=headers,
                timeout=TEST_TIMEOUT
            )
            
            if response.status_code == 200:
                courses = response.json()
                course_count = len(courses)
                
                # Look for courses with quiz content
                quiz_courses = []
                for course in courses[:5]:  # Check first 5 courses
                    if course.get('modules'):
                        for module in course['modules']:
                            if module.get('lessons'):
                                for lesson in module['lessons']:
                                    if lesson.get('type') == 'quiz':
                                        quiz_courses.append(course)
                                        break
                
                self.log_result(
                    test_name, 
                    'PASS', 
                    f"Can access courses ({course_count} total, {len(quiz_courses)} with quizzes)",
                    {
                        'total_courses': course_count,
                        'quiz_courses': len(quiz_courses),
                        'sample_quiz_courses': [c.get('title', 'Unknown') for c in quiz_courses[:3]]
                    }
                )
                return True
            else:
                self.log_result(
                    test_name, 
                    'FAIL', 
                    f"Cannot access courses - Status: {response.status_code}",
                    response.text[:200] if response.text else "No response body"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(test_name, 'FAIL', f"Request failed: {str(e)}")
            return False
    
    def run_urgent_auth_tests(self):
        """Run all urgent authentication tests"""
        print("🚨 URGENT AUTHENTICATION TESTING - REMOTE BACKEND USER ACCOUNTS")
        print("=" * 80)
        print(f"Testing against: {BACKEND_URL}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Test known admin credentials
        print("STEP 1: Testing known admin credentials...")
        admin_success = self.test_authentication(ADMIN_CREDENTIALS, "admin")
        
        if not admin_success:
            print("❌ CRITICAL: Admin credentials failed. Cannot proceed with account creation.")
            return self.generate_report()
        
        admin_token = self.auth_tokens.get("admin")
        print()
        
        # Step 2: Test potential student credentials
        print("STEP 2: Testing potential student credentials...")
        student_found = False
        
        for i, creds in enumerate(POTENTIAL_STUDENT_CREDENTIALS):
            print(f"Testing student credential set {i+1}/{len(POTENTIAL_STUDENT_CREDENTIALS)}...")
            if self.test_authentication(creds, f"student_{i+1}"):
                student_found = True
        
        print()
        
        # Step 3: Create new test student if none found
        if not student_found:
            print("STEP 3: No existing student credentials found. Creating new test student...")
            new_student_creds = self.create_test_student_account(admin_token)
            if new_student_creds:
                student_found = True
        else:
            print("STEP 3: Existing student credentials found. Skipping account creation.")
        
        print()
        
        # Step 4: Test quiz access for working accounts
        print("STEP 4: Testing quiz access for working accounts...")
        
        for user_type, token in self.auth_tokens.items():
            if token:
                self.test_quiz_access(token, user_type)
        
        print()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("🎯 URGENT AUTHENTICATION TEST RESULTS")
        print("=" * 80)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Working Credentials Summary
        if self.working_credentials:
            print("✅ WORKING CREDENTIALS FOUND:")
            print("-" * 40)
            for i, cred_info in enumerate(self.working_credentials, 1):
                creds = cred_info['credentials']
                user_info = cred_info['user_info']
                print(f"{i}. Email: {creds['username_or_email']}")
                print(f"   Password: {creds['password']}")
                print(f"   Role: {user_info.get('role', 'unknown')}")
                print(f"   Name: {user_info.get('full_name', 'unknown')}")
                print(f"   User ID: {user_info.get('id', 'unknown')}")
                if cred_info.get('details', {}).get('requires_password_change'):
                    print(f"   ⚠️  Requires password change on first login")
                print()
        else:
            print("❌ NO WORKING CREDENTIALS FOUND")
            print()
        
        # Detailed Results
        print("📋 DETAILED TEST RESULTS:")
        print("-" * 40)
        for result in self.results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"{status_icon} {result['test']}: {result['message']}")
            if result.get('details') and isinstance(result['details'], dict):
                for key, value in result['details'].items():
                    print(f"   {key}: {value}")
        
        print()
        print("🎯 CONCLUSION:")
        if self.working_credentials:
            admin_creds = [c for c in self.working_credentials if c['user_info'].get('role') == 'admin']
            student_creds = [c for c in self.working_credentials if c['user_info'].get('role') == 'learner']
            
            print(f"✅ Found {len(admin_creds)} working admin account(s)")
            print(f"✅ Found {len(student_creds)} working student account(s)")
            print("✅ User can now proceed with quiz functionality testing")
        else:
            print("❌ No working credentials found. Manual intervention required.")
        
        return {
            'success_rate': success_rate,
            'working_credentials': self.working_credentials,
            'total_tests': total_tests,
            'passed': self.passed,
            'failed': self.failed
        }

def main():
    """Main execution function"""
    tester = UrgentAuthTester()
    results = tester.run_urgent_auth_tests()
    
    # Exit with appropriate code
    if results['working_credentials']:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()