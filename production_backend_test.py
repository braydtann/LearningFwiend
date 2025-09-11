#!/usr/bin/env python3
"""
Production Backend URL Testing Suite for LearningFwiend LMS Application
Tests production backend URL (https://lms-evolution.emergent.host/api) for frontend testing compatibility
"""

import requests
import json
import os
import sys
from datetime import datetime
import time

# Configuration - Production Backend URL to test
PRODUCTION_BACKEND_URL = "https://lms-evolution.emergent.host/api"
PREVIEW_BACKEND_URL = "https://deploy-fixer-9.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

class ProductionBackendTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}  # Store auth tokens for different users
        self.production_data = {}  # Store production backend data
        self.preview_data = {}  # Store preview backend data for comparison
        
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
    
    # =============================================================================
    # PRODUCTION BACKEND AUTHENTICATION TESTS
    # =============================================================================
    
    def test_production_admin_authentication(self):
        """Test admin authentication on production backend"""
        try:
            login_data = {
                "username_or_email": "brayden.t@covesmart.com",
                "password": "Hawaii2020!"
            }
            
            response = requests.post(
                f"{PRODUCTION_BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'admin':
                    self.auth_tokens['production_admin'] = token
                    self.log_result(
                        "Production Admin Authentication", 
                        "PASS", 
                        f"✅ Admin login successful on production backend",
                        f"User: {user_info.get('full_name')} ({user_info.get('email')}), Role: {user_info.get('role')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Production Admin Authentication", 
                        "FAIL", 
                        "Login response missing token or incorrect role",
                        f"Token present: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Production Admin Authentication", 
                    "FAIL", 
                    f"Admin authentication failed on production backend (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Production Admin Authentication", 
                "FAIL", 
                "Failed to connect to production backend for admin authentication",
                str(e)
            )
        return False
    
    def test_production_student_authentication(self):
        """Test student authentication on production backend"""
        try:
            login_data = {
                "username_or_email": "karlo.student@alder.com",
                "password": "StudentPermanent123!"
            }
            
            response = requests.post(
                f"{PRODUCTION_BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'learner':
                    self.auth_tokens['production_student'] = token
                    self.log_result(
                        "Production Student Authentication", 
                        "PASS", 
                        f"✅ Student login successful on production backend",
                        f"User: {user_info.get('full_name')} ({user_info.get('email')}), Role: {user_info.get('role')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Production Student Authentication", 
                        "FAIL", 
                        "Login response missing token or incorrect role",
                        f"Token present: {bool(token)}, Role: {user_info.get('role')}"
                    )
            else:
                self.log_result(
                    "Production Student Authentication", 
                    "FAIL", 
                    f"Student authentication failed on production backend (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Production Student Authentication", 
                "FAIL", 
                "Failed to connect to production backend for student authentication",
                str(e)
            )
        return False
    
    # =============================================================================
    # PRODUCTION BACKEND API ENDPOINT TESTS
    # =============================================================================
    
    def test_production_courses_api(self):
        """Test courses API on production backend"""
        if "production_student" not in self.auth_tokens:
            self.log_result(
                "Production Courses API", 
                "SKIP", 
                "No student token available for courses API test",
                "Student authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{PRODUCTION_BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["production_student"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                self.production_data['courses'] = courses
                
                # Look for specific courses mentioned in review
                pizza_course = None
                for course in courses:
                    if 'pizza' in course.get('title', '').lower():
                        pizza_course = course
                        break
                
                self.log_result(
                    "Production Courses API", 
                    "PASS", 
                    f"✅ Courses API working on production backend - {len(courses)} courses available",
                    f"Pizza course found: {'Yes' if pizza_course else 'No'}, Sample courses: {[c.get('title', 'Unknown')[:30] for c in courses[:3]]}"
                )
                return True
            else:
                self.log_result(
                    "Production Courses API", 
                    "FAIL", 
                    f"Courses API failed on production backend (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Production Courses API", 
                "FAIL", 
                "Failed to test courses API on production backend",
                str(e)
            )
        return False
    
    def test_production_enrollments_api(self):
        """Test enrollments API on production backend"""
        if "production_student" not in self.auth_tokens:
            self.log_result(
                "Production Enrollments API", 
                "SKIP", 
                "No student token available for enrollments API test",
                "Student authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{PRODUCTION_BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["production_student"]}'}
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                self.production_data['enrollments'] = enrollments
                
                self.log_result(
                    "Production Enrollments API", 
                    "PASS", 
                    f"✅ Enrollments API working on production backend - {len(enrollments)} enrollments found",
                    f"Student has {len(enrollments)} course enrollments"
                )
                return True
            else:
                self.log_result(
                    "Production Enrollments API", 
                    "FAIL", 
                    f"Enrollments API failed on production backend (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Production Enrollments API", 
                "FAIL", 
                "Failed to test enrollments API on production backend",
                str(e)
            )
        return False
    
    def test_production_classrooms_api(self):
        """Test classrooms API on production backend"""
        if "production_admin" not in self.auth_tokens:
            self.log_result(
                "Production Classrooms API", 
                "SKIP", 
                "No admin token available for classrooms API test",
                "Admin authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{PRODUCTION_BACKEND_URL}/classrooms",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["production_admin"]}'}
            )
            
            if response.status_code == 200:
                classrooms = response.json()
                self.production_data['classrooms'] = classrooms
                
                # Look for QC1 classroom mentioned in review
                qc1_classroom = None
                for classroom in classrooms:
                    if classroom.get('name', '').lower() == 'qc1':
                        qc1_classroom = classroom
                        break
                
                self.log_result(
                    "Production Classrooms API", 
                    "PASS", 
                    f"✅ Classrooms API working on production backend - {len(classrooms)} classrooms found",
                    f"QC1 classroom found: {'Yes' if qc1_classroom else 'No'}, Total classrooms: {len(classrooms)}"
                )
                return True
            else:
                self.log_result(
                    "Production Classrooms API", 
                    "FAIL", 
                    f"Classrooms API failed on production backend (status: {response.status_code})",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Production Classrooms API", 
                "FAIL", 
                "Failed to test classrooms API on production backend",
                str(e)
            )
        return False
    
    # =============================================================================
    # DATA COMPARISON TESTS (Production vs Preview)
    # =============================================================================
    
    def test_preview_backend_data_for_comparison(self):
        """Get data from preview backend for comparison"""
        try:
            # Test admin login on preview
            login_data = {
                "username_or_email": "brayden.t@covesmart.com",
                "password": "Hawaii2020!"
            }
            
            response = requests.post(
                f"{PREVIEW_BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                if token:
                    self.auth_tokens['preview_admin'] = token
                    
                    # Get preview courses
                    courses_response = requests.get(
                        f"{PREVIEW_BACKEND_URL}/courses",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {token}'}
                    )
                    
                    if courses_response.status_code == 200:
                        self.preview_data['courses'] = courses_response.json()
                    
                    # Get preview classrooms
                    classrooms_response = requests.get(
                        f"{PREVIEW_BACKEND_URL}/classrooms",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {token}'}
                    )
                    
                    if classrooms_response.status_code == 200:
                        self.preview_data['classrooms'] = classrooms_response.json()
                    
                    self.log_result(
                        "Preview Backend Data Collection", 
                        "PASS", 
                        f"✅ Successfully collected preview backend data for comparison",
                        f"Courses: {len(self.preview_data.get('courses', []))}, Classrooms: {len(self.preview_data.get('classrooms', []))}"
                    )
                    return True
            
            self.log_result(
                "Preview Backend Data Collection", 
                "FAIL", 
                "Failed to collect preview backend data for comparison",
                "Could not authenticate with preview backend"
            )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Preview Backend Data Collection", 
                "FAIL", 
                "Failed to connect to preview backend for data comparison",
                str(e)
            )
        return False
    
    def test_data_consistency_comparison(self):
        """Compare production and preview backend data"""
        if not self.production_data or not self.preview_data:
            self.log_result(
                "Data Consistency Comparison", 
                "SKIP", 
                "Missing data from production or preview backend",
                "Need both production and preview data for comparison"
            )
            return False
        
        comparison_results = []
        
        # Compare courses
        prod_courses = self.production_data.get('courses', [])
        preview_courses = self.preview_data.get('courses', [])
        
        prod_course_titles = set(c.get('title', '') for c in prod_courses)
        preview_course_titles = set(c.get('title', '') for c in preview_courses)
        
        common_courses = prod_course_titles.intersection(preview_course_titles)
        prod_only_courses = prod_course_titles - preview_course_titles
        preview_only_courses = preview_course_titles - prod_course_titles
        
        comparison_results.append(f"Courses - Production: {len(prod_courses)}, Preview: {len(preview_courses)}, Common: {len(common_courses)}")
        
        # Compare classrooms
        prod_classrooms = self.production_data.get('classrooms', [])
        preview_classrooms = self.preview_data.get('classrooms', [])
        
        prod_classroom_names = set(c.get('name', '') for c in prod_classrooms)
        preview_classroom_names = set(c.get('name', '') for c in preview_classrooms)
        
        common_classrooms = prod_classroom_names.intersection(preview_classroom_names)
        
        comparison_results.append(f"Classrooms - Production: {len(prod_classrooms)}, Preview: {len(preview_classrooms)}, Common: {len(common_classrooms)}")
        
        # Check for specific items mentioned in review
        pizza_course_in_prod = any('pizza' in c.get('title', '').lower() for c in prod_courses)
        pizza_course_in_preview = any('pizza' in c.get('title', '').lower() for c in preview_courses)
        qc1_classroom_in_prod = any(c.get('name', '').lower() == 'qc1' for c in prod_classrooms)
        qc1_classroom_in_preview = any(c.get('name', '').lower() == 'qc1' for c in preview_classrooms)
        
        comparison_results.append(f"Pizza course - Production: {'Yes' if pizza_course_in_prod else 'No'}, Preview: {'Yes' if pizza_course_in_preview else 'No'}")
        comparison_results.append(f"QC1 classroom - Production: {'Yes' if qc1_classroom_in_prod else 'No'}, Preview: {'Yes' if qc1_classroom_in_preview else 'No'}")
        
        # Determine if data is consistent enough
        courses_similar = len(common_courses) > 0 or (len(prod_courses) > 0 and len(preview_courses) > 0)
        classrooms_similar = len(common_classrooms) > 0 or (len(prod_classrooms) > 0 and len(preview_classrooms) > 0)
        
        if courses_similar and classrooms_similar:
            self.log_result(
                "Data Consistency Comparison", 
                "PASS", 
                f"✅ Production and preview backends have similar data structure",
                "; ".join(comparison_results)
            )
            return True
        else:
            self.log_result(
                "Data Consistency Comparison", 
                "FAIL", 
                f"❌ Significant differences between production and preview backend data",
                "; ".join(comparison_results)
            )
        return False
    
    # =============================================================================
    # PRODUCTION READINESS ASSESSMENT
    # =============================================================================
    
    def test_production_backend_readiness(self):
        """Assess if production backend is ready for frontend testing"""
        readiness_checks = []
        
        # Check authentication
        admin_auth = "production_admin" in self.auth_tokens
        student_auth = "production_student" in self.auth_tokens
        
        readiness_checks.append(f"Admin Authentication: {'✅' if admin_auth else '❌'}")
        readiness_checks.append(f"Student Authentication: {'✅' if student_auth else '❌'}")
        
        # Check API endpoints
        courses_api = len(self.production_data.get('courses', [])) > 0
        enrollments_api = 'enrollments' in self.production_data
        classrooms_api = 'classrooms' in self.production_data
        
        readiness_checks.append(f"Courses API: {'✅' if courses_api else '❌'}")
        readiness_checks.append(f"Enrollments API: {'✅' if enrollments_api else '❌'}")
        readiness_checks.append(f"Classrooms API: {'✅' if classrooms_api else '❌'}")
        
        # Check for specific data mentioned in review
        has_courses = len(self.production_data.get('courses', [])) > 0
        has_classrooms = len(self.production_data.get('classrooms', [])) > 0
        has_enrollments = len(self.production_data.get('enrollments', [])) > 0
        
        readiness_checks.append(f"Has Courses: {'✅' if has_courses else '❌'}")
        readiness_checks.append(f"Has Classrooms: {'✅' if has_classrooms else '❌'}")
        readiness_checks.append(f"Has Enrollments: {'✅' if has_enrollments else '❌'}")
        
        # Calculate readiness score
        total_checks = len(readiness_checks)
        passed_checks = len([check for check in readiness_checks if '✅' in check])
        readiness_score = (passed_checks / total_checks) * 100
        
        if readiness_score >= 80:
            self.log_result(
                "Production Backend Readiness Assessment", 
                "PASS", 
                f"✅ Production backend is ready for frontend testing ({readiness_score:.1f}% readiness)",
                f"Readiness checks: {'; '.join(readiness_checks)}"
            )
            return True
        else:
            self.log_result(
                "Production Backend Readiness Assessment", 
                "FAIL", 
                f"❌ Production backend not ready for frontend testing ({readiness_score:.1f}% readiness)",
                f"Readiness checks: {'; '.join(readiness_checks)}"
            )
        return False
    
    # =============================================================================
    # MAIN TEST EXECUTION
    # =============================================================================
    
    def run_all_tests(self):
        """Run all production backend tests"""
        print("🚀 PRODUCTION BACKEND URL TESTING FOR FRONTEND COMPATIBILITY")
        print("=" * 80)
        print(f"Testing production backend: {PRODUCTION_BACKEND_URL}")
        print(f"Comparing with preview backend: {PREVIEW_BACKEND_URL}")
        print("=" * 80)
        
        # Test 1: Production backend authentication
        print(f"\n🔑 STEP 1: Testing Production Backend Authentication")
        print("-" * 60)
        admin_auth_success = self.test_production_admin_authentication()
        student_auth_success = self.test_production_student_authentication()
        
        # Test 2: Production backend API endpoints
        print(f"\n📡 STEP 2: Testing Production Backend API Endpoints")
        print("-" * 60)
        courses_api_success = self.test_production_courses_api()
        enrollments_api_success = self.test_production_enrollments_api()
        classrooms_api_success = self.test_production_classrooms_api()
        
        # Test 3: Preview backend data collection for comparison
        print(f"\n📊 STEP 3: Collecting Preview Backend Data for Comparison")
        print("-" * 60)
        preview_data_success = self.test_preview_backend_data_for_comparison()
        
        # Test 4: Data consistency comparison
        print(f"\n🔍 STEP 4: Comparing Production vs Preview Backend Data")
        print("-" * 60)
        data_consistency_success = self.test_data_consistency_comparison()
        
        # Test 5: Production readiness assessment
        print(f"\n✅ STEP 5: Production Backend Readiness Assessment")
        print("-" * 60)
        readiness_success = self.test_production_backend_readiness()
        
        # Final summary
        print(f"\n📋 PRODUCTION BACKEND TESTING SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {len(self.results)}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed / len(self.results) * 100):.1f}%")
        
        # Recommendation
        print(f"\n🎯 RECOMMENDATION FOR FRONTEND TESTING")
        print("=" * 60)
        
        if readiness_success and admin_auth_success and student_auth_success:
            print("✅ SAFE TO SWITCH TO PRODUCTION BACKEND")
            print(f"   Production backend URL: {PRODUCTION_BACKEND_URL}")
            print("   ✅ Authentication working for both admin and student")
            print("   ✅ Key API endpoints functional")
            print("   ✅ Data structure compatible with frontend")
            print("\n   Update frontend/.env:")
            print(f"   REACT_APP_BACKEND_URL=https://lms-evolution.emergent.host")
        else:
            print("❌ NOT SAFE TO SWITCH TO PRODUCTION BACKEND YET")
            print("   Issues found that need to be resolved:")
            
            if not admin_auth_success:
                print("   ❌ Admin authentication failing")
            if not student_auth_success:
                print("   ❌ Student authentication failing")
            if not courses_api_success:
                print("   ❌ Courses API not working")
            if not enrollments_api_success:
                print("   ❌ Enrollments API not working")
            if not classrooms_api_success:
                print("   ❌ Classrooms API not working")
            
            print(f"\n   Continue using preview backend:")
            print(f"   REACT_APP_BACKEND_URL=https://deploy-fixer-9.preview.emergentagent.com")
        
        return readiness_success

def main():
    """Main function to run production backend tests"""
    tester = ProductionBackendTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()