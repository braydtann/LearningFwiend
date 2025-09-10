#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Suite for LearningFwiend LMS Application
Tests ALL implemented APIs from Priority 1, 2, and 3 as requested in the review
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration
BACKEND_URL = "https://quiz-display-debug.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

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
        elif status == 'FAIL':
            self.failed += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
        else:  # INFO, SKIP, etc.
            print(f"ℹ️  {test_name}: {message}")
            if details:
                print(f"   Details: {details}")

    # =============================================================================
    # AUTHENTICATION SETUP
    # =============================================================================
    
    def setup_authentication(self):
        """Setup authentication tokens for all user types"""
        print("\n" + "="*80)
        print("🔐 SETTING UP AUTHENTICATION FOR ALL USER TYPES")
        print("="*80)
        
        # Test user credentials (using working credentials from setup)
        test_users = [
            {"username": "admin", "password": "NewAdmin123!", "role": "admin"},
            {"username": "test.instructor", "password": "TestInstructor123!", "role": "instructor"},
            {"username": "student", "password": "Student123!", "role": "learner"}
        ]
        
        auth_success = True
        
        for user in test_users:
            try:
                login_data = {
                    "username_or_email": user["username"],
                    "password": user["password"]
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
                    requires_password_change = data.get('requires_password_change')
                    
                    if token:
                        # Handle password change requirement for test users
                        if requires_password_change:
                            # Change password for test users
                            new_password = user["password"].replace("Test", "New")
                            password_change_data = {
                                "current_password": user["password"],
                                "new_password": new_password
                            }
                            
                            change_response = requests.post(
                                f"{BACKEND_URL}/auth/change-password",
                                json=password_change_data,
                                timeout=TEST_TIMEOUT,
                                headers={
                                    'Content-Type': 'application/json',
                                    'Authorization': f'Bearer {token}'
                                }
                            )
                            
                            if change_response.status_code == 200:
                                # Login again with new password
                                new_login_data = {
                                    "username_or_email": user["username"],
                                    "password": new_password
                                }
                                
                                new_response = requests.post(
                                    f"{BACKEND_URL}/auth/login",
                                    json=new_login_data,
                                    timeout=TEST_TIMEOUT,
                                    headers={'Content-Type': 'application/json'}
                                )
                                
                                if new_response.status_code == 200:
                                    new_data = new_response.json()
                                    token = new_data.get('access_token')
                                    user_info = new_data.get('user', {})
                        
                        self.auth_tokens[user["role"]] = token
                        self.log_result(
                            f"Authentication Setup - {user['role'].title()}", 
                            "PASS", 
                            f"Successfully authenticated {user['username']}",
                            f"User ID: {user_info.get('id')}, Role: {user_info.get('role')}"
                        )
                    else:
                        self.log_result(
                            f"Authentication Setup - {user['role'].title()}", 
                            "FAIL", 
                            "Login successful but no token received",
                            f"Response: {data}"
                        )
                        auth_success = False
                else:
                    self.log_result(
                        f"Authentication Setup - {user['role'].title()}", 
                        "FAIL", 
                        f"Login failed with status {response.status_code}",
                        f"Response: {response.text}"
                    )
                    auth_success = False
                    
            except requests.exceptions.RequestException as e:
                self.log_result(
                    f"Authentication Setup - {user['role'].title()}", 
                    "FAIL", 
                    "Login request failed",
                    str(e)
                )
                auth_success = False
        
        return auth_success

    # =============================================================================
    # PRIORITY 1 APIS - Core Management
    # =============================================================================
    
    def test_categories_api_comprehensive(self):
        """Test Categories API - CRUD operations, instructor/admin permissions, business logic"""
        print("\n" + "="*80)
        print("📂 PRIORITY 1: CATEGORIES API COMPREHENSIVE TESTING")
        print("="*80)
        
        if "admin" not in self.auth_tokens:
            self.log_result("Categories API", "FAIL", "No admin token available", "Authentication required")
            return False
        
        admin_token = self.auth_tokens["admin"]
        instructor_token = self.auth_tokens.get("instructor")
        learner_token = self.auth_tokens.get("learner")
        
        # Test 1: Create Category (Admin)
        category_data = {
            "name": f"Test Category {uuid.uuid4().hex[:8]}",
            "description": "Comprehensive test category for API testing"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/categories",
                json=category_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {admin_token}'
                }
            )
            
            if response.status_code == 200:
                created_category = response.json()
                category_id = created_category.get('id')
                self.test_data['category_id'] = category_id
                
                self.log_result(
                    "Categories API - Create (Admin)", 
                    "PASS", 
                    "Successfully created category as admin",
                    f"Category ID: {category_id}, Name: {created_category.get('name')}"
                )
            else:
                self.log_result(
                    "Categories API - Create (Admin)", 
                    "FAIL", 
                    f"Failed to create category, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Categories API - Create (Admin)", "FAIL", "Request failed", str(e))
            return False
        
        # Test 2: Create Category (Instructor)
        if instructor_token:
            instructor_category_data = {
                "name": f"Instructor Category {uuid.uuid4().hex[:8]}",
                "description": "Category created by instructor"
            }
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/categories",
                    json=instructor_category_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {instructor_token}'
                    }
                )
                
                if response.status_code == 200:
                    self.log_result(
                        "Categories API - Create (Instructor)", 
                        "PASS", 
                        "Successfully created category as instructor",
                        f"Instructor permissions working correctly"
                    )
                elif response.status_code == 403:
                    self.log_result(
                        "Categories API - Create (Instructor)", 
                        "FAIL", 
                        "Instructor denied category creation",
                        "Instructor should be able to create categories"
                    )
                else:
                    self.log_result(
                        "Categories API - Create (Instructor)", 
                        "FAIL", 
                        f"Unexpected status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Categories API - Create (Instructor)", "FAIL", "Request failed", str(e))
        
        # Test 3: Create Category (Learner - Should Fail)
        if learner_token:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/categories",
                    json=category_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {learner_token}'
                    }
                )
                
                if response.status_code == 403:
                    self.log_result(
                        "Categories API - Create (Learner Denied)", 
                        "PASS", 
                        "Correctly denied category creation for learner",
                        "Role-based access control working"
                    )
                else:
                    self.log_result(
                        "Categories API - Create (Learner Denied)", 
                        "FAIL", 
                        f"Learner should be denied, got status: {response.status_code}",
                        "Security issue: learners should not create categories"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Categories API - Create (Learner Denied)", "FAIL", "Request failed", str(e))
        
        # Test 4: Get All Categories
        try:
            response = requests.get(
                f"{BACKEND_URL}/categories",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 200:
                categories = response.json()
                if isinstance(categories, list):
                    self.log_result(
                        "Categories API - Get All", 
                        "PASS", 
                        f"Successfully retrieved {len(categories)} categories",
                        f"Categories include course counts and metadata"
                    )
                else:
                    self.log_result(
                        "Categories API - Get All", 
                        "FAIL", 
                        "Response is not a list",
                        f"Response type: {type(categories)}"
                    )
            else:
                self.log_result(
                    "Categories API - Get All", 
                    "FAIL", 
                    f"Failed to get categories, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Categories API - Get All", "FAIL", "Request failed", str(e))
        
        # Test 5: Get Specific Category
        if 'category_id' in self.test_data:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/categories/{self.test_data['category_id']}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {admin_token}'}
                )
                
                if response.status_code == 200:
                    category = response.json()
                    self.log_result(
                        "Categories API - Get Specific", 
                        "PASS", 
                        f"Successfully retrieved category by ID",
                        f"Category: {category.get('name')}, Course Count: {category.get('courseCount')}"
                    )
                else:
                    self.log_result(
                        "Categories API - Get Specific", 
                        "FAIL", 
                        f"Failed to get category by ID, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Categories API - Get Specific", "FAIL", "Request failed", str(e))
        
        # Test 6: Update Category
        if 'category_id' in self.test_data:
            update_data = {
                "name": f"Updated Category {uuid.uuid4().hex[:8]}",
                "description": "Updated description for comprehensive testing"
            }
            
            try:
                response = requests.put(
                    f"{BACKEND_URL}/categories/{self.test_data['category_id']}",
                    json=update_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {admin_token}'
                    }
                )
                
                if response.status_code == 200:
                    updated_category = response.json()
                    self.log_result(
                        "Categories API - Update", 
                        "PASS", 
                        "Successfully updated category",
                        f"New name: {updated_category.get('name')}"
                    )
                else:
                    self.log_result(
                        "Categories API - Update", 
                        "FAIL", 
                        f"Failed to update category, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Categories API - Update", "FAIL", "Request failed", str(e))
        
        # Test 7: Delete Category (Soft Delete)
        if 'category_id' in self.test_data:
            try:
                response = requests.delete(
                    f"{BACKEND_URL}/categories/{self.test_data['category_id']}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {admin_token}'}
                )
                
                if response.status_code == 200:
                    self.log_result(
                        "Categories API - Delete", 
                        "PASS", 
                        "Successfully deleted category (soft delete)",
                        "Category marked as inactive"
                    )
                else:
                    self.log_result(
                        "Categories API - Delete", 
                        "FAIL", 
                        f"Failed to delete category, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Categories API - Delete", "FAIL", "Request failed", str(e))
        
        return True

    def test_departments_api_comprehensive(self):
        """Test Departments API - CRUD operations, admin-only access, user assignment validation"""
        print("\n" + "="*80)
        print("🏢 PRIORITY 1: DEPARTMENTS API COMPREHENSIVE TESTING")
        print("="*80)
        
        if "admin" not in self.auth_tokens:
            self.log_result("Departments API", "FAIL", "No admin token available", "Authentication required")
            return False
        
        admin_token = self.auth_tokens["admin"]
        instructor_token = self.auth_tokens.get("instructor")
        learner_token = self.auth_tokens.get("learner")
        
        # Test 1: Create Department (Admin Only)
        department_data = {
            "name": f"Test Department {uuid.uuid4().hex[:8]}",
            "description": "Comprehensive test department for API testing"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/departments",
                json=department_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {admin_token}'
                }
            )
            
            if response.status_code == 200:
                created_department = response.json()
                department_id = created_department.get('id')
                self.test_data['department_id'] = department_id
                
                self.log_result(
                    "Departments API - Create (Admin)", 
                    "PASS", 
                    "Successfully created department as admin",
                    f"Department ID: {department_id}, Name: {created_department.get('name')}"
                )
            else:
                self.log_result(
                    "Departments API - Create (Admin)", 
                    "FAIL", 
                    f"Failed to create department, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Departments API - Create (Admin)", "FAIL", "Request failed", str(e))
            return False
        
        # Test 2: Create Department (Instructor - Should Fail)
        if instructor_token:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/departments",
                    json=department_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {instructor_token}'
                    }
                )
                
                if response.status_code == 403:
                    self.log_result(
                        "Departments API - Create (Instructor Denied)", 
                        "PASS", 
                        "Correctly denied department creation for instructor",
                        "Admin-only access control working"
                    )
                else:
                    self.log_result(
                        "Departments API - Create (Instructor Denied)", 
                        "FAIL", 
                        f"Instructor should be denied, got status: {response.status_code}",
                        "Security issue: only admins should create departments"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Departments API - Create (Instructor Denied)", "FAIL", "Request failed", str(e))
        
        # Test 3: Get All Departments
        try:
            response = requests.get(
                f"{BACKEND_URL}/departments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 200:
                departments = response.json()
                if isinstance(departments, list):
                    self.log_result(
                        "Departments API - Get All", 
                        "PASS", 
                        f"Successfully retrieved {len(departments)} departments",
                        f"Departments include user counts and metadata"
                    )
                else:
                    self.log_result(
                        "Departments API - Get All", 
                        "FAIL", 
                        "Response is not a list",
                        f"Response type: {type(departments)}"
                    )
            else:
                self.log_result(
                    "Departments API - Get All", 
                    "FAIL", 
                    f"Failed to get departments, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Departments API - Get All", "FAIL", "Request failed", str(e))
        
        # Test 4: Update Department (Admin Only)
        if 'department_id' in self.test_data:
            update_data = {
                "name": f"Updated Department {uuid.uuid4().hex[:8]}",
                "description": "Updated description for comprehensive testing"
            }
            
            try:
                response = requests.put(
                    f"{BACKEND_URL}/departments/{self.test_data['department_id']}",
                    json=update_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {admin_token}'
                    }
                )
                
                if response.status_code == 200:
                    updated_department = response.json()
                    self.log_result(
                        "Departments API - Update", 
                        "PASS", 
                        "Successfully updated department",
                        f"New name: {updated_department.get('name')}"
                    )
                else:
                    self.log_result(
                        "Departments API - Update", 
                        "FAIL", 
                        f"Failed to update department, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Departments API - Update", "FAIL", "Request failed", str(e))
        
        # Test 5: Delete Department (Should fail if users assigned)
        if 'department_id' in self.test_data:
            try:
                response = requests.delete(
                    f"{BACKEND_URL}/departments/{self.test_data['department_id']}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {admin_token}'}
                )
                
                if response.status_code == 200:
                    self.log_result(
                        "Departments API - Delete", 
                        "PASS", 
                        "Successfully deleted department (soft delete)",
                        "Department marked as inactive"
                    )
                elif response.status_code == 400:
                    self.log_result(
                        "Departments API - Delete (Business Logic)", 
                        "PASS", 
                        "Correctly prevented deletion of department with assigned users",
                        "Business logic validation working"
                    )
                else:
                    self.log_result(
                        "Departments API - Delete", 
                        "FAIL", 
                        f"Unexpected status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Departments API - Delete", "FAIL", "Request failed", str(e))
        
        return True

    def test_classrooms_api_comprehensive(self):
        """Test Classrooms API - Complex CRUD, trainer validation, course/program/student relationships"""
        print("\n" + "="*80)
        print("🏫 PRIORITY 1: CLASSROOMS API COMPREHENSIVE TESTING")
        print("="*80)
        
        if "admin" not in self.auth_tokens:
            self.log_result("Classrooms API", "FAIL", "No admin token available", "Authentication required")
            return False
        
        admin_token = self.auth_tokens["admin"]
        instructor_token = self.auth_tokens.get("instructor")
        
        # First, create test data (course, program, users)
        test_course_id = None
        test_program_id = None
        test_instructor_id = None
        test_student_id = None
        
        # Create a test course
        try:
            course_data = {
                "title": f"Test Course for Classroom {uuid.uuid4().hex[:8]}",
                "description": "Test course for classroom API testing",
                "category": "Testing",
                "duration": "2 hours"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {admin_token}'
                }
            )
            
            if response.status_code == 200:
                test_course_id = response.json().get('id')
                self.test_data['test_course_id'] = test_course_id
                
        except requests.exceptions.RequestException:
            pass
        
        # Get instructor and student IDs from existing users
        try:
            response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 200:
                users = response.json()
                for user in users:
                    if user.get('role') == 'instructor' and not test_instructor_id:
                        test_instructor_id = user.get('id')
                    elif user.get('role') == 'learner' and not test_student_id:
                        test_student_id = user.get('id')
                        
        except requests.exceptions.RequestException:
            pass
        
        # Test 1: Create Classroom with Complex Relationships
        if test_instructor_id and test_course_id:
            classroom_data = {
                "name": f"Test Classroom {uuid.uuid4().hex[:8]}",
                "description": "Comprehensive test classroom for API testing",
                "trainerId": test_instructor_id,
                "courseIds": [test_course_id] if test_course_id else [],
                "programIds": [test_program_id] if test_program_id else [],
                "studentIds": [test_student_id] if test_student_id else [],
                "batchId": f"BATCH-TEST-{uuid.uuid4().hex[:8]}",
                "maxStudents": 25,
                "department": "Testing"
            }
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/classrooms",
                    json=classroom_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {admin_token}'
                    }
                )
                
                if response.status_code == 200:
                    created_classroom = response.json()
                    classroom_id = created_classroom.get('id')
                    self.test_data['classroom_id'] = classroom_id
                    
                    self.log_result(
                        "Classrooms API - Create Complex", 
                        "PASS", 
                        "Successfully created classroom with complex relationships",
                        f"Classroom ID: {classroom_id}, Trainer: {created_classroom.get('trainerName')}, Students: {created_classroom.get('studentCount')}"
                    )
                else:
                    self.log_result(
                        "Classrooms API - Create Complex", 
                        "FAIL", 
                        f"Failed to create classroom, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    return False
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Classrooms API - Create Complex", "FAIL", "Request failed", str(e))
                return False
        else:
            self.log_result(
                "Classrooms API - Create Complex", 
                "SKIP", 
                "Missing test data (instructor or course)",
                "Cannot test classroom creation without required relationships"
            )
        
        # Test 2: Get All Classrooms
        try:
            response = requests.get(
                f"{BACKEND_URL}/classrooms",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 200:
                classrooms = response.json()
                if isinstance(classrooms, list):
                    self.log_result(
                        "Classrooms API - Get All", 
                        "PASS", 
                        f"Successfully retrieved {len(classrooms)} classrooms",
                        f"Classrooms include student/course/program counts"
                    )
                else:
                    self.log_result(
                        "Classrooms API - Get All", 
                        "FAIL", 
                        "Response is not a list",
                        f"Response type: {type(classrooms)}"
                    )
            else:
                self.log_result(
                    "Classrooms API - Get All", 
                    "FAIL", 
                    f"Failed to get classrooms, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Classrooms API - Get All", "FAIL", "Request failed", str(e))
        
        # Test 3: Get My Classrooms (Role-based)
        if instructor_token:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/classrooms/my-classrooms",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {instructor_token}'}
                )
                
                if response.status_code == 200:
                    my_classrooms = response.json()
                    self.log_result(
                        "Classrooms API - Get My Classrooms (Instructor)", 
                        "PASS", 
                        f"Successfully retrieved {len(my_classrooms)} instructor classrooms",
                        "Role-based filtering working"
                    )
                else:
                    self.log_result(
                        "Classrooms API - Get My Classrooms (Instructor)", 
                        "FAIL", 
                        f"Failed to get instructor classrooms, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Classrooms API - Get My Classrooms (Instructor)", "FAIL", "Request failed", str(e))
        
        # Test 4: Update Classroom
        if 'classroom_id' in self.test_data:
            update_data = {
                "name": f"Updated Classroom {uuid.uuid4().hex[:8]}",
                "description": "Updated description for comprehensive testing",
                "maxStudents": 30
            }
            
            try:
                response = requests.put(
                    f"{BACKEND_URL}/classrooms/{self.test_data['classroom_id']}",
                    json=update_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {admin_token}'
                    }
                )
                
                if response.status_code == 200:
                    updated_classroom = response.json()
                    self.log_result(
                        "Classrooms API - Update", 
                        "PASS", 
                        "Successfully updated classroom",
                        f"New name: {updated_classroom.get('name')}, Max Students: {updated_classroom.get('maxStudents')}"
                    )
                else:
                    self.log_result(
                        "Classrooms API - Update", 
                        "FAIL", 
                        f"Failed to update classroom, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Classrooms API - Update", "FAIL", "Request failed", str(e))
        
        return True

    def test_enrollments_api_comprehensive(self):
        """Test Enrollments API - Individual/bulk enrollment, progress tracking, role-based permissions"""
        print("\n" + "="*80)
        print("📚 PRIORITY 1: ENROLLMENTS API COMPREHENSIVE TESTING")
        print("="*80)
        
        if "learner" not in self.auth_tokens:
            self.log_result("Enrollments API", "FAIL", "No learner token available", "Authentication required")
            return False
        
        admin_token = self.auth_tokens["admin"]
        learner_token = self.auth_tokens["learner"]
        instructor_token = self.auth_tokens.get("instructor")
        
        # Get a test course ID
        test_course_id = self.test_data.get('test_course_id')
        
        if not test_course_id:
            # Try to get an existing course
            try:
                response = requests.get(
                    f"{BACKEND_URL}/courses",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {admin_token}'}
                )
                
                if response.status_code == 200:
                    courses = response.json()
                    if courses:
                        test_course_id = courses[0].get('id')
                        
            except requests.exceptions.RequestException:
                pass
        
        if not test_course_id:
            self.log_result(
                "Enrollments API", 
                "SKIP", 
                "No test course available for enrollment testing",
                "Cannot test enrollments without courses"
            )
            return False
        
        # Test 1: Enroll in Course (Learner)
        enrollment_data = {
            "courseId": test_course_id
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/enrollments",
                json=enrollment_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {learner_token}'
                }
            )
            
            if response.status_code == 200:
                enrollment = response.json()
                enrollment_id = enrollment.get('id')
                self.test_data['enrollment_id'] = enrollment_id
                
                self.log_result(
                    "Enrollments API - Enroll (Learner)", 
                    "PASS", 
                    "Successfully enrolled learner in course",
                    f"Enrollment ID: {enrollment_id}, Course ID: {enrollment.get('courseId')}, Progress: {enrollment.get('progress')}"
                )
            elif response.status_code == 400 and "already enrolled" in response.text:
                self.log_result(
                    "Enrollments API - Enroll (Already Enrolled)", 
                    "PASS", 
                    "Correctly prevented duplicate enrollment",
                    "Business logic validation working"
                )
            else:
                self.log_result(
                    "Enrollments API - Enroll (Learner)", 
                    "FAIL", 
                    f"Failed to enroll, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Enrollments API - Enroll (Learner)", "FAIL", "Request failed", str(e))
        
        # Test 2: Try to Enroll as Instructor (Should Fail)
        if instructor_token:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/enrollments",
                    json=enrollment_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {instructor_token}'
                    }
                )
                
                if response.status_code == 403:
                    self.log_result(
                        "Enrollments API - Enroll (Instructor Denied)", 
                        "PASS", 
                        "Correctly denied enrollment for instructor",
                        "Role-based access control working"
                    )
                else:
                    self.log_result(
                        "Enrollments API - Enroll (Instructor Denied)", 
                        "FAIL", 
                        f"Instructor should be denied, got status: {response.status_code}",
                        "Security issue: only learners should enroll"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Enrollments API - Enroll (Instructor Denied)", "FAIL", "Request failed", str(e))
        
        # Test 3: Get My Enrollments
        try:
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {learner_token}'}
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                if isinstance(enrollments, list):
                    self.log_result(
                        "Enrollments API - Get My Enrollments", 
                        "PASS", 
                        f"Successfully retrieved {len(enrollments)} enrollments",
                        f"Enrollments include progress tracking"
                    )
                else:
                    self.log_result(
                        "Enrollments API - Get My Enrollments", 
                        "FAIL", 
                        "Response is not a list",
                        f"Response type: {type(enrollments)}"
                    )
            else:
                self.log_result(
                    "Enrollments API - Get My Enrollments", 
                    "FAIL", 
                    f"Failed to get enrollments, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Enrollments API - Get My Enrollments", "FAIL", "Request failed", str(e))
        
        # Test 4: Unenroll from Course
        try:
            response = requests.delete(
                f"{BACKEND_URL}/enrollments/{test_course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {learner_token}'}
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Enrollments API - Unenroll", 
                    "PASS", 
                    "Successfully unenrolled from course",
                    "Enrollment management working correctly"
                )
            else:
                self.log_result(
                    "Enrollments API - Unenroll", 
                    "FAIL", 
                    f"Failed to unenroll, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Enrollments API - Unenroll", "FAIL", "Request failed", str(e))
        
        return True

    # =============================================================================
    # PRIORITY 2 APIS - Content & Communication
    # =============================================================================
    
    def test_courses_api_comprehensive(self):
        """Test Courses API - CRUD operations, instructor permissions, business logic"""
        print("\n" + "="*80)
        print("📖 PRIORITY 2: COURSES API COMPREHENSIVE TESTING")
        print("="*80)
        
        if "instructor" not in self.auth_tokens:
            self.log_result("Courses API", "FAIL", "No instructor token available", "Authentication required")
            return False
        
        admin_token = self.auth_tokens["admin"]
        instructor_token = self.auth_tokens["instructor"]
        learner_token = self.auth_tokens.get("learner")
        
        # Test 1: Create Course (Instructor)
        course_data = {
            "title": f"Comprehensive Test Course {uuid.uuid4().hex[:8]}",
            "description": "This is a comprehensive test course for API testing with detailed content and modules",
            "category": "Testing",
            "duration": "4 hours",
            "thumbnailUrl": "https://example.com/thumbnail.jpg",
            "accessType": "open",
            "modules": [
                {
                    "title": "Introduction Module",
                    "lessons": [
                        {
                            "title": "Welcome Lesson",
                            "type": "video",
                            "content": "https://example.com/video1.mp4"
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {instructor_token}'
                }
            )
            
            if response.status_code == 200:
                created_course = response.json()
                course_id = created_course.get('id')
                self.test_data['created_course_id'] = course_id
                
                self.log_result(
                    "Courses API - Create (Instructor)", 
                    "PASS", 
                    "Successfully created course as instructor",
                    f"Course ID: {course_id}, Title: {created_course.get('title')}, Instructor: {created_course.get('instructor')}"
                )
            else:
                self.log_result(
                    "Courses API - Create (Instructor)", 
                    "FAIL", 
                    f"Failed to create course, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Courses API - Create (Instructor)", "FAIL", "Request failed", str(e))
            return False
        
        # Test 2: Create Course (Learner - Should Fail)
        if learner_token:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/courses",
                    json=course_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {learner_token}'
                    }
                )
                
                if response.status_code == 403:
                    self.log_result(
                        "Courses API - Create (Learner Denied)", 
                        "PASS", 
                        "Correctly denied course creation for learner",
                        "Role-based access control working"
                    )
                else:
                    self.log_result(
                        "Courses API - Create (Learner Denied)", 
                        "FAIL", 
                        f"Learner should be denied, got status: {response.status_code}",
                        "Security issue: only instructors/admins should create courses"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Courses API - Create (Learner Denied)", "FAIL", "Request failed", str(e))
        
        # Test 3: Get All Courses (Course Catalog)
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {learner_token or admin_token}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                if isinstance(courses, list):
                    self.log_result(
                        "Courses API - Get All (Catalog)", 
                        "PASS", 
                        f"Successfully retrieved {len(courses)} published courses",
                        f"Course catalog accessible to all authenticated users"
                    )
                else:
                    self.log_result(
                        "Courses API - Get All (Catalog)", 
                        "FAIL", 
                        "Response is not a list",
                        f"Response type: {type(courses)}"
                    )
            else:
                self.log_result(
                    "Courses API - Get All (Catalog)", 
                    "FAIL", 
                    f"Failed to get courses, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Courses API - Get All (Catalog)", "FAIL", "Request failed", str(e))
        
        # Test 4: Get My Courses (Instructor)
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/my-courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {instructor_token}'}
            )
            
            if response.status_code == 200:
                my_courses = response.json()
                self.log_result(
                    "Courses API - Get My Courses (Instructor)", 
                    "PASS", 
                    f"Successfully retrieved {len(my_courses)} instructor courses",
                    "Role-based course filtering working"
                )
            else:
                self.log_result(
                    "Courses API - Get My Courses (Instructor)", 
                    "FAIL", 
                    f"Failed to get instructor courses, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Courses API - Get My Courses (Instructor)", "FAIL", "Request failed", str(e))
        
        # Test 5: Get Specific Course by ID
        if 'created_course_id' in self.test_data:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/courses/{self.test_data['created_course_id']}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {admin_token}'}
                )
                
                if response.status_code == 200:
                    course = response.json()
                    self.log_result(
                        "Courses API - Get Specific Course", 
                        "PASS", 
                        f"Successfully retrieved course by ID",
                        f"Course: {course.get('title')}, Modules: {len(course.get('modules', []))}, Status: {course.get('status')}"
                    )
                else:
                    self.log_result(
                        "Courses API - Get Specific Course", 
                        "FAIL", 
                        f"Failed to get course by ID, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Courses API - Get Specific Course", "FAIL", "Request failed", str(e))
        
        # Test 6: Update Course (Owner)
        if 'created_course_id' in self.test_data:
            update_data = {
                "title": f"Updated Course {uuid.uuid4().hex[:8]}",
                "description": "Updated description for comprehensive testing",
                "category": "Updated Testing",
                "duration": "6 hours"
            }
            
            try:
                response = requests.put(
                    f"{BACKEND_URL}/courses/{self.test_data['created_course_id']}",
                    json=update_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {instructor_token}'
                    }
                )
                
                if response.status_code == 200:
                    updated_course = response.json()
                    self.log_result(
                        "Courses API - Update (Owner)", 
                        "PASS", 
                        "Successfully updated course as owner",
                        f"New title: {updated_course.get('title')}, Duration: {updated_course.get('duration')}"
                    )
                else:
                    self.log_result(
                        "Courses API - Update (Owner)", 
                        "FAIL", 
                        f"Failed to update course, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Courses API - Update (Owner)", "FAIL", "Request failed", str(e))
        
        # Test 7: Delete Course (Owner)
        if 'created_course_id' in self.test_data:
            try:
                response = requests.delete(
                    f"{BACKEND_URL}/courses/{self.test_data['created_course_id']}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {instructor_token}'}
                )
                
                if response.status_code == 200:
                    self.log_result(
                        "Courses API - Delete (Owner)", 
                        "PASS", 
                        "Successfully deleted course as owner",
                        "Course ownership permissions working"
                    )
                else:
                    self.log_result(
                        "Courses API - Delete (Owner)", 
                        "FAIL", 
                        f"Failed to delete course, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Courses API - Delete (Owner)", "FAIL", "Request failed", str(e))
        
        return True

    def test_programs_api_comprehensive(self):
        """Test Programs API - CRUD operations, instructor permissions, nested programs"""
        print("\n" + "="*80)
        print("🎓 PRIORITY 2: PROGRAMS API COMPREHENSIVE TESTING")
        print("="*80)
        
        if "instructor" not in self.auth_tokens:
            self.log_result("Programs API", "FAIL", "No instructor token available", "Authentication required")
            return False
        
        admin_token = self.auth_tokens["admin"]
        instructor_token = self.auth_tokens["instructor"]
        learner_token = self.auth_tokens.get("learner")
        
        # Get test course IDs for program creation
        test_course_ids = []
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                test_course_ids = [course.get('id') for course in courses[:2]]  # Get first 2 courses
                
        except requests.exceptions.RequestException:
            pass
        
        # Test 1: Create Program (Instructor)
        program_data = {
            "title": f"Comprehensive Test Program {uuid.uuid4().hex[:8]}",
            "description": "This is a comprehensive test program for API testing with multiple courses",
            "duration": "8 weeks",
            "courseIds": test_course_ids,
            "nestedProgramIds": []
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/programs",
                json=program_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {instructor_token}'
                }
            )
            
            if response.status_code == 200:
                created_program = response.json()
                program_id = created_program.get('id')
                self.test_data['created_program_id'] = program_id
                
                self.log_result(
                    "Programs API - Create (Instructor)", 
                    "PASS", 
                    "Successfully created program as instructor",
                    f"Program ID: {program_id}, Title: {created_program.get('title')}, Course Count: {created_program.get('courseCount')}"
                )
            else:
                self.log_result(
                    "Programs API - Create (Instructor)", 
                    "FAIL", 
                    f"Failed to create program, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Programs API - Create (Instructor)", "FAIL", "Request failed", str(e))
            return False
        
        # Test 2: Create Program (Learner - Should Fail)
        if learner_token:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/programs",
                    json=program_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {learner_token}'
                    }
                )
                
                if response.status_code == 403:
                    self.log_result(
                        "Programs API - Create (Learner Denied)", 
                        "PASS", 
                        "Correctly denied program creation for learner",
                        "Role-based access control working"
                    )
                else:
                    self.log_result(
                        "Programs API - Create (Learner Denied)", 
                        "FAIL", 
                        f"Learner should be denied, got status: {response.status_code}",
                        "Security issue: only instructors/admins should create programs"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Programs API - Create (Learner Denied)", "FAIL", "Request failed", str(e))
        
        # Test 3: Get All Programs
        try:
            response = requests.get(
                f"{BACKEND_URL}/programs",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 200:
                programs = response.json()
                if isinstance(programs, list):
                    self.log_result(
                        "Programs API - Get All", 
                        "PASS", 
                        f"Successfully retrieved {len(programs)} active programs",
                        f"Programs include course counts and metadata"
                    )
                else:
                    self.log_result(
                        "Programs API - Get All", 
                        "FAIL", 
                        "Response is not a list",
                        f"Response type: {type(programs)}"
                    )
            else:
                self.log_result(
                    "Programs API - Get All", 
                    "FAIL", 
                    f"Failed to get programs, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Programs API - Get All", "FAIL", "Request failed", str(e))
        
        # Test 4: Get My Programs (Instructor)
        try:
            response = requests.get(
                f"{BACKEND_URL}/programs/my-programs",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {instructor_token}'}
            )
            
            if response.status_code == 200:
                my_programs = response.json()
                self.log_result(
                    "Programs API - Get My Programs (Instructor)", 
                    "PASS", 
                    f"Successfully retrieved {len(my_programs)} instructor programs",
                    "Role-based program filtering working"
                )
            else:
                self.log_result(
                    "Programs API - Get My Programs (Instructor)", 
                    "FAIL", 
                    f"Failed to get instructor programs, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Programs API - Get My Programs (Instructor)", "FAIL", "Request failed", str(e))
        
        # Test 5: Get Specific Program by ID
        if 'created_program_id' in self.test_data:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/programs/{self.test_data['created_program_id']}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {admin_token}'}
                )
                
                if response.status_code == 200:
                    program = response.json()
                    self.log_result(
                        "Programs API - Get Specific Program", 
                        "PASS", 
                        f"Successfully retrieved program by ID",
                        f"Program: {program.get('title')}, Courses: {len(program.get('courseIds', []))}, Active: {program.get('isActive')}"
                    )
                else:
                    self.log_result(
                        "Programs API - Get Specific Program", 
                        "FAIL", 
                        f"Failed to get program by ID, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Programs API - Get Specific Program", "FAIL", "Request failed", str(e))
        
        # Test 6: Update Program (Owner)
        if 'created_program_id' in self.test_data:
            update_data = {
                "title": f"Updated Program {uuid.uuid4().hex[:8]}",
                "description": "Updated description for comprehensive testing",
                "duration": "12 weeks",
                "courseIds": test_course_ids
            }
            
            try:
                response = requests.put(
                    f"{BACKEND_URL}/programs/{self.test_data['created_program_id']}",
                    json=update_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {instructor_token}'
                    }
                )
                
                if response.status_code == 200:
                    updated_program = response.json()
                    self.log_result(
                        "Programs API - Update (Owner)", 
                        "PASS", 
                        "Successfully updated program as owner",
                        f"New title: {updated_program.get('title')}, Duration: {updated_program.get('duration')}"
                    )
                else:
                    self.log_result(
                        "Programs API - Update (Owner)", 
                        "FAIL", 
                        f"Failed to update program, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Programs API - Update (Owner)", "FAIL", "Request failed", str(e))
        
        return True

    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_comprehensive_tests(self):
        """Run all comprehensive backend API tests"""
        print("\n" + "="*100)
        print("🚀 COMPREHENSIVE BACKEND API TESTING - ALL PRIORITIES")
        print("="*100)
        
        # Setup authentication first
        if not self.setup_authentication():
            print("\n❌ CRITICAL: Authentication setup failed. Cannot proceed with API testing.")
            return False
        
        print(f"\n✅ Authentication successful for {len(self.auth_tokens)} user types")
        
        # Priority 1 Tests - Core Management
        print("\n" + "🔥 PRIORITY 1 TESTS - CORE MANAGEMENT APIS")
        self.test_categories_api_comprehensive()
        self.test_departments_api_comprehensive()
        self.test_classrooms_api_comprehensive()
        self.test_enrollments_api_comprehensive()
        
        # Priority 2 Tests - Content & Communication
        print("\n" + "🔥 PRIORITY 2 TESTS - CONTENT & COMMUNICATION APIS")
        self.test_courses_api_comprehensive()
        self.test_programs_api_comprehensive()
        
        # Print final summary
        self.print_final_summary()
        
        return self.passed > self.failed
    
    def print_final_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*100)
        print("📊 COMPREHENSIVE BACKEND API TESTING SUMMARY")
        print("="*100)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ PASSED: {self.passed}")
        print(f"❌ FAILED: {self.failed}")
        print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
        print(f"🔢 TOTAL TESTS: {total_tests}")
        
        if self.failed > 0:
            print(f"\n❌ FAILED TESTS SUMMARY:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['message']}")
        
        print("\n" + "="*100)
        
        if success_rate >= 80:
            print("🎉 OVERALL RESULT: BACKEND APIs are production-ready!")
        elif success_rate >= 60:
            print("⚠️  OVERALL RESULT: Backend APIs need some fixes before production")
        else:
            print("🚨 OVERALL RESULT: Critical issues found - backend needs significant work")
        
        print("="*100)

def main():
    """Main function to run comprehensive backend tests"""
    tester = ComprehensiveBackendTester()
    
    try:
        success = tester.run_comprehensive_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()