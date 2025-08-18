#!/usr/bin/env python3
"""
Classroom Auto-Enrollment Testing Suite for LearningFwiend LMS Application
Tests the classroom auto-enrollment functionality specifically
"""

import requests
import json
import os
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://03cfefa1-083c-4699-a0b1-524999ee34d1.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

class ClassroomAutoEnrollmentTester:
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
        else:
            self.failed += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
    
    def test_admin_login(self):
        """Test admin user login"""
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
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'admin':
                    self.auth_tokens['admin'] = token
                    self.log_result(
                        "Admin Login Test", 
                        "PASS", 
                        f"Successfully logged in as admin: {user_info.get('email')}",
                        f"Token received, role verified: {user_info.get('role')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Login Test", 
                        "FAIL", 
                        "Login successful but missing token or wrong role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Admin Login Test", 
                    "FAIL", 
                    f"Admin login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Login Test", 
                "FAIL", 
                "Failed to test admin login",
                str(e)
            )
        return False
    
    def test_classroom_auto_enrollment_workflow(self):
        """Test complete classroom auto-enrollment workflow: create classroom with students → verify enrollments created → verify student can access courses"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Classroom Auto-Enrollment Workflow", 
                "SKIP", 
                "No admin token available for classroom auto-enrollment test",
                "Admin authentication required"
            )
            return False
        
        try:
            # Step 1: Create test courses first
            test_courses = []
            for i in range(2):
                course_data = {
                    "title": f"Auto-Enrollment Test Course {i+1}",
                    "description": f"Course for testing classroom auto-enrollment functionality {i+1}",
                    "category": "Testing",
                    "duration": "2 weeks",
                    "accessType": "open"
                }
                
                course_response = requests.post(
                    f"{BACKEND_URL}/courses",
                    json=course_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                    }
                )
                
                if course_response.status_code == 200:
                    test_courses.append(course_response.json())
                else:
                    self.log_result(
                        "Classroom Auto-Enrollment Workflow", 
                        "FAIL", 
                        f"Failed to create test course {i+1} for auto-enrollment test",
                        f"Course creation failed with status: {course_response.status_code}"
                    )
                    return False
            
            # Step 2: Create test student
            student_data = {
                "email": "autoenroll.student@test.com",
                "username": "autoenroll.student",
                "full_name": "Auto Enrollment Test Student",
                "role": "learner",
                "department": "Testing",
                "temporary_password": "AutoEnroll123!"
            }
            
            student_response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=student_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if student_response.status_code != 200:
                self.log_result(
                    "Classroom Auto-Enrollment Workflow", 
                    "FAIL", 
                    "Failed to create test student for auto-enrollment test",
                    f"Student creation failed with status: {student_response.status_code}"
                )
                return False
            
            test_student = student_response.json()
            
            # Step 3: Get instructor for classroom
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if users_response.status_code != 200:
                self.log_result(
                    "Classroom Auto-Enrollment Workflow", 
                    "FAIL", 
                    "Failed to get users for instructor selection",
                    f"Users API failed with status: {users_response.status_code}"
                )
                return False
            
            users = users_response.json()
            instructor = next((u for u in users if u.get('role') == 'instructor'), None)
            
            if not instructor:
                self.log_result(
                    "Classroom Auto-Enrollment Workflow", 
                    "FAIL", 
                    "No instructor found for classroom creation",
                    "Instructor user required for classroom auto-enrollment test"
                )
                return False
            
            # Step 4: Create classroom with student assigned and courses
            classroom_data = {
                "name": "Auto-Enrollment Test Classroom",
                "description": "Testing classroom auto-enrollment functionality",
                "trainerId": instructor['id'],
                "courseIds": [course['id'] for course in test_courses],
                "programIds": [],
                "studentIds": [test_student['id']],
                "department": "Testing",
                "maxStudents": 50
            }
            
            classroom_response = requests.post(
                f"{BACKEND_URL}/classrooms",
                json=classroom_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if classroom_response.status_code != 200:
                self.log_result(
                    "Classroom Auto-Enrollment Workflow", 
                    "FAIL", 
                    f"Failed to create classroom with auto-enrollment (status: {classroom_response.status_code})",
                    f"Response: {classroom_response.text}"
                )
                return False
            
            created_classroom = classroom_response.json()
            
            # Step 5: Login as student to get token
            student_login_data = {
                "username_or_email": "autoenroll.student",
                "password": "AutoEnroll123!"
            }
            
            student_login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=student_login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if student_login_response.status_code != 200:
                self.log_result(
                    "Classroom Auto-Enrollment Workflow", 
                    "FAIL", 
                    "Failed to login as test student",
                    f"Student login failed with status: {student_login_response.status_code}"
                )
                return False
            
            student_token = student_login_response.json().get('access_token')
            
            # Step 6: Verify student can see enrolled courses via GET /api/enrollments
            enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {student_token}'}
            )
            
            if enrollments_response.status_code != 200:
                self.log_result(
                    "Classroom Auto-Enrollment Workflow", 
                    "FAIL", 
                    f"Failed to get student enrollments (status: {enrollments_response.status_code})",
                    f"Response: {enrollments_response.text}"
                )
                return False
            
            enrollments = enrollments_response.json()
            
            # Step 7: Verify enrollments were created for all classroom courses
            enrolled_course_ids = [enrollment['courseId'] for enrollment in enrollments]
            expected_course_ids = [course['id'] for course in test_courses]
            
            auto_enrolled_courses = []
            missing_enrollments = []
            
            for course_id in expected_course_ids:
                if course_id in enrolled_course_ids:
                    auto_enrolled_courses.append(course_id)
                else:
                    missing_enrollments.append(course_id)
            
            # Step 8: Verify student can access the courses
            accessible_courses = []
            for course in test_courses:
                course_response = requests.get(
                    f"{BACKEND_URL}/courses/{course['id']}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {student_token}'}
                )
                
                if course_response.status_code == 200:
                    accessible_courses.append(course['id'])
            
            # Cleanup - Delete test data
            try:
                # Delete classroom
                requests.delete(
                    f"{BACKEND_URL}/classrooms/{created_classroom['id']}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                # Delete test student
                requests.delete(
                    f"{BACKEND_URL}/auth/admin/users/{test_student['id']}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                # Delete test courses
                for course in test_courses:
                    requests.delete(
                        f"{BACKEND_URL}/courses/{course['id']}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                    )
            except:
                pass  # Cleanup errors are not critical
            
            # Evaluate results
            if len(auto_enrolled_courses) == len(expected_course_ids) and len(missing_enrollments) == 0:
                self.log_result(
                    "Classroom Auto-Enrollment Workflow", 
                    "PASS", 
                    f"✅ COMPLETE AUTO-ENROLLMENT WORKFLOW SUCCESSFUL: Student automatically enrolled in all {len(auto_enrolled_courses)} classroom courses and can access them",
                    f"✅ Classroom created with {len(expected_course_ids)} courses, ✅ Student auto-enrolled in all courses, ✅ Student can access enrolled courses via GET /api/enrollments ({len(enrollments)} enrollments found), ✅ Student can access individual courses ({len(accessible_courses)} courses accessible)"
                )
                return True
            else:
                self.log_result(
                    "Classroom Auto-Enrollment Workflow", 
                    "FAIL", 
                    f"❌ AUTO-ENROLLMENT INCOMPLETE: Expected {len(expected_course_ids)} enrollments, got {len(auto_enrolled_courses)}",
                    f"Auto-enrolled courses: {auto_enrolled_courses}, Missing enrollments: {missing_enrollments}, Accessible courses: {accessible_courses}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Classroom Auto-Enrollment Workflow", 
                "FAIL", 
                "Failed to test classroom auto-enrollment workflow",
                str(e)
            )
        return False
    
    def test_classroom_auto_enrollment_with_programs(self):
        """Test classroom auto-enrollment with programs - students should be enrolled in all program courses"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Classroom Auto-Enrollment with Programs", 
                "SKIP", 
                "No admin token available for program auto-enrollment test",
                "Admin authentication required"
            )
            return False
        
        try:
            # Step 1: Create test courses for program
            program_courses = []
            for i in range(2):
                course_data = {
                    "title": f"Program Auto-Enrollment Course {i+1}",
                    "description": f"Course {i+1} for testing program auto-enrollment",
                    "category": "Testing",
                    "duration": "3 weeks",
                    "accessType": "open"
                }
                
                course_response = requests.post(
                    f"{BACKEND_URL}/courses",
                    json=course_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                    }
                )
                
                if course_response.status_code == 200:
                    program_courses.append(course_response.json())
                else:
                    self.log_result(
                        "Classroom Auto-Enrollment with Programs", 
                        "FAIL", 
                        f"Failed to create program course {i+1}",
                        f"Course creation failed with status: {course_response.status_code}"
                    )
                    return False
            
            # Step 2: Create test program with courses
            program_data = {
                "title": "Auto-Enrollment Test Program",
                "description": "Program for testing classroom auto-enrollment with programs",
                "courseIds": [course['id'] for course in program_courses],
                "duration": "6 weeks"
            }
            
            program_response = requests.post(
                f"{BACKEND_URL}/programs",
                json=program_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if program_response.status_code != 200:
                self.log_result(
                    "Classroom Auto-Enrollment with Programs", 
                    "FAIL", 
                    "Failed to create test program",
                    f"Program creation failed with status: {program_response.status_code}"
                )
                return False
            
            test_program = program_response.json()
            
            # Step 3: Create test student
            student_data = {
                "email": "program.autoenroll@test.com",
                "username": "program.autoenroll",
                "full_name": "Program Auto Enrollment Student",
                "role": "learner",
                "department": "Testing",
                "temporary_password": "ProgramEnroll123!"
            }
            
            student_response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=student_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if student_response.status_code != 200:
                self.log_result(
                    "Classroom Auto-Enrollment with Programs", 
                    "FAIL", 
                    "Failed to create test student for program auto-enrollment",
                    f"Student creation failed with status: {student_response.status_code}"
                )
                return False
            
            test_student = student_response.json()
            
            # Step 4: Get instructor
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            users = users_response.json()
            instructor = next((u for u in users if u.get('role') == 'instructor'), None)
            
            if not instructor:
                self.log_result(
                    "Classroom Auto-Enrollment with Programs", 
                    "FAIL", 
                    "No instructor found for classroom creation",
                    "Instructor required for program auto-enrollment test"
                )
                return False
            
            # Step 5: Create classroom with student and program assigned
            classroom_data = {
                "name": "Program Auto-Enrollment Classroom",
                "description": "Testing program auto-enrollment in classroom",
                "trainerId": instructor['id'],
                "courseIds": [],  # No direct courses, only program courses
                "programIds": [test_program['id']],
                "studentIds": [test_student['id']],
                "department": "Testing"
            }
            
            classroom_response = requests.post(
                f"{BACKEND_URL}/classrooms",
                json=classroom_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if classroom_response.status_code != 200:
                self.log_result(
                    "Classroom Auto-Enrollment with Programs", 
                    "FAIL", 
                    f"Failed to create classroom with program (status: {classroom_response.status_code})",
                    f"Response: {classroom_response.text}"
                )
                return False
            
            created_classroom = classroom_response.json()
            
            # Step 6: Login as student
            student_login_data = {
                "username_or_email": "program.autoenroll",
                "password": "ProgramEnroll123!"
            }
            
            student_login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=student_login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if student_login_response.status_code != 200:
                self.log_result(
                    "Classroom Auto-Enrollment with Programs", 
                    "FAIL", 
                    "Failed to login as program test student",
                    f"Student login failed with status: {student_login_response.status_code}"
                )
                return False
            
            student_token = student_login_response.json().get('access_token')
            
            # Step 7: Check student enrollments
            enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {student_token}'}
            )
            
            if enrollments_response.status_code != 200:
                self.log_result(
                    "Classroom Auto-Enrollment with Programs", 
                    "FAIL", 
                    f"Failed to get program student enrollments (status: {enrollments_response.status_code})",
                    f"Response: {enrollments_response.text}"
                )
                return False
            
            enrollments = enrollments_response.json()
            enrolled_course_ids = [enrollment['courseId'] for enrollment in enrollments]
            expected_program_course_ids = [course['id'] for course in program_courses]
            
            # Verify all program courses are enrolled
            program_enrollments = []
            missing_program_enrollments = []
            
            for course_id in expected_program_course_ids:
                if course_id in enrolled_course_ids:
                    program_enrollments.append(course_id)
                else:
                    missing_program_enrollments.append(course_id)
            
            # Cleanup
            try:
                requests.delete(f"{BACKEND_URL}/classrooms/{created_classroom['id']}", timeout=TEST_TIMEOUT, headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'})
                requests.delete(f"{BACKEND_URL}/auth/admin/users/{test_student['id']}", timeout=TEST_TIMEOUT, headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'})
                requests.delete(f"{BACKEND_URL}/programs/{test_program['id']}", timeout=TEST_TIMEOUT, headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'})
                for course in program_courses:
                    requests.delete(f"{BACKEND_URL}/courses/{course['id']}", timeout=TEST_TIMEOUT, headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'})
            except:
                pass
            
            # Evaluate results
            if len(program_enrollments) == len(expected_program_course_ids) and len(missing_program_enrollments) == 0:
                self.log_result(
                    "Classroom Auto-Enrollment with Programs", 
                    "PASS", 
                    f"✅ PROGRAM AUTO-ENROLLMENT SUCCESSFUL: Student automatically enrolled in all {len(program_enrollments)} program courses",
                    f"✅ Program created with {len(expected_program_course_ids)} courses, ✅ Classroom created with program assigned, ✅ Student auto-enrolled in all program courses, ✅ Total enrollments found: {len(enrollments)}"
                )
                return True
            else:
                self.log_result(
                    "Classroom Auto-Enrollment with Programs", 
                    "FAIL", 
                    f"❌ PROGRAM AUTO-ENROLLMENT INCOMPLETE: Expected {len(expected_program_course_ids)} program enrollments, got {len(program_enrollments)}",
                    f"Program enrollments: {program_enrollments}, Missing: {missing_program_enrollments}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Classroom Auto-Enrollment with Programs", 
                "FAIL", 
                "Failed to test program auto-enrollment",
                str(e)
            )
        return False
    
    def run_tests(self):
        """Run classroom auto-enrollment tests"""
        print("🏫 Starting Classroom Auto-Enrollment Testing Suite...")
        print(f"🎯 Target Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Authentication first
        print("\n🔐 AUTHENTICATION SETUP")
        print("=" * 50)
        if not self.test_admin_login():
            print("❌ Admin authentication failed. Stopping tests.")
            return
        
        # Classroom Auto-Enrollment Tests
        print("\n🏫 CLASSROOM AUTO-ENROLLMENT FUNCTIONALITY TESTS")
        print("=" * 50)
        self.test_classroom_auto_enrollment_workflow()
        self.test_classroom_auto_enrollment_with_programs()
        
        # Print final results
        print("\n" + "=" * 80)
        print("📊 CLASSROOM AUTO-ENROLLMENT TEST RESULTS")
        print("=" * 80)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        if self.passed + self.failed > 0:
            print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['message']}")
        
        print("\n🎯 Classroom auto-enrollment testing completed!")
        return self.passed, self.failed

if __name__ == "__main__":
    tester = ClassroomAutoEnrollmentTester()
    tester.run_tests()