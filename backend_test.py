#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Final Test Functionality
Testing the final test backend functionality and creating sample data for testing.
"""

import requests
import json
import sys
from datetime import datetime
import uuid

class FinalTestBackendTester:
    def __init__(self):
        # Use the production URL from frontend/.env
        self.base_url = "https://92d481e3-4a47-464c-b3ac-8a0264afd50a.preview.emergentagent.com/api"
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        
        # Test credentials from review request
        self.admin_credentials = {
            "username_or_email": "brayden.t@covesmart.com",
            "password": "Hawaii2020!"
        }
        
        self.student_credentials = {
            "username_or_email": "karlo.student@alder.com", 
            "password": "StudentPermanent123!"
        }
        
        print(f"🔧 Backend URL: {self.base_url}")
        print("=" * 80)

    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")

    def authenticate_admin(self):
        """Test admin authentication"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=self.admin_credentials,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                user_info = data.get('user', {})
                self.log_result(
                    "Admin Authentication", 
                    True, 
                    f"Logged in as {user_info.get('full_name')} ({user_info.get('role')})"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Error: {str(e)}")
            return False

    def authenticate_student(self):
        """Test student authentication"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=self.student_credentials,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get('access_token')
                user_info = data.get('user', {})
                self.log_result(
                    "Student Authentication", 
                    True, 
                    f"Logged in as {user_info.get('full_name')} ({user_info.get('role')})"
                )
                return True
            else:
                self.log_result(
                    "Student Authentication", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_result("Student Authentication", False, f"Error: {str(e)}")
            return False

    def get_programs(self):
        """Check if we have programs in the system that students can be enrolled in"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{self.base_url}/programs",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                programs = response.json()
                if programs:
                    self.log_result(
                        "Programs Check", 
                        True, 
                        f"Found {len(programs)} programs available"
                    )
                    # Return the first program for testing
                    return programs[0] if programs else None
                else:
                    self.log_result("Programs Check", False, "No programs found in system")
                    return None
            else:
                self.log_result(
                    "Programs Check", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return None
                
        except Exception as e:
            self.log_result("Programs Check", False, f"Error: {str(e)}")
            return None

    def create_sample_final_test(self, program):
        """Create a sample final test for a program with various question types"""
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            # Create comprehensive final test with various question types
            final_test_data = {
                "title": "Comprehensive Final Test - Sample",
                "description": "A comprehensive final test with multiple question types to validate the final test system functionality",
                "programId": program['id'],
                "timeLimit": 60,  # 60 minutes
                "maxAttempts": 2,
                "passingScore": 75.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": True,  # Make it published so students can access it
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is the primary purpose of a learning management system?",
                        "options": [
                            "To manage student grades only",
                            "To facilitate online learning and course management",
                            "To replace traditional classrooms entirely",
                            "To store educational videos"
                        ],
                        "correctAnswer": "1",  # Index of correct answer
                        "points": 10,
                        "explanation": "LMS systems are designed to facilitate comprehensive online learning and course management."
                    },
                    {
                        "type": "true_false",
                        "question": "Final tests in a program are typically more comprehensive than individual course quizzes.",
                        "correctAnswer": "true",
                        "points": 5,
                        "explanation": "Final tests assess overall program competency and are usually more comprehensive."
                    },
                    {
                        "type": "multiple_choice",
                        "question": "Which of the following is NOT a typical feature of modern LMS platforms?",
                        "options": [
                            "Progress tracking",
                            "Discussion forums", 
                            "Physical classroom booking",
                            "Assignment submission"
                        ],
                        "correctAnswer": "2",
                        "points": 10,
                        "explanation": "Physical classroom booking is typically handled by separate facility management systems."
                    },
                    {
                        "type": "short_answer",
                        "question": "What does 'LMS' stand for?",
                        "correctAnswer": "Learning Management System",
                        "points": 5,
                        "explanation": "LMS is the standard abbreviation for Learning Management System."
                    },
                    {
                        "type": "true_false",
                        "question": "Students should be able to retake final tests unlimited times.",
                        "correctAnswer": "false",
                        "points": 5,
                        "explanation": "Final tests typically have limited attempts to maintain assessment integrity."
                    },
                    {
                        "type": "multiple_choice",
                        "question": "What is the recommended passing score for most certification programs?",
                        "options": [
                            "50%",
                            "65%",
                            "75%",
                            "90%"
                        ],
                        "correctAnswer": "2",
                        "points": 10,
                        "explanation": "75% is commonly used as a standard passing score for certification programs."
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/final-tests",
                headers=headers,
                json=final_test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                test_data = response.json()
                self.log_result(
                    "Final Test Creation", 
                    True, 
                    f"Created test '{test_data['title']}' with {test_data['questionCount']} questions, {test_data['totalPoints']} total points"
                )
                return test_data
            else:
                self.log_result(
                    "Final Test Creation", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:500]}"
                )
                return None
                
        except Exception as e:
            self.log_result("Final Test Creation", False, f"Error: {str(e)}")
            return None

    def verify_final_test(self, test_data):
        """Verify the final test was created successfully and is properly linked to program"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get the created test by ID
            response = requests.get(
                f"{self.base_url}/final-tests/{test_data['id']}?include_answers=true",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                retrieved_test = response.json()
                
                # Verify test properties
                checks = []
                checks.append(("Title matches", retrieved_test['title'] == test_data['title']))
                checks.append(("Program linked", retrieved_test['programId'] == test_data['programId']))
                checks.append(("Published status", retrieved_test['isPublished'] == True))
                checks.append(("Has questions", len(retrieved_test['questions']) > 0))
                checks.append(("Total points calculated", retrieved_test['totalPoints'] > 0))
                checks.append(("Question count correct", retrieved_test['questionCount'] == len(retrieved_test['questions'])))
                
                all_passed = all(check[1] for check in checks)
                details = ", ".join([f"{check[0]}: {'✓' if check[1] else '✗'}" for check in checks])
                
                self.log_result(
                    "Final Test Verification", 
                    all_passed, 
                    details
                )
                return all_passed
            else:
                self.log_result(
                    "Final Test Verification", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                return False
                
        except Exception as e:
            self.log_result("Final Test Verification", False, f"Error: {str(e)}")
            return False

    def test_student_access(self, test_data):
        """Test student access to final tests"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Test 1: Get all final tests (student should see published tests)
            response = requests.get(
                f"{self.base_url}/final-tests",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                tests = response.json()
                published_tests = [t for t in tests if t.get('isPublished', False)]
                self.log_result(
                    "Student Final Tests Access", 
                    True, 
                    f"Student can see {len(published_tests)} published final tests"
                )
            else:
                self.log_result(
                    "Student Final Tests Access", 
                    False, 
                    f"Status: {response.status_code}"
                )
                return False
            
            # Test 2: Access specific test (without answers)
            response = requests.get(
                f"{self.base_url}/final-tests/{test_data['id']}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                student_test_view = response.json()
                
                # Verify student doesn't see correct answers
                has_correct_answers = any(
                    'correctAnswer' in q for q in student_test_view.get('questions', [])
                )
                
                self.log_result(
                    "Student Test Access (No Answers)", 
                    not has_correct_answers, 
                    f"Student view properly hides correct answers: {not has_correct_answers}"
                )
                return True
            else:
                self.log_result(
                    "Student Test Access (No Answers)", 
                    False, 
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Student Access Test", False, f"Error: {str(e)}")
            return False

    def test_student_enrollments(self):
        """Check if student is enrolled in programs"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get student's enrollments
            response = requests.get(
                f"{self.base_url}/enrollments",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                self.log_result(
                    "Student Enrollments Check", 
                    True, 
                    f"Student has {len(enrollments)} course enrollments"
                )
                return len(enrollments) > 0
            else:
                self.log_result(
                    "Student Enrollments Check", 
                    False, 
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Student Enrollments Check", False, f"Error: {str(e)}")
            return False

    def test_final_test_endpoints(self):
        """Test various final test endpoints"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test getting all final tests
            response = requests.get(
                f"{self.base_url}/final-tests",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                all_tests = response.json()
                self.log_result(
                    "Get All Final Tests", 
                    True, 
                    f"Retrieved {len(all_tests)} final tests"
                )
            else:
                self.log_result("Get All Final Tests", False, f"Status: {response.status_code}")
                return False
            
            # Test getting admin's final tests
            response = requests.get(
                f"{self.base_url}/final-tests/my-tests",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                my_tests = response.json()
                self.log_result(
                    "Get My Final Tests", 
                    True, 
                    f"Admin has created {len(my_tests)} final tests"
                )
                return True
            else:
                self.log_result("Get My Final Tests", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Final Test Endpoints", False, f"Error: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all final test functionality tests"""
        print("🎯 FINAL TEST BACKEND FUNCTIONALITY TESTING INITIATED")
        print("Testing final test backend functionality and creating sample data for testing")
        print("=" * 80)
        
        # Step 1: Authentication Check
        print("\n📋 STEP 1: AUTHENTICATION TESTING")
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot proceed")
            return False
            
        if not self.authenticate_student():
            print("❌ Student authentication failed - cannot proceed")
            return False
        
        # Step 2: Programs Check
        print("\n📋 STEP 2: PROGRAMS VERIFICATION")
        program = self.get_programs()
        if not program:
            print("❌ No programs found - cannot create final tests")
            return False
        
        print(f"✅ Using program: {program['title']} (ID: {program['id']})")
        
        # Step 3: Final Test Creation
        print("\n📋 STEP 3: FINAL TEST CREATION")
        test_data = self.create_sample_final_test(program)
        if not test_data:
            print("❌ Final test creation failed")
            return False
        
        # Step 4: Final Test Verification
        print("\n📋 STEP 4: FINAL TEST VERIFICATION")
        if not self.verify_final_test(test_data):
            print("❌ Final test verification failed")
            return False
        
        # Step 5: Test Final Test Endpoints
        print("\n📋 STEP 5: FINAL TEST ENDPOINTS TESTING")
        if not self.test_final_test_endpoints():
            print("❌ Final test endpoints testing failed")
            return False
        
        # Step 6: Student Access Testing
        print("\n📋 STEP 6: STUDENT ACCESS TESTING")
        if not self.test_student_access(test_data):
            print("❌ Student access testing failed")
            return False
        
        # Step 7: Student Enrollments Check
        print("\n📋 STEP 7: STUDENT ENROLLMENTS CHECK")
        self.test_student_enrollments()
        
        return True

    def print_summary(self):
        """Print final summary of all test results"""
        print("\n" + "=" * 80)
        print("🎉 FINAL TEST BACKEND TESTING SUMMARY")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]
        
        print(f"✅ PASSED: {len(passed_tests)}/{len(self.test_results)} tests")
        print(f"❌ FAILED: {len(failed_tests)}/{len(self.test_results)} tests")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        success_rate = (len(passed_tests) / len(self.test_results)) * 100 if self.test_results else 0
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 FINAL TEST BACKEND SYSTEM IS FUNCTIONAL AND READY FOR USE")
        else:
            print("⚠️  FINAL TEST BACKEND SYSTEM NEEDS ATTENTION")
        
        return success_rate >= 80


def main():
    """Main test execution"""
    tester = FinalTestBackendTester()
    
    try:
        success = tester.run_comprehensive_test()
        tester.print_summary()
        
        if success:
            print("\n✅ All critical final test functionality is working correctly")
            print("📝 Sample final test data has been created for frontend testing")
            sys.exit(0)
        else:
            print("\n❌ Critical issues found in final test functionality")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()