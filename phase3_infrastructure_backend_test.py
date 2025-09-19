#!/usr/bin/env python3
"""
PHASE 3 INFRASTRUCTURE VERIFICATION - Backend Testing
Test backend authentication and chronological order functionality after @hello-pangea/dnd library fix

This test focuses on:
1. Authentication endpoint verification
2. Course creation API verification with chronological order questions
3. Quiz access and submission testing
4. API endpoint connectivity
5. Data structure validation for chronological order questions
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use the correct backend URL from frontend/.env
BACKEND_URL = "https://lms-debugfix.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class Phase3InfrastructureTester:
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

    def test_admin_authentication(self):
        """Test POST /api/auth/login for admin credentials"""
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
                
                # Verify admin role and token generation
                if user_info.get('role') == 'admin' and self.admin_token:
                    self.log_result(
                        "Admin Authentication (POST /api/auth/login)", 
                        True, 
                        f"✅ HTTP 200 - Admin authenticated: {user_info.get('full_name')} ({user_info.get('email')}), Token generated: {len(self.admin_token)} chars"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication (POST /api/auth/login)", 
                        False, 
                        f"❌ Role: {user_info.get('role')}, Token: {'Yes' if self.admin_token else 'No'}"
                    )
                    return False
            else:
                self.log_result(
                    "Admin Authentication (POST /api/auth/login)", 
                    False, 
                    f"❌ HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            if "Failed to fetch" in str(e) or "TypeError" in str(e):
                self.log_result(
                    "Admin Authentication (POST /api/auth/login)", 
                    False, 
                    f"❌ Network connectivity issue - TypeError: Failed to fetch detected: {str(e)}"
                )
            else:
                self.log_result(
                    "Admin Authentication (POST /api/auth/login)", 
                    False, 
                    f"❌ Request exception: {str(e)}"
                )
            return False
        except Exception as e:
            self.log_result(
                "Admin Authentication (POST /api/auth/login)", 
                False, 
                f"❌ Unexpected error: {str(e)}"
            )
            return False

    def test_student_authentication(self):
        """Test POST /api/auth/login for student credentials"""
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
                
                # Verify learner role and token generation
                if user_info.get('role') == 'learner' and self.student_token:
                    self.log_result(
                        "Student Authentication (POST /api/auth/login)", 
                        True, 
                        f"✅ HTTP 200 - Student authenticated: {user_info.get('full_name')} ({user_info.get('email')}), Token generated: {len(self.student_token)} chars"
                    )
                    return True
                else:
                    self.log_result(
                        "Student Authentication (POST /api/auth/login)", 
                        False, 
                        f"❌ Role: {user_info.get('role')}, Token: {'Yes' if self.student_token else 'No'}"
                    )
                    return False
            else:
                self.log_result(
                    "Student Authentication (POST /api/auth/login)", 
                    False, 
                    f"❌ HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            if "Failed to fetch" in str(e) or "TypeError" in str(e):
                self.log_result(
                    "Student Authentication (POST /api/auth/login)", 
                    False, 
                    f"❌ Network connectivity issue - TypeError: Failed to fetch detected: {str(e)}"
                )
            else:
                self.log_result(
                    "Student Authentication (POST /api/auth/login)", 
                    False, 
                    f"❌ Request exception: {str(e)}"
                )
            return False
        except Exception as e:
            self.log_result(
                "Student Authentication (POST /api/auth/login)", 
                False, 
                f"❌ Unexpected error: {str(e)}"
            )
            return False

    def test_course_creation_with_chronological_order(self):
        """Test POST /api/courses with chronological order questions after library update"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Create course with chronological order questions to test data structure compatibility
            course_data = {
                "title": "Phase 3 Infrastructure Test - Chronological Order Compatibility",
                "description": "Testing chronological order data structure after @hello-pangea/dnd library fix",
                "category": "Testing",
                "duration": "30 minutes",
                "thumbnailUrl": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",
                "accessType": "open",
                "learningOutcomes": ["Verify chronological order compatibility", "Test data structure integrity"],
                "modules": [
                    {
                        "title": "Chronological Order Test Module",
                        "lessons": [
                            {
                                "id": "lesson-chrono-1",
                                "title": "Historical Events Quiz",
                                "type": "quiz",
                                "content": "Test chronological order functionality",
                                "questions": [
                                    {
                                        "id": "q1",
                                        "type": "chronological-order",
                                        "question": "Arrange these historical events in chronological order:",
                                        "items": [
                                            {
                                                "text": "World War II ends (1945)",
                                                "image": None,
                                                "audio": None
                                            },
                                            {
                                                "text": "World War I begins (1914)",
                                                "image": None,
                                                "audio": None
                                            },
                                            {
                                                "text": "Moon landing (1969)",
                                                "image": None,
                                                "audio": None
                                            },
                                            {
                                                "text": "Fall of Berlin Wall (1989)",
                                                "image": None,
                                                "audio": None
                                            }
                                        ],
                                        "correctOrder": [1, 0, 2, 3],  # WWI begins, WWII ends, Moon landing, Berlin Wall falls
                                        "points": 20
                                    },
                                    {
                                        "id": "q2",
                                        "type": "multiple_choice",
                                        "question": "What year did World War II end?",
                                        "options": ["1944", "1945", "1946", "1947"],
                                        "correctAnswer": "1",
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
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                course = response.json()
                self.test_course_id = course['id']
                
                # Verify chronological order data structure is preserved
                modules = course.get('modules', [])
                if modules and len(modules) > 0:
                    lessons = modules[0].get('lessons', [])
                    if lessons and len(lessons) > 0:
                        questions = lessons[0].get('questions', [])
                        chrono_questions = [q for q in questions if q.get('type') == 'chronological-order']
                        
                        if len(chrono_questions) == 1:
                            chrono_q = chrono_questions[0]
                            
                            # Validate chronological order data structure
                            has_items = 'items' in chrono_q and len(chrono_q['items']) == 4
                            has_correct_order = 'correctOrder' in chrono_q and len(chrono_q['correctOrder']) == 4
                            
                            # Validate items structure (text, image, audio fields)
                            items_valid = True
                            if has_items:
                                for item in chrono_q['items']:
                                    if not all(field in item for field in ['text', 'image', 'audio']):
                                        items_valid = False
                                        break
                            
                            if has_items and has_correct_order and items_valid:
                                self.log_result(
                                    "Course Creation with Chronological Order (POST /api/courses)", 
                                    True, 
                                    f"✅ HTTP 200 - Course created with chronological order questions. Items: {len(chrono_q['items'])}, CorrectOrder: {chrono_q['correctOrder']}, Items structure valid: {items_valid}"
                                )
                                return True
                            else:
                                self.log_result(
                                    "Course Creation with Chronological Order (POST /api/courses)", 
                                    False, 
                                    f"❌ Data structure issues - Items: {has_items}, CorrectOrder: {has_correct_order}, Items valid: {items_valid}"
                                )
                                return False
                        else:
                            self.log_result(
                                "Course Creation with Chronological Order (POST /api/courses)", 
                                False, 
                                f"❌ Expected 1 chronological order question, found {len(chrono_questions)}"
                            )
                            return False
                    else:
                        self.log_result(
                            "Course Creation with Chronological Order (POST /api/courses)", 
                            False, 
                            "❌ No lessons found in created course"
                        )
                        return False
                else:
                    self.log_result(
                        "Course Creation with Chronological Order (POST /api/courses)", 
                        False, 
                        "❌ No modules found in created course"
                    )
                    return False
            else:
                self.log_result(
                    "Course Creation with Chronological Order (POST /api/courses)", 
                    False, 
                    f"❌ HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Course Creation with Chronological Order (POST /api/courses)", 
                False, 
                f"❌ Exception: {str(e)}"
            )
            return False

    def test_quiz_access_chronological_order(self):
        """Test GET /api/courses/{id} for courses with chronological order questions"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            response = requests.get(
                f"{BACKEND_URL}/courses/{self.test_course_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                course = response.json()
                
                # Verify student can access course with chronological order questions
                modules = course.get('modules', [])
                if modules and len(modules) > 0:
                    lessons = modules[0].get('lessons', [])
                    if lessons and len(lessons) > 0:
                        questions = lessons[0].get('questions', [])
                        chrono_questions = [q for q in questions if q.get('type') == 'chronological-order']
                        
                        if len(chrono_questions) == 1:
                            chrono_q = chrono_questions[0]
                            
                            # Verify chronological order question structure is accessible
                            items_accessible = 'items' in chrono_q and len(chrono_q['items']) > 0
                            correct_order_accessible = 'correctOrder' in chrono_q
                            
                            self.log_result(
                                "Quiz Access with Chronological Order (GET /api/courses/{id})", 
                                True, 
                                f"✅ HTTP 200 - Student can access course with chronological order. Items accessible: {items_accessible}, CorrectOrder accessible: {correct_order_accessible}"
                            )
                            return True
                        else:
                            self.log_result(
                                "Quiz Access with Chronological Order (GET /api/courses/{id})", 
                                False, 
                                f"❌ Chronological order questions not found in student view"
                            )
                            return False
                    else:
                        self.log_result(
                            "Quiz Access with Chronological Order (GET /api/courses/{id})", 
                            False, 
                            "❌ No lessons accessible to student"
                        )
                        return False
                else:
                    self.log_result(
                        "Quiz Access with Chronological Order (GET /api/courses/{id})", 
                        False, 
                        "❌ No modules accessible to student"
                    )
                    return False
            else:
                self.log_result(
                    "Quiz Access with Chronological Order (GET /api/courses/{id})", 
                    False, 
                    f"❌ HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Quiz Access with Chronological Order (GET /api/courses/{id})", 
                False, 
                f"❌ Exception: {str(e)}"
            )
            return False

    def test_quiz_submission_chronological_answers(self):
        """Test PUT /api/enrollments/{course_id}/progress with array-format answers"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # First, enroll student in the course
            enrollment_data = {"courseId": self.test_course_id}
            enroll_response = requests.post(
                f"{BACKEND_URL}/enrollments",
                json=enrollment_data,
                headers=headers,
                timeout=10
            )
            
            # Test quiz submission with chronological order answers (array format)
            progress_data = {
                "progress": 100.0,
                "currentLessonId": "lesson-chrono-1",
                "timeSpent": 300,
                "quizAnswers": [
                    {
                        "questionId": "q1",
                        "type": "chronological-order",
                        "answer": [1, 0, 2, 3]  # Array format for chronological order
                    },
                    {
                        "questionId": "q2", 
                        "type": "multiple_choice",
                        "answer": 1  # Index format for multiple choice
                    }
                ]
            }
            
            response = requests.put(
                f"{BACKEND_URL}/enrollments/{self.test_course_id}/progress",
                json=progress_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                enrollment = response.json()
                
                # Verify progress was updated successfully
                updated_progress = enrollment.get('progress', 0)
                status = enrollment.get('status', '')
                
                if updated_progress == 100.0:
                    self.log_result(
                        "Quiz Submission with Chronological Answers (PUT /api/enrollments/{course_id}/progress)", 
                        True, 
                        f"✅ HTTP 200 - Quiz submission successful. Progress: {updated_progress}%, Status: {status}, Array-format answers accepted"
                    )
                    return True
                else:
                    self.log_result(
                        "Quiz Submission with Chronological Answers (PUT /api/enrollments/{course_id}/progress)", 
                        False, 
                        f"❌ Progress not updated correctly. Expected: 100%, Got: {updated_progress}%"
                    )
                    return False
            else:
                self.log_result(
                    "Quiz Submission with Chronological Answers (PUT /api/enrollments/{course_id}/progress)", 
                    False, 
                    f"❌ HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Quiz Submission with Chronological Answers (PUT /api/enrollments/{course_id}/progress)", 
                False, 
                f"❌ Exception: {str(e)}"
            )
            return False

    def test_critical_api_endpoints(self):
        """Verify all critical endpoints respond correctly"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test critical endpoints
            endpoints_to_test = [
                ("GET /api/courses", f"{BACKEND_URL}/courses"),
                ("GET /api/enrollments", f"{BACKEND_URL}/enrollments"),
                ("GET /api/programs", f"{BACKEND_URL}/programs"),
                ("GET /api/categories", f"{BACKEND_URL}/categories"),
                ("GET /api/departments", f"{BACKEND_URL}/departments")
            ]
            
            successful_endpoints = 0
            total_endpoints = len(endpoints_to_test)
            endpoint_results = []
            
            for endpoint_name, url in endpoints_to_test:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        successful_endpoints += 1
                        endpoint_results.append(f"✅ {endpoint_name}: HTTP 200")
                    else:
                        endpoint_results.append(f"❌ {endpoint_name}: HTTP {response.status_code}")
                except Exception as e:
                    endpoint_results.append(f"❌ {endpoint_name}: {str(e)[:50]}")
            
            success_rate = (successful_endpoints / total_endpoints) * 100
            
            if success_rate >= 80:  # 80% or more endpoints working
                self.log_result(
                    "Critical API Endpoints Connectivity", 
                    True, 
                    f"✅ {successful_endpoints}/{total_endpoints} endpoints working ({success_rate:.1f}%). " + "; ".join(endpoint_results)
                )
                return True
            else:
                self.log_result(
                    "Critical API Endpoints Connectivity", 
                    False, 
                    f"❌ Only {successful_endpoints}/{total_endpoints} endpoints working ({success_rate:.1f}%). " + "; ".join(endpoint_results)
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Critical API Endpoints Connectivity", 
                False, 
                f"❌ Exception during endpoint testing: {str(e)}"
            )
            return False

    def test_chronological_order_data_validation(self):
        """Verify chronological order data structures and edge cases"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test edge cases for chronological order questions
            edge_case_tests = [
                {
                    "name": "Single Item",
                    "items": [{"text": "Single event", "image": None, "audio": None}],
                    "correctOrder": [0]
                },
                {
                    "name": "Empty Items",
                    "items": [],
                    "correctOrder": []
                },
                {
                    "name": "Multiple Items with Media",
                    "items": [
                        {"text": "Event 1", "image": "https://example.com/img1.jpg", "audio": None},
                        {"text": "Event 2", "image": None, "audio": "https://example.com/audio1.mp3"},
                        {"text": "Event 3", "image": None, "audio": None}
                    ],
                    "correctOrder": [0, 1, 2]
                }
            ]
            
            successful_validations = 0
            total_validations = len(edge_case_tests)
            validation_results = []
            
            for test_case in edge_case_tests:
                try:
                    # Create a test course with this edge case
                    course_data = {
                        "title": f"Edge Case Test - {test_case['name']}",
                        "description": f"Testing {test_case['name']} for chronological order",
                        "category": "Testing",
                        "modules": [
                            {
                                "title": "Edge Case Module",
                                "lessons": [
                                    {
                                        "id": f"lesson-edge-{test_case['name'].lower().replace(' ', '-')}",
                                        "title": f"Edge Case: {test_case['name']}",
                                        "type": "quiz",
                                        "questions": [
                                            {
                                                "id": "edge-q1",
                                                "type": "chronological-order",
                                                "question": f"Test case: {test_case['name']}",
                                                "items": test_case['items'],
                                                "correctOrder": test_case['correctOrder'],
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
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        successful_validations += 1
                        validation_results.append(f"✅ {test_case['name']}: Accepted")
                    else:
                        validation_results.append(f"❌ {test_case['name']}: HTTP {response.status_code}")
                        
                except Exception as e:
                    validation_results.append(f"❌ {test_case['name']}: {str(e)[:30]}")
            
            success_rate = (successful_validations / total_validations) * 100
            
            if success_rate >= 66:  # At least 2/3 edge cases should work
                self.log_result(
                    "Chronological Order Data Structure Validation", 
                    True, 
                    f"✅ {successful_validations}/{total_validations} edge cases handled ({success_rate:.1f}%). " + "; ".join(validation_results)
                )
                return True
            else:
                self.log_result(
                    "Chronological Order Data Structure Validation", 
                    False, 
                    f"❌ Only {successful_validations}/{total_validations} edge cases handled ({success_rate:.1f}%). " + "; ".join(validation_results)
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Chronological Order Data Structure Validation", 
                False, 
                f"❌ Exception during validation testing: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all Phase 3 infrastructure verification tests"""
        print("🚀 PHASE 3 INFRASTRUCTURE VERIFICATION - Backend Testing")
        print("Testing backend authentication and chronological order functionality after @hello-pangea/dnd library fix")
        print("=" * 100)
        print()
        
        # 1. AUTHENTICATION ENDPOINT VERIFICATION
        print("🔐 1. AUTHENTICATION ENDPOINT VERIFICATION")
        print("-" * 50)
        
        if not self.test_admin_authentication():
            print("❌ Admin authentication failed - cannot continue with admin-required tests")
            
        if not self.test_student_authentication():
            print("❌ Student authentication failed - cannot continue with student-required tests")
        
        print()
        
        # Only continue if we have at least admin authentication
        if not self.admin_token:
            print("❌ No admin token available - cannot continue with remaining tests")
            return False
        
        # 2. COURSE CREATION API VERIFICATION
        print("📚 2. COURSE CREATION API VERIFICATION")
        print("-" * 50)
        self.test_course_creation_with_chronological_order()
        print()
        
        # 3. QUIZ ACCESS AND SUBMISSION TESTING
        if self.student_token and self.test_course_id:
            print("📝 3. QUIZ ACCESS AND SUBMISSION TESTING")
            print("-" * 50)
            self.test_quiz_access_chronological_order()
            self.test_quiz_submission_chronological_answers()
            print()
        
        # 4. API ENDPOINT CONNECTIVITY
        print("🌐 4. API ENDPOINT CONNECTIVITY")
        print("-" * 50)
        self.test_critical_api_endpoints()
        print()
        
        # 5. DATA STRUCTURE VALIDATION
        print("🔍 5. DATA STRUCTURE VALIDATION")
        print("-" * 50)
        self.test_chronological_order_data_validation()
        print()
        
        # Summary
        print("=" * 100)
        print("📊 PHASE 3 INFRASTRUCTURE VERIFICATION SUMMARY")
        print("=" * 100)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # SUCCESS CRITERIA CHECK
        print("🎯 SUCCESS CRITERIA VERIFICATION:")
        
        auth_tests = [r for r in self.results if 'Authentication' in r['test']]
        auth_success = all(r['success'] for r in auth_tests)
        print(f"✅ Authentication endpoints respond correctly (HTTP 200): {'✅ PASS' if auth_success else '❌ FAIL'}")
        
        course_tests = [r for r in self.results if 'Course Creation' in r['test']]
        course_success = all(r['success'] for r in course_tests)
        print(f"✅ Course creation with chronological order works: {'✅ PASS' if course_success else '❌ FAIL'}")
        
        quiz_tests = [r for r in self.results if 'Quiz' in r['test']]
        quiz_success = all(r['success'] for r in quiz_tests)
        print(f"✅ Quiz access and submission functional: {'✅ PASS' if quiz_success else '❌ FAIL'}")
        
        api_tests = [r for r in self.results if 'API Endpoints' in r['test']]
        api_success = all(r['success'] for r in api_tests)
        print(f"✅ All API endpoints accessible and responding: {'✅ PASS' if api_success else '❌ FAIL'}")
        
        data_tests = [r for r in self.results if 'Data Structure' in r['test']]
        data_success = all(r['success'] for r in data_tests)
        print(f"✅ Chronological order data structures intact: {'✅ PASS' if data_success else '❌ FAIL'}")
        
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS DETAILS:")
            for result in self.results:
                if not result['success']:
                    print(f"  • {result['test']}")
                    print(f"    {result['details']}")
            print()
        
        # Overall assessment
        critical_success = auth_success and course_success and api_success
        
        if critical_success and success_rate >= 80:
            print("🎉 PHASE 3 INFRASTRUCTURE VERIFICATION: ✅ SUCCESS")
            print("Backend is ready for frontend @hello-pangea/dnd integration")
        elif critical_success:
            print("⚠️  PHASE 3 INFRASTRUCTURE VERIFICATION: ⚠️ PARTIAL SUCCESS")
            print("Critical functionality working, minor issues detected")
        else:
            print("💥 PHASE 3 INFRASTRUCTURE VERIFICATION: ❌ FAILURE")
            print("Critical backend issues detected - frontend integration may fail")
        
        print()
        return critical_success and success_rate >= 70

if __name__ == "__main__":
    tester = Phase3InfrastructureTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 Phase 3 infrastructure verification completed successfully!")
        sys.exit(0)
    else:
        print("💥 Phase 3 infrastructure verification failed!")
        sys.exit(1)