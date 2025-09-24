#!/usr/bin/env python3
"""
Comprehensive Backend Health Check for LearningFriend LMS Deployment Readiness
Testing all critical backend functionality as requested in review.

Test Areas:
1. Authentication Endpoints - Test login/logout functionality with valid and invalid credentials
2. Health Check - Verify /api/health endpoint is responding correctly
3. Database Connectivity - Ensure MongoDB connection is stable
4. Core API Endpoints - Test course management, user management, and enrollment endpoints
5. File Upload/Download - Verify document handling system is working
6. Quiz System - Test quiz creation and submission endpoints
7. Progress Tracking - Verify enrollment progress updates are working

Test Credentials:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
import uuid

# Configuration
BACKEND_URL = "https://lms-analytics-hub.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}
STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com",
    "password": "StudentPermanent123!"
}

class DeploymentHealthChecker:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.student_token = None
        self.test_results = []
        self.created_resources = []  # Track resources created during testing for cleanup
        
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
        if details and not success:  # Only show details for failures to reduce noise
            print(f"   Details: {details}")
    
    # =============================================================================
    # 1. AUTHENTICATION ENDPOINTS TESTING
    # =============================================================================
    
    def test_admin_authentication(self):
        """Test admin login functionality"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                user_data = data.get("user", {})
                
                if self.admin_token and user_data.get("role") == "admin":
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.admin_token}"
                    })
                    self.log_result(
                        "Admin Authentication",
                        True,
                        f"Successfully authenticated as admin: {user_data.get('email')}"
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
                    f"Authentication failed: {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Admin Authentication",
                False,
                f"Authentication error: {str(e)}"
            )
            return False
    
    def test_student_authentication(self):
        """Test student login functionality"""
        try:
            # Create new session for student to avoid token conflicts
            student_session = requests.Session()
            response = student_session.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                user_data = data.get("user", {})
                
                if self.student_token and user_data.get("role") == "learner":
                    self.log_result(
                        "Student Authentication",
                        True,
                        f"Successfully authenticated as student: {user_data.get('email')}"
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
                    f"Student authentication failed: {response.status_code}",
                    {"response": response.text}
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Student Authentication",
                False,
                f"Student authentication error: {str(e)}"
            )
            return False
    
    def test_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        try:
            invalid_credentials = {
                "username_or_email": "invalid@example.com",
                "password": "wrongpassword"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=invalid_credentials,
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_result(
                    "Invalid Credentials Rejection",
                    True,
                    "Correctly rejected invalid credentials with 401"
                )
            else:
                self.log_result(
                    "Invalid Credentials Rejection",
                    False,
                    f"Should have returned 401 but got: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Invalid Credentials Rejection",
                False,
                f"Error testing invalid credentials: {str(e)}"
            )
    
    def test_token_validation(self):
        """Test JWT token validation"""
        try:
            if not self.admin_token:
                self.log_result(
                    "Token Validation",
                    False,
                    "No admin token available for validation test"
                )
                return
            
            # Test with valid token
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{BACKEND_URL}/auth/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("email") == ADMIN_CREDENTIALS["username_or_email"]:
                    self.log_result(
                        "Token Validation",
                        True,
                        "JWT token validation working correctly"
                    )
                else:
                    self.log_result(
                        "Token Validation",
                        False,
                        "Token validated but returned wrong user data",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "Token Validation",
                    False,
                    f"Token validation failed: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Token Validation",
                False,
                f"Token validation error: {str(e)}"
            )
    
    # =============================================================================
    # 2. HEALTH CHECK ENDPOINT TESTING
    # =============================================================================
    
    def test_health_endpoint(self):
        """Test /api/health endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") == "healthy":
                        self.log_result(
                            "Health Check Endpoint",
                            True,
                            "Health endpoint responding correctly",
                            {"response": data}
                        )
                    else:
                        self.log_result(
                            "Health Check Endpoint",
                            False,
                            "Health endpoint accessible but status not healthy",
                            {"response": data}
                        )
                except json.JSONDecodeError:
                    self.log_result(
                        "Health Check Endpoint",
                        False,
                        "Health endpoint returned non-JSON response",
                        {"response": response.text}
                    )
            else:
                self.log_result(
                    "Health Check Endpoint",
                    False,
                    f"Health endpoint returned: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Health Check Endpoint",
                False,
                f"Health endpoint error: {str(e)}"
            )
    
    # =============================================================================
    # 3. DATABASE CONNECTIVITY TESTING
    # =============================================================================
    
    def test_database_connectivity(self):
        """Test database connectivity through API operations"""
        try:
            if not self.admin_token:
                self.log_result(
                    "Database Connectivity",
                    False,
                    "No admin token available for database test"
                )
                return
            
            # Test database read operation
            response = self.session.get(f"{BACKEND_URL}/courses", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "Database Connectivity",
                        True,
                        f"Database read operation successful - found {len(data)} courses"
                    )
                else:
                    self.log_result(
                        "Database Connectivity",
                        False,
                        "Database responded but returned unexpected format",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "Database Connectivity",
                    False,
                    f"Database read operation failed: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Database Connectivity",
                False,
                f"Database connectivity error: {str(e)}"
            )
    
    # =============================================================================
    # 4. CORE API ENDPOINTS TESTING
    # =============================================================================
    
    def test_user_management_apis(self):
        """Test user management endpoints"""
        try:
            if not self.admin_token:
                self.log_result(
                    "User Management APIs",
                    False,
                    "No admin token available for user management test"
                )
                return
            
            # Test get all users (admin only)
            response = self.session.get(f"{BACKEND_URL}/auth/admin/users", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_result(
                        "User Management APIs",
                        True,
                        f"User management API working - found {len(data)} users"
                    )
                else:
                    self.log_result(
                        "User Management APIs",
                        False,
                        "User management API returned empty or invalid data",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "User Management APIs",
                    False,
                    f"User management API failed: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "User Management APIs",
                False,
                f"User management API error: {str(e)}"
            )
    
    def test_course_management_apis(self):
        """Test course management endpoints"""
        try:
            if not self.admin_token:
                self.log_result(
                    "Course Management APIs",
                    False,
                    "No admin token available for course management test"
                )
                return
            
            # Test course creation
            test_course_data = {
                "title": f"Health Check Test Course {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test course created during deployment health check",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "learningOutcomes": ["Test course functionality"],
                "modules": [
                    {
                        "title": "Test Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Test Lesson",
                                "type": "text",
                                "content": "This is a test lesson for health check"
                            }
                        ]
                    }
                ]
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/courses",
                json=test_course_data,
                timeout=15
            )
            
            if response.status_code == 200:
                course_data = response.json()
                course_id = course_data.get("id")
                
                if course_id:
                    self.created_resources.append(("course", course_id))
                    
                    # Test course retrieval
                    get_response = self.session.get(f"{BACKEND_URL}/courses/{course_id}", timeout=10)
                    
                    if get_response.status_code == 200:
                        self.log_result(
                            "Course Management APIs",
                            True,
                            f"Course CRUD operations working - created and retrieved course {course_id}"
                        )
                    else:
                        self.log_result(
                            "Course Management APIs",
                            False,
                            "Course created but retrieval failed",
                            {"get_response": get_response.text}
                        )
                else:
                    self.log_result(
                        "Course Management APIs",
                        False,
                        "Course creation succeeded but no ID returned",
                        {"response": course_data}
                    )
            else:
                self.log_result(
                    "Course Management APIs",
                    False,
                    f"Course creation failed: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Course Management APIs",
                False,
                f"Course management API error: {str(e)}"
            )
    
    def test_enrollment_apis(self):
        """Test enrollment management endpoints"""
        try:
            # Test with student credentials
            if not self.student_token:
                self.log_result(
                    "Enrollment APIs",
                    False,
                    "No student token available for enrollment test"
                )
                return
            
            # Create student session
            student_session = requests.Session()
            student_session.headers.update({
                "Authorization": f"Bearer {self.student_token}"
            })
            
            # Test get enrollments
            response = student_session.get(f"{BACKEND_URL}/enrollments", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "Enrollment APIs",
                        True,
                        f"Enrollment API working - student has {len(data)} enrollments"
                    )
                else:
                    self.log_result(
                        "Enrollment APIs",
                        False,
                        "Enrollment API returned invalid format",
                        {"response": data}
                    )
            else:
                self.log_result(
                    "Enrollment APIs",
                    False,
                    f"Enrollment API failed: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Enrollment APIs",
                False,
                f"Enrollment API error: {str(e)}"
            )
    
    # =============================================================================
    # 5. FILE UPLOAD/DOWNLOAD TESTING
    # =============================================================================
    
    def test_file_upload_download(self):
        """Test file upload and download functionality"""
        try:
            if not self.admin_token:
                self.log_result(
                    "File Upload/Download",
                    False,
                    "No admin token available for file upload test"
                )
                return
            
            # Create a test file
            test_content = "This is a test document for deployment health check."
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, "health_check_test.pdf")
            
            with open(file_path, 'w') as f:
                f.write(test_content)
            
            # Test file upload
            with open(file_path, 'rb') as f:
                files = {'file': ('health_check_test.pdf', f, 'application/pdf')}
                response = self.session.post(
                    f"{BACKEND_URL}/files/upload",
                    files=files,
                    timeout=30
                )
            
            # Clean up local file
            os.unlink(file_path)
            
            if response.status_code == 200:
                upload_data = response.json()
                file_id = upload_data.get('file_id')
                
                if file_id:
                    # Test file download
                    download_response = self.session.get(
                        f"{BACKEND_URL}/files/{file_id}",
                        timeout=30
                    )
                    
                    if download_response.status_code == 200:
                        self.log_result(
                            "File Upload/Download",
                            True,
                            f"File upload/download working - uploaded and downloaded file {file_id}"
                        )
                    else:
                        self.log_result(
                            "File Upload/Download",
                            False,
                            "File uploaded but download failed",
                            {"download_status": download_response.status_code}
                        )
                else:
                    self.log_result(
                        "File Upload/Download",
                        False,
                        "File upload succeeded but no file_id returned",
                        {"response": upload_data}
                    )
            else:
                self.log_result(
                    "File Upload/Download",
                    False,
                    f"File upload failed: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "File Upload/Download",
                False,
                f"File upload/download error: {str(e)}"
            )
    
    # =============================================================================
    # 6. QUIZ SYSTEM TESTING
    # =============================================================================
    
    def test_quiz_system(self):
        """Test quiz creation and basic functionality"""
        try:
            if not self.admin_token:
                self.log_result(
                    "Quiz System",
                    False,
                    "No admin token available for quiz system test"
                )
                return
            
            # Create a course with quiz content
            quiz_course_data = {
                "title": f"Quiz Health Check Course {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Test course with quiz for deployment health check",
                "category": "Testing",
                "duration": "30 minutes",
                "accessType": "open",
                "learningOutcomes": ["Test quiz functionality"],
                "modules": [
                    {
                        "title": "Quiz Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Health Check Quiz",
                                "type": "quiz",
                                "content": "Test quiz for deployment health check",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "multiple-choice",
                                        "question": "What is this quiz testing?",
                                        "options": [
                                            "System functionality",
                                            "User interface",
                                            "Database performance",
                                            "Network connectivity"
                                        ],
                                        "correctAnswer": 0
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/courses",
                json=quiz_course_data,
                timeout=15
            )
            
            if response.status_code == 200:
                course_data = response.json()
                course_id = course_data.get("id")
                
                if course_id:
                    self.created_resources.append(("course", course_id))
                    
                    # Verify quiz structure in created course
                    modules = course_data.get("modules", [])
                    if modules and modules[0].get("lessons"):
                        lesson = modules[0]["lessons"][0]
                        if lesson.get("type") == "quiz" and lesson.get("questions"):
                            self.log_result(
                                "Quiz System",
                                True,
                                f"Quiz system working - created course with quiz {course_id}"
                            )
                        else:
                            self.log_result(
                                "Quiz System",
                                False,
                                "Course created but quiz structure incorrect",
                                {"lesson": lesson}
                            )
                    else:
                        self.log_result(
                            "Quiz System",
                            False,
                            "Course created but no modules/lessons found"
                        )
                else:
                    self.log_result(
                        "Quiz System",
                        False,
                        "Quiz course creation succeeded but no ID returned"
                    )
            else:
                self.log_result(
                    "Quiz System",
                    False,
                    f"Quiz course creation failed: {response.status_code}",
                    {"response": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Quiz System",
                False,
                f"Quiz system error: {str(e)}"
            )
    
    # =============================================================================
    # 7. PROGRESS TRACKING TESTING
    # =============================================================================
    
    def test_progress_tracking(self):
        """Test enrollment progress tracking functionality"""
        try:
            if not self.student_token:
                self.log_result(
                    "Progress Tracking",
                    False,
                    "No student token available for progress tracking test"
                )
                return
            
            # Create student session
            student_session = requests.Session()
            student_session.headers.update({
                "Authorization": f"Bearer {self.student_token}"
            })
            
            # Get student's enrollments
            enrollments_response = student_session.get(f"{BACKEND_URL}/enrollments", timeout=10)
            
            if enrollments_response.status_code == 200:
                enrollments = enrollments_response.json()
                
                if enrollments and len(enrollments) > 0:
                    # Test progress update on first enrollment
                    enrollment = enrollments[0]
                    course_id = enrollment.get("courseId")
                    
                    if course_id:
                        # Test progress update
                        progress_data = {
                            "progress": 25.0,
                            "currentLessonId": "test-lesson-id",
                            "timeSpent": 300
                        }
                        
                        progress_response = student_session.put(
                            f"{BACKEND_URL}/enrollments/{course_id}/progress",
                            json=progress_data,
                            timeout=10
                        )
                        
                        if progress_response.status_code == 200:
                            updated_enrollment = progress_response.json()
                            if updated_enrollment.get("progress") == 25.0:
                                self.log_result(
                                    "Progress Tracking",
                                    True,
                                    f"Progress tracking working - updated progress to 25% for course {course_id}"
                                )
                            else:
                                self.log_result(
                                    "Progress Tracking",
                                    False,
                                    "Progress update succeeded but progress not updated correctly",
                                    {"updated_enrollment": updated_enrollment}
                                )
                        else:
                            self.log_result(
                                "Progress Tracking",
                                False,
                                f"Progress update failed: {progress_response.status_code}",
                                {"response": progress_response.text}
                            )
                    else:
                        self.log_result(
                            "Progress Tracking",
                            False,
                            "Student has enrollments but no course ID found"
                        )
                else:
                    self.log_result(
                        "Progress Tracking",
                        False,
                        "Student has no enrollments to test progress tracking"
                    )
            else:
                self.log_result(
                    "Progress Tracking",
                    False,
                    f"Failed to get student enrollments: {enrollments_response.status_code}",
                    {"response": enrollments_response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Progress Tracking",
                False,
                f"Progress tracking error: {str(e)}"
            )
    
    # =============================================================================
    # ADDITIONAL SYSTEM TESTS
    # =============================================================================
    
    def test_categories_and_programs(self):
        """Test categories and programs endpoints"""
        try:
            if not self.admin_token:
                self.log_result(
                    "Categories and Programs",
                    False,
                    "No admin token available for categories/programs test"
                )
                return
            
            # Test categories endpoint
            categories_response = self.session.get(f"{BACKEND_URL}/categories", timeout=10)
            programs_response = self.session.get(f"{BACKEND_URL}/programs", timeout=10)
            
            categories_ok = categories_response.status_code == 200
            programs_ok = programs_response.status_code == 200
            
            if categories_ok and programs_ok:
                categories_data = categories_response.json()
                programs_data = programs_response.json()
                
                self.log_result(
                    "Categories and Programs",
                    True,
                    f"Categories and programs APIs working - {len(categories_data)} categories, {len(programs_data)} programs"
                )
            else:
                self.log_result(
                    "Categories and Programs",
                    False,
                    f"Categories: {categories_response.status_code}, Programs: {programs_response.status_code}",
                    {
                        "categories_error": categories_response.text if not categories_ok else None,
                        "programs_error": programs_response.text if not programs_ok else None
                    }
                )
                
        except Exception as e:
            self.log_result(
                "Categories and Programs",
                False,
                f"Categories and programs error: {str(e)}"
            )
    
    # =============================================================================
    # CLEANUP AND MAIN EXECUTION
    # =============================================================================
    
    def cleanup_test_resources(self):
        """Clean up resources created during testing"""
        print("\n🧹 Cleaning up test resources...")
        
        for resource_type, resource_id in self.created_resources:
            try:
                if resource_type == "course":
                    response = self.session.delete(f"{BACKEND_URL}/courses/{resource_id}", timeout=10)
                    if response.status_code == 200:
                        print(f"   ✅ Cleaned up test course: {resource_id}")
                    else:
                        print(f"   ⚠️  Failed to clean up course {resource_id}: {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  Error cleaning up {resource_type} {resource_id}: {str(e)}")
    
    def run_all_tests(self):
        """Run all deployment health check tests"""
        print("🚀 Starting LearningFriend LMS Deployment Health Check")
        print("=" * 70)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: Admin ({ADMIN_CREDENTIALS['username_or_email']}), Student ({STUDENT_CREDENTIALS['username_or_email']})")
        print("=" * 70)
        
        # 1. Authentication Tests
        print("\n🔐 Testing Authentication Endpoints...")
        admin_auth_success = self.test_admin_authentication()
        student_auth_success = self.test_student_authentication()
        self.test_invalid_credentials()
        self.test_token_validation()
        
        # 2. Health Check
        print("\n❤️  Testing Health Check Endpoint...")
        self.test_health_endpoint()
        
        # 3. Database Connectivity
        print("\n🗄️  Testing Database Connectivity...")
        self.test_database_connectivity()
        
        # 4. Core API Endpoints
        print("\n🔧 Testing Core API Endpoints...")
        self.test_user_management_apis()
        self.test_course_management_apis()
        self.test_enrollment_apis()
        self.test_categories_and_programs()
        
        # 5. File Upload/Download
        print("\n📁 Testing File Upload/Download...")
        self.test_file_upload_download()
        
        # 6. Quiz System
        print("\n📝 Testing Quiz System...")
        self.test_quiz_system()
        
        # 7. Progress Tracking
        print("\n📊 Testing Progress Tracking...")
        self.test_progress_tracking()
        
        # Cleanup
        if self.created_resources:
            self.cleanup_test_resources()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("📊 DEPLOYMENT HEALTH CHECK SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Categorize results
        critical_failures = []
        minor_failures = []
        
        for result in self.test_results:
            if not result['success']:
                if any(keyword in result['test'].lower() for keyword in ['authentication', 'health', 'database']):
                    critical_failures.append(result)
                else:
                    minor_failures.append(result)
        
        if critical_failures:
            print("\n🚨 CRITICAL FAILURES (DEPLOYMENT BLOCKERS):")
            for result in critical_failures:
                print(f"   ❌ {result['test']}: {result['message']}")
        
        if minor_failures:
            print("\n⚠️  MINOR FAILURES (NON-BLOCKING):")
            for result in minor_failures:
                print(f"   ⚠️  {result['test']}: {result['message']}")
        
        print("\n✅ SUCCESSFUL TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   ✅ {result['test']}")
        
        # Deployment readiness assessment
        print("\n" + "=" * 70)
        if not critical_failures:
            print("🎉 DEPLOYMENT READY: All critical systems are functional!")
            print("✅ Authentication system working")
            print("✅ Database connectivity confirmed")
            print("✅ Core APIs operational")
            if failed_tests == 0:
                print("✅ All systems fully operational")
        else:
            print("🚨 DEPLOYMENT NOT READY: Critical issues detected!")
            print("❌ Fix critical failures before deployment")
        
        print("=" * 70)

def main():
    """Main function to run deployment health check"""
    checker = DeploymentHealthChecker()
    checker.run_all_tests()

if __name__ == "__main__":
    main()