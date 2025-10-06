#!/usr/bin/env python3
"""
LearningFriend LMS Backend Testing - Program Creation and Final Test Creation Debug
Specifically testing the issues reported in review request:
- Network connection errors (ERR_CONNECTION_RESET, ERR_NAME_NOT_RESOLVED)
- 422 HTTP errors when creating programs with final tests
- Testing the entire workflow of creating a program with final test
- Checking if recent changes to make FinalTestCreate questions field optional are causing validation issues
"""

import requests
import json
import sys
from datetime import datetime
import uuid
import time

# Configuration
BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class ProgramFinalTestDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30  # 30 second timeout
        self.admin_token = None
        self.test_results = []
        self.created_program_id = None
        self.created_final_test_id = None
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_network_connectivity(self):
        """Test 1: Basic network connectivity to backend"""
        try:
            print("🔍 Testing network connectivity...")
            
            # Test basic connectivity
            response = self.session.get(f"{BACKEND_URL}/", timeout=10)
            
            if response.status_code == 200:
                self.log_test("Network Connectivity - Basic", True, f"Backend reachable, status: {response.status_code}")
            else:
                self.log_test("Network Connectivity - Basic", False, f"Unexpected status: {response.status_code}")
                return False
                
            # Test health endpoint if available
            try:
                health_response = self.session.get(f"{BACKEND_URL}/health", timeout=10)
                if health_response.status_code == 200:
                    self.log_test("Network Connectivity - Health Check", True, "Health endpoint accessible")
                else:
                    self.log_test("Network Connectivity - Health Check", False, f"Health endpoint status: {health_response.status_code}")
            except Exception as e:
                self.log_test("Network Connectivity - Health Check", False, f"Health endpoint not available: {str(e)}")
            
            return True
            
        except requests.exceptions.ConnectTimeout:
            self.log_test("Network Connectivity - Basic", False, "Connection timeout - ERR_CONNECTION_RESET equivalent")
            return False
        except requests.exceptions.ConnectionError as e:
            self.log_test("Network Connectivity - Basic", False, f"Connection error - ERR_NAME_NOT_RESOLVED equivalent: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Network Connectivity - Basic", False, f"Network error: {str(e)}")
            return False
    
    def authenticate_admin(self):
        """Test 2: Admin authentication"""
        try:
            print("🔐 Testing admin authentication...")
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                self.log_test("Admin Authentication", True, f"Logged in as {data['user']['full_name']} ({data['user']['role']})")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectTimeout:
            self.log_test("Admin Authentication", False, "Connection timeout during authentication")
            return False
        except requests.exceptions.ConnectionError as e:
            self.log_test("Admin Authentication", False, f"Connection error during authentication: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Authentication exception: {str(e)}")
            return False
    
    def test_program_creation_endpoint(self):
        """Test 3: Program creation endpoint - POST /api/programs"""
        try:
            print("📚 Testing program creation endpoint...")
            
            program_data = {
                "title": f"Debug Test Program {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Program created during debug testing for network connectivity issues",
                "departmentId": None,
                "duration": "8 weeks",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            print(f"    Sending POST request to: {BACKEND_URL}/programs")
            print(f"    Request data: {json.dumps(program_data, indent=2)}")
            
            response = self.session.post(f"{BACKEND_URL}/programs", json=program_data, timeout=20)
            
            print(f"    Response status: {response.status_code}")
            print(f"    Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                program = response.json()
                self.created_program_id = program["id"]
                self.log_test("Program Creation Endpoint", True, 
                            f"Created program: {program['title']} (ID: {program['id']})")
                print(f"    Created program response: {json.dumps(program, indent=2, default=str)}")
                return program
            elif response.status_code == 422:
                self.log_test("Program Creation Endpoint", False, 
                            f"422 Validation Error: {response.text}")
                print(f"    422 Error details: {response.text}")
                return None
            else:
                self.log_test("Program Creation Endpoint", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except requests.exceptions.ConnectTimeout:
            self.log_test("Program Creation Endpoint", False, "Connection timeout - ERR_CONNECTION_RESET")
            return None
        except requests.exceptions.ConnectionError as e:
            self.log_test("Program Creation Endpoint", False, f"Connection error - ERR_NAME_NOT_RESOLVED: {str(e)}")
            return None
        except Exception as e:
            self.log_test("Program Creation Endpoint", False, f"Exception: {str(e)}")
            return None
    
    def test_final_test_creation_endpoint(self):
        """Test 4: Final test creation endpoint - POST /api/final-tests"""
        try:
            print("🎯 Testing final test creation endpoint...")
            
            if not self.created_program_id:
                self.log_test("Final Test Creation Endpoint", False, "No program ID available for testing")
                return None
            
            # Test with optional questions field (recent change mentioned in review)
            final_test_data = {
                "title": f"Debug Final Test {datetime.now().strftime('%H%M%S')}",
                "description": "Final test created during debug testing",
                "programId": self.created_program_id,
                # Intentionally omitting questions field to test if it's truly optional
                "timeLimit": 60,
                "maxAttempts": 3,
                "passingScore": 75.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": False
            }
            
            print(f"    Sending POST request to: {BACKEND_URL}/final-tests")
            print(f"    Request data: {json.dumps(final_test_data, indent=2)}")
            
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=final_test_data, timeout=20)
            
            print(f"    Response status: {response.status_code}")
            print(f"    Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                final_test = response.json()
                self.created_final_test_id = final_test["id"]
                self.log_test("Final Test Creation Endpoint", True, 
                            f"Created final test: {final_test['title']} (ID: {final_test['id']})")
                print(f"    Created final test response: {json.dumps(final_test, indent=2, default=str)}")
                return final_test
            elif response.status_code == 422:
                self.log_test("Final Test Creation Endpoint", False, 
                            f"422 Validation Error: {response.text}")
                print(f"    422 Error details: {response.text}")
                
                # Try again with explicit empty questions array
                print("    Retrying with explicit empty questions array...")
                final_test_data["questions"] = []
                
                retry_response = self.session.post(f"{BACKEND_URL}/final-tests", json=final_test_data, timeout=20)
                
                if retry_response.status_code == 200:
                    final_test = retry_response.json()
                    self.created_final_test_id = final_test["id"]
                    self.log_test("Final Test Creation Endpoint (Retry)", True, 
                                f"Created final test with explicit empty questions: {final_test['title']}")
                    return final_test
                else:
                    self.log_test("Final Test Creation Endpoint (Retry)", False, 
                                f"Retry failed - Status: {retry_response.status_code}, Response: {retry_response.text}")
                    return None
            else:
                self.log_test("Final Test Creation Endpoint", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except requests.exceptions.ConnectTimeout:
            self.log_test("Final Test Creation Endpoint", False, "Connection timeout - ERR_CONNECTION_RESET")
            return None
        except requests.exceptions.ConnectionError as e:
            self.log_test("Final Test Creation Endpoint", False, f"Connection error - ERR_NAME_NOT_RESOLVED: {str(e)}")
            return None
        except Exception as e:
            self.log_test("Final Test Creation Endpoint", False, f"Exception: {str(e)}")
            return None
    
    def test_programs_js_workflow(self):
        """Test 5: Complete workflow as done in Programs.js"""
        try:
            print("🔄 Testing complete Programs.js workflow...")
            
            # Step 1: Create a program (simulating Programs.js behavior)
            workflow_program_data = {
                "title": f"Workflow Test Program {datetime.now().strftime('%H%M%S')}",
                "description": "Testing the complete workflow as done in Programs.js",
                "departmentId": None,
                "duration": "6 weeks",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            print("    Step 1: Creating program...")
            program_response = self.session.post(f"{BACKEND_URL}/programs", json=workflow_program_data, timeout=20)
            
            if program_response.status_code != 200:
                self.log_test("Programs.js Workflow - Program Creation", False, 
                            f"Program creation failed: {program_response.status_code} - {program_response.text}")
                return False
            
            workflow_program = program_response.json()
            workflow_program_id = workflow_program["id"]
            print(f"    Program created successfully: {workflow_program_id}")
            
            # Step 2: Create final test for the program (simulating Programs.js behavior)
            workflow_final_test_data = {
                "title": f"Workflow Final Test {datetime.now().strftime('%H%M%S')}",
                "description": "Final test created as part of Programs.js workflow",
                "programId": workflow_program_id,
                "questions": [],  # Start with empty questions as per recent changes
                "timeLimit": 90,
                "maxAttempts": 2,
                "passingScore": 80.0,
                "shuffleQuestions": True,
                "showResults": True,
                "isPublished": False
            }
            
            print("    Step 2: Creating final test...")
            final_test_response = self.session.post(f"{BACKEND_URL}/final-tests", json=workflow_final_test_data, timeout=20)
            
            if final_test_response.status_code != 200:
                self.log_test("Programs.js Workflow - Final Test Creation", False, 
                            f"Final test creation failed: {final_test_response.status_code} - {final_test_response.text}")
                return False
            
            workflow_final_test = final_test_response.json()
            workflow_final_test_id = workflow_final_test["id"]
            print(f"    Final test created successfully: {workflow_final_test_id}")
            
            # Step 3: Verify the association (simulating Programs.js verification)
            print("    Step 3: Verifying program-final test association...")
            
            # Get the program and verify it exists
            program_check_response = self.session.get(f"{BACKEND_URL}/programs/{workflow_program_id}", timeout=15)
            
            if program_check_response.status_code != 200:
                self.log_test("Programs.js Workflow - Program Verification", False, 
                            f"Program verification failed: {program_check_response.status_code}")
                return False
            
            # Get the final test and verify it's associated with the program
            final_test_check_response = self.session.get(f"{BACKEND_URL}/final-tests/{workflow_final_test_id}", timeout=15)
            
            if final_test_check_response.status_code != 200:
                self.log_test("Programs.js Workflow - Final Test Verification", False, 
                            f"Final test verification failed: {final_test_check_response.status_code}")
                return False
            
            final_test_check = final_test_check_response.json()
            
            if final_test_check["programId"] != workflow_program_id:
                self.log_test("Programs.js Workflow - Association Verification", False, 
                            f"Program ID mismatch: expected {workflow_program_id}, got {final_test_check['programId']}")
                return False
            
            self.log_test("Programs.js Workflow", True, 
                        f"Complete workflow successful: Program {workflow_program_id} → Final Test {workflow_final_test_id}")
            return True
            
        except requests.exceptions.ConnectTimeout:
            self.log_test("Programs.js Workflow", False, "Connection timeout during workflow")
            return False
        except requests.exceptions.ConnectionError as e:
            self.log_test("Programs.js Workflow", False, f"Connection error during workflow: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Programs.js Workflow", False, f"Workflow exception: {str(e)}")
            return False
    
    def test_validation_edge_cases(self):
        """Test 6: Validation edge cases for recent changes"""
        try:
            print("🧪 Testing validation edge cases...")
            
            if not self.created_program_id:
                self.log_test("Validation Edge Cases", False, "No program ID available for testing")
                return False
            
            # Test case 1: Final test with null questions
            test_case_1 = {
                "title": "Edge Case 1 - Null Questions",
                "description": "Testing null questions field",
                "programId": self.created_program_id,
                "questions": None,  # Explicitly null
                "timeLimit": 45,
                "maxAttempts": 1,
                "passingScore": 70.0,
                "isPublished": False
            }
            
            response_1 = self.session.post(f"{BACKEND_URL}/final-tests", json=test_case_1, timeout=15)
            
            if response_1.status_code == 200:
                self.log_test("Validation Edge Case - Null Questions", True, "Null questions accepted")
            elif response_1.status_code == 422:
                self.log_test("Validation Edge Case - Null Questions", False, f"422 Error: {response_1.text}")
            else:
                self.log_test("Validation Edge Case - Null Questions", False, f"Unexpected status: {response_1.status_code}")
            
            # Test case 2: Final test without questions field at all
            test_case_2 = {
                "title": "Edge Case 2 - Missing Questions Field",
                "description": "Testing missing questions field",
                "programId": self.created_program_id,
                # questions field completely omitted
                "timeLimit": 45,
                "maxAttempts": 1,
                "passingScore": 70.0,
                "isPublished": False
            }
            
            response_2 = self.session.post(f"{BACKEND_URL}/final-tests", json=test_case_2, timeout=15)
            
            if response_2.status_code == 200:
                self.log_test("Validation Edge Case - Missing Questions Field", True, "Missing questions field accepted")
            elif response_2.status_code == 422:
                self.log_test("Validation Edge Case - Missing Questions Field", False, f"422 Error: {response_2.text}")
            else:
                self.log_test("Validation Edge Case - Missing Questions Field", False, f"Unexpected status: {response_2.status_code}")
            
            # Test case 3: Invalid program ID
            test_case_3 = {
                "title": "Edge Case 3 - Invalid Program ID",
                "description": "Testing invalid program ID",
                "programId": "invalid-program-id-12345",
                "questions": [],
                "timeLimit": 45,
                "maxAttempts": 1,
                "passingScore": 70.0,
                "isPublished": False
            }
            
            response_3 = self.session.post(f"{BACKEND_URL}/final-tests", json=test_case_3, timeout=15)
            
            if response_3.status_code == 422 or response_3.status_code == 404:
                self.log_test("Validation Edge Case - Invalid Program ID", True, f"Invalid program ID properly rejected: {response_3.status_code}")
            else:
                self.log_test("Validation Edge Case - Invalid Program ID", False, f"Invalid program ID not properly handled: {response_3.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Validation Edge Cases", False, f"Exception: {str(e)}")
            return False
    
    def test_backend_logs_analysis(self):
        """Test 7: Analyze backend behavior and logs"""
        try:
            print("📊 Analyzing backend behavior...")
            
            # Test multiple rapid requests to see if there are rate limiting or connection issues
            rapid_test_results = []
            
            for i in range(5):
                start_time = time.time()
                try:
                    response = self.session.get(f"{BACKEND_URL}/programs", timeout=10)
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    rapid_test_results.append({
                        "request": i + 1,
                        "status": response.status_code,
                        "response_time": response_time,
                        "success": response.status_code == 200
                    })
                    
                except Exception as e:
                    rapid_test_results.append({
                        "request": i + 1,
                        "status": "ERROR",
                        "response_time": None,
                        "success": False,
                        "error": str(e)
                    })
                
                time.sleep(0.5)  # Small delay between requests
            
            successful_requests = sum(1 for result in rapid_test_results if result["success"])
            avg_response_time = sum(r["response_time"] for r in rapid_test_results if r["response_time"]) / len([r for r in rapid_test_results if r["response_time"]])
            
            if successful_requests >= 4:  # Allow for 1 failure
                self.log_test("Backend Behavior Analysis", True, 
                            f"Rapid requests: {successful_requests}/5 successful, avg response time: {avg_response_time:.2f}s")
            else:
                self.log_test("Backend Behavior Analysis", False, 
                            f"Rapid requests: only {successful_requests}/5 successful")
                
                # Print detailed results for failed requests
                for result in rapid_test_results:
                    if not result["success"]:
                        print(f"    Failed request {result['request']}: {result.get('error', result['status'])}")
            
            return successful_requests >= 4
            
        except Exception as e:
            self.log_test("Backend Behavior Analysis", False, f"Exception: {str(e)}")
            return False
    
    def run_debug_tests(self):
        """Run all debug tests for program and final test creation issues"""
        print("🚀 Starting Program & Final Test Creation Debug Testing")
        print("=" * 80)
        print("🎯 Focus: Network connectivity, 422 errors, and validation issues")
        print("=" * 80)
        
        # Test 1: Network connectivity
        if not self.test_network_connectivity():
            print("❌ Network connectivity failed. This explains ERR_CONNECTION_RESET/ERR_NAME_NOT_RESOLVED errors.")
            return False
        
        # Test 2: Authentication
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed with API tests.")
            return False
        
        # Test 3: Program creation
        program = self.test_program_creation_endpoint()
        
        # Test 4: Final test creation
        final_test = self.test_final_test_creation_endpoint()
        
        # Test 5: Complete workflow
        self.test_programs_js_workflow()
        
        # Test 6: Validation edge cases
        self.test_validation_edge_cases()
        
        # Test 7: Backend behavior analysis
        self.test_backend_logs_analysis()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 DEBUG TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests < total_tests:
            print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
            print("\n🔍 FAILED TESTS ANALYSIS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}")
                    print(f"     Issue: {result['details']}")
        
        # Specific analysis for the reported issues
        print("\n" + "=" * 80)
        print("🎯 SPECIFIC ISSUE ANALYSIS")
        print("=" * 80)
        
        network_issues = [r for r in self.test_results if not r["success"] and ("Connection" in r["details"] or "timeout" in r["details"])]
        validation_issues = [r for r in self.test_results if not r["success"] and "422" in r["details"]]
        
        if network_issues:
            print("🚨 NETWORK CONNECTIVITY ISSUES DETECTED:")
            for issue in network_issues:
                print(f"  - {issue['test']}: {issue['details']}")
            print("  💡 This explains the ERR_CONNECTION_RESET and ERR_NAME_NOT_RESOLVED errors reported by user.")
        
        if validation_issues:
            print("🚨 VALIDATION ISSUES DETECTED:")
            for issue in validation_issues:
                print(f"  - {issue['test']}: {issue['details']}")
            print("  💡 This explains the 422 HTTP errors when creating programs with final tests.")
        
        if not network_issues and not validation_issues:
            print("✅ NO CRITICAL ISSUES DETECTED:")
            print("  - Network connectivity is working properly")
            print("  - Program creation endpoint is functional")
            print("  - Final test creation endpoint is functional")
            print("  - Recent changes to make questions field optional are working correctly")
        
        print(f"\n🎯 Overall System Status: {'✅ HEALTHY' if success_rate >= 80 else '❌ NEEDS ATTENTION'}")
        
        return success_rate >= 80

if __name__ == "__main__":
    debugger = ProgramFinalTestDebugger()
    success = debugger.run_debug_tests()
    sys.exit(0 if success else 1)