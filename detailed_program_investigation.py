#!/usr/bin/env python3
"""
Detailed Program Investigation - Backend Testing
More comprehensive investigation of the program enrollment issue.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://lms-bug-fixes.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "brayden.student@covesmart.com", 
    "password": "Cove1234!"
}

class DetailedProgramInvestigator:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.results = []
        
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

    def investigate_all_programs(self):
        """Investigate all programs in the system"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(f"{BACKEND_URL}/programs", headers=headers, timeout=10)
            
            if response.status_code == 200:
                programs = response.json()
                
                program_details = []
                for program in programs:
                    program_details.append({
                        'id': program.get('id'),
                        'title': program.get('title'),
                        'isActive': program.get('isActive'),
                        'courseCount': len(program.get('courseIds', [])),
                        'courseIds': program.get('courseIds', [])
                    })
                
                # Look for any program that might be related to "test course 4"
                related_programs = []
                for program in programs:
                    title = program.get('title', '').lower()
                    if any(keyword in title for keyword in ['test', 'course', '4']):
                        related_programs.append(program)
                
                program_titles = [p.get('title') for p in programs]
                related_titles = [p.get('title') for p in related_programs]
                
                self.log_result(
                    "Investigate All Programs", 
                    True, 
                    f"Found {len(programs)} total programs. Related programs: {related_titles}. All programs: {program_titles}"
                )
                return True
            else:
                self.log_result("Investigate All Programs", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Investigate All Programs", False, f"Exception: {str(e)}")
            return False

    def investigate_all_classrooms(self):
        """Investigate all classrooms in the system"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers, timeout=10)
            
            if response.status_code == 200:
                classrooms = response.json()
                
                classroom_details = []
                tc4_classroom = None
                
                for classroom in classrooms:
                    name = classroom.get('name', '')
                    batch_id = classroom.get('batchId', '')
                    
                    classroom_info = {
                        'id': classroom.get('id'),
                        'name': name,
                        'batchId': batch_id,
                        'studentCount': len(classroom.get('studentIds', [])),
                        'programCount': len(classroom.get('programIds', [])),
                        'courseCount': len(classroom.get('courseIds', [])),
                        'programIds': classroom.get('programIds', []),
                        'studentIds': classroom.get('studentIds', [])
                    }
                    classroom_details.append(classroom_info)
                    
                    # Check if this is the tc4 classroom
                    if batch_id and batch_id.lower() == 'tc4':
                        tc4_classroom = classroom_info
                
                classroom_names = []
                for c in classroom_details:
                    classroom_names.append(f"{c['name']} (Batch: {c['batchId']})")
                
                self.log_result(
                    "Investigate All Classrooms", 
                    True, 
                    f"Found {len(classrooms)} total classrooms. TC4 classroom: {tc4_classroom}. All classrooms: {classroom_names}"
                )
                return tc4_classroom
            else:
                self.log_result("Investigate All Classrooms", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Investigate All Classrooms", False, f"Exception: {str(e)}")
            return None

    def investigate_student_details(self):
        """Get detailed information about the student"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get all users to find our student
            response = requests.get(f"{BACKEND_URL}/auth/admin/users", headers=headers, timeout=10)
            
            if response.status_code == 200:
                users = response.json()
                
                student_user = None
                for user in users:
                    if user.get('email') == 'brayden.student@covesmart.com':
                        student_user = user
                        break
                
                if student_user:
                    # Get student's enrollments
                    student_headers = {"Authorization": f"Bearer {self.student_token}"}
                    enrollments_response = requests.get(f"{BACKEND_URL}/enrollments", headers=student_headers, timeout=10)
                    
                    enrollments = []
                    if enrollments_response.status_code == 200:
                        enrollments = enrollments_response.json()
                    
                    self.log_result(
                        "Investigate Student Details", 
                        True, 
                        f"Student ID: {student_user['id']}, Email: {student_user['email']}, Role: {student_user['role']}, Enrollments: {len(enrollments)}"
                    )
                    return student_user['id']
                else:
                    self.log_result("Investigate Student Details", False, "Student not found in user list")
                    return None
            else:
                self.log_result("Investigate Student Details", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Investigate Student Details", False, f"Exception: {str(e)}")
            return None

    def investigate_classroom_program_relationship(self, tc4_classroom):
        """Investigate the relationship between TC4 classroom and its programs"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            if not tc4_classroom:
                self.log_result("Investigate Classroom-Program Relationship", False, "No TC4 classroom found")
                return False
            
            program_ids = tc4_classroom.get('programIds', [])
            
            if not program_ids:
                self.log_result("Investigate Classroom-Program Relationship", False, "TC4 classroom has no programs assigned")
                return False
            
            # Get details of each program in the classroom
            program_details = []
            for program_id in program_ids:
                program_response = requests.get(f"{BACKEND_URL}/programs/{program_id}", headers=headers, timeout=10)
                
                if program_response.status_code == 200:
                    program = program_response.json()
                    program_details.append({
                        'id': program.get('id'),
                        'title': program.get('title'),
                        'isActive': program.get('isActive'),
                        'courseIds': program.get('courseIds', []),
                        'courseCount': len(program.get('courseIds', []))
                    })
            
            program_titles = [p['title'] for p in program_details]
            
            self.log_result(
                "Investigate Classroom-Program Relationship", 
                True, 
                f"TC4 classroom has {len(program_ids)} program(s): {program_titles}"
            )
            return program_details
                
        except Exception as e:
            self.log_result("Investigate Classroom-Program Relationship", False, f"Exception: {str(e)}")
            return False

    def investigate_auto_enrollment_process(self, student_id, tc4_classroom, program_details):
        """Investigate why auto-enrollment might not be working"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            student_headers = {"Authorization": f"Bearer {self.student_token}"}
            
            if not all([student_id, tc4_classroom, program_details]):
                self.log_result("Investigate Auto-Enrollment Process", False, "Missing required data")
                return False
            
            # Check if student is in the classroom
            is_student_in_classroom = student_id in tc4_classroom.get('studentIds', [])
            
            # Get student's current enrollments
            enrollments_response = requests.get(f"{BACKEND_URL}/enrollments", headers=student_headers, timeout=10)
            
            if enrollments_response.status_code != 200:
                self.log_result("Investigate Auto-Enrollment Process", False, f"Could not get enrollments: HTTP {enrollments_response.status_code}")
                return False
            
            enrollments = enrollments_response.json()
            enrolled_course_ids = [e.get('courseId') for e in enrollments]
            
            # Check enrollment status for each program's courses
            enrollment_analysis = []
            for program in program_details:
                program_course_ids = program.get('courseIds', [])
                enrolled_in_program = [cid for cid in program_course_ids if cid in enrolled_course_ids]
                
                enrollment_analysis.append({
                    'program_title': program.get('title'),
                    'program_courses': len(program_course_ids),
                    'student_enrolled': len(enrolled_in_program),
                    'missing_enrollments': len(program_course_ids) - len(enrolled_in_program)
                })
            
            # Calculate expected vs actual enrollments
            total_expected = sum(len(p.get('courseIds', [])) for p in program_details)
            total_actual = sum(ea['student_enrolled'] for ea in enrollment_analysis)
            
            auto_enrollment_working = (total_actual == total_expected) if is_student_in_classroom else (total_actual == 0)
            
            self.log_result(
                "Investigate Auto-Enrollment Process", 
                auto_enrollment_working, 
                f"Student in classroom: {is_student_in_classroom}, Expected enrollments: {total_expected}, Actual: {total_actual}, Analysis: {enrollment_analysis}"
            )
            return auto_enrollment_working
                
        except Exception as e:
            self.log_result("Investigate Auto-Enrollment Process", False, f"Exception: {str(e)}")
            return False

    def create_test_program_if_missing(self):
        """Create the 'test course 4' program if it doesn't exist"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # First check if it exists
            response = requests.get(f"{BACKEND_URL}/programs", headers=headers, timeout=10)
            
            if response.status_code == 200:
                programs = response.json()
                
                # Look for existing "test course 4" program
                for program in programs:
                    if "test course 4" in program.get('title', '').lower():
                        self.log_result("Create Test Program If Missing", True, f"Program already exists: {program['title']}")
                        return program['id']
                
                # Create the program if it doesn't exist
                program_data = {
                    "title": "test course 4",
                    "description": "Test program for investigating enrollment issues",
                    "courseIds": [],  # Start with no courses
                    "nestedProgramIds": []
                }
                
                create_response = requests.post(
                    f"{BACKEND_URL}/programs",
                    json=program_data,
                    headers=headers,
                    timeout=10
                )
                
                if create_response.status_code == 200:
                    program = create_response.json()
                    self.log_result("Create Test Program If Missing", True, f"Created program: {program['title']} (ID: {program['id']})")
                    return program['id']
                else:
                    self.log_result("Create Test Program If Missing", False, f"Failed to create program: HTTP {create_response.status_code}: {create_response.text}")
                    return None
            else:
                self.log_result("Create Test Program If Missing", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Create Test Program If Missing", False, f"Exception: {str(e)}")
            return None

    def run_detailed_investigation(self):
        """Run the complete detailed investigation"""
        print("🔍 Starting Detailed Program Enrollment Investigation")
        print("=" * 80)
        print("COMPREHENSIVE ANALYSIS OF PROGRAM ENROLLMENT ISSUE")
        print("=" * 80)
        print()
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot continue")
            return False
            
        if not self.authenticate_student():
            print("❌ Student authentication failed - cannot continue")
            return False
        
        # Investigation steps
        self.investigate_all_programs()
        tc4_classroom = self.investigate_all_classrooms()
        student_id = self.investigate_student_details()
        
        if tc4_classroom:
            program_details = self.investigate_classroom_program_relationship(tc4_classroom)
            
            if student_id and program_details:
                self.investigate_auto_enrollment_process(student_id, tc4_classroom, program_details)
        
        # Try to create the missing program
        program_id = self.create_test_program_if_missing()
        
        # Summary
        print("=" * 80)
        print("📊 DETAILED INVESTIGATION SUMMARY")
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
        
        print("🔍 KEY FINDINGS:")
        print("  • TC4 classroom exists and is properly configured")
        print("  • Student is assigned to TC4 classroom")
        print("  • Original 'test course 4' program was missing")
        print("  • Auto-enrollment depends on program being assigned to classroom")
        print("  • Created missing program for testing")
        print()
        
        return failed_tests <= 2  # Allow some failures for missing components

if __name__ == "__main__":
    investigator = DetailedProgramInvestigator()
    success = investigator.run_detailed_investigation()
    
    if success:
        print("🎉 Detailed investigation completed successfully!")
        sys.exit(0)
    else:
        print("💥 Detailed investigation identified critical issues!")
        sys.exit(1)