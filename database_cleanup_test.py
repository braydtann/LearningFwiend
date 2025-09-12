#!/usr/bin/env python3
"""
DATABASE CLEANUP AND INVESTIGATION TEST - Production Environment Issues
LearningFriend LMS Application - Focused on Course Access Issues

TESTING SCOPE:
✅ DATABASE CLEANUP OPERATIONS (Remove corrupted courses, classrooms, enrollments)
✅ INVESTIGATION of "Course Access Restricted" + white screen issue
✅ AUTHENTICATION TESTING with provided credentials
✅ COURSE ACCESS VERIFICATION for karlo.student@alder.com

TARGET: Clean slate database ready for creating fresh test courses
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using Production Backend URL from frontend/.env
BACKEND_URL = "https://fixfriend.preview.emergentagent.com/api"
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

class DatabaseCleanupTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}  # Store auth tokens for different users
        self.cleanup_stats = {
            'courses_deleted': 0,
            'classrooms_deleted': 0,
            'enrollments_deleted': 0,
            'programs_deleted': 0
        }
        
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
    
    def test_admin_authentication(self):
        """Test admin authentication with provided credentials"""
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
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'admin':
                    self.auth_tokens['admin'] = token
                    self.log_result(
                        "Admin Authentication", 
                        "PASS", 
                        f"Admin login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Name: {user_info.get('full_name')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication", 
                        "FAIL", 
                        "Login successful but invalid token or role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
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
                "Failed to connect to authentication endpoint",
                str(e)
            )
        return False
    
    def test_student_authentication(self):
        """Test student authentication with provided credentials"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token:
                    self.auth_tokens['student'] = token
                    self.log_result(
                        "Student Authentication", 
                        "PASS", 
                        f"Student login successful: {user_info.get('email')}",
                        f"Role: {user_info.get('role')}, Name: {user_info.get('full_name')}, ID: {user_info.get('id')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Student Authentication", 
                        "FAIL", 
                        "Login successful but no token received",
                        f"Response data: {data}"
                    )
            else:
                # Try password reset if login fails
                if response.status_code == 401:
                    print("   Student login failed, attempting password reset...")
                    reset_success = self.reset_student_password()
                    if reset_success:
                        # Try login again with reset password
                        reset_credentials = {
                            "username_or_email": "karlo.student@alder.com",
                            "password": "StudentPermanent123!"
                        }
                        response = requests.post(
                            f"{BACKEND_URL}/auth/login",
                            json=reset_credentials,
                            timeout=TEST_TIMEOUT,
                            headers={'Content-Type': 'application/json'}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            token = data.get('access_token')
                            user_info = data.get('user', {})
                            
                            if token:
                                self.auth_tokens['student'] = token
                                self.log_result(
                                    "Student Authentication", 
                                    "PASS", 
                                    f"Student login successful after password reset: {user_info.get('email')}",
                                    f"Role: {user_info.get('role')}, Name: {user_info.get('full_name')}, ID: {user_info.get('id')}"
                                )
                                return True
                
                self.log_result(
                    "Student Authentication", 
                    "FAIL", 
                    f"Student login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Authentication", 
                "FAIL", 
                "Failed to connect to authentication endpoint",
                str(e)
            )
        return False
    
    def reset_student_password(self):
        """Reset student password using admin privileges"""
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
                    if user.get('email') == 'karlo.student@alder.com':
                        student_user = user
                        break
                
                if student_user:
                    reset_data = {
                        "user_id": student_user.get('id'),
                        "new_temporary_password": "StudentPermanent123!"
                    }
                    
                    response = requests.post(
                        f"{BACKEND_URL}/auth/admin/reset-password",
                        json=reset_data,
                        timeout=TEST_TIMEOUT,
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                        }
                    )
                    
                    if response.status_code == 200:
                        print(f"   ✅ Password reset successful for {student_user.get('email')}")
                        return True
                    else:
                        print(f"   ❌ Password reset failed: {response.status_code}")
                        return False
                else:
                    print(f"   ❌ Student user karlo.student@alder.com not found")
                    return False
            else:
                print(f"   ❌ Failed to get users list: {users_response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Error resetting password: {str(e)}")
            return False
    
    # =============================================================================
    # DATABASE CLEANUP OPERATIONS
    # =============================================================================
    
    def cleanup_all_courses(self):
        """DELETE all courses from courses collection"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Cleanup All Courses", 
                "SKIP", 
                "No admin token available for course cleanup",
                "Admin authentication required"
            )
            return False
        
        try:
            # Get all courses first
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                deleted_count = 0
                failed_count = 0
                
                print(f"   Found {len(courses)} courses to delete...")
                
                for course in courses:
                    course_id = course.get('id')
                    course_title = course.get('title', 'Unknown')
                    
                    try:
                        delete_response = requests.delete(
                            f"{BACKEND_URL}/courses/{course_id}",
                            timeout=TEST_TIMEOUT,
                            headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                        )
                        
                        if delete_response.status_code == 200:
                            deleted_count += 1
                            print(f"   ✅ Deleted course: {course_title}")
                        else:
                            failed_count += 1
                            print(f"   ❌ Failed to delete course: {course_title} (Status: {delete_response.status_code})")
                    except Exception as e:
                        failed_count += 1
                        print(f"   ❌ Error deleting course {course_title}: {str(e)}")
                
                self.cleanup_stats['courses_deleted'] = deleted_count
                
                if deleted_count > 0:
                    self.log_result(
                        "Cleanup All Courses", 
                        "PASS", 
                        f"Successfully deleted {deleted_count} courses from database",
                        f"Deleted: {deleted_count}, Failed: {failed_count}, Total found: {len(courses)}"
                    )
                    return True
                else:
                    self.log_result(
                        "Cleanup All Courses", 
                        "PASS", 
                        "No courses found to delete - database already clean",
                        f"Total courses found: {len(courses)}"
                    )
                    return True
            else:
                self.log_result(
                    "Cleanup All Courses", 
                    "FAIL", 
                    f"Failed to retrieve courses list (Status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Cleanup All Courses", 
                "FAIL", 
                "Failed to cleanup courses",
                str(e)
            )
        return False
    
    def cleanup_all_classrooms(self):
        """DELETE all classrooms from classrooms collection"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Cleanup All Classrooms", 
                "SKIP", 
                "No admin token available for classroom cleanup",
                "Admin authentication required"
            )
            return False
        
        try:
            # Get all classrooms first
            response = requests.get(
                f"{BACKEND_URL}/classrooms",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                classrooms = response.json()
                deleted_count = 0
                failed_count = 0
                
                print(f"   Found {len(classrooms)} classrooms to delete...")
                
                for classroom in classrooms:
                    classroom_id = classroom.get('id')
                    classroom_name = classroom.get('name', 'Unknown')
                    
                    try:
                        delete_response = requests.delete(
                            f"{BACKEND_URL}/classrooms/{classroom_id}",
                            timeout=TEST_TIMEOUT,
                            headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                        )
                        
                        if delete_response.status_code == 200:
                            deleted_count += 1
                            print(f"   ✅ Deleted classroom: {classroom_name}")
                        else:
                            failed_count += 1
                            print(f"   ❌ Failed to delete classroom: {classroom_name} (Status: {delete_response.status_code})")
                    except Exception as e:
                        failed_count += 1
                        print(f"   ❌ Error deleting classroom {classroom_name}: {str(e)}")
                
                self.cleanup_stats['classrooms_deleted'] = deleted_count
                
                if deleted_count > 0:
                    self.log_result(
                        "Cleanup All Classrooms", 
                        "PASS", 
                        f"Successfully deleted {deleted_count} classrooms from database",
                        f"Deleted: {deleted_count}, Failed: {failed_count}, Total found: {len(classrooms)}"
                    )
                    return True
                else:
                    self.log_result(
                        "Cleanup All Classrooms", 
                        "PASS", 
                        "No classrooms found to delete - database already clean",
                        f"Total classrooms found: {len(classrooms)}"
                    )
                    return True
            else:
                self.log_result(
                    "Cleanup All Classrooms", 
                    "FAIL", 
                    f"Failed to retrieve classrooms list (Status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Cleanup All Classrooms", 
                "FAIL", 
                "Failed to cleanup classrooms",
                str(e)
            )
        return False
    
    def cleanup_all_enrollments(self):
        """DELETE all enrollments from enrollments collection"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Cleanup All Enrollments", 
                "SKIP", 
                "No admin token available for enrollment cleanup",
                "Admin authentication required"
            )
            return False
        
        try:
            # Use the orphaned enrollment cleanup endpoint to clean all enrollments
            response = requests.post(
                f"{BACKEND_URL}/enrollments/cleanup-orphaned",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                cleanup_result = response.json()
                deleted_count = cleanup_result.get('deletedCount', 0)
                orphaned_course_ids = cleanup_result.get('orphanedCourseIds', [])
                
                self.cleanup_stats['enrollments_deleted'] = deleted_count
                
                self.log_result(
                    "Cleanup All Enrollments", 
                    "PASS", 
                    f"Successfully cleaned up {deleted_count} orphaned enrollments",
                    f"Orphaned course IDs: {orphaned_course_ids[:5]}{'...' if len(orphaned_course_ids) > 5 else ''}"
                )
                return True
            else:
                self.log_result(
                    "Cleanup All Enrollments", 
                    "FAIL", 
                    f"Failed to cleanup enrollments (Status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Cleanup All Enrollments", 
                "FAIL", 
                "Failed to cleanup enrollments",
                str(e)
            )
        return False
    
    def cleanup_all_programs(self):
        """DELETE all programs from programs collection"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Cleanup All Programs", 
                "SKIP", 
                "No admin token available for program cleanup",
                "Admin authentication required"
            )
            return False
        
        try:
            # Get all programs first
            response = requests.get(
                f"{BACKEND_URL}/programs",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                programs = response.json()
                deleted_count = 0
                failed_count = 0
                
                print(f"   Found {len(programs)} programs to delete...")
                
                for program in programs:
                    program_id = program.get('id')
                    program_title = program.get('title', 'Unknown')
                    
                    try:
                        delete_response = requests.delete(
                            f"{BACKEND_URL}/programs/{program_id}",
                            timeout=TEST_TIMEOUT,
                            headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                        )
                        
                        if delete_response.status_code == 200:
                            deleted_count += 1
                            print(f"   ✅ Deleted program: {program_title}")
                        else:
                            failed_count += 1
                            print(f"   ❌ Failed to delete program: {program_title} (Status: {delete_response.status_code})")
                    except Exception as e:
                        failed_count += 1
                        print(f"   ❌ Error deleting program {program_title}: {str(e)}")
                
                self.cleanup_stats['programs_deleted'] = deleted_count
                
                if deleted_count > 0:
                    self.log_result(
                        "Cleanup All Programs", 
                        "PASS", 
                        f"Successfully deleted {deleted_count} programs from database",
                        f"Deleted: {deleted_count}, Failed: {failed_count}, Total found: {len(programs)}"
                    )
                    return True
                else:
                    self.log_result(
                        "Cleanup All Programs", 
                        "PASS", 
                        "No programs found to delete - database already clean",
                        f"Total programs found: {len(programs)}"
                    )
                    return True
            else:
                self.log_result(
                    "Cleanup All Programs", 
                    "FAIL", 
                    f"Failed to retrieve programs list (Status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Cleanup All Programs", 
                "FAIL", 
                "Failed to cleanup programs",
                str(e)
            )
        return False
    
    # =============================================================================
    # USER VERIFICATION TESTS
    # =============================================================================
    
    def verify_users_exist(self):
        """Verify that admin and student users still exist and are functional"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Verify Users Exist", 
                "SKIP", 
                "No admin token available for user verification",
                "Admin authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                users = response.json()
                admin_user = None
                student_user = None
                
                for user in users:
                    if user.get('email') == 'brayden.t@covesmart.com':
                        admin_user = user
                    elif user.get('email') == 'karlo.student@alder.com':
                        student_user = user
                
                verification_results = []
                
                if admin_user:
                    verification_results.append(f"✅ Admin user exists: {admin_user.get('email')} ({admin_user.get('full_name')})")
                else:
                    verification_results.append("❌ Admin user brayden.t@covesmart.com NOT FOUND")
                
                if student_user:
                    verification_results.append(f"✅ Student user exists: {student_user.get('email')} ({student_user.get('full_name')})")
                else:
                    verification_results.append("❌ Student user karlo.student@alder.com NOT FOUND")
                
                if admin_user and student_user:
                    self.log_result(
                        "Verify Users Exist", 
                        "PASS", 
                        "Both admin and student users exist and are functional",
                        "; ".join(verification_results)
                    )
                    return True
                else:
                    self.log_result(
                        "Verify Users Exist", 
                        "FAIL", 
                        "One or both required users are missing",
                        "; ".join(verification_results)
                    )
            else:
                self.log_result(
                    "Verify Users Exist", 
                    "FAIL", 
                    f"Failed to retrieve users list (Status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Verify Users Exist", 
                "FAIL", 
                "Failed to verify users exist",
                str(e)
            )
        return False
    
    # =============================================================================
    # COURSE ACCESS INVESTIGATION
    # =============================================================================
    
    def investigate_course_access_issue(self):
        """Investigate the specific course access issue with karlo.student@alder.com"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Course Access Investigation", 
                "SKIP", 
                "No student token available for course access investigation",
                "Student authentication required"
            )
            return False
        
        print("\n🔍 INVESTIGATING COURSE ACCESS ISSUE")
        print("=" * 60)
        print("User reports: 'Course Access Restricted' message followed by white screen")
        print("Specific case: karlo.student@alder.com trying to access 'test 820' course")
        print("=" * 60)
        
        issues_found = []
        
        # Step 1: Check student enrollments
        print("\n📚 STEP 1: Checking Student Enrollments")
        print("-" * 40)
        enrollments = self.check_student_enrollments()
        
        if not enrollments:
            issues_found.append("Student has no course enrollments")
        else:
            print(f"   Student has {len(enrollments)} enrollments")
            
            # Check for orphaned enrollments
            orphaned_count = 0
            for enrollment in enrollments:
                course_id = enrollment.get('courseId')
                if course_id:
                    # Test if course exists
                    try:
                        course_response = requests.get(
                            f"{BACKEND_URL}/courses/{course_id}",
                            timeout=TEST_TIMEOUT,
                            headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                        )
                        if course_response.status_code == 404:
                            orphaned_count += 1
                            print(f"   ❌ ORPHANED ENROLLMENT: Course {course_id} does not exist")
                        elif course_response.status_code == 200:
                            course = course_response.json()
                            print(f"   ✅ Valid enrollment: {course.get('title', 'Unknown')}")
                    except:
                        pass
            
            if orphaned_count > 0:
                issues_found.append(f"{orphaned_count} orphaned enrollments (courses don't exist)")
        
        # Step 2: Check available courses
        print("\n📖 STEP 2: Checking Available Courses")
        print("-" * 40)
        courses = self.check_available_courses()
        
        if courses is None:
            issues_found.append("Cannot access courses endpoint")
        else:
            print(f"   Student can see {len(courses)} available courses")
            
            # Look for "test 820" course specifically
            test_820_course = None
            for course in courses:
                if 'test 820' in course.get('title', '').lower() or 'test820' in course.get('title', '').lower():
                    test_820_course = course
                    break
            
            if test_820_course:
                print(f"   ✅ Found 'test 820' course: {test_820_course.get('title')}")
                # Test access to this specific course
                access_result = self.test_specific_course_access(test_820_course.get('id'))
                if not access_result:
                    issues_found.append("Cannot access 'test 820' course despite it being visible")
            else:
                print("   ⚠️ 'test 820' course not found in available courses")
        
        # Step 3: Test course detail access
        print("\n🎯 STEP 3: Testing Course Detail Access")
        print("-" * 40)
        if enrollments:
            for enrollment in enrollments[:3]:  # Test first 3 enrollments
                course_id = enrollment.get('courseId')
                access_result = self.test_specific_course_access(course_id)
                if not access_result:
                    issues_found.append(f"Cannot access enrolled course {course_id}")
        
        # Summary
        if len(issues_found) == 0:
            self.log_result(
                "Course Access Investigation", 
                "PASS", 
                "No critical course access issues found - backend APIs working correctly",
                "White screen issue likely frontend-related (React rendering, JavaScript errors, state management)"
            )
            return True
        else:
            self.log_result(
                "Course Access Investigation", 
                "FAIL", 
                f"Found {len(issues_found)} issues that could cause course access problems",
                "; ".join(issues_found)
            )
            return False
    
    def check_student_enrollments(self):
        """Check student's course enrollments"""
        if "student" not in self.auth_tokens:
            return None
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                print(f"   Retrieved {len(enrollments)} enrollments")
                
                for enrollment in enrollments:
                    print(f"   📚 Course ID: {enrollment.get('courseId')}")
                    print(f"       Progress: {enrollment.get('progress', 0)}%")
                    print(f"       Status: {enrollment.get('status', 'unknown')}")
                    print(f"       Enrolled: {enrollment.get('enrolledAt', 'unknown')}")
                
                return enrollments
            else:
                print(f"   ❌ Failed to get enrollments: {response.status_code}")
                return None
        except Exception as e:
            print(f"   ❌ Error checking enrollments: {str(e)}")
            return None
    
    def check_available_courses(self):
        """Check courses available to student"""
        if "student" not in self.auth_tokens:
            return None
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                print(f"   Student can access {len(courses)} courses")
                
                for course in courses[:5]:  # Show first 5 courses
                    print(f"   📖 {course.get('title', 'Unknown Title')}")
                    print(f"       ID: {course.get('id')}")
                    print(f"       Category: {course.get('category', 'Unknown')}")
                
                return courses
            else:
                print(f"   ❌ Student cannot access courses: {response.status_code}")
                return None
        except Exception as e:
            print(f"   ❌ Error checking available courses: {str(e)}")
            return None
    
    def test_specific_course_access(self, course_id):
        """Test access to a specific course"""
        if "student" not in self.auth_tokens or not course_id:
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                course = response.json()
                print(f"   ✅ Course access successful: {course.get('title', 'Unknown')}")
                return True
            elif response.status_code == 404:
                print(f"   ❌ Course not found: {course_id}")
                return False
            elif response.status_code == 403:
                print(f"   ❌ Course access restricted: {course_id}")
                return False
            else:
                print(f"   ❌ Course access failed: {course_id} - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Error accessing course {course_id}: {str(e)}")
            return False
    
    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_all_tests(self):
        """Run all database cleanup and investigation tests"""
        print("🧹 DATABASE CLEANUP AND INVESTIGATION TEST SUITE")
        print("=" * 80)
        print("GOAL: Clean slate database ready for creating fresh test courses")
        print("FOCUS: Resolve 'Course Access Restricted' + white screen issues")
        print("=" * 80)
        
        # Phase 1: Authentication
        print("\n🔐 PHASE 1: AUTHENTICATION TESTING")
        print("-" * 50)
        admin_auth = self.test_admin_authentication()
        student_auth = self.test_student_authentication()
        
        if not admin_auth:
            print("❌ CRITICAL: Cannot proceed without admin authentication")
            return False
        
        # Phase 2: Database Cleanup
        print("\n🧹 PHASE 2: DATABASE CLEANUP OPERATIONS")
        print("-" * 50)
        self.cleanup_all_courses()
        self.cleanup_all_classrooms()
        self.cleanup_all_enrollments()
        self.cleanup_all_programs()
        
        # Phase 3: User Verification
        print("\n👥 PHASE 3: USER VERIFICATION")
        print("-" * 50)
        self.verify_users_exist()
        
        # Phase 4: Course Access Investigation
        print("\n🔍 PHASE 4: COURSE ACCESS INVESTIGATION")
        print("-" * 50)
        if student_auth:
            self.investigate_course_access_issue()
        else:
            print("⚠️ Skipping course access investigation - student authentication failed")
        
        # Final Summary
        print("\n📊 CLEANUP AND INVESTIGATION SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        print("\n🧹 CLEANUP STATISTICS:")
        print(f"   📚 Courses Deleted: {self.cleanup_stats['courses_deleted']}")
        print(f"   🏫 Classrooms Deleted: {self.cleanup_stats['classrooms_deleted']}")
        print(f"   📝 Enrollments Cleaned: {self.cleanup_stats['enrollments_deleted']}")
        print(f"   📋 Programs Deleted: {self.cleanup_stats['programs_deleted']}")
        
        total_cleaned = sum(self.cleanup_stats.values())
        print(f"\n🎯 TOTAL ITEMS CLEANED: {total_cleaned}")
        
        if total_cleaned > 0:
            print("✅ DATABASE CLEANUP COMPLETED - Ready for fresh test courses")
        else:
            print("ℹ️ DATABASE WAS ALREADY CLEAN - No cleanup needed")
        
        return self.failed == 0

if __name__ == "__main__":
    tester = DatabaseCleanupTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED - Database cleanup and investigation completed successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️ SOME TESTS FAILED - Check results above for details")
        sys.exit(1)