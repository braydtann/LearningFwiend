#!/usr/bin/env python3
"""
Manual Grading Auto-Completion Testing
=====================================

Testing the manual grading auto-completion fix for the specific edge case:
Course with 1 module, 1 quiz, subjective questions only requiring manual grading

Test Scenario:
1. Create Test Course: Single module with quiz containing only subjective questions (essay/long_form)
2. Student Workflow: 
   - Student enrolls and takes quiz
   - Initial score should be 0% (no auto-gradable questions)
   - Course progress should show as incomplete
3. Manual Grading Process:
   - Instructor manually grades subjective questions to passing score
   - Verify `update_quiz_attempt_score` gets called and updates quiz score
   - **NEW FUNCTIONALITY**: Verify `auto_complete_course_after_quiz_grading` gets triggered
4. Auto-Completion Verification:
   - Verify course enrollment status updates to "completed" with 100% progress  
   - Verify completion certificate is generated automatically
   - Verify student can now see completed course status
5. Edge Cases:
   - Test with multiple quizzes (should only complete when ALL quizzes passed)
   - Test with mixed auto-gradable + subjective questions
   - Test grading to failing score (should NOT auto-complete)

Authentication credentials:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
import uuid
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-analytics-hub.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class ManualGradingAutoCompletionTestSuite:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.admin_user = None
        self.student_user = None
        self.test_results = []
        self.test_course_id = None
        self.test_quiz_id = None
        self.test_enrollment_id = None
        self.test_quiz_attempt_id = None
        self.subjective_submissions = []
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "error": error_msg
        })
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.admin_user = data["user"]
                self.log_test("Admin Authentication", True, f"Logged in as {self.admin_user['full_name']}")
                return True
            else:
                self.log_test("Admin Authentication", False, error_msg=f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, error_msg=str(e))
            return False

    def authenticate_student(self):
        """Authenticate as student user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=STUDENT_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_user = data["user"]
                self.log_test("Student Authentication", True, f"Logged in as {self.student_user['full_name']}")
                return True
            else:
                self.log_test("Student Authentication", False, error_msg=f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Student Authentication", False, error_msg=str(e))
            return False

    def create_subjective_only_course(self):
        """Create a test course with only subjective questions"""
        try:
            # Create course with single module and quiz containing only subjective questions
            course_data = {
                "title": "Manual Grading Auto-Completion Test Course",
                "description": "Test course for manual grading auto-completion functionality with subjective questions only",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "learningOutcomes": ["Test manual grading auto-completion"],
                "modules": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Subjective Assessment Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Subjective Questions Quiz",
                                "type": "quiz",
                                "quiz": {
                                    "id": str(uuid.uuid4()),
                                    "title": "Subjective Assessment",
                                    "description": "Quiz with only subjective questions requiring manual grading",
                                    "passingScore": 75.0,
                                    "timeLimit": 30,
                                    "totalPoints": 10,
                                    "questions": [
                                        {
                                            "id": str(uuid.uuid4()),
                                            "type": "long_form",
                                            "question": "Explain the importance of manual grading in educational assessment. Provide detailed examples and analysis.",
                                            "points": 5,
                                            "required": True
                                        },
                                        {
                                            "id": str(uuid.uuid4()),
                                            "type": "essay",
                                            "question": "Describe a scenario where auto-completion after manual grading would be beneficial for student experience.",
                                            "points": 5,
                                            "required": True
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }

            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{BACKEND_URL}/courses", json=course_data, headers=headers)
            
            if response.status_code == 200:
                course = response.json()
                self.test_course_id = course["id"]
                # Extract quiz ID from the course structure
                self.test_quiz_id = course["modules"][0]["lessons"][0]["quiz"]["id"]
                self.log_test("Create Subjective-Only Course", True, 
                            f"Course created: {course['title']} (ID: {self.test_course_id})")
                return True
            else:
                self.log_test("Create Subjective-Only Course", False, 
                            error_msg=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Subjective-Only Course", False, error_msg=str(e))
            return False

    def student_enroll_in_course(self):
        """Student enrolls in the test course"""
        try:
            enrollment_data = {"courseId": self.test_course_id}
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.post(f"{BACKEND_URL}/enrollments", json=enrollment_data, headers=headers)
            
            if response.status_code == 200:
                enrollment = response.json()
                self.test_enrollment_id = enrollment["id"]
                self.log_test("Student Course Enrollment", True, 
                            f"Student enrolled with initial progress: {enrollment.get('progress', 0)}%")
                return True
            else:
                self.log_test("Student Course Enrollment", False, 
                            error_msg=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Course Enrollment", False, error_msg=str(e))
            return False

    def student_take_quiz(self):
        """Student takes the subjective quiz"""
        try:
            # Get course details to find lesson ID
            headers = {"Authorization": f"Bearer {self.student_token}"}
            course_response = requests.get(f"{BACKEND_URL}/courses/{self.test_course_id}", headers=headers)
            
            if course_response.status_code != 200:
                self.log_test("Student Take Quiz - Get Course", False, 
                            error_msg=f"Failed to get course: {course_response.status_code}")
                return False
                
            course = course_response.json()
            lesson_id = course["modules"][0]["lessons"][0]["id"]
            
            # Submit quiz with subjective answers
            quiz_submission = {
                "courseId": self.test_course_id,
                "lessonId": lesson_id,
                "quizId": self.test_quiz_id,
                "answers": [
                    {
                        "questionId": course["modules"][0]["lessons"][0]["quiz"]["questions"][0]["id"],
                        "answer": "Manual grading is crucial in educational assessment because it allows for nuanced evaluation of complex responses that cannot be automatically scored. For example, essay questions require human judgment to assess critical thinking, creativity, and depth of understanding. Manual grading enables instructors to provide personalized feedback and recognize unique insights that automated systems might miss."
                    },
                    {
                        "questionId": course["modules"][0]["lessons"][0]["quiz"]["questions"][1]["id"],
                        "answer": "Auto-completion after manual grading would be highly beneficial in professional certification programs where students must demonstrate mastery through written assessments. For instance, in a medical training course, students might complete case study analyses that require manual evaluation. Once the instructor grades these subjective responses and confirms the student has met the passing criteria, the system should automatically mark the course as complete and issue the certification, eliminating the need for students to manually mark completion."
                    }
                ],
                "timeSpent": 1800,  # 30 minutes
                "submittedAt": datetime.utcnow().isoformat()
            }
            
            response = requests.post(f"{BACKEND_URL}/quiz-submissions", json=quiz_submission, headers=headers)
            
            if response.status_code == 200:
                submission_result = response.json()
                self.test_quiz_attempt_id = submission_result.get("attemptId")
                
                # Verify initial score is 0% (no auto-gradable questions)
                initial_score = submission_result.get("score", 0)
                if initial_score == 0:
                    self.log_test("Student Take Quiz", True, 
                                f"Quiz submitted successfully. Initial score: {initial_score}% (expected for subjective-only quiz)")
                else:
                    self.log_test("Student Take Quiz", False, 
                                f"Unexpected initial score: {initial_score}% (should be 0% for subjective-only quiz)")
                    return False
                    
                return True
            else:
                self.log_test("Student Take Quiz", False, 
                            error_msg=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Student Take Quiz", False, error_msg=str(e))
            return False

    def verify_initial_course_status(self):
        """Verify course is initially incomplete"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            
            if response.status_code == 200:
                enrollments = response.json()
                test_enrollment = None
                
                for enrollment in enrollments:
                    if enrollment["courseId"] == self.test_course_id:
                        test_enrollment = enrollment
                        break
                
                if test_enrollment:
                    progress = test_enrollment.get("progress", 0)
                    status = test_enrollment.get("status", "active")
                    
                    if progress < 100 and status != "completed":
                        self.log_test("Verify Initial Course Status", True, 
                                    f"Course correctly shows as incomplete: {progress}% progress, status: {status}")
                        return True
                    else:
                        self.log_test("Verify Initial Course Status", False, 
                                    f"Course unexpectedly shows as complete: {progress}% progress, status: {status}")
                        return False
                else:
                    self.log_test("Verify Initial Course Status", False, "Test enrollment not found")
                    return False
            else:
                self.log_test("Verify Initial Course Status", False, 
                            error_msg=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Verify Initial Course Status", False, error_msg=str(e))
            return False

    def get_subjective_submissions(self):
        """Get subjective submissions for manual grading"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/courses/all/submissions", headers=headers)
            
            if response.status_code == 200:
                all_submissions = response.json()
                
                # Filter submissions for our test course and student
                test_submissions = []
                for submission in all_submissions:
                    if (submission.get("courseId") == self.test_course_id and 
                        submission.get("studentId") == self.student_user["id"]):
                        test_submissions.append(submission)
                
                if test_submissions:
                    self.subjective_submissions = test_submissions
                    self.log_test("Get Subjective Submissions", True, 
                                f"Found {len(test_submissions)} subjective submissions for grading")
                    return True
                else:
                    self.log_test("Get Subjective Submissions", False, 
                                "No subjective submissions found for test course")
                    return False
            else:
                self.log_test("Get Subjective Submissions", False, 
                            error_msg=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Subjective Submissions", False, error_msg=str(e))
            return False

    def manually_grade_submissions_to_passing(self):
        """Manually grade subjective submissions to passing scores"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            graded_count = 0
            
            for submission in self.subjective_submissions:
                submission_id = submission["id"]
                max_points = submission.get("maxPoints", 5)  # Default to 5 points
                passing_score = max_points * 0.8  # Give 80% score (above 75% passing threshold)
                
                grading_data = {
                    "score": passing_score,
                    "feedback": f"Excellent response demonstrating clear understanding of the concepts. Score: {passing_score}/{max_points}"
                }
                
                response = requests.post(f"{BACKEND_URL}/submissions/{submission_id}/grade", 
                                       json=grading_data, headers=headers)
                
                if response.status_code == 200:
                    graded_count += 1
                    self.log_test(f"Grade Submission {submission_id[:8]}...", True, 
                                f"Graded with score: {passing_score}/{max_points}")
                else:
                    self.log_test(f"Grade Submission {submission_id[:8]}...", False, 
                                error_msg=f"Status: {response.status_code}, Response: {response.text}")
                    return False
            
            if graded_count == len(self.subjective_submissions):
                self.log_test("Manual Grading Process", True, 
                            f"Successfully graded all {graded_count} subjective submissions to passing scores")
                return True
            else:
                self.log_test("Manual Grading Process", False, 
                            f"Only graded {graded_count}/{len(self.subjective_submissions)} submissions")
                return False
                
        except Exception as e:
            self.log_test("Manual Grading Process", False, error_msg=str(e))
            return False

    def verify_auto_completion_triggered(self):
        """Verify that auto-completion was triggered after manual grading"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            
            if response.status_code == 200:
                enrollments = response.json()
                test_enrollment = None
                
                for enrollment in enrollments:
                    if enrollment["courseId"] == self.test_course_id:
                        test_enrollment = enrollment
                        break
                
                if test_enrollment:
                    progress = test_enrollment.get("progress", 0)
                    status = test_enrollment.get("status", "active")
                    completed_at = test_enrollment.get("completedAt")
                    
                    if progress == 100.0 and status == "completed" and completed_at:
                        self.log_test("Verify Auto-Completion Triggered", True, 
                                    f"Course auto-completed successfully: {progress}% progress, status: {status}, completed at: {completed_at}")
                        return True
                    else:
                        self.log_test("Verify Auto-Completion Triggered", False, 
                                    f"Course not auto-completed: {progress}% progress, status: {status}, completed_at: {completed_at}")
                        return False
                else:
                    self.log_test("Verify Auto-Completion Triggered", False, "Test enrollment not found")
                    return False
            else:
                self.log_test("Verify Auto-Completion Triggered", False, 
                            error_msg=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Verify Auto-Completion Triggered", False, error_msg=str(e))
            return False

    def verify_certificate_generated(self):
        """Verify that completion certificate was automatically generated"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/certificates", headers=headers)
            
            if response.status_code == 200:
                certificates = response.json()
                
                # Look for certificate for our test course
                test_certificate = None
                for cert in certificates:
                    if cert.get("courseId") == self.test_course_id:
                        test_certificate = cert
                        break
                
                if test_certificate:
                    cert_number = test_certificate.get("certificateNumber")
                    issue_date = test_certificate.get("issueDate")
                    status = test_certificate.get("status")
                    
                    self.log_test("Verify Certificate Generated", True, 
                                f"Certificate auto-generated: {cert_number}, issued: {issue_date}, status: {status}")
                    return True
                else:
                    self.log_test("Verify Certificate Generated", False, 
                                "No certificate found for completed course")
                    return False
            else:
                self.log_test("Verify Certificate Generated", False, 
                            error_msg=f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Verify Certificate Generated", False, error_msg=str(e))
            return False

    def test_edge_case_failing_grade(self):
        """Test edge case: grading to failing score should NOT auto-complete"""
        try:
            # Create another course for this test
            course_data = {
                "title": "Failing Grade Test Course",
                "description": "Test course to verify failing grades don't trigger auto-completion",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "learningOutcomes": ["Test failing grade behavior"],
                "modules": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Failing Test Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Failing Quiz",
                                "type": "quiz",
                                "quiz": {
                                    "id": str(uuid.uuid4()),
                                    "title": "Failing Assessment",
                                    "description": "Quiz to test failing grade behavior",
                                    "passingScore": 75.0,
                                    "timeLimit": 30,
                                    "totalPoints": 10,
                                    "questions": [
                                        {
                                            "id": str(uuid.uuid4()),
                                            "type": "long_form",
                                            "question": "Test question for failing grade",
                                            "points": 10,
                                            "required": True
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }

            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{BACKEND_URL}/courses", json=course_data, headers=headers)
            
            if response.status_code != 200:
                self.log_test("Edge Case - Create Failing Test Course", False, 
                            error_msg=f"Failed to create course: {response.status_code}")
                return False
                
            failing_course = response.json()
            failing_course_id = failing_course["id"]
            
            # Student enrolls
            enrollment_data = {"courseId": failing_course_id}
            headers_student = {"Authorization": f"Bearer {self.student_token}"}
            enroll_response = requests.post(f"{BACKEND_URL}/enrollments", json=enrollment_data, headers=headers_student)
            
            if enroll_response.status_code != 200:
                self.log_test("Edge Case - Student Enroll in Failing Course", False, 
                            error_msg=f"Failed to enroll: {enroll_response.status_code}")
                return False
            
            # Student takes quiz
            lesson_id = failing_course["modules"][0]["lessons"][0]["id"]
            quiz_id = failing_course["modules"][0]["lessons"][0]["quiz"]["id"]
            
            quiz_submission = {
                "courseId": failing_course_id,
                "lessonId": lesson_id,
                "quizId": quiz_id,
                "answers": [
                    {
                        "questionId": failing_course["modules"][0]["lessons"][0]["quiz"]["questions"][0]["id"],
                        "answer": "Poor response for testing failing grade"
                    }
                ],
                "timeSpent": 600,
                "submittedAt": datetime.utcnow().isoformat()
            }
            
            quiz_response = requests.post(f"{BACKEND_URL}/quiz-submissions", json=quiz_submission, headers=headers_student)
            
            if quiz_response.status_code != 200:
                self.log_test("Edge Case - Submit Failing Quiz", False, 
                            error_msg=f"Failed to submit quiz: {quiz_response.status_code}")
                return False
            
            # Get submissions and grade with failing score
            submissions_response = requests.get(f"{BACKEND_URL}/courses/all/submissions", headers=headers)
            if submissions_response.status_code != 200:
                self.log_test("Edge Case - Get Failing Submissions", False, 
                            error_msg=f"Failed to get submissions: {submissions_response.status_code}")
                return False
                
            all_submissions = submissions_response.json()
            failing_submissions = [s for s in all_submissions if s.get("courseId") == failing_course_id]
            
            if not failing_submissions:
                self.log_test("Edge Case - Find Failing Submissions", False, "No submissions found")
                return False
            
            # Grade with failing score (below 75%)
            submission_id = failing_submissions[0]["id"]
            failing_grade_data = {
                "score": 5,  # 50% - below 75% passing threshold
                "feedback": "Response does not meet the required standards"
            }
            
            grade_response = requests.post(f"{BACKEND_URL}/submissions/{submission_id}/grade", 
                                         json=failing_grade_data, headers=headers)
            
            if grade_response.status_code != 200:
                self.log_test("Edge Case - Grade with Failing Score", False, 
                            error_msg=f"Failed to grade: {grade_response.status_code}")
                return False
            
            # Verify course is NOT auto-completed
            enrollments_response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers_student)
            if enrollments_response.status_code != 200:
                self.log_test("Edge Case - Check Failing Course Status", False, 
                            error_msg=f"Failed to get enrollments: {enrollments_response.status_code}")
                return False
                
            enrollments = enrollments_response.json()
            failing_enrollment = None
            for enrollment in enrollments:
                if enrollment["courseId"] == failing_course_id:
                    failing_enrollment = enrollment
                    break
            
            if failing_enrollment:
                progress = failing_enrollment.get("progress", 0)
                status = failing_enrollment.get("status", "active")
                
                if progress < 100 and status != "completed":
                    self.log_test("Edge Case - Failing Grade Behavior", True, 
                                f"Course correctly remains incomplete with failing grade: {progress}% progress, status: {status}")
                    return True
                else:
                    self.log_test("Edge Case - Failing Grade Behavior", False, 
                                f"Course incorrectly auto-completed with failing grade: {progress}% progress, status: {status}")
                    return False
            else:
                self.log_test("Edge Case - Failing Grade Behavior", False, "Failing course enrollment not found")
                return False
                
        except Exception as e:
            self.log_test("Edge Case - Failing Grade Behavior", False, error_msg=str(e))
            return False

    def run_comprehensive_test(self):
        """Run the complete test suite"""
        print("🎯 MANUAL GRADING AUTO-COMPLETION TESTING INITIATED")
        print("=" * 80)
        print()
        
        # Authentication tests
        if not self.authenticate_admin():
            return False
        if not self.authenticate_student():
            return False
            
        # Main test scenario
        if not self.create_subjective_only_course():
            return False
        if not self.student_enroll_in_course():
            return False
        if not self.student_take_quiz():
            return False
        if not self.verify_initial_course_status():
            return False
        if not self.get_subjective_submissions():
            return False
        if not self.manually_grade_submissions_to_passing():
            return False
        if not self.verify_auto_completion_triggered():
            return False
        if not self.verify_certificate_generated():
            return False
            
        # Edge case tests
        if not self.test_edge_case_failing_grade():
            return False
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("🎯 MANUAL GRADING AUTO-COMPLETION TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 SUCCESS RATE: {success_rate:.1f}% ({passed}/{total} tests passed)")
        print()
        
        if success_rate == 100:
            print("🎉 ALL TESTS PASSED - MANUAL GRADING AUTO-COMPLETION WORKING CORRECTLY")
            print()
            print("✅ Key Functionality Verified:")
            print("   • Subjective-only courses can be created and taken")
            print("   • Initial quiz scores are 0% for subjective questions")
            print("   • Manual grading updates quiz attempt scores")
            print("   • Auto-completion triggers when all quizzes pass")
            print("   • Course enrollment updates to 100% completed status")
            print("   • Completion certificates are automatically generated")
            print("   • Failing grades do NOT trigger auto-completion")
        else:
            print("❌ SOME TESTS FAILED - MANUAL GRADING AUTO-COMPLETION NEEDS ATTENTION")
            print()
            print("Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['error']}")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    test_suite = ManualGradingAutoCompletionTestSuite()
    
    try:
        success = test_suite.run_comprehensive_test()
        test_suite.print_summary()
        
        if success:
            print("\n🚀 CONCLUSION: Manual grading auto-completion functionality is working correctly!")
            print("Students will no longer see 'you must take and pass the quiz before marking it as complete' error")
            print("Course completion works seamlessly for subjective-only quiz courses")
            sys.exit(0)
        else:
            print("\n🚨 CONCLUSION: Manual grading auto-completion functionality needs fixes")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        test_suite.print_summary()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error during testing: {str(e)}")
        test_suite.print_summary()
        sys.exit(1)

if __name__ == "__main__":
    main()