#!/usr/bin/env python3
"""
Focused Multiple Choice Final Exam Scoring Test
===============================================

This test focuses specifically on the scoring functionality to verify the 0% bug fix.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://learning-score-fix.preview.emergentagent.com"
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

class FocusedScoringTest:
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

    def create_simple_test(self):
        """Create a simple final test for scoring verification"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get or create a program
            programs_response = requests.get(f"{API_BASE}/programs", headers=headers)
            programs = programs_response.json() if programs_response.status_code == 200 else []
            
            if not programs:
                # Create a simple program
                program_data = {
                    "title": "Scoring Test Program",
                    "description": "Test program for scoring verification",
                    "courseIds": [],
                    "nestedProgramIds": []
                }
                prog_response = requests.post(f"{API_BASE}/programs", json=program_data, headers=headers)
                if prog_response.status_code == 200:
                    program_id = prog_response.json()['id']
                else:
                    self.log_result("Create Test Program", False, f"HTTP {prog_response.status_code}")
                    return None
            else:
                program_id = programs[0]['id']
            
            # Create simple final test
            final_test_data = {
                "title": f"Scoring Fix Test - {datetime.now().strftime('%H%M%S')}",
                "description": "Simple test to verify Multiple Choice scoring fix",
                "programId": program_id,
                "timeLimit": 15,
                "passingScore": 50,
                "isPublished": True,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is 1 + 1?",
                        "options": ["1", "2", "3", "4"],
                        "correctAnswer": "1",  # Index 1 = "2"
                        "points": 25,
                        "explanation": "1 + 1 = 2"
                    },
                    {
                        "type": "multiple_choice",
                        "question": "What color is the sun?",
                        "options": ["Blue", "Yellow", "Green", "Purple"],
                        "correctAnswer": "1",  # Index 1 = "Yellow"
                        "points": 25,
                        "explanation": "The sun appears yellow"
                    },
                    {
                        "type": "true_false",
                        "question": "Water boils at 100°C.",
                        "options": ["True", "False"],
                        "correctAnswer": "0",  # Index 0 = "True"
                        "points": 25,
                        "explanation": "Water boils at 100°C at sea level"
                    },
                    {
                        "type": "true_false",
                        "question": "The Earth is flat.",
                        "options": ["True", "False"],
                        "correctAnswer": "1",  # Index 1 = "False"
                        "points": 25,
                        "explanation": "The Earth is spherical"
                    }
                ]
            }
            
            response = requests.post(f"{API_BASE}/final-tests", json=final_test_data, headers=headers)
            if response.status_code == 200:
                test_id = response.json()['id']
                self.log_result("Create Simple Test", True, f"Test ID: {test_id}")
                return test_id
            else:
                self.log_result("Create Simple Test", False, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_result("Create Simple Test", False, f"Exception: {str(e)}")
            return None

    def test_perfect_score(self, test_id):
        """Test perfect score (all correct answers)"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Submit all correct answers using INDEX format (the fix)
            attempt_data = {
                "finalTestId": test_id,
                "answers": [
                    {"questionId": "q1", "answer": "1"},  # Correct: "2"
                    {"questionId": "q2", "answer": "1"},  # Correct: "Yellow"
                    {"questionId": "q3", "answer": "0"},  # Correct: "True"
                    {"questionId": "q4", "answer": "1"}   # Correct: "False"
                ]
            }
            
            response = requests.post(f"{API_BASE}/final-test-attempts", json=attempt_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                score = data.get('score', 0)
                percentage = data.get('percentage', 0)
                passed = data.get('passed', False)
                
                # CRITICAL TEST: Should get 100% for all correct answers
                if score == 100 and percentage == 100.0 and passed:
                    self.log_result("Perfect Score Test", True, 
                                  f"✅ SCORING FIX WORKING: {score}/100 points ({percentage}%), Passed: {passed}")
                    return True
                elif score > 0:
                    self.log_result("Perfect Score Test", True, 
                                  f"⚠️ PARTIAL SUCCESS: {score}/100 points ({percentage}%), Passed: {passed}")
                    return True
                else:
                    self.log_result("Perfect Score Test", False, 
                                  f"🚨 CRITICAL BUG: Still getting 0% score! Score: {score}, Percentage: {percentage}")
                    return False
            else:
                self.log_result("Perfect Score Test", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Perfect Score Test", False, f"Exception: {str(e)}")
            return False

    def test_zero_score(self, test_id):
        """Test zero score (all wrong answers)"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Submit all wrong answers
            attempt_data = {
                "finalTestId": test_id,
                "answers": [
                    {"questionId": "q1", "answer": "0"},  # Wrong: "1" (correct is "2")
                    {"questionId": "q2", "answer": "0"},  # Wrong: "Blue" (correct is "Yellow")
                    {"questionId": "q3", "answer": "1"},  # Wrong: "False" (correct is "True")
                    {"questionId": "q4", "answer": "0"}   # Wrong: "True" (correct is "False")
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
                    self.log_result("Zero Score Test", True, 
                                  f"Score: {score}/100 points ({percentage}%), Passed: {passed}")
                    return True
                else:
                    self.log_result("Zero Score Test", False, 
                                  f"Expected 0% for wrong answers, got {score} points ({percentage}%)")
                    return False
            else:
                self.log_result("Zero Score Test", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Zero Score Test", False, f"Exception: {str(e)}")
            return False

    def test_partial_score(self, test_id):
        """Test partial score (half correct answers)"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Submit half correct answers
            attempt_data = {
                "finalTestId": test_id,
                "answers": [
                    {"questionId": "q1", "answer": "1"},  # Correct: 25 points
                    {"questionId": "q2", "answer": "0"},  # Wrong: 0 points
                    {"questionId": "q3", "answer": "0"},  # Correct: 25 points
                    {"questionId": "q4", "answer": "0"}   # Wrong: 0 points
                ]
            }
            
            response = requests.post(f"{API_BASE}/final-test-attempts", json=attempt_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                score = data.get('score', 0)
                percentage = data.get('percentage', 0)
                passed = data.get('passed', False)
                
                # Should get 50% (50/100 points)
                if score == 50 and percentage == 50.0 and passed:
                    self.log_result("Partial Score Test", True, 
                                  f"Score: {score}/100 points ({percentage}%), Passed: {passed}")
                    return True
                else:
                    self.log_result("Partial Score Test", False, 
                                  f"Expected 50 points (50%), got {score} points ({percentage}%)")
                    return False
            else:
                self.log_result("Partial Score Test", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Partial Score Test", False, f"Exception: {str(e)}")
            return False

    def run_focused_tests(self):
        """Run focused scoring tests"""
        print("🎯 FOCUSED MULTIPLE CHOICE SCORING FIX TEST")
        print("=" * 50)
        print()
        
        if not self.authenticate():
            return False
            
        test_id = self.create_simple_test()
        if not test_id:
            return False
            
        # Critical scoring tests
        perfect_success = self.test_perfect_score(test_id)
        zero_success = self.test_zero_score(test_id)
        partial_success = self.test_partial_score(test_id)
        
        return perfect_success and zero_success and partial_success

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("🎯 FOCUSED SCORING TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ PASSED: {passed}/{total} tests ({success_rate:.1f}% success rate)")
        
        # Check critical tests
        critical_tests = ["Perfect Score Test", "Zero Score Test", "Partial Score Test"]
        critical_results = [r for r in self.test_results if r['test'] in critical_tests]
        critical_passed = sum(1 for r in critical_results if r['success'])
        
        print()
        print("🔍 CRITICAL ASSESSMENT:")
        if critical_passed == len(critical_tests):
            print("✅ MULTIPLE CHOICE SCORING FIX IS WORKING!")
            print("   - Students get correct scores (not 0%)")
            print("   - Index-based answer format working")
            print("   - Scoring logic functional")
        else:
            print("❌ MULTIPLE CHOICE SCORING FIX HAS ISSUES!")
            print("   - Students may still get incorrect scores")
            
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = FocusedScoringTest()
    
    try:
        success = tester.run_focused_tests()
        result = tester.print_summary()
        
        if success and result:
            print("\n🎉 CONCLUSION: Multiple Choice scoring fix is working!")
            sys.exit(0)
        else:
            print("\n🚨 CONCLUSION: Multiple Choice scoring fix needs attention!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()