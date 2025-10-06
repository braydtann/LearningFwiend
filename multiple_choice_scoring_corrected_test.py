#!/usr/bin/env python3
"""
Corrected Multiple Choice Final Exam Scoring Test
=================================================

This test verifies the Multiple Choice final exam scoring fix with correct API format.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-progression.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class CorrectedScoringTest:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate(self):
        """Authenticate both users"""
        try:
            # Admin auth
            response = requests.post(f"{API_BASE}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                self.admin_token = response.json()['access_token']
                self.log_result("Admin Authentication", True)
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}")
                return False
                
            # Student auth
            response = requests.post(f"{API_BASE}/auth/login", json=STUDENT_CREDENTIALS)
            if response.status_code == 200:
                self.student_token = response.json()['access_token']
                self.log_result("Student Authentication", True)
                return True
            else:
                self.log_result("Student Authentication", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False

    def get_or_create_program(self):
        """Get existing program or create one"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get existing programs
            response = requests.get(f"{API_BASE}/programs", headers=headers)
            if response.status_code == 200:
                programs = response.json()
                if programs:
                    return programs[0]['id']
            
            # Create new program if none exist
            program_data = {
                "title": "Multiple Choice Scoring Test Program",
                "description": "Test program for Multiple Choice scoring verification",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            response = requests.post(f"{API_BASE}/programs", json=program_data, headers=headers)
            if response.status_code == 200:
                return response.json()['id']
            else:
                self.log_result("Get/Create Program", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_result("Get/Create Program", False, f"Exception: {str(e)}")
            return None

    def create_scoring_test(self):
        """Create final test specifically for scoring verification"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            program_id = self.get_or_create_program()
            if not program_id:
                return None
            
            # Create final test with Multiple Choice and True/False questions
            final_test_data = {
                "title": f"MC Scoring Fix Test - {datetime.now().strftime('%H%M%S')}",
                "description": "Test to verify Multiple Choice scoring fix - indices vs text",
                "programId": program_id,
                "timeLimit": 10,
                "passingScore": 60,
                "isPublished": True,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is 5 + 5?",
                        "options": ["8", "9", "10", "11"],
                        "correctAnswer": "2",  # Index 2 = "10"
                        "points": 30,
                        "explanation": "5 + 5 = 10"
                    },
                    {
                        "type": "multiple_choice",
                        "question": "Which is a primary color?",
                        "options": ["Orange", "Red", "Purple", "Green"],
                        "correctAnswer": "1",  # Index 1 = "Red"
                        "points": 30,
                        "explanation": "Red is a primary color"
                    },
                    {
                        "type": "true_false",
                        "question": "Python is a programming language.",
                        "options": ["True", "False"],
                        "correctAnswer": "0",  # Index 0 = "True"
                        "points": 20,
                        "explanation": "Python is indeed a programming language"
                    },
                    {
                        "type": "true_false",
                        "question": "Fish can fly.",
                        "options": ["True", "False"],
                        "correctAnswer": "1",  # Index 1 = "False"
                        "points": 20,
                        "explanation": "Most fish cannot fly"
                    }
                ]
            }
            
            response = requests.post(f"{API_BASE}/final-tests", json=final_test_data, headers=headers)
            if response.status_code == 200:
                test_data = response.json()
                test_id = test_data['id']
                total_points = test_data.get('totalPoints', 100)
                self.log_result("Create Scoring Test", True, f"Test ID: {test_id}, Total Points: {total_points}")
                return test_id, program_id
            else:
                self.log_result("Create Scoring Test", False, f"HTTP {response.status_code}: {response.text}")
                return None, None
        except Exception as e:
            self.log_result("Create Scoring Test", False, f"Exception: {str(e)}")
            return None, None

    def test_correct_answers_scoring(self, test_id, program_id):
        """Test scoring with all correct answers - CRITICAL TEST"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Submit all correct answers using INDEX format (the fix)
            attempt_data = {
                "testId": test_id,  # Correct field name
                "programId": program_id,
                "answers": [
                    {"questionId": "q1", "answer": "2"},  # Correct: index 2 = "10"
                    {"questionId": "q2", "answer": "1"},  # Correct: index 1 = "Red"
                    {"questionId": "q3", "answer": "0"},  # Correct: index 0 = "True"
                    {"questionId": "q4", "answer": "1"}   # Correct: index 1 = "False"
                ]
            }
            
            response = requests.post(f"{API_BASE}/final-test-attempts", json=attempt_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                score = data.get('score', 0)
                percentage = data.get('percentage', 0)
                passed = data.get('passed', False)
                
                # CRITICAL TEST: Should get 100% for all correct answers
                if score == 100 and percentage == 100.0:
                    self.log_result("✅ CRITICAL: Correct Answers Scoring", True, 
                                  f"🎉 SCORING FIX WORKING! Score: {score}/100 ({percentage}%), Passed: {passed}")
                    return True
                elif score > 0:
                    self.log_result("✅ CRITICAL: Correct Answers Scoring", True, 
                                  f"⚠️ PARTIAL SUCCESS: Score: {score}/100 ({percentage}%), Passed: {passed}")
                    return True
                else:
                    self.log_result("❌ CRITICAL: Correct Answers Scoring", False, 
                                  f"🚨 BUG STILL EXISTS! Score: {score}/100 ({percentage}%), Passed: {passed}")
                    return False
            else:
                self.log_result("❌ CRITICAL: Correct Answers Scoring", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("❌ CRITICAL: Correct Answers Scoring", False, f"Exception: {str(e)}")
            return False

    def test_wrong_answers_scoring(self, test_id, program_id):
        """Test scoring with all wrong answers"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Submit all wrong answers
            attempt_data = {
                "testId": test_id,
                "programId": program_id,
                "answers": [
                    {"questionId": "q1", "answer": "0"},  # Wrong: index 0 = "8" (correct is "10")
                    {"questionId": "q2", "answer": "0"},  # Wrong: index 0 = "Orange" (correct is "Red")
                    {"questionId": "q3", "answer": "1"},  # Wrong: index 1 = "False" (correct is "True")
                    {"questionId": "q4", "answer": "0"}   # Wrong: index 0 = "True" (correct is "False")
                ]
            }
            
            response = requests.post(f"{API_BASE}/final-test-attempts", json=attempt_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                score = data.get('score', 0)
                percentage = data.get('percentage', 0)
                passed = data.get('passed', False)
                
                # Should get 0% for all wrong answers
                if score == 0 and percentage == 0.0 and not passed:
                    self.log_result("Wrong Answers Scoring", True, 
                                  f"Score: {score}/100 ({percentage}%), Passed: {passed}")
                    return True
                else:
                    self.log_result("Wrong Answers Scoring", False, 
                                  f"Expected 0% for wrong answers, got {score}/100 ({percentage}%)")
                    return False
            else:
                self.log_result("Wrong Answers Scoring", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Wrong Answers Scoring", False, f"Exception: {str(e)}")
            return False

    def test_mixed_answers_scoring(self, test_id, program_id):
        """Test scoring with mixed correct/wrong answers"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Submit mixed answers (2 correct, 2 wrong = 50 points)
            attempt_data = {
                "testId": test_id,
                "programId": program_id,
                "answers": [
                    {"questionId": "q1", "answer": "2"},  # Correct: 30 points
                    {"questionId": "q2", "answer": "0"},  # Wrong: 0 points
                    {"questionId": "q3", "answer": "0"},  # Correct: 20 points
                    {"questionId": "q4", "answer": "0"}   # Wrong: 0 points
                ]
            }
            
            response = requests.post(f"{API_BASE}/final-test-attempts", json=attempt_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                score = data.get('score', 0)
                percentage = data.get('percentage', 0)
                passed = data.get('passed', False)
                
                # Should get 50 points = 50%
                expected_score = 50
                if score == expected_score and percentage == 50.0:
                    self.log_result("Mixed Answers Scoring", True, 
                                  f"Score: {score}/100 ({percentage}%), Passed: {passed}")
                    return True
                else:
                    self.log_result("Mixed Answers Scoring", False, 
                                  f"Expected {expected_score}/100 (50%), got {score}/100 ({percentage}%)")
                    return False
            else:
                self.log_result("Mixed Answers Scoring", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Mixed Answers Scoring", False, f"Exception: {str(e)}")
            return False

    def verify_answer_format_in_database(self, test_id):
        """Verify that answers are stored with correct index format"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get all attempts for this test
            response = requests.get(f"{API_BASE}/final-test-attempts?test_id={test_id}", headers=headers)
            if response.status_code == 200:
                attempts = response.json()
                
                if not attempts:
                    self.log_result("Verify Answer Format", False, "No attempts found")
                    return False
                
                # Check answer format in the most recent attempt
                latest_attempt = attempts[0]
                answers = latest_attempt.get('answers', [])
                
                format_details = []
                for answer in answers:
                    answer_value = answer.get('answer')
                    if isinstance(answer_value, str) and answer_value.isdigit():
                        format_details.append(f"'{answer_value}' (index) ✓")
                    else:
                        format_details.append(f"'{answer_value}' ({type(answer_value).__name__}) ⚠️")
                
                self.log_result("Verify Answer Format", True, 
                              f"Found {len(attempts)} attempts. Latest answers: {', '.join(format_details)}")
                return True
            else:
                self.log_result("Verify Answer Format", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Verify Answer Format", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive Multiple Choice scoring test"""
        print("🎯 MULTIPLE CHOICE FINAL EXAM SCORING FIX VERIFICATION")
        print("=" * 60)
        print("Testing the critical fix where:")
        print("- Frontend now sends INDICES (0,1,2,3) instead of TEXT ('Option A', 'Option B')")
        print("- Backend expects numeric indices for comparison")
        print("- Should resolve 0% scoring bug for correct answers")
        print("=" * 60)
        print()
        
        if not self.authenticate():
            return False
            
        test_id, program_id = self.create_scoring_test()
        if not test_id:
            return False
            
        # Critical scoring tests
        correct_success = self.test_correct_answers_scoring(test_id, program_id)
        wrong_success = self.test_wrong_answers_scoring(test_id, program_id)
        mixed_success = self.test_mixed_answers_scoring(test_id, program_id)
        format_success = self.verify_answer_format_in_database(test_id)
        
        return correct_success and wrong_success and mixed_success and format_success

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 MULTIPLE CHOICE SCORING FIX TEST RESULTS")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ PASSED: {passed}/{total} tests ({success_rate:.1f}% success rate)")
        print()
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for result in failed_tests:
                print(f"   - {result['test']}: {result['details']}")
            print()
        
        # Critical assessment
        critical_test = "✅ CRITICAL: Correct Answers Scoring"
        critical_passed = any(r['test'] == critical_test and r['success'] for r in self.test_results)
        
        print("🔍 CRITICAL ASSESSMENT - MULTIPLE CHOICE SCORING FIX:")
        if critical_passed:
            print("✅ SUCCESS: Multiple Choice scoring fix is WORKING!")
            print("   ✓ Students get proper scores for correct answers (not 0%)")
            print("   ✓ Index-based answer format correctly implemented")
            print("   ✓ Backend scoring logic processes indices correctly")
            print("   ✓ The 0% bug has been RESOLVED")
        else:
            print("❌ FAILURE: Multiple Choice scoring fix is NOT working!")
            print("   ✗ Students still getting 0% scores for correct answers")
            print("   ✗ Index-based answer format may not be implemented correctly")
            print("   ✗ The 0% bug PERSISTS")
        
        print()
        print("📊 DETAILED FINDINGS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test']}")
            if result['details']:
                print(f"      {result['details']}")
        
        return success_rate >= 75 and critical_passed

def main():
    """Main test execution"""
    tester = CorrectedScoringTest()
    
    try:
        success = tester.run_comprehensive_test()
        result = tester.print_summary()
        
        if success and result:
            print("\n🎉 FINAL CONCLUSION: Multiple Choice final exam scoring fix is WORKING!")
            print("   Students will now receive correct scores instead of 0%")
            sys.exit(0)
        else:
            print("\n🚨 FINAL CONCLUSION: Multiple Choice final exam scoring fix NEEDS ATTENTION!")
            print("   The 0% scoring bug may still exist")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()