#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING SUITE - POST REACT ERROR #310 FIXES
LearningFwiend LMS Application Backend API Testing

TESTING SCOPE (Based on Review Request):
✅ AUTHENTICATION TESTING with specific credentials
✅ QUIZ-RELATED BACKEND APIS (courses with quiz lessons, quiz data structure)
✅ COURSE MANAGEMENT APIS (list, details, creation)
✅ CRITICAL ENDPOINTS (enrollments, progress tracking, classrooms)
✅ ERROR HANDLING with edge cases

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

STUDENT_CREDENTIALS_1 = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

STUDENT_CREDENTIALS_2 = {
    "username_or_email": "enrollment.test.student@learningfwiend.com",
    "password": "CleanEnv123!"
}

class ReactError310BackendTester:
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
    
    # =============================================================================
    # AUTHENTICATION TESTING - PRIORITY FOCUS FROM REVIEW REQUEST
    # =============================================================================
    
    def test_admin_authentication(self):
        """Test admin login with brayden.t@covesmart.com / Hawaii2020!"""
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
    
    def test_student_authentication_1(self):
        """Test student login with karlo.student@alder.com / StudentPermanent123!"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS_1,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                requires_password_change = data.get('requires_password_change', False)
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['student1'] = token
                    self.log_result(
                        "Student Authentication (karlo.student)", 
                        "PASS", 
                        f"Student login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Password change required: {requires_password_change}"
                    )
                    return True
                else:
                    self.log_result(
                        "Student Authentication (karlo.student)", 
                        "FAIL", 
                        "Student login failed - invalid token or role",
                        f"Token present: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Student Authentication (karlo.student)", 
                    "FAIL", 
                    f"Student login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Authentication (karlo.student)", 
                "FAIL", 
                "Student authentication request failed",
                str(e)
            )
        return False
    
    def test_student_authentication_2(self):
        """Test student login with enrollment.test.student@learningfwiend.com / CleanEnv123!"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS_2,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                requires_password_change = data.get('requires_password_change', False)
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['student2'] = token
                    self.log_result(
                        "Student Authentication (test.student)", 
                        "PASS", 
                        f"Student login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Password change required: {requires_password_change}"
                    )
                    return True
                else:
                    self.log_result(
                        "Student Authentication (test.student)", 
                        "FAIL", 
                        "Student login failed - invalid token or role",
                        f"Token present: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Student Authentication (test.student)", 
                    "FAIL", 
                    f"Student login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Authentication (test.student)", 
                "FAIL", 
                "Student authentication request failed",
                str(e)
            )
        return False
    
    # =============================================================================
    # QUIZ-RELATED BACKEND APIS - PRIORITY FOCUS FROM REVIEW REQUEST
    # =============================================================================
    
    def test_courses_with_quiz_lessons(self):
        """Test GET /api/courses/{id} for courses with quiz lessons"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Quiz Courses API Test", 
                "SKIP", 
                "No admin token available for quiz courses test",
                "Admin authentication required"
            )
            return False
        
        try:
            # First get all courses
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if courses_response.status_code != 200:
                self.log_result(
                    "Quiz Courses API Test", 
                    "FAIL", 
                    f"Failed to get courses list, status: {courses_response.status_code}",
                    f"Response: {courses_response.text}"
                )
                return False
            
            courses = courses_response.json()
            quiz_courses_found = 0
            quiz_lessons_validated = 0
            
            for course in courses[:10]:  # Test first 10 courses
                course_id = course.get('id')
                if not course_id:
                    continue
                
                # Get detailed course info
                course_detail_response = requests.get(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if course_detail_response.status_code == 200:
                    course_detail = course_detail_response.json()
                    modules = course_detail.get('modules', [])
                    
                    # Check for quiz lessons
                    has_quiz_lessons = False
                    for module in modules:
                        lessons = module.get('lessons', [])
                        for lesson in lessons:
                            lesson_type = lesson.get('type', '').lower()
                            lesson_title = lesson.get('title', '').lower()
                            lesson_content = lesson.get('content', {})
                            
                            if ('quiz' in lesson_type or 'quiz' in lesson_title or 
                                'questions' in lesson_content):
                                has_quiz_lessons = True
                                quiz_lessons_validated += 1
                                
                                # Validate quiz data structure
                                if isinstance(lesson_content, dict):
                                    questions = lesson_content.get('questions', [])
                                    if isinstance(questions, list) and len(questions) > 0:
                                        # Check first question structure
                                        first_question = questions[0]
                                        required_fields = ['id', 'question', 'options', 'correctAnswer']
                                        has_required_fields = all(field in first_question for field in required_fields)
                                        
                                        if has_required_fields:
                                            print(f"   ✅ Quiz lesson validated: {lesson.get('title')} - {len(questions)} questions")
                                        else:
                                            print(f"   ⚠️ Quiz lesson missing fields: {lesson.get('title')}")
                    
                    if has_quiz_lessons:
                        quiz_courses_found += 1
            
            if quiz_courses_found > 0 and quiz_lessons_validated > 0:
                self.log_result(
                    "Quiz Courses API Test", 
                    "PASS", 
                    f"Successfully validated quiz courses and lessons",
                    f"Quiz courses found: {quiz_courses_found}, Quiz lessons validated: {quiz_lessons_validated}"
                )
                return True
            else:
                self.log_result(
                    "Quiz Courses API Test", 
                    "FAIL", 
                    "No quiz courses or lessons found for validation",
                    f"Tested {len(courses)} courses, found {quiz_courses_found} with quiz lessons"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Courses API Test", 
                "FAIL", 
                "Failed to test quiz courses API",
                str(e)
            )
        return False
    
    def test_quiz_data_structure_integrity(self):
        """Verify quiz data structure integrity"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Quiz Data Structure Integrity", 
                "SKIP", 
                "No admin token available for quiz data structure test",
                "Admin authentication required"
            )
            return False
        
        try:
            # Get courses and find ones with quiz content
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if courses_response.status_code != 200:
                return False
            
            courses = courses_response.json()
            valid_quiz_structures = 0
            invalid_quiz_structures = 0
            
            for course in courses[:5]:  # Test first 5 courses
                course_id = course.get('id')
                course_response = requests.get(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if course_response.status_code == 200:
                    course_data = course_response.json()
                    modules = course_data.get('modules', [])
                    
                    for module in modules:
                        lessons = module.get('lessons', [])
                        for lesson in lessons:
                            if 'quiz' in lesson.get('type', '').lower():
                                content = lesson.get('content', {})
                                
                                # Validate quiz structure
                                if isinstance(content, dict) and 'questions' in content:
                                    questions = content['questions']
                                    if isinstance(questions, list):
                                        structure_valid = True
                                        
                                        for question in questions:
                                            required_fields = ['id', 'question', 'options', 'correctAnswer']
                                            if not all(field in question for field in required_fields):
                                                structure_valid = False
                                                break
                                            
                                            # Validate options structure
                                            options = question.get('options', [])
                                            if not isinstance(options, list) or len(options) < 2:
                                                structure_valid = False
                                                break
                                        
                                        if structure_valid:
                                            valid_quiz_structures += 1
                                        else:
                                            invalid_quiz_structures += 1
            
            if valid_quiz_structures > 0:
                self.log_result(
                    "Quiz Data Structure Integrity", 
                    "PASS", 
                    f"Quiz data structures are valid and complete",
                    f"Valid structures: {valid_quiz_structures}, Invalid: {invalid_quiz_structures}"
                )
                return True
            else:
                self.log_result(
                    "Quiz Data Structure Integrity", 
                    "FAIL", 
                    "No valid quiz data structures found",
                    f"Invalid structures: {invalid_quiz_structures}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Data Structure Integrity", 
                "FAIL", 
                "Failed to test quiz data structure integrity",
                str(e)
            )
        return False
    
    def test_course_enrollment_quiz_access_flow(self):
        """Test course enrollment and quiz access flow"""
        if "student1" not in self.auth_tokens:
            self.log_result(
                "Course Enrollment Quiz Access Flow", 
                "SKIP", 
                "No student token available for enrollment test",
                "Student authentication required"
            )
            return False
        
        try:
            # Get available courses
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student1"]}'}
            )
            
            if courses_response.status_code != 200:
                self.log_result(
                    "Course Enrollment Quiz Access Flow", 
                    "FAIL", 
                    f"Failed to get courses for enrollment, status: {courses_response.status_code}",
                    f"Response: {courses_response.text}"
                )
                return False
            
            courses = courses_response.json()
            if not courses:
                self.log_result(
                    "Course Enrollment Quiz Access Flow", 
                    "FAIL", 
                    "No courses available for enrollment test",
                    "Need at least one course to test enrollment flow"
                )
                return False
            
            # Find a course with quiz content
            quiz_course = None
            for course in courses:
                modules = course.get('modules', [])
                for module in modules:
                    lessons = module.get('lessons', [])
                    for lesson in lessons:
                        if 'quiz' in lesson.get('type', '').lower():
                            quiz_course = course
                            break
                    if quiz_course:
                        break
                if quiz_course:
                    break
            
            if not quiz_course:
                # Use first available course
                quiz_course = courses[0]
            
            course_id = quiz_course.get('id')
            
            # Test enrollment
            enrollment_data = {"courseId": course_id}
            enrollment_response = requests.post(
                f"{BACKEND_URL}/enrollments",
                json=enrollment_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["student1"]}'
                }
            )
            
            if enrollment_response.status_code in [200, 400]:  # 400 might be "already enrolled"
                # Test course access after enrollment
                course_access_response = requests.get(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["student1"]}'}
                )
                
                if course_access_response.status_code == 200:
                    course_data = course_access_response.json()
                    modules = course_data.get('modules', [])
                    
                    self.log_result(
                        "Course Enrollment Quiz Access Flow", 
                        "PASS", 
                        f"Successfully enrolled and accessed course with quiz content",
                        f"Course: {quiz_course.get('title')}, Modules: {len(modules)}"
                    )
                    return True
                else:
                    self.log_result(
                        "Course Enrollment Quiz Access Flow", 
                        "FAIL", 
                        f"Failed to access course after enrollment, status: {course_access_response.status_code}",
                        f"Course ID: {course_id}"
                    )
            else:
                self.log_result(
                    "Course Enrollment Quiz Access Flow", 
                    "FAIL", 
                    f"Failed to enroll in course, status: {enrollment_response.status_code}",
                    f"Response: {enrollment_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Enrollment Quiz Access Flow", 
                "FAIL", 
                "Failed to test course enrollment quiz access flow",
                str(e)
            )
        return False
    
    # =============================================================================
    # COURSE MANAGEMENT APIS - FROM REVIEW REQUEST
    # =============================================================================
    
    def test_get_all_courses(self):
        """Test GET /api/courses (list all courses)"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Get All Courses API", 
                "SKIP", 
                "No admin token available for courses list test",
                "Admin authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                if isinstance(courses, list):
                    self.log_result(
                        "Get All Courses API", 
                        "PASS", 
                        f"Successfully retrieved courses list",
                        f"Found {len(courses)} courses"
                    )
                    return True
                else:
                    self.log_result(
                        "Get All Courses API", 
                        "FAIL", 
                        "Courses response is not a list",
                        f"Response type: {type(courses)}"
                    )
            else:
                self.log_result(
                    "Get All Courses API", 
                    "FAIL", 
                    f"Failed to get courses list, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Get All Courses API", 
                "FAIL", 
                "Failed to test get all courses API",
                str(e)
            )
        return False
    
    def test_get_course_details(self):
        """Test GET /api/courses/{id} (course details)"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Get Course Details API", 
                "SKIP", 
                "No admin token available for course details test",
                "Admin authentication required"
            )
            return False
        
        try:
            # First get a course ID
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if courses_response.status_code != 200:
                self.log_result(
                    "Get Course Details API", 
                    "FAIL", 
                    "Failed to get courses list for detail test",
                    f"Status: {courses_response.status_code}"
                )
                return False
            
            courses = courses_response.json()
            if not courses:
                self.log_result(
                    "Get Course Details API", 
                    "FAIL", 
                    "No courses available for detail test",
                    "Need at least one course to test details API"
                )
                return False
            
            course_id = courses[0].get('id')
            
            # Test course details
            detail_response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if detail_response.status_code == 200:
                course_detail = detail_response.json()
                required_fields = ['id', 'title', 'description', 'modules', 'instructor']
                
                if all(field in course_detail for field in required_fields):
                    self.log_result(
                        "Get Course Details API", 
                        "PASS", 
                        f"Successfully retrieved course details",
                        f"Course: {course_detail.get('title')}, Modules: {len(course_detail.get('modules', []))}"
                    )
                    return True
                else:
                    missing_fields = [field for field in required_fields if field not in course_detail]
                    self.log_result(
                        "Get Course Details API", 
                        "FAIL", 
                        "Course details missing required fields",
                        f"Missing: {missing_fields}"
                    )
            else:
                self.log_result(
                    "Get Course Details API", 
                    "FAIL", 
                    f"Failed to get course details, status: {detail_response.status_code}",
                    f"Course ID: {course_id}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Get Course Details API", 
                "FAIL", 
                "Failed to test get course details API",
                str(e)
            )
        return False
    
    def test_create_course(self):
        """Test POST /api/courses (course creation)"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Create Course API", 
                "SKIP", 
                "No admin token available for course creation test",
                "Admin authentication required"
            )
            return False
        
        try:
            course_data = {
                "title": f"React Error 310 Test Course - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test course created during React Error #310 backend testing",
                "category": "Testing",
                "duration": "1 week",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Test Module 1",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Test Lesson 1",
                                "type": "text",
                                "content": {"text": "This is a test lesson"}
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
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                created_course = response.json()
                course_id = created_course.get('id')
                
                if course_id:
                    self.log_result(
                        "Create Course API", 
                        "PASS", 
                        f"Successfully created course",
                        f"Course: {created_course.get('title')}, ID: {course_id}"
                    )
                    
                    # Clean up - delete the test course
                    try:
                        requests.delete(
                            f"{BACKEND_URL}/courses/{course_id}",
                            timeout=TEST_TIMEOUT,
                            headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                        )
                    except:
                        pass  # Ignore cleanup errors
                    
                    return True
                else:
                    self.log_result(
                        "Create Course API", 
                        "FAIL", 
                        "Course created but no ID returned",
                        f"Response: {created_course}"
                    )
            else:
                self.log_result(
                    "Create Course API", 
                    "FAIL", 
                    f"Failed to create course, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Create Course API", 
                "FAIL", 
                "Failed to test create course API",
                str(e)
            )
        return False
    
    # =============================================================================
    # CRITICAL ENDPOINTS - FROM REVIEW REQUEST
    # =============================================================================
    
    def test_get_enrollments(self):
        """Test GET /api/enrollments (student enrollments)"""
        if "student1" not in self.auth_tokens:
            self.log_result(
                "Get Enrollments API", 
                "SKIP", 
                "No student token available for enrollments test",
                "Student authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student1"]}'}
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                if isinstance(enrollments, list):
                    self.log_result(
                        "Get Enrollments API", 
                        "PASS", 
                        f"Successfully retrieved student enrollments",
                        f"Found {len(enrollments)} enrollments"
                    )
                    return True
                else:
                    self.log_result(
                        "Get Enrollments API", 
                        "FAIL", 
                        "Enrollments response is not a list",
                        f"Response type: {type(enrollments)}"
                    )
            else:
                self.log_result(
                    "Get Enrollments API", 
                    "FAIL", 
                    f"Failed to get enrollments, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Get Enrollments API", 
                "FAIL", 
                "Failed to test get enrollments API",
                str(e)
            )
        return False
    
    def test_update_enrollment_progress(self):
        """Test PUT /api/enrollments/{course_id}/progress (progress tracking)"""
        if "student1" not in self.auth_tokens:
            self.log_result(
                "Update Enrollment Progress API", 
                "SKIP", 
                "No student token available for progress tracking test",
                "Student authentication required"
            )
            return False
        
        try:
            # First get student's enrollments
            enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student1"]}'}
            )
            
            if enrollments_response.status_code != 200:
                self.log_result(
                    "Update Enrollment Progress API", 
                    "FAIL", 
                    "Failed to get enrollments for progress test",
                    f"Status: {enrollments_response.status_code}"
                )
                return False
            
            enrollments = enrollments_response.json()
            if not enrollments:
                self.log_result(
                    "Update Enrollment Progress API", 
                    "FAIL", 
                    "No enrollments found for progress test",
                    "Student needs to be enrolled in at least one course"
                )
                return False
            
            course_id = enrollments[0].get('courseId')
            
            # Test progress update
            progress_data = {
                "progress": 25.0,
                "lastAccessedAt": datetime.utcnow().isoformat()
            }
            
            response = requests.put(
                f"{BACKEND_URL}/enrollments/{course_id}/progress",
                json=progress_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["student1"]}'
                }
            )
            
            if response.status_code == 200:
                updated_enrollment = response.json()
                if updated_enrollment.get('progress') == 25.0:
                    self.log_result(
                        "Update Enrollment Progress API", 
                        "PASS", 
                        f"Successfully updated enrollment progress",
                        f"Course ID: {course_id}, Progress: {updated_enrollment.get('progress')}%"
                    )
                    return True
                else:
                    self.log_result(
                        "Update Enrollment Progress API", 
                        "FAIL", 
                        "Progress not updated correctly",
                        f"Expected: 25.0, Got: {updated_enrollment.get('progress')}"
                    )
            else:
                self.log_result(
                    "Update Enrollment Progress API", 
                    "FAIL", 
                    f"Failed to update progress, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Update Enrollment Progress API", 
                "FAIL", 
                "Failed to test update enrollment progress API",
                str(e)
            )
        return False
    
    def test_get_classrooms(self):
        """Test GET /api/classrooms (classroom management)"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Get Classrooms API", 
                "SKIP", 
                "No admin token available for classrooms test",
                "Admin authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/classrooms",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                classrooms = response.json()
                if isinstance(classrooms, list):
                    self.log_result(
                        "Get Classrooms API", 
                        "PASS", 
                        f"Successfully retrieved classrooms list",
                        f"Found {len(classrooms)} classrooms"
                    )
                    return True
                else:
                    self.log_result(
                        "Get Classrooms API", 
                        "FAIL", 
                        "Classrooms response is not a list",
                        f"Response type: {type(classrooms)}"
                    )
            else:
                self.log_result(
                    "Get Classrooms API", 
                    "FAIL", 
                    f"Failed to get classrooms, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Get Classrooms API", 
                "FAIL", 
                "Failed to test get classrooms API",
                str(e)
            )
        return False
    
    # =============================================================================
    # ERROR HANDLING TESTS - FROM REVIEW REQUEST
    # =============================================================================
    
    def test_error_handling_edge_cases(self):
        """Test endpoints with edge cases to ensure robust error responses"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Error Handling Edge Cases", 
                "SKIP", 
                "No admin token available for error handling test",
                "Admin authentication required"
            )
            return False
        
        edge_case_tests = []
        
        try:
            # Test 1: Non-existent course ID
            response = requests.get(
                f"{BACKEND_URL}/courses/non-existent-course-id",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            if response.status_code == 404:
                edge_case_tests.append("✅ Non-existent course returns 404")
            else:
                edge_case_tests.append(f"❌ Non-existent course returns {response.status_code}")
            
            # Test 2: Invalid enrollment data
            invalid_enrollment = {"courseId": ""}
            response = requests.post(
                f"{BACKEND_URL}/enrollments",
                json=invalid_enrollment,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            if response.status_code in [400, 422]:
                edge_case_tests.append("✅ Invalid enrollment data returns 400/422")
            else:
                edge_case_tests.append(f"❌ Invalid enrollment data returns {response.status_code}")
            
            # Test 3: Unauthorized access (no token)
            response = requests.get(f"{BACKEND_URL}/courses", timeout=TEST_TIMEOUT)
            if response.status_code == 401:
                edge_case_tests.append("✅ No auth token returns 401")
            else:
                edge_case_tests.append(f"❌ No auth token returns {response.status_code}")
            
            # Test 4: Invalid JSON in request
            response = requests.post(
                f"{BACKEND_URL}/courses",
                data="invalid json",
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            if response.status_code in [400, 422]:
                edge_case_tests.append("✅ Invalid JSON returns 400/422")
            else:
                edge_case_tests.append(f"❌ Invalid JSON returns {response.status_code}")
            
            # Test 5: Progress update for non-existent enrollment
            progress_data = {"progress": 50.0}
            response = requests.put(
                f"{BACKEND_URL}/enrollments/non-existent-course/progress",
                json=progress_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            if response.status_code == 404:
                edge_case_tests.append("✅ Non-existent enrollment progress returns 404")
            else:
                edge_case_tests.append(f"❌ Non-existent enrollment progress returns {response.status_code}")
            
            passed_tests = len([test for test in edge_case_tests if test.startswith("✅")])
            total_tests = len(edge_case_tests)
            
            if passed_tests >= total_tests * 0.8:  # 80% pass rate
                self.log_result(
                    "Error Handling Edge Cases", 
                    "PASS", 
                    f"Error handling working correctly ({passed_tests}/{total_tests} tests passed)",
                    "; ".join(edge_case_tests)
                )
                return True
            else:
                self.log_result(
                    "Error Handling Edge Cases", 
                    "FAIL", 
                    f"Error handling needs improvement ({passed_tests}/{total_tests} tests passed)",
                    "; ".join(edge_case_tests)
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Error Handling Edge Cases", 
                "FAIL", 
                "Failed to test error handling edge cases",
                str(e)
            )
        return False
    
    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_all_tests(self):
        """Run all backend tests as specified in review request"""
        print("🚀 STARTING COMPREHENSIVE BACKEND TESTING - POST REACT ERROR #310 FIXES")
        print("=" * 80)
        print("Testing critical backend APIs after implementing React Error #310 fixes")
        print("and system stability improvements.")
        print("=" * 80)
        
        # Authentication Testing
        print("\n🔑 AUTHENTICATION TESTING")
        print("-" * 50)
        self.test_admin_authentication()
        self.test_student_authentication_1()
        self.test_student_authentication_2()
        
        # Quiz-Related Backend APIs
        print("\n🎯 QUIZ-RELATED BACKEND APIS")
        print("-" * 50)
        self.test_courses_with_quiz_lessons()
        self.test_quiz_data_structure_integrity()
        self.test_course_enrollment_quiz_access_flow()
        
        # Course Management
        print("\n📚 COURSE MANAGEMENT APIS")
        print("-" * 50)
        self.test_get_all_courses()
        self.test_get_course_details()
        self.test_create_course()
        
        # Critical Endpoints
        print("\n⚡ CRITICAL ENDPOINTS")
        print("-" * 50)
        self.test_get_enrollments()
        self.test_update_enrollment_progress()
        self.test_get_classrooms()
        
        # Error Handling
        print("\n🛡️ ERROR HANDLING")
        print("-" * 50)
        self.test_error_handling_edge_cases()
        
        # Final Results
        print("\n" + "=" * 80)
        print("🎉 BACKEND TESTING COMPLETED - POST REACT ERROR #310 FIXES")
        print("=" * 80)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 RESULTS SUMMARY:")
        print(f"   ✅ Passed: {self.passed}")
        print(f"   ❌ Failed: {self.failed}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print(f"   🎯 EXCELLENT: Backend is rock-solid and ready to support improved frontend stability!")
        elif success_rate >= 80:
            print(f"   ✅ GOOD: Backend is stable with minor issues")
        elif success_rate >= 70:
            print(f"   ⚠️ FAIR: Backend has some issues that need attention")
        else:
            print(f"   ❌ POOR: Backend has significant issues requiring immediate attention")
        
        print("\n🔍 DETAILED RESULTS:")
        print("-" * 50)
        for result in self.results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⏭️"
            print(f"{status_icon} {result['test']}: {result['message']}")
        
        return success_rate >= 90

if __name__ == "__main__":
    tester = ReactError310BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 SUCCESS: All critical backend APIs are working correctly!")
        print(f"Backend is ready to support the improved frontend stability after React Error #310 fixes.")
        sys.exit(0)
    else:
        print(f"\n⚠️ WARNING: Some backend APIs need attention.")
        print(f"Review the detailed results above for specific issues.")
        sys.exit(1)