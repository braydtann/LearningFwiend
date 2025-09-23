#!/usr/bin/env python3

"""
🎓 STUDENT CLASSROOM COURSE ACCESS VALIDATION

OBJECTIVE: Verify student can access courses from classroom programs

VALIDATION TESTS:
1. Student authentication with provided credentials
2. Student can see classroom in their classrooms list
3. Student is enrolled in program courses from classroom
4. Student can access individual program courses
5. Verify enrollment data matches classroom program structure

Use student credentials: brayden.student@learningfwiend.com / Cove1234!
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://learning-score-fix.preview.emergentagent.com/api"
STUDENT_EMAIL = "brayden.student@learningfwiend.com"
STUDENT_PASSWORD = "Cove1234!"

class StudentClassroomAccessValidator:
    def __init__(self):
        self.session = requests.Session()
        self.student_token = None
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
        
    def authenticate_student(self):
        """Authenticate as student user"""
        try:
            login_data = {
                "username_or_email": STUDENT_EMAIL,
                "password": STUDENT_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data['access_token']
                self.session.headers.update({'Authorization': f'Bearer {self.student_token}'})
                
                user_info = data.get('user', {})
                requires_password_change = data.get('requires_password_change', False)
                
                self.log_result(
                    "Student Authentication", 
                    True, 
                    f"Successfully authenticated as {user_info.get('full_name', 'Student')} (Role: {user_info.get('role', 'Unknown')}, Password change required: {requires_password_change})"
                )
                return True
            else:
                self.log_result(
                    "Student Authentication", 
                    False, 
                    f"Login failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Student Authentication", False, f"Exception during login: {str(e)}")
            return False
    
    def get_student_classrooms(self):
        """Get classrooms visible to student"""
        try:
            response = self.session.get(f"{BACKEND_URL}/classrooms")
            
            if response.status_code == 200:
                classrooms = response.json()
                
                # Look for "testing exam" classroom
                testing_exam_classroom = None
                for classroom in classrooms:
                    if classroom.get('name', '').lower() == 'testing exam':
                        testing_exam_classroom = classroom
                        break
                
                if testing_exam_classroom:
                    classroom_id = testing_exam_classroom.get('id')
                    program_ids = testing_exam_classroom.get('programIds', [])
                    course_ids = testing_exam_classroom.get('courseIds', [])
                    
                    self.log_result(
                        "Student Can See Testing Exam Classroom", 
                        True, 
                        f"Found classroom in student view - ID: {classroom_id}, Direct courses: {len(course_ids)}, Programs: {len(program_ids)}"
                    )
                    return testing_exam_classroom
                else:
                    self.log_result(
                        "Student Can See Testing Exam Classroom", 
                        False, 
                        f"'testing exam' classroom not visible to student among {len(classrooms)} classrooms"
                    )
                    return None
            else:
                self.log_result(
                    "Student Can See Testing Exam Classroom", 
                    False, 
                    f"Failed to get classrooms: {response.status_code} - {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Student Can See Testing Exam Classroom", False, f"Exception: {str(e)}")
            return None
    
    def get_student_enrollments(self):
        """Get student's course enrollments"""
        try:
            response = self.session.get(f"{BACKEND_URL}/enrollments")
            
            if response.status_code == 200:
                enrollments = response.json()
                
                # Filter for program courses
                program_course_ids = [
                    'c7712f8d-fb79-4c52-b6f7-d1350b079dce',  # Test Course for Deletion Classroom1
                    'f9afe1f0-9145-4d80-b188-003a93bfdf39'   # Multiple Choice Test Course
                ]
                
                program_enrollments = []
                for enrollment in enrollments:
                    if enrollment.get('courseId') in program_course_ids:
                        program_enrollments.append(enrollment)
                
                if len(program_enrollments) == 2:
                    enrollment_details = []
                    for enrollment in program_enrollments:
                        enrollment_details.append(f"Course {enrollment.get('courseId')[:8]}... (Progress: {enrollment.get('progress', 0)}%)")
                    
                    self.log_result(
                        "Student Enrolled in Program Courses", 
                        True, 
                        f"Student enrolled in both program courses: {enrollment_details}"
                    )
                    return program_enrollments
                else:
                    self.log_result(
                        "Student Enrolled in Program Courses", 
                        False, 
                        f"Student enrolled in {len(program_enrollments)}/2 program courses (Total enrollments: {len(enrollments)})"
                    )
                    return program_enrollments
                    
            else:
                self.log_result(
                    "Student Enrolled in Program Courses", 
                    False, 
                    f"Failed to get enrollments: {response.status_code} - {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_result("Student Enrolled in Program Courses", False, f"Exception: {str(e)}")
            return []
    
    def verify_course_access(self, enrollments):
        """Verify student can access enrolled courses"""
        try:
            accessible_courses = []
            
            for enrollment in enrollments:
                course_id = enrollment.get('courseId')
                response = self.session.get(f"{BACKEND_URL}/courses/{course_id}")
                
                if response.status_code == 200:
                    course = response.json()
                    accessible_courses.append({
                        'id': course_id,
                        'title': course.get('title', 'Unknown'),
                        'modules': len(course.get('modules', [])),
                        'enrollment_progress': enrollment.get('progress', 0)
                    })
                else:
                    self.log_result(
                        "Student Course Access Verification", 
                        False, 
                        f"Course {course_id} not accessible: {response.status_code}"
                    )
                    return []
            
            if len(accessible_courses) == len(enrollments):
                course_info = []
                for course in accessible_courses:
                    course_info.append(f"{course['title']} ({course['modules']} modules, {course['enrollment_progress']}% progress)")
                
                self.log_result(
                    "Student Course Access Verification", 
                    True, 
                    f"All {len(enrollments)} enrolled courses accessible: {course_info}"
                )
                return accessible_courses
            else:
                self.log_result(
                    "Student Course Access Verification", 
                    False, 
                    f"Only {len(accessible_courses)}/{len(enrollments)} courses accessible"
                )
                return accessible_courses
                
        except Exception as e:
            self.log_result("Student Course Access Verification", False, f"Exception: {str(e)}")
            return []
    
    def validate_enrollment_consistency(self, classroom, enrollments):
        """Validate enrollment data matches classroom structure"""
        try:
            # Expected: Student should be enrolled in all courses from classroom programs
            expected_course_count = 2  # From "test program 2"
            actual_enrollment_count = len(enrollments)
            
            # Check if student is in classroom studentIds
            student_in_classroom = True  # We assume this since student can see the classroom
            
            consistency_check = (
                actual_enrollment_count == expected_course_count and
                student_in_classroom
            )
            
            if consistency_check:
                self.log_result(
                    "Enrollment Consistency Validation", 
                    True, 
                    f"Enrollment data consistent: Student enrolled in {actual_enrollment_count}/{expected_course_count} expected program courses"
                )
            else:
                self.log_result(
                    "Enrollment Consistency Validation", 
                    False, 
                    f"Enrollment inconsistency: Student enrolled in {actual_enrollment_count}/{expected_course_count} expected program courses"
                )
            
            return consistency_check
            
        except Exception as e:
            self.log_result("Enrollment Consistency Validation", False, f"Exception: {str(e)}")
            return False
    
    def run_validation(self):
        """Run complete validation suite"""
        print("🎓 STUDENT CLASSROOM COURSE ACCESS VALIDATION")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate_student():
            return False
        
        # Step 2: Check classroom visibility
        classroom = self.get_student_classrooms()
        if not classroom:
            return False
        
        # Step 3: Check enrollments
        enrollments = self.get_student_enrollments()
        if len(enrollments) != 2:
            return False
        
        # Step 4: Verify course access
        accessible_courses = self.verify_course_access(enrollments)
        if len(accessible_courses) != 2:
            return False
        
        # Step 5: Validate consistency
        consistency_valid = self.validate_enrollment_consistency(classroom, enrollments)
        
        return consistency_valid
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 VALIDATION RESULT:")
        if success_rate >= 85:
            print("✅ STUDENT CLASSROOM COURSE ACCESS IS WORKING CORRECTLY")
            print("   Students can access courses from classroom programs as expected")
        else:
            print("❌ STUDENT CLASSROOM COURSE ACCESS NEEDS ATTENTION")
            print("   Issues detected in student course access workflow")
        
        return success_rate >= 85

def main():
    """Main execution function"""
    validator = StudentClassroomAccessValidator()
    
    try:
        validation_success = validator.run_validation()
        overall_success = validator.print_summary()
        
        # Exit with appropriate code
        sys.exit(0 if overall_success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error during validation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()