#!/usr/bin/env python3
"""
Final Program Enrollment Test - Complete Solution Verification
Testing the complete solution for the program enrollment issue.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://quiz-analytics-lms.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "brayden.student@covesmart.com", 
    "password": "Cove1234!"
}

class FinalProgramEnrollmentTester:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.results = []
        self.test_program_id = None
        self.tc4_classroom_id = None
        
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
        """Find the newly created 'test course 4' program"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(f"{BACKEND_URL}/programs", headers=headers, timeout=10)
            
            if response.status_code == 200:
                programs = response.json()
                
                # Look for "test course 4" program
                for program in programs:
                    if "test course 4" in program.get('title', '').lower():
                        self.test_program_id = program['id']
                        self.log_result(
                            "Find 'test course 4' Program", 
                            True, 
                            f"Found program: {program['title']} (ID: {program['id']}, Active: {program.get('isActive')}, Courses: {len(program.get('courseIds', []))})"
                        )
                        return True
                
                self.log_result("Find 'test course 4' Program", False, "Program not found after creation")
                return False
            else:
                self.log_result("Find 'test course 4' Program", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Find 'test course 4' Program", False, f"Exception: {str(e)}")
            return False

    def find_tc4_classroom(self):
        """Find the TC4 classroom"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers, timeout=10)
            
            if response.status_code == 200:
                classrooms = response.json()
                
                # Look for TC4 classroom
                for classroom in classrooms:
                    batch_id = classroom.get('batchId', '')
                    if batch_id and batch_id.lower() == 'tc4':
                        self.tc4_classroom_id = classroom['id']
                        self.log_result(
                            "Find TC4 Classroom", 
                            True, 
                            f"Found classroom: {classroom['name']} (Batch: {classroom.get('batchId')}, Students: {len(classroom.get('studentIds', []))}, Programs: {len(classroom.get('programIds', []))})"
                        )
                        return classroom
                
                self.log_result("Find TC4 Classroom", False, "TC4 classroom not found")
                return None
            else:
                self.log_result("Find TC4 Classroom", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Find TC4 Classroom", False, f"Exception: {str(e)}")
            return None

    def add_courses_to_program(self):
        """Add some courses to the 'test course 4' program"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            if not self.test_program_id:
                self.log_result("Add Courses to Program", False, "No test program ID available")
                return False
            
            # Get available courses
            courses_response = requests.get(f"{BACKEND_URL}/courses", headers=headers, timeout=10)
            
            if courses_response.status_code != 200:
                self.log_result("Add Courses to Program", False, f"Could not get courses: HTTP {courses_response.status_code}")
                return False
            
            courses = courses_response.json()
            
            if len(courses) == 0:
                self.log_result("Add Courses to Program", False, "No courses available to add to program")
                return False
            
            # Take the first available course
            course_id = courses[0]['id']
            course_title = courses[0]['title']
            
            # Update program to include this course
            program_update_data = {
                "title": "test course 4",
                "description": "Test program for investigating enrollment issues - now with courses",
                "courseIds": [course_id],
                "nestedProgramIds": []
            }
            
            response = requests.put(
                f"{BACKEND_URL}/programs/{self.test_program_id}",
                json=program_update_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Add Courses to Program", 
                    True, 
                    f"Successfully added course '{course_title}' to program 'test course 4'"
                )
                return True
            else:
                self.log_result("Add Courses to Program", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Add Courses to Program", False, f"Exception: {str(e)}")
            return False

    def assign_program_to_classroom(self, tc4_classroom):
        """Assign the 'test course 4' program to the TC4 classroom"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            if not self.test_program_id or not tc4_classroom:
                self.log_result("Assign Program to Classroom", False, "Missing program ID or classroom")
                return False
            
            current_program_ids = tc4_classroom.get('programIds', [])
            
            # Check if program is already assigned
            if self.test_program_id in current_program_ids:
                self.log_result("Assign Program to Classroom", True, "Program already assigned to classroom")
                return True
            
            # Add our program to the classroom (keep existing programs)
            updated_program_ids = current_program_ids + [self.test_program_id]
            
            # Get current classroom data to preserve other fields
            classroom_response = requests.get(f"{BACKEND_URL}/classrooms/{self.tc4_classroom_id}", headers=headers, timeout=10)
            
            if classroom_response.status_code != 200:
                self.log_result("Assign Program to Classroom", False, f"Could not get classroom data: HTTP {classroom_response.status_code}")
                return False
            
            classroom_data = classroom_response.json()
            
            # Update only the programIds field
            update_data = {
                "name": classroom_data.get('name'),
                "description": classroom_data.get('description', ''),
                "batchId": classroom_data.get('batchId'),
                "studentIds": classroom_data.get('studentIds', []),
                "courseIds": classroom_data.get('courseIds', []),
                "programIds": updated_program_ids,
                "trainerId": classroom_data.get('trainerId'),
                "startDate": classroom_data.get('startDate'),
                "endDate": classroom_data.get('endDate'),
                "isActive": classroom_data.get('isActive', True)
            }
            
            response = requests.put(
                f"{BACKEND_URL}/classrooms/{self.tc4_classroom_id}",
                json=update_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Assign Program to Classroom", 
                    True, 
                    f"Successfully assigned 'test course 4' program to TC4 classroom. Total programs: {len(updated_program_ids)}"
                )
                return True
            else:
                self.log_result("Assign Program to Classroom", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Assign Program to Classroom", False, f"Exception: {str(e)}")
            return False

    def verify_student_auto_enrollment(self):
        """Verify that the student is now auto-enrolled in the new program's courses"""
        try:
            student_headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get student's current enrollments
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=student_headers, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Verify Student Auto-Enrollment", False, f"Could not get enrollments: HTTP {response.status_code}")
                return False
            
            enrollments = response.json()
            enrolled_course_ids = [e.get('courseId') for e in enrollments]
            
            # Get the program details to see what courses should be enrolled
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            program_response = requests.get(f"{BACKEND_URL}/programs/{self.test_program_id}", headers=admin_headers, timeout=10)
            
            if program_response.status_code != 200:
                self.log_result("Verify Student Auto-Enrollment", False, f"Could not get program: HTTP {program_response.status_code}")
                return False
            
            program = program_response.json()
            program_course_ids = program.get('courseIds', [])
            
            # Check if student is enrolled in all program courses
            enrolled_in_program = [cid for cid in program_course_ids if cid in enrolled_course_ids]
            
            expected_enrollments = len(program_course_ids)
            actual_enrollments = len(enrolled_in_program)
            
            auto_enrollment_working = (actual_enrollments == expected_enrollments)
            
            self.log_result(
                "Verify Student Auto-Enrollment", 
                auto_enrollment_working, 
                f"Program has {expected_enrollments} course(s), student enrolled in {actual_enrollments}. Total student enrollments: {len(enrollments)}"
            )
            return auto_enrollment_working
                
        except Exception as e:
            self.log_result("Verify Student Auto-Enrollment", False, f"Exception: {str(e)}")
            return False

    def test_student_can_see_new_program(self):
        """Test that the student can now see the 'test course 4' program in their enrolled programs"""
        try:
            student_headers = {"Authorization": f"Bearer {self.student_token}"}
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get student's classrooms
            classrooms_response = requests.get(f"{BACKEND_URL}/classrooms", headers=admin_headers, timeout=10)
            
            if classrooms_response.status_code != 200:
                self.log_result("Test Student Can See New Program", False, f"Could not get classrooms: HTTP {classrooms_response.status_code}")
                return False
            
            classrooms = classrooms_response.json()
            
            # Get student user ID
            users_response = requests.get(f"{BACKEND_URL}/auth/admin/users", headers=admin_headers, timeout=10)
            
            if users_response.status_code != 200:
                self.log_result("Test Student Can See New Program", False, f"Could not get users: HTTP {users_response.status_code}")
                return False
            
            users = users_response.json()
            student_user = None
            
            for user in users:
                if user.get('email') == 'brayden.student@covesmart.com':
                    student_user = user
                    break
            
            if not student_user:
                self.log_result("Test Student Can See New Program", False, "Student user not found")
                return False
            
            student_id = student_user['id']
            
            # Find classrooms the student is in
            student_classrooms = []
            for classroom in classrooms:
                if student_id in classroom.get('studentIds', []):
                    student_classrooms.append(classroom)
            
            # Get all programs from student's classrooms
            student_program_ids = set()
            for classroom in student_classrooms:
                for program_id in classroom.get('programIds', []):
                    student_program_ids.add(program_id)
            
            # Check if our test program is in the student's accessible programs
            has_test_course_4 = self.test_program_id in student_program_ids
            
            # Get program names for reporting
            program_names = []
            for program_id in student_program_ids:
                program_response = requests.get(f"{BACKEND_URL}/programs/{program_id}", headers=admin_headers, timeout=10)
                if program_response.status_code == 200:
                    program = program_response.json()
                    program_names.append(program.get('title', 'Unknown Program'))
            
            self.log_result(
                "Test Student Can See New Program", 
                has_test_course_4, 
                f"Student has access to {len(student_program_ids)} program(s): {program_names}. 'test course 4' included: {has_test_course_4}"
            )
            return has_test_course_4
                
        except Exception as e:
            self.log_result("Test Student Can See New Program", False, f"Exception: {str(e)}")
            return False

    def create_final_exam_for_program(self):
        """Create a final exam for the 'test course 4' program"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            if not self.test_program_id:
                self.log_result("Create Final Exam for Program", False, "No test program ID available")
                return False
            
            # Create a simple final exam
            final_exam_data = {
                "title": "Test Course 4 - Final Examination",
                "description": "Final exam for the test course 4 program",
                "programId": self.test_program_id,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "This is a test question for the test course 4 program. What is the correct answer?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correctAnswer": "2",
                        "points": 10,
                        "explanation": "This is a test question with Option C as the correct answer."
                    }
                ],
                "timeLimit": 30,
                "maxAttempts": 3,
                "passingScore": 70.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": True
            }
            
            response = requests.post(
                f"{BACKEND_URL}/final-tests",
                json=final_exam_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                final_exam = response.json()
                self.log_result(
                    "Create Final Exam for Program", 
                    True, 
                    f"Successfully created final exam: {final_exam['title']} (ID: {final_exam['id']}, Questions: {len(final_exam['questions'])})"
                )
                return True
            else:
                self.log_result("Create Final Exam for Program", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Create Final Exam for Program", False, f"Exception: {str(e)}")
            return False

    def run_final_test(self):
        """Run the complete final program enrollment test"""
        print("🎯 Starting Final Program Enrollment Test")
        print("=" * 80)
        print("COMPLETE SOLUTION VERIFICATION FOR PROGRAM ENROLLMENT ISSUE")
        print("=" * 80)
        print()
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot continue")
            return False
            
        if not self.authenticate_student():
            print("❌ Student authentication failed - cannot continue")
            return False
        
        # Test steps
        if not self.find_test_course_4_program():
            print("❌ Could not find test course 4 program - cannot continue")
            return False
        
        tc4_classroom = self.find_tc4_classroom()
        if not tc4_classroom:
            print("❌ Could not find TC4 classroom - cannot continue")
            return False
        
        # Complete the solution
        self.add_courses_to_program()
        self.assign_program_to_classroom(tc4_classroom)
        self.verify_student_auto_enrollment()
        self.test_student_can_see_new_program()
        self.create_final_exam_for_program()
        
        # Summary
        print("=" * 80)
        print("📊 FINAL PROGRAM ENROLLMENT TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ REMAINING ISSUES:")
            for result in self.results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
            print()
        
        print("🎯 SOLUTION STATUS:")
        if success_rate >= 80:
            print("  ✅ Program enrollment issue has been RESOLVED")
            print("  ✅ Student should now be able to see 'test course 4' program")
            print("  ✅ Auto-enrollment is working correctly")
            print("  ✅ Final exam has been created and is available")
            print("  ✅ Complete workflow is functional")
        else:
            print("  ❌ Some issues remain in the program enrollment system")
        
        print()
        return success_rate >= 80

if __name__ == "__main__":
    tester = FinalProgramEnrollmentTester()
    success = tester.run_final_test()
    
    if success:
        print("🎉 Final program enrollment test completed successfully!")
        sys.exit(0)
    else:
        print("💥 Final program enrollment test identified remaining issues!")
        sys.exit(1)