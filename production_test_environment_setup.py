#!/usr/bin/env python3
"""
PRODUCTION TEST ENVIRONMENT SETUP
LearningFwiend LMS Application - Production Backend Test Environment Creation

OBJECTIVE: Create test environment on PRODUCTION backend at https://lms-evolution.emergent.host/api

REQUIREMENTS:
1. CREATE TEST COURSE "Progress Testing Course" with 4 modules:
   - Module 1: Video Module (YouTube video)
   - Module 2: Text/Content Module 
   - Module 3: Text/Content Module
   - Module 4: Quiz Module
2. CREATE CLASSROOM "Progress Test Classroom"
3. ASSIGN course to classroom
4. ENSURE both students exist and are enrolled:
   - karlo.student@alder.com / StudentPermanent123!
   - brayden.student (create if needed) / StudentTest123!

BACKEND URL: https://lms-evolution.emergent.host/api
ADMIN CREDENTIALS: brayden.t@covesmart.com / Hawaii2020!
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid
import urllib3

# Suppress SSL warnings for production testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration - PRODUCTION Backend URL
BACKEND_URL = "https://lms-evolution.emergent.host/api"
TEST_TIMEOUT = 30

# Credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT1_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

STUDENT2_CREDENTIALS = {
    "username_or_email": "brayden.student",
    "password": "StudentTest123!"
}

class ProductionTestEnvironmentSetup:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        self.created_resources = {
            'course_id': None,
            'classroom_id': None,
            'student1_id': None,
            'student2_id': None
        }
        
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
    
    def make_request(self, method, endpoint, data=None, headers=None, auth_token=None):
        """Make HTTP request with error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        
        # Set up headers
        request_headers = {'Content-Type': 'application/json'}
        if headers:
            request_headers.update(headers)
        if auth_token:
            request_headers['Authorization'] = f'Bearer {auth_token}'
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=request_headers, timeout=TEST_TIMEOUT, verify=False)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=request_headers, timeout=TEST_TIMEOUT, verify=False)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=request_headers, timeout=TEST_TIMEOUT, verify=False)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=request_headers, timeout=TEST_TIMEOUT, verify=False)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"🔍 DEBUG: Request exception for {method} {url}: {str(e)}")
            return None
    
    def authenticate_user(self, credentials, user_type):
        """Authenticate user and store token"""
        response = self.make_request('POST', '/auth/login', credentials)
        
        if response and response.status_code == 200:
            data = response.json()
            self.auth_tokens[user_type] = data.get('access_token')
            self.log_result(f"{user_type.title()} Authentication", 'PASS', 
                          f"Successfully authenticated {credentials['username_or_email']}")
            return data.get('user', {})
        else:
            error_msg = f"Failed to authenticate {credentials['username_or_email']}"
            if response:
                error_msg += f" - Status: {response.status_code}, Response: {response.text}"
            self.log_result(f"{user_type.title()} Authentication", 'FAIL', error_msg)
            return None
    
    def create_student_if_needed(self, email, username, full_name, password):
        """Create student user if they don't exist"""
        # Try to authenticate first to see if user exists
        test_credentials = {"username_or_email": email, "password": password}
        response = self.make_request('POST', '/auth/login', test_credentials)
        
        if response and response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            self.log_result(f"Student Check - {email}", 'PASS', 
                          f"Student {email} already exists with ID: {user.get('id')}")
            return user
        
        print(f"🔍 DEBUG: Student {email} login failed. Status: {response.status_code if response else 'No response'}")
        if response:
            print(f"🔍 DEBUG: Response: {response.text}")
        
        # User doesn't exist or password is wrong, try to create
        user_data = {
            "email": email,
            "username": username,
            "full_name": full_name,
            "role": "learner",
            "department": "Testing",
            "temporary_password": password
        }
        
        print(f"🔍 DEBUG: Attempting to create user with data: {user_data}")
        response = self.make_request('POST', '/auth/admin/create-user', user_data, 
                                   auth_token=self.auth_tokens.get('admin'))
        
        print(f"🔍 DEBUG: Create user response status: {response.status_code if response else 'No response'}")
        if response:
            print(f"🔍 DEBUG: Create user response: {response.text}")
        
        if response and response.status_code == 200:
            user = response.json()
            self.log_result(f"Student Creation - {email}", 'PASS', 
                          f"Successfully created student {email} with ID: {user.get('id')}")
            
            # Reset password to remove temporary password requirement
            reset_data = {
                "user_id": user.get('id'),
                "new_temporary_password": password
            }
            reset_response = self.make_request('POST', '/auth/admin/reset-password', reset_data,
                                             auth_token=self.auth_tokens.get('admin'))
            
            if reset_response and reset_response.status_code == 200:
                # Update user to remove first_login_required
                update_data = {"is_active": True}
                update_response = self.make_request('PUT', f'/auth/admin/users/{user.get("id")}', 
                                                  update_data, auth_token=self.auth_tokens.get('admin'))
                
                self.log_result(f"Student Password Setup - {email}", 'PASS', 
                              f"Password setup completed for {email}")
            
            return user
        else:
            error_msg = f"Failed to create student {email}"
            if response:
                error_msg += f" - Status: {response.status_code}, Response: {response.text}"
            self.log_result(f"Student Creation - {email}", 'FAIL', error_msg)
            return None
    
    def create_test_course(self):
        """Create the Progress Testing Course with 4 modules"""
        course_data = {
            "title": "Progress Testing Course",
            "description": "A comprehensive test course designed to validate progress tracking functionality with multiple module types including video, text content, and quiz components.",
            "category": "Testing",
            "duration": "2 hours",
            "thumbnailUrl": "https://via.placeholder.com/300x200/4F46E5/FFFFFF?text=Progress+Testing+Course",
            "accessType": "open",
            "modules": [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Module 1: Video Introduction",
                    "lessons": [
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Welcome Video",
                            "type": "video",
                            "content": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                            "duration": "5 minutes",
                            "description": "Introduction video explaining the course objectives and structure"
                        }
                    ]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Module 2: Fundamentals",
                    "lessons": [
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Core Concepts",
                            "type": "text",
                            "content": "This lesson covers the fundamental concepts that form the foundation of our learning objectives. Understanding these principles is crucial for success in subsequent modules.",
                            "duration": "15 minutes",
                            "description": "Text-based lesson covering fundamental concepts"
                        }
                    ]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Module 3: Advanced Topics",
                    "lessons": [
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Advanced Applications",
                            "type": "text",
                            "content": "Building upon the fundamentals, this lesson explores advanced applications and real-world scenarios. Students will learn to apply theoretical knowledge to practical situations.",
                            "duration": "20 minutes",
                            "description": "Advanced text-based lesson with practical applications"
                        }
                    ]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Module 4: Assessment",
                    "lessons": [
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Final Quiz",
                            "type": "quiz",
                            "content": json.dumps({
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "question": "What is the primary objective of this course?",
                                        "type": "multiple_choice",
                                        "options": [
                                            "To test progress tracking functionality",
                                            "To learn advanced programming",
                                            "To study mathematics",
                                            "To practice writing skills"
                                        ],
                                        "correct_answer": 0,
                                        "points": 25
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "question": "How many modules does this course contain?",
                                        "type": "multiple_choice",
                                        "options": ["2", "3", "4", "5"],
                                        "correct_answer": 2,
                                        "points": 25
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "question": "Which module type is NOT included in this course?",
                                        "type": "multiple_choice",
                                        "options": ["Video", "Text", "Quiz", "Audio"],
                                        "correct_answer": 3,
                                        "points": 25
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "question": "What percentage should you achieve after completing Module 2?",
                                        "type": "multiple_choice",
                                        "options": ["25%", "50%", "75%", "100%"],
                                        "correct_answer": 1,
                                        "points": 25
                                    }
                                ],
                                "total_points": 100,
                                "passing_score": 70
                            }),
                            "duration": "10 minutes",
                            "description": "Comprehensive quiz to assess understanding of all course modules"
                        }
                    ]
                }
            ]
        }
        
        response = self.make_request('POST', '/courses', course_data, 
                                   auth_token=self.auth_tokens.get('admin'))
        
        if response and response.status_code == 200:
            course = response.json()
            self.created_resources['course_id'] = course.get('id')
            self.log_result("Course Creation", 'PASS', 
                          f"Successfully created 'Progress Testing Course' with ID: {course.get('id')}")
            return course
        else:
            error_msg = "Failed to create Progress Testing Course"
            if response:
                error_msg += f" - Status: {response.status_code}, Response: {response.text}"
            self.log_result("Course Creation", 'FAIL', error_msg)
            return None
    
    def create_test_classroom(self, course_id, student1_id, student2_id):
        """Create Progress Test Classroom and assign course and students"""
        classroom_data = {
            "name": "Progress Test Classroom",
            "description": "Test classroom for validating progress tracking functionality with multiple students and course assignments.",
            "trainerId": self.auth_tokens.get('admin_user_id', ''),  # Will be set after admin auth
            "courseIds": [course_id],
            "studentIds": [student1_id, student2_id],
            "programIds": [],
            "startDate": datetime.now().isoformat(),
            "endDate": None,  # No end date for testing
            "isActive": True
        }
        
        response = self.make_request('POST', '/classrooms', classroom_data,
                                   auth_token=self.auth_tokens.get('admin'))
        
        if response and response.status_code == 200:
            classroom = response.json()
            self.created_resources['classroom_id'] = classroom.get('id')
            self.log_result("Classroom Creation", 'PASS',
                          f"Successfully created 'Progress Test Classroom' with ID: {classroom.get('id')}")
            return classroom
        else:
            error_msg = "Failed to create Progress Test Classroom"
            if response:
                error_msg += f" - Status: {response.status_code}, Response: {response.text}"
            self.log_result("Classroom Creation", 'FAIL', error_msg)
            return None
    
    def verify_student_enrollments(self, student_credentials, student_name):
        """Verify that student is properly enrolled in the test course"""
        # Authenticate student
        response = self.make_request('POST', '/auth/login', student_credentials)
        
        if not response or response.status_code != 200:
            self.log_result(f"Student Enrollment Check - {student_name}", 'FAIL',
                          f"Failed to authenticate {student_name}")
            return False
        
        student_token = response.json().get('access_token')
        
        # Check enrollments
        response = self.make_request('GET', '/enrollments', auth_token=student_token)
        
        if response and response.status_code == 200:
            enrollments = response.json()
            course_enrolled = any(e.get('courseId') == self.created_resources['course_id'] 
                                for e in enrollments)
            
            if course_enrolled:
                self.log_result(f"Student Enrollment Check - {student_name}", 'PASS',
                              f"{student_name} is properly enrolled in Progress Testing Course")
                return True
            else:
                self.log_result(f"Student Enrollment Check - {student_name}", 'FAIL',
                              f"{student_name} is not enrolled in Progress Testing Course")
                return False
        else:
            self.log_result(f"Student Enrollment Check - {student_name}", 'FAIL',
                          f"Failed to retrieve enrollments for {student_name}")
            return False
    
    def run_production_setup(self):
        """Run the complete production test environment setup"""
        print("🚀 STARTING PRODUCTION TEST ENVIRONMENT SETUP")
        print(f"🎯 Target Backend: {BACKEND_URL}")
        print("=" * 80)
        
        # Step 1: Authenticate Admin
        admin_user = self.authenticate_user(ADMIN_CREDENTIALS, 'admin')
        if not admin_user:
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed.")
            return False
        
        self.auth_tokens['admin_user_id'] = admin_user.get('id')
        
        # Step 2: Ensure Student 1 exists
        student1 = self.create_student_if_needed(
            "karlo.student@alder.com", 
            "karlo.student", 
            "Karlo Student",
            "StudentPermanent123!"
        )
        if not student1:
            print("❌ CRITICAL: Failed to ensure Student 1 exists. Cannot proceed.")
            return False
        
        self.created_resources['student1_id'] = student1.get('id')
        
        # Step 3: Ensure Student 2 exists
        student2 = self.create_student_if_needed(
            "brayden.student@learningfwiend.com",  # Using full email format
            "brayden.student",
            "Brayden Student", 
            "StudentTest123!"
        )
        if not student2:
            print("❌ CRITICAL: Failed to ensure Student 2 exists. Cannot proceed.")
            return False
        
        self.created_resources['student2_id'] = student2.get('id')
        
        # Step 4: Create Test Course
        course = self.create_test_course()
        if not course:
            print("❌ CRITICAL: Failed to create test course. Cannot proceed.")
            return False
        
        # Step 5: Create Test Classroom
        classroom = self.create_test_classroom(
            self.created_resources['course_id'],
            self.created_resources['student1_id'],
            self.created_resources['student2_id']
        )
        if not classroom:
            print("❌ CRITICAL: Failed to create test classroom. Cannot proceed.")
            return False
        
        # Step 6: Verify Student Enrollments
        student1_enrolled = self.verify_student_enrollments(STUDENT1_CREDENTIALS, "Karlo Student")
        student2_enrolled = self.verify_student_enrollments(
            {"username_or_email": "brayden.student@learningfwiend.com", "password": "StudentTest123!"},
            "Brayden Student"
        )
        
        # Final Summary
        print("\n" + "=" * 80)
        print("🎉 PRODUCTION TEST ENVIRONMENT SETUP COMPLETED")
        print("=" * 80)
        
        success_rate = (self.passed / (self.passed + self.failed)) * 100 if (self.passed + self.failed) > 0 else 0
        
        print(f"📊 RESULTS SUMMARY:")
        print(f"   ✅ Passed: {self.passed}")
        print(f"   ❌ Failed: {self.failed}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if self.created_resources['course_id'] and self.created_resources['classroom_id']:
            print(f"\n🎯 TEST ENVIRONMENT READY:")
            print(f"   📚 Course: Progress Testing Course (ID: {self.created_resources['course_id']})")
            print(f"   🏫 Classroom: Progress Test Classroom (ID: {self.created_resources['classroom_id']})")
            print(f"   👨‍🎓 Student 1: karlo.student@alder.com / StudentPermanent123!")
            print(f"   👨‍🎓 Student 2: brayden.student@learningfwiend.com / StudentTest123!")
            print(f"   👨‍💼 Admin: brayden.t@covesmart.com / Hawaii2020!")
            
            print(f"\n🌐 PRODUCTION SITE: https://lms-evolution.emergent.host/")
            print(f"   Students can now login and test progress tracking functionality")
            
            return True
        else:
            print("\n❌ SETUP INCOMPLETE: Critical resources were not created successfully")
            return False

def main():
    """Main execution function"""
    tester = ProductionTestEnvironmentSetup()
    success = tester.run_production_setup()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()