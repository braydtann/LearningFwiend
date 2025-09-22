#!/usr/bin/env python3
"""
🎯 STUDENT DASHBOARD ENROLLED PROGRAMS FUNCTIONALITY TESTING
LearningFwiend LMS Application Backend API Testing

TESTING OBJECTIVES (from review request):
1. Authentication Test: Login with existing student credentials (karlo.student@alder.com / StudentPermanent123!)
2. Classroom Enrollment Check: Get all classrooms and find ones where this student is enrolled
3. Programs Data Integrity: Get all programs that should be accessible to this student
4. Student Dashboard Data Flow: Test the loadEnrolledPrograms function logic
5. Final Test Access: Check if /final-test/program/{programId} endpoint exists

GOAL: Understand why the "Enrolled Programs" section might not be showing up on the student dashboard
and ensure the final exam access is working properly.

Admin credentials: brayden.t@covesmart.com / Hawaii2020!
Student credentials: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Using the backend URL from supervisor config
BACKEND_URL = "https://lms-bug-fixes.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class StudentDashboardTester:
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
    # AUTHENTICATION TESTS
    # =============================================================================
    
    def test_student_authentication(self):
        """Test 1: Login with existing student credentials"""
        print("\n🔐 TEST 1: Student Authentication")
        print("=" * 60)
        print(f"Testing login with: {STUDENT_CREDENTIALS['username_or_email']}")
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token:
                    self.auth_tokens['student'] = token
                    self.log_result(
                        "Student Authentication", 
                        "PASS", 
                        f"✅ Student login successful: {user_info.get('full_name', 'Unknown')} ({user_info.get('role', 'Unknown')})",
                        f"User ID: {user_info.get('id')}, Email: {user_info.get('email')}"
                    )
                    
                    # Check if password change is required
                    requires_password_change = data.get('requires_password_change', False)
                    if requires_password_change:
                        print("⚠️ Note: Student account requires password change on first login")
                    
                    return True
                else:
                    self.log_result(
                        "Student Authentication", 
                        "FAIL", 
                        "❌ No access token received in response",
                        f"Response: {data}"
                    )
                    return False
            else:
                self.log_result(
                    "Student Authentication", 
                    "FAIL", 
                    f"❌ Login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Student Authentication", 
                "FAIL", 
                f"❌ Authentication error: {str(e)}",
                "Network or server error during login"
            )
            return False
    
    def test_admin_authentication(self):
        """Helper: Authenticate admin for additional checks"""
        print("\n🔑 Admin Authentication (for additional checks)")
        print("-" * 50)
        
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
                if token:
                    self.auth_tokens['admin'] = token
                    print(f"✅ Admin authenticated: {data.get('user', {}).get('full_name', 'Unknown')}")
                    return True
            
            print(f"❌ Admin authentication failed: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"❌ Admin authentication error: {str(e)}")
            return False
    
    # =============================================================================
    # CLASSROOM ENROLLMENT TESTS
    # =============================================================================
    
    def test_classroom_enrollment_check(self):
        """Test 2: Get all classrooms and find ones where this student is enrolled"""
        print("\n🏫 TEST 2: Classroom Enrollment Check")
        print("=" * 60)
        
        if 'student' not in self.auth_tokens:
            self.log_result(
                "Classroom Enrollment Check", 
                "FAIL", 
                "❌ Cannot test - student not authenticated",
                "Student authentication required for this test"
            )
            return []
        
        try:
            # Get student's current user info
            student_response = requests.get(
                f"{BACKEND_URL}/auth/me",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if student_response.status_code != 200:
                self.log_result(
                    "Classroom Enrollment Check", 
                    "FAIL", 
                    f"❌ Cannot get student info: {student_response.status_code}",
                    student_response.text
                )
                return []
            
            student_info = student_response.json()
            student_id = student_info.get('id')
            
            print(f"Student ID: {student_id}")
            print(f"Student Name: {student_info.get('full_name')}")
            
            # Get all classrooms (need admin access for this)
            if 'admin' not in self.auth_tokens:
                admin_success = self.test_admin_authentication()
                if not admin_success:
                    self.log_result(
                        "Classroom Enrollment Check", 
                        "FAIL", 
                        "❌ Cannot get classrooms - admin access required",
                        "Need admin access to list all classrooms"
                    )
                    return []
            
            classrooms_response = requests.get(
                f"{BACKEND_URL}/classrooms",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if classrooms_response.status_code == 200:
                all_classrooms = classrooms_response.json()
                print(f"📚 Total classrooms in system: {len(all_classrooms)}")
                
                # Find classrooms where this student is enrolled
                student_classrooms = []
                for classroom in all_classrooms:
                    student_ids = classroom.get('studentIds', [])
                    if student_id in student_ids:
                        student_classrooms.append(classroom)
                
                print(f"🎓 Student enrolled in {len(student_classrooms)} classrooms:")
                
                classroom_details = []
                for i, classroom in enumerate(student_classrooms):
                    print(f"\n   📋 Classroom {i+1}: {classroom.get('title', 'Untitled')}")
                    print(f"      ID: {classroom.get('id')}")
                    print(f"      Programs: {len(classroom.get('programIds', []))} programs")
                    print(f"      Courses: {len(classroom.get('courseIds', []))} direct courses")
                    print(f"      Students: {len(classroom.get('studentIds', []))} total students")
                    print(f"      Active: {classroom.get('isActive', False)}")
                    
                    classroom_details.append({
                        'id': classroom.get('id'),
                        'title': classroom.get('title'),
                        'programIds': classroom.get('programIds', []),
                        'courseIds': classroom.get('courseIds', []),
                        'studentCount': len(classroom.get('studentIds', [])),
                        'isActive': classroom.get('isActive', False)
                    })
                
                if len(student_classrooms) > 0:
                    self.log_result(
                        "Classroom Enrollment Check", 
                        "PASS", 
                        f"✅ Student enrolled in {len(student_classrooms)} classrooms with programs",
                        f"Classrooms: {[c.get('title') for c in student_classrooms]}"
                    )
                else:
                    self.log_result(
                        "Classroom Enrollment Check", 
                        "FAIL", 
                        "❌ Student not enrolled in any classrooms",
                        "This explains why no enrolled programs are showing"
                    )
                
                return classroom_details
            else:
                self.log_result(
                    "Classroom Enrollment Check", 
                    "FAIL", 
                    f"❌ Failed to get classrooms: {classrooms_response.status_code}",
                    classrooms_response.text
                )
                return []
                
        except Exception as e:
            self.log_result(
                "Classroom Enrollment Check", 
                "FAIL", 
                f"❌ Error checking classroom enrollment: {str(e)}",
                "Network or server error"
            )
            return []
    
    # =============================================================================
    # PROGRAMS DATA INTEGRITY TESTS
    # =============================================================================
    
    def test_programs_data_integrity(self, student_classrooms):
        """Test 3: Get all programs that should be accessible to this student"""
        print("\n📚 TEST 3: Programs Data Integrity")
        print("=" * 60)
        
        if not student_classrooms:
            self.log_result(
                "Programs Data Integrity", 
                "FAIL", 
                "❌ No classrooms found - cannot check program access",
                "Student must be enrolled in classrooms with programs"
            )
            return []
        
        try:
            # Get all programs
            programs_response = requests.get(
                f"{BACKEND_URL}/programs",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if programs_response.status_code == 200:
                all_programs = programs_response.json()
                print(f"📖 Total programs in system: {len(all_programs)}")
                
                # Find programs that student should have access to
                accessible_program_ids = set()
                for classroom in student_classrooms:
                    program_ids = classroom.get('programIds', [])
                    accessible_program_ids.update(program_ids)
                
                print(f"🎯 Programs student should access: {len(accessible_program_ids)}")
                
                accessible_programs = []
                program_details = []
                
                for program_id in accessible_program_ids:
                    # Find the program details
                    program = next((p for p in all_programs if p.get('id') == program_id), None)
                    if program:
                        accessible_programs.append(program)
                        
                        print(f"\n   📋 Program: {program.get('title', 'Untitled')}")
                        print(f"      ID: {program.get('id')}")
                        print(f"      Courses: {len(program.get('courseIds', []))} courses")
                        print(f"      Instructor: {program.get('instructor', 'Unknown')}")
                        print(f"      Active: {program.get('isActive', False)}")
                        
                        # Check if courses in program exist
                        course_ids = program.get('courseIds', [])
                        valid_courses = self.check_program_courses(course_ids)
                        
                        program_details.append({
                            'id': program.get('id'),
                            'title': program.get('title'),
                            'courseIds': course_ids,
                            'courseCount': len(course_ids),
                            'validCourses': len(valid_courses),
                            'isActive': program.get('isActive', False),
                            'instructor': program.get('instructor')
                        })
                    else:
                        print(f"   ❌ Program {program_id} not found in system!")
                
                if len(accessible_programs) > 0:
                    total_courses = sum(len(p.get('courseIds', [])) for p in accessible_programs)
                    self.log_result(
                        "Programs Data Integrity", 
                        "PASS", 
                        f"✅ Found {len(accessible_programs)} accessible programs with {total_courses} total courses",
                        f"Programs: {[p.get('title') for p in accessible_programs]}"
                    )
                else:
                    self.log_result(
                        "Programs Data Integrity", 
                        "FAIL", 
                        "❌ No accessible programs found despite classroom enrollment",
                        f"Expected program IDs: {list(accessible_program_ids)}"
                    )
                
                return program_details
            else:
                self.log_result(
                    "Programs Data Integrity", 
                    "FAIL", 
                    f"❌ Failed to get programs: {programs_response.status_code}",
                    programs_response.text
                )
                return []
                
        except Exception as e:
            self.log_result(
                "Programs Data Integrity", 
                "FAIL", 
                f"❌ Error checking programs: {str(e)}",
                "Network or server error"
            )
            return []
    
    def check_program_courses(self, course_ids):
        """Helper: Check if courses in program exist and are accessible"""
        valid_courses = []
        
        for course_id in course_ids:
            try:
                course_response = requests.get(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                )
                
                if course_response.status_code == 200:
                    course = course_response.json()
                    valid_courses.append(course)
                    print(f"      ✅ Course: {course.get('title', 'Untitled')} (ID: {course_id})")
                else:
                    print(f"      ❌ Course {course_id} not accessible: {course_response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Error checking course {course_id}: {str(e)}")
        
        return valid_courses
    
    # =============================================================================
    # STUDENT DASHBOARD DATA FLOW TESTS
    # =============================================================================
    
    def test_student_dashboard_data_flow(self, program_details):
        """Test 4: Test the loadEnrolledPrograms function logic"""
        print("\n📊 TEST 4: Student Dashboard Data Flow")
        print("=" * 60)
        
        if 'student' not in self.auth_tokens:
            self.log_result(
                "Student Dashboard Data Flow", 
                "FAIL", 
                "❌ Cannot test - student not authenticated",
                "Student authentication required"
            )
            return False
        
        try:
            # Step 1: Get student's enrollments
            print("Step 1: Getting student enrollments...")
            enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if enrollments_response.status_code != 200:
                self.log_result(
                    "Student Dashboard Data Flow", 
                    "FAIL", 
                    f"❌ Cannot get student enrollments: {enrollments_response.status_code}",
                    enrollments_response.text
                )
                return False
            
            enrollments = enrollments_response.json()
            print(f"   📚 Student has {len(enrollments)} total enrollments")
            
            # Step 2: Calculate program completion status
            print("\nStep 2: Calculating program completion...")
            program_completion = {}
            
            for program in program_details:
                program_id = program['id']
                program_title = program['title']
                course_ids = program['courseIds']
                
                print(f"\n   📋 Analyzing program: {program_title}")
                print(f"      Program courses: {len(course_ids)}")
                
                # Find enrollments for this program's courses
                program_enrollments = []
                for enrollment in enrollments:
                    if enrollment.get('courseId') in course_ids:
                        program_enrollments.append(enrollment)
                
                print(f"      Student enrolled in: {len(program_enrollments)} of {len(course_ids)} courses")
                
                # Calculate completion percentage
                if len(course_ids) > 0:
                    enrolled_percentage = (len(program_enrollments) / len(course_ids)) * 100
                    
                    # Calculate progress percentage
                    total_progress = sum(e.get('progress', 0) for e in program_enrollments)
                    avg_progress = total_progress / len(program_enrollments) if program_enrollments else 0
                    
                    # Check if program is completed (all courses 100%)
                    completed_courses = [e for e in program_enrollments if e.get('progress', 0) >= 100]
                    is_completed = len(completed_courses) == len(course_ids) and len(course_ids) > 0
                    
                    program_completion[program_id] = {
                        'title': program_title,
                        'total_courses': len(course_ids),
                        'enrolled_courses': len(program_enrollments),
                        'completed_courses': len(completed_courses),
                        'enrolled_percentage': enrolled_percentage,
                        'avg_progress': avg_progress,
                        'is_completed': is_completed,
                        'enrollments': program_enrollments
                    }
                    
                    print(f"      Enrollment: {enrolled_percentage:.1f}%")
                    print(f"      Progress: {avg_progress:.1f}%")
                    print(f"      Completed: {'✅ YES' if is_completed else '❌ NO'}")
                else:
                    print(f"      ⚠️ Program has no courses")
            
            # Step 3: Summary
            print(f"\n📊 PROGRAM COMPLETION SUMMARY:")
            completed_programs = [p for p in program_completion.values() if p['is_completed']]
            in_progress_programs = [p for p in program_completion.values() if not p['is_completed'] and p['enrolled_courses'] > 0]
            
            print(f"   ✅ Completed programs: {len(completed_programs)}")
            print(f"   📚 In-progress programs: {len(in_progress_programs)}")
            print(f"   📖 Total accessible programs: {len(program_completion)}")
            
            if len(program_completion) > 0:
                self.log_result(
                    "Student Dashboard Data Flow", 
                    "PASS", 
                    f"✅ Dashboard data flow working: {len(completed_programs)} completed, {len(in_progress_programs)} in progress",
                    f"Total programs analyzed: {len(program_completion)}"
                )
                return program_completion
            else:
                self.log_result(
                    "Student Dashboard Data Flow", 
                    "FAIL", 
                    "❌ No program data available for dashboard",
                    "Student has no accessible programs"
                )
                return {}
                
        except Exception as e:
            self.log_result(
                "Student Dashboard Data Flow", 
                "FAIL", 
                f"❌ Error in dashboard data flow: {str(e)}",
                "Network or server error"
            )
            return {}
    
    # =============================================================================
    # FINAL TEST ACCESS TESTS
    # =============================================================================
    
    def test_final_test_access(self, program_completion):
        """Test 5: Check if /final-test/program/{programId} endpoint exists"""
        print("\n🎯 TEST 5: Final Test Access")
        print("=" * 60)
        
        if not program_completion:
            self.log_result(
                "Final Test Access", 
                "FAIL", 
                "❌ No programs available to test final exam access",
                "Need completed programs to test final exam functionality"
            )
            return False
        
        try:
            # Test final exam access for completed programs
            completed_programs = [p for p in program_completion.values() if p['is_completed']]
            accessible_programs = list(program_completion.keys())
            
            print(f"Testing final exam access for {len(accessible_programs)} programs...")
            
            final_test_results = []
            
            for program_id in accessible_programs:
                program_info = program_completion[program_id]
                program_title = program_info['title']
                is_completed = program_info['is_completed']
                
                print(f"\n   📋 Testing: {program_title}")
                print(f"      Program ID: {program_id}")
                print(f"      Completed: {'✅ YES' if is_completed else '❌ NO'}")
                
                # Test final exam endpoint
                try:
                    final_test_response = requests.get(
                        f"{BACKEND_URL}/final-test/program/{program_id}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                    )
                    
                    print(f"      Final test endpoint: {final_test_response.status_code}")
                    
                    if final_test_response.status_code == 200:
                        final_test_data = final_test_response.json()
                        print(f"      ✅ Final test accessible")
                        final_test_results.append({
                            'program_id': program_id,
                            'program_title': program_title,
                            'accessible': True,
                            'completed': is_completed,
                            'response': final_test_data
                        })
                    elif final_test_response.status_code == 404:
                        print(f"      ❌ Final test endpoint not found")
                        final_test_results.append({
                            'program_id': program_id,
                            'program_title': program_title,
                            'accessible': False,
                            'completed': is_completed,
                            'error': 'Endpoint not found'
                        })
                    elif final_test_response.status_code == 403:
                        print(f"      ⚠️ Final test access denied (may require completion)")
                        final_test_results.append({
                            'program_id': program_id,
                            'program_title': program_title,
                            'accessible': False,
                            'completed': is_completed,
                            'error': 'Access denied'
                        })
                    else:
                        print(f"      ❌ Unexpected response: {final_test_response.status_code}")
                        final_test_results.append({
                            'program_id': program_id,
                            'program_title': program_title,
                            'accessible': False,
                            'completed': is_completed,
                            'error': f'HTTP {final_test_response.status_code}'
                        })
                        
                except Exception as e:
                    print(f"      ❌ Error testing final exam: {str(e)}")
                    final_test_results.append({
                        'program_id': program_id,
                        'program_title': program_title,
                        'accessible': False,
                        'completed': is_completed,
                        'error': str(e)
                    })
            
            # Summary
            accessible_finals = [r for r in final_test_results if r['accessible']]
            
            print(f"\n🎯 FINAL TEST ACCESS SUMMARY:")
            print(f"   Programs tested: {len(final_test_results)}")
            print(f"   Final tests accessible: {len(accessible_finals)}")
            print(f"   Completed programs: {len(completed_programs)}")
            
            if len(accessible_finals) > 0:
                self.log_result(
                    "Final Test Access", 
                    "PASS", 
                    f"✅ Final test access working: {len(accessible_finals)} programs have accessible final exams",
                    f"Accessible: {[r['program_title'] for r in accessible_finals]}"
                )
            else:
                # Check if this is expected (no completed programs) or an error
                if len(completed_programs) == 0:
                    self.log_result(
                        "Final Test Access", 
                        "PASS", 
                        "✅ No final tests accessible (expected - no completed programs)",
                        "Student needs to complete programs before accessing final exams"
                    )
                else:
                    self.log_result(
                        "Final Test Access", 
                        "FAIL", 
                        f"❌ Final test endpoint not working despite {len(completed_programs)} completed programs",
                        "Final exam functionality may not be implemented"
                    )
            
            return final_test_results
            
        except Exception as e:
            self.log_result(
                "Final Test Access", 
                "FAIL", 
                f"❌ Error testing final exam access: {str(e)}",
                "Network or server error"
            )
            return []
    
    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_comprehensive_test(self):
        """Run all student dashboard enrolled programs tests"""
        print("🎯 STUDENT DASHBOARD ENROLLED PROGRAMS FUNCTIONALITY TESTING")
        print("=" * 80)
        print("GOAL: Understand why 'Enrolled Programs' section might not be showing")
        print("      and ensure final exam access is working properly")
        print("=" * 80)
        
        # Test 1: Student Authentication
        auth_success = self.test_student_authentication()
        if not auth_success:
            print("\n❌ CRITICAL: Cannot proceed without student authentication")
            return False
        
        # Test 2: Classroom Enrollment Check
        student_classrooms = self.test_classroom_enrollment_check()
        
        # Test 3: Programs Data Integrity
        program_details = self.test_programs_data_integrity(student_classrooms)
        
        # Test 4: Student Dashboard Data Flow
        program_completion = self.test_student_dashboard_data_flow(program_details)
        
        # Test 5: Final Test Access
        final_test_results = self.test_final_test_access(program_completion)
        
        # Final Summary
        self.print_final_summary(student_classrooms, program_details, program_completion, final_test_results)
        
        return self.passed > self.failed
    
    def print_final_summary(self, student_classrooms, program_details, program_completion, final_test_results):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 STUDENT DASHBOARD ENROLLED PROGRAMS - FINAL SUMMARY")
        print("=" * 80)
        
        print(f"\n📊 TEST RESULTS:")
        print(f"   ✅ Passed: {self.passed}")
        print(f"   ❌ Failed: {self.failed}")
        print(f"   📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        
        # Check why "Enrolled Programs" might not be showing
        if not student_classrooms:
            print("   ❌ CRITICAL ISSUE: Student not enrolled in any classrooms")
            print("      → This explains why 'Enrolled Programs' section is empty")
            print("      → Solution: Enroll student in classrooms with programs")
        elif not program_details:
            print("   ❌ CRITICAL ISSUE: Classrooms have no programs assigned")
            print("      → Student is in classrooms but they contain no programs")
            print("      → Solution: Assign programs to student's classrooms")
        elif not program_completion:
            print("   ❌ CRITICAL ISSUE: Programs exist but student has no course enrollments")
            print("      → Programs are assigned but auto-enrollment may not be working")
            print("      → Solution: Check auto-enrollment logic in classroom assignment")
        else:
            print("   ✅ ENROLLED PROGRAMS DATA AVAILABLE:")
            print(f"      → Student in {len(student_classrooms)} classrooms")
            print(f"      → Access to {len(program_details)} programs")
            print(f"      → {len([p for p in program_completion.values() if p['is_completed']])} completed programs")
            print(f"      → {len([p for p in program_completion.values() if not p['is_completed'] and p['enrolled_courses'] > 0])} in-progress programs")
        
        print(f"\n🎯 FINAL EXAM ACCESS:")
        if final_test_results:
            accessible_finals = [r for r in final_test_results if r['accessible']]
            if accessible_finals:
                print(f"   ✅ Final exams accessible for {len(accessible_finals)} programs")
            else:
                print(f"   ❌ No final exams accessible (may need endpoint implementation)")
        else:
            print(f"   ⚠️ Cannot test final exams - no programs available")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if not student_classrooms:
            print("   1. Enroll karlo.student@alder.com in classrooms with programs")
            print("   2. Verify classroom auto-enrollment is working")
        elif not program_details:
            print("   1. Assign programs to student's existing classrooms")
            print("   2. Verify program-classroom relationships")
        elif not program_completion:
            print("   1. Check auto-enrollment logic when students are added to classrooms")
            print("   2. Manually enroll student in program courses if needed")
        else:
            print("   1. Enrolled Programs functionality should be working")
            print("   2. Check frontend StudentDashboard.js loadEnrolledPrograms() function")
            print("   3. Verify API calls are reaching the backend correctly")
        
        if not final_test_results or not any(r['accessible'] for r in final_test_results):
            print("   4. Implement /final-test/program/{programId} endpoint if missing")
            print("   5. Verify final exam access logic for completed programs")

def main():
    """Main test execution"""
    tester = StudentDashboardTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print(f"\n🎉 TESTING COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print(f"\n❌ TESTING COMPLETED WITH ISSUES")
        sys.exit(1)

if __name__ == "__main__":
    main()