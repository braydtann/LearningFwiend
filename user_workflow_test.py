#!/usr/bin/env python3
"""
User Workflow Test - Replicating the exact user scenario from the review request

This test replicates the user's exact workflow:
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

BACKEND_URL = "https://test-grading-fix.preview.emergentagent.com/api"
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class UserWorkflowTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def authenticate(self):
        """Authenticate as admin"""
        print("🔐 Authenticating as admin...")
        
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
                self.log_result("Admin Authentication", True, f"Authenticated as {user_info.get('full_name')}")
                return True
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_user_workflow(self):
        """Test the complete user workflow"""
        print("\n📚 Testing Complete User Workflow...")
        
        # Step 1: Create a program
        print("\n1️⃣ Creating program with title and description...")
        
        program_data = {
            "title": "User Test Program - All Question Types",
            "description": "Testing the complete workflow with all question types after data structure fixes",
            "departmentId": None,
            "duration": "90 minutes",
            "courseIds": [],
            "nestedProgramIds": []
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            
            if response.status_code == 200:
                program = response.json()
                program_id = program.get("id")
                self.log_result("Program Creation", True, f"Created: {program.get('title')}")
            else:
                self.log_result("Program Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Program Creation", False, f"Exception: {str(e)}")
            return False
        
        # Step 2: Create final test with all question types
        print("\n2️⃣ Adding multiple question types to final test...")
        
        # Using the EXACT question types mentioned in the review request
        final_test_data = {
            "programId": program_id,
            "title": "Complete Question Types Test",
            "description": "Testing all question types: multiple_choice, select-all-that-apply, true_false, short_answer, essay, chronological-order",
            "passingScore": 75,
            "timeLimit": 60,
            "questions": [
                {
                    "type": "multiple_choice",
                    "question": "Which programming language is known for its simplicity?",
                    "options": ["C++", "Python", "Assembly", "Fortran"],
                    "correctAnswer": "1",  # Python
                    "points": 10
                },
                {
                    "type": "select-all-that-apply",  # Using hyphen format as per review
                    "question": "Select all that are web technologies:",
                    "options": ["HTML", "Python", "CSS", "JavaScript"],
                    "correctAnswers": [0, 2, 3],  # HTML, CSS, JavaScript
                    "points": 15
                },
                {
                    "type": "true_false",
                    "question": "Python is an interpreted language.",
                    "correctAnswer": "true",
                    "points": 5
                },
                {
                    "type": "short_answer",
                    "question": "What does API stand for?",
                    "correctAnswer": "Application Programming Interface",
                    "points": 10
                },
                {
                    "type": "essay",
                    "question": "Explain the benefits of using version control systems in software development.",
                    "points": 20
                },
                {
                    "type": "chronological-order",  # Using hyphen format as per review
                    "question": "Arrange these software development phases in chronological order:",
                    "items": ["Testing", "Design", "Requirements", "Implementation"],  # Proper items array
                    "correctOrder": [2, 1, 3, 0],  # Requirements, Design, Implementation, Testing
                    "points": 15
                }
            ]
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=final_test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                test_id = final_test.get("id")
                
                # Check for [object Object] errors
                response_text = json.dumps(final_test)
                has_object_object = "[object Object]" in response_text
                
                if has_object_object:
                    self.log_result("Final Test Creation", False, "Response contains [object Object] errors")
                    return False
                else:
                    self.log_result("Final Test Creation", True, f"Created test with {len(final_test_data['questions'])} question types")
                    self.log_result("No [object Object] Errors", True, "Response is clean")
                    
            elif response.status_code == 422:
                # Parse validation errors
                try:
                    error_data = response.json()
                    self.log_result("Final Test Creation", False, f"422 Validation Error - Data structure issues remain")
                    print(f"    Validation Details: {json.dumps(error_data, indent=2)}")
                    return False
                except:
                    self.log_result("Final Test Creation", False, f"422 Error: {response.text}")
                    return False
            else:
                self.log_result("Final Test Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Final Test Creation", False, f"Exception: {str(e)}")
            return False
        
        # Step 3: Verify chronological-order questions have proper items array
        print("\n3️⃣ Verifying chronological-order questions have proper items array...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/final-tests/{test_id}")
            
            if response.status_code == 200:
                test_details = response.json()
                questions = test_details.get("questions", [])
                
                chronological_questions = [q for q in questions if q.get("type") == "chronological-order"]
                
                if chronological_questions:
                    chrono_q = chronological_questions[0]
                    items = chrono_q.get("items", [])
                    correct_order = chrono_q.get("correctOrder", [])
                    
                    if items and isinstance(items, list) and len(items) > 0:
                        self.log_result("Chronological Order Items Array", True, f"Found {len(items)} items: {items}")
                    else:
                        self.log_result("Chronological Order Items Array", False, "Items array missing or empty")
                        return False
                        
                    if correct_order and isinstance(correct_order, list):
                        self.log_result("Chronological Order Correct Order", True, f"Correct order: {correct_order}")
                    else:
                        self.log_result("Chronological Order Correct Order", False, "Correct order missing")
                        return False
                else:
                    self.log_result("Chronological Order Questions", False, "No chronological-order questions found")
                    return False
            else:
                self.log_result("Test Details Retrieval", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Chronological Order Verification", False, f"Exception: {str(e)}")
            return False
        
        # Step 4: Verify all question types were created successfully
        print("\n4️⃣ Verifying all question types were created without 422 errors...")
        
        expected_types = ["multiple_choice", "select-all-that-apply", "true_false", "short_answer", "essay", "chronological-order"]
        found_types = [q.get("type") for q in questions]
        
        missing_types = []
        for expected_type in expected_types:
            if expected_type not in found_types:
                missing_types.append(expected_type)
        
        if missing_types:
            self.log_result("All Question Types Created", False, f"Missing types: {missing_types}")
            return False
        else:
            self.log_result("All Question Types Created", True, f"All 6 question types present: {found_types}")
        
        return True
    
    def run_test(self):
        """Run the complete test"""
        print("🚀 TESTING USER WORKFLOW - POST DATA STRUCTURE FIXES")
        print("=" * 70)
        print("Replicating the exact user scenario from review request:")
        print("1. Create program with title and description")
        print("2. Add all question types with correct data structures")
        print("3. Verify chronological-order questions have items array")
        print("4. Confirm no 422 errors or [object Object] issues")
        print("=" * 70)
        
        if not self.authenticate():
            return False
        
        success = self.test_user_workflow()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ Passed: {passed}/{total} tests ({success_rate:.1f}% success rate)")
        
        if success_rate == 100:
            print("\n🎉 USER'S ISSUES ARE COMPLETELY RESOLVED!")
            print("✅ Data Structure Fix: Question types use correct hyphens")
            print("✅ Chronological Order Fix: Questions have proper items array")
            print("✅ [object Object] Resolution: No errors in responses")
            print("✅ Complete program → final test workflow: FUNCTIONAL")
            print("\n🎯 The user can now successfully:")
            print("   • Create programs with all question types")
            print("   • Use select-all-that-apply and chronological-order")
            print("   • Complete the full workflow without errors")
        else:
            print(f"\n⚠️  {total - passed} tests failed - Issues still need attention")
            
            failed_tests = [result for result in self.test_results if not result["success"]]
            for failed_test in failed_tests:
                print(f"❌ {failed_test['test']}: {failed_test['details']}")
        
        return success_rate == 100

if __name__ == "__main__":
    tester = UserWorkflowTester()
    success = tester.run_test()
    sys.exit(0 if success else 1)