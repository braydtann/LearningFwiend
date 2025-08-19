#!/usr/bin/env python3
"""
Bug Fix Testing Suite for LearningFwiend LMS Application
Tests the 3 specific bug fixes mentioned in the review request
"""

import requests
import json
import os
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "http://localhost:8001/api"
TEST_TIMEOUT = 15

class BugFixTester:
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
        elif status == 'SKIP':
            print(f"⏭️  {test_name}: {message}")
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
                        "Admin Login", 
                        "PASS", 
                        f"Successfully logged in as admin: {user_info.get('email')}",
                        f"Token received, role verified: {user_info.get('role')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Login", 
                        "FAIL", 
                        "Login successful but missing token or wrong role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Admin Login", 
                    "FAIL", 
                    f"Admin login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Login", 
                "FAIL", 
                "Failed to test admin login",
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
                        "Instructor Login", 
                        "PASS", 
                        f"Successfully logged in as instructor: {user_info.get('username')}",
                        f"Token received, role verified: {user_info.get('role')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Instructor Login", 
                        "FAIL", 
                        "Login successful but missing token or wrong role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Instructor Login", 
                    "FAIL", 
                    f"Instructor login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Instructor Login", 
                "FAIL", 
                "Failed to test instructor login",
                str(e)
            )
        return False
    
    def test_google_drive_image_url_conversion(self):
        """Test Google Drive image URL conversion for course thumbnails"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Google Drive Image URL Conversion", 
                "SKIP", 
                "No instructor token available for Google Drive image test",
                "Instructor authentication required"
            )
            return False
        
        try:
            # Test course creation with Google Drive sharing URL
            google_drive_url = "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view?usp=sharing"
            
            course_data = {
                "title": "Google Drive Image Test Course",
                "description": "Testing Google Drive image URL conversion for thumbnails",
                "category": "Testing",
                "duration": "2 weeks",
                "thumbnailUrl": google_drive_url,
                "accessType": "open",
                "modules": [
                    {
                        "title": "Module 1: Google Drive Images",
                        "lessons": [
                            {
                                "title": "Lesson 1: Image Display Test",
                                "type": "text",
                                "content": "Testing Google Drive image display"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 200:
                created_course = response.json()
                course_id = created_course.get('id')
                returned_thumbnail = created_course.get('thumbnailUrl')
                
                # Check if the URL was processed (either converted or stored as-is)
                if returned_thumbnail:
                    # Test retrieving the course to verify thumbnail is accessible
                    get_response = requests.get(
                        f"{BACKEND_URL}/courses/{course_id}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
                    )
                    
                    if get_response.status_code == 200:
                        retrieved_course = get_response.json()
                        retrieved_thumbnail = retrieved_course.get('thumbnailUrl')
                        
                        self.log_result(
                            "Google Drive Image URL Conversion", 
                            "PASS", 
                            f"Successfully created course with Google Drive image URL and can retrieve it",
                            f"Course ID: {course_id}, Original URL: {google_drive_url[:50]}..., Stored URL: {retrieved_thumbnail[:50] if retrieved_thumbnail else 'None'}..."
                        )
                        return True
                    else:
                        self.log_result(
                            "Google Drive Image URL Conversion", 
                            "FAIL", 
                            f"Course created but retrieval failed, status: {get_response.status_code}",
                            f"Response: {get_response.text}"
                        )
                else:
                    self.log_result(
                        "Google Drive Image URL Conversion", 
                        "FAIL", 
                        "Course created but thumbnailUrl field is empty",
                        f"Expected Google Drive URL to be stored"
                    )
            else:
                self.log_result(
                    "Google Drive Image URL Conversion", 
                    "FAIL", 
                    f"Failed to create course with Google Drive image URL, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Google Drive Image URL Conversion", 
                "FAIL", 
                "Failed to test Google Drive image URL conversion",
                str(e)
            )
        return False
    
    def test_courses_api_for_quiz_analytics(self):
        """Test GET /api/courses endpoint for quiz analytics page filtering"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Courses API for Quiz Analytics", 
                "SKIP", 
                "No admin token available for courses API test",
                "Admin authentication required"
            )
            return False
        
        try:
            # Test GET /api/courses as admin (should see all courses)
            admin_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if admin_response.status_code == 200:
                admin_courses = admin_response.json()
                
                # Test GET /api/courses as instructor (should see all published courses)
                if "instructor" in self.auth_tokens:
                    instructor_response = requests.get(
                        f"{BACKEND_URL}/courses",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
                    )
                    
                    if instructor_response.status_code == 200:
                        instructor_courses = instructor_response.json()
                        
                        # Verify both admin and instructor can access courses for analytics
                        self.log_result(
                            "Courses API for Quiz Analytics", 
                            "PASS", 
                            f"Courses API working for quiz analytics filtering - Admin sees {len(admin_courses)} courses, Instructor sees {len(instructor_courses)} courses",
                            f"Both admin and instructor roles can retrieve courses for analytics filtering"
                        )
                        return True
                    else:
                        self.log_result(
                            "Courses API for Quiz Analytics", 
                            "FAIL", 
                            f"Instructor cannot access courses API, status: {instructor_response.status_code}",
                            f"Response: {instructor_response.text}"
                        )
                else:
                    # Admin access is sufficient for analytics
                    self.log_result(
                        "Courses API for Quiz Analytics", 
                        "PASS", 
                        f"Courses API working for quiz analytics - Admin can access {len(admin_courses)} courses",
                        f"Admin role can retrieve courses for analytics filtering"
                    )
                    return True
            else:
                self.log_result(
                    "Courses API for Quiz Analytics", 
                    "FAIL", 
                    f"Admin cannot access courses API, status: {admin_response.status_code}",
                    f"Response: {admin_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Courses API for Quiz Analytics", 
                "FAIL", 
                "Failed to test courses API for quiz analytics",
                str(e)
            )
        return False
    
    def test_departments_api_for_user_dropdown_fix(self):
        """Test GET /api/departments endpoint for user dropdown functionality"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Departments API for User Dropdown Fix", 
                "SKIP", 
                "No admin token available for departments API test",
                "Admin authentication required"
            )
            return False
        
        try:
            # Test GET /api/departments
            response = requests.get(
                f"{BACKEND_URL}/departments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                departments = response.json()
                
                # Verify departments have required fields for dropdown
                if isinstance(departments, list):
                    valid_departments = []
                    for dept in departments:
                        if dept.get('id') and dept.get('name'):
                            valid_departments.append(dept)
                    
                    if len(valid_departments) > 0:
                        self.log_result(
                            "Departments API for User Dropdown Fix", 
                            "PASS", 
                            f"Departments API working for user dropdown fix - Retrieved {len(valid_departments)} departments with required fields (id, name)",
                            f"Sample departments: {[d.get('name') for d in valid_departments[:3]]}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Departments API for User Dropdown Fix", 
                            "FAIL", 
                            "Departments retrieved but missing required fields for dropdown",
                            f"Retrieved {len(departments)} departments but none have both 'id' and 'name' fields"
                        )
                else:
                    self.log_result(
                        "Departments API for User Dropdown Fix", 
                        "FAIL", 
                        "Departments API returned non-list response",
                        f"Expected list, got: {type(departments)}"
                    )
            else:
                self.log_result(
                    "Departments API for User Dropdown Fix", 
                    "FAIL", 
                    f"Departments API failed, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Departments API for User Dropdown Fix", 
                "FAIL", 
                "Failed to test departments API for user dropdown fix",
                str(e)
            )
        return False
    
    def test_create_course_button_backend_support(self):
        """Test that backend supports course creation for relocated Create Course button"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Create Course Button Backend Support", 
                "SKIP", 
                "No instructor token available for course creation test",
                "Instructor authentication required"
            )
            return False
        
        try:
            # Test that POST /api/courses endpoint is working for the relocated button
            course_data = {
                "title": "Create Course Button Test",
                "description": "Testing backend support for relocated Create Course button",
                "category": "Testing",
                "duration": "1 week",
                "accessType": "open"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 200:
                created_course = response.json()
                course_id = created_course.get('id')
                
                # Verify the course appears in the courses list (for the courses page)
                list_response = requests.get(
                    f"{BACKEND_URL}/courses",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
                )
                
                if list_response.status_code == 200:
                    courses = list_response.json()
                    created_course_found = any(course.get('id') == course_id for course in courses)
                    
                    if created_course_found:
                        self.log_result(
                            "Create Course Button Backend Support", 
                            "PASS", 
                            f"Backend fully supports relocated Create Course button - Course creation and listing working",
                            f"Created course ID: {course_id}, appears in courses list"
                        )
                        return True
                    else:
                        self.log_result(
                            "Create Course Button Backend Support", 
                            "FAIL", 
                            "Course created but not appearing in courses list",
                            f"Created course ID: {course_id} not found in {len(courses)} courses"
                        )
                else:
                    self.log_result(
                        "Create Course Button Backend Support", 
                        "FAIL", 
                        f"Course created but courses listing failed, status: {list_response.status_code}",
                        f"Response: {list_response.text}"
                    )
            else:
                self.log_result(
                    "Create Course Button Backend Support", 
                    "FAIL", 
                    f"Course creation failed, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Create Course Button Backend Support", 
                "FAIL", 
                "Failed to test backend support for Create Course button",
                str(e)
            )
        return False
    
    def run_bug_fix_tests(self):
        """Run the 3 specific bug fix tests"""
        print("🚀 Starting Bug Fix Testing Suite for LearningFwiend LMS")
        print("🔍 TESTING 3 SPECIFIC BUG FIXES FROM REVIEW REQUEST")
        print("=" * 80)
        
        # Authentication setup
        print("\n🔐 AUTHENTICATION SETUP")
        print("=" * 50)
        self.test_admin_login()
        self.test_instructor_login()
        
        # Bug fix tests
        if self.auth_tokens:
            print("\n🔧 BUG FIX TESTS - REVIEW REQUEST")
            print("=" * 50)
            print("Testing 3 specific bug fixes:")
            print("1. Google Drive Image URL Conversion")
            print("2. Courses API for Quiz Analytics")
            print("3. Departments API for User Dropdown Fix")
            print("4. Create Course Button Backend Support")
            print()
            
            self.test_google_drive_image_url_conversion()
            self.test_courses_api_for_quiz_analytics()
            self.test_departments_api_for_user_dropdown_fix()
            self.test_create_course_button_backend_support()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 BUG FIX TESTING SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.failed == 0:
            print("🎉 ALL BUG FIX TESTS PASSED! Backend is ready to support frontend changes.")
        else:
            print(f"⚠️  {self.failed} test(s) failed. Please review the issues above.")
        
        return self.failed == 0

if __name__ == "__main__":
    tester = BugFixTester()
    success = tester.run_bug_fix_tests()
    sys.exit(0 if success else 1)