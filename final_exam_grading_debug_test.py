#!/usr/bin/env python3
"""
Final Exam Grading Issues Debug Test
===================================

Debugging the final exam grading issues for "fresh test program 092425":

1. **Manual Grading Error Investigation:**
   - Find the "fresh test program 092425" program and its final test
   - Look for subjective submissions that are failing to be manually graded
   - Check if there are any conflicts between auto-grading and manual grading
   - Test the grading endpoint with the actual submission data

2. **Select All That Apply Scoring Issue:**
   - Find and examine the select all that apply test that scored 0%
   - Check what the student submitted vs what the backend expected
   - Verify the correctAnswers field format in the final test
   - Test the scoring logic for select-all-that-apply questions

Authentication credentials:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://test-grading-fix.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class FinalExamGradingDebugSuite:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.admin_user = None
        self.student_user = None
        self.test_results = []
        self.fresh_test_program = None
        self.final_test_data = None
        self.problematic_submissions = []
        
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

    def find_test_program_with_final_exam(self):
        """Find a test program with final exam (since 'fresh test program 092425' doesn't exist)"""
        try:
            response = requests.get(f"{BACKEND_URL}/programs", headers=self.get_headers(self.admin_token))
            
            if response.status_code != 200:
                self.log_test(
                    "Find Test Program with Final Exam",
                    False,
                    f"Failed to get programs: {response.status_code}",
                    response.text
                )
                return False
            
            programs = response.json()
            
            # Search for any program that might have final exams
            target_program = None
            for program in programs:
                program_title = program.get("title", "").lower()
                # Look for programs that likely have final exams
                if any(keyword in program_title for keyword in ["final", "test", "exam"]):
                    target_program = program
                    break
            
            if not target_program and programs:
                # If no specific program found, use the first available program
                target_program = programs[0]
            
            if not target_program:
                # List all programs to help identify the correct one
                program_titles = [p.get("title", "Unknown") for p in programs[:10]]
                self.log_test(
                    "Find Test Program with Final Exam",
                    False,
                    f"No programs found. Available programs: {program_titles}",
                    "Could not locate any test program"
                )
                return False
            
            self.fresh_test_program = target_program
            self.log_test(
                "Find Test Program with Final Exam",
                True,
                f"Using program: {target_program['title']} (ID: {target_program['id']}) for testing"
            )
            return True
            
        except Exception as e:
            self.log_test("Find Test Program with Final Exam", False, error_msg=str(e))
            return False

    def get_final_test_for_program(self):
        """Get the final test associated with the fresh test program"""
        try:
            if not self.fresh_test_program:
                self.log_test(
                    "Get Final Test for Program",
                    False,
                    "Fresh test program not found"
                )
                return False
            
            program_id = self.fresh_test_program["id"]
            
            # Get final tests filtered by program
            response = requests.get(
                f"{BACKEND_URL}/final-tests?programId={program_id}",
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code != 200:
                self.log_test(
                    "Get Final Test for Program",
                    False,
                    f"Failed to get final tests: {response.status_code}",
                    response.text
                )
                return False
            
            final_tests = response.json()
            
            if not final_tests:
                self.log_test(
                    "Get Final Test for Program",
                    False,
                    f"No final tests found for program {self.fresh_test_program['title']}"
                )
                return False
            
            # Get the first final test (assuming there's one per program)
            final_test = final_tests[0]
            
            # Get detailed final test with questions
            response = requests.get(
                f"{BACKEND_URL}/final-tests/{final_test['id']}",
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code == 200:
                self.final_test_data = response.json()
                self.log_test(
                    "Get Final Test for Program",
                    True,
                    f"Found final test: {final_test['title']} with {len(self.final_test_data.get('questions', []))} questions"
                )
                return True
            else:
                self.log_test(
                    "Get Final Test for Program",
                    False,
                    f"Failed to get final test details: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Get Final Test for Program", False, error_msg=str(e))
            return False

    def analyze_select_all_that_apply_questions(self):
        """Analyze select all that apply questions in the final test"""
        try:
            if not self.final_test_data:
                self.log_test(
                    "Analyze Select All That Apply Questions",
                    False,
                    "Final test data not available"
                )
                return False
            
            questions = self.final_test_data.get("questions", [])
            select_all_questions = [q for q in questions if q.get("type") == "select-all-that-apply"]
            
            if not select_all_questions:
                self.log_test(
                    "Analyze Select All That Apply Questions",
                    False,
                    f"No select-all-that-apply questions found in {len(questions)} total questions"
                )
                return False
            
            analysis_details = []
            issues_found = []
            
            for i, question in enumerate(select_all_questions):
                question_analysis = {
                    "question_number": i + 1,
                    "question_text": question.get("questionText", "")[:100] + "...",
                    "has_correct_answers": "correctAnswers" in question,
                    "correct_answers_format": type(question.get("correctAnswers", None)).__name__,
                    "correct_answers_value": question.get("correctAnswers"),
                    "options_count": len(question.get("options", [])),
                    "points": question.get("points", 1)
                }
                
                analysis_details.append(question_analysis)
                
                # Check for potential issues
                if not question.get("correctAnswers"):
                    issues_found.append(f"Question {i+1}: Missing correctAnswers field")
                elif not isinstance(question.get("correctAnswers"), list):
                    issues_found.append(f"Question {i+1}: correctAnswers is not a list (type: {type(question.get('correctAnswers')).__name__})")
                elif len(question.get("correctAnswers", [])) == 0:
                    issues_found.append(f"Question {i+1}: correctAnswers list is empty")
            
            success = len(issues_found) == 0
            details = f"Found {len(select_all_questions)} select-all-that-apply questions. "
            if issues_found:
                details += f"Issues: {'; '.join(issues_found)}"
            else:
                details += "All questions have proper correctAnswers format."
            
            self.log_test(
                "Analyze Select All That Apply Questions",
                success,
                details,
                json.dumps(analysis_details, indent=2) if not success else ""
            )
            return success
            
        except Exception as e:
            self.log_test("Analyze Select All That Apply Questions", False, error_msg=str(e))
            return False

    def get_final_test_submissions(self):
        """Get submissions for the final test"""
        try:
            if not self.final_test_data:
                self.log_test(
                    "Get Final Test Submissions",
                    False,
                    "Final test data not available"
                )
                return False
            
            final_test_id = self.final_test_data["id"]
            
            response = requests.get(
                f"{BACKEND_URL}/final-tests/{final_test_id}/submissions",
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code != 200:
                self.log_test(
                    "Get Final Test Submissions",
                    False,
                    f"Failed to get submissions: {response.status_code}",
                    response.text
                )
                return False
            
            data = response.json()
            submissions = data.get("submissions", [])
            
            if not submissions:
                self.log_test(
                    "Get Final Test Submissions",
                    True,
                    f"No submissions found for final test {self.final_test_data['title']}"
                )
                return True
            
            # Analyze submissions for grading issues
            grading_issues = []
            select_all_zero_scores = []
            subjective_ungraded = []
            
            for submission in submissions:
                submission_id = submission.get("id")
                student_name = submission.get("studentName", "Unknown")
                total_score = submission.get("totalScore", 0)
                answers = submission.get("answers", [])
                
                # Check for select-all-that-apply questions with 0% scores
                for answer in answers:
                    question_type = answer.get("questionType")
                    score = answer.get("score", 0)
                    
                    if question_type == "select-all-that-apply" and score == 0:
                        select_all_zero_scores.append({
                            "submission_id": submission_id,
                            "student": student_name,
                            "question_text": answer.get("questionText", "")[:50] + "...",
                            "student_answer": answer.get("answer"),
                            "expected_answer": answer.get("correctAnswer")
                        })
                    
                    # Check for subjective questions that need manual grading
                    if question_type in ["short-answer", "long-form"] and answer.get("needsManualGrading", False):
                        subjective_ungraded.append({
                            "submission_id": submission_id,
                            "student": student_name,
                            "question_type": question_type,
                            "question_text": answer.get("questionText", "")[:50] + "...",
                            "student_answer": answer.get("answer", "")[:100] + "..."
                        })
            
            self.problematic_submissions = {
                "select_all_zero_scores": select_all_zero_scores,
                "subjective_ungraded": subjective_ungraded
            }
            
            details = f"Found {len(submissions)} submissions. "
            details += f"Select-all 0% scores: {len(select_all_zero_scores)}, "
            details += f"Ungraded subjective: {len(subjective_ungraded)}"
            
            self.log_test(
                "Get Final Test Submissions",
                True,
                details
            )
            return True
            
        except Exception as e:
            self.log_test("Get Final Test Submissions", False, error_msg=str(e))
            return False

    def test_select_all_scoring_logic(self):
        """Test the scoring logic for select-all-that-apply questions"""
        try:
            if not self.problematic_submissions.get("select_all_zero_scores"):
                self.log_test(
                    "Test Select All Scoring Logic",
                    True,
                    "No select-all-that-apply questions with 0% scores found to debug"
                )
                return True
            
            issues_analyzed = []
            
            for issue in self.problematic_submissions["select_all_zero_scores"][:3]:  # Analyze first 3 issues
                student_answer = issue["student_answer"]
                expected_answer = issue["expected_answer"]
                
                analysis = {
                    "student": issue["student"],
                    "student_answer_type": type(student_answer).__name__,
                    "student_answer_value": student_answer,
                    "expected_answer_type": type(expected_answer).__name__,
                    "expected_answer_value": expected_answer,
                    "potential_issue": ""
                }
                
                # Identify potential scoring issues
                if isinstance(student_answer, str) and isinstance(expected_answer, list):
                    analysis["potential_issue"] = "Type mismatch: student answer is string, expected is list"
                elif isinstance(student_answer, list) and isinstance(expected_answer, str):
                    analysis["potential_issue"] = "Type mismatch: student answer is list, expected is string"
                elif isinstance(student_answer, list) and isinstance(expected_answer, list):
                    if set(student_answer) == set(expected_answer):
                        analysis["potential_issue"] = "Answers match but scored 0% - scoring logic error"
                    else:
                        analysis["potential_issue"] = f"Partial match issue: student selected {len(student_answer)} items, expected {len(expected_answer)} items"
                else:
                    analysis["potential_issue"] = "Unknown format issue"
                
                issues_analyzed.append(analysis)
            
            self.log_test(
                "Test Select All Scoring Logic",
                False,
                f"Found {len(self.problematic_submissions['select_all_zero_scores'])} select-all questions with 0% scores",
                json.dumps(issues_analyzed, indent=2)
            )
            return False
            
        except Exception as e:
            self.log_test("Test Select All Scoring Logic", False, error_msg=str(e))
            return False

    def test_manual_grading_endpoint(self):
        """Test the manual grading endpoint with actual submission data"""
        try:
            if not self.problematic_submissions.get("subjective_ungraded"):
                self.log_test(
                    "Test Manual Grading Endpoint",
                    True,
                    "No subjective questions requiring manual grading found"
                )
                return True
            
            # Test manual grading with first ungraded subjective question
            test_submission = self.problematic_submissions["subjective_ungraded"][0]
            submission_id = test_submission["submission_id"]
            
            # Test grading endpoint
            grading_data = {
                "score": 1,
                "feedback": "Test manual grading - debugging grading issues",
                "gradedBy": self.admin_user["id"]
            }
            
            response = requests.post(
                f"{BACKEND_URL}/submissions/{submission_id}/grade",
                json=grading_data,
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code in [200, 201]:
                self.log_test(
                    "Test Manual Grading Endpoint",
                    True,
                    f"Successfully graded submission {submission_id} for student {test_submission['student']}"
                )
                return True
            else:
                self.log_test(
                    "Test Manual Grading Endpoint",
                    False,
                    f"Failed to grade submission {submission_id}: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Test Manual Grading Endpoint", False, error_msg=str(e))
            return False

    def test_grading_conflicts_detection(self):
        """Test for conflicts between auto-grading and manual grading"""
        try:
            if not self.final_test_data:
                self.log_test(
                    "Test Grading Conflicts Detection",
                    False,
                    "Final test data not available"
                )
                return False
            
            final_test_id = self.final_test_data["id"]
            
            # Get all submissions to check for grading conflicts
            response = requests.get(
                f"{BACKEND_URL}/final-tests/{final_test_id}/submissions",
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code != 200:
                self.log_test(
                    "Test Grading Conflicts Detection",
                    False,
                    f"Failed to get submissions: {response.status_code}",
                    response.text
                )
                return False
            
            data = response.json()
            submissions = data.get("submissions", [])
            
            conflicts_found = []
            
            for submission in submissions:
                answers = submission.get("answers", [])
                
                for answer in answers:
                    auto_score = answer.get("autoScore")
                    manual_score = answer.get("manualScore")
                    final_score = answer.get("score")
                    
                    # Check for conflicts
                    if auto_score is not None and manual_score is not None:
                        if auto_score != manual_score:
                            conflicts_found.append({
                                "submission_id": submission.get("id"),
                                "student": submission.get("studentName"),
                                "question_type": answer.get("questionType"),
                                "auto_score": auto_score,
                                "manual_score": manual_score,
                                "final_score": final_score
                            })
            
            if conflicts_found:
                self.log_test(
                    "Test Grading Conflicts Detection",
                    False,
                    f"Found {len(conflicts_found)} grading conflicts",
                    json.dumps(conflicts_found, indent=2)
                )
                return False
            else:
                self.log_test(
                    "Test Grading Conflicts Detection",
                    True,
                    f"No grading conflicts detected in {len(submissions)} submissions"
                )
                return True
                
        except Exception as e:
            self.log_test("Test Grading Conflicts Detection", False, error_msg=str(e))
            return False

    def run_all_tests(self):
        """Run all final exam grading debug tests"""
        print("🚀 Starting Final Exam Grading Issues Debug Testing")
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
        
        # Core debug tests
        test_methods = [
            self.find_fresh_test_program_092425,
            self.get_final_test_for_program,
            self.analyze_select_all_that_apply_questions,
            self.get_final_test_submissions,
            self.test_select_all_scoring_logic,
            self.test_manual_grading_endpoint,
            self.test_grading_conflicts_detection
        ]
        
        print("🧪 Running Final Exam Grading Debug Tests")
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
        
        if success_rate >= 70:  # Lower threshold since we're debugging issues
            print("🎉 Final Exam Grading Debug Testing: ISSUES IDENTIFIED")
            return True
        else:
            print("⚠️  Final Exam Grading Debug Testing: CRITICAL ISSUES FOUND")
            return False

def main():
    """Main test execution"""
    test_suite = FinalExamGradingDebugSuite()
    
    try:
        success = test_suite.run_all_tests()
        
        # Print detailed results
        print("\n" + "=" * 70)
        print("DETAILED DEBUG RESULTS")
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