#!/usr/bin/env python3
"""
Student Authentication Debugging Test for White Screen Issue
Focus: karlo.student@alder.com authentication and course access
"""

import requests
import json
import os
import sys
from datetime import datetime
import time

# Configuration - Using Production Backend URL from frontend/.env
BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

class StudentAuthTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        
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
    
    def test_admin_login(self):
        """Test admin login to get admin access for user management"""
        try:
            login_data = {
                "username_or_email": "brayden.t@covesmart.com",
                "password": "Hawaii2020!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
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
                        "Admin Login", 
                        "PASS", 
                        f"Admin login successful: {user_info.get('email')}",
                        f"Token received, role: {user_info.get('role')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Login", 
                        "FAIL", 
                        "Admin login failed - invalid token or role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Admin Login", 
                    "FAIL", 
                    f"Admin login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Login", 
                "FAIL", 
                "Admin login request failed",
                str(e)
            )
        return False
    
    def find_student_in_system(self):
        """Find karlo.student@alder.com in the system"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Find Student in System", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return None
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                users = response.json()
                target_student = None
                
                for user in users:
                    if user.get('email') == 'karlo.student@alder.com':
                        target_student = user
                        break
                
                if target_student:
                    self.log_result(
                        "Find Student in System", 
                        "PASS", 
                        f"Found student: {target_student.get('email')}",
                        f"ID: {target_student.get('id')}, Name: {target_student.get('full_name')}, Role: {target_student.get('role')}"
                    )
                    return target_student
                else:
                    self.log_result(
                        "Find Student in System", 
                        "FAIL", 
                        "Student karlo.student@alder.com not found in system",
                        f"Searched {len(users)} users"
                    )
                    return None
            else:
                self.log_result(
                    "Find Student in System", 
                    "FAIL", 
                    f"Failed to get users list: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Find Student in System", 
                "FAIL", 
                "Failed to search for student",
                str(e)
            )
        return None
    
    def reset_student_password(self, student):
        """Reset student password to StudentPermanent123!"""
        if "admin" not in self.auth_tokens:
            return False
        
        try:
            reset_data = {
                "user_id": student.get('id'),
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
                reset_info = response.json()
                self.log_result(
                    "Reset Student Password", 
                    "PASS", 
                    f"Password reset successful for {student.get('email')}",
                    f"New password: StudentPermanent123!, Reset at: {reset_info.get('reset_at')}"
                )
                return True
            else:
                self.log_result(
                    "Reset Student Password", 
                    "FAIL", 
                    f"Password reset failed: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Reset Student Password", 
                "FAIL", 
                "Password reset request failed",
                str(e)
            )
        return False
    
    def test_student_login(self, student):
        """Test student login with the reset password"""
        try:
            login_data = {
                "username_or_email": student.get('email'),
                "password": "StudentPermanent123!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                requires_password_change = data.get('requires_password_change', False)
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['student'] = token
                    self.log_result(
                        "Student Login", 
                        "PASS", 
                        f"Student login successful: {user_info.get('email')}",
                        f"Token received, Role: {user_info.get('role')}, Password change required: {requires_password_change}"
                    )
                    return True
                else:
                    self.log_result(
                        "Student Login", 
                        "FAIL", 
                        "Student login failed - invalid token or role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Student Login", 
                    "FAIL", 
                    f"Student login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Login", 
                "FAIL", 
                "Student login request failed",
                str(e)
            )
        return False
    
    def test_student_enrollments(self):
        """Test student's course enrollments"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Student Enrollments", 
                "SKIP", 
                "No student token available",
                "Student authentication required"
            )
            return None
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                self.log_result(
                    "Student Enrollments", 
                    "PASS", 
                    f"Retrieved {len(enrollments)} enrollments for student",
                    f"Enrollments: {[{'courseId': e.get('courseId'), 'progress': e.get('progress', 0)} for e in enrollments]}"
                )
                return enrollments
            else:
                self.log_result(
                    "Student Enrollments", 
                    "FAIL", 
                    f"Failed to get enrollments: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Enrollments", 
                "FAIL", 
                "Failed to get student enrollments",
                str(e)
            )
        return None
    
    def test_student_courses_access(self):
        """Test student access to courses endpoint"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Student Courses Access", 
                "SKIP", 
                "No student token available",
                "Student authentication required"
            )
            return None
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                self.log_result(
                    "Student Courses Access", 
                    "PASS", 
                    f"Student can access courses endpoint - {len(courses)} courses available",
                    f"Sample courses: {[{'id': c.get('id'), 'title': c.get('title')} for c in courses[:3]]}"
                )
                return courses
            else:
                self.log_result(
                    "Student Courses Access", 
                    "FAIL", 
                    f"Student cannot access courses: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Courses Access", 
                "FAIL", 
                "Failed to test student courses access",
                str(e)
            )
        return None
    
    def check_student_classroom_assignments(self, student):
        """Check if student is assigned to any classrooms"""
        if "admin" not in self.auth_tokens:
            return None
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/classrooms",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                classrooms = response.json()
                student_classrooms = []
                
                for classroom in classrooms:
                    student_ids = classroom.get('studentIds', [])
                    if student.get('id') in student_ids:
                        student_classrooms.append({
                            'id': classroom.get('id'),
                            'name': classroom.get('name'),
                            'courseIds': classroom.get('courseIds', []),
                            'programIds': classroom.get('programIds', [])
                        })
                
                if student_classrooms:
                    self.log_result(
                        "Student Classroom Assignments", 
                        "PASS", 
                        f"Student is assigned to {len(student_classrooms)} classroom(s)",
                        f"Classrooms: {[c['name'] for c in student_classrooms]}"
                    )
                else:
                    self.log_result(
                        "Student Classroom Assignments", 
                        "FAIL", 
                        "Student is not assigned to any classrooms",
                        f"Checked {len(classrooms)} classrooms"
                    )
                
                return student_classrooms
            else:
                self.log_result(
                    "Student Classroom Assignments", 
                    "FAIL", 
                    f"Failed to get classrooms: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Classroom Assignments", 
                "FAIL", 
                "Failed to check classroom assignments",
                str(e)
            )
        return None
    
    def test_specific_course_access(self, course_id):
        """Test student access to a specific course"""
        if "student" not in self.auth_tokens:
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                course = response.json()
                self.log_result(
                    f"Course Access - {course_id[:8]}", 
                    "PASS", 
                    f"Student can access course: {course.get('title')}",
                    f"Modules: {len(course.get('modules', []))}, Category: {course.get('category')}"
                )
                return True
            elif response.status_code == 404:
                self.log_result(
                    f"Course Access - {course_id[:8]}", 
                    "FAIL", 
                    f"Course not found: {course_id}",
                    "Course may have been deleted or doesn't exist"
                )
            else:
                self.log_result(
                    f"Course Access - {course_id[:8]}", 
                    "FAIL", 
                    f"Course access failed: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                f"Course Access - {course_id[:8]}", 
                "FAIL", 
                "Failed to test course access",
                str(e)
            )
        return False
    
    def run_comprehensive_test(self):
        """Run comprehensive student authentication test"""
        print("🚀 STUDENT AUTHENTICATION DEBUGGING FOR WHITE SCREEN ISSUE")
        print("=" * 80)
        print("Focus: karlo.student@alder.com authentication and course access")
        print("Goal: Reset password to StudentPermanent123! and verify access")
        print("=" * 80)
        
        # Step 1: Admin login
        print("\n🔑 STEP 1: Admin Authentication")
        print("-" * 50)
        admin_success = self.test_admin_login()
        
        if not admin_success:
            print("❌ Cannot proceed without admin access")
            return False
        
        # Step 2: Find student
        print("\n👤 STEP 2: Find Student in System")
        print("-" * 50)
        student = self.find_student_in_system()
        
        if not student:
            print("❌ Cannot proceed without finding the student")
            return False
        
        # Step 3: Reset password
        print("\n🔐 STEP 3: Reset Student Password")
        print("-" * 50)
        reset_success = self.reset_student_password(student)
        
        if not reset_success:
            print("❌ Password reset failed")
            return False
        
        # Step 4: Test student login
        print("\n🎓 STEP 4: Test Student Login")
        print("-" * 50)
        login_success = self.test_student_login(student)
        
        if not login_success:
            print("❌ Student login failed even after password reset")
            return False
        
        # Step 5: Check enrollments
        print("\n📚 STEP 5: Check Student Enrollments")
        print("-" * 50)
        enrollments = self.test_student_enrollments()
        
        # Step 6: Test courses access
        print("\n📖 STEP 6: Test Courses Access")
        print("-" * 50)
        courses = self.test_student_courses_access()
        
        # Step 7: Check classroom assignments
        print("\n🏫 STEP 7: Check Classroom Assignments")
        print("-" * 50)
        classrooms = self.check_student_classroom_assignments(student)
        
        # Step 8: Test specific course access
        print("\n🎯 STEP 8: Test Specific Course Access")
        print("-" * 50)
        if enrollments:
            for enrollment in enrollments[:3]:  # Test first 3 enrollments
                course_id = enrollment.get('courseId')
                if course_id:
                    self.test_specific_course_access(course_id)
        
        # Summary
        print("\n📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        # Provide working credentials
        if login_success:
            print("\n🎉 WORKING STUDENT CREDENTIALS FOR FRONTEND TESTING:")
            print("=" * 60)
            print(f"📧 Email: {student.get('email')}")
            print(f"🔑 Password: StudentPermanent123!")
            print(f"👤 Name: {student.get('full_name')}")
            print(f"🆔 Student ID: {student.get('id')}")
            print(f"📚 Enrollments: {len(enrollments) if enrollments else 0}")
            print(f"🏫 Classrooms: {len(classrooms) if classrooms else 0}")
            print("=" * 60)
        
        return login_success and (self.passed > self.failed)

def main():
    """Main test execution"""
    tester = StudentAuthTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ STUDENT AUTHENTICATION DEBUGGING COMPLETED SUCCESSFULLY")
        print("Student can now login and access courses")
    else:
        print("\n❌ STUDENT AUTHENTICATION DEBUGGING FAILED")
        print("Issues found that need to be addressed")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())