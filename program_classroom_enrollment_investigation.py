#!/usr/bin/env python3
"""
🚨 CRITICAL BUG INVESTIGATION: Program Assignment to Classroom Enrollment Issue

INVESTIGATION OBJECTIVES:
1. Find 'test program 2' - Verify program exists and student assignment
2. Check student assignment - Verify brayden.student is properly assigned to the program  
3. Check classroom creation - Find the classroom associated with this program
4. Test auto-enrollment logic - Verify if program assignment triggers classroom enrollment
5. Check enrollment records - Look for enrollment records for brayden.student
6. Test enrollment status display - Verify how frontend determines enrollment status

CURRENT ISSUE: 
Student can see classroom in their classrooms list BUT classroom shows student is NOT enrolled 
(enrollment status mismatch). This suggests an issue with the auto-enrollment logic when students 
are assigned to programs.
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL - using internal port
BACKEND_URL = "http://localhost:8001/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "brayden.student@learningfwiend.com",
    "password": "Cove1234!"  # Based on previous test results
}

class ProgramClassroomEnrollmentInvestigator:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.admin_user = None
        self.student_user = None
        self.test_results = []
        
    def log_result(self, test_name, success, details, data=None):
        """Log test result with timestamp"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2)}")
    
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.admin_user = data["user"]
                self.log_result("Admin Authentication", True, f"Successfully authenticated as {self.admin_user['full_name']}")
                return True
            else:
                self.log_result("Admin Authentication", False, f"Failed with status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_student(self):
        """Authenticate student user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=STUDENT_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.student_token = data["access_token"]
                self.student_user = data["user"]
                self.log_result("Student Authentication", True, f"Successfully authenticated as {self.student_user['full_name']}")
                return True
            else:
                self.log_result("Student Authentication", False, f"Failed with status {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_result("Student Authentication", False, f"Exception: {str(e)}")
            return False
    
    def find_test_program_2(self):
        """Find 'test program 2' and verify its existence"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/programs", headers=headers)
            
            if response.status_code == 200:
                programs = response.json()
                test_program_2 = None
                
                # Look for 'test program 2' (case insensitive)
                for program in programs:
                    if 'test program 2' in program.get('title', '').lower():
                        test_program_2 = program
                        break
                
                if test_program_2:
                    self.log_result("Find Test Program 2", True, 
                                  f"Found program: {test_program_2['title']} (ID: {test_program_2['id']})",
                                  test_program_2)
                    return test_program_2
                else:
                    # List all programs for debugging
                    program_titles = [p.get('title', 'No title') for p in programs]
                    self.log_result("Find Test Program 2", False, 
                                  f"Program not found. Available programs: {program_titles}",
                                  {"available_programs": program_titles})
                    return None
            else:
                self.log_result("Find Test Program 2", False, f"API call failed with status {response.status_code}", response.text)
                return None
        except Exception as e:
            self.log_result("Find Test Program 2", False, f"Exception: {str(e)}")
            return None
    
    def check_program_student_assignment(self, program_id):
        """Check if brayden.student is assigned to the program"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/programs/{program_id}", headers=headers)
            
            if response.status_code == 200:
                program = response.json()
                
                # Check if there's a student assignment mechanism
                # This might be through classrooms that reference the program
                self.log_result("Check Program Details", True, 
                              f"Program details retrieved: {program.get('title')}",
                              program)
                return program
            else:
                self.log_result("Check Program Details", False, f"Failed to get program details: {response.status_code}", response.text)
                return None
        except Exception as e:
            self.log_result("Check Program Details", False, f"Exception: {str(e)}")
            return None
    
    def find_classrooms_with_program(self, program_id):
        """Find classrooms that include the test program"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers)
            
            if response.status_code == 200:
                classrooms = response.json()
                program_classrooms = []
                
                for classroom in classrooms:
                    program_ids = classroom.get('programIds', [])
                    if program_id in program_ids:
                        program_classrooms.append(classroom)
                
                if program_classrooms:
                    self.log_result("Find Program Classrooms", True, 
                                  f"Found {len(program_classrooms)} classrooms with program",
                                  program_classrooms)
                    return program_classrooms
                else:
                    self.log_result("Find Program Classrooms", False, 
                                  "No classrooms found with this program",
                                  {"all_classrooms": classrooms})
                    return []
            else:
                self.log_result("Find Program Classrooms", False, f"Failed to get classrooms: {response.status_code}", response.text)
                return []
        except Exception as e:
            self.log_result("Find Program Classrooms", False, f"Exception: {str(e)}")
            return []
    
    def check_student_classroom_assignment(self, classrooms):
        """Check if brayden.student is assigned to any of the classrooms"""
        student_classrooms = []
        
        for classroom in classrooms:
            student_ids = classroom.get('studentIds', [])
            if self.student_user['id'] in student_ids:
                student_classrooms.append(classroom)
        
        if student_classrooms:
            self.log_result("Check Student Classroom Assignment", True, 
                          f"Student is assigned to {len(student_classrooms)} classrooms",
                          student_classrooms)
            return student_classrooms
        else:
            self.log_result("Check Student Classroom Assignment", False, 
                          f"Student {self.student_user['full_name']} not found in any program classrooms",
                          {"student_id": self.student_user['id'], "classrooms_checked": len(classrooms)})
            return []
    
    def check_student_enrollments(self):
        """Check what courses brayden.student is enrolled in"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            
            if response.status_code == 200:
                enrollments = response.json()
                self.log_result("Check Student Enrollments", True, 
                              f"Student has {len(enrollments)} enrollments",
                              enrollments)
                return enrollments
            else:
                self.log_result("Check Student Enrollments", False, f"Failed to get enrollments: {response.status_code}", response.text)
                return []
        except Exception as e:
            self.log_result("Check Student Enrollments", False, f"Exception: {str(e)}")
            return []
    
    def check_classroom_courses_vs_enrollments(self, classrooms, enrollments):
        """Compare courses in classrooms vs actual enrollments"""
        try:
            # Get all course IDs from classrooms
            classroom_course_ids = set()
            for classroom in classrooms:
                course_ids = classroom.get('courseIds', [])
                classroom_course_ids.update(course_ids)
            
            # Get all course IDs from enrollments
            enrollment_course_ids = set()
            for enrollment in enrollments:
                enrollment_course_ids.add(enrollment.get('courseId'))
            
            # Check for mismatches
            missing_enrollments = classroom_course_ids - enrollment_course_ids
            extra_enrollments = enrollment_course_ids - classroom_course_ids
            
            if missing_enrollments or extra_enrollments:
                self.log_result("Course Enrollment Mismatch", False, 
                              f"Mismatch detected - Missing: {len(missing_enrollments)}, Extra: {len(extra_enrollments)}",
                              {
                                  "classroom_courses": list(classroom_course_ids),
                                  "enrolled_courses": list(enrollment_course_ids),
                                  "missing_enrollments": list(missing_enrollments),
                                  "extra_enrollments": list(extra_enrollments)
                              })
                return False
            else:
                self.log_result("Course Enrollment Mismatch", True, 
                              "All classroom courses have corresponding enrollments")
                return True
        except Exception as e:
            self.log_result("Course Enrollment Mismatch", False, f"Exception: {str(e)}")
            return False
    
    def test_auto_enrollment_logic(self, program_id):
        """Test if program assignment should trigger auto-enrollment"""
        try:
            # Get program details
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/programs/{program_id}", headers=headers)
            
            if response.status_code == 200:
                program = response.json()
                program_course_ids = program.get('courseIds', [])
                
                # Check if student is enrolled in program courses
                student_headers = {"Authorization": f"Bearer {self.student_token}"}
                enrollments_response = requests.get(f"{BACKEND_URL}/enrollments", headers=student_headers)
                
                if enrollments_response.status_code == 200:
                    enrollments = enrollments_response.json()
                    enrolled_course_ids = [e.get('courseId') for e in enrollments]
                    
                    missing_program_courses = set(program_course_ids) - set(enrolled_course_ids)
                    
                    if missing_program_courses:
                        self.log_result("Auto-Enrollment Logic Test", False, 
                                      f"Student missing enrollments for {len(missing_program_courses)} program courses",
                                      {
                                          "program_courses": program_course_ids,
                                          "enrolled_courses": enrolled_course_ids,
                                          "missing_courses": list(missing_program_courses)
                                      })
                        return False
                    else:
                        self.log_result("Auto-Enrollment Logic Test", True, 
                                      "Student is enrolled in all program courses")
                        return True
                else:
                    self.log_result("Auto-Enrollment Logic Test", False, f"Failed to get student enrollments: {enrollments_response.status_code}")
                    return False
            else:
                self.log_result("Auto-Enrollment Logic Test", False, f"Failed to get program details: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Auto-Enrollment Logic Test", False, f"Exception: {str(e)}")
            return False
    
    def investigate_enrollment_status_display(self, classrooms):
        """Investigate how enrollment status is determined for display"""
        try:
            for classroom in classrooms:
                classroom_id = classroom['id']
                
                # Get classroom students (admin view)
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = requests.get(f"{BACKEND_URL}/classrooms/{classroom_id}/students", headers=headers)
                
                if response.status_code == 200:
                    students = response.json()
                    student_found = False
                    
                    for student in students:
                        if student.get('id') == self.student_user['id']:
                            student_found = True
                            self.log_result("Classroom Student List", True, 
                                          f"Student found in classroom {classroom['title']} student list",
                                          student)
                            break
                    
                    if not student_found:
                        self.log_result("Classroom Student List", False, 
                                      f"Student NOT found in classroom {classroom['title']} student list",
                                      {"classroom_students": students})
                else:
                    self.log_result("Classroom Student List", False, 
                                  f"Failed to get classroom students: {response.status_code}")
        except Exception as e:
            self.log_result("Enrollment Status Display Investigation", False, f"Exception: {str(e)}")
    
    def run_investigation(self):
        """Run the complete investigation"""
        print("🚨 STARTING CRITICAL BUG INVESTIGATION: Program Assignment to Classroom Enrollment Issue")
        print("=" * 80)
        
        # Step 1: Authenticate users
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        if not self.authenticate_student():
            print("❌ Cannot proceed without student authentication")
            return False
        
        # Step 2: Find 'test program 2'
        test_program = self.find_test_program_2()
        if not test_program:
            print("❌ Cannot proceed without finding test program 2")
            return False
        
        program_id = test_program['id']
        
        # Step 3: Check program details and student assignment
        program_details = self.check_program_student_assignment(program_id)
        
        # Step 4: Find classrooms associated with this program
        program_classrooms = self.find_classrooms_with_program(program_id)
        
        # Step 5: Check if student is assigned to these classrooms
        student_classrooms = self.check_student_classroom_assignment(program_classrooms)
        
        # Step 6: Check student's actual enrollments
        student_enrollments = self.check_student_enrollments()
        
        # Step 7: Compare classroom courses vs enrollments
        if student_classrooms:
            self.check_classroom_courses_vs_enrollments(student_classrooms, student_enrollments)
        
        # Step 8: Test auto-enrollment logic
        self.test_auto_enrollment_logic(program_id)
        
        # Step 9: Investigate enrollment status display
        if student_classrooms:
            self.investigate_enrollment_status_display(student_classrooms)
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Show failed tests
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        return failed_tests == 0

if __name__ == "__main__":
    investigator = ProgramClassroomEnrollmentInvestigator()
    success = investigator.run_investigation()
    
    # Save detailed results
    with open('/app/program_classroom_enrollment_investigation_results.json', 'w') as f:
        json.dump(investigator.test_results, f, indent=2, default=str)
    
    print(f"\n📊 Detailed results saved to: program_classroom_enrollment_investigation_results.json")
    
    if success:
        print("🎉 Investigation completed successfully - no critical issues found")
        sys.exit(0)
    else:
        print("🚨 Investigation found critical issues that need attention")
        sys.exit(1)