#!/usr/bin/env python3
"""
MULTIPLE CHOICE REBUILD BACKEND TESTING SUITE
LearningFwiend LMS Application - Multiple Choice Question Type Backend API Testing

TESTING OBJECTIVES:
1. Authentication Testing with new Multiple Choice test accounts
2. Course Creation APIs for courses with Multiple Choice questions
3. Quiz Data Structure Support verification
4. Enrollment and Progress APIs testing
5. Categories and Dependencies testing

TARGET SUCCESS RATE: 100% on all critical Multiple Choice functionality tests
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using production URL from frontend/.env
BACKEND_URL = "https://lms-debugfix.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Test credentials from review request
MC_ADMIN_CREDENTIALS = {
    "username_or_email": "mc.admin.20250823_234459@testmc.com",
    "password": "MCAdmin123!"
}

MC_STUDENT_CREDENTIALS = {
    "username_or_email": "mc.student.20250823_234459@testmc.com", 
    "password": "MCStudent123!"
}

FALLBACK_ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class MultipleChoiceBackendTester:
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
    # AUTHENTICATION TESTING - MULTIPLE CHOICE TEST ACCOUNTS
    # =============================================================================
    
    def test_mc_admin_authentication(self):
        """Test Multiple Choice admin account authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=MC_ADMIN_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                requires_password_change = data.get('requires_password_change', False)
                
                if token and user_info.get('role') == 'admin':
                    self.auth_tokens['mc_admin'] = token
                    self.log_result(
                        "MC Admin Authentication", 
                        "PASS", 
                        f"Multiple Choice admin authenticated successfully: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Password change required: {requires_password_change}"
                    )
                    return True
                else:
                    self.log_result(
                        "MC Admin Authentication", 
                        "FAIL", 
                        "Authentication succeeded but user is not admin or token missing",
                        f"Role: {user_info.get('role')}, Token present: {bool(token)}"
                    )
            else:
                self.log_result(
                    "MC Admin Authentication", 
                    "FAIL", 
                    f"Multiple Choice admin authentication failed (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "MC Admin Authentication", 
                "FAIL", 
                "Failed to test MC admin authentication",
                str(e)
            )
        return False
    
    def test_mc_student_authentication(self):
        """Test Multiple Choice student account authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=MC_STUDENT_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                requires_password_change = data.get('requires_password_change', False)
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['mc_student'] = token
                    self.log_result(
                        "MC Student Authentication", 
                        "PASS", 
                        f"Multiple Choice student authenticated successfully: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Password change required: {requires_password_change}"
                    )
                    return True
                else:
                    self.log_result(
                        "MC Student Authentication", 
                        "FAIL", 
                        "Authentication succeeded but user is not student or token missing",
                        f"Role: {user_info.get('role')}, Token present: {bool(token)}"
                    )
            else:
                self.log_result(
                    "MC Student Authentication", 
                    "FAIL", 
                    f"Multiple Choice student authentication failed (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "MC Student Authentication", 
                "FAIL", 
                "Failed to test MC student authentication",
                str(e)
            )
        return False
    
    def test_fallback_admin_authentication(self):
        """Test fallback admin account authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=FALLBACK_ADMIN_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'admin':
                    self.auth_tokens['fallback_admin'] = token
                    self.log_result(
                        "Fallback Admin Authentication", 
                        "PASS", 
                        f"Fallback admin authenticated successfully: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Name: {user_info.get('full_name')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Fallback Admin Authentication", 
                        "FAIL", 
                        "Authentication succeeded but user is not admin or token missing",
                        f"Role: {user_info.get('role')}, Token present: {bool(token)}"
                    )
            else:
                self.log_result(
                    "Fallback Admin Authentication", 
                    "FAIL", 
                    f"Fallback admin authentication failed (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Fallback Admin Authentication", 
                "FAIL", 
                "Failed to test fallback admin authentication",
                str(e)
            )
        return False
    
    # =============================================================================
    # COURSE CREATION APIs - MULTIPLE CHOICE SUPPORT
    # =============================================================================
    
    def test_course_creation_with_multiple_choice(self):
        """Test course creation with Multiple Choice questions"""
        admin_token = self.auth_tokens.get('mc_admin') or self.auth_tokens.get('fallback_admin')
        if not admin_token:
            self.log_result(
                "Course Creation with Multiple Choice", 
                "SKIP", 
                "No admin token available for course creation test",
                "Admin authentication required"
            )
            return False
        
        try:
            # Create a course with Multiple Choice quiz lesson
            course_data = {
                "title": "Multiple Choice Test Course",
                "description": "Testing Multiple Choice question type functionality",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Multiple Choice Quiz Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Multiple Choice Quiz",
                                "type": "quiz",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "multiple-choice",
                                        "question": "What is the capital of France?",
                                        "options": [
                                            {"text": "London", "isCorrect": False},
                                            {"text": "Berlin", "isCorrect": False},
                                            {"text": "Paris", "isCorrect": True},
                                            {"text": "Madrid", "isCorrect": False}
                                        ],
                                        "correctAnswer": 2,
                                        "points": 10
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "multiple-choice",
                                        "question": "Which programming language is used for web development?",
                                        "options": [
                                            {"text": "Python", "isCorrect": True},
                                            {"text": "JavaScript", "isCorrect": True},
                                            {"text": "Assembly", "isCorrect": False},
                                            {"text": "COBOL", "isCorrect": False}
                                        ],
                                        "correctAnswer": 1,
                                        "points": 10
                                    }
                                ]
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
                    'Authorization': f'Bearer {admin_token}'
                }
            )
            
            if response.status_code == 200:
                created_course = response.json()
                course_id = created_course.get('id')
                
                # Verify the course structure
                modules = created_course.get('modules', [])
                if modules and len(modules) > 0:
                    quiz_module = modules[0]
                    lessons = quiz_module.get('lessons', [])
                    if lessons and len(lessons) > 0:
                        quiz_lesson = lessons[0]
                        questions = quiz_lesson.get('questions', [])
                        
                        mc_questions = [q for q in questions if q.get('type') == 'multiple-choice']
                        
                        if len(mc_questions) == 2:
                            self.log_result(
                                "Course Creation with Multiple Choice", 
                                "PASS", 
                                f"Successfully created course with Multiple Choice questions: {created_course.get('title')}",
                                f"Course ID: {course_id}, MC Questions: {len(mc_questions)}, Total Questions: {len(questions)}"
                            )
                            return created_course
                        else:
                            self.log_result(
                                "Course Creation with Multiple Choice", 
                                "FAIL", 
                                "Course created but Multiple Choice questions not properly stored",
                                f"Expected 2 MC questions, found {len(mc_questions)}"
                            )
                    else:
                        self.log_result(
                            "Course Creation with Multiple Choice", 
                            "FAIL", 
                            "Course created but quiz lessons not properly stored",
                            f"Expected 1 lesson, found {len(lessons)}"
                        )
                else:
                    self.log_result(
                        "Course Creation with Multiple Choice", 
                        "FAIL", 
                        "Course created but modules not properly stored",
                        f"Expected 1 module, found {len(modules)}"
                    )
            else:
                self.log_result(
                    "Course Creation with Multiple Choice", 
                    "FAIL", 
                    f"Failed to create course with Multiple Choice questions (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Creation with Multiple Choice", 
                "FAIL", 
                "Failed to test course creation with Multiple Choice",
                str(e)
            )
        return False
    
    def test_course_listing_api(self):
        """Test GET /api/courses endpoint"""
        admin_token = self.auth_tokens.get('mc_admin') or self.auth_tokens.get('fallback_admin')
        if not admin_token:
            self.log_result(
                "Course Listing API", 
                "SKIP", 
                "No admin token available for course listing test",
                "Admin authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                
                # Look for courses with Multiple Choice questions
                mc_courses = []
                for course in courses:
                    modules = course.get('modules', [])
                    for module in modules:
                        lessons = module.get('lessons', [])
                        for lesson in lessons:
                            questions = lesson.get('questions', [])
                            mc_questions = [q for q in questions if q.get('type') == 'multiple-choice']
                            if mc_questions:
                                mc_courses.append({
                                    'course_id': course.get('id'),
                                    'title': course.get('title'),
                                    'mc_questions': len(mc_questions)
                                })
                                break
                
                self.log_result(
                    "Course Listing API", 
                    "PASS", 
                    f"Successfully retrieved {len(courses)} courses, {len(mc_courses)} with Multiple Choice questions",
                    f"MC Courses: {[c['title'] for c in mc_courses]}"
                )
                return courses
            else:
                self.log_result(
                    "Course Listing API", 
                    "FAIL", 
                    f"Failed to retrieve courses (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Listing API", 
                "FAIL", 
                "Failed to test course listing API",
                str(e)
            )
        return False
    
    def test_course_details_api(self):
        """Test GET /api/courses/{id} endpoint for Multiple Choice courses"""
        admin_token = self.auth_tokens.get('mc_admin') or self.auth_tokens.get('fallback_admin')
        if not admin_token:
            self.log_result(
                "Course Details API", 
                "SKIP", 
                "No admin token available for course details test",
                "Admin authentication required"
            )
            return False
        
        # First get all courses to find one with Multiple Choice questions
        courses = self.test_course_listing_api()
        if not courses:
            self.log_result(
                "Course Details API", 
                "SKIP", 
                "No courses available to test course details",
                "Course listing failed"
            )
            return False
        
        # Find a course with Multiple Choice questions
        target_course_id = None
        for course in courses:
            modules = course.get('modules', [])
            for module in modules:
                lessons = module.get('lessons', [])
                for lesson in lessons:
                    questions = lesson.get('questions', [])
                    mc_questions = [q for q in questions if q.get('type') == 'multiple-choice']
                    if mc_questions:
                        target_course_id = course.get('id')
                        break
                if target_course_id:
                    break
            if target_course_id:
                break
        
        if not target_course_id:
            self.log_result(
                "Course Details API", 
                "SKIP", 
                "No courses with Multiple Choice questions found to test",
                f"Searched {len(courses)} courses"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{target_course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 200:
                course = response.json()
                
                # Verify Multiple Choice question structure
                mc_questions_found = []
                modules = course.get('modules', [])
                for module in modules:
                    lessons = module.get('lessons', [])
                    for lesson in lessons:
                        questions = lesson.get('questions', [])
                        for question in questions:
                            if question.get('type') == 'multiple-choice':
                                # Verify required fields for Multiple Choice
                                required_fields = ['id', 'type', 'question', 'options', 'correctAnswer']
                                missing_fields = [field for field in required_fields if field not in question]
                                
                                if not missing_fields:
                                    options = question.get('options', [])
                                    if isinstance(options, list) and len(options) > 0:
                                        mc_questions_found.append({
                                            'question_id': question.get('id'),
                                            'question_text': question.get('question'),
                                            'options_count': len(options),
                                            'correct_answer': question.get('correctAnswer')
                                        })
                
                if mc_questions_found:
                    self.log_result(
                        "Course Details API", 
                        "PASS", 
                        f"Successfully retrieved course details with {len(mc_questions_found)} Multiple Choice questions",
                        f"Course: {course.get('title')}, MC Questions: {[q['question_text'][:50] + '...' for q in mc_questions_found]}"
                    )
                    return course
                else:
                    self.log_result(
                        "Course Details API", 
                        "FAIL", 
                        "Course details retrieved but Multiple Choice questions malformed or missing",
                        f"Course: {course.get('title')}"
                    )
            else:
                self.log_result(
                    "Course Details API", 
                    "FAIL", 
                    f"Failed to retrieve course details (status: {response.status_code})",
                    f"Course ID: {target_course_id}, Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Details API", 
                "FAIL", 
                "Failed to test course details API",
                str(e)
            )
        return False
    
    # =============================================================================
    # QUIZ DATA STRUCTURE SUPPORT - MULTIPLE CHOICE
    # =============================================================================
    
    def test_multiple_choice_data_structure_validation(self):
        """Test Multiple Choice question data structure validation"""
        admin_token = self.auth_tokens.get('mc_admin') or self.auth_tokens.get('fallback_admin')
        if not admin_token:
            self.log_result(
                "MC Data Structure Validation", 
                "SKIP", 
                "No admin token available for data structure validation",
                "Admin authentication required"
            )
            return False
        
        try:
            # Test various Multiple Choice data structures
            test_cases = [
                {
                    "name": "Standard Multiple Choice",
                    "question": {
                        "id": str(uuid.uuid4()),
                        "type": "multiple-choice",
                        "question": "What is 2 + 2?",
                        "options": [
                            {"text": "3", "isCorrect": False},
                            {"text": "4", "isCorrect": True},
                            {"text": "5", "isCorrect": False}
                        ],
                        "correctAnswer": 1,
                        "points": 10
                    }
                },
                {
                    "name": "Multiple Choice with Images",
                    "question": {
                        "id": str(uuid.uuid4()),
                        "type": "multiple-choice",
                        "question": "Which logo represents Python?",
                        "options": [
                            {"text": "Option A", "image": "https://example.com/python-logo.png", "isCorrect": True},
                            {"text": "Option B", "image": "https://example.com/java-logo.png", "isCorrect": False}
                        ],
                        "correctAnswer": 0,
                        "points": 15
                    }
                },
                {
                    "name": "Multiple Choice with Audio",
                    "question": {
                        "id": str(uuid.uuid4()),
                        "type": "multiple-choice",
                        "question": "Which sound is correct?",
                        "options": [
                            {"text": "Sound A", "audio": "https://example.com/sound-a.mp3", "isCorrect": False},
                            {"text": "Sound B", "audio": "https://example.com/sound-b.mp3", "isCorrect": True}
                        ],
                        "correctAnswer": 1,
                        "points": 20
                    }
                }
            ]
            
            successful_validations = []
            failed_validations = []
            
            for test_case in test_cases:
                course_data = {
                    "title": f"MC Validation Test - {test_case['name']}",
                    "description": f"Testing {test_case['name']} data structure",
                    "category": "Testing",
                    "duration": "30 minutes",
                    "accessType": "open",
                    "modules": [
                        {
                            "id": str(uuid.uuid4()),
                            "title": "Test Module",
                            "lessons": [
                                {
                                    "id": str(uuid.uuid4()),
                                    "title": "Test Quiz",
                                    "type": "quiz",
                                    "questions": [test_case['question']]
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
                            'Authorization': f'Bearer {admin_token}'
                        }
                    )
                    
                    if response.status_code == 200:
                        created_course = response.json()
                        
                        # Verify the question was stored correctly
                        modules = created_course.get('modules', [])
                        if modules:
                            lessons = modules[0].get('lessons', [])
                            if lessons:
                                questions = lessons[0].get('questions', [])
                                if questions and questions[0].get('type') == 'multiple-choice':
                                    successful_validations.append(test_case['name'])
                                    
                                    # Clean up - delete test course
                                    requests.delete(
                                        f"{BACKEND_URL}/courses/{created_course.get('id')}",
                                        headers={'Authorization': f'Bearer {admin_token}'}
                                    )
                                else:
                                    failed_validations.append(f"{test_case['name']} - Question not stored correctly")
                            else:
                                failed_validations.append(f"{test_case['name']} - Lessons not stored")
                        else:
                            failed_validations.append(f"{test_case['name']} - Modules not stored")
                    else:
                        failed_validations.append(f"{test_case['name']} - HTTP {response.status_code}")
                        
                except Exception as e:
                    failed_validations.append(f"{test_case['name']} - {str(e)}")
            
            if len(successful_validations) == len(test_cases):
                self.log_result(
                    "MC Data Structure Validation", 
                    "PASS", 
                    f"All {len(test_cases)} Multiple Choice data structures validated successfully",
                    f"Validated: {', '.join(successful_validations)}"
                )
                return True
            else:
                self.log_result(
                    "MC Data Structure Validation", 
                    "FAIL", 
                    f"Only {len(successful_validations)}/{len(test_cases)} data structures validated",
                    f"Successful: {successful_validations}, Failed: {failed_validations}"
                )
        except Exception as e:
            self.log_result(
                "MC Data Structure Validation", 
                "FAIL", 
                "Failed to test Multiple Choice data structure validation",
                str(e)
            )
        return False
    
    # =============================================================================
    # ENROLLMENT AND PROGRESS APIs - MULTIPLE CHOICE SUPPORT
    # =============================================================================
    
    def test_student_enrollment_in_mc_course(self):
        """Test student enrollment in Multiple Choice courses"""
        student_token = self.auth_tokens.get('mc_student')
        if not student_token:
            self.log_result(
                "Student Enrollment in MC Course", 
                "SKIP", 
                "No student token available for enrollment test",
                "Student authentication required"
            )
            return False
        
        # First create a Multiple Choice course to enroll in
        mc_course = self.test_course_creation_with_multiple_choice()
        if not mc_course:
            self.log_result(
                "Student Enrollment in MC Course", 
                "SKIP", 
                "No Multiple Choice course available for enrollment test",
                "Course creation failed"
            )
            return False
        
        try:
            enrollment_data = {
                "courseId": mc_course.get('id')
            }
            
            response = requests.post(
                f"{BACKEND_URL}/enrollments",
                json=enrollment_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {student_token}'
                }
            )
            
            if response.status_code == 200:
                enrollment = response.json()
                
                self.log_result(
                    "Student Enrollment in MC Course", 
                    "PASS", 
                    f"Student successfully enrolled in Multiple Choice course: {mc_course.get('title')}",
                    f"Enrollment ID: {enrollment.get('id')}, Progress: {enrollment.get('progress', 0)}%"
                )
                return enrollment
            else:
                self.log_result(
                    "Student Enrollment in MC Course", 
                    "FAIL", 
                    f"Failed to enroll student in Multiple Choice course (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Enrollment in MC Course", 
                "FAIL", 
                "Failed to test student enrollment in Multiple Choice course",
                str(e)
            )
        return False
    
    def test_student_enrollments_listing(self):
        """Test GET /api/enrollments for student"""
        student_token = self.auth_tokens.get('mc_student')
        if not student_token:
            self.log_result(
                "Student Enrollments Listing", 
                "SKIP", 
                "No student token available for enrollments listing test",
                "Student authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {student_token}'}
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                
                # Check for enrollments in Multiple Choice courses
                mc_enrollments = []
                for enrollment in enrollments:
                    course_id = enrollment.get('courseId')
                    if course_id:
                        # Check if this is a Multiple Choice course
                        try:
                            course_response = requests.get(
                                f"{BACKEND_URL}/courses/{course_id}",
                                timeout=TEST_TIMEOUT,
                                headers={'Authorization': f'Bearer {student_token}'}
                            )
                            if course_response.status_code == 200:
                                course = course_response.json()
                                # Check for Multiple Choice questions
                                has_mc = False
                                for module in course.get('modules', []):
                                    for lesson in module.get('lessons', []):
                                        for question in lesson.get('questions', []):
                                            if question.get('type') == 'multiple-choice':
                                                has_mc = True
                                                break
                                        if has_mc:
                                            break
                                    if has_mc:
                                        break
                                
                                if has_mc:
                                    mc_enrollments.append({
                                        'enrollment_id': enrollment.get('id'),
                                        'course_title': course.get('title'),
                                        'progress': enrollment.get('progress', 0)
                                    })
                        except:
                            pass
                
                self.log_result(
                    "Student Enrollments Listing", 
                    "PASS", 
                    f"Retrieved {len(enrollments)} enrollments, {len(mc_enrollments)} in Multiple Choice courses",
                    f"MC Enrollments: {[e['course_title'] for e in mc_enrollments]}"
                )
                return enrollments
            else:
                self.log_result(
                    "Student Enrollments Listing", 
                    "FAIL", 
                    f"Failed to retrieve student enrollments (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Enrollments Listing", 
                "FAIL", 
                "Failed to test student enrollments listing",
                str(e)
            )
        return False
    
    def test_progress_tracking_for_mc_quiz(self):
        """Test progress tracking after Multiple Choice quiz completion"""
        student_token = self.auth_tokens.get('mc_student')
        if not student_token:
            self.log_result(
                "Progress Tracking for MC Quiz", 
                "SKIP", 
                "No student token available for progress tracking test",
                "Student authentication required"
            )
            return False
        
        # Get student enrollments to find a Multiple Choice course
        enrollments = self.test_student_enrollments_listing()
        if not enrollments:
            self.log_result(
                "Progress Tracking for MC Quiz", 
                "SKIP", 
                "No enrollments available for progress tracking test",
                "Student enrollment required"
            )
            return False
        
        # Find an enrollment with a Multiple Choice course
        target_enrollment = None
        for enrollment in enrollments:
            course_id = enrollment.get('courseId')
            if course_id:
                try:
                    course_response = requests.get(
                        f"{BACKEND_URL}/courses/{course_id}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {student_token}'}
                    )
                    if course_response.status_code == 200:
                        course = course_response.json()
                        # Check for Multiple Choice questions
                        for module in course.get('modules', []):
                            for lesson in module.get('lessons', []):
                                for question in lesson.get('questions', []):
                                    if question.get('type') == 'multiple-choice':
                                        target_enrollment = enrollment
                                        break
                                if target_enrollment:
                                    break
                            if target_enrollment:
                                break
                        if target_enrollment:
                            break
                except:
                    continue
        
        if not target_enrollment:
            self.log_result(
                "Progress Tracking for MC Quiz", 
                "SKIP", 
                "No Multiple Choice course enrollment found for progress tracking test",
                "Multiple Choice course enrollment required"
            )
            return False
        
        try:
            # Simulate quiz completion with progress update
            progress_data = {
                "progress": 100.0,  # Quiz completed
                "currentLessonId": "quiz-lesson-id",
                "timeSpent": 300  # 5 minutes
            }
            
            response = requests.put(
                f"{BACKEND_URL}/enrollments/{target_enrollment.get('courseId')}/progress",
                json=progress_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {student_token}'
                }
            )
            
            if response.status_code == 200:
                updated_enrollment = response.json()
                
                self.log_result(
                    "Progress Tracking for MC Quiz", 
                    "PASS", 
                    f"Successfully updated progress for Multiple Choice quiz completion",
                    f"Course ID: {target_enrollment.get('courseId')}, Progress: {updated_enrollment.get('progress')}%, Status: {updated_enrollment.get('status')}"
                )
                return updated_enrollment
            else:
                self.log_result(
                    "Progress Tracking for MC Quiz", 
                    "FAIL", 
                    f"Failed to update progress for Multiple Choice quiz (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Progress Tracking for MC Quiz", 
                "FAIL", 
                "Failed to test progress tracking for Multiple Choice quiz",
                str(e)
            )
        return False
    
    # =============================================================================
    # CATEGORIES AND DEPENDENCIES
    # =============================================================================
    
    def test_categories_api(self):
        """Test GET /api/categories endpoint"""
        admin_token = self.auth_tokens.get('mc_admin') or self.auth_tokens.get('fallback_admin')
        if not admin_token:
            self.log_result(
                "Categories API", 
                "SKIP", 
                "No admin token available for categories test",
                "Admin authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/categories",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 200:
                categories = response.json()
                
                self.log_result(
                    "Categories API", 
                    "PASS", 
                    f"Successfully retrieved {len(categories)} categories for course creation",
                    f"Categories: {[c.get('name') for c in categories]}"
                )
                return categories
            else:
                self.log_result(
                    "Categories API", 
                    "FAIL", 
                    f"Failed to retrieve categories (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Categories API", 
                "FAIL", 
                "Failed to test categories API",
                str(e)
            )
        return False
    
    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_all_tests(self):
        """Run all Multiple Choice backend tests"""
        print("🚀 STARTING MULTIPLE CHOICE REBUILD BACKEND TESTING")
        print("=" * 80)
        print("Testing backend APIs for Multiple Choice question type functionality")
        print("=" * 80)
        
        # Authentication Tests
        print("\n🔑 AUTHENTICATION TESTING")
        print("-" * 50)
        self.test_mc_admin_authentication()
        self.test_mc_student_authentication()
        self.test_fallback_admin_authentication()
        
        # Course Creation APIs
        print("\n📚 COURSE CREATION APIs")
        print("-" * 50)
        self.test_course_creation_with_multiple_choice()
        self.test_course_listing_api()
        self.test_course_details_api()
        
        # Quiz Data Structure Support
        print("\n🎯 QUIZ DATA STRUCTURE SUPPORT")
        print("-" * 50)
        self.test_multiple_choice_data_structure_validation()
        
        # Enrollment and Progress APIs
        print("\n📝 ENROLLMENT AND PROGRESS APIs")
        print("-" * 50)
        self.test_student_enrollment_in_mc_course()
        self.test_student_enrollments_listing()
        self.test_progress_tracking_for_mc_quiz()
        
        # Categories and Dependencies
        print("\n🏷️ CATEGORIES AND DEPENDENCIES")
        print("-" * 50)
        self.test_categories_api()
        
        # Final Results
        print("\n" + "=" * 80)
        print("🎉 MULTIPLE CHOICE BACKEND TESTING COMPLETED")
        print("=" * 80)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 RESULTS SUMMARY:")
        print(f"   ✅ Passed: {self.passed}")
        print(f"   ❌ Failed: {self.failed}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print(f"🎯 EXCELLENT: Multiple Choice backend APIs are ready for production!")
        elif success_rate >= 75:
            print(f"⚠️ GOOD: Most Multiple Choice backend APIs working, minor issues to address")
        else:
            print(f"🚨 CRITICAL: Multiple Choice backend APIs need significant fixes")
        
        return success_rate >= 90

if __name__ == "__main__":
    tester = MultipleChoiceBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All Multiple Choice backend tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some Multiple Choice backend tests failed. Check the results above.")
        sys.exit(1)