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
BACKEND_URL = "https://cab231cc-2c4f-4af4-b0fd-87bd9c8e35fc.preview.emergentagent.com/api"
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
    # CRITICAL PASSWORD CHANGE LOOP BUG INVESTIGATION
    # =============================================================================
    
    def test_check_specific_user_status(self):
        """Check the status of user brayden.t@covesmart.com"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Check User Status - brayden.t@covesmart.com", 
                "SKIP", 
                "No admin token available, skipping user status check",
                "Admin login required first"
            )
            return False
        
        try:
            # Get all users to find brayden.t@covesmart.com
            response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                users = response.json()
                target_user = None
                
                for user in users:
                    if user.get('email') == 'brayden.t@covesmart.com':
                        target_user = user
                        break
                
                if target_user:
                    self.log_result(
                        "Check User Status - brayden.t@covesmart.com", 
                        "PASS", 
                        f"Found user brayden.t@covesmart.com",
                        f"User details: ID={target_user.get('id')}, first_login_required={target_user.get('first_login_required')}, is_active={target_user.get('is_active')}, created_at={target_user.get('created_at')}"
                    )
                    return target_user
                else:
                    # User doesn't exist, let's create them for testing
                    self.log_result(
                        "Check User Status - brayden.t@covesmart.com", 
                        "INFO", 
                        "User brayden.t@covesmart.com not found, will create for testing",
                        "Creating test user to reproduce the issue"
                    )
                    
                    # Create the user
                    user_data = {
                        "email": "brayden.t@covesmart.com",
                        "username": "brayden.t",
                        "full_name": "Brayden Test User",
                        "role": "learner",
                        "department": "Testing",
                        "temporary_password": "TempPass123!"
                    }
                    
                    create_response = requests.post(
                        f"{BACKEND_URL}/auth/admin/create-user",
                        json=user_data,
                        timeout=TEST_TIMEOUT,
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                        }
                    )
                    
                    if create_response.status_code == 200:
                        created_user = create_response.json()
                        self.log_result(
                            "Create Test User - brayden.t@covesmart.com", 
                            "PASS", 
                            "Successfully created test user brayden.t@covesmart.com",
                            f"User ID: {created_user.get('id')}, first_login_required: {created_user.get('first_login_required')}"
                        )
                        return created_user
                    else:
                        self.log_result(
                            "Create Test User - brayden.t@covesmart.com", 
                            "FAIL", 
                            f"Failed to create test user with status {create_response.status_code}",
                            f"Response: {create_response.text}"
                        )
            else:
                self.log_result(
                    "Check User Status - brayden.t@covesmart.com", 
                    "FAIL", 
                    f"Failed to get users list with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Check User Status - brayden.t@covesmart.com", 
                "FAIL", 
                "Failed to check user status",
                str(e)
            )
        return False
    
    def test_password_change_workflow_complete(self):
        """Test the complete password change workflow to identify the loop issue"""
        # First, ensure we have the test user
        test_user = self.test_check_specific_user_status()
        if not test_user:
            self.log_result(
                "Password Change Workflow - Complete Test", 
                "FAIL", 
                "Could not find or create test user brayden.t@covesmart.com",
                "Test user required for workflow testing"
            )
            return False
        
        try:
            # Step 1: Login with temporary password
            login_data = {
                "username_or_email": "brayden.t@covesmart.com",
                "password": "TempPass123!"
            }
            
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if login_response.status_code != 200:
                self.log_result(
                    "Password Change Workflow - Login Step", 
                    "FAIL", 
                    f"Failed to login with temporary password, status: {login_response.status_code}",
                    f"Response: {login_response.text}"
                )
                return False
            
            login_data_response = login_response.json()
            user_token = login_data_response.get('access_token')
            requires_password_change = login_data_response.get('requires_password_change')
            
            self.log_result(
                "Password Change Workflow - Login Step", 
                "PASS", 
                f"Successfully logged in, requires_password_change: {requires_password_change}",
                f"Token received, user data: {login_data_response.get('user', {})}"
            )
            
            # Step 2: Change password
            password_change_data = {
                "current_password": "TempPass123!",
                "new_password": "NewPassword123!"
            }
            
            change_response = requests.post(
                f"{BACKEND_URL}/auth/change-password",
                json=password_change_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {user_token}'
                }
            )
            
            if change_response.status_code != 200:
                self.log_result(
                    "Password Change Workflow - Change Step", 
                    "FAIL", 
                    f"Failed to change password, status: {change_response.status_code}",
                    f"Response: {change_response.text}"
                )
                return False
            
            change_data_response = change_response.json()
            self.log_result(
                "Password Change Workflow - Change Step", 
                "PASS", 
                "Successfully changed password",
                f"Response: {change_data_response}"
            )
            
            # Step 3: Login again with new password to check if loop issue exists
            login_data_new = {
                "username_or_email": "brayden.t@covesmart.com",
                "password": "NewPassword123!"
            }
            
            login_response_new = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data_new,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if login_response_new.status_code != 200:
                self.log_result(
                    "Password Change Workflow - Verification Step", 
                    "FAIL", 
                    f"Failed to login with new password, status: {login_response_new.status_code}",
                    f"Response: {login_response_new.text}"
                )
                return False
            
            login_data_new_response = login_response_new.json()
            requires_password_change_after = login_data_new_response.get('requires_password_change')
            
            # This is the critical check - if requires_password_change is still True, we have the loop bug
            if requires_password_change_after:
                self.log_result(
                    "Password Change Workflow - CRITICAL BUG DETECTED", 
                    "FAIL", 
                    "PASSWORD CHANGE LOOP BUG CONFIRMED: User still required to change password after successful change",
                    f"requires_password_change should be False but is: {requires_password_change_after}. User flags not properly updated in database."
                )
                
                # Get user details again to see current database state
                if "admin" in self.auth_tokens:
                    users_response = requests.get(
                        f"{BACKEND_URL}/auth/admin/users",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                    )
                    
                    if users_response.status_code == 200:
                        users = users_response.json()
                        for user in users:
                            if user.get('email') == 'brayden.t@covesmart.com':
                                self.log_result(
                                    "Password Change Workflow - Database State Check", 
                                    "INFO", 
                                    "Current user database state after password change",
                                    f"first_login_required: {user.get('first_login_required')}, is_temporary_password: Not visible in response, last_login: {user.get('last_login')}"
                                )
                                break
                
                return False
            else:
                self.log_result(
                    "Password Change Workflow - Complete Test", 
                    "PASS", 
                    "Password change workflow working correctly - no loop detected",
                    f"requires_password_change correctly set to: {requires_password_change_after}"
                )
                return True
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Password Change Workflow - Complete Test", 
                "FAIL", 
                "Failed to complete password change workflow test",
                str(e)
            )
        return False
    
    def test_password_change_database_update_verification(self):
        """Verify that password change properly updates database flags"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Password Change DB Update Verification", 
                "SKIP", 
                "No admin token available, skipping database verification",
                "Admin login required first"
            )
            return False
        
        try:
            # Create a fresh test user for this specific test
            test_user_data = {
                "email": "password.test@covesmart.com",
                "username": "password.test",
                "full_name": "Password Test User",
                "role": "learner",
                "department": "Testing",
                "temporary_password": "TempTest123!"
            }
            
            create_response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=test_user_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if create_response.status_code not in [200, 400]:  # 400 if user already exists
                self.log_result(
                    "Password Change DB Update - User Creation", 
                    "FAIL", 
                    f"Failed to create test user, status: {create_response.status_code}",
                    f"Response: {create_response.text}"
                )
                return False
            
            # Get user details before password change
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if users_response.status_code != 200:
                self.log_result(
                    "Password Change DB Update - Get Users Before", 
                    "FAIL", 
                    f"Failed to get users, status: {users_response.status_code}",
                    f"Response: {users_response.text}"
                )
                return False
            
            users = users_response.json()
            test_user_before = None
            for user in users:
                if user.get('email') == 'password.test@covesmart.com':
                    test_user_before = user
                    break
            
            if not test_user_before:
                self.log_result(
                    "Password Change DB Update - Find User Before", 
                    "FAIL", 
                    "Could not find test user in database",
                    "User should exist after creation"
                )
                return False
            
            self.log_result(
                "Password Change DB Update - User State Before", 
                "INFO", 
                "User state before password change",
                f"first_login_required: {test_user_before.get('first_login_required')}, created_at: {test_user_before.get('created_at')}"
            )
            
            # Login and change password
            login_data = {
                "username_or_email": "password.test@covesmart.com",
                "password": "TempTest123!"
            }
            
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if login_response.status_code != 200:
                self.log_result(
                    "Password Change DB Update - Login", 
                    "FAIL", 
                    f"Failed to login, status: {login_response.status_code}",
                    f"Response: {login_response.text}"
                )
                return False
            
            user_token = login_response.json().get('access_token')
            
            # Change password
            password_change_data = {
                "current_password": "TempTest123!",
                "new_password": "NewTest123!"
            }
            
            change_response = requests.post(
                f"{BACKEND_URL}/auth/change-password",
                json=password_change_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {user_token}'
                }
            )
            
            if change_response.status_code != 200:
                self.log_result(
                    "Password Change DB Update - Change Password", 
                    "FAIL", 
                    f"Failed to change password, status: {change_response.status_code}",
                    f"Response: {change_response.text}"
                )
                return False
            
            # Get user details after password change
            users_response_after = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if users_response_after.status_code != 200:
                self.log_result(
                    "Password Change DB Update - Get Users After", 
                    "FAIL", 
                    f"Failed to get users after password change, status: {users_response_after.status_code}",
                    f"Response: {users_response_after.text}"
                )
                return False
            
            users_after = users_response_after.json()
            test_user_after = None
            for user in users_after:
                if user.get('email') == 'password.test@covesmart.com':
                    test_user_after = user
                    break
            
            if not test_user_after:
                self.log_result(
                    "Password Change DB Update - Find User After", 
                    "FAIL", 
                    "Could not find test user in database after password change",
                    "User should still exist after password change"
                )
                return False
            
            # Compare before and after states
            first_login_before = test_user_before.get('first_login_required')
            first_login_after = test_user_after.get('first_login_required')
            
            self.log_result(
                "Password Change DB Update - User State After", 
                "INFO", 
                "User state after password change",
                f"first_login_required: {first_login_after} (was: {first_login_before}), last_login: {test_user_after.get('last_login')}"
            )
            
            # Check if the database was properly updated
            if first_login_before == True and first_login_after == False:
                self.log_result(
                    "Password Change DB Update Verification", 
                    "PASS", 
                    "Database properly updated - first_login_required changed from True to False",
                    f"Password change correctly updated user flags in database"
                )
                return True
            elif first_login_before == True and first_login_after == True:
                self.log_result(
                    "Password Change DB Update Verification", 
                    "FAIL", 
                    "CRITICAL BUG: Database NOT updated - first_login_required still True after password change",
                    f"This confirms the password change loop bug - database update is failing"
                )
                return False
            else:
                self.log_result(
                    "Password Change DB Update Verification", 
                    "INFO", 
                    f"Unexpected state: first_login_required before: {first_login_before}, after: {first_login_after}",
                    "May need further investigation"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Password Change DB Update Verification", 
                "FAIL", 
                "Failed to verify database update",
                str(e)
            )
        return False
    
    def test_password_change_loop_bug_reproduction(self):
        """Reproduce the exact password change loop bug scenario"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Password Change Loop Bug Reproduction", 
                "SKIP", 
                "No admin token available, skipping bug reproduction test",
                "Admin login required first"
            )
            return False
        
        try:
            # Step 1: Create a fresh user with temporary password
            bug_test_user_data = {
                "email": "bug.reproduction@covesmart.com",
                "username": "bug.reproduction",
                "full_name": "Bug Reproduction User",
                "role": "learner",
                "department": "Testing",
                "temporary_password": "BugTest123!"
            }
            
            # Delete user if exists first
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if users_response.status_code == 200:
                users = users_response.json()
                for user in users:
                    if user.get('email') == 'bug.reproduction@covesmart.com':
                        # Delete existing user
                        requests.delete(
                            f"{BACKEND_URL}/auth/admin/users/{user['id']}",
                            timeout=TEST_TIMEOUT,
                            headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                        )
                        break
            
            create_response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=bug_test_user_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if create_response.status_code != 200:
                self.log_result(
                    "Password Change Loop Bug - User Creation", 
                    "FAIL", 
                    f"Failed to create bug test user, status: {create_response.status_code}",
                    f"Response: {create_response.text}"
                )
                return False
            
            created_user = create_response.json()
            self.log_result(
                "Password Change Loop Bug - User Creation", 
                "PASS", 
                "Created fresh test user with temporary password",
                f"User: {created_user.get('email')}, first_login_required: {created_user.get('first_login_required')}"
            )
            
            # Step 2: First login with temporary password
            login_data = {
                "username_or_email": "bug.reproduction@covesmart.com",
                "password": "BugTest123!"
            }
            
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if login_response.status_code != 200:
                self.log_result(
                    "Password Change Loop Bug - First Login", 
                    "FAIL", 
                    f"Failed first login with temporary password, status: {login_response.status_code}",
                    f"Response: {login_response.text}"
                )
                return False
            
            login_data_response = login_response.json()
            user_token = login_data_response.get('access_token')
            requires_password_change_initial = login_data_response.get('requires_password_change')
            
            self.log_result(
                "Password Change Loop Bug - First Login", 
                "PASS", 
                f"First login successful, requires_password_change: {requires_password_change_initial}",
                f"This should be True for temporary password users"
            )
            
            if not requires_password_change_initial:
                self.log_result(
                    "Password Change Loop Bug - Initial State Check", 
                    "FAIL", 
                    "User with temporary password does not require password change",
                    "This indicates the temporary password system is not working correctly"
                )
                return False
            
            # Step 3: Change password
            password_change_data = {
                "current_password": "BugTest123!",
                "new_password": "NewBugTest123!"
            }
            
            change_response = requests.post(
                f"{BACKEND_URL}/auth/change-password",
                json=password_change_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {user_token}'
                }
            )
            
            if change_response.status_code != 200:
                self.log_result(
                    "Password Change Loop Bug - Password Change", 
                    "FAIL", 
                    f"Failed to change password, status: {change_response.status_code}",
                    f"Response: {change_response.text}"
                )
                return False
            
            self.log_result(
                "Password Change Loop Bug - Password Change", 
                "PASS", 
                "Password change API call successful",
                f"Response: {change_response.json()}"
            )
            
            # Step 4: CRITICAL TEST - Login again with new password
            login_data_new = {
                "username_or_email": "bug.reproduction@covesmart.com",
                "password": "NewBugTest123!"
            }
            
            login_response_new = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data_new,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if login_response_new.status_code != 200:
                self.log_result(
                    "Password Change Loop Bug - Second Login", 
                    "FAIL", 
                    f"Failed to login with new password, status: {login_response_new.status_code}",
                    f"Response: {login_response_new.text}"
                )
                return False
            
            login_data_new_response = login_response_new.json()
            requires_password_change_after = login_data_new_response.get('requires_password_change')
            
            # THIS IS THE CRITICAL CHECK FOR THE BUG
            if requires_password_change_after:
                self.log_result(
                    "Password Change Loop Bug - CRITICAL BUG CONFIRMED", 
                    "FAIL", 
                    "🚨 PASSWORD CHANGE LOOP BUG DETECTED: User still required to change password after successful change",
                    f"requires_password_change should be False but is: {requires_password_change_after}. This confirms the reported bug where users get stuck in password change loop."
                )
                
                # Get detailed database state for debugging
                users_response_debug = requests.get(
                    f"{BACKEND_URL}/auth/admin/users",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if users_response_debug.status_code == 200:
                    users_debug = users_response_debug.json()
                    for user in users_debug:
                        if user.get('email') == 'bug.reproduction@covesmart.com':
                            self.log_result(
                                "Password Change Loop Bug - Database State Debug", 
                                "INFO", 
                                "Database state after password change shows the issue",
                                f"first_login_required: {user.get('first_login_required')} (should be False), last_login: {user.get('last_login')}, created_at: {user.get('created_at')}"
                            )
                            break
                
                return False
            else:
                self.log_result(
                    "Password Change Loop Bug - Bug Check", 
                    "PASS", 
                    "No password change loop detected - system working correctly",
                    f"requires_password_change correctly set to: {requires_password_change_after}"
                )
                return True
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Password Change Loop Bug Reproduction", 
                "FAIL", 
                "Failed to complete bug reproduction test",
                str(e)
            )
        return False
        """Detailed test of the password change API endpoint"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Password Change API - Detailed Test", 
                "SKIP", 
                "No admin token available, skipping detailed API test",
                "Admin login required first"
            )
            return False
        
        try:
            # Create a test user specifically for API testing
            api_test_user_data = {
                "email": "api.test@covesmart.com",
                "username": "api.test",
                "full_name": "API Test User",
                "role": "learner",
                "department": "Testing",
                "temporary_password": "ApiTest123!"
            }
            
            create_response = requests.post(
                f"{BACKEND_URL}/auth/admin/create-user",
                json=api_test_user_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if create_response.status_code not in [200, 400]:
                self.log_result(
                    "Password Change API - User Creation", 
                    "FAIL", 
                    f"Failed to create API test user, status: {create_response.status_code}",
                    f"Response: {create_response.text}"
                )
                return False
            
            # Login to get user token
            login_data = {
                "username_or_email": "api.test@covesmart.com",
                "password": "ApiTest123!"
            }
            
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if login_response.status_code != 200:
                self.log_result(
                    "Password Change API - Login for Token", 
                    "FAIL", 
                    f"Failed to login for API test, status: {login_response.status_code}",
                    f"Response: {login_response.text}"
                )
                return False
            
            user_token = login_response.json().get('access_token')
            
            # Test the password change API with detailed logging
            password_change_data = {
                "current_password": "ApiTest123!",
                "new_password": "NewApiTest123!"
            }
            
            self.log_result(
                "Password Change API - Request Details", 
                "INFO", 
                "Making password change API request",
                f"Endpoint: POST {BACKEND_URL}/auth/change-password, Data: {password_change_data}"
            )
            
            change_response = requests.post(
                f"{BACKEND_URL}/auth/change-password",
                json=password_change_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {user_token}'
                }
            )
            
            self.log_result(
                "Password Change API - Response Details", 
                "INFO", 
                f"Password change API response: Status {change_response.status_code}",
                f"Response headers: {dict(change_response.headers)}, Response body: {change_response.text}"
            )
            
            if change_response.status_code == 200:
                response_data = change_response.json()
                expected_message = "Password changed successfully"
                
                if response_data.get('message') == expected_message:
                    self.log_result(
                        "Password Change API - Detailed Test", 
                        "PASS", 
                        "Password change API working correctly",
                        f"Received expected success message: {expected_message}"
                    )
                    
                    # Verify the password actually changed by trying to login with new password
                    verify_login_data = {
                        "username_or_email": "api.test@covesmart.com",
                        "password": "NewApiTest123!"
                    }
                    
                    verify_response = requests.post(
                        f"{BACKEND_URL}/auth/login",
                        json=verify_login_data,
                        timeout=TEST_TIMEOUT,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        self.log_result(
                            "Password Change API - Verification Login", 
                            "PASS", 
                            "Successfully logged in with new password",
                            f"requires_password_change: {verify_data.get('requires_password_change')}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Password Change API - Verification Login", 
                            "FAIL", 
                            f"Failed to login with new password, status: {verify_response.status_code}",
                            f"Response: {verify_response.text}"
                        )
                        return False
                else:
                    self.log_result(
                        "Password Change API - Detailed Test", 
                        "FAIL", 
                        f"Unexpected response message",
                        f"Expected: '{expected_message}', Got: '{response_data.get('message')}'"
                    )
                    return False
            else:
                self.log_result(
                    "Password Change API - Detailed Test", 
                    "FAIL", 
                    f"Password change API failed with status {change_response.status_code}",
                    f"Response: {change_response.text}"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Password Change API - Detailed Test", 
                "FAIL", 
                "Failed to complete detailed API test",
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
                "temporary_password": "NewAdmin123!"
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
            {"username": "admin", "password": "NewAdmin123!", "role": "admin"},
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
                "current_password": "NewAdmin123!",
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
    
    # =============================================================================
    # USER DELETION TESTS - NEW FEATURE
    # =============================================================================
    
    def test_user_deletion_successful(self):
        """Test successful user deletion by admin"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "User Deletion - Successful Test", 
                "SKIP", 
                "No admin token available, skipping user deletion test",
                "Admin login required first"
            )
            return False
        
        try:
            # First, get list of users to find a deletable user
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if users_response.status_code != 200:
                self.log_result(
                    "User Deletion - Successful Test", 
                    "FAIL", 
                    "Could not get users list for deletion test",
                    f"Status: {users_response.status_code}"
                )
                return False
            
            users = users_response.json()
            deletable_user = None
            
            # Find a non-admin user to delete (instructor or student)
            for user in users:
                if user.get('role') != 'admin' and user.get('username') in ['instructor', 'student']:
                    deletable_user = user
                    break
            
            if not deletable_user:
                self.log_result(
                    "User Deletion - Successful Test", 
                    "SKIP", 
                    "No suitable user found for deletion test",
                    "Need instructor or student user to delete"
                )
                return False
            
            # Delete the user
            response = requests.delete(
                f"{BACKEND_URL}/auth/admin/users/{deletable_user['id']}",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['message', 'deleted_user']
                
                if all(field in data for field in required_fields):
                    deleted_user_info = data.get('deleted_user', {})
                    if deleted_user_info.get('id') == deletable_user['id']:
                        self.log_result(
                            "User Deletion - Successful Test", 
                            "PASS", 
                            f"Successfully deleted user {deletable_user['username']}",
                            f"Deleted user: {deleted_user_info.get('username')} ({deleted_user_info.get('role')})"
                        )
                        return True
                    else:
                        self.log_result(
                            "User Deletion - Successful Test", 
                            "FAIL", 
                            "Deleted user ID mismatch",
                            f"Expected: {deletable_user['id']}, Got: {deleted_user_info.get('id')}"
                        )
                else:
                    self.log_result(
                        "User Deletion - Successful Test", 
                        "FAIL", 
                        "Deletion response missing required fields",
                        f"Missing: {[f for f in required_fields if f not in data]}"
                    )
            else:
                self.log_result(
                    "User Deletion - Successful Test", 
                    "FAIL", 
                    f"User deletion failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "User Deletion - Successful Test", 
                "FAIL", 
                "Failed to test user deletion",
                str(e)
            )
        return False
    
    def test_admin_cannot_delete_self(self):
        """Test that admin cannot delete their own account"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "User Deletion - Admin Self-Delete Prevention", 
                "SKIP", 
                "No admin token available, skipping self-deletion test",
                "Admin login required first"
            )
            return False
        
        try:
            # Get current admin user info
            me_response = requests.get(
                f"{BACKEND_URL}/auth/me",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if me_response.status_code != 200:
                self.log_result(
                    "User Deletion - Admin Self-Delete Prevention", 
                    "FAIL", 
                    "Could not get current admin user info",
                    f"Status: {me_response.status_code}"
                )
                return False
            
            admin_user = me_response.json()
            admin_id = admin_user.get('id')
            
            # Try to delete self
            response = requests.delete(
                f"{BACKEND_URL}/auth/admin/users/{admin_id}",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 400:
                data = response.json()
                if "Cannot delete your own admin account" in data.get('detail', ''):
                    self.log_result(
                        "User Deletion - Admin Self-Delete Prevention", 
                        "PASS", 
                        "Successfully prevented admin from deleting own account",
                        f"Error message: {data.get('detail')}"
                    )
                    return True
                else:
                    self.log_result(
                        "User Deletion - Admin Self-Delete Prevention", 
                        "FAIL", 
                        "Wrong error message for self-deletion attempt",
                        f"Expected 'Cannot delete your own admin account', got: {data.get('detail')}"
                    )
            else:
                self.log_result(
                    "User Deletion - Admin Self-Delete Prevention", 
                    "FAIL", 
                    f"Expected 400 status for self-deletion, got {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "User Deletion - Admin Self-Delete Prevention", 
                "FAIL", 
                "Failed to test admin self-deletion prevention",
                str(e)
            )
        return False
    
    def test_delete_nonexistent_user(self):
        """Test deleting a non-existent user returns 404"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "User Deletion - Non-existent User", 
                "SKIP", 
                "No admin token available, skipping non-existent user test",
                "Admin login required first"
            )
            return False
        
        try:
            # Use a fake UUID that doesn't exist
            fake_user_id = "00000000-0000-0000-0000-000000000000"
            
            response = requests.delete(
                f"{BACKEND_URL}/auth/admin/users/{fake_user_id}",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 404:
                data = response.json()
                if "User not found" in data.get('detail', ''):
                    self.log_result(
                        "User Deletion - Non-existent User", 
                        "PASS", 
                        "Correctly returned 404 for non-existent user",
                        f"Error message: {data.get('detail')}"
                    )
                    return True
                else:
                    self.log_result(
                        "User Deletion - Non-existent User", 
                        "FAIL", 
                        "Wrong error message for non-existent user",
                        f"Expected 'User not found', got: {data.get('detail')}"
                    )
            else:
                self.log_result(
                    "User Deletion - Non-existent User", 
                    "FAIL", 
                    f"Expected 404 status for non-existent user, got {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "User Deletion - Non-existent User", 
                "FAIL", 
                "Failed to test non-existent user deletion",
                str(e)
            )
        return False
    
    def test_non_admin_cannot_delete_users(self):
        """Test that non-admin users cannot delete users"""
        # Test with instructor token if available
        test_roles = ["instructor", "learner"]
        
        for role in test_roles:
            if role not in self.auth_tokens:
                # Try to login as this role first
                role_username = "instructor" if role == "instructor" else "student"
                role_password = "Instructor123!" if role == "instructor" else "Student123!"
                
                try:
                    login_data = {
                        "username_or_email": role_username,
                        "password": role_password
                    }
                    
                    login_response = requests.post(
                        f"{BACKEND_URL}/auth/login",
                        json=login_data,
                        timeout=TEST_TIMEOUT,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if login_response.status_code == 200:
                        login_data_response = login_response.json()
                        self.auth_tokens[role] = login_data_response['access_token']
                    else:
                        self.log_result(
                            f"User Deletion - Non-Admin Access ({role})", 
                            "SKIP", 
                            f"Could not login as {role} for access control test",
                            f"Login status: {login_response.status_code}"
                        )
                        continue
                except requests.exceptions.RequestException:
                    self.log_result(
                        f"User Deletion - Non-Admin Access ({role})", 
                        "SKIP", 
                        f"Could not login as {role} for access control test",
                        "Login request failed"
                    )
                    continue
            
            # Now test deletion with non-admin token
            try:
                fake_user_id = "00000000-0000-0000-0000-000000000000"
                
                response = requests.delete(
                    f"{BACKEND_URL}/auth/admin/users/{fake_user_id}",
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Authorization': f'Bearer {self.auth_tokens[role]}'
                    }
                )
                
                if response.status_code == 403:
                    data = response.json()
                    if "Admin access required" in data.get('detail', ''):
                        self.log_result(
                            f"User Deletion - Non-Admin Access ({role})", 
                            "PASS", 
                            f"Correctly denied {role} access to user deletion",
                            f"Error message: {data.get('detail')}"
                        )
                    else:
                        self.log_result(
                            f"User Deletion - Non-Admin Access ({role})", 
                            "FAIL", 
                            f"Wrong error message for {role} access denial",
                            f"Expected 'Admin access required', got: {data.get('detail')}"
                        )
                else:
                    self.log_result(
                        f"User Deletion - Non-Admin Access ({role})", 
                        "FAIL", 
                        f"Expected 403 status for {role} access, got {response.status_code}",
                        f"Response: {response.text}"
                    )
            except requests.exceptions.RequestException as e:
                self.log_result(
                    f"User Deletion - Non-Admin Access ({role})", 
                    "FAIL", 
                    f"Failed to test {role} access control",
                    str(e)
                )
    
    def test_last_admin_protection(self):
        """Test that the last admin user cannot be deleted"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "User Deletion - Last Admin Protection", 
                "SKIP", 
                "No admin token available, skipping last admin protection test",
                "Admin login required first"
            )
            return False
        
        try:
            # Get list of all users
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if users_response.status_code != 200:
                self.log_result(
                    "User Deletion - Last Admin Protection", 
                    "FAIL", 
                    "Could not get users list for last admin test",
                    f"Status: {users_response.status_code}"
                )
                return False
            
            users = users_response.json()
            admin_users = [user for user in users if user.get('role') == 'admin']
            
            if len(admin_users) > 1:
                self.log_result(
                    "User Deletion - Last Admin Protection", 
                    "SKIP", 
                    f"Multiple admin users found ({len(admin_users)}), cannot test last admin protection",
                    "Need exactly one admin user for this test"
                )
                return False
            elif len(admin_users) == 0:
                self.log_result(
                    "User Deletion - Last Admin Protection", 
                    "FAIL", 
                    "No admin users found in system",
                    "This should not happen"
                )
                return False
            
            # Try to delete the only admin user
            admin_user = admin_users[0]
            
            response = requests.delete(
                f"{BACKEND_URL}/auth/admin/users/{admin_user['id']}",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 400:
                data = response.json()
                if "Cannot delete the last admin user" in data.get('detail', ''):
                    self.log_result(
                        "User Deletion - Last Admin Protection", 
                        "PASS", 
                        "Successfully prevented deletion of last admin user",
                        f"Error message: {data.get('detail')}"
                    )
                    return True
                else:
                    self.log_result(
                        "User Deletion - Last Admin Protection", 
                        "FAIL", 
                        "Wrong error message for last admin deletion",
                        f"Expected 'Cannot delete the last admin user', got: {data.get('detail')}"
                    )
            else:
                self.log_result(
                    "User Deletion - Last Admin Protection", 
                    "FAIL", 
                    f"Expected 400 status for last admin deletion, got {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "User Deletion - Last Admin Protection", 
                "FAIL", 
                "Failed to test last admin protection",
                str(e)
            )
        return False
    
    def test_invalid_user_id_format(self):
        """Test deletion with invalid user ID format"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "User Deletion - Invalid ID Format", 
                "SKIP", 
                "No admin token available, skipping invalid ID test",
                "Admin login required first"
            )
            return False
        
        invalid_ids = ["invalid-id", "123", "", "not-a-uuid"]
        
        for invalid_id in invalid_ids:
            try:
                response = requests.delete(
                    f"{BACKEND_URL}/auth/admin/users/{invalid_id}",
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                    }
                )
                
                # Should return 404 for invalid ID (user not found)
                if response.status_code == 404:
                    self.log_result(
                        f"User Deletion - Invalid ID ({invalid_id})", 
                        "PASS", 
                        f"Correctly handled invalid user ID: {invalid_id}",
                        f"Returned 404 as expected"
                    )
                else:
                    self.log_result(
                        f"User Deletion - Invalid ID ({invalid_id})", 
                        "INFO", 
                        f"Invalid ID {invalid_id} returned status {response.status_code}",
                        f"Response: {response.text}"
                    )
            except requests.exceptions.RequestException as e:
                self.log_result(
                    f"User Deletion - Invalid ID ({invalid_id})", 
                    "FAIL", 
                    f"Failed to test invalid ID: {invalid_id}",
                    str(e)
                )
    
    def test_unauthorized_deletion_attempt(self):
        """Test deletion without authentication token"""
        try:
            fake_user_id = "00000000-0000-0000-0000-000000000000"
            
            response = requests.delete(
                f"{BACKEND_URL}/auth/admin/users/{fake_user_id}",
                timeout=TEST_TIMEOUT
                # No Authorization header
            )
            
            if response.status_code == 403:
                self.log_result(
                    "User Deletion - Unauthorized Access", 
                    "PASS", 
                    "Correctly denied access without authentication token",
                    f"Returned 403 Forbidden"
                )
                return True
            else:
                self.log_result(
                    "User Deletion - Unauthorized Access", 
                    "FAIL", 
                    f"Expected 403 status for unauthorized access, got {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "User Deletion - Unauthorized Access", 
                "FAIL", 
                "Failed to test unauthorized deletion attempt",
                str(e)
            )
        return False
    
    # =============================================================================
    # PROGRAMS API TESTS - CLOUD MIGRATION TESTING
    # =============================================================================
    
    def test_programs_get_all_active(self):
        """Test GET /api/programs - Retrieve all active programs"""
        if "admin" not in self.auth_tokens and "instructor" not in self.auth_tokens:
            self.log_result(
                "Programs API - GET All Active", 
                "SKIP", 
                "No admin or instructor token available",
                "Authentication required for programs access"
            )
            return False
        
        # Use admin token if available, otherwise instructor
        token = self.auth_tokens.get("admin") or self.auth_tokens.get("instructor")
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/programs",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {token}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "Programs API - GET All Active", 
                        "PASS", 
                        f"Successfully retrieved {len(data)} active programs",
                        f"Programs found: {[p.get('title', 'No title') for p in data[:3]]}"  # Show first 3
                    )
                    return data
                else:
                    self.log_result(
                        "Programs API - GET All Active", 
                        "FAIL", 
                        "Response is not a list",
                        f"Response type: {type(data)}"
                    )
            else:
                self.log_result(
                    "Programs API - GET All Active", 
                    "FAIL", 
                    f"Request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Programs API - GET All Active", 
                "FAIL", 
                "Failed to retrieve active programs",
                str(e)
            )
        return False
    
    def test_programs_create_new(self):
        """Test POST /api/programs - Create new program with backend data structure"""
        if "admin" not in self.auth_tokens and "instructor" not in self.auth_tokens:
            self.log_result(
                "Programs API - POST Create New", 
                "SKIP", 
                "No admin or instructor token available",
                "Authentication required for program creation"
            )
            return False
        
        # Use admin token if available, otherwise instructor
        token = self.auth_tokens.get("admin") or self.auth_tokens.get("instructor")
        
        # Test program data as specified in the review request
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
                    'Authorization': f'Bearer {token}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'title', 'description', 'instructorId', 'instructor', 'isActive', 'courseCount', 'created_at', 'updated_at']
                
                if all(field in data for field in required_fields):
                    # Verify backend creates the expected fields
                    if (data.get('title') == test_program_data['title'] and
                        data.get('description') == test_program_data['description'] and
                        data.get('duration') == test_program_data['duration'] and
                        data.get('isActive') == True and
                        data.get('courseCount') == 0):  # Empty courseIds should result in courseCount 0
                        
                        self.log_result(
                            "Programs API - POST Create New", 
                            "PASS", 
                            f"Successfully created program '{data.get('title')}'",
                            f"Program ID: {data.get('id')}, Instructor: {data.get('instructor')}, Active: {data.get('isActive')}"
                        )
                        return data  # Return created program for further testing
                    else:
                        self.log_result(
                            "Programs API - POST Create New", 
                            "FAIL", 
                            "Created program data doesn't match expected values",
                            f"Expected title: {test_program_data['title']}, Got: {data.get('title')}"
                        )
                else:
                    self.log_result(
                        "Programs API - POST Create New", 
                        "FAIL", 
                        "Response missing required backend fields",
                        f"Missing: {[f for f in required_fields if f not in data]}"
                    )
            else:
                self.log_result(
                    "Programs API - POST Create New", 
                    "FAIL", 
                    f"Program creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Programs API - POST Create New", 
                "FAIL", 
                "Failed to create new program",
                str(e)
            )
        return False
    
    def test_programs_get_specific(self, program_id=None):
        """Test GET /api/programs/{program_id} - Get specific program by ID"""
        if "admin" not in self.auth_tokens and "instructor" not in self.auth_tokens:
            self.log_result(
                "Programs API - GET Specific", 
                "SKIP", 
                "No admin or instructor token available",
                "Authentication required for program access"
            )
            return False
        
        # If no program_id provided, try to get one from existing programs
        if not program_id:
            programs = self.test_programs_get_all_active()
            if programs and len(programs) > 0:
                program_id = programs[0].get('id')
            else:
                self.log_result(
                    "Programs API - GET Specific", 
                    "SKIP", 
                    "No program ID available for testing",
                    "Need existing program or program_id parameter"
                )
                return False
        
        token = self.auth_tokens.get("admin") or self.auth_tokens.get("instructor")
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/programs/{program_id}",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {token}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'title', 'description', 'instructorId', 'instructor', 'isActive', 'courseCount']
                
                if all(field in data for field in required_fields):
                    if data.get('id') == program_id:
                        self.log_result(
                            "Programs API - GET Specific", 
                            "PASS", 
                            f"Successfully retrieved program '{data.get('title')}'",
                            f"Program ID: {program_id}, Instructor: {data.get('instructor')}"
                        )
                        return data
                    else:
                        self.log_result(
                            "Programs API - GET Specific", 
                            "FAIL", 
                            "Retrieved program ID doesn't match requested ID",
                            f"Requested: {program_id}, Got: {data.get('id')}"
                        )
                else:
                    self.log_result(
                        "Programs API - GET Specific", 
                        "FAIL", 
                        "Response missing required fields",
                        f"Missing: {[f for f in required_fields if f not in data]}"
                    )
            elif response.status_code == 404:
                self.log_result(
                    "Programs API - GET Specific", 
                    "PASS", 
                    f"Correctly returned 404 for program ID: {program_id}",
                    "Program not found as expected"
                )
                return True
            else:
                self.log_result(
                    "Programs API - GET Specific", 
                    "FAIL", 
                    f"Request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Programs API - GET Specific", 
                "FAIL", 
                "Failed to retrieve specific program",
                str(e)
            )
        return False
    
    def test_programs_update_existing(self, program_id=None, program_data=None):
        """Test PUT /api/programs/{program_id} - Update existing program"""
        if "admin" not in self.auth_tokens and "instructor" not in self.auth_tokens:
            self.log_result(
                "Programs API - PUT Update", 
                "SKIP", 
                "No admin or instructor token available",
                "Authentication required for program updates"
            )
            return False
        
        # If no program provided, create one first
        if not program_id or not program_data:
            created_program = self.test_programs_create_new()
            if not created_program:
                self.log_result(
                    "Programs API - PUT Update", 
                    "SKIP", 
                    "Could not create test program for update testing",
                    "Program creation failed"
                )
                return False
            program_id = created_program.get('id')
            program_data = created_program
        
        token = self.auth_tokens.get("admin") or self.auth_tokens.get("instructor")
        
        # Update the program data
        updated_data = {
            "title": f"{program_data.get('title', 'Test Program')} - Updated",
            "description": f"{program_data.get('description', 'Test description')} - Updated via API test",
            "courseIds": program_data.get('courseIds', []),
            "nestedProgramIds": program_data.get('nestedProgramIds', []),
            "duration": "6 weeks"  # Changed from original 4 weeks
        }
        
        try:
            response = requests.put(
                f"{BACKEND_URL}/programs/{program_id}",
                json=updated_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if (data.get('title') == updated_data['title'] and
                    data.get('description') == updated_data['description'] and
                    data.get('duration') == updated_data['duration'] and
                    data.get('id') == program_id):
                    
                    self.log_result(
                        "Programs API - PUT Update", 
                        "PASS", 
                        f"Successfully updated program '{data.get('title')}'",
                        f"Updated fields: title, description, duration"
                    )
                    return data
                else:
                    self.log_result(
                        "Programs API - PUT Update", 
                        "FAIL", 
                        "Updated program data doesn't match expected values",
                        f"Expected title: {updated_data['title']}, Got: {data.get('title')}"
                    )
            elif response.status_code == 404:
                self.log_result(
                    "Programs API - PUT Update", 
                    "FAIL", 
                    f"Program not found for update: {program_id}",
                    "Program may have been deleted or doesn't exist"
                )
            elif response.status_code == 403:
                self.log_result(
                    "Programs API - PUT Update", 
                    "FAIL", 
                    "Access denied - user cannot update this program",
                    "User may not own this program"
                )
            else:
                self.log_result(
                    "Programs API - PUT Update", 
                    "FAIL", 
                    f"Program update failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Programs API - PUT Update", 
                "FAIL", 
                "Failed to update program",
                str(e)
            )
        return False
    
    def test_programs_delete(self, program_id=None):
        """Test DELETE /api/programs/{program_id} - Delete program"""
        if "admin" not in self.auth_tokens and "instructor" not in self.auth_tokens:
            self.log_result(
                "Programs API - DELETE", 
                "SKIP", 
                "No admin or instructor token available",
                "Authentication required for program deletion"
            )
            return False
        
        # If no program_id provided, create one first
        if not program_id:
            created_program = self.test_programs_create_new()
            if not created_program:
                self.log_result(
                    "Programs API - DELETE", 
                    "SKIP", 
                    "Could not create test program for deletion testing",
                    "Program creation failed"
                )
                return False
            program_id = created_program.get('id')
        
        token = self.auth_tokens.get("admin") or self.auth_tokens.get("instructor")
        
        try:
            response = requests.delete(
                f"{BACKEND_URL}/programs/{program_id}",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {token}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'successfully deleted' in data['message'].lower():
                    self.log_result(
                        "Programs API - DELETE", 
                        "PASS", 
                        f"Successfully deleted program {program_id}",
                        f"Message: {data.get('message')}"
                    )
                    
                    # Verify program is actually deleted by trying to retrieve it
                    verify_response = requests.get(
                        f"{BACKEND_URL}/programs/{program_id}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {token}'}
                    )
                    
                    if verify_response.status_code == 404:
                        self.log_result(
                            "Programs API - DELETE Verification", 
                            "PASS", 
                            "Confirmed program was deleted (404 on retrieval)",
                            "Deletion verified successfully"
                        )
                        return True
                    else:
                        self.log_result(
                            "Programs API - DELETE Verification", 
                            "FAIL", 
                            f"Program still exists after deletion (status: {verify_response.status_code})",
                            "Deletion may not have been completed"
                        )
                else:
                    self.log_result(
                        "Programs API - DELETE", 
                        "FAIL", 
                        "Unexpected response format for deletion",
                        f"Response: {data}"
                    )
            elif response.status_code == 404:
                self.log_result(
                    "Programs API - DELETE", 
                    "PASS", 
                    f"Program not found for deletion: {program_id}",
                    "404 response is valid for non-existent program"
                )
                return True
            elif response.status_code == 403:
                self.log_result(
                    "Programs API - DELETE", 
                    "FAIL", 
                    "Access denied - user cannot delete this program",
                    "User may not own this program"
                )
            else:
                self.log_result(
                    "Programs API - DELETE", 
                    "FAIL", 
                    f"Program deletion failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Programs API - DELETE", 
                "FAIL", 
                "Failed to delete program",
                str(e)
            )
        return False
    
    def test_programs_authentication_admin_instructor(self):
        """Test authentication with admin and instructor users for programs"""
        test_results = []
        
        # Test with admin user
        if "admin" in self.auth_tokens:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/programs",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if response.status_code == 200:
                    test_results.append(("admin", "PASS", "Admin can access programs API"))
                else:
                    test_results.append(("admin", "FAIL", f"Admin access failed: {response.status_code}"))
            except requests.exceptions.RequestException as e:
                test_results.append(("admin", "FAIL", f"Admin request failed: {str(e)}"))
        
        # Test with instructor user
        if "instructor" in self.auth_tokens:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/programs",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
                )
                
                if response.status_code == 200:
                    test_results.append(("instructor", "PASS", "Instructor can access programs API"))
                else:
                    test_results.append(("instructor", "FAIL", f"Instructor access failed: {response.status_code}"))
            except requests.exceptions.RequestException as e:
                test_results.append(("instructor", "FAIL", f"Instructor request failed: {str(e)}"))
        
        # Test with student user (should be denied)
        if "learner" in self.auth_tokens:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/programs",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["learner"]}'}
                )
                
                if response.status_code == 403:
                    test_results.append(("learner", "PASS", "Student correctly denied access to programs API"))
                else:
                    test_results.append(("learner", "FAIL", f"Student access should be denied, got: {response.status_code}"))
            except requests.exceptions.RequestException as e:
                test_results.append(("learner", "FAIL", f"Student request failed: {str(e)}"))
        
        # Log all results
        for role, status, message in test_results:
            self.log_result(
                f"Programs Authentication - {role.title()}", 
                status, 
                message,
                f"Role-based access control test for {role}"
            )
        
        return len([r for r in test_results if r[1] == "PASS"]) > 0
    
    def test_programs_error_handling(self):
        """Test error handling for invalid requests"""
        if "admin" not in self.auth_tokens and "instructor" not in self.auth_tokens:
            self.log_result(
                "Programs Error Handling", 
                "SKIP", 
                "No admin or instructor token available",
                "Authentication required for error handling tests"
            )
            return False
        
        token = self.auth_tokens.get("admin") or self.auth_tokens.get("instructor")
        error_tests = []
        
        # Test 1: Invalid program ID access
        try:
            response = requests.get(
                f"{BACKEND_URL}/programs/invalid-program-id",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code == 404:
                error_tests.append(("Invalid Program ID", "PASS", "Correctly returned 404 for invalid program ID"))
            else:
                error_tests.append(("Invalid Program ID", "FAIL", f"Expected 404, got {response.status_code}"))
        except requests.exceptions.RequestException as e:
            error_tests.append(("Invalid Program ID", "FAIL", f"Request failed: {str(e)}"))
        
        # Test 2: Missing required fields in program creation
        try:
            invalid_program_data = {
                "description": "Missing title field"
                # Missing required 'title' field
            }
            
            response = requests.post(
                f"{BACKEND_URL}/programs",
                json=invalid_program_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
            )
            
            if response.status_code == 422:  # Validation error
                error_tests.append(("Missing Required Fields", "PASS", "Correctly rejected program with missing title"))
            else:
                error_tests.append(("Missing Required Fields", "FAIL", f"Expected 422, got {response.status_code}"))
        except requests.exceptions.RequestException as e:
            error_tests.append(("Missing Required Fields", "FAIL", f"Request failed: {str(e)}"))
        
        # Test 3: Unauthorized access (no token)
        try:
            response = requests.get(
                f"{BACKEND_URL}/programs",
                timeout=TEST_TIMEOUT
                # No Authorization header
            )
            
            if response.status_code == 403:
                error_tests.append(("Unauthorized Access", "PASS", "Correctly denied access without token"))
            else:
                error_tests.append(("Unauthorized Access", "FAIL", f"Expected 403, got {response.status_code}"))
        except requests.exceptions.RequestException as e:
            error_tests.append(("Unauthorized Access", "FAIL", f"Request failed: {str(e)}"))
        
        # Log all error handling test results
        for test_name, status, message in error_tests:
            self.log_result(
                f"Programs Error Handling - {test_name}", 
                status, 
                message,
                "Error handling validation"
            )
        
        return len([t for t in error_tests if t[1] == "PASS"]) > 0
    
    def test_programs_data_structure_validation(self):
        """Test that programs use correct data structure (title instead of name, etc.)"""
        if "admin" not in self.auth_tokens and "instructor" not in self.auth_tokens:
            self.log_result(
                "Programs Data Structure", 
                "SKIP", 
                "No admin or instructor token available",
                "Authentication required for data structure validation"
            )
            return False
        
        # Create a test program to validate structure
        created_program = self.test_programs_create_new()
        if not created_program:
            self.log_result(
                "Programs Data Structure", 
                "FAIL", 
                "Could not create test program for data structure validation",
                "Program creation failed"
            )
            return False
        
        # Validate the data structure
        expected_fields = {
            'id': str,
            'title': str,  # Should be 'title', not 'name'
            'description': str,
            'instructorId': str,
            'instructor': str,
            'isActive': bool,
            'courseCount': int,
            'created_at': str,
            'updated_at': str,
            'courseIds': list,
            'nestedProgramIds': list
        }
        
        validation_results = []
        
        for field, expected_type in expected_fields.items():
            if field in created_program:
                actual_type = type(created_program[field])
                if field in ['created_at', 'updated_at']:
                    # These should be datetime strings
                    if isinstance(created_program[field], str):
                        validation_results.append((field, "PASS", f"Field present with correct type"))
                    else:
                        validation_results.append((field, "FAIL", f"Expected string datetime, got {actual_type}"))
                elif actual_type == expected_type:
                    validation_results.append((field, "PASS", f"Field present with correct type"))
                else:
                    validation_results.append((field, "FAIL", f"Expected {expected_type}, got {actual_type}"))
            else:
                validation_results.append((field, "FAIL", f"Required field missing"))
        
        # Check that 'name' field is NOT present (should be 'title')
        if 'name' in created_program:
            validation_results.append(("name_field_check", "FAIL", "Program still uses 'name' field instead of 'title'"))
        else:
            validation_results.append(("name_field_check", "PASS", "Program correctly uses 'title' field instead of 'name'"))
        
        # Log all validation results
        passed_validations = 0
        for field, status, message in validation_results:
            self.log_result(
                f"Programs Data Structure - {field}", 
                status, 
                message,
                f"Field validation for {field}"
            )
            if status == "PASS":
                passed_validations += 1
        
        # Clean up test program
        if created_program.get('id'):
            self.test_programs_delete(created_program['id'])
        
        return passed_validations > len(validation_results) * 0.8  # 80% pass rate
    
    # =============================================================================
    # COURSE MANAGEMENT API TESTS - CRITICAL FOR COURSEDETAIL FIX
    # =============================================================================
    
    def test_course_creation_api(self):
        """Test POST /api/courses - Create new course with proper authentication"""
        if "admin" not in self.auth_tokens and "instructor" not in self.auth_tokens:
            self.log_result(
                "Course API - POST Create Course", 
                "SKIP", 
                "No admin or instructor token available",
                "Authentication required for course creation"
            )
            return False
        
        # Use instructor token if available, otherwise admin
        token = self.auth_tokens.get("instructor") or self.auth_tokens.get("admin")
        role = "instructor" if "instructor" in self.auth_tokens else "admin"
        
        # Test course data with realistic content
        test_course_data = {
            "title": "Advanced Web Development",
            "description": "Learn modern web development with React, Node.js, and MongoDB",
            "category": "Technology",
            "duration": "8 weeks",
            "thumbnailUrl": "https://example.com/thumbnail.jpg",
            "accessType": "open",
            "modules": [
                {
                    "title": "Introduction to React",
                    "lessons": [
                        {
                            "id": "lesson-1",
                            "title": "React Basics",
                            "type": "video",
                            "content": "https://youtube.com/watch?v=example"
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=test_course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'title', 'description', 'category', 'instructorId', 'instructor', 'status', 'enrolledStudents', 'rating', 'created_at', 'updated_at']
                
                if all(field in data for field in required_fields):
                    # Verify course data structure and UUIDs
                    if (data.get('title') == test_course_data['title'] and
                        data.get('description') == test_course_data['description'] and
                        data.get('category') == test_course_data['category'] and
                        data.get('status') == 'published' and
                        data.get('enrolledStudents') == 0 and
                        isinstance(data.get('id'), str) and len(data.get('id')) > 10):  # UUID check
                        
                        self.log_result(
                            "Course API - POST Create Course", 
                            "PASS", 
                            f"Successfully created course '{data.get('title')}' with UUID",
                            f"Course ID: {data.get('id')}, Instructor: {data.get('instructor')}, Status: {data.get('status')}"
                        )
                        return data  # Return created course for further testing
                    else:
                        self.log_result(
                            "Course API - POST Create Course", 
                            "FAIL", 
                            "Created course data doesn't match expected values",
                            f"Expected title: {test_course_data['title']}, Got: {data.get('title')}"
                        )
                else:
                    self.log_result(
                        "Course API - POST Create Course", 
                        "FAIL", 
                        "Response missing required backend fields",
                        f"Missing: {[f for f in required_fields if f not in data]}"
                    )
            elif response.status_code == 403:
                self.log_result(
                    "Course API - POST Create Course", 
                    "FAIL", 
                    f"Access denied for {role} role - course creation should be allowed",
                    f"Response: {response.text}"
                )
            else:
                self.log_result(
                    "Course API - POST Create Course", 
                    "FAIL", 
                    f"Course creation failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course API - POST Create Course", 
                "FAIL", 
                "Failed to create new course",
                str(e)
            )
        return False
    
    def test_get_all_courses_api(self):
        """Test GET /api/courses - Get all published courses"""
        if "admin" not in self.auth_tokens and "instructor" not in self.auth_tokens:
            self.log_result(
                "Course API - GET All Courses", 
                "SKIP", 
                "No authentication token available",
                "Authentication required for course access"
            )
            return False
        
        # Use any available token
        token = self.auth_tokens.get("admin") or self.auth_tokens.get("instructor") or self.auth_tokens.get("learner")
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {token}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "Course API - GET All Courses", 
                        "PASS", 
                        f"Successfully retrieved {len(data)} published courses",
                        f"Courses found: {[c.get('title', 'No title') for c in data[:3]]}"  # Show first 3
                    )
                    return data
                else:
                    self.log_result(
                        "Course API - GET All Courses", 
                        "FAIL", 
                        "Response is not a list",
                        f"Response type: {type(data)}"
                    )
            else:
                self.log_result(
                    "Course API - GET All Courses", 
                    "FAIL", 
                    f"Request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course API - GET All Courses", 
                "FAIL", 
                "Failed to retrieve courses",
                str(e)
            )
        return False
    
    def test_get_course_by_id_api(self, course_id=None):
        """Test GET /api/courses/{course_id} - CRITICAL for CourseDetail page fix"""
        if "admin" not in self.auth_tokens and "instructor" not in self.auth_tokens:
            self.log_result(
                "Course API - GET Course by ID (CRITICAL)", 
                "SKIP", 
                "No authentication token available",
                "Authentication required for course access"
            )
            return False
        
        # If no course_id provided, try to get one from existing courses
        if not course_id:
            courses = self.test_get_all_courses_api()
            if courses and len(courses) > 0:
                course_id = courses[0].get('id')
            else:
                # Try to create a course first
                created_course = self.test_course_creation_api()
                if created_course:
                    course_id = created_course.get('id')
                else:
                    self.log_result(
                        "Course API - GET Course by ID (CRITICAL)", 
                        "SKIP", 
                        "No course ID available for testing",
                        "Need existing course or successful course creation"
                    )
                    return False
        
        token = self.auth_tokens.get("admin") or self.auth_tokens.get("instructor") or self.auth_tokens.get("learner")
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {token}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'title', 'description', 'category', 'instructorId', 'instructor', 'status', 'modules']
                
                if all(field in data for field in required_fields):
                    # Verify this is the correct course and data structure is consistent
                    if (data.get('id') == course_id and
                        isinstance(data.get('modules'), list) and
                        data.get('status') == 'published'):
                        
                        self.log_result(
                            "Course API - GET Course by ID (CRITICAL)", 
                            "PASS", 
                            f"Successfully retrieved course '{data.get('title')}' by ID",
                            f"Course ID: {course_id}, Modules: {len(data.get('modules', []))}, Status: {data.get('status')}"
                        )
                        return data
                    else:
                        self.log_result(
                            "Course API - GET Course by ID (CRITICAL)", 
                            "FAIL", 
                            "Retrieved course data inconsistent or incorrect ID",
                            f"Expected ID: {course_id}, Got: {data.get('id')}"
                        )
                else:
                    self.log_result(
                        "Course API - GET Course by ID (CRITICAL)", 
                        "FAIL", 
                        "Response missing required fields for CourseDetail page",
                        f"Missing: {[f for f in required_fields if f not in data]}"
                    )
            elif response.status_code == 404:
                self.log_result(
                    "Course API - GET Course by ID (CRITICAL)", 
                    "FAIL", 
                    f"Course not found - this causes 'no course found' in CourseDetail",
                    f"Course ID: {course_id} returned 404"
                )
            else:
                self.log_result(
                    "Course API - GET Course by ID (CRITICAL)", 
                    "FAIL", 
                    f"Request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course API - GET Course by ID (CRITICAL)", 
                "FAIL", 
                "Failed to retrieve course by ID - CourseDetail will fail",
                str(e)
            )
        return False
    
    def test_get_my_courses_api(self):
        """Test GET /api/courses/my-courses - Get courses for instructors"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Course API - GET My Courses (Instructor)", 
                "SKIP", 
                "No instructor token available",
                "Instructor authentication required for my-courses endpoint"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/my-courses",
                timeout=TEST_TIMEOUT,
                headers={
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(
                        "Course API - GET My Courses (Instructor)", 
                        "PASS", 
                        f"Successfully retrieved {len(data)} instructor courses",
                        f"Instructor courses: {[c.get('title', 'No title') for c in data[:3]]}"
                    )
                    return data
                else:
                    self.log_result(
                        "Course API - GET My Courses (Instructor)", 
                        "FAIL", 
                        "Response is not a list",
                        f"Response type: {type(data)}"
                    )
            else:
                self.log_result(
                    "Course API - GET My Courses (Instructor)", 
                    "FAIL", 
                    f"Request failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course API - GET My Courses (Instructor)", 
                "FAIL", 
                "Failed to retrieve instructor courses",
                str(e)
            )
        return False
    
    def test_course_authentication_requirements(self):
        """Test that course endpoints require proper authentication"""
        test_endpoints = [
            ("POST", "/courses", {"title": "Test", "description": "Test", "category": "Test"}),
            ("GET", "/courses", None),
            ("GET", "/courses/test-id", None),
            ("GET", "/courses/my-courses", None)
        ]
        
        for method, endpoint, data in test_endpoints:
            try:
                if method == "POST":
                    response = requests.post(
                        f"{BACKEND_URL}{endpoint}",
                        json=data,
                        timeout=TEST_TIMEOUT,
                        headers={'Content-Type': 'application/json'}
                        # No Authorization header
                    )
                else:
                    response = requests.get(
                        f"{BACKEND_URL}{endpoint}",
                        timeout=TEST_TIMEOUT
                        # No Authorization header
                    )
                
                if response.status_code == 403:
                    self.log_result(
                        f"Course Auth - {method} {endpoint}", 
                        "PASS", 
                        "Correctly requires authentication",
                        f"Returned 403 Forbidden without token"
                    )
                else:
                    self.log_result(
                        f"Course Auth - {method} {endpoint}", 
                        "FAIL", 
                        f"Expected 403 for unauthenticated request, got {response.status_code}",
                        f"Response: {response.text}"
                    )
            except requests.exceptions.RequestException as e:
                self.log_result(
                    f"Course Auth - {method} {endpoint}", 
                    "FAIL", 
                    f"Failed to test authentication for {method} {endpoint}",
                    str(e)
                )
    
    def test_course_error_handling(self):
        """Test error handling for course endpoints"""
        if "admin" not in self.auth_tokens and "instructor" not in self.auth_tokens:
            self.log_result(
                "Course API - Error Handling", 
                "SKIP", 
                "No authentication token available",
                "Authentication required for error handling tests"
            )
            return False
        
        token = self.auth_tokens.get("instructor") or self.auth_tokens.get("admin")
        
        # Test 1: Get non-existent course
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/non-existent-course-id",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code == 404:
                self.log_result(
                    "Course Error - Non-existent Course", 
                    "PASS", 
                    "Correctly returns 404 for non-existent course",
                    "This is the expected behavior for CourseDetail error handling"
                )
            else:
                self.log_result(
                    "Course Error - Non-existent Course", 
                    "FAIL", 
                    f"Expected 404 for non-existent course, got {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Error - Non-existent Course", 
                "FAIL", 
                "Failed to test non-existent course error handling",
                str(e)
            )
        
        # Test 2: Create course with invalid data
        try:
            invalid_course_data = {
                "title": "",  # Empty title should fail validation
                "description": "",
                "category": ""
            }
            
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=invalid_course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
            )
            
            if response.status_code == 422:  # Validation error
                self.log_result(
                    "Course Error - Invalid Data", 
                    "PASS", 
                    "Correctly validates course creation data",
                    "Returns 422 for invalid course data"
                )
            else:
                self.log_result(
                    "Course Error - Invalid Data", 
                    "INFO", 
                    f"Course creation with empty data returned {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Error - Invalid Data", 
                "FAIL", 
                "Failed to test invalid course data handling",
                str(e)
            )
    
    def test_course_data_consistency(self):
        """Test data consistency between course creation and retrieval"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Course Data Consistency", 
                "SKIP", 
                "No instructor token available",
                "Instructor authentication required for consistency test"
            )
            return False
        
        # Create a course
        created_course = self.test_course_creation_api()
        if not created_course:
            self.log_result(
                "Course Data Consistency", 
                "FAIL", 
                "Could not create course for consistency testing",
                "Course creation failed"
            )
            return False
        
        # Retrieve the same course by ID
        retrieved_course = self.test_get_course_by_id_api(created_course.get('id'))
        if not retrieved_course:
            self.log_result(
                "Course Data Consistency", 
                "FAIL", 
                "Could not retrieve created course by ID",
                f"Course ID: {created_course.get('id')}"
            )
            return False
        
        # Compare key fields
        consistency_fields = ['id', 'title', 'description', 'category', 'instructorId', 'instructor', 'status']
        inconsistent_fields = []
        
        for field in consistency_fields:
            if created_course.get(field) != retrieved_course.get(field):
                inconsistent_fields.append(f"{field}: created='{created_course.get(field)}' vs retrieved='{retrieved_course.get(field)}'")
        
        if not inconsistent_fields:
            self.log_result(
                "Course Data Consistency", 
                "PASS", 
                "Course data is consistent between creation and retrieval",
                f"All {len(consistency_fields)} key fields match perfectly"
            )
            return True
        else:
            self.log_result(
                "Course Data Consistency", 
                "FAIL", 
                "Course data inconsistency detected",
                f"Inconsistent fields: {inconsistent_fields}"
            )
            return False
    
    def test_complete_course_workflow(self):
        """Test complete course workflow: create → list → retrieve by ID"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "Complete Course Workflow", 
                "SKIP", 
                "No instructor token available",
                "Instructor authentication required for workflow test"
            )
            return False
        
        workflow_success = True
        
        # Step 1: Create course
        print("   Step 1: Creating course...")
        created_course = self.test_course_creation_api()
        if not created_course:
            workflow_success = False
        
        # Step 2: Verify it appears in course list
        print("   Step 2: Checking course appears in list...")
        all_courses = self.test_get_all_courses_api()
        if all_courses and created_course:
            course_found_in_list = any(c.get('id') == created_course.get('id') for c in all_courses)
            if not course_found_in_list:
                self.log_result(
                    "Workflow - Course in List", 
                    "FAIL", 
                    "Created course not found in course list",
                    f"Course ID: {created_course.get('id')} not in {len(all_courses)} courses"
                )
                workflow_success = False
            else:
                self.log_result(
                    "Workflow - Course in List", 
                    "PASS", 
                    "Created course appears in course list",
                    f"Course found in list of {len(all_courses)} courses"
                )
        else:
            workflow_success = False
        
        # Step 3: Verify it can be retrieved by ID
        print("   Step 3: Retrieving course by ID...")
        if created_course:
            retrieved_course = self.test_get_course_by_id_api(created_course.get('id'))
            if not retrieved_course:
                workflow_success = False
        else:
            workflow_success = False
        
        if workflow_success and created_course:
            self.log_result(
                "Complete Course Workflow", 
                "PASS", 
                "Complete workflow successful: create → list → retrieve by ID",
                f"Course '{created_course.get('title')}' passed all workflow steps"
            )
        else:
            self.log_result(
                "Complete Course Workflow", 
                "FAIL", 
                "Course workflow failed at one or more steps",
                "This will cause issues in CourseDetail page"
            )
        
        return workflow_success
    
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
        
        print("\n" + "=" * 60)
        print("🚨 CRITICAL PASSWORD CHANGE LOOP BUG INVESTIGATION")
        print("=" * 60)
        
        # Critical Test 1: Check specific user status
        self.test_check_specific_user_status()
        
        # Critical Test 2: Complete password change workflow
        self.test_password_change_workflow_complete()
        
        # Critical Test 3: Database update verification
        self.test_password_change_database_update_verification()
        
        # Critical Test 4: Detailed API testing
        self.test_password_change_api_detailed()
        
        # Critical Test 5: Bug reproduction test
        self.test_password_change_loop_bug_reproduction()
        
        print("\n" + "=" * 60)
        print("🗑️  USER DELETION FUNCTIONALITY TESTS")
        print("=" * 60)
        
        # User Deletion Test 1: Successful deletion
        self.test_user_deletion_successful()
        
        # User Deletion Test 2: Admin cannot delete self
        self.test_admin_cannot_delete_self()
        
        # User Deletion Test 3: Delete non-existent user
        self.test_delete_nonexistent_user()
        
        # User Deletion Test 4: Non-admin access control
        self.test_non_admin_cannot_delete_users()
        
        # User Deletion Test 5: Last admin protection
        self.test_last_admin_protection()
        
        # User Deletion Test 6: Invalid user ID format
        self.test_invalid_user_id_format()
        
        # User Deletion Test 7: Unauthorized access
        self.test_unauthorized_deletion_attempt()
        
        print("\n" + "=" * 60)
        print("📚 PROGRAMS API TESTS - CLOUD MIGRATION")
        print("=" * 60)
        
        # Programs API Test 1: Authentication testing
        self.test_programs_authentication_admin_instructor()
        
        # Programs API Test 2: Get all active programs
        self.test_programs_get_all_active()
        
        # Programs API Test 3: Create new program
        created_program = self.test_programs_create_new()
        
        # Programs API Test 4: Get specific program
        if created_program:
            self.test_programs_get_specific(created_program.get('id'))
        else:
            self.test_programs_get_specific()  # Try with existing programs
        
        # Programs API Test 5: Update existing program
        if created_program:
            self.test_programs_update_existing(created_program.get('id'), created_program)
        else:
            self.test_programs_update_existing()  # Create and update
        
        # Programs API Test 6: Delete program
        # Note: We'll create a separate program for deletion to avoid conflicts
        self.test_programs_delete()
        
        # Programs API Test 7: Error handling
        self.test_programs_error_handling()
        
        # Programs API Test 8: Data structure validation
        self.test_programs_data_structure_validation()
        
        print("\n" + "=" * 60)
        print("📚 COURSE MANAGEMENT API TESTS - CRITICAL FOR COURSEDETAIL FIX")
        print("=" * 60)
        
        # Course API Test 1: Authentication requirements
        self.test_course_authentication_requirements()
        
        # Course API Test 2: Create course
        self.test_course_creation_api()
        
        # Course API Test 3: Get all courses
        self.test_get_all_courses_api()
        
        # Course API Test 4: Get course by ID (CRITICAL)
        self.test_get_course_by_id_api()
        
        # Course API Test 5: Get my courses (instructor)
        self.test_get_my_courses_api()
        
        # Course API Test 6: Error handling
        self.test_course_error_handling()
        
        # Course API Test 7: Data consistency
        self.test_course_data_consistency()
        
        # Course API Test 8: Complete workflow
        self.test_complete_course_workflow()
        
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