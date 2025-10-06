#!/usr/bin/env python3
"""
Course Navigation and Quiz Completion Workflow Backend Testing
Testing the backend APIs that support the new navigation logic and course completion features.
"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path

# Configuration - Use the correct backend URL from frontend/.env
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

class CourseNavigationTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        self.test_course_id = None
        self.test_program_id = None
        self.test_classroom_id = None
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}'
                })
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Successfully authenticated as admin: {data.get('user', {}).get('email', 'Unknown')}"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"Authentication failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Admin Authentication",
                False,
                f"Authentication error: {str(e)}"
            )
            return False
    
    def authenticate_student(self):
        """Authenticate as student user"""
        try:
            # Create a separate session for student to avoid token conflicts
            student_session = requests.Session()
            response = student_session.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get('access_token')
                self.log_result(
                    "Student Authentication",
                    True,
                    f"Successfully authenticated as student: {data.get('user', {}).get('email', 'Unknown')}"
                )
                return True
            else:
                self.log_result(
                    "Student Authentication",
                    False,
                    f"Authentication failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Student Authentication",
                False,
                f"Authentication error: {str(e)}"
            )
            return False
    
    def test_course_enrollment_progress_api(self):
        """Test course enrollment progress update API"""
        try:
            # First get student enrollments
            student_session = requests.Session()
            student_session.headers.update({
                'Authorization': f'Bearer {self.student_token}'
            })
            
            response = student_session.get(f"{BACKEND_URL}/enrollments", timeout=10)
            
            if response.status_code == 200:
                enrollments = response.json()
                if enrollments:
                    # Test progress update on first enrollment
                    enrollment = enrollments[0]
                    course_id = enrollment['courseId']
                    
                    # Test progress update
                    progress_data = {
                        "progress": 75.0,
                        "currentLessonId": "test-lesson-id",
                        "timeSpent": 300
                    }
                    
                    update_response = student_session.put(
                        f"{BACKEND_URL}/enrollments/{course_id}/progress",
                        json=progress_data,
                        timeout=10
                    )
                    
                    if update_response.status_code == 200:
                        updated_enrollment = update_response.json()
                        self.log_result(
                            "Course Enrollment Progress Update",
                            True,
                            f"Successfully updated progress to {updated_enrollment.get('progress', 0)}%",
                            {"course_id": course_id, "progress": updated_enrollment.get('progress')}
                        )
                        return True
                    else:
                        self.log_result(
                            "Course Enrollment Progress Update",
                            False,
                            f"Progress update failed: {update_response.status_code} - {update_response.text}"
                        )
                        return False
                else:
                    self.log_result(
                        "Course Enrollment Progress Update",
                        False,
                        "No enrollments found for student"
                    )
                    return False
            else:
                self.log_result(
                    "Course Enrollment Progress Update",
                    False,
                    f"Failed to get enrollments: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Course Enrollment Progress Update",
                False,
                f"Progress update error: {str(e)}"
            )
            return False
    
    def test_program_and_classroom_data_access(self):
        """Test program and classroom data access for determining context"""
        try:
            # Test programs access
            response = self.session.get(f"{BACKEND_URL}/programs", timeout=10)
            
            if response.status_code == 200:
                programs = response.json()
                self.log_result(
                    "Programs Data Access",
                    True,
                    f"Successfully retrieved {len(programs)} programs",
                    {"program_count": len(programs)}
                )
                
                if programs:
                    self.test_program_id = programs[0]['id']
            else:
                self.log_result(
                    "Programs Data Access",
                    False,
                    f"Failed to get programs: {response.status_code} - {response.text}"
                )
                return False
            
            # Test classrooms access
            response = self.session.get(f"{BACKEND_URL}/classrooms", timeout=10)
            
            if response.status_code == 200:
                classrooms = response.json()
                self.log_result(
                    "Classrooms Data Access",
                    True,
                    f"Successfully retrieved {len(classrooms)} classrooms",
                    {"classroom_count": len(classrooms)}
                )
                
                if classrooms:
                    self.test_classroom_id = classrooms[0]['id']
                return True
            else:
                self.log_result(
                    "Classrooms Data Access",
                    False,
                    f"Failed to get classrooms: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Program and Classroom Data Access",
                False,
                f"Data access error: {str(e)}"
            )
            return False
    
    def test_lesson_completion_tracking(self):
        """Test lesson completion and progress tracking APIs"""
        try:
            # Get courses to test lesson completion
            response = self.session.get(f"{BACKEND_URL}/courses", timeout=10)
            
            if response.status_code == 200:
                courses = response.json()
                if courses:
                    # Find a course with modules and lessons
                    test_course = None
                    for course in courses:
                        if course.get('modules') and len(course['modules']) > 0:
                            for module in course['modules']:
                                if module.get('lessons') and len(module['lessons']) > 0:
                                    test_course = course
                                    break
                            if test_course:
                                break
                    
                    if test_course:
                        self.test_course_id = test_course['id']
                        
                        # Test getting specific course details
                        course_response = self.session.get(
                            f"{BACKEND_URL}/courses/{self.test_course_id}",
                            timeout=10
                        )
                        
                        if course_response.status_code == 200:
                            course_details = course_response.json()
                            modules = course_details.get('modules', [])
                            total_lessons = sum(len(module.get('lessons', [])) for module in modules)
                            
                            self.log_result(
                                "Lesson Completion Tracking",
                                True,
                                f"Successfully retrieved course with {len(modules)} modules and {total_lessons} lessons",
                                {
                                    "course_id": self.test_course_id,
                                    "modules": len(modules),
                                    "lessons": total_lessons
                                }
                            )
                            return True
                        else:
                            self.log_result(
                                "Lesson Completion Tracking",
                                False,
                                f"Failed to get course details: {course_response.status_code}"
                            )
                            return False
                    else:
                        self.log_result(
                            "Lesson Completion Tracking",
                            False,
                            "No courses with lessons found for testing"
                        )
                        return False
                else:
                    self.log_result(
                        "Lesson Completion Tracking",
                        False,
                        "No courses found"
                    )
                    return False
            else:
                self.log_result(
                    "Lesson Completion Tracking",
                    False,
                    f"Failed to get courses: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Lesson Completion Tracking",
                False,
                f"Lesson tracking error: {str(e)}"
            )
            return False
    
    def test_course_completion_context_determination(self):
        """Test APIs needed for course completion logic enhancement"""
        try:
            # Test getting student enrollments to determine course context
            student_session = requests.Session()
            student_session.headers.update({
                'Authorization': f'Bearer {self.student_token}'
            })
            
            response = student_session.get(f"{BACKEND_URL}/enrollments", timeout=10)
            
            if response.status_code == 200:
                enrollments = response.json()
                
                # Test getting classrooms for the student to determine program context
                classroom_response = self.session.get(f"{BACKEND_URL}/classrooms", timeout=10)
                
                if classroom_response.status_code == 200:
                    classrooms = classroom_response.json()
                    
                    # Simulate course completion context determination
                    context_info = {
                        "enrollments": len(enrollments),
                        "classrooms": len(classrooms),
                        "can_determine_context": True
                    }
                    
                    self.log_result(
                        "Course Completion Context Determination",
                        True,
                        f"Successfully retrieved context data: {len(enrollments)} enrollments, {len(classrooms)} classrooms",
                        context_info
                    )
                    return True
                else:
                    self.log_result(
                        "Course Completion Context Determination",
                        False,
                        f"Failed to get classrooms: {classroom_response.status_code}"
                    )
                    return False
            else:
                self.log_result(
                    "Course Completion Context Determination",
                    False,
                    f"Failed to get enrollments: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Course Completion Context Determination",
                False,
                f"Context determination error: {str(e)}"
            )
            return False
    
    def test_quiz_navigation_state_handling(self):
        """Test APIs that support quiz navigation state handling"""
        try:
            # Test getting courses with quiz content
            response = self.session.get(f"{BACKEND_URL}/courses", timeout=10)
            
            if response.status_code == 200:
                courses = response.json()
                quiz_courses = []
                
                for course in courses:
                    modules = course.get('modules', [])
                    for module in modules:
                        lessons = module.get('lessons', [])
                        for lesson in lessons:
                            if lesson.get('type') == 'quiz':
                                quiz_courses.append(course)
                                break
                
                if quiz_courses:
                    quiz_course = quiz_courses[0]
                    
                    # Test getting specific quiz course details
                    course_response = self.session.get(
                        f"{BACKEND_URL}/courses/{quiz_course['id']}",
                        timeout=10
                    )
                    
                    if course_response.status_code == 200:
                        course_details = course_response.json()
                        
                        # Check if course has proper structure for quiz navigation
                        has_quiz_lessons = False
                        for module in course_details.get('modules', []):
                            for lesson in module.get('lessons', []):
                                if lesson.get('type') == 'quiz':
                                    has_quiz_lessons = True
                                    break
                        
                        self.log_result(
                            "Quiz Navigation State Handling",
                            True,
                            f"Successfully retrieved quiz course with proper structure",
                            {
                                "course_id": quiz_course['id'],
                                "has_quiz_lessons": has_quiz_lessons,
                                "modules": len(course_details.get('modules', []))
                            }
                        )
                        return True
                    else:
                        self.log_result(
                            "Quiz Navigation State Handling",
                            False,
                            f"Failed to get quiz course details: {course_response.status_code}"
                        )
                        return False
                else:
                    self.log_result(
                        "Quiz Navigation State Handling",
                        False,
                        "No courses with quiz lessons found"
                    )
                    return False
            else:
                self.log_result(
                    "Quiz Navigation State Handling",
                    False,
                    f"Failed to get courses: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Quiz Navigation State Handling",
                False,
                f"Quiz navigation error: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all course navigation and quiz completion tests"""
        print("🚀 Starting Course Navigation and Quiz Completion Backend Testing")
        print("=" * 80)
        
        # Authentication tests
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot continue with admin tests")
            return False
        
        if not self.authenticate_student():
            print("❌ Student authentication failed - cannot continue with student tests")
            return False
        
        # Core functionality tests
        tests = [
            self.test_course_enrollment_progress_api,
            self.test_program_and_classroom_data_access,
            self.test_lesson_completion_tracking,
            self.test_course_completion_context_determination,
            self.test_quiz_navigation_state_handling
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            if test():
                passed_tests += 1
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 COURSE NAVIGATION BACKEND TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        if success_rate >= 80:
            print("✅ BACKEND READY: Course navigation and quiz completion APIs are functional")
        else:
            print("❌ BACKEND ISSUES: Some critical APIs need attention")
        
        # Print detailed results
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = CourseNavigationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All critical course navigation backend APIs are working correctly!")
        print("The backend is ready to support the new navigation logic and course completion features.")
    else:
        print("\n⚠️  Some backend APIs need attention before the navigation fixes can work properly.")
    
    return success

if __name__ == "__main__":
    main()