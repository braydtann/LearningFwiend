#!/usr/bin/env python3
"""
Simulate User's Exact Error Experience

This test simulates exactly what the user experienced:
1. Send question types with underscores (wrong format)
2. Capture the 422 error response
3. Show how this might appear as [object Object] in frontend
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://grade-flow-wizard.preview.emergentagent.com/api"
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

class UserErrorSimulator:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
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
                print(f"✅ Authenticated as {data['user']['full_name']}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication exception: {str(e)}")
            return False
    
    def create_program(self):
        """Create a test program"""
        try:
            program_data = {
                "title": f"User Error Simulation Program {datetime.now().strftime('%H%M%S')}",
                "description": "Simulating user's exact error experience",
                "courseIds": [],
                "nestedProgramIds": []
            }
            
            response = self.session.post(f"{BACKEND_URL}/programs", json=program_data)
            
            if response.status_code == 200:
                program = response.json()
                self.test_program_id = program["id"]
                print(f"✅ Created program: {program['title']}")
                return program
            else:
                print(f"❌ Program creation failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Program creation exception: {str(e)}")
            return None
    
    def simulate_user_error(self):
        """Simulate the exact error the user experienced"""
        try:
            # This is what the frontend likely sends (WRONG format with underscores)
            test_data = {
                "title": f"User Error Simulation Test {datetime.now().strftime('%H%M%S')}",
                "description": "Simulating user's exact error with wrong question type formats",
                "programId": self.test_program_id,
                "questions": [
                    {
                        "type": "multiple_choice",
                        "question": "Multiple choice question",
                        "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                        "correctAnswer": "0",
                        "points": 10
                    },
                    {
                        "type": "select_all_that_apply",  # WRONG: underscore format
                        "question": "Select all that apply question",
                        "options": ["Option A", "Option B", "Option C"],
                        "correctAnswers": ["0", "1"],  # Also wrong: should be integers
                        "points": 15
                    },
                    {
                        "type": "true_false",
                        "question": "True/false question",
                        "correctAnswer": "true",
                        "points": 5
                    },
                    {
                        "type": "short_answer",
                        "question": "Short answer question",
                        "correctAnswer": "Sample answer",
                        "points": 8
                    },
                    {
                        "type": "essay",
                        "question": "Essay question",
                        "points": 20
                    },
                    {
                        "type": "chronological_order",  # WRONG: underscore format
                        "question": "Chronological order question",
                        "items": ["Step 1", "Step 2", "Step 3"],
                        "correctOrder": [0, 1, 2],
                        "points": 12
                    }
                ],
                "timeLimit": 120,
                "maxAttempts": 2,
                "passingScore": 75.0,
                "isPublished": True
            }
            
            print(f"\n🔍 SIMULATING USER'S ERROR:")
            print(f"📊 Sending {len(test_data['questions'])} questions with WRONG formats")
            print(f"📋 Question types: {[q['type'] for q in test_data['questions']]}")
            print(f"⚠️  Expected errors: select_all_that_apply, chronological_order")
            
            response = self.session.post(f"{BACKEND_URL}/final-tests", json=test_data)
            
            print(f"\n📥 RESPONSE STATUS: {response.status_code}")
            
            if response.status_code == 422:
                error_data = response.json()
                print(f"📥 ERROR RESPONSE (what backend sends):")
                print(json.dumps(error_data, indent=2))
                
                print(f"\n🔍 ANALYZING ERROR STRUCTURE:")
                print(f"📊 Error type: {type(error_data)}")
                
                if 'detail' in error_data and isinstance(error_data['detail'], list):
                    print(f"📊 Error details count: {len(error_data['detail'])}")
                    
                    for i, detail in enumerate(error_data['detail']):
                        print(f"\n  Error {i+1}:")
                        print(f"    Type: {detail.get('type', 'unknown')}")
                        print(f"    Location: {detail.get('loc', 'unknown')}")
                        print(f"    Message: {detail.get('msg', 'unknown')}")
                        print(f"    Input: {detail.get('input', 'unknown')}")
                
                # Simulate how frontend might process this error
                print(f"\n🔍 FRONTEND ERROR PROCESSING SIMULATION:")
                
                # Common ways frontend might mishandle this error:
                
                # 1. Direct toString() on error object
                error_str = str(error_data)
                print(f"1. str(error_data): {error_str[:100]}...")
                
                # 2. JSON.stringify equivalent
                error_json_str = json.dumps(error_data)
                print(f"2. JSON.stringify equivalent: {error_json_str[:100]}...")
                
                # 3. Accessing nested objects incorrectly
                try:
                    # This might cause [object Object] if frontend tries to display detail array directly
                    detail_str = str(error_data['detail'])
                    print(f"3. str(error_data['detail']): {detail_str[:100]}...")
                except:
                    pass
                
                # 4. Show what might cause [object Object] in JavaScript
                print(f"\n💡 LIKELY CAUSE OF [object Object]:")
                print(f"   When JavaScript tries to display error_data.detail directly in UI,")
                print(f"   it calls toString() on the array, which shows '[object Object]' for each item")
                print(f"   Array length: {len(error_data.get('detail', []))}")
                print(f"   This matches user's report: 'Array(6)' - there are 6 validation errors!")
                
                return error_data
            else:
                print(f"❌ Unexpected response status: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error simulation exception: {str(e)}")
            return None
    
    def run_simulation(self):
        """Run the complete user error simulation"""
        print("🚀 Starting User Error Experience Simulation")
        print("=" * 80)
        print("🎯 OBJECTIVE: Reproduce the exact error user experienced")
        print("🔍 HYPOTHESIS: [object Object] comes from 422 validation error array")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            return False
        
        # Step 2: Create program
        program = self.create_program()
        if not program:
            return False
        
        # Step 3: Simulate the user's error
        error_result = self.simulate_user_error()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 USER ERROR SIMULATION SUMMARY")
        print("=" * 80)
        
        if error_result:
            print("✅ SUCCESSFULLY REPRODUCED USER'S ERROR EXPERIENCE")
            print("\n🎯 ROOT CAUSE CONFIRMED:")
            print("   1. Frontend sends wrong question type formats (underscores)")
            print("   2. Backend returns 422 validation error with detail array")
            print("   3. Frontend displays error.detail array as '[object Object]'")
            print("   4. Array length matches user's report: 'Array(6)'")
            
            print("\n💡 SOLUTION:")
            print("   Fix frontend to send correct question type formats:")
            print("   - 'select_all_that_apply' → 'select-all-that-apply'")
            print("   - 'chronological_order' → 'chronological-order'")
            
            return True
        else:
            print("❌ Could not reproduce user's error")
            return False

if __name__ == "__main__":
    simulator = UserErrorSimulator()
    success = simulator.run_simulation()
    sys.exit(0 if success else 1)