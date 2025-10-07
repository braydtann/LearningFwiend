#!/usr/bin/env python3
"""
URGENT: Final Exam Scoring Investigation - Root Cause Analysis
Based on the debug test, I found the issue: the question's correctAnswer field is None!

The scoring logic is working correctly, but the questions being created don't have 
the correctAnswer field populated properly.

Investigation Focus:
1. Check how questions are stored when creating final tests
2. Verify the question data structure in the database
3. Test the actual question creation process
4. Fix the data structure issue
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://quiz-progress-fix.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"
STUDENT_EMAIL = "karlo.student@alder.com"
STUDENT_PASSWORD = "StudentPermanent123!"

class FinalExamScoringInvestigator:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.student_token = None
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
    
    def authenticate_student(self):
        """Authenticate as student user"""
        try:
            # Create new session for student
            student_session = requests.Session()
            response = student_session.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": STUDENT_EMAIL,
                "password": STUDENT_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_session = student_session
                self.student_session.headers.update({
                    "Authorization": f"Bearer {self.student_token}"
                })
                self.log_test("Student Authentication", True, f"Logged in as {data['user']['full_name']}")
                return True
            else:
                self.log_test("Student Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False
    
    def investigate_question_creation_process(self):
        """Investigate how questions are created and stored"""
        try:
            # Create a test program
            test_program_data = {
                "title": f"Question Investigation {datetime.now().strftime('%H%M%S')}",
                "description": "Testing question creation process",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            program_response = self.session.post(f"{BACKEND_URL}/programs", json=test_program_data)
            
            if program_response.status_code != 200:
                self.log_test("Question Creation Investigation", False, f"Failed to create program: {program_response.status_code}")
                return False
            
            program = program_response.json()
            program_id = program["id"]
            
            # Create final test with explicit question structure
            test_data = {
                "title": "Question Structure Investigation",
                "description": "Testing question data structure",
                "programId": program_id,
                "questions": [
                    {
                        "id": str(uuid.uuid4()),  # Explicit ID
                        "type": "multiple_choice",
                        "question": "What is 2 + 2?",
                        "options": ["2", "3", "4", "5"],
                        "correctAnswer": "2",  # Index 2 = "4"
                        "points": 10,
                        "explanation": "2 + 2 = 4"
                    }
                ],
                "timeLimit": 60,
                "maxAttempts": 3,
                "passingScore": 75.0,
                "isPublished": True
            }
            
            print(f"🔍 Creating test with question data:")
            print(json.dumps(test_data["questions"][0], indent=2))
            
            test_response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            if test_response.status_code == 200:
                final_test = test_response.json()
                created_question = final_test["questions"][0]
                
                print(f"🔍 Question as stored in database:")
                print(json.dumps(created_question, indent=2))
                
                # Check if correctAnswer field is preserved
                if "correctAnswer" in created_question and created_question["correctAnswer"] is not None:
                    self.log_test("Question Creation Investigation", True, 
                                f"✅ correctAnswer field preserved: {created_question['correctAnswer']}")
                    self.investigation_test_id = final_test["id"]
                    return True
                else:
                    self.log_test("Question Creation Investigation", False, 
                                f"❌ correctAnswer field lost during creation. Available fields: {list(created_question.keys())}")
                    return False
            else:
                self.log_test("Question Creation Investigation", False, 
                            f"Failed to create test: {test_response.status_code}, {test_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Question Creation Investigation", False, f"Exception: {str(e)}")
            return False
    
    def test_scoring_with_proper_data(self):
        """Test scoring with properly structured question data"""
        try:
            if not hasattr(self, 'investigation_test_id'):
                self.log_test("Scoring Test with Proper Data", False, "No investigation test ID available")
                return False
            
            # Get the test to verify structure
            test_response = self.student_session.get(f"{BACKEND_URL}/final-tests/{self.investigation_test_id}")
            
            if test_response.status_code != 200:
                self.log_test("Scoring Test with Proper Data", False, f"Failed to get test: {test_response.status_code}")
                return False
            
            test_data = test_response.json()
            question = test_data["questions"][0]
            
            print(f"🔍 Testing with question structure:")
            print(f"   Question ID: {question.get('id')}")
            print(f"   Question type: {question.get('type')}")
            print(f"   Correct answer: {question.get('correctAnswer')}")
            print(f"   Options: {question.get('options', [])}")
            
            # Submit correct answer
            submission_data = {
                "testId": self.investigation_test_id,
                "answers": [
                    {
                        "questionId": question.get("id"),
                        "answer": question.get("correctAnswer"),  # Use the correct answer
                        "questionType": question.get("type")
                    }
                ],
                "timeSpent": 30,
                "completedAt": datetime.now().isoformat()
            }
            
            print(f"🔍 Submitting answer: {question.get('correctAnswer')}")
            
            submit_response = self.student_session.post(f"{BACKEND_URL}/final-test-attempts", json=submission_data)
            
            if submit_response.status_code == 200:
                result = submit_response.json()
                score = result.get("score", 0)
                
                print(f"🔍 Result: Score = {score}%, Points = {result.get('pointsEarned', 0)}/{result.get('totalPoints', 0)}")
                
                if score > 0:
                    self.log_test("Scoring Test with Proper Data", True, 
                                f"✅ Scoring working correctly: {score}%")
                    return True
                else:
                    self.log_test("Scoring Test with Proper Data", False, 
                                f"❌ Still getting 0% score. Full result: {result}")
                    return False
            else:
                self.log_test("Scoring Test with Proper Data", False, 
                            f"Submission failed: {submit_response.status_code}, {submit_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Scoring Test with Proper Data", False, f"Exception: {str(e)}")
            return False
    
    def examine_existing_final_tests(self):
        """Examine existing final tests to see their question structure"""
        try:
            # Get all final tests
            response = self.session.get(f"{BACKEND_URL}/final-tests")
            
            if response.status_code != 200:
                self.log_test("Existing Tests Examination", False, f"Failed to get tests: {response.status_code}")
                return False
            
            final_tests = response.json()
            
            if not final_tests:
                self.log_test("Existing Tests Examination", False, "No final tests found")
                return False
            
            print(f"🔍 Examining {len(final_tests)} existing final tests...")
            
            issues_found = []
            tests_examined = 0
            
            for test in final_tests[:5]:  # Examine first 5 tests
                tests_examined += 1
                test_issues = []
                
                print(f"\n📋 Test: {test['title']} (ID: {test['id']})")
                print(f"   Questions: {len(test.get('questions', []))}")
                
                for i, question in enumerate(test.get('questions', [])):
                    print(f"   Q{i+1}: Type={question.get('type', 'unknown')}")
                    
                    # Check for correctAnswer field
                    if 'correctAnswer' not in question:
                        test_issues.append(f"Q{i+1} missing correctAnswer field")
                        print(f"        ❌ Missing correctAnswer field")
                    elif question['correctAnswer'] is None:
                        test_issues.append(f"Q{i+1} has null correctAnswer")
                        print(f"        ❌ correctAnswer is null")
                    else:
                        print(f"        ✅ correctAnswer: {question['correctAnswer']}")
                    
                    # Check for other required fields based on type
                    if question.get('type') == 'multiple_choice':
                        if 'options' not in question or not question['options']:
                            test_issues.append(f"Q{i+1} missing options")
                            print(f"        ❌ Missing options")
                        else:
                            print(f"        ✅ Options: {len(question['options'])} items")
                
                if test_issues:
                    issues_found.extend([f"Test '{test['title']}': {issue}" for issue in test_issues])
            
            if issues_found:
                self.log_test("Existing Tests Examination", False, 
                            f"❌ Found {len(issues_found)} issues across {tests_examined} tests")
                print(f"\n🚨 Issues found:")
                for issue in issues_found[:10]:  # Show first 10 issues
                    print(f"   - {issue}")
                return False
            else:
                self.log_test("Existing Tests Examination", True, 
                            f"✅ All {tests_examined} tests have proper question structure")
                return True
                
        except Exception as e:
            self.log_test("Existing Tests Examination", False, f"Exception: {str(e)}")
            return False
    
    def test_different_question_types(self):
        """Test different question types to see which ones work"""
        try:
            # Create a test program
            test_program_data = {
                "title": f"Question Types Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing different question types",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            program_response = self.session.post(f"{BACKEND_URL}/programs", json=test_program_data)
            
            if program_response.status_code != 200:
                self.log_test("Question Types Test", False, f"Failed to create program: {program_response.status_code}")
                return False
            
            program = program_response.json()
            program_id = program["id"]
            
            # Test each question type individually
            question_types = [
                {
                    "name": "Multiple Choice",
                    "data": {
                        "type": "multiple_choice",
                        "question": "What is 1 + 1?",
                        "options": ["1", "2", "3", "4"],
                        "correctAnswer": "1",  # Index 1 = "2"
                        "points": 25
                    }
                },
                {
                    "name": "True/False",
                    "data": {
                        "type": "true_false",
                        "question": "The sky is blue.",
                        "correctAnswer": "true",
                        "points": 25
                    }
                }
            ]
            
            results = []
            
            for qt in question_types:
                # Create test with single question type
                test_data = {
                    "title": f"{qt['name']} Test",
                    "description": f"Testing {qt['name']} question type",
                    "programId": program_id,
                    "questions": [qt["data"]],
                    "timeLimit": 60,
                    "maxAttempts": 3,
                    "passingScore": 75.0,
                    "isPublished": True
                }
                
                test_response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
                
                if test_response.status_code == 200:
                    final_test = test_response.json()
                    test_id = final_test["id"]
                    question = final_test["questions"][0]
                    
                    # Test submission
                    submission_data = {
                        "testId": test_id,
                        "answers": [
                            {
                                "questionId": question.get("id", "q1"),
                                "answer": question.get("correctAnswer"),
                                "questionType": question.get("type")
                            }
                        ],
                        "timeSpent": 15,
                        "completedAt": datetime.now().isoformat()
                    }
                    
                    submit_response = self.student_session.post(f"{BACKEND_URL}/final-test-attempts", json=submission_data)
                    
                    if submit_response.status_code == 200:
                        result = submit_response.json()
                        score = result.get("score", 0)
                        results.append({
                            "type": qt["name"],
                            "score": score,
                            "working": score > 0,
                            "correctAnswer": question.get("correctAnswer")
                        })
                        print(f"✅ {qt['name']}: Score = {score}% (correctAnswer: {question.get('correctAnswer')})")
                    else:
                        results.append({
                            "type": qt["name"],
                            "score": 0,
                            "working": False,
                            "error": f"Submission failed: {submit_response.status_code}"
                        })
                        print(f"❌ {qt['name']}: Submission failed - {submit_response.status_code}")
                else:
                    results.append({
                        "type": qt["name"],
                        "score": 0,
                        "working": False,
                        "error": f"Test creation failed: {test_response.status_code}"
                    })
                    print(f"❌ {qt['name']}: Test creation failed - {test_response.status_code}")
            
            working_types = [r for r in results if r["working"]]
            
            if working_types:
                self.log_test("Question Types Test", True, 
                            f"✅ {len(working_types)}/{len(question_types)} question types working: {[r['type'] for r in working_types]}")
                return True
            else:
                self.log_test("Question Types Test", False, 
                            f"❌ No question types working properly. Results: {results}")
                return False
                
        except Exception as e:
            self.log_test("Question Types Test", False, f"Exception: {str(e)}")
            return False
    
    def run_investigation(self):
        """Run comprehensive investigation of the scoring issue"""
        print("🔍 URGENT: Final Exam Scoring Investigation - Root Cause Analysis")
        print("=" * 80)
        print("Focus: Question data structure and scoring logic investigation")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Admin authentication failed. Cannot proceed.")
            return False
        
        if not self.authenticate_student():
            print("❌ Student authentication failed. Cannot proceed.")
            return False
        
        # Step 2: Investigate question creation process
        print("\n🔍 STEP 1: Investigating question creation process...")
        creation_ok = self.investigate_question_creation_process()
        
        # Step 3: Test scoring with proper data
        print("\n🔍 STEP 2: Testing scoring with proper question data...")
        scoring_ok = self.test_scoring_with_proper_data()
        
        # Step 4: Examine existing final tests
        print("\n🔍 STEP 3: Examining existing final tests...")
        existing_ok = self.examine_existing_final_tests()
        
        # Step 5: Test different question types
        print("\n🔍 STEP 4: Testing different question types...")
        types_ok = self.test_different_question_types()
        
        # Summary
        print("\n" + "=" * 80)
        print("🔍 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests < total_tests:
            print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
            print("\n🚨 ISSUES IDENTIFIED:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        # Root cause analysis
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        if creation_ok and scoring_ok:
            print("  ✅ Question creation and scoring logic working correctly")
        if not existing_ok:
            print("  🚨 CRITICAL: Existing final tests have malformed question data")
        if types_ok:
            print("  ✅ Question types are working when properly structured")
        
        return success_rate >= 75

if __name__ == "__main__":
    investigator = FinalExamScoringInvestigator()
    success = investigator.run_investigation()
    sys.exit(0 if success else 1)