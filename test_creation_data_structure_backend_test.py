#!/usr/bin/env python3
"""
Backend Testing Script for LearningFriend LMS
Focus: Test Creation Data Structure Format Validation

Review Request Testing:
Test final test creation with the correct data structure format after frontend fixes. 
The issue was data type mismatch between frontend and backend:

1. Test final test creation with proper question format:
   - type: 'multiple_choice' (underscore, not hyphen)
   - options: ['Option 1', 'Option 2', 'Option 3'] (array of strings, not objects)
   - correctAnswer: '0' (string, not integer)

2. Test with a complete multiple choice question to verify validation passes
3. Test with empty questions array to ensure that still works

Admin credentials: brayden.t@covesmart.com / Hawaii2020!
The user was getting 422 errors because frontend was sending incorrect data format.
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration - Using correct backend URL from frontend/.env
BACKEND_URL = "https://lms-chronology.emergent.host/api"

# Test credentials
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class TestCreationDataStructureTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.test_program_id = None
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                self.log_test("Admin Authentication", True, f"Logged in as {data['user']['full_name']}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def create_test_program(self):
        """Create a test program for final test association"""
        try:
            program_data = {
                "title": f"Data Structure Test Program {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test program for data structure validation testing",
                "departmentId": None,
                "duration": "2 weeks",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            
            if response.status_code == 200:
                program = response.json()
                self.test_program_id = program["id"]
                self.log_test("Program Creation", True, f"Created program: {program['title']} (ID: {program['id']})")
                return program
            else:
                self.log_test("Program Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Program Creation", False, f"Exception: {str(e)}")
            return None
    
    def test_correct_multiple_choice_format(self):
        """Test 1: Test creation with CORRECT multiple choice data format"""
        try:
            test_data = {
                "title": f"Correct Format Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing with correct data structure format",
                "programId": self.test_program_id,
                "questions": [
                    {
                        "type": "multiple_choice",  # underscore, not hyphen
                        "question": "What is the capital of France?",
                        "options": ["London", "Berlin", "Paris", "Madrid"],  # array of strings, not objects
                        "correctAnswer": "2",  # string, not integer
                        "points": 10,
                        "explanation": "Paris is the capital of France"
                    },
                    {
                        "type": "multiple_choice",  # underscore, not hyphen
                        "question": "Which programming language is known for its simplicity?",
                        "options": ["C++", "Python", "Assembly", "Java"],  # array of strings, not objects
                        "correctAnswer": "1",  # string, not integer
                        "points": 10,
                        "explanation": "Python is known for its simplicity and readability"
                    }
                ],
                "timeLimit": 60,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                
                # Verify the test was created correctly with proper data structure
                if (final_test["questionCount"] == 2 and 
                    final_test["totalPoints"] == 20 and
                    final_test["programId"] == self.test_program_id and
                    len(final_test["questions"]) == 2):
                    
                    # Check that questions have correct format
                    question1 = final_test["questions"][0]
                    question2 = final_test["questions"][1]
                    
                    format_correct = (
                        question1["type"] == "multiple_choice" and
                        isinstance(question1["options"], list) and
                        isinstance(question1["correctAnswer"], str) and
                        question2["type"] == "multiple_choice" and
                        isinstance(question2["options"], list) and
                        isinstance(question2["correctAnswer"], str)
                    )
                    
                    if format_correct:
                        self.log_test("Correct Multiple Choice Format", True, 
                                    f"Created test with correct data format - NO 422 errors")
                        return final_test
                    else:
                        self.log_test("Correct Multiple Choice Format", False, 
                                    f"Test created but data format validation failed")
                        return None
                else:
                    self.log_test("Correct Multiple Choice Format", False, 
                                f"Test created but basic validation failed: {final_test}")
                    return None
            else:
                self.log_test("Correct Multiple Choice Format", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Correct Multiple Choice Format", False, f"Exception: {str(e)}")
            return None
    
    def test_empty_questions_array(self):
        """Test 2: Test creation with empty questions array (should work)"""
        try:
            test_data = {
                "title": f"Empty Questions Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing with empty questions array",
                "programId": self.test_program_id,
                "questions": [],  # Empty questions array
                "timeLimit": 60,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": False
            }
            
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                
                # Verify the test was created correctly with empty questions
                if (final_test["questionCount"] == 0 and 
                    final_test["totalPoints"] == 0 and
                    final_test["programId"] == self.test_program_id and
                    len(final_test["questions"]) == 0):
                    self.log_test("Empty Questions Array", True, 
                                f"Successfully created test with empty questions array")
                    return final_test
                else:
                    self.log_test("Empty Questions Array", False, 
                                f"Test created but validation failed: {final_test}")
                    return None
            else:
                self.log_test("Empty Questions Array", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Empty Questions Array", False, f"Exception: {str(e)}")
            return None
    
    def test_course_creation_with_correct_format(self):
        """Test 3: Course creation with correct multiple choice format"""
        try:
            course_data = {
                "title": f"Test Course Correct Format {datetime.now().strftime('%H%M%S')}",
                "description": "Testing course creation with correct question format",
                "category": "Technology",
                "duration": "2 hours",
                "accessType": "open",
                "learningOutcomes": ["Learn correct data formats"],
                "modules": [
                    {
                        "title": "Quiz Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Multiple Choice Quiz",
                                "type": "quiz",
                                "content": "",
                                "questions": [
                                    {
                                        "type": "multiple_choice",  # underscore, not hyphen
                                        "question": "What is the correct format for options?",
                                        "options": ["Array of objects", "Array of strings", "Single string", "Number"],  # array of strings
                                        "correctAnswer": "1",  # string, not integer
                                        "points": 10,
                                        "explanation": "Options should be an array of strings"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/courses", json=course_data)
            
            if response.status_code == 200:
                course = response.json()
                
                # Verify the course was created correctly
                if (course["title"].startswith("Test Course Correct Format") and
                    len(course["modules"]) == 1 and
                    len(course["modules"][0]["lessons"]) == 1):
                    
                    lesson = course["modules"][0]["lessons"][0]
                    if (lesson["type"] == "quiz" and 
                        len(lesson["questions"]) == 1):
                        
                        question = lesson["questions"][0]
                        format_correct = (
                            question["type"] == "multiple_choice" and
                            isinstance(question["options"], list) and
                            isinstance(question["correctAnswer"], str)
                        )
                        
                        if format_correct:
                            self.log_test("Course Creation Correct Format", True, 
                                        f"Created course with correct quiz format")
                            return course
                        else:
                            self.log_test("Course Creation Correct Format", False, 
                                        f"Course created but question format validation failed")
                            return None
                else:
                    self.log_test("Course Creation Correct Format", False, 
                                f"Course created but structure validation failed")
                    return None
            else:
                self.log_test("Course Creation Correct Format", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Course Creation Correct Format", False, f"Exception: {str(e)}")
            return None
    
    def test_mixed_question_types_correct_format(self):
        """Test 4: Test creation with mixed question types in correct format"""
        try:
            test_data = {
                "title": f"Mixed Types Correct Format Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing with mixed question types in correct format",
                "programId": self.test_program_id,
                "questions": [
                    {
                        "type": "multiple_choice",  # correct underscore
                        "question": "What is the largest planet?",
                        "options": ["Earth", "Jupiter", "Saturn", "Mars"],  # array of strings
                        "correctAnswer": "1",  # string
                        "points": 10,
                        "explanation": "Jupiter is the largest planet"
                    },
                    {
                        "type": "true_false",  # correct underscore
                        "question": "The Earth is flat.",
                        "correctAnswer": "false",  # string
                        "points": 5,
                        "explanation": "The Earth is round"
                    },
                    {
                        "type": "short_answer",  # correct underscore
                        "question": "What is the chemical symbol for water?",
                        "correctAnswer": "H2O",  # string
                        "points": 5,
                        "explanation": "Water is H2O"
                    }
                ],
                "timeLimit": 90,
                "maxAttempts": 3,
                "passingScore": 70.0,
                "shuffleQuestions": True,
                "showResults": True,
                "isPublished": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                
                # Verify the test was created correctly
                if (final_test["questionCount"] == 3 and 
                    final_test["totalPoints"] == 20 and
                    len(final_test["questions"]) == 3):
                    
                    # Check that all question types are correct
                    types_correct = all(
                        q["type"] in ["multiple_choice", "true_false", "short_answer"] 
                        for q in final_test["questions"]
                    )
                    
                    if types_correct:
                        self.log_test("Mixed Question Types Correct Format", True, 
                                    f"Successfully created test with mixed question types")
                        return final_test
                    else:
                        self.log_test("Mixed Question Types Correct Format", False, 
                                    f"Question types validation failed")
                        return None
                else:
                    self.log_test("Mixed Question Types Correct Format", False, 
                                f"Test created but validation failed: {final_test}")
                    return None
            else:
                self.log_test("Mixed Question Types Correct Format", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Mixed Question Types Correct Format", False, f"Exception: {str(e)}")
            return None
    
    def run_all_tests(self):
        """Run all data structure validation tests"""
        print("🚀 Starting LearningFriend LMS Test Creation Data Structure Testing")
        print("=" * 80)
        print("Focus: Validating correct data structure format to prevent 422 errors")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Create test program
        program = self.create_test_program()
        if not program:
            print("❌ Program creation failed. Cannot proceed with tests.")
            return False
        
        # Step 3: Test correct multiple choice format
        self.test_correct_multiple_choice_format()
        
        # Step 4: Test empty questions array
        self.test_empty_questions_array()
        
        # Step 5: Test course creation with correct format
        self.test_course_creation_with_correct_format()
        
        # Step 6: Test mixed question types with correct format
        self.test_mixed_question_types_correct_format()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY - DATA STRUCTURE VALIDATION")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests < total_tests:
            print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🎯 Data Structure Validation: {'✅ WORKING' if success_rate >= 80 else '❌ NEEDS ATTENTION'}")
        
        # Specific findings for the review request
        print("\n" + "=" * 80)
        print("📋 REVIEW REQUEST FINDINGS")
        print("=" * 80)
        
        correct_format_test = next((r for r in self.test_results if "Correct Multiple Choice Format" in r["test"]), None)
        empty_questions_test = next((r for r in self.test_results if "Empty Questions Array" in r["test"]), None)
        
        if correct_format_test and correct_format_test["success"]:
            print("✅ FIXED: Test creation with correct data structure format works (no 422 errors)")
            print("   - type: 'multiple_choice' (underscore) ✅")
            print("   - options: ['Option 1', 'Option 2'] (array of strings) ✅")
            print("   - correctAnswer: '0' (string) ✅")
        else:
            print("❌ ISSUE: Test creation with correct format still failing")
        
        if empty_questions_test and empty_questions_test["success"]:
            print("✅ CONFIRMED: Empty questions array still works as expected")
        else:
            print("❌ ISSUE: Empty questions array functionality broken")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = TestCreationDataStructureTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)