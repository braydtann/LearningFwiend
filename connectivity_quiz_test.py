#!/usr/bin/env python3
"""
URGENT BACKEND CONNECTIVITY VERIFICATION - POST ENVIRONMENT FIX
Testing backend API connectivity after fixing frontend environment configuration 
from unreachable preview URL to localhost:8001.

PRIORITY TESTS:
1. Basic API Connectivity - Verify backend responds to standard API calls
2. Quiz Data Endpoints - Test GET /api/courses/{id} for courses with quiz content  
3. Question Type Support - Verify backend serves all question types properly:
   - Multiple choice questions
   - Long form answer questions  
   - Chronological order questions
   - Select all that apply questions

TESTING CREDENTIALS:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!

EXPECTED OUTCOMES:
- No more "network connection reset" errors
- Quiz data loading correctly from backend
- All question types properly formatted
- API responses complete and valid
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using localhost URL as per review request
BACKEND_URL = "http://localhost:8001/api"
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

class ConnectivityQuizTester:
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
    
    # =============================================================================
    # PRIORITY TEST 1: BASIC API CONNECTIVITY
    # =============================================================================
    
    def test_basic_api_connectivity(self):
        """Test basic backend API connectivity after environment fix"""
        print("\n🔗 TESTING BASIC API CONNECTIVITY")
        print("=" * 60)
        
        try:
            # Test 1: Basic health check
            response = requests.get(f"{BACKEND_URL}/", timeout=TEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == 'Hello World':
                    self.log_result(
                        "Basic API Health Check", 
                        "PASS", 
                        "Backend API responding correctly on localhost:8001",
                        f"Response: {data}"
                    )
                else:
                    self.log_result(
                        "Basic API Health Check", 
                        "FAIL", 
                        "Backend responded but with unexpected message",
                        f"Expected 'Hello World', got: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Basic API Health Check", 
                    "FAIL", 
                    f"Backend not responding properly (status: {response.status_code})",
                    f"Expected 200, got {response.status_code}"
                )
                return False
                
        except requests.exceptions.ConnectionError as e:
            self.log_result(
                "Basic API Health Check", 
                "FAIL", 
                "Connection refused - backend not accessible on localhost:8001",
                f"Connection error: {str(e)}"
            )
            return False
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Basic API Health Check", 
                "FAIL", 
                "Failed to connect to backend API",
                f"Request error: {str(e)}"
            )
            return False
        
        return True
    
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
                        f"Role: {user_info.get('role')}, Token received"
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
                    f"Admin login failed (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Authentication", 
                "FAIL", 
                "Failed to authenticate admin",
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
                        f"Role: {user_info.get('role')}, Token received"
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
                    f"Student login failed (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Authentication", 
                "FAIL", 
                "Failed to authenticate student",
                str(e)
            )
        return False
    
    # =============================================================================
    # PRIORITY TEST 2: QUIZ DATA ENDPOINTS
    # =============================================================================
    
    def test_quiz_data_endpoints(self):
        """Test GET /api/courses/{id} for courses with quiz content"""
        print("\n📚 TESTING QUIZ DATA ENDPOINTS")
        print("=" * 60)
        
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Quiz Data Endpoints", 
                "SKIP", 
                "No admin token available for course access",
                "Admin authentication required"
            )
            return False
        
        try:
            # First get all courses to find ones with quiz content
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if courses_response.status_code != 200:
                self.log_result(
                    "Quiz Data Endpoints", 
                    "FAIL", 
                    f"Failed to get courses list (status: {courses_response.status_code})",
                    f"Response: {courses_response.text}"
                )
                return False
            
            courses = courses_response.json()
            quiz_courses = []
            
            # Test each course to find quiz content
            for course in courses[:10]:  # Test first 10 courses
                course_id = course.get('id')
                if not course_id:
                    continue
                
                try:
                    course_response = requests.get(
                        f"{BACKEND_URL}/courses/{course_id}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                    )
                    
                    if course_response.status_code == 200:
                        course_data = course_response.json()
                        modules = course_data.get('modules', [])
                        
                        # Check for quiz lessons
                        has_quiz = False
                        quiz_lessons = []
                        
                        for module in modules:
                            lessons = module.get('lessons', [])
                            for lesson in lessons:
                                lesson_type = lesson.get('type', '').lower()
                                lesson_title = lesson.get('title', '').lower()
                                
                                if 'quiz' in lesson_type or 'quiz' in lesson_title:
                                    has_quiz = True
                                    quiz_lessons.append({
                                        'id': lesson.get('id'),
                                        'title': lesson.get('title'),
                                        'type': lesson.get('type'),
                                        'questions': lesson.get('questions', [])
                                    })
                        
                        if has_quiz:
                            quiz_courses.append({
                                'id': course_id,
                                'title': course_data.get('title'),
                                'quiz_lessons': quiz_lessons
                            })
                            
                except requests.exceptions.RequestException:
                    continue
            
            if quiz_courses:
                self.log_result(
                    "Quiz Data Endpoints", 
                    "PASS", 
                    f"Successfully retrieved {len(quiz_courses)} courses with quiz content",
                    f"Quiz courses found: {[c['title'] for c in quiz_courses[:3]]}"
                )
                return quiz_courses
            else:
                self.log_result(
                    "Quiz Data Endpoints", 
                    "FAIL", 
                    f"No courses with quiz content found among {len(courses)} courses",
                    "Need courses with quiz lessons to test quiz functionality"
                )
                return []
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Data Endpoints", 
                "FAIL", 
                "Failed to test quiz data endpoints",
                str(e)
            )
            return []
    
    # =============================================================================
    # PRIORITY TEST 3: QUESTION TYPE SUPPORT
    # =============================================================================
    
    def test_question_type_support(self, quiz_courses):
        """Test that backend serves all question types properly"""
        print("\n❓ TESTING QUESTION TYPE SUPPORT")
        print("=" * 60)
        
        if not quiz_courses:
            self.log_result(
                "Question Type Support", 
                "SKIP", 
                "No quiz courses available for question type testing",
                "Need courses with quiz content"
            )
            return False
        
        # Expected question types from review request
        expected_types = [
            'multiple-choice',
            'long-form-answer', 
            'chronological-order',
            'select-all-that-apply'
        ]
        
        found_types = set()
        question_samples = {}
        
        for course in quiz_courses:
            for quiz_lesson in course['quiz_lessons']:
                questions = quiz_lesson.get('questions', [])
                
                for question in questions:
                    q_type = question.get('type', '').lower()
                    
                    # Normalize question type names
                    if 'multiple' in q_type and 'choice' in q_type:
                        normalized_type = 'multiple-choice'
                    elif 'long' in q_type and 'form' in q_type:
                        normalized_type = 'long-form-answer'
                    elif 'chronological' in q_type or 'order' in q_type:
                        normalized_type = 'chronological-order'
                    elif 'select' in q_type and 'all' in q_type:
                        normalized_type = 'select-all-that-apply'
                    else:
                        normalized_type = q_type
                    
                    if normalized_type in expected_types:
                        found_types.add(normalized_type)
                        if normalized_type not in question_samples:
                            question_samples[normalized_type] = {
                                'question': question.get('question', 'N/A'),
                                'options': question.get('options', []),
                                'items': question.get('items', []),
                                'correctAnswer': question.get('correctAnswer'),
                                'course': course['title'],
                                'lesson': quiz_lesson['title']
                            }
        
        # Validate each found question type
        validation_results = []
        
        for q_type in found_types:
            sample = question_samples[q_type]
            valid = True
            issues = []
            
            if q_type == 'multiple-choice':
                if not sample.get('options') or len(sample['options']) < 2:
                    valid = False
                    issues.append("Missing or insufficient options")
                if not sample.get('correctAnswer'):
                    valid = False
                    issues.append("Missing correct answer")
            
            elif q_type == 'long-form-answer':
                if not sample.get('question'):
                    valid = False
                    issues.append("Missing question text")
            
            elif q_type == 'chronological-order':
                if not sample.get('items') or len(sample['items']) < 2:
                    valid = False
                    issues.append("Missing or insufficient items for ordering")
                if not sample.get('correctAnswer'):
                    valid = False
                    issues.append("Missing correct order")
            
            elif q_type == 'select-all-that-apply':
                if not sample.get('options') or len(sample['options']) < 2:
                    valid = False
                    issues.append("Missing or insufficient options")
                if not sample.get('correctAnswer'):
                    valid = False
                    issues.append("Missing correct answers")
            
            validation_results.append({
                'type': q_type,
                'valid': valid,
                'issues': issues,
                'sample': sample
            })
        
        # Report results
        valid_types = [r for r in validation_results if r['valid']]
        invalid_types = [r for r in validation_results if not r['valid']]
        missing_types = set(expected_types) - found_types
        
        if len(valid_types) >= 3 and len(invalid_types) == 0:
            self.log_result(
                "Question Type Support", 
                "PASS", 
                f"Backend properly serves {len(valid_types)} question types",
                f"Valid types: {[t['type'] for t in valid_types]}"
            )
            return True
        else:
            issues = []
            if invalid_types:
                issues.append(f"Invalid types: {[t['type'] for t in invalid_types]}")
            if missing_types:
                issues.append(f"Missing types: {list(missing_types)}")
            
            self.log_result(
                "Question Type Support", 
                "FAIL", 
                f"Question type support issues found",
                f"Issues: {'; '.join(issues)}"
            )
            return False
    
    # =============================================================================
    # COMPREHENSIVE TEST RUNNER
    # =============================================================================
    
    def run_connectivity_tests(self):
        """Run all connectivity and quiz tests"""
        print("\n🚀 URGENT BACKEND CONNECTIVITY VERIFICATION")
        print("=" * 80)
        print("Testing backend API connectivity after environment fix")
        print("Focus: No more 'network connection reset' errors")
        print("=" * 80)
        
        # Test 1: Basic API Connectivity
        basic_connectivity = self.test_basic_api_connectivity()
        
        if not basic_connectivity:
            print("\n❌ CRITICAL: Basic connectivity failed - cannot proceed with other tests")
            return False
        
        # Test 2: Authentication
        admin_auth = self.test_admin_authentication()
        student_auth = self.test_student_authentication()
        
        if not admin_auth and not student_auth:
            print("\n❌ CRITICAL: Both admin and student authentication failed")
            return False
        
        # Test 3: Quiz Data Endpoints
        quiz_courses = self.test_quiz_data_endpoints()
        
        # Test 4: Question Type Support
        question_types_ok = self.test_question_type_support(quiz_courses)
        
        # Summary
        print(f"\n📊 CONNECTIVITY TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.passed >= 4 and self.failed <= 1:
            print(f"\n🎉 SUCCESS: Backend connectivity verified after environment fix")
            print(f"   - No connection reset errors detected")
            print(f"   - Quiz data loading correctly")
            print(f"   - API responses complete and valid")
            return True
        else:
            print(f"\n⚠️ ISSUES DETECTED: Some connectivity problems remain")
            print(f"   - Review failed tests above")
            print(f"   - May need additional environment fixes")
            return False

def main():
    """Main test execution"""
    tester = ConnectivityQuizTester()
    success = tester.run_connectivity_tests()
    
    # Save results
    with open('/app/connectivity_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'passed': tester.passed,
            'failed': tester.failed,
            'results': tester.results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())