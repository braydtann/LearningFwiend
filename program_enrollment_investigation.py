#!/usr/bin/env python3
"""
Program Enrollment Investigation - Backend Testing
Investigating specific issue where student cannot see newly created program despite admin assignment.

ISSUE CONTEXT:
- Admin created program "test course 4" 
- Admin created final exam for this program
- Admin attached existing courses to the program
- Admin assigned it in classroom creator for class "test program 4" with batch ID "tc4"
- Student (brayden.student@covesmart.com) only sees "test3" in enrolled programs, not the new "test course 4"
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "brayden.student@covesmart.com", 
    "password": "Cove1234!"
}

class ProgramEnrollmentInvestigator:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.results = []
        self.test_program_id = None
        self.test_classroom_id = None
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_admin(self):
        """Test admin authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                user_info = data.get('user', {})
                
                if user_info.get('role') == 'admin':
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Authenticated as {user_info.get('full_name')} ({user_info.get('email')})"
                    )
                    return True
                else:
                    self.log_result("Admin Authentication", False, f"User role is {user_info.get('role')}, expected admin")
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def authenticate_student(self):
        """Test student authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get('access_token')
                user_info = data.get('user', {})
                
                if user_info.get('role') == 'learner':
                    self.log_result(
                        "Student Authentication", 
                        True, 
                        f"Authenticated as {user_info.get('full_name')} ({user_info.get('email')})"
                    )
                    return True
                else:
                    self.log_result("Student Authentication", False, f"User role is {user_info.get('role')}, expected learner")
                    return False
            else:
                self.log_result("Student Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Student Authentication", False, f"Exception: {str(e)}")
            return False

    def find_test_course_4_program(self):
        """Find the 'test course 4' program mentioned in the issue"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(f"{BACKEND_URL}/programs", headers=headers, timeout=10)
            
            if response.status_code == 200:
                programs = response.json()
                
                # Look for "test course 4" program
                test_program = None
                for program in programs:
                    if "test course 4" in program.get('title', '').lower():
                        test_program = program
                        self.test_program_id = program['id']
                        break
                
                if test_program:
                    self.log_result(
                        "Find 'test course 4' Program", 
                        True, 
                        f"Found program: {test_program['title']} (ID: {test_program['id']}, Active: {test_program.get('isActive')}, Courses: {len(test_program.get('courseIds', []))})"
                    )
                    return True
                else:
                    # List all programs for debugging
                    program_titles = [p.get('title', 'No Title') for p in programs]
                    self.log_result(
                        "Find 'test course 4' Program", 
                        False, 
                        f"Program not found. Available programs: {program_titles}"
                    )
                    return False
            else:
                self.log_result("Find 'test course 4' Program", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Find 'test course 4' Program", False, f"Exception: {str(e)}")
            return False

    def find_test_program_4_classroom(self):
        """Find the 'test program 4' classroom with batch ID 'tc4'"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers, timeout=10)
            
            if response.status_code == 200:
                classrooms = response.json()
                
                # Look for "test program 4" classroom with batch ID "tc4"
                test_classroom = None
                for classroom in classrooms:
                    classroom_name = classroom.get('name', '').lower()
                    batch_id = classroom.get('batchId', '').lower()
                    
                    if ("test program 4" in classroom_name) or (batch_id == "tc4"):
                        test_classroom = classroom
                        self.test_classroom_id = classroom['id']
                        break
                
                if test_classroom:
                    student_count = len(test_classroom.get('studentIds', []))
                    program_count = len(test_classroom.get('programIds', []))
                    course_count = len(test_classroom.get('courseIds', []))
                    
                    self.log_result(
                        "Find 'test program 4' Classroom", 
                        True, 
                        f"Found classroom: {test_classroom['name']} (Batch: {test_classroom.get('batchId')}, Students: {student_count}, Programs: {program_count}, Courses: {course_count})"
                    )
                    return True
                else:
                    # List all classrooms for debugging
                    classroom_info = []
                    for c in classrooms:
                        classroom_info.append(f"{c.get('name', 'No Name')} (Batch: {c.get('batchId', 'No Batch')})")
                    
                    self.log_result(
                        "Find 'test program 4' Classroom", 
                        False, 
                        f"Classroom not found. Available classrooms: {classroom_info}"
                    )
                    return False
            else:
                self.log_result("Find 'test program 4' Classroom", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Find 'test program 4' Classroom", False, f"Exception: {str(e)}")
            return False

    def verify_student_in_classroom(self):
        """Verify if brayden.student@covesmart.com is assigned to the test classroom"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            if not self.test_classroom_id:
                self.log_result("Verify Student in Classroom", False, "No test classroom ID available")
                return False
            
            # Get classroom details
            response = requests.get(f"{BACKEND_URL}/classrooms/{self.test_classroom_id}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                classroom = response.json()
                student_ids = classroom.get('studentIds', [])
                
                # Get student user ID
                student_response = requests.get(f"{BACKEND_URL}/auth/admin/users", headers=headers, timeout=10)
                
                if student_response.status_code == 200:
                    users = student_response.json()
                    student_user = None
                    
                    for user in users:
                        if user.get('email') == 'brayden.student@covesmart.com':
                            student_user = user
                            break
                    
                    if student_user:
                        student_id = student_user['id']
                        is_assigned = student_id in student_ids
                        
                        self.log_result(
                            "Verify Student in Classroom", 
                            is_assigned, 
                            f"Student {student_user['email']} (ID: {student_id}) {'IS' if is_assigned else 'IS NOT'} assigned to classroom. Total students in classroom: {len(student_ids)}"
                        )
                        return is_assigned
                    else:
                        self.log_result("Verify Student in Classroom", False, "Student user not found in system")
                        return False
                else:
                    self.log_result("Verify Student in Classroom", False, f"Could not get users: HTTP {student_response.status_code}")
                    return False
            else:
                self.log_result("Verify Student in Classroom", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Verify Student in Classroom", False, f"Exception: {str(e)}")
            return False

    def verify_program_in_classroom(self):
        """Verify if the 'test course 4' program is associated with the classroom"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            if not self.test_classroom_id or not self.test_program_id:
                self.log_result("Verify Program in Classroom", False, "Missing classroom or program ID")
                return False
            
            # Get classroom details
            response = requests.get(f"{BACKEND_URL}/classrooms/{self.test_classroom_id}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                classroom = response.json()
                program_ids = classroom.get('programIds', [])
                
                is_associated = self.test_program_id in program_ids
                
                self.log_result(
                    "Verify Program in Classroom", 
                    is_associated, 
                    f"Program 'test course 4' (ID: {self.test_program_id}) {'IS' if is_associated else 'IS NOT'} associated with classroom. Total programs in classroom: {len(program_ids)}"
                )
                return is_associated
            else:
                self.log_result("Verify Program in Classroom", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Verify Program in Classroom", False, f"Exception: {str(e)}")
            return False

    def test_student_enrollments(self):
        """Test what enrollments the student can see"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers, timeout=10)
            
            if response.status_code == 200:
                enrollments = response.json()
                
                # Get course details for each enrollment
                course_names = []
                for enrollment in enrollments:
                    course_id = enrollment.get('courseId')
                    if course_id:
                        course_response = requests.get(f"{BACKEND_URL}/courses/{course_id}", headers=headers, timeout=10)
                        if course_response.status_code == 200:
                            course = course_response.json()
                            course_names.append(course.get('title', 'Unknown Course'))
                
                has_test3 = any('test3' in name.lower() for name in course_names)
                has_test_course_4 = any('test course 4' in name.lower() for name in course_names)
                
                self.log_result(
                    "Test Student Enrollments", 
                    True, 
                    f"Student has {len(enrollments)} enrollments. Courses: {course_names}. Has 'test3': {has_test3}, Has 'test course 4': {has_test_course_4}"
                )
                return True
            else:
                self.log_result("Test Student Enrollments", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Test Student Enrollments", False, f"Exception: {str(e)}")
            return False

    def test_student_classrooms(self):
        """Test what classrooms the student is assigned to"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get all classrooms and check which ones include our student
            response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers, timeout=10)
            
            if response.status_code == 200:
                classrooms = response.json()
                
                # Get student user ID first
                student_response = requests.get(f"{BACKEND_URL}/auth/admin/users", headers=headers, timeout=10)
                
                if student_response.status_code == 200:
                    users = student_response.json()
                    student_user = None
                    
                    for user in users:
                        if user.get('email') == 'brayden.student@covesmart.com':
                            student_user = user
                            break
                    
                    if student_user:
                        student_id = student_user['id']
                        student_classrooms = []
                        
                        for classroom in classrooms:
                            if student_id in classroom.get('studentIds', []):
                                student_classrooms.append({
                                    'name': classroom.get('name'),
                                    'batchId': classroom.get('batchId'),
                                    'programCount': len(classroom.get('programIds', [])),
                                    'courseCount': len(classroom.get('courseIds', []))
                                })
                        
                        self.log_result(
                            "Test Student Classrooms", 
                            True, 
                            f"Student is assigned to {len(student_classrooms)} classrooms: {student_classrooms}"
                        )
                        return True
                    else:
                        self.log_result("Test Student Classrooms", False, "Student user not found")
                        return False
                else:
                    self.log_result("Test Student Classrooms", False, f"Could not get users: HTTP {student_response.status_code}")
                    return False
            else:
                self.log_result("Test Student Classrooms", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Test Student Classrooms", False, f"Exception: {str(e)}")
            return False

    def test_auto_enrollment_logic(self):
        """Test if auto-enrollment from classroom to program courses is working"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            if not self.test_classroom_id or not self.test_program_id:
                self.log_result("Test Auto-Enrollment Logic", False, "Missing classroom or program ID")
                return False
            
            # Get classroom details
            classroom_response = requests.get(f"{BACKEND_URL}/classrooms/{self.test_classroom_id}", headers=headers, timeout=10)
            
            if classroom_response.status_code != 200:
                self.log_result("Test Auto-Enrollment Logic", False, f"Could not get classroom: HTTP {classroom_response.status_code}")
                return False
            
            classroom = classroom_response.json()
            
            # Get program details
            program_response = requests.get(f"{BACKEND_URL}/programs/{self.test_program_id}", headers=headers, timeout=10)
            
            if program_response.status_code != 200:
                self.log_result("Test Auto-Enrollment Logic", False, f"Could not get program: HTTP {program_response.status_code}")
                return False
            
            program = program_response.json()
            
            # Check if program is in classroom
            program_in_classroom = self.test_program_id in classroom.get('programIds', [])
            
            # Get student enrollments
            student_headers = {"Authorization": f"Bearer {self.student_token}"}
            enrollments_response = requests.get(f"{BACKEND_URL}/enrollments", headers=student_headers, timeout=10)
            
            if enrollments_response.status_code != 200:
                self.log_result("Test Auto-Enrollment Logic", False, f"Could not get student enrollments: HTTP {enrollments_response.status_code}")
                return False
            
            enrollments = enrollments_response.json()
            enrolled_course_ids = [e.get('courseId') for e in enrollments]
            
            # Check if student is enrolled in program courses
            program_course_ids = program.get('courseIds', [])
            enrolled_in_program_courses = [course_id for course_id in program_course_ids if course_id in enrolled_course_ids]
            
            expected_enrollments = len(program_course_ids) if program_in_classroom else 0
            actual_enrollments = len(enrolled_in_program_courses)
            
            auto_enrollment_working = (actual_enrollments == expected_enrollments)
            
            self.log_result(
                "Test Auto-Enrollment Logic", 
                auto_enrollment_working, 
                f"Program in classroom: {program_in_classroom}, Program courses: {len(program_course_ids)}, Student enrolled in program courses: {actual_enrollments}/{expected_enrollments}"
            )
            return auto_enrollment_working
                
        except Exception as e:
            self.log_result("Test Auto-Enrollment Logic", False, f"Exception: {str(e)}")
            return False

    def test_final_exam_association(self):
        """Test if final exam exists for the program and is accessible"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            if not self.test_program_id:
                self.log_result("Test Final Exam Association", False, "No test program ID available")
                return False
            
            # Get final tests
            response = requests.get(f"{BACKEND_URL}/final-tests", headers=headers, timeout=10)
            
            if response.status_code == 200:
                final_tests = response.json()
                
                # Look for final test associated with our program
                program_final_tests = []
                for test in final_tests:
                    if test.get('programId') == self.test_program_id:
                        program_final_tests.append({
                            'title': test.get('title'),
                            'isPublished': test.get('isPublished'),
                            'questions': len(test.get('questions', []))
                        })
                
                has_final_exam = len(program_final_tests) > 0
                
                self.log_result(
                    "Test Final Exam Association", 
                    has_final_exam, 
                    f"Program has {len(program_final_tests)} final exam(s): {program_final_tests}"
                )
                return has_final_exam
            else:
                self.log_result("Test Final Exam Association", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Test Final Exam Association", False, f"Exception: {str(e)}")
            return False

    def run_investigation(self):
        """Run the complete program enrollment investigation"""
        print("🔍 Starting Program Enrollment Investigation")
        print("=" * 80)
        print("ISSUE: Student cannot see newly created program despite admin assignment")
        print("PROGRAM: 'test course 4'")
        print("CLASSROOM: 'test program 4' with batch ID 'tc4'")
        print("STUDENT: brayden.student@covesmart.com")
        print("=" * 80)
        print()
        
        # Authentication tests
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot continue")
            return False
            
        if not self.authenticate_student():
            print("❌ Student authentication failed - cannot continue")
            return False
        
        # Investigation steps
        test_methods = [
            self.find_test_course_4_program,
            self.find_test_program_4_classroom,
            self.verify_student_in_classroom,
            self.verify_program_in_classroom,
            self.test_student_enrollments,
            self.test_student_classrooms,
            self.test_auto_enrollment_logic,
            self.test_final_exam_association
        ]
        
        for test_method in test_methods:
            try:
                test_method()
                time.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                self.log_result(test_method.__name__, False, f"Unexpected error: {str(e)}")
        
        # Summary
        print("=" * 80)
        print("📊 PROGRAM ENROLLMENT INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print()
        
        if failed_tests > 0:
            print("❌ ISSUES IDENTIFIED:")
            for result in self.results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
            print()
        
        # Root cause analysis
        print("🔍 ROOT CAUSE ANALYSIS:")
        
        # Check key failure points
        program_found = any(r['success'] for r in self.results if 'test course 4' in r['test'].lower())
        classroom_found = any(r['success'] for r in self.results if 'test program 4' in r['test'].lower())
        student_in_classroom = any(r['success'] for r in self.results if 'student in classroom' in r['test'].lower())
        program_in_classroom = any(r['success'] for r in self.results if 'program in classroom' in r['test'].lower())
        auto_enrollment_working = any(r['success'] for r in self.results if 'auto-enrollment' in r['test'].lower())
        
        if not program_found:
            print("  ❌ CRITICAL: Program 'test course 4' not found - may not have been created or published")
        elif not classroom_found:
            print("  ❌ CRITICAL: Classroom 'test program 4' with batch 'tc4' not found")
        elif not student_in_classroom:
            print("  ❌ CRITICAL: Student not properly assigned to classroom")
        elif not program_in_classroom:
            print("  ❌ CRITICAL: Program not properly associated with classroom")
        elif not auto_enrollment_working:
            print("  ❌ CRITICAL: Auto-enrollment logic not working for classroom assignments")
        else:
            print("  ✅ All components appear to be configured correctly")
        
        print()
        return failed_tests == 0

if __name__ == "__main__":
    investigator = ProgramEnrollmentInvestigator()
    success = investigator.run_investigation()
    
    if success:
        print("🎉 Program enrollment investigation completed - no issues found!")
        sys.exit(0)
    else:
        print("💥 Program enrollment investigation identified issues!")
        sys.exit(1)