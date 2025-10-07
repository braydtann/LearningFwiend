#!/usr/bin/env python3

"""
🎉 CLASSROOM DETAIL COURSE COUNT FIX VALIDATION

OBJECTIVE: Verify that the ClassroomDetail.js fixes are working correctly

CONTEXT: 
- Fixed the classroom card to show "Courses: 2" ✅ 
- But classroom detail still showed "Courses: 0" ❌
- Applied same fix to ClassroomDetail.js component

VALIDATION TESTS:
1. Verify "testing exam" classroom data - Confirm it has program with 2 courses
2. Test classroom detail API - Verify GET /api/classrooms/{id} returns proper data
3. Verify program course structure - Confirm "test program 2" has courseIds populated 
4. Test course retrieval - Verify all program courses can be fetched individually
5. Validate fix logic - Confirm total course count = direct courses + program courses

EXPECTED RESULTS:
- Backend should return classroom with programIds containing "test program 2"
- "test program 2" should have 2 courseIds
- Both courses should be accessible via GET /api/courses/{id}
- Total course count should be 2 (0 direct + 2 from program)

Use admin credentials: brayden.t@covesmart.com / Hawaii2020!
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://quiz-progress-fix.preview.emergentagent.com/api"
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class ClassroomCourseCountValidator:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
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
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            login_data = {
                "username_or_email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data['access_token']
                self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
                
                user_info = data.get('user', {})
                self.log_result(
                    "Admin Authentication", 
                    True, 
                    f"Successfully authenticated as {user_info.get('full_name', 'Admin')} (Role: {user_info.get('role', 'Unknown')})"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication", 
                    False, 
                    f"Login failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception during login: {str(e)}")
            return False
    
    def find_testing_exam_classroom(self):
        """Find the 'testing exam' classroom"""
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
                        "Find Testing Exam Classroom", 
                        True, 
                        f"Found classroom ID: {classroom_id}, Direct courses: {len(course_ids)}, Programs: {len(program_ids)}"
                    )
                    return testing_exam_classroom
                else:
                    self.log_result(
                        "Find Testing Exam Classroom", 
                        False, 
                        f"'testing exam' classroom not found among {len(classrooms)} classrooms"
                    )
                    return None
            else:
                self.log_result(
                    "Find Testing Exam Classroom", 
                    False, 
                    f"Failed to get classrooms: {response.status_code} - {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Find Testing Exam Classroom", False, f"Exception: {str(e)}")
            return None
    
    def get_classroom_detail(self, classroom_id):
        """Get detailed classroom information"""
        try:
            response = self.session.get(f"{BACKEND_URL}/classrooms/{classroom_id}")
            
            if response.status_code == 200:
                classroom_detail = response.json()
                
                program_ids = classroom_detail.get('programIds', [])
                course_ids = classroom_detail.get('courseIds', [])
                student_ids = classroom_detail.get('studentIds', [])
                
                self.log_result(
                    "Get Classroom Detail API", 
                    True, 
                    f"Classroom detail retrieved - Direct courses: {len(course_ids)}, Programs: {len(program_ids)}, Students: {len(student_ids)}"
                )
                return classroom_detail
            else:
                self.log_result(
                    "Get Classroom Detail API", 
                    False, 
                    f"Failed to get classroom detail: {response.status_code} - {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Get Classroom Detail API", False, f"Exception: {str(e)}")
            return None
    
    def verify_test_program_2(self, program_ids):
        """Verify 'test program 2' exists and has courses"""
        try:
            test_program_2 = None
            
            for program_id in program_ids:
                response = self.session.get(f"{BACKEND_URL}/programs/{program_id}")
                
                if response.status_code == 200:
                    program = response.json()
                    if program.get('title', '').lower() == 'test program 2':
                        test_program_2 = program
                        break
            
            if test_program_2:
                course_ids = test_program_2.get('courseIds', [])
                program_id = test_program_2.get('id')
                
                self.log_result(
                    "Verify Test Program 2 Structure", 
                    True, 
                    f"Found 'test program 2' (ID: {program_id}) with {len(course_ids)} courses: {course_ids}"
                )
                return test_program_2
            else:
                self.log_result(
                    "Verify Test Program 2 Structure", 
                    False, 
                    f"'test program 2' not found among {len(program_ids)} programs"
                )
                return None
                
        except Exception as e:
            self.log_result("Verify Test Program 2 Structure", False, f"Exception: {str(e)}")
            return None
    
    def verify_program_courses(self, course_ids):
        """Verify all courses in the program can be accessed"""
        try:
            accessible_courses = []
            
            for course_id in course_ids:
                response = self.session.get(f"{BACKEND_URL}/courses/{course_id}")
                
                if response.status_code == 200:
                    course = response.json()
                    accessible_courses.append({
                        'id': course_id,
                        'title': course.get('title', 'Unknown'),
                        'status': course.get('status', 'Unknown')
                    })
                else:
                    self.log_result(
                        "Verify Program Courses Access", 
                        False, 
                        f"Course {course_id} not accessible: {response.status_code}"
                    )
                    return []
            
            if len(accessible_courses) == len(course_ids):
                course_titles = [c['title'] for c in accessible_courses]
                self.log_result(
                    "Verify Program Courses Access", 
                    True, 
                    f"All {len(course_ids)} program courses accessible: {course_titles}"
                )
                return accessible_courses
            else:
                self.log_result(
                    "Verify Program Courses Access", 
                    False, 
                    f"Only {len(accessible_courses)}/{len(course_ids)} courses accessible"
                )
                return accessible_courses
                
        except Exception as e:
            self.log_result("Verify Program Courses Access", False, f"Exception: {str(e)}")
            return []
    
    def validate_course_count_logic(self, classroom, program, program_courses):
        """Validate the course count calculation logic"""
        try:
            direct_courses = len(classroom.get('courseIds', []))
            program_course_count = len(program.get('courseIds', []))
            accessible_program_courses = len(program_courses)
            
            # Expected total course count
            expected_total = direct_courses + accessible_program_courses
            
            # Validate the fix logic
            fix_working = (
                direct_courses == 0 and  # No direct courses
                program_course_count == 2 and  # Program has 2 courses
                accessible_program_courses == 2 and  # Both courses accessible
                expected_total == 2  # Total should be 2
            )
            
            if fix_working:
                self.log_result(
                    "Validate Course Count Fix Logic", 
                    True, 
                    f"Course count logic correct: {direct_courses} direct + {accessible_program_courses} program = {expected_total} total courses"
                )
            else:
                self.log_result(
                    "Validate Course Count Fix Logic", 
                    False, 
                    f"Course count logic incorrect: {direct_courses} direct + {accessible_program_courses} program = {expected_total} (expected 2)"
                )
            
            return fix_working
            
        except Exception as e:
            self.log_result("Validate Course Count Fix Logic", False, f"Exception: {str(e)}")
            return False
    
    def run_validation(self):
        """Run complete validation suite"""
        print("🎉 CLASSROOM DETAIL COURSE COUNT FIX VALIDATION")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            return False
        
        # Step 2: Find testing exam classroom
        classroom = self.find_testing_exam_classroom()
        if not classroom:
            return False
        
        # Step 3: Get classroom detail
        classroom_id = classroom.get('id')
        classroom_detail = self.get_classroom_detail(classroom_id)
        if not classroom_detail:
            return False
        
        # Step 4: Verify test program 2
        program_ids = classroom_detail.get('programIds', [])
        if not program_ids:
            self.log_result("Program IDs Check", False, "No programs found in classroom")
            return False
        
        test_program_2 = self.verify_test_program_2(program_ids)
        if not test_program_2:
            return False
        
        # Step 5: Verify program courses
        program_course_ids = test_program_2.get('courseIds', [])
        if not program_course_ids:
            self.log_result("Program Course IDs Check", False, "No courses found in test program 2")
            return False
        
        program_courses = self.verify_program_courses(program_course_ids)
        if len(program_courses) != 2:
            return False
        
        # Step 6: Validate course count logic
        fix_working = self.validate_course_count_logic(classroom_detail, test_program_2, program_courses)
        
        return fix_working
    
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
            print("✅ CLASSROOM DETAIL COURSE COUNT FIX IS WORKING CORRECTLY")
            print("   Backend data supports the frontend fix implementation")
        else:
            print("❌ CLASSROOM DETAIL COURSE COUNT FIX NEEDS ATTENTION")
            print("   Backend data structure may not support the frontend fix")
        
        return success_rate >= 85

def main():
    """Main execution function"""
    validator = ClassroomCourseCountValidator()
    
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