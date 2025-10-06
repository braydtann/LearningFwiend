#!/usr/bin/env python3
"""
Final Test Creation Debug - Step by Step Analysis
=================================================

This test debugs the final test creation process to see why questions
are not being stored in the database.

Admin: brayden.t@covesmart.com / Hawaii2020!
"""

import requests
import json
import sys
from datetime import datetime

BACKEND_URL = "https://lms-progression.preview.emergentagent.com/api"

ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class CreationDebugger:
    def __init__(self):
        self.admin_token = None
        
    def authenticate(self):
        """Authenticate admin"""
        response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "username_or_email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code != 200:
            print(f"❌ Admin auth failed: {response.status_code}")
            return False
            
        self.admin_token = response.json()["access_token"]
        print(f"✅ Admin authenticated")
        return True
    
    def create_program(self):
        """Create a test program"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        program_data = {
            "title": f"Creation Debug Program {datetime.now().strftime('%H%M%S')}",
            "description": "Debug program for creation testing",
            "courseIds": [],
            "nestedProgramIds": []
        }
        
        response = requests.post(f"{BACKEND_URL}/programs", json=program_data, headers=headers)
        
        if response.status_code == 200:
            program = response.json()
            print(f"✅ Program created: {program['id']}")
            return program['id']
        else:
            print(f"❌ Program creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    
    def test_creation_step_by_step(self, program_id):
        """Test final test creation with detailed debugging"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Create test data
        test_data = {
            "title": f"Creation Debug Test {datetime.now().strftime('%H%M%S')}",
            "description": "Debug test for creation process",
            "programId": program_id,
            "questions": [
                {
                    "type": "multiple_choice",
                    "question": "Debug question: What is 1 + 1?",
                    "options": ["1", "2", "3", "4"],
                    "correctAnswer": "1",  # Index 1 = "2"
                    "points": 10,
                    "explanation": "1 + 1 = 2"
                }
            ],
            "timeLimit": 30,
            "maxAttempts": 3,
            "passingScore": 70.0,
            "shuffleQuestions": False,
            "showResults": True,
            "isPublished": True
        }
        
        print("\n🔍 CREATION REQUEST DATA:")
        print(f"   Title: {test_data['title']}")
        print(f"   Program ID: {test_data['programId']}")
        print(f"   Questions Count: {len(test_data['questions'])}")
        print(f"   Question 1:")
        print(f"     Type: {test_data['questions'][0]['type']}")
        print(f"     Text: {test_data['questions'][0]['question']}")
        print(f"     Options: {test_data['questions'][0]['options']}")
        print(f"     Correct Answer: {test_data['questions'][0]['correctAnswer']}")
        print(f"     Points: {test_data['questions'][0]['points']}")
        
        # Submit creation request
        response = requests.post(f"{BACKEND_URL}/final-tests", json=test_data, headers=headers)
        
        print(f"\n🔍 CREATION RESPONSE:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            created_test = response.json()
            test_id = created_test['id']
            
            print(f"   ✅ Test created successfully")
            print(f"   Test ID: {test_id}")
            print(f"   Questions in response: {len(created_test.get('questions', []))}")
            print(f"   Total Points: {created_test.get('totalPoints', 0)}")
            print(f"   Question Count: {created_test.get('questionCount', 0)}")
            
            # Analyze the response questions
            if created_test.get('questions'):
                for i, q in enumerate(created_test['questions']):
                    print(f"   Response Question {i+1}:")
                    print(f"     ID: {q.get('id', 'NO_ID')}")
                    print(f"     Type: {q.get('type', 'NO_TYPE')}")
                    print(f"     Correct Answer: {q.get('correctAnswer', 'NO_CORRECT')}")
                    print(f"     Points: {q.get('points', 'NO_POINTS')}")
            else:
                print(f"   ❌ No questions in creation response!")
            
            return test_id
        else:
            print(f"   ❌ Creation failed")
            print(f"   Error: {response.text}")
            return None
    
    def verify_database_storage(self, test_id):
        """Verify the test was stored correctly in database"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get the test back from database
        response = requests.get(f"{BACKEND_URL}/final-tests/{test_id}", headers=headers)
        
        print(f"\n🔍 DATABASE VERIFICATION:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            stored_test = response.json()
            
            print(f"   ✅ Test retrieved from database")
            print(f"   Test ID: {stored_test.get('id')}")
            print(f"   Questions in database: {len(stored_test.get('questions', []))}")
            print(f"   Total Points: {stored_test.get('totalPoints', 0)}")
            print(f"   Question Count: {stored_test.get('questionCount', 0)}")
            
            # Analyze stored questions
            if stored_test.get('questions'):
                for i, q in enumerate(stored_test['questions']):
                    print(f"   Database Question {i+1}:")
                    print(f"     ID: {q.get('id', 'NO_ID')}")
                    print(f"     Type: {q.get('type', 'NO_TYPE')}")
                    print(f"     Text: {q.get('question', 'NO_TEXT')[:50]}...")
                    print(f"     Correct Answer: {q.get('correctAnswer', 'NO_CORRECT')}")
                    print(f"     Points: {q.get('points', 'NO_POINTS')}")
                    print(f"     Options: {q.get('options', 'NO_OPTIONS')}")
            else:
                print(f"   ❌ NO QUESTIONS FOUND IN DATABASE!")
                print(f"   🚨 THIS IS THE ROOT CAUSE OF 0% SCORES!")
            
            return stored_test
        else:
            print(f"   ❌ Failed to retrieve test")
            print(f"   Error: {response.text}")
            return None
    
    def test_direct_database_query(self, test_id):
        """Test if we can get the raw database document"""
        # This would require direct MongoDB access, but we can try the admin endpoint
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Try to get all final tests to see if our test appears
        response = requests.get(f"{BACKEND_URL}/final-tests", headers=headers)
        
        print(f"\n🔍 ALL TESTS QUERY:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            all_tests = response.json()
            print(f"   Total tests found: {len(all_tests)}")
            
            # Find our test
            our_test = None
            for test in all_tests:
                if test.get('id') == test_id:
                    our_test = test
                    break
            
            if our_test:
                print(f"   ✅ Found our test in list")
                print(f"   Questions in list: {len(our_test.get('questions', []))}")
                
                if not our_test.get('questions'):
                    print(f"   ❌ CONFIRMED: Questions missing from database storage")
                    print(f"   🔧 This explains why all final tests show 0 questions")
                else:
                    print(f"   ✅ Questions present in database")
            else:
                print(f"   ❌ Our test not found in list")
        else:
            print(f"   ❌ Failed to get all tests: {response.status_code}")
    
    def run_debug(self):
        """Run complete creation debugging"""
        print("🔍 FINAL TEST CREATION DEBUG")
        print("=" * 50)
        
        if not self.authenticate():
            return False
        
        program_id = self.create_program()
        if not program_id:
            return False
        
        test_id = self.test_creation_step_by_step(program_id)
        if not test_id:
            return False
        
        stored_test = self.verify_database_storage(test_id)
        
        self.test_direct_database_query(test_id)
        
        print("\n" + "=" * 50)
        print("🎯 CREATION DEBUG COMPLETE")
        
        if stored_test and stored_test.get('questions'):
            print("✅ Questions are being stored correctly")
        else:
            print("❌ CRITICAL: Questions are NOT being stored in database")
            print("🔧 This is the root cause of 0% scoring issue")
        
        return True

if __name__ == "__main__":
    debugger = CreationDebugger()
    success = debugger.run_debug()
    sys.exit(0 if success else 1)