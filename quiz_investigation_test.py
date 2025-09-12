#!/usr/bin/env python3
"""
URGENT: Different Course Quiz Investigation + Creation Bug
QUIZ INVESTIGATION BACKEND TESTING SUITE

INVESTIGATION SCOPE:
✅ Find and examine course "All quizzes as options" 
✅ Check quiz structure and question types in this specific course
✅ Verify if quiz data structure differs from expected format
✅ Test chronological order question creation process
✅ Check if there are data format mismatches causing React Error #31

LOGIN: brayden.student@learningfwiend.com / Cove1234!
TARGET COURSE: "All quizzes as options" 
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using Production Backend URL from frontend/.env
BACKEND_URL = "https://coursemate-14.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "brayden.student@learningfwiend.com", 
    "password": "Cove1234!"
}

class QuizInvestigationTester:
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
    
    def test_admin_login(self):
        """Test admin authentication"""
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
                        f"Role: {user_info.get('role')}, Name: {user_info.get('full_name')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication", 
                        "FAIL", 
                        "Login response missing token or incorrect role",
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
                "Failed to connect to authentication endpoint",
                str(e)
            )
        return False
    
    def test_student_login(self):
        """Test student authentication"""
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
                
                if token:
                    self.auth_tokens['student'] = token
                    self.log_result(
                        "Student Authentication", 
                        "PASS", 
                        f"Student login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Name: {user_info.get('full_name')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Student Authentication", 
                        "FAIL", 
                        "Login response missing token",
                        f"Response data: {data}"
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
    
    def find_all_quizzes_as_options_course(self):
        """Find the specific course 'All quizzes as options'"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Find 'All quizzes as options' Course", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return None
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                target_course = None
                
                # Look for exact match first
                for course in courses:
                    if course.get('title', '').lower() == 'all quizzes as options':
                        target_course = course
                        break
                
                # If not found, look for partial matches
                if not target_course:
                    for course in courses:
                        title = course.get('title', '').lower()
                        if 'all quizzes' in title or 'quiz' in title and 'option' in title:
                            target_course = course
                            break
                
                if target_course:
                    self.log_result(
                        "Find 'All quizzes as options' Course", 
                        "PASS", 
                        f"Found target course: {target_course.get('title')}",
                        f"Course ID: {target_course.get('id')}, Modules: {len(target_course.get('modules', []))}"
                    )
                    return target_course
                else:
                    # List all courses for debugging
                    all_course_titles = [c.get('title', 'Untitled') for c in courses]
                    quiz_courses = [c for c in courses if 'quiz' in c.get('title', '').lower()]
                    option_courses = [c for c in courses if 'option' in c.get('title', '').lower()]
                    
                    print(f"\n📋 ALL AVAILABLE COURSES ({len(courses)} total):")
                    for i, course in enumerate(courses[:20]):  # Show first 20 courses
                        print(f"   {i+1}. {course.get('title', 'Untitled')} (ID: {course.get('id', 'N/A')[:8]}...)")
                    
                    if len(courses) > 20:
                        print(f"   ... and {len(courses) - 20} more courses")
                    
                    # Look for courses that might be the target
                    potential_matches = []
                    for course in courses:
                        title = course.get('title', '').lower()
                        if any(word in title for word in ['quiz', 'option', 'all', 'question']):
                            potential_matches.append(course)
                    
                    self.log_result(
                        "Find 'All quizzes as options' Course", 
                        "FAIL", 
                        f"Course 'All quizzes as options' not found among {len(courses)} courses",
                        f"Quiz courses: {[c.get('title') for c in quiz_courses]}; Option courses: {[c.get('title') for c in option_courses]}; Potential matches: {[c.get('title') for c in potential_matches[:5]]}"
                    )
                    
                    # Return the first potential match for analysis
                    if potential_matches:
                        print(f"\n🎯 Using potential match for analysis: {potential_matches[0].get('title')}")
                        return potential_matches[0]
            else:
                self.log_result(
                    "Find 'All quizzes as options' Course", 
                    "FAIL", 
                    f"Failed to retrieve courses, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Find 'All quizzes as options' Course", 
                "FAIL", 
                "Failed to search for target course",
                str(e)
            )
        return None
    
    def analyze_course_quiz_structure(self, course):
        """Analyze the quiz structure of the target course"""
        if not course:
            return None
        
        try:
            course_id = course.get('id')
            
            # Get detailed course information
            response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                detailed_course = response.json()
                modules = detailed_course.get('modules', [])
                
                analysis = {
                    'course_id': course_id,
                    'title': detailed_course.get('title'),
                    'total_modules': len(modules),
                    'quiz_modules': 0,
                    'quiz_lessons': [],
                    'question_types': set(),
                    'data_structure_issues': [],
                    'potential_react_error_causes': []
                }
                
                for module_idx, module in enumerate(modules):
                    lessons = module.get('lessons', [])
                    module_has_quiz = False
                    
                    for lesson_idx, lesson in enumerate(lessons):
                        lesson_type = lesson.get('type', '').lower()
                        lesson_title = lesson.get('title', '').lower()
                        
                        if 'quiz' in lesson_type or 'quiz' in lesson_title:
                            module_has_quiz = True
                            lesson_analysis = {
                                'module_index': module_idx,
                                'lesson_index': lesson_idx,
                                'lesson_id': lesson.get('id'),
                                'lesson_title': lesson.get('title'),
                                'lesson_type': lesson.get('type'),
                                'content': lesson.get('content', {}),
                                'questions': []
                            }
                            
                            # Analyze quiz content
                            content = lesson.get('content', {})
                            questions = content.get('questions', [])
                            
                            for q_idx, question in enumerate(questions):
                                q_type = question.get('type', 'unknown')
                                analysis['question_types'].add(q_type)
                                
                                question_analysis = {
                                    'question_index': q_idx,
                                    'type': q_type,
                                    'question': question.get('question', ''),
                                    'has_options': 'options' in question,
                                    'has_items': 'items' in question,
                                    'has_correct_answer': 'correctAnswer' in question,
                                    'raw_data': question
                                }
                                
                                # Check for potential React Error #31 causes
                                if q_type == 'chronological-order':
                                    if 'items' not in question:
                                        analysis['data_structure_issues'].append(f"Chronological question {q_idx} missing 'items' field")
                                        analysis['potential_react_error_causes'].append("Missing 'items' field for chronological-order question")
                                    elif not isinstance(question.get('items'), list):
                                        analysis['data_structure_issues'].append(f"Chronological question {q_idx} 'items' is not a list")
                                        analysis['potential_react_error_causes'].append("'items' field is not an array for chronological-order question")
                                
                                if q_type == 'select-all-that-apply':
                                    if 'options' not in question:
                                        analysis['data_structure_issues'].append(f"Select-all question {q_idx} missing 'options' field")
                                        analysis['potential_react_error_causes'].append("Missing 'options' field for select-all-that-apply question")
                                    elif not isinstance(question.get('options'), list):
                                        analysis['data_structure_issues'].append(f"Select-all question {q_idx} 'options' is not a list")
                                        analysis['potential_react_error_causes'].append("'options' field is not an array for select-all-that-apply question")
                                
                                lesson_analysis['questions'].append(question_analysis)
                            
                            analysis['quiz_lessons'].append(lesson_analysis)
                    
                    if module_has_quiz:
                        analysis['quiz_modules'] += 1
                
                # Log the analysis
                issues_count = len(analysis['data_structure_issues'])
                react_error_causes = len(analysis['potential_react_error_causes'])
                
                if issues_count == 0 and react_error_causes == 0:
                    self.log_result(
                        "Course Quiz Structure Analysis", 
                        "PASS", 
                        f"Quiz structure analysis complete - no critical issues found",
                        f"Modules: {analysis['total_modules']}, Quiz modules: {analysis['quiz_modules']}, Question types: {list(analysis['question_types'])}"
                    )
                else:
                    self.log_result(
                        "Course Quiz Structure Analysis", 
                        "FAIL", 
                        f"Found {issues_count} data structure issues and {react_error_causes} potential React Error #31 causes",
                        f"Issues: {analysis['data_structure_issues'][:3]}; React Error causes: {analysis['potential_react_error_causes'][:3]}"
                    )
                
                return analysis
            else:
                self.log_result(
                    "Course Quiz Structure Analysis", 
                    "FAIL", 
                    f"Failed to get detailed course info, status: {response.status_code}",
                    f"Course ID: {course_id}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Quiz Structure Analysis", 
                "FAIL", 
                "Failed to analyze course quiz structure",
                str(e)
            )
        return None
    
    def test_student_course_access(self, course):
        """Test if student can access the target course"""
        if not course or "student" not in self.auth_tokens:
            self.log_result(
                "Student Course Access Test", 
                "SKIP", 
                "No course or student token available",
                "Course and student authentication required"
            )
            return False
        
        try:
            course_id = course.get('id')
            
            # Test student access to the specific course
            response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                course_data = response.json()
                self.log_result(
                    "Student Course Access Test", 
                    "PASS", 
                    f"Student can access course: {course_data.get('title')}",
                    f"Course ID: {course_id}, Modules: {len(course_data.get('modules', []))}"
                )
                return True
            elif response.status_code == 403:
                self.log_result(
                    "Student Course Access Test", 
                    "FAIL", 
                    "Student access denied (403) - may need enrollment",
                    f"Course ID: {course_id}"
                )
            elif response.status_code == 404:
                self.log_result(
                    "Student Course Access Test", 
                    "FAIL", 
                    "Course not found (404) - course may not exist",
                    f"Course ID: {course_id}"
                )
            else:
                self.log_result(
                    "Student Course Access Test", 
                    "FAIL", 
                    f"Student course access failed with status {response.status_code}",
                    f"Course ID: {course_id}, Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Course Access Test", 
                "FAIL", 
                "Failed to test student course access",
                str(e)
            )
        return False
    
    def test_chronological_order_creation(self):
        """Test chronological order question creation process"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Chronological Order Creation Test", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            # Create a test course with chronological order question
            test_course_data = {
                "title": "Chronological Order Test Course",
                "description": "Testing chronological order question creation with commas and spaces",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Test Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Chronological Order Quiz",
                                "type": "quiz",
                                "content": {
                                    "questions": [
                                        {
                                            "type": "chronological-order",
                                            "question": "Arrange these events in chronological order:",
                                            "items": [
                                                "First event",
                                                "Second event", 
                                                "Third event",
                                                "Fourth event"
                                            ],
                                            "correctAnswer": "2, 1, 4, 3"  # Testing comma-separated format
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
                
                # Verify the course was created with correct structure
                verify_response = requests.get(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if verify_response.status_code == 200:
                    verified_course = verify_response.json()
                    modules = verified_course.get('modules', [])
                    
                    if modules and modules[0].get('lessons'):
                        lesson = modules[0]['lessons'][0]
                        questions = lesson.get('content', {}).get('questions', [])
                        
                        if questions and questions[0].get('type') == 'chronological-order':
                            question = questions[0]
                            correct_answer = question.get('correctAnswer')
                            items = question.get('items', [])
                            
                            # Test comma parsing
                            comma_test_passed = ',' in correct_answer if correct_answer else False
                            items_test_passed = len(items) == 4
                            
                            if comma_test_passed and items_test_passed:
                                self.log_result(
                                    "Chronological Order Creation Test", 
                                    "PASS", 
                                    "Chronological order question created successfully with comma-separated answer",
                                    f"Course ID: {course_id}, Correct Answer: '{correct_answer}', Items: {len(items)}"
                                )
                                
                                # Clean up - delete test course
                                requests.delete(
                                    f"{BACKEND_URL}/courses/{course_id}",
                                    timeout=TEST_TIMEOUT,
                                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                                )
                                
                                return True
                            else:
                                self.log_result(
                                    "Chronological Order Creation Test", 
                                    "FAIL", 
                                    "Chronological order question structure incorrect",
                                    f"Comma test: {comma_test_passed}, Items test: {items_test_passed}, Answer: '{correct_answer}'"
                                )
                        else:
                            self.log_result(
                                "Chronological Order Creation Test", 
                                "FAIL", 
                                "Created course missing chronological order question",
                                f"Questions found: {len(questions)}, Types: {[q.get('type') for q in questions]}"
                            )
                    else:
                        self.log_result(
                            "Chronological Order Creation Test", 
                            "FAIL", 
                            "Created course missing modules or lessons",
                            f"Modules: {len(modules)}"
                        )
                else:
                    self.log_result(
                        "Chronological Order Creation Test", 
                        "FAIL", 
                        f"Failed to verify created course, status: {verify_response.status_code}",
                        f"Course ID: {course_id}"
                    )
            else:
                self.log_result(
                    "Chronological Order Creation Test", 
                    "FAIL", 
                    f"Failed to create test course, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Chronological Order Creation Test", 
                "FAIL", 
                "Failed to test chronological order creation",
                str(e)
            )
        return False
    
    def test_quiz_data_format_compatibility(self, course_analysis):
        """Test if quiz data format is compatible with frontend expectations"""
        if not course_analysis:
            self.log_result(
                "Quiz Data Format Compatibility Test", 
                "SKIP", 
                "No course analysis available",
                "Course analysis required"
            )
            return False
        
        compatibility_issues = []
        compatibility_warnings = []
        
        # Check each quiz lesson for format compatibility
        for lesson in course_analysis.get('quiz_lessons', []):
            lesson_title = lesson.get('lesson_title', 'Unknown')
            questions = lesson.get('questions', [])
            
            for question in questions:
                q_type = question.get('type')
                q_index = question.get('question_index')
                raw_data = question.get('raw_data', {})
                
                # Check required fields for each question type
                if q_type == 'multiple-choice':
                    if not question.get('has_options'):
                        compatibility_issues.append(f"Multiple choice question {q_index} in '{lesson_title}' missing 'options' field")
                    if not question.get('has_correct_answer'):
                        compatibility_issues.append(f"Multiple choice question {q_index} in '{lesson_title}' missing 'correctAnswer' field")
                
                elif q_type == 'true-false':
                    if not question.get('has_correct_answer'):
                        compatibility_issues.append(f"True/false question {q_index} in '{lesson_title}' missing 'correctAnswer' field")
                
                elif q_type == 'short-answer':
                    if not question.get('has_correct_answer'):
                        compatibility_warnings.append(f"Short answer question {q_index} in '{lesson_title}' missing 'correctAnswer' field (may be optional)")
                
                elif q_type == 'select-all-that-apply':
                    if not question.get('has_options'):
                        compatibility_issues.append(f"Select-all question {q_index} in '{lesson_title}' missing 'options' field")
                    if not question.get('has_correct_answer'):
                        compatibility_issues.append(f"Select-all question {q_index} in '{lesson_title}' missing 'correctAnswer' field")
                
                elif q_type == 'chronological-order':
                    if not question.get('has_items'):
                        compatibility_issues.append(f"Chronological question {q_index} in '{lesson_title}' missing 'items' field")
                    if not question.get('has_correct_answer'):
                        compatibility_issues.append(f"Chronological question {q_index} in '{lesson_title}' missing 'correctAnswer' field")
                    
                    # Check if items is an array
                    items = raw_data.get('items')
                    if items is not None and not isinstance(items, list):
                        compatibility_issues.append(f"Chronological question {q_index} in '{lesson_title}' 'items' field is not an array")
                
                elif q_type == 'long-form-answer':
                    # Long form answers typically don't need specific validation
                    pass
                
                else:
                    compatibility_warnings.append(f"Unknown question type '{q_type}' in question {q_index} of '{lesson_title}'")
        
        # Determine test result
        critical_issues = len(compatibility_issues)
        warnings = len(compatibility_warnings)
        
        if critical_issues == 0:
            self.log_result(
                "Quiz Data Format Compatibility Test", 
                "PASS", 
                f"Quiz data format is compatible with frontend - {warnings} warnings",
                f"Analyzed {len(course_analysis.get('quiz_lessons', []))} quiz lessons, {warnings} warnings: {compatibility_warnings[:3]}"
            )
            return True
        else:
            self.log_result(
                "Quiz Data Format Compatibility Test", 
                "FAIL", 
                f"Found {critical_issues} critical compatibility issues that could cause React Error #31",
                f"Critical issues: {compatibility_issues[:3]}; Warnings: {compatibility_warnings[:2]}"
            )
            return False
    
    def run_investigation(self):
        """Run the complete quiz investigation"""
        print("🔍 URGENT: Different Course Quiz Investigation + Creation Bug")
        print("=" * 80)
        print("INVESTIGATION SCOPE:")
        print("✅ Find and examine course 'All quizzes as options'")
        print("✅ Check quiz structure and question types in this specific course")
        print("✅ Verify if quiz data structure differs from expected format")
        print("✅ Test chronological order question creation process")
        print("✅ Check if there are data format mismatches causing React Error #31")
        print("=" * 80)
        
        # Step 1: Authentication
        print("\n🔑 STEP 1: Authentication")
        print("-" * 50)
        admin_success = self.test_admin_login()
        student_success = self.test_student_login()
        
        if not admin_success:
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Step 2: Find target course
        print("\n🎯 STEP 2: Find 'All quizzes as options' Course")
        print("-" * 50)
        target_course = self.find_all_quizzes_as_options_course()
        
        if not target_course:
            print("⚠️ Target course not found, but continuing with other tests")
        
        # Step 3: Analyze quiz structure
        print("\n📊 STEP 3: Analyze Quiz Structure")
        print("-" * 50)
        course_analysis = None
        if target_course:
            course_analysis = self.analyze_course_quiz_structure(target_course)
        else:
            print("⚠️ Skipping quiz structure analysis - no target course")
        
        # Step 4: Test student access
        print("\n👤 STEP 4: Test Student Access")
        print("-" * 50)
        if student_success and target_course:
            self.test_student_course_access(target_course)
        else:
            print("⚠️ Skipping student access test - authentication failed or no target course")
        
        # Step 5: Test chronological order creation
        print("\n📝 STEP 5: Test Chronological Order Creation")
        print("-" * 50)
        self.test_chronological_order_creation()
        
        # Step 6: Test data format compatibility
        print("\n🔧 STEP 6: Test Quiz Data Format Compatibility")
        print("-" * 50)
        self.test_quiz_data_format_compatibility(course_analysis)
        
        # Summary
        print(f"\n📊 INVESTIGATION SUMMARY")
        print("=" * 50)
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if course_analysis:
            print(f"\n🎯 TARGET COURSE ANALYSIS:")
            print(f"   Course: {course_analysis.get('title')}")
            print(f"   Quiz Modules: {course_analysis.get('quiz_modules')}")
            print(f"   Question Types: {list(course_analysis.get('question_types', []))}")
            print(f"   Data Issues: {len(course_analysis.get('data_structure_issues', []))}")
            print(f"   React Error Causes: {len(course_analysis.get('potential_react_error_causes', []))}")
        
        return self.failed == 0

def main():
    tester = QuizInvestigationTester()
    success = tester.run_investigation()
    
    if success:
        print("\n🎉 INVESTIGATION COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("\n🚨 INVESTIGATION FOUND ISSUES - REVIEW RESULTS ABOVE")
        sys.exit(1)

if __name__ == "__main__":
    main()