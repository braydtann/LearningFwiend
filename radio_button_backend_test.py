#!/usr/bin/env python3

"""
Backend Testing Script for Final Test Creation with Radio Button Fixes
Testing the backend functionality for final test creation with proper radio button selections.

Focus Areas:
1. Admin authentication with specified credentials
2. Program creation with final test questions
3. Multiple choice questions with string correctAnswer
4. True/false questions with string correctAnswer ("0" or "1")
5. Backend validation for string-based correctAnswer values
6. Complete program creation workflow
7. Data structure compatibility verification
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://lms-analytics-hub.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_admin(self):
        """Test admin authentication with specified credentials"""
        print("🔐 Testing Admin Authentication...")
        
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.admin_user = data.get("user")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                
                self.log_test(
                    "Admin Authentication",
                    True,
                    f"Admin logged in: {self.admin_user.get('full_name')}, Role: {self.admin_user.get('role')}"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication",
                    False,
                    f"Login failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Admin Authentication",
                False,
                f"Authentication error: {str(e)}"
            )
            return False

    def test_program_creation(self):
        """Test program creation for final test association"""
        print("📚 Testing Program Creation...")
        
        try:
            program_data = {
                "title": f"Radio Button Test Program - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test program for radio button functionality validation in final tests",
                "departmentId": None,
                "duration": "2 weeks",
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
                
                self.log_test(
                    "Program Creation",
                    True,
                    f"Program created successfully: {program.get('title')} (ID: {program_id})"
                )
                return program_id
            else:
                self.log_test(
                    "Program Creation",
                    False,
                    f"Program creation failed with status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Program Creation",
                False,
                f"Program creation error: {str(e)}"
            )
            return None

    def test_multiple_choice_final_test(self, program_id):
        """Test final test creation with multiple choice questions (string correctAnswer)"""
        print("🔘 Testing Multiple Choice Final Test Creation...")
        
        try:
            # Multiple choice question with string correctAnswer
            final_test_data = {
                "title": "Multiple Choice Radio Button Test",
                "description": "Testing multiple choice questions with string correctAnswer",
                "programId": program_id,
                "passingScore": 75,
                "maxAttempts": 3,
                "timeLimit": 60,
                "isPublished": True,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is the capital of Hawaii?",
                        "options": ["Honolulu", "Maui", "Kauai", "Big Island"],
                        "correctAnswer": "0",  # String type as required by radio button fixes
                        "points": 10,
                        "explanation": "Honolulu is the capital and largest city of Hawaii."
                    },
                    {
                        "type": "multiple_choice", 
                        "question": "Which programming language is known for web development?",
                        "options": ["Python", "JavaScript", "C++", "Assembly"],
                        "correctAnswer": "1",  # String type as required
                        "points": 10,
                        "explanation": "JavaScript is primarily used for web development."
                    }
                ]
            }
            
            response = self.session.post(
                f"{API_BASE}/final-tests",
                json=final_test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                final_test = response.json()
                test_id = final_test.get("id")
                
                # Verify data structure
                questions = final_test.get("questions", [])
                all_correct_format = True
                format_details = []
                
                for i, question in enumerate(questions):
                    correct_answer = question.get("correctAnswer")
                    question_type = question.get("type")
                    
                    # Verify correctAnswer is string type
                    if isinstance(correct_answer, str):
                        format_details.append(f"Question {i+1}: correctAnswer='{correct_answer}' (string) ✅")
                    else:
                        format_details.append(f"Question {i+1}: correctAnswer={correct_answer} ({type(correct_answer).__name__}) ❌")
                        all_correct_format = False
                
                self.log_test(
                    "Multiple Choice Final Test Creation",
                    True,
                    f"Final test created: {final_test.get('title')} (ID: {test_id}). " +
                    f"Questions: {len(questions)}. Format validation: {'; '.join(format_details)}"
                )
                
                # Test data structure compatibility
                self.log_test(
                    "Multiple Choice Data Structure Validation",
                    all_correct_format,
                    f"All correctAnswer fields are strings: {all_correct_format}"
                )
                
                return test_id
            else:
                self.log_test(
                    "Multiple Choice Final Test Creation",
                    False,
                    f"Final test creation failed with status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Multiple Choice Final Test Creation",
                False,
                f"Final test creation error: {str(e)}"
            )
            return None

    def test_true_false_final_test(self, program_id):
        """Test final test creation with true/false questions (string correctAnswer)"""
        print("✅ Testing True/False Final Test Creation...")
        
        try:
            # True/false question with string correctAnswer
            final_test_data = {
                "title": "True/False Radio Button Test",
                "description": "Testing true/false questions with string correctAnswer",
                "programId": program_id,
                "passingScore": 75,
                "maxAttempts": 3,
                "timeLimit": 30,
                "isPublished": True,
                "questions": [
                    {
                        "type": "true_false",
                        "question": "Hawaii is the 50th state of the United States.",
                        "options": ["True", "False"],
                        "correctAnswer": "0",  # String "0" for True
                        "points": 15,
                        "explanation": "Hawaii became the 50th state on August 21, 1959."
                    },
                    {
                        "type": "true_false",
                        "question": "JavaScript is a compiled programming language.",
                        "options": ["True", "False"],
                        "correctAnswer": "1",  # String "1" for False
                        "points": 15,
                        "explanation": "JavaScript is an interpreted language, not compiled."
                    }
                ]
            }
            
            response = self.session.post(
                f"{API_BASE}/final-tests",
                json=final_test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                final_test = response.json()
                test_id = final_test.get("id")
                
                # Verify data structure
                questions = final_test.get("questions", [])
                all_correct_format = True
                format_details = []
                
                for i, question in enumerate(questions):
                    correct_answer = question.get("correctAnswer")
                    question_type = question.get("type")
                    
                    # Verify correctAnswer is string type and valid value
                    if isinstance(correct_answer, str) and correct_answer in ["0", "1"]:
                        format_details.append(f"Question {i+1}: correctAnswer='{correct_answer}' (valid string) ✅")
                    else:
                        format_details.append(f"Question {i+1}: correctAnswer={correct_answer} (invalid format) ❌")
                        all_correct_format = False
                
                self.log_test(
                    "True/False Final Test Creation",
                    True,
                    f"Final test created: {final_test.get('title')} (ID: {test_id}). " +
                    f"Questions: {len(questions)}. Format validation: {'; '.join(format_details)}"
                )
                
                # Test data structure compatibility
                self.log_test(
                    "True/False Data Structure Validation",
                    all_correct_format,
                    f"All correctAnswer fields are valid strings ('0' or '1'): {all_correct_format}"
                )
                
                return test_id
            else:
                self.log_test(
                    "True/False Final Test Creation",
                    False,
                    f"Final test creation failed with status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "True/False Final Test Creation",
                False,
                f"Final test creation error: {str(e)}"
            )
            return None

    def test_mixed_question_types_final_test(self, program_id):
        """Test final test creation with both multiple choice and true/false questions"""
        print("🔀 Testing Mixed Question Types Final Test Creation...")
        
        try:
            # Mixed question types with string correctAnswer
            final_test_data = {
                "title": "Mixed Radio Button Test",
                "description": "Testing mixed question types with string correctAnswer values",
                "programId": program_id,
                "passingScore": 75,
                "maxAttempts": 3,
                "timeLimit": 45,
                "isPublished": True,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "Which HTTP status code indicates success?",
                        "options": ["404", "200", "500", "403"],
                        "correctAnswer": "1",  # String type
                        "points": 20,
                        "explanation": "HTTP 200 indicates a successful request."
                    },
                    {
                        "type": "true_false",
                        "question": "HTTP is a stateless protocol.",
                        "options": ["True", "False"],
                        "correctAnswer": "0",  # String "0" for True
                        "points": 20,
                        "explanation": "HTTP is indeed a stateless protocol."
                    },
                    {
                        "type": "multiple_choice",
                        "question": "What does API stand for?",
                        "options": ["Application Programming Interface", "Advanced Programming Interface", "Automated Programming Interface", "Application Process Interface"],
                        "correctAnswer": "0",  # String type
                        "points": 20,
                        "explanation": "API stands for Application Programming Interface."
                    },
                    {
                        "type": "true_false",
                        "question": "JSON stands for JavaScript Object Notation.",
                        "options": ["True", "False"],
                        "correctAnswer": "0",  # String "0" for True
                        "points": 20,
                        "explanation": "JSON does stand for JavaScript Object Notation."
                    }
                ]
            }
            
            response = self.session.post(
                f"{API_BASE}/final-tests",
                json=final_test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                final_test = response.json()
                test_id = final_test.get("id")
                
                # Verify data structure
                questions = final_test.get("questions", [])
                all_correct_format = True
                format_details = []
                question_type_counts = {"multiple_choice": 0, "true_false": 0}
                
                for i, question in enumerate(questions):
                    correct_answer = question.get("correctAnswer")
                    question_type = question.get("type")
                    
                    # Count question types
                    if question_type in question_type_counts:
                        question_type_counts[question_type] += 1
                    
                    # Verify correctAnswer is string type
                    if isinstance(correct_answer, str):
                        format_details.append(f"Q{i+1}({question_type}): correctAnswer='{correct_answer}' ✅")
                    else:
                        format_details.append(f"Q{i+1}({question_type}): correctAnswer={correct_answer} ❌")
                        all_correct_format = False
                
                self.log_test(
                    "Mixed Question Types Final Test Creation",
                    True,
                    f"Final test created: {final_test.get('title')} (ID: {test_id}). " +
                    f"Questions: {len(questions)} (MC: {question_type_counts['multiple_choice']}, TF: {question_type_counts['true_false']}). " +
                    f"Format: {'; '.join(format_details)}"
                )
                
                # Test comprehensive data structure compatibility
                self.log_test(
                    "Mixed Question Types Data Structure Validation",
                    all_correct_format,
                    f"All correctAnswer fields are strings across mixed question types: {all_correct_format}"
                )
                
                return test_id
            else:
                self.log_test(
                    "Mixed Question Types Final Test Creation",
                    False,
                    f"Final test creation failed with status {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Mixed Question Types Final Test Creation",
                False,
                f"Final test creation error: {str(e)}"
            )
            return None

    def test_backend_validation_compatibility(self, program_id):
        """Test backend validation for string-based correctAnswer values"""
        print("🔍 Testing Backend Validation Compatibility...")
        
        try:
            # Test with various correctAnswer formats to ensure backend accepts strings
            test_cases = [
                {
                    "name": "String correctAnswer",
                    "data": {
                        "type": "multiple_choice",
                        "question": "Test question with string correctAnswer",
                        "options": ["Option A", "Option B", "Option C"],
                        "correctAnswer": "1",  # String
                        "points": 10
                    },
                    "should_pass": True
                },
                {
                    "name": "Integer correctAnswer (should fail if validation is strict)",
                    "data": {
                        "type": "multiple_choice", 
                        "question": "Test question with integer correctAnswer",
                        "options": ["Option A", "Option B", "Option C"],
                        "correctAnswer": 1,  # Integer
                        "points": 10
                    },
                    "should_pass": False  # Based on radio button fixes, should require string
                }
            ]
            
            validation_results = []
            
            for test_case in test_cases:
                final_test_data = {
                    "title": f"Validation Test - {test_case['name']}",
                    "description": "Testing backend validation for correctAnswer format",
                    "programId": program_id,
                    "passingScore": 75,
                    "maxAttempts": 1,
                    "timeLimit": 10,
                    "isPublished": False,
                    "questions": [test_case["data"]]
                }
                
                response = self.session.post(
                    f"{API_BASE}/final-tests",
                    json=final_test_data,
                    timeout=10
                )
                
                success = response.status_code == 200
                validation_results.append({
                    "test_case": test_case["name"],
                    "expected": test_case["should_pass"],
                    "actual": success,
                    "status_code": response.status_code,
                    "response": response.text[:200] if not success else "Success"
                })
            
            # Analyze validation results
            all_validation_correct = all(
                result["expected"] == result["actual"] 
                for result in validation_results
            )
            
            details = "; ".join([
                f"{result['test_case']}: Expected {result['expected']}, Got {result['actual']} ({result['status_code']})"
                for result in validation_results
            ])
            
            self.log_test(
                "Backend Validation Compatibility",
                all_validation_correct,
                f"Validation tests: {details}"
            )
            
            return all_validation_correct
            
        except Exception as e:
            self.log_test(
                "Backend Validation Compatibility",
                False,
                f"Validation testing error: {str(e)}"
            )
            return False

    def test_final_test_retrieval(self, test_ids):
        """Test retrieval of created final tests to verify data structure"""
        print("📖 Testing Final Test Retrieval...")
        
        try:
            retrieval_success = True
            retrieval_details = []
            
            for test_id in test_ids:
                if test_id:
                    response = self.session.get(
                        f"{API_BASE}/final-tests/{test_id}",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        final_test = response.json()
                        questions = final_test.get("questions", [])
                        
                        # Verify data structure integrity
                        structure_valid = True
                        for question in questions:
                            if not isinstance(question.get("correctAnswer"), str):
                                structure_valid = False
                                break
                        
                        retrieval_details.append(
                            f"Test {test_id[:8]}: {len(questions)} questions, structure valid: {structure_valid}"
                        )
                        
                        if not structure_valid:
                            retrieval_success = False
                    else:
                        retrieval_details.append(f"Test {test_id[:8]}: Retrieval failed ({response.status_code})")
                        retrieval_success = False
            
            self.log_test(
                "Final Test Retrieval",
                retrieval_success,
                f"Retrieved tests: {'; '.join(retrieval_details)}"
            )
            
            return retrieval_success
            
        except Exception as e:
            self.log_test(
                "Final Test Retrieval",
                False,
                f"Retrieval testing error: {str(e)}"
            )
            return False

    def run_comprehensive_test(self):
        """Run comprehensive backend testing for radio button fixes"""
        print("🚀 STARTING COMPREHENSIVE BACKEND TESTING FOR RADIO BUTTON FIXES")
        print("=" * 80)
        print()
        
        # Step 1: Admin Authentication
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with testing.")
            return False
        
        # Step 2: Program Creation
        program_id = self.test_program_creation()
        if not program_id:
            print("❌ CRITICAL: Program creation failed. Cannot proceed with final test creation.")
            return False
        
        # Step 3: Test Multiple Choice Final Test
        mc_test_id = self.test_multiple_choice_final_test(program_id)
        
        # Step 4: Test True/False Final Test
        tf_test_id = self.test_true_false_final_test(program_id)
        
        # Step 5: Test Mixed Question Types Final Test
        mixed_test_id = self.test_mixed_question_types_final_test(program_id)
        
        # Step 6: Test Backend Validation Compatibility
        self.test_backend_validation_compatibility(program_id)
        
        # Step 7: Test Final Test Retrieval
        test_ids = [test_id for test_id in [mc_test_id, tf_test_id, mixed_test_id] if test_id]
        self.test_final_test_retrieval(test_ids)
        
        # Generate summary
        self.generate_summary()
        
        return True

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print()
        print("=" * 80)
        print("🎯 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results
        critical_tests = [
            "Admin Authentication",
            "Program Creation", 
            "Multiple Choice Final Test Creation",
            "True/False Final Test Creation",
            "Mixed Question Types Final Test Creation"
        ]
        
        validation_tests = [
            "Multiple Choice Data Structure Validation",
            "True/False Data Structure Validation", 
            "Mixed Question Types Data Structure Validation",
            "Backend Validation Compatibility"
        ]
        
        print("🔑 CRITICAL FUNCTIONALITY:")
        for test_name in critical_tests:
            result = next((r for r in self.test_results if r["test"] == test_name), None)
            if result:
                status = "✅ WORKING" if result["success"] else "❌ FAILING"
                print(f"   {test_name}: {status}")
        
        print()
        print("🔍 DATA STRUCTURE VALIDATION:")
        for test_name in validation_tests:
            result = next((r for r in self.test_results if r["test"] == test_name), None)
            if result:
                status = "✅ VALID" if result["success"] else "❌ INVALID"
                print(f"   {test_name}: {status}")
        
        print()
        print("📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {status}: {result['test']}")
            if result["details"]:
                print(f"      {result['details']}")
        
        print()
        
        # Final assessment
        critical_passed = all(
            next((r for r in self.test_results if r["test"] == test_name), {"success": False})["success"]
            for test_name in critical_tests
        )
        
        validation_passed = all(
            next((r for r in self.test_results if r["test"] == test_name), {"success": False})["success"]
            for test_name in validation_tests
        )
        
        if critical_passed and validation_passed:
            print("🎉 CONCLUSION: RADIO BUTTON FIXES WORKING CORRECTLY")
            print("   ✅ All critical functionality operational")
            print("   ✅ All data structure validation passed")
            print("   ✅ Backend properly handles string-based correctAnswer values")
            print("   ✅ No 422 validation errors with properly formatted data")
            print("   ✅ Complete program creation workflow functional")
        elif critical_passed:
            print("⚠️  CONCLUSION: PARTIAL SUCCESS")
            print("   ✅ Critical functionality operational")
            print("   ❌ Some data structure validation issues detected")
        else:
            print("❌ CONCLUSION: CRITICAL ISSUES DETECTED")
            print("   ❌ Core functionality failing")
            print("   🔧 Immediate fixes required")
        
        print("=" * 80)

def main():
    """Main execution function"""
    print("🧪 BACKEND TESTING FOR FINAL TEST CREATION WITH RADIO BUTTON FIXES")
    print("Testing backend functionality for final test creation with proper radio button selections")
    print()
    
    tester = BackendTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print("\n✅ Testing completed successfully!")
            return 0
        else:
            print("\n❌ Testing completed with critical failures!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Testing failed with unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())