#!/usr/bin/env python3
"""
URGENT: Final Exam Scoring Debug Test - 0% Score Investigation
Testing the specific issue where users get 0% scores despite answering correctly.

Critical Investigation Areas:
1. Verify QuestionResponse model has correctAnswer field
2. Live data analysis on deployed system
3. Frontend-Backend data flow debugging
4. Answer format matching verification
5. Deployment verification of recent fixes

User Issue: Created 4 programs with final exams (True/False, Multiple Choice, 
Select All That Apply, Chronological Order), answered all correctly but got 0% scores.

Test Environment: https://lms-progression-1.preview.emergentagent.com
Admin: brayden.t@covesmart.com / Hawaii2020!
Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration - Using deployed URL
BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"
STUDENT_EMAIL = "karlo.student@alder.com"
STUDENT_PASSWORD = "StudentPermanent123!"

class FinalExamScoringDebugger:
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
    
    def verify_deployed_backend_model(self):
        """Verify the QuestionResponse model structure in deployed backend"""
        try:
            # Create a test final test to examine the data structure
            test_program_data = {
                "title": f"Model Verification Program {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Testing deployed backend model structure",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            program_response = self.session.post(f"{BACKEND_URL}/programs", json=test_program_data)
            
            if program_response.status_code != 200:
                self.log_test("Backend Model Verification", False, f"Failed to create test program: {program_response.status_code}")
                return False
            
            program = program_response.json()
            program_id = program["id"]
            
            # Create final test with questions to examine structure
            test_data = {
                "title": "Model Structure Test",
                "description": "Testing question response model structure",
                "programId": program_id,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "Test question for model verification?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correctAnswer": "1",
                        "points": 10,
                        "explanation": "Testing correctAnswer field presence"
                    }
                ],
                "timeLimit": 60,
                "maxAttempts": 3,
                "passingScore": 75.0,
                "isPublished": True
            }
            
            test_response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            if test_response.status_code == 200:
                final_test = test_response.json()
                
                # Examine the question structure
                if final_test["questions"] and len(final_test["questions"]) > 0:
                    question = final_test["questions"][0]
                    has_correct_answer = "correctAnswer" in question
                    
                    if has_correct_answer:
                        self.log_test("Backend Model Verification", True, 
                                    f"✅ correctAnswer field present in deployed model: {question['correctAnswer']}")
                        self.test_final_test_id = final_test["id"]
                        return True
                    else:
                        self.log_test("Backend Model Verification", False, 
                                    f"❌ correctAnswer field MISSING from deployed model. Available fields: {list(question.keys())}")
                        return False
                else:
                    self.log_test("Backend Model Verification", False, "No questions found in created test")
                    return False
            else:
                self.log_test("Backend Model Verification", False, f"Failed to create test: {test_response.status_code}, {test_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Backend Model Verification", False, f"Exception: {str(e)}")
            return False
    
    def analyze_live_final_test_data(self):
        """Analyze actual final test data structure on deployed system"""
        try:
            # Get all final tests to examine their structure
            response = self.session.get(f"{BACKEND_URL}/final-tests")
            
            if response.status_code == 200:
                final_tests = response.json()
                
                if not final_tests:
                    self.log_test("Live Data Analysis", False, "No final tests found on deployed system")
                    return False
                
                # Analyze the first few tests
                analysis_results = []
                for i, test in enumerate(final_tests[:3]):  # Analyze first 3 tests
                    test_analysis = {
                        "test_id": test["id"],
                        "title": test["title"],
                        "question_count": len(test.get("questions", [])),
                        "questions_have_correct_answer": []
                    }
                    
                    for j, question in enumerate(test.get("questions", [])):
                        has_correct_answer = "correctAnswer" in question
                        correct_answer_value = question.get("correctAnswer", "MISSING")
                        test_analysis["questions_have_correct_answer"].append({
                            "question_index": j,
                            "type": question.get("type", "unknown"),
                            "has_correct_answer": has_correct_answer,
                            "correct_answer_value": correct_answer_value
                        })
                    
                    analysis_results.append(test_analysis)
                
                # Check if all questions have correctAnswer field
                all_have_correct_answer = True
                missing_count = 0
                total_questions = 0
                
                for test_analysis in analysis_results:
                    for q_analysis in test_analysis["questions_have_correct_answer"]:
                        total_questions += 1
                        if not q_analysis["has_correct_answer"]:
                            all_have_correct_answer = False
                            missing_count += 1
                
                if all_have_correct_answer and total_questions > 0:
                    self.log_test("Live Data Analysis", True, 
                                f"✅ All {total_questions} questions across {len(analysis_results)} tests have correctAnswer field")
                else:
                    self.log_test("Live Data Analysis", False, 
                                f"❌ {missing_count}/{total_questions} questions missing correctAnswer field")
                
                # Store first test for submission testing
                if analysis_results:
                    self.live_test_id = analysis_results[0]["test_id"]
                
                return all_have_correct_answer
                
            else:
                self.log_test("Live Data Analysis", False, f"Failed to get final tests: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Live Data Analysis", False, f"Exception: {str(e)}")
            return False
    
    def test_submission_flow_debug(self):
        """Test actual submission flow with detailed debugging"""
        try:
            if not hasattr(self, 'test_final_test_id'):
                self.log_test("Submission Flow Debug", False, "No test final test ID available")
                return False
            
            # Get the test details first
            test_response = self.student_session.get(f"{BACKEND_URL}/final-tests/{self.test_final_test_id}")
            
            if test_response.status_code != 200:
                self.log_test("Submission Flow Debug", False, f"Failed to get test details: {test_response.status_code}")
                return False
            
            test_data = test_response.json()
            
            if not test_data.get("questions"):
                self.log_test("Submission Flow Debug", False, "Test has no questions")
                return False
            
            # Prepare submission with correct answer
            question = test_data["questions"][0]
            correct_answer = question.get("correctAnswer")
            
            submission_data = {
                "testId": self.test_final_test_id,
                "answers": [
                    {
                        "questionId": question.get("id", "q1"),
                        "answer": correct_answer,  # Submit the correct answer
                        "questionType": question.get("type", "multiple_choice")
                    }
                ],
                "timeSpent": 30,
                "completedAt": datetime.now().isoformat()
            }
            
            print(f"🔍 DEBUG - Submitting answer: {correct_answer} for question type: {question.get('type')}")
            print(f"🔍 DEBUG - Question correctAnswer field: {correct_answer}")
            print(f"🔍 DEBUG - Submission data: {json.dumps(submission_data, indent=2)}")
            
            # Submit the test
            submit_response = self.student_session.post(f"{BACKEND_URL}/final-test-attempts", json=submission_data)
            
            if submit_response.status_code == 200:
                result = submit_response.json()
                score = result.get("score", 0)
                passed = result.get("passed", False)
                
                print(f"🔍 DEBUG - Submission result: Score={score}%, Passed={passed}")
                print(f"🔍 DEBUG - Full result: {json.dumps(result, indent=2)}")
                
                if score > 0:
                    self.log_test("Submission Flow Debug", True, 
                                f"✅ Scoring working correctly: {score}% (Expected >0%)")
                    return True
                else:
                    self.log_test("Submission Flow Debug", False, 
                                f"❌ CRITICAL: Got 0% score despite correct answer. Result: {result}")
                    return False
            else:
                self.log_test("Submission Flow Debug", False, 
                            f"Submission failed: {submit_response.status_code}, {submit_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Submission Flow Debug", False, f"Exception: {str(e)}")
            return False
    
    def test_answer_format_matching(self):
        """Test different answer formats to identify matching issues"""
        try:
            # Create a comprehensive test with different question types
            test_program_data = {
                "title": f"Answer Format Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing answer format matching",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            program_response = self.session.post(f"{BACKEND_URL}/programs", json=test_program_data)
            
            if program_response.status_code != 200:
                self.log_test("Answer Format Test Setup", False, f"Failed to create program: {program_response.status_code}")
                return False
            
            program = program_response.json()
            program_id = program["id"]
            
            # Create test with multiple question types
            test_data = {
                "title": "Answer Format Matching Test",
                "description": "Testing different answer formats",
                "programId": program_id,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "Multiple choice test - what is 2+2?",
                        "options": ["3", "4", "5", "6"],
                        "correctAnswer": "1",  # Index 1 = "4"
                        "points": 25
                    },
                    {
                        "type": "true_false",
                        "question": "True/False test - Python is a programming language",
                        "correctAnswer": "true",
                        "points": 25
                    },
                    {
                        "type": "select_all_that_apply",
                        "question": "Select all programming languages",
                        "options": ["Python", "HTML", "JavaScript", "CSS"],
                        "correctAnswers": ["0", "2"],  # Python and JavaScript
                        "points": 25
                    },
                    {
                        "type": "chronological_order",
                        "question": "Order these events chronologically",
                        "items": ["Event A", "Event B", "Event C", "Event D"],
                        "correctOrder": ["1", "0", "3", "2"],
                        "points": 25
                    }
                ],
                "timeLimit": 120,
                "maxAttempts": 5,
                "passingScore": 75.0,
                "isPublished": True
            }
            
            test_response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            if test_response.status_code != 200:
                self.log_test("Answer Format Test Creation", False, f"Failed to create test: {test_response.status_code}, {test_response.text}")
                return False
            
            format_test = test_response.json()
            format_test_id = format_test["id"]
            
            # Test different submission formats
            test_cases = [
                {
                    "name": "Exact Format Match",
                    "answers": [
                        {"questionId": "q1", "answer": "1", "questionType": "multiple_choice"},
                        {"questionId": "q2", "answer": "true", "questionType": "true_false"},
                        {"questionId": "q3", "answer": ["0", "2"], "questionType": "select_all_that_apply"},
                        {"questionId": "q4", "answer": ["1", "0", "3", "2"], "questionType": "chronological_order"}
                    ]
                },
                {
                    "name": "String vs Number Format",
                    "answers": [
                        {"questionId": "q1", "answer": 1, "questionType": "multiple_choice"},  # Number instead of string
                        {"questionId": "q2", "answer": True, "questionType": "true_false"},  # Boolean instead of string
                        {"questionId": "q3", "answer": [0, 2], "questionType": "select_all_that_apply"},  # Numbers instead of strings
                        {"questionId": "q4", "answer": [1, 0, 3, 2], "questionType": "chronological_order"}  # Numbers instead of strings
                    ]
                }
            ]
            
            results = []
            for test_case in test_cases:
                submission_data = {
                    "testId": format_test_id,
                    "answers": test_case["answers"],
                    "timeSpent": 60,
                    "completedAt": datetime.now().isoformat()
                }
                
                submit_response = self.student_session.post(f"{BACKEND_URL}/final-test-attempts", json=submission_data)
                
                if submit_response.status_code == 200:
                    result = submit_response.json()
                    score = result.get("score", 0)
                    results.append({
                        "test_case": test_case["name"],
                        "score": score,
                        "passed": result.get("passed", False),
                        "success": True
                    })
                    print(f"🔍 {test_case['name']}: Score = {score}%")
                else:
                    results.append({
                        "test_case": test_case["name"],
                        "score": 0,
                        "passed": False,
                        "success": False,
                        "error": f"{submit_response.status_code}: {submit_response.text}"
                    })
                    print(f"❌ {test_case['name']}: Failed - {submit_response.status_code}")
            
            # Analyze results
            working_formats = [r for r in results if r["success"] and r["score"] > 0]
            
            if working_formats:
                self.log_test("Answer Format Matching", True, 
                            f"✅ Found working format(s): {[r['test_case'] for r in working_formats]}")
                return True
            else:
                self.log_test("Answer Format Matching", False, 
                            f"❌ No answer formats produced scores > 0%. All results: {results}")
                return False
                
        except Exception as e:
            self.log_test("Answer Format Matching", False, f"Exception: {str(e)}")
            return False
    
    def verify_scoring_logic_backend(self):
        """Verify the scoring logic is working in the backend"""
        try:
            # Get the submit_final_test_attempt endpoint details by examining a test
            if not hasattr(self, 'test_final_test_id'):
                self.log_test("Scoring Logic Verification", False, "No test ID available")
                return False
            
            # Get test details to understand scoring
            test_response = self.session.get(f"{BACKEND_URL}/final-tests/{self.test_final_test_id}")
            
            if test_response.status_code != 200:
                self.log_test("Scoring Logic Verification", False, f"Failed to get test: {test_response.status_code}")
                return False
            
            test_data = test_response.json()
            total_points = test_data.get("totalPoints", 0)
            questions = test_data.get("questions", [])
            
            if not questions:
                self.log_test("Scoring Logic Verification", False, "Test has no questions")
                return False
            
            # Test with deliberately wrong answer first
            wrong_submission = {
                "testId": self.test_final_test_id,
                "answers": [
                    {
                        "questionId": questions[0].get("id", "q1"),
                        "answer": "999",  # Deliberately wrong answer
                        "questionType": questions[0].get("type", "multiple_choice")
                    }
                ],
                "timeSpent": 15,
                "completedAt": datetime.now().isoformat()
            }
            
            wrong_response = self.student_session.post(f"{BACKEND_URL}/final-test-attempts", json=wrong_submission)
            
            if wrong_response.status_code == 200:
                wrong_result = wrong_response.json()
                wrong_score = wrong_result.get("score", -1)
                
                # Now test with correct answer
                correct_submission = {
                    "testId": self.test_final_test_id,
                    "answers": [
                        {
                            "questionId": questions[0].get("id", "q1"),
                            "answer": questions[0].get("correctAnswer"),  # Correct answer
                            "questionType": questions[0].get("type", "multiple_choice")
                        }
                    ],
                    "timeSpent": 20,
                    "completedAt": datetime.now().isoformat()
                }
                
                correct_response = self.student_session.post(f"{BACKEND_URL}/final-test-attempts", json=correct_submission)
                
                if correct_response.status_code == 200:
                    correct_result = correct_response.json()
                    correct_score = correct_result.get("score", -1)
                    
                    print(f"🔍 SCORING DEBUG:")
                    print(f"   Wrong answer score: {wrong_score}%")
                    print(f"   Correct answer score: {correct_score}%")
                    print(f"   Question correctAnswer: {questions[0].get('correctAnswer')}")
                    print(f"   Question points: {questions[0].get('points', 0)}")
                    print(f"   Total test points: {total_points}")
                    
                    if correct_score > wrong_score:
                        self.log_test("Scoring Logic Verification", True, 
                                    f"✅ Scoring logic working: Wrong={wrong_score}%, Correct={correct_score}%")
                        return True
                    else:
                        self.log_test("Scoring Logic Verification", False, 
                                    f"❌ Scoring logic broken: Wrong={wrong_score}%, Correct={correct_score}%")
                        return False
                else:
                    self.log_test("Scoring Logic Verification", False, 
                                f"Correct answer submission failed: {correct_response.status_code}")
                    return False
            else:
                self.log_test("Scoring Logic Verification", False, 
                            f"Wrong answer submission failed: {wrong_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Scoring Logic Verification", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_debug(self):
        """Run comprehensive debugging of the 0% scoring issue"""
        print("🚨 URGENT: Final Exam Scoring Debug - 0% Score Investigation")
        print("=" * 80)
        print("Issue: Users getting 0% scores despite answering correctly")
        print("Environment: https://lms-progression-1.preview.emergentagent.com")
        print("=" * 80)
        
        # Step 1: Authenticate both admin and student
        if not self.authenticate_admin():
            print("❌ Admin authentication failed. Cannot proceed.")
            return False
        
        if not self.authenticate_student():
            print("❌ Student authentication failed. Cannot proceed.")
            return False
        
        # Step 2: Verify deployed backend model has correctAnswer field
        print("\n🔍 STEP 1: Verifying deployed backend model structure...")
        model_verified = self.verify_deployed_backend_model()
        
        # Step 3: Analyze live final test data
        print("\n🔍 STEP 2: Analyzing live final test data structure...")
        live_data_ok = self.analyze_live_final_test_data()
        
        # Step 4: Test submission flow with debugging
        print("\n🔍 STEP 3: Testing submission flow with detailed debugging...")
        submission_ok = self.test_submission_flow_debug()
        
        # Step 5: Test answer format matching
        print("\n🔍 STEP 4: Testing answer format matching...")
        format_ok = self.test_answer_format_matching()
        
        # Step 6: Verify scoring logic
        print("\n🔍 STEP 5: Verifying backend scoring logic...")
        scoring_ok = self.verify_scoring_logic_backend()
        
        # Summary
        print("\n" + "=" * 80)
        print("🔍 DEBUGGING SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests < total_tests:
            print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
            print("\n🚨 CRITICAL ISSUES FOUND:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        # Root cause analysis
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        if not model_verified:
            print("  🚨 CRITICAL: Backend model missing correctAnswer field")
        if not live_data_ok:
            print("  🚨 CRITICAL: Live data structure issues detected")
        if not submission_ok:
            print("  🚨 CRITICAL: Submission flow producing 0% scores")
        if not format_ok:
            print("  🚨 CRITICAL: Answer format matching issues")
        if not scoring_ok:
            print("  🚨 CRITICAL: Backend scoring logic broken")
        
        if success_rate >= 80:
            print("  ✅ No critical issues found - scoring should work correctly")
        else:
            print("  ❌ Critical issues identified - immediate fix required")
        
        return success_rate >= 80

if __name__ == "__main__":
    debugger = FinalExamScoringDebugger()
    success = debugger.run_comprehensive_debug()
    sys.exit(0 if success else 1)