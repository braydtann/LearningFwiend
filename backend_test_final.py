#!/usr/bin/env python3
"""
Final Comprehensive Backend API Testing Suite - All Priority APIs with Correct Models
"""

import requests
import json
import uuid
from datetime import datetime, timedelta

BACKEND_URL = "https://learningfwiend-fix.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

class FinalBackendTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        self.test_data = {}
        
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
        elif status == 'FAIL':
            self.failed += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
        else:
            print(f"ℹ️  {test_name}: {message}")
            if details:
                print(f"   Details: {details}")

    def setup_authentication(self):
        """Setup authentication tokens"""
        test_users = [
            {"username": "admin", "password": "NewAdmin123!", "role": "admin"},
            {"username": "test.instructor", "password": "NewInstructor123!", "role": "instructor"},
            {"username": "student", "password": "NewStudent123!", "role": "learner"}
        ]
        
        for user in test_users:
            try:
                login_data = {
                    "username_or_email": user["username"],
                    "password": user["password"]
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json=login_data,
                    timeout=TEST_TIMEOUT,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get('access_token')
                    if token:
                        self.auth_tokens[user["role"]] = token
                        
            except requests.exceptions.RequestException:
                pass
        
        return len(self.auth_tokens) >= 2

    def get_test_student_id(self):
        """Get a test student ID for certificate testing"""
        admin_token = self.auth_tokens.get("admin")
        if not admin_token:
            return None
            
        try:
            response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 200:
                users = response.json()
                for user in users:
                    if user.get('role') == 'learner':
                        return user.get('id')
                        
        except requests.exceptions.RequestException:
            pass
            
        return None

    def get_test_course_id(self):
        """Get a test course ID"""
        admin_token = self.auth_tokens.get("admin")
        if not admin_token:
            return None
            
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                if courses:
                    return courses[0].get('id')
                    
        except requests.exceptions.RequestException:
            pass
            
        return None

    def test_announcements_api_comprehensive(self):
        """Test Announcements API with correct models"""
        print("\n" + "="*80)
        print("📢 PRIORITY 2: ANNOUNCEMENTS API COMPREHENSIVE TESTING")
        print("="*80)
        
        admin_token = self.auth_tokens.get("admin")
        instructor_token = self.auth_tokens.get("instructor")
        learner_token = self.auth_tokens.get("learner")
        
        if not admin_token:
            self.log_result("Announcements API", "SKIP", "No admin token available", "Cannot test without authentication")
            return
        
        # Test 1: Create Announcement (Admin)
        announcement_data = {
            "title": f"Test Announcement {uuid.uuid4().hex[:8]}",
            "content": "This is a comprehensive test announcement for API testing with detailed content and formatting.",
            "type": "general",
            "targetAudience": "all",
            "priority": "normal",
            "attachments": []
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/announcements",
                json=announcement_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {admin_token}'
                }
            )
            
            if response.status_code == 200:
                created_announcement = response.json()
                announcement_id = created_announcement.get('id')
                self.test_data['announcement_id'] = announcement_id
                
                self.log_result(
                    "Announcements API - Create (Admin)", 
                    "PASS", 
                    "Successfully created announcement as admin",
                    f"Announcement ID: {announcement_id}, Title: {created_announcement.get('title')}, Priority: {created_announcement.get('priority')}"
                )
            else:
                self.log_result(
                    "Announcements API - Create (Admin)", 
                    "FAIL", 
                    f"Failed to create announcement, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                return
                
        except requests.exceptions.RequestException as e:
            self.log_result("Announcements API - Create (Admin)", "FAIL", "Request failed", str(e))
            return
        
        # Test 2: Get All Announcements
        try:
            response = requests.get(
                f"{BACKEND_URL}/announcements",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {learner_token or admin_token}'}
            )
            
            if response.status_code == 200:
                announcements = response.json()
                if isinstance(announcements, list):
                    self.log_result(
                        "Announcements API - Get All", 
                        "PASS", 
                        f"Successfully retrieved {len(announcements)} announcements",
                        f"Announcements include role-based filtering and metadata"
                    )
                else:
                    self.log_result(
                        "Announcements API - Get All", 
                        "FAIL", 
                        "Response is not a list",
                        f"Response type: {type(announcements)}"
                    )
            else:
                self.log_result(
                    "Announcements API - Get All", 
                    "FAIL", 
                    f"Failed to get announcements, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Announcements API - Get All", "FAIL", "Request failed", str(e))
        
        # Test 3: Get My Announcements (Instructor)
        if instructor_token:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/announcements/my-announcements",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {instructor_token}'}
                )
                
                if response.status_code == 200:
                    my_announcements = response.json()
                    self.log_result(
                        "Announcements API - Get My Announcements", 
                        "PASS", 
                        f"Successfully retrieved {len(my_announcements)} instructor announcements",
                        "Role-based announcement filtering working"
                    )
                else:
                    self.log_result(
                        "Announcements API - Get My Announcements", 
                        "FAIL", 
                        f"Failed to get instructor announcements, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Announcements API - Get My Announcements", "FAIL", "Request failed", str(e))
        
        # Test 4: Update Announcement
        if 'announcement_id' in self.test_data:
            update_data = {
                "title": f"Updated Announcement {uuid.uuid4().hex[:8]}",
                "content": "Updated content for comprehensive testing",
                "priority": "high",
                "isPinned": True
            }
            
            try:
                response = requests.put(
                    f"{BACKEND_URL}/announcements/{self.test_data['announcement_id']}",
                    json=update_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {admin_token}'
                    }
                )
                
                if response.status_code == 200:
                    updated_announcement = response.json()
                    self.log_result(
                        "Announcements API - Update", 
                        "PASS", 
                        "Successfully updated announcement",
                        f"New title: {updated_announcement.get('title')}, Pinned: {updated_announcement.get('isPinned')}"
                    )
                else:
                    self.log_result(
                        "Announcements API - Update", 
                        "FAIL", 
                        f"Failed to update announcement, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Announcements API - Update", "FAIL", "Request failed", str(e))

    def test_certificates_api_comprehensive(self):
        """Test Certificates API with correct models"""
        print("\n" + "="*80)
        print("🏆 PRIORITY 2: CERTIFICATES API COMPREHENSIVE TESTING")
        print("="*80)
        
        admin_token = self.auth_tokens.get("admin")
        
        if not admin_token:
            self.log_result("Certificates API", "SKIP", "No admin token available", "Cannot test without authentication")
            return
        
        # Get test data
        test_student_id = self.get_test_student_id()
        test_course_id = self.get_test_course_id()
        
        if not test_student_id:
            self.log_result("Certificates API", "SKIP", "No test student available", "Cannot test without student")
            return
        
        # Test 1: Create Certificate (Course Completion)
        certificate_data = {
            "studentId": test_student_id,
            "courseId": test_course_id,
            "type": "completion",
            "template": "default"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/certificates",
                json=certificate_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {admin_token}'
                }
            )
            
            if response.status_code == 200:
                created_certificate = response.json()
                certificate_id = created_certificate.get('id')
                self.test_data['certificate_id'] = certificate_id
                
                self.log_result(
                    "Certificates API - Create (Course)", 
                    "PASS", 
                    "Successfully created course completion certificate",
                    f"Certificate ID: {certificate_id}, Number: {created_certificate.get('certificateNumber')}, Type: {created_certificate.get('type')}"
                )
            else:
                self.log_result(
                    "Certificates API - Create (Course)", 
                    "FAIL", 
                    f"Failed to create certificate, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                return
                
        except requests.exceptions.RequestException as e:
            self.log_result("Certificates API - Create (Course)", "FAIL", "Request failed", str(e))
            return
        
        # Test 2: Get All Certificates
        try:
            response = requests.get(
                f"{BACKEND_URL}/certificates",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 200:
                certificates = response.json()
                if isinstance(certificates, list):
                    self.log_result(
                        "Certificates API - Get All", 
                        "PASS", 
                        f"Successfully retrieved {len(certificates)} certificates",
                        f"Certificates include verification data and metadata"
                    )
                else:
                    self.log_result(
                        "Certificates API - Get All", 
                        "FAIL", 
                        "Response is not a list",
                        f"Response type: {type(certificates)}"
                    )
            else:
                self.log_result(
                    "Certificates API - Get All", 
                    "FAIL", 
                    f"Failed to get certificates, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Certificates API - Get All", "FAIL", "Request failed", str(e))
        
        # Test 3: Verify Certificate
        if 'certificate_id' in self.test_data:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/certificates/{self.test_data['certificate_id']}/verify",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {admin_token}'}
                )
                
                if response.status_code == 200:
                    verification = response.json()
                    self.log_result(
                        "Certificates API - Verify", 
                        "PASS", 
                        "Successfully verified certificate",
                        f"Valid: {verification.get('isValid')}, Student: {verification.get('studentName')}"
                    )
                else:
                    self.log_result(
                        "Certificates API - Verify", 
                        "FAIL", 
                        f"Failed to verify certificate, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Certificates API - Verify", "FAIL", "Request failed", str(e))

    def test_quizzes_api_comprehensive(self):
        """Test Quiz/Assessment API with correct models"""
        print("\n" + "="*80)
        print("📝 PRIORITY 3: QUIZ/ASSESSMENT API COMPREHENSIVE TESTING")
        print("="*80)
        
        instructor_token = self.auth_tokens.get("instructor")
        learner_token = self.auth_tokens.get("learner")
        
        if not instructor_token:
            self.log_result("Quiz/Assessment API", "SKIP", "No instructor token available", "Cannot test without authentication")
            return
        
        # Get test course ID
        test_course_id = self.get_test_course_id()
        
        # Test 1: Create Quiz
        quiz_data = {
            "title": f"Comprehensive Test Quiz {uuid.uuid4().hex[:8]}",
            "description": "This is a comprehensive test quiz for API testing with multiple question types",
            "courseId": test_course_id,
            "timeLimit": 30,
            "passingScore": 70.0,
            "maxAttempts": 3,
            "shuffleQuestions": True,
            "showResults": True,
            "questions": [
                {
                    "type": "multiple_choice",
                    "question": "What is the capital of France?",
                    "options": ["London", "Berlin", "Paris", "Madrid"],
                    "correctAnswer": "Paris",
                    "points": 10,
                    "explanation": "Paris is the capital and largest city of France."
                },
                {
                    "type": "true_false",
                    "question": "Python is a programming language.",
                    "correctAnswer": "true",
                    "points": 5,
                    "explanation": "Python is indeed a popular programming language."
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/quizzes",
                json=quiz_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {instructor_token}'
                }
            )
            
            if response.status_code == 200:
                created_quiz = response.json()
                quiz_id = created_quiz.get('id')
                self.test_data['quiz_id'] = quiz_id
                
                self.log_result(
                    "Quiz/Assessment API - Create", 
                    "PASS", 
                    "Successfully created quiz as instructor",
                    f"Quiz ID: {quiz_id}, Title: {created_quiz.get('title')}, Questions: {len(created_quiz.get('questions', []))}"
                )
            else:
                self.log_result(
                    "Quiz/Assessment API - Create", 
                    "FAIL", 
                    f"Failed to create quiz, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                return
                
        except requests.exceptions.RequestException as e:
            self.log_result("Quiz/Assessment API - Create", "FAIL", "Request failed", str(e))
            return
        
        # Test 2: Get All Quizzes
        try:
            response = requests.get(
                f"{BACKEND_URL}/quizzes",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {instructor_token}'}
            )
            
            if response.status_code == 200:
                quizzes = response.json()
                if isinstance(quizzes, list):
                    self.log_result(
                        "Quiz/Assessment API - Get All", 
                        "PASS", 
                        f"Successfully retrieved {len(quizzes)} quizzes",
                        f"Quizzes include question counts and metadata"
                    )
                else:
                    self.log_result(
                        "Quiz/Assessment API - Get All", 
                        "FAIL", 
                        "Response is not a list",
                        f"Response type: {type(quizzes)}"
                    )
            else:
                self.log_result(
                    "Quiz/Assessment API - Get All", 
                    "FAIL", 
                    f"Failed to get quizzes, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Quiz/Assessment API - Get All", "FAIL", "Request failed", str(e))
        
        # Test 3: Submit Quiz Attempt (Learner)
        if learner_token and 'quiz_id' in self.test_data:
            attempt_data = {
                "answers": [
                    {
                        "questionId": "q1",
                        "answer": "Paris"
                    },
                    {
                        "questionId": "q2", 
                        "answer": "true"
                    }
                ],
                "timeSpent": 15
            }
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/quizzes/{self.test_data['quiz_id']}/attempts",
                    json=attempt_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {learner_token}'
                    }
                )
                
                if response.status_code == 200:
                    attempt_result = response.json()
                    self.log_result(
                        "Quiz/Assessment API - Submit Attempt", 
                        "PASS", 
                        "Successfully submitted quiz attempt",
                        f"Score: {attempt_result.get('score')}, Passed: {attempt_result.get('passed')}"
                    )
                else:
                    self.log_result(
                        "Quiz/Assessment API - Submit Attempt", 
                        "FAIL", 
                        f"Failed to submit attempt, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Quiz/Assessment API - Submit Attempt", "FAIL", "Request failed", str(e))

    def test_analytics_api_comprehensive(self):
        """Test Analytics API - System stats, course analytics, user analytics"""
        print("\n" + "="*80)
        print("📊 PRIORITY 3: ANALYTICS API COMPREHENSIVE TESTING")
        print("="*80)
        
        admin_token = self.auth_tokens.get("admin")
        
        if not admin_token:
            self.log_result("Analytics API", "SKIP", "No admin token available", "Cannot test without authentication")
            return
        
        # Test 1: System Statistics
        try:
            response = requests.get(
                f"{BACKEND_URL}/analytics/system-stats",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 200:
                stats = response.json()
                self.log_result(
                    "Analytics API - System Stats", 
                    "PASS", 
                    "Successfully retrieved system statistics",
                    f"Users: {stats.get('totalUsers')}, Courses: {stats.get('totalCourses')}, Enrollments: {stats.get('totalEnrollments')}"
                )
            else:
                self.log_result(
                    "Analytics API - System Stats", 
                    "FAIL", 
                    f"Failed to get system stats, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Analytics API - System Stats", "FAIL", "Request failed", str(e))
        
        # Test 2: Course Analytics
        test_course_id = self.get_test_course_id()
        if test_course_id:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/analytics/courses/{test_course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {admin_token}'}
                )
                
                if response.status_code == 200:
                    course_analytics = response.json()
                    self.log_result(
                        "Analytics API - Course Analytics", 
                        "PASS", 
                        "Successfully retrieved course analytics",
                        f"Enrollments: {course_analytics.get('enrollmentCount')}, Completion Rate: {course_analytics.get('completionRate')}"
                    )
                else:
                    self.log_result(
                        "Analytics API - Course Analytics", 
                        "FAIL", 
                        f"Failed to get course analytics, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_result("Analytics API - Course Analytics", "FAIL", "Request failed", str(e))
        
        # Test 3: User Analytics
        try:
            response = requests.get(
                f"{BACKEND_URL}/analytics/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 200:
                user_analytics = response.json()
                self.log_result(
                    "Analytics API - User Analytics", 
                    "PASS", 
                    "Successfully retrieved user analytics",
                    f"Active Users: {user_analytics.get('activeUsers')}, New Registrations: {user_analytics.get('newRegistrations')}"
                )
            else:
                self.log_result(
                    "Analytics API - User Analytics", 
                    "FAIL", 
                    f"Failed to get user analytics, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Analytics API - User Analytics", "FAIL", "Request failed", str(e))

    def test_performance_and_edge_cases(self):
        """Test Performance & Edge Cases"""
        print("\n" + "="*80)
        print("⚡ PERFORMANCE & EDGE CASES TESTING")
        print("="*80)
        
        admin_token = self.auth_tokens.get("admin")
        
        if not admin_token:
            self.log_result("Performance Testing", "SKIP", "No admin token available", "Cannot test without authentication")
            return
        
        # Test 1: Large Data Volume (Get all courses)
        try:
            start_time = datetime.now()
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            
            if response.status_code == 200:
                courses = response.json()
                self.log_result(
                    "Performance - Large Data Volume", 
                    "PASS", 
                    f"Retrieved {len(courses)} courses in {response_time:.2f} seconds",
                    f"Response time acceptable for production use"
                )
            else:
                self.log_result(
                    "Performance - Large Data Volume", 
                    "FAIL", 
                    f"Failed to retrieve courses, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Performance - Large Data Volume", "FAIL", "Request failed", str(e))
        
        # Test 2: Error Handling - Invalid Data
        try:
            invalid_course_data = {
                "title": "",  # Invalid empty title
                "description": "Test",
                "category": "Test"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=invalid_course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {admin_token}'
                }
            )
            
            if response.status_code == 422:
                self.log_result(
                    "Error Handling - Invalid Data", 
                    "PASS", 
                    "Correctly rejected invalid course data with validation error",
                    f"Proper validation error response"
                )
            else:
                self.log_result(
                    "Error Handling - Invalid Data", 
                    "FAIL", 
                    f"Should have rejected invalid data, got status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Error Handling - Invalid Data", "FAIL", "Request failed", str(e))
        
        # Test 3: Authentication Edge Case - Invalid Token
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': 'Bearer invalid-token-12345'}
            )
            
            if response.status_code == 401:
                self.log_result(
                    "Authentication - Invalid Token", 
                    "PASS", 
                    "Correctly rejected invalid authentication token",
                    f"Proper authentication error handling"
                )
            else:
                self.log_result(
                    "Authentication - Invalid Token", 
                    "FAIL", 
                    f"Should have rejected invalid token, got status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Authentication - Invalid Token", "FAIL", "Request failed", str(e))

    def run_final_comprehensive_tests(self):
        """Run all final comprehensive tests"""
        print("\n" + "="*100)
        print("🚀 FINAL COMPREHENSIVE BACKEND API TESTING - ALL PRIORITIES")
        print("="*100)
        
        if not self.setup_authentication():
            print("\n❌ CRITICAL: Authentication setup failed. Cannot proceed with API testing.")
            return False
        
        print(f"\n✅ Authentication successful for {len(self.auth_tokens)} user types")
        
        # Priority 2 Tests - Content & Communication
        self.test_announcements_api_comprehensive()
        self.test_certificates_api_comprehensive()
        
        # Priority 3 Tests - Assessment & Analytics
        self.test_quizzes_api_comprehensive()
        self.test_analytics_api_comprehensive()
        
        # Performance & Edge Cases
        self.test_performance_and_edge_cases()
        
        # Print final summary
        self.print_final_summary()
        
        return self.passed > self.failed
    
    def print_final_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*100)
        print("📊 FINAL COMPREHENSIVE BACKEND API TESTING SUMMARY")
        print("="*100)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ PASSED: {self.passed}")
        print(f"❌ FAILED: {self.failed}")
        print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
        print(f"🔢 TOTAL TESTS: {total_tests}")
        
        if self.failed > 0:
            print(f"\n❌ FAILED TESTS SUMMARY:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['message']}")
        
        print("\n" + "="*100)
        
        if success_rate >= 80:
            print("🎉 OVERALL RESULT: BACKEND APIs are production-ready!")
        elif success_rate >= 60:
            print("⚠️  OVERALL RESULT: Backend APIs need some fixes before production")
        else:
            print("🚨 OVERALL RESULT: Critical issues found - backend needs significant work")
        
        print("="*100)

def main():
    """Main function"""
    tester = FinalBackendTester()
    tester.run_final_comprehensive_tests()

if __name__ == "__main__":
    main()