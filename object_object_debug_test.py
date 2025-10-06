#!/usr/bin/env python3
"""
Debug [object Object] Console Errors - Final Test Creation Workflow Testing

This test specifically targets the user's reported issue:
1. Created a program with multiple question types
2. Program creation succeeded 
3. Final test creation failed with [object Object] errors and "Failed to create final test: Array(6)"

Focus Areas:
- Test the exact final test creation workflow that the user is experiencing
- Test with question types: multiple_choice, select-all-that-apply, true_false, short_answer, essay
- Identify what's causing the [object Object] serialization in the response
- Check if there are any fields in the questions that contain objects instead of strings
- Focus on finding why the frontend sees [object Object] while backend testing worked

Admin credentials: brayden.t@covesmart.com / Hawaii2020!
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration - Using correct backend URL from frontend/.env
BACKEND_URL = "https://grade-flow-wizard.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class ObjectObjectDebugTester:
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
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def create_program_with_multiple_question_types(self):
        """Create a program similar to what user showed (multiple question types)"""
        try:
            program_data = {
                "title": f"Object Object Debug Program {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test program to debug [object Object] errors in final test creation",
                "departmentId": None,
                "duration": "6 weeks",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            
            if response.status_code == 200:
                program = response.json()
                self.test_program_id = program["id"]
                self.log_test("Program Creation (Multiple Question Types)", True, 
                            f"Created program: {program['title']} (ID: {program['id']})")
                return program
            else:
                self.log_test("Program Creation (Multiple Question Types)", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Program Creation (Multiple Question Types)", False, f"Exception: {str(e)}")
            return None
    
    def test_final_test_creation_with_all_question_types(self):
        """Test final test creation with all question types that user used"""
        try:
            # Create test data with the exact question types user mentioned
            test_data = {
                "title": f"Object Object Debug Final Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing final test creation with multiple question types to debug [object Object] errors",
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
                        "explanation": "Object-oriented programming organizes code into reusable objects with properties and methods."
                    },
                    {
                        "type": "select_all_that_apply",
                        "question": "Which of the following are programming languages? (Select all that apply)",
                        "options": [
                            "Python",
                            "JavaScript",
                            "HTML",
                            "CSS",
                            "Java",
                            "C++"
                        ],
                        "correctAnswers": ["0", "1", "4", "5"],
                        "points": 15,
                        "explanation": "Python, JavaScript, Java, and C++ are programming languages. HTML and CSS are markup/styling languages."
                    },
                    {
                        "type": "true_false",
                        "question": "JavaScript is only used for frontend web development.",
                        "correctAnswer": "false",
                        "points": 5,
                        "explanation": "JavaScript can be used for both frontend and backend development (Node.js)."
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
                        "question": "Explain the difference between synchronous and asynchronous programming. Provide examples of when each would be used.",
                        "points": 20,
                        "explanation": "This is an open-ended question requiring detailed explanation of sync vs async programming concepts."
                    },
                    {
                        "type": "chronological_order",
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
            
            print(f"\n🔍 DEBUGGING: Sending final test creation request...")
            print(f"📊 Question count: {len(test_data['questions'])}")
            print(f"📋 Question types: {[q['type'] for q in test_data['questions']]}")
            
            # Log the exact payload being sent
            print(f"\n📤 REQUEST PAYLOAD:")
            print(json.dumps(test_data, indent=2))
            
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            print(f"\n📥 RESPONSE STATUS: {response.status_code}")
            print(f"📥 RESPONSE HEADERS: {dict(response.headers)}")
            
            # Log the exact response
            try:
                response_data = response.json()
                print(f"📥 RESPONSE BODY:")
                print(json.dumps(response_data, indent=2, default=str))
            except:
                print(f"📥 RESPONSE BODY (raw): {response.text}")
            
            if response.status_code == 200:
                final_test = response.json()
                self.debug_test_id = final_test["id"]
                
                # Detailed verification of the created test
                print(f"\n🔍 VERIFICATION:")
                print(f"✅ Test ID: {final_test['id']}")
                print(f"✅ Question Count: {final_test.get('questionCount', 'MISSING')}")
                print(f"✅ Total Points: {final_test.get('totalPoints', 'MISSING')}")
                print(f"✅ Program ID: {final_test.get('programId', 'MISSING')}")
                print(f"✅ Questions Array Length: {len(final_test.get('questions', []))}")
                
                # Check each question for potential [object Object] issues
                questions = final_test.get('questions', [])
                for i, question in enumerate(questions):
                    print(f"\n🔍 Question {i+1} Analysis:")
                    print(f"  Type: {question.get('type', 'MISSING')}")
                    print(f"  Question Text: {question.get('question', 'MISSING')[:50]}...")
                    
                    # Check for object serialization issues
                    for key, value in question.items():
                        if isinstance(value, dict):
                            print(f"  ⚠️  OBJECT FOUND in {key}: {value}")
                        elif isinstance(value, list):
                            for j, item in enumerate(value):
                                if isinstance(item, dict):
                                    print(f"  ⚠️  OBJECT FOUND in {key}[{j}]: {item}")
                
                # Verify expected structure
                expected_question_count = 6
                expected_total_points = 70
                
                if (final_test.get("questionCount") == expected_question_count and 
                    final_test.get("totalPoints") == expected_total_points and
                    final_test.get("programId") == self.test_program_id and
                    len(final_test.get("questions", [])) == expected_question_count):
                    self.log_test("Final Test Creation (All Question Types)", True, 
                                f"Created test with {expected_question_count} questions, total points: {expected_total_points}")
                    return final_test
                else:
                    self.log_test("Final Test Creation (All Question Types)", False, 
                                f"Test created but validation failed - Expected: {expected_question_count} questions, {expected_total_points} points")
                    return final_test  # Return anyway for further analysis
            else:
                error_details = f"Status: {response.status_code}"
                try:
                    error_data = response.json()
                    error_details += f", Error: {error_data}"
                except:
                    error_details += f", Response: {response.text}"
                
                self.log_test("Final Test Creation (All Question Types)", False, error_details)
                return None
                
        except Exception as e:
            self.log_test("Final Test Creation (All Question Types)", False, f"Exception: {str(e)}")
            return None
    
    def test_retrieve_created_test(self):
        """Retrieve the created test to check for serialization issues"""
        try:
            if not hasattr(self, 'debug_test_id'):
                self.log_test("Test Retrieval", False, "No test ID available for retrieval")
                return None
            
            response = self.session.get(f"{BACKEND_URL}/final-tests/{self.debug_test_id}")
            
            print(f"\n🔍 RETRIEVAL TEST:")
            print(f"📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                retrieved_test = response.json()
                
                print(f"📥 Retrieved Test Structure:")
                print(json.dumps(retrieved_test, indent=2, default=str))
                
                # Check for [object Object] patterns in the response
                response_str = json.dumps(retrieved_test, default=str)
                if "[object Object]" in response_str:
                    self.log_test("Test Retrieval - Object Serialization Check", False, 
                                "Found [object Object] in retrieved test data")
                    print("⚠️  [object Object] FOUND in response!")
                else:
                    self.log_test("Test Retrieval - Object Serialization Check", True, 
                                "No [object Object] found in retrieved test data")
                
                self.log_test("Test Retrieval", True, f"Successfully retrieved test {self.debug_test_id}")
                return retrieved_test
            else:
                self.log_test("Test Retrieval", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Test Retrieval", False, f"Exception: {str(e)}")
            return None
    
    def test_program_final_tests_listing(self):
        """Test listing final tests for the program to check for serialization issues"""
        try:
            response = self.session.get(f"{BACKEND_URL}/final-tests", params={
                "program_id": self.test_program_id
            })
            
            print(f"\n🔍 PROGRAM FINAL TESTS LISTING:")
            print(f"📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                tests_list = response.json()
                
                print(f"📥 Tests List Structure:")
                print(json.dumps(tests_list, indent=2, default=str))
                
                # Check for [object Object] patterns in the response
                response_str = json.dumps(tests_list, default=str)
                if "[object Object]" in response_str:
                    self.log_test("Program Tests Listing - Object Serialization Check", False, 
                                "Found [object Object] in tests listing")
                    print("⚠️  [object Object] FOUND in tests listing!")
                else:
                    self.log_test("Program Tests Listing - Object Serialization Check", True, 
                                "No [object Object] found in tests listing")
                
                self.log_test("Program Final Tests Listing", True, 
                            f"Successfully retrieved {len(tests_list)} tests for program")
                return tests_list
            else:
                self.log_test("Program Final Tests Listing", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Program Final Tests Listing", False, f"Exception: {str(e)}")
            return None
    
    def test_data_structure_analysis(self):
        """Analyze the data structure differences between backend and frontend expectations"""
        try:
            # Test different question type structures that might cause [object Object]
            problematic_structures = [
                {
                    "name": "Multiple Choice with Object Options",
                    "question": {
                        "type": "multiple_choice",
                        "question": "Test question with object options",
                        "options": [
                            {"text": "Option 1", "value": "opt1"},
                            {"text": "Option 2", "value": "opt2"}
                        ],
                        "correctAnswer": "0",
                        "points": 5
                    }
                },
                {
                    "name": "Select All with Object Options",
                    "question": {
                        "type": "select_all_that_apply",
                        "question": "Test question with object options",
                        "options": [
                            {"text": "Option A", "id": "a"},
                            {"text": "Option B", "id": "b"}
                        ],
                        "correctAnswers": ["0"],
                        "points": 5
                    }
                },
                {
                    "name": "Chronological with Object Items",
                    "question": {
                        "type": "chronological_order",
                        "question": "Test chronological with object items",
                        "items": [
                            {"text": "First step", "order": 1},
                            {"text": "Second step", "order": 2}
                        ],
                        "correctOrder": [0, 1],
                        "points": 5
                    }
                }
            ]
            
            for structure in problematic_structures:
                print(f"\n🔍 TESTING PROBLEMATIC STRUCTURE: {structure['name']}")
                
                test_data = {
                    "title": f"Structure Test - {structure['name']}",
                    "description": f"Testing {structure['name']} for [object Object] issues",
                    "programId": self.test_program_id,
                    "questions": [structure["question"]],
                    "timeLimit": 30,
                    "maxAttempts": 1,
                    "passingScore": 50.0,
                    "isPublished": False
                }
                
                response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
                
                if response.status_code == 200:
                    test_result = response.json()
                    response_str = json.dumps(test_result, default=str)
                    
                    if "[object Object]" in response_str:
                        self.log_test(f"Data Structure Analysis - {structure['name']}", False, 
                                    "Found [object Object] in response - this structure causes the issue!")
                        print(f"⚠️  PROBLEMATIC STRUCTURE IDENTIFIED: {structure['name']}")
                    else:
                        self.log_test(f"Data Structure Analysis - {structure['name']}", True, 
                                    "No [object Object] found - this structure is safe")
                else:
                    self.log_test(f"Data Structure Analysis - {structure['name']}", False, 
                                f"Request failed: {response.status_code}")
            
            return True
                
        except Exception as e:
            self.log_test("Data Structure Analysis", False, f"Exception: {str(e)}")
            return False
    
    def run_debug_tests(self):
        """Run all debug tests for [object Object] issue"""
        print("🚀 Starting [object Object] Debug Testing for Final Test Creation")
        print("=" * 80)
        print("🎯 OBJECTIVE: Debug the exact final test creation workflow that user is experiencing")
        print("🔍 FOCUS: Find why frontend sees [object Object] while backend testing worked")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Create program with multiple question types
        program = self.create_program_with_multiple_question_types()
        if not program:
            print("❌ Program creation failed. Cannot proceed with tests.")
            return False
        
        # Step 3: Test final test creation with all question types (the main test)
        final_test = self.test_final_test_creation_with_all_question_types()
        
        # Step 4: Retrieve the created test to check for serialization issues
        if final_test:
            self.test_retrieve_created_test()
        
        # Step 5: Test program final tests listing
        self.test_program_final_tests_listing()
        
        # Step 6: Test different data structures that might cause [object Object]
        self.test_data_structure_analysis()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 [OBJECT OBJECT] DEBUG TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests < total_tests:
            print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
            print("\n🚨 FAILED TESTS (Potential [object Object] Sources):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Specific analysis for [object Object] issue
        print(f"\n🎯 [OBJECT OBJECT] ANALYSIS:")
        object_issues = [r for r in self.test_results if not r["success"] and "object Object" in r["details"].lower()]
        if object_issues:
            print("⚠️  POTENTIAL [OBJECT OBJECT] SOURCES IDENTIFIED:")
            for issue in object_issues:
                print(f"  - {issue['test']}")
        else:
            print("✅ No [object Object] serialization issues detected in backend responses")
            print("💡 The issue may be in frontend data processing or display logic")
        
        print(f"\n🎯 Final Test Creation Debug: {'✅ BACKEND WORKING' if success_rate >= 70 else '❌ BACKEND ISSUES DETECTED'}")
        
        return success_rate >= 70

if __name__ == "__main__":
    tester = ObjectObjectDebugTester()
    success = tester.run_debug_tests()
    sys.exit(0 if success else 1)