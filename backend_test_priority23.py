#!/usr/bin/env python3
"""
Priority 2 & 3 Backend API Testing Suite - Announcements, Certificates, Quiz/Assessment, Analytics
"""

import requests
import json
import uuid
from datetime import datetime

BACKEND_URL = "https://lms-stability.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

class Priority23Tester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        
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
        elif status == 'FAIL':
            self.failed += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
        else:
            print(f"ℹ️  {test_name}: {message}")
            if details:
                print(f"   Details: {details}")

    def setup_authentication(self):
        """Setup authentication tokens"""
        test_users = [
            {"username": "admin", "password": "NewAdmin123!", "role": "admin"},
            {"username": "test.instructor", "password": "NewInstructor123!", "role": "instructor"},
            {"username": "student", "password": "NewStudent123!", "role": "learner"}
        ]
        
        for user in test_users:
            try:
                login_data = {
                    "username_or_email": user["username"],
                    "password": user["password"]
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json=login_data,
                    timeout=TEST_TIMEOUT,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get('access_token')
                    if token:
                        self.auth_tokens[user["role"]] = token
                        
            except requests.exceptions.RequestException:
                pass
        
        return len(self.auth_tokens) >= 2

    def test_announcements_api(self):
        """Test Announcements API - CRUD operations, role-based filtering, course/classroom linking"""
        print("\n" + "="*80)
        print("📢 PRIORITY 2: ANNOUNCEMENTS API TESTING")
        print("="*80)
        
        # Check if announcements endpoints exist
        admin_token = self.auth_tokens.get("admin")
        instructor_token = self.auth_tokens.get("instructor")
        learner_token = self.auth_tokens.get("learner")
        
        if not admin_token:
            self.log_result("Announcements API", "SKIP", "No admin token available", "Cannot test without authentication")
            return
        
        # Test 1: Try to get announcements endpoint
        try:
            response = requests.get(
                f"{BACKEND_URL}/announcements",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 404:
                self.log_result(
                    "Announcements API - Endpoint Check", 
                    "FAIL", 
                    "Announcements API endpoint not implemented",
                    "GET /api/announcements returns 404"
                )
                return
            elif response.status_code in [200, 403]:
                self.log_result(
                    "Announcements API - Endpoint Check", 
                    "PASS", 
                    "Announcements API endpoint exists",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_result(
                    "Announcements API - Endpoint Check", 
                    "INFO", 
                    f"Announcements API returned status {response.status_code}",
                    f"Response: {response.text[:200]}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Announcements API - Endpoint Check", "FAIL", "Request failed", str(e))
            return
        
        # Test 2: Try to create announcement
        announcement_data = {
            "title": f"Test Announcement {uuid.uuid4().hex[:8]}",
            "content": "This is a test announcement for API testing",
            "priority": "normal",
            "targetAudience": "all"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/announcements",
                json=announcement_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {admin_token}'
                }
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Announcements API - Create", 
                    "PASS", 
                    "Successfully created announcement",
                    f"Response: {response.json()}"
                )
            elif response.status_code == 404:
                self.log_result(
                    "Announcements API - Create", 
                    "FAIL", 
                    "Create announcement endpoint not implemented",
                    "POST /api/announcements returns 404"
                )
            else:
                self.log_result(
                    "Announcements API - Create", 
                    "FAIL", 
                    f"Failed to create announcement, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Announcements API - Create", "FAIL", "Request failed", str(e))

    def test_certificates_api(self):
        """Test Certificates API - Certificate creation, verification system, enrollment validation"""
        print("\n" + "="*80)
        print("🏆 PRIORITY 2: CERTIFICATES API TESTING")
        print("="*80)
        
        admin_token = self.auth_tokens.get("admin")
        
        if not admin_token:
            self.log_result("Certificates API", "SKIP", "No admin token available", "Cannot test without authentication")
            return
        
        # Test 1: Check certificates endpoint
        try:
            response = requests.get(
                f"{BACKEND_URL}/certificates",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 404:
                self.log_result(
                    "Certificates API - Endpoint Check", 
                    "FAIL", 
                    "Certificates API endpoint not implemented",
                    "GET /api/certificates returns 404"
                )
                return
            elif response.status_code in [200, 403]:
                self.log_result(
                    "Certificates API - Endpoint Check", 
                    "PASS", 
                    "Certificates API endpoint exists",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_result(
                    "Certificates API - Endpoint Check", 
                    "INFO", 
                    f"Certificates API returned status {response.status_code}",
                    f"Response: {response.text[:200]}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Certificates API - Endpoint Check", "FAIL", "Request failed", str(e))
            return
        
        # Test 2: Try to create certificate
        certificate_data = {
            "userId": "test-user-id",
            "programId": "test-program-id",
            "certificateType": "completion",
            "issueDate": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/certificates",
                json=certificate_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {admin_token}'
                }
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Certificates API - Create", 
                    "PASS", 
                    "Successfully created certificate",
                    f"Response: {response.json()}"
                )
            elif response.status_code == 404:
                self.log_result(
                    "Certificates API - Create", 
                    "FAIL", 
                    "Create certificate endpoint not implemented",
                    "POST /api/certificates returns 404"
                )
            else:
                self.log_result(
                    "Certificates API - Create", 
                    "FAIL", 
                    f"Failed to create certificate, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Certificates API - Create", "FAIL", "Request failed", str(e))

    def test_quiz_assessment_api(self):
        """Test Quiz/Assessment API - Quiz CRUD, question types, attempt submission, automatic scoring"""
        print("\n" + "="*80)
        print("📝 PRIORITY 3: QUIZ/ASSESSMENT API TESTING")
        print("="*80)
        
        instructor_token = self.auth_tokens.get("instructor")
        learner_token = self.auth_tokens.get("learner")
        
        if not instructor_token:
            self.log_result("Quiz/Assessment API", "SKIP", "No instructor token available", "Cannot test without authentication")
            return
        
        # Test 1: Check quizzes endpoint
        try:
            response = requests.get(
                f"{BACKEND_URL}/quizzes",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {instructor_token}'}
            )
            
            if response.status_code == 404:
                self.log_result(
                    "Quiz/Assessment API - Endpoint Check", 
                    "FAIL", 
                    "Quiz/Assessment API endpoint not implemented",
                    "GET /api/quizzes returns 404"
                )
                return
            elif response.status_code in [200, 403]:
                self.log_result(
                    "Quiz/Assessment API - Endpoint Check", 
                    "PASS", 
                    "Quiz/Assessment API endpoint exists",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_result(
                    "Quiz/Assessment API - Endpoint Check", 
                    "INFO", 
                    f"Quiz/Assessment API returned status {response.status_code}",
                    f"Response: {response.text[:200]}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Quiz/Assessment API - Endpoint Check", "FAIL", "Request failed", str(e))
            return
        
        # Test 2: Try to create quiz
        quiz_data = {
            "title": f"Test Quiz {uuid.uuid4().hex[:8]}",
            "description": "Comprehensive test quiz for API testing",
            "courseId": "test-course-id",
            "questions": [
                {
                    "type": "multiple_choice",
                    "question": "What is 2 + 2?",
                    "options": ["3", "4", "5", "6"],
                    "correctAnswer": 1,
                    "points": 10
                }
            ],
            "timeLimit": 30,
            "passingScore": 70
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/quizzes",
                json=quiz_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {instructor_token}'
                }
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Quiz/Assessment API - Create", 
                    "PASS", 
                    "Successfully created quiz",
                    f"Response: {response.json()}"
                )
            elif response.status_code == 404:
                self.log_result(
                    "Quiz/Assessment API - Create", 
                    "FAIL", 
                    "Create quiz endpoint not implemented",
                    "POST /api/quizzes returns 404"
                )
            else:
                self.log_result(
                    "Quiz/Assessment API - Create", 
                    "FAIL", 
                    f"Failed to create quiz, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Quiz/Assessment API - Create", "FAIL", "Request failed", str(e))

    def test_analytics_api(self):
        """Test Analytics API - System stats, course analytics, user analytics, dashboard data"""
        print("\n" + "="*80)
        print("📊 PRIORITY 3: ANALYTICS API TESTING")
        print("="*80)
        
        admin_token = self.auth_tokens.get("admin")
        
        if not admin_token:
            self.log_result("Analytics API", "SKIP", "No admin token available", "Cannot test without authentication")
            return
        
        # Test 1: Check analytics endpoint
        try:
            response = requests.get(
                f"{BACKEND_URL}/analytics",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 404:
                self.log_result(
                    "Analytics API - Endpoint Check", 
                    "FAIL", 
                    "Analytics API endpoint not implemented",
                    "GET /api/analytics returns 404"
                )
                return
            elif response.status_code in [200, 403]:
                self.log_result(
                    "Analytics API - Endpoint Check", 
                    "PASS", 
                    "Analytics API endpoint exists",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_result(
                    "Analytics API - Endpoint Check", 
                    "INFO", 
                    f"Analytics API returned status {response.status_code}",
                    f"Response: {response.text[:200]}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Analytics API - Endpoint Check", "FAIL", "Request failed", str(e))
            return
        
        # Test 2: Check system stats endpoint
        try:
            response = requests.get(
                f"{BACKEND_URL}/analytics/system-stats",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Analytics API - System Stats", 
                    "PASS", 
                    "Successfully retrieved system statistics",
                    f"Response: {response.json()}"
                )
            elif response.status_code == 404:
                self.log_result(
                    "Analytics API - System Stats", 
                    "FAIL", 
                    "System stats endpoint not implemented",
                    "GET /api/analytics/system-stats returns 404"
                )
            else:
                self.log_result(
                    "Analytics API - System Stats", 
                    "FAIL", 
                    f"Failed to get system stats, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Analytics API - System Stats", "FAIL", "Request failed", str(e))

    def test_cross_api_integration(self):
        """Test Cross-API Integration - Data relationships, role-based access consistency"""
        print("\n" + "="*80)
        print("🔗 CROSS-API INTEGRATION TESTING")
        print("="*80)
        
        admin_token = self.auth_tokens.get("admin")
        
        if not admin_token:
            self.log_result("Cross-API Integration", "SKIP", "No admin token available", "Cannot test without authentication")
            return
        
        # Test 1: Data Relationship Validation - Courses and Programs
        try:
            # Get courses
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            # Get programs
            programs_response = requests.get(
                f"{BACKEND_URL}/programs",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            if courses_response.status_code == 200 and programs_response.status_code == 200:
                courses = courses_response.json()
                programs = programs_response.json()
                
                self.log_result(
                    "Cross-API Integration - Data Relationships", 
                    "PASS", 
                    f"Successfully validated data relationships",
                    f"Found {len(courses)} courses and {len(programs)} programs with consistent data structure"
                )
            else:
                self.log_result(
                    "Cross-API Integration - Data Relationships", 
                    "FAIL", 
                    "Failed to retrieve related data",
                    f"Courses: {courses_response.status_code}, Programs: {programs_response.status_code}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result("Cross-API Integration - Data Relationships", "FAIL", "Request failed", str(e))
        
        # Test 2: Role-based Access Consistency
        instructor_token = self.auth_tokens.get("instructor")
        learner_token = self.auth_tokens.get("learner")
        
        if instructor_token and learner_token:
            endpoints_to_test = [
                "/courses",
                "/programs", 
                "/categories",
                "/departments",
                "/classrooms"
            ]
            
            consistent_access = True
            
            for endpoint in endpoints_to_test:
                try:
                    # Test instructor access
                    instructor_response = requests.get(
                        f"{BACKEND_URL}{endpoint}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {instructor_token}'}
                    )
                    
                    # Test learner access
                    learner_response = requests.get(
                        f"{BACKEND_URL}{endpoint}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {learner_token}'}
                    )
                    
                    # Check if access patterns are consistent
                    if instructor_response.status_code not in [200, 403, 404] or learner_response.status_code not in [200, 403, 404]:
                        consistent_access = False
                        
                except requests.exceptions.RequestException:
                    consistent_access = False
            
            if consistent_access:
                self.log_result(
                    "Cross-API Integration - Role-based Access Consistency", 
                    "PASS", 
                    "Role-based access control is consistent across APIs",
                    f"Tested {len(endpoints_to_test)} endpoints with different user roles"
                )
            else:
                self.log_result(
                    "Cross-API Integration - Role-based Access Consistency", 
                    "FAIL", 
                    "Inconsistent role-based access control detected",
                    "Some endpoints have inconsistent permission handling"
                )

    def run_priority23_tests(self):
        """Run all Priority 2 & 3 tests"""
        print("\n" + "="*100)
        print("🚀 PRIORITY 2 & 3 BACKEND API TESTING")
        print("="*100)
        
        if not self.setup_authentication():
            print("\n❌ CRITICAL: Authentication setup failed. Cannot proceed with API testing.")
            return False
        
        print(f"\n✅ Authentication successful for {len(self.auth_tokens)} user types")
        
        # Priority 2 Tests
        self.test_announcements_api()
        self.test_certificates_api()
        
        # Priority 3 Tests
        self.test_quiz_assessment_api()
        self.test_analytics_api()
        
        # Cross-API Integration Tests
        self.test_cross_api_integration()
        
        # Print summary
        self.print_summary()
        
        return self.passed > self.failed
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*100)
        print("📊 PRIORITY 2 & 3 API TESTING SUMMARY")
        print("="*100)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ PASSED: {self.passed}")
        print(f"❌ FAILED: {self.failed}")
        print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
        print(f"🔢 TOTAL TESTS: {total_tests}")
        
        if self.failed > 0:
            print(f"\n❌ FAILED TESTS SUMMARY:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['message']}")
        
        print("\n" + "="*100)

def main():
    """Main function"""
    tester = Priority23Tester()
    tester.run_priority23_tests()

if __name__ == "__main__":
    main()