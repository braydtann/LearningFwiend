#!/usr/bin/env python3
"""
Detailed Verification Test - Inspect the created final test to ensure all data structures are correct
"""

import requests
import json
import sys

# Configuration
BACKEND_URL = "https://lms-progression.preview.emergentagent.com/api"
ADMIN_EMAIL = "brayden.t@covesmart.com"
ADMIN_PASSWORD = "Hawaii2020!"

def main():
    session = requests.Session()
    
    # Login
    print("🔐 Logging in as admin...")
    response = session.post(f"{BACKEND_URL}/auth/login", json={
        "username_or_email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    # Get all final tests
    print("\n📋 Getting all final tests...")
    response = session.get(f"{BACKEND_URL}/final-tests")
    
    if response.status_code != 200:
        print(f"❌ Failed to get final tests: {response.status_code}")
        return
    
    tests = response.json()
    
    # Find our test
    target_test = None
    for test in tests:
        if "Comprehensive Final Test - All Question Types" in test.get("title", ""):
            target_test = test
            break
    
    if not target_test:
        print("❌ Could not find our test")
        return
    
    print(f"✅ Found test: {target_test['title']} (ID: {target_test['id']})")
    
    # Get detailed test with questions
    print(f"\n🔍 Getting detailed test data...")
    response = session.get(f"{BACKEND_URL}/final-tests/{target_test['id']}")
    
    if response.status_code != 200:
        print(f"❌ Failed to get test details: {response.status_code}")
        return
    
    detailed_test = response.json()
    questions = detailed_test.get("questions", [])
    
    print(f"✅ Retrieved test with {len(questions)} questions")
    
    # Analyze each question
    print("\n📊 DETAILED QUESTION ANALYSIS:")
    print("=" * 80)
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. Question Type: {question.get('type')}")
        print(f"   Question: {question.get('question')[:50]}...")
        print(f"   Points: {question.get('points')}")
        
        q_type = question.get('type')
        
        if q_type == "multiple_choice":
            print(f"   Options: {question.get('options', [])}")
            print(f"   Correct Answer: {question.get('correctAnswer')} (type: {type(question.get('correctAnswer'))})")
            
        elif q_type == "select-all-that-apply":
            print(f"   Options: {question.get('options', [])}")
            print(f"   Correct Answers: {question.get('correctAnswers')} (type: {type(question.get('correctAnswers'))})")
            
        elif q_type == "true_false":
            print(f"   Correct Answer: {question.get('correctAnswer')} (type: {type(question.get('correctAnswer'))})")
            
        elif q_type == "chronological-order":
            print(f"   Items: {question.get('items', [])}")
            print(f"   Correct Order: {question.get('correctOrder')} (type: {type(question.get('correctOrder'))})")
            
        elif q_type in ["short_answer", "essay"]:
            correct_answer = question.get('correctAnswer')
            if correct_answer:
                print(f"   Correct Answer: {correct_answer[:30]}... (type: {type(correct_answer)})")
            else:
                print(f"   Correct Answer: None (essay questions don't need correct answers)")
    
    print("\n" + "=" * 80)
    print("🎯 VALIDATION SUMMARY:")
    
    # Check for issues
    issues = []
    
    for question in questions:
        q_type = question.get('type')
        q_id = question.get('id', 'unknown')[:8]
        
        if q_type == "multiple_choice":
            if not question.get('correctAnswer'):
                issues.append(f"Multiple choice question {q_id} missing correctAnswer")
            elif not isinstance(question.get('correctAnswer'), str):
                issues.append(f"Multiple choice question {q_id} correctAnswer should be string")
                
        elif q_type == "select-all-that-apply":
            if not question.get('correctAnswers'):
                issues.append(f"Select-all-that-apply question {q_id} missing correctAnswers")
            elif not isinstance(question.get('correctAnswers'), list):
                issues.append(f"Select-all-that-apply question {q_id} correctAnswers should be list")
                
        elif q_type == "true_false":
            if not question.get('correctAnswer'):
                issues.append(f"True/false question {q_id} missing correctAnswer")
            elif question.get('correctAnswer') not in ["true", "false"]:
                issues.append(f"True/false question {q_id} correctAnswer should be 'true' or 'false'")
                
        elif q_type == "chronological-order":
            if not question.get('items'):
                issues.append(f"Chronological order question {q_id} missing items array")
            elif not question.get('correctOrder'):
                issues.append(f"Chronological order question {q_id} missing correctOrder")
                
        elif q_type == "short_answer":
            if not question.get('correctAnswer'):
                issues.append(f"Short answer question {q_id} missing correctAnswer")
    
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"   • {issue}")
    else:
        print("✅ ALL QUESTIONS HAVE PROPER DATA STRUCTURES!")
    
    # Check for [object Object] in the JSON
    json_str = json.dumps(detailed_test)
    if "[object Object]" in json_str:
        print("❌ [object Object] found in response!")
    else:
        print("✅ No [object Object] errors in response!")
    
    print(f"\n🎉 FINAL VERIFICATION COMPLETE")
    print(f"   Total Questions: {len(questions)}")
    print(f"   Issues Found: {len(issues)}")
    print(f"   Success Rate: {((len(questions) - len(issues)) / len(questions) * 100):.1f}%")

if __name__ == "__main__":
    main()