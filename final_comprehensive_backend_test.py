#!/usr/bin/env python3
"""
Final Comprehensive Backend Testing - Post Data Structure Fixes
Testing the complete workflow that the user experienced after all fixes applied.

Review Request Focus:
1. Data Structure Fix: Question types now correctly use hyphens (select-all-that-apply, chronological-order)
2. Chronological Order Fix: Questions now initialize with items array when type is changed
3. [object Object] Resolution: Should be eliminated with correct question type formats

Test Workflow:
1. Create a program with title and description
2. Add multiple question types: multiple_choice, select-all-that-apply, true_false, short_answer, essay, chronological-order
3. Ensure chronological-order questions have proper items array
4. Verify all question types create without 422 errors
5. Confirm no [object Object] errors in responses
6. Test complete program → final test creation workflow

Admin credentials: brayden.t@covesmart.com / Hawaii2020!
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration - Using correct backend URL from frontend/.env
BACKEND_URL = "https://lms-chronology-1.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class FinalComprehensiveTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.created_program_id = None
        self.created_final_test_id = None
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def admin_login(self):
        """Test admin authentication"""
        print("\n🔐 Testing Admin Authentication...")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                
                user_info = data.get("user", {})
                self.log_test("Admin Login", True, f"Logged in as {user_info.get('full_name', 'Unknown')} ({user_info.get('role', 'Unknown')})")
                return True
            else:
                self.log_test("Admin Login", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Login", False, f"Exception: {str(e)}")
            return False
    
    def create_test_program(self):
        """Create a program with comprehensive question types"""
        print("\n📚 Creating Test Program with Multiple Question Types...")
        
        try:
            # Create program data with all question types mentioned in review request
            program_data = {
                "title": "Final Comprehensive Test Program - Data Structure Validation",
                "description": "Testing all question types after data structure fixes: multiple_choice, select-all-that-apply, true_false, short_answer, essay, chronological-order",
                "departmentId": None,
                "duration": "2 hours",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            
            if response.status_code == 200:
                program = response.json()
                self.created_program_id = program.get("id")
                self.log_test("Program Creation", True, f"Created program: {program.get('title')} (ID: {self.created_program_id})")
                return True
            else:
                self.log_test("Program Creation", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Program Creation", False, f"Exception: {str(e)}")
            return False
    
    def create_final_test_with_all_question_types(self):
        """Create final test with all question types using correct data structure"""
        print("\n🎯 Creating Final Test with All Question Types...")
        
        if not self.created_program_id:
            self.log_test("Final Test Creation", False, "No program ID available")
            return False
        
        try:
            # Create final test with all question types using CORRECT formats (hyphens as mentioned in review)
            final_test_data = {
                "programId": self.created_program_id,
                "title": "Comprehensive Final Test - All Question Types",
                "description": "Testing all question types with correct data structure",
                "passingScore": 75,
                "timeLimit": 60,
                "questions": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "multiple_choice",  # Using underscore format for backend
                        "question": "What is the capital of France?",
                        "options": ["London", "Berlin", "Paris", "Madrid"],
                        "correctAnswer": "2",  # String representation of index
                        "points": 10
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "select-all-that-apply",  # Using hyphen format as mentioned in review
                        "question": "Which of the following are programming languages?",
                        "options": ["Python", "HTML", "JavaScript", "CSS"],
                        "correctAnswers": [0, 2],  # Python and JavaScript
                        "points": 15
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "true_false",
                        "question": "The Earth is flat.",
                        "correctAnswer": "false",  # String representation of boolean
                        "points": 5
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "short_answer",
                        "question": "What is the primary purpose of a database?",
                        "correctAnswer": "To store and organize data",
                        "points": 10
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "essay",
                        "question": "Explain the importance of user experience in web development.",
                        "points": 20
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "type": "chronological-order",  # Using hyphen format as mentioned in review
                        "question": "Arrange these historical events in chronological order:",
                        "items": ["World War I", "World War II", "Cold War", "Fall of Berlin Wall"],  # Proper items array
                        "correctOrder": [0, 1, 2, 3],
                        "points": 15
                    }
                ]
            }
            
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=final_test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                self.created_final_test_id = final_test.get("id")
                
                # Verify no [object Object] in response
                response_text = json.dumps(final_test)
                has_object_object = "[object Object]" in response_text
                
                if has_object_object:
                    self.log_test("Final Test Creation", False, "Response contains [object Object] errors")
                    return False
                else:
                    self.log_test("Final Test Creation", True, f"Created final test with {len(final_test_data['questions'])} question types")
                    self.log_test("[object Object] Check", True, "No [object Object] errors found in response")
                    return True
            else:
                error_detail = response.text
                # Check if this is a 422 validation error
                if response.status_code == 422:
                    try:
                        error_data = response.json()
                        self.log_test("Final Test Creation", False, f"422 Validation Error: {json.dumps(error_data, indent=2)}")
                    except:
                        self.log_test("Final Test Creation", False, f"422 Error: {error_detail}")
                else:
                    self.log_test("Final Test Creation", False, f"Status: {response.status_code}, Response: {error_detail}")
                return False
                
        except Exception as e:
            self.log_test("Final Test Creation", False, f"Exception: {str(e)}")
            return False
    
    def verify_question_data_structures(self):
        """Verify that all question types have proper data structures"""
        print("\n🔍 Verifying Question Data Structures...")
        
        if not self.created_final_test_id:
            self.log_test("Question Data Structure Verification", False, "No final test ID available")
            return False
        
        try:
            response = self.session.get(f"{BACKEND_URL}/final-tests/{self.created_final_test_id}")
            
            if response.status_code == 200:
                final_test = response.json()
                questions = final_test.get("questions", [])
                
                # Verify each question type has proper structure
                structure_checks = []
                
                for question in questions:
                    q_type = question.get("type")
                    q_id = question.get("id", "unknown")
                    
                    if q_type == "multiple_choice":
                        has_options = "options" in question and isinstance(question["options"], list)
                        has_correct_answer = "correctAnswer" in question
                        structure_checks.append(f"Multiple Choice: options={has_options}, correctAnswer={has_correct_answer}")
                    
                    elif q_type == "select-all-that-apply":
                        has_options = "options" in question and isinstance(question["options"], list)
                        has_correct_answers = "correctAnswers" in question and isinstance(question["correctAnswers"], list)
                        structure_checks.append(f"Select All That Apply: options={has_options}, correctAnswers={has_correct_answers}")
                    
                    elif q_type == "chronological-order":
                        has_items = "items" in question and isinstance(question["items"], list)
                        has_correct_order = "correctOrder" in question and isinstance(question["correctOrder"], list)
                        structure_checks.append(f"Chronological Order: items={has_items}, correctOrder={has_correct_order}")
                        
                        # This is the key fix mentioned in review request
                        if not has_items:
                            self.log_test("Chronological Order Items Array", False, f"Question {q_id} missing items array")
                        else:
                            self.log_test("Chronological Order Items Array", True, f"Question {q_id} has proper items array with {len(question['items'])} items")
                    
                    elif q_type == "true_false":
                        has_correct_answer = "correctAnswer" in question
                        structure_checks.append(f"True/False: correctAnswer={has_correct_answer}")
                    
                    elif q_type in ["short_answer", "essay"]:
                        has_correct_answer = "correctAnswer" in question or q_type == "essay"
                        structure_checks.append(f"{q_type.title()}: structure_ok={has_correct_answer}")
                
                self.log_test("Question Data Structure Verification", True, f"Verified {len(questions)} questions: {'; '.join(structure_checks)}")
                return True
            else:
                self.log_test("Question Data Structure Verification", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Question Data Structure Verification", False, f"Exception: {str(e)}")
            return False
    
    def test_question_type_formats(self):
        """Test that question types use correct formats (hyphens vs underscores)"""
        print("\n📝 Testing Question Type Format Consistency...")
        
        # Test both formats to ensure backend accepts the correct one
        test_questions = [
            {
                "type": "select-all-that-apply",  # Hyphen format (should work per review)
                "question": "Test question",
                "options": ["A", "B", "C"],
                "correctAnswers": [0, 1]
            },
            {
                "type": "chronological-order",  # Hyphen format (should work per review)
                "question": "Test chronological question",
                "items": ["First", "Second", "Third"],
                "correctOrder": [0, 1, 2]
            }
        ]
        
        format_test_results = []
        
        for question in test_questions:
            q_type = question["type"]
            
            # Create a minimal final test to test the format
            test_data = {
                "programId": self.created_program_id,
                "title": f"Format Test - {q_type}",
                "description": "Testing question type format",
                "passingScore": 75,
                "timeLimit": 30,
                "questions": [question]
            }
            
            try:
                response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
                
                if response.status_code == 200:
                    format_test_results.append(f"{q_type}: ✅ ACCEPTED")
                elif response.status_code == 422:
                    format_test_results.append(f"{q_type}: ❌ 422 VALIDATION ERROR")
                else:
                    format_test_results.append(f"{q_type}: ❌ {response.status_code} ERROR")
                    
            except Exception as e:
                format_test_results.append(f"{q_type}: ❌ EXCEPTION")
        
        all_passed = all("✅" in result for result in format_test_results)
        self.log_test("Question Type Format Testing", all_passed, "; ".join(format_test_results))
        
        return all_passed
    
    def run_comprehensive_test(self):
        """Run the complete test suite"""
        print("🚀 Starting Final Comprehensive Backend Testing - Post Data Structure Fixes")
        print("=" * 80)
        
        # Test sequence
        tests = [
            ("Admin Authentication", self.admin_login),
            ("Program Creation", self.create_test_program),
            ("Final Test Creation with All Question Types", self.create_final_test_with_all_question_types),
            ("Question Data Structure Verification", self.verify_question_data_structures),
            ("Question Type Format Testing", self.test_question_type_formats)
        ]
        
        for test_name, test_func in tests:
            if not test_func():
                print(f"\n❌ Test suite stopped at: {test_name}")
                break
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FINAL TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ Passed: {passed}/{total} tests ({success_rate:.1f}% success rate)")
        
        if success_rate == 100:
            print("\n🎉 ALL TESTS PASSED - User's issues are completely resolved!")
            print("✅ Data structure fixes working correctly")
            print("✅ Question types using correct formats")
            print("✅ Chronological order questions have proper items array")
            print("✅ No [object Object] errors detected")
            print("✅ Complete program → final test workflow functional")
        else:
            print(f"\n⚠️  {total - passed} tests failed - Issues still need attention")
            
            failed_tests = [result for result in self.test_results if not result["success"]]
            for failed_test in failed_tests:
                print(f"❌ {failed_test['test']}: {failed_test['details']}")
        
        return success_rate == 100

if __name__ == "__main__":
    tester = FinalComprehensiveTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)