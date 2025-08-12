#!/usr/bin/env python3
"""
Backend Testing Suite for LearningFwiend LMS Application
Tests FastAPI backend service, API endpoints, and database connectivity
"""

import requests
import json
import os
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://educademy-2.preview.emergentagent.com/api"
TEST_TIMEOUT = 10

class BackendTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}  # Store auth tokens for different users
        
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
    
    def test_backend_health(self):
        """Test if backend service is accessible"""
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=TEST_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == 'Hello World':
                    self.log_result(
                        "Backend Health Check", 
                        "PASS", 
                        "Backend service is running and accessible",
                        f"Response: {data}"
                    )
                    return True
                else:
                    self.log_result(
                        "Backend Health Check", 
                        "FAIL", 
                        "Backend responded but with unexpected message",
                        f"Expected 'Hello World', got: {data}"
                    )
            else:
                self.log_result(
                    "Backend Health Check", 
                    "FAIL", 
                    f"Backend returned status code {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Backend Health Check", 
                "FAIL", 
                "Failed to connect to backend service",
                str(e)
            )
            return False
        return False
    
    def test_status_endpoint_post(self):
        """Test POST /api/status endpoint"""
        try:
            test_data = {
                "client_name": "LearningFwiend_Test_Client"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/status", 
                json=test_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'client_name', 'timestamp']
                
                if all(field in data for field in required_fields):
                    if data['client_name'] == test_data['client_name']:
                        self.log_result(
                            "POST Status Endpoint", 
                            "PASS", 
                            "Successfully created status check entry",
                            f"Created entry with ID: {data.get('id')}"
                        )
                        return data['id']  # Return ID for further testing
                    else:
                        self.log_result(
                            "POST Status Endpoint", 
                            "FAIL", 
                            "Client name mismatch in response",
                            f"Expected: {test_data['client_name']}, Got: {data.get('client_name')}"
                        )
                else:
                    self.log_result(
                        "POST Status Endpoint", 
                        "FAIL", 
                        "Response missing required fields",
                        f"Missing fields: {[f for f in required_fields if f not in data]}"
                    )
            else:
                self.log_result(
                    "POST Status Endpoint", 
                    "FAIL", 
                    f"Request failed with status code {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "POST Status Endpoint", 
                "FAIL", 
                "Failed to make POST request to status endpoint",
                str(e)
            )
        return None
    
    def test_status_endpoint_get(self):
        """Test GET /api/status endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/status", timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check if the entries have required structure
                        sample_entry = data[0]
                        required_fields = ['id', 'client_name', 'timestamp']
                        
                        if all(field in sample_entry for field in required_fields):
                            self.log_result(
                                "GET Status Endpoint", 
                                "PASS", 
                                f"Successfully retrieved {len(data)} status check entries",
                                f"Sample entry structure: {list(sample_entry.keys())}"
                            )
                            return True
                        else:
                            self.log_result(
                                "GET Status Endpoint", 
                                "FAIL", 
                                "Status entries missing required fields",
                                f"Missing fields: {[f for f in required_fields if f not in sample_entry]}"
                            )
                    else:
                        self.log_result(
                            "GET Status Endpoint", 
                            "PASS", 
                            "Successfully retrieved empty status list (no entries yet)",
                            "Empty list response is valid"
                        )
                        return True
                else:
                    self.log_result(
                        "GET Status Endpoint", 
                        "FAIL", 
                        "Response is not a list",
                        f"Response type: {type(data)}, Content: {data}"
                    )
            else:
                self.log_result(
                    "GET Status Endpoint", 
                    "FAIL", 
                    f"Request failed with status code {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "GET Status Endpoint", 
                "FAIL", 
                "Failed to make GET request to status endpoint",
                str(e)
            )
        return False
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        try:
            # Make an OPTIONS request to check CORS headers
            response = requests.options(f"{BACKEND_URL}/", timeout=TEST_TIMEOUT)
            
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers'),
            }
            
            if cors_headers['access-control-allow-origin']:
                self.log_result(
                    "CORS Configuration", 
                    "PASS", 
                    "CORS headers are properly configured",
                    f"CORS headers: {cors_headers}"
                )
                return True
            else:
                self.log_result(
                    "CORS Configuration", 
                    "FAIL", 
                    "CORS headers not found or improperly configured",
                    f"Available headers: {dict(response.headers)}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "CORS Configuration", 
                "FAIL", 
                "Failed to test CORS configuration",
                str(e)
            )
        return False
    
    def test_database_integration(self):
        """Test database integration by creating and retrieving data"""
        try:
            # First, create a test entry
            test_data = {
                "client_name": "Database_Integration_Test"
            }
            
            post_response = requests.post(
                f"{BACKEND_URL}/status", 
                json=test_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if post_response.status_code == 200:
                created_entry = post_response.json()
                created_id = created_entry.get('id')
                
                # Wait a moment for database write
                time.sleep(1)
                
                # Now retrieve all entries and check if our entry exists
                get_response = requests.get(f"{BACKEND_URL}/status", timeout=TEST_TIMEOUT)
                
                if get_response.status_code == 200:
                    all_entries = get_response.json()
                    
                    # Look for our created entry
                    found_entry = None
                    for entry in all_entries:
                        if entry.get('id') == created_id:
                            found_entry = entry
                            break
                    
                    if found_entry:
                        self.log_result(
                            "Database Integration", 
                            "PASS", 
                            "Successfully created and retrieved data from database",
                            f"Created entry with ID {created_id} and successfully retrieved it"
                        )
                        return True
                    else:
                        self.log_result(
                            "Database Integration", 
                            "FAIL", 
                            "Created entry not found in database retrieval",
                            f"Created ID {created_id} not found in {len(all_entries)} entries"
                        )
                else:
                    self.log_result(
                        "Database Integration", 
                        "FAIL", 
                        "Failed to retrieve data after creation",
                        f"GET request failed with status {get_response.status_code}"
                    )
            else:
                self.log_result(
                    "Database Integration", 
                    "FAIL", 
                    "Failed to create test entry in database",
                    f"POST request failed with status {post_response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Database Integration", 
                "FAIL", 
                "Failed to test database integration",
                str(e)
            )
        return False
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        try:
            # Test invalid JSON data
            invalid_response = requests.post(
                f"{BACKEND_URL}/status", 
                json={"invalid_field": "test"},
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            # Should return 422 for validation error
            if invalid_response.status_code == 422:
                self.log_result(
                    "Error Handling", 
                    "PASS", 
                    "Properly handles invalid request data with validation error",
                    f"Returned status 422 for invalid data"
                )
                return True
            else:
                self.log_result(
                    "Error Handling", 
                    "FAIL", 
                    f"Unexpected status code for invalid data: {invalid_response.status_code}",
                    f"Response: {invalid_response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Error Handling", 
                "FAIL", 
                "Failed to test error handling",
                str(e)
            )
        return False
    
    # =============================================================================
    # AUTHENTICATION SYSTEM TESTS
    # =============================================================================
    
    def test_admin_user_creation(self):
        """Test admin user creation endpoint"""
        try:
            # First, we need to create the admin user if it doesn't exist
            admin_data = {
                "email": "admin@learningfwiend.com",
                "username": "admin",
                "full_name": "System Administrator",
                "role": "admin",
                "department": "IT",
                "temporary_password": "Admin123!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=admin_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            # This might fail if admin already exists, which is fine
            if response.status_code in [200, 400]:  # 400 if user already exists
                self.log_result(
                    "Admin User Setup", 
                    "PASS", 
                    "Admin user creation endpoint accessible",
                    f"Status: {response.status_code}"
                )
                return True
            else:
                self.log_result(
                    "Admin User Setup", 
                    "FAIL", 
                    f"Unexpected status code: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin User Setup", 
                "FAIL", 
                "Failed to test admin user creation",
                str(e)
            )
        return False
    
    def test_user_login(self):
        """Test user login with different user types"""
        test_users = [
            {"username": "admin", "password": "Admin123!", "role": "admin"},
            {"username": "instructor", "password": "Instructor123!", "role": "instructor"},
            {"username": "student", "password": "Student123!", "role": "learner"}
        ]
        
        login_success = False
        
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
                    required_fields = ['access_token', 'token_type', 'user', 'requires_password_change']
                    
                    if all(field in data for field in required_fields):
                        # Store token for later tests
                        self.auth_tokens[user["role"]] = data['access_token']
                        
                        self.log_result(
                            f"Login Test ({user['username']})", 
                            "PASS", 
                            f"Successfully logged in {user['username']} with role {user['role']}",
                            f"Token received, requires_password_change: {data.get('requires_password_change')}"
                        )
                        login_success = True
                    else:
                        self.log_result(
                            f"Login Test ({user['username']})", 
                            "FAIL", 
                            "Login response missing required fields",
                            f"Missing: {[f for f in required_fields if f not in data]}"
                        )
                elif response.status_code == 401:
                    # User might not exist yet, try to create them first
                    self.log_result(
                        f"Login Test ({user['username']})", 
                        "INFO", 
                        f"User {user['username']} not found or wrong password",
                        "Will attempt to create user if admin token available"
                    )
                else:
                    self.log_result(
                        f"Login Test ({user['username']})", 
                        "FAIL", 
                        f"Login failed with status {response.status_code}",
                        f"Response: {response.text}"
                    )
            except requests.exceptions.RequestException as e:
                self.log_result(
                    f"Login Test ({user['username']})", 
                    "FAIL", 
                    f"Failed to test login for {user['username']}",
                    str(e)
                )
        
        return login_success
    
    def test_create_test_users(self):
        """Create test users using admin endpoint"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Create Test Users", 
                "SKIP", 
                "No admin token available, skipping user creation",
                "Admin login required first"
            )
            return False
        
        test_users = [
            {
                "email": "instructor@learningfwiend.com",
                "username": "instructor",
                "full_name": "Test Instructor",
                "role": "instructor",
                "department": "Education",
                "temporary_password": "Instructor123!"
            },
            {
                "email": "student@learningfwiend.com",
                "username": "student",
                "full_name": "Test Student",
                "role": "learner",
                "department": "General",
                "temporary_password": "Student123!"
            }
        ]
        
        created_users = 0
        
        for user_data in test_users:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/auth/admin/create-user",
                    json=user_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(
                        f"Create User ({user_data['username']})", 
                        "PASS", 
                        f"Successfully created user {user_data['username']}",
                        f"User ID: {data.get('id')}"
                    )
                    created_users += 1
                elif response.status_code == 400:
                    # User already exists
                    self.log_result(
                        f"Create User ({user_data['username']})", 
                        "INFO", 
                        f"User {user_data['username']} already exists",
                        "This is expected if user was created previously"
                    )
                    created_users += 1  # Count as success since user exists
                else:
                    self.log_result(
                        f"Create User ({user_data['username']})", 
                        "FAIL", 
                        f"Failed to create user with status {response.status_code}",
                        f"Response: {response.text}"
                    )
            except requests.exceptions.RequestException as e:
                self.log_result(
                    f"Create User ({user_data['username']})", 
                    "FAIL", 
                    f"Failed to create user {user_data['username']}",
                    str(e)
                )
        
        return created_users > 0
    
    def test_password_change(self):
        """Test password change functionality"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Password Change Test", 
                "SKIP", 
                "No admin token available, skipping password change test",
                "Admin login required first"
            )
            return False
        
        try:
            password_change_data = {
                "current_password": "Admin123!",
                "new_password": "NewAdmin123!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/change-password",
                json=password_change_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == 'Password changed successfully':
                    self.log_result(
                        "Password Change Test", 
                        "PASS", 
                        "Successfully changed password",
                        "Password change endpoint working correctly"
                    )
                    
                    # Test login with new password
                    login_data = {
                        "username_or_email": "admin",
                        "password": "NewAdmin123!"
                    }
                    
                    login_response = requests.post(
                        f"{BACKEND_URL}/auth/login",
                        json=login_data,
                        timeout=TEST_TIMEOUT,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if login_response.status_code == 200:
                        login_data_response = login_response.json()
                        # Update token
                        self.auth_tokens["admin"] = login_data_response['access_token']
                        
                        self.log_result(
                            "Password Change Verification", 
                            "PASS", 
                            "Successfully logged in with new password",
                            f"requires_password_change: {login_data_response.get('requires_password_change')}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Password Change Verification", 
                            "FAIL", 
                            "Failed to login with new password",
                            f"Status: {login_response.status_code}"
                        )
                else:
                    self.log_result(
                        "Password Change Test", 
                        "FAIL", 
                        "Unexpected response message",
                        f"Response: {data}"
                    )
            else:
                self.log_result(
                    "Password Change Test", 
                    "FAIL", 
                    f"Password change failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Password Change Test", 
                "FAIL", 
                "Failed to test password change",
                str(e)
            )
        return False
    
    def test_admin_get_users(self):
        """Test admin endpoint to get all users"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Admin Get Users Test", 
                "SKIP", 
                "No admin token available, skipping get users test",
                "Admin login required first"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "Admin Get Users Test", 
                        "PASS", 
                        f"Successfully retrieved {len(data)} users",
                        f"Users found: {[user.get('username') for user in data]}"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Get Users Test", 
                        "FAIL", 
                        "Response is not a list",
                        f"Response type: {type(data)}"
                    )
            else:
                self.log_result(
                    "Admin Get Users Test", 
                    "FAIL", 
                    f"Failed to get users with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Get Users Test", 
                "FAIL", 
                "Failed to test get users endpoint",
                str(e)
            )
        return False
    
    def test_get_current_user(self):
        """Test get current user endpoint"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Get Current User Test", 
                "SKIP", 
                "No admin token available, skipping current user test",
                "Admin login required first"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/auth/me",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'email', 'username', 'full_name', 'role']
                
                if all(field in data for field in required_fields):
                    self.log_result(
                        "Get Current User Test", 
                        "PASS", 
                        f"Successfully retrieved current user info for {data.get('username')}",
                        f"Role: {data.get('role')}, Email: {data.get('email')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Get Current User Test", 
                        "FAIL", 
                        "Response missing required fields",
                        f"Missing: {[f for f in required_fields if f not in data]}"
                    )
            else:
                self.log_result(
                    "Get Current User Test", 
                    "FAIL", 
                    f"Failed to get current user with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Get Current User Test", 
                "FAIL", 
                "Failed to test get current user endpoint",
                str(e)
            )
        return False
    
    def test_admin_password_reset(self):
        """Test admin password reset functionality"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Admin Password Reset Test", 
                "SKIP", 
                "No admin token available, skipping password reset test",
                "Admin login required first"
            )
            return False
        
        # First, get list of users to find a user to reset
        try:
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if users_response.status_code != 200:
                self.log_result(
                    "Admin Password Reset Test", 
                    "FAIL", 
                    "Could not get users list for password reset test",
                    f"Status: {users_response.status_code}"
                )
                return False
            
            users = users_response.json()
            test_user = None
            
            # Find a non-admin user to reset password for
            for user in users:
                if user.get('role') != 'admin' and user.get('username') in ['instructor', 'student']:
                    test_user = user
                    break
            
            if not test_user:
                self.log_result(
                    "Admin Password Reset Test", 
                    "SKIP", 
                    "No suitable test user found for password reset",
                    "Need instructor or student user"
                )
                return False
            
            # Reset password
            reset_data = {
                "user_id": test_user['id'],
                "new_temporary_password": "ResetTest123!"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/admin/reset-password",
                json=reset_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['message', 'user_id', 'temporary_password', 'reset_at']
                
                if all(field in data for field in required_fields):
                    self.log_result(
                        "Admin Password Reset Test", 
                        "PASS", 
                        f"Successfully reset password for user {test_user['username']}",
                        f"New temporary password set"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Password Reset Test", 
                        "FAIL", 
                        "Password reset response missing required fields",
                        f"Missing: {[f for f in required_fields if f not in data]}"
                    )
            else:
                self.log_result(
                    "Admin Password Reset Test", 
                    "FAIL", 
                    f"Password reset failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Password Reset Test", 
                "FAIL", 
                "Failed to test admin password reset",
                str(e)
            )
        return False
    
    def test_password_validation(self):
        """Test password validation rules"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Password Validation Test", 
                "SKIP", 
                "No admin token available, skipping password validation test",
                "Admin login required first"
            )
            return False
        
        # Test weak passwords that should fail validation
        weak_passwords = [
            "123",  # Too short
            "password",  # No number or special char
            "Password",  # No number or special char
            "Password123",  # No special char
            "Password!"  # No number
        ]
        
        validation_working = 0
        
        for weak_password in weak_passwords:
            try:
                user_data = {
                    "email": f"test{len(weak_passwords)}@test.com",
                    "username": f"testuser{len(weak_passwords)}",
                    "full_name": "Test User",
                    "role": "learner",
                    "temporary_password": weak_password
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/auth/admin/create-user",
                    json=user_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                    }
                )
                
                if response.status_code == 422:  # Validation error expected
                    validation_working += 1
                    self.log_result(
                        f"Password Validation ({weak_password})", 
                        "PASS", 
                        f"Correctly rejected weak password: {weak_password}",
                        "Validation working as expected"
                    )
                else:
                    self.log_result(
                        f"Password Validation ({weak_password})", 
                        "FAIL", 
                        f"Weak password accepted: {weak_password}",
                        f"Status: {response.status_code}"
                    )
            except requests.exceptions.RequestException as e:
                self.log_result(
                    f"Password Validation ({weak_password})", 
                    "FAIL", 
                    f"Failed to test password validation for: {weak_password}",
                    str(e)
                )
        
        return validation_working > 0
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend Testing Suite for LearningFwiend LMS")
        print("=" * 60)
        
        # Test 1: Backend Health Check
        health_ok = self.test_backend_health()
        
        if not health_ok:
            print("\n❌ Backend service is not accessible. Stopping tests.")
            return self.generate_summary()
        
        # Test 2: CORS Configuration
        self.test_cors_configuration()
        
        # Test 3: POST Status Endpoint
        self.test_status_endpoint_post()
        
        # Test 4: GET Status Endpoint
        self.test_status_endpoint_get()
        
        # Test 5: Database Integration
        self.test_database_integration()
        
        # Test 6: Error Handling
        self.test_error_handling()
        
        print("\n" + "=" * 60)
        print("🔐 AUTHENTICATION SYSTEM TESTS")
        print("=" * 60)
        
        # Authentication Test 1: Setup admin user
        self.test_admin_user_creation()
        
        # Authentication Test 2: User login tests
        self.test_user_login()
        
        # Authentication Test 3: Create test users
        self.test_create_test_users()
        
        # Authentication Test 4: Password change
        self.test_password_change()
        
        # Authentication Test 5: Admin get users
        self.test_admin_get_users()
        
        # Authentication Test 6: Get current user
        self.test_get_current_user()
        
        # Authentication Test 7: Admin password reset
        self.test_admin_password_reset()
        
        # Authentication Test 8: Password validation
        self.test_password_validation()
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 BACKEND TESTING SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%" if (self.passed + self.failed) > 0 else "No tests run")
        
        if self.failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['message']}")
        
        return {
            'total_tests': len(self.results),
            'passed': self.passed,
            'failed': self.failed,
            'success_rate': (self.passed / (self.passed + self.failed) * 100) if (self.passed + self.failed) > 0 else 0,
            'results': self.results
        }

if __name__ == "__main__":
    tester = BackendTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if summary['failed'] == 0 else 1)