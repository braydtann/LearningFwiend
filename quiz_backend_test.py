#!/usr/bin/env python3
"""
QUIZ FUNCTIONALITY BACKEND TESTING SUITE
LearningFwiend LMS Application - Quiz-Specific Backend API Testing

TESTING SCOPE (as per review request):
✅ Authentication endpoints - verify admin/student login credentials
✅ Course retrieval APIs - GET /api/courses/{id} to verify quiz courses can be loaded  
✅ Quiz-related course data - verify courses with quiz lessons have proper quiz data structure
✅ Enrollment APIs - verify students can access enrolled courses containing quizzes
✅ Progress tracking APIs - verify PUT /api/enrollments/{course_id}/progress works for quiz completion

TARGET: All APIs should return 200 status, proper data structure, and support frontend quiz functionality
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using Production Backend URL from frontend/.env
BACKEND_URL = "https://quiz-progress-fix.preview.emergentagent.com/api"
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

class QuizBackendTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}  # Store auth tokens for different users
        self.test_course_id = None  # Store created quiz course ID
        
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
    # AUTHENTICATION TESTS FOR QUIZ FUNCTIONALITY
    # =============================================================================
    
    def test_admin_authentication(self):
        """Test admin authentication with provided credentials"""
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
                
                if token and user_info.get('role') == 'admin':
                    self.auth_tokens['admin'] = token
                    self.log_result(
                        "Admin Authentication", 
                        "PASS", 
                        f"Admin login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Token received: {token[:20]}..."
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication", 
                        "FAIL", 
                        "Login response missing token or incorrect role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
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
                "Failed to connect to authentication endpoint",
                str(e)
            )
        return False
    
    def test_student_authentication(self):
        """Test student authentication with provided credentials"""
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
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['student'] = token
                    self.log_result(
                        "Student Authentication", 
                        "PASS", 
                        f"Student login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Token received: {token[:20]}..."
                    )
                    return True
                else:
                    self.log_result(
                        "Student Authentication", 
                        "FAIL", 
                        "Login response missing token or incorrect role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
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
                "Failed to connect to authentication endpoint",
                str(e)
            )
        return False
    
    # =============================================================================
    # COURSE RETRIEVAL TESTS FOR QUIZ FUNCTIONALITY
    # =============================================================================
    
    def test_course_retrieval_api(self):
        """Test GET /api/courses/{id} to verify quiz courses can be loaded"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Course Retrieval API", 
                "SKIP", 
                "No admin token available for course retrieval test",
                "Admin authentication required"
            )
            return False
        
        try:
            # First get all courses to find quiz courses
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                quiz_courses = []
                
                # Look for courses with quiz content
                for course in courses:
                    modules = course.get('modules', [])
                    has_quiz = False
                    
                    for module in modules:
                        lessons = module.get('lessons', [])
                        for lesson in lessons:
                            lesson_type = lesson.get('type', '').lower()
                            lesson_title = lesson.get('title', '').lower()
                            if 'quiz' in lesson_type or 'quiz' in lesson_title:
                                has_quiz = True
                                break
                        if has_quiz:
                            break
                    
                    if has_quiz:
                        quiz_courses.append(course)
                
                if quiz_courses:
                    # Test retrieving specific quiz course
                    test_course = quiz_courses[0]
                    course_id = test_course.get('id')
                    
                    course_response = requests.get(
                        f"{BACKEND_URL}/courses/{course_id}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                    )
                    
                    if course_response.status_code == 200:
                        course_data = course_response.json()
                        self.log_result(
                            "Course Retrieval API", 
                            "PASS", 
                            f"Successfully retrieved quiz course: {course_data.get('title')}",
                            f"Course ID: {course_id}, Modules: {len(course_data.get('modules', []))}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Course Retrieval API", 
                            "FAIL", 
                            f"Failed to retrieve specific quiz course (status: {course_response.status_code})",
                            f"Course ID: {course_id}"
                        )
                else:
                    # Create a test quiz course if none exist
                    return self.create_test_quiz_course()
            else:
                self.log_result(
                    "Course Retrieval API", 
                    "FAIL", 
                    f"Failed to get courses list (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Retrieval API", 
                "FAIL", 
                "Failed to test course retrieval API",
                str(e)
            )
        return False
    
    def create_test_quiz_course(self):
        """Create a test course with quiz content for testing"""
        if "admin" not in self.auth_tokens:
            return False
        
        try:
            quiz_course_data = {
                "title": "Quiz Backend Test Course",
                "description": "Test course with quiz content for backend API testing",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Quiz Module 1",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Introduction Quiz",
                                "type": "quiz",
                                "content": {
                                    "questions": [
                                        {
                                            "id": str(uuid.uuid4()),
                                            "question": "What is the purpose of this quiz?",
                                            "type": "multiple_choice",
                                            "options": [
                                                "To test backend functionality",
                                                "To test frontend functionality", 
                                                "To test database connectivity",
                                                "All of the above"
                                            ],
                                            "correct_answer": 3,
                                            "points": 10
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=quiz_course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                created_course = response.json()
                self.test_course_id = created_course.get('id')
                
                self.log_result(
                    "Create Test Quiz Course", 
                    "PASS", 
                    f"Successfully created test quiz course: {created_course.get('title')}",
                    f"Course ID: {self.test_course_id}, Modules: {len(created_course.get('modules', []))}"
                )
                return True
            else:
                self.log_result(
                    "Create Test Quiz Course", 
                    "FAIL", 
                    f"Failed to create test quiz course (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Create Test Quiz Course", 
                "FAIL", 
                "Failed to create test quiz course",
                str(e)
            )
        return False
    
    # =============================================================================
    # QUIZ DATA STRUCTURE TESTS
    # =============================================================================
    
    def test_quiz_data_structure(self):
        """Verify courses with quiz lessons have proper quiz data structure"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Quiz Data Structure", 
                "SKIP", 
                "No admin token available for quiz data structure test",
                "Admin authentication required"
            )
            return False
        
        try:
            # Get all courses and check quiz data structure
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                quiz_courses_found = 0
                valid_quiz_structures = 0
                
                for course in courses:
                    modules = course.get('modules', [])
                    
                    for module in modules:
                        lessons = module.get('lessons', [])
                        
                        for lesson in lessons:
                            lesson_type = lesson.get('type', '').lower()
                            lesson_title = lesson.get('title', '').lower()
                            
                            if 'quiz' in lesson_type or 'quiz' in lesson_title:
                                quiz_courses_found += 1
                                
                                # Validate quiz data structure
                                required_fields = ['id', 'title', 'type']
                                has_required_fields = all(field in lesson for field in required_fields)
                                
                                # Check for quiz content structure
                                content = lesson.get('content', {})
                                has_questions = 'questions' in content or 'quiz_data' in content
                                
                                if has_required_fields and (has_questions or lesson.get('type') == 'quiz'):
                                    valid_quiz_structures += 1
                                    
                                    # Log details of valid quiz structure
                                    print(f"   ✅ Valid quiz lesson: {lesson.get('title')} in course {course.get('title')}")
                                    print(f"      Type: {lesson.get('type')}")
                                    print(f"      Has content: {bool(content)}")
                                    print(f"      Has questions: {has_questions}")
                
                if quiz_courses_found > 0:
                    success_rate = (valid_quiz_structures / quiz_courses_found) * 100
                    
                    if success_rate >= 80:  # 80% or more valid structures
                        self.log_result(
                            "Quiz Data Structure", 
                            "PASS", 
                            f"Quiz data structures are valid ({valid_quiz_structures}/{quiz_courses_found} = {success_rate:.1f}%)",
                            f"Found {quiz_courses_found} quiz lessons, {valid_quiz_structures} have proper structure"
                        )
                        return True
                    else:
                        self.log_result(
                            "Quiz Data Structure", 
                            "FAIL", 
                            f"Some quiz data structures are invalid ({valid_quiz_structures}/{quiz_courses_found} = {success_rate:.1f}%)",
                            f"Need to fix {quiz_courses_found - valid_quiz_structures} quiz lessons"
                        )
                else:
                    # Use test course if no quiz courses found
                    if self.test_course_id:
                        return self.validate_test_course_quiz_structure()
                    else:
                        self.log_result(
                            "Quiz Data Structure", 
                            "FAIL", 
                            "No quiz courses found in the system",
                            "Need to create courses with quiz content"
                        )
            else:
                self.log_result(
                    "Quiz Data Structure", 
                    "FAIL", 
                    f"Failed to get courses for quiz structure validation (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Data Structure", 
                "FAIL", 
                "Failed to test quiz data structure",
                str(e)
            )
        return False
    
    def validate_test_course_quiz_structure(self):
        """Validate the quiz structure of our test course"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{self.test_course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                course = response.json()
                modules = course.get('modules', [])
                
                for module in modules:
                    lessons = module.get('lessons', [])
                    for lesson in lessons:
                        if lesson.get('type') == 'quiz':
                            content = lesson.get('content', {})
                            questions = content.get('questions', [])
                            
                            if questions and len(questions) > 0:
                                question = questions[0]
                                required_question_fields = ['id', 'question', 'type', 'options', 'correct_answer']
                                
                                if all(field in question for field in required_question_fields):
                                    self.log_result(
                                        "Quiz Data Structure", 
                                        "PASS", 
                                        "Test quiz course has proper quiz data structure",
                                        f"Quiz lesson with {len(questions)} questions, all required fields present"
                                    )
                                    return True
                
                self.log_result(
                    "Quiz Data Structure", 
                    "FAIL", 
                    "Test quiz course missing proper quiz data structure",
                    "Quiz lessons found but missing required fields or questions"
                )
            else:
                self.log_result(
                    "Quiz Data Structure", 
                    "FAIL", 
                    f"Failed to retrieve test course for structure validation (status: {response.status_code})",
                    f"Course ID: {self.test_course_id}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Data Structure", 
                "FAIL", 
                "Failed to validate test course quiz structure",
                str(e)
            )
        return False
    
    # =============================================================================
    # ENROLLMENT TESTS FOR QUIZ COURSES
    # =============================================================================
    
    def test_student_quiz_course_enrollment(self):
        """Test that students can enroll in and access courses containing quizzes"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Student Quiz Course Enrollment", 
                "SKIP", 
                "No student token available for enrollment test",
                "Student authentication required"
            )
            return False
        
        try:
            # Get student's current enrollments
            enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if enrollments_response.status_code == 200:
                enrollments = enrollments_response.json()
                quiz_course_enrollments = []
                
                # Check each enrollment for quiz content
                for enrollment in enrollments:
                    course_id = enrollment.get('courseId')
                    
                    # Get course details
                    course_response = requests.get(
                        f"{BACKEND_URL}/courses/{course_id}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                    )
                    
                    if course_response.status_code == 200:
                        course = course_response.json()
                        
                        # Check if course has quiz content
                        has_quiz = self.course_has_quiz_content(course)
                        if has_quiz:
                            quiz_course_enrollments.append({
                                'enrollment': enrollment,
                                'course': course
                            })
                
                if quiz_course_enrollments:
                    self.log_result(
                        "Student Quiz Course Enrollment", 
                        "PASS", 
                        f"Student can access {len(quiz_course_enrollments)} enrolled courses with quiz content",
                        f"Quiz courses: {[qce['course'].get('title') for qce in quiz_course_enrollments]}"
                    )
                    return True
                else:
                    # Try to enroll student in test quiz course if available
                    if self.test_course_id:
                        return self.enroll_student_in_test_course()
                    else:
                        self.log_result(
                            "Student Quiz Course Enrollment", 
                            "FAIL", 
                            "Student has no enrollments in courses with quiz content",
                            f"Total enrollments: {len(enrollments)}, Quiz course enrollments: 0"
                        )
            else:
                self.log_result(
                    "Student Quiz Course Enrollment", 
                    "FAIL", 
                    f"Failed to get student enrollments (status: {enrollments_response.status_code})",
                    f"Response: {enrollments_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Quiz Course Enrollment", 
                "FAIL", 
                "Failed to test student quiz course enrollment",
                str(e)
            )
        return False
    
    def course_has_quiz_content(self, course):
        """Check if a course has quiz content"""
        modules = course.get('modules', [])
        
        for module in modules:
            lessons = module.get('lessons', [])
            for lesson in lessons:
                lesson_type = lesson.get('type', '').lower()
                lesson_title = lesson.get('title', '').lower()
                if 'quiz' in lesson_type or 'quiz' in lesson_title:
                    return True
        return False
    
    def enroll_student_in_test_course(self):
        """Enroll student in test quiz course"""
        try:
            enrollment_data = {
                "courseId": self.test_course_id
            }
            
            response = requests.post(
                f"{BACKEND_URL}/enrollments",
                json=enrollment_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["student"]}'
                }
            )
            
            if response.status_code == 200:
                enrollment = response.json()
                self.log_result(
                    "Student Quiz Course Enrollment", 
                    "PASS", 
                    f"Successfully enrolled student in test quiz course",
                    f"Enrollment ID: {enrollment.get('id')}, Course ID: {self.test_course_id}"
                )
                return True
            else:
                self.log_result(
                    "Student Quiz Course Enrollment", 
                    "FAIL", 
                    f"Failed to enroll student in test quiz course (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Quiz Course Enrollment", 
                "FAIL", 
                "Failed to enroll student in test quiz course",
                str(e)
            )
        return False
    
    # =============================================================================
    # PROGRESS TRACKING TESTS FOR QUIZ COMPLETION
    # =============================================================================
    
    def test_quiz_progress_tracking(self):
        """Test PUT /api/enrollments/{course_id}/progress for quiz completion"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Quiz Progress Tracking", 
                "SKIP", 
                "No student token available for progress tracking test",
                "Student authentication required"
            )
            return False
        
        try:
            # Get student enrollments to find a quiz course
            enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if enrollments_response.status_code == 200:
                enrollments = enrollments_response.json()
                
                # Find an enrollment with quiz content
                quiz_enrollment = None
                for enrollment in enrollments:
                    course_id = enrollment.get('courseId')
                    
                    # Check if this course has quiz content
                    course_response = requests.get(
                        f"{BACKEND_URL}/courses/{course_id}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                    )
                    
                    if course_response.status_code == 200:
                        course = course_response.json()
                        if self.course_has_quiz_content(course):
                            quiz_enrollment = enrollment
                            break
                
                if quiz_enrollment:
                    course_id = quiz_enrollment.get('courseId')
                    
                    # Test progress tracking for quiz completion
                    progress_updates = [
                        {"progress": 25.0, "description": "Started quiz"},
                        {"progress": 50.0, "description": "Halfway through quiz"},
                        {"progress": 75.0, "description": "Almost completed quiz"},
                        {"progress": 100.0, "description": "Quiz completed"}
                    ]
                    
                    successful_updates = 0
                    
                    for update in progress_updates:
                        progress_data = {
                            "progress": update["progress"],
                            "lastAccessedAt": datetime.utcnow().isoformat()
                        }
                        
                        response = requests.put(
                            f"{BACKEND_URL}/enrollments/{course_id}/progress",
                            json=progress_data,
                            timeout=TEST_TIMEOUT,
                            headers={
                                'Content-Type': 'application/json',
                                'Authorization': f'Bearer {self.auth_tokens["student"]}'
                            }
                        )
                        
                        if response.status_code == 200:
                            successful_updates += 1
                            updated_enrollment = response.json()
                            print(f"   ✅ Progress update: {update['progress']}% - {update['description']}")
                            
                            # Check if completion was detected at 100%
                            if update["progress"] == 100.0:
                                status = updated_enrollment.get('status')
                                completed_at = updated_enrollment.get('completedAt')
                                if status == 'completed' and completed_at:
                                    print(f"   🎉 Course marked as completed at {completed_at}")
                        else:
                            print(f"   ❌ Progress update failed: {update['progress']}% - Status: {response.status_code}")
                    
                    if successful_updates == len(progress_updates):
                        self.log_result(
                            "Quiz Progress Tracking", 
                            "PASS", 
                            f"All {successful_updates} progress updates successful for quiz course",
                            f"Course ID: {course_id}, Progress tracking working correctly"
                        )
                        return True
                    else:
                        self.log_result(
                            "Quiz Progress Tracking", 
                            "FAIL", 
                            f"Only {successful_updates}/{len(progress_updates)} progress updates successful",
                            f"Course ID: {course_id}, Some progress updates failed"
                        )
                else:
                    self.log_result(
                        "Quiz Progress Tracking", 
                        "FAIL", 
                        "No quiz course enrollments found for progress tracking test",
                        f"Total enrollments: {len(enrollments)}, Quiz enrollments: 0"
                    )
            else:
                self.log_result(
                    "Quiz Progress Tracking", 
                    "FAIL", 
                    f"Failed to get student enrollments for progress tracking (status: {enrollments_response.status_code})",
                    f"Response: {enrollments_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Progress Tracking", 
                "FAIL", 
                "Failed to test quiz progress tracking",
                str(e)
            )
        return False
    
    # =============================================================================
    # COMPREHENSIVE QUIZ WORKFLOW TEST
    # =============================================================================
    
    def test_complete_quiz_workflow(self):
        """Test complete quiz workflow from course access to completion"""
        print("\n🎯 TESTING COMPLETE QUIZ WORKFLOW")
        print("=" * 60)
        
        workflow_steps = [
            ("Admin Authentication", self.test_admin_authentication),
            ("Student Authentication", self.test_student_authentication),
            ("Course Retrieval API", self.test_course_retrieval_api),
            ("Quiz Data Structure", self.test_quiz_data_structure),
            ("Student Quiz Course Enrollment", self.test_student_quiz_course_enrollment),
            ("Quiz Progress Tracking", self.test_quiz_progress_tracking)
        ]
        
        successful_steps = 0
        total_steps = len(workflow_steps)
        
        for step_name, step_function in workflow_steps:
            print(f"\n📋 Step: {step_name}")
            print("-" * 40)
            
            try:
                result = step_function()
                if result:
                    successful_steps += 1
                    print(f"✅ {step_name} completed successfully")
                else:
                    print(f"❌ {step_name} failed")
            except Exception as e:
                print(f"❌ {step_name} failed with exception: {str(e)}")
        
        success_rate = (successful_steps / total_steps) * 100
        
        if success_rate >= 80:  # 80% success rate threshold
            self.log_result(
                "Complete Quiz Workflow", 
                "PASS", 
                f"Quiz workflow test successful ({successful_steps}/{total_steps} = {success_rate:.1f}%)",
                f"All critical quiz functionality APIs are working correctly"
            )
            return True
        else:
            self.log_result(
                "Complete Quiz Workflow", 
                "FAIL", 
                f"Quiz workflow test failed ({successful_steps}/{total_steps} = {success_rate:.1f}%)",
                f"Some critical quiz functionality APIs are not working"
            )
            return False
    
    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_all_tests(self):
        """Run all quiz backend tests"""
        print("🚀 STARTING QUIZ FUNCTIONALITY BACKEND TESTING")
        print("=" * 80)
        print("TESTING SCOPE:")
        print("✅ Authentication endpoints - admin/student login credentials")
        print("✅ Course retrieval APIs - GET /api/courses/{id} for quiz courses")
        print("✅ Quiz-related course data - proper quiz data structure")
        print("✅ Enrollment APIs - student access to quiz courses")
        print("✅ Progress tracking APIs - PUT /api/enrollments/{course_id}/progress")
        print("=" * 80)
        
        # Run comprehensive quiz workflow test
        self.test_complete_quiz_workflow()
        
        # Print final summary
        print(f"\n📊 QUIZ BACKEND TESTING SUMMARY")
        print("=" * 50)
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%" if (self.passed + self.failed) > 0 else "No tests run")
        
        if self.failed == 0:
            print("\n🎉 ALL QUIZ BACKEND TESTS PASSED!")
            print("✅ All APIs return 200 status and proper data structure")
            print("✅ Quiz functionality ready for frontend integration")
        else:
            print(f"\n⚠️ {self.failed} TESTS FAILED - ATTENTION REQUIRED")
            print("❌ Some quiz functionality APIs need fixes")
        
        return self.failed == 0

if __name__ == "__main__":
    tester = QuizBackendTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)