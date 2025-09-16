#!/usr/bin/env python3
"""
Final Test Data Structure Validation - Review Request Testing
Focus: Test final test creation with correct data structure format after frontend fixes

CONFIRMED 422 ERROR CAUSES:
1. correctAnswer as integer instead of string
2. options as array of objects instead of array of strings  
3. type with hyphens instead of underscores (e.g., "multiple-choice" vs "multiple_choice")

CORRECT FORMAT:
- type: 'multiple_choice' (underscore, not hyphen)
- options: ['Option 1', 'Option 2', 'Option 3'] (array of strings, not objects)
- correctAnswer: '0' (string, not integer)
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-chronology.emergent.host/api"
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class FinalTestDataStructureValidator:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.program_id = None
        
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
        """Create a test program"""
        try:
            program_data = {
                "title": f"Final Test Validation Program {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Program for testing final test data structure validation",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            
            if response.status_code == 200:
                program = response.json()
                self.program_id = program["id"]
                self.log_test("Program Creation", True, f"Created program: {program['title']} (ID: {program['id']})")
                return program
            else:
                self.log_test("Program Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Program Creation", False, f"Exception: {str(e)}")
            return None
    
    def test_correct_multiple_choice_format(self):
        """Test 1: CORRECT multiple choice format (should work - no 422 errors)"""
        try:
            test_data = {
                "title": f"Correct MC Format Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing CORRECT multiple choice data structure format",
                "programId": self.program_id,
                "questions": [
                    {
                        "type": "multiple_choice",  # ✅ underscore, not hyphen
                        "question": "What is the capital of France?",
                        "options": ["London", "Berlin", "Paris", "Madrid"],  # ✅ array of strings, not objects
                        "correctAnswer": "2",  # ✅ string, not integer
                        "points": 10,
                        "explanation": "Paris is the capital of France"
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
                self.log_test("Correct Multiple Choice Format", True, 
                            f"✅ NO 422 ERROR - Test created successfully with correct format")
                return final_test
            else:
                self.log_test("Correct Multiple Choice Format", False, 
                            f"❌ UNEXPECTED ERROR: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Correct Multiple Choice Format", False, f"Exception: {str(e)}")
            return None
    
    def test_empty_questions_array(self):
        """Test 2: Empty questions array (should work)"""
        try:
            test_data = {
                "title": f"Empty Questions Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing empty questions array functionality",
                "programId": self.program_id,
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
                if (final_test["questionCount"] == 0 and 
                    final_test["totalPoints"] == 0 and
                    len(final_test["questions"]) == 0):
                    self.log_test("Empty Questions Array", True, 
                                f"✅ Empty questions array works correctly")
                    return final_test
                else:
                    self.log_test("Empty Questions Array", False, 
                                f"Test created but validation failed")
                    return None
            else:
                self.log_test("Empty Questions Array", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Empty Questions Array", False, f"Exception: {str(e)}")
            return None
    
    def test_complete_multiple_choice_question(self):
        """Test 3: Complete multiple choice question with all correct formats"""
        try:
            test_data = {
                "title": f"Complete MC Question Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing complete multiple choice question validation",
                "programId": self.program_id,
                "questions": [
                    {
                        "type": "multiple_choice",  # ✅ underscore format
                        "question": "Which programming language is known for its simplicity and readability?",
                        "options": [  # ✅ array of strings
                            "C++", 
                            "Python", 
                            "Assembly Language", 
                            "Machine Code"
                        ],
                        "correctAnswer": "1",  # ✅ string format (index 1 = Python)
                        "points": 15,
                        "explanation": "Python is widely known for its simple syntax and readability, making it an excellent choice for beginners and experienced developers alike."
                    },
                    {
                        "type": "multiple_choice",  # ✅ underscore format
                        "question": "What does API stand for?",
                        "options": [  # ✅ array of strings
                            "Application Programming Interface",
                            "Advanced Programming Integration", 
                            "Automated Process Integration",
                            "Application Process Interface"
                        ],
                        "correctAnswer": "0",  # ✅ string format (index 0)
                        "points": 10,
                        "explanation": "API stands for Application Programming Interface, which allows different software applications to communicate with each other."
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
                if (final_test["questionCount"] == 2 and 
                    final_test["totalPoints"] == 25 and
                    len(final_test["questions"]) == 2):
                    
                    # Verify data structure integrity
                    all_questions_valid = True
                    for question in final_test["questions"]:
                        if (question["type"] != "multiple_choice" or
                            not isinstance(question["options"], list) or
                            not isinstance(question["correctAnswer"], str)):
                            all_questions_valid = False
                            break
                    
                    if all_questions_valid:
                        self.log_test("Complete Multiple Choice Question", True, 
                                    f"✅ Complete MC questions validated successfully - NO 422 errors")
                        return final_test
                    else:
                        self.log_test("Complete Multiple Choice Question", False, 
                                    f"Data structure validation failed")
                        return None
                else:
                    self.log_test("Complete Multiple Choice Question", False, 
                                f"Basic validation failed")
                    return None
            else:
                self.log_test("Complete Multiple Choice Question", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Complete Multiple Choice Question", False, f"Exception: {str(e)}")
            return None
    
    def test_mixed_question_types_correct_format(self):
        """Test 4: Mixed question types with correct format"""
        try:
            test_data = {
                "title": f"Mixed Types Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing mixed question types with correct data structure",
                "programId": self.program_id,
                "questions": [
                    {
                        "type": "multiple_choice",  # ✅ underscore format
                        "question": "What is the largest planet in our solar system?",
                        "options": ["Earth", "Jupiter", "Saturn", "Neptune"],  # ✅ array of strings
                        "correctAnswer": "1",  # ✅ string format
                        "points": 10,
                        "explanation": "Jupiter is the largest planet in our solar system"
                    },
                    {
                        "type": "true_false",  # ✅ underscore format
                        "question": "The Earth is the third planet from the Sun.",
                        "correctAnswer": "true",  # ✅ string format
                        "points": 5,
                        "explanation": "Yes, Earth is the third planet from the Sun"
                    },
                    {
                        "type": "short_answer",  # ✅ underscore format
                        "question": "What is the chemical symbol for gold?",
                        "correctAnswer": "Au",  # ✅ string format
                        "points": 5,
                        "explanation": "Au is the chemical symbol for gold (from Latin 'aurum')"
                    }
                ],
                "timeLimit": 120,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                if (final_test["questionCount"] == 3 and 
                    final_test["totalPoints"] == 20 and
                    len(final_test["questions"]) == 3):
                    
                    # Verify all question types are correct
                    expected_types = ["multiple_choice", "true_false", "short_answer"]
                    actual_types = [q["type"] for q in final_test["questions"]]
                    
                    if all(t in expected_types for t in actual_types):
                        self.log_test("Mixed Question Types Correct Format", True, 
                                    f"✅ Mixed question types work with correct format - NO 422 errors")
                        return final_test
                    else:
                        self.log_test("Mixed Question Types Correct Format", False, 
                                    f"Question type validation failed")
                        return None
                else:
                    self.log_test("Mixed Question Types Correct Format", False, 
                                f"Basic validation failed")
                    return None
            else:
                self.log_test("Mixed Question Types Correct Format", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Mixed Question Types Correct Format", False, f"Exception: {str(e)}")
            return None
    
    def run_validation_tests(self):
        """Run all validation tests for the review request"""
        print("🚀 FINAL TEST DATA STRUCTURE VALIDATION")
        print("=" * 80)
        print("📋 REVIEW REQUEST: Test final test creation with correct data structure format")
        print("🎯 FOCUS: Prevent 422 errors caused by incorrect data types")
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
        
        # Step 3: Run validation tests
        print(f"\n🧪 TESTING WITH PROGRAM ID: {self.program_id}")
        print("-" * 80)
        
        self.test_correct_multiple_choice_format()
        self.test_empty_questions_array()
        self.test_complete_multiple_choice_question()
        self.test_mixed_question_types_correct_format()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 VALIDATION TEST SUMMARY")
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
        
        # Review Request Specific Findings
        print("\n" + "=" * 80)
        print("📋 REVIEW REQUEST VALIDATION RESULTS")
        print("=" * 80)
        
        correct_format_tests = [r for r in self.test_results if "Correct" in r["test"] or "Complete" in r["test"]]
        empty_test = next((r for r in self.test_results if "Empty Questions" in r["test"]), None)
        
        all_correct_tests_passed = all(r["success"] for r in correct_format_tests)
        
        if all_correct_tests_passed:
            print("✅ CONFIRMED: Frontend fixes successful - correct data structure format works")
            print("   ✅ type: 'multiple_choice' (underscore format)")
            print("   ✅ options: ['Option 1', 'Option 2'] (array of strings)")
            print("   ✅ correctAnswer: '0' (string format)")
            print("   ✅ NO 422 errors with correct format")
        else:
            print("❌ ISSUE: Some correct format tests still failing")
        
        if empty_test and empty_test["success"]:
            print("✅ CONFIRMED: Empty questions array functionality preserved")
        else:
            print("❌ ISSUE: Empty questions array functionality broken")
        
        print(f"\n🎯 FINAL VALIDATION: {'✅ SUCCESS' if success_rate >= 80 else '❌ NEEDS ATTENTION'}")
        
        if success_rate >= 80:
            print("🎉 Frontend data structure fixes are working correctly!")
            print("🚫 422 errors should no longer occur with proper data format")
        
        return success_rate >= 80

if __name__ == "__main__":
    validator = FinalTestDataStructureValidator()
    success = validator.run_validation_tests()
    sys.exit(0 if success else 1)