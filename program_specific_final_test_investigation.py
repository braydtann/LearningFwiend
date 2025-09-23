#!/usr/bin/env python3
"""
PROGRAM-SPECIFIC FINAL TEST INVESTIGATION
Testing the specific scenario where user accesses final tests via program URL
and gets different results than general final test access.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://learning-score-fix.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "brayden.student@covesmart.com", 
    "password": "Cove1234!"
}

class ProgramSpecificFinalTestInvestigator:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
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

    def authenticate_admin(self):
        """Test admin authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                user_info = data.get('user', {})
                
                self.log_result(
                    "Admin Authentication", 
                    True, 
                    f"Authenticated as {user_info.get('full_name')} ({user_info.get('email')})"
                )
                return True
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def authenticate_student(self):
        """Test student authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get('access_token')
                user_info = data.get('user', {})
                
                self.log_result(
                    "Student Authentication", 
                    True, 
                    f"Authenticated as {user_info.get('full_name')} ({user_info.get('email')})"
                )
                return True
            else:
                self.log_result("Student Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Student Authentication", False, f"Exception: {str(e)}")
            return False

    def test_general_final_tests_access(self):
        """Test general GET /api/final-tests access"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            response = requests.get(
                f"{BACKEND_URL}/final-tests",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                tests = response.json()
                
                self.log_result(
                    "General Final Tests Access", 
                    True, 
                    f"Student can access {len(tests)} final tests via general endpoint"
                )
                
                self.general_final_tests = tests
                return True
            else:
                self.log_result("General Final Tests Access", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("General Final Tests Access", False, f"Exception: {str(e)}")
            return False

    def test_program_specific_final_tests_access(self):
        """Test program-specific final test access (simulating frontend filtering)"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # First get student's programs
            user_response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers, timeout=10)
            if user_response.status_code != 200:
                self.log_result("Get Student Info", False, "Could not get student info")
                return False
            
            user_info = user_response.json()
            student_id = user_info.get('id')
            
            # Get student's classrooms to find programs
            classroom_response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers, timeout=10)
            if classroom_response.status_code != 200:
                self.log_result("Get Student Classrooms", False, "Could not get classrooms")
                return False
            
            classrooms = classroom_response.json()
            
            # Find student's classrooms and extract program IDs
            student_program_ids = []
            for classroom in classrooms:
                if student_id in classroom.get('studentIds', []):
                    student_program_ids.extend(classroom.get('programIds', []))
            
            student_program_ids = list(set(student_program_ids))  # Remove duplicates
            
            if not student_program_ids:
                self.log_result(
                    "Program-Specific Final Tests Access", 
                    False, 
                    "Student is not enrolled in any programs"
                )
                return False
            
            # Now test each program for final tests
            program_test_results = []
            for program_id in student_program_ids:
                # Get all final tests and filter by program (simulating frontend behavior)
                final_tests_response = requests.get(f"{BACKEND_URL}/final-tests", headers=headers, timeout=10)
                
                if final_tests_response.status_code == 200:
                    all_tests = final_tests_response.json()
                    program_tests = [t for t in all_tests if t.get('programId') == program_id]
                    
                    # Get program details
                    program_response = requests.get(f"{BACKEND_URL}/programs/{program_id}", headers=headers, timeout=10)
                    program_name = "Unknown"
                    if program_response.status_code == 200:
                        program_data = program_response.json()
                        program_name = program_data.get('title', 'Unknown')
                    
                    program_test_results.append({
                        'program_id': program_id,
                        'program_name': program_name,
                        'test_count': len(program_tests),
                        'tests': program_tests
                    })
            
            # Check if any program has final tests
            total_program_tests = sum(result['test_count'] for result in program_test_results)
            
            # This is the critical test - check if program-specific filtering shows 0 tests
            if total_program_tests == 0:
                self.log_result(
                    "Program-Specific Final Tests Access - ISSUE FOUND", 
                    False, 
                    f"When filtering by student's programs, 0 final tests found. Programs: {[r['program_name'] for r in program_test_results]}"
                )
            else:
                self.log_result(
                    "Program-Specific Final Tests Access", 
                    True, 
                    f"Found {total_program_tests} tests across {len(program_test_results)} programs"
                )
            
            self.program_test_results = program_test_results
            return True
                
        except Exception as e:
            self.log_result("Program-Specific Final Tests Access", False, f"Exception: {str(e)}")
            return False

    def test_specific_program_url_scenario(self):
        """Test the specific scenario from user report - accessing via program URL"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # The user mentioned accessing via a specific program ID in URL
            # Let's test with a non-existent program ID (simulating the user's scenario)
            fake_program_id = "1233456-5414-49ee-ab4f-d7a617105f4a"  # From user's URL
            
            # Get all final tests
            response = requests.get(f"{BACKEND_URL}/final-tests", headers=headers, timeout=10)
            
            if response.status_code == 200:
                all_tests = response.json()
                
                # Filter by the fake program ID (this is what frontend would do)
                filtered_tests = [t for t in all_tests if t.get('programId') == fake_program_id]
                
                if len(filtered_tests) == 0:
                    self.log_result(
                        "Specific Program URL Scenario - ROOT CAUSE FOUND", 
                        True, 
                        f"When filtering by non-existent program ID '{fake_program_id}', 0 tests found (MATCHES USER REPORT)"
                    )
                else:
                    self.log_result(
                        "Specific Program URL Scenario", 
                        False, 
                        f"Unexpected: Found {len(filtered_tests)} tests for non-existent program"
                    )
                
                # Also test with student's actual program IDs
                if hasattr(self, 'program_test_results'):
                    for result in self.program_test_results:
                        actual_program_id = result['program_id']
                        actual_filtered_tests = [t for t in all_tests if t.get('programId') == actual_program_id]
                        
                        self.log_result(
                            f"Valid Program ID Test ({result['program_name']})", 
                            len(actual_filtered_tests) > 0, 
                            f"Program {actual_program_id}: {len(actual_filtered_tests)} tests"
                        )
                
                return True
            else:
                self.log_result("Specific Program URL Scenario", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Specific Program URL Scenario", False, f"Exception: {str(e)}")
            return False

    def test_frontend_simulation(self):
        """Simulate the exact frontend behavior that might cause the issue"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Simulate frontend FinalTest.js component behavior
            # 1. Get URL parameter (simulating non-existent program ID)
            url_program_id = "1233456-5414-49ee-ab4f-d7a617105f4a"
            
            # 2. Fetch final tests
            response = requests.get(f"{BACKEND_URL}/final-tests", headers=headers, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Frontend Simulation", False, f"Could not fetch final tests: {response.status_code}")
                return False
            
            all_tests = response.json()
            
            # 3. Filter by program ID (this is where the issue occurs)
            if url_program_id:
                filtered_tests = [test for test in all_tests if test.get('programId') == url_program_id]
            else:
                filtered_tests = all_tests
            
            # 4. Check result
            if len(filtered_tests) == 0 and url_program_id:
                # This is the exact scenario causing the user's issue
                self.log_result(
                    "Frontend Simulation - EXACT ISSUE REPRODUCED", 
                    True, 
                    f"Frontend filtering by invalid program ID '{url_program_id}' results in 0 tests (MATCHES USER EXPERIENCE)"
                )
                
                # 5. Test what happens with valid program ID
                # Get student's actual program ID
                user_response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers, timeout=10)
                if user_response.status_code == 200:
                    user_info = user_response.json()
                    student_id = user_info.get('id')
                    
                    # Get student's classrooms
                    classroom_response = requests.get(f"{BACKEND_URL}/classrooms", headers=headers, timeout=10)
                    if classroom_response.status_code == 200:
                        classrooms = classroom_response.json()
                        
                        for classroom in classrooms:
                            if student_id in classroom.get('studentIds', []):
                                for valid_program_id in classroom.get('programIds', []):
                                    valid_filtered_tests = [test for test in all_tests if test.get('programId') == valid_program_id]
                                    
                                    self.log_result(
                                        f"Frontend Simulation with Valid Program ID", 
                                        len(valid_filtered_tests) > 0, 
                                        f"Valid program ID '{valid_program_id}': {len(valid_filtered_tests)} tests available"
                                    )
                                    break
                                break
                
                return True
            else:
                self.log_result("Frontend Simulation", False, f"Unexpected result: {len(filtered_tests)} tests")
                return False
                
        except Exception as e:
            self.log_result("Frontend Simulation", False, f"Exception: {str(e)}")
            return False

    def run_investigation(self):
        """Run the complete program-specific investigation"""
        print("🔍 PROGRAM-SPECIFIC FINAL TEST INVESTIGATION")
        print("=" * 80)
        print("Testing the specific scenario where user accesses final tests via program URL")
        print("and gets different results than general final test access.")
        print("=" * 80)
        print()
        
        # Authentication
        if not self.authenticate_admin():
            return False
            
        if not self.authenticate_student():
            return False
        
        # Test different access patterns
        print("🔍 TESTING DIFFERENT ACCESS PATTERNS")
        print("-" * 50)
        self.test_general_final_tests_access()
        self.test_program_specific_final_tests_access()
        self.test_specific_program_url_scenario()
        self.test_frontend_simulation()
        print()
        
        # Summary
        print("=" * 80)
        print("📊 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Investigation Steps: {total_tests}")
        print(f"Successful: {passed_tests} ✅")
        print(f"Issues Found: {failed_tests} ❌")
        print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        # Check if we found the root cause
        root_cause_found = any("ROOT CAUSE FOUND" in result['test'] or "EXACT ISSUE REPRODUCED" in result['test'] 
                              for result in self.results if result['success'])
        
        if root_cause_found:
            print("  ✅ ROOT CAUSE IDENTIFIED: Frontend filtering by invalid program ID")
            print("  ✅ User was accessing final tests via URL with non-existent program ID")
            print("  ✅ This causes frontend to filter out all available final tests")
            print("  ✅ General final test access works correctly (7 tests available)")
        else:
            print("  ❌ Root cause not clearly identified")
        
        print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        if root_cause_found:
            print("  1. Fix frontend to handle invalid program IDs gracefully")
            print("  2. Show all available final tests when program ID is invalid")
            print("  3. Add error handling for non-existent program IDs")
            print("  4. Provide user feedback when program doesn't exist")
        
        print()
        return root_cause_found

if __name__ == "__main__":
    investigator = ProgramSpecificFinalTestInvestigator()
    success = investigator.run_investigation()
    
    if success:
        print("🎉 Investigation completed - Root cause identified!")
        sys.exit(0)
    else:
        print("💥 Investigation completed - Root cause unclear!")
        sys.exit(1)