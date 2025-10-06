#!/usr/bin/env python3
"""
Detailed Final Exam Access Test
Investigating the specific "No final test available for this program" issue
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://grade-flow-wizard.preview.emergentagent.com/api"

# Test credentials
STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class DetailedFinalExamTester:
    def __init__(self):
        self.student_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate_student(self):
        """Authenticate student and return token"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=STUDENT_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                self.log_result("Student Authentication", True, 
                              f"User: {user_info.get('full_name', 'Unknown')} ({user_info.get('role', 'Unknown')})")
                return token
            else:
                self.log_result("Student Authentication", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_result("Student Authentication", False, f"Exception: {str(e)}")
            return None
    
    def get_student_enrolled_programs(self):
        """Get programs student is enrolled in through classrooms"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get student's classrooms
            response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers)
            if response.status_code != 200:
                self.log_result("Get Student Classrooms", False, f"Status: {response.status_code}")
                return []
            
            classrooms = response.json()
            student_classrooms = []
            
            # Find classrooms where student is enrolled
            for classroom in classrooms:
                if classroom.get('studentIds') and any(student_id for student_id in classroom.get('studentIds', [])):
                    student_classrooms.append(classroom)
            
            self.log_result("Student Enrolled Classrooms", True, f"Found {len(student_classrooms)} classrooms")
            
            # Extract program IDs from classrooms
            enrolled_program_ids = set()
            for classroom in student_classrooms:
                program_ids = classroom.get('programIds', [])
                enrolled_program_ids.update(program_ids)
            
            self.log_result("Student Enrolled Programs", True, f"Enrolled in {len(enrolled_program_ids)} programs")
            
            return list(enrolled_program_ids)
            
        except Exception as e:
            self.log_result("Get Student Enrolled Programs", False, f"Exception: {str(e)}")
            return []
    
    def check_program_completion_status(self, program_id):
        """Check if student has completed all courses in a program"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get program details
            response = requests.get(f"{BACKEND_URL}/programs/{program_id}", headers=headers)
            if response.status_code != 200:
                self.log_result(f"Get Program {program_id}", False, f"Status: {response.status_code}")
                return False, "Program not found"
            
            program = response.json()
            program_title = program.get('title', 'Unknown')
            course_ids = program.get('courseIds', [])
            
            self.log_result(f"Program Details ({program_title})", True, f"Contains {len(course_ids)} courses")
            
            # Get student enrollments
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            if response.status_code != 200:
                self.log_result("Get Student Enrollments", False, f"Status: {response.status_code}")
                return False, "Cannot get enrollments"
            
            enrollments = response.json()
            
            # Check completion status for each course in program
            completed_courses = 0
            total_courses = len(course_ids)
            
            for course_id in course_ids:
                enrollment = next((e for e in enrollments if e.get('courseId') == course_id), None)
                if enrollment:
                    progress = enrollment.get('progress', 0)
                    status = enrollment.get('status', 'active')
                    if progress >= 100 or status == 'completed':
                        completed_courses += 1
            
            completion_percentage = (completed_courses / total_courses * 100) if total_courses > 0 else 0
            is_completed = completed_courses == total_courses
            
            self.log_result(f"Program Completion ({program_title})", True, 
                          f"Completed: {completed_courses}/{total_courses} courses ({completion_percentage:.1f}%)")
            
            return is_completed, f"{completed_courses}/{total_courses} courses completed"
            
        except Exception as e:
            self.log_result(f"Check Program Completion {program_id}", False, f"Exception: {str(e)}")
            return False, f"Exception: {str(e)}"
    
    def test_final_test_access_for_program(self, program_id):
        """Test final test access for a specific program"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get program details first
            response = requests.get(f"{BACKEND_URL}/programs/{program_id}", headers=headers)
            if response.status_code != 200:
                self.log_result(f"Program Access {program_id}", False, f"Status: {response.status_code}")
                return
            
            program = response.json()
            program_title = program.get('title', 'Unknown')
            
            # Test final tests for this program
            params = {"program_id": program_id}
            response = requests.get(f"{BACKEND_URL}/final-tests", headers=headers, params=params)
            
            if response.status_code == 200:
                final_tests = response.json()
                test_count = len(final_tests)
                
                if test_count > 0:
                    self.log_result(f"Final Tests Available ({program_title})", True, 
                                  f"Found {test_count} final test(s)")
                    
                    # Check if tests are published and accessible
                    published_tests = [t for t in final_tests if t.get('isPublished', False)]
                    self.log_result(f"Published Final Tests ({program_title})", True,
                                  f"Published: {len(published_tests)}/{test_count}")
                    
                    # Show test details
                    for i, test in enumerate(published_tests[:2]):  # Show first 2 tests
                        test_title = test.get('title', 'Unknown')
                        test_id = test.get('id', 'Unknown')
                        print(f"   Test {i+1}: {test_title} (ID: {test_id})")
                    
                    return published_tests
                else:
                    self.log_result(f"Final Tests Available ({program_title})", False,
                                  "No final tests found for this program")
                    return []
            else:
                self.log_result(f"Final Tests API ({program_title})", False,
                              f"Status: {response.status_code}, Response: {response.text}")
                return []
                
        except Exception as e:
            self.log_result(f"Final Test Access {program_id}", False, f"Exception: {str(e)}")
            return []
    
    def test_final_test_attempt_creation(self, test_id, program_title):
        """Test creating a final test attempt (this might trigger the 422 error)"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Try to create a final test attempt
            attempt_data = {
                "finalTestId": test_id
            }
            
            response = requests.post(f"{BACKEND_URL}/final-test-attempts", 
                                   headers=headers, json=attempt_data)
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                attempt_id = data.get('id', 'Unknown')
                self.log_result(f"Final Test Attempt Creation ({program_title})", True,
                              f"Created attempt: {attempt_id}")
                return True
            elif response.status_code == 422:
                self.log_result(f"Final Test Attempt Creation ({program_title})", False,
                              f"422 ERROR: {response.text}")
                return False
            else:
                self.log_result(f"Final Test Attempt Creation ({program_title})", False,
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"Final Test Attempt Creation ({program_title})", False, f"Exception: {str(e)}")
            return False
    
    def test_program_access_check(self, program_id):
        """Test program access check endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            response = requests.get(f"{BACKEND_URL}/programs/{program_id}/access-check", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                has_access = data.get('hasAccess', False)
                reason = data.get('reason', 'Unknown')
                message = data.get('message', '')
                
                self.log_result(f"Program Access Check {program_id}", True,
                              f"Access: {has_access}, Reason: {reason}, Message: {message}")
                return has_access
            else:
                self.log_result(f"Program Access Check {program_id}", False,
                              f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"Program Access Check {program_id}", False, f"Exception: {str(e)}")
            return False
    
    def run_detailed_investigation(self):
        """Run detailed final exam investigation"""
        print("🔍 DETAILED FINAL EXAM ACCESS INVESTIGATION")
        print("=" * 60)
        
        # 1. Authenticate
        print("\n1. AUTHENTICATION")
        print("-" * 30)
        self.student_token = self.authenticate_student()
        
        if not self.student_token:
            print("❌ Authentication failed - cannot proceed")
            return
        
        # 2. Get enrolled programs
        print("\n2. STUDENT ENROLLED PROGRAMS")
        print("-" * 30)
        enrolled_program_ids = self.get_student_enrolled_programs()
        
        if not enrolled_program_ids:
            print("❌ No enrolled programs found")
            return
        
        # 3. Test each enrolled program
        print("\n3. PROGRAM-BY-PROGRAM ANALYSIS")
        print("-" * 30)
        
        for program_id in enrolled_program_ids:
            print(f"\n🔍 Analyzing Program: {program_id}")
            print("-" * 40)
            
            # Check program access
            has_access = self.test_program_access_check(program_id)
            
            # Check completion status
            is_completed, completion_details = self.check_program_completion_status(program_id)
            
            # Test final test access
            final_tests = self.test_final_test_access_for_program(program_id)
            
            # If final tests exist and student has access, test attempt creation
            if final_tests and has_access:
                for test in final_tests[:1]:  # Test first available test
                    test_id = test.get('id')
                    program_response = requests.get(f"{BACKEND_URL}/programs/{program_id}", 
                                                  headers={"Authorization": f"Bearer {self.student_token}"})
                    program_title = program_response.json().get('title', 'Unknown') if program_response.status_code == 200 else 'Unknown'
                    
                    self.test_final_test_attempt_creation(test_id, program_title)
        
        # 4. Summary
        print("\n" + "=" * 60)
        print("📊 DETAILED INVESTIGATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Identify root cause
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        
        # Check for 422 errors
        error_422_tests = [r for r in self.test_results if not r['success'] and '422' in r['details']]
        if error_422_tests:
            print("❌ 422 ERRORS FOUND:")
            for test in error_422_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        # Check for missing final tests
        no_tests_found = [r for r in self.test_results if not r['success'] and 'No final tests found' in r['details']]
        if no_tests_found:
            print("❌ PROGRAMS WITH NO FINAL TESTS:")
            for test in no_tests_found:
                print(f"   • {test['test']}: {test['details']}")
        
        # Check for access issues
        access_issues = [r for r in self.test_results if not r['success'] and 'Access:' in r['details']]
        if access_issues:
            print("❌ PROGRAM ACCESS ISSUES:")
            for test in access_issues:
                print(f"   • {test['test']}: {test['details']}")
        
        if not error_422_tests and not no_tests_found and not access_issues:
            print("✅ No critical issues identified - final exam system appears to be working correctly")
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "error_422_count": len(error_422_tests),
            "no_tests_count": len(no_tests_found),
            "access_issues_count": len(access_issues)
        }

if __name__ == "__main__":
    tester = DetailedFinalExamTester()
    results = tester.run_detailed_investigation()
    
    # Exit with appropriate code
    sys.exit(0 if results["failed"] == 0 else 1)