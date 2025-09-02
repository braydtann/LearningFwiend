#!/usr/bin/env python3
"""
Comprehensive Classroom CRUD Testing
Tests all classroom functionality including creation, retrieval, update, and validation
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://project-summary-3.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

class ComprehensiveClassroomTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        self.test_data = {}
        
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
            if details:
                print(f"   Details: {details}")
    
    def authenticate_users(self):
        """Authenticate all user types"""
        credentials = {
            'admin': {"username_or_email": "admin", "password": "NewAdmin123!"},
            'instructor': {"username_or_email": "instructor", "password": "Instructor123!"},
            'learner': {"username_or_email": "student", "password": "Student123!"}
        }
        
        for role, creds in credentials.items():
            try:
                response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json=creds,
                    timeout=TEST_TIMEOUT,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_tokens[role] = data.get('access_token')
                    self.log_result(
                        f"{role.title()} Authentication", 
                        "PASS", 
                        f"Successfully authenticated as {role}",
                        f"User: {data.get('user', {}).get('username')}"
                    )
                else:
                    self.log_result(
                        f"{role.title()} Authentication", 
                        "FAIL", 
                        f"Failed to authenticate {role}",
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
                    return False
            except Exception as e:
                self.log_result(
                    f"{role.title()} Authentication", 
                    "FAIL", 
                    f"Exception during {role} authentication",
                    str(e)
                )
                return False
        
        return True
    
    def setup_test_data(self):
        """Setup test data - get users, courses, programs"""
        try:
            # Get users
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if users_response.status_code == 200:
                users = users_response.json()
                self.test_data['instructors'] = [u for u in users if u.get('role') == 'instructor']
                self.test_data['learners'] = [u for u in users if u.get('role') == 'learner']
                
                self.log_result(
                    "Test Data Setup - Users", 
                    "PASS", 
                    f"Retrieved {len(self.test_data['instructors'])} instructors and {len(self.test_data['learners'])} learners",
                    f"Total users: {len(users)}"
                )
            else:
                self.log_result(
                    "Test Data Setup - Users", 
                    "FAIL", 
                    "Could not retrieve users",
                    f"Status: {users_response.status_code}"
                )
                return False
            
            # Get courses
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if courses_response.status_code == 200:
                self.test_data['courses'] = courses_response.json()
                self.log_result(
                    "Test Data Setup - Courses", 
                    "PASS", 
                    f"Retrieved {len(self.test_data['courses'])} courses",
                    f"Available for classroom assignment"
                )
            else:
                self.test_data['courses'] = []
                self.log_result(
                    "Test Data Setup - Courses", 
                    "INFO", 
                    "No courses available",
                    "Will test without course assignments"
                )
            
            # Get programs
            programs_response = requests.get(
                f"{BACKEND_URL}/programs",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            if programs_response.status_code == 200:
                self.test_data['programs'] = programs_response.json()
                self.log_result(
                    "Test Data Setup - Programs", 
                    "PASS", 
                    f"Retrieved {len(self.test_data['programs'])} programs",
                    f"Available for classroom assignment"
                )
            else:
                self.test_data['programs'] = []
                self.log_result(
                    "Test Data Setup - Programs", 
                    "INFO", 
                    "No programs available",
                    "Will test without program assignments"
                )
            
            return True
            
        except Exception as e:
            self.log_result(
                "Test Data Setup", 
                "FAIL", 
                "Failed to setup test data",
                str(e)
            )
            return False
    
    def test_classroom_creation_comprehensive(self):
        """Test comprehensive classroom creation with various scenarios"""
        if not self.test_data.get('instructors'):
            self.log_result(
                "Classroom Creation - Comprehensive", 
                "SKIP", 
                "No instructors available for testing",
                "Need at least one instructor"
            )
            return False
        
        # Test 1: Basic classroom creation
        basic_classroom_data = {
            "name": "Comprehensive Test Classroom - Basic",
            "description": "Basic classroom creation test",
            "trainerId": self.test_data['instructors'][0]['id'],
            "courseIds": [],
            "programIds": [],
            "studentIds": [],
            "batchId": "COMP-TEST-001",
            "department": "Testing"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/classrooms",
                json=basic_classroom_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 200:
                created = response.json()
                self.test_data['created_classroom'] = created
                self.log_result(
                    "Classroom Creation - Basic", 
                    "PASS", 
                    f"Successfully created basic classroom: {created.get('name')}",
                    f"ID: {created.get('id')}, Trainer: {created.get('trainerName')}"
                )
            else:
                self.log_result(
                    "Classroom Creation - Basic", 
                    "FAIL", 
                    f"Failed to create basic classroom, status: {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
        except Exception as e:
            self.log_result(
                "Classroom Creation - Basic", 
                "FAIL", 
                "Exception during basic classroom creation",
                str(e)
            )
            return False
        
        # Test 2: Classroom with courses and students
        if self.test_data.get('courses') and self.test_data.get('learners'):
            advanced_classroom_data = {
                "name": "Comprehensive Test Classroom - Advanced",
                "description": "Advanced classroom with courses and students",
                "trainerId": self.test_data['instructors'][0]['id'],
                "courseIds": [course['id'] for course in self.test_data['courses'][:2]],
                "programIds": [program['id'] for program in self.test_data['programs'][:1]] if self.test_data.get('programs') else [],
                "studentIds": [learner['id'] for learner in self.test_data['learners'][:3]],
                "batchId": "COMP-TEST-002",
                "department": "Testing",
                "maxStudents": 30
            }
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/classrooms",
                    json=advanced_classroom_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                    }
                )
                
                if response.status_code == 200:
                    created = response.json()
                    self.log_result(
                        "Classroom Creation - Advanced", 
                        "PASS", 
                        f"Successfully created advanced classroom with {created.get('courseCount', 0)} courses and {created.get('studentCount', 0)} students",
                        f"ID: {created.get('id')}, Name: {created.get('name')}"
                    )
                else:
                    self.log_result(
                        "Classroom Creation - Advanced", 
                        "FAIL", 
                        f"Failed to create advanced classroom, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
            except Exception as e:
                self.log_result(
                    "Classroom Creation - Advanced", 
                    "FAIL", 
                    "Exception during advanced classroom creation",
                    str(e)
                )
        
        return True
    
    def test_classroom_retrieval_methods(self):
        """Test different methods of retrieving classrooms"""
        # Test 1: Get all classrooms
        try:
            response = requests.get(
                f"{BACKEND_URL}/classrooms",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                classrooms = response.json()
                self.log_result(
                    "Classroom Retrieval - Get All", 
                    "PASS", 
                    f"Successfully retrieved {len(classrooms)} classrooms",
                    f"All classrooms accessible via GET /api/classrooms"
                )
                
                # Test 2: Get specific classroom by ID
                if classrooms and len(classrooms) > 0:
                    classroom_id = classrooms[0]['id']
                    specific_response = requests.get(
                        f"{BACKEND_URL}/classrooms/{classroom_id}",
                        timeout=TEST_TIMEOUT,
                        headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                    )
                    
                    if specific_response.status_code == 200:
                        specific_classroom = specific_response.json()
                        self.log_result(
                            "Classroom Retrieval - By ID", 
                            "PASS", 
                            f"Successfully retrieved specific classroom: {specific_classroom.get('name')}",
                            f"GET /api/classrooms/{classroom_id} working correctly"
                        )
                    else:
                        self.log_result(
                            "Classroom Retrieval - By ID", 
                            "FAIL", 
                            f"Failed to retrieve classroom by ID, status: {specific_response.status_code}",
                            f"Response: {specific_response.text}"
                        )
                
            else:
                self.log_result(
                    "Classroom Retrieval - Get All", 
                    "FAIL", 
                    f"Failed to retrieve classrooms, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Classroom Retrieval - Get All", 
                "FAIL", 
                "Exception during classroom retrieval",
                str(e)
            )
    
    def test_classroom_permissions(self):
        """Test classroom permissions for different user roles"""
        # Test 1: Admin can create classrooms
        if self.test_data.get('instructors'):
            admin_classroom_data = {
                "name": "Admin Created Classroom",
                "description": "Testing admin permissions",
                "trainerId": self.test_data['instructors'][0]['id'],
                "courseIds": [],
                "programIds": [],
                "studentIds": [],
                "batchId": "ADMIN-TEST-001",
                "department": "Testing"
            }
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/classrooms",
                    json=admin_classroom_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                    }
                )
                
                if response.status_code == 200:
                    self.log_result(
                        "Classroom Permissions - Admin Create", 
                        "PASS", 
                        "Admin can successfully create classrooms",
                        f"Created classroom: {response.json().get('name')}"
                    )
                else:
                    self.log_result(
                        "Classroom Permissions - Admin Create", 
                        "FAIL", 
                        f"Admin failed to create classroom, status: {response.status_code}",
                        f"Response: {response.text}"
                    )
            except Exception as e:
                self.log_result(
                    "Classroom Permissions - Admin Create", 
                    "FAIL", 
                    "Exception during admin classroom creation",
                    str(e)
                )
        
        # Test 2: Learner cannot create classrooms
        if self.test_data.get('instructors'):
            learner_classroom_data = {
                "name": "Learner Attempt Classroom",
                "description": "Testing learner permissions (should fail)",
                "trainerId": self.test_data['instructors'][0]['id'],
                "courseIds": [],
                "programIds": [],
                "studentIds": [],
                "batchId": "LEARNER-TEST-001",
                "department": "Testing"
            }
            
            try:
                response = requests.post(
                    f"{BACKEND_URL}/classrooms",
                    json=learner_classroom_data,
                    timeout=TEST_TIMEOUT,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.auth_tokens["learner"]}'
                    }
                )
                
                if response.status_code == 403:
                    self.log_result(
                        "Classroom Permissions - Learner Denied", 
                        "PASS", 
                        "Learner correctly denied classroom creation (403 Forbidden)",
                        "Permission system working correctly"
                    )
                elif response.status_code == 200:
                    self.log_result(
                        "Classroom Permissions - Learner Denied", 
                        "FAIL", 
                        "Learner was allowed to create classroom (security issue)",
                        "Learners should not be able to create classrooms"
                    )
                else:
                    self.log_result(
                        "Classroom Permissions - Learner Denied", 
                        "INFO", 
                        f"Learner classroom creation failed with status {response.status_code}",
                        f"Expected 403, got {response.status_code}"
                    )
            except Exception as e:
                self.log_result(
                    "Classroom Permissions - Learner Denied", 
                    "FAIL", 
                    "Exception during learner permission test",
                    str(e)
                )
    
    def test_classroom_validation(self):
        """Test classroom data validation"""
        # Test 1: Invalid trainer ID
        invalid_trainer_data = {
            "name": "Invalid Trainer Test",
            "description": "Testing invalid trainer validation",
            "trainerId": "invalid-trainer-id-12345",
            "courseIds": [],
            "programIds": [],
            "studentIds": [],
            "batchId": "INVALID-001",
            "department": "Testing"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/classrooms",
                json=invalid_trainer_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 400:
                self.log_result(
                    "Classroom Validation - Invalid Trainer", 
                    "PASS", 
                    "Invalid trainer ID correctly rejected (400 Bad Request)",
                    "Validation system working correctly"
                )
            else:
                self.log_result(
                    "Classroom Validation - Invalid Trainer", 
                    "FAIL", 
                    f"Invalid trainer ID not properly validated, status: {response.status_code}",
                    f"Expected 400, got {response.status_code}. Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Classroom Validation - Invalid Trainer", 
                "FAIL", 
                "Exception during trainer validation test",
                str(e)
            )
        
        # Test 2: Missing required fields
        incomplete_data = {
            "description": "Missing name field",
            "trainerId": self.test_data['instructors'][0]['id'] if self.test_data.get('instructors') else "test-id"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/classrooms",
                json=incomplete_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 422:
                self.log_result(
                    "Classroom Validation - Missing Fields", 
                    "PASS", 
                    "Missing required fields correctly rejected (422 Validation Error)",
                    "Field validation working correctly"
                )
            else:
                self.log_result(
                    "Classroom Validation - Missing Fields", 
                    "FAIL", 
                    f"Missing fields not properly validated, status: {response.status_code}",
                    f"Expected 422, got {response.status_code}. Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "Classroom Validation - Missing Fields", 
                "FAIL", 
                "Exception during field validation test",
                str(e)
            )
    
    def run_all_tests(self):
        """Run all comprehensive classroom tests"""
        print("🏫 COMPREHENSIVE CLASSROOM CRUD TESTING")
        print("=" * 60)
        print("Testing complete classroom functionality including creation,")
        print("retrieval, permissions, and validation after recent fixes.")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate_users():
            print("\n❌ Authentication failed - cannot proceed with tests")
            return
        
        # Step 2: Setup test data
        if not self.setup_test_data():
            print("\n❌ Test data setup failed - cannot proceed with tests")
            return
        
        print(f"\n📋 COMPREHENSIVE CLASSROOM TESTING")
        print("-" * 40)
        
        # Step 3: Run all tests
        self.test_classroom_creation_comprehensive()
        self.test_classroom_retrieval_methods()
        self.test_classroom_permissions()
        self.test_classroom_validation()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TESTING SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.failed > 0:
            print(f"\n🔍 FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['message']}")
        
        # Overall assessment
        creation_tests = [r for r in self.results if 'Creation' in r['test'] and r['status'] == 'PASS']
        retrieval_tests = [r for r in self.results if 'Retrieval' in r['test'] and r['status'] == 'PASS']
        
        print(f"\n🎯 CLASSROOM FUNCTIONALITY ASSESSMENT:")
        print(f"   • Creation: {'✅ Working' if creation_tests else '❌ Issues found'}")
        print(f"   • Retrieval: {'✅ Working' if retrieval_tests else '❌ Issues found'}")
        print(f"   • Permissions: {'✅ Working' if any('Permissions' in r['test'] and r['status'] == 'PASS' for r in self.results) else '❌ Issues found'}")
        print(f"   • Validation: {'✅ Working' if any('Validation' in r['test'] and r['status'] == 'PASS' for r in self.results) else '❌ Issues found'}")

if __name__ == "__main__":
    tester = ComprehensiveClassroomTester()
    tester.run_all_tests()