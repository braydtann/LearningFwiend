#!/usr/bin/env python3
"""
URGENT QUIZ SUBMISSION API DEBUGGING TEST
LearningFwiend LMS Application - Quiz Submission Issue Investigation

ISSUE DETAILS:
- User can start quiz successfully (ReferenceError 'F' is now fixed)
- Quiz submission failing with 422 error on PUT /api/enrollments/{course_id}/progress endpoint
- Console shows "Error submitting quiz: Error: Failed to update progress"
- Need to test with specific credentials and course

TARGET: PUT /api/enrollments/{course_id}/progress endpoint
EXPECTED DATA FORMAT: { progress: float (0-100), currentLessonId: string, timeSpent: int }
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using Production Backend URL from frontend/.env
BACKEND_URL = "https://lms-quiz-repair.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Test credentials from review request
STUDENT_CREDENTIALS = {
    "username_or_email": "brayden.student@learningfwiend.com",
    "password": "Cove1234!"
}

class QuizSubmissionTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        self.student_info = None
        self.target_course_id = None
        
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
    
    def test_student_authentication(self):
        """Test student authentication with provided credentials"""
        print("\n🔑 TESTING STUDENT AUTHENTICATION")
        print("=" * 60)
        print(f"Testing credentials: {STUDENT_CREDENTIALS['username_or_email']} / {STUDENT_CREDENTIALS['password']}")
        
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
                requires_password_change = data.get('requires_password_change', False)
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['student'] = token
                    self.student_info = user_info
                    
                    self.log_result(
                        "Student Authentication", 
                        "PASS", 
                        f"✅ Student login successful: {user_info.get('full_name')} ({user_info.get('email')})",
                        f"User ID: {user_info.get('id')}, Password change required: {requires_password_change}"
                    )
                    return True
                else:
                    self.log_result(
                        "Student Authentication", 
                        "FAIL", 
                        "Login successful but user is not a student or token missing",
                        f"Role: {user_info.get('role')}, Token present: {bool(token)}"
                    )
            else:
                self.log_result(
                    "Student Authentication", 
                    "FAIL", 
                    f"Authentication failed with status {response.status_code}",
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
    
    def find_target_course(self):
        """Find the target course 'ttttt' mentioned in the issue"""
        print("\n🔍 FINDING TARGET COURSE 'ttttt'")
        print("=" * 60)
        
        if "student" not in self.auth_tokens:
            self.log_result(
                "Find Target Course", 
                "FAIL", 
                "No student authentication token available",
                "Student must be authenticated first"
            )
            return False
        
        try:
            # Get all courses available to student
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                print(f"Found {len(courses)} courses available to student")
                
                # Look for course with title 'ttttt'
                target_course = None
                for course in courses:
                    if course.get('title', '').lower() == 'ttttt':
                        target_course = course
                        break
                
                if target_course:
                    self.target_course_id = target_course.get('id')
                    
                    self.log_result(
                        "Find Target Course", 
                        "PASS", 
                        f"✅ Found target course 'ttttt': {target_course.get('title')}",
                        f"Course ID: {self.target_course_id}, Modules: {len(target_course.get('modules', []))}"
                    )
                    
                    # Print course structure for debugging
                    print(f"\n📚 COURSE STRUCTURE:")
                    print(f"   Title: {target_course.get('title')}")
                    print(f"   ID: {self.target_course_id}")
                    print(f"   Description: {target_course.get('description', 'N/A')}")
                    print(f"   Category: {target_course.get('category', 'N/A')}")
                    print(f"   Modules: {len(target_course.get('modules', []))}")
                    
                    modules = target_course.get('modules', [])
                    for i, module in enumerate(modules):
                        print(f"   Module {i+1}: {module.get('title', 'Untitled')}")
                        lessons = module.get('lessons', [])
                        for j, lesson in enumerate(lessons):
                            lesson_type = lesson.get('type', 'unknown')
                            print(f"     Lesson {j+1}: {lesson.get('title', 'Untitled')} (Type: {lesson_type})")
                    
                    return True
                else:
                    # List available courses for debugging
                    print(f"\n📋 AVAILABLE COURSES:")
                    for course in courses[:10]:  # Show first 10 courses
                        print(f"   - {course.get('title', 'Untitled')} (ID: {course.get('id')})")
                    
                    self.log_result(
                        "Find Target Course", 
                        "FAIL", 
                        "Target course 'ttttt' not found in available courses",
                        f"Searched {len(courses)} courses, none matched 'ttttt'"
                    )
            else:
                self.log_result(
                    "Find Target Course", 
                    "FAIL", 
                    f"Failed to retrieve courses list, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Find Target Course", 
                "FAIL", 
                "Failed to connect to courses endpoint",
                str(e)
            )
        return False
    
    def check_student_enrollment(self):
        """Check if student is enrolled in the target course"""
        print("\n📝 CHECKING STUDENT ENROLLMENT IN TARGET COURSE")
        print("=" * 60)
        
        if not self.target_course_id or "student" not in self.auth_tokens:
            self.log_result(
                "Check Student Enrollment", 
                "SKIP", 
                "Target course not found or student not authenticated",
                "Prerequisites not met"
            )
            return False
        
        try:
            # Get student's enrollments
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                print(f"Student has {len(enrollments)} total enrollments")
                
                # Check if enrolled in target course
                target_enrollment = None
                for enrollment in enrollments:
                    if enrollment.get('courseId') == self.target_course_id:
                        target_enrollment = enrollment
                        break
                
                if target_enrollment:
                    self.log_result(
                        "Check Student Enrollment", 
                        "PASS", 
                        f"✅ Student is enrolled in target course",
                        f"Enrollment ID: {target_enrollment.get('id')}, Progress: {target_enrollment.get('progress', 0)}%, Status: {target_enrollment.get('status', 'unknown')}"
                    )
                    
                    print(f"\n📊 ENROLLMENT DETAILS:")
                    print(f"   Enrollment ID: {target_enrollment.get('id')}")
                    print(f"   Course ID: {target_enrollment.get('courseId')}")
                    print(f"   Progress: {target_enrollment.get('progress', 0)}%")
                    print(f"   Status: {target_enrollment.get('status', 'unknown')}")
                    print(f"   Enrolled At: {target_enrollment.get('enrolledAt', 'unknown')}")
                    print(f"   Last Accessed: {target_enrollment.get('lastAccessedAt', 'never')}")
                    
                    return target_enrollment
                else:
                    self.log_result(
                        "Check Student Enrollment", 
                        "FAIL", 
                        "Student is NOT enrolled in target course",
                        f"Course ID {self.target_course_id} not found in {len(enrollments)} enrollments"
                    )
            else:
                self.log_result(
                    "Check Student Enrollment", 
                    "FAIL", 
                    f"Failed to retrieve enrollments, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Check Student Enrollment", 
                "FAIL", 
                "Failed to connect to enrollments endpoint",
                str(e)
            )
        return False
    
    def test_progress_update_endpoint_structure(self):
        """Test the structure and requirements of the progress update endpoint"""
        print("\n🔧 TESTING PROGRESS UPDATE ENDPOINT STRUCTURE")
        print("=" * 60)
        
        if not self.target_course_id or "student" not in self.auth_tokens:
            self.log_result(
                "Progress Update Endpoint Structure", 
                "SKIP", 
                "Target course not found or student not authenticated",
                "Prerequisites not met"
            )
            return False
        
        # Test different data formats to understand what the API expects
        test_cases = [
            {
                "name": "Empty Request",
                "data": {},
                "expected_status": [400, 422]
            },
            {
                "name": "Progress Only",
                "data": {"progress": 50.0},
                "expected_status": [200, 422]
            },
            {
                "name": "Progress with Current Lesson",
                "data": {"progress": 75.0, "currentLessonId": "test-lesson-id"},
                "expected_status": [200, 422]
            },
            {
                "name": "Full Expected Format",
                "data": {"progress": 100.0, "currentLessonId": "test-lesson-id", "timeSpent": 300},
                "expected_status": [200, 422]
            },
            {
                "name": "Invalid Progress (String)",
                "data": {"progress": "100", "currentLessonId": "test-lesson-id", "timeSpent": 300},
                "expected_status": [422]
            },
            {
                "name": "Invalid Progress (Over 100)",
                "data": {"progress": 150.0, "currentLessonId": "test-lesson-id", "timeSpent": 300},
                "expected_status": [200, 422]  # API might clamp to 100
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"\n🧪 Testing: {test_case['name']}")
            print(f"   Data: {test_case['data']}")
            
            try:
                response = requests.put(
                    f"{BACKEND_URL}/enrollments/{self.target_course_id}/progress",
                    json=test_case['data'],
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["student"]}'
                    }
                )
                
                status_code = response.status_code
                response_text = response.text
                
                print(f"   Status: {status_code}")
                print(f"   Response: {response_text[:200]}{'...' if len(response_text) > 200 else ''}")
                
                if status_code in test_case['expected_status']:
                    result_status = "EXPECTED"
                else:
                    result_status = "UNEXPECTED"
                
                results.append({
                    'test_name': test_case['name'],
                    'status_code': status_code,
                    'expected': test_case['expected_status'],
                    'result': result_status,
                    'response': response_text,
                    'data_sent': test_case['data']
                })
                
                # If we get a 422, try to parse the error details
                if status_code == 422:
                    try:
                        error_data = response.json()
                        print(f"   422 Error Details: {error_data}")
                    except:
                        pass
                
            except requests.exceptions.RequestException as e:
                print(f"   Error: {str(e)}")
                results.append({
                    'test_name': test_case['name'],
                    'status_code': 'ERROR',
                    'expected': test_case['expected_status'],
                    'result': 'ERROR',
                    'response': str(e),
                    'data_sent': test_case['data']
                })
        
        # Analyze results
        successful_tests = [r for r in results if r['result'] == 'EXPECTED']
        failed_tests = [r for r in results if r['result'] != 'EXPECTED']
        
        if len(successful_tests) >= len(test_cases) // 2:
            self.log_result(
                "Progress Update Endpoint Structure", 
                "PASS", 
                f"✅ Endpoint structure analysis completed: {len(successful_tests)}/{len(test_cases)} tests behaved as expected",
                f"Results: {[r['test_name'] + ':' + str(r['status_code']) for r in results]}"
            )
        else:
            self.log_result(
                "Progress Update Endpoint Structure", 
                "FAIL", 
                f"❌ Endpoint structure issues found: {len(failed_tests)}/{len(test_cases)} tests had unexpected results",
                f"Failed tests: {[r['test_name'] + ':' + str(r['status_code']) + ' (expected ' + str(r['expected']) + ')' for r in failed_tests]}"
            )
        
        return results
    
    def test_quiz_submission_with_real_data(self):
        """Test quiz submission with realistic data that matches frontend expectations"""
        print("\n🎯 TESTING QUIZ SUBMISSION WITH REALISTIC DATA")
        print("=" * 60)
        
        if not self.target_course_id or "student" not in self.auth_tokens:
            self.log_result(
                "Quiz Submission with Real Data", 
                "SKIP", 
                "Target course not found or student not authenticated",
                "Prerequisites not met"
            )
            return False
        
        # First, get the course structure to find a real lesson ID
        try:
            course_response = requests.get(
                f"{BACKEND_URL}/courses/{self.target_course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if course_response.status_code != 200:
                self.log_result(
                    "Quiz Submission with Real Data", 
                    "FAIL", 
                    f"Cannot retrieve course details, status: {course_response.status_code}",
                    f"Response: {course_response.text}"
                )
                return False
            
            course_data = course_response.json()
            modules = course_data.get('modules', [])
            
            # Find a lesson ID from the course structure
            lesson_id = None
            quiz_lesson_id = None
            
            for module in modules:
                lessons = module.get('lessons', [])
                for lesson in lessons:
                    if not lesson_id:
                        lesson_id = lesson.get('id')
                    
                    # Look specifically for quiz lessons
                    lesson_type = lesson.get('type', '').lower()
                    if 'quiz' in lesson_type and not quiz_lesson_id:
                        quiz_lesson_id = lesson.get('id')
            
            # Use quiz lesson ID if available, otherwise use any lesson ID
            current_lesson_id = quiz_lesson_id or lesson_id
            
            if not current_lesson_id:
                self.log_result(
                    "Quiz Submission with Real Data", 
                    "FAIL", 
                    "No lesson IDs found in course structure",
                    f"Course has {len(modules)} modules but no lessons with IDs"
                )
                return False
            
            print(f"Using lesson ID: {current_lesson_id} ({'quiz lesson' if quiz_lesson_id else 'regular lesson'})")
            
            # Test realistic quiz submission data
            quiz_submission_data = {
                "progress": 100.0,  # Quiz completed
                "currentLessonId": current_lesson_id,
                "timeSpent": 180  # 3 minutes spent on quiz
            }
            
            print(f"\n📤 SUBMITTING QUIZ DATA:")
            print(f"   Progress: {quiz_submission_data['progress']}%")
            print(f"   Current Lesson ID: {quiz_submission_data['currentLessonId']}")
            print(f"   Time Spent: {quiz_submission_data['timeSpent']} seconds")
            
            response = requests.put(
                f"{BACKEND_URL}/enrollments/{self.target_course_id}/progress",
                json=quiz_submission_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["student"]}'
                }
            )
            
            print(f"\n📥 RESPONSE:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Text: {response.text}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    self.log_result(
                        "Quiz Submission with Real Data", 
                        "PASS", 
                        "✅ Quiz submission successful - 422 error resolved!",
                        f"Updated progress: {response_data.get('progress', 'unknown')}%, Status: {response_data.get('status', 'unknown')}"
                    )
                    
                    print(f"\n🎉 SUCCESS! Quiz submission worked:")
                    print(f"   Updated Progress: {response_data.get('progress', 'unknown')}%")
                    print(f"   Enrollment Status: {response_data.get('status', 'unknown')}")
                    print(f"   Last Accessed: {response_data.get('lastAccessedAt', 'unknown')}")
                    
                    return True
                except:
                    self.log_result(
                        "Quiz Submission with Real Data", 
                        "PASS", 
                        "✅ Quiz submission successful (200 OK) but response not JSON",
                        f"Status: 200, Response: {response.text[:100]}"
                    )
                    return True
                    
            elif response.status_code == 422:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'Unknown validation error')
                    
                    self.log_result(
                        "Quiz Submission with Real Data", 
                        "FAIL", 
                        f"❌ 422 VALIDATION ERROR - Same issue as reported by user",
                        f"Error details: {error_detail}"
                    )
                    
                    print(f"\n🚨 422 VALIDATION ERROR DETAILS:")
                    print(f"   Error: {error_detail}")
                    print(f"   Full response: {response.text}")
                    
                    # This is the exact issue reported by the user
                    return False
                except:
                    self.log_result(
                        "Quiz Submission with Real Data", 
                        "FAIL", 
                        f"❌ 422 ERROR - Cannot parse error details",
                        f"Status: 422, Response: {response.text}"
                    )
                    return False
            else:
                self.log_result(
                    "Quiz Submission with Real Data", 
                    "FAIL", 
                    f"❌ Unexpected status code: {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Quiz Submission with Real Data", 
                "FAIL", 
                "Failed to connect to progress update endpoint",
                str(e)
            )
            return False
    
    def test_enrollment_progress_model_validation(self):
        """Test what the EnrollmentProgressUpdate model expects vs what we're sending"""
        print("\n🔍 TESTING ENROLLMENT PROGRESS MODEL VALIDATION")
        print("=" * 60)
        
        if not self.target_course_id or "student" not in self.auth_tokens:
            self.log_result(
                "Enrollment Progress Model Validation", 
                "SKIP", 
                "Target course not found or student not authenticated",
                "Prerequisites not met"
            )
            return False
        
        # Test various field combinations to understand the model
        validation_tests = [
            {
                "name": "Minimal Valid Data",
                "data": {"progress": 25.0}
            },
            {
                "name": "With Module Progress",
                "data": {
                    "progress": 50.0,
                    "currentModuleId": "test-module-id",
                    "currentLessonId": "test-lesson-id"
                }
            },
            {
                "name": "With Time Tracking",
                "data": {
                    "progress": 75.0,
                    "currentLessonId": "test-lesson-id",
                    "timeSpent": 240,
                    "lastAccessedAt": datetime.utcnow().isoformat()
                }
            },
            {
                "name": "Complete Progress Data",
                "data": {
                    "progress": 100.0,
                    "currentModuleId": "test-module-id",
                    "currentLessonId": "test-lesson-id",
                    "timeSpent": 300,
                    "lastAccessedAt": datetime.utcnow().isoformat(),
                    "moduleProgress": []
                }
            }
        ]
        
        validation_results = []
        
        for test in validation_tests:
            print(f"\n🧪 Testing: {test['name']}")
            
            try:
                response = requests.put(
                    f"{BACKEND_URL}/enrollments/{self.target_course_id}/progress",
                    json=test['data'],
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["student"]}'
                    }
                )
                
                status_code = response.status_code
                
                if status_code == 200:
                    print(f"   ✅ SUCCESS: {test['name']}")
                    validation_results.append(f"✅ {test['name']}: SUCCESS")
                elif status_code == 422:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('detail', 'Unknown validation error')
                        print(f"   ❌ VALIDATION ERROR: {error_msg}")
                        validation_results.append(f"❌ {test['name']}: {error_msg}")
                    except:
                        print(f"   ❌ VALIDATION ERROR: Cannot parse error")
                        validation_results.append(f"❌ {test['name']}: Unparseable 422 error")
                else:
                    print(f"   ⚠️ UNEXPECTED: Status {status_code}")
                    validation_results.append(f"⚠️ {test['name']}: Status {status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ CONNECTION ERROR: {str(e)}")
                validation_results.append(f"❌ {test['name']}: Connection error")
        
        # Summary
        successful_validations = [r for r in validation_results if r.startswith('✅')]
        failed_validations = [r for r in validation_results if r.startswith('❌')]
        
        if len(successful_validations) > 0:
            self.log_result(
                "Enrollment Progress Model Validation", 
                "PASS", 
                f"✅ Found {len(successful_validations)} working data formats",
                f"Working formats: {'; '.join(successful_validations)}"
            )
        else:
            self.log_result(
                "Enrollment Progress Model Validation", 
                "FAIL", 
                f"❌ No data formats worked - all {len(failed_validations)} tests failed",
                f"All failures: {'; '.join(failed_validations)}"
            )
        
        return len(successful_validations) > 0
    
    def run_all_tests(self):
        """Run all quiz submission tests"""
        print("🚨 URGENT: QUIZ SUBMISSION API DEBUGGING")
        print("=" * 80)
        print("User Issue: Quiz starts successfully but submission fails with 422 error")
        print("Target: PUT /api/enrollments/{course_id}/progress endpoint")
        print("Credentials: brayden.student@learningfwiend.com / Cove1234!")
        print("Course: 'ttttt'")
        print("=" * 80)
        
        # Test sequence
        tests = [
            self.test_student_authentication,
            self.find_target_course,
            self.check_student_enrollment,
            self.test_progress_update_endpoint_structure,
            self.test_enrollment_progress_model_validation,
            self.test_quiz_submission_with_real_data
        ]
        
        for test in tests:
            try:
                result = test()
                if not result and test.__name__ in ['test_student_authentication', 'find_target_course']:
                    print(f"\n⚠️ Critical test failed: {test.__name__}")
                    print("Cannot continue with remaining tests")
                    break
            except Exception as e:
                print(f"\n❌ Test {test.__name__} crashed: {str(e)}")
                self.log_result(
                    test.__name__, 
                    "FAIL", 
                    f"Test crashed with exception: {str(e)}",
                    "Unexpected error during test execution"
                )
        
        # Final summary
        print(f"\n📊 QUIZ SUBMISSION DEBUGGING SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%" if (self.passed + self.failed) > 0 else "No tests completed")
        
        if self.failed > 0:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        return self.passed, self.failed

if __name__ == "__main__":
    tester = QuizSubmissionTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)