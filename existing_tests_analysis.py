#!/usr/bin/env python3
"""
Analysis of Existing Final Tests - Data Structure Investigation
==============================================================

This script analyzes existing final tests to identify why they're producing 0% scores.
Focus on finding tests with missing correctAnswer fields or malformed question data.

Admin: brayden.t@covesmart.com / Hawaii2020!
Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime

BACKEND_URL = "https://lms-progression.preview.emergentagent.com/api"

ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"
STUDENT_EMAIL = "karlo.student@alder.com"
STUDENT_PASSWORD = "StudentPermanent123!"

class ExistingTestsAnalyzer:
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
    
    def get_all_final_tests(self):
        """Get all final tests and analyze their structure"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        response = requests.get(f"{BACKEND_URL}/final-tests", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get final tests: {response.status_code}")
            return []
            
        tests = response.json()
        print(f"✅ Found {len(tests)} final tests")
        
        return tests
    
    def analyze_test_structure(self, test):
        """Analyze a single test's structure for issues"""
        issues = []
        
        test_id = test.get('id', 'NO_ID')
        title = test.get('title', 'NO_TITLE')
        questions = test.get('questions', [])
        
        print(f"\n🔍 Analyzing Test: {title} (ID: {test_id})")
        print(f"   Questions: {len(questions)}")
        print(f"   Total Points: {test.get('totalPoints', 0)}")
        print(f"   Published: {test.get('isPublished', False)}")
        
        if not questions:
            issues.append("No questions found")
            print("   ❌ No questions found")
            return issues
        
        for i, question in enumerate(questions):
            q_id = question.get('id', 'NO_ID')
            q_type = question.get('type', 'NO_TYPE')
            correct_answer = question.get('correctAnswer')
            points = question.get('points', 0)
            
            print(f"   Question {i+1}: {q_id}")
            print(f"     Type: {q_type}")
            print(f"     Correct Answer: {correct_answer}")
            print(f"     Points: {points}")
            
            # Check for missing correctAnswer
            if correct_answer is None:
                issues.append(f"Question {i+1} missing correctAnswer")
                print(f"     ❌ Missing correctAnswer field")
            
            # Check for missing question ID
            if q_id == 'NO_ID':
                issues.append(f"Question {i+1} missing ID")
                print(f"     ❌ Missing question ID")
            
            # Check question type specific issues
            if q_type == 'multiple_choice':
                options = question.get('options', [])
                if not options:
                    issues.append(f"Question {i+1} missing options")
                    print(f"     ❌ Missing options for multiple choice")
                else:
                    print(f"     Options: {options}")
                    
                    # Check if correctAnswer is valid index
                    if correct_answer is not None:
                        try:
                            correct_index = int(correct_answer)
                            if correct_index < 0 or correct_index >= len(options):
                                issues.append(f"Question {i+1} invalid correctAnswer index")
                                print(f"     ❌ Invalid correctAnswer index: {correct_index} (options: {len(options)})")
                        except (ValueError, TypeError):
                            issues.append(f"Question {i+1} correctAnswer not numeric")
                            print(f"     ❌ correctAnswer not numeric: {correct_answer}")
            
            elif q_type == 'true_false':
                if correct_answer not in ['true', 'false', True, False]:
                    issues.append(f"Question {i+1} invalid true/false answer")
                    print(f"     ❌ Invalid true/false answer: {correct_answer}")
            
            elif q_type == 'select-all-that-apply':
                correct_answers = question.get('correctAnswers')
                if correct_answers is None:
                    issues.append(f"Question {i+1} missing correctAnswers")
                    print(f"     ❌ Missing correctAnswers field")
                else:
                    print(f"     Correct Answers: {correct_answers}")
            
            elif q_type == 'chronological-order':
                correct_order = question.get('correctOrder')
                if correct_order is None:
                    issues.append(f"Question {i+1} missing correctOrder")
                    print(f"     ❌ Missing correctOrder field")
                else:
                    print(f"     Correct Order: {correct_order}")
        
        if issues:
            print(f"   ❌ Found {len(issues)} issues:")
            for issue in issues:
                print(f"     - {issue}")
        else:
            print(f"   ✅ No structural issues found")
        
        return issues
    
    def test_problematic_test_submission(self, test):
        """Try to submit to a problematic test to see the exact failure"""
        if not test.get('questions'):
            print("   ⏭️  Skipping test with no questions")
            return None
            
        test_id = test.get('id')
        questions = test.get('questions', [])
        
        # Create submission with "correct" answers based on what we think is correct
        answers = []
        for question in questions:
            q_id = question.get('id')
            q_type = question.get('type')
            
            if q_type == 'multiple_choice':
                # Try to submit the correctAnswer value
                correct_answer = question.get('correctAnswer', '0')
                answers.append({
                    "questionId": q_id,
                    "answer": str(correct_answer)
                })
            elif q_type == 'true_false':
                # Try to submit the correctAnswer value
                correct_answer = question.get('correctAnswer', 'true')
                answers.append({
                    "questionId": q_id,
                    "answer": str(correct_answer)
                })
            else:
                # For other types, submit a default
                answers.append({
                    "questionId": q_id,
                    "answer": "0"
                })
        
        submission_data = {
            "testId": test_id,
            "programId": test.get('programId'),
            "answers": answers,
            "timeSpent": 30
        }
        
        print(f"   🔍 Testing submission to: {test.get('title', 'Unknown')}")
        print(f"      Submitting {len(answers)} answers")
        
        student_headers = {"Authorization": f"Bearer {self.student_token}"}
        response = requests.post(f"{BACKEND_URL}/final-test-attempts", 
                               json=submission_data, headers=student_headers)
        
        if response.status_code == 200:
            result = response.json()
            score = result.get('score', 0)
            points = result.get('pointsEarned', 0)
            total = result.get('totalPoints', 0)
            
            print(f"      ✅ Submission successful: {score}% ({points}/{total} points)")
            
            if score == 0 and total > 0:
                print(f"      ❌ ZERO SCORE ISSUE CONFIRMED")
                return result
            else:
                print(f"      ✅ Scoring appears to work")
                return result
        else:
            print(f"      ❌ Submission failed: {response.status_code}")
            print(f"         Error: {response.text}")
            return None
    
    def run_analysis(self):
        """Run complete analysis of existing tests"""
        print("🔍 EXISTING FINAL TESTS ANALYSIS")
        print("=" * 50)
        
        if not self.authenticate():
            return False
        
        tests = self.get_all_final_tests()
        if not tests:
            print("❌ No tests found to analyze")
            return False
        
        problematic_tests = []
        
        for test in tests:
            issues = self.analyze_test_structure(test)
            if issues:
                problematic_tests.append({
                    'test': test,
                    'issues': issues
                })
        
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"   Total Tests: {len(tests)}")
        print(f"   Problematic Tests: {len(problematic_tests)}")
        
        if problematic_tests:
            print(f"\n🚨 PROBLEMATIC TESTS FOUND:")
            for item in problematic_tests[:3]:  # Test first 3 problematic tests
                test = item['test']
                issues = item['issues']
                
                print(f"\n   Test: {test.get('title', 'Unknown')}")
                print(f"   Issues: {len(issues)}")
                for issue in issues:
                    print(f"     - {issue}")
                
                # Try to submit to this test
                self.test_problematic_test_submission(test)
        
        print(f"\n🎯 CONCLUSION:")
        if problematic_tests:
            print(f"   ❌ Found {len(problematic_tests)} tests with structural issues")
            print(f"   🔧 These tests need data structure fixes")
        else:
            print(f"   ✅ All tests have proper structure")
        
        return True

if __name__ == "__main__":
    analyzer = ExistingTestsAnalyzer()
    success = analyzer.run_analysis()
    sys.exit(0 if success else 1)