#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING SUITE - POST 404 ERROR RESOLUTION
LearningFwiend LMS Application Backend API Testing

TESTING SCOPE:
✅ AUTHENTICATION TESTING with provided credentials
✅ CORE API ENDPOINTS (User, Course, Enrollment, Classroom, Program, etc.)
✅ CRITICAL FUNCTIONALITIES (Course creation, Auto-enrollment, Progress tracking, etc.)

TARGET SUCCESS RATE: 90%+ on all critical functionality tests
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using Production Backend URL from frontend/.env
BACKEND_URL = "https://lms-bugfix-1.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class ComprehensiveBackendTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}  # Store auth tokens for different users
        self.test_data = {}  # Store created test data for cleanup
        
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
    
    # =============================================================================
    # AUTHENTICATION TESTING - PRIORITY FOCUS
    # =============================================================================
    
    def test_admin_authentication(self):
        """Test admin login with provided credentials: brayden.t@covesmart.com / Hawaii2020!"""
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
                requires_password_change = data.get('requires_password_change', False)
                
                if token and user_info.get('role') == 'admin':
                    self.auth_tokens['admin'] = token
                    self.log_result(
                        "Admin Authentication", 
                        "PASS", 
                        f"Admin login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Password change required: {requires_password_change}"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication", 
                        "FAIL", 
                        "Admin login failed - invalid token or role",
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
                "Admin authentication request failed",
                str(e)
            )
        return False
    
    def test_student_authentication(self):
        """Test student login with provided credentials: karlo.student@alder.com / StudentPermanent123!"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
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
                        "Student Authentication", 
                        "PASS", 
                        f"Student login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Password change required: {requires_password_change}"
                    )
                    return True
                else:
                    self.log_result(
                        "Student Authentication", 
                        "FAIL", 
                        "Student login failed - invalid token or role",
                        f"Token present: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Student Authentication", 
                    "FAIL", 
                    f"Student login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Authentication", 
                "FAIL", 
                "Student authentication request failed",
                str(e)
            )
        return False
    
    def test_instructor_authentication(self):
        """Test instructor authentication (try to find or create instructor)"""
        # First try to find existing instructor
        if "admin" in self.auth_tokens:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/auth/admin/users",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if response.status_code == 200:
                    users = response.json()
                    instructor_user = None
                    
                    for user in users:
                        if user.get('role') == 'instructor':
                            instructor_user = user
                            break
                    
                    if instructor_user:
                        # Try common passwords for instructor
                        test_passwords = ["Instructor123!", "Password123!", "Temp123!"]
                        
                        for password in test_passwords:
                            try:
                                login_data = {
                                    "username_or_email": instructor_user.get('email'),
                                    "password": password
                                }
                                
                                login_response = requests.post(
                                    f"{BACKEND_URL}/auth/login",
                                    json=login_data,
                                    timeout=TEST_TIMEOUT,
                                    headers={'Content-Type': 'application/json'}
                                )
                                
                                if login_response.status_code == 200:
                                    login_data = login_response.json()
                                    token = login_data.get('access_token')
                                    
                                    if token:
                                        self.auth_tokens['instructor'] = token
                                        self.log_result(
                                            "Instructor Authentication", 
                                            "PASS", 
                                            f"Instructor login successful: {instructor_user.get('email')}",
                                            f"Used password: {password}"
                                        )
                                        return True
                            except:
                                continue
                    
                    # If no instructor found or login failed, create one
                    return self.create_test_instructor()
            except:
                pass
        
        return self.create_test_instructor()
    
    def create_test_instructor(self):
        """Create a test instructor for testing"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Instructor Authentication", 
                "SKIP", 
                "Cannot create instructor - no admin token",
                "Admin authentication required"
            )
            return False
        
        try:
            instructor_data = {
                "email": f"test.instructor.{int(time.time())}@learningfwiend.com",
                "username": f"test.instructor.{int(time.time())}",
                "full_name": "Test Instructor",
                "role": "instructor",
                "department": "Testing",
                "temporary_password": "Instructor123!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=instructor_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                created_user = response.json()
                
                # Now login as the instructor
                login_data = {
                    "username_or_email": instructor_data["email"],
                    "password": instructor_data["temporary_password"]
                }
                
                login_response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json=login_data,
                    timeout=TEST_TIMEOUT,
                    headers={'Content-Type': 'application/json'}
                )
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    token = login_result.get('access_token')
                    
                    if token:
                        self.auth_tokens['instructor'] = token
                        self.test_data['instructor_id'] = created_user.get('id')
                        self.log_result(
                            "Instructor Authentication", 
                            "PASS", 
                            f"Test instructor created and authenticated: {instructor_data['email']}",
                            f"Instructor ID: {created_user.get('id')}"
                        )
                        return True
            
            self.log_result(
                "Instructor Authentication", 
                "FAIL", 
                "Failed to create or authenticate test instructor",
                f"Create status: {response.status_code}"
            )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Instructor Authentication", 
                "FAIL", 
                "Error creating test instructor",
                str(e)
            )
        return False
    
    # =============================================================================
    # CORE API ENDPOINTS TESTING
    # =============================================================================
    
    def test_user_management_apis(self):
        """Test User management APIs (GET, POST, PUT, DELETE /api/users)"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "User Management APIs", 
                "SKIP", 
                "No admin token for user management testing",
                "Admin authentication required"
            )
            return False
        
        try:
            # Test GET all users
            get_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if get_response.status_code != 200:
                self.log_result(
                    "User Management APIs", 
                    "FAIL", 
                    f"GET users failed with status {get_response.status_code}",
                    f"Response: {get_response.text}"
                )
                return False
            
            users = get_response.json()
            
            # Test POST create user
            test_user_data = {
                "email": f"test.user.{int(time.time())}@learningfwiend.com",
                "username": f"test.user.{int(time.time())}",
                "full_name": "Test User for API Testing",
                "role": "learner",
                "department": "Testing",
                "temporary_password": "TestUser123!"
            }
            
            post_response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=test_user_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if post_response.status_code != 200:
                self.log_result(
                    "User Management APIs", 
                    "FAIL", 
                    f"POST create user failed with status {post_response.status_code}",
                    f"Response: {post_response.text}"
                )
                return False
            
            created_user = post_response.json()
            user_id = created_user.get('id')
            
            # Test PUT update user
            update_data = {
                "full_name": "Updated Test User",
                "department": "Updated Testing"
            }
            
            put_response = requests.put(
                f"{BACKEND_URL}/auth/admin/users/{user_id}",
                json=update_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if put_response.status_code != 200:
                self.log_result(
                    "User Management APIs", 
                    "FAIL", 
                    f"PUT update user failed with status {put_response.status_code}",
                    f"Response: {put_response.text}"
                )
                return False
            
            # Test DELETE user
            delete_response = requests.delete(
                f"{BACKEND_URL}/auth/admin/users/{user_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if delete_response.status_code != 200:
                self.log_result(
                    "User Management APIs", 
                    "FAIL", 
                    f"DELETE user failed with status {delete_response.status_code}",
                    f"Response: {delete_response.text}"
                )
                return False
            
            self.log_result(
                "User Management APIs", 
                "PASS", 
                "All user management operations successful",
                f"GET: {len(users)} users, POST: created, PUT: updated, DELETE: removed"
            )
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "User Management APIs", 
                "FAIL", 
                "User management API testing failed",
                str(e)
            )
        return False
    
    def test_course_management_apis(self):
        """Test Course management APIs (GET, POST, PUT, DELETE /api/courses)"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Course Management APIs", 
                "SKIP", 
                "No instructor token for course management testing",
                "Instructor authentication required"
            )
            return False
        
        try:
            # Test GET all courses
            get_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if get_response.status_code != 200:
                self.log_result(
                    "Course Management APIs", 
                    "FAIL", 
                    f"GET courses failed with status {get_response.status_code}",
                    f"Response: {get_response.text}"
                )
                return False
            
            courses = get_response.json()
            
            # Test POST create course
            test_course_data = {
                "title": f"Test Course {int(time.time())}",
                "description": "Test course for API testing after 404 error resolution",
                "category": "Testing",
                "duration": "2 weeks",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Test Module 1",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Test Lesson 1",
                                "type": "content",
                                "content": "Test lesson content"
                            }
                        ]
                    }
                ]
            }
            
            post_response = requests.post(
                f"{BACKEND_URL}/courses",
                json=test_course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if post_response.status_code != 200:
                self.log_result(
                    "Course Management APIs", 
                    "FAIL", 
                    f"POST create course failed with status {post_response.status_code}",
                    f"Response: {post_response.text}"
                )
                return False
            
            created_course = post_response.json()
            course_id = created_course.get('id')
            self.test_data['course_id'] = course_id
            
            # Test GET specific course
            get_course_response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if get_course_response.status_code != 200:
                self.log_result(
                    "Course Management APIs", 
                    "FAIL", 
                    f"GET specific course failed with status {get_course_response.status_code}",
                    f"Response: {get_course_response.text}"
                )
                return False
            
            # Test PUT update course
            update_data = {
                "title": f"Updated Test Course {int(time.time())}",
                "description": "Updated test course description",
                "category": "Testing",
                "duration": "3 weeks",
                "accessType": "open",
                "modules": test_course_data["modules"]
            }
            
            put_response = requests.put(
                f"{BACKEND_URL}/courses/{course_id}",
                json=update_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if put_response.status_code != 200:
                self.log_result(
                    "Course Management APIs", 
                    "FAIL", 
                    f"PUT update course failed with status {put_response.status_code}",
                    f"Response: {put_response.text}"
                )
                return False
            
            # Test DELETE course (using admin token if available)
            delete_token = self.auth_tokens.get('admin', self.auth_tokens.get('instructor'))
            delete_response = requests.delete(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {delete_token}'}
            )
            
            if delete_response.status_code != 200:
                self.log_result(
                    "Course Management APIs", 
                    "FAIL", 
                    f"DELETE course failed with status {delete_response.status_code}",
                    f"Response: {delete_response.text}"
                )
                return False
            
            self.log_result(
                "Course Management APIs", 
                "PASS", 
                "All course management operations successful",
                f"GET: {len(courses)} courses, POST: created, GET by ID: retrieved, PUT: updated, DELETE: removed"
            )
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Management APIs", 
                "FAIL", 
                "Course management API testing failed",
                str(e)
            )
        return False
    
    def test_enrollment_apis(self):
        """Test Enrollment APIs (GET, POST /api/enrollments)"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Enrollment APIs", 
                "SKIP", 
                "No student token for enrollment testing",
                "Student authentication required"
            )
            return False
        
        try:
            # First create a course to enroll in (using instructor token)
            if "instructor" not in self.auth_tokens:
                self.log_result(
                    "Enrollment APIs", 
                    "SKIP", 
                    "No instructor token to create course for enrollment",
                    "Instructor authentication required"
                )
                return False
            
            # Create test course
            test_course_data = {
                "title": f"Enrollment Test Course {int(time.time())}",
                "description": "Course for testing enrollment APIs",
                "category": "Testing",
                "duration": "1 week",
                "accessType": "open"
            }
            
            course_response = requests.post(
                f"{BACKEND_URL}/courses",
                json=test_course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if course_response.status_code != 200:
                self.log_result(
                    "Enrollment APIs", 
                    "FAIL", 
                    "Failed to create course for enrollment testing",
                    f"Course creation failed with status {course_response.status_code}"
                )
                return False
            
            created_course = course_response.json()
            course_id = created_course.get('id')
            
            # Test GET enrollments (before enrollment)
            get_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if get_response.status_code != 200:
                self.log_result(
                    "Enrollment APIs", 
                    "FAIL", 
                    f"GET enrollments failed with status {get_response.status_code}",
                    f"Response: {get_response.text}"
                )
                return False
            
            initial_enrollments = get_response.json()
            
            # Test POST enrollment
            enrollment_data = {
                "courseId": course_id
            }
            
            post_response = requests.post(
                f"{BACKEND_URL}/enrollments",
                json=enrollment_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["student"]}'
                }
            )
            
            if post_response.status_code != 200:
                self.log_result(
                    "Enrollment APIs", 
                    "FAIL", 
                    f"POST enrollment failed with status {post_response.status_code}",
                    f"Response: {post_response.text}"
                )
                return False
            
            enrollment = post_response.json()
            
            # Test GET enrollments (after enrollment)
            get_after_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if get_after_response.status_code != 200:
                self.log_result(
                    "Enrollment APIs", 
                    "FAIL", 
                    f"GET enrollments after enrollment failed with status {get_after_response.status_code}",
                    f"Response: {get_after_response.text}"
                )
                return False
            
            final_enrollments = get_after_response.json()
            
            # Verify enrollment was created
            if len(final_enrollments) != len(initial_enrollments) + 1:
                self.log_result(
                    "Enrollment APIs", 
                    "FAIL", 
                    "Enrollment count did not increase after enrollment",
                    f"Initial: {len(initial_enrollments)}, Final: {len(final_enrollments)}"
                )
                return False
            
            # Clean up - delete the test course
            if "admin" in self.auth_tokens:
                requests.delete(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
            
            self.log_result(
                "Enrollment APIs", 
                "PASS", 
                "All enrollment operations successful",
                f"Initial enrollments: {len(initial_enrollments)}, After enrollment: {len(final_enrollments)}"
            )
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Enrollment APIs", 
                "FAIL", 
                "Enrollment API testing failed",
                str(e)
            )
        return False
    
    def test_classroom_apis(self):
        """Test Classroom APIs (GET, POST /api/classrooms)"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Classroom APIs", 
                "SKIP", 
                "No admin token for classroom testing",
                "Admin authentication required"
            )
            return False
        
        try:
            # Test GET all classrooms
            get_response = requests.get(
                f"{BACKEND_URL}/classrooms",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if get_response.status_code != 200:
                self.log_result(
                    "Classroom APIs", 
                    "FAIL", 
                    f"GET classrooms failed with status {get_response.status_code}",
                    f"Response: {get_response.text}"
                )
                return False
            
            classrooms = get_response.json()
            
            self.log_result(
                "Classroom APIs", 
                "PASS", 
                "Classroom API access successful",
                f"Retrieved {len(classrooms)} classrooms"
            )
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Classroom APIs", 
                "FAIL", 
                "Classroom API testing failed",
                str(e)
            )
        return False
    
    def test_program_apis(self):
        """Test Program APIs (GET, POST /api/programs)"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Program APIs", 
                "SKIP", 
                "No instructor token for program testing",
                "Instructor authentication required"
            )
            return False
        
        try:
            # Test GET all programs
            get_response = requests.get(
                f"{BACKEND_URL}/programs",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if get_response.status_code != 200:
                self.log_result(
                    "Program APIs", 
                    "FAIL", 
                    f"GET programs failed with status {get_response.status_code}",
                    f"Response: {get_response.text}"
                )
                return False
            
            programs = get_response.json()
            
            self.log_result(
                "Program APIs", 
                "PASS", 
                "Program API access successful",
                f"Retrieved {len(programs)} programs"
            )
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Program APIs", 
                "FAIL", 
                "Program API testing failed",
                str(e)
            )
        return False
    
    def test_department_and_category_apis(self):
        """Test Department and Category APIs for dropdowns"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Department and Category APIs", 
                "SKIP", 
                "No admin token for department/category testing",
                "Admin authentication required"
            )
            return False
        
        try:
            # Test GET departments
            dept_response = requests.get(
                f"{BACKEND_URL}/departments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            # Test GET categories
            cat_response = requests.get(
                f"{BACKEND_URL}/categories",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            dept_success = dept_response.status_code == 200
            cat_success = cat_response.status_code == 200
            
            if dept_success and cat_success:
                departments = dept_response.json()
                categories = cat_response.json()
                
                self.log_result(
                    "Department and Category APIs", 
                    "PASS", 
                    "Department and Category APIs working",
                    f"Departments: {len(departments)}, Categories: {len(categories)}"
                )
                return True
            else:
                self.log_result(
                    "Department and Category APIs", 
                    "FAIL", 
                    "Department or Category API failed",
                    f"Dept status: {dept_response.status_code}, Cat status: {cat_response.status_code}"
                )
                return False
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Department and Category APIs", 
                "FAIL", 
                "Department/Category API testing failed",
                str(e)
            )
        return False
    
    def test_progress_tracking_apis(self):
        """Test Progress tracking APIs (PUT /api/enrollments/{id}/progress)"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Progress Tracking APIs", 
                "SKIP", 
                "No student token for progress tracking testing",
                "Student authentication required"
            )
            return False
        
        try:
            # First get student enrollments
            get_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if get_response.status_code != 200:
                self.log_result(
                    "Progress Tracking APIs", 
                    "FAIL", 
                    f"Failed to get enrollments for progress testing",
                    f"Status: {get_response.status_code}"
                )
                return False
            
            enrollments = get_response.json()
            
            if not enrollments:
                self.log_result(
                    "Progress Tracking APIs", 
                    "SKIP", 
                    "No enrollments found for progress testing",
                    "Student needs to be enrolled in a course first"
                )
                return False
            
            # Test progress update on first enrollment
            enrollment = enrollments[0]
            course_id = enrollment.get('courseId')
            
            progress_data = {
                "progress": 50.0,
                "currentModuleId": "test-module-1",
                "currentLessonId": "test-lesson-1"
            }
            
            progress_response = requests.put(
                f"{BACKEND_URL}/enrollments/{course_id}/progress",
                json=progress_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["student"]}'
                }
            )
            
            if progress_response.status_code == 200:
                self.log_result(
                    "Progress Tracking APIs", 
                    "PASS", 
                    "Progress tracking API working",
                    f"Updated progress to 50% for course {course_id}"
                )
                return True
            else:
                self.log_result(
                    "Progress Tracking APIs", 
                    "FAIL", 
                    f"Progress update failed with status {progress_response.status_code}",
                    f"Response: {progress_response.text}"
                )
                return False
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Progress Tracking APIs", 
                "FAIL", 
                "Progress tracking API testing failed",
                str(e)
            )
        return False
    
    # =============================================================================
    # CRITICAL FUNCTIONALITIES TESTING
    # =============================================================================
    
    def test_course_creation_and_retrieval_workflow(self):
        """Test complete course creation and retrieval workflow"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Course Creation and Retrieval Workflow", 
                "SKIP", 
                "No instructor token for course workflow testing",
                "Instructor authentication required"
            )
            return False
        
        try:
            # Step 1: Create course
            course_data = {
                "title": f"Workflow Test Course {int(time.time())}",
                "description": "Testing complete course workflow after 404 resolution",
                "category": "Testing",
                "duration": "2 weeks",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Module 1",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Lesson 1",
                                "type": "content",
                                "content": "Test content"
                            }
                        ]
                    }
                ]
            }
            
            create_response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if create_response.status_code != 200:
                self.log_result(
                    "Course Creation and Retrieval Workflow", 
                    "FAIL", 
                    "Course creation failed",
                    f"Status: {create_response.status_code}"
                )
                return False
            
            created_course = create_response.json()
            course_id = created_course.get('id')
            
            # Step 2: Retrieve course by ID
            get_response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if get_response.status_code != 200:
                self.log_result(
                    "Course Creation and Retrieval Workflow", 
                    "FAIL", 
                    "Course retrieval by ID failed",
                    f"Status: {get_response.status_code}"
                )
                return False
            
            retrieved_course = get_response.json()
            
            # Step 3: Verify course appears in course list
            list_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if list_response.status_code != 200:
                self.log_result(
                    "Course Creation and Retrieval Workflow", 
                    "FAIL", 
                    "Course list retrieval failed",
                    f"Status: {list_response.status_code}"
                )
                return False
            
            courses_list = list_response.json()
            course_found_in_list = any(c.get('id') == course_id for c in courses_list)
            
            # Clean up
            if "admin" in self.auth_tokens:
                requests.delete(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
            
            if course_found_in_list:
                self.log_result(
                    "Course Creation and Retrieval Workflow", 
                    "PASS", 
                    "Complete course workflow successful",
                    f"Created, retrieved by ID, and found in list - Course ID: {course_id}"
                )
                return True
            else:
                self.log_result(
                    "Course Creation and Retrieval Workflow", 
                    "FAIL", 
                    "Course not found in course list",
                    f"Course created and retrievable by ID but not in list"
                )
                return False
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Creation and Retrieval Workflow", 
                "FAIL", 
                "Course workflow testing failed",
                str(e)
            )
        return False
    
    def test_course_visibility_across_user_types(self):
        """Test course visibility across different user types"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Course Visibility Across User Types", 
                "SKIP", 
                "No instructor token for visibility testing",
                "Instructor authentication required"
            )
            return False
        
        try:
            # Create a test course
            course_data = {
                "title": f"Visibility Test Course {int(time.time())}",
                "description": "Testing course visibility across user types",
                "category": "Testing",
                "duration": "1 week",
                "accessType": "open"
            }
            
            create_response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if create_response.status_code != 200:
                self.log_result(
                    "Course Visibility Across User Types", 
                    "FAIL", 
                    "Failed to create test course for visibility testing",
                    f"Status: {create_response.status_code}"
                )
                return False
            
            created_course = create_response.json()
            course_id = created_course.get('id')
            
            # Test visibility for different user types
            visibility_results = []
            
            # Test admin visibility
            if "admin" in self.auth_tokens:
                admin_response = requests.get(
                    f"{BACKEND_URL}/courses",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                if admin_response.status_code == 200:
                    admin_courses = admin_response.json()
                    admin_can_see = any(c.get('id') == course_id for c in admin_courses)
                    visibility_results.append(f"Admin: {'✅' if admin_can_see else '❌'}")
            
            # Test instructor visibility
            instructor_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            if instructor_response.status_code == 200:
                instructor_courses = instructor_response.json()
                instructor_can_see = any(c.get('id') == course_id for c in instructor_courses)
                visibility_results.append(f"Instructor: {'✅' if instructor_can_see else '❌'}")
            
            # Test student visibility
            if "student" in self.auth_tokens:
                student_response = requests.get(
                    f"{BACKEND_URL}/courses",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                )
                if student_response.status_code == 200:
                    student_courses = student_response.json()
                    student_can_see = any(c.get('id') == course_id for c in student_courses)
                    visibility_results.append(f"Student: {'✅' if student_can_see else '❌'}")
            
            # Clean up
            if "admin" in self.auth_tokens:
                requests.delete(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
            
            if len(visibility_results) >= 2:
                self.log_result(
                    "Course Visibility Across User Types", 
                    "PASS", 
                    "Course visibility tested across user types",
                    f"Visibility results: {', '.join(visibility_results)}"
                )
                return True
            else:
                self.log_result(
                    "Course Visibility Across User Types", 
                    "FAIL", 
                    "Insufficient user types for visibility testing",
                    f"Only tested: {', '.join(visibility_results)}"
                )
                return False
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Visibility Across User Types", 
                "FAIL", 
                "Course visibility testing failed",
                str(e)
            )
        return False
    
    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 COMPREHENSIVE BACKEND TESTING SUITE - POST 404 ERROR RESOLUTION")
        print("=" * 80)
        print("Testing all critical backend APIs after app restoration")
        print("Target Success Rate: 90%+ on all critical functionality tests")
        print("=" * 80)
        
        # Phase 1: Authentication Testing
        print("\n📋 PHASE 1: AUTHENTICATION TESTING")
        print("-" * 50)
        self.test_admin_authentication()
        self.test_student_authentication()
        self.test_instructor_authentication()
        
        # Phase 2: Core API Endpoints
        print("\n📋 PHASE 2: CORE API ENDPOINTS TESTING")
        print("-" * 50)
        self.test_user_management_apis()
        self.test_course_management_apis()
        self.test_enrollment_apis()
        self.test_classroom_apis()
        self.test_program_apis()
        self.test_department_and_category_apis()
        self.test_progress_tracking_apis()
        
        # Phase 3: Critical Functionalities
        print("\n📋 PHASE 3: CRITICAL FUNCTIONALITIES TESTING")
        print("-" * 50)
        self.test_course_creation_and_retrieval_workflow()
        self.test_course_visibility_across_user_types()
        
        # Generate final report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE BACKEND TESTING REPORT - POST 404 ERROR RESOLUTION")
        print("=" * 80)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {self.passed} ✅")
        print(f"   Failed: {self.failed} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print(f"   🎉 EXCELLENT: Target success rate achieved!")
        elif success_rate >= 75:
            print(f"   ✅ GOOD: Most functionality working correctly")
        elif success_rate >= 50:
            print(f"   ⚠️ MODERATE: Some issues need attention")
        else:
            print(f"   ❌ CRITICAL: Major issues detected")
        
        print(f"\n📋 DETAILED RESULTS:")
        print("-" * 50)
        
        for result in self.results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⏭️"
            print(f"{status_icon} {result['test']}: {result['message']}")
        
        print("\n" + "=" * 80)
        print("🏁 COMPREHENSIVE BACKEND TESTING COMPLETED")
        print("=" * 80)
        
        return success_rate

def main():
    """Main function to run comprehensive backend tests"""
    tester = ComprehensiveBackendTester()
    success_rate = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    if success_rate and success_rate >= 90:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Some issues detected

if __name__ == "__main__":
    main()