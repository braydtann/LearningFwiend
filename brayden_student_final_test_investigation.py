#!/usr/bin/env python3
"""
Specific Investigation for Brayden Student Final Test Access Issue
Testing why brayden.student@covesmart.com sees 0 final tests while others see 7 tests.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://quiz-analytics-lms.preview.emergentagent.com/api"

# Test credentials for the specific student mentioned in review request
BRAYDEN_STUDENT_CREDENTIALS = [
    {
        "username_or_email": "brayden.student@covesmart.com",
        "password": "Hawaii2020!"
    },
    {
        "username_or_email": "brayden.student@covesmart.com", 
        "password": "Cove1234!"
    },
    {
        "username_or_email": "brayden.student@covesmart.com",
        "password": "StudentTest123!"
    }
]

# Comparison student credentials
KARLO_STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com",
    "password": "StudentPermanent123!"
}

# Admin credentials for investigation
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class FinalTestAccessInvestigator:
    def __init__(self):
        self.brayden_token = None
        self.karlo_token = None
        self.admin_token = None
        self.brayden_user_info = None
        self.karlo_user_info = None
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

    def authenticate_brayden_student(self):
        """Try to authenticate brayden.student@covesmart.com with different passwords"""
        for i, credentials in enumerate(BRAYDEN_STUDENT_CREDENTIALS):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json=credentials,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.brayden_token = data.get('access_token')
                    self.brayden_user_info = data.get('user', {})
                    
                    self.log_result(
                        f"Brayden Student Authentication (Password {i+1})", 
                        True, 
                        f"Authenticated as {self.brayden_user_info.get('full_name')} ({self.brayden_user_info.get('email')}) with password {i+1}"
                    )
                    return True
                else:
                    self.log_result(
                        f"Brayden Student Authentication (Password {i+1})", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Brayden Student Authentication (Password {i+1})", 
                    False, 
                    f"Exception: {str(e)}"
                )
        
        return False

    def authenticate_karlo_student(self):
        """Authenticate karlo.student@alder.com for comparison"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=KARLO_STUDENT_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.karlo_token = data.get('access_token')
                self.karlo_user_info = data.get('user', {})
                
                self.log_result(
                    "Karlo Student Authentication", 
                    True, 
                    f"Authenticated as {self.karlo_user_info.get('full_name')} ({self.karlo_user_info.get('email')})"
                )
                return True
            else:
                self.log_result("Karlo Student Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Karlo Student Authentication", False, f"Exception: {str(e)}")
            return False

    def authenticate_admin(self):
        """Authenticate admin for investigation"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                
                self.log_result(
                    "Admin Authentication", 
                    True, 
                    f"Authenticated as admin"
                )
                return True
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def test_brayden_final_tests_access(self):
        """Test brayden.student final tests access without program_id filter"""
        try:
            headers = {"Authorization": f"Bearer {self.brayden_token}"}
            
            response = requests.get(
                f"{BACKEND_URL}/final-tests",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                tests = response.json()
                test_count = len(tests)
                
                self.log_result(
                    "Brayden Final Tests Access (No Filter)", 
                    True, 
                    f"Found {test_count} final tests available to brayden.student@covesmart.com"
                )
                
                # Log details of each test
                if test_count > 0:
                    print("   Available Final Tests:")
                    for test in tests:
                        print(f"     - {test.get('title', 'Unknown')} (ID: {test.get('id', 'Unknown')}, Program: {test.get('programId', 'None')})")
                else:
                    print("   No final tests found for this student")
                
                return test_count
            else:
                self.log_result(
                    "Brayden Final Tests Access (No Filter)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return 0
                
        except Exception as e:
            self.log_result("Brayden Final Tests Access (No Filter)", False, f"Exception: {str(e)}")
            return 0

    def test_brayden_final_tests_with_program_filter(self):
        """Test brayden.student final tests access with specific program_id"""
        program_id = "1233456-5414-49ee-ab4f-d7a617105f4a"
        
        try:
            headers = {"Authorization": f"Bearer {self.brayden_token}"}
            
            response = requests.get(
                f"{BACKEND_URL}/final-tests?program_id={program_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                tests = response.json()
                test_count = len(tests)
                
                self.log_result(
                    "Brayden Final Tests Access (With Program Filter)", 
                    True, 
                    f"Found {test_count} final tests for program {program_id}"
                )
                
                # Log details of each test
                if test_count > 0:
                    print("   Available Final Tests for Program:")
                    for test in tests:
                        print(f"     - {test.get('title', 'Unknown')} (ID: {test.get('id', 'Unknown')})")
                
                return test_count
            else:
                self.log_result(
                    "Brayden Final Tests Access (With Program Filter)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return 0
                
        except Exception as e:
            self.log_result("Brayden Final Tests Access (With Program Filter)", False, f"Exception: {str(e)}")
            return 0

    def test_karlo_final_tests_access(self):
        """Test karlo.student final tests access for comparison"""
        try:
            headers = {"Authorization": f"Bearer {self.karlo_token}"}
            
            response = requests.get(
                f"{BACKEND_URL}/final-tests",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                tests = response.json()
                test_count = len(tests)
                
                self.log_result(
                    "Karlo Final Tests Access (Comparison)", 
                    True, 
                    f"Found {test_count} final tests available to karlo.student@alder.com"
                )
                
                # Log details of each test
                if test_count > 0:
                    print("   Available Final Tests:")
                    for test in tests:
                        print(f"     - {test.get('title', 'Unknown')} (ID: {test.get('id', 'Unknown')}, Program: {test.get('programId', 'None')})")
                
                return test_count
            else:
                self.log_result(
                    "Karlo Final Tests Access (Comparison)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return 0
                
        except Exception as e:
            self.log_result("Karlo Final Tests Access (Comparison)", False, f"Exception: {str(e)}")
            return 0

    def investigate_student_permissions(self):
        """Compare student permissions and enrollments"""
        try:
            # Get Brayden's enrollments
            brayden_headers = {"Authorization": f"Bearer {self.brayden_token}"}
            brayden_enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                headers=brayden_headers,
                timeout=10
            )
            
            # Get Karlo's enrollments
            karlo_headers = {"Authorization": f"Bearer {self.karlo_token}"}
            karlo_enrollments_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                headers=karlo_headers,
                timeout=10
            )
            
            brayden_enrollments = []
            karlo_enrollments = []
            
            if brayden_enrollments_response.status_code == 200:
                brayden_enrollments = brayden_enrollments_response.json()
            
            if karlo_enrollments_response.status_code == 200:
                karlo_enrollments = karlo_enrollments_response.json()
            
            self.log_result(
                "Student Permissions Investigation", 
                True, 
                f"Brayden enrollments: {len(brayden_enrollments)}, Karlo enrollments: {len(karlo_enrollments)}"
            )
            
            print("   Brayden Student Enrollments:")
            for enrollment in brayden_enrollments:
                print(f"     - Course: {enrollment.get('courseId', 'Unknown')}, Progress: {enrollment.get('progress', 0)}%")
            
            print("   Karlo Student Enrollments:")
            for enrollment in karlo_enrollments:
                print(f"     - Course: {enrollment.get('courseId', 'Unknown')}, Progress: {enrollment.get('progress', 0)}%")
            
            return True
                
        except Exception as e:
            self.log_result("Student Permissions Investigation", False, f"Exception: {str(e)}")
            return False

    def investigate_published_final_tests(self):
        """Check all published final tests from admin perspective"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(
                f"{BACKEND_URL}/final-tests",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                tests = response.json()
                published_tests = [test for test in tests if test.get('isPublished', False)]
                
                self.log_result(
                    "Published Final Tests Investigation", 
                    True, 
                    f"Total final tests: {len(tests)}, Published: {len(published_tests)}"
                )
                
                print("   All Published Final Tests:")
                for test in published_tests:
                    print(f"     - {test.get('title', 'Unknown')} (ID: {test.get('id', 'Unknown')}, Program: {test.get('programId', 'None')})")
                
                return len(published_tests)
            else:
                self.log_result(
                    "Published Final Tests Investigation", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return 0
                
        except Exception as e:
            self.log_result("Published Final Tests Investigation", False, f"Exception: {str(e)}")
            return 0

    def check_student_program_access(self):
        """Check if students have access to programs that contain final tests"""
        program_id = "1233456-5414-49ee-ab4f-d7a617105f4a"
        
        try:
            # Check Brayden's program access
            brayden_headers = {"Authorization": f"Bearer {self.brayden_token}"}
            brayden_response = requests.get(
                f"{BACKEND_URL}/programs/{program_id}/access-check",
                headers=brayden_headers,
                timeout=10
            )
            
            # Check Karlo's program access
            karlo_headers = {"Authorization": f"Bearer {self.karlo_token}"}
            karlo_response = requests.get(
                f"{BACKEND_URL}/programs/{program_id}/access-check",
                headers=karlo_headers,
                timeout=10
            )
            
            brayden_access = None
            karlo_access = None
            
            if brayden_response.status_code == 200:
                brayden_access = brayden_response.json()
            
            if karlo_response.status_code == 200:
                karlo_access = karlo_response.json()
            
            self.log_result(
                "Student Program Access Check", 
                True, 
                f"Checked program access for both students"
            )
            
            print(f"   Brayden Program Access: {brayden_access}")
            print(f"   Karlo Program Access: {karlo_access}")
            
            return True
                
        except Exception as e:
            self.log_result("Student Program Access Check", False, f"Exception: {str(e)}")
            return False

    def run_investigation(self):
        """Run complete investigation of final test access discrepancy"""
        print("🔍 Starting Final Test Access Investigation for brayden.student@covesmart.com")
        print("=" * 80)
        print()
        
        # Authentication
        if not self.authenticate_brayden_student():
            print("❌ Brayden student authentication failed - cannot continue")
            return False
            
        if not self.authenticate_karlo_student():
            print("❌ Karlo student authentication failed - cannot continue comparison")
            return False
            
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot investigate from admin perspective")
            return False
        
        # Investigation tests
        print("🔍 INVESTIGATING FINAL TEST ACCESS DISCREPANCY")
        print("-" * 50)
        
        brayden_tests_no_filter = self.test_brayden_final_tests_access()
        brayden_tests_with_filter = self.test_brayden_final_tests_with_program_filter()
        karlo_tests = self.test_karlo_final_tests_access()
        published_tests = self.investigate_published_final_tests()
        
        self.investigate_student_permissions()
        self.check_student_program_access()
        
        # Analysis
        print("=" * 80)
        print("📊 FINAL TEST ACCESS INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        
        print(f"Total Investigation Steps: {total_tests}")
        print(f"Completed Successfully: {passed_tests} ✅")
        print()
        
        print("🔍 KEY FINDINGS:")
        print(f"  • Brayden Student (no filter): {brayden_tests_no_filter} final tests")
        print(f"  • Brayden Student (with program filter): {brayden_tests_with_filter} final tests")
        print(f"  • Karlo Student (comparison): {karlo_tests} final tests")
        print(f"  • Total Published Final Tests: {published_tests}")
        print()
        
        # Root cause analysis
        if brayden_tests_no_filter == 0 and karlo_tests > 0:
            print("🚨 ROOT CAUSE IDENTIFIED:")
            print("  • Brayden student has different access permissions than Karlo student")
            print("  • This could be due to:")
            print("    - Different program enrollments")
            print("    - Different classroom assignments")
            print("    - Different course completion status")
            print("    - User role or permission differences")
        elif brayden_tests_no_filter == karlo_tests:
            print("✅ NO ACCESS DISCREPANCY DETECTED:")
            print("  • Both students have the same number of accessible final tests")
        else:
            print("⚠️ PARTIAL ACCESS DISCREPANCY:")
            print("  • Students have different but non-zero access to final tests")
        
        print()
        return True

if __name__ == "__main__":
    investigator = FinalTestAccessInvestigator()
    success = investigator.run_investigation()
    
    if success:
        print("🎉 Final test access investigation completed!")
        sys.exit(0)
    else:
        print("💥 Final test access investigation failed!")
        sys.exit(1)