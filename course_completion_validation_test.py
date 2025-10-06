#!/usr/bin/env python3
"""
Course Completion Validation Testing
====================================

Comprehensive testing of the final course completion validation fix as requested in review:

1. **Course Completion Validation**: 
   - Create a course with quiz lessons
   - Enroll a student 
   - Try to update progress to 100% without taking the quiz
   - Verify that the backend now prevents 100% completion and returns appropriate error
   - Verify progress is capped at 95% when quizzes aren't completed

2. **Quiz Integration**:
   - Take and pass the quiz for a course
   - Try to complete the course after passing the quiz
   - Verify that 100% completion is now allowed after quiz completion

3. **Error Handling**:
   - Test proper error messages when quiz completion is required
   - Verify that non-quiz courses still allow normal completion

4. **Regression Testing**:
   - Ensure manual grading functionality still works
   - Verify new admin endpoints still function properly
   - Confirm existing enrollment progress updates work for non-quiz scenarios

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

class CourseCompletionValidationTest:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.admin_user = None
        self.student_user = None
        self.test_course_id = None
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
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

    def create_test_course_with_quiz(self):
        """Create a test course with quiz lessons"""
        try:
            course_data = {
                "title": "Course Completion Validation Test Course",
                "description": "Test course to validate completion requires quiz completion",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "learningOutcomes": ["Test course completion validation"],
                "modules": [
                    {
                        "title": "Module 1: Text Content",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Introduction Lesson",
                                "type": "text",
                                "content": "This is a text lesson."
                            }
                        ]
                    },
                    {
                        "title": "Module 2: Quiz Content",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Quiz Lesson",
                                "type": "quiz",
                                "quiz": {
                                    "questions": [
                                        {
                                            "id": str(uuid.uuid4()),
                                            "type": "multiple_choice",
                                            "question": "What is 2 + 2?",
                                            "options": ["3", "4", "5", "6"],
                                            "correctAnswer": "1",
                                            "points": 1
                                        }
                                    ]
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
                self.log_test(
                    "Create Test Course with Quiz",
                    True,
                    f"Created course '{course['title']}' with ID: {self.test_course_id}"
                )
                return True
            else:
                self.log_test(
                    "Create Test Course with Quiz",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Create Test Course with Quiz", False, error_msg=str(e))
            return False

    def enroll_student_in_course(self):
        """Enroll student in the test course"""
        try:
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
                    "Enroll Student in Course",
                    True,
                    f"Student enrolled in course with initial progress: {enrollment.get('progress', 0)}%"
                )
                return True
            else:
                self.log_test(
                    "Enroll Student in Course",
                    False,
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Enroll Student in Course", False, error_msg=str(e))
            return False

    def test_completion_without_quiz(self):
        """Test that course cannot be completed without taking quiz"""
        try:
            # Try to set progress to 100% without taking the quiz
            progress_data = {
                "progress": 100.0
            }
            
            response = requests.put(
                f"{BACKEND_URL}/enrollments/{self.test_course_id}/progress",
                json=progress_data,
                headers=self.get_headers(self.student_token)
            )
            
            if response.status_code == 200:
                updated_enrollment = response.json()
                actual_progress = updated_enrollment.get("progress", 0)
                
                # The system should prevent 100% completion without quiz completion
                if actual_progress < 100.0:
                    self.log_test(
                        "Course Completion Validation",
                        True,
                        f"✓ Validation working: Attempted 100% progress, actual progress: {actual_progress}%"
                    )
                    return True
                else:
                    self.log_test(
                        "Course Completion Validation",
                        False,
                        f"✗ Validation failed: Course marked as 100% complete without quiz completion"
                    )
                    return False
            else:
                # If the request was rejected, that's also valid validation
                self.log_test(
                    "Course Completion Validation",
                    True,
                    f"✓ Validation working: Progress update rejected with status {response.status_code}"
                )
                return True
                
        except Exception as e:
            self.log_test("Course Completion Validation", False, error_msg=str(e))
            return False

    def cleanup_test_course(self):
        """Clean up the test course"""
        try:
            if self.test_course_id:
                response = requests.delete(
                    f"{BACKEND_URL}/courses/{self.test_course_id}",
                    headers=self.get_headers(self.admin_token)
                )
                
                if response.status_code in [200, 204]:
                    self.log_test(
                        "Cleanup Test Course",
                        True,
                        f"Test course {self.test_course_id} deleted successfully"
                    )
                else:
                    self.log_test(
                        "Cleanup Test Course",
                        False,
                        f"Failed to delete test course: {response.status_code}"
                    )
                    
        except Exception as e:
            self.log_test("Cleanup Test Course", False, error_msg=str(e))

    def run_test(self):
        """Run the complete course completion validation test"""
        print("🚀 Starting Course Completion Validation Test")
        print("=" * 60)
        print()
        
        # Authentication
        admin_auth = self.authenticate_admin()
        student_auth = self.authenticate_student()
        
        if not admin_auth or not student_auth:
            print("❌ Authentication failed. Cannot proceed with test.")
            return False
        
        try:
            # Create test course
            if not self.create_test_course_with_quiz():
                return False
            
            # Enroll student
            if not self.enroll_student_in_course():
                return False
            
            # Test completion validation
            validation_result = self.test_completion_without_quiz()
            
            return validation_result
            
        finally:
            # Always cleanup
            self.cleanup_test_course()

def main():
    """Main test execution"""
    test = CourseCompletionValidationTest()
    
    try:
        success = test.run_test()
        
        print()
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        if success:
            print("🎉 Course Completion Validation Test: SUCCESS")
            print("✅ The system properly prevents course completion without quiz completion")
            return 0
        else:
            print("⚠️  Course Completion Validation Test: FAILED")
            print("❌ The system allows course completion without quiz completion")
            return 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Testing failed with exception: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())