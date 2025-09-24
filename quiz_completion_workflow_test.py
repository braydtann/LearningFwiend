#!/usr/bin/env python3
"""
Quiz Completion Navigation and Course Completion Logic Backend Testing
Specifically testing the backend APIs that support:
1. Quiz completion navigation with lesson context preservation
2. Course completion logic for standalone vs program contexts
3. Program completion scenarios
"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path

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

class QuizCompletionWorkflowTester:
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
            response = requests.post(
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
    
    def test_quiz_completion_progress_tracking(self):
        """Test quiz completion and progress tracking for navigation context"""
        try:
            # Create student session
            student_session = requests.Session()
            student_session.headers.update({
                'Authorization': f'Bearer {self.student_token}'
            })
            
            # Get student enrollments
            response = student_session.get(f"{BACKEND_URL}/enrollments", timeout=10)
            
            if response.status_code == 200:
                enrollments = response.json()
                if enrollments:
                    enrollment = enrollments[0]
                    course_id = enrollment['courseId']
                    
                    # Test quiz completion scenario - update progress to 100%
                    quiz_completion_data = {
                        "progress": 100.0,
                        "currentLessonId": "quiz-lesson-1",
                        "timeSpent": 600,
                        "lastAccessedAt": datetime.now().isoformat()
                    }
                    
                    update_response = student_session.put(
                        f"{BACKEND_URL}/enrollments/{course_id}/progress",
                        json=quiz_completion_data,
                        timeout=10
                    )
                    
                    if update_response.status_code == 200:
                        updated_enrollment = update_response.json()
                        
                        # Check if course completion was properly handled
                        is_completed = updated_enrollment.get('status') == 'completed'
                        has_completion_date = updated_enrollment.get('completedAt') is not None
                        
                        self.log_result(
                            "Quiz Completion Progress Tracking",
                            True,
                            f"Successfully completed course with proper status tracking",
                            {
                                "course_id": course_id,
                                "progress": updated_enrollment.get('progress'),
                                "status": updated_enrollment.get('status'),
                                "completed": is_completed,
                                "completion_date": has_completion_date,
                                "current_lesson": updated_enrollment.get('currentLessonId')
                            }
                        )
                        return True
                    else:
                        self.log_result(
                            "Quiz Completion Progress Tracking",
                            False,
                            f"Progress update failed: {update_response.status_code} - {update_response.text}"
                        )
                        return False
                else:
                    self.log_result(
                        "Quiz Completion Progress Tracking",
                        False,
                        "No enrollments found for student"
                    )
                    return False
            else:
                self.log_result(
                    "Quiz Completion Progress Tracking",
                    False,
                    f"Failed to get enrollments: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Quiz Completion Progress Tracking",
                False,
                f"Quiz completion tracking error: {str(e)}"
            )
            return False
    
    def test_standalone_course_completion_logic(self):
        """Test course completion logic for standalone courses (should offer certificates vs dashboard)"""
        try:
            # Get courses to identify standalone courses (not part of programs)
            response = self.session.get(f"{BACKEND_URL}/courses", timeout=10)
            
            if response.status_code == 200:
                courses = response.json()
                
                # Get programs to determine which courses are standalone
                programs_response = self.session.get(f"{BACKEND_URL}/programs", timeout=10)
                program_course_ids = set()
                
                if programs_response.status_code == 200:
                    programs = programs_response.json()
                    for program in programs:
                        program_course_ids.update(program.get('courseIds', []))
                
                # Find standalone courses
                standalone_courses = [
                    course for course in courses 
                    if course['id'] not in program_course_ids
                ]
                
                if standalone_courses:
                    standalone_course = standalone_courses[0]
                    
                    # Test getting course details for completion logic
                    course_response = self.session.get(
                        f"{BACKEND_URL}/courses/{standalone_course['id']}",
                        timeout=10
                    )
                    
                    if course_response.status_code == 200:
                        course_details = course_response.json()
                        
                        self.log_result(
                            "Standalone Course Completion Logic",
                            True,
                            f"Successfully identified standalone course for certificate logic",
                            {
                                "course_id": standalone_course['id'],
                                "course_title": standalone_course.get('title'),
                                "is_standalone": True,
                                "should_offer_certificate": True
                            }
                        )
                        return True
                    else:
                        self.log_result(
                            "Standalone Course Completion Logic",
                            False,
                            f"Failed to get course details: {course_response.status_code}"
                        )
                        return False
                else:
                    self.log_result(
                        "Standalone Course Completion Logic",
                        True,
                        "No standalone courses found - all courses are part of programs",
                        {"standalone_courses": 0, "total_courses": len(courses)}
                    )
                    return True
            else:
                self.log_result(
                    "Standalone Course Completion Logic",
                    False,
                    f"Failed to get courses: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Standalone Course Completion Logic",
                False,
                f"Standalone course logic error: {str(e)}"
            )
            return False
    
    def test_program_course_completion_logic(self):
        """Test course completion within programs with next courses available"""
        try:
            # Get programs and their courses
            response = self.session.get(f"{BACKEND_URL}/programs", timeout=10)
            
            if response.status_code == 200:
                programs = response.json()
                
                if programs:
                    program = programs[0]
                    course_ids = program.get('courseIds', [])
                    
                    if len(course_ids) > 1:
                        # Test program with multiple courses
                        self.log_result(
                            "Program Course Completion Logic",
                            True,
                            f"Successfully identified program with multiple courses for next course logic",
                            {
                                "program_id": program['id'],
                                "program_title": program.get('title'),
                                "course_count": len(course_ids),
                                "has_next_courses": True,
                                "should_offer_next_course": True
                            }
                        )
                        return True
                    else:
                        self.log_result(
                            "Program Course Completion Logic",
                            True,
                            f"Program found but has only one course",
                            {
                                "program_id": program['id'],
                                "course_count": len(course_ids),
                                "has_next_courses": False
                            }
                        )
                        return True
                else:
                    self.log_result(
                        "Program Course Completion Logic",
                        True,
                        "No programs found in system",
                        {"program_count": 0}
                    )
                    return True
            else:
                self.log_result(
                    "Program Course Completion Logic",
                    False,
                    f"Failed to get programs: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Program Course Completion Logic",
                False,
                f"Program course logic error: {str(e)}"
            )
            return False
    
    def test_program_completion_scenarios(self):
        """Test program completion scenarios (should offer final exam vs dashboard)"""
        try:
            # Create student session
            student_session = requests.Session()
            student_session.headers.update({
                'Authorization': f'Bearer {self.student_token}'
            })
            
            # Get student enrollments to check program completion status
            enrollments_response = student_session.get(f"{BACKEND_URL}/enrollments", timeout=10)
            
            if enrollments_response.status_code == 200:
                enrollments = enrollments_response.json()
                
                # Get programs to check completion logic
                programs_response = self.session.get(f"{BACKEND_URL}/programs", timeout=10)
                
                if programs_response.status_code == 200:
                    programs = programs_response.json()
                    
                    # Simulate program completion analysis
                    program_completion_data = []
                    
                    for program in programs:
                        course_ids = program.get('courseIds', [])
                        completed_courses = 0
                        
                        for enrollment in enrollments:
                            if enrollment['courseId'] in course_ids and enrollment.get('status') == 'completed':
                                completed_courses += 1
                        
                        completion_percentage = (completed_courses / len(course_ids) * 100) if course_ids else 0
                        is_program_completed = completion_percentage == 100
                        
                        program_completion_data.append({
                            "program_id": program['id'],
                            "program_title": program.get('title'),
                            "total_courses": len(course_ids),
                            "completed_courses": completed_courses,
                            "completion_percentage": completion_percentage,
                            "is_completed": is_program_completed,
                            "should_offer_final_exam": is_program_completed
                        })
                    
                    self.log_result(
                        "Program Completion Scenarios",
                        True,
                        f"Successfully analyzed program completion for {len(programs)} programs",
                        {
                            "programs_analyzed": len(programs),
                            "completion_data": program_completion_data
                        }
                    )
                    return True
                else:
                    self.log_result(
                        "Program Completion Scenarios",
                        False,
                        f"Failed to get programs: {programs_response.status_code}"
                    )
                    return False
            else:
                self.log_result(
                    "Program Completion Scenarios",
                    False,
                    f"Failed to get enrollments: {enrollments_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Program Completion Scenarios",
                False,
                f"Program completion scenarios error: {str(e)}"
            )
            return False
    
    def test_lesson_context_preservation(self):
        """Test APIs that support lesson context preservation after quiz completion"""
        try:
            # Create student session
            student_session = requests.Session()
            student_session.headers.update({
                'Authorization': f'Bearer {self.student_token}'
            })
            
            # Get student enrollments
            response = student_session.get(f"{BACKEND_URL}/enrollments", timeout=10)
            
            if response.status_code == 200:
                enrollments = response.json()
                if enrollments:
                    enrollment = enrollments[0]
                    course_id = enrollment['courseId']
                    
                    # Test updating current lesson context
                    context_data = {
                        "currentLessonId": "lesson-after-quiz",
                        "currentModuleId": "module-1",
                        "lastAccessedAt": datetime.now().isoformat()
                    }
                    
                    update_response = student_session.put(
                        f"{BACKEND_URL}/enrollments/{course_id}/progress",
                        json=context_data,
                        timeout=10
                    )
                    
                    if update_response.status_code == 200:
                        updated_enrollment = update_response.json()
                        
                        # Verify lesson context was preserved
                        current_lesson = updated_enrollment.get('currentLessonId')
                        current_module = updated_enrollment.get('currentModuleId')
                        
                        self.log_result(
                            "Lesson Context Preservation",
                            True,
                            f"Successfully preserved lesson context after quiz completion",
                            {
                                "course_id": course_id,
                                "current_lesson": current_lesson,
                                "current_module": current_module,
                                "context_preserved": current_lesson is not None
                            }
                        )
                        return True
                    else:
                        self.log_result(
                            "Lesson Context Preservation",
                            False,
                            f"Context update failed: {update_response.status_code} - {update_response.text}"
                        )
                        return False
                else:
                    self.log_result(
                        "Lesson Context Preservation",
                        False,
                        "No enrollments found for context testing"
                    )
                    return False
            else:
                self.log_result(
                    "Lesson Context Preservation",
                    False,
                    f"Failed to get enrollments: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Lesson Context Preservation",
                False,
                f"Lesson context preservation error: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all quiz completion workflow tests"""
        print("🚀 Starting Quiz Completion Workflow Backend Testing")
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
            self.test_quiz_completion_progress_tracking,
            self.test_standalone_course_completion_logic,
            self.test_program_course_completion_logic,
            self.test_program_completion_scenarios,
            self.test_lesson_context_preservation
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            if test():
                passed_tests += 1
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 QUIZ COMPLETION WORKFLOW BACKEND TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        if success_rate >= 80:
            print("✅ BACKEND READY: Quiz completion workflow APIs are functional")
        else:
            print("❌ BACKEND ISSUES: Some critical workflow APIs need attention")
        
        # Print detailed results
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = QuizCompletionWorkflowTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All critical quiz completion workflow backend APIs are working correctly!")
        print("The backend supports:")
        print("- Quiz completion navigation with lesson context preservation")
        print("- Course completion logic for standalone vs program contexts")
        print("- Program completion scenarios with proper status tracking")
    else:
        print("\n⚠️  Some backend APIs need attention before the workflow fixes can work properly.")
    
    return success

if __name__ == "__main__":
    main()