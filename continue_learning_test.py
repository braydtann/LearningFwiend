#!/usr/bin/env python3
"""
Continue Learning Blank Page Investigation
Focused test for the specific issue reported
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001/api"
TEST_TIMEOUT = 15

class ContinueLearningTester:
    def __init__(self):
        self.auth_tokens = {}
        
    def log_result(self, test_name, status, message, details=None):
        """Log test result"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if status == 'PASS':
            print(f"[{timestamp}] ✅ {test_name}: {message}")
        elif status == 'FAIL':
            print(f"[{timestamp}] ❌ {test_name}: {message}")
        else:
            print(f"[{timestamp}] ℹ️  {test_name}: {message}")
        
        if details:
            print(f"    Details: {details}")
    
    def login_student(self):
        """Login as student to get auth token"""
        try:
            login_data = {
                "username_or_email": "student",
                "password": "Student123!"
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
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['learner'] = token
                    self.log_result(
                        "Student Login", 
                        "PASS", 
                        f"Successfully logged in as student: {user_info.get('username')}",
                        f"User ID: {user_info.get('id')}, Role: {user_info.get('role')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Student Login", 
                        "FAIL", 
                        "Login successful but missing token or wrong role",
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
                "Failed to login as student",
                str(e)
            )
        return False
    
    def test_get_available_courses(self):
        """Test GET /api/courses to see what courses are available"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["learner"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                
                self.log_result(
                    "Get Available Courses", 
                    "PASS", 
                    f"Successfully retrieved {len(courses)} available courses from database",
                    f"First 3 courses: {[c.get('title', 'No title') for c in courses[:3]]}"
                )
                
                # Print detailed course information
                print("\n📚 AVAILABLE COURSES DETAILS:")
                print("=" * 50)
                for i, course in enumerate(courses[:5], 1):
                    print(f"{i}. Title: {course.get('title', 'No title')}")
                    print(f"   ID: {course.get('id', 'No ID')}")
                    print(f"   Status: {course.get('status', 'No status')}")
                    print(f"   Instructor: {course.get('instructor', 'No instructor')}")
                    print(f"   Modules: {len(course.get('modules', []))}")
                    print(f"   Description: {course.get('description', 'No description')[:100]}...")
                    print()
                
                return courses
            else:
                self.log_result(
                    "Get Available Courses", 
                    "FAIL", 
                    f"Failed to retrieve courses, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Get Available Courses", 
                "FAIL", 
                "Failed to test course retrieval",
                str(e)
            )
        return []
    
    def test_student_enrollments(self):
        """Test GET /api/enrollments to see what courses student is enrolled in"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["learner"]}'}
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                
                if enrollments:
                    self.log_result(
                        "Student Enrollments", 
                        "PASS", 
                        f"Student has {len(enrollments)} course enrollments",
                        f"Enrolled course IDs: {[e.get('courseId', 'No ID')[:8] + '...' for e in enrollments[:3]]}"
                    )
                    
                    # Print detailed enrollment information
                    print("\n🎓 STUDENT ENROLLMENTS DETAILS:")
                    print("=" * 50)
                    for i, enrollment in enumerate(enrollments, 1):
                        print(f"{i}. Course ID: {enrollment.get('courseId', 'No ID')}")
                        print(f"   Enrolled At: {enrollment.get('enrolledAt', 'No date')}")
                        print(f"   Progress: {enrollment.get('progress', 0)}%")
                        print(f"   Status: {enrollment.get('status', 'No status')}")
                        print()
                    
                    return enrollments
                else:
                    self.log_result(
                        "Student Enrollments", 
                        "INFO", 
                        "Student has no course enrollments (empty list)",
                        "This could explain blank 'Continue Learning' page - no enrolled courses"
                    )
                    return []
            else:
                self.log_result(
                    "Student Enrollments", 
                    "FAIL", 
                    f"Failed to retrieve student enrollments, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Student Enrollments", 
                "FAIL", 
                "Failed to test student enrollments",
                str(e)
            )
        return []
    
    def test_course_detail_by_id(self, course_id, course_title="Unknown"):
        """Test GET /api/courses/{course_id} for a specific course"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["learner"]}'}
            )
            
            if response.status_code == 200:
                course_data = response.json()
                
                # Check for fields that CourseDetail.js needs
                critical_fields = ['id', 'title', 'description', 'modules', 'instructor']
                missing_critical = [field for field in critical_fields if field not in course_data]
                
                # Check modules structure
                modules = course_data.get('modules', [])
                modules_valid = True
                if modules:
                    for module in modules:
                        if not isinstance(module, dict) or 'title' not in module:
                            modules_valid = False
                            break
                
                if not missing_critical and modules_valid:
                    self.log_result(
                        f"Course Detail - {course_title}", 
                        "PASS", 
                        f"Course detail endpoint returns complete data for CourseDetail.js",
                        f"Course has all required fields and {len(modules)} modules"
                    )
                    
                    # Print detailed course information
                    print(f"\n📖 COURSE DETAIL - {course_title}:")
                    print("=" * 50)
                    print(f"ID: {course_data.get('id')}")
                    print(f"Title: {course_data.get('title')}")
                    print(f"Description: {course_data.get('description', '')[:200]}...")
                    print(f"Instructor: {course_data.get('instructor')}")
                    print(f"Status: {course_data.get('status')}")
                    print(f"Modules: {len(modules)}")
                    if modules:
                        print("Module titles:")
                        for i, module in enumerate(modules[:3], 1):
                            print(f"  {i}. {module.get('title', 'No title')}")
                    print()
                    
                    return True
                else:
                    self.log_result(
                        f"Course Detail - {course_title}", 
                        "FAIL", 
                        f"Course detail endpoint missing critical data for CourseDetail.js",
                        f"Missing fields: {missing_critical}, Modules valid: {modules_valid}"
                    )
            elif response.status_code == 404:
                self.log_result(
                    f"Course Detail - {course_title}", 
                    "FAIL", 
                    f"Course not found (404) - This would cause CourseDetail.js to show blank page",
                    f"Course ID: {course_id}"
                )
            else:
                self.log_result(
                    f"Course Detail - {course_title}", 
                    "FAIL", 
                    f"Course detail endpoint failed, status: {response.status_code}",
                    f"This would cause CourseDetail.js to show blank page. Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                f"Course Detail - {course_title}", 
                "FAIL", 
                "Course detail endpoint request failed",
                f"Network error would cause blank page: {str(e)}"
            )
        return False
    
    def cross_reference_enrollments_with_courses(self, enrollments, courses):
        """Cross-reference student enrollments with available courses"""
        print("\n🔍 CROSS-REFERENCING ENROLLMENTS WITH COURSES:")
        print("=" * 60)
        
        if not enrollments:
            print("❌ Student has no enrollments - this explains the blank 'Continue Learning' page")
            return False
        
        if not courses:
            print("❌ No courses available in database - this would cause blank pages")
            return False
        
        # Create a lookup dictionary for courses
        course_lookup = {course.get('id'): course for course in courses}
        
        valid_enrollments = 0
        invalid_enrollments = 0
        
        for enrollment in enrollments:
            course_id = enrollment.get('courseId')
            if course_id in course_lookup:
                course = course_lookup[course_id]
                print(f"✅ Enrollment valid: {course.get('title', 'No title')} (ID: {course_id[:8]}...)")
                valid_enrollments += 1
            else:
                print(f"❌ Enrollment invalid: Course ID {course_id[:8]}... not found in available courses")
                invalid_enrollments += 1
        
        if invalid_enrollments > 0:
            print(f"\n🚨 ISSUE FOUND: {invalid_enrollments} enrollments reference non-existent courses!")
            print("This would cause 'Continue Learning' to show blank pages when trying to load course details.")
            return False
        else:
            print(f"\n✅ All {valid_enrollments} enrollments reference valid courses")
            return True
    
    def run_investigation(self):
        """Run the complete Continue Learning investigation"""
        print("🔍 CONTINUE LEARNING BLANK PAGE INVESTIGATION")
        print("=" * 60)
        print("Investigating why CourseDetail.js shows a blank page when students click 'Continue Learning'")
        print()
        
        # Step 1: Login as student
        if not self.login_student():
            print("❌ Cannot proceed without student authentication")
            return
        
        # Step 2: Check available courses in database
        print("\n📚 STEP 1: Checking available courses in database...")
        available_courses = self.test_get_available_courses()
        
        # Step 3: Check student enrollments
        print("\n🎓 STEP 2: Checking student enrollments...")
        enrollments = self.test_student_enrollments()
        
        # Step 4: Cross-reference enrollments with courses
        print("\n🔍 STEP 3: Cross-referencing enrollments with available courses...")
        valid_cross_ref = self.cross_reference_enrollments_with_courses(enrollments, available_courses)
        
        # Step 5: Test course detail endpoints for enrolled courses
        if enrollments and available_courses:
            print("\n📖 STEP 4: Testing course detail endpoints for enrolled courses...")
            course_lookup = {course.get('id'): course for course in available_courses}
            
            for enrollment in enrollments[:3]:  # Test first 3 enrollments
                course_id = enrollment.get('courseId')
                course = course_lookup.get(course_id)
                course_title = course.get('title', 'Unknown') if course else 'Unknown'
                self.test_course_detail_by_id(course_id, course_title)
        
        # Step 6: Summary and diagnosis
        print("\n🏁 INVESTIGATION SUMMARY:")
        print("=" * 60)
        
        if not available_courses:
            print("❌ ROOT CAUSE: No courses available in database")
            print("   SOLUTION: Create courses or check database connectivity")
        elif not enrollments:
            print("❌ ROOT CAUSE: Student has no course enrollments")
            print("   SOLUTION: Enroll student in courses or check enrollment system")
        elif not valid_cross_ref:
            print("❌ ROOT CAUSE: Student enrollments reference non-existent courses")
            print("   SOLUTION: Clean up invalid enrollments or restore missing courses")
        else:
            print("✅ All systems appear to be working correctly")
            print("   The blank page issue may be in the frontend CourseDetail.js component")
            print("   or in the specific course ID being accessed")

if __name__ == "__main__":
    tester = ContinueLearningTester()
    tester.run_investigation()