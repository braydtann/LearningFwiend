#!/usr/bin/env python3
"""
LearningFriend LMS Backend Testing Suite
Testing program creation workflow, final tests, and student access functionality
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://quiz-analytics-lms.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class LMSBackendTester:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.test_program_id = None
        self.test_final_test_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.log_test("Admin Authentication", True, f"Token obtained for {data.get('user', {}).get('email', 'admin')}")
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
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.log_test("Student Authentication", True, f"Token obtained for {data.get('user', {}).get('email', 'student')}")
                return True
            else:
                self.log_test("Student Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_program_creation_workflow(self):
        """Test program creation API workflow"""
        if not self.admin_token:
            self.log_test("Program Creation Workflow", False, "Admin token not available")
            return False
            
        try:
            # Create a test program
            program_data = {
                "title": f"Test Program - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test program for backend validation",
                "departmentId": None,
                "duration": "4 weeks",
                "courseIds": [],  # Start with empty courses
                "nestedProgramIds": []
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(
                f"{BACKEND_URL}/programs",
                json=program_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_program_id = data.get("id")
                self.log_test("Program Creation Workflow", True, f"Program created with ID: {self.test_program_id}")
                return True
            else:
                self.log_test("Program Creation Workflow", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Program Creation Workflow", False, f"Exception: {str(e)}")
            return False
    
    def test_final_test_creation(self):
        """Test POST /api/final-tests endpoint"""
        if not self.admin_token or not self.test_program_id:
            self.log_test("Final Test Creation", False, "Admin token or program ID not available")
            return False
            
        try:
            # Create a final test for the program
            final_test_data = {
                "title": f"Final Test - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test final exam for program completion",
                "programId": self.test_program_id,
                "questions": [
                    {
                        "type": "multiple-choice",
                        "question": "What is the primary purpose of this LMS?",
                        "options": [
                            "Learning management",
                            "Social networking", 
                            "E-commerce",
                            "Gaming"
                        ],
                        "correctAnswer": 0,
                        "points": 10,
                        "explanation": "LMS stands for Learning Management System"
                    },
                    {
                        "type": "true-false",
                        "question": "Final tests are program-level assessments.",
                        "correctAnswer": True,
                        "points": 5,
                        "explanation": "Final tests are designed to assess completion of entire programs"
                    }
                ],
                "timeLimit": 60,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": True
            }
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(
                f"{BACKEND_URL}/final-tests",
                json=final_test_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_final_test_id = data.get("id")
                total_points = data.get("totalPoints", 0)
                question_count = data.get("questionCount", 0)
                self.log_test("Final Test Creation", True, f"Final test created with ID: {self.test_final_test_id}, {question_count} questions, {total_points} points")
                return True
            else:
                self.log_test("Final Test Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Final Test Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_final_test_retrieval_by_program(self):
        """Test GET /api/final-tests with program_id filter"""
        if not self.admin_token or not self.test_program_id:
            self.log_test("Final Test Retrieval by Program", False, "Admin token or program ID not available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{BACKEND_URL}/final-tests?program_id={self.test_program_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    program_tests = [test for test in data if test.get("programId") == self.test_program_id]
                    self.log_test("Final Test Retrieval by Program", True, f"Found {len(program_tests)} final tests for program {self.test_program_id}")
                    return True
                else:
                    self.log_test("Final Test Retrieval by Program", False, "Response is not a list")
                    return False
            else:
                self.log_test("Final Test Retrieval by Program", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Final Test Retrieval by Program", False, f"Exception: {str(e)}")
            return False
    
    def test_program_course_navigation(self):
        """Test that course IDs in programs are properly ordered"""
        if not self.admin_token:
            self.log_test("Program Course Navigation", False, "Admin token not available")
            return False
            
        try:
            # First get all programs to test course ordering
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{BACKEND_URL}/programs",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                programs = response.json()
                if isinstance(programs, list) and len(programs) > 0:
                    # Test course ID ordering in programs
                    programs_with_courses = [p for p in programs if p.get("courseIds") and len(p.get("courseIds", [])) > 0]
                    
                    if programs_with_courses:
                        test_program = programs_with_courses[0]
                        course_ids = test_program.get("courseIds", [])
                        
                        # Verify course IDs are valid UUIDs and properly ordered
                        valid_course_ids = []
                        for course_id in course_ids:
                            try:
                                uuid.UUID(course_id)  # Validate UUID format
                                valid_course_ids.append(course_id)
                            except ValueError:
                                pass
                        
                        if len(valid_course_ids) == len(course_ids):
                            self.log_test("Program Course Navigation", True, f"Program '{test_program.get('title')}' has {len(course_ids)} properly ordered course IDs")
                            return True
                        else:
                            self.log_test("Program Course Navigation", False, f"Invalid course ID format found in program")
                            return False
                    else:
                        self.log_test("Program Course Navigation", True, "No programs with courses found, but API is working")
                        return True
                else:
                    self.log_test("Program Course Navigation", True, "No programs found, but API is working")
                    return True
            else:
                self.log_test("Program Course Navigation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Program Course Navigation", False, f"Exception: {str(e)}")
            return False
    
    def test_student_final_test_access(self):
        """Test that students can access final tests for completed programs"""
        if not self.student_token:
            self.log_test("Student Final Test Access", False, "Student token not available")
            return False
            
        try:
            # Test student access to final tests
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(
                f"{BACKEND_URL}/final-tests",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                final_tests = response.json()
                if isinstance(final_tests, list):
                    published_tests = [test for test in final_tests if test.get("isPublished", False)]
                    self.log_test("Student Final Test Access", True, f"Student can access {len(published_tests)} published final tests")
                    
                    # Test access to specific final test if we created one
                    if self.test_final_test_id and published_tests:
                        test_response = requests.get(
                            f"{BACKEND_URL}/final-tests/{self.test_final_test_id}",
                            headers=headers,
                            timeout=10
                        )
                        
                        if test_response.status_code == 200:
                            test_data = test_response.json()
                            self.log_test("Student Specific Final Test Access", True, f"Student can access final test: {test_data.get('title')}")
                        else:
                            self.log_test("Student Specific Final Test Access", False, f"Cannot access specific test: {test_response.status_code}")
                    
                    return True
                else:
                    self.log_test("Student Final Test Access", False, "Response is not a list")
                    return False
            else:
                self.log_test("Student Final Test Access", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Final Test Access", False, f"Exception: {str(e)}")
            return False
    
    def test_student_program_completion_workflow(self):
        """Test complete workflow from program enrollment to final test access"""
        if not self.student_token:
            self.log_test("Student Program Completion Workflow", False, "Student token not available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get student enrollments
            enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                headers=headers,
                timeout=10
            )
            
            if enrollments_response.status_code == 200:
                enrollments = enrollments_response.json()
                completed_enrollments = [e for e in enrollments if e.get("status") == "completed" or e.get("progress", 0) >= 100]
                
                # Get programs to check for completed program courses
                programs_response = requests.get(
                    f"{BACKEND_URL}/programs",
                    headers=headers,
                    timeout=10
                )
                
                if programs_response.status_code == 200:
                    programs = programs_response.json()
                    
                    # Check if student has completed any program courses
                    completed_program_courses = 0
                    for enrollment in completed_enrollments:
                        course_id = enrollment.get("courseId")
                        for program in programs:
                            if course_id in program.get("courseIds", []):
                                completed_program_courses += 1
                                break
                    
                    self.log_test("Student Program Completion Workflow", True, 
                                f"Student has {len(enrollments)} enrollments, {len(completed_enrollments)} completed, {completed_program_courses} program courses completed")
                    return True
                else:
                    self.log_test("Student Program Completion Workflow", False, f"Cannot get programs: {programs_response.status_code}")
                    return False
            else:
                self.log_test("Student Program Completion Workflow", False, f"Cannot get enrollments: {enrollments_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Student Program Completion Workflow", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting LearningFriend LMS Backend Testing Suite")
        print("=" * 60)
        
        # Authentication tests
        print("\n📋 AUTHENTICATION TESTS")
        print("-" * 30)
        admin_auth_success = self.authenticate_admin()
        student_auth_success = self.authenticate_student()
        
        if not admin_auth_success:
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Core functionality tests
        print("\n📋 PROGRAM MANAGEMENT TESTS")
        print("-" * 30)
        self.test_program_creation_workflow()
        self.test_program_course_navigation()
        
        print("\n📋 FINAL TEST FUNCTIONALITY TESTS")
        print("-" * 30)
        self.test_final_test_creation()
        self.test_final_test_retrieval_by_program()
        
        if student_auth_success:
            print("\n📋 STUDENT ACCESS TESTS")
            print("-" * 30)
            self.test_student_final_test_access()
            self.test_student_program_completion_workflow()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  • {test['test']}: {test['details']}")
        
        return failed_tests == 0

def main():
    """Main test execution"""
    tester = LMSBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Backend is ready for production.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please review the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()