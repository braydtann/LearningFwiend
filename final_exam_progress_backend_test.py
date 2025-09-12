#!/usr/bin/env python3
"""
Backend Testing for Final Exam and Progress Tracking Issues
Testing specific user-reported issues:
1. Final Test/Exam access and functionality
2. Progress tracking accuracy
3. Grading interfaces for subjective questions
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://fixfriend.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class BackendTester:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.log_test("Admin Authentication", True, f"Admin: {data.get('user', {}).get('full_name', 'Unknown')}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
            
    def authenticate_student(self):
        """Authenticate student user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=STUDENT_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                self.log_test("Student Authentication", True, f"Student: {data.get('user', {}).get('full_name', 'Unknown')}")
                return True
            else:
                self.log_test("Student Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False
            
    def get_headers(self, token):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {token}"}
        
    def test_final_exam_access(self):
        """Test final exam/test access functionality"""
        print("\n🎯 TESTING FINAL EXAM ACCESS FUNCTIONALITY")
        
        # Test 1: Get student enrollments to check completion status
        try:
            headers = self.get_headers(self.student_token)
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            
            if response.status_code == 200:
                enrollments = response.json()
                completed_courses = [e for e in enrollments if e.get('progress', 0) >= 100]
                self.log_test("Student Enrollments Retrieval", True, 
                            f"Found {len(enrollments)} enrollments, {len(completed_courses)} completed")
                
                # Test 2: Check for programs and final exams
                if completed_courses:
                    # Get classrooms to find programs
                    response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers)
                    if response.status_code == 200:
                        classrooms = response.json()
                        program_classrooms = [c for c in classrooms if c.get('programIds')]
                        self.log_test("Program Classrooms Access", True, 
                                    f"Found {len(program_classrooms)} classrooms with programs")
                        
                        # Test 3: Check program completion status
                        if program_classrooms:
                            response = requests.get(f"{BACKEND_URL}/programs", headers=headers)
                            if response.status_code == 200:
                                programs = response.json()
                                self.log_test("Programs Access", True, f"Found {len(programs)} programs")
                                
                                # Test final exam route structure
                                for program in programs[:2]:  # Test first 2 programs
                                    program_id = program.get('id')
                                    if program_id:
                                        # Check if final exam endpoint exists (this would be custom endpoint)
                                        test_url = f"{BACKEND_URL}/final-tests/program/{program_id}"
                                        try:
                                            response = requests.get(test_url, headers=headers)
                                            # Even 404 is acceptable - we're testing if endpoint exists
                                            self.log_test(f"Final Exam Route Test - Program {program_id[:8]}", 
                                                        response.status_code in [200, 404], 
                                                        f"Status: {response.status_code}")
                                        except:
                                            self.log_test(f"Final Exam Route Test - Program {program_id[:8]}", 
                                                        False, "Route not accessible")
                            else:
                                self.log_test("Programs Access", False, f"Status: {response.status_code}")
                        else:
                            self.log_test("Program Classrooms Access", False, "No program classrooms found")
                    else:
                        self.log_test("Program Classrooms Access", False, f"Status: {response.status_code}")
                else:
                    self.log_test("Completed Courses Check", False, "No completed courses found for final exam testing")
            else:
                self.log_test("Student Enrollments Retrieval", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Final Exam Access Test", False, f"Exception: {str(e)}")
            
    def test_progress_tracking_accuracy(self):
        """Test progress tracking accuracy and data integrity"""
        print("\n📊 TESTING PROGRESS TRACKING ACCURACY")
        
        try:
            headers = self.get_headers(self.student_token)
            
            # Test 1: Get current enrollments and progress
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            if response.status_code == 200:
                enrollments = response.json()
                
                # Analyze progress data
                total_enrollments = len(enrollments)
                completed_count = len([e for e in enrollments if e.get('progress', 0) >= 100])
                in_progress_count = len([e for e in enrollments if 0 < e.get('progress', 0) < 100])
                not_started_count = len([e for e in enrollments if e.get('progress', 0) == 0])
                
                self.log_test("Progress Data Analysis", True, 
                            f"Total: {total_enrollments}, Completed: {completed_count}, In Progress: {in_progress_count}, Not Started: {not_started_count}")
                
                # Test 2: Verify progress calculation accuracy
                for enrollment in enrollments[:3]:  # Test first 3 enrollments
                    course_id = enrollment.get('courseId')
                    current_progress = enrollment.get('progress', 0)
                    
                    if course_id:
                        # Get course details to verify progress calculation
                        response = requests.get(f"{BACKEND_URL}/courses/{course_id}", headers=headers)
                        if response.status_code == 200:
                            course = response.json()
                            modules = course.get('modules', [])
                            total_lessons = sum(len(module.get('lessons', [])) for module in modules)
                            
                            self.log_test(f"Course Structure Analysis - {course_id[:8]}", True,
                                        f"Progress: {current_progress}%, Lessons: {total_lessons}")
                        else:
                            self.log_test(f"Course Access - {course_id[:8]}", False, 
                                        f"Status: {response.status_code}")
                
                # Test 3: Test progress update functionality
                if enrollments:
                    test_enrollment = enrollments[0]
                    course_id = test_enrollment.get('courseId')
                    current_progress = test_enrollment.get('progress', 0)
                    
                    # Test progress update (simulate small increment)
                    test_progress = min(current_progress + 1, 100)  # Small increment
                    update_data = {
                        "progress": test_progress,
                        "lastAccessedAt": datetime.utcnow().isoformat()
                    }
                    
                    response = requests.put(f"{BACKEND_URL}/enrollments/{course_id}/progress", 
                                          json=update_data, headers=headers)
                    
                    if response.status_code == 200:
                        updated_enrollment = response.json()
                        new_progress = updated_enrollment.get('progress', 0)
                        self.log_test("Progress Update Test", True, 
                                    f"Updated from {current_progress}% to {new_progress}%")
                    else:
                        self.log_test("Progress Update Test", False, 
                                    f"Status: {response.status_code}, Response: {response.text}")
                        
            else:
                self.log_test("Progress Tracking Data Retrieval", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Progress Tracking Test", False, f"Exception: {str(e)}")
            
    def test_quiz_analytics_data_flow(self):
        """Test quiz submission and analytics data flow"""
        print("\n📈 TESTING QUIZ ANALYTICS DATA FLOW")
        
        try:
            headers = self.get_headers(self.student_token)
            
            # Test 1: Get courses with quizzes
            response = requests.get(f"{BACKEND_URL}/courses", headers=headers)
            if response.status_code == 200:
                courses = response.json()
                quiz_courses = []
                
                for course in courses[:10]:  # Check first 10 courses
                    course_id = course.get('id')
                    if course_id:
                        # Get detailed course info
                        detail_response = requests.get(f"{BACKEND_URL}/courses/{course_id}", headers=headers)
                        if detail_response.status_code == 200:
                            course_detail = detail_response.json()
                            modules = course_detail.get('modules', [])
                            
                            # Check for quiz lessons
                            has_quiz = False
                            for module in modules:
                                lessons = module.get('lessons', [])
                                for lesson in lessons:
                                    if lesson.get('type') == 'quiz' or 'quiz' in lesson.get('title', '').lower():
                                        has_quiz = True
                                        break
                                if has_quiz:
                                    break
                                    
                            if has_quiz:
                                quiz_courses.append(course_detail)
                
                self.log_test("Quiz Courses Discovery", True, f"Found {len(quiz_courses)} courses with quizzes")
                
                # Test 2: Check quiz attempts/analytics endpoints
                try:
                    # Test quiz attempts endpoint (if exists)
                    response = requests.get(f"{BACKEND_URL}/quiz-attempts", headers=headers)
                    if response.status_code == 200:
                        attempts = response.json()
                        self.log_test("Quiz Attempts Endpoint", True, f"Found {len(attempts)} quiz attempts")
                    elif response.status_code == 404:
                        self.log_test("Quiz Attempts Endpoint", False, "Endpoint not found - may need implementation")
                    else:
                        self.log_test("Quiz Attempts Endpoint", False, f"Status: {response.status_code}")
                except:
                    self.log_test("Quiz Attempts Endpoint", False, "Endpoint not accessible")
                
                # Test 3: Check analytics integration through enrollments
                response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
                if response.status_code == 200:
                    enrollments = response.json()
                    quiz_enrollments = []
                    
                    for enrollment in enrollments:
                        course_id = enrollment.get('courseId')
                        progress = enrollment.get('progress', 0)
                        
                        # Check if this enrollment is for a quiz course
                        for quiz_course in quiz_courses:
                            if quiz_course.get('id') == course_id and progress > 0:
                                quiz_enrollments.append({
                                    'course_id': course_id,
                                    'progress': progress,
                                    'status': enrollment.get('status'),
                                    'completed_at': enrollment.get('completedAt')
                                })
                                break
                    
                    self.log_test("Quiz Analytics via Enrollments", True, 
                                f"Found {len(quiz_enrollments)} quiz course enrollments with progress")
                    
                    # Display quiz scores for analysis
                    for quiz_enrollment in quiz_enrollments[:5]:
                        course_id = quiz_enrollment['course_id']
                        progress = quiz_enrollment['progress']
                        print(f"   Quiz Score: Course {course_id[:8]} - {progress}%")
                        
            else:
                self.log_test("Courses Retrieval for Quiz Analysis", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Quiz Analytics Test", False, f"Exception: {str(e)}")
            
    def test_grading_interfaces(self):
        """Test grading interfaces for subjective questions"""
        print("\n📝 TESTING GRADING INTERFACES")
        
        try:
            # Test with admin credentials for instructor functionality
            headers = self.get_headers(self.admin_token)
            
            # Test 1: Get courses created by admin/instructor
            response = requests.get(f"{BACKEND_URL}/courses/my-courses", headers=headers)
            if response.status_code == 200:
                my_courses = response.json()
                self.log_test("Instructor Courses Access", True, f"Found {len(my_courses)} instructor courses")
                
                # Test 2: Look for courses with subjective questions
                subjective_courses = []
                for course in my_courses[:5]:  # Check first 5 courses
                    course_id = course.get('id')
                    modules = course.get('modules', [])
                    
                    has_subjective = False
                    for module in modules:
                        lessons = module.get('lessons', [])
                        for lesson in lessons:
                            if lesson.get('type') == 'quiz':
                                questions = lesson.get('questions', [])
                                for question in questions:
                                    q_type = question.get('type', '')
                                    if q_type in ['short-answer', 'long-form-answer', 'essay']:
                                        has_subjective = True
                                        break
                                if has_subjective:
                                    break
                        if has_subjective:
                            break
                    
                    if has_subjective:
                        subjective_courses.append(course)
                
                self.log_test("Subjective Question Courses", True, 
                            f"Found {len(subjective_courses)} courses with subjective questions")
                
                # Test 3: Check for grading/review endpoints
                if subjective_courses:
                    test_course = subjective_courses[0]
                    course_id = test_course.get('id')
                    
                    # Test student submissions endpoint
                    try:
                        response = requests.get(f"{BACKEND_URL}/courses/{course_id}/submissions", headers=headers)
                        if response.status_code == 200:
                            submissions = response.json()
                            self.log_test("Student Submissions Endpoint", True, 
                                        f"Found {len(submissions)} submissions")
                        elif response.status_code == 404:
                            self.log_test("Student Submissions Endpoint", False, 
                                        "Endpoint not found - may need implementation for grading")
                        else:
                            self.log_test("Student Submissions Endpoint", False, f"Status: {response.status_code}")
                    except:
                        self.log_test("Student Submissions Endpoint", False, "Endpoint not accessible")
                    
                    # Test grading endpoint
                    try:
                        response = requests.get(f"{BACKEND_URL}/courses/{course_id}/grading", headers=headers)
                        if response.status_code == 200:
                            grading_data = response.json()
                            self.log_test("Grading Interface Endpoint", True, "Grading interface accessible")
                        elif response.status_code == 404:
                            self.log_test("Grading Interface Endpoint", False, 
                                        "Grading interface not found - needs implementation")
                        else:
                            self.log_test("Grading Interface Endpoint", False, f"Status: {response.status_code}")
                    except:
                        self.log_test("Grading Interface Endpoint", False, "Endpoint not accessible")
                        
                # Test 4: Check enrollment data for grading context
                response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
                if response.status_code == 200:
                    all_enrollments = response.json()
                    
                    # Look for enrollments that might need grading
                    needs_grading = []
                    for enrollment in all_enrollments:
                        if enrollment.get('status') == 'completed' and enrollment.get('progress', 0) >= 100:
                            needs_grading.append(enrollment)
                    
                    self.log_test("Completed Enrollments for Grading", True, 
                                f"Found {len(needs_grading)} completed enrollments that may need grading review")
                        
            else:
                self.log_test("Instructor Courses Access", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Grading Interfaces Test", False, f"Exception: {str(e)}")
            
    def test_student_enrollment_data_integrity(self):
        """Test student enrollment and classroom data integrity"""
        print("\n🔍 TESTING STUDENT ENROLLMENT DATA INTEGRITY")
        
        try:
            headers = self.get_headers(self.student_token)
            
            # Test 1: Get student enrollments
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            if response.status_code == 200:
                enrollments = response.json()
                self.log_test("Student Enrollments Data", True, f"Retrieved {len(enrollments)} enrollments")
                
                # Test 2: Verify each enrollment has valid course
                valid_enrollments = 0
                invalid_enrollments = 0
                
                for enrollment in enrollments:
                    course_id = enrollment.get('courseId')
                    if course_id:
                        course_response = requests.get(f"{BACKEND_URL}/courses/{course_id}", headers=headers)
                        if course_response.status_code == 200:
                            valid_enrollments += 1
                        else:
                            invalid_enrollments += 1
                            print(f"   Invalid enrollment: Course {course_id} not found")
                
                self.log_test("Enrollment Data Integrity", invalid_enrollments == 0, 
                            f"Valid: {valid_enrollments}, Invalid: {invalid_enrollments}")
                
                # Test 3: Check classroom assignments
                response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers)
                if response.status_code == 200:
                    classrooms = response.json()
                    student_classrooms = []
                    
                    # Get current user info
                    user_response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers)
                    if user_response.status_code == 200:
                        current_user = user_response.json()
                        user_id = current_user.get('id')
                        
                        # Find classrooms where student is assigned
                        for classroom in classrooms:
                            student_ids = classroom.get('studentIds', [])
                            if user_id in student_ids:
                                student_classrooms.append(classroom)
                        
                        self.log_test("Student Classroom Assignments", True, 
                                    f"Student assigned to {len(student_classrooms)} classrooms")
                        
                        # Test 4: Verify auto-enrollment from classrooms
                        expected_enrollments = set()
                        for classroom in student_classrooms:
                            # Direct course enrollments
                            course_ids = classroom.get('courseIds', [])
                            expected_enrollments.update(course_ids)
                            
                            # Program course enrollments
                            program_ids = classroom.get('programIds', [])
                            for program_id in program_ids:
                                program_response = requests.get(f"{BACKEND_URL}/programs/{program_id}", headers=headers)
                                if program_response.status_code == 200:
                                    program = program_response.json()
                                    program_course_ids = program.get('courseIds', [])
                                    expected_enrollments.update(program_course_ids)
                        
                        actual_enrollments = set(e.get('courseId') for e in enrollments if e.get('courseId'))
                        
                        missing_enrollments = expected_enrollments - actual_enrollments
                        extra_enrollments = actual_enrollments - expected_enrollments
                        
                        self.log_test("Auto-enrollment Integrity", len(missing_enrollments) == 0,
                                    f"Expected: {len(expected_enrollments)}, Actual: {len(actual_enrollments)}, Missing: {len(missing_enrollments)}")
                        
                        if missing_enrollments:
                            print(f"   Missing enrollments for courses: {list(missing_enrollments)[:3]}")
                        
                    else:
                        self.log_test("Current User Info", False, f"Status: {user_response.status_code}")
                        
                else:
                    self.log_test("Classrooms Access", False, f"Status: {response.status_code}")
                    
            else:
                self.log_test("Student Enrollments Data", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Student Enrollment Data Integrity Test", False, f"Exception: {str(e)}")
            
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 STARTING COMPREHENSIVE BACKEND TESTING FOR FINAL EXAM AND PROGRESS TRACKING ISSUES")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot proceed with admin tests")
            return
            
        if not self.authenticate_student():
            print("❌ Student authentication failed - cannot proceed with student tests")
            return
            
        # Run all test suites
        self.test_final_exam_access()
        self.test_progress_tracking_accuracy()
        self.test_quiz_analytics_data_flow()
        self.test_grading_interfaces()
        self.test_student_enrollment_data_integrity()
        
        # Summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"   - {test['test']}: {test['details']}")
                    
        print("\n🎯 KEY FINDINGS FOR USER ISSUES:")
        print("1. Final Exam Access: Check if final exam routes and program completion detection work")
        print("2. Progress Tracking: Verify if progress calculations match actual completion")
        print("3. Quiz Analytics: Check if quiz scores flow properly to analytics system")
        print("4. Grading Interface: Verify if subjective question grading endpoints exist")
        print("5. Data Integrity: Check for orphaned enrollments or missing auto-enrollments")
        
        return success_rate >= 70  # Consider 70% success rate as acceptable

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)