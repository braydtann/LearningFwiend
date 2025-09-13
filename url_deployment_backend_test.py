#!/usr/bin/env python3
"""
LearningFriend LMS Backend Testing - URL Configuration Verification
Testing backend functionality after URL configuration change to lms-chronology.emergent.host

Focus Areas:
1. Authentication endpoints - admin and student login
2. Health endpoint verification
3. Core API endpoints - course management APIs
4. Database connectivity - MongoDB connection stability
"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path

# Configuration - Updated to new deployment URL
BACKEND_URL = "https://lms-chronology.emergent.host/api"

# Test credentials as specified in review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class URLDeploymentTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_health_endpoint(self):
        """Test /api/health endpoint"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/health",
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") == "healthy" or "healthy" in response.text.lower():
                        self.log_result(
                            "Health Endpoint",
                            True,
                            "Health endpoint responding correctly",
                            {"response": data if isinstance(data, dict) else response.text}
                        )
                    else:
                        self.log_result(
                            "Health Endpoint",
                            False,
                            "Health endpoint returned unexpected response",
                            {"response": data if isinstance(data, dict) else response.text}
                        )
                except json.JSONDecodeError:
                    # Health endpoint might return plain text
                    if "healthy" in response.text.lower():
                        self.log_result(
                            "Health Endpoint",
                            True,
                            "Health endpoint responding correctly (plain text)",
                            {"response": response.text}
                        )
                    else:
                        self.log_result(
                            "Health Endpoint",
                            False,
                            "Health endpoint returned unexpected text response",
                            {"response": response.text}
                        )
            else:
                self.log_result(
                    "Health Endpoint",
                    False,
                    f"Health endpoint failed: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Health Endpoint",
                False,
                f"Health endpoint error: {str(e)}"
            )
    
    def test_admin_authentication(self):
        """Test admin authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                user_info = data.get("user", {})
                
                if self.admin_token and user_info.get("role") == "admin":
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.admin_token}"
                    })
                    self.log_result(
                        "Admin Authentication",
                        True,
                        f"Successfully authenticated admin: {user_info.get('email')}",
                        {
                            "user_id": user_info.get("id"),
                            "role": user_info.get("role"),
                            "full_name": user_info.get("full_name")
                        }
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication",
                        False,
                        "Authentication succeeded but missing token or admin role",
                        {"response": data}
                    )
                    return False
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"Admin authentication failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Admin Authentication",
                False,
                f"Admin authentication error: {str(e)}"
            )
            return False
    
    def test_student_authentication(self):
        """Test student authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                user_info = data.get("user", {})
                
                if self.student_token and user_info.get("role") == "learner":
                    self.log_result(
                        "Student Authentication",
                        True,
                        f"Successfully authenticated student: {user_info.get('email')}",
                        {
                            "user_id": user_info.get("id"),
                            "role": user_info.get("role"),
                            "full_name": user_info.get("full_name")
                        }
                    )
                    return True
                else:
                    self.log_result(
                        "Student Authentication",
                        False,
                        "Authentication succeeded but missing token or learner role",
                        {"response": data}
                    )
                    return False
            else:
                self.log_result(
                    "Student Authentication",
                    False,
                    f"Student authentication failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Student Authentication",
                False,
                f"Student authentication error: {str(e)}"
            )
            return False
    
    def test_database_connectivity(self):
        """Test database connectivity by fetching courses"""
        try:
            if not self.admin_token:
                self.log_result(
                    "Database Connectivity",
                    False,
                    "Cannot test database - admin authentication required"
                )
                return
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{BACKEND_URL}/courses",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "Database Connectivity",
                        True,
                        f"Successfully connected to database - retrieved {len(data)} courses",
                        {"course_count": len(data)}
                    )
                else:
                    self.log_result(
                        "Database Connectivity",
                        False,
                        "Database connected but unexpected response format",
                        {"response_type": type(data).__name__}
                    )
            else:
                self.log_result(
                    "Database Connectivity",
                    False,
                    f"Database connectivity test failed: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Database Connectivity",
                False,
                f"Database connectivity error: {str(e)}"
            )
    
    def test_course_management_apis(self):
        """Test core course management APIs"""
        if not self.admin_token:
            self.log_result(
                "Course Management APIs",
                False,
                "Cannot test course APIs - admin authentication required"
            )
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 1: Get all courses
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                courses = response.json()
                self.log_result(
                    "Get All Courses API",
                    True,
                    f"Successfully retrieved {len(courses)} courses"
                )
                
                # Test 2: Get specific course details if courses exist
                if courses and len(courses) > 0:
                    course_id = courses[0].get("id")
                    if course_id:
                        detail_response = requests.get(
                            f"{BACKEND_URL}/courses/{course_id}",
                            headers=headers,
                            timeout=10
                        )
                        
                        if detail_response.status_code == 200:
                            course_detail = detail_response.json()
                            self.log_result(
                                "Get Course Details API",
                                True,
                                f"Successfully retrieved course details: {course_detail.get('title', 'Unknown')}"
                            )
                        else:
                            self.log_result(
                                "Get Course Details API",
                                False,
                                f"Failed to get course details: {detail_response.status_code}"
                            )
                    else:
                        self.log_result(
                            "Get Course Details API",
                            False,
                            "Cannot test course details - no course ID found"
                        )
                else:
                    self.log_result(
                        "Get Course Details API",
                        True,
                        "No courses available to test details API (expected for new deployment)"
                    )
            else:
                self.log_result(
                    "Get All Courses API",
                    False,
                    f"Failed to get courses: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Course Management APIs",
                False,
                f"Course management API error: {str(e)}"
            )
    
    def test_enrollment_apis(self):
        """Test enrollment APIs"""
        if not self.student_token:
            self.log_result(
                "Enrollment APIs",
                False,
                "Cannot test enrollment APIs - student authentication required"
            )
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = requests.get(
                f"{BACKEND_URL}/enrollments",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                enrollments = response.json()
                self.log_result(
                    "Student Enrollments API",
                    True,
                    f"Successfully retrieved {len(enrollments)} enrollments for student"
                )
            else:
                self.log_result(
                    "Student Enrollments API",
                    False,
                    f"Failed to get enrollments: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Enrollment APIs",
                False,
                f"Enrollment API error: {str(e)}"
            )
    
    def test_user_management_apis(self):
        """Test user management APIs"""
        if not self.admin_token:
            self.log_result(
                "User Management APIs",
                False,
                "Cannot test user management APIs - admin authentication required"
            )
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test get current user info
            response = requests.get(
                f"{BACKEND_URL}/auth/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_info = response.json()
                self.log_result(
                    "Get Current User API",
                    True,
                    f"Successfully retrieved current user info: {user_info.get('email')}"
                )
            else:
                self.log_result(
                    "Get Current User API",
                    False,
                    f"Failed to get current user: {response.status_code} - {response.text}"
                )
            
            # Test get all users (admin only)
            response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                users = response.json()
                self.log_result(
                    "Get All Users API",
                    True,
                    f"Successfully retrieved {len(users)} users from system"
                )
            else:
                self.log_result(
                    "Get All Users API",
                    False,
                    f"Failed to get all users: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "User Management APIs",
                False,
                f"User management API error: {str(e)}"
            )
    
    def test_programs_and_categories(self):
        """Test programs and categories APIs"""
        if not self.admin_token:
            self.log_result(
                "Programs and Categories APIs",
                False,
                "Cannot test programs/categories APIs - admin authentication required"
            )
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test programs API
            response = requests.get(
                f"{BACKEND_URL}/programs",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                programs = response.json()
                self.log_result(
                    "Programs API",
                    True,
                    f"Successfully retrieved {len(programs)} programs"
                )
            else:
                self.log_result(
                    "Programs API",
                    False,
                    f"Failed to get programs: {response.status_code} - {response.text}"
                )
            
            # Test categories API
            response = requests.get(
                f"{BACKEND_URL}/categories",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                categories = response.json()
                self.log_result(
                    "Categories API",
                    True,
                    f"Successfully retrieved {len(categories)} categories"
                )
            else:
                self.log_result(
                    "Categories API",
                    False,
                    f"Failed to get categories: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_result(
                "Programs and Categories APIs",
                False,
                f"Programs/Categories API error: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all URL deployment verification tests"""
        print("🚀 Starting LearningFriend LMS Backend Testing")
        print("🌐 Testing URL Configuration: https://lms-chronology.emergent.host")
        print("=" * 70)
        
        # Test 1: Health endpoint (no auth required)
        print("\n🏥 Testing Health Endpoint...")
        self.test_health_endpoint()
        
        # Test 2: Authentication endpoints
        print("\n🔐 Testing Authentication Endpoints...")
        admin_auth_success = self.test_admin_authentication()
        student_auth_success = self.test_student_authentication()
        
        # Test 3: Database connectivity
        print("\n🗄️ Testing Database Connectivity...")
        self.test_database_connectivity()
        
        # Test 4: Core API endpoints (require authentication)
        if admin_auth_success:
            print("\n📚 Testing Course Management APIs...")
            self.test_course_management_apis()
            
            print("\n👥 Testing User Management APIs...")
            self.test_user_management_apis()
            
            print("\n📋 Testing Programs and Categories APIs...")
            self.test_programs_and_categories()
        
        if student_auth_success:
            print("\n📝 Testing Enrollment APIs...")
            self.test_enrollment_apis()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 URL DEPLOYMENT VERIFICATION SUMMARY")
        print("🌐 Backend URL: https://lms-chronology.emergent.host/api")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🚨 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   ✅ {result['test']}: {result['message']}")
        
        # Deployment readiness assessment
        print("\n" + "=" * 70)
        print("🎯 DEPLOYMENT READINESS ASSESSMENT")
        print("=" * 70)
        
        critical_tests = [
            "Health Endpoint",
            "Admin Authentication", 
            "Student Authentication",
            "Database Connectivity"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['test'] in critical_tests and result['success'])
        critical_total = len([r for r in self.test_results if r['test'] in critical_tests])
        
        if critical_passed == critical_total:
            print("🎉 DEPLOYMENT READY: All critical systems operational")
        else:
            print("⚠️  DEPLOYMENT ISSUES: Critical systems need attention")
            
        print(f"Critical Systems: {critical_passed}/{critical_total} operational")

def main():
    """Main function to run URL deployment verification tests"""
    tester = URLDeploymentTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()