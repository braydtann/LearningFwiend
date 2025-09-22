#!/usr/bin/env python3
"""
URGENT DISCREPANCY INVESTIGATION: Final Test Access Issue
Testing the specific issue where brayden.student@covesmart.com sees 0 final tests 
while previous testing found 7 final tests available.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use the correct backend URL from frontend/.env
BACKEND_URL = "https://lms-bug-fixes.preview.emergentagent.com/api"

# Test credentials from the review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "brayden.student@covesmart.com", 
    "password": "Cove1234!"
}

class FinalTestDiscrepancyInvestigator:
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
                
                if user_info.get('role') == 'admin':
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Authenticated as {user_info.get('full_name')} ({user_info.get('email')})"
                    )
                    return True
                else:
                    self.log_result("Admin Authentication", False, f"User role is {user_info.get('role')}, expected admin")
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def authenticate_student(self):
        """Test student authentication with EXACT credentials from review request"""
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
                
                if user_info.get('role') == 'learner':
                    self.log_result(
                        "Student Authentication (brayden.student@covesmart.com)", 
                        True, 
                        f"Authenticated as {user_info.get('full_name')} ({user_info.get('email')})"
                    )
                    return True
                else:
                    self.log_result("Student Authentication", False, f"User role is {user_info.get('role')}, expected learner")
                    return False
            else:
                self.log_result("Student Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Student Authentication", False, f"Exception: {str(e)}")
            return False

    def check_admin_final_tests_view(self):
        """Check GET /api/final-tests from admin perspective"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(
                f"{BACKEND_URL}/final-tests",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                tests = response.json()
                
                # Analyze final tests from admin perspective
                total_tests = len(tests)
                published_tests = [t for t in tests if t.get('isPublished', False)]
                unpublished_tests = [t for t in tests if not t.get('isPublished', False)]
                
                # Check program associations
                tests_with_programs = [t for t in tests if t.get('programId')]
                tests_without_programs = [t for t in tests if not t.get('programId')]
                
                self.log_result(
                    "Admin Final Tests View", 
                    True, 
                    f"Total: {total_tests}, Published: {len(published_tests)}, Unpublished: {len(unpublished_tests)}, With Programs: {len(tests_with_programs)}, Without Programs: {len(tests_without_programs)}"
                )
                
                # Store for comparison
                self.admin_final_tests = tests
                return True
            else:
                self.log_result("Admin Final Tests View", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Final Tests View", False, f"Exception: {str(e)}")
            return False

    def check_student_final_tests_view(self):
        """Check GET /api/final-tests from student perspective"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            response = requests.get(
                f"{BACKEND_URL}/final-tests",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                tests = response.json()
                
                total_tests = len(tests)
                
                # This is the critical test - student should see some final tests
                if total_tests == 0:
                    self.log_result(
                        "Student Final Tests View - CRITICAL ISSUE CONFIRMED", 
                        False, 
                        f"Student sees {total_tests} final tests (MATCHES USER REPORT OF 0 TESTS)"
                    )
                else:
                    self.log_result(
                        "Student Final Tests View", 
                        True, 
                        f"Student sees {total_tests} final tests"
                    )
                
                # Store for comparison
                self.student_final_tests = tests
                return True
            else:
                self.log_result("Student Final Tests View", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Student Final Tests View", False, f"Exception: {str(e)}")
            return False

    def check_student_program_enrollments(self):
        """Check if student is enrolled in programs and which programs"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Check student enrollments
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                
                # Check classrooms (which contain programs)
                classroom_response = requests.get(
                    f"{BACKEND_URL}/classrooms",
                    headers=headers,
                    timeout=10
                )
                
                classrooms = []
                if classroom_response.status_code == 200:
                    classrooms = classroom_response.json()
                
                # Find classrooms where student is enrolled
                student_classrooms = []
                for classroom in classrooms:
                    # Check if student is in this classroom
                    student_ids = classroom.get('studentIds', [])
                    # Get current user ID from token (we'll need to get this from user info)
                    user_response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers, timeout=10)
                    if user_response.status_code == 200:
                        user_info = user_response.json()
                        student_id = user_info.get('id')
                        if student_id in student_ids:
                            student_classrooms.append(classroom)
                
                # Extract program IDs from student's classrooms
                program_ids = []
                for classroom in student_classrooms:
                    program_ids.extend(classroom.get('programIds', []))
                
                program_ids = list(set(program_ids))  # Remove duplicates
                
                self.log_result(
                    "Student Program Enrollments", 
                    True, 
                    f"Course enrollments: {len(enrollments)}, Student classrooms: {len(student_classrooms)}, Program IDs: {program_ids}"
                )
                
                # Store for analysis
                self.student_program_ids = program_ids
                self.student_enrollments = enrollments
                self.student_classrooms = student_classrooms
                return True
            else:
                self.log_result("Student Program Enrollments", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Student Program Enrollments", False, f"Exception: {str(e)}")
            return False

    def check_program_test3_existence(self):
        """Check if program 'test3' exists and its details"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(
                f"{BACKEND_URL}/programs",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                programs = response.json()
                
                # Look for program named 'test3' or similar
                test3_programs = [p for p in programs if 'test3' in p.get('title', '').lower()]
                
                if test3_programs:
                    program = test3_programs[0]  # Take first match
                    program_id = program.get('id')
                    
                    # Check if any final tests are associated with this program
                    associated_tests = []
                    if hasattr(self, 'admin_final_tests'):
                        associated_tests = [t for t in self.admin_final_tests if t.get('programId') == program_id]
                    
                    self.log_result(
                        "Program 'test3' Existence", 
                        True, 
                        f"Found program: {program.get('title')} (ID: {program_id}), Associated final tests: {len(associated_tests)}"
                    )
                    
                    self.test3_program = program
                    return True
                else:
                    self.log_result(
                        "Program 'test3' Existence", 
                        False, 
                        f"No program with 'test3' in title found among {len(programs)} programs"
                    )
                    return False
            else:
                self.log_result("Program 'test3' Existence", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Program 'test3' Existence", False, f"Exception: {str(e)}")
            return False

    def analyze_final_test_permissions(self):
        """Analyze why student can't see final tests that admin can see"""
        try:
            if not hasattr(self, 'admin_final_tests') or not hasattr(self, 'student_final_tests'):
                self.log_result("Final Test Permissions Analysis", False, "Missing admin or student final test data")
                return False
            
            admin_count = len(self.admin_final_tests)
            student_count = len(self.student_final_tests)
            
            # Detailed analysis
            analysis_details = []
            
            if admin_count > 0 and student_count == 0:
                analysis_details.append("CRITICAL: Admin sees tests but student sees none")
                
                # Check each admin test for why student can't see it
                for test in self.admin_final_tests:
                    test_id = test.get('id')
                    test_title = test.get('title', 'Unknown')
                    is_published = test.get('isPublished', False)
                    program_id = test.get('programId')
                    
                    reasons = []
                    if not is_published:
                        reasons.append("NOT_PUBLISHED")
                    
                    if program_id:
                        if hasattr(self, 'student_program_ids') and program_id not in self.student_program_ids:
                            reasons.append("NOT_ENROLLED_IN_PROGRAM")
                    else:
                        reasons.append("NO_PROGRAM_ASSOCIATION")
                    
                    analysis_details.append(f"Test '{test_title}': {', '.join(reasons) if reasons else 'SHOULD_BE_VISIBLE'}")
            
            elif admin_count == student_count:
                analysis_details.append("Admin and student see same number of tests")
            else:
                analysis_details.append(f"Admin sees {admin_count}, student sees {student_count}")
            
            self.log_result(
                "Final Test Permissions Analysis", 
                True, 
                "; ".join(analysis_details)
            )
            return True
                
        except Exception as e:
            self.log_result("Final Test Permissions Analysis", False, f"Exception: {str(e)}")
            return False

    def check_role_based_restrictions(self):
        """Check if there are role-based restrictions affecting this student"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Get current user info to check role and permissions
            response = requests.get(
                f"{BACKEND_URL}/auth/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_info = response.json()
                
                role = user_info.get('role')
                is_active = user_info.get('is_active', True)
                department = user_info.get('department')
                
                # Check if user account has any restrictions
                restrictions = []
                if not is_active:
                    restrictions.append("ACCOUNT_INACTIVE")
                if role != 'learner':
                    restrictions.append(f"UNEXPECTED_ROLE_{role}")
                
                self.log_result(
                    "Role-based Restrictions Check", 
                    len(restrictions) == 0, 
                    f"Role: {role}, Active: {is_active}, Department: {department}, Restrictions: {restrictions if restrictions else 'NONE'}"
                )
                return len(restrictions) == 0
            else:
                self.log_result("Role-based Restrictions Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Role-based Restrictions Check", False, f"Exception: {str(e)}")
            return False

    def investigate_discrepancy_root_cause(self):
        """Investigate the root cause of the discrepancy"""
        try:
            # Compare what admin sees vs what student sees
            admin_tests = getattr(self, 'admin_final_tests', [])
            student_tests = getattr(self, 'student_final_tests', [])
            
            root_causes = []
            
            # Check if it's a publication issue
            unpublished_tests = [t for t in admin_tests if not t.get('isPublished', False)]
            if len(unpublished_tests) == len(admin_tests):
                root_causes.append("ALL_TESTS_UNPUBLISHED")
            elif len(unpublished_tests) > 0:
                root_causes.append(f"{len(unpublished_tests)}_TESTS_UNPUBLISHED")
            
            # Check if it's a program association issue
            tests_without_programs = [t for t in admin_tests if not t.get('programId')]
            if len(tests_without_programs) > 0:
                root_causes.append(f"{len(tests_without_programs)}_TESTS_WITHOUT_PROGRAMS")
            
            # Check if student is not enrolled in any programs with final tests
            student_program_ids = getattr(self, 'student_program_ids', [])
            if len(student_program_ids) == 0:
                root_causes.append("STUDENT_NOT_ENROLLED_IN_ANY_PROGRAMS")
            else:
                # Check if any admin tests match student's programs
                matching_tests = [t for t in admin_tests if t.get('programId') in student_program_ids]
                if len(matching_tests) == 0:
                    root_causes.append("NO_TESTS_FOR_STUDENT_PROGRAMS")
            
            # Check if it's a permissions/access issue
            if len(admin_tests) > 0 and len(student_tests) == 0 and not root_causes:
                root_causes.append("UNKNOWN_PERMISSIONS_ISSUE")
            
            self.log_result(
                "Root Cause Investigation", 
                True, 
                f"Identified causes: {root_causes if root_causes else ['NO_CLEAR_CAUSE_FOUND']}"
            )
            
            self.root_causes = root_causes
            return True
                
        except Exception as e:
            self.log_result("Root Cause Investigation", False, f"Exception: {str(e)}")
            return False

    def run_investigation(self):
        """Run the complete discrepancy investigation"""
        print("🚨 URGENT DISCREPANCY INVESTIGATION: Final Test Access Issue")
        print("=" * 80)
        print("Investigating why brayden.student@covesmart.com sees 0 final tests")
        print("while previous testing found 7 final tests available.")
        print("=" * 80)
        print()
        
        # Step 1: Authentication
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot continue investigation")
            return False
            
        if not self.authenticate_student():
            print("❌ Student authentication failed - cannot continue investigation")
            return False
        
        # Step 2: Compare admin vs student views
        print("🔍 STEP 1: Comparing Admin vs Student Final Test Views")
        print("-" * 50)
        self.check_admin_final_tests_view()
        self.check_student_final_tests_view()
        print()
        
        # Step 3: Check student program enrollments
        print("🔍 STEP 2: Checking Student Program Enrollments")
        print("-" * 50)
        self.check_student_program_enrollments()
        print()
        
        # Step 4: Check program 'test3' existence
        print("🔍 STEP 3: Checking Program 'test3' Existence")
        print("-" * 50)
        self.check_program_test3_existence()
        print()
        
        # Step 5: Analyze permissions
        print("🔍 STEP 4: Analyzing Final Test Permissions")
        print("-" * 50)
        self.analyze_final_test_permissions()
        print()
        
        # Step 6: Check role-based restrictions
        print("🔍 STEP 5: Checking Role-based Restrictions")
        print("-" * 50)
        self.check_role_based_restrictions()
        print()
        
        # Step 7: Root cause analysis
        print("🔍 STEP 6: Root Cause Investigation")
        print("-" * 50)
        self.investigate_discrepancy_root_cause()
        print()
        
        # Summary
        print("=" * 80)
        print("📊 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Investigation Steps Completed: {total_tests}")
        print(f"Successful: {passed_tests} ✅")
        print(f"Issues Found: {failed_tests} ❌")
        print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        admin_tests = getattr(self, 'admin_final_tests', [])
        student_tests = getattr(self, 'student_final_tests', [])
        root_causes = getattr(self, 'root_causes', [])
        
        print(f"  • Admin sees: {len(admin_tests)} final tests")
        print(f"  • Student sees: {len(student_tests)} final tests")
        print(f"  • Discrepancy: {len(admin_tests) - len(student_tests)} tests")
        
        if root_causes:
            print(f"  • Root causes identified: {', '.join(root_causes)}")
        
        print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        if 'ALL_TESTS_UNPUBLISHED' in root_causes:
            print("  1. Publish final tests (set isPublished = true)")
        if 'STUDENT_NOT_ENROLLED_IN_ANY_PROGRAMS' in root_causes:
            print("  2. Enroll student in programs that have final tests")
        if 'NO_TESTS_FOR_STUDENT_PROGRAMS' in root_causes:
            print("  3. Create final tests for student's enrolled programs")
        if 'TESTS_WITHOUT_PROGRAMS' in root_causes:
            print("  4. Associate final tests with appropriate programs")
        
        print()
        return len(student_tests) > 0  # Success if student can see final tests

if __name__ == "__main__":
    investigator = FinalTestDiscrepancyInvestigator()
    success = investigator.run_investigation()
    
    if success:
        print("🎉 Investigation completed - Student can access final tests!")
        sys.exit(0)
    else:
        print("💥 Investigation completed - DISCREPANCY CONFIRMED!")
        sys.exit(1)