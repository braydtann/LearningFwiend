#!/usr/bin/env python3
"""
STUDENT COURSE ACCESS INVESTIGATION - DATA STRUCTURE ANALYSIS
LearningFwiend LMS Application Backend API Testing

CRITICAL INVESTIGATION NEEDED:
1. CHECK if test.student@cleanenv.com is actually ENROLLED in "Production Test Course - Clean Environment"
2. VERIFY the course structure and data format matches frontend expectations
3. ANALYZE enrollment data structure for any missing fields
4. TEST the specific course access flow for this student
5. CHECK if course modules/lessons structure is compatible with CourseDetail.js

TESTING CREDENTIALS:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: test.student@cleanenv.com / CleanEnv123!
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using Production Backend URL
BACKEND_URL = "https://lms-evolution.emergent.host/api"
TEST_TIMEOUT = 15

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "test.student@cleanenv.com",
    "password": "CleanEnv123!"
}

class StudentCourseAccessTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}  # Store auth tokens for different users
        self.target_course_name = "Production Test Course - Clean Environment"
        self.target_course_id = None
        self.student_info = None
        
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
                        "Admin login failed - invalid token or role",
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
                "Failed to connect to backend for admin login",
                str(e)
            )
        return False
    
    def test_student_login(self):
        """Test student authentication"""
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
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['student'] = token
                    self.student_info = user_info
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
                        "Student login failed - invalid token or role",
                        f"Token: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
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
                "Failed to connect to backend for student login",
                str(e)
            )
        return False
    
    def find_target_course(self):
        """Find the 'Production Test Course - Clean Environment' course"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Find Target Course", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                target_course = None
                
                for course in courses:
                    if course.get('title') == self.target_course_name:
                        target_course = course
                        self.target_course_id = course.get('id')
                        break
                
                if target_course:
                    modules = target_course.get('modules', [])
                    total_lessons = sum(len(module.get('lessons', [])) for module in modules)
                    
                    self.log_result(
                        "Find Target Course", 
                        "PASS", 
                        f"Found target course: {self.target_course_name}",
                        f"ID: {self.target_course_id}, Modules: {len(modules)}, Total Lessons: {total_lessons}, Instructor: {target_course.get('instructor')}"
                    )
                    return target_course
                else:
                    self.log_result(
                        "Find Target Course", 
                        "FAIL", 
                        f"Target course '{self.target_course_name}' not found",
                        f"Searched {len(courses)} courses, target course not found"
                    )
            else:
                self.log_result(
                    "Find Target Course", 
                    "FAIL", 
                    f"Failed to retrieve courses, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Find Target Course", 
                "FAIL", 
                "Failed to search for target course",
                str(e)
            )
        return False
    
    def check_student_enrollment_status(self):
        """Check if test.student@cleanenv.com is enrolled in the target course"""
        if "student" not in self.auth_tokens or not self.target_course_id:
            self.log_result(
                "Student Enrollment Status", 
                "SKIP", 
                "Missing student token or target course ID",
                f"Student token: {bool('student' in self.auth_tokens)}, Course ID: {bool(self.target_course_id)}"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                target_enrollment = None
                
                for enrollment in enrollments:
                    if enrollment.get('courseId') == self.target_course_id:
                        target_enrollment = enrollment
                        break
                
                if target_enrollment:
                    self.log_result(
                        "Student Enrollment Status", 
                        "PASS", 
                        f"✅ STUDENT IS ENROLLED in target course",
                        f"Enrollment ID: {target_enrollment.get('id')}, Progress: {target_enrollment.get('progress', 0)}%, Status: {target_enrollment.get('status')}, Enrolled: {target_enrollment.get('enrolledAt')}"
                    )
                    return target_enrollment
                else:
                    self.log_result(
                        "Student Enrollment Status", 
                        "FAIL", 
                        f"❌ STUDENT IS NOT ENROLLED in target course",
                        f"Student has {len(enrollments)} enrollments but none for target course ID: {self.target_course_id}"
                    )
            else:
                self.log_result(
                    "Student Enrollment Status", 
                    "FAIL", 
                    f"Failed to retrieve student enrollments, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Enrollment Status", 
                "FAIL", 
                "Failed to check student enrollment status",
                str(e)
            )
        return False
    
    def analyze_course_structure(self):
        """Analyze the course structure and data format for frontend compatibility"""
        if not self.target_course_id:
            self.log_result(
                "Course Structure Analysis", 
                "SKIP", 
                "No target course ID available",
                "Target course must be found first"
            )
            return False
        
        try:
            # Get course details as student (this is what frontend would do)
            response = requests.get(
                f"{BACKEND_URL}/courses/{self.target_course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                course = response.json()
                
                # Analyze course structure
                analysis = {
                    'has_modules': bool(course.get('modules')),
                    'module_count': len(course.get('modules', [])),
                    'total_lessons': 0,
                    'lesson_types': {},
                    'modules_with_lessons': 0,
                    'empty_modules': 0,
                    'required_fields_present': {},
                    'potential_issues': []
                }
                
                # Check required fields for frontend
                required_fields = ['id', 'title', 'description', 'modules', 'instructor', 'instructorId']
                for field in required_fields:
                    analysis['required_fields_present'][field] = field in course and course[field] is not None
                
                # Analyze modules and lessons
                modules = course.get('modules', [])
                for module in modules:
                    lessons = module.get('lessons', [])
                    if lessons:
                        analysis['modules_with_lessons'] += 1
                        analysis['total_lessons'] += len(lessons)
                        
                        for lesson in lessons:
                            lesson_type = lesson.get('type', 'unknown')
                            analysis['lesson_types'][lesson_type] = analysis['lesson_types'].get(lesson_type, 0) + 1
                    else:
                        analysis['empty_modules'] += 1
                
                # Check for potential issues
                if not analysis['has_modules']:
                    analysis['potential_issues'].append("Course has no modules array")
                elif analysis['module_count'] == 0:
                    analysis['potential_issues'].append("Course modules array is empty")
                elif analysis['total_lessons'] == 0:
                    analysis['potential_issues'].append("Course has modules but no lessons")
                elif analysis['empty_modules'] > 0:
                    analysis['potential_issues'].append(f"{analysis['empty_modules']} modules have no lessons")
                
                # Check for missing required fields
                missing_fields = [field for field, present in analysis['required_fields_present'].items() if not present]
                if missing_fields:
                    analysis['potential_issues'].append(f"Missing required fields: {', '.join(missing_fields)}")
                
                if len(analysis['potential_issues']) == 0:
                    self.log_result(
                        "Course Structure Analysis", 
                        "PASS", 
                        f"✅ Course structure is compatible with frontend expectations",
                        f"Modules: {analysis['module_count']}, Lessons: {analysis['total_lessons']}, Lesson types: {analysis['lesson_types']}"
                    )
                else:
                    self.log_result(
                        "Course Structure Analysis", 
                        "FAIL", 
                        f"❌ Course structure has potential compatibility issues",
                        f"Issues: {'; '.join(analysis['potential_issues'])}"
                    )
                
                return analysis
                
            elif response.status_code == 404:
                self.log_result(
                    "Course Structure Analysis", 
                    "FAIL", 
                    f"❌ CRITICAL: Course not found (404) - this would cause white screen",
                    f"Course ID {self.target_course_id} returns 404 when accessed by student"
                )
            else:
                self.log_result(
                    "Course Structure Analysis", 
                    "FAIL", 
                    f"Failed to retrieve course details, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Structure Analysis", 
                "FAIL", 
                "Failed to analyze course structure",
                str(e)
            )
        return False
    
    def analyze_enrollment_data_structure(self):
        """Analyze enrollment data structure for missing fields"""
        if "student" not in self.auth_tokens:
            self.log_result(
                "Enrollment Data Structure Analysis", 
                "SKIP", 
                "No student token available",
                "Student authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                
                if not enrollments:
                    self.log_result(
                        "Enrollment Data Structure Analysis", 
                        "FAIL", 
                        f"❌ Student has no enrollments - this explains white screen on 'Continue Learning'",
                        "Student needs to be enrolled in courses to see content"
                    )
                    return False
                
                # Analyze enrollment structure
                analysis = {
                    'total_enrollments': len(enrollments),
                    'required_fields_present': {},
                    'optional_fields_present': {},
                    'missing_fields': [],
                    'data_issues': []
                }
                
                # Check required fields for frontend
                required_fields = ['id', 'userId', 'courseId', 'enrolledAt', 'progress', 'status']
                optional_fields = ['completedAt', 'moduleProgress', 'currentModuleId', 'currentLessonId', 'lastAccessedAt']
                
                # Analyze first enrollment as sample
                sample_enrollment = enrollments[0]
                
                for field in required_fields:
                    analysis['required_fields_present'][field] = field in sample_enrollment and sample_enrollment[field] is not None
                    if not analysis['required_fields_present'][field]:
                        analysis['missing_fields'].append(field)
                
                for field in optional_fields:
                    analysis['optional_fields_present'][field] = field in sample_enrollment and sample_enrollment[field] is not None
                
                # Check for data issues
                for enrollment in enrollments:
                    course_id = enrollment.get('courseId')
                    if not course_id:
                        analysis['data_issues'].append("Enrollment missing courseId")
                        continue
                    
                    # Test if course exists
                    try:
                        course_response = requests.get(
                            f"{BACKEND_URL}/courses/{course_id}",
                            timeout=TEST_TIMEOUT,
                            headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                        )
                        if course_response.status_code == 404:
                            analysis['data_issues'].append(f"Orphaned enrollment - course {course_id} not found")
                    except:
                        pass
                
                if len(analysis['missing_fields']) == 0 and len(analysis['data_issues']) == 0:
                    self.log_result(
                        "Enrollment Data Structure Analysis", 
                        "PASS", 
                        f"✅ Enrollment data structure is complete and valid",
                        f"Enrollments: {analysis['total_enrollments']}, Required fields: all present, Optional fields: {sum(analysis['optional_fields_present'].values())}/{len(optional_fields)}"
                    )
                else:
                    issues = []
                    if analysis['missing_fields']:
                        issues.append(f"Missing required fields: {', '.join(analysis['missing_fields'])}")
                    if analysis['data_issues']:
                        issues.append(f"Data issues: {'; '.join(analysis['data_issues'])}")
                    
                    self.log_result(
                        "Enrollment Data Structure Analysis", 
                        "FAIL", 
                        f"❌ Enrollment data structure has issues that could cause white screen",
                        '; '.join(issues)
                    )
                
                return analysis
                
            else:
                self.log_result(
                    "Enrollment Data Structure Analysis", 
                    "FAIL", 
                    f"Failed to retrieve enrollments, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Enrollment Data Structure Analysis", 
                "FAIL", 
                "Failed to analyze enrollment data structure",
                str(e)
            )
        return False
    
    def test_course_access_flow(self):
        """Test the specific course access flow that would happen when clicking 'Continue Learning'"""
        if "student" not in self.auth_tokens or not self.target_course_id:
            self.log_result(
                "Course Access Flow Test", 
                "SKIP", 
                "Missing student token or target course ID",
                f"Student token: {bool('student' in self.auth_tokens)}, Course ID: {bool(self.target_course_id)}"
            )
            return False
        
        flow_steps = []
        
        try:
            # Step 1: Get student's enrollments (what happens when clicking Continue Learning)
            print("   Step 1: Getting student enrollments...")
            enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
            )
            
            if enrollments_response.status_code == 200:
                enrollments = enrollments_response.json()
                flow_steps.append(f"✅ Step 1: Retrieved {len(enrollments)} enrollments")
                
                # Step 2: Find target course enrollment
                print("   Step 2: Finding target course enrollment...")
                target_enrollment = None
                for enrollment in enrollments:
                    if enrollment.get('courseId') == self.target_course_id:
                        target_enrollment = enrollment
                        break
                
                if target_enrollment:
                    flow_steps.append(f"✅ Step 2: Found target course enrollment")
                    
                    # Step 3: Get course details (what CourseDetail.js would do)
                    print("   Step 3: Getting course details...")
                    course_response = requests.get(
                        f"{BACKEND_URL}/courses/{self.target_course_id}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {self.auth_tokens["student"]}'}
                    )
                    
                    if course_response.status_code == 200:
                        course = course_response.json()
                        flow_steps.append(f"✅ Step 3: Retrieved course details")
                        
                        # Step 4: Validate course has content
                        print("   Step 4: Validating course content...")
                        modules = course.get('modules', [])
                        if modules and len(modules) > 0:
                            total_lessons = sum(len(module.get('lessons', [])) for module in modules)
                            if total_lessons > 0:
                                flow_steps.append(f"✅ Step 4: Course has {len(modules)} modules and {total_lessons} lessons")
                                
                                self.log_result(
                                    "Course Access Flow Test", 
                                    "PASS", 
                                    f"✅ Complete course access flow successful",
                                    '; '.join(flow_steps)
                                )
                                return True
                            else:
                                flow_steps.append(f"❌ Step 4: Course has modules but no lessons")
                        else:
                            flow_steps.append(f"❌ Step 4: Course has no modules")
                    else:
                        flow_steps.append(f"❌ Step 3: Course details request failed ({course_response.status_code})")
                else:
                    flow_steps.append(f"❌ Step 2: Target course enrollment not found")
            else:
                flow_steps.append(f"❌ Step 1: Enrollments request failed ({enrollments_response.status_code})")
            
            self.log_result(
                "Course Access Flow Test", 
                "FAIL", 
                f"❌ Course access flow failed - this would cause white screen",
                '; '.join(flow_steps)
            )
            
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Access Flow Test", 
                "FAIL", 
                "Course access flow failed due to network error",
                str(e)
            )
        return False
    
    def run_investigation(self):
        """Run the complete investigation"""
        print("🔍 STUDENT COURSE ACCESS INVESTIGATION - DATA STRUCTURE ANALYSIS")
        print("=" * 80)
        print(f"Target Course: {self.target_course_name}")
        print(f"Student: {STUDENT_CREDENTIALS['username_or_email']}")
        print(f"Backend: {BACKEND_URL}")
        print("=" * 80)
        
        # Step 1: Admin authentication
        print("\n🔑 STEP 1: Admin Authentication")
        print("-" * 50)
        admin_success = self.test_admin_login()
        
        # Step 2: Student authentication
        print("\n🎓 STEP 2: Student Authentication")
        print("-" * 50)
        student_success = self.test_student_login()
        
        # Step 3: Find target course
        print("\n📚 STEP 3: Find Target Course")
        print("-" * 50)
        course_found = self.find_target_course()
        
        # Step 4: Check student enrollment status
        print("\n📝 STEP 4: Check Student Enrollment Status")
        print("-" * 50)
        enrollment_status = self.check_student_enrollment_status()
        
        # Step 5: Analyze course structure
        print("\n🏗️ STEP 5: Analyze Course Structure")
        print("-" * 50)
        course_analysis = self.analyze_course_structure()
        
        # Step 6: Analyze enrollment data structure
        print("\n📊 STEP 6: Analyze Enrollment Data Structure")
        print("-" * 50)
        enrollment_analysis = self.analyze_enrollment_data_structure()
        
        # Step 7: Test complete course access flow
        print("\n🔄 STEP 7: Test Course Access Flow")
        print("-" * 50)
        flow_success = self.test_course_access_flow()
        
        # Summary
        print("\n📋 INVESTIGATION SUMMARY")
        print("=" * 50)
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📊 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        # Root cause analysis
        print("\n🎯 ROOT CAUSE ANALYSIS")
        print("-" * 30)
        
        if not student_success:
            print("❌ CRITICAL: Student authentication failed - this would cause white screen")
        elif not course_found:
            print("❌ CRITICAL: Target course not found - this would cause white screen")
        elif not enrollment_status:
            print("❌ CRITICAL: Student not enrolled in target course - this explains white screen on 'Continue Learning'")
        elif not flow_success:
            print("❌ CRITICAL: Course access flow failed - this would cause white screen")
        else:
            print("✅ All critical components working - white screen may be frontend-related")
        
        return self.passed > self.failed

if __name__ == "__main__":
    tester = StudentCourseAccessTester()
    success = tester.run_investigation()
    
    if success:
        print("\n🎉 Investigation completed successfully")
        sys.exit(0)
    else:
        print("\n⚠️ Investigation found critical issues")
        sys.exit(1)