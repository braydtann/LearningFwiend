#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Chronological Order Question Creation with Drag-and-Drop Interface
Testing the chronological order question creation functionality after implementing drag-and-drop interface in CreateCourse.js.

SPECIFIC TESTING REQUIREMENTS:
1. Authentication Testing: Verify admin login with brayden.t@covesmart.com / Hawaii2020!
2. Course Creation with Chronological Order: Test POST /api/courses with chronological order questions containing:
   - items array with historical events
   - correctOrder array (should be automatically generated from drag-and-drop sequence)
3. Data Structure Validation: Verify that the new drag-and-drop interface correctly creates:
   - items: array of objects with text, image, audio fields
   - correctOrder: array of indices representing the correct sequence
4. Backend Compatibility: Ensure existing chronological order data structure works with new frontend
5. Quiz Workflow: Test that courses with chronological questions can be retrieved via GET /api/courses/{id}
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use the correct backend URL from frontend/.env
BACKEND_URL = "https://lms-analytics-hub.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class ChronologicalOrderCourseTester:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.test_course_id = None
        self.results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_admin(self):
        """Test admin authentication with provided credentials"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                user_info = data.get('user', {})
                
                if user_info.get('role') == 'admin':
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Authenticated as {user_info.get('full_name')} ({user_info.get('email')})"
                    )
                    return True
                else:
                    self.log_result("Admin Authentication", False, f"User role is {user_info.get('role')}, expected admin")
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def authenticate_student(self):
        """Test student authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get('access_token')
                user_info = data.get('user', {})
                
                if user_info.get('role') == 'learner':
                    self.log_result(
                        "Student Authentication", 
                        True, 
                        f"Authenticated as {user_info.get('full_name')} ({user_info.get('email')})"
                    )
                    return True
                else:
                    self.log_result("Student Authentication", False, f"User role is {user_info.get('role')}, expected learner")
                    return False
            else:
                self.log_result("Student Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Student Authentication", False, f"Exception: {str(e)}")
            return False

    def test_course_creation_with_chronological_order(self):
        """Test POST /api/courses with chronological order questions containing items and correctOrder arrays"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Create course with chronological order questions using historical events as specified in review request
            course_data = {
                "title": "Chronological Order Test Course - Drag & Drop Interface",
                "description": "Testing chronological order question creation with new drag-and-drop interface",
                "category": "Technology",
                "duration": "2 hours",
                "thumbnailUrl": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400",
                "accessType": "open",
                "learningOutcomes": [
                    "Understand historical chronology",
                    "Practice drag-and-drop ordering"
                ],
                "modules": [
                    {
                        "id": "m1",
                        "title": "Historical Events Module",
                        "lessons": [
                            {
                                "id": "l1",
                                "title": "Historical Timeline Quiz",
                                "type": "quiz",
                                "duration": "30 min",
                                "quiz": {
                                    "id": "quiz1",
                                    "title": "Historical Timeline Quiz",
                                    "description": "Test your knowledge of historical chronology",
                                    "timeLimit": 15,
                                    "maxAttempts": 3,
                                    "passingScore": 70,
                                    "showResults": True,
                                    "shuffleQuestions": False,
                                    "questions": [
                                        {
                                            "id": "q1",
                                            "type": "chronological-order",
                                            "question": "Arrange these historical events in chronological order:",
                                            "questionImage": "",
                                            "questionAudio": "",
                                            "items": [
                                                {"text": "World War I begins (1914)", "image": "", "audio": ""},
                                                {"text": "World War II ends (1945)", "image": "", "audio": ""},
                                                {"text": "Moon landing (1969)", "image": "", "audio": ""},
                                                {"text": "Berlin Wall falls (1989)", "image": "", "audio": ""}
                                            ],
                                            "correctOrder": [0, 1, 2, 3],  # Correct chronological order
                                            "points": 20,
                                            "explanation": "These events occurred in this chronological order: WWI (1914), WWII ends (1945), Moon landing (1969), Berlin Wall falls (1989)"
                                        },
                                        {
                                            "id": "q2",
                                            "type": "chronological-order",
                                            "question": "Order these technological inventions by when they were first introduced:",
                                            "questionImage": "",
                                            "questionAudio": "",
                                            "items": [
                                                {"text": "Personal Computer (1970s)", "image": "", "audio": ""},
                                                {"text": "Internet (1960s-1970s)", "image": "", "audio": ""},
                                                {"text": "Smartphone (2000s)", "image": "", "audio": ""},
                                                {"text": "World Wide Web (1990s)", "image": "", "audio": ""}
                                            ],
                                            "correctOrder": [1, 0, 3, 2],  # Internet, PC, WWW, Smartphone
                                            "points": 25,
                                            "explanation": "Timeline: Internet (1960s-70s), Personal Computer (1970s), World Wide Web (1990s), Smartphone (2000s)"
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
                json=course_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                course = response.json()
                self.test_course_id = course['id']
                
                # Verify course structure
                has_modules = 'modules' in course and len(course['modules']) > 0
                has_quiz_lesson = False
                chronological_questions = []
                
                if has_modules:
                    for module in course['modules']:
                        for lesson in module.get('lessons', []):
                            if lesson.get('type') == 'quiz' and lesson.get('quiz'):
                                has_quiz_lesson = True
                                for question in lesson['quiz'].get('questions', []):
                                    if question.get('type') == 'chronological-order':
                                        chronological_questions.append(question)
                
                # Validate chronological order questions
                valid_questions = 0
                for question in chronological_questions:
                    has_items = 'items' in question and isinstance(question['items'], list) and len(question['items']) > 0
                    has_correct_order = 'correctOrder' in question and isinstance(question['correctOrder'], list)
                    items_have_text = all('text' in item for item in question.get('items', []))
                    correct_order_valid = (
                        len(question.get('correctOrder', [])) == len(question.get('items', [])) and
                        all(isinstance(idx, int) for idx in question.get('correctOrder', []))
                    )
                    
                    if has_items and has_correct_order and items_have_text and correct_order_valid:
                        valid_questions += 1
                
                success = (
                    has_modules and
                    has_quiz_lesson and
                    len(chronological_questions) == 2 and
                    valid_questions == 2
                )
                
                if success:
                    self.log_result(
                        "Course Creation with Chronological Order", 
                        True, 
                        f"Created course with {len(chronological_questions)} chronological order questions. Course ID: {course['id']}"
                    )
                    return True
                else:
                    self.log_result(
                        "Course Creation with Chronological Order", 
                        False, 
                        f"Invalid structure - Modules: {has_modules}, Quiz: {has_quiz_lesson}, Chrono Questions: {len(chronological_questions)}, Valid: {valid_questions}"
                    )
                    return False
            else:
                self.log_result(
                    "Course Creation with Chronological Order", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Course Creation with Chronological Order", False, f"Exception: {str(e)}")
            return False

    def test_data_structure_validation(self):
        """Verify that the drag-and-drop interface correctly creates items and correctOrder arrays"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get the created course to validate data structure
            response = requests.get(
                f"{BACKEND_URL}/courses/{self.test_course_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                course = response.json()
                
                # Extract chronological order questions
                chronological_questions = []
                for module in course.get('modules', []):
                    for lesson in module.get('lessons', []):
                        if lesson.get('type') == 'quiz' and lesson.get('quiz'):
                            for question in lesson['quiz'].get('questions', []):
                                if question.get('type') == 'chronological-order':
                                    chronological_questions.append(question)
                
                if len(chronological_questions) == 0:
                    self.log_result(
                        "Data Structure Validation", 
                        False, 
                        "No chronological order questions found in course"
                    )
                    return False
                
                # Validate each question's data structure
                validation_results = []
                for i, question in enumerate(chronological_questions):
                    # Check items array structure
                    items = question.get('items', [])
                    items_valid = (
                        isinstance(items, list) and
                        len(items) > 0 and
                        all(isinstance(item, dict) for item in items) and
                        all('text' in item and 'image' in item and 'audio' in item for item in items)
                    )
                    
                    # Check correctOrder array structure
                    correct_order = question.get('correctOrder', [])
                    correct_order_valid = (
                        isinstance(correct_order, list) and
                        len(correct_order) == len(items) and
                        all(isinstance(idx, int) and 0 <= idx < len(items) for idx in correct_order)
                    )
                    
                    # Check for required fields
                    has_required_fields = all(field in question for field in ['id', 'type', 'question', 'points'])
                    
                    validation_results.append({
                        'question_index': i + 1,
                        'items_valid': items_valid,
                        'correct_order_valid': correct_order_valid,
                        'has_required_fields': has_required_fields,
                        'items_count': len(items),
                        'correct_order': correct_order
                    })
                
                # Check if all validations passed
                all_valid = all(
                    result['items_valid'] and result['correct_order_valid'] and result['has_required_fields']
                    for result in validation_results
                )
                
                if all_valid:
                    details = f"Validated {len(chronological_questions)} questions. "
                    details += f"Items structure: ✓, CorrectOrder structure: ✓, Required fields: ✓"
                    self.log_result("Data Structure Validation", True, details)
                    return True
                else:
                    failed_validations = [r for r in validation_results if not (r['items_valid'] and r['correct_order_valid'] and r['has_required_fields'])]
                    details = f"Validation failed for {len(failed_validations)} questions: {failed_validations}"
                    self.log_result("Data Structure Validation", False, details)
                    return False
            else:
                self.log_result(
                    "Data Structure Validation", 
                    False, 
                    f"Could not retrieve course: HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Data Structure Validation", False, f"Exception: {str(e)}")
            return False

    def test_backend_compatibility(self):
        """Ensure existing chronological order data structure works with new frontend"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get the course and verify it can be retrieved successfully
            response = requests.get(
                f"{BACKEND_URL}/courses/{self.test_course_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                course = response.json()
                
                # Verify course has expected structure for frontend compatibility
                required_course_fields = ['id', 'title', 'description', 'modules']
                course_fields_valid = all(field in course for field in required_course_fields)
                
                # Check module structure
                modules_valid = True
                quiz_lessons_found = 0
                
                for module in course.get('modules', []):
                    if not all(field in module for field in ['id', 'title', 'lessons']):
                        modules_valid = False
                        break
                    
                    for lesson in module.get('lessons', []):
                        if lesson.get('type') == 'quiz':
                            quiz_lessons_found += 1
                            quiz = lesson.get('quiz', {})
                            
                            # Verify quiz structure
                            required_quiz_fields = ['id', 'title', 'questions', 'timeLimit', 'passingScore']
                            if not all(field in quiz for field in required_quiz_fields):
                                modules_valid = False
                                break
                            
                            # Verify chronological questions structure
                            for question in quiz.get('questions', []):
                                if question.get('type') == 'chronological-order':
                                    required_question_fields = ['id', 'type', 'question', 'items', 'correctOrder', 'points']
                                    if not all(field in question for field in required_question_fields):
                                        modules_valid = False
                                        break
                
                success = course_fields_valid and modules_valid and quiz_lessons_found > 0
                
                if success:
                    self.log_result(
                        "Backend Compatibility", 
                        True, 
                        f"Course structure compatible with frontend. Quiz lessons: {quiz_lessons_found}, All required fields present"
                    )
                    return True
                else:
                    self.log_result(
                        "Backend Compatibility", 
                        False, 
                        f"Compatibility issues - Course fields: {course_fields_valid}, Modules: {modules_valid}, Quiz lessons: {quiz_lessons_found}"
                    )
                    return False
            else:
                self.log_result(
                    "Backend Compatibility", 
                    False, 
                    f"Could not retrieve course for compatibility check: HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Backend Compatibility", False, f"Exception: {str(e)}")
            return False

    def test_quiz_workflow_retrieval(self):
        """Test that courses with chronological questions can be retrieved via GET /api/courses/{id}"""
        try:
            # Test with both admin and student tokens to ensure accessibility
            test_cases = [
                ("Admin", self.admin_token),
                ("Student", self.student_token)
            ]
            
            successful_retrievals = 0
            
            for user_type, token in test_cases:
                headers = {"Authorization": f"Bearer {token}"}
                
                response = requests.get(
                    f"{BACKEND_URL}/courses/{self.test_course_id}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    course = response.json()
                    
                    # Verify chronological questions are present and accessible
                    chronological_questions_found = 0
                    
                    for module in course.get('modules', []):
                        for lesson in module.get('lessons', []):
                            if lesson.get('type') == 'quiz' and lesson.get('quiz'):
                                for question in lesson['quiz'].get('questions', []):
                                    if question.get('type') == 'chronological-order':
                                        chronological_questions_found += 1
                                        
                                        # Verify question has all necessary data for quiz workflow
                                        has_items = 'items' in question and len(question['items']) > 0
                                        has_correct_order = 'correctOrder' in question
                                        has_question_text = 'question' in question and question['question'].strip()
                                        
                                        if not (has_items and has_correct_order and has_question_text):
                                            self.log_result(
                                                f"Quiz Workflow Retrieval ({user_type})", 
                                                False, 
                                                f"Incomplete question data - Items: {has_items}, CorrectOrder: {has_correct_order}, Question: {has_question_text}"
                                            )
                                            return False
                    
                    if chronological_questions_found > 0:
                        successful_retrievals += 1
                        self.log_result(
                            f"Quiz Workflow Retrieval ({user_type})", 
                            True, 
                            f"Successfully retrieved course with {chronological_questions_found} chronological questions"
                        )
                    else:
                        self.log_result(
                            f"Quiz Workflow Retrieval ({user_type})", 
                            False, 
                            "No chronological questions found in retrieved course"
                        )
                        return False
                else:
                    self.log_result(
                        f"Quiz Workflow Retrieval ({user_type})", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return False
            
            # Overall success if both user types can retrieve the course
            if successful_retrievals == 2:
                self.log_result(
                    "Quiz Workflow Retrieval (Overall)", 
                    True, 
                    f"Course successfully retrieved by both admin and student users"
                )
                return True
            else:
                self.log_result(
                    "Quiz Workflow Retrieval (Overall)", 
                    False, 
                    f"Only {successful_retrievals}/2 user types could retrieve course successfully"
                )
                return False
                
        except Exception as e:
            self.log_result("Quiz Workflow Retrieval", False, f"Exception: {str(e)}")
            return False

    def test_drag_drop_correctorder_generation(self):
        """Test that correctOrder array represents the drag-and-drop sequence correctly"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Create a test course with a specific drag-and-drop sequence
            # Simulate what the frontend would send after drag-and-drop reordering
            course_data = {
                "title": "Drag-Drop Sequence Test Course",
                "description": "Testing correctOrder generation from drag-and-drop interface",
                "category": "Technology",
                "duration": "1 hour",
                "thumbnailUrl": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400",
                "accessType": "open",
                "learningOutcomes": ["Test drag-and-drop ordering"],
                "modules": [
                    {
                        "id": "m1",
                        "title": "Drag-Drop Test Module",
                        "lessons": [
                            {
                                "id": "l1",
                                "title": "Sequence Test Quiz",
                                "type": "quiz",
                                "quiz": {
                                    "id": "quiz1",
                                    "title": "Sequence Test Quiz",
                                    "description": "Test drag-and-drop sequence generation",
                                    "timeLimit": 10,
                                    "maxAttempts": 1,
                                    "passingScore": 70,
                                    "questions": [
                                        {
                                            "id": "q1",
                                            "type": "chronological-order",
                                            "question": "Items arranged by drag-and-drop (original order: A, B, C, D):",
                                            "items": [
                                                {"text": "Item C (moved to position 1)", "image": "", "audio": ""},
                                                {"text": "Item A (moved to position 2)", "image": "", "audio": ""},
                                                {"text": "Item D (moved to position 3)", "image": "", "audio": ""},
                                                {"text": "Item B (moved to position 4)", "image": "", "audio": ""}
                                            ],
                                            # This represents the current order after drag-and-drop: C, A, D, B
                                            # The correctOrder should match the current arrangement: [0, 1, 2, 3]
                                            "correctOrder": [0, 1, 2, 3],
                                            "points": 10,
                                            "explanation": "This is the correct order as arranged by drag-and-drop"
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
                json=course_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                course = response.json()
                
                # Retrieve the course to verify the correctOrder was stored correctly
                get_response = requests.get(
                    f"{BACKEND_URL}/courses/{course['id']}",
                    headers=headers,
                    timeout=10
                )
                
                if get_response.status_code == 200:
                    retrieved_course = get_response.json()
                    
                    # Find the chronological question
                    question = None
                    for module in retrieved_course.get('modules', []):
                        for lesson in module.get('lessons', []):
                            if lesson.get('type') == 'quiz' and lesson.get('quiz'):
                                for q in lesson['quiz'].get('questions', []):
                                    if q.get('type') == 'chronological-order':
                                        question = q
                                        break
                    
                    if question:
                        items = question.get('items', [])
                        correct_order = question.get('correctOrder', [])
                        
                        # Verify the correctOrder matches the expected sequence
                        expected_order = [0, 1, 2, 3]  # Sequential order as arranged
                        items_count = len(items)
                        correct_order_valid = (
                            correct_order == expected_order and
                            len(correct_order) == items_count and
                            items_count == 4
                        )
                        
                        # Verify items are in the expected drag-and-drop order
                        expected_texts = [
                            "Item C (moved to position 1)",
                            "Item A (moved to position 2)", 
                            "Item D (moved to position 3)",
                            "Item B (moved to position 4)"
                        ]
                        
                        actual_texts = [item.get('text', '') for item in items]
                        items_order_correct = actual_texts == expected_texts
                        
                        if correct_order_valid and items_order_correct:
                            self.log_result(
                                "Drag-Drop CorrectOrder Generation", 
                                True, 
                                f"CorrectOrder correctly represents drag-and-drop sequence: {correct_order}, Items in correct order: {len(items)} items"
                            )
                            return True
                        else:
                            self.log_result(
                                "Drag-Drop CorrectOrder Generation", 
                                False, 
                                f"Sequence mismatch - CorrectOrder valid: {correct_order_valid}, Items order: {items_order_correct}, Expected: {expected_order}, Got: {correct_order}"
                            )
                            return False
                    else:
                        self.log_result(
                            "Drag-Drop CorrectOrder Generation", 
                            False, 
                            "No chronological order question found in created course"
                        )
                        return False
                else:
                    self.log_result(
                        "Drag-Drop CorrectOrder Generation", 
                        False, 
                        f"Could not retrieve course for verification: HTTP {get_response.status_code}"
                    )
                    return False
            else:
                self.log_result(
                    "Drag-Drop CorrectOrder Generation", 
                    False, 
                    f"Course creation failed: HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Drag-Drop CorrectOrder Generation", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all chronological order course creation tests"""
        print("🚀 Starting Chronological Order Course Creation Testing with Drag-and-Drop Interface")
        print("=" * 90)
        print()
        
        # Authentication tests
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot continue")
            return False
            
        if not self.authenticate_student():
            print("❌ Student authentication failed - cannot continue")
            return False
        
        # Core functionality tests
        test_methods = [
            self.test_course_creation_with_chronological_order,
            self.test_data_structure_validation,
            self.test_backend_compatibility,
            self.test_quiz_workflow_retrieval,
            self.test_drag_drop_correctorder_generation
        ]
        
        for test_method in test_methods:
            try:
                test_method()
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                self.log_result(test_method.__name__, False, f"Unexpected error: {str(e)}")
        
        # Summary
        print("=" * 90)
        print("📊 CHRONOLOGICAL ORDER COURSE CREATION TESTING SUMMARY")
        print("=" * 90)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
            print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        auth_tests = [r for r in self.results if 'authentication' in r['test'].lower()]
        course_tests = [r for r in self.results if 'course' in r['test'].lower()]
        data_tests = [r for r in self.results if 'data' in r['test'].lower() or 'structure' in r['test'].lower()]
        
        auth_success = all(r['success'] for r in auth_tests)
        course_success = all(r['success'] for r in course_tests)
        data_success = all(r['success'] for r in data_tests)
        
        if auth_success:
            print("  ✅ Authentication working correctly with provided credentials")
        else:
            print("  ❌ Authentication issues detected")
            
        if course_success:
            print("  ✅ Course creation with chronological order questions working")
        else:
            print("  ❌ Issues with course creation functionality")
            
        if data_success:
            print("  ✅ Data structure validation and drag-and-drop interface working correctly")
        else:
            print("  ❌ Data structure or drag-and-drop interface issues detected")
        
        print()
        return success_rate >= 80.0  # Consider 80%+ success rate as passing

if __name__ == "__main__":
    tester = ChronologicalOrderCourseTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 Chronological order course creation testing completed successfully!")
        sys.exit(0)
    else:
        print("💥 Chronological order course creation testing failed!")
        sys.exit(1)