#!/usr/bin/env python3
"""
Comprehensive Program and Final Test Creation Testing
Testing the specific issues reported in review request with focus on:
1. Program creation endpoint: POST /api/programs
2. Final test creation endpoint: POST /api/final-tests 
3. Complete workflow of creating a program with final test (as done in Programs.js)
4. Recent changes to make FinalTestCreate questions field optional
5. Network connectivity issues between frontend and backend
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

class ComprehensiveProgramFinalTestTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30
        self.admin_token = None
        self.test_results = []
        self.created_programs = []
        self.created_final_tests = []
        
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
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username_or_email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                self.log_test("Admin Authentication", True, f"Logged in as {data['user']['full_name']}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_program_creation_basic(self):
        """Test 1: Basic program creation - POST /api/programs"""
        try:
            program_data = {
                "title": f"Test Program {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Basic program creation test",
                "departmentId": None,
                "duration": "4 weeks",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            
            if response.status_code == 200:
                program = response.json()
                self.created_programs.append(program["id"])
                self.log_test("Program Creation - Basic", True, 
                            f"Created program: {program['title']} (ID: {program['id']})")
                return program
            else:
                self.log_test("Program Creation - Basic", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Program Creation - Basic", False, f"Exception: {str(e)}")
            return None
    
    def test_final_test_creation_empty_questions(self, program_id):
        """Test 2: Final test creation with empty questions array"""
        try:
            test_data = {
                "title": f"Empty Questions Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing final test with empty questions array",
                "programId": program_id,
                "questions": [],  # Empty array
                "timeLimit": 60,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": False
            }
            
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                self.created_final_tests.append(final_test["id"])
                self.log_test("Final Test Creation - Empty Questions Array", True, 
                            f"Created test: {final_test['title']} (ID: {final_test['id']})")
                return final_test
            else:
                self.log_test("Final Test Creation - Empty Questions Array", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Final Test Creation - Empty Questions Array", False, f"Exception: {str(e)}")
            return None
    
    def test_final_test_creation_no_questions_field(self, program_id):
        """Test 3: Final test creation without questions field (testing optional field)"""
        try:
            test_data = {
                "title": f"No Questions Field Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing final test without questions field",
                "programId": program_id,
                # questions field omitted entirely
                "timeLimit": 90,
                "maxAttempts": 3,
                "passingScore": 80.0,
                "shuffleQuestions": True,
                "showResults": True,
                "isPublished": False
            }
            
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                self.created_final_tests.append(final_test["id"])
                self.log_test("Final Test Creation - No Questions Field", True, 
                            f"Created test: {final_test['title']} (ID: {final_test['id']})")
                return final_test
            else:
                self.log_test("Final Test Creation - No Questions Field", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Final Test Creation - No Questions Field", False, f"Exception: {str(e)}")
            return None
    
    def test_final_test_creation_null_questions(self, program_id):
        """Test 4: Final test creation with null questions (edge case)"""
        try:
            test_data = {
                "title": f"Null Questions Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing final test with null questions",
                "programId": program_id,
                "questions": None,  # Explicitly null
                "timeLimit": 45,
                "maxAttempts": 1,
                "passingScore": 70.0,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": False
            }
            
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                self.created_final_tests.append(final_test["id"])
                self.log_test("Final Test Creation - Null Questions", True, 
                            f"Created test: {final_test['title']} (ID: {final_test['id']})")
                return final_test
            elif response.status_code == 422:
                self.log_test("Final Test Creation - Null Questions", False, 
                            f"422 Validation Error (Expected): {response.text}")
                return None
            else:
                self.log_test("Final Test Creation - Null Questions", False, 
                            f"Unexpected Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Final Test Creation - Null Questions", False, f"Exception: {str(e)}")
            return None
    
    def test_final_test_creation_with_questions(self, program_id):
        """Test 5: Final test creation with actual questions"""
        try:
            test_data = {
                "title": f"With Questions Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing final test with actual questions",
                "programId": program_id,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "What is 2 + 2?",
                        "options": ["3", "4", "5", "6"],
                        "correctAnswer": "1",  # Index 1 = "4"
                        "points": 10,
                        "explanation": "Basic arithmetic"
                    },
                    {
                        "type": "true_false",
                        "question": "The sky is blue.",
                        "correctAnswer": "true",
                        "points": 5,
                        "explanation": "Generally true during clear weather"
                    }
                ],
                "timeLimit": 120,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "shuffleQuestions": True,
                "showResults": True,
                "isPublished": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            if response.status_code == 200:
                final_test = response.json()
                self.created_final_tests.append(final_test["id"])
                
                # Verify question count and total points
                if (final_test["questionCount"] == 2 and 
                    final_test["totalPoints"] == 15):
                    self.log_test("Final Test Creation - With Questions", True, 
                                f"Created test with 2 questions, 15 total points: {final_test['title']}")
                    return final_test
                else:
                    self.log_test("Final Test Creation - With Questions", False, 
                                f"Question count or points mismatch: {final_test}")
                    return None
            else:
                self.log_test("Final Test Creation - With Questions", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Final Test Creation - With Questions", False, f"Exception: {str(e)}")
            return None
    
    def test_programs_js_complete_workflow(self):
        """Test 6: Complete workflow as implemented in Programs.js"""
        try:
            # Step 1: Create program (as Programs.js does)
            program_data = {
                "title": f"Programs.js Workflow Test {datetime.now().strftime('%H%M%S')}",
                "description": "Testing complete Programs.js workflow",
                "courseIds": [],
                "nestedProgramIds": [],
                "duration": "6 weeks"
            }
            
            program_response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            
            if program_response.status_code != 200:
                self.log_test("Programs.js Workflow - Program Creation", False, 
                            f"Program creation failed: {program_response.status_code}")
                return False
            
            program = program_response.json()
            program_id = program["id"]
            self.created_programs.append(program_id)
            
            # Step 2: Create final test (as Programs.js does)
            # Simulating the exact data structure from Programs.js
            final_test_data = {
                "title": f"{program_data['title']} Final Assessment",
                "description": f"Comprehensive final test for {program_data['title']}",
                "programId": program_id,
                "questions": [],  # Empty questions as typically sent from Programs.js
                "timeLimit": 90,
                "maxAttempts": 2,
                "passingScore": 75,
                "shuffleQuestions": False,
                "showResults": True,
                "isPublished": True
            }
            
            final_test_response = self.session.post(f"{BACKEND_URL}/final-tests", json=final_test_data)
            
            if final_test_response.status_code != 200:
                self.log_test("Programs.js Workflow - Final Test Creation", False, 
                            f"Final test creation failed: {final_test_response.status_code} - {final_test_response.text}")
                return False
            
            final_test = final_test_response.json()
            final_test_id = final_test["id"]
            self.created_final_tests.append(final_test_id)
            
            # Step 3: Verify association
            verification_response = self.session.get(f"{BACKEND_URL}/final-tests/{final_test_id}")
            
            if verification_response.status_code != 200:
                self.log_test("Programs.js Workflow - Verification", False, 
                            f"Verification failed: {verification_response.status_code}")
                return False
            
            verified_test = verification_response.json()
            
            if verified_test["programId"] != program_id:
                self.log_test("Programs.js Workflow - Association Check", False, 
                            f"Program ID mismatch: expected {program_id}, got {verified_test['programId']}")
                return False
            
            self.log_test("Programs.js Complete Workflow", True, 
                        f"Successfully created program {program_id} and associated final test {final_test_id}")
            return True
            
        except Exception as e:
            self.log_test("Programs.js Complete Workflow", False, f"Exception: {str(e)}")
            return False
    
    def test_network_stress_test(self):
        """Test 7: Network stress test to identify connection issues"""
        try:
            success_count = 0
            total_requests = 10
            response_times = []
            
            for i in range(total_requests):
                start_time = time.time()
                try:
                    response = self.session.get(f"{BACKEND_URL}/programs", timeout=15)
                    end_time = time.time()
                    response_time = end_time - start_time
                    response_times.append(response_time)
                    
                    if response.status_code == 200:
                        success_count += 1
                    
                except requests.exceptions.ConnectTimeout:
                    print(f"    Request {i+1}: Connection timeout (ERR_CONNECTION_RESET)")
                except requests.exceptions.ConnectionError as e:
                    print(f"    Request {i+1}: Connection error (ERR_NAME_NOT_RESOLVED): {str(e)}")
                except Exception as e:
                    print(f"    Request {i+1}: Other error: {str(e)}")
                
                time.sleep(0.2)  # Small delay between requests
            
            success_rate = (success_count / total_requests) * 100
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            if success_rate >= 90:
                self.log_test("Network Stress Test", True, 
                            f"Success rate: {success_rate}%, Avg response time: {avg_response_time:.2f}s")
                return True
            else:
                self.log_test("Network Stress Test", False, 
                            f"Poor success rate: {success_rate}% ({success_count}/{total_requests})")
                return False
                
        except Exception as e:
            self.log_test("Network Stress Test", False, f"Exception: {str(e)}")
            return False
    
    def test_422_error_scenarios(self):
        """Test 8: Specific scenarios that might cause 422 errors"""
        try:
            # Create a test program first
            program_data = {
                "title": f"422 Test Program {datetime.now().strftime('%H%M%S')}",
                "description": "Program for testing 422 errors",
                "courseIds": [],
                "nestedProgramIds": [],
                "duration": "2 weeks"
            }
            
            program_response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            if program_response.status_code != 200:
                self.log_test("422 Error Scenarios - Setup", False, "Failed to create test program")
                return False
            
            program = program_response.json()
            program_id = program["id"]
            self.created_programs.append(program_id)
            
            # Test various 422 scenarios
            test_scenarios = [
                {
                    "name": "Missing Title",
                    "data": {
                        "description": "Test without title",
                        "programId": program_id,
                        "questions": []
                    },
                    "expect_422": True
                },
                {
                    "name": "Invalid Program ID",
                    "data": {
                        "title": "Test with invalid program ID",
                        "description": "Testing invalid program ID",
                        "programId": "invalid-program-id",
                        "questions": []
                    },
                    "expect_422": True
                },
                {
                    "name": "Invalid Passing Score",
                    "data": {
                        "title": "Test with invalid passing score",
                        "description": "Testing invalid passing score",
                        "programId": program_id,
                        "questions": [],
                        "passingScore": 150.0  # Invalid: > 100
                    },
                    "expect_422": True
                },
                {
                    "name": "Invalid Max Attempts",
                    "data": {
                        "title": "Test with invalid max attempts",
                        "description": "Testing invalid max attempts",
                        "programId": program_id,
                        "questions": [],
                        "maxAttempts": 10  # Invalid: > 5
                    },
                    "expect_422": True
                }
            ]
            
            all_scenarios_passed = True
            
            for scenario in test_scenarios:
                response = self.session.post(f"{BACKEND_URL}/final-tests", json=scenario["data"])
                
                if scenario["expect_422"]:
                    if response.status_code == 422:
                        print(f"    ✅ {scenario['name']}: Correctly returned 422")
                    else:
                        print(f"    ❌ {scenario['name']}: Expected 422, got {response.status_code}")
                        all_scenarios_passed = False
                else:
                    if response.status_code == 200:
                        print(f"    ✅ {scenario['name']}: Correctly succeeded")
                        # Clean up created test
                        test_data = response.json()
                        self.created_final_tests.append(test_data["id"])
                    else:
                        print(f"    ❌ {scenario['name']}: Expected 200, got {response.status_code}")
                        all_scenarios_passed = False
            
            self.log_test("422 Error Scenarios", all_scenarios_passed, 
                        f"Tested {len(test_scenarios)} validation scenarios")
            return all_scenarios_passed
            
        except Exception as e:
            self.log_test("422 Error Scenarios", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up created test data"""
        try:
            cleanup_count = 0
            
            # Delete created final tests
            for test_id in self.created_final_tests:
                try:
                    response = self.session.delete(f"{BACKEND_URL}/final-tests/{test_id}")
                    if response.status_code in [200, 204, 404]:  # 404 is OK if already deleted
                        cleanup_count += 1
                except:
                    pass  # Ignore cleanup errors
            
            # Delete created programs
            for program_id in self.created_programs:
                try:
                    response = self.session.delete(f"{BACKEND_URL}/programs/{program_id}")
                    if response.status_code in [200, 204, 404]:  # 404 is OK if already deleted
                        cleanup_count += 1
                except:
                    pass  # Ignore cleanup errors
            
            print(f"🧹 Cleaned up {cleanup_count} test items")
            
        except Exception as e:
            print(f"⚠️ Cleanup warning: {str(e)}")
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Program & Final Test Creation Testing")
        print("=" * 80)
        print("🎯 Testing specific issues from review request:")
        print("   - Network connection errors (ERR_CONNECTION_RESET, ERR_NAME_NOT_RESOLVED)")
        print("   - 422 HTTP errors when creating programs with final tests")
        print("   - Complete Programs.js workflow")
        print("   - Recent changes to make FinalTestCreate questions field optional")
        print("=" * 80)
        
        # Authenticate
        if not self.authenticate_admin():
            print("❌ Authentication failed. Cannot proceed.")
            return False
        
        # Test 1: Basic program creation
        program = self.test_program_creation_basic()
        if not program:
            print("❌ Basic program creation failed. Cannot proceed with final test tests.")
            return False
        
        program_id = program["id"]
        
        # Test 2-5: Final test creation variations
        self.test_final_test_creation_empty_questions(program_id)
        self.test_final_test_creation_no_questions_field(program_id)
        self.test_final_test_creation_null_questions(program_id)
        self.test_final_test_creation_with_questions(program_id)
        
        # Test 6: Complete Programs.js workflow
        self.test_programs_js_complete_workflow()
        
        # Test 7: Network stress test
        self.test_network_stress_test()
        
        # Test 8: 422 error scenarios
        self.test_422_error_scenarios()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests < total_tests:
            print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}")
                    print(f"     Issue: {result['details']}")
        
        # Analysis for specific reported issues
        print("\n" + "=" * 80)
        print("🎯 ISSUE-SPECIFIC ANALYSIS")
        print("=" * 80)
        
        network_failures = [r for r in self.test_results if not r["success"] and 
                          ("Connection" in r["details"] or "timeout" in r["details"] or "Network" in r["test"])]
        
        validation_failures = [r for r in self.test_results if not r["success"] and "422" in r["details"]]
        
        workflow_failures = [r for r in self.test_results if not r["success"] and "Workflow" in r["test"]]
        
        if network_failures:
            print("🚨 NETWORK CONNECTIVITY ISSUES:")
            for failure in network_failures:
                print(f"  - {failure['test']}: {failure['details']}")
            print("  💡 This explains ERR_CONNECTION_RESET and ERR_NAME_NOT_RESOLVED errors")
        else:
            print("✅ NETWORK CONNECTIVITY: No issues detected")
        
        if validation_failures:
            print("\n🚨 VALIDATION ISSUES (422 ERRORS):")
            for failure in validation_failures:
                print(f"  - {failure['test']}: {failure['details']}")
            print("  💡 This explains 422 HTTP errors when creating programs with final tests")
        else:
            print("✅ VALIDATION: No unexpected 422 errors detected")
        
        if workflow_failures:
            print("\n🚨 WORKFLOW ISSUES:")
            for failure in workflow_failures:
                print(f"  - {failure['test']}: {failure['details']}")
            print("  💡 This explains issues with Programs.js workflow")
        else:
            print("✅ PROGRAMS.JS WORKFLOW: Working correctly")
        
        # Specific findings
        print("\n" + "=" * 80)
        print("🔍 KEY FINDINGS")
        print("=" * 80)
        
        questions_field_tests = [r for r in self.test_results if "Questions" in r["test"]]
        questions_working = sum(1 for r in questions_field_tests if r["success"])
        
        print(f"📝 Questions Field Handling: {questions_working}/{len(questions_field_tests)} scenarios working")
        
        if questions_working == len(questions_field_tests):
            print("  ✅ Recent changes to make questions field optional are working correctly")
        else:
            print("  ⚠️ Some issues with questions field handling detected")
        
        print(f"\n🎯 Overall System Health: {'✅ HEALTHY' if success_rate >= 85 else '⚠️ NEEDS ATTENTION' if success_rate >= 70 else '❌ CRITICAL ISSUES'}")
        
        # Cleanup
        self.cleanup_test_data()
        
        return success_rate >= 85

if __name__ == "__main__":
    tester = ComprehensiveProgramFinalTestTester()
    success = tester.run_comprehensive_tests()
    sys.exit(0 if success else 1)