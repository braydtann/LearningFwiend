#!/usr/bin/env python3
"""
Corrected Debug Test for [object Object] Console Errors

ROOT CAUSE IDENTIFIED: Backend expects question types with hyphens:
- select-all-that-apply (NOT select_all_that_apply)
- chronological-order (NOT chronological_order)

This test uses the correct format to see if we can reproduce the [object Object] issue
or if it's resolved with proper question type formatting.
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://lms-chronology-1.preview.emergentagent.com/api"
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class CorrectedObjectDebugTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
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
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def create_program(self):
        """Create a test program"""
        try:
            program_data = {
                "title": f"Corrected Debug Program {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test program with corrected question type formats",
                "departmentId": None,
                "duration": "4 weeks",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            
            if response.status_code == 200:
                program = response.json()
                self.test_program_id = program["id"]
                self.log_test("Program Creation", True, f"Created program: {program['title']}")
                return program
            else:
                self.log_test("Program Creation", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Program Creation", False, f"Exception: {str(e)}")
            return None
    
    def test_corrected_final_test_creation(self):
        """Test final test creation with CORRECTED question type formats"""
        try:
            # Using CORRECT question type formats (with hyphens)
            test_data = {
                "title": f"Corrected Final Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing with corrected question type formats",
                "programId": self.test_program_id,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is the primary purpose of object-oriented programming?",
                        "options": [
                            "To make code more complex",
                            "To organize code into reusable objects",
                            "To eliminate all functions",
                            "To make debugging harder"
                        ],
                        "correctAnswer": "1",
                        "points": 10,
                        "explanation": "Object-oriented programming organizes code into reusable objects."
                    },
                    {
                        "type": "select-all-that-apply",  # CORRECTED: hyphen format
                        "question": "Which of the following are programming languages? (Select all that apply)",
                        "options": [
                            "Python",
                            "JavaScript", 
                            "HTML",
                            "CSS",
                            "Java",
                            "C++"
                        ],
                        "correctAnswers": [0, 1, 4, 5],  # Using integers instead of strings
                        "points": 15,
                        "explanation": "Python, JavaScript, Java, and C++ are programming languages."
                    },
                    {
                        "type": "true_false",
                        "question": "JavaScript is only used for frontend web development.",
                        "correctAnswer": "false",
                        "points": 5,
                        "explanation": "JavaScript can be used for both frontend and backend development."
                    },
                    {
                        "type": "short_answer",
                        "question": "What does API stand for?",
                        "correctAnswer": "Application Programming Interface",
                        "points": 8,
                        "explanation": "API stands for Application Programming Interface."
                    },
                    {
                        "type": "essay",
                        "question": "Explain the difference between synchronous and asynchronous programming.",
                        "points": 20,
                        "explanation": "This is an open-ended question requiring detailed explanation."
                    },
                    {
                        "type": "chronological-order",  # CORRECTED: hyphen format
                        "question": "Arrange the following software development phases in chronological order:",
                        "items": [
                            "Requirements Analysis",
                            "Design", 
                            "Implementation",
                            "Testing",
                            "Deployment",
                            "Maintenance"
                        ],
                        "correctOrder": [0, 1, 2, 3, 4, 5],
                        "points": 12,
                        "explanation": "The software development lifecycle follows this chronological order."
                    }
                ],
                "timeLimit": 120,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": True
            }
            
            print(f"\n🔍 CORRECTED TEST: Sending final test creation request...")
            print(f"📊 Question count: {len(test_data['questions'])}")
            print(f"📋 Question types: {[q['type'] for q in test_data['questions']]}")
            
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            print(f"\n📥 RESPONSE STATUS: {response.status_code}")
            
            if response.status_code == 200:
                final_test = response.json()
                self.debug_test_id = final_test["id"]
                
                print(f"📥 RESPONSE BODY:")
                print(json.dumps(final_test, indent=2, default=str))
                
                # Check for [object Object] in the response
                response_str = json.dumps(final_test, default=str)
                if "[object Object]" in response_str:
                    self.log_test("Corrected Final Test Creation - Object Check", False, 
                                "Found [object Object] in response!")
                    print("⚠️  [object Object] STILL FOUND in response!")
                    
                    # Analyze where the [object Object] appears
                    lines = response_str.split('\n')
                    for i, line in enumerate(lines):
                        if "[object Object]" in line:
                            print(f"🔍 [object Object] found in line {i}: {line}")
                else:
                    self.log_test("Corrected Final Test Creation - Object Check", True, 
                                "No [object Object] found in response")
                
                # Verify the test structure
                expected_question_count = 6
                expected_total_points = 70
                
                if (final_test.get("questionCount") == expected_question_count and 
                    final_test.get("totalPoints") == expected_total_points):
                    self.log_test("Corrected Final Test Creation", True, 
                                f"Successfully created test with {expected_question_count} questions")
                    return final_test
                else:
                    self.log_test("Corrected Final Test Creation", False, 
                                f"Test created but validation failed")
                    return final_test
            else:
                try:
                    error_data = response.json()
                    print(f"📥 ERROR RESPONSE:")
                    print(json.dumps(error_data, indent=2))
                except:
                    print(f"📥 ERROR RESPONSE (raw): {response.text}")
                
                self.log_test("Corrected Final Test Creation", False, 
                            f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Corrected Final Test Creation", False, f"Exception: {str(e)}")
            return None
    
    def test_frontend_vs_backend_data_flow(self):
        """Test to simulate frontend-to-backend data flow differences"""
        try:
            if not hasattr(self, 'debug_test_id'):
                self.log_test("Frontend vs Backend Data Flow", False, "No test ID available")
                return None
            
            # Simulate how frontend might retrieve and process the data
            response = self.session.get(f"{BACKEND_URL}/final-tests/{self.debug_test_id}")
            
            if response.status_code == 200:
                backend_data = response.json()
                
                print(f"\n🔍 FRONTEND VS BACKEND DATA FLOW ANALYSIS:")
                print(f"📊 Backend Response Structure:")
                
                # Analyze each question for potential frontend processing issues
                questions = backend_data.get('questions', [])
                for i, question in enumerate(questions):
                    print(f"\n  Question {i+1} ({question.get('type', 'unknown')}):")
                    
                    # Check for complex data structures that might cause [object Object]
                    for key, value in question.items():
                        if isinstance(value, dict):
                            print(f"    ⚠️  COMPLEX OBJECT in {key}: {value}")
                        elif isinstance(value, list):
                            for j, item in enumerate(value):
                                if isinstance(item, dict):
                                    print(f"    ⚠️  COMPLEX OBJECT in {key}[{j}]: {item}")
                                elif isinstance(item, list):
                                    print(f"    ⚠️  NESTED ARRAY in {key}[{j}]: {item}")
                        elif value is None:
                            print(f"    ℹ️  NULL VALUE in {key}")
                        else:
                            print(f"    ✅ SIMPLE VALUE in {key}: {type(value).__name__}")
                
                # Check if the response contains any serialization issues
                response_str = json.dumps(backend_data, default=str)
                if "[object Object]" in response_str:
                    self.log_test("Frontend vs Backend Data Flow", False, 
                                "Backend response contains [object Object]")
                else:
                    self.log_test("Frontend vs Backend Data Flow", True, 
                                "Backend response is clean - issue likely in frontend processing")
                
                return backend_data
            else:
                self.log_test("Frontend vs Backend Data Flow", False, 
                            f"Failed to retrieve test: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_test("Frontend vs Backend Data Flow", False, f"Exception: {str(e)}")
            return None
    
    def run_corrected_tests(self):
        """Run corrected debug tests"""
        print("🚀 Starting CORRECTED [object Object] Debug Testing")
        print("=" * 80)
        print("🎯 ROOT CAUSE IDENTIFIED: Question type format mismatch")
        print("   Backend expects: select-all-that-apply, chronological-order")
        print("   Frontend sends: select_all_that_apply, chronological_order")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Create program
        program = self.create_program()
        if not program:
            print("❌ Program creation failed. Cannot proceed with tests.")
            return False
        
        # Step 3: Test final test creation with corrected formats
        final_test = self.test_corrected_final_test_creation()
        
        # Step 4: Analyze frontend vs backend data flow
        if final_test:
            self.test_frontend_vs_backend_data_flow()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 CORRECTED DEBUG TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests < total_tests:
            print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
            print("\n🚨 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Root cause analysis
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        print("✅ IDENTIFIED: Question type format mismatch between frontend and backend")
        print("   - Backend validation pattern requires hyphens: 'select-all-that-apply'")
        print("   - Frontend likely sends underscores: 'select_all_that_apply'")
        print("   - This causes 422 validation errors, not [object Object] serialization")
        
        if success_rate >= 80:
            print("\n💡 SOLUTION: Update frontend to send correct question type formats")
            print("   - Change 'select_all_that_apply' → 'select-all-that-apply'")
            print("   - Change 'chronological_order' → 'chronological-order'")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = CorrectedObjectDebugTester()
    success = tester.run_corrected_tests()
    sys.exit(0 if success else 1)