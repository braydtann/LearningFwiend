#!/usr/bin/env python3
"""
Program Access Control Testing Suite for LearningFwiend LMS
Tests the new program access control functionality based on classroom end dates
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta
import time

# Configuration - Using Production Backend URL from frontend/.env
BACKEND_URL = "https://lms-chronology-1.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

class ProgramAccessTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}  # Store auth tokens for different users
        
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
        elif status == 'SKIP':
            print(f"⏭️  {test_name}: {message}")
        else:
            self.failed += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
    
    def authenticate_users(self):
        """Authenticate all required user types"""
        print("🔐 AUTHENTICATION SETUP")
        print("=" * 50)
        
        # Admin login
        try:
            login_data = {
                "username_or_email": "brayden.t@covesmart.com",
                "password": "Hawaii2020!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_tokens['admin'] = data.get('access_token')
                print("✅ Admin authentication successful")
            else:
                print("❌ Admin authentication failed")
                return False
        except Exception as e:
            print(f"❌ Admin authentication error: {e}")
            return False
        
        # Instructor login
        try:
            login_data = {
                "username_or_email": "instructor",
                "password": "Instructor123!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_tokens['instructor'] = data.get('access_token')
                print("✅ Instructor authentication successful")
            else:
                print("❌ Instructor authentication failed")
                return False
        except Exception as e:
            print(f"❌ Instructor authentication error: {e}")
            return False
        
        # Student login
        try:
            login_data = {
                "username_or_email": "test.student@learningfwiend.com",
                "password": "Student123!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_tokens['learner'] = data.get('access_token')
                print("✅ Student authentication successful")
            else:
                print("❌ Student authentication failed")
                return False
        except Exception as e:
            print(f"❌ Student authentication error: {e}")
            return False
        
        return True
    
    def create_test_program(self):
        """Create a test program for access control testing"""
        try:
            program_data = {
                "title": "Program Access Control Test Program",
                "description": "Test program for access control functionality testing",
                "departmentId": None,
                "duration": "8 weeks",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            response = requests.post(
                f"{BACKEND_URL}/programs",
                json=program_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        return None
    
    def create_test_student(self, username_suffix):
        """Create a test student for access control testing"""
        try:
            student_data = {
                "email": f"{username_suffix}@learningfwiend.com",
                "username": username_suffix,
                "full_name": f"Test Student {username_suffix}",
                "role": "learner",
                "department": "Testing",
                "temporary_password": "TestStudent123!"
            }
            
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
                return response.json()
        except requests.exceptions.RequestException:
            pass
        return None
    
    def create_test_classroom_with_program(self, name, program_id, student_id, end_date=None):
        """Create a test classroom with program and student assignment"""
        try:
            # Get instructor ID for classroom trainer
            instructor_response = requests.get(
                f"{BACKEND_URL}/auth/me",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if instructor_response.status_code != 200:
                return None
            
            instructor_data = instructor_response.json()
            instructor_id = instructor_data.get('id')
            
            classroom_data = {
                "name": name,
                "description": f"Test classroom for program access control: {name}",
                "trainerId": instructor_id,
                "courseIds": [],
                "programIds": [program_id],
                "studentIds": [student_id],
                "batchId": None,
                "startDate": None,
                "endDate": end_date.isoformat() if end_date else None,
                "maxStudents": 50,
                "department": "Testing"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/classrooms",
                json=classroom_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        return None
    
    def login_test_student(self, username):
        """Login as a test student and return token"""
        try:
            login_data = {
                "username_or_email": f"{username}@learningfwiend.com",
                "password": "TestStudent123!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('access_token')
        except requests.exceptions.RequestException:
            pass
        return None
    
    def check_program_access(self, program_id, token, expected_reason=None, expected_access=None):
        """Check program access with a specific token"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/programs/{program_id}/access-check",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code == 200:
                data = response.json()
                has_access = data.get('hasAccess')
                reason = data.get('reason')
                message = data.get('message', '')
                
                if expected_access is not None and expected_reason is not None:
                    return has_access == expected_access and reason == expected_reason
                else:
                    return data
        except requests.exceptions.RequestException:
            pass
        return None
    
    def test_admin_instructor_access(self):
        """Test that admins and instructors always have access to programs"""
        # Create test program first
        test_program = self.create_test_program()
        if not test_program:
            self.log_result(
                "Admin/Instructor Access", 
                "SKIP", 
                "Could not create test program for access control test",
                "Program creation required first"
            )
            return False
        
        program_id = test_program.get('id')
        
        # Test admin access
        admin_result = self.check_program_access(program_id, self.auth_tokens['admin'])
        admin_success = (admin_result and 
                        admin_result.get('hasAccess') == True and 
                        admin_result.get('reason') == 'admin_access')
        
        # Test instructor access
        instructor_result = self.check_program_access(program_id, self.auth_tokens['instructor'])
        instructor_success = (instructor_result and 
                             instructor_result.get('hasAccess') == True and 
                             instructor_result.get('reason') == 'admin_access')
        
        if admin_success and instructor_success:
            self.log_result(
                "Admin/Instructor Access", 
                "PASS", 
                "Both admins and instructors correctly get admin_access to programs",
                f"Program ID: {program_id}, Admin: {admin_result}, Instructor: {instructor_result}"
            )
            return program_id
        else:
            self.log_result(
                "Admin/Instructor Access", 
                "FAIL", 
                "Admin or instructor access control not working correctly",
                f"Admin result: {admin_result}, Instructor result: {instructor_result}"
            )
        return None
    
    def test_student_no_classroom(self, program_id):
        """Test that students not enrolled in any classroom with the program are denied access"""
        # Test student access (should be denied - not enrolled)
        student_result = self.check_program_access(program_id, self.auth_tokens['learner'])
        student_success = (student_result and 
                          student_result.get('hasAccess') == False and 
                          student_result.get('reason') == 'not_enrolled')
        
        if student_success:
            self.log_result(
                "Student Not Enrolled", 
                "PASS", 
                "Students not enrolled in any classroom with program correctly denied access",
                f"Program ID: {program_id}, Student result: {student_result}"
            )
            return True
        else:
            self.log_result(
                "Student Not Enrolled", 
                "FAIL", 
                "Student access control not working correctly for non-enrolled students",
                f"Program ID: {program_id}, Expected: denied access, Got: {student_result}"
            )
        return False
    
    def test_student_active_classroom(self, program_id):
        """Test student access when enrolled in classroom with program and no end date or future end date"""
        # Create test student
        test_student = self.create_test_student("active.classroom.student")
        if not test_student:
            self.log_result(
                "Student Active Classroom", 
                "SKIP", 
                "Could not create test student for access control test",
                "Student creation required first"
            )
            return False
        
        student_id = test_student.get('id')
        
        # Test 1: Classroom with no end date (indefinite access)
        classroom_no_end = self.create_test_classroom_with_program(
            "Active Classroom No End Date",
            program_id,
            student_id,
            end_date=None
        )
        
        if classroom_no_end:
            # Login as the test student
            student_token = self.login_test_student("active.classroom.student")
            if student_token:
                access_result = self.check_program_access(program_id, student_token)
                access_success = (access_result and 
                                access_result.get('hasAccess') == True and 
                                access_result.get('reason') == 'classroom_active')
                
                if access_success:
                    self.log_result(
                        "Student Active Classroom (No End Date)", 
                        "PASS", 
                        "Student correctly granted access to program through classroom with no end date",
                        f"Program ID: {program_id}, Result: {access_result}"
                    )
                else:
                    self.log_result(
                        "Student Active Classroom (No End Date)", 
                        "FAIL", 
                        "Student access control failed for classroom with no end date",
                        f"Program ID: {program_id}, Expected: access granted, Got: {access_result}"
                    )
                    return False
            else:
                self.log_result(
                    "Student Active Classroom (No End Date)", 
                    "SKIP", 
                    "Could not login as test student",
                    "Student authentication required"
                )
                return False
        
        # Test 2: Classroom with future end date
        future_date = datetime.utcnow() + timedelta(days=30)
        classroom_future_end = self.create_test_classroom_with_program(
            "Active Classroom Future End Date",
            program_id,
            student_id,
            end_date=future_date
        )
        
        if classroom_future_end:
            access_result = self.check_program_access(program_id, student_token)
            access_success = (access_result and 
                            access_result.get('hasAccess') == True and 
                            access_result.get('reason') == 'classroom_active')
            
            if access_success:
                self.log_result(
                    "Student Active Classroom (Future End Date)", 
                    "PASS", 
                    "Student correctly granted access to program through classroom with future end date",
                    f"Program ID: {program_id}, Result: {access_result}"
                )
                return True
            else:
                self.log_result(
                    "Student Active Classroom (Future End Date)", 
                    "FAIL", 
                    "Student access control failed for classroom with future end date",
                    f"Program ID: {program_id}, Expected: access granted, Got: {access_result}"
                )
        
        return False
    
    def test_student_expired_classroom(self, program_id):
        """Test student access when enrolled in classroom with program but end date has passed"""
        # Create test student
        test_student = self.create_test_student("expired.classroom.student")
        if not test_student:
            self.log_result(
                "Student Expired Classroom", 
                "SKIP", 
                "Could not create test student for access control test",
                "Student creation required first"
            )
            return False
        
        student_id = test_student.get('id')
        
        # Create classroom with past end date
        past_date = datetime.utcnow() - timedelta(days=30)
        classroom_expired = self.create_test_classroom_with_program(
            "Expired Classroom",
            program_id,
            student_id,
            end_date=past_date
        )
        
        if classroom_expired:
            # Login as the test student
            student_token = self.login_test_student("expired.classroom.student")
            if student_token:
                access_result = self.check_program_access(program_id, student_token)
                access_success = (access_result and 
                                access_result.get('hasAccess') == False and 
                                access_result.get('reason') == 'classroom_expired')
                
                if access_success:
                    self.log_result(
                        "Student Expired Classroom", 
                        "PASS", 
                        "Student correctly denied access to program through expired classroom",
                        f"Program ID: {program_id}, Result: {access_result}"
                    )
                    return True
                else:
                    self.log_result(
                        "Student Expired Classroom", 
                        "FAIL", 
                        "Student access control failed for expired classroom",
                        f"Program ID: {program_id}, Expected: access denied, Got: {access_result}"
                    )
            else:
                self.log_result(
                    "Student Expired Classroom", 
                    "SKIP", 
                    "Could not login as test student",
                    "Student authentication required"
                )
        else:
            self.log_result(
                "Student Expired Classroom", 
                "SKIP", 
                "Could not create test classroom with expired end date",
                "Classroom creation required first"
            )
        
        return False
    
    def test_response_structure(self, program_id):
        """Test that program access check returns correct response structure"""
        # Test admin response structure
        try:
            response = requests.get(
                f"{BACKEND_URL}/programs/{program_id}/access-check",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['hasAccess', 'reason']
                optional_fields = ['message', 'activeClassrooms', 'expiredClassrooms']
                
                # Check required fields
                missing_required = [field for field in required_fields if field not in data]
                present_optional = [field for field in optional_fields if field in data]
                
                if not missing_required:
                    self.log_result(
                        "Response Structure", 
                        "PASS", 
                        "Program access check returns correct response structure",
                        f"Required fields: {required_fields}, Optional fields present: {present_optional}, Response: {data}"
                    )
                    return True
                else:
                    self.log_result(
                        "Response Structure", 
                        "FAIL", 
                        "Program access check response missing required fields",
                        f"Missing: {missing_required}, Response: {data}"
                    )
            else:
                self.log_result(
                    "Response Structure", 
                    "FAIL", 
                    f"Program access check failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Response Structure", 
                "FAIL", 
                "Failed to test program access check response structure",
                str(e)
            )
        
        return False
    
    def test_nonexistent_program(self):
        """Test program access check for non-existent program"""
        fake_program_id = "non-existent-program-id-12345"
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/programs/{fake_program_id}/access-check",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 404:
                self.log_result(
                    "Non-existent Program", 
                    "PASS", 
                    "Program access check correctly returns 404 for non-existent program",
                    f"Program ID: {fake_program_id}, Status: 404 Not Found"
                )
                return True
            else:
                self.log_result(
                    "Non-existent Program", 
                    "FAIL", 
                    f"Unexpected status code for non-existent program: {response.status_code}",
                    f"Expected: 404, Got: {response.status_code}, Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Non-existent Program", 
                "FAIL", 
                "Failed to test program access check for non-existent program",
                str(e)
            )
        
        return False
    
    def run_all_tests(self):
        """Run all program access control tests"""
        print("🚀 Starting Program Access Control Testing Suite")
        print(f"📡 Testing Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Authenticate users
        if not self.authenticate_users():
            print("❌ Authentication failed - stopping tests")
            return self.generate_summary()
        
        print("\n🎯 PROGRAM ACCESS CONTROL TESTS")
        print("=" * 70)
        print("Testing program access control functionality based on classroom end dates:")
        print("1. Admin/Instructor Access: GET /api/programs/{program_id}/access-check")
        print("2. Student Access Control based on classroom end dates")
        print("3. Response structure validation")
        print("4. Error handling for non-existent programs")
        print()
        
        # Test 1: Admin/Instructor access (creates test program)
        program_id = self.test_admin_instructor_access()
        
        if program_id:
            # Test 2: Student not enrolled
            self.test_student_no_classroom(program_id)
            
            # Test 3: Student with active classroom
            self.test_student_active_classroom(program_id)
            
            # Test 4: Student with expired classroom
            self.test_student_expired_classroom(program_id)
            
            # Test 5: Response structure
            self.test_response_structure(program_id)
        
        # Test 6: Non-existent program
        self.test_nonexistent_program()
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("📊 PROGRAM ACCESS CONTROL TEST RESULTS SUMMARY")
        print("=" * 80)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['message']}")
        
        print("\n✅ PROGRAM ACCESS CONTROL TESTING COMPLETED")
        return {
            'passed': self.passed,
            'failed': self.failed,
            'success_rate': success_rate,
            'results': self.results
        }

if __name__ == "__main__":
    tester = ProgramAccessTester()
    summary = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if summary['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)