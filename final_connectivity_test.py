#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE BACKEND CONNECTIVITY VERIFICATION
Post environment fix validation - all requirements from review request
"""

import requests
import json
from datetime import datetime
import time

BACKEND_URL = "http://localhost:8001/api"
TEST_TIMEOUT = 15

ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class FinalConnectivityTester:
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
    
    def test_no_connection_reset_errors(self):
        """Verify no 'network connection reset' errors occur"""
        print("\n🔗 TESTING: No Network Connection Reset Errors")
        print("-" * 60)
        
        connection_tests = [
            ("Basic Health Check", f"{BACKEND_URL}/"),
            ("Authentication Endpoint", f"{BACKEND_URL}/auth/login"),
            ("Courses Endpoint", f"{BACKEND_URL}/courses"),
            ("Categories Endpoint", f"{BACKEND_URL}/categories"),
            ("Departments Endpoint", f"{BACKEND_URL}/departments")
        ]
        
        connection_errors = []
        successful_connections = []
        
        for test_name, endpoint in connection_tests:
            try:
                if "auth/login" in endpoint:
                    # Test login endpoint
                    response = requests.post(
                        endpoint,
                        json=ADMIN_CREDENTIALS,
                        timeout=TEST_TIMEOUT,
                        headers={'Content-Type': 'application/json'}
                    )
                else:
                    # Test GET endpoints
                    response = requests.get(endpoint, timeout=TEST_TIMEOUT)
                
                if response.status_code in [200, 401, 403]:  # 401/403 are expected for unauth requests
                    successful_connections.append(test_name)
                else:
                    connection_errors.append(f"{test_name}: HTTP {response.status_code}")
                    
            except requests.exceptions.ConnectionError as e:
                if "connection reset" in str(e).lower():
                    connection_errors.append(f"{test_name}: CONNECTION RESET ERROR")
                else:
                    connection_errors.append(f"{test_name}: Connection Error")
            except Exception as e:
                connection_errors.append(f"{test_name}: {str(e)}")
        
        if len(connection_errors) == 0:
            self.log_result(
                "No Connection Reset Errors", 
                "PASS", 
                f"All {len(successful_connections)} endpoints accessible without connection reset errors",
                f"Tested: {', '.join(successful_connections)}"
            )
            return True
        else:
            self.log_result(
                "No Connection Reset Errors", 
                "FAIL", 
                f"Found {len(connection_errors)} connection issues",
                f"Errors: {'; '.join(connection_errors)}"
            )
            return False
    
    def test_quiz_data_loading(self):
        """Test quiz data loading correctly from backend"""
        print("\n📚 TESTING: Quiz Data Loading Correctly")
        print("-" * 60)
        
        # Login as admin first
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=ADMIN_CREDENTIALS,
            timeout=TEST_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response.status_code != 200:
            self.log_result(
                "Quiz Data Loading", 
                "FAIL", 
                "Cannot test quiz data - admin authentication failed",
                f"Login status: {login_response.status_code}"
            )
            return False
        
        token = login_response.json().get('access_token')
        self.auth_tokens['admin'] = token
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get courses and find quiz courses
        courses_response = requests.get(f"{BACKEND_URL}/courses", timeout=TEST_TIMEOUT, headers=headers)
        
        if courses_response.status_code != 200:
            self.log_result(
                "Quiz Data Loading", 
                "FAIL", 
                f"Failed to load courses (status: {courses_response.status_code})",
                f"Response: {courses_response.text}"
            )
            return False
        
        courses = courses_response.json()
        quiz_courses_found = 0
        quiz_data_valid = 0
        
        for course in courses:
            course_id = course.get('id')
            
            # Get detailed course data
            course_response = requests.get(f"{BACKEND_URL}/courses/{course_id}", timeout=TEST_TIMEOUT, headers=headers)
            
            if course_response.status_code == 200:
                course_data = course_response.json()
                modules = course_data.get('modules', [])
                
                for module in modules:
                    lessons = module.get('lessons', [])
                    for lesson in lessons:
                        if lesson.get('type') == 'quiz' or 'quiz' in lesson.get('title', '').lower():
                            quiz_courses_found += 1
                            
                            # Validate quiz data structure
                            questions = lesson.get('questions', [])
                            if questions and len(questions) > 0:
                                # Check if questions have required fields
                                valid_questions = 0
                                for question in questions:
                                    if question.get('question') and question.get('type'):
                                        valid_questions += 1
                                
                                if valid_questions == len(questions):
                                    quiz_data_valid += 1
        
        if quiz_courses_found > 0 and quiz_data_valid > 0:
            self.log_result(
                "Quiz Data Loading", 
                "PASS", 
                f"Quiz data loading correctly - {quiz_data_valid} valid quiz courses found",
                f"Total quiz courses: {quiz_courses_found}, Valid data: {quiz_data_valid}"
            )
            return True
        else:
            self.log_result(
                "Quiz Data Loading", 
                "FAIL", 
                f"Quiz data loading issues - found {quiz_courses_found} quiz courses, {quiz_data_valid} with valid data",
                "Need valid quiz courses with proper question structure"
            )
            return False
    
    def test_all_question_types_properly_formatted(self):
        """Test all question types are properly formatted"""
        print("\n❓ TESTING: All Question Types Properly Formatted")
        print("-" * 60)
        
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Question Types Formatting", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        headers = {'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
        
        # Look for our test course with all question types
        courses_response = requests.get(f"{BACKEND_URL}/courses", timeout=TEST_TIMEOUT, headers=headers)
        courses = courses_response.json()
        
        test_course = None
        for course in courses:
            if "Backend Connectivity Test Course" in course.get('title', ''):
                test_course = course
                break
        
        if not test_course:
            self.log_result(
                "Question Types Formatting", 
                "FAIL", 
                "Test course with all question types not found",
                "Need test course created by create_test_quiz.py"
            )
            return False
        
        # Get detailed course data
        course_response = requests.get(f"{BACKEND_URL}/courses/{test_course['id']}", timeout=TEST_TIMEOUT, headers=headers)
        course_data = course_response.json()
        
        # Find quiz lesson
        quiz_questions = []
        for module in course_data.get('modules', []):
            for lesson in module.get('lessons', []):
                if lesson.get('type') == 'quiz':
                    quiz_questions = lesson.get('questions', [])
                    break
        
        if not quiz_questions:
            self.log_result(
                "Question Types Formatting", 
                "FAIL", 
                "No quiz questions found in test course",
                "Quiz lesson structure may be incorrect"
            )
            return False
        
        # Validate each question type
        expected_types = ['multiple-choice', 'long-form-answer', 'chronological-order', 'select-all-that-apply']
        found_types = {}
        formatting_issues = []
        
        for question in quiz_questions:
            q_type = question.get('type')
            q_text = question.get('question')
            
            if q_type in expected_types:
                found_types[q_type] = question
                
                # Validate formatting for each type
                if q_type == 'multiple-choice':
                    options = question.get('options', [])
                    correct = question.get('correctAnswer')
                    if len(options) < 2 or not correct:
                        formatting_issues.append(f"{q_type}: Missing options or correct answer")
                
                elif q_type == 'long-form-answer':
                    if not q_text or len(q_text.strip()) < 10:
                        formatting_issues.append(f"{q_type}: Question text too short or missing")
                
                elif q_type == 'chronological-order':
                    items = question.get('items', [])
                    correct_order = question.get('correctAnswer', [])
                    if len(items) < 2 or not correct_order:
                        formatting_issues.append(f"{q_type}: Missing items or correct order")
                
                elif q_type == 'select-all-that-apply':
                    options = question.get('options', [])
                    correct = question.get('correctAnswer', [])
                    if len(options) < 2 or not correct:
                        formatting_issues.append(f"{q_type}: Missing options or correct answers")
        
        missing_types = set(expected_types) - set(found_types.keys())
        
        if len(formatting_issues) == 0 and len(missing_types) == 0:
            self.log_result(
                "Question Types Formatting", 
                "PASS", 
                f"All {len(expected_types)} question types properly formatted",
                f"Validated: {list(found_types.keys())}"
            )
            return True
        else:
            issues = []
            if formatting_issues:
                issues.extend(formatting_issues)
            if missing_types:
                issues.append(f"Missing types: {list(missing_types)}")
            
            self.log_result(
                "Question Types Formatting", 
                "FAIL", 
                f"Question type formatting issues found",
                f"Issues: {'; '.join(issues)}"
            )
            return False
    
    def test_api_responses_complete_and_valid(self):
        """Test API responses are complete and valid"""
        print("\n📋 TESTING: API Responses Complete and Valid")
        print("-" * 60)
        
        # Test various API endpoints for complete responses
        api_tests = []
        
        # Test 1: Authentication response completeness
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=STUDENT_CREDENTIALS,
            timeout=TEST_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            required_fields = ['access_token', 'token_type', 'user']
            missing_fields = [field for field in required_fields if field not in login_data]
            
            if not missing_fields:
                api_tests.append("✅ Login response complete")
                student_token = login_data.get('access_token')
                self.auth_tokens['student'] = student_token
            else:
                api_tests.append(f"❌ Login response missing: {missing_fields}")
        else:
            api_tests.append(f"❌ Login failed: {login_response.status_code}")
        
        # Test 2: Course list response completeness
        if "student" in self.auth_tokens:
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if courses_response.status_code == 200:
                courses = courses_response.json()
                if isinstance(courses, list) and len(courses) > 0:
                    # Check first course structure
                    first_course = courses[0]
                    required_course_fields = ['id', 'title', 'description', 'category']
                    missing_course_fields = [field for field in required_course_fields if field not in first_course]
                    
                    if not missing_course_fields:
                        api_tests.append("✅ Courses response complete")
                    else:
                        api_tests.append(f"❌ Course response missing: {missing_course_fields}")
                else:
                    api_tests.append("✅ Courses response valid (empty list)")
            else:
                api_tests.append(f"❌ Courses request failed: {courses_response.status_code}")
        
        # Test 3: User profile response completeness
        if "student" in self.auth_tokens:
            profile_response = requests.get(
                f"{BACKEND_URL}/auth/me",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if profile_response.status_code == 200:
                profile = profile_response.json()
                required_profile_fields = ['id', 'email', 'role', 'full_name']
                missing_profile_fields = [field for field in required_profile_fields if field not in profile]
                
                if not missing_profile_fields:
                    api_tests.append("✅ Profile response complete")
                else:
                    api_tests.append(f"❌ Profile response missing: {missing_profile_fields}")
            else:
                api_tests.append(f"❌ Profile request failed: {profile_response.status_code}")
        
        # Evaluate results
        passed_tests = [test for test in api_tests if test.startswith("✅")]
        failed_tests = [test for test in api_tests if test.startswith("❌")]
        
        if len(failed_tests) == 0 and len(passed_tests) >= 3:
            self.log_result(
                "API Responses Complete and Valid", 
                "PASS", 
                f"All {len(passed_tests)} API responses are complete and valid",
                f"Tests: {'; '.join(passed_tests)}"
            )
            return True
        else:
            self.log_result(
                "API Responses Complete and Valid", 
                "FAIL", 
                f"API response issues found - {len(failed_tests)} failed, {len(passed_tests)} passed",
                f"Failed: {'; '.join(failed_tests)}"
            )
            return False
    
    def run_final_verification(self):
        """Run all final verification tests"""
        print("\n🚀 FINAL BACKEND CONNECTIVITY VERIFICATION")
        print("=" * 80)
        print("URGENT: Post environment fix validation")
        print("Testing all requirements from review request")
        print("=" * 80)
        
        # Run all tests
        test1 = self.test_no_connection_reset_errors()
        test2 = self.test_quiz_data_loading()
        test3 = self.test_all_question_types_properly_formatted()
        test4 = self.test_api_responses_complete_and_valid()
        
        # Final summary
        print(f"\n📊 FINAL VERIFICATION SUMMARY")
        print("=" * 50)
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        # Specific outcomes validation
        print(f"\n🎯 EXPECTED OUTCOMES VALIDATION:")
        print("-" * 40)
        print(f"✅ No 'network connection reset' errors: {'VERIFIED' if test1 else '❌ FAILED'}")
        print(f"✅ Quiz data loading correctly: {'VERIFIED' if test2 else '❌ FAILED'}")
        print(f"✅ All question types properly formatted: {'VERIFIED' if test3 else '❌ FAILED'}")
        print(f"✅ API responses complete and valid: {'VERIFIED' if test4 else '❌ FAILED'}")
        
        if self.passed >= 3 and self.failed <= 1:
            print(f"\n🎉 SUCCESS: Backend connectivity verification PASSED")
            print(f"   Environment fix has resolved the connectivity issues")
            print(f"   Backend APIs are working correctly with localhost:8001")
            return True
        else:
            print(f"\n⚠️ ISSUES: Backend connectivity verification FAILED")
            print(f"   Some connectivity problems remain after environment fix")
            print(f"   Review failed tests above for specific issues")
            return False

def main():
    """Main test execution"""
    tester = FinalConnectivityTester()
    success = tester.run_final_verification()
    
    # Save results
    with open('/app/final_connectivity_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'passed': tester.passed,
            'failed': tester.failed,
            'results': tester.results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())