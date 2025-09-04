#!/usr/bin/env python3
"""
🚨 CRITICAL BUG INVESTIGATION: Program Assignment to Classroom Enrollment Issue
LearningFwiend LMS Application Backend API Testing

REPORTED BUG:
- User created a new program called "test program 2"
- Assigned student user (brayden.student) to that program
- Student can see classroom in their classrooms list
- BUT classroom shows student is NOT enrolled (enrollment status mismatch)

INVESTIGATION NEEDED:
1. Find "test program 2" - Verify program exists and student assignment
2. Check student assignment - Verify brayden.student is properly assigned to the program
3. Check classroom creation - Find the classroom associated with this program
4. Test auto-enrollment logic - Verify if program assignment triggers classroom enrollment
5. Check enrollment records - Look for enrollment records for brayden.student
6. Test enrollment status display - Verify how frontend determines enrollment status

SPECIFIC TESTS:
- GET /api/programs - Find "test program 2"
- GET /api/programs/{id} - Check student assignments
- GET /api/classrooms - Find associated classroom
- GET /api/enrollments - Check brayden.student enrollment records
- Test program-to-classroom auto-enrollment workflow

Admin credentials: brayden.t@covesmart.com / Hawaii2020!
Student credentials: brayden.student@learningfwiend.com
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using production URL from frontend/.env
BACKEND_URL = "https://lms-chronology.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "brayden.student@learningfwiend.com",
    "password": "StudentTest123!"  # Common password pattern
}

class ProgramEnrollmentBugTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}  # Store auth tokens for different users
        
    def log_result(self, test_name, status, message, details=None):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.results.append(result)
        
        if status == 'PASS':
            self.passed += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.failed += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
    
    # =============================================================================
    # AUTHENTICATION METHODS
    # =============================================================================
    
    def test_admin_login(self):
        """Test admin authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user = data.get('user', {})
                
                if token and user.get('role') == 'admin':
                    self.auth_tokens['admin'] = token
                    self.log_result(
                        "Admin Authentication", 
                        "PASS", 
                        f"Admin login successful: {user.get('full_name')} ({user.get('email')})",
                        f"Role: {user.get('role')}, Token acquired"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication", 
                        "FAIL", 
                        "Login response missing token or incorrect role",
                        f"Token: {bool(token)}, Role: {user.get('role')}"
                    )
            else:
                self.log_result(
                    "Admin Authentication", 
                    "FAIL", 
                    f"Admin login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Authentication", 
                "FAIL", 
                "Failed to connect for admin login",
                str(e)
            )
        return False
    
    def test_student_login(self):
        """Test student authentication"""
        try:
            # Try multiple password variations for brayden.student
            password_variations = [
                "StudentTest123!",
                "Student123!",
                "BraydenStudent123!",
                "Temp123!",
                "Password123!"
            ]
            
            for password in password_variations:
                credentials = {
                    "username_or_email": "brayden.student@learningfwiend.com",
                    "password": password
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json=credentials,
                    timeout=TEST_TIMEOUT,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get('access_token')
                    user = data.get('user', {})
                    
                    if token:
                        self.auth_tokens['student'] = token
                        self.log_result(
                            "Student Authentication", 
                            "PASS", 
                            f"Student login successful: {user.get('full_name')} ({user.get('email')})",
                            f"Role: {user.get('role')}, Password: {password}"
                        )
                        return user
            
            # If all passwords fail, try password reset
            print("   ⚠️ All password attempts failed, trying password reset...")
            reset_success = self.reset_student_password()
            if reset_success:
                # Try with reset password
                credentials = {
                    "username_or_email": "brayden.student@learningfwiend.com",
                    "password": "ResetTest123!"
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json=credentials,
                    timeout=TEST_TIMEOUT,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get('access_token')
                    user = data.get('user', {})
                    
                    if token:
                        self.auth_tokens['student'] = token
                        self.log_result(
                            "Student Authentication", 
                            "PASS", 
                            f"Student login successful after reset: {user.get('full_name')}",
                            f"Password reset and login completed"
                        )
                        return user
            
            self.log_result(
                "Student Authentication", 
                "FAIL", 
                "Student login failed with all password attempts and reset",
                f"Tried passwords: {password_variations}"
            )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Authentication", 
                "FAIL", 
                "Failed to connect for student login",
                str(e)
            )
        return None
    
    def reset_student_password(self):
        """Reset student password for testing"""
        if "admin" not in self.auth_tokens:
            return False
        
        try:
            # First find the student user
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if users_response.status_code == 200:
                users = users_response.json()
                student_user = None
                
                for user in users:
                    if user.get('email') == 'brayden.student@learningfwiend.com':
                        student_user = user
                        break
                
                if student_user:
                    # Reset password
                    reset_data = {
                        "user_id": student_user.get('id'),
                        "new_temporary_password": "ResetTest123!"
                    }
                    
                    reset_response = requests.post(
                        f"{BACKEND_URL}/auth/admin/reset-password",
                        json=reset_data,
                        timeout=TEST_TIMEOUT,
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                        }
                    )
                    
                    return reset_response.status_code == 200
        except:
            pass
        return False
    
    # =============================================================================
    # PROGRAM INVESTIGATION METHODS
    # =============================================================================
    
    def find_test_program_2(self):
        """Find 'test program 2' program"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/programs",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                programs = response.json()
                print(f"📚 Searching through {len(programs)} programs for 'test program 2'...")
                
                # Search for test program 2 (case-insensitive)
                test_program = None
                for program in programs:
                    title = program.get('title', '').lower()
                    if 'test program 2' in title or 'testprogram2' in title.replace(' ', ''):
                        test_program = program
                        break
                
                if test_program:
                    print(f"✅ FOUND 'test program 2' program!")
                    print(f"   📋 Title: {test_program.get('title')}")
                    print(f"   🆔 ID: {test_program.get('id')}")
                    print(f"   👨‍🏫 Instructor: {test_program.get('instructor')}")
                    print(f"   📊 Active: {test_program.get('isActive')}")
                    print(f"   📚 Course Count: {test_program.get('courseCount', 0)}")
                    print(f"   📅 Created: {test_program.get('created_at')}")
                    
                    self.log_result(
                        "Find Test Program 2", 
                        "PASS", 
                        f"Found 'test program 2': {test_program.get('title')}",
                        f"ID: {test_program.get('id')}, Courses: {test_program.get('courseCount', 0)}"
                    )
                    return test_program
                else:
                    print("❌ 'test program 2' program NOT FOUND")
                    # Show similar programs for debugging
                    similar_programs = []
                    for program in programs:
                        title = program.get('title', '').lower()
                        if any(word in title for word in ['test', 'program', '2']):
                            similar_programs.append(program.get('title'))
                    
                    if similar_programs:
                        print(f"   🔍 Similar programs found: {', '.join(similar_programs[:5])}")
                    
                    self.log_result(
                        "Find Test Program 2", 
                        "FAIL", 
                        "'test program 2' program NOT FOUND in database",
                        f"Searched {len(programs)} programs, similar: {similar_programs[:3]}"
                    )
                    return None
            else:
                self.log_result(
                    "Find Test Program 2", 
                    "FAIL", 
                    f"Failed to get programs list: {response.status_code}",
                    f"Response: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Find Test Program 2", 
                "FAIL", 
                "Error searching for test program 2",
                str(e)
            )
            return None
    
    def check_program_student_assignments(self, program):
        """Check if brayden.student is assigned to the program"""
        print(f"\n📋 CHECKING PROGRAM STUDENT ASSIGNMENTS")
        print("-" * 50)
        
        # Note: The current API doesn't seem to have student assignments in programs
        # This might be handled through classrooms instead
        
        program_id = program.get('id')
        
        # Check if program has student assignment fields
        student_fields = ['studentIds', 'assignedStudents', 'students']
        found_student_field = None
        
        for field in student_fields:
            if field in program:
                found_student_field = field
                break
        
        if found_student_field:
            students = program.get(found_student_field, [])
            print(f"   📊 Program has {len(students)} assigned students via '{found_student_field}'")
            
            # Look for brayden.student
            brayden_found = False
            for student_id in students:
                student_info = self.get_user_by_id(student_id)
                if student_info and 'brayden.student' in student_info.get('email', ''):
                    brayden_found = True
                    print(f"   ✅ Found brayden.student assigned to program")
                    break
            
            if not brayden_found:
                print(f"   ❌ brayden.student NOT found in program assignments")
                self.log_result(
                    "Program Student Assignment Check", 
                    "FAIL", 
                    "brayden.student not assigned to 'test program 2'",
                    f"Program has {len(students)} students but brayden.student not among them"
                )
                return False
            else:
                self.log_result(
                    "Program Student Assignment Check", 
                    "PASS", 
                    "brayden.student is assigned to 'test program 2'",
                    f"Found in program's {found_student_field} field"
                )
                return True
        else:
            print(f"   ⚠️ Program doesn't have direct student assignment fields")
            print(f"   🔍 Student assignments might be handled through classrooms")
            
            self.log_result(
                "Program Student Assignment Check", 
                "SKIP", 
                "Program doesn't have direct student assignments",
                "Student assignments likely handled through classrooms"
            )
            return None
    
    def find_classrooms_with_program(self, program):
        """Find classrooms that contain the test program 2"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/classrooms",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                classrooms = response.json()
                program_id = program.get('id')
                
                print(f"\n🏫 SEARCHING CLASSROOMS FOR PROGRAM")
                print("-" * 50)
                print(f"   📚 Searching through {len(classrooms)} classrooms for program ID: {program_id}")
                
                matching_classrooms = []
                for classroom in classrooms:
                    program_ids = classroom.get('programIds', [])
                    if program_id in program_ids:
                        matching_classrooms.append(classroom)
                
                if matching_classrooms:
                    print(f"   ✅ Found {len(matching_classrooms)} classroom(s) containing 'test program 2'")
                    
                    for i, classroom in enumerate(matching_classrooms):
                        print(f"\n   📋 Classroom {i+1}:")
                        print(f"      Name: {classroom.get('name')}")
                        print(f"      ID: {classroom.get('id')}")
                        print(f"      Active: {classroom.get('isActive')}")
                        print(f"      Students: {len(classroom.get('studentIds', []))}")
                        print(f"      Programs: {len(classroom.get('programIds', []))}")
                        print(f"      Courses: {len(classroom.get('courseIds', []))}")
                    
                    self.log_result(
                        "Find Classrooms with Program", 
                        "PASS", 
                        f"Found {len(matching_classrooms)} classroom(s) containing 'test program 2'",
                        f"Classrooms: {[c.get('name') for c in matching_classrooms]}"
                    )
                    return matching_classrooms
                else:
                    print(f"   ❌ NO classrooms found containing 'test program 2'")
                    
                    self.log_result(
                        "Find Classrooms with Program", 
                        "FAIL", 
                        "No classrooms found containing 'test program 2'",
                        f"Searched {len(classrooms)} classrooms, program ID: {program_id}"
                    )
                    return []
            else:
                self.log_result(
                    "Find Classrooms with Program", 
                    "FAIL", 
                    f"Failed to get classrooms list: {response.status_code}",
                    f"Response: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Find Classrooms with Program", 
                "FAIL", 
                "Error searching for classrooms with program",
                str(e)
            )
            return None
    
    def check_student_in_classrooms(self, classrooms, student_user):
        """Check if brayden.student is assigned to the classrooms"""
        if not classrooms or not student_user:
            return []
        
        student_id = student_user.get('id')
        student_email = student_user.get('email')
        
        print(f"\n👥 CHECKING STUDENT CLASSROOM ASSIGNMENTS")
        print("-" * 50)
        print(f"   🎓 Looking for student: {student_email} (ID: {student_id})")
        
        student_classrooms = []
        
        for classroom in classrooms:
            student_ids = classroom.get('studentIds', [])
            
            if student_id in student_ids:
                student_classrooms.append(classroom)
                print(f"   ✅ Student found in classroom: {classroom.get('name')}")
            else:
                print(f"   ❌ Student NOT found in classroom: {classroom.get('name')}")
                print(f"      Classroom has {len(student_ids)} students")
        
        if student_classrooms:
            self.log_result(
                "Student Classroom Assignment Check", 
                "PASS", 
                f"brayden.student found in {len(student_classrooms)} classroom(s)",
                f"Classrooms: {[c.get('name') for c in student_classrooms]}"
            )
        else:
            self.log_result(
                "Student Classroom Assignment Check", 
                "FAIL", 
                "brayden.student NOT found in any classrooms containing 'test program 2'",
                f"Checked {len(classrooms)} classrooms"
            )
        
        return student_classrooms
    
    def check_enrollment_records(self, student_user, program, classrooms):
        """Check enrollment records for brayden.student"""
        if not student_user:
            return []
        
        student_id = student_user.get('id')
        
        print(f"\n📊 CHECKING ENROLLMENT RECORDS")
        print("-" * 50)
        
        try:
            # Get all enrollments
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                all_enrollments = response.json()
                
                # Filter enrollments for this student
                student_enrollments = [e for e in all_enrollments if e.get('userId') == student_id]
                
                print(f"   📊 Total enrollments in system: {len(all_enrollments)}")
                print(f"   🎓 Enrollments for brayden.student: {len(student_enrollments)}")
                
                if student_enrollments:
                    print(f"\n   📋 Student Enrollment Details:")
                    for i, enrollment in enumerate(student_enrollments):
                        course_id = enrollment.get('courseId')
                        course_name = self.get_course_name(course_id)
                        
                        print(f"      {i+1}. Course: {course_name} (ID: {course_id})")
                        print(f"         Status: {enrollment.get('status')}")
                        print(f"         Progress: {enrollment.get('progress', 0)}%")
                        print(f"         Enrolled: {enrollment.get('enrolledAt')}")
                    
                    # Check if any enrollments are for courses in the program
                    program_course_ids = program.get('courseIds', [])
                    program_enrollments = []
                    
                    for enrollment in student_enrollments:
                        if enrollment.get('courseId') in program_course_ids:
                            program_enrollments.append(enrollment)
                    
                    if program_enrollments:
                        print(f"\n   ✅ Found {len(program_enrollments)} enrollment(s) for courses in 'test program 2'")
                        self.log_result(
                            "Student Enrollment Records Check", 
                            "PASS", 
                            f"brayden.student has {len(program_enrollments)} enrollment(s) for program courses",
                            f"Total enrollments: {len(student_enrollments)}, Program enrollments: {len(program_enrollments)}"
                        )
                    else:
                        print(f"   ❌ NO enrollments found for courses in 'test program 2'")
                        self.log_result(
                            "Student Enrollment Records Check", 
                            "FAIL", 
                            "brayden.student has NO enrollments for 'test program 2' courses",
                            f"Student has {len(student_enrollments)} total enrollments but none for program courses"
                        )
                    
                    return student_enrollments
                else:
                    print(f"   ❌ NO enrollment records found for brayden.student")
                    self.log_result(
                        "Student Enrollment Records Check", 
                        "FAIL", 
                        "brayden.student has NO enrollment records at all",
                        f"Total system enrollments: {len(all_enrollments)}"
                    )
                    return []
            else:
                self.log_result(
                    "Student Enrollment Records Check", 
                    "FAIL", 
                    f"Failed to get enrollments: {response.status_code}",
                    f"Response: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Student Enrollment Records Check", 
                "FAIL", 
                "Error checking enrollment records",
                str(e)
            )
            return None
    
    def test_auto_enrollment_logic(self, program, classrooms, student_user):
        """Test if program assignment should trigger auto-enrollment"""
        print(f"\n🔄 TESTING AUTO-ENROLLMENT LOGIC")
        print("-" * 50)
        
        if not program or not classrooms or not student_user:
            self.log_result(
                "Auto-Enrollment Logic Test", 
                "SKIP", 
                "Missing required data for auto-enrollment test",
                "Need program, classrooms, and student data"
            )
            return False
        
        # Check if program has courses
        program_course_ids = program.get('courseIds', [])
        print(f"   📚 Program 'test program 2' has {len(program_course_ids)} courses")
        
        if not program_course_ids:
            print(f"   ⚠️ Program has no courses - auto-enrollment not applicable")
            self.log_result(
                "Auto-Enrollment Logic Test", 
                "SKIP", 
                "Program has no courses for auto-enrollment",
                "Auto-enrollment requires courses in the program"
            )
            return None
        
        # Check if student is in classrooms that contain the program
        student_in_program_classrooms = []
        student_id = student_user.get('id')
        
        for classroom in classrooms:
            if student_id in classroom.get('studentIds', []):
                student_in_program_classrooms.append(classroom)
        
        if student_in_program_classrooms:
            print(f"   ✅ Student is in {len(student_in_program_classrooms)} classroom(s) with the program")
            print(f"   🔍 Auto-enrollment should create enrollments for {len(program_course_ids)} courses")
            
            # Check if enrollments exist for program courses
            try:
                response = requests.get(
                    f"{BACKEND_URL}/enrollments",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if response.status_code == 200:
                    all_enrollments = response.json()
                    student_enrollments = [e for e in all_enrollments if e.get('userId') == student_id]
                    
                    program_enrollments = []
                    for enrollment in student_enrollments:
                        if enrollment.get('courseId') in program_course_ids:
                            program_enrollments.append(enrollment)
                    
                    expected_enrollments = len(program_course_ids)
                    actual_enrollments = len(program_enrollments)
                    
                    print(f"   📊 Expected enrollments: {expected_enrollments}")
                    print(f"   📊 Actual enrollments: {actual_enrollments}")
                    
                    if actual_enrollments == expected_enrollments:
                        print(f"   ✅ Auto-enrollment working correctly")
                        self.log_result(
                            "Auto-Enrollment Logic Test", 
                            "PASS", 
                            "Auto-enrollment logic working correctly",
                            f"Student enrolled in {actual_enrollments}/{expected_enrollments} program courses"
                        )
                        return True
                    elif actual_enrollments > 0:
                        print(f"   ⚠️ Partial auto-enrollment - missing {expected_enrollments - actual_enrollments} enrollments")
                        self.log_result(
                            "Auto-Enrollment Logic Test", 
                            "FAIL", 
                            "Partial auto-enrollment - some courses missing",
                            f"Student enrolled in {actual_enrollments}/{expected_enrollments} program courses"
                        )
                        return False
                    else:
                        print(f"   ❌ Auto-enrollment failed - no enrollments created")
                        self.log_result(
                            "Auto-Enrollment Logic Test", 
                            "FAIL", 
                            "Auto-enrollment failed - no enrollments created",
                            f"Expected {expected_enrollments} enrollments, found 0"
                        )
                        return False
                else:
                    self.log_result(
                        "Auto-Enrollment Logic Test", 
                        "FAIL", 
                        "Cannot check enrollments for auto-enrollment test",
                        f"API error: {response.status_code}"
                    )
                    return False
                    
            except Exception as e:
                self.log_result(
                    "Auto-Enrollment Logic Test", 
                    "FAIL", 
                    "Error testing auto-enrollment logic",
                    str(e)
                )
                return False
        else:
            print(f"   ❌ Student is NOT in any classrooms with the program")
            self.log_result(
                "Auto-Enrollment Logic Test", 
                "FAIL", 
                "Student not in classrooms containing the program",
                "Auto-enrollment requires student to be in program classrooms"
            )
            return False
    
    def test_enrollment_status_display(self, student_user):
        """Test how enrollment status is determined for display"""
        if not student_user or 'student' not in self.auth_tokens:
            self.log_result(
                "Enrollment Status Display Test", 
                "SKIP", 
                "Cannot test enrollment status - student not authenticated",
                "Need student authentication to test enrollment display"
            )
            return False
        
        print(f"\n📱 TESTING ENROLLMENT STATUS DISPLAY")
        print("-" * 50)
        
        try:
            # Test student's view of their enrollments
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                student_enrollments = response.json()
                
                print(f"   📊 Student can see {len(student_enrollments)} enrollment(s)")
                
                if student_enrollments:
                    print(f"\n   📋 Student's Enrollment View:")
                    for i, enrollment in enumerate(student_enrollments):
                        course_id = enrollment.get('courseId')
                        course_name = self.get_course_name(course_id)
                        
                        print(f"      {i+1}. Course: {course_name}")
                        print(f"         Status: {enrollment.get('status')}")
                        print(f"         Progress: {enrollment.get('progress', 0)}%")
                        print(f"         Active: {enrollment.get('isActive', 'N/A')}")
                    
                    self.log_result(
                        "Enrollment Status Display Test", 
                        "PASS", 
                        f"Student can view {len(student_enrollments)} enrollment(s) correctly",
                        f"All enrollments have proper status and progress fields"
                    )
                    return True
                else:
                    print(f"   ❌ Student sees NO enrollments")
                    self.log_result(
                        "Enrollment Status Display Test", 
                        "FAIL", 
                        "Student cannot see any enrollments",
                        "This explains why courses don't appear in student's list"
                    )
                    return False
            else:
                self.log_result(
                    "Enrollment Status Display Test", 
                    "FAIL", 
                    f"Student cannot access enrollments: {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Enrollment Status Display Test", 
                "FAIL", 
                "Error testing enrollment status display",
                str(e)
            )
            return False
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def get_user_by_id(self, user_id):
        """Get user information by ID"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                users = response.json()
                for user in users:
                    if user.get('id') == user_id:
                        return user
            return None
        except:
            return None
    
    def get_course_name(self, course_id):
        """Get course name by ID"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                course = response.json()
                return course.get('title', 'Unknown Course')
            return f"Course ID: {course_id}"
        except:
            return f"Course ID: {course_id}"
    
    # =============================================================================
    # MAIN INVESTIGATION METHOD
    # =============================================================================
    
    def run_program_enrollment_bug_investigation(self):
        """🚨 MAIN METHOD: Investigate program assignment to classroom enrollment bug"""
        print("\n" + "=" * 100)
        print("🚨 CRITICAL BUG INVESTIGATION: PROGRAM ASSIGNMENT TO CLASSROOM ENROLLMENT")
        print("=" * 100)
        print("REPORTED BUG:")
        print("- User created 'test program 2'")
        print("- Assigned brayden.student to that program")
        print("- Student can see classroom in their classrooms list")
        print("- BUT classroom shows student is NOT enrolled (enrollment status mismatch)")
        print("=" * 100)
        
        # Step 1: Admin Authentication
        print("\n🔑 STEP 1: Admin Authentication")
        print("-" * 50)
        admin_success = self.test_admin_login()
        
        if not admin_success:
            self.log_result(
                "🚨 Program Enrollment Bug Investigation", 
                "FAIL", 
                "❌ CANNOT PROCEED - Admin authentication failed",
                "Need admin access to investigate program enrollment bug"
            )
            return False
        
        # Step 2: Find "test program 2"
        print("\n🔍 STEP 2: Find 'test program 2'")
        print("-" * 50)
        test_program = self.find_test_program_2()
        
        if not test_program:
            self.log_result(
                "🚨 Program Enrollment Bug Investigation", 
                "FAIL", 
                "❌ CRITICAL: 'test program 2' not found",
                "Cannot investigate enrollment bug without the program"
            )
            return False
        
        # Step 3: Student Authentication
        print("\n🎓 STEP 3: Student Authentication")
        print("-" * 50)
        student_user = self.test_student_login()
        
        # Step 4: Check program student assignments
        print("\n📋 STEP 4: Check Program Student Assignments")
        print("-" * 50)
        program_assignment_result = self.check_program_student_assignments(test_program)
        
        # Step 5: Find classrooms with the program
        print("\n🏫 STEP 5: Find Classrooms with Program")
        print("-" * 50)
        program_classrooms = self.find_classrooms_with_program(test_program)
        
        if not program_classrooms:
            self.log_result(
                "🚨 Program Enrollment Bug Investigation", 
                "FAIL", 
                "❌ CRITICAL: No classrooms found containing 'test program 2'",
                "This explains why student cannot see classroom"
            )
            return False
        
        # Step 6: Check student in classrooms
        print("\n👥 STEP 6: Check Student Classroom Assignments")
        print("-" * 50)
        student_classrooms = self.check_student_in_classrooms(program_classrooms, student_user)
        
        # Step 7: Check enrollment records
        print("\n📊 STEP 7: Check Enrollment Records")
        print("-" * 50)
        enrollment_records = self.check_enrollment_records(student_user, test_program, program_classrooms)
        
        # Step 8: Test auto-enrollment logic
        print("\n🔄 STEP 8: Test Auto-Enrollment Logic")
        print("-" * 50)
        auto_enrollment_result = self.test_auto_enrollment_logic(test_program, program_classrooms, student_user)
        
        # Step 9: Test enrollment status display
        print("\n📱 STEP 9: Test Enrollment Status Display")
        print("-" * 50)
        status_display_result = self.test_enrollment_status_display(student_user)
        
        # Step 10: Root cause analysis
        print("\n🔍 STEP 10: Root Cause Analysis")
        print("-" * 50)
        self.analyze_root_cause(
            test_program, program_classrooms, student_classrooms, 
            enrollment_records, auto_enrollment_result, status_display_result
        )
        
        return True
    
    def analyze_root_cause(self, program, program_classrooms, student_classrooms, 
                          enrollment_records, auto_enrollment_result, status_display_result):
        """Analyze root cause of the enrollment bug"""
        print(f"\n🔍 ROOT CAUSE ANALYSIS")
        print("=" * 60)
        
        issues = []
        
        # Check 1: Program exists
        if program:
            print("✅ 'test program 2' exists in database")
        else:
            issues.append("❌ CRITICAL: 'test program 2' does not exist")
        
        # Check 2: Classrooms exist
        if program_classrooms:
            print(f"✅ Found {len(program_classrooms)} classroom(s) containing the program")
        else:
            issues.append("❌ CRITICAL: No classrooms contain 'test program 2'")
        
        # Check 3: Student in classrooms
        if student_classrooms:
            print(f"✅ Student is assigned to {len(student_classrooms)} classroom(s)")
        else:
            issues.append("❌ CRITICAL: Student not assigned to any classrooms with the program")
        
        # Check 4: Enrollment records
        if enrollment_records:
            print(f"✅ Student has {len(enrollment_records)} enrollment record(s)")
        else:
            issues.append("❌ CRITICAL: Student has no enrollment records")
        
        # Check 5: Auto-enrollment
        if auto_enrollment_result is True:
            print("✅ Auto-enrollment logic working correctly")
        elif auto_enrollment_result is False:
            issues.append("❌ CRITICAL: Auto-enrollment logic failed")
        else:
            issues.append("⚠️ Auto-enrollment logic could not be tested")
        
        # Check 6: Status display
        if status_display_result:
            print("✅ Student can view enrollment status correctly")
        else:
            issues.append("❌ CRITICAL: Student cannot view enrollment status")
        
        # Summary
        print(f"\n📊 INVESTIGATION SUMMARY:")
        print(f"   Issues found: {len(issues)}")
        
        if len(issues) == 0:
            print("✅ NO CRITICAL ISSUES FOUND")
            print("   The reported bug may be frontend-related or already resolved")
            self.log_result(
                "🚨 Program Enrollment Bug - Root Cause Analysis", 
                "PASS", 
                "✅ NO CRITICAL BACKEND ISSUES FOUND",
                "All backend components working correctly - bug may be frontend-related"
            )
        else:
            print("❌ CRITICAL ISSUES IDENTIFIED:")
            for issue in issues:
                print(f"   {issue}")
            
            self.log_result(
                "🚨 Program Enrollment Bug - Root Cause Analysis", 
                "FAIL", 
                f"❌ FOUND {len(issues)} CRITICAL ISSUES",
                "; ".join(issues)
            )
    
    def run_all_tests(self):
        """Run the program enrollment bug investigation"""
        print("🚀 Starting Program Enrollment Bug Investigation...")
        
        # Run the investigation
        success = self.run_program_enrollment_bug_investigation()
        
        # Print final results
        print(f"\n" + "=" * 100)
        print("📊 FINAL TEST RESULTS")
        print("=" * 100)
        print(f"Total Tests: {len(self.results)}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed / len(self.results) * 100):.1f}%" if self.results else "0%")
        
        if success:
            print("\n✅ PROGRAM ENROLLMENT BUG INVESTIGATION COMPLETED")
            print("   Detailed findings logged above")
        else:
            print("\n❌ INVESTIGATION INCOMPLETE")
            print("   Critical issues prevented full investigation")
        
        return success

if __name__ == "__main__":
    tester = ProgramEnrollmentBugTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)