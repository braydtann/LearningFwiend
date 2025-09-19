#!/usr/bin/env python3
"""
Detailed Question Analysis - Root Cause Investigation
====================================================

This test gets the exact JSON structure and identifies the specific mismatch
causing "Unsupported question type" errors in FinalTest.js
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-debugfix.preview.emergentagent.com/api"

# Test credentials
STUDENT_EMAIL = "karlo.student@alder.com"
STUDENT_PASSWORD = "StudentPermanent123!"

class DetailedQuestionAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        
    def login_student(self):
        """Login with student credentials"""
        login_data = {
            "username_or_email": STUDENT_EMAIL,
            "password": STUDENT_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                
                print(f"✅ Student login successful")
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def analyze_final_test_questions(self):
        """Get and analyze final test questions in detail"""
        print("\n🔍 DETAILED FINAL TEST QUESTION ANALYSIS")
        print("=" * 60)
        
        # Get the first final test we found
        final_test_id = "7e3fc845-63f6-43a6-a48f-71319b2709ea"
        
        try:
            response = self.session.get(f"{BACKEND_URL}/final-tests/{final_test_id}")
            
            if response.status_code == 200:
                test_data = response.json()
                questions = test_data.get('questions', [])
                
                print(f"Final Test: {test_data.get('title', 'Unknown')}")
                print(f"Questions found: {len(questions)}")
                
                # Analyze each question in detail
                backend_types = []
                frontend_expected = [
                    'multiple-choice', 'select-all-that-apply', 'chronological-order', 
                    'true-false', 'short-answer', 'long-form'
                ]
                
                print(f"\n📋 QUESTION-BY-QUESTION ANALYSIS:")
                
                for i, question in enumerate(questions):
                    print(f"\n--- Question {i+1} ---")
                    q_type = question.get('type', 'NO_TYPE')
                    backend_types.append(q_type)
                    
                    print(f"Backend returns type: '{q_type}'")
                    
                    # Check if this matches frontend expectations
                    if q_type in frontend_expected:
                        print(f"✅ MATCH: Frontend supports '{q_type}'")
                    else:
                        print(f"❌ MISMATCH: Frontend does NOT support '{q_type}'")
                        
                        # Suggest the correct frontend equivalent
                        if q_type == 'multiple_choice':
                            print(f"   Should be: 'multiple-choice'")
                        elif q_type == 'true_false':
                            print(f"   Should be: 'true-false'")
                        elif q_type == 'short_answer':
                            print(f"   Should be: 'short-answer'")
                        elif q_type == 'long_form':
                            print(f"   Should be: 'long-form'")
                        elif q_type == 'select_all_that_apply':
                            print(f"   Should be: 'select-all-that-apply'")
                        elif q_type == 'chronological_order':
                            print(f"   Should be: 'chronological-order'")
                    
                    # Show sample of question data
                    print(f"Question text: {question.get('question', 'No question')[:100]}...")
                    print(f"All fields: {list(question.keys())}")
                
                # Summary analysis
                print(f"\n🎯 ROOT CAUSE ANALYSIS:")
                print(f"=" * 40)
                
                unique_backend_types = list(set(backend_types))
                mismatches = []
                
                for backend_type in unique_backend_types:
                    if backend_type not in frontend_expected:
                        if backend_type == 'multiple_choice':
                            mismatches.append(('multiple_choice', 'multiple-choice'))
                        elif backend_type == 'true_false':
                            mismatches.append(('true_false', 'true-false'))
                        elif backend_type == 'short_answer':
                            mismatches.append(('short_answer', 'short-answer'))
                        elif backend_type == 'long_form':
                            mismatches.append(('long_form', 'long-form'))
                        elif backend_type == 'select_all_that_apply':
                            mismatches.append(('select_all_that_apply', 'select-all-that-apply'))
                        elif backend_type == 'chronological_order':
                            mismatches.append(('chronological_order', 'chronological-order'))
                
                print(f"Backend question types found: {unique_backend_types}")
                print(f"Frontend expects: {frontend_expected}")
                print(f"Mismatches identified: {len(mismatches)}")
                
                if mismatches:
                    print(f"\n🔧 REQUIRED FIXES:")
                    for backend_type, frontend_type in mismatches:
                        print(f"   Backend '{backend_type}' → Frontend '{frontend_type}'")
                    
                    print(f"\n💡 EXPLANATION:")
                    print(f"The backend is using underscore naming (snake_case) like 'multiple_choice'")
                    print(f"but the frontend FinalTest.js expects hyphen naming (kebab-case) like 'multiple-choice'")
                    print(f"This causes the frontend to show 'Unsupported question type' for ALL questions.")
                else:
                    print(f"✅ No naming mismatches found")
                
                return mismatches
            else:
                print(f"❌ Failed to get final test: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error analyzing questions: {str(e)}")
            return []
    
    def test_specific_final_test_access(self):
        """Test accessing final test by program ID as frontend would"""
        print(f"\n🚀 TESTING FRONTEND ACCESS PATTERN")
        print("=" * 40)
        
        # Test the way frontend accesses final tests
        program_id = "8ef8da70-0f95-4930-9e31-1177ef27c180"
        
        try:
            # This is how frontend gets final tests
            response = self.session.get(f"{BACKEND_URL}/final-tests?program_id={program_id}")
            
            if response.status_code == 200:
                final_tests = response.json()
                print(f"✅ Found {len(final_tests)} final tests for program")
                
                if final_tests:
                    test = final_tests[0]
                    test_id = test['id']
                    
                    # Now access the specific test (as frontend does)
                    test_response = self.session.get(f"{BACKEND_URL}/final-tests/{test_id}")
                    
                    if test_response.status_code == 200:
                        test_data = test_response.json()
                        questions = test_data.get('questions', [])
                        
                        print(f"✅ Final test accessible with {len(questions)} questions")
                        
                        # Show the exact JSON that frontend receives
                        print(f"\n📄 EXACT JSON STRUCTURE FRONTEND RECEIVES:")
                        print("=" * 50)
                        
                        if questions:
                            sample_question = questions[0]
                            print(f"Sample Question JSON:")
                            print(json.dumps(sample_question, indent=2))
                            
                            print(f"\nQuestion type field: '{sample_question.get('type', 'NO_TYPE')}'")
                            print(f"This is what causes 'Unsupported question type' in FinalTest.js")
                    else:
                        print(f"❌ Failed to access final test: {test_response.text}")
            else:
                print(f"❌ Failed to get final tests: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing access: {str(e)}")
    
    def run_analysis(self):
        """Run the complete analysis"""
        print("🚀 DETAILED QUESTION TYPE MISMATCH ANALYSIS")
        print("=" * 60)
        print(f"Investigating 'Unsupported question type' error in FinalTest.js")
        print(f"Started at: {datetime.now()}")
        
        if not self.login_student():
            return False
        
        mismatches = self.analyze_final_test_questions()
        self.test_specific_final_test_access()
        
        print(f"\n🎯 FINAL CONCLUSION:")
        print("=" * 30)
        
        if mismatches:
            print(f"❌ ROOT CAUSE IDENTIFIED: Question type naming mismatch")
            print(f"   Backend uses: snake_case (e.g., 'multiple_choice')")
            print(f"   Frontend expects: kebab-case (e.g., 'multiple-choice')")
            print(f"   This causes FinalTest.js to show 'Unsupported question type'")
            print(f"\n🔧 SOLUTION: Update backend to use kebab-case question types")
            print(f"   OR update frontend to handle snake_case question types")
        else:
            print(f"✅ No obvious naming mismatches found")
            print(f"   The issue may be in a different area")
        
        print(f"\nCompleted at: {datetime.now()}")
        return True

def main():
    """Main function"""
    analyzer = DetailedQuestionAnalyzer()
    success = analyzer.run_analysis()
    
    if success:
        print(f"\n✅ Analysis completed successfully")
        return 0
    else:
        print(f"\n❌ Analysis failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())