#!/usr/bin/env python3
"""
Comprehensive Grading System Test
=================================

Testing the grading system for final exams and quizzes:
1. Test final exam attempts and submissions
2. Test select-all-that-apply scoring logic
3. Test manual grading endpoints
4. Test subjective question grading
5. Investigate grading conflicts

Authentication credentials:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class GradingSystemTestSuite:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.admin_user = None
        self.student_user = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.admin_user = data["user"]
                self.log_test(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as {self.admin_user['full_name']} ({self.admin_user['role']})"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication", 
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, error_msg=str(e))
            return False

    def authenticate_student(self):
        """Authenticate student user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=STUDENT_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_user = data["user"]
                self.log_test(
                    "Student Authentication",
                    True,
                    f"Successfully authenticated as {self.student_user['full_name']} ({self.student_user['role']})"
                )
                return True
            else:
                self.log_test(
                    "Student Authentication",
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, error_msg=str(e))
            return False

    def get_headers(self, token):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {token}"}

    def test_final_tests_access(self):
        """Test access to final tests"""
        try:
            response = requests.get(f"{BACKEND_URL}/final-tests", headers=self.get_headers(self.student_token))
            
            if response.status_code == 200:
                final_tests = response.json()
                self.log_test(
                    "Final Tests Access",
                    True,
                    f"Found {len(final_tests)} final tests available to student"
                )
                return final_tests
            else:
                self.log_test(
                    "Final Tests Access",
                    False,
                    f"Failed to get final tests: {response.status_code}",
                    response.text
                )
                return []
                
        except Exception as e:
            self.log_test("Final Tests Access", False, error_msg=str(e))
            return []

    def test_final_test_attempts(self):
        """Test final test attempts"""
        try:
            final_tests = self.test_final_tests_access()
            if not final_tests:
                self.log_test(
                    "Final Test Attempts",
                    False,
                    "No final tests available to test attempts"
                )
                return False
            
            # Test with first available final test
            final_test = final_tests[0]
            test_id = final_test["id"]
            
            response = requests.get(
                f"{BACKEND_URL}/final-tests/{test_id}/attempts",
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code == 200:
                attempts = response.json()
                self.log_test(
                    "Final Test Attempts",
                    True,
                    f"Found {len(attempts)} attempts for final test '{final_test.get('title', 'Unknown')}'"
                )
                return attempts
            else:
                self.log_test(
                    "Final Test Attempts",
                    False,
                    f"Failed to get attempts: {response.status_code}",
                    response.text
                )
                return []
                
        except Exception as e:
            self.log_test("Final Test Attempts", False, error_msg=str(e))
            return []

    def test_all_submissions_endpoint(self):
        """Test the all submissions endpoint"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/all/submissions",
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code == 200:
                data = response.json()
                submissions = data.get("submissions", [])
                
                # Analyze submissions for grading issues
                select_all_issues = []
                subjective_ungraded = []
                grading_conflicts = []
                
                for submission in submissions:
                    question_type = submission.get("questionType", "")
                    score = submission.get("score")
                    is_graded = submission.get("isGraded", False)
                    student_answer = submission.get("studentAnswer")
                    correct_answer = submission.get("correctAnswer")
                    
                    # Check for select-all-that-apply issues
                    if question_type == "select-all-that-apply" and score == 0:
                        select_all_issues.append({
                            "submission_id": submission.get("id"),
                            "student_name": submission.get("studentName"),
                            "student_answer": student_answer,
                            "correct_answer": correct_answer,
                            "question_text": submission.get("questionText", "")[:50] + "..."
                        })
                    
                    # Check for ungraded subjective questions
                    if question_type in ["short-answer", "long-form"] and not is_graded:
                        subjective_ungraded.append({
                            "submission_id": submission.get("id"),
                            "student_name": submission.get("studentName"),
                            "question_type": question_type,
                            "student_answer": str(student_answer)[:100] + "..." if student_answer else "No answer"
                        })
                
                details = f"Found {len(submissions)} total submissions. "
                details += f"Select-all 0% scores: {len(select_all_issues)}, "
                details += f"Ungraded subjective: {len(subjective_ungraded)}"
                
                self.log_test(
                    "All Submissions Analysis",
                    True,
                    details
                )
                
                # Store for further analysis
                self.select_all_issues = select_all_issues
                self.subjective_ungraded = subjective_ungraded
                
                return True
            else:
                self.log_test(
                    "All Submissions Analysis",
                    False,
                    f"Failed to get submissions: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("All Submissions Analysis", False, error_msg=str(e))
            return False

    def test_select_all_scoring_issues(self):
        """Test select-all-that-apply scoring issues"""
        try:
            if not hasattr(self, 'select_all_issues') or not self.select_all_issues:
                self.log_test(
                    "Select All Scoring Issues",
                    True,
                    "No select-all-that-apply scoring issues found"
                )
                return True
            
            issues_analyzed = []
            
            for issue in self.select_all_issues[:3]:  # Analyze first 3 issues
                student_answer = issue["student_answer"]
                correct_answer = issue["correct_answer"]
                
                analysis = {
                    "student_name": issue["student_name"],
                    "student_answer_type": type(student_answer).__name__,
                    "student_answer_value": student_answer,
                    "correct_answer_type": type(correct_answer).__name__,
                    "correct_answer_value": correct_answer,
                    "potential_issue": ""
                }
                
                # Identify potential scoring issues
                if isinstance(student_answer, str) and isinstance(correct_answer, list):
                    analysis["potential_issue"] = "Type mismatch: student answer is string, expected is list"
                elif isinstance(student_answer, list) and isinstance(correct_answer, str):
                    analysis["potential_issue"] = "Type mismatch: student answer is list, expected is string"
                elif isinstance(student_answer, list) and isinstance(correct_answer, list):
                    if set(student_answer) == set(correct_answer):
                        analysis["potential_issue"] = "Answers match but scored 0% - scoring logic error"
                    else:
                        analysis["potential_issue"] = f"Partial match: student selected {len(student_answer)} items, expected {len(correct_answer)} items"
                else:
                    analysis["potential_issue"] = "Unknown format issue"
                
                issues_analyzed.append(analysis)
            
            self.log_test(
                "Select All Scoring Issues",
                False,
                f"Found {len(self.select_all_issues)} select-all questions with 0% scores",
                json.dumps(issues_analyzed, indent=2)
            )
            return False
            
        except Exception as e:
            self.log_test("Select All Scoring Issues", False, error_msg=str(e))
            return False

    def test_manual_grading_workflow(self):
        """Test manual grading workflow"""
        try:
            if not hasattr(self, 'subjective_ungraded') or not self.subjective_ungraded:
                self.log_test(
                    "Manual Grading Workflow",
                    True,
                    "No ungraded subjective questions found"
                )
                return True
            
            # Test grading with first ungraded submission
            test_submission = self.subjective_ungraded[0]
            submission_id = test_submission["submission_id"]
            
            # Test grading endpoint
            grading_data = {
                "score": 1,
                "feedback": "Test manual grading - comprehensive grading system test",
                "isGraded": True
            }
            
            response = requests.put(
                f"{BACKEND_URL}/subjective-submissions/{submission_id}/grade",
                json=grading_data,
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code in [200, 201]:
                self.log_test(
                    "Manual Grading Workflow",
                    True,
                    f"Successfully graded submission {submission_id} for student {test_submission['student_name']}"
                )
                return True
            else:
                self.log_test(
                    "Manual Grading Workflow",
                    False,
                    f"Failed to grade submission {submission_id}: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Manual Grading Workflow", False, error_msg=str(e))
            return False

    def test_quiz_attempts_and_scoring(self):
        """Test quiz attempts and scoring"""
        try:
            # Get available quizzes
            response = requests.get(f"{BACKEND_URL}/quizzes", headers=self.get_headers(self.student_token))
            
            if response.status_code != 200:
                self.log_test(
                    "Quiz Attempts and Scoring",
                    False,
                    f"Failed to get quizzes: {response.status_code}",
                    response.text
                )
                return False
            
            quizzes = response.json()
            if not quizzes:
                self.log_test(
                    "Quiz Attempts and Scoring",
                    True,
                    "No quizzes available for testing"
                )
                return True
            
            # Test with first quiz
            quiz = quizzes[0]
            quiz_id = quiz["id"]
            
            # Get quiz attempts
            response = requests.get(
                f"{BACKEND_URL}/quizzes/{quiz_id}/attempts",
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code == 200:
                attempts = response.json()
                self.log_test(
                    "Quiz Attempts and Scoring",
                    True,
                    f"Found {len(attempts)} attempts for quiz '{quiz.get('title', 'Unknown')}'"
                )
                return True
            else:
                self.log_test(
                    "Quiz Attempts and Scoring",
                    False,
                    f"Failed to get quiz attempts: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Quiz Attempts and Scoring", False, error_msg=str(e))
            return False

    def test_grading_system_health(self):
        """Test overall grading system health"""
        try:
            # Test various grading-related endpoints
            endpoints_to_test = [
                ("/courses/all/submissions", "All Submissions"),
                ("/final-tests", "Final Tests"),
                ("/quizzes", "Quizzes")
            ]
            
            healthy_endpoints = 0
            total_endpoints = len(endpoints_to_test)
            
            for endpoint, name in endpoints_to_test:
                response = requests.get(
                    f"{BACKEND_URL}{endpoint}",
                    headers=self.get_headers(self.admin_token)
                )
                
                if response.status_code == 200:
                    healthy_endpoints += 1
            
            health_percentage = (healthy_endpoints / total_endpoints) * 100
            
            self.log_test(
                "Grading System Health",
                health_percentage >= 80,
                f"Grading system health: {health_percentage:.1f}% ({healthy_endpoints}/{total_endpoints} endpoints healthy)"
            )
            
            return health_percentage >= 80
            
        except Exception as e:
            self.log_test("Grading System Health", False, error_msg=str(e))
            return False

    def run_all_tests(self):
        """Run all grading system tests"""
        print("🚀 Starting Comprehensive Grading System Testing")
        print("=" * 70)
        print()
        
        # Authentication tests
        admin_auth_success = self.authenticate_admin()
        student_auth_success = self.authenticate_student()
        
        if not admin_auth_success or not student_auth_success:
            print("❌ Authentication failed. Cannot proceed with API tests.")
            return False
        
        print("🔐 Authentication completed successfully")
        print()
        
        # Core grading system tests
        test_methods = [
            self.test_final_tests_access,
            self.test_final_test_attempts,
            self.test_all_submissions_endpoint,
            self.test_select_all_scoring_issues,
            self.test_manual_grading_workflow,
            self.test_quiz_attempts_and_scoring,
            self.test_grading_system_health
        ]
        
        print("🧪 Running Comprehensive Grading System Tests")
        print("-" * 50)
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                success = test_method()
                if success:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ FAIL {test_method.__name__} - Exception: {str(e)}")
        
        print()
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 70:
            print("🎉 Comprehensive Grading System Testing: SUCCESS")
            return True
        else:
            print("⚠️  Comprehensive Grading System Testing: NEEDS ATTENTION")
            return False

def main():
    """Main test execution"""
    test_suite = GradingSystemTestSuite()
    
    try:
        success = test_suite.run_all_tests()
        
        # Print detailed results
        print("\n" + "=" * 70)
        print("DETAILED TEST RESULTS")
        print("=" * 70)
        
        for result in test_suite.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   📝 {result['details']}")
            if result["error"]:
                print(f"   ⚠️  {result['error']}")
            print()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Testing failed with exception: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())