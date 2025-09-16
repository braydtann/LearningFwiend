#!/usr/bin/env python3
"""
Backend Testing Script for LearningFriend LMS
Focus: Final Test Creation and bcrypt Authentication Issues

Review Request Testing:
1. Test final test creation endpoint: POST /api/final-tests with empty questions array
2. Test program creation with final test workflow 
3. Verify that bcrypt authentication errors are resolved
4. Check if 422 errors during final test creation are still occurring

Admin credentials: brayden.t@covesmart.com / Hawaii2020!
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration - Using correct backend URL from frontend/.env
BACKEND_URL = "https://lms-chronology.emergent.host/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error_msg=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def authenticate_admin(self):
        """Test admin authentication with bcrypt fix verification"""
        print("🔐 Testing Admin Authentication (bcrypt fix verification)...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                user_info = data.get('user', {})
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}'
                })
                
                self.log_result(
                    "Admin Authentication (bcrypt fix)",
                    True,
                    f"Successfully authenticated as {user_info.get('full_name', 'Admin')} ({user_info.get('email', 'N/A')})"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_result(
                    "Admin Authentication (bcrypt fix)",
                    False,
                    f"Status: {response.status_code}",
                    error_detail
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Authentication (bcrypt fix)",
                False,
                "",
                f"Network error: {str(e)}"
            )
            return False

    def test_program_creation(self):
        """Test program creation for final test workflow"""
        print("📚 Testing Program Creation for Final Test Workflow...")
        
        if not self.admin_token:
            self.log_result("Program Creation", False, "", "No admin token available")
            return None
            
        # Create a test program
        program_data = {
            "title": f"Final Test Program {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "description": "Test program for final test creation workflow",
            "departmentId": None,
            "duration": "4 weeks",
            "courseIds": [],
            "nestedProgramIds": []
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/programs",
                json=program_data,
                timeout=30
            )
            
            if response.status_code == 200:
                program = response.json()
                program_id = program.get('id')
                
                self.log_result(
                    "Program Creation",
                    True,
                    f"Created program '{program.get('title')}' with ID: {program_id}"
                )
                return program_id
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_result(
                    "Program Creation",
                    False,
                    f"Status: {response.status_code}",
                    error_detail
                )
                return None
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Program Creation",
                False,
                "",
                f"Network error: {str(e)}"
            )
            return None

    def test_final_test_creation_empty_questions(self, program_id):
        """Test final test creation with empty questions array (main focus)"""
        print("🎯 Testing Final Test Creation with Empty Questions Array...")
        
        if not self.admin_token or not program_id:
            self.log_result("Final Test Creation (Empty Questions)", False, "", "Missing admin token or program ID")
            return None
            
        # Test data with empty questions array
        final_test_data = {
            "title": f"Empty Questions Final Test {datetime.now().strftime('%H%M%S')}",
            "description": "Testing final test creation with empty questions array",
            "programId": program_id,
            "questions": [],  # Empty questions array - this is the key test
            "timeLimit": 60,
            "maxAttempts": 2,
            "passingScore": 75.0,
            "shuffleQuestions": False,
            "showResults": True,
            "isPublished": False
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/final-tests",
                json=final_test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                final_test = response.json()
                test_id = final_test.get('id')
                question_count = final_test.get('questionCount', 0)
                total_points = final_test.get('totalPoints', 0)
                
                self.log_result(
                    "Final Test Creation (Empty Questions)",
                    True,
                    f"Created final test '{final_test.get('title')}' with {question_count} questions, {total_points} total points"
                )
                return test_id
            elif response.status_code == 422:
                # This is the specific error we're checking for
                try:
                    error_detail = response.json().get('detail', 'Unknown validation error')
                except:
                    error_detail = "422 Unprocessable Entity"
                    
                self.log_result(
                    "Final Test Creation (Empty Questions)",
                    False,
                    f"422 ERROR DETECTED - This is the reported issue",
                    f"Validation error: {error_detail}"
                )
                return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_result(
                    "Final Test Creation (Empty Questions)",
                    False,
                    f"Status: {response.status_code}",
                    error_detail
                )
                return None
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Final Test Creation (Empty Questions)",
                False,
                "",
                f"Network error: {str(e)}"
            )
            return None

    def test_final_test_creation_with_questions(self, program_id):
        """Test final test creation with actual questions"""
        print("📝 Testing Final Test Creation with Questions...")
        
        if not self.admin_token or not program_id:
            self.log_result("Final Test Creation (With Questions)", False, "", "Missing admin token or program ID")
            return None
            
        # Test data with sample questions
        final_test_data = {
            "title": f"Sample Questions Final Test {datetime.now().strftime('%H%M%S')}",
            "description": "Testing final test creation with sample questions",
            "programId": program_id,
            "questions": [
                {
                    "type": "multiple-choice",
                    "question": "What is the primary purpose of a Learning Management System?",
                    "options": [
                        "To manage student data",
                        "To deliver educational content and track progress",
                        "To create course schedules",
                        "To handle financial transactions"
                    ],
                    "correctAnswer": 1,
                    "points": 10,
                    "explanation": "LMS systems are designed to deliver educational content and track student progress."
                },
                {
                    "type": "true-false",
                    "question": "Final tests can be created without any questions initially.",
                    "correctAnswer": True,
                    "points": 5,
                    "explanation": "Yes, final tests can be created with empty questions array and questions added later."
                }
            ],
            "timeLimit": 45,
            "maxAttempts": 3,
            "passingScore": 80.0,
            "shuffleQuestions": True,
            "showResults": True,
            "isPublished": True
        }
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/final-tests",
                json=final_test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                final_test = response.json()
                test_id = final_test.get('id')
                question_count = final_test.get('questionCount', 0)
                total_points = final_test.get('totalPoints', 0)
                
                self.log_result(
                    "Final Test Creation (With Questions)",
                    True,
                    f"Created final test '{final_test.get('title')}' with {question_count} questions, {total_points} total points"
                )
                return test_id
            elif response.status_code == 422:
                try:
                    error_detail = response.json().get('detail', 'Unknown validation error')
                except:
                    error_detail = "422 Unprocessable Entity"
                    
                self.log_result(
                    "Final Test Creation (With Questions)",
                    False,
                    f"422 ERROR - Validation issue with questions",
                    f"Validation error: {error_detail}"
                )
                return None
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_result(
                    "Final Test Creation (With Questions)",
                    False,
                    f"Status: {response.status_code}",
                    error_detail
                )
                return None
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Final Test Creation (With Questions)",
                False,
                "",
                f"Network error: {str(e)}"
            )
            return None

    def test_get_final_tests(self):
        """Test retrieving final tests"""
        print("📋 Testing Final Tests Retrieval...")
        
        if not self.admin_token:
            self.log_result("Final Tests Retrieval", False, "", "No admin token available")
            return
            
        try:
            response = self.session.get(
                f"{BACKEND_URL}/final-tests",
                timeout=30
            )
            
            if response.status_code == 200:
                final_tests = response.json()
                test_count = len(final_tests)
                
                self.log_result(
                    "Final Tests Retrieval",
                    True,
                    f"Retrieved {test_count} final tests"
                )
                
                # Show details of first few tests
                for i, test in enumerate(final_tests[:3]):
                    print(f"   Test {i+1}: '{test.get('title')}' - {test.get('questionCount', 0)} questions, Published: {test.get('isPublished', False)}")
                    
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_result(
                    "Final Tests Retrieval",
                    False,
                    f"Status: {response.status_code}",
                    error_detail
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Final Tests Retrieval",
                False,
                "",
                f"Network error: {str(e)}"
            )

    def test_programs_retrieval(self):
        """Test retrieving programs"""
        print("🏫 Testing Programs Retrieval...")
        
        if not self.admin_token:
            self.log_result("Programs Retrieval", False, "", "No admin token available")
            return
            
        try:
            response = self.session.get(
                f"{BACKEND_URL}/programs",
                timeout=30
            )
            
            if response.status_code == 200:
                programs = response.json()
                program_count = len(programs)
                
                self.log_result(
                    "Programs Retrieval",
                    True,
                    f"Retrieved {program_count} programs"
                )
                
                # Show details of first few programs
                for i, program in enumerate(programs[:3]):
                    print(f"   Program {i+1}: '{program.get('title')}' - {program.get('courseCount', 0)} courses")
                    
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_result(
                    "Programs Retrieval",
                    False,
                    f"Status: {response.status_code}",
                    error_detail
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Programs Retrieval",
                False,
                "",
                f"Network error: {str(e)}"
            )

    def test_health_endpoint(self):
        """Test basic health endpoint"""
        print("🏥 Testing Health Endpoint...")
        
        try:
            response = self.session.get(
                f"{BACKEND_URL}/health",
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Health Endpoint",
                    True,
                    "Backend is responding to health checks"
                )
            else:
                self.log_result(
                    "Health Endpoint",
                    False,
                    f"Status: {response.status_code}",
                    "Health endpoint not responding correctly"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Health Endpoint",
                False,
                "",
                f"Network error: {str(e)}"
            )

    def run_comprehensive_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Backend Testing for Final Test Creation Issues")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Test 1: Health check
        self.test_health_endpoint()
        
        # Test 2: Admin authentication (bcrypt fix verification)
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Test 3: Programs retrieval
        self.test_programs_retrieval()
        
        # Test 4: Program creation for final test workflow
        program_id = self.test_program_creation()
        
        if program_id:
            # Test 5: Final test creation with empty questions (main focus)
            self.test_final_test_creation_empty_questions(program_id)
            
            # Test 6: Final test creation with questions
            self.test_final_test_creation_with_questions(program_id)
        
        # Test 7: Final tests retrieval
        self.test_get_final_tests()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['error']}")
            print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        # Check for 422 errors specifically
        has_422_error = any("422" in result['error'] for result in self.test_results if not result['success'])
        if has_422_error:
            print("   • ⚠️  422 ERRORS DETECTED - The reported issue is still occurring")
        else:
            print("   • ✅ No 422 errors detected in final test creation")
        
        # Check authentication
        auth_success = any(result['success'] for result in self.test_results if "Authentication" in result['test'])
        if auth_success:
            print("   • ✅ bcrypt authentication fix is working correctly")
        else:
            print("   • ❌ bcrypt authentication issues detected")
        
        # Check final test creation
        final_test_success = any(result['success'] for result in self.test_results if "Final Test Creation" in result['test'])
        if final_test_success:
            print("   • ✅ Final test creation is working (at least partially)")
        else:
            print("   • ❌ Final test creation is completely failing")
        
        print("\n" + "=" * 80)
        print("🎯 REVIEW REQUEST STATUS:")
        print("1. Final test creation with empty questions: " + ("✅ WORKING" if not has_422_error else "❌ 422 ERROR"))
        print("2. Program creation workflow: " + ("✅ WORKING" if any("Program Creation" in r['test'] and r['success'] for r in self.test_results) else "❌ FAILING"))
        print("3. bcrypt authentication fix: " + ("✅ RESOLVED" if auth_success else "❌ STILL BROKEN"))
        print("4. 422 errors during final test creation: " + ("❌ STILL OCCURRING" if has_422_error else "✅ RESOLVED"))
        print("=" * 80)

if __name__ == "__main__":
    tester = BackendTester()
    tester.run_comprehensive_tests()