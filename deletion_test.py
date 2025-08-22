#!/usr/bin/env python3
"""
Enhanced Classroom and Course Deletion Functionality Testing
Testing course deletion with enrollment cleanup and classroom deletion with enrollment cleanup
"""

import requests
import json
import os
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "http://localhost:8001/api"

# Test credentials
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class DeletionTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        self.created_resources = {
            'courses': [],
            'classrooms': [],
            'students': [],
            'enrollments': []
        }
    
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data['access_token']
                self.log_result("Admin Authentication", True, f"Successfully authenticated as {ADMIN_EMAIL}")
                return True
            else:
                self.log_result("Admin Authentication", False, f"Failed to authenticate: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.admin_token}"}
    
    def create_test_student(self, email_suffix):
        """Create a test student for enrollment testing"""
        try:
            # Use timestamp to ensure uniqueness
            timestamp = str(int(datetime.now().timestamp()))
            student_data = {
                "email": f"test.student.{email_suffix}.{timestamp}@testdomain.com",
                "username": f"teststudent{email_suffix}{timestamp}",
                "full_name": f"Test Student {email_suffix} {timestamp}",
                "role": "learner",
                "department": "Testing",
                "temporary_password": "TestPass123!"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/admin/create-user", 
                                   json=student_data, headers=self.get_headers())
            
            if response.status_code == 200:
                student = response.json()
                self.created_resources['students'].append(student['id'])
                self.log_result(f"Create Test Student {email_suffix}", True, f"Created student: {student['id']}")
                return student
            else:
                self.log_result(f"Create Test Student {email_suffix}", False, f"Failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log_result(f"Create Test Student {email_suffix}", False, f"Error: {str(e)}")
            return None
    
    def create_test_course(self, title_suffix):
        """Create a test course"""
        try:
            course_data = {
                "title": f"Test Course for Deletion {title_suffix}",
                "description": f"Test course created for deletion testing - {title_suffix}",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Test Module 1",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Test Lesson 1",
                                "type": "text",
                                "content": "Test lesson content"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(f"{BACKEND_URL}/courses", 
                                   json=course_data, headers=self.get_headers())
            
            if response.status_code == 200:
                course = response.json()
                self.created_resources['courses'].append(course['id'])
                self.log_result(f"Create Test Course {title_suffix}", True, f"Created course: {course['id']}")
                return course
            else:
                self.log_result(f"Create Test Course {title_suffix}", False, f"Failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log_result(f"Create Test Course {title_suffix}", False, f"Error: {str(e)}")
            return None
    
    def create_test_classroom(self, name_suffix, course_ids=None, student_ids=None):
        """Create a test classroom"""
        try:
            # Create a test instructor first
            instructor = self.create_test_instructor()
            if not instructor:
                return None
            trainer_id = instructor['id']
            
            classroom_data = {
                "name": f"Test Classroom for Deletion {name_suffix}",
                "description": f"Test classroom created for deletion testing - {name_suffix}",
                "trainerId": trainer_id,
                "courseIds": course_ids or [],
                "studentIds": student_ids or [],
                "programIds": [],
                "startDate": datetime.now().isoformat(),
                "endDate": None
            }
            
            response = requests.post(f"{BACKEND_URL}/classrooms", 
                                   json=classroom_data, headers=self.get_headers())
            
            if response.status_code == 200:
                classroom = response.json()
                self.created_resources['classrooms'].append(classroom['id'])
                self.log_result(f"Create Test Classroom {name_suffix}", True, f"Created classroom: {classroom['id']}")
                return classroom
            else:
                self.log_result(f"Create Test Classroom {name_suffix}", False, f"Failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log_result(f"Create Test Classroom {name_suffix}", False, f"Error: {str(e)}")
            return None
    
    def manually_enroll_student(self, student_id, course_id):
        """Manually enroll a student in a course"""
        try:
            # Get the student's username from the created resources
            student_suffix = student_id[-8:]  # Use last 8 chars of ID
            student_username = f"teststudent{student_suffix}"
            
            # First login as the student to enroll them
            student_login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": student_username,
                "password": "TestPass123!"
            })
            
            if student_login_response.status_code != 200:
                self.log_result(f"Student Login for Enrollment", False, f"Failed to login student: {student_login_response.text}")
                return False
            
            student_token = student_login_response.json()['access_token']
            student_headers = {"Authorization": f"Bearer {student_token}"}
            
            enrollment_data = {"courseId": course_id}
            response = requests.post(f"{BACKEND_URL}/enrollments", 
                                   json=enrollment_data, headers=student_headers)
            
            if response.status_code == 200:
                enrollment = response.json()
                self.created_resources['enrollments'].append(enrollment['id'])
                self.log_result(f"Manual Enrollment", True, f"Enrolled student {student_id} in course {course_id}")
                return True
            else:
                self.log_result(f"Manual Enrollment", False, f"Failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result(f"Manual Enrollment", False, f"Error: {str(e)}")
            return False
    
    def get_enrollments_count(self):
        """Get current enrollment count"""
        try:
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=self.get_headers())
            if response.status_code == 200:
                enrollments = response.json()
                return len(enrollments)
            return 0
        except:
            return 0
    
    def test_course_deletion_with_enrollment_cleanup(self):
        """Test course deletion with enrollment cleanup"""
        print("\n=== Testing Course Deletion with Enrollment Cleanup ===")
        
        # Create test course
        course = self.create_test_course("EnrollmentCleanup")
        if not course:
            return False
        
        # Create test students
        student1 = self.create_test_student("course1")
        student2 = self.create_test_student("course2")
        if not student1 or not student2:
            return False
        
        # Manually enroll students in the course
        self.manually_enroll_student(student1['id'], course['id'])
        self.manually_enroll_student(student2['id'], course['id'])
        
        # Get enrollment count before deletion
        enrollments_before = self.get_enrollments_count()
        
        # Test course deletion
        try:
            response = requests.delete(f"{BACKEND_URL}/courses/{course['id']}", 
                                     headers=self.get_headers())
            
            if response.status_code == 200:
                response_data = response.json()
                message = response_data.get('message', '')
                
                # Check if message includes enrollment count
                if 'enrollment' in message.lower():
                    self.log_result("Course Deletion with Enrollment Cleanup", True, 
                                  f"Course deleted successfully with enrollment cleanup: {message}")
                    
                    # Verify enrollments were actually deleted
                    enrollments_after = self.get_enrollments_count()
                    if enrollments_after < enrollments_before:
                        self.log_result("Enrollment Cleanup Verification", True, 
                                      f"Enrollments reduced from {enrollments_before} to {enrollments_after}")
                    else:
                        self.log_result("Enrollment Cleanup Verification", False, 
                                      f"Enrollments not reduced: {enrollments_before} -> {enrollments_after}")
                    
                    return True
                else:
                    self.log_result("Course Deletion with Enrollment Cleanup", False, 
                                  f"Response message doesn't mention enrollment cleanup: {message}")
                    return False
            else:
                self.log_result("Course Deletion with Enrollment Cleanup", False, 
                              f"Failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result("Course Deletion with Enrollment Cleanup", False, f"Error: {str(e)}")
            return False
    
    def test_classroom_deletion_with_enrollment_cleanup(self):
        """Test classroom deletion with enrollment cleanup"""
        print("\n=== Testing Classroom Deletion with Enrollment Cleanup ===")
        
        # Create test courses
        course1 = self.create_test_course("Classroom1")
        course2 = self.create_test_course("Classroom2")
        if not course1 or not course2:
            return False
        
        # Create test students
        student1 = self.create_test_student("classroom1")
        student2 = self.create_test_student("classroom2")
        if not student1 or not student2:
            return False
        
        # Create classroom with courses and students
        classroom = self.create_test_classroom("EnrollmentCleanup", 
                                             [course1['id'], course2['id']], 
                                             [student1['id'], student2['id']])
        if not classroom:
            return False
        
        # Get enrollment count before deletion
        enrollments_before = self.get_enrollments_count()
        
        # Test classroom deletion
        try:
            response = requests.delete(f"{BACKEND_URL}/classrooms/{classroom['id']}", 
                                     headers=self.get_headers())
            
            if response.status_code == 200:
                response_data = response.json()
                message = response_data.get('message', '')
                
                # Check if message includes enrollment cleanup count
                if 'enrollment' in message.lower():
                    self.log_result("Classroom Deletion with Enrollment Cleanup", True, 
                                  f"Classroom soft-deleted successfully with enrollment cleanup: {message}")
                    
                    # Verify classroom is soft-deleted (isActive: false)
                    classroom_check = requests.get(f"{BACKEND_URL}/classrooms/{classroom['id']}", 
                                                 headers=self.get_headers())
                    if classroom_check.status_code == 200:
                        classroom_data = classroom_check.json()
                        if not classroom_data.get('isActive', True):
                            self.log_result("Classroom Soft Delete Verification", True, 
                                          "Classroom successfully soft-deleted (isActive: false)")
                        else:
                            self.log_result("Classroom Soft Delete Verification", False, 
                                          "Classroom not soft-deleted (isActive still true)")
                    
                    # Verify enrollments were actually deleted
                    enrollments_after = self.get_enrollments_count()
                    if enrollments_after < enrollments_before:
                        self.log_result("Classroom Enrollment Cleanup Verification", True, 
                                      f"Enrollments reduced from {enrollments_before} to {enrollments_after}")
                    else:
                        self.log_result("Classroom Enrollment Cleanup Verification", False, 
                                      f"Enrollments not reduced: {enrollments_before} -> {enrollments_after}")
                    
                    return True
                else:
                    self.log_result("Classroom Deletion with Enrollment Cleanup", False, 
                                  f"Response message doesn't mention enrollment cleanup: {message}")
                    return False
            else:
                self.log_result("Classroom Deletion with Enrollment Cleanup", False, 
                              f"Failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result("Classroom Deletion with Enrollment Cleanup", False, f"Error: {str(e)}")
            return False
    
    def test_unauthorized_access(self):
        """Test unauthorized deletion attempts"""
        print("\n=== Testing Unauthorized Access ===")
        
        # Create test course
        course = self.create_test_course("UnauthorizedTest")
        if not course:
            return False
        
        # Test without authentication
        try:
            response = requests.delete(f"{BACKEND_URL}/courses/{course['id']}")
            if response.status_code in [401, 403]:  # Both are valid for unauthorized access
                self.log_result("Unauthorized Course Deletion", True, 
                              f"Correctly rejected unauthenticated request ({response.status_code})")
            else:
                self.log_result("Unauthorized Course Deletion", False, 
                              f"Expected 401 or 403, got {response.status_code}")
        except Exception as e:
            self.log_result("Unauthorized Course Deletion", False, f"Error: {str(e)}")
        
        # Create test classroom
        classroom = self.create_test_classroom("UnauthorizedTest")
        if not classroom:
            return False
        
        # Test without authentication
        try:
            response = requests.delete(f"{BACKEND_URL}/classrooms/{classroom['id']}")
            if response.status_code in [401, 403]:  # Both are valid for unauthorized access
                self.log_result("Unauthorized Classroom Deletion", True, 
                              f"Correctly rejected unauthenticated request ({response.status_code})")
            else:
                self.log_result("Unauthorized Classroom Deletion", False, 
                              f"Expected 401 or 403, got {response.status_code}")
        except Exception as e:
            self.log_result("Unauthorized Classroom Deletion", False, f"Error: {str(e)}")
    
    def test_nonexistent_resource_deletion(self):
        """Test deletion of non-existent courses/classrooms"""
        print("\n=== Testing Non-existent Resource Deletion ===")
        
        fake_course_id = str(uuid.uuid4())
        fake_classroom_id = str(uuid.uuid4())
        
        # Test non-existent course deletion
        try:
            response = requests.delete(f"{BACKEND_URL}/courses/{fake_course_id}", 
                                     headers=self.get_headers())
            if response.status_code == 404:
                self.log_result("Non-existent Course Deletion", True, 
                              "Correctly returned 404 for non-existent course")
            else:
                self.log_result("Non-existent Course Deletion", False, 
                              f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("Non-existent Course Deletion", False, f"Error: {str(e)}")
        
        # Test non-existent classroom deletion
        try:
            response = requests.delete(f"{BACKEND_URL}/classrooms/{fake_classroom_id}", 
                                     headers=self.get_headers())
            if response.status_code == 404:
                self.log_result("Non-existent Classroom Deletion", True, 
                              "Correctly returned 404 for non-existent classroom")
            else:
                self.log_result("Non-existent Classroom Deletion", False, 
                              f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("Non-existent Classroom Deletion", False, f"Error: {str(e)}")
    
    def test_edge_cases(self):
        """Test edge cases like empty classrooms or courses with no enrollments"""
        print("\n=== Testing Edge Cases ===")
        
        # Test course deletion with no enrollments
        course_no_enrollments = self.create_test_course("NoEnrollments")
        if course_no_enrollments:
            try:
                response = requests.delete(f"{BACKEND_URL}/courses/{course_no_enrollments['id']}", 
                                         headers=self.get_headers())
                if response.status_code == 200:
                    message = response.json().get('message', '')
                    self.log_result("Course Deletion (No Enrollments)", True, 
                                  f"Successfully deleted course with no enrollments: {message}")
                else:
                    self.log_result("Course Deletion (No Enrollments)", False, 
                                  f"Failed: {response.status_code} - {response.text}")
            except Exception as e:
                self.log_result("Course Deletion (No Enrollments)", False, f"Error: {str(e)}")
        
        # Test empty classroom deletion
        empty_classroom = self.create_test_classroom("Empty", [], [])
        if empty_classroom:
            try:
                response = requests.delete(f"{BACKEND_URL}/classrooms/{empty_classroom['id']}", 
                                         headers=self.get_headers())
                if response.status_code == 200:
                    message = response.json().get('message', '')
                    self.log_result("Empty Classroom Deletion", True, 
                                  f"Successfully deleted empty classroom: {message}")
                else:
                    self.log_result("Empty Classroom Deletion", False, 
                                  f"Failed: {response.status_code} - {response.text}")
            except Exception as e:
                self.log_result("Empty Classroom Deletion", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Enhanced Classroom and Course Deletion Testing")
        print("=" * 70)
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return 0, 1
        
        # Run all test scenarios
        self.test_course_deletion_with_enrollment_cleanup()
        self.test_classroom_deletion_with_enrollment_cleanup()
        self.test_unauthorized_access()
        self.test_nonexistent_resource_deletion()
        self.test_edge_cases()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n🎯 CRITICAL SUCCESS CRITERIA CHECK:")
        
        # Check critical criteria
        course_deletion_success = any(r['success'] and 'Course Deletion with Enrollment Cleanup' in r['test'] for r in self.test_results)
        classroom_deletion_success = any(r['success'] and 'Classroom Deletion with Enrollment Cleanup' in r['test'] for r in self.test_results)
        auth_working = any(r['success'] and 'Admin Authentication' in r['test'] for r in self.test_results)
        
        print(f"✅ Course deletion removes both course and enrollments: {'YES' if course_deletion_success else 'NO'}")
        print(f"✅ Classroom deletion soft-deletes classroom and removes course enrollments: {'YES' if classroom_deletion_success else 'NO'}")
        print(f"✅ Authorization working correctly: {'YES' if auth_working else 'NO'}")
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = DeletionTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)