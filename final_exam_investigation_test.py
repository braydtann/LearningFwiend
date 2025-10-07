#!/usr/bin/env python3
"""
Final Exam Investigation Test
Testing the specific issue: "No final test available for this program" and 422 error
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://quiz-progress-fix.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class FinalExamTester:
    def __init__(self):
        self.admin_token = None
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
    
    def authenticate_user(self, credentials, user_type):
        """Authenticate user and return token"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=credentials)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                self.log_result(f"{user_type} Authentication", True, 
                              f"User: {user_info.get('full_name', 'Unknown')} ({user_info.get('role', 'Unknown')})")
                return token
            else:
                self.log_result(f"{user_type} Authentication", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_result(f"{user_type} Authentication", False, f"Exception: {str(e)}")
            return None
    
    def test_final_tests_endpoint(self, token, user_type, program_id=None):
        """Test GET /api/final-tests endpoint"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {}
            if program_id:
                params["program_id"] = program_id
            
            response = requests.get(f"{BACKEND_URL}/final-tests", headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                test_count = len(data)
                
                if program_id:
                    # Filter tests for specific program
                    program_tests = [test for test in data if test.get('programId') == program_id]
                    program_test_count = len(program_tests)
                    
                    self.log_result(f"{user_type} Final Tests for Program {program_id}", True,
                                  f"Total tests: {test_count}, Program-specific tests: {program_test_count}")
                    
                    if program_test_count == 0:
                        self.log_result(f"{user_type} Program Final Test Availability", False,
                                      f"No final tests found for program {program_id}")
                    
                    return program_tests
                else:
                    self.log_result(f"{user_type} All Final Tests", True, f"Found {test_count} final tests")
                    return data
            else:
                self.log_result(f"{user_type} Final Tests API", False,
                              f"Status: {response.status_code}, Response: {response.text}")
                return []
                
        except Exception as e:
            self.log_result(f"{user_type} Final Tests API", False, f"Exception: {str(e)}")
            return []
    
    def test_programs_endpoint(self, token, user_type):
        """Test GET /api/programs endpoint to find available programs"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BACKEND_URL}/programs", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                program_count = len(data)
                self.log_result(f"{user_type} Programs List", True, f"Found {program_count} programs")
                
                # Show first few programs for reference
                if data:
                    for i, program in enumerate(data[:3]):
                        print(f"   Program {i+1}: {program.get('title', 'Unknown')} (ID: {program.get('id', 'Unknown')})")
                
                return data
            else:
                self.log_result(f"{user_type} Programs API", False,
                              f"Status: {response.status_code}, Response: {response.text}")
                return []
                
        except Exception as e:
            self.log_result(f"{user_type} Programs API", False, f"Exception: {str(e)}")
            return []
    
    def test_student_enrollments(self, token):
        """Test student enrollments to check program completion status"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                enrollment_count = len(data)
                self.log_result("Student Enrollments", True, f"Found {enrollment_count} enrollments")
                
                # Check completion status
                completed_enrollments = [e for e in data if e.get('status') == 'completed' or e.get('progress', 0) >= 100]
                self.log_result("Student Completed Courses", True, 
                              f"Completed: {len(completed_enrollments)}/{enrollment_count}")
                
                return data
            else:
                self.log_result("Student Enrollments", False,
                              f"Status: {response.status_code}, Response: {response.text}")
                return []
                
        except Exception as e:
            self.log_result("Student Enrollments", False, f"Exception: {str(e)}")
            return []
    
    def test_classrooms_for_programs(self, token, user_type):
        """Test classrooms to understand program assignments"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                classroom_count = len(data)
                self.log_result(f"{user_type} Classrooms", True, f"Found {classroom_count} classrooms")
                
                # Check for program assignments
                classrooms_with_programs = [c for c in data if c.get('programIds')]
                self.log_result(f"{user_type} Classrooms with Programs", True,
                              f"Classrooms with programs: {len(classrooms_with_programs)}")
                
                return data
            else:
                self.log_result(f"{user_type} Classrooms", False,
                              f"Status: {response.status_code}, Response: {response.text}")
                return []
                
        except Exception as e:
            self.log_result(f"{user_type} Classrooms", False, f"Exception: {str(e)}")
            return []
    
    def test_program_completion_logic(self, student_token, programs):
        """Test program completion logic for determining final exam access"""
        if not programs:
            self.log_result("Program Completion Logic", False, "No programs available to test")
            return
        
        # Test with first available program
        test_program = programs[0]
        program_id = test_program.get('id')
        program_title = test_program.get('title', 'Unknown')
        
        try:
            headers = {"Authorization": f"Bearer {student_token}"}
            
            # Check program access
            response = requests.get(f"{BACKEND_URL}/programs/{program_id}/access-check", headers=headers)
            
            if response.status_code == 200:
                access_data = response.json()
                has_access = access_data.get('hasAccess', False)
                reason = access_data.get('reason', 'Unknown')
                
                self.log_result(f"Program Access Check ({program_title})", True,
                              f"Access: {has_access}, Reason: {reason}")
                
                # If student has access, check for final tests
                if has_access:
                    final_tests = self.test_final_tests_endpoint(student_token, "Student", program_id)
                    if not final_tests:
                        self.log_result("Final Test Availability Issue", False,
                                      f"Student has program access but no final tests available for program {program_id}")
                
            else:
                self.log_result(f"Program Access Check ({program_title})", False,
                              f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Program Completion Logic", False, f"Exception: {str(e)}")
    
    def investigate_422_error(self, student_token):
        """Investigate potential 422 error scenarios"""
        try:
            headers = {"Authorization": f"Bearer {student_token}"}
            
            # Test various endpoints that might cause 422 errors
            test_endpoints = [
                ("/final-tests", "GET", {}),
                ("/enrollments", "GET", {}),
                ("/programs", "GET", {}),
            ]
            
            for endpoint, method, params in test_endpoints:
                try:
                    if method == "GET":
                        response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, params=params)
                    
                    if response.status_code == 422:
                        self.log_result(f"422 Error Investigation - {endpoint}", False,
                                      f"422 error found: {response.text}")
                    elif response.status_code == 200:
                        self.log_result(f"422 Error Investigation - {endpoint}", True,
                                      f"No 422 error, status: {response.status_code}")
                    else:
                        self.log_result(f"422 Error Investigation - {endpoint}", True,
                                      f"Different status: {response.status_code}")
                        
                except Exception as e:
                    self.log_result(f"422 Error Investigation - {endpoint}", False, f"Exception: {str(e)}")
                    
        except Exception as e:
            self.log_result("422 Error Investigation", False, f"Exception: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run comprehensive final exam investigation"""
        print("🔍 FINAL EXAM AVAILABILITY INVESTIGATION")
        print("=" * 60)
        
        # 1. Authenticate users
        print("\n1. AUTHENTICATION TESTING")
        print("-" * 30)
        self.admin_token = self.authenticate_user(ADMIN_CREDENTIALS, "Admin")
        self.student_token = self.authenticate_user(STUDENT_CREDENTIALS, "Student")
        
        if not self.admin_token or not self.student_token:
            print("❌ Authentication failed - cannot proceed with testing")
            return
        
        # 2. Test final tests endpoints
        print("\n2. FINAL TESTS ENDPOINT TESTING")
        print("-" * 30)
        admin_final_tests = self.test_final_tests_endpoint(self.admin_token, "Admin")
        student_final_tests = self.test_final_tests_endpoint(self.student_token, "Student")
        
        # 3. Test programs
        print("\n3. PROGRAMS TESTING")
        print("-" * 30)
        admin_programs = self.test_programs_endpoint(self.admin_token, "Admin")
        student_programs = self.test_programs_endpoint(self.student_token, "Student")
        
        # 4. Test student enrollments and completion
        print("\n4. STUDENT ENROLLMENT & COMPLETION TESTING")
        print("-" * 30)
        student_enrollments = self.test_student_enrollments(self.student_token)
        
        # 5. Test classrooms for program assignments
        print("\n5. CLASSROOM PROGRAM ASSIGNMENTS")
        print("-" * 30)
        admin_classrooms = self.test_classrooms_for_programs(self.admin_token, "Admin")
        
        # 6. Test program completion logic
        print("\n6. PROGRAM COMPLETION LOGIC TESTING")
        print("-" * 30)
        self.test_program_completion_logic(self.student_token, student_programs)
        
        # 7. Investigate 422 errors
        print("\n7. 422 ERROR INVESTIGATION")
        print("-" * 30)
        self.investigate_422_error(self.student_token)
        
        # 8. Test specific program filtering
        print("\n8. PROGRAM-SPECIFIC FINAL TEST FILTERING")
        print("-" * 30)
        if student_programs:
            for program in student_programs[:2]:  # Test first 2 programs
                program_id = program.get('id')
                program_title = program.get('title', 'Unknown')
                print(f"\nTesting program: {program_title} (ID: {program_id})")
                
                admin_program_tests = self.test_final_tests_endpoint(self.admin_token, "Admin", program_id)
                student_program_tests = self.test_final_tests_endpoint(self.student_token, "Student", program_id)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 INVESTIGATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print("\n🔍 KEY FINDINGS:")
        critical_failures = [r for r in self.test_results if not r['success'] and 
                           ('Final Test' in r['test'] or '422' in r['test'] or 'Program' in r['test'])]
        
        if critical_failures:
            print("❌ CRITICAL ISSUES IDENTIFIED:")
            for failure in critical_failures:
                print(f"   • {failure['test']}: {failure['details']}")
        else:
            print("✅ No critical issues found in final exam functionality")
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "critical_failures": critical_failures,
            "all_results": self.test_results
        }

if __name__ == "__main__":
    tester = FinalExamTester()
    results = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if results["failed"] == 0 else 1)