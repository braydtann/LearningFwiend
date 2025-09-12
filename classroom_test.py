#!/usr/bin/env python3
"""
Classroom Creation Functionality Testing
Tests the classroom creation workflow after fixes to resolve the issue where
classrooms weren't showing up in the list after creation.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://task-summary-5.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

class ClassroomTester:
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
            if details:
                print(f"   Details: {details}")
    
    def authenticate_users(self):
        """Authenticate admin and instructor users"""
        # Admin login
        admin_login_data = {
            "username_or_email": "admin",
            "password": "NewAdmin123!"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=admin_login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_tokens['admin'] = data.get('access_token')
                self.log_result(
                    "Admin Authentication", 
                    "PASS", 
                    f"Successfully logged in as admin: {data.get('user', {}).get('username')}",
                    f"Token received, role: {data.get('user', {}).get('role')}"
                )
            else:
                self.log_result(
                    "Admin Authentication", 
                    "FAIL", 
                    f"Admin login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
        except Exception as e:
            self.log_result(
                "Admin Authentication", 
                "FAIL", 
                "Failed to authenticate admin",
                str(e)
            )
            return False
        
        # Instructor login
        instructor_login_data = {
            "username_or_email": "instructor",
            "password": "Instructor123!"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=instructor_login_data,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_tokens['instructor'] = data.get('access_token')
                self.log_result(
                    "Instructor Authentication", 
                    "PASS", 
                    f"Successfully logged in as instructor: {data.get('user', {}).get('username')}",
                    f"Token received, role: {data.get('user', {}).get('role')}"
                )
            else:
                self.log_result(
                    "Instructor Authentication", 
                    "FAIL", 
                    f"Instructor login failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
                return False
        except Exception as e:
            self.log_result(
                "Instructor Authentication", 
                "FAIL", 
                "Failed to authenticate instructor",
                str(e)
            )
            return False
        
        return True
    
    def test_get_classrooms_endpoint(self):
        """Test GET /api/classrooms endpoint exists and works"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "GET Classrooms Endpoint", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/classrooms",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                classrooms = response.json()
                self.log_result(
                    "GET Classrooms Endpoint", 
                    "PASS", 
                    f"Successfully retrieved {len(classrooms)} classrooms from database",
                    f"Endpoint working correctly, returned list of classrooms"
                )
                return classrooms
            else:
                self.log_result(
                    "GET Classrooms Endpoint", 
                    "FAIL", 
                    f"Failed to get classrooms, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "GET Classrooms Endpoint", 
                "FAIL", 
                "Failed to test GET classrooms endpoint",
                str(e)
            )
        return False
    
    def test_post_classrooms_endpoint(self):
        """Test POST /api/classrooms endpoint exists and works"""
        if "instructor" not in self.auth_tokens:
            self.log_result(
                "POST Classrooms Endpoint", 
                "SKIP", 
                "No instructor token available",
                "Instructor authentication required"
            )
            return False
        
        # First, get available instructors and courses for the classroom
        try:
            # Get users to find instructors
            users_response = requests.get(
                f"{BACKEND_URL}/auth/admin/users",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if users_response.status_code != 200:
                self.log_result(
                    "POST Classrooms Endpoint - Setup", 
                    "FAIL", 
                    "Could not get users list for classroom setup",
                    f"Users API failed with status: {users_response.status_code}"
                )
                return False
            
            users = users_response.json()
            instructors = [u for u in users if u.get('role') == 'instructor']
            
            if not instructors:
                self.log_result(
                    "POST Classrooms Endpoint - Setup", 
                    "FAIL", 
                    "No instructors found in database",
                    "Need at least one instructor to create classroom"
                )
                return False
            
            # Get courses
            courses_response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["instructor"]}'}
            )
            
            courses = []
            if courses_response.status_code == 200:
                courses = courses_response.json()
            
            # Create classroom data
            course_ids = [course['id'] for course in courses[:2]] if len(courses) >= 2 else [courses[0]['id']] if courses else []
            classroom_data = {
                "name": "Test Classroom - API Test",
                "description": "Testing classroom creation via API after fixes",
                "trainerId": instructors[0]['id'],
                "courseIds": course_ids,
                "programIds": [],
                "studentIds": [],
                "batchId": "BATCH-2024-TEST-001",
                "department": "Testing",
                "maxStudents": 25
            }
            
            # Test POST endpoint
            response = requests.post(
                f"{BACKEND_URL}/classrooms",
                json=classroom_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["instructor"]}'
                }
            )
            
            if response.status_code == 200:
                created_classroom = response.json()
                self.log_result(
                    "POST Classrooms Endpoint", 
                    "PASS", 
                    f"Successfully created classroom: {created_classroom.get('name')}",
                    f"Classroom ID: {created_classroom.get('id')}, Trainer: {created_classroom.get('trainerName')}"
                )
                return created_classroom
            else:
                self.log_result(
                    "POST Classrooms Endpoint", 
                    "FAIL", 
                    f"Failed to create classroom, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "POST Classrooms Endpoint", 
                "FAIL", 
                "Failed to test POST classrooms endpoint",
                str(e)
            )
        return False
    
    def test_classroom_creation_workflow(self):
        """Test complete classroom creation workflow - create then verify it appears in list"""
        print("\n🔄 Testing Complete Classroom Creation Workflow")
        
        # Step 1: Get initial classroom count
        initial_classrooms = self.test_get_classrooms_endpoint()
        if initial_classrooms is False:
            self.log_result(
                "Classroom Creation Workflow - Initial Count", 
                "FAIL", 
                "Could not get initial classroom count",
                "Cannot proceed with workflow test"
            )
            return False
        
        initial_count = len(initial_classrooms) if initial_classrooms else 0
        self.log_result(
            "Classroom Creation Workflow - Initial Count", 
            "INFO", 
            f"Initial classroom count: {initial_count}",
            "Baseline established for workflow test"
        )
        
        # Step 2: Create a new classroom
        created_classroom = self.test_post_classrooms_endpoint()
        if not created_classroom:
            self.log_result(
                "Classroom Creation Workflow - Creation Step", 
                "FAIL", 
                "Could not create classroom",
                "Cannot proceed with workflow verification"
            )
            return False
        
        created_classroom_id = created_classroom.get('id')
        created_classroom_name = created_classroom.get('name')
        
        # Step 3: Wait a moment for database consistency
        time.sleep(2)
        
        # Step 4: Get updated classroom list
        updated_classrooms = self.test_get_classrooms_endpoint()
        if updated_classrooms is False:
            self.log_result(
                "Classroom Creation Workflow - Verification Step", 
                "FAIL", 
                "Could not get updated classroom list",
                "Cannot verify if classroom appears in list"
            )
            return False
        
        updated_count = len(updated_classrooms) if updated_classrooms else 0
        
        # Step 5: Verify the classroom appears in the list
        found_classroom = None
        for classroom in updated_classrooms:
            if classroom.get('id') == created_classroom_id:
                found_classroom = classroom
                break
        
        if found_classroom:
            self.log_result(
                "Classroom Creation Workflow - Complete Test", 
                "PASS", 
                f"✅ WORKFLOW SUCCESS: Created classroom '{created_classroom_name}' appears in classroom list",
                f"Initial count: {initial_count}, Updated count: {updated_count}, Found classroom ID: {created_classroom_id}"
            )
            
            # Additional verification - check classroom data structure
            required_fields = ['id', 'name', 'trainerId', 'trainerName', 'studentCount', 'courseCount']
            missing_fields = [field for field in required_fields if field not in found_classroom]
            
            if not missing_fields:
                self.log_result(
                    "Classroom Data Structure", 
                    "PASS", 
                    "Classroom data structure is complete with all required fields",
                    f"Fields present: {list(found_classroom.keys())}"
                )
            else:
                self.log_result(
                    "Classroom Data Structure", 
                    "FAIL", 
                    f"Classroom missing required fields: {missing_fields}",
                    f"Available fields: {list(found_classroom.keys())}"
                )
            
            return True
        else:
            self.log_result(
                "Classroom Creation Workflow - Complete Test", 
                "FAIL", 
                f"❌ CRITICAL ISSUE: Created classroom '{created_classroom_name}' NOT found in classroom list",
                f"This confirms the reported bug - classrooms not showing up after creation. Initial count: {initial_count}, Updated count: {updated_count}"
            )
            return False
    
    def test_classroom_data_structure(self):
        """Test classroom data structure and required fields"""
        classrooms = self.test_get_classrooms_endpoint()
        if not classrooms:
            self.log_result(
                "Classroom Data Structure", 
                "SKIP", 
                "No classrooms available to test data structure",
                "Need at least one classroom in database"
            )
            return False
        
        sample_classroom = classrooms[0]
        required_fields = [
            'id', 'name', 'trainerId', 'trainerName', 
            'studentCount', 'courseCount', 'programCount',
            'isActive', 'created_at'
        ]
        
        missing_fields = [field for field in required_fields if field not in sample_classroom]
        
        if not missing_fields:
            self.log_result(
                "Classroom Data Structure", 
                "PASS", 
                "Classroom data structure contains all required fields",
                f"Sample classroom fields: {list(sample_classroom.keys())}"
            )
            return True
        else:
            self.log_result(
                "Classroom Data Structure", 
                "FAIL", 
                f"Classroom data structure missing required fields: {missing_fields}",
                f"Available fields: {list(sample_classroom.keys())}"
            )
            return False
    
    def test_mongodb_atlas_storage(self):
        """Verify that classrooms are stored in MongoDB Atlas shared database"""
        if "admin" not in self.auth_tokens:
            self.log_result(
                "MongoDB Atlas Storage", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            # Get classrooms to verify they're stored in Atlas
            response = requests.get(
                f"{BACKEND_URL}/classrooms",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                classrooms = response.json()
                
                # Also verify we can create and retrieve (full CRUD test)
                test_classroom_data = {
                    "name": "Atlas Storage Test Classroom",
                    "description": "Testing MongoDB Atlas storage",
                    "trainerId": "test-trainer-id",  # We'll use a real instructor ID
                    "courseIds": [],
                    "programIds": [],
                    "studentIds": [],
                    "batchId": "ATLAS-TEST-001",
                    "department": "Testing"
                }
                
                # Get a real instructor ID
                users_response = requests.get(
                    f"{BACKEND_URL}/auth/admin/users",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if users_response.status_code == 200:
                    users = users_response.json()
                    instructors = [u for u in users if u.get('role') == 'instructor']
                    if instructors:
                        test_classroom_data["trainerId"] = instructors[0]['id']
                        
                        # Create test classroom
                        create_response = requests.post(
                            f"{BACKEND_URL}/classrooms",
                            json=test_classroom_data,
                            timeout=TEST_TIMEOUT,
                            headers={
                                'Content-Type': 'application/json',
                                'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                            }
                        )
                        
                        if create_response.status_code == 200:
                            created = create_response.json()
                            self.log_result(
                                "MongoDB Atlas Storage", 
                                "PASS", 
                                f"Classrooms successfully stored in MongoDB Atlas shared database",
                                f"Retrieved {len(classrooms)} existing classrooms and created test classroom ID: {created.get('id')}"
                            )
                            return True
                
                self.log_result(
                    "MongoDB Atlas Storage", 
                    "PASS", 
                    f"Classrooms are retrievable from MongoDB Atlas shared database",
                    f"Retrieved {len(classrooms)} classrooms from learningfwiend_shared database"
                )
                return True
            else:
                self.log_result(
                    "MongoDB Atlas Storage", 
                    "FAIL", 
                    f"Could not retrieve classrooms from Atlas database, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.log_result(
                "MongoDB Atlas Storage", 
                "FAIL", 
                "Failed to test MongoDB Atlas storage",
                str(e)
            )
        return False
    
    def run_all_tests(self):
        """Run all classroom tests"""
        print("🏫 CLASSROOM CREATION FUNCTIONALITY TESTING")
        print("=" * 60)
        print("Testing classroom creation after fixes to resolve the issue")
        print("where classrooms weren't showing up in the list after creation.")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate_users():
            print("\n❌ Authentication failed - cannot proceed with tests")
            return
        
        print("\n📋 TESTING CLASSROOM API ENDPOINTS")
        print("-" * 40)
        
        # Step 2: Test individual endpoints
        self.test_get_classrooms_endpoint()
        self.test_post_classrooms_endpoint()
        
        print("\n🔄 TESTING COMPLETE WORKFLOW")
        print("-" * 40)
        
        # Step 3: Test complete workflow (the main issue)
        self.test_classroom_creation_workflow()
        
        print("\n🗃️  TESTING DATA STRUCTURE & STORAGE")
        print("-" * 40)
        
        # Step 4: Test data structure and storage
        self.test_classroom_data_structure()
        self.test_mongodb_atlas_storage()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 CLASSROOM TESTING SUMMARY")
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
        
        # Specific analysis for the reported issue
        workflow_test = next((r for r in self.results if 'Complete Test' in r['test']), None)
        if workflow_test:
            if workflow_test['status'] == 'PASS':
                print(f"\n✅ ISSUE RESOLVED: Classroom creation workflow is working correctly")
                print(f"   Classrooms now appear in the list after creation as expected")
            else:
                print(f"\n❌ ISSUE PERSISTS: Classroom creation workflow still has problems")
                print(f"   The reported issue where classrooms don't show up after creation is still present")

if __name__ == "__main__":
    tester = ClassroomTester()
    tester.run_all_tests()