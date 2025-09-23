#!/usr/bin/env python3
"""
Real Final Exam Submission Test
===============================

Test a real submission to the test we just created to see if scoring works.

Admin: brayden.t@covesmart.com / Hawaii2020!
Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime

BACKEND_URL = "https://learning-score-fix.preview.emergentagent.com/api"

ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"
STUDENT_EMAIL = "karlo.student@alder.com"
STUDENT_PASSWORD = "StudentPermanent123!"

class RealSubmissionTester:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        
    def authenticate(self):
        """Authenticate both users"""
        # Admin auth
        admin_response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "username_or_email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if admin_response.status_code != 200:
            print(f"❌ Admin auth failed: {admin_response.status_code}")
            return False
            
        self.admin_token = admin_response.json()["access_token"]
        print(f"✅ Admin authenticated")
        
        # Student auth
        student_response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "username_or_email": STUDENT_EMAIL,
            "password": STUDENT_PASSWORD
        })
        
        if student_response.status_code != 200:
            print(f"❌ Student auth failed: {student_response.status_code}")
            return False
            
        self.student_token = student_response.json()["access_token"]
        print(f"✅ Student authenticated")
        
        return True
    
    def find_recent_test(self):
        """Find the most recent test we can submit to"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        response = requests.get(f"{BACKEND_URL}/final-tests", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get tests: {response.status_code}")
            return None
        
        tests = response.json()
        
        # Find a published test with questions (we need to check individual tests)
        for test in tests:
            if test.get('isPublished') and test.get('questionCount', 0) > 0:
                # Get the full test details
                test_response = requests.get(f"{BACKEND_URL}/final-tests/{test['id']}", headers=headers)
                
                if test_response.status_code == 200:
                    full_test = test_response.json()
                    if full_test.get('questions'):
                        print(f"✅ Found test with questions: {full_test['title']}")
                        print(f"   Test ID: {full_test['id']}")
                        print(f"   Questions: {len(full_test['questions'])}")
                        print(f"   Total Points: {full_test.get('totalPoints', 0)}")
                        return full_test
        
        print(f"❌ No suitable test found")
        return None
    
    def submit_to_test(self, test):
        """Submit answers to the test"""
        student_headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # Create answers for all questions
        answers = []
        for question in test['questions']:
            q_id = question.get('id')
            q_type = question.get('type')
            
            if q_type == 'multiple_choice':
                # Submit the correct answer
                correct_answer = question.get('correctAnswer', '0')
                answers.append({
                    "questionId": q_id,
                    "answer": str(correct_answer)
                })
                print(f"   Question {q_id}: Submitting correct answer '{correct_answer}'")
                
            elif q_type == 'true_false':
                # Submit the correct answer
                correct_answer = question.get('correctAnswer', 'true')
                answers.append({
                    "questionId": q_id,
                    "answer": str(correct_answer)
                })
                print(f"   Question {q_id}: Submitting correct answer '{correct_answer}'")
                
            else:
                # For other types, submit a default
                answers.append({
                    "questionId": q_id,
                    "answer": "0"
                })
                print(f"   Question {q_id}: Submitting default answer '0'")
        
        submission_data = {
            "testId": test['id'],
            "programId": test['programId'],
            "answers": answers,
            "timeSpent": 60
        }
        
        print(f"\n🔍 SUBMITTING TO TEST:")
        print(f"   Test: {test['title']}")
        print(f"   Test ID: {test['id']}")
        print(f"   Program ID: {test['programId']}")
        print(f"   Answers: {len(answers)}")
        
        response = requests.post(f"{BACKEND_URL}/final-test-attempts", 
                               json=submission_data, headers=student_headers)
        
        print(f"\n🔍 SUBMISSION RESULT:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"   ✅ Submission successful!")
            print(f"   Score: {result.get('score', 0)}%")
            print(f"   Points Earned: {result.get('pointsEarned', 0)}")
            print(f"   Total Points: {result.get('totalPoints', 0)}")
            print(f"   Passed: {result.get('isPassed', False)}")
            
            # Check if we got the expected score
            expected_total = test.get('totalPoints', 0)
            actual_total = result.get('totalPoints', 0)
            actual_score = result.get('score', 0)
            
            if actual_total == expected_total and actual_score > 0:
                print(f"   ✅ SCORING WORKING CORRECTLY!")
            elif actual_total != expected_total:
                print(f"   ❌ Total points mismatch: Expected {expected_total}, Got {actual_total}")
            elif actual_score == 0:
                print(f"   ❌ ZERO SCORE ISSUE CONFIRMED")
            
            return result
        else:
            print(f"   ❌ Submission failed")
            print(f"   Error: {response.text}")
            return None
    
    def run_test(self):
        """Run the real submission test"""
        print("🎯 REAL FINAL EXAM SUBMISSION TEST")
        print("=" * 50)
        
        if not self.authenticate():
            return False
        
        test = self.find_recent_test()
        if not test:
            return False
        
        result = self.submit_to_test(test)
        
        print("\n" + "=" * 50)
        print("🎯 REAL SUBMISSION TEST COMPLETE")
        
        if result:
            score = result.get('score', 0)
            if score > 0:
                print("✅ Final exam scoring is working correctly!")
            else:
                print("❌ Final exam scoring is still broken (0% score)")
        else:
            print("❌ Submission failed")
        
        return result is not None and result.get('score', 0) > 0

if __name__ == "__main__":
    tester = RealSubmissionTester()
    success = tester.run_test()
    sys.exit(0 if success else 1)