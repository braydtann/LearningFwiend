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
BACKEND_URL = "https://e73e9636-5e9a-4a84-96b9-ee88880c778b.preview.emergentagent.com/api"
TEST_TIMEOUT = 10

class BackendTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        
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