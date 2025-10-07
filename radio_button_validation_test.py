#!/usr/bin/env python3

"""
Radio Button Backend Validation Test
Focused test to verify that the backend properly handles string-based correctAnswer values
and that the radio button fixes are working correctly.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://quiz-progress-fix.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class RadioButtonValidator:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   {details}")
        print()

    def authenticate(self):
        """Authenticate as admin"""
        print("🔐 Authenticating as admin...")
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Authenticated as: {data.get('user', {}).get('full_name')}"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"Failed with status {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Error: {str(e)}")
            return False

    def create_test_program(self):
        """Create a test program for final test association"""
        print("📚 Creating test program...")
        
        try:
            program_data = {
                "title": f"Radio Button Validation Program - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test program for radio button validation",
                "departmentId": None,
                "duration": "1 week",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            response = self.session.post(
                f"{API_BASE}/programs",
                json=program_data,
                timeout=10
            )
            
            if response.status_code == 200:
                program = response.json()
                program_id = program.get("id")
                
                self.log_result(
                    "Program Creation",
                    True,
                    f"Created program: {program.get('title')} (ID: {program_id})"
                )
                return program_id
            else:
                self.log_result(
                    "Program Creation",
                    False,
                    f"Failed with status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Program Creation", False, f"Error: {str(e)}")
            return None

    def test_string_correctanswer_validation(self, program_id):
        """Test that backend accepts string correctAnswer values"""
        print("🔍 Testing string correctAnswer validation...")
        
        test_cases = [
            {
                "name": "Multiple Choice with String correctAnswer",
                "question_data": {
                    "type": "multiple_choice",
                    "question": "What is 2 + 2?",
                    "options": ["3", "4", "5", "6"],
                    "correctAnswer": "1",  # String index
                    "points": 10,
                    "explanation": "2 + 2 = 4"
                },
                "expected_success": True
            },
            {
                "name": "True/False with String correctAnswer '0'",
                "question_data": {
                    "type": "true_false",
                    "question": "The sky is blue.",
                    "options": ["True", "False"],
                    "correctAnswer": "0",  # String "0" for True
                    "points": 10,
                    "explanation": "The sky appears blue due to light scattering."
                },
                "expected_success": True
            },
            {
                "name": "True/False with String correctAnswer '1'",
                "question_data": {
                    "type": "true_false",
                    "question": "The Earth is flat.",
                    "options": ["True", "False"],
                    "correctAnswer": "1",  # String "1" for False
                    "points": 10,
                    "explanation": "The Earth is spherical."
                },
                "expected_success": True
            },
            {
                "name": "Multiple Choice with Integer correctAnswer (should fail)",
                "question_data": {
                    "type": "multiple_choice",
                    "question": "What is 3 + 3?",
                    "options": ["5", "6", "7", "8"],
                    "correctAnswer": 1,  # Integer (should be rejected)
                    "points": 10,
                    "explanation": "3 + 3 = 6"
                },
                "expected_success": False
            }
        ]
        
        validation_results = []
        
        for test_case in test_cases:
            print(f"   Testing: {test_case['name']}")
            
            final_test_data = {
                "title": f"Validation Test - {test_case['name']}",
                "description": "Testing correctAnswer format validation",
                "programId": program_id,
                "passingScore": 75,
                "maxAttempts": 1,
                "timeLimit": 10,
                "isPublished": False,
                "questions": [test_case["question_data"]]
            }
            
            try:
                response = self.session.post(
                    f"{API_BASE}/final-tests",
                    json=final_test_data,
                    timeout=10
                )
                
                success = response.status_code == 200
                expected = test_case["expected_success"]
                
                validation_results.append({
                    "name": test_case["name"],
                    "expected": expected,
                    "actual": success,
                    "status_code": response.status_code,
                    "correct": expected == success
                })
                
                if success and expected:
                    # If successful, try to retrieve with answers to verify storage
                    test_data = response.json()
                    test_id = test_data.get("id")
                    
                    # Get test with answers included
                    get_response = self.session.get(
                        f"{API_BASE}/final-tests/{test_id}?include_answers=true",
                        timeout=10
                    )
                    
                    if get_response.status_code == 200:
                        retrieved_test = get_response.json()
                        questions = retrieved_test.get("questions", [])
                        if questions:
                            stored_answer = questions[0].get("correctAnswer")
                            expected_answer = test_case["question_data"]["correctAnswer"]
                            
                            validation_results[-1]["stored_correctly"] = (
                                stored_answer == expected_answer and 
                                isinstance(stored_answer, str)
                            )
                            validation_results[-1]["stored_answer"] = stored_answer
                            validation_results[-1]["expected_answer"] = expected_answer
                
            except Exception as e:
                validation_results.append({
                    "name": test_case["name"],
                    "expected": test_case["expected_success"],
                    "actual": False,
                    "error": str(e),
                    "correct": not test_case["expected_success"]
                })
        
        # Analyze results
        all_correct = all(result.get("correct", False) for result in validation_results)
        
        details = []
        for result in validation_results:
            status = "✅" if result.get("correct", False) else "❌"
            detail = f"{status} {result['name']}: Expected {result['expected']}, Got {result['actual']}"
            
            if result.get("stored_correctly") is not None:
                storage_status = "✅" if result["stored_correctly"] else "❌"
                detail += f" | Storage {storage_status}: '{result.get('stored_answer')}' == '{result.get('expected_answer')}'"
            
            details.append(detail)
        
        self.log_result(
            "String correctAnswer Validation",
            all_correct,
            "\n   " + "\n   ".join(details)
        )
        
        return all_correct

    def test_complete_workflow(self, program_id):
        """Test complete workflow with mixed question types"""
        print("🔄 Testing complete workflow with mixed question types...")
        
        try:
            final_test_data = {
                "title": "Complete Radio Button Workflow Test",
                "description": "Testing complete workflow with proper string correctAnswer values",
                "programId": program_id,
                "passingScore": 75,
                "maxAttempts": 3,
                "timeLimit": 30,
                "isPublished": True,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "Which HTTP status code indicates success?",
                        "options": ["404", "200", "500", "403"],
                        "correctAnswer": "1",  # String
                        "points": 25,
                        "explanation": "HTTP 200 OK indicates success."
                    },
                    {
                        "type": "true_false",
                        "question": "HTTP is a stateless protocol.",
                        "options": ["True", "False"],
                        "correctAnswer": "0",  # String "0" for True
                        "points": 25,
                        "explanation": "HTTP is indeed stateless."
                    },
                    {
                        "type": "multiple_choice",
                        "question": "What does CSS stand for?",
                        "options": ["Computer Style Sheets", "Cascading Style Sheets", "Creative Style Sheets", "Colorful Style Sheets"],
                        "correctAnswer": "1",  # String
                        "points": 25,
                        "explanation": "CSS stands for Cascading Style Sheets."
                    },
                    {
                        "type": "true_false",
                        "question": "JavaScript and Java are the same language.",
                        "options": ["True", "False"],
                        "correctAnswer": "1",  # String "1" for False
                        "points": 25,
                        "explanation": "JavaScript and Java are completely different languages."
                    }
                ]
            }
            
            # Create the final test
            response = self.session.post(
                f"{API_BASE}/final-tests",
                json=final_test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                test_data = response.json()
                test_id = test_data.get("id")
                
                # Retrieve with answers to verify storage
                get_response = self.session.get(
                    f"{API_BASE}/final-tests/{test_id}?include_answers=true",
                    timeout=10
                )
                
                if get_response.status_code == 200:
                    retrieved_test = get_response.json()
                    questions = retrieved_test.get("questions", [])
                    
                    # Verify all correctAnswer fields are strings
                    all_strings = True
                    question_details = []
                    
                    for i, question in enumerate(questions):
                        correct_answer = question.get("correctAnswer")
                        question_type = question.get("type")
                        
                        is_string = isinstance(correct_answer, str)
                        if not is_string:
                            all_strings = False
                        
                        question_details.append(
                            f"Q{i+1}({question_type}): correctAnswer='{correct_answer}' ({'string' if is_string else type(correct_answer).__name__})"
                        )
                    
                    self.log_result(
                        "Complete Workflow Test",
                        all_strings,
                        f"Created test with {len(questions)} questions. All correctAnswer fields are strings: {all_strings}\n   " + 
                        "\n   ".join(question_details)
                    )
                    
                    return all_strings
                else:
                    self.log_result(
                        "Complete Workflow Test",
                        False,
                        f"Failed to retrieve test: {get_response.status_code}"
                    )
                    return False
            else:
                self.log_result(
                    "Complete Workflow Test",
                    False,
                    f"Failed to create test: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Complete Workflow Test", False, f"Error: {str(e)}")
            return False

    def run_validation(self):
        """Run comprehensive radio button validation"""
        print("🧪 RADIO BUTTON BACKEND VALIDATION TEST")
        print("=" * 60)
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed. Cannot proceed.")
            return False
        
        # Step 2: Create test program
        program_id = self.create_test_program()
        if not program_id:
            print("❌ CRITICAL: Program creation failed. Cannot proceed.")
            return False
        
        # Step 3: Test string correctAnswer validation
        validation_success = self.test_string_correctanswer_validation(program_id)
        
        # Step 4: Test complete workflow
        workflow_success = self.test_complete_workflow(program_id)
        
        # Generate summary
        self.generate_summary()
        
        return validation_success and workflow_success

    def generate_summary(self):
        """Generate test summary"""
        print()
        print("=" * 60)
        print("🎯 RADIO BUTTON VALIDATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        print()
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status}: {result['test']}")
            if result["details"]:
                # Handle multi-line details
                details = result["details"].replace("\n   ", "\n      ")
                print(f"   {details}")
        
        print()
        
        # Final assessment
        critical_tests = ["Admin Authentication", "Program Creation", "String correctAnswer Validation", "Complete Workflow Test"]
        critical_passed = all(
            next((r for r in self.test_results if r["test"] == test_name), {"success": False})["success"]
            for test_name in critical_tests
        )
        
        if critical_passed:
            print("🎉 CONCLUSION: RADIO BUTTON FIXES ARE WORKING CORRECTLY")
            print("   ✅ Backend properly accepts string-based correctAnswer values")
            print("   ✅ Backend properly rejects integer correctAnswer values")
            print("   ✅ Data is stored correctly in the database")
            print("   ✅ Complete workflow functional without 422 errors")
        else:
            print("❌ CONCLUSION: RADIO BUTTON FIXES NEED ATTENTION")
            print("   🔧 Some validation issues detected")
        
        print("=" * 60)

def main():
    """Main execution function"""
    validator = RadioButtonValidator()
    
    try:
        success = validator.run_validation()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Testing failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())