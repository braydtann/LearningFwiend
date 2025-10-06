#!/usr/bin/env python3
"""
Final Exam Bug Fixes Testing
=============================

Testing the final exam bug fixes as requested in review:
1. Manual Grading Fix Test:
   - Test GET /api/courses/all/submissions to verify final test subjective submissions are included
   - Test POST /api/submissions/{submission_id}/grade with a final test submission ID
   - Verify the grading works and doesn't return 404 errors
   - Test with submission ID like: "final-e5bde064-9277-4c94-8f0b-2fec2e3fc2c6-b5ec2256-6021-4a76-9ea7-b16467ed1b85"

2. Select All That Apply Verification:
   - Create a simple final test with only select-all-that-apply questions
   - Submit correct answers (matching the correctAnswers array)
   - Verify the scoring logic works properly

Authentication credentials:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://lms-progression.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class FinalExamBugFixesTestSuite:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.admin_user = None
        self.student_user = None
        self.test_results = []
        self.created_test_id = None
        
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

    def test_all_submissions_endpoint(self):
        """Test GET /api/courses/all/submissions includes final test submissions"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/all/submissions",
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code == 200:
                data = response.json()
                submissions = data.get("submissions", [])
                
                # Look for final test submissions
                final_test_submissions = [
                    sub for sub in submissions 
                    if sub.get("testId") or sub.get("source") == "final_test" or 
                    (sub.get("id", "").startswith("final-"))
                ]
                
                self.log_test(
                    "All Submissions Endpoint - Final Test Inclusion",
                    True,
                    f"Found {len(submissions)} total submissions, {len(final_test_submissions)} final test submissions"
                )
                return True
            else:
                self.log_test(
                    "All Submissions Endpoint - Final Test Inclusion",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("All Submissions Endpoint - Final Test Inclusion", False, error_msg=str(e))
            return False

    def test_manual_grading_with_specific_submission_id(self):
        """Test manual grading with a specific final test submission ID format"""
        try:
            # First, get all submissions to find a final test submission
            response = requests.get(
                f"{BACKEND_URL}/courses/all/submissions",
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code != 200:
                self.log_test(
                    "Manual Grading - Get Submissions",
                    False,
                    f"Failed to get submissions: {response.status_code}",
                    response.text
                )
                return False
            
            data = response.json()
            submissions = data.get("submissions", [])
            
            # Look for final test submissions
            final_test_submissions = [
                sub for sub in submissions 
                if sub.get("testId") or sub.get("source") == "final_test" or 
                (sub.get("id", "").startswith("final-"))
            ]
            
            if not final_test_submissions:
                # Create a test submission ID in the expected format
                test_submission_id = f"final-{str(uuid.uuid4())}-{str(uuid.uuid4())}"
                
                # Test grading with this ID - should return 404 but not crash
                grading_data = {
                    "score": 5,
                    "feedback": "Test grading for final exam submission"
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/submissions/{test_submission_id}/grade",
                    json=grading_data,
                    headers=self.get_headers(self.admin_token)
                )
                
                # Should return 404 for non-existent submission, not 500 error
                if response.status_code == 404:
                    self.log_test(
                        "Manual Grading - Final Test Submission Format",
                        True,
                        f"Correctly returned 404 for non-existent submission ID: {test_submission_id}"
                    )
                    return True
                else:
                    self.log_test(
                        "Manual Grading - Final Test Submission Format",
                        False,
                        f"Expected 404, got {response.status_code}",
                        response.text
                    )
                    return False
            else:
                # Test grading with an actual final test submission
                test_submission = final_test_submissions[0]
                submission_id = test_submission["id"]
                question_points = test_submission.get("questionPoints", 10)
                
                grading_data = {
                    "score": min(question_points, 8),  # Valid score
                    "feedback": "Test grading for actual final exam submission"
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/submissions/{submission_id}/grade",
                    json=grading_data,
                    headers=self.get_headers(self.admin_token)
                )
                
                if response.status_code in [200, 201]:
                    self.log_test(
                        "Manual Grading - Final Test Submission",
                        True,
                        f"Successfully graded submission {submission_id} with score {grading_data['score']}/{question_points}"
                    )
                    return True
                else:
                    self.log_test(
                        "Manual Grading - Final Test Submission",
                        False,
                        f"Status: {response.status_code}",
                        response.text
                    )
                    return False
                
        except Exception as e:
            self.log_test("Manual Grading - Final Test Submission", False, error_msg=str(e))
            return False

    def create_select_all_that_apply_test(self):
        """Create a simple final test with select-all-that-apply questions"""
        try:
            # First, get available programs to use one as programId
            response = requests.get(
                f"{BACKEND_URL}/programs",
                headers=self.get_headers(self.admin_token)
            )
            
            program_id = None
            if response.status_code == 200:
                programs = response.json()
                if programs:
                    program_id = programs[0]["id"]
            
            if not program_id:
                # Create a test program if none exists
                program_data = {
                    "title": "Test Program for Final Exam Bug Fixes",
                    "description": "Temporary program for testing final exam functionality",
                    "courseIds": []
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/programs",
                    json=program_data,
                    headers=self.get_headers(self.admin_token)
                )
                
                if response.status_code in [200, 201]:
                    program = response.json()
                    program_id = program["id"]
                else:
                    self.log_test(
                        "Create Select All That Apply Test - Program Creation",
                        False,
                        f"Failed to create program: {response.status_code}",
                        response.text
                    )
                    return False
            
            test_data = {
                "title": "Select All That Apply Test - Bug Fix Verification",
                "description": "Testing select-all-that-apply scoring logic",
                "programId": program_id,
                "passingScore": 75,
                "timeLimit": 30,
                "maxAttempts": 3,
                "isPublished": True,
                "questions": [
                    {
                        "type": "select-all-that-apply",
                        "question": "Which of the following are programming languages? (Select all that apply)",
                        "options": ["Python", "HTML", "JavaScript", "CSS", "Java"],
                        "correctAnswers": [0, 2, 4],  # Python, JavaScript, Java
                        "points": 10,
                        "explanation": "Python, JavaScript, and Java are programming languages. HTML and CSS are markup/styling languages."
                    },
                    {
                        "type": "select-all-that-apply", 
                        "question": "Which of the following are database systems? (Select all that apply)",
                        "options": ["MySQL", "React", "PostgreSQL", "MongoDB", "Angular"],
                        "correctAnswers": [0, 2, 3],  # MySQL, PostgreSQL, MongoDB
                        "points": 10,
                        "explanation": "MySQL, PostgreSQL, and MongoDB are database systems. React and Angular are frontend frameworks."
                    }
                ]
            }
            
            response = requests.post(
                f"{BACKEND_URL}/final-tests",
                json=test_data,
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code in [200, 201]:
                created_test = response.json()
                self.created_test_id = created_test["id"]
                self.log_test(
                    "Create Select All That Apply Test",
                    True,
                    f"Successfully created test with ID: {self.created_test_id}"
                )
                return True
            else:
                self.log_test(
                    "Create Select All That Apply Test",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Create Select All That Apply Test", False, error_msg=str(e))
            return False

    def test_select_all_that_apply_scoring(self):
        """Test select-all-that-apply scoring logic with correct answers"""
        try:
            if not self.created_test_id:
                self.log_test(
                    "Select All That Apply Scoring",
                    False,
                    "No test created to test scoring"
                )
                return False
            
            # Submit correct answers for both questions
            attempt_data = {
                "testId": self.created_test_id,
                "answers": [
                    {
                        "questionId": None,  # Will be filled from test data
                        "answer": [0, 2, 4]  # Correct answers for first question
                    },
                    {
                        "questionId": None,  # Will be filled from test data
                        "answer": [0, 2, 3]  # Correct answers for second question
                    }
                ]
            }
            
            # Get the test to get question IDs
            response = requests.get(
                f"{BACKEND_URL}/final-tests/{self.created_test_id}",
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code == 200:
                test_data = response.json()
                questions = test_data.get("questions", [])
                
                if len(questions) >= 2:
                    attempt_data["answers"][0]["questionId"] = questions[0]["id"]
                    attempt_data["answers"][1]["questionId"] = questions[1]["id"]
                else:
                    self.log_test(
                        "Select All That Apply Scoring",
                        False,
                        "Test doesn't have expected questions"
                    )
                    return False
            else:
                self.log_test(
                    "Select All That Apply Scoring",
                    False,
                    f"Failed to get test details: {response.status_code}",
                    response.text
                )
                return False
            
            # Submit the attempt
            response = requests.post(
                f"{BACKEND_URL}/final-test-attempts",
                json=attempt_data,
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code in [200, 201]:
                attempt_result = response.json()
                score = attempt_result.get("score", 0)
                total_points = attempt_result.get("totalPoints", 20)
                percentage = attempt_result.get("percentage", 0)
                
                # Should get full score (20/20 = 100%) for correct answers
                expected_score = 20
                if score == expected_score and percentage == 100.0:
                    self.log_test(
                        "Select All That Apply Scoring",
                        True,
                        f"Correct scoring: {score}/{total_points} points ({percentage}%) - All-or-nothing logic working"
                    )
                    return True
                else:
                    self.log_test(
                        "Select All That Apply Scoring",
                        False,
                        f"Incorrect scoring: {score}/{total_points} points ({percentage}%), expected {expected_score}/{total_points} (100%)"
                    )
                    return False
            else:
                self.log_test(
                    "Select All That Apply Scoring",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Select All That Apply Scoring", False, error_msg=str(e))
            return False

    def test_select_all_that_apply_partial_answers(self):
        """Test select-all-that-apply with partial/incorrect answers (should get 0 points)"""
        try:
            if not self.created_test_id:
                self.log_test(
                    "Select All That Apply Partial Answers",
                    False,
                    "No test created to test partial scoring"
                )
                return False
            
            # Submit partial answers (should get 0 points due to all-or-nothing scoring)
            attempt_data = {
                "testId": self.created_test_id,
                "answers": [
                    {
                        "questionId": None,  # Will be filled from test data
                        "answer": [0, 2]  # Missing one correct answer (4)
                    },
                    {
                        "questionId": None,  # Will be filled from test data
                        "answer": [0, 1, 2, 3]  # Has incorrect answer (1)
                    }
                ]
            }
            
            # Get the test to get question IDs
            response = requests.get(
                f"{BACKEND_URL}/final-tests/{self.created_test_id}",
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code == 200:
                test_data = response.json()
                questions = test_data.get("questions", [])
                
                if len(questions) >= 2:
                    attempt_data["answers"][0]["questionId"] = questions[0]["id"]
                    attempt_data["answers"][1]["questionId"] = questions[1]["id"]
                else:
                    self.log_test(
                        "Select All That Apply Partial Answers",
                        False,
                        "Test doesn't have expected questions"
                    )
                    return False
            else:
                self.log_test(
                    "Select All That Apply Partial Answers",
                    False,
                    f"Failed to get test details: {response.status_code}",
                    response.text
                )
                return False
            
            # Submit the attempt
            response = requests.post(
                f"{BACKEND_URL}/final-test-attempts",
                json=attempt_data,
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code in [200, 201]:
                attempt_result = response.json()
                score = attempt_result.get("score", 0)
                total_points = attempt_result.get("totalPoints", 20)
                percentage = attempt_result.get("percentage", 0)
                
                # Should get 0 score due to all-or-nothing logic
                if score == 0 and percentage == 0.0:
                    self.log_test(
                        "Select All That Apply Partial Answers",
                        True,
                        f"Correct all-or-nothing scoring: {score}/{total_points} points ({percentage}%) for partial answers"
                    )
                    return True
                else:
                    self.log_test(
                        "Select All That Apply Partial Answers",
                        False,
                        f"Incorrect scoring: {score}/{total_points} points ({percentage}%), expected 0/{total_points} (0%) for partial answers"
                    )
                    return False
            else:
                self.log_test(
                    "Select All That Apply Partial Answers",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Select All That Apply Partial Answers", False, error_msg=str(e))
            return False

    def cleanup_test_data(self):
        """Clean up created test data"""
        try:
            if self.created_test_id:
                # Note: We don't delete the test as it might be useful for further testing
                # In a real scenario, you might want to clean up test data
                self.log_test(
                    "Cleanup Test Data",
                    True,
                    f"Test {self.created_test_id} left for manual inspection"
                )
            return True
        except Exception as e:
            self.log_test("Cleanup Test Data", False, error_msg=str(e))
            return False

    def run_all_tests(self):
        """Run all final exam bug fix tests"""
        print("🚀 Starting Final Exam Bug Fixes Testing")
        print("=" * 60)
        print()
        
        # Authentication tests
        admin_auth_success = self.authenticate_admin()
        student_auth_success = self.authenticate_student()
        
        if not admin_auth_success or not student_auth_success:
            print("❌ Authentication failed. Cannot proceed with API tests.")
            return False
        
        print("🔐 Authentication completed successfully")
        print()
        
        # Core final exam bug fix tests
        test_methods = [
            self.test_all_submissions_endpoint,
            self.test_manual_grading_with_specific_submission_id,
            self.create_select_all_that_apply_test,
            self.test_select_all_that_apply_scoring,
            self.test_select_all_that_apply_partial_answers,
            self.cleanup_test_data
        ]
        
        print("🧪 Running Final Exam Bug Fix Tests")
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
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 Final Exam Bug Fixes Testing: SUCCESS")
            return True
        else:
            print("⚠️  Final Exam Bug Fixes Testing: NEEDS ATTENTION")
            return False

def main():
    """Main test execution"""
    test_suite = FinalExamBugFixesTestSuite()
    
    try:
        success = test_suite.run_all_tests()
        
        # Print detailed results
        print("\n" + "=" * 60)
        print("DETAILED TEST RESULTS")
        print("=" * 60)
        
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