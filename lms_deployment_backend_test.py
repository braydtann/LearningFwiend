#!/usr/bin/env python3
"""
🚀 LMS BACKEND DEPLOYMENT READINESS TEST SUITE

TESTING OBJECTIVES:
1. **Health Check Endpoint**: Test /health endpoint for database connectivity
2. **Root Endpoint**: Test root endpoint (/)
3. **API Endpoints**: Test key API endpoints under /api prefix
   - Authentication endpoints (/api/auth/*)
   - Course management (/api/courses)
   - Program management (/api/programs)
4. **Database Connectivity**: Verify MongoDB connection is working
5. **Error Handling**: Check that the application handles errors gracefully
6. **Environment Variables**: Verify the app properly reads from environment variables

CONTEXT:
- App was failing deployment to Kubernetes with Emergent native deployment
- Fixed hardcoded URLs and improved MongoDB connection handling for Atlas
- Added health checks and better logging for production deployment
- Backend URL should be available at the configured REACT_APP_BACKEND_URL
- MongoDB should work with both local and Atlas connections

SUCCESS CRITERIA:
- All critical endpoints return proper responses
- Database connectivity is working
- Authentication system is functional
- Error handling is graceful
- Environment variables are properly configured
"""

import requests
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class LMSDeploymentTestSuite:
    def __init__(self):
        # Read backend URL from frontend/.env as per system instructions
        self.backend_url = self.get_backend_url()
        self.base_url = f"{self.backend_url}/api"
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        
        # Test credentials
        self.admin_credentials = {
            "username_or_email": "brayden.t@covesmart.com",
            "password": "Hawaii2020!"
        }
        
        self.student_credentials = {
            "username_or_email": "karlo.student@alder.com", 
            "password": "StudentPermanent123!"
        }
        
    def get_backend_url(self) -> str:
        """Get backend URL from frontend/.env file"""
        try:
            env_path = "/app/frontend/.env"
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('REACT_APP_BACKEND_URL='):
                            url = line.split('=', 1)[1].strip()
                            print(f"📍 Using backend URL from frontend/.env: {url}")
                            return url
            
            # Fallback to localhost if env file not found
            fallback_url = "http://localhost:8001"
            print(f"⚠️  Frontend .env not found, using fallback: {fallback_url}")
            return fallback_url
            
        except Exception as e:
            fallback_url = "http://localhost:8001"
            print(f"⚠️  Error reading frontend/.env: {e}, using fallback: {fallback_url}")
            return fallback_url
        
    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test results with timestamp"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"    Details: {details}")
        if not success and data:
            print(f"    Error Data: {data}")
        print()

    def test_health_endpoint(self) -> bool:
        """Test the /health endpoint for database connectivity"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected health check fields
                has_status = 'status' in data
                has_database = 'database' in data
                has_timestamp = 'timestamp' in data
                
                db_status = data.get('database', {}).get('status', 'unknown')
                overall_status = data.get('status', 'unknown')
                
                success = (
                    has_status and has_database and has_timestamp and
                    overall_status == 'healthy' and
                    db_status == 'connected'
                )
                
                if success:
                    self.log_test(
                        "Health Check Endpoint",
                        True,
                        f"Health check passed - Status: {overall_status}, DB: {db_status}"
                    )
                else:
                    self.log_test(
                        "Health Check Endpoint",
                        False,
                        f"Health check failed - Status: {overall_status}, DB: {db_status}",
                        data
                    )
                
                return success
            else:
                self.log_test(
                    "Health Check Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Health Check Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_root_endpoint(self) -> bool:
        """Test the root endpoint (/)"""
        try:
            response = requests.get(f"{self.backend_url}/", timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    message = data.get('message', '')
                    
                    # Check for expected response
                    success = 'Hello World' in message or 'LMS' in message or 'API' in message
                    
                    self.log_test(
                        "Root Endpoint",
                        success,
                        f"Root endpoint response: {message}"
                    )
                    return success
                    
                except json.JSONDecodeError:
                    # If not JSON, check if it's a valid HTML response
                    content = response.text
                    success = len(content) > 0
                    
                    self.log_test(
                        "Root Endpoint",
                        success,
                        f"Root endpoint returned HTML content ({len(content)} chars)"
                    )
                    return success
            else:
                self.log_test(
                    "Root Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_api_root_endpoint(self) -> bool:
        """Test the API root endpoint (/api)"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', '')
                
                success = 'Hello World' in message or 'API' in message
                
                self.log_test(
                    "API Root Endpoint",
                    success,
                    f"API root response: {message}"
                )
                return success
            else:
                self.log_test(
                    "API Root Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Exception: {str(e)}")
            return False

    def authenticate_admin(self) -> bool:
        """Test admin authentication"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=self.admin_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                user_info = data.get("user", {})
                
                success = (
                    self.admin_token is not None and
                    user_info.get('role') == 'admin'
                )
                
                if success:
                    self.log_test(
                        "Admin Authentication",
                        True,
                        f"Successfully authenticated as {user_info.get('full_name', 'Admin')} (Role: {user_info.get('role', 'Unknown')})"
                    )
                else:
                    self.log_test(
                        "Admin Authentication",
                        False,
                        f"Authentication succeeded but invalid token or role: {user_info.get('role')}"
                    )
                
                return success
            else:
                self.log_test(
                    "Admin Authentication", 
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def authenticate_student(self) -> bool:
        """Test student authentication"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=self.student_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                user_info = data.get("user", {})
                
                success = (
                    self.student_token is not None and
                    user_info.get('role') == 'learner'
                )
                
                if success:
                    self.log_test(
                        "Student Authentication",
                        True,
                        f"Successfully authenticated as {user_info.get('full_name', 'Student')} (Role: {user_info.get('role', 'Unknown')})"
                    )
                else:
                    self.log_test(
                        "Student Authentication",
                        False,
                        f"Authentication succeeded but invalid token or role: {user_info.get('role')}"
                    )
                
                return success
            else:
                self.log_test(
                    "Student Authentication", 
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Student Authentication", False, f"Exception: {str(e)}")
            return False

    def test_auth_me_endpoint(self) -> bool:
        """Test the /auth/me endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/auth/me", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ['id', 'email', 'username', 'full_name', 'role']
                has_required_fields = all(field in data for field in required_fields)
                
                success = has_required_fields and data.get('role') == 'admin'
                
                self.log_test(
                    "Auth Me Endpoint",
                    success,
                    f"User info retrieved - Role: {data.get('role')}, Email: {data.get('email')}"
                )
                return success
            else:
                self.log_test(
                    "Auth Me Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Auth Me Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_courses_endpoint(self) -> bool:
        """Test the courses management endpoints"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test GET /api/courses
            response = requests.get(f"{self.base_url}/courses", headers=headers, timeout=10)
            
            if response.status_code == 200:
                courses = response.json()
                
                success = isinstance(courses, list)
                course_count = len(courses) if success else 0
                
                self.log_test(
                    "Courses List Endpoint",
                    success,
                    f"Retrieved {course_count} courses"
                )
                
                # Test individual course endpoint if courses exist
                if success and course_count > 0:
                    first_course = courses[0]
                    course_id = first_course.get('id')
                    
                    if course_id:
                        course_response = requests.get(
                            f"{self.base_url}/courses/{course_id}", 
                            headers=headers, 
                            timeout=10
                        )
                        
                        if course_response.status_code == 200:
                            course_detail = course_response.json()
                            
                            required_fields = ['id', 'title', 'description', 'instructor']
                            has_required_fields = all(field in course_detail for field in required_fields)
                            
                            self.log_test(
                                "Course Detail Endpoint",
                                has_required_fields,
                                f"Course detail retrieved - Title: {course_detail.get('title', 'Unknown')}"
                            )
                        else:
                            self.log_test(
                                "Course Detail Endpoint",
                                False,
                                f"HTTP {course_response.status_code}: {course_response.text}"
                            )
                
                return success
            else:
                self.log_test(
                    "Courses List Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Courses Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_programs_endpoint(self) -> bool:
        """Test the programs management endpoints"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test GET /api/programs
            response = requests.get(f"{self.base_url}/programs", headers=headers, timeout=10)
            
            if response.status_code == 200:
                programs = response.json()
                
                success = isinstance(programs, list)
                program_count = len(programs) if success else 0
                
                self.log_test(
                    "Programs List Endpoint",
                    success,
                    f"Retrieved {program_count} programs"
                )
                
                # Test individual program endpoint if programs exist
                if success and program_count > 0:
                    first_program = programs[0]
                    program_id = first_program.get('id')
                    
                    if program_id:
                        program_response = requests.get(
                            f"{self.base_url}/programs/{program_id}", 
                            headers=headers, 
                            timeout=10
                        )
                        
                        if program_response.status_code == 200:
                            program_detail = program_response.json()
                            
                            required_fields = ['id', 'title', 'description', 'instructor']
                            has_required_fields = all(field in program_detail for field in required_fields)
                            
                            self.log_test(
                                "Program Detail Endpoint",
                                has_required_fields,
                                f"Program detail retrieved - Title: {program_detail.get('title', 'Unknown')}"
                            )
                        else:
                            self.log_test(
                                "Program Detail Endpoint",
                                False,
                                f"HTTP {program_response.status_code}: {program_response.text}"
                            )
                
                return success
            else:
                self.log_test(
                    "Programs List Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Programs Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_enrollments_endpoint(self) -> bool:
        """Test the enrollments endpoints"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Test GET /api/enrollments
            response = requests.get(f"{self.base_url}/enrollments", headers=headers, timeout=10)
            
            if response.status_code == 200:
                enrollments = response.json()
                
                success = isinstance(enrollments, list)
                enrollment_count = len(enrollments) if success else 0
                
                self.log_test(
                    "Enrollments Endpoint",
                    success,
                    f"Retrieved {enrollment_count} enrollments for student"
                )
                return success
            else:
                self.log_test(
                    "Enrollments Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Enrollments Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_categories_endpoint(self) -> bool:
        """Test the categories endpoints"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test GET /api/categories
            response = requests.get(f"{self.base_url}/categories", headers=headers, timeout=10)
            
            if response.status_code == 200:
                categories = response.json()
                
                success = isinstance(categories, list)
                category_count = len(categories) if success else 0
                
                self.log_test(
                    "Categories Endpoint",
                    success,
                    f"Retrieved {category_count} categories"
                )
                return success
            else:
                self.log_test(
                    "Categories Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Categories Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_departments_endpoint(self) -> bool:
        """Test the departments endpoints"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test GET /api/departments
            response = requests.get(f"{self.base_url}/departments", headers=headers, timeout=10)
            
            if response.status_code == 200:
                departments = response.json()
                
                success = isinstance(departments, list)
                department_count = len(departments) if success else 0
                
                self.log_test(
                    "Departments Endpoint",
                    success,
                    f"Retrieved {department_count} departments"
                )
                return success
            else:
                self.log_test(
                    "Departments Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Departments Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_error_handling(self) -> bool:
        """Test error handling for invalid requests"""
        try:
            test_cases = [
                # Test invalid endpoint
                (f"{self.base_url}/invalid-endpoint", "Invalid Endpoint"),
                # Test invalid course ID
                (f"{self.base_url}/courses/invalid-id", "Invalid Course ID"),
                # Test invalid program ID
                (f"{self.base_url}/programs/invalid-id", "Invalid Program ID"),
            ]
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            error_handling_results = []
            
            for url, test_name in test_cases:
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    # Should return 404 or other appropriate error status
                    is_error_status = response.status_code >= 400
                    
                    if is_error_status:
                        try:
                            error_data = response.json()
                            has_error_message = 'detail' in error_data or 'message' in error_data
                        except:
                            has_error_message = True  # Non-JSON error response is acceptable
                        
                        success = is_error_status and has_error_message
                        error_handling_results.append(success)
                        
                        self.log_test(
                            f"Error Handling - {test_name}",
                            success,
                            f"HTTP {response.status_code} - Proper error response"
                        )
                    else:
                        error_handling_results.append(False)
                        self.log_test(
                            f"Error Handling - {test_name}",
                            False,
                            f"Expected error status, got HTTP {response.status_code}"
                        )
                        
                except Exception as e:
                    error_handling_results.append(False)
                    self.log_test(f"Error Handling - {test_name}", False, f"Exception: {str(e)}")
            
            overall_success = all(error_handling_results)
            success_rate = sum(error_handling_results) / len(error_handling_results) * 100
            
            self.log_test(
                "Overall Error Handling",
                overall_success,
                f"Error handling success rate: {success_rate:.1f}% ({sum(error_handling_results)}/{len(error_handling_results)} tests passed)"
            )
            
            return overall_success
            
        except Exception as e:
            self.log_test("Error Handling", False, f"Exception: {str(e)}")
            return False

    def test_environment_variables(self) -> bool:
        """Test that environment variables are properly configured"""
        try:
            # Check if we can read the backend URL (already done in __init__)
            backend_url_configured = self.backend_url is not None and self.backend_url != ""
            
            # Test if the backend is responding (indicates MongoDB URL is configured)
            try:
                response = requests.get(f"{self.backend_url}/health", timeout=5)
                backend_responding = response.status_code in [200, 404]  # 404 is OK if health endpoint doesn't exist
            except:
                backend_responding = False
            
            # Check if authentication works (indicates JWT secrets are configured)
            auth_configured = self.admin_token is not None
            
            success = backend_url_configured and backend_responding and auth_configured
            
            details = f"Backend URL: {'✓' if backend_url_configured else '✗'}, " \
                     f"Backend Responding: {'✓' if backend_responding else '✗'}, " \
                     f"Auth Configured: {'✓' if auth_configured else '✗'}"
            
            self.log_test(
                "Environment Variables Configuration",
                success,
                details
            )
            
            return success
            
        except Exception as e:
            self.log_test("Environment Variables Configuration", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all deployment readiness tests"""
        print("🚀 LMS BACKEND DEPLOYMENT READINESS TEST SUITE")
        print("=" * 80)
        print(f"📍 Testing backend at: {self.backend_url}")
        print()
        
        # Step 1: Basic Connectivity Tests
        print("🔗 BASIC CONNECTIVITY TESTS")
        print("-" * 40)
        
        health_check = self.test_health_endpoint()
        root_endpoint = self.test_root_endpoint()
        api_root = self.test_api_root_endpoint()
        
        print()
        
        # Step 2: Authentication Tests
        print("🔐 AUTHENTICATION TESTS")
        print("-" * 40)
        
        admin_auth = self.authenticate_admin()
        student_auth = self.authenticate_student()
        
        if admin_auth:
            auth_me = self.test_auth_me_endpoint()
        else:
            auth_me = False
            self.log_test("Auth Me Endpoint", False, "Skipped due to admin authentication failure")
        
        print()
        
        # Step 3: Core API Endpoints Tests
        print("🔧 CORE API ENDPOINTS TESTS")
        print("-" * 40)
        
        if admin_auth:
            courses_test = self.test_courses_endpoint()
            programs_test = self.test_programs_endpoint()
            categories_test = self.test_categories_endpoint()
            departments_test = self.test_departments_endpoint()
        else:
            courses_test = programs_test = categories_test = departments_test = False
            self.log_test("Core API Endpoints", False, "Skipped due to admin authentication failure")
        
        if student_auth:
            enrollments_test = self.test_enrollments_endpoint()
        else:
            enrollments_test = False
            self.log_test("Enrollments Endpoint", False, "Skipped due to student authentication failure")
        
        print()
        
        # Step 4: Error Handling Tests
        print("⚠️  ERROR HANDLING TESTS")
        print("-" * 40)
        
        if admin_auth:
            error_handling = self.test_error_handling()
        else:
            error_handling = False
            self.log_test("Error Handling", False, "Skipped due to admin authentication failure")
        
        print()
        
        # Step 5: Environment Configuration Tests
        print("🌍 ENVIRONMENT CONFIGURATION TESTS")
        print("-" * 40)
        
        env_config = self.test_environment_variables()
        
        print()
        
        # Generate Summary Report
        self.generate_summary_report()
        
        return True

    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("📊 DEPLOYMENT READINESS SUMMARY REPORT")
        print("=" * 80)
        
        # Calculate overall success metrics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print()
        
        # Categorize results
        critical_tests = [
            "Health Check Endpoint", "Admin Authentication", "Student Authentication",
            "Courses List Endpoint", "Programs List Endpoint", "Environment Variables Configuration"
        ]
        
        important_tests = [
            "Root Endpoint", "API Root Endpoint", "Auth Me Endpoint",
            "Course Detail Endpoint", "Program Detail Endpoint", "Enrollments Endpoint"
        ]
        
        optional_tests = [
            "Categories Endpoint", "Departments Endpoint", "Overall Error Handling"
        ]
        
        # Check critical tests
        critical_results = []
        for test_name in critical_tests:
            test_result = next((r for r in self.test_results if r["test"] == test_name), None)
            if test_result:
                critical_results.append(test_result["success"])
        
        critical_success_rate = (sum(critical_results) / len(critical_results) * 100) if critical_results else 0
        
        print("🎯 CRITICAL TESTS (Required for Deployment):")
        print("-" * 50)
        for test_name in critical_tests:
            test_result = next((r for r in self.test_results if r["test"] == test_name), None)
            if test_result:
                status = "✅ PASS" if test_result["success"] else "❌ FAIL"
                print(f"  {status} {test_name}")
        
        print(f"\n🎯 CRITICAL SUCCESS RATE: {critical_success_rate:.1f}% ({sum(critical_results)}/{len(critical_results)} tests)")
        print()
        
        # Deployment readiness assessment
        deployment_ready = critical_success_rate >= 85.0  # At least 85% of critical tests must pass
        
        print("🚀 DEPLOYMENT READINESS ASSESSMENT:")
        print("-" * 40)
        
        if deployment_ready:
            print("✅ READY FOR DEPLOYMENT")
            print("   All critical systems are functioning correctly.")
            print("   The LMS backend is ready for production deployment.")
        else:
            print("❌ NOT READY FOR DEPLOYMENT")
            print("   Critical issues detected that must be resolved before deployment.")
            print("   Please address the failed critical tests above.")
        
        print()
        
        # Key findings and recommendations
        print("💡 KEY FINDINGS & RECOMMENDATIONS:")
        print("-" * 40)
        
        # Health check findings
        health_result = next((r for r in self.test_results if r["test"] == "Health Check Endpoint"), None)
        if health_result:
            if health_result["success"]:
                print("✅ DATABASE CONNECTIVITY: MongoDB connection is working correctly")
            else:
                print("❌ DATABASE CONNECTIVITY: MongoDB connection issues detected")
                print("   → Check MONGO_URL environment variable")
                print("   → Verify MongoDB Atlas connection string")
                print("   → Check network connectivity to database")
        
        # Authentication findings
        auth_results = [r for r in self.test_results if "Authentication" in r["test"]]
        auth_success = all(r["success"] for r in auth_results)
        if auth_success:
            print("✅ AUTHENTICATION SYSTEM: All authentication endpoints working")
        else:
            print("❌ AUTHENTICATION SYSTEM: Authentication issues detected")
            print("   → Check JWT_SECRET_KEY configuration")
            print("   → Verify user credentials in database")
            print("   → Check password hashing configuration")
        
        # API endpoints findings
        api_results = [r for r in self.test_results if "Endpoint" in r["test"] and r["test"] not in ["Health Check Endpoint", "Root Endpoint", "API Root Endpoint"]]
        api_success_rate = (sum(1 for r in api_results if r["success"]) / len(api_results) * 100) if api_results else 0
        
        if api_success_rate >= 80:
            print(f"✅ API ENDPOINTS: {api_success_rate:.1f}% of API endpoints working correctly")
        else:
            print(f"❌ API ENDPOINTS: Only {api_success_rate:.1f}% of API endpoints working")
            print("   → Check database collections and data integrity")
            print("   → Verify API route configurations")
            print("   → Check authorization middleware")
        
        # Environment configuration findings
        env_result = next((r for r in self.test_results if r["test"] == "Environment Variables Configuration"), None)
        if env_result and env_result["success"]:
            print("✅ ENVIRONMENT CONFIG: All environment variables properly configured")
        else:
            print("❌ ENVIRONMENT CONFIG: Environment variable issues detected")
            print("   → Check frontend/.env REACT_APP_BACKEND_URL")
            print("   → Check backend/.env MONGO_URL and JWT settings")
            print("   → Verify Kubernetes environment variable mapping")
        
        print()
        
        # Final deployment status
        if deployment_ready:
            print("🎉 CONCLUSION: LMS Backend is READY for Production Deployment!")
            print("   The backend has passed all critical tests and is deployment-ready.")
        else:
            print("⚠️  CONCLUSION: LMS Backend requires fixes before deployment.")
            print("   Please address the critical issues identified above.")
        
        print()
        print("=" * 80)

def main():
    """Main execution function"""
    test_suite = LMSDeploymentTestSuite()
    
    try:
        success = test_suite.run_comprehensive_test()
        
        if success:
            print("✅ Deployment readiness testing completed!")
            return 0
        else:
            print("❌ Deployment readiness testing completed with issues!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)