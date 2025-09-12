#!/usr/bin/env python3
"""
Comprehensive Backend Testing Suite for LearningFwiend LMS Application
Focus: Testing APIs that were previously falling back to mockData
"""

import requests
import json
import os
import sys
from datetime import datetime
import time

# Configuration - Using Production Backend URL from frontend/.env
BACKEND_URL = "https://learning-analytics-2.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

class ComprehensiveBackendTester:
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
        elif status == 'FAIL':
            self.failed += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
        else:  # SKIP
            print(f"⏭️ {test_name}: {message}")
    
    def test_admin_login(self):
        """Test admin user login with SPECIFIC admin credentials from review request"""
        try:
            # Test SPECIFIC admin credentials from review request: brayden.t@covesmart.com / Hawaii2020!
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
                        "Admin Authentication Test", 
                        "PASS", 
                        f"✅ ADMIN CREDENTIALS WORKING: {user_info.get('email')} ({user_info.get('full_name')})",
                        f"Token received, role verified: {user_info.get('role')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication Test", 
                        "FAIL", 
                        "🚨 CRITICAL: Login successful but missing token or wrong role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}, Expected: admin"
                    )
            else:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'No error detail provided')
                except:
                    error_detail = response.text
                
                self.log_result(
                    "Admin Authentication Test", 
                    "FAIL", 
                    f"🚨 CRITICAL: Admin credentials FAILED with status {response.status_code}",
                    f"Error: {error_detail}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Authentication Test", 
                "FAIL", 
                "🚨 CRITICAL: Failed to connect to authentication endpoint",
                str(e)
            )
        return False
    
    def test_instructor_login(self):
        """Test instructor user login"""
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
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'instructor':
                    self.auth_tokens['instructor'] = token
                    self.log_result(
                        "Instructor Login Test", 
                        "PASS", 
                        f"Successfully logged in as instructor: {user_info.get('username')}",
                        f"Token received, role verified: {user_info.get('role')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Instructor Login Test", 
                        "FAIL", 
                        "Login successful but missing token or wrong role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Instructor Login Test", 
                    "FAIL", 
                    f"Instructor login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Instructor Login Test", 
                "FAIL", 
                "Failed to test instructor login",
                str(e)
            )
        return False
    
    def test_student_login(self):
        """Test student user login"""
        try:
            login_data = {
                "username_or_email": "comprehensive.test.student",
                "password": "ComprehensiveTest123!"
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
                requires_password_change = data.get('requires_password_change', False)
                
                if token and user_info.get('role') == 'learner':
                    # If password change is required, change it to a permanent password
                    if requires_password_change:
                        change_password_data = {
                            "current_password": "ComprehensiveTest123!",
                            "new_password": "StudentPermanent123!"
                        }
                        
                        change_response = requests.post(
                            f"{BACKEND_URL}/auth/change-password",
                            json=change_password_data,
                            timeout=TEST_TIMEOUT,
                            headers={
                                'Content-Type': 'application/json',
                                'Authorization': f'Bearer {token}'
                            }
                        )
                        
                        if change_response.status_code == 200:
                            # Login again with new password
                            new_login_data = {
                                "username_or_email": "comprehensive.test.student",
                                "password": "StudentPermanent123!"
                            }
                            
                            new_response = requests.post(
                                f"{BACKEND_URL}/auth/login",
                                json=new_login_data,
                                timeout=TEST_TIMEOUT,
                                headers={'Content-Type': 'application/json'}
                            )
                            
                            if new_response.status_code == 200:
                                new_data = new_response.json()
                                new_token = new_data.get('access_token')
                                self.auth_tokens['learner'] = new_token
                                
                                self.log_result(
                                    "Student Login Test", 
                                    "PASS", 
                                    f"Successfully logged in as student with permanent password: {user_info.get('username')}",
                                    f"Token received, role verified: {user_info.get('role')}, password changed from temporary"
                                )
                                return True
                    else:
                        self.auth_tokens['learner'] = token
                        self.log_result(
                            "Student Login Test", 
                            "PASS", 
                            f"Successfully logged in as student: {user_info.get('username')}",
                            f"Token received, role verified: {user_info.get('role')}"
                        )
                        return True
                else:
                    self.log_result(
                        "Student Login Test", 
                        "FAIL", 
                        "Login successful but missing token or wrong role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
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
    
    def test_course_management_comprehensive(self):
        """Test all course management APIs comprehensively"""
        print("\n📚 COMPREHENSIVE COURSE MANAGEMENT APIs TESTING")
        print("-" * 60)
        
        if "instructor" not in self.auth_tokens and "admin" not in self.auth_tokens:
            self.log_result(
                "Course Management Comprehensive", 
                "SKIP", 
                "No instructor or admin token available",
                "Authentication required for course management"
            )
            return False
        
        token = self.auth_tokens.get("instructor") or self.auth_tokens.get("admin")
        
        try:
            # Test 1: Create course
            course_data = {
                "title": "Comprehensive Test Course",
                "description": "Testing course management APIs after mockData cleanup",
                "category": "Testing",
                "duration": "4 weeks",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Module 1: Introduction",
                        "lessons": [
                            {"id": "lesson1", "title": "Welcome", "type": "video"},
                            {"id": "lesson2", "title": "Overview", "type": "text"}
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
                    'Authorization': f'Bearer {token}'
                }
            )
            
            if create_response.status_code != 200:
                self.log_result(
                    "Course Management - Create Course", 
                    "FAIL", 
                    f"Course creation failed with status {create_response.status_code}",
                    f"Response: {create_response.text}"
                )
                return False
            
            created_course = create_response.json()
            course_id = created_course['id']
            
            # Test 2: Get all courses (critical for course listing)
            list_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if list_response.status_code != 200:
                self.log_result(
                    "Course Management - List Courses", 
                    "FAIL", 
                    f"Course listing failed with status {list_response.status_code}",
                    f"Response: {list_response.text}"
                )
                return False
            
            courses = list_response.json()
            course_found = any(c['id'] == course_id for c in courses)
            
            # Test 3: Get course by ID (critical for CourseDetail page)
            detail_response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if detail_response.status_code != 200:
                self.log_result(
                    "Course Management - Get Course by ID", 
                    "FAIL", 
                    f"Course detail retrieval failed with status {detail_response.status_code}",
                    f"Response: {detail_response.text}"
                )
                return False
            
            course_detail = detail_response.json()
            
            # Test 4: Update course
            update_data = {
                "title": "Updated Comprehensive Test Course",
                "description": "Updated description for testing",
                "category": "Testing",
                "duration": "6 weeks",
                "accessType": "open"
            }
            
            update_response = requests.put(
                f"{BACKEND_URL}/courses/{course_id}",
                json=update_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
            )
            
            update_success = update_response.status_code == 200
            
            # Test 5: Delete course (cleanup)
            delete_response = requests.delete(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            delete_success = delete_response.status_code == 200
            
            # Summary
            tests_passed = sum([
                create_response.status_code == 200,
                list_response.status_code == 200 and course_found,
                detail_response.status_code == 200,
                update_success,
                delete_success
            ])
            
            self.log_result(
                "Course Management Comprehensive", 
                "PASS" if tests_passed >= 4 else "FAIL", 
                f"Course management APIs working - {tests_passed}/5 operations successful",
                f"Create: {'✅' if create_response.status_code == 200 else '❌'}, List: {'✅' if course_found else '❌'}, Detail: {'✅' if detail_response.status_code == 200 else '❌'}, Update: {'✅' if update_success else '❌'}, Delete: {'✅' if delete_success else '❌'}"
            )
            
            return tests_passed >= 4
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Management Comprehensive", 
                "FAIL", 
                "Failed to test course management APIs",
                str(e)
            )
        return False
    
    def test_user_management_comprehensive(self):
        """Test all user management APIs comprehensively"""
        print("\n👥 COMPREHENSIVE USER MANAGEMENT APIs TESTING")
        print("-" * 60)
        
        if "admin" not in self.auth_tokens:
            self.log_result(
                "User Management Comprehensive", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required for user management"
            )
            return False
        
        try:
            # Test 1: Get all users
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if users_response.status_code != 200:
                self.log_result(
                    "User Management - Get All Users", 
                    "FAIL", 
                    f"Get users failed with status {users_response.status_code}",
                    f"Response: {users_response.text}"
                )
                return False
            
            users = users_response.json()
            
            # Test 2: Create user
            user_data = {
                "email": "test.user.comprehensive@learningfwiend.com",
                "username": "test.user.comprehensive",
                "full_name": "Test User Comprehensive",
                "role": "learner",
                "department": "Testing",
                "temporary_password": "TestUser123!"
            }
            
            create_response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=user_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if create_response.status_code != 200:
                self.log_result(
                    "User Management - Create User", 
                    "FAIL", 
                    f"User creation failed with status {create_response.status_code}",
                    f"Response: {create_response.text}"
                )
                return False
            
            created_user = create_response.json()
            user_id = created_user['id']
            
            # Test 3: Update user
            update_data = {
                "full_name": "Updated Test User Comprehensive",
                "department": "Updated Testing"
            }
            
            update_response = requests.put(
                f"{BACKEND_URL}/auth/admin/users/{user_id}",
                json=update_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            update_success = update_response.status_code == 200
            
            # Test 4: Reset user password
            reset_data = {
                "user_id": user_id,
                "new_temporary_password": "ResetTest123!"
            }
            
            reset_response = requests.post(
                f"{BACKEND_URL}/auth/admin/reset-password",
                json=reset_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            reset_success = reset_response.status_code == 200
            
            # Test 5: Delete user (cleanup)
            delete_response = requests.delete(
                f"{BACKEND_URL}/auth/admin/users/{user_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            delete_success = delete_response.status_code == 200
            
            # Summary
            tests_passed = sum([
                users_response.status_code == 200,
                create_response.status_code == 200,
                update_success,
                reset_success,
                delete_success
            ])
            
            self.log_result(
                "User Management Comprehensive", 
                "PASS" if tests_passed >= 4 else "FAIL", 
                f"User management APIs working - {tests_passed}/5 operations successful",
                f"List: {'✅' if users_response.status_code == 200 else '❌'}, Create: {'✅' if create_response.status_code == 200 else '❌'}, Update: {'✅' if update_success else '❌'}, Reset: {'✅' if reset_success else '❌'}, Delete: {'✅' if delete_success else '❌'}"
            )
            
            return tests_passed >= 4
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "User Management Comprehensive", 
                "FAIL", 
                "Failed to test user management APIs",
                str(e)
            )
        return False
    
    def test_enrollment_management_comprehensive(self):
        """Test all enrollment APIs comprehensively"""
        print("\n🎓 COMPREHENSIVE ENROLLMENT APIs TESTING")
        print("-" * 60)
        
        if "learner" not in self.auth_tokens:
            self.log_result(
                "Enrollment Management Comprehensive", 
                "SKIP", 
                "No student token available",
                "Student authentication required for enrollment testing"
            )
            return False
        
        try:
            # First get available courses
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["learner"]}'}
            )
            
            if courses_response.status_code != 200 or not courses_response.json():
                self.log_result(
                    "Enrollment Management - Prerequisites", 
                    "FAIL", 
                    "No courses available for enrollment testing",
                    f"Courses API status: {courses_response.status_code}"
                )
                return False
            
            courses = courses_response.json()
            test_course = courses[0]
            
            # Test 1: Create enrollment
            enrollment_data = {
                "courseId": test_course["id"]
            }
            
            enroll_response = requests.post(
                f"{BACKEND_URL}/enrollments",
                json=enrollment_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["learner"]}'
                }
            )
            
            # Handle duplicate enrollment case
            if enroll_response.status_code == 400 and "already enrolled" in enroll_response.text.lower():
                enroll_success = True
            else:
                enroll_success = enroll_response.status_code == 200
            
            # Test 2: Get my enrollments
            my_enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["learner"]}'}
            )
            
            my_enrollments_success = my_enrollments_response.status_code == 200
            
            # Test 3: Update enrollment progress
            if my_enrollments_success and my_enrollments_response.json():
                progress_data = {
                    "progress": 25.0,
                    "lastAccessedAt": datetime.utcnow().isoformat() + "Z"
                }
                
                progress_response = requests.put(
                    f"{BACKEND_URL}/enrollments/{test_course['id']}/progress",
                    json=progress_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["learner"]}'
                    }
                )
                
                progress_success = progress_response.status_code == 200
            else:
                progress_success = False
            
            # Summary
            tests_passed = sum([
                enroll_success,
                my_enrollments_success,
                progress_success
            ])
            
            self.log_result(
                "Enrollment Management Comprehensive", 
                "PASS" if tests_passed >= 2 else "FAIL", 
                f"Enrollment APIs working - {tests_passed}/3 operations successful",
                f"Enroll: {'✅' if enroll_success else '❌'}, Get: {'✅' if my_enrollments_success else '❌'}, Progress: {'✅' if progress_success else '❌'}"
            )
            
            return tests_passed >= 2
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Enrollment Management Comprehensive", 
                "FAIL", 
                "Failed to test enrollment APIs",
                str(e)
            )
        return False
    
    def test_department_apis_comprehensive(self):
        """Test department APIs for dropdown functionality"""
        print("\n🏢 COMPREHENSIVE DEPARTMENT APIs TESTING")
        print("-" * 60)
        
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Department APIs Comprehensive", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required for department management"
            )
            return False
        
        try:
            # Test 1: Get all departments (critical for dropdowns)
            departments_response = requests.get(
                f"{BACKEND_URL}/departments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if departments_response.status_code != 200:
                self.log_result(
                    "Department APIs - Get Departments", 
                    "FAIL", 
                    f"Get departments failed with status {departments_response.status_code}",
                    f"Response: {departments_response.text}"
                )
                return False
            
            departments = departments_response.json()
            
            self.log_result(
                "Department APIs Comprehensive", 
                "PASS", 
                f"Department APIs working - retrieved {len(departments)} departments",
                f"Critical for dropdown functionality in user creation forms"
            )
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Department APIs Comprehensive", 
                "FAIL", 
                "Failed to test department APIs",
                str(e)
            )
        return False
    
    def test_categories_apis_comprehensive(self):
        """Test categories APIs for course creation"""
        print("\n📂 COMPREHENSIVE CATEGORIES APIs TESTING")
        print("-" * 60)
        
        if "instructor" not in self.auth_tokens and "admin" not in self.auth_tokens:
            self.log_result(
                "Categories APIs Comprehensive", 
                "SKIP", 
                "No instructor or admin token available",
                "Authentication required for category management"
            )
            return False
        
        token = self.auth_tokens.get("instructor") or self.auth_tokens.get("admin")
        
        try:
            # Test 1: Get all categories (critical for course creation dropdowns)
            categories_response = requests.get(
                f"{BACKEND_URL}/categories",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if categories_response.status_code != 200:
                self.log_result(
                    "Categories APIs - Get Categories", 
                    "FAIL", 
                    f"Get categories failed with status {categories_response.status_code}",
                    f"Response: {categories_response.text}"
                )
                return False
            
            categories = categories_response.json()
            
            self.log_result(
                "Categories APIs Comprehensive", 
                "PASS", 
                f"Categories APIs working - retrieved {len(categories)} categories",
                f"Critical for dropdown functionality in course creation forms"
            )
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Categories APIs Comprehensive", 
                "FAIL", 
                "Failed to test categories APIs",
                str(e)
            )
        return False
    
    def test_classroom_management_comprehensive(self):
        """Test classroom management APIs comprehensively"""
        print("\n🏫 COMPREHENSIVE CLASSROOM MANAGEMENT APIs TESTING")
        print("-" * 60)
        
        if "instructor" not in self.auth_tokens and "admin" not in self.auth_tokens:
            self.log_result(
                "Classroom Management Comprehensive", 
                "SKIP", 
                "No instructor or admin token available",
                "Authentication required for classroom management"
            )
            return False
        
        token = self.auth_tokens.get("instructor") or self.auth_tokens.get("admin")
        
        try:
            # Test 1: Get all classrooms
            list_response = requests.get(
                f"{BACKEND_URL}/classrooms",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            list_success = list_response.status_code == 200
            
            # Test 2: Get classroom students (if classrooms exist)
            if list_success and list_response.json():
                classrooms = list_response.json()
                if classrooms:
                    classroom_id = classrooms[0]['id']
                    students_response = requests.get(
                        f"{BACKEND_URL}/classrooms/{classroom_id}/students",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {token}'}
                    )
                    students_success = students_response.status_code == 200
                else:
                    students_success = True  # No classrooms to test
            else:
                students_success = False
            
            # Summary
            tests_passed = sum([list_success, students_success])
            
            self.log_result(
                "Classroom Management Comprehensive", 
                "PASS" if tests_passed >= 1 else "FAIL", 
                f"Classroom APIs working - {tests_passed}/2 operations successful",
                f"List: {'✅' if list_success else '❌'}, Students: {'✅' if students_success else '❌'}"
            )
            
            return tests_passed >= 1
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Classroom Management Comprehensive", 
                "FAIL", 
                "Failed to test classroom APIs",
                str(e)
            )
        return False
    
    def test_program_management_comprehensive(self):
        """Test program management APIs comprehensively"""
        print("\n📋 COMPREHENSIVE PROGRAM MANAGEMENT APIs TESTING")
        print("-" * 60)
        
        if "instructor" not in self.auth_tokens and "admin" not in self.auth_tokens:
            self.log_result(
                "Program Management Comprehensive", 
                "SKIP", 
                "No instructor or admin token available",
                "Authentication required for program management"
            )
            return False
        
        token = self.auth_tokens.get("instructor") or self.auth_tokens.get("admin")
        
        try:
            # Test 1: Get all programs
            list_response = requests.get(
                f"{BACKEND_URL}/programs",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            list_success = list_response.status_code == 200
            
            if list_success:
                programs = list_response.json()
                self.log_result(
                    "Program Management Comprehensive", 
                    "PASS", 
                    f"Program APIs working - retrieved {len(programs)} programs",
                    f"Program management functionality available"
                )
                return True
            else:
                self.log_result(
                    "Program Management Comprehensive", 
                    "FAIL", 
                    f"Program listing failed with status {list_response.status_code}",
                    f"Response: {list_response.text}"
                )
                return False
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Program Management Comprehensive", 
                "FAIL", 
                "Failed to test program APIs",
                str(e)
            )
        return False
    
    def test_progress_tracking_comprehensive(self):
        """Test progress tracking APIs comprehensively"""
        print("\n📈 COMPREHENSIVE PROGRESS TRACKING APIs TESTING")
        print("-" * 60)
        
        if "learner" not in self.auth_tokens:
            self.log_result(
                "Progress Tracking Comprehensive", 
                "SKIP", 
                "No student token available",
                "Student authentication required for progress tracking"
            )
            return False
        
        try:
            # Get student enrollments
            enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["learner"]}'}
            )
            
            if enrollments_response.status_code != 200:
                self.log_result(
                    "Progress Tracking - Prerequisites", 
                    "FAIL", 
                    "Cannot get enrollments for progress tracking test",
                    f"Enrollments API status: {enrollments_response.status_code}"
                )
                return False
            
            enrollments = enrollments_response.json()
            if not enrollments:
                self.log_result(
                    "Progress Tracking - Prerequisites", 
                    "SKIP", 
                    "No enrollments available for progress tracking test",
                    "Student needs to be enrolled in at least one course"
                )
                return False
            
            test_enrollment = enrollments[0]
            course_id = test_enrollment['courseId']
            
            # Test 1: Update progress to 50%
            progress_data = {
                "progress": 50.0,
                "lastAccessedAt": datetime.utcnow().isoformat() + "Z"
            }
            
            progress_response = requests.put(
                f"{BACKEND_URL}/enrollments/{course_id}/progress",
                json=progress_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["learner"]}'
                }
            )
            
            progress_success = progress_response.status_code == 200
            
            self.log_result(
                "Progress Tracking Comprehensive", 
                "PASS" if progress_success else "FAIL", 
                f"Progress tracking APIs {'working' if progress_success else 'failed'}",
                f"Progress update: {'✅' if progress_success else '❌'}"
            )
            
            return progress_success
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Progress Tracking Comprehensive", 
                "FAIL", 
                "Failed to test progress tracking APIs",
                str(e)
            )
        return False
    
    def run_comprehensive_backend_tests(self):
        """Run comprehensive backend testing suite focusing on post-mockData cleanup"""
        print("\n" + "="*80)
        print("🚀 COMPREHENSIVE BACKEND TESTING SUITE - POST MOCKDATA CLEANUP")
        print("="*80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Timeout: {TEST_TIMEOUT}s")
        print("Focus: APIs that were previously falling back to mockData")
        print("="*80)
        
        # Priority 1: Authentication Endpoints (Critical - No Mock Fallback)
        print("\n🔐 PRIORITY 1: AUTHENTICATION ENDPOINTS (CRITICAL)")
        print("-" * 60)
        admin_success = self.test_admin_login()
        instructor_success = self.test_instructor_login() 
        student_success = self.test_student_login()
        
        # Priority 2: Course Management APIs (Critical - No Mock Fallback)
        print("\n📚 PRIORITY 2: COURSE MANAGEMENT APIs (CRITICAL)")
        print("-" * 60)
        course_success = self.test_course_management_comprehensive()
        
        # Priority 3: User Management APIs (Critical - No Mock Fallback)
        print("\n👥 PRIORITY 3: USER MANAGEMENT APIs (CRITICAL)")
        print("-" * 60)
        user_success = self.test_user_management_comprehensive()
        
        # Priority 4: Enrollment APIs (Critical - No Mock Fallback)
        print("\n🎓 PRIORITY 4: ENROLLMENT APIs (CRITICAL)")
        print("-" * 60)
        enrollment_success = self.test_enrollment_management_comprehensive()
        
        # Priority 5: Department APIs (Critical for Dropdowns)
        print("\n🏢 PRIORITY 5: DEPARTMENT APIs (CRITICAL FOR DROPDOWNS)")
        print("-" * 60)
        department_success = self.test_department_apis_comprehensive()
        
        # Priority 6: Categories APIs (Critical for Course Creation)
        print("\n📂 PRIORITY 6: CATEGORIES APIs (CRITICAL FOR COURSE CREATION)")
        print("-" * 60)
        categories_success = self.test_categories_apis_comprehensive()
        
        # Priority 7: Classroom Management APIs (Critical - No Mock Fallback)
        print("\n🏫 PRIORITY 7: CLASSROOM MANAGEMENT APIs (CRITICAL)")
        print("-" * 60)
        classroom_success = self.test_classroom_management_comprehensive()
        
        # Priority 8: Program Management APIs (Critical - No Mock Fallback)
        print("\n📋 PRIORITY 8: PROGRAM MANAGEMENT APIs (CRITICAL)")
        print("-" * 60)
        program_success = self.test_program_management_comprehensive()
        
        # Priority 9: Progress Tracking APIs (Critical for Course Progress)
        print("\n📈 PRIORITY 9: PROGRESS TRACKING APIs (CRITICAL)")
        print("-" * 60)
        progress_success = self.test_progress_tracking_comprehensive()
        
        # Final Results Summary
        self.print_final_summary()
        
        return {
            'admin_auth': admin_success,
            'instructor_auth': instructor_success,
            'student_auth': student_success,
            'course_management': course_success,
            'user_management': user_success,
            'enrollment_management': enrollment_success,
            'department_apis': department_success,
            'categories_apis': categories_success,
            'classroom_management': classroom_success,
            'program_management': program_success,
            'progress_tracking': progress_success
        }
    
    def print_final_summary(self):
        """Print final test summary"""
        print(f"\n" + "=" * 80)
        print(f"📊 COMPREHENSIVE BACKEND TESTING SUMMARY")
        print(f"=" * 80)
        
        print(f"📈 Test Results:")
        print(f"   Total Tests: {self.passed + self.failed}")
        print(f"   ✅ Passed: {self.passed}")
        print(f"   ❌ Failed: {self.failed}")
        print(f"   Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%" if (self.passed + self.failed) > 0 else "0.0%")
        
        # Show critical failures
        critical_failures = [r for r in self.results if r['status'] == 'FAIL']
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['message']}")
        
        # Show authentication status
        auth_status = []
        if 'admin' in self.auth_tokens:
            auth_status.append("✅ Admin")
        else:
            auth_status.append("❌ Admin")
        
        if 'instructor' in self.auth_tokens:
            auth_status.append("✅ Instructor")
        else:
            auth_status.append("❌ Instructor")
        
        if 'learner' in self.auth_tokens:
            auth_status.append("✅ Student")
        else:
            auth_status.append("❌ Student")
        
        print(f"\n🔐 Authentication Status: {' | '.join(auth_status)}")
        
        print(f"\n" + "=" * 80)


if __name__ == "__main__":
    tester = ComprehensiveBackendTester()
    
    # Run comprehensive backend tests
    results = tester.run_comprehensive_backend_tests()
    
    # Exit with appropriate code
    sys.exit(0 if tester.failed == 0 else 1)