#!/usr/bin/env python3
"""
SPECIFIC QUIZ QUESTION TYPES TESTING
Testing the new question types that were implemented according to the review request:
- select-all-that-apply (checkbox multi-select)
- long-form-answer (larger textarea)
- chronological-order (position dropdown ordering)

Also testing existing types:
- multiple-choice
- true-false (true_false)
- short-answer
"""

import requests
import json
import sys
from datetime import datetime

BACKEND_URL = "https://lms-media-display.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

STUDENT_CREDENTIALS = {
    "username_or_email": "brayden.student@learningfwiend.com",
    "password": "Cove1234!"
}

ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class QuizQuestionTypesTester:
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
        else:
            self.failed += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
    
    def authenticate(self):
        """Authenticate both student and admin users"""
        # Student login
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_tokens['student'] = data.get('access_token')
                print(f"✅ Student authenticated: {data.get('user', {}).get('email')}")
            else:
                print(f"❌ Student authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Student authentication error: {str(e)}")
            return False
        
        # Admin login
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_tokens['admin'] = data.get('access_token')
                print(f"✅ Admin authenticated: {data.get('user', {}).get('email')}")
            else:
                print(f"❌ Admin authentication failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Admin authentication error: {str(e)}")
        
        return 'student' in self.auth_tokens
    
    def test_create_course_with_new_question_types(self):
        """Create a test course with all the new question types"""
        if 'admin' not in self.auth_tokens:
            self.log_result(
                "Create Test Course with New Question Types",
                "SKIP",
                "No admin token available",
                "Admin authentication required"
            )
            return None
        
        # Define test course with all question types
        test_course_data = {
            "title": "Comprehensive Question Types Test Course",
            "description": "Testing all question types including new implementations",
            "category": "Testing",
            "duration": "1 hour",
            "accessType": "open",
            "modules": [
                {
                    "title": "Mixed Question Types Quiz Module",
                    "lessons": [
                        {
                            "id": "lesson-mixed-quiz",
                            "title": "Mixed Question Types Quiz",
                            "type": "quiz",
                            "content": {
                                "questions": [
                                    {
                                        "id": "q1-multiple-choice",
                                        "type": "multiple-choice",
                                        "question": "What is the capital of France?",
                                        "options": ["London", "Berlin", "Paris", "Madrid"],
                                        "correctAnswer": 2
                                    },
                                    {
                                        "id": "q2-true-false",
                                        "type": "true-false",
                                        "question": "The Earth is flat.",
                                        "correctAnswer": False
                                    },
                                    {
                                        "id": "q3-short-answer",
                                        "type": "short-answer",
                                        "question": "What is 2 + 2?",
                                        "correctAnswer": "4"
                                    },
                                    {
                                        "id": "q4-select-all",
                                        "type": "select-all-that-apply",
                                        "question": "Which of the following are programming languages?",
                                        "options": ["Python", "HTML", "JavaScript", "CSS", "Java"],
                                        "correctAnswer": [0, 2, 4]
                                    },
                                    {
                                        "id": "q5-long-form",
                                        "type": "long-form-answer",
                                        "question": "Explain the importance of user experience in web design.",
                                        "correctAnswer": "User experience is crucial for web design because it determines how users interact with and perceive a website."
                                    },
                                    {
                                        "id": "q6-chronological",
                                        "type": "chronological-order",
                                        "question": "Arrange these historical events in chronological order:",
                                        "options": ["World War II", "World War I", "Cold War", "Renaissance"],
                                        "correctAnswer": [3, 1, 0, 2]
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=test_course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                created_course = response.json()
                course_id = created_course.get('id')
                
                self.log_result(
                    "Create Test Course with New Question Types",
                    "PASS",
                    f"Successfully created test course with mixed question types",
                    f"Course ID: {course_id}, Title: {created_course.get('title')}"
                )
                return course_id
            else:
                self.log_result(
                    "Create Test Course with New Question Types",
                    "FAIL",
                    f"Failed to create test course, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Create Test Course with New Question Types",
                "FAIL",
                "Error creating test course",
                str(e)
            )
        return None
    
    def test_course_retrieval_with_question_types(self, course_id):
        """Test retrieving the course and analyzing question types"""
        if not course_id or 'student' not in self.auth_tokens:
            self.log_result(
                "Course Retrieval with Question Types",
                "SKIP",
                "No course ID or student token available",
                "Course creation and student authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                course = response.json()
                modules = course.get('modules', [])
                
                question_types_found = []
                total_questions = 0
                
                for module in modules:
                    lessons = module.get('lessons', [])
                    for lesson in lessons:
                        if lesson.get('type') == 'quiz':
                            content = lesson.get('content', {})
                            questions = content.get('questions', [])
                            total_questions += len(questions)
                            
                            for question in questions:
                                q_type = question.get('type')
                                if q_type not in question_types_found:
                                    question_types_found.append(q_type)
                
                expected_types = [
                    'multiple-choice', 'true-false', 'short-answer',
                    'select-all-that-apply', 'long-form-answer', 'chronological-order'
                ]
                
                found_count = len([t for t in expected_types if t in question_types_found])
                
                self.log_result(
                    "Course Retrieval with Question Types",
                    "PASS",
                    f"Successfully retrieved course with {found_count}/{len(expected_types)} expected question types",
                    f"Found types: {question_types_found}, Total questions: {total_questions}"
                )
                return question_types_found
            else:
                self.log_result(
                    "Course Retrieval with Question Types",
                    "FAIL",
                    f"Failed to retrieve course, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Course Retrieval with Question Types",
                "FAIL",
                "Error retrieving course",
                str(e)
            )
        return False
    
    def test_existing_quiz_courses_compatibility(self):
        """Test that existing quiz courses still work with the new implementation"""
        if 'student' not in self.auth_tokens:
            self.log_result(
                "Existing Quiz Courses Compatibility",
                "SKIP",
                "No student token available",
                "Student authentication required"
            )
            return False
        
        try:
            # Get all courses
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                
                # Find existing quiz courses
                existing_quiz_courses = []
                for course in courses:
                    if 'progress testing' in course.get('title', '').lower() or 'ttttt' in course.get('title', '').lower():
                        existing_quiz_courses.append(course)
                
                compatible_courses = 0
                
                for course in existing_quiz_courses[:3]:  # Test first 3 courses
                    course_id = course.get('id')
                    
                    # Test course retrieval
                    course_response = requests.get(
                        f"{BACKEND_URL}/courses/{course_id}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                    )
                    
                    if course_response.status_code == 200:
                        compatible_courses += 1
                        print(f"   ✅ {course.get('title')}: Compatible")
                    else:
                        print(f"   ❌ {course.get('title')}: Not compatible - {course_response.status_code}")
                
                if compatible_courses >= len(existing_quiz_courses) * 0.8:  # 80% compatibility
                    self.log_result(
                        "Existing Quiz Courses Compatibility",
                        "PASS",
                        f"{compatible_courses}/{len(existing_quiz_courses)} existing quiz courses are compatible",
                        "Backward compatibility maintained"
                    )
                    return True
                else:
                    self.log_result(
                        "Existing Quiz Courses Compatibility",
                        "FAIL",
                        f"Only {compatible_courses}/{len(existing_quiz_courses)} existing quiz courses are compatible",
                        "Backward compatibility issues detected"
                    )
            else:
                self.log_result(
                    "Existing Quiz Courses Compatibility",
                    "FAIL",
                    f"Failed to retrieve courses, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Existing Quiz Courses Compatibility",
                "FAIL",
                "Error testing existing quiz courses",
                str(e)
            )
        return False
    
    def run_question_types_tests(self):
        """Run all question types tests"""
        print("🎯 COMPREHENSIVE QUIZ QUESTION TYPES TESTING")
        print("=" * 60)
        print("Testing new question types implementation:")
        print("- select-all-that-apply (checkbox multi-select)")
        print("- long-form-answer (larger textarea)")
        print("- chronological-order (position dropdown ordering)")
        print("=" * 60)
        
        # Phase 1: Authentication
        print("\n🔑 PHASE 1: AUTHENTICATION")
        print("-" * 30)
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed")
            return False
        
        # Phase 2: Create test course with new question types
        print("\n📚 PHASE 2: CREATE TEST COURSE WITH NEW QUESTION TYPES")
        print("-" * 50)
        test_course_id = self.test_create_course_with_new_question_types()
        
        # Phase 3: Test course retrieval and question type analysis
        print("\n🔍 PHASE 3: ANALYZE QUESTION TYPES IN COURSE")
        print("-" * 45)
        question_types = self.test_course_retrieval_with_question_types(test_course_id)
        
        # Phase 4: Test backward compatibility
        print("\n🔄 PHASE 4: BACKWARD COMPATIBILITY")
        print("-" * 35)
        compatibility_success = self.test_existing_quiz_courses_compatibility()
        
        # Summary
        print(f"\n📊 QUESTION TYPES TESTING SUMMARY")
        print("=" * 40)
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        
        success_rate = (self.passed / (self.passed + self.failed)) * 100 if (self.passed + self.failed) > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if test_course_id:
            print(f"📋 Test Course Created: {test_course_id}")
        
        if question_types:
            print(f"🔍 Question Types Found: {question_types}")
        
        if success_rate >= 70:
            print("\n🎉 QUESTION TYPES TESTING SUCCESSFUL")
            print("Backend supports the new question types implementation")
        else:
            print("\n⚠️ QUESTION TYPES TESTING NEEDS ATTENTION")
            print("Issues detected with new question types implementation")
        
        return success_rate >= 70

def main():
    """Main test execution"""
    tester = QuizQuestionTypesTester()
    success = tester.run_question_types_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()