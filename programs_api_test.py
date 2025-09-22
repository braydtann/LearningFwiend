#!/usr/bin/env python3
"""
Focused Programs API Testing for Cloud Migration
Tests the specific scenarios mentioned in the review request
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-bug-fixes.preview.emergentagent.com/api"
TEST_TIMEOUT = 10

class ProgramsAPITester:
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
        else:  # INFO/SKIP
            print(f"ℹ️  {test_name}: {message}")
    
    def authenticate_users(self):
        """Authenticate admin and instructor users as specified in review request"""
        test_users = [
            {"username": "admin", "password": "NewAdmin123!", "role": "admin"},
            {"username": "instructor", "password": "Instructor123!", "role": "instructor"}
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
                    self.auth_tokens[user["role"]] = data['access_token']
                    self.log_result(
                        f"Authentication - {user['username']}", 
                        "PASS", 
                        f"Successfully authenticated {user['username']} ({user['role']})",
                        f"Token obtained, requires_password_change: {data.get('requires_password_change')}"
                    )
                else:
                    self.log_result(
                        f"Authentication - {user['username']}", 
                        "FAIL", 
                        f"Authentication failed with status {response.status_code}",
                        f"Response: {response.text}"
                    )
            except requests.exceptions.RequestException as e:
                self.log_result(
                    f"Authentication - {user['username']}", 
                    "FAIL", 
                    f"Authentication request failed",
                    str(e)
                )
    
    def test_get_all_programs(self):
        """Test GET /api/programs - Retrieve all active programs"""
        if "admin" not in self.auth_tokens:
            self.log_result("GET All Programs", "SKIP", "No admin token available", "")
            return []
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/programs",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                programs = response.json()
                self.log_result(
                    "GET All Programs", 
                    "PASS", 
                    f"Successfully retrieved {len(programs)} active programs",
                    f"Programs: {[p.get('title', 'No title') for p in programs]}"
                )
                return programs
            else:
                self.log_result(
                    "GET All Programs", 
                    "FAIL", 
                    f"Request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result("GET All Programs", "FAIL", "Request failed", str(e))
        return []
    
    def test_create_program(self):
        """Test POST /api/programs - Create new program with specified test data"""
        if "admin" not in self.auth_tokens:
            self.log_result("Create Program", "SKIP", "No admin token available", "")
            return None
        
        # Test data as specified in review request
        test_program_data = {
            "title": "Test Program Migration",
            "description": "Testing cloud migration functionality",
            "courseIds": [],
            "nestedProgramIds": [],
            "duration": "4 weeks"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/programs",
                json=test_program_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                program = response.json()
                
                # Verify backend creates expected fields
                expected_backend_fields = ['id', 'instructorId', 'instructor', 'isActive', 'courseCount', 'created_at', 'updated_at']
                missing_fields = [f for f in expected_backend_fields if f not in program]
                
                if not missing_fields:
                    self.log_result(
                        "Create Program", 
                        "PASS", 
                        f"Successfully created program '{program.get('title')}'",
                        f"Backend fields created: programId={program.get('id')}, instructorId={program.get('instructorId')}, instructor={program.get('instructor')}, isActive={program.get('isActive')}, courseCount={program.get('courseCount')}"
                    )
                    return program
                else:
                    self.log_result(
                        "Create Program", 
                        "FAIL", 
                        "Program created but missing backend fields",
                        f"Missing: {missing_fields}"
                    )
            else:
                self.log_result(
                    "Create Program", 
                    "FAIL", 
                    f"Program creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result("Create Program", "FAIL", "Request failed", str(e))
        return None
    
    def test_get_specific_program(self, program_id):
        """Test GET /api/programs/{program_id} - Get specific program by ID"""
        if "admin" not in self.auth_tokens:
            self.log_result("Get Specific Program", "SKIP", "No admin token available", "")
            return None
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/programs/{program_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                program = response.json()
                self.log_result(
                    "Get Specific Program", 
                    "PASS", 
                    f"Successfully retrieved program '{program.get('title')}'",
                    f"Program ID: {program.get('id')}, Instructor: {program.get('instructor')}"
                )
                return program
            elif response.status_code == 404:
                self.log_result(
                    "Get Specific Program", 
                    "FAIL", 
                    f"Program not found: {program_id}",
                    "Program may have been deleted"
                )
            else:
                self.log_result(
                    "Get Specific Program", 
                    "FAIL", 
                    f"Request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result("Get Specific Program", "FAIL", "Request failed", str(e))
        return None
    
    def test_update_program(self, program_id):
        """Test PUT /api/programs/{program_id} - Update existing program"""
        if "admin" not in self.auth_tokens:
            self.log_result("Update Program", "SKIP", "No admin token available", "")
            return None
        
        update_data = {
            "title": "Test Program Migration - Updated",
            "description": "Testing cloud migration functionality - Updated via API",
            "courseIds": [],
            "nestedProgramIds": [],
            "duration": "6 weeks"
        }
        
        try:
            response = requests.put(
                f"{BACKEND_URL}/programs/{program_id}",
                json=update_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                program = response.json()
                self.log_result(
                    "Update Program", 
                    "PASS", 
                    f"Successfully updated program '{program.get('title')}'",
                    f"Updated duration: {program.get('duration')}"
                )
                return program
            else:
                self.log_result(
                    "Update Program", 
                    "FAIL", 
                    f"Update failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result("Update Program", "FAIL", "Request failed", str(e))
        return None
    
    def test_delete_program(self, program_id):
        """Test DELETE /api/programs/{program_id} - Delete program"""
        if "admin" not in self.auth_tokens:
            self.log_result("Delete Program", "SKIP", "No admin token available", "")
            return False
        
        try:
            response = requests.delete(
                f"{BACKEND_URL}/programs/{program_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Delete Program", 
                    "PASS", 
                    f"Successfully deleted program {program_id}",
                    f"Message: {data.get('message')}"
                )
                return True
            else:
                self.log_result(
                    "Delete Program", 
                    "FAIL", 
                    f"Delete failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result("Delete Program", "FAIL", "Request failed", str(e))
        return False
    
    def test_instructor_access(self):
        """Test instructor user access to programs"""
        if "instructor" not in self.auth_tokens:
            self.log_result("Instructor Access", "SKIP", "No instructor token available", "")
            return
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/programs",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if response.status_code == 200:
                programs = response.json()
                self.log_result(
                    "Instructor Access", 
                    "PASS", 
                    f"Instructor can access programs API ({len(programs)} programs)",
                    "Instructor permissions working correctly"
                )
            else:
                self.log_result(
                    "Instructor Access", 
                    "FAIL", 
                    f"Instructor access denied with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result("Instructor Access", "FAIL", "Request failed", str(e))
    
    def test_instructor_program_creation(self):
        """Test instructor creating programs"""
        if "instructor" not in self.auth_tokens:
            self.log_result("Instructor Create Program", "SKIP", "No instructor token available", "")
            return None
        
        instructor_program_data = {
            "title": "Instructor Test Program",
            "description": "Program created by instructor for testing",
            "courseIds": [],
            "nestedProgramIds": [],
            "duration": "3 weeks"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/programs",
                json=instructor_program_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 200:
                program = response.json()
                self.log_result(
                    "Instructor Create Program", 
                    "PASS", 
                    f"Instructor successfully created program '{program.get('title')}'",
                    f"Program ID: {program.get('id')}"
                )
                return program
            else:
                self.log_result(
                    "Instructor Create Program", 
                    "FAIL", 
                    f"Instructor program creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result("Instructor Create Program", "FAIL", "Request failed", str(e))
        return None
    
    def test_error_scenarios(self):
        """Test error handling scenarios"""
        if "admin" not in self.auth_tokens:
            self.log_result("Error Scenarios", "SKIP", "No admin token available", "")
            return
        
        # Test 1: Invalid program ID access
        try:
            response = requests.get(
                f"{BACKEND_URL}/programs/invalid-program-id",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 404:
                self.log_result(
                    "Error - Invalid Program ID", 
                    "PASS", 
                    "Correctly returned 404 for invalid program ID",
                    "Error handling working"
                )
            else:
                self.log_result(
                    "Error - Invalid Program ID", 
                    "FAIL", 
                    f"Expected 404, got {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result("Error - Invalid Program ID", "FAIL", "Request failed", str(e))
        
        # Test 2: Missing required fields
        try:
            invalid_data = {"description": "Missing title"}
            response = requests.post(
                f"{BACKEND_URL}/programs",
                json=invalid_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 422:
                self.log_result(
                    "Error - Missing Required Fields", 
                    "PASS", 
                    "Correctly rejected program with missing title",
                    "Validation working"
                )
            else:
                self.log_result(
                    "Error - Missing Required Fields", 
                    "FAIL", 
                    f"Expected 422, got {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result("Error - Missing Required Fields", "FAIL", "Request failed", str(e))
    
    def test_data_structure(self, program):
        """Test that program uses correct data structure (title instead of name)"""
        if not program:
            self.log_result("Data Structure", "SKIP", "No program data available", "")
            return
        
        # Check for 'title' field (not 'name')
        if 'title' in program and 'name' not in program:
            self.log_result(
                "Data Structure - Title Field", 
                "PASS", 
                "Program correctly uses 'title' instead of 'name'",
                f"Title: {program.get('title')}"
            )
        else:
            self.log_result(
                "Data Structure - Title Field", 
                "FAIL", 
                "Program data structure issue",
                f"Has title: {'title' in program}, Has name: {'name' in program}"
            )
        
        # Check backend-created fields
        backend_fields = ['id', 'instructorId', 'instructor', 'isActive', 'courseCount', 'created_at', 'updated_at']
        missing_fields = [f for f in backend_fields if f not in program]
        
        if not missing_fields:
            self.log_result(
                "Data Structure - Backend Fields", 
                "PASS", 
                "All backend fields present",
                f"Fields: {', '.join(backend_fields)}"
            )
        else:
            self.log_result(
                "Data Structure - Backend Fields", 
                "FAIL", 
                "Missing backend fields",
                f"Missing: {missing_fields}"
            )
    
    def run_programs_api_tests(self):
        """Run all Programs API tests as specified in review request"""
        print("🚀 Starting Programs API Testing for Cloud Migration")
        print("=" * 60)
        
        # Step 1: Authenticate users (admin/NewAdmin123!, instructor/Instructor123!)
        print("\n🔐 AUTHENTICATION")
        self.authenticate_users()
        
        if not self.auth_tokens:
            print("❌ No authentication tokens available. Cannot proceed with tests.")
            return self.generate_summary()
        
        # Step 2: Test GET /api/programs - Retrieve all active programs
        print("\n📚 PROGRAMS API ENDPOINTS")
        programs = self.test_get_all_programs()
        
        # Step 3: Test POST /api/programs - Create new program with backend data structure
        created_program = self.test_create_program()
        
        # Step 4: Test GET /api/programs/{program_id} - Get specific program by ID
        if created_program:
            retrieved_program = self.test_get_specific_program(created_program['id'])
            
            # Step 5: Test PUT /api/programs/{program_id} - Update existing program
            updated_program = self.test_update_program(created_program['id'])
            
            # Step 6: Test data structure
            self.test_data_structure(created_program)
        
        # Step 7: Test instructor access and functions
        print("\n👨‍🏫 INSTRUCTOR TESTING")
        self.test_instructor_access()
        instructor_program = self.test_instructor_program_creation()
        
        # Step 8: Test error handling
        print("\n⚠️  ERROR HANDLING")
        self.test_error_scenarios()
        
        # Step 9: Clean up - DELETE programs
        print("\n🗑️  CLEANUP")
        if created_program:
            self.test_delete_program(created_program['id'])
        if instructor_program:
            self.test_delete_program(instructor_program['id'])
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 PROGRAMS API TESTING SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        total_tests = self.passed + self.failed
        if total_tests > 0:
            success_rate = (self.passed / total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        else:
            print("📈 Success Rate: No tests run")
        
        if self.failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['message']}")
        
        return {
            'total_tests': total_tests,
            'passed': self.passed,
            'failed': self.failed,
            'success_rate': success_rate if total_tests > 0 else 0,
            'results': self.results
        }

if __name__ == "__main__":
    tester = ProgramsAPITester()
    summary = tester.run_programs_api_tests()
    
    # Exit with appropriate code
    sys.exit(0 if summary['failed'] == 0 else 1)