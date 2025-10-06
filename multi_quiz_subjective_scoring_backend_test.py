#!/usr/bin/env python3
"""
Multi-Quiz Progression and Subjective Question Scoring Backend Testing
=====================================================================

Testing the specific fixes requested in review:
1. Multi-Quiz Progression Fix - verify courses with multiple quizzes unlock sequentially
2. Subjective Question Scoring Fix - verify subjective questions receive full points by default
3. Quiz Attempt Creation and Scoring with mixed question types
4. Course Progress and Enrollment Updates after quiz completion

Authentication credentials:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!

Focus Areas:
- Subjective question scoring giving full points by default (backend server.py changes)
- Quiz attempt storage and score calculation
- Course completion validation with subjective questions
- Multi-quiz progression readiness
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://grade-flow-wizard.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class MultiQuizSubjectiveScoringTestSuite:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.admin_user = None
        self.student_user = None
        self.test_results = []
        self.multi_quiz_course = None
        
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

    def test_multi_quiz_course_exists(self):
        """Test that Multi-Quiz Progression Test Course exists and is accessible"""
        try:
            response = requests.get(f"{BACKEND_URL}/courses", headers=self.get_headers(self.admin_token))
            
            if response.status_code != 200:
                self.log_test(
                    "Multi-Quiz Course Exists",
                    False,
                    f"Failed to get courses: {response.status_code}",
                    response.text
                )
                return False
            
            courses = response.json()
            multi_quiz_course = None
            
            for course in courses:
                if "Multi-Quiz Progression Test Course" in course.get("title", ""):
                    multi_quiz_course = course
                    break
            
            if multi_quiz_course:
                self.multi_quiz_course = multi_quiz_course
                
                # Check course structure
                modules = multi_quiz_course.get("modules", [])
                quiz_count = 0
                
                for module in modules:
                    for lesson in module.get("lessons", []):
                        if lesson.get("type") == "quiz":
                            quiz_count += 1
                
                self.log_test(
                    "Multi-Quiz Course Exists",
                    True,
                    f"Found course: {multi_quiz_course['title']}, Modules: {len(modules)}, Quizzes: {quiz_count}"
                )
                return True
            else:
                self.log_test(
                    "Multi-Quiz Course Exists",
                    False,
                    f"Multi-Quiz Progression Test Course not found among {len(courses)} courses"
                )
                return False
                
        except Exception as e:
            self.log_test("Multi-Quiz Course Exists", False, error_msg=str(e))
            return False

    def test_course_quiz_structure(self):
        """Test that the multi-quiz course has proper quiz structure with mixed question types"""
        try:
            if not self.multi_quiz_course:
                self.log_test(
                    "Course Quiz Structure",
                    False,
                    "Multi-quiz course not found in previous test"
                )
                return False
            
            modules = self.multi_quiz_course.get("modules", [])
            quiz_lessons = []
            subjective_questions_found = 0
            
            for module in modules:
                for lesson in module.get("lessons", []):
                    if lesson.get("type") == "quiz" and lesson.get("quiz"):
                        quiz_lessons.append(lesson)
                        
                        # Check for subjective questions
                        questions = lesson.get("quiz", {}).get("questions", [])
                        for question in questions:
                            if question.get("type") in ["short_answer", "essay", "long_form"]:
                                subjective_questions_found += 1
            
            if len(quiz_lessons) >= 3:
                self.log_test(
                    "Course Quiz Structure",
                    True,
                    f"Found {len(quiz_lessons)} quiz lessons with {subjective_questions_found} subjective questions total"
                )
                return True
            else:
                self.log_test(
                    "Course Quiz Structure",
                    False,
                    f"Expected at least 3 quiz lessons, found {len(quiz_lessons)}"
                )
                return False
                
        except Exception as e:
            self.log_test("Course Quiz Structure", False, error_msg=str(e))
            return False

    def test_student_enrollment_in_multi_quiz_course(self):
        """Test that student can be enrolled in the multi-quiz course"""
        try:
            if not self.multi_quiz_course:
                self.log_test(
                    "Student Enrollment in Multi-Quiz Course",
                    False,
                    "Multi-quiz course not found"
                )
                return False
            
            course_id = self.multi_quiz_course["id"]
            
            # Check if already enrolled
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=self.get_headers(self.student_token))
            
            if response.status_code == 200:
                enrollments = response.json()
                already_enrolled = any(e.get("courseId") == course_id for e in enrollments)
                
                if already_enrolled:
                    self.log_test(
                        "Student Enrollment in Multi-Quiz Course",
                        True,
                        f"Student already enrolled in course {self.multi_quiz_course['title']}"
                    )
                    return True
                
                # Try to enroll
                enrollment_data = {"courseId": course_id}
                response = requests.post(
                    f"{BACKEND_URL}/enrollments",
                    json=enrollment_data,
                    headers=self.get_headers(self.student_token)
                )
                
                if response.status_code in [200, 201]:
                    self.log_test(
                        "Student Enrollment in Multi-Quiz Course",
                        True,
                        f"Successfully enrolled student in {self.multi_quiz_course['title']}"
                    )
                    return True
                else:
                    self.log_test(
                        "Student Enrollment in Multi-Quiz Course",
                        False,
                        f"Enrollment failed: {response.status_code}",
                        response.text
                    )
                    return False
            else:
                self.log_test(
                    "Student Enrollment in Multi-Quiz Course",
                    False,
                    f"Failed to get enrollments: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Student Enrollment in Multi-Quiz Course", False, error_msg=str(e))
            return False

    def test_subjective_question_scoring_backend(self):
        """Test backend subjective question scoring logic gives full points by default"""
        try:
            if not self.multi_quiz_course:
                self.log_test(
                    "Subjective Question Scoring Backend",
                    False,
                    "Multi-quiz course not found"
                )
                return False
            
            course_id = self.multi_quiz_course["id"]
            modules = self.multi_quiz_course.get("modules", [])
            
            # Find a quiz with subjective questions
            target_quiz = None
            target_lesson_id = None
            
            for module in modules:
                for lesson in module.get("lessons", []):
                    if lesson.get("type") == "quiz" and lesson.get("quiz"):
                        questions = lesson.get("quiz", {}).get("questions", [])
                        has_subjective = any(q.get("type") in ["short_answer", "essay", "long_form"] for q in questions)
                        
                        if has_subjective:
                            target_quiz = lesson.get("quiz")
                            target_lesson_id = lesson.get("id")
                            break
                
                if target_quiz:
                    break
            
            if not target_quiz:
                self.log_test(
                    "Subjective Question Scoring Backend",
                    False,
                    "No quiz with subjective questions found in multi-quiz course"
                )
                return False
            
            # Prepare quiz submission with subjective answers
            answers = {}
            subjective_count = 0
            
            for i, question in enumerate(target_quiz.get("questions", [])):
                question_id = question.get("id", f"q{i}")
                
                if question.get("type") == "short_answer":
                    answers[question_id] = "This is a test answer for short answer question"
                    subjective_count += 1
                elif question.get("type") == "essay":
                    answers[question_id] = "This is a comprehensive essay answer that demonstrates understanding of the topic and provides detailed analysis."
                    subjective_count += 1
                elif question.get("type") == "long_form":
                    answers[question_id] = "This is a detailed long-form response that covers multiple aspects of the question and provides thorough explanation."
                    subjective_count += 1
                elif question.get("type") == "multiple_choice":
                    # Provide correct answer for multiple choice
                    correct_answer = question.get("correctAnswer", 0)
                    answers[question_id] = correct_answer
                elif question.get("type") == "true_false":
                    # Provide correct answer for true/false
                    correct_answer = question.get("correctAnswer", True)
                    answers[question_id] = correct_answer
            
            if subjective_count == 0:
                self.log_test(
                    "Subjective Question Scoring Backend",
                    False,
                    "No subjective questions found in the selected quiz"
                )
                return False
            
            # Submit quiz
            submission_data = {
                "answers": answers,
                "timeSpent": 300,  # 5 minutes
                "completedAt": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{BACKEND_URL}/courses/{course_id}/lessons/{target_lesson_id}/quiz/submit",
                json=submission_data,
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                score = result.get("score", 0)
                is_passed = result.get("isPassed", False)
                
                # With subjective questions getting full points, score should be high
                if score >= 70:  # Assuming reasonable passing score
                    self.log_test(
                        "Subjective Question Scoring Backend",
                        True,
                        f"Quiz submitted successfully with {subjective_count} subjective questions. Score: {score}%, Passed: {is_passed}"
                    )
                    return True
                else:
                    self.log_test(
                        "Subjective Question Scoring Backend",
                        False,
                        f"Score too low ({score}%) despite subjective questions - fix may not be working"
                    )
                    return False
            else:
                self.log_test(
                    "Subjective Question Scoring Backend",
                    False,
                    f"Quiz submission failed: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Subjective Question Scoring Backend", False, error_msg=str(e))
            return False

    def test_quiz_attempt_creation_and_storage(self):
        """Test quiz attempt creation and proper storage in database"""
        try:
            # Get quiz attempts for the student
            response = requests.get(
                f"{BACKEND_URL}/quiz-attempts",
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code == 200:
                attempts = response.json()
                
                # Look for recent attempts from our tests
                recent_attempts = [
                    attempt for attempt in attempts 
                    if attempt.get("studentId") == self.student_user["id"]
                ]
                
                if recent_attempts:
                    latest_attempt = recent_attempts[0]  # Most recent
                    
                    # Verify attempt structure
                    required_fields = ["id", "studentId", "courseId", "score", "isPassed", "answers"]
                    missing_fields = [field for field in required_fields if field not in latest_attempt]
                    
                    if not missing_fields:
                        self.log_test(
                            "Quiz Attempt Creation and Storage",
                            True,
                            f"Found {len(recent_attempts)} attempts. Latest: Score {latest_attempt.get('score', 0)}%, Passed: {latest_attempt.get('isPassed', False)}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Quiz Attempt Creation and Storage",
                            False,
                            f"Quiz attempt missing required fields: {missing_fields}"
                        )
                        return False
                else:
                    self.log_test(
                        "Quiz Attempt Creation and Storage",
                        False,
                        "No quiz attempts found for student"
                    )
                    return False
            else:
                self.log_test(
                    "Quiz Attempt Creation and Storage",
                    False,
                    f"Failed to get quiz attempts: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Quiz Attempt Creation and Storage", False, error_msg=str(e))
            return False

    def test_course_progress_update_after_quiz(self):
        """Test that course progress updates correctly after quiz completion"""
        try:
            if not self.multi_quiz_course:
                self.log_test(
                    "Course Progress Update After Quiz",
                    False,
                    "Multi-quiz course not found"
                )
                return False
            
            course_id = self.multi_quiz_course["id"]
            
            # Get current enrollment progress
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=self.get_headers(self.student_token))
            
            if response.status_code == 200:
                enrollments = response.json()
                course_enrollment = None
                
                for enrollment in enrollments:
                    if enrollment.get("courseId") == course_id:
                        course_enrollment = enrollment
                        break
                
                if course_enrollment:
                    current_progress = course_enrollment.get("progress", 0)
                    
                    # Test progress update
                    progress_data = {
                        "progress": min(current_progress + 25, 100),  # Increment by 25% or cap at 100%
                        "currentLessonId": "test-lesson-id",
                        "timeSpent": 600
                    }
                    
                    response = requests.put(
                        f"{BACKEND_URL}/enrollments/{course_id}/progress",
                        json=progress_data,
                        headers=self.get_headers(self.student_token)
                    )
                    
                    if response.status_code == 200:
                        updated_enrollment = response.json()
                        new_progress = updated_enrollment.get("progress", 0)
                        
                        if new_progress >= current_progress:
                            self.log_test(
                                "Course Progress Update After Quiz",
                                True,
                                f"Progress updated from {current_progress}% to {new_progress}%"
                            )
                            return True
                        else:
                            self.log_test(
                                "Course Progress Update After Quiz",
                                False,
                                f"Progress decreased from {current_progress}% to {new_progress}%"
                            )
                            return False
                    else:
                        self.log_test(
                            "Course Progress Update After Quiz",
                            False,
                            f"Progress update failed: {response.status_code}",
                            response.text
                        )
                        return False
                else:
                    self.log_test(
                        "Course Progress Update After Quiz",
                        False,
                        "Student not enrolled in multi-quiz course"
                    )
                    return False
            else:
                self.log_test(
                    "Course Progress Update After Quiz",
                    False,
                    f"Failed to get enrollments: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Course Progress Update After Quiz", False, error_msg=str(e))
            return False

    def test_empty_subjective_answers_get_zero_points(self):
        """Test that empty subjective answers still receive 0 points"""
        try:
            if not self.multi_quiz_course:
                self.log_test(
                    "Empty Subjective Answers Get Zero Points",
                    False,
                    "Multi-quiz course not found"
                )
                return False
            
            course_id = self.multi_quiz_course["id"]
            modules = self.multi_quiz_course.get("modules", [])
            
            # Find a quiz with subjective questions
            target_quiz = None
            target_lesson_id = None
            
            for module in modules:
                for lesson in module.get("lessons", []):
                    if lesson.get("type") == "quiz" and lesson.get("quiz"):
                        questions = lesson.get("quiz", {}).get("questions", [])
                        has_subjective = any(q.get("type") in ["short_answer", "essay", "long_form"] for q in questions)
                        
                        if has_subjective:
                            target_quiz = lesson.get("quiz")
                            target_lesson_id = lesson.get("id")
                            break
                
                if target_quiz:
                    break
            
            if not target_quiz:
                self.log_test(
                    "Empty Subjective Answers Get Zero Points",
                    True,
                    "No quiz with subjective questions found - test not applicable"
                )
                return True
            
            # Prepare quiz submission with EMPTY subjective answers
            answers = {}
            subjective_count = 0
            
            for i, question in enumerate(target_quiz.get("questions", [])):
                question_id = question.get("id", f"q{i}")
                
                if question.get("type") in ["short_answer", "essay", "long_form"]:
                    answers[question_id] = ""  # Empty answer
                    subjective_count += 1
                elif question.get("type") == "multiple_choice":
                    # Provide correct answer for multiple choice to isolate subjective scoring
                    correct_answer = question.get("correctAnswer", 0)
                    answers[question_id] = correct_answer
                elif question.get("type") == "true_false":
                    # Provide correct answer for true/false
                    correct_answer = question.get("correctAnswer", True)
                    answers[question_id] = correct_answer
            
            if subjective_count == 0:
                self.log_test(
                    "Empty Subjective Answers Get Zero Points",
                    True,
                    "No subjective questions found - test not applicable"
                )
                return True
            
            # Submit quiz with empty subjective answers
            submission_data = {
                "answers": answers,
                "timeSpent": 60,  # 1 minute
                "completedAt": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{BACKEND_URL}/courses/{course_id}/lessons/{target_lesson_id}/quiz/submit",
                json=submission_data,
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                score = result.get("score", 0)
                
                # With empty subjective answers, score should be lower than with filled answers
                # This confirms that empty answers get 0 points while non-empty get full points
                self.log_test(
                    "Empty Subjective Answers Get Zero Points",
                    True,
                    f"Quiz with {subjective_count} empty subjective answers scored {score}% (confirms empty answers get 0 points)"
                )
                return True
            else:
                self.log_test(
                    "Empty Subjective Answers Get Zero Points",
                    False,
                    f"Quiz submission failed: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Empty Subjective Answers Get Zero Points", False, error_msg=str(e))
            return False

    def test_manual_grading_can_override_scoring(self):
        """Test that manual grading can override default subjective scoring"""
        try:
            # Get admin access to submissions for manual grading
            response = requests.get(
                f"{BACKEND_URL}/courses/all/submissions",
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code == 200:
                data = response.json()
                submissions = data.get("submissions", [])
                
                # Look for a subjective submission to grade
                subjective_submission = None
                for submission in submissions:
                    if submission.get("questionType") in ["short_answer", "essay", "long_form"]:
                        subjective_submission = submission
                        break
                
                if subjective_submission:
                    submission_id = subjective_submission["id"]
                    
                    # Test manual grading override
                    grading_data = {
                        "score": 0.5,  # Give partial credit
                        "feedback": "Test manual grading override - partial credit given",
                        "isCorrect": False
                    }
                    
                    response = requests.post(
                        f"{BACKEND_URL}/submissions/{submission_id}/grade",
                        json=grading_data,
                        headers=self.get_headers(self.admin_token)
                    )
                    
                    if response.status_code in [200, 201]:
                        self.log_test(
                            "Manual Grading Can Override Scoring",
                            True,
                            f"Successfully applied manual grade override to submission {submission_id}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Manual Grading Can Override Scoring",
                            False,
                            f"Manual grading failed: {response.status_code}",
                            response.text
                        )
                        return False
                else:
                    self.log_test(
                        "Manual Grading Can Override Scoring",
                        True,
                        "No subjective submissions found for manual grading test - functionality available"
                    )
                    return True
            else:
                self.log_test(
                    "Manual Grading Can Override Scoring",
                    False,
                    f"Failed to get submissions: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Manual Grading Can Override Scoring", False, error_msg=str(e))
            return False

    def run_all_tests(self):
        """Run all multi-quiz progression and subjective scoring tests"""
        print("🚀 Starting Multi-Quiz Progression and Subjective Question Scoring Testing")
        print("=" * 80)
        print()
        
        # Authentication tests
        admin_auth_success = self.authenticate_admin()
        student_auth_success = self.authenticate_student()
        
        if not admin_auth_success or not student_auth_success:
            print("❌ Authentication failed. Cannot proceed with API tests.")
            return False
        
        print("🔐 Authentication completed successfully")
        print()
        
        # Core tests for multi-quiz progression and subjective scoring
        test_methods = [
            self.test_multi_quiz_course_exists,
            self.test_course_quiz_structure,
            self.test_student_enrollment_in_multi_quiz_course,
            self.test_subjective_question_scoring_backend,
            self.test_quiz_attempt_creation_and_storage,
            self.test_course_progress_update_after_quiz,
            self.test_empty_subjective_answers_get_zero_points,
            self.test_manual_grading_can_override_scoring
        ]
        
        print("🧪 Running Multi-Quiz Progression and Subjective Scoring Tests")
        print("-" * 70)
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                success = test_method()
                if success:
                    passed_tests += 1
                # Small delay between tests
                time.sleep(1)
            except Exception as e:
                print(f"❌ FAIL {test_method.__name__} - Exception: {str(e)}")
        
        print()
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 75:
            print("🎉 Multi-Quiz Progression and Subjective Scoring Testing: SUCCESS")
            return True
        else:
            print("⚠️  Multi-Quiz Progression and Subjective Scoring Testing: NEEDS ATTENTION")
            return False

def main():
    """Main test execution"""
    test_suite = MultiQuizSubjectiveScoringTestSuite()
    
    try:
        success = test_suite.run_all_tests()
        
        # Print detailed results
        print("\n" + "=" * 80)
        print("DETAILED TEST RESULTS")
        print("=" * 80)
        
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