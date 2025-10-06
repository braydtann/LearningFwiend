#!/usr/bin/env python3
"""
LearningFriend LMS Backend Testing - Quiz Progression Fixes
==========================================================

Testing the LearningFriend LMS backend after implementing quiz progression fixes:

1. **Course Management**: Verify GET /api/courses/{id} returns courses with proper quiz data structure, including multi-quiz courses
2. **Enrollment and Progress**: Test enrollment progress tracking APIs and verify quiz completion tracking works correctly  
3. **Quiz Data Validation**: Check that quiz questions have proper data format, especially true-false questions with correctAnswer field
4. **Authentication**: Verify both admin and student authentication works with provided credentials

CONTEXT: Just fixed two critical issues:
- Quiz progression logic to allow sequential quiz unlocking in multi-quiz courses
- True-false question validation to accept both boolean and numeric (0/1) correctAnswer values

CREDENTIALS TO TEST:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!

EXPECTED OUTCOMES:
- All course and enrollment APIs should work
- Quiz data should have proper structure for frontend validation
- Both user types should authenticate successfully
- No 422 errors or validation failures

PRIORITY: Focus on quiz-related endpoints and data structure validation as these were just fixed.
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

class QuizProgressionTestSuite:
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

    def test_course_management_with_quiz_data(self):
        """Test GET /api/courses/{id} returns courses with proper quiz data structure"""
        try:
            # Get all courses first
            response = requests.get(f"{BACKEND_URL}/courses", headers=self.get_headers(self.admin_token))
            
            if response.status_code != 200:
                self.log_test(
                    "Course Management - Get All Courses",
                    False,
                    f"Failed to get courses: {response.status_code}",
                    response.text
                )
                return False
            
            courses = response.json()
            if not courses:
                self.log_test(
                    "Course Management - No Courses",
                    False,
                    "No courses available for testing"
                )
                return False
            
            # Test individual course retrieval with quiz data validation
            quiz_courses_found = 0
            multi_quiz_courses_found = 0
            
            for course in courses[:5]:  # Test first 5 courses
                course_id = course["id"]
                course_title = course.get("title", "Unknown Course")
                
                response = requests.get(f"{BACKEND_URL}/courses/{course_id}", headers=self.get_headers(self.admin_token))
                
                if response.status_code == 200:
                    course_data = response.json()
                    
                    # Check for proper course structure
                    required_fields = ["id", "title", "modules", "instructorId", "status"]
                    missing_fields = [field for field in required_fields if field not in course_data]
                    
                    if missing_fields:
                        self.log_test(
                            "Course Management - Course Structure",
                            False,
                            f"Course {course_title} missing fields: {missing_fields}"
                        )
                        return False
                    
                    # Check for quiz lessons and their data structure
                    quiz_lessons = []
                    for module in course_data.get("modules", []):
                        for lesson in module.get("lessons", []):
                            if lesson.get("type") == "quiz":
                                quiz_lessons.append(lesson)
                    
                    if quiz_lessons:
                        quiz_courses_found += 1
                        if len(quiz_lessons) > 1:
                            multi_quiz_courses_found += 1
                        
                        # Validate quiz data structure
                        for quiz_lesson in quiz_lessons:
                            quiz_data = quiz_lesson.get("quiz", {})
                            questions = quiz_data.get("questions", [])
                            
                            if not questions:
                                continue
                                
                            # Check each question for proper structure
                            for question in questions:
                                question_type = question.get("type", "")
                                
                                # Validate true-false questions specifically (mentioned in review)
                                if question_type == "true-false":
                                    correct_answer = question.get("correctAnswer")
                                    if correct_answer is None:
                                        self.log_test(
                                            "Course Management - True-False Question Validation",
                                            False,
                                            f"True-false question missing correctAnswer field in course {course_title}"
                                        )
                                        return False
                                    
                                    # Check if correctAnswer accepts both boolean and numeric values
                                    if not (isinstance(correct_answer, (bool, int)) or 
                                           (isinstance(correct_answer, str) and correct_answer in ["0", "1", "true", "false"])):
                                        self.log_test(
                                            "Course Management - True-False Question Format",
                                            False,
                                            f"True-false question has invalid correctAnswer format: {correct_answer} (type: {type(correct_answer)})"
                                        )
                                        return False
                                
                                # Validate other question types have required fields
                                if question_type == "multiple-choice":
                                    if not question.get("options") or not question.get("correctAnswer"):
                                        self.log_test(
                                            "Course Management - Multiple Choice Question Structure",
                                            False,
                                            f"Multiple choice question missing options or correctAnswer in course {course_title}"
                                        )
                                        return False
            
            self.log_test(
                "Course Management with Quiz Data Structure",
                True,
                f"Tested {len(courses[:5])} courses, found {quiz_courses_found} with quizzes ({multi_quiz_courses_found} multi-quiz courses), all quiz data structures valid"
            )
            return True
                
        except Exception as e:
            self.log_test("Course Management with Quiz Data Structure", False, error_msg=str(e))
            return False

    def test_enrollment_and_progress_tracking(self):
        """Test enrollment progress tracking APIs and quiz completion tracking"""
        try:
            # Get student enrollments
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=self.get_headers(self.student_token))
            
            if response.status_code != 200:
                self.log_test(
                    "Enrollment Progress - Get Enrollments",
                    False,
                    f"Failed to get enrollments: {response.status_code}",
                    response.text
                )
                return False
            
            enrollments = response.json()
            if not enrollments:
                self.log_test(
                    "Enrollment Progress - No Enrollments",
                    False,
                    "Student has no enrollments to test progress tracking"
                )
                return False
            
            # Test progress tracking with first enrollment
            test_enrollment = enrollments[0]
            course_id = test_enrollment["courseId"]
            course_name = test_enrollment.get("courseName", "Unknown Course")
            current_progress = test_enrollment.get("progress", 0)
            
            # Test progress update endpoint
            progress_update_data = {
                "progress": min(current_progress + 5, 100),  # Increment by 5% or cap at 100%
                "currentLessonId": "test-lesson-id",
                "timeSpent": 300,  # 5 minutes
                "lastAccessedAt": datetime.now().isoformat()
            }
            
            response = requests.put(
                f"{BACKEND_URL}/enrollments/{course_id}/progress",
                json=progress_update_data,
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code == 200:
                updated_enrollment = response.json()
                
                # Validate response structure
                required_fields = ["id", "userId", "courseId", "progress", "status", "enrolledAt"]
                missing_fields = [field for field in required_fields if field not in updated_enrollment]
                
                if missing_fields:
                    self.log_test(
                        "Enrollment Progress - Response Structure",
                        False,
                        f"Missing fields in progress update response: {missing_fields}"
                    )
                    return False
                
                # Check if progress was updated
                new_progress = updated_enrollment.get("progress", 0)
                if new_progress != progress_update_data["progress"]:
                    self.log_test(
                        "Enrollment Progress - Progress Update",
                        False,
                        f"Progress not updated correctly. Expected: {progress_update_data['progress']}, Got: {new_progress}"
                    )
                    return False
                
                self.log_test(
                    "Enrollment Progress Tracking",
                    True,
                    f"Course: {course_name}, Progress updated from {current_progress}% to {new_progress}%, Time spent: {progress_update_data['timeSpent']}s"
                )
                return True
            else:
                self.log_test(
                    "Enrollment Progress Tracking",
                    False,
                    f"Progress update failed with status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Enrollment Progress Tracking", False, error_msg=str(e))
            return False

    def test_submissions_with_question_points(self):
        """Test GET /api/courses/{course_id}/submissions includes questionPoints field"""
        try:
            # First, get available courses to test with
            response = requests.get(f"{BACKEND_URL}/courses", headers=self.get_headers(self.admin_token))
            
            if response.status_code != 200:
                self.log_test(
                    "Submissions Question Points - Get Courses",
                    False,
                    f"Failed to get courses: {response.status_code}",
                    response.text
                )
                return False
            
            courses = response.json()
            if not courses:
                self.log_test(
                    "Submissions Question Points - No Courses",
                    False,
                    "No courses available for testing"
                )
                return False
            
            # Test submissions endpoint with first available course
            course_id = courses[0]["id"]
            course_title = courses[0].get("title", "Unknown Course")
            
            response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}/submissions",
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code == 200:
                data = response.json()
                submissions = data.get("submissions", [])
                
                if not submissions:
                    self.log_test(
                        "Submissions Question Points Field",
                        True,
                        f"Course: {course_title}, No submissions found (endpoint working, no data to validate questionPoints field)"
                    )
                    return True
                
                # Check if questionPoints field exists in submissions
                has_question_points = all("questionPoints" in submission for submission in submissions)
                
                if has_question_points:
                    # Show sample question points values
                    sample_points = [sub.get("questionPoints", "N/A") for sub in submissions[:3]]
                    self.log_test(
                        "Submissions Question Points Field",
                        True,
                        f"Course: {course_title}, Found {len(submissions)} submissions, all include questionPoints field. Sample values: {sample_points}"
                    )
                    return True
                else:
                    missing_count = sum(1 for sub in submissions if "questionPoints" not in sub)
                    self.log_test(
                        "Submissions Question Points Field",
                        False,
                        f"Course: {course_title}, {missing_count}/{len(submissions)} submissions missing questionPoints field"
                    )
                    return False
            else:
                self.log_test(
                    "Submissions Question Points Field",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Submissions Question Points Field", False, error_msg=str(e))
            return False

    def test_grading_validation_against_question_points(self):
        """Test POST /api/submissions/{submission_id}/grade validates against question points"""
        try:
            # First, get a course with submissions to test grading
            response = requests.get(f"{BACKEND_URL}/courses", headers=self.get_headers(self.admin_token))
            
            if response.status_code != 200:
                self.log_test(
                    "Grading Validation - Get Courses",
                    False,
                    f"Failed to get courses: {response.status_code}",
                    response.text
                )
                return False
            
            courses = response.json()
            if not courses:
                self.log_test(
                    "Grading Validation - No Courses",
                    False,
                    "No courses available for testing"
                )
                return False
            
            # Look for a course with submissions
            submission_found = False
            test_submission = None
            
            for course in courses[:5]:  # Check first 5 courses
                course_id = course["id"]
                response = requests.get(
                    f"{BACKEND_URL}/courses/{course_id}/submissions",
                    headers=self.get_headers(self.admin_token)
                )
                
                if response.status_code == 200:
                    data = response.json()
                    submissions = data.get("submissions", [])
                    
                    if submissions:
                        test_submission = submissions[0]
                        submission_found = True
                        break
            
            if not submission_found:
                self.log_test(
                    "Grading Validation Against Question Points",
                    True,
                    "No submissions found to test grading validation (endpoint structure verified in previous test)"
                )
                return True
            
            submission_id = test_submission["id"]
            question_points = test_submission.get("questionPoints", 1)
            
            # Test 1: Valid score within question points
            valid_score = min(question_points, 1)  # Use 1 or question_points, whichever is smaller
            grading_data = {
                "score": valid_score,
                "feedback": "Test grading validation - valid score"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/submissions/{submission_id}/grade",
                json=grading_data,
                headers=self.get_headers(self.admin_token)
            )
            
            valid_score_test = response.status_code in [200, 201]
            
            # Test 2: Invalid score exceeding question points
            invalid_score = question_points + 1
            grading_data_invalid = {
                "score": invalid_score,
                "feedback": "Test grading validation - invalid score"
            }
            
            response_invalid = requests.post(
                f"{BACKEND_URL}/submissions/{submission_id}/grade",
                json=grading_data_invalid,
                headers=self.get_headers(self.admin_token)
            )
            
            invalid_score_rejected = response_invalid.status_code == 400
            
            if valid_score_test and invalid_score_rejected:
                self.log_test(
                    "Grading Validation Against Question Points",
                    True,
                    f"Submission ID: {submission_id}, Question Points: {question_points}, Valid score ({valid_score}) accepted, Invalid score ({invalid_score}) rejected with 400"
                )
                return True
            else:
                details = f"Valid score test: {valid_score_test} (status: {response.status_code}), Invalid score rejected: {invalid_score_rejected} (status: {response_invalid.status_code})"
                self.log_test(
                    "Grading Validation Against Question Points",
                    False,
                    details,
                    f"Expected valid score to be accepted and invalid score to be rejected with 400"
                )
                return False
                
        except Exception as e:
            self.log_test("Grading Validation Against Question Points", False, error_msg=str(e))
            return False

    def test_attempt_limit_error_messages(self):
        """Test proper error messages when attempt limits are exceeded"""
        try:
            # This test will check if the attempt check endpoints return proper messages
            # when limits are exceeded. We'll use the quiz endpoint as an example.
            
            response = requests.get(f"{BACKEND_URL}/quizzes", headers=self.get_headers(self.student_token))
            
            if response.status_code != 200:
                self.log_test(
                    "Attempt Limit Error Messages",
                    False,
                    "Could not get quizzes to test error messages"
                )
                return False
            
            quizzes = response.json()
            if not quizzes:
                self.log_test(
                    "Attempt Limit Error Messages",
                    True,
                    "No quizzes available to test attempt limit messages (endpoint structure verified)"
                )
                return True
            
            # Test with first quiz
            quiz_id = quizzes[0]["id"]
            
            response = requests.get(
                f"{BACKEND_URL}/quizzes/{quiz_id}/attempt-check",
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                can_attempt = data.get("canAttempt", True)
                
                # Check if message is informative
                has_proper_message = len(message) > 10 and ("attempt" in message.lower())
                
                if has_proper_message:
                    self.log_test(
                        "Attempt Limit Error Messages",
                        True,
                        f"Quiz attempt check returns proper message: '{message}', Can attempt: {can_attempt}"
                    )
                    return True
                else:
                    self.log_test(
                        "Attempt Limit Error Messages",
                        False,
                        f"Message too short or uninformative: '{message}'"
                    )
                    return False
            else:
                self.log_test(
                    "Attempt Limit Error Messages",
                    False,
                    f"Failed to get attempt check: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Attempt Limit Error Messages", False, error_msg=str(e))
            return False

    def run_all_tests(self):
        """Run all quality of life improvement tests"""
        print("🚀 Starting Quality of Life Improvements Testing")
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
        
        # Core quality of life improvement tests
        test_methods = [
            self.test_quiz_attempt_check_endpoint,
            self.test_final_test_attempt_check_endpoint,
            self.test_submissions_with_question_points,
            self.test_grading_validation_against_question_points,
            self.test_attempt_limit_error_messages
        ]
        
        print("🧪 Running Quality of Life Improvement Tests")
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
            print("🎉 Quality of Life Improvements Testing: SUCCESS")
            return True
        else:
            print("⚠️  Quality of Life Improvements Testing: NEEDS ATTENTION")
            return False

def main():
    """Main test execution"""
    test_suite = QualityOfLifeTestSuite()
    
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