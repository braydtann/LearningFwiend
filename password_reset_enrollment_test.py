#!/usr/bin/env python3
"""
Password Reset and Enrollment Verification Backend Testing
==========================================================

Testing the specific requirements from review request:
1. Reset Password for brayden.student@learningfwiend.com to "Cove1234!"
2. Test Student Login with new password
3. Check Student Dashboard - what student sees in courses/classrooms
4. Verify Enrollment Display - check if enrolled courses show up correctly
5. Debug Course Count Issue - classroom shows 0 courses but should have 2 from program

Admin credentials: brayden.t@covesmart.com / Hawaii2020!
Student credentials: brayden.student@learningfwiend.com / Cove1234! (after reset)
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://summarize-it-2.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"
STUDENT_EMAIL = "brayden.student@learningfwiend.com"
NEW_STUDENT_PASSWORD = "Cove1234!"

class PasswordResetEnrollmentTester:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.student_user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test result with timestamp"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {details}")
        
    def admin_login(self):
        """Test 1: Admin Authentication"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data['access_token']
                admin_name = data['user']['full_name']
                admin_role = data['user']['role']
                self.log_result("Admin Authentication", True, 
                    f"Admin login successful - Name: {admin_name}, Role: {admin_role}")
                return True
            else:
                self.log_result("Admin Authentication", False, 
                    f"Login failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def find_student_user(self):
        """Test 2: Find Student User ID"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/auth/admin/users", headers=headers)
            
            if response.status_code == 200:
                users = response.json()
                student_user = None
                
                for user in users:
                    if user['email'] == STUDENT_EMAIL:
                        student_user = user
                        break
                
                if student_user:
                    self.student_user_id = student_user['id']
                    self.log_result("Find Student User", True, 
                        f"Found student - ID: {self.student_user_id}, Name: {student_user['full_name']}, Role: {student_user['role']}")
                    return True
                else:
                    self.log_result("Find Student User", False, 
                        f"Student {STUDENT_EMAIL} not found among {len(users)} users")
                    return False
            else:
                self.log_result("Find Student User", False, 
                    f"Failed to get users: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Find Student User", False, f"Exception: {str(e)}")
            return False
    
    def reset_student_password(self):
        """Test 3: Reset Student Password to Cove1234!"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            reset_data = {
                "user_id": self.student_user_id,
                "new_temporary_password": NEW_STUDENT_PASSWORD
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/admin/reset-password", 
                                   headers=headers, json=reset_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Reset Student Password", True, 
                    f"Password reset successful - {data['message']}")
                return True
            else:
                self.log_result("Reset Student Password", False, 
                    f"Password reset failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Reset Student Password", False, f"Exception: {str(e)}")
            return False
    
    def test_student_login(self):
        """Test 4: Test Student Login with New Password"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": STUDENT_EMAIL,
                "password": NEW_STUDENT_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data['access_token']
                student_name = data['user']['full_name']
                requires_change = data.get('requires_password_change', False)
                self.log_result("Student Login Test", True, 
                    f"Student login successful - Name: {student_name}, Requires password change: {requires_change}")
                return True
            else:
                self.log_result("Student Login Test", False, 
                    f"Student login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Student Login Test", False, f"Exception: {str(e)}")
            return False
    
    def check_student_enrollments(self):
        """Test 5: Check Student Enrollments"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            
            if response.status_code == 200:
                enrollments = response.json()
                enrollment_count = len(enrollments)
                
                enrollment_details = []
                for enrollment in enrollments:
                    course_name = enrollment.get('courseName', 'Unknown Course')
                    progress = enrollment.get('progress', 0)
                    status = enrollment.get('status', 'unknown')
                    enrollment_details.append(f"Course: {course_name}, Progress: {progress}%, Status: {status}")
                
                self.log_result("Student Enrollments Check", True, 
                    f"Found {enrollment_count} enrollments: {'; '.join(enrollment_details) if enrollment_details else 'No enrollments'}")
                return enrollments
            else:
                self.log_result("Student Enrollments Check", False, 
                    f"Failed to get enrollments: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.log_result("Student Enrollments Check", False, f"Exception: {str(e)}")
            return []
    
    def check_student_courses_access(self):
        """Test 6: Check What Courses Student Can Access"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/courses", headers=headers)
            
            if response.status_code == 200:
                courses = response.json()
                course_count = len(courses)
                
                course_details = []
                for course in courses[:5]:  # Show first 5 courses
                    title = course.get('title', 'Unknown Title')
                    instructor = course.get('instructor', 'Unknown Instructor')
                    enrolled_students = course.get('enrolledStudents', 0)
                    course_details.append(f"'{title}' by {instructor} ({enrolled_students} students)")
                
                self.log_result("Student Course Access", True, 
                    f"Student can access {course_count} courses. Sample: {'; '.join(course_details)}")
                return courses
            else:
                self.log_result("Student Course Access", False, 
                    f"Failed to get courses: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.log_result("Student Course Access", False, f"Exception: {str(e)}")
            return []
    
    def check_student_classrooms(self):
        """Test 7: Check Student Classrooms"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers)
            
            if response.status_code == 200:
                classrooms = response.json()
                classroom_count = len(classrooms)
                
                classroom_details = []
                for classroom in classrooms:
                    name = classroom.get('name', 'Unknown Classroom')
                    course_count = len(classroom.get('courseIds', []))
                    program_count = len(classroom.get('programIds', []))
                    student_count = len(classroom.get('studentIds', []))
                    classroom_details.append(f"'{name}' - {course_count} courses, {program_count} programs, {student_count} students")
                
                self.log_result("Student Classrooms Check", True, 
                    f"Student can see {classroom_count} classrooms: {'; '.join(classroom_details) if classroom_details else 'No classrooms'}")
                return classrooms
            else:
                self.log_result("Student Classrooms Check", False, 
                    f"Failed to get classrooms: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.log_result("Student Classrooms Check", False, f"Exception: {str(e)}")
            return []
    
    def investigate_course_count_issue(self, classrooms):
        """Test 8: Debug Course Count Issue - Classroom shows 0 courses but should have 2 from program"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            for classroom in classrooms:
                classroom_name = classroom.get('name', 'Unknown')
                course_ids = classroom.get('courseIds', [])
                program_ids = classroom.get('programIds', [])
                
                print(f"\n🔍 INVESTIGATING CLASSROOM: '{classroom_name}'")
                print(f"   Direct Course IDs: {len(course_ids)} - {course_ids}")
                print(f"   Program IDs: {len(program_ids)} - {program_ids}")
                
                # Check programs for additional courses
                total_program_courses = 0
                for program_id in program_ids:
                    try:
                        prog_response = requests.get(f"{BACKEND_URL}/programs/{program_id}", headers=headers)
                        if prog_response.status_code == 200:
                            program = prog_response.json()
                            prog_course_ids = program.get('courseIds', [])
                            total_program_courses += len(prog_course_ids)
                            print(f"   Program '{program.get('title', 'Unknown')}': {len(prog_course_ids)} courses - {prog_course_ids}")
                        else:
                            print(f"   Program {program_id}: Failed to fetch - {prog_response.status_code}")
                    except Exception as e:
                        print(f"   Program {program_id}: Exception - {str(e)}")
                
                expected_total = len(course_ids) + total_program_courses
                print(f"   EXPECTED TOTAL COURSES: {expected_total} (Direct: {len(course_ids)} + Program: {total_program_courses})")
                
                if expected_total != len(course_ids):
                    self.log_result("Course Count Issue Investigation", False, 
                        f"Classroom '{classroom_name}' shows {len(course_ids)} direct courses but should have {expected_total} total courses (including {total_program_courses} from programs)")
                else:
                    self.log_result("Course Count Issue Investigation", True, 
                        f"Classroom '{classroom_name}' course count is correct: {expected_total} courses")
            
            return True
            
        except Exception as e:
            self.log_result("Course Count Issue Investigation", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all password reset and enrollment verification tests"""
        print("🔧 PASSWORD RESET AND ENROLLMENT VERIFICATION TESTING")
        print("=" * 60)
        
        # Test 1: Admin Authentication
        if not self.admin_login():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Test 2: Find Student User
        if not self.find_student_user():
            print("❌ Cannot proceed without finding student user")
            return False
        
        # Test 3: Reset Student Password
        if not self.reset_student_password():
            print("❌ Password reset failed")
            return False
        
        # Test 4: Test Student Login
        if not self.test_student_login():
            print("❌ Student login failed after password reset")
            return False
        
        # Test 5: Check Student Enrollments
        enrollments = self.check_student_enrollments()
        
        # Test 6: Check Student Course Access
        courses = self.check_student_courses_access()
        
        # Test 7: Check Student Classrooms
        classrooms = self.check_student_classrooms()
        
        # Test 8: Investigate Course Count Issue
        if classrooms:
            self.investigate_course_count_issue(classrooms)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ PASSED: {passed_tests}/{total_tests} tests ({success_rate:.1f}% success rate)")
        
        if passed_tests < total_tests:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['details']}")
        
        print(f"\n🎯 CRITICAL FINDINGS:")
        print(f"   - Student password reset: {'✅ WORKING' if any(r['test'] == 'Reset Student Password' and r['success'] for r in self.test_results) else '❌ FAILED'}")
        print(f"   - Student login: {'✅ WORKING' if any(r['test'] == 'Student Login Test' and r['success'] for r in self.test_results) else '❌ FAILED'}")
        print(f"   - Student enrollments: {len(enrollments)} found")
        print(f"   - Student course access: {len(courses)} courses accessible")
        print(f"   - Student classrooms: {len(classrooms)} classrooms visible")
        
        return success_rate >= 75  # Consider successful if 75% or more tests pass

if __name__ == "__main__":
    tester = PasswordResetEnrollmentTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 PASSWORD RESET AND ENROLLMENT VERIFICATION TESTING COMPLETED SUCCESSFULLY")
    else:
        print("\n🚨 PASSWORD RESET AND ENROLLMENT VERIFICATION TESTING COMPLETED WITH ISSUES")
    
    sys.exit(0 if success else 1)