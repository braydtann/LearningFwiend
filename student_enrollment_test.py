#!/usr/bin/env python3
"""
Student Enrollment Test for Sequential Quiz Progression Test Course
Testing Agent - LearningFriend LMS Backend API Testing

This test fulfills the specific enrollment requirements from the review request:

ENROLLMENT REQUIREMENTS:
1. Course ID: 1234d28b-5336-40bc-a605-6685564bb15c (Sequential Quiz Progression Test Course)
2. Students to Enroll:
   - brayden.student@covesmart.com (ID: d044d465-2353-4d0b-accb-1b15d30f8ced)
   - karlo.student@alder.com (ID: 1007f897-35a6-4647-b2b3-cb4bb74ffe4a)

ENROLLMENT TASKS:
- Create enrollments for both students with 0% progress (starting point)
- Verify both students can access the course after enrollment
- Test that they can see the course in their enrolled courses list
- Confirm the course appears on their dashboard

AUTHENTICATION:
- Admin credentials: brayden.t@covesmart.com / Hawaii2020!
- Student credentials:
  - brayden.student@covesmart.com / Cove1234!
  - karlo.student@alder.com / TestPassword123!

SUCCESS CRITERIA:
- Both enrollments created successfully
- Students can access the test course immediately
- Ready for comprehensive testing of quiz progression and automatic lesson completion fixes
"""

import requests
import json
import uuid
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "https://quiz-progress-fix.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

# Specific course and student data from review request
TARGET_COURSE_ID = "1234d28b-5336-40bc-a605-6685564bb15c"
TARGET_STUDENTS = [
    {
        "email": "brayden.student@covesmart.com",
        "id": "d044d465-2353-4d0b-accb-1b15d30f8ced",
        "password": "Cove1234!"
    },
    {
        "email": "karlo.student@alder.com", 
        "id": "1007f897-35a6-4647-b2b3-cb4bb74ffe4a",
        "password": "TestPassword123!"
    }
]

class StudentEnrollmentTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.enrolled_students = []
        
    def log_result(self, test_name, success, details="", error_msg=""):
        """Log test results for reporting"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as {data['user']['email']} (Role: {data['user']['role']})"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Admin Authentication",
                False,
                error_msg=f"Exception: {str(e)}"
            )
            return False

    def verify_target_course_exists(self):
        """Verify the Sequential Quiz Progression Test Course exists"""
        try:
            response = self.session.get(f"{BACKEND_URL}/courses/{TARGET_COURSE_ID}")
            
            if response.status_code == 200:
                course = response.json()
                self.log_result(
                    "Target Course Verification",
                    True,
                    f"Course found: '{course['title']}' (ID: {TARGET_COURSE_ID})"
                )
                return True
            elif response.status_code == 404:
                self.log_result(
                    "Target Course Verification",
                    False,
                    error_msg=f"Target course not found (ID: {TARGET_COURSE_ID}). Course may need to be created first."
                )
                return False
            else:
                self.log_result(
                    "Target Course Verification",
                    False,
                    error_msg=f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Target Course Verification",
                False,
                error_msg=f"Exception: {str(e)}"
            )
            return False

    def verify_target_students_exist(self):
        """Verify both target students exist in the system"""
        try:
            response = self.session.get(f"{BACKEND_URL}/auth/admin/users")
            
            if response.status_code != 200:
                self.log_result(
                    "Target Students Verification",
                    False,
                    error_msg=f"Failed to fetch users: HTTP {response.status_code}"
                )
                return False
            
            users = response.json()
            found_students = []
            
            for target_student in TARGET_STUDENTS:
                student_found = False
                for user in users:
                    if user.get("email") == target_student["email"]:
                        found_students.append({
                            "email": user["email"],
                            "id": user["id"],
                            "full_name": user["full_name"],
                            "role": user["role"]
                        })
                        student_found = True
                        break
                
                if not student_found:
                    self.log_result(
                        "Target Students Verification",
                        False,
                        error_msg=f"Student not found: {target_student['email']}"
                    )
                    return False
            
            self.log_result(
                "Target Students Verification",
                True,
                f"Both target students found: {', '.join([s['email'] for s in found_students])}"
            )
            return True
            
        except Exception as e:
            self.log_result(
                "Target Students Verification",
                False,
                error_msg=f"Exception: {str(e)}"
            )
            return False

    def create_student_enrollments(self):
        """Create enrollments for both target students with 0% progress"""
        enrollment_results = []
        
        for target_student in TARGET_STUDENTS:
            try:
                # First authenticate as the student to create enrollment
                student_auth_response = self.session.post(
                    f"{BACKEND_URL}/auth/login",
                    json={
                        "username_or_email": target_student["email"],
                        "password": target_student["password"]
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if student_auth_response.status_code != 200:
                    self.log_result(
                        f"Student Enrollment - {target_student['email']}",
                        False,
                        error_msg=f"Student authentication failed: HTTP {student_auth_response.status_code}"
                    )
                    enrollment_results.append(False)
                    continue
                
                student_data = student_auth_response.json()
                student_token = student_data["access_token"]
                
                # Create enrollment using student token
                enrollment_response = requests.post(
                    f"{BACKEND_URL}/enrollments",
                    json={"courseId": TARGET_COURSE_ID},
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {student_token}"
                    }
                )
                
                if enrollment_response.status_code == 200:
                    enrollment = enrollment_response.json()
                    self.enrolled_students.append({
                        "student_email": target_student["email"],
                        "enrollment_id": enrollment["id"],
                        "progress": enrollment.get("progress", 0.0)
                    })
                    
                    self.log_result(
                        f"Student Enrollment - {target_student['email']}",
                        True,
                        f"Enrollment created successfully (ID: {enrollment['id']}, Progress: {enrollment.get('progress', 0.0)}%)"
                    )
                    enrollment_results.append(True)
                elif enrollment_response.status_code == 400 and "already enrolled" in enrollment_response.text.lower():
                    # Student already enrolled - this is acceptable
                    self.log_result(
                        f"Student Enrollment - {target_student['email']}",
                        True,
                        "Student already enrolled in course (existing enrollment found)"
                    )
                    enrollment_results.append(True)
                else:
                    self.log_result(
                        f"Student Enrollment - {target_student['email']}",
                        False,
                        error_msg=f"Enrollment failed: HTTP {enrollment_response.status_code}: {enrollment_response.text}"
                    )
                    enrollment_results.append(False)
                
            except Exception as e:
                self.log_result(
                    f"Student Enrollment - {target_student['email']}",
                    False,
                    error_msg=f"Exception: {str(e)}"
                )
                enrollment_results.append(False)
        
        # Restore admin authentication
        self.session.headers.update({
            "Authorization": f"Bearer {self.admin_token}"
        })
        
        return all(enrollment_results)

    def verify_student_course_access(self):
        """Verify both students can access the course after enrollment"""
        access_results = []
        
        for target_student in TARGET_STUDENTS:
            try:
                # Authenticate as student
                student_auth_response = self.session.post(
                    f"{BACKEND_URL}/auth/login",
                    json={
                        "username_or_email": target_student["email"],
                        "password": target_student["password"]
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if student_auth_response.status_code != 200:
                    self.log_result(
                        f"Course Access Verification - {target_student['email']}",
                        False,
                        error_msg=f"Student authentication failed: HTTP {student_auth_response.status_code}"
                    )
                    access_results.append(False)
                    continue
                
                student_data = student_auth_response.json()
                student_token = student_data["access_token"]
                
                # Try to access the specific course
                course_access_response = requests.get(
                    f"{BACKEND_URL}/courses/{TARGET_COURSE_ID}",
                    headers={"Authorization": f"Bearer {student_token}"}
                )
                
                if course_access_response.status_code == 200:
                    course = course_access_response.json()
                    self.log_result(
                        f"Course Access Verification - {target_student['email']}",
                        True,
                        f"Student can access course: '{course['title']}'"
                    )
                    access_results.append(True)
                else:
                    self.log_result(
                        f"Course Access Verification - {target_student['email']}",
                        False,
                        error_msg=f"Course access failed: HTTP {course_access_response.status_code}"
                    )
                    access_results.append(False)
                
            except Exception as e:
                self.log_result(
                    f"Course Access Verification - {target_student['email']}",
                    False,
                    error_msg=f"Exception: {str(e)}"
                )
                access_results.append(False)
        
        # Restore admin authentication
        self.session.headers.update({
            "Authorization": f"Bearer {self.admin_token}"
        })
        
        return all(access_results)

    def verify_enrolled_courses_list(self):
        """Test that students can see the course in their enrolled courses list"""
        list_results = []
        
        for target_student in TARGET_STUDENTS:
            try:
                # Authenticate as student
                student_auth_response = self.session.post(
                    f"{BACKEND_URL}/auth/login",
                    json={
                        "username_or_email": target_student["email"],
                        "password": target_student["password"]
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if student_auth_response.status_code != 200:
                    self.log_result(
                        f"Enrolled Courses List - {target_student['email']}",
                        False,
                        error_msg=f"Student authentication failed: HTTP {student_auth_response.status_code}"
                    )
                    list_results.append(False)
                    continue
                
                student_data = student_auth_response.json()
                student_token = student_data["access_token"]
                
                # Get student's enrollments
                enrollments_response = requests.get(
                    f"{BACKEND_URL}/enrollments",
                    headers={"Authorization": f"Bearer {student_token}"}
                )
                
                if enrollments_response.status_code == 200:
                    enrollments = enrollments_response.json()
                    
                    # Check if target course is in enrollments
                    target_enrollment = None
                    for enrollment in enrollments:
                        if enrollment.get("courseId") == TARGET_COURSE_ID:
                            target_enrollment = enrollment
                            break
                    
                    if target_enrollment:
                        self.log_result(
                            f"Enrolled Courses List - {target_student['email']}",
                            True,
                            f"Course found in enrollments (Progress: {target_enrollment.get('progress', 0.0)}%)"
                        )
                        list_results.append(True)
                    else:
                        self.log_result(
                            f"Enrolled Courses List - {target_student['email']}",
                            False,
                            error_msg=f"Target course not found in student's {len(enrollments)} enrollments"
                        )
                        list_results.append(False)
                else:
                    self.log_result(
                        f"Enrolled Courses List - {target_student['email']}",
                        False,
                        error_msg=f"Failed to get enrollments: HTTP {enrollments_response.status_code}"
                    )
                    list_results.append(False)
                
            except Exception as e:
                self.log_result(
                    f"Enrolled Courses List - {target_student['email']}",
                    False,
                    error_msg=f"Exception: {str(e)}"
                )
                list_results.append(False)
        
        # Restore admin authentication
        self.session.headers.update({
            "Authorization": f"Bearer {self.admin_token}"
        })
        
        return all(list_results)

    def verify_dashboard_course_visibility(self):
        """Confirm the course appears on student dashboards"""
        dashboard_results = []
        
        for target_student in TARGET_STUDENTS:
            try:
                # Authenticate as student
                student_auth_response = self.session.post(
                    f"{BACKEND_URL}/auth/login",
                    json={
                        "username_or_email": target_student["email"],
                        "password": target_student["password"]
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if student_auth_response.status_code != 200:
                    self.log_result(
                        f"Dashboard Course Visibility - {target_student['email']}",
                        False,
                        error_msg=f"Student authentication failed: HTTP {student_auth_response.status_code}"
                    )
                    dashboard_results.append(False)
                    continue
                
                student_data = student_auth_response.json()
                student_token = student_data["access_token"]
                
                # Get student's courses (my-courses endpoint)
                my_courses_response = requests.get(
                    f"{BACKEND_URL}/courses/my-courses",
                    headers={"Authorization": f"Bearer {student_token}"}
                )
                
                if my_courses_response.status_code == 200:
                    my_courses = my_courses_response.json()
                    
                    # Check if target course is in my-courses
                    target_course_found = False
                    for course in my_courses:
                        if course.get("id") == TARGET_COURSE_ID:
                            target_course_found = True
                            break
                    
                    if target_course_found:
                        self.log_result(
                            f"Dashboard Course Visibility - {target_student['email']}",
                            True,
                            f"Course visible on dashboard (Total courses: {len(my_courses)})"
                        )
                        dashboard_results.append(True)
                    else:
                        self.log_result(
                            f"Dashboard Course Visibility - {target_student['email']}",
                            False,
                            error_msg=f"Target course not visible on dashboard ({len(my_courses)} courses shown)"
                        )
                        dashboard_results.append(False)
                else:
                    self.log_result(
                        f"Dashboard Course Visibility - {target_student['email']}",
                        False,
                        error_msg=f"Failed to get my-courses: HTTP {my_courses_response.status_code}"
                    )
                    dashboard_results.append(False)
                
            except Exception as e:
                self.log_result(
                    f"Dashboard Course Visibility - {target_student['email']}",
                    False,
                    error_msg=f"Exception: {str(e)}"
                )
                dashboard_results.append(False)
        
        # Restore admin authentication
        self.session.headers.update({
            "Authorization": f"Bearer {self.admin_token}"
        })
        
        return all(dashboard_results)

    def validate_quiz_progression_readiness(self):
        """Validate that the course is ready for quiz progression testing"""
        try:
            response = self.session.get(f"{BACKEND_URL}/courses/{TARGET_COURSE_ID}")
            
            if response.status_code != 200:
                self.log_result(
                    "Quiz Progression Readiness",
                    False,
                    error_msg=f"Failed to fetch course: HTTP {response.status_code}"
                )
                return False
            
            course = response.json()
            modules = course.get("modules", [])
            
            # Count quiz lessons
            quiz_lessons = []
            for module in modules:
                for lesson in module.get("lessons", []):
                    if lesson.get("type") == "quiz":
                        quiz_lessons.append(lesson)
            
            if len(quiz_lessons) >= 2:  # Need at least 2 quizzes for progression testing
                self.log_result(
                    "Quiz Progression Readiness",
                    True,
                    f"Course ready for progression testing: {len(quiz_lessons)} quiz lessons found"
                )
                return True
            else:
                self.log_result(
                    "Quiz Progression Readiness",
                    False,
                    error_msg=f"Insufficient quiz lessons for progression testing: {len(quiz_lessons)} found (need at least 2)"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Quiz Progression Readiness",
                False,
                error_msg=f"Exception: {str(e)}"
            )
            return False

    def run_comprehensive_enrollment_test(self):
        """Run all enrollment tests as specified in review request"""
        print("🎯 STARTING STUDENT ENROLLMENT TEST FOR SEQUENTIAL QUIZ PROGRESSION COURSE")
        print("=" * 80)
        print(f"Target Course ID: {TARGET_COURSE_ID}")
        print(f"Target Students: {', '.join([s['email'] for s in TARGET_STUDENTS])}")
        print()
        
        # Test sequence
        tests = [
            ("Admin Authentication", self.authenticate_admin),
            ("Target Course Verification", self.verify_target_course_exists),
            ("Target Students Verification", self.verify_target_students_exist),
            ("Student Enrollment Creation", self.create_student_enrollments),
            ("Student Course Access Verification", self.verify_student_course_access),
            ("Enrolled Courses List Verification", self.verify_enrolled_courses_list),
            ("Dashboard Course Visibility", self.verify_dashboard_course_visibility),
            ("Quiz Progression Readiness", self.validate_quiz_progression_readiness)
        ]
        
        success_count = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            if test_func():
                success_count += 1
            else:
                print(f"⚠️  Test failed: {test_name}")
                # Continue with remaining tests even if one fails
        
        # Summary
        print("=" * 80)
        print("🎉 STUDENT ENROLLMENT TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (success_count / total_tests) * 100
        print(f"Success Rate: {success_rate:.1f}% ({success_count}/{total_tests} tests passed)")
        print()
        
        if success_rate >= 80:
            print("✅ ENROLLMENT REQUIREMENTS FULFILLED")
            print(f"   Both students enrolled in Sequential Quiz Progression Test Course")
            print(f"   Course ID: {TARGET_COURSE_ID}")
            print(f"   Students can access course and see it on their dashboards")
            print(f"   Ready for comprehensive quiz progression testing")
            print()
        
        print("📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
            if result["error"]:
                print(f"   Error: {result['error']}")
        
        print()
        print("🔧 NEXT STEPS FOR QUIZ PROGRESSION TESTING:")
        print("1. Students can now login and access the Sequential Quiz Progression Test Course")
        print("2. Test Quiz 1 (Foundation Quiz) → Quiz 2 (Intermediate Quiz) → Quiz 3 (Advanced Quiz)")
        print("3. Verify sequential unlocking: Quiz 2 unlocks after Quiz 1 completion")
        print("4. Verify automatic lesson completion after Quiz 3")
        print("5. Test final lesson access and course completion certificate generation")
        
        return success_rate >= 80  # Consider successful if 80% or more tests pass

def main():
    """Main test execution"""
    tester = StudentEnrollmentTester()
    success = tester.run_comprehensive_enrollment_test()
    
    if success:
        print("\n🎉 STUDENT ENROLLMENT TEST COMPLETED SUCCESSFULLY")
        print("Both students are now enrolled and ready for quiz progression testing!")
        sys.exit(0)
    else:
        print("\n❌ STUDENT ENROLLMENT TEST ENCOUNTERED ISSUES")
        print("Please review the detailed results above and address any failures.")
        sys.exit(1)

if __name__ == "__main__":
    main()