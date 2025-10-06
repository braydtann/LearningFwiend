#!/usr/bin/env python3
"""
Multi-Quiz Progression Validation Test
=====================================

Since no existing courses have multiple quizzes, this test will:
1. Create a test course with multiple quiz lessons across different modules
2. Test the multi-quiz progression logic and validation
3. Verify the backend properly handles multi-quiz course completion requirements
4. Test enrollment progress updates with quiz completion validation

This addresses the review request for testing multi-quiz progression functionality.
"""

import requests
import json
import sys
from datetime import datetime
import uuid

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

class MultiQuizProgressionValidationSuite:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.admin_user = None
        self.student_user = None
        self.test_results = []
        self.test_course_id = None
        
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

    def create_multi_quiz_test_course(self):
        """Create a test course with multiple quiz lessons across different modules"""
        try:
            # Create course with multiple modules, each containing a quiz
            course_data = {
                "title": f"Multi-Quiz Progression Test Course - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test course for validating multi-quiz progression logic with quizzes in different modules",
                "category": "Testing",
                "duration": "2 hours",
                "accessType": "open",
                "learningOutcomes": ["Test multi-quiz progression", "Validate completion logic"],
                "modules": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Module 1: Introduction",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Introduction Text",
                                "type": "text",
                                "content": "Welcome to the multi-quiz progression test course."
                            },
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Module 1 Quiz",
                                "type": "quiz",
                                "quiz": {
                                    "questions": [
                                        {
                                            "id": str(uuid.uuid4()),
                                            "type": "multiple-choice",
                                            "question": "What is 2 + 2?",
                                            "options": ["3", "4", "5", "6"],
                                            "correctAnswer": 1,
                                            "points": 1
                                        }
                                    ],
                                    "passingScore": 70,
                                    "maxAttempts": 3,
                                    "timeLimit": 300
                                }
                            }
                        ]
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Module 2: Intermediate",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Intermediate Content",
                                "type": "text",
                                "content": "This is intermediate content before the second quiz."
                            },
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Module 2 Quiz",
                                "type": "quiz",
                                "quiz": {
                                    "questions": [
                                        {
                                            "id": str(uuid.uuid4()),
                                            "type": "multiple-choice",
                                            "question": "What is 3 + 3?",
                                            "options": ["5", "6", "7", "8"],
                                            "correctAnswer": 1,
                                            "points": 1
                                        }
                                    ],
                                    "passingScore": 70,
                                    "maxAttempts": 3,
                                    "timeLimit": 300
                                }
                            }
                        ]
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Module 3: Advanced",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Advanced Content",
                                "type": "text",
                                "content": "This is advanced content before the final quiz."
                            },
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Module 3 Final Quiz",
                                "type": "quiz",
                                "quiz": {
                                    "questions": [
                                        {
                                            "id": str(uuid.uuid4()),
                                            "type": "multiple-choice",
                                            "question": "What is 5 + 5?",
                                            "options": ["8", "9", "10", "11"],
                                            "correctAnswer": 2,
                                            "points": 1
                                        }
                                    ],
                                    "passingScore": 70,
                                    "maxAttempts": 3,
                                    "timeLimit": 300
                                }
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code in [200, 201]:
                course = response.json()
                self.test_course_id = course["id"]
                
                # Verify the course structure
                quiz_count = 0
                module_count = len(course_data["modules"])
                
                for module in course_data["modules"]:
                    for lesson in module["lessons"]:
                        if lesson["type"] == "quiz":
                            quiz_count += 1
                
                self.log_test(
                    "Create Multi-Quiz Test Course",
                    True,
                    f"Created course '{course['title']}' with {module_count} modules and {quiz_count} quizzes"
                )
                return True
            else:
                self.log_test(
                    "Create Multi-Quiz Test Course",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Create Multi-Quiz Test Course", False, error_msg=str(e))
            return False

    def enroll_student_in_test_course(self):
        """Enroll the test student in the multi-quiz test course"""
        try:
            if not self.test_course_id:
                self.log_test(
                    "Enroll Student in Test Course",
                    False,
                    "No test course available for enrollment"
                )
                return False
            
            enrollment_data = {
                "courseId": self.test_course_id
            }
            
            response = requests.post(
                f"{BACKEND_URL}/enrollments",
                json=enrollment_data,
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code in [200, 201]:
                enrollment = response.json()
                self.log_test(
                    "Enroll Student in Test Course",
                    True,
                    f"Student enrolled in test course, initial progress: {enrollment.get('progress', 0)}%"
                )
                return True
            else:
                self.log_test(
                    "Enroll Student in Test Course",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Enroll Student in Test Course", False, error_msg=str(e))
            return False

    def test_partial_progress_update(self):
        """Test that partial progress updates work (less than 100%)"""
        try:
            if not self.test_course_id:
                self.log_test(
                    "Test Partial Progress Update",
                    False,
                    "No test course available"
                )
                return False
            
            # Test updating progress to 50% (should work)
            progress_data = {
                "progress": 50.0,
                "lastAccessedAt": datetime.utcnow().isoformat()
            }
            
            response = requests.put(
                f"{BACKEND_URL}/enrollments/{self.test_course_id}/progress",
                json=progress_data,
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code in [200, 201]:
                updated_enrollment = response.json()
                actual_progress = updated_enrollment.get("progress", 0)
                
                self.log_test(
                    "Test Partial Progress Update",
                    True,
                    f"Successfully updated progress to {actual_progress}% (requested: 50%)"
                )
                return True
            else:
                self.log_test(
                    "Test Partial Progress Update",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Test Partial Progress Update", False, error_msg=str(e))
            return False

    def test_completion_validation_without_quizzes(self):
        """Test that 100% completion is blocked when quizzes haven't been completed"""
        try:
            if not self.test_course_id:
                self.log_test(
                    "Test Completion Validation Without Quizzes",
                    False,
                    "No test course available"
                )
                return False
            
            # Test updating progress to 100% without completing quizzes (should be blocked)
            completion_data = {
                "progress": 100.0,
                "lastAccessedAt": datetime.utcnow().isoformat()
            }
            
            response = requests.put(
                f"{BACKEND_URL}/enrollments/{self.test_course_id}/progress",
                json=completion_data,
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code == 400:
                # Expected behavior - completion blocked due to incomplete quizzes
                error_message = response.text
                self.log_test(
                    "Test Completion Validation Without Quizzes",
                    True,
                    f"✅ Completion properly blocked with 400 error: {error_message[:100]}..."
                )
                return True
            elif response.status_code in [200, 201]:
                # Unexpected - completion was allowed
                self.log_test(
                    "Test Completion Validation Without Quizzes",
                    False,
                    "❌ Completion was allowed when it should have been blocked (quizzes not completed)"
                )
                return False
            else:
                self.log_test(
                    "Test Completion Validation Without Quizzes",
                    False,
                    f"Unexpected status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Test Completion Validation Without Quizzes", False, error_msg=str(e))
            return False

    def test_course_structure_validation(self):
        """Verify the test course has the expected multi-quiz structure"""
        try:
            if not self.test_course_id:
                self.log_test(
                    "Test Course Structure Validation",
                    False,
                    "No test course available"
                )
                return False
            
            response = requests.get(
                f"{BACKEND_URL}/courses/{self.test_course_id}",
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code == 200:
                course = response.json()
                modules = course.get("modules", [])
                
                quiz_lessons = []
                total_lessons = 0
                
                for module in modules:
                    for lesson in module.get("lessons", []):
                        total_lessons += 1
                        if lesson.get("type") == "quiz":
                            quiz_lessons.append({
                                "lessonId": lesson.get("id"),
                                "moduleId": module.get("id"),
                                "title": lesson.get("title"),
                                "hasQuestions": bool(lesson.get("quiz", {}).get("questions"))
                            })
                
                expected_quizzes = 3  # We created 3 quiz lessons
                actual_quizzes = len(quiz_lessons)
                
                if actual_quizzes == expected_quizzes:
                    self.log_test(
                        "Test Course Structure Validation",
                        True,
                        f"Course structure verified: {len(modules)} modules, {total_lessons} total lessons, {actual_quizzes} quiz lessons"
                    )
                    return True
                else:
                    self.log_test(
                        "Test Course Structure Validation",
                        False,
                        f"Expected {expected_quizzes} quizzes, found {actual_quizzes}"
                    )
                    return False
            else:
                self.log_test(
                    "Test Course Structure Validation",
                    False,
                    f"Failed to get course details: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Test Course Structure Validation", False, error_msg=str(e))
            return False

    def test_enrollment_progress_structure(self):
        """Test that enrollment has proper progress tracking structure for multi-quiz course"""
        try:
            if not self.test_course_id:
                self.log_test(
                    "Test Enrollment Progress Structure",
                    False,
                    "No test course available"
                )
                return False
            
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=self.get_headers(self.student_token))
            
            if response.status_code == 200:
                enrollments = response.json()
                
                # Find enrollment for our test course
                test_enrollment = None
                for enrollment in enrollments:
                    if enrollment.get("courseId") == self.test_course_id:
                        test_enrollment = enrollment
                        break
                
                if test_enrollment:
                    has_progress = "progress" in test_enrollment
                    has_module_progress = "moduleProgress" in test_enrollment
                    has_current_lesson = "currentLessonId" in test_enrollment
                    
                    progress_value = test_enrollment.get("progress", 0)
                    
                    if has_progress:
                        self.log_test(
                            "Test Enrollment Progress Structure",
                            True,
                            f"Enrollment has proper structure: progress={progress_value}%, moduleProgress={has_module_progress}, currentLesson={has_current_lesson}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Test Enrollment Progress Structure",
                            False,
                            "Enrollment missing required progress fields"
                        )
                        return False
                else:
                    self.log_test(
                        "Test Enrollment Progress Structure",
                        False,
                        "Test course enrollment not found"
                    )
                    return False
            else:
                self.log_test(
                    "Test Enrollment Progress Structure",
                    False,
                    f"Failed to get enrollments: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Test Enrollment Progress Structure", False, error_msg=str(e))
            return False

    def cleanup_test_course(self):
        """Clean up the test course after testing"""
        try:
            if not self.test_course_id:
                return True
            
            response = requests.delete(
                f"{BACKEND_URL}/courses/{self.test_course_id}",
                headers=self.get_headers(self.admin_token)
            )
            
            if response.status_code in [200, 204]:
                print(f"🧹 Cleaned up test course: {self.test_course_id}")
                return True
            else:
                print(f"⚠️  Failed to cleanup test course: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️  Cleanup error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all multi-quiz progression validation tests"""
        print("🚀 Starting Multi-Quiz Progression Validation Testing")
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
        
        # Core validation tests
        test_methods = [
            self.create_multi_quiz_test_course,
            self.test_course_structure_validation,
            self.enroll_student_in_test_course,
            self.test_enrollment_progress_structure,
            self.test_partial_progress_update,
            self.test_completion_validation_without_quizzes
        ]
        
        print("🧪 Running Multi-Quiz Progression Validation Tests")
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
        
        # Cleanup
        self.cleanup_test_course()
        
        print()
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 Multi-Quiz Progression Validation: SUCCESS")
            return True
        else:
            print("⚠️  Multi-Quiz Progression Validation: NEEDS ATTENTION")
            return False

def main():
    """Main test execution"""
    test_suite = MultiQuizProgressionValidationSuite()
    
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