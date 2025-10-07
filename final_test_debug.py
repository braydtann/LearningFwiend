#!/usr/bin/env python3
"""
Final Test Debug - Specific Investigation
========================================

This test specifically investigates the final test data structure
to understand the question type mismatch issue.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://quiz-progress-fix.preview.emergentagent.com/api"

# Test credentials
STUDENT_EMAIL = "karlo.student@alder.com"
STUDENT_PASSWORD = "StudentPermanent123!"

class FinalTestDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.student_id = None
        
    def login_student(self):
        """Login with student credentials"""
        print("🔐 Logging in as student...")
        
        login_data = {
            "username_or_email": STUDENT_EMAIL,
            "password": STUDENT_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.student_id = data["user"]["id"]
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"✅ Student login successful - {data['user']['full_name']}")
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def get_final_test_data(self):
        """Get final test data and analyze structure"""
        print("\n🎯 Getting final test data...")
        
        # First get programs to find program ID
        try:
            response = self.session.get(f"{BACKEND_URL}/programs")
            if response.status_code == 200:
                programs = response.json()
                print(f"Found {len(programs)} programs")
                
                for program in programs:
                    program_id = program['id']
                    print(f"\n📋 Checking program: {program['title']} (ID: {program_id})")
                    
                    # Try to get final test for this program
                    final_test_response = self.session.get(f"{BACKEND_URL}/final-tests?program_id={program_id}")
                    print(f"Final test response status: {final_test_response.status_code}")
                    
                    if final_test_response.status_code == 200:
                        final_tests = final_test_response.json()
                        
                        if final_tests:
                            print(f"✅ Found {len(final_tests)} final test(s)")
                            
                            for test in final_tests:
                                print(f"\n🔍 FINAL TEST ANALYSIS:")
                                print(f"Test ID: {test.get('id', 'No ID')}")
                                print(f"Title: {test.get('title', 'No title')}")
                                print(f"Program ID: {test.get('programId', 'No program ID')}")
                                
                                # Analyze questions structure
                                questions = test.get('questions', [])
                                print(f"Questions found: {len(questions)}")
                                
                                if questions:
                                    print(f"\n📝 QUESTION STRUCTURE ANALYSIS:")
                                    
                                    for i, question in enumerate(questions):
                                        print(f"\n   Question {i+1}:")
                                        print(f"   Raw JSON: {json.dumps(question, indent=6)}")
                                        
                                        # Analyze specific fields
                                        q_type = question.get('type', 'NO_TYPE')
                                        print(f"   Type: '{q_type}'")
                                        
                                        # Check all fields present
                                        print(f"   All fields: {list(question.keys())}")
                                        
                                        # Type-specific analysis
                                        if q_type == 'chronological-order':
                                            items = question.get('items', [])
                                            correct_order = question.get('correctOrder', [])
                                            print(f"   Items count: {len(items)}")
                                            print(f"   Items: {items}")
                                            print(f"   Correct order: {correct_order}")
                                        
                                        elif q_type == 'multiple-choice':
                                            options = question.get('options', [])
                                            correct_answer = question.get('correctAnswer')
                                            print(f"   Options count: {len(options)}")
                                            print(f"   Options: {options}")
                                            print(f"   Correct answer: {correct_answer}")
                                        
                                        elif q_type == 'select-all-that-apply':
                                            options = question.get('options', [])
                                            correct_answers = question.get('correctAnswers', [])
                                            print(f"   Options count: {len(options)}")
                                            print(f"   Options: {options}")
                                            print(f"   Correct answers: {correct_answers}")
                                
                                # Test the actual final test access endpoint
                                print(f"\n🚀 Testing final test access...")
                                test_id = test.get('id')
                                if test_id:
                                    test_access_response = self.session.get(f"{BACKEND_URL}/final-tests/{test_id}")
                                    print(f"Final test access status: {test_access_response.status_code}")
                                    
                                    if test_access_response.status_code == 200:
                                        test_data = test_access_response.json()
                                        print(f"✅ Final test accessible")
                                        print(f"Questions in response: {len(test_data.get('questions', []))}")
                                        
                                        # Compare question structure
                                        response_questions = test_data.get('questions', [])
                                        if response_questions:
                                            print(f"\n🔍 RESPONSE QUESTION ANALYSIS:")
                                            for i, q in enumerate(response_questions):
                                                print(f"   Response Question {i+1} type: '{q.get('type', 'NO_TYPE')}'")
                                                print(f"   Response Question {i+1} fields: {list(q.keys())}")
                                    else:
                                        print(f"❌ Final test access failed: {test_access_response.text}")
                        else:
                            print(f"⚠️ No final tests found for program {program['title']}")
                    else:
                        print(f"❌ Failed to get final tests: {final_test_response.text}")
            else:
                print(f"❌ Failed to get programs: {response.text}")
                
        except Exception as e:
            print(f"❌ Error getting final test data: {str(e)}")
    
    def test_frontend_expectations(self):
        """Test what the frontend expects vs what backend provides"""
        print(f"\n🎨 FRONTEND EXPECTATIONS ANALYSIS:")
        
        frontend_expected_types = [
            'multiple-choice', 'select-all-that-apply', 'chronological-order', 
            'true-false', 'short-answer', 'long-form'
        ]
        
        print(f"Frontend expects these question types:")
        for q_type in frontend_expected_types:
            print(f"   - '{q_type}'")
        
        print(f"\nFrontend component likely has switch/case statements expecting these exact strings.")
        print(f"If backend returns different strings (like 'chronological_order' instead of 'chronological-order'),")
        print(f"the frontend will show 'Unsupported question type' error.")
    
    def run_debug(self):
        """Run the complete debug analysis"""
        print("🚀 FINAL TEST DEBUG ANALYSIS")
        print("=" * 50)
        
        if not self.login_student():
            return False
        
        self.get_final_test_data()
        self.test_frontend_expectations()
        
        return True

def main():
    """Main function"""
    debugger = FinalTestDebugger()
    success = debugger.run_debug()
    
    if success:
        print(f"\n✅ Final test debug completed")
        return 0
    else:
        print(f"\n❌ Final test debug failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())