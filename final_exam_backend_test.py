#!/usr/bin/env python3
"""
Backend Testing Script for Final Exam and Grading System Endpoints
Testing the newly added final exam and grading system functionality
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://coursemate-14.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class FinalExamBackendTester:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        self.created_resources = {
            'final_tests': [],
            'programs': [],
            'courses': []
        }

    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")

    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data['access_token']
                self.log_test("Admin Authentication", True, f"Admin: {data['user']['full_name']}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def authenticate_student(self):
        """Authenticate student user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=STUDENT_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data['access_token']
                self.log_test("Student Authentication", True, f"Student: {data['user']['full_name']}")
                return True
            else:
                self.log_test("Student Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False

    def get_headers(self, token):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def test_create_program_for_final_test(self):
        """Create a test program for final test"""
        try:
            program_data = {
                "title": "Final Exam Test Program",
                "description": "Test program for final exam functionality",
                "departmentId": None,
                "duration": "4 weeks",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            response = requests.post(
                f"{BACKEND_URL}/programs",
                json=program_data,
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code == 200:
                program = response.json()
                self.created_resources['programs'].append(program['id'])
                self.log_test("Create Test Program", True, f"Program ID: {program['id']}")
                return program['id']
            else:
                self.log_test("Create Test Program", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.log_test("Create Test Program", False, f"Exception: {str(e)}")
            return None

    def test_create_final_test(self, program_id):
        """Test POST /api/final-tests endpoint"""
        try:
            final_test_data = {
                "title": "Sample Final Exam",
                "description": "Comprehensive final exam for testing",
                "programId": program_id,
                "timeLimit": 60,
                "passingScore": 75.0,
                "maxAttempts": 2,
                "isPublished": True,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is the capital of France?",
                        "options": ["London", "Berlin", "Paris", "Madrid"],
                        "correctAnswer": "2",
                        "points": 10,
                        "explanation": "Paris is the capital and largest city of France."
                    },
                    {
                        "type": "true_false",
                        "question": "Python is a programming language.",
                        "correctAnswer": "true",
                        "points": 5,
                        "explanation": "Python is indeed a popular programming language."
                    },
                    {
                        "type": "short_answer",
                        "question": "What does API stand for?",
                        "correctAnswer": "Application Programming Interface",
                        "points": 10,
                        "explanation": "API stands for Application Programming Interface."
                    }
                ]
            }
            
            response = requests.post(
                f"{BACKEND_URL}/final-tests",
                json=final_test_data,
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code == 200:
                final_test = response.json()
                self.created_resources['final_tests'].append(final_test['id'])
                self.log_test("Create Final Test", True, f"Test ID: {final_test['id']}, Questions: {len(final_test['questions'])}")
                return final_test['id']
            else:
                self.log_test("Create Final Test", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.log_test("Create Final Test", False, f"Exception: {str(e)}")
            return None

    def test_get_all_final_tests(self):
        """Test GET /api/final-tests endpoint"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/final-tests",
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code == 200:
                final_tests = response.json()
                self.log_test("Get All Final Tests", True, f"Found {len(final_tests)} final tests")
                return final_tests
            else:
                self.log_test("Get All Final Tests", False, f"Status: {response.status_code}, Response: {response.text}")
                return []
        except Exception as e:
            self.log_test("Get All Final Tests", False, f"Exception: {str(e)}")
            return []

    def test_get_specific_final_test(self, test_id):
        """Test GET /api/final-tests/{test_id} endpoint"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/final-tests/{test_id}",
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code == 200:
                final_test = response.json()
                self.log_test("Get Specific Final Test", True, f"Test: {final_test['title']}, Questions: {len(final_test['questions'])}")
                return final_test
            else:
                self.log_test("Get Specific Final Test", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.log_test("Get Specific Final Test", False, f"Exception: {str(e)}")
            return None

    def test_student_access_final_test(self, test_id):
        """Test student access to final test"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/final-tests/{test_id}",
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code == 200:
                final_test = response.json()
                # Check if correct answers are hidden from students
                has_correct_answers = any('correctAnswer' in q for q in final_test.get('questions', []))
                self.log_test("Student Access Final Test", True, f"Access granted, Answers hidden: {not has_correct_answers}")
                return final_test
            else:
                self.log_test("Student Access Final Test", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.log_test("Student Access Final Test", False, f"Exception: {str(e)}")
            return None

    def test_submit_final_test_attempt(self, test_id, final_test_data):
        """Test POST /api/final-test-attempts endpoint"""
        try:
            # Get the actual question IDs from the final test
            questions = final_test_data.get('questions', [])
            if not questions:
                self.log_test("Submit Final Test Attempt", False, "No questions found in final test")
                return None
            
            # Create answers using actual question IDs
            answers = []
            for i, question in enumerate(questions):
                question_id = question.get('id', f'q{i+1}')
                if question['type'] == 'multiple_choice':
                    answers.append({"questionId": question_id, "answer": "2"})  # Paris
                elif question['type'] == 'true_false':
                    answers.append({"questionId": question_id, "answer": "true"})
                elif question['type'] == 'short_answer':
                    answers.append({"questionId": question_id, "answer": "Application Programming Interface"})
            
            attempt_data = {
                "testId": test_id,
                "answers": answers,
                "timeSpent": 1800  # 30 minutes
            }
            
            response = requests.post(
                f"{BACKEND_URL}/final-test-attempts",
                json=attempt_data,
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code == 200:
                attempt = response.json()
                self.log_test("Submit Final Test Attempt", True, f"Score: {attempt['score']}%, Passed: {attempt['isPassed']}")
                return attempt['id']
            else:
                self.log_test("Submit Final Test Attempt", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            self.log_test("Submit Final Test Attempt", False, f"Exception: {str(e)}")
            return None

    def test_get_final_test_attempts(self):
        """Test GET /api/final-test-attempts endpoint"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/final-test-attempts",
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code == 200:
                attempts = response.json()
                self.log_test("Get Final Test Attempts", True, f"Found {len(attempts)} attempts")
                return attempts
            else:
                self.log_test("Get Final Test Attempts", False, f"Status: {response.status_code}, Response: {response.text}")
                return []
        except Exception as e:
            self.log_test("Get Final Test Attempts", False, f"Exception: {str(e)}")
            return []

    def test_grading_system_endpoints(self):
        """Test grading system endpoints (if implemented)"""
        # Note: Based on the backend code review, these endpoints don't appear to be implemented yet
        # Testing if they exist
        
        # Test GET /api/courses/{course_id}/submissions
        try:
            # First get a course ID
            response = requests.get(f"{BACKEND_URL}/courses", headers=self.get_headers(self.admin_token))
            if response.status_code == 200:
                courses = response.json()
                if courses:
                    course_id = courses[0]['id']
                    
                    # Test submissions endpoint
                    response = requests.get(
                        f"{BACKEND_URL}/courses/{course_id}/submissions",
                        headers=self.get_headers(self.admin_token)
                    )
                    
                    if response.status_code == 200:
                        submissions = response.json()
                        self.log_test("Get Course Submissions", True, f"Found {len(submissions)} submissions")
                    elif response.status_code == 404:
                        self.log_test("Get Course Submissions", False, "Endpoint not implemented (404)")
                    else:
                        self.log_test("Get Course Submissions", False, f"Status: {response.status_code}")
                else:
                    self.log_test("Get Course Submissions", False, "No courses available for testing")
            else:
                self.log_test("Get Course Submissions", False, "Could not get courses list")
        except Exception as e:
            self.log_test("Get Course Submissions", False, f"Exception: {str(e)}")

        # Test POST /api/submissions/{submission_id}/grade
        try:
            fake_submission_id = str(uuid.uuid4())
            grade_data = {
                "score": 85,
                "feedback": "Good work!",
                "gradedBy": "instructor"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/submissions/{fake_submission_id}/grade",
                json=grade_data,
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code == 200:
                self.log_test("Grade Submission", True, "Grading endpoint working")
            elif response.status_code == 404:
                self.log_test("Grade Submission", False, "Endpoint not implemented (404)")
            else:
                self.log_test("Grade Submission", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Grade Submission", False, f"Exception: {str(e)}")

        # Test GET /api/submissions/{submission_id}/grade
        try:
            fake_submission_id = str(uuid.uuid4())
            response = requests.get(
                f"{BACKEND_URL}/submissions/{fake_submission_id}/grade",
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code == 200:
                self.log_test("Get Submission Grade", True, "Get grade endpoint working")
            elif response.status_code == 404:
                self.log_test("Get Submission Grade", False, "Endpoint not implemented (404)")
            else:
                self.log_test("Get Submission Grade", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get Submission Grade", False, f"Exception: {str(e)}")

    def test_user_requirements_verification(self):
        """Test user requirements from review request"""
        print("\n🎯 USER REQUIREMENTS VERIFICATION:")
        
        # 1. Can instructors now create and save final exam questions?
        if self.created_resources['final_tests']:
            print("✅ 1. Instructors can create and save final exam questions")
        else:
            print("❌ 1. Final exam creation failed")
        
        # 2. Can students access and take final exams?
        student_attempts = self.test_get_final_test_attempts()
        if student_attempts:
            print("✅ 2. Students can access and take final exams")
        else:
            print("❌ 2. Student final exam access issues")
        
        # 3. Can instructors view and grade subjective answers?
        print("⚠️  3. Grading system endpoints not fully implemented yet")
        
        # 4. Does the analytics/progress data flow work correctly?
        print("⚠️  4. Analytics integration needs verification with actual data")

    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🚀 FINAL EXAM AND GRADING SYSTEM BACKEND TESTING")
        print("=" * 60)
        
        # Authentication tests
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot continue")
            return
        
        if not self.authenticate_student():
            print("❌ Student authentication failed - cannot continue")
            return
        
        # Create test program
        program_id = self.test_create_program_for_final_test()
        if not program_id:
            print("❌ Program creation failed - cannot test final exams")
            return
        
        # Final test management tests
        print("\n📝 FINAL TEST MANAGEMENT ENDPOINTS:")
        test_id = self.test_create_final_test(program_id)
        final_test_data = None
        
        if test_id:
            self.test_get_all_final_tests()
            final_test_data = self.test_get_specific_final_test(test_id)
            self.test_student_access_final_test(test_id)
            if final_test_data:
                self.test_submit_final_test_attempt(test_id, final_test_data)
            self.test_get_final_test_attempts()
        
        # Grading system tests
        print("\n📊 GRADING SYSTEM ENDPOINTS:")
        self.test_grading_system_endpoints()
        
        # User requirements verification
        self.test_user_requirements_verification()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print("\n🎯 FINAL EXAM SYSTEM STATUS:")
        if success_rate >= 80:
            print("✅ Final exam system is working correctly")
        elif success_rate >= 60:
            print("⚠️  Final exam system has some issues but core functionality works")
        else:
            print("❌ Final exam system has significant issues")
        
        print("\n📝 RECOMMENDATIONS:")
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print("Priority fixes needed:")
            for test in failed_tests:
                print(f"- {test['test']}: {test['details']}")
        else:
            print("✅ All tests passed - system ready for production")

if __name__ == "__main__":
    tester = FinalExamBackendTester()
    tester.run_comprehensive_test()