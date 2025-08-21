#!/usr/bin/env python3
"""
CLASSROOM AUTO-ENROLLMENT DEBUG TEST
Specific test to debug the issue reported in review request:
- User creates classroom "PC1" with "pizza course" and assigns student
- Student appears enrolled on course card but classroom details show no students
- Student gets white screen when accessing course
"""

import requests
import json
import os
import sys
from datetime import datetime
import time

# Configuration - Using Production Backend URL from frontend/.env
BACKEND_URL = "https://lms-evolution-1.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

class ClassroomDebugTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        self.test_data = {}  # Store created test data
        
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
    
    def authenticate_admin(self):
        """Authenticate as admin using specified credentials"""
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
                        "Admin Authentication", 
                        "PASS", 
                        f"Successfully authenticated as admin: {user_info.get('email')}",
                        f"Admin ID: {user_info.get('id')}, Name: {user_info.get('full_name')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication", 
                        "FAIL", 
                        "Login successful but missing token or wrong role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                error_detail = "Unknown error"
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'No error detail provided')
                except:
                    error_detail = response.text
                
                self.log_result(
                    "Admin Authentication", 
                    "FAIL", 
                    f"Admin authentication failed with status {response.status_code}",
                    f"Error: {error_detail}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Authentication", 
                "FAIL", 
                "Failed to connect to authentication endpoint",
                str(e)
            )
        return False
    
    def create_test_student(self):
        """Create a test student for classroom assignment"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Create Test Student", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            student_data = {
                "email": "pizza.student@learningfwiend.com",
                "username": "pizza.student",
                "full_name": "Pizza Student",
                "role": "learner",
                "department": "Testing",
                "temporary_password": "PizzaTest123!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=student_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                created_student = response.json()
                self.test_data['student'] = created_student
                
                self.log_result(
                    "Create Test Student", 
                    "PASS", 
                    f"Successfully created test student: {created_student.get('username')}",
                    f"Student ID: {created_student.get('id')}, Email: {created_student.get('email')}"
                )
                return created_student
            else:
                self.log_result(
                    "Create Test Student", 
                    "FAIL", 
                    f"Failed to create test student (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Create Test Student", 
                "FAIL", 
                "Failed to create test student",
                str(e)
            )
        return False
    
    def create_pizza_course(self):
        """Create a 'pizza course' similar to user's scenario"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Create Pizza Course", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            course_data = {
                "title": "Pizza Course",
                "description": "A comprehensive course about pizza making and management",
                "category": "Culinary",
                "duration": "4 weeks",
                "accessType": "open",
                "modules": [
                    {
                        "title": "Pizza Basics",
                        "lessons": [
                            {"id": "lesson1", "title": "Introduction to Pizza", "content": "Basic pizza concepts"},
                            {"id": "lesson2", "title": "Pizza Dough", "content": "Making perfect dough"}
                        ]
                    },
                    {
                        "title": "Advanced Techniques",
                        "lessons": [
                            {"id": "lesson3", "title": "Toppings", "content": "Choosing the right toppings"},
                            {"id": "lesson4", "title": "Baking", "content": "Perfect baking techniques"}
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                created_course = response.json()
                self.test_data['course'] = created_course
                
                self.log_result(
                    "Create Pizza Course", 
                    "PASS", 
                    f"Successfully created pizza course: {created_course.get('title')}",
                    f"Course ID: {created_course.get('id')}, Modules: {len(created_course.get('modules', []))}"
                )
                return created_course
            else:
                self.log_result(
                    "Create Pizza Course", 
                    "FAIL", 
                    f"Failed to create pizza course (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Create Pizza Course", 
                "FAIL", 
                "Failed to create pizza course",
                str(e)
            )
        return False
    
    def create_pc1_classroom(self):
        """Create classroom 'PC1' with student and pizza course assignment"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Create PC1 Classroom", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        if 'student' not in self.test_data or 'course' not in self.test_data:
            self.log_result(
                "Create PC1 Classroom", 
                "SKIP", 
                "Missing test student or course data",
                "Student and course must be created first"
            )
            return False
        
        try:
            # Get admin user info for trainer assignment
            admin_response = requests.get(
                f"{BACKEND_URL}/auth/me",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if admin_response.status_code != 200:
                self.log_result(
                    "Create PC1 Classroom", 
                    "FAIL", 
                    "Failed to get admin user info for trainer assignment",
                    f"Status: {admin_response.status_code}"
                )
                return False
            
            admin_info = admin_response.json()
            
            # Find an instructor to assign as trainer
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            instructor_id = None
            if users_response.status_code == 200:
                users = users_response.json()
                for user in users:
                    if user.get('role') == 'instructor':
                        instructor_id = user.get('id')
                        break
            
            # If no instructor found, create one
            if not instructor_id:
                instructor_data = {
                    "email": "pizza.instructor@learningfwiend.com",
                    "username": "pizza.instructor",
                    "full_name": "Pizza Instructor",
                    "role": "instructor",
                    "department": "Culinary",
                    "temporary_password": "InstructorTest123!"
                }
                
                instructor_response = requests.post(
                    f"{BACKEND_URL}/auth/admin/create-user",
                    json=instructor_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                    }
                )
                
                if instructor_response.status_code == 200:
                    instructor = instructor_response.json()
                    instructor_id = instructor.get('id')
                    self.test_data['instructor'] = instructor
                else:
                    self.log_result(
                        "Create PC1 Classroom", 
                        "FAIL", 
                        "Failed to create instructor for classroom",
                        f"Status: {instructor_response.status_code}"
                    )
                    return False
            
            classroom_data = {
                "name": "PC1",
                "description": "Pizza Course Classroom 1 - Testing auto-enrollment functionality",
                "trainerId": instructor_id,
                "courseIds": [self.test_data['course']['id']],
                "programIds": [],
                "studentIds": [self.test_data['student']['id']],
                "startDate": datetime.utcnow().isoformat(),
                "endDate": None,  # No end date
                "location": "Virtual",
                "capacity": 30
            }
            
            response = requests.post(
                f"{BACKEND_URL}/classrooms",
                json=classroom_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                created_classroom = response.json()
                self.test_data['classroom'] = created_classroom
                
                self.log_result(
                    "Create PC1 Classroom", 
                    "PASS", 
                    f"Successfully created PC1 classroom: {created_classroom.get('name')}",
                    f"Classroom ID: {created_classroom.get('id')}, Students: {len(created_classroom.get('studentIds', []))}, Courses: {len(created_classroom.get('courseIds', []))}"
                )
                return created_classroom
            else:
                self.log_result(
                    "Create PC1 Classroom", 
                    "FAIL", 
                    f"Failed to create PC1 classroom (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Create PC1 Classroom", 
                "FAIL", 
                "Failed to create PC1 classroom",
                str(e)
            )
        return False
    
    def test_classroom_students_endpoint(self):
        """Test GET /api/classrooms/{id}/students endpoint"""
        if 'classroom' not in self.test_data:
            self.log_result(
                "Test Classroom Students Endpoint", 
                "SKIP", 
                "No classroom data available",
                "Classroom must be created first"
            )
            return False
        
        try:
            classroom_id = self.test_data['classroom']['id']
            
            response = requests.get(
                f"{BACKEND_URL}/classrooms/{classroom_id}/students",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                students = response.json()
                expected_student_id = self.test_data['student']['id']
                
                # Check if our test student is in the list
                found_student = None
                for student in students:
                    if student.get('id') == expected_student_id:
                        found_student = student
                        break
                
                if found_student:
                    self.log_result(
                        "Test Classroom Students Endpoint", 
                        "PASS", 
                        f"✅ Student correctly appears in classroom students list",
                        f"Found student: {found_student.get('full_name')} ({found_student.get('email')}), Total students: {len(students)}"
                    )
                    return True
                else:
                    self.log_result(
                        "Test Classroom Students Endpoint", 
                        "FAIL", 
                        f"❌ BUG CONFIRMED: Student NOT found in classroom students list",
                        f"Expected student ID: {expected_student_id}, Found {len(students)} students: {[s.get('id') for s in students]}"
                    )
                    return False
            else:
                self.log_result(
                    "Test Classroom Students Endpoint", 
                    "FAIL", 
                    f"Failed to get classroom students (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Test Classroom Students Endpoint", 
                "FAIL", 
                "Failed to test classroom students endpoint",
                str(e)
            )
        return False
    
    def test_student_enrollments(self):
        """Test GET /api/enrollments endpoint to check if auto-enrollment worked"""
        if 'student' not in self.test_data:
            self.log_result(
                "Test Student Enrollments", 
                "SKIP", 
                "No student data available",
                "Student must be created first"
            )
            return False
        
        try:
            # First authenticate as the student
            student_login_data = {
                "username_or_email": "pizza.student@learningfwiend.com",
                "password": "PizzaTest123!"
            }
            
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=student_login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                student_token = login_data.get('access_token')
                requires_password_change = login_data.get('requires_password_change', False)
                
                # If password change is required, change it
                if requires_password_change:
                    change_password_data = {
                        "current_password": "PizzaTest123!",
                        "new_password": "PizzaPermanent123!"
                    }
                    
                    change_response = requests.post(
                        f"{BACKEND_URL}/auth/change-password",
                        json=change_password_data,
                        timeout=TEST_TIMEOUT,
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {student_token}'
                        }
                    )
                    
                    if change_response.status_code == 200:
                        # Login again with new password
                        new_login_data = {
                            "username_or_email": "pizza.student@learningfwiend.com",
                            "password": "PizzaPermanent123!"
                        }
                        
                        new_login_response = requests.post(
                            f"{BACKEND_URL}/auth/login",
                            json=new_login_data,
                            timeout=TEST_TIMEOUT,
                            headers={'Content-Type': 'application/json'}
                        )
                        
                        if new_login_response.status_code == 200:
                            new_login_data = new_login_response.json()
                            student_token = new_login_data.get('access_token')
                
                # Now check enrollments
                enrollments_response = requests.get(
                    f"{BACKEND_URL}/enrollments",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {student_token}'}
                )
                
                if enrollments_response.status_code == 200:
                    enrollments = enrollments_response.json()
                    expected_course_id = self.test_data['course']['id']
                    
                    # Check if student is enrolled in the pizza course
                    found_enrollment = None
                    for enrollment in enrollments:
                        if enrollment.get('courseId') == expected_course_id:
                            found_enrollment = enrollment
                            break
                    
                    if found_enrollment:
                        self.log_result(
                            "Test Student Enrollments", 
                            "PASS", 
                            f"✅ Auto-enrollment WORKING: Student enrolled in pizza course",
                            f"Enrollment ID: {found_enrollment.get('id')}, Course ID: {found_enrollment.get('courseId')}, Status: {found_enrollment.get('status')}, Progress: {found_enrollment.get('progress', 0)}%"
                        )
                        self.test_data['enrollment'] = found_enrollment
                        return True
                    else:
                        self.log_result(
                            "Test Student Enrollments", 
                            "FAIL", 
                            f"❌ BUG CONFIRMED: Auto-enrollment FAILED - Student NOT enrolled in pizza course",
                            f"Expected course ID: {expected_course_id}, Found {len(enrollments)} enrollments: {[e.get('courseId') for e in enrollments]}"
                        )
                        return False
                else:
                    self.log_result(
                        "Test Student Enrollments", 
                        "FAIL", 
                        f"Failed to get student enrollments (status: {enrollments_response.status_code})",
                        f"Response: {enrollments_response.text}"
                    )
            else:
                self.log_result(
                    "Test Student Enrollments", 
                    "FAIL", 
                    f"Failed to authenticate as student (status: {login_response.status_code})",
                    f"Response: {login_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Test Student Enrollments", 
                "FAIL", 
                "Failed to test student enrollments",
                str(e)
            )
        return False
    
    def test_course_access(self):
        """Test if student can access the course (to debug white screen issue)"""
        if 'course' not in self.test_data:
            self.log_result(
                "Test Course Access", 
                "SKIP", 
                "No course data available",
                "Course must be created first"
            )
            return False
        
        try:
            # Authenticate as student first
            student_login_data = {
                "username_or_email": "pizza.student@learningfwiend.com",
                "password": "PizzaPermanent123!"  # Use permanent password if changed
            }
            
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=student_login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if login_response.status_code != 200:
                # Try with original password
                student_login_data["password"] = "PizzaTest123!"
                login_response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json=student_login_data,
                    timeout=TEST_TIMEOUT,
                    headers={'Content-Type': 'application/json'}
                )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                student_token = login_data.get('access_token')
                
                # Test course access
                course_id = self.test_data['course']['id']
                course_response = requests.get(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {student_token}'}
                )
                
                if course_response.status_code == 200:
                    course_data = course_response.json()
                    modules = course_data.get('modules', [])
                    
                    self.log_result(
                        "Test Course Access", 
                        "PASS", 
                        f"✅ Student CAN access pizza course - No white screen issue",
                        f"Course: {course_data.get('title')}, Modules: {len(modules)}, Status: {course_data.get('status')}"
                    )
                    return True
                elif course_response.status_code == 404:
                    self.log_result(
                        "Test Course Access", 
                        "FAIL", 
                        f"❌ BUG CONFIRMED: Course NOT FOUND - This could cause white screen",
                        f"Course ID: {course_id}, Status: 404 Not Found"
                    )
                    return False
                else:
                    self.log_result(
                        "Test Course Access", 
                        "FAIL", 
                        f"❌ Course access failed - Status: {course_response.status_code}",
                        f"Response: {course_response.text}"
                    )
                    return False
            else:
                self.log_result(
                    "Test Course Access", 
                    "FAIL", 
                    f"Failed to authenticate as student for course access test",
                    f"Status: {login_response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Test Course Access", 
                "FAIL", 
                "Failed to test course access",
                str(e)
            )
        return False
    
    def test_manual_enrollment(self):
        """Test manual enrollment if auto-enrollment failed"""
        if 'student' not in self.test_data or 'course' not in self.test_data:
            self.log_result(
                "Test Manual Enrollment", 
                "SKIP", 
                "Missing student or course data",
                "Student and course must be created first"
            )
            return False
        
        try:
            # Authenticate as student
            student_login_data = {
                "username_or_email": "pizza.student@learningfwiend.com",
                "password": "PizzaPermanent123!"
            }
            
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=student_login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if login_response.status_code != 200:
                # Try with original password
                student_login_data["password"] = "PizzaTest123!"
                login_response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json=student_login_data,
                    timeout=TEST_TIMEOUT,
                    headers={'Content-Type': 'application/json'}
                )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                student_token = login_data.get('access_token')
                
                # Try manual enrollment
                enrollment_data = {
                    "courseId": self.test_data['course']['id']
                }
                
                enrollment_response = requests.post(
                    f"{BACKEND_URL}/enrollments",
                    json=enrollment_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {student_token}'
                    }
                )
                
                if enrollment_response.status_code == 200:
                    enrollment = enrollment_response.json()
                    self.log_result(
                        "Test Manual Enrollment", 
                        "PASS", 
                        f"✅ Manual enrollment WORKS - Student can enroll manually",
                        f"Enrollment ID: {enrollment.get('id')}, Course ID: {enrollment.get('courseId')}"
                    )
                    return True
                elif enrollment_response.status_code == 400:
                    # Check if already enrolled
                    error_data = enrollment_response.json()
                    if "already enrolled" in error_data.get('detail', '').lower():
                        self.log_result(
                            "Test Manual Enrollment", 
                            "PASS", 
                            f"✅ Student already enrolled (auto-enrollment worked)",
                            f"Error: {error_data.get('detail')}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Test Manual Enrollment", 
                            "FAIL", 
                            f"❌ Manual enrollment failed with validation error",
                            f"Error: {error_data.get('detail')}"
                        )
                else:
                    self.log_result(
                        "Test Manual Enrollment", 
                        "FAIL", 
                        f"❌ Manual enrollment failed - Status: {enrollment_response.status_code}",
                        f"Response: {enrollment_response.text}"
                    )
            else:
                self.log_result(
                    "Test Manual Enrollment", 
                    "FAIL", 
                    f"Failed to authenticate as student for manual enrollment test",
                    f"Status: {login_response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Test Manual Enrollment", 
                "FAIL", 
                "Failed to test manual enrollment",
                str(e)
            )
        return False
    
    def cleanup_test_data(self):
        """Clean up created test data"""
        if "admin" not in self.auth_tokens:
            print("⚠️ Cannot cleanup - no admin token available")
            return
        
        cleanup_results = []
        
        # Delete test student
        if 'student' in self.test_data:
            try:
                student_id = self.test_data['student']['id']
                response = requests.delete(
                    f"{BACKEND_URL}/auth/admin/users/{student_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                if response.status_code == 200:
                    cleanup_results.append("✅ Deleted test student")
                else:
                    cleanup_results.append(f"❌ Failed to delete test student: {response.status_code}")
            except:
                cleanup_results.append("❌ Error deleting test student")
        
        # Delete test course
        if 'course' in self.test_data:
            try:
                course_id = self.test_data['course']['id']
                response = requests.delete(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                if response.status_code == 200:
                    cleanup_results.append("✅ Deleted test course")
                else:
                    cleanup_results.append(f"❌ Failed to delete test course: {response.status_code}")
            except:
                cleanup_results.append("❌ Error deleting test course")
        
        # Delete test classroom
        if 'classroom' in self.test_data:
            try:
                classroom_id = self.test_data['classroom']['id']
                response = requests.delete(
                    f"{BACKEND_URL}/classrooms/{classroom_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                if response.status_code == 200:
                    cleanup_results.append("✅ Deleted test classroom")
                else:
                    cleanup_results.append(f"❌ Failed to delete test classroom: {response.status_code}")
            except:
                cleanup_results.append("❌ Error deleting test classroom")
        
        # Delete test instructor if created
        if 'instructor' in self.test_data:
            try:
                instructor_id = self.test_data['instructor']['id']
                response = requests.delete(
                    f"{BACKEND_URL}/auth/admin/users/{instructor_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                if response.status_code == 200:
                    cleanup_results.append("✅ Deleted test instructor")
                else:
                    cleanup_results.append(f"❌ Failed to delete test instructor: {response.status_code}")
            except:
                cleanup_results.append("❌ Error deleting test instructor")
        
        print(f"\n🧹 CLEANUP RESULTS:")
        for result in cleanup_results:
            print(f"   {result}")
    
    def run_debug_tests(self):
        """Run all debug tests in sequence"""
        print("🔍 CLASSROOM AUTO-ENROLLMENT DEBUG TEST")
        print("=" * 80)
        print("Debugging specific issue: User creates classroom 'PC1' with 'pizza course'")
        print("and assigns student, but student doesn't appear in classroom details")
        print("=" * 80)
        
        # Step 1: Authenticate as admin
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return
        
        # Step 2: Create test student
        if not self.create_test_student():
            print("❌ Cannot proceed without test student")
            return
        
        # Step 3: Create pizza course
        if not self.create_pizza_course():
            print("❌ Cannot proceed without pizza course")
            return
        
        # Step 4: Create PC1 classroom with auto-enrollment
        if not self.create_pc1_classroom():
            print("❌ Cannot proceed without PC1 classroom")
            return
        
        # Step 5: Test classroom students endpoint
        classroom_students_ok = self.test_classroom_students_endpoint()
        
        # Step 6: Test student enrollments
        student_enrollments_ok = self.test_student_enrollments()
        
        # Step 7: Test course access (white screen debug)
        course_access_ok = self.test_course_access()
        
        # Step 8: Test manual enrollment as fallback
        manual_enrollment_ok = self.test_manual_enrollment()
        
        # Summary
        print(f"\n📊 DEBUG TEST SUMMARY:")
        print("=" * 60)
        print(f"✅ Admin Authentication: PASS")
        print(f"✅ Test Student Creation: PASS")
        print(f"✅ Pizza Course Creation: PASS")
        print(f"✅ PC1 Classroom Creation: PASS")
        print(f"{'✅' if classroom_students_ok else '❌'} Classroom Students Endpoint: {'PASS' if classroom_students_ok else 'FAIL'}")
        print(f"{'✅' if student_enrollments_ok else '❌'} Student Auto-Enrollment: {'PASS' if student_enrollments_ok else 'FAIL'}")
        print(f"{'✅' if course_access_ok else '❌'} Course Access (White Screen): {'PASS' if course_access_ok else 'FAIL'}")
        print(f"{'✅' if manual_enrollment_ok else '❌'} Manual Enrollment Fallback: {'PASS' if manual_enrollment_ok else 'FAIL'}")
        
        # Determine overall result
        critical_tests = [classroom_students_ok, student_enrollments_ok, course_access_ok]
        if all(critical_tests):
            print(f"\n🎉 RESULT: NO BUG DETECTED - Classroom auto-enrollment is working correctly")
            print("The reported issue may be frontend-related or resolved.")
        else:
            print(f"\n🚨 RESULT: BUG CONFIRMED - Issues found in classroom auto-enrollment")
            if not classroom_students_ok:
                print("   • Students not appearing in classroom details")
            if not student_enrollments_ok:
                print("   • Auto-enrollment not creating enrollment records")
            if not course_access_ok:
                print("   • Course access issues (potential cause of white screen)")
        
        print(f"\nTotal Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        # Cleanup
        self.cleanup_test_data()

def main():
    """Main function to run the debug tests"""
    tester = ClassroomDebugTester()
    tester.run_debug_tests()

if __name__ == "__main__":
    main()