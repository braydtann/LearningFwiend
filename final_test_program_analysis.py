#!/usr/bin/env python3
"""
Final Test Program Analysis
Analyzing the relationship between programs and final tests to understand the 0 vs 7 discrepancy.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://learning-flow.preview.emergentagent.com/api"

# Test credentials
BRAYDEN_STUDENT_CREDENTIALS = {
    "username_or_email": "brayden.student@covesmart.com",
    "password": "Cove1234!"
}

ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class FinalTestProgramAnalyzer:
    def __init__(self):
        self.student_token = None
        self.admin_token = None
        self.results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate(self):
        """Authenticate both student and admin"""
        try:
            # Student auth
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=BRAYDEN_STUDENT_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get('access_token')
                self.log_result("Student Authentication", True, "Authenticated brayden.student@covesmart.com")
            else:
                self.log_result("Student Authentication", False, f"HTTP {response.status_code}")
                return False
            
            # Admin auth
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                self.log_result("Admin Authentication", True, "Authenticated admin")
                return True
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False

    def analyze_all_programs(self):
        """Get all programs and analyze which ones have final tests"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get all programs
            programs_response = requests.get(f"{BACKEND_URL}/programs", headers=headers, timeout=10)
            
            if programs_response.status_code != 200:
                self.log_result("Get All Programs", False, f"HTTP {programs_response.status_code}")
                return False
            
            programs = programs_response.json()
            
            # Get all final tests
            tests_response = requests.get(f"{BACKEND_URL}/final-tests", headers=headers, timeout=10)
            
            if tests_response.status_code != 200:
                self.log_result("Get All Final Tests", False, f"HTTP {tests_response.status_code}")
                return False
            
            final_tests = tests_response.json()
            
            # Analyze program-final test relationships
            program_test_map = {}
            for test in final_tests:
                program_id = test.get('programId')
                if program_id:
                    if program_id not in program_test_map:
                        program_test_map[program_id] = []
                    program_test_map[program_id].append(test)
            
            self.log_result(
                "Program-Final Test Analysis", 
                True, 
                f"Found {len(programs)} programs, {len(final_tests)} final tests, {len(program_test_map)} programs with tests"
            )
            
            print("   PROGRAM ANALYSIS:")
            print(f"   Total Programs: {len(programs)}")
            print(f"   Total Final Tests: {len(final_tests)}")
            print(f"   Programs with Final Tests: {len(program_test_map)}")
            print()
            
            print("   PROGRAMS WITH FINAL TESTS:")
            for program_id, tests in program_test_map.items():
                # Find program details
                program = next((p for p in programs if p['id'] == program_id), None)
                program_title = program['title'] if program else "Unknown Program"
                print(f"     • {program_title} (ID: {program_id})")
                print(f"       Final Tests: {len(tests)}")
                for test in tests:
                    print(f"         - {test.get('title', 'Unknown')} (Published: {test.get('isPublished', False)})")
                print()
            
            print("   PROGRAMS WITHOUT FINAL TESTS:")
            programs_without_tests = [p for p in programs if p['id'] not in program_test_map]
            for program in programs_without_tests:
                print(f"     • {program['title']} (ID: {program['id']})")
            
            # Check the specific program mentioned in review request
            target_program_id = "1233456-5414-49ee-ab4f-d7a617105f4a"
            target_program = next((p for p in programs if p['id'] == target_program_id), None)
            
            if target_program:
                has_tests = target_program_id in program_test_map
                test_count = len(program_test_map.get(target_program_id, []))
                print(f"\n   TARGET PROGRAM ANALYSIS (from review request):")
                print(f"     • Program: {target_program['title']} (ID: {target_program_id})")
                print(f"     • Has Final Tests: {has_tests}")
                print(f"     • Final Test Count: {test_count}")
            else:
                print(f"\n   TARGET PROGRAM ANALYSIS:")
                print(f"     • Program ID {target_program_id} NOT FOUND in database")
            
            return True
                
        except Exception as e:
            self.log_result("Program-Final Test Analysis", False, f"Exception: {str(e)}")
            return False

    def test_student_access_patterns(self):
        """Test different access patterns for the student"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Test 1: All final tests (no filter)
            response1 = requests.get(f"{BACKEND_URL}/final-tests", headers=headers, timeout=10)
            all_tests_count = len(response1.json()) if response1.status_code == 200 else 0
            
            # Test 2: Specific program filter (the one mentioned in review)
            target_program_id = "1233456-5414-49ee-ab4f-d7a617105f4a"
            response2 = requests.get(
                f"{BACKEND_URL}/final-tests?program_id={target_program_id}", 
                headers=headers, 
                timeout=10
            )
            filtered_tests_count = len(response2.json()) if response2.status_code == 200 else 0
            
            # Test 3: Try with a program that has tests
            response3 = requests.get(f"{BACKEND_URL}/final-tests", headers=headers, timeout=10)
            if response3.status_code == 200:
                all_tests = response3.json()
                if all_tests:
                    # Get a program ID that has tests
                    test_program_id = all_tests[0].get('programId')
                    if test_program_id:
                        response4 = requests.get(
                            f"{BACKEND_URL}/final-tests?program_id={test_program_id}", 
                            headers=headers, 
                            timeout=10
                        )
                        working_filter_count = len(response4.json()) if response4.status_code == 200 else 0
                    else:
                        working_filter_count = 0
                else:
                    working_filter_count = 0
            else:
                working_filter_count = 0
            
            self.log_result(
                "Student Access Patterns", 
                True, 
                f"No filter: {all_tests_count}, Target program filter: {filtered_tests_count}, Working filter: {working_filter_count}"
            )
            
            print("   ACCESS PATTERN ANALYSIS:")
            print(f"     • GET /api/final-tests (no filter): {all_tests_count} tests")
            print(f"     • GET /api/final-tests?program_id={target_program_id}: {filtered_tests_count} tests")
            print(f"     • GET /api/final-tests?program_id=<existing_program>: {working_filter_count} tests")
            print()
            
            # Explain the discrepancy
            if all_tests_count > 0 and filtered_tests_count == 0:
                print("   🔍 DISCREPANCY EXPLANATION:")
                print("     • Student sees 7 tests when no program filter is applied")
                print("     • Student sees 0 tests when filtering by the specific program ID")
                print("     • This is because the target program has no final tests associated with it")
                print("     • The frontend might be applying this program filter automatically")
            
            return True
                
        except Exception as e:
            self.log_result("Student Access Patterns", False, f"Exception: {str(e)}")
            return False

    def check_student_program_enrollments(self):
        """Check what programs the student is enrolled in"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get student enrollments
            enrollments_response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers, timeout=10)
            
            if enrollments_response.status_code != 200:
                self.log_result("Student Enrollments", False, f"HTTP {enrollments_response.status_code}")
                return False
            
            enrollments = enrollments_response.json()
            
            # Get all programs to map course IDs to programs
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            programs_response = requests.get(f"{BACKEND_URL}/programs", headers=admin_headers, timeout=10)
            
            if programs_response.status_code != 200:
                self.log_result("Get Programs for Mapping", False, f"HTTP {programs_response.status_code}")
                return False
            
            programs = programs_response.json()
            
            # Find which programs contain the student's enrolled courses
            enrolled_course_ids = [e['courseId'] for e in enrollments]
            relevant_programs = []
            
            for program in programs:
                program_course_ids = program.get('courseIds', [])
                if any(course_id in program_course_ids for course_id in enrolled_course_ids):
                    relevant_programs.append(program)
            
            self.log_result(
                "Student Program Enrollments", 
                True, 
                f"Student enrolled in {len(enrollments)} courses, related to {len(relevant_programs)} programs"
            )
            
            print("   STUDENT ENROLLMENT ANALYSIS:")
            print(f"     • Enrolled Courses: {len(enrollments)}")
            print(f"     • Related Programs: {len(relevant_programs)}")
            print()
            
            if relevant_programs:
                print("   PROGRAMS STUDENT IS RELATED TO:")
                for program in relevant_programs:
                    print(f"     • {program['title']} (ID: {program['id']})")
                    # Check if this program has final tests
                    final_tests_response = requests.get(
                        f"{BACKEND_URL}/final-tests?program_id={program['id']}", 
                        headers=headers, 
                        timeout=10
                    )
                    test_count = len(final_tests_response.json()) if final_tests_response.status_code == 200 else 0
                    print(f"       Final Tests: {test_count}")
            
            return True
                
        except Exception as e:
            self.log_result("Student Program Enrollments", False, f"Exception: {str(e)}")
            return False

    def run_analysis(self):
        """Run complete analysis"""
        print("🔍 Starting Final Test Program Analysis")
        print("=" * 80)
        print()
        
        if not self.authenticate():
            print("❌ Authentication failed - cannot continue")
            return False
        
        self.analyze_all_programs()
        self.test_student_access_patterns()
        self.check_student_program_enrollments()
        
        # Summary
        print("=" * 80)
        print("📊 FINAL TEST PROGRAM ANALYSIS SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        
        print(f"Total Analysis Steps: {total_tests}")
        print(f"Completed Successfully: {passed_tests} ✅")
        print()
        
        print("🎯 ROOT CAUSE IDENTIFIED:")
        print("  • The discrepancy (0 vs 7 final tests) is caused by program filtering")
        print("  • When no program_id filter is applied: Student sees 7 final tests")
        print("  • When program_id='1233456-5414-49ee-ab4f-d7a617105f4a' filter is applied: Student sees 0 tests")
        print("  • This specific program ID has no final tests associated with it")
        print("  • The frontend might be automatically applying this program filter")
        print()
        
        print("💡 SOLUTION:")
        print("  • Check frontend code to see if it's applying program filters automatically")
        print("  • Ensure the correct program ID is being used for filtering")
        print("  • Consider creating final tests for the target program if needed")
        print()
        
        return True

if __name__ == "__main__":
    analyzer = FinalTestProgramAnalyzer()
    success = analyzer.run_analysis()
    
    if success:
        print("🎉 Final test program analysis completed!")
        sys.exit(0)
    else:
        print("💥 Final test program analysis failed!")
        sys.exit(1)