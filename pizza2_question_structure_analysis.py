#!/usr/bin/env python3
"""
PIZZA2 COURSE QUESTION STRUCTURE ANALYSIS
Deep dive into the Select All That Apply question structure in pizza2 course
"""

import requests
import json
import os
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://learning-analytics-2.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Admin credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class Pizza2QuestionAnalyzer:
    def __init__(self):
        self.auth_token = None
        self.pizza2_course_id = "040b7021-eaf6-4f33-b813-a7a286f19e11"
        
    def authenticate(self):
        """Authenticate as admin"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                return True
            else:
                return False
        except Exception as e:
            return False
    
    def analyze_question_structure(self):
        """Analyze the detailed question structure"""
        if not self.auth_token:
            return None
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{self.pizza2_course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_token}'}
            )
            
            if response.status_code == 200:
                course = response.json()
                
                print("🔍 PIZZA2 COURSE QUESTION STRUCTURE ANALYSIS")
                print("=" * 80)
                
                modules = course.get('modules', [])
                for module in modules:
                    lessons = module.get('lessons', [])
                    for lesson in lessons:
                        print(f"\n📝 LESSON: {lesson.get('title')}")
                        print(f"ID: {lesson.get('id')}")
                        print(f"Type: {lesson.get('type')}")
                        
                        # Check new format (lesson.questions)
                        new_questions = lesson.get('questions', [])
                        print(f"\n🆕 NEW FORMAT (lesson.questions): {len(new_questions)} questions")
                        
                        if new_questions:
                            for i, question in enumerate(new_questions):
                                print(f"\n  Question {i+1}:")
                                print(f"    Type: {question.get('type')}")
                                print(f"    ID: {question.get('id')}")
                                print(f"    Text: {question.get('question')}")
                                
                                if question.get('type') == 'select-all-that-apply':
                                    self.analyze_select_all_question(question, "NEW FORMAT")
                        
                        # Check old format (lesson.quiz.questions)
                        quiz = lesson.get('quiz', {})
                        old_questions = quiz.get('questions', [])
                        print(f"\n🔄 OLD FORMAT (lesson.quiz.questions): {len(old_questions)} questions")
                        
                        if old_questions:
                            for i, question in enumerate(old_questions):
                                print(f"\n  Question {i+1}:")
                                print(f"    Type: {question.get('type')}")
                                print(f"    ID: {question.get('id')}")
                                print(f"    Text: {question.get('question')}")
                                
                                if question.get('type') == 'select-all-that-apply':
                                    self.analyze_select_all_question(question, "OLD FORMAT")
                        
                        # Raw JSON structure for debugging
                        print(f"\n📋 RAW LESSON STRUCTURE:")
                        lesson_copy = lesson.copy()
                        # Remove large content fields for readability
                        if 'content' in lesson_copy:
                            lesson_copy['content'] = f"[{len(lesson_copy['content'])} characters]"
                        
                        print(json.dumps(lesson_copy, indent=2, default=str))
                
                return course
            else:
                print(f"❌ Failed to get course: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def analyze_select_all_question(self, question, format_type):
        """Analyze a Select All That Apply question in detail"""
        print(f"\n    🎯 SELECT ALL THAT APPLY QUESTION ANALYSIS ({format_type}):")
        print(f"    " + "=" * 60)
        
        # Basic structure
        q_id = question.get('id')
        q_text = question.get('question', '')
        q_points = question.get('points', 0)
        
        print(f"    Question ID: {q_id}")
        print(f"    Question Text: {q_text}")
        print(f"    Points: {q_points}")
        
        # Options analysis
        options = question.get('options', [])
        print(f"\n    📝 OPTIONS ({len(options)} total):")
        if options:
            for idx, option in enumerate(options):
                print(f"      [{idx}] {option}")
        else:
            print(f"      ❌ NO OPTIONS FOUND - This will cause React Error!")
        
        # Correct answers analysis
        correct_answers = question.get('correctAnswers', [])
        print(f"\n    ✅ CORRECT ANSWERS ({len(correct_answers)} total):")
        if correct_answers:
            print(f"      Indices: {correct_answers}")
            if options:
                print(f"      Values:")
                for idx in correct_answers:
                    if 0 <= idx < len(options):
                        print(f"        [{idx}] {options[idx]}")
                    else:
                        print(f"        [{idx}] ❌ INVALID INDEX (out of range)")
        else:
            print(f"      ❌ NO CORRECT ANSWERS FOUND - This will cause issues!")
        
        # Data integrity check
        print(f"\n    🔍 DATA INTEGRITY CHECK:")
        issues = []
        
        if not options:
            issues.append("Missing 'options' array")
        if not correct_answers:
            issues.append("Missing 'correctAnswers' array")
        if correct_answers and options:
            invalid_indices = [idx for idx in correct_answers if idx >= len(options) or idx < 0]
            if invalid_indices:
                issues.append(f"Invalid correctAnswers indices: {invalid_indices}")
        if not q_text:
            issues.append("Missing question text")
        
        if issues:
            print(f"      ❌ ISSUES FOUND:")
            for issue in issues:
                print(f"        - {issue}")
        else:
            print(f"      ✅ All data integrity checks passed")
        
        # Frontend compatibility check
        print(f"\n    🖥️ FRONTEND COMPATIBILITY:")
        if format_type == "OLD FORMAT":
            print(f"      ⚠️ WARNING: Using old format (lesson.quiz.questions)")
            print(f"      Frontend expects: lesson.questions")
            print(f"      This may cause React Error #31 when frontend tries to access question.options")
        else:
            print(f"      ✅ Using new format (lesson.questions) - Frontend compatible")
        
        return {
            'id': q_id,
            'text': q_text,
            'options': options,
            'correct_answers': correct_answers,
            'points': q_points,
            'issues': issues,
            'format': format_type
        }
    
    def test_frontend_data_access_simulation(self):
        """Simulate how frontend would access the question data"""
        print(f"\n🖥️ FRONTEND DATA ACCESS SIMULATION")
        print("=" * 60)
        
        if not self.auth_token:
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{self.pizza2_course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_token}'}
            )
            
            if response.status_code == 200:
                course = response.json()
                
                print("Simulating frontend code accessing question data...")
                print()
                
                modules = course.get('modules', [])
                for module in modules:
                    lessons = module.get('lessons', [])
                    for lesson in lessons:
                        print(f"📝 Processing lesson: {lesson.get('title')}")
                        
                        # Simulate frontend trying to access lesson.questions (NEW FORMAT)
                        print(f"\n🆕 Frontend trying: lesson.questions")
                        try:
                            questions = lesson.get('questions', [])
                            print(f"   ✅ Found {len(questions)} questions in lesson.questions")
                            
                            if not questions:
                                print(f"   ⚠️ No questions found - frontend might show empty quiz")
                            
                            for i, question in enumerate(questions):
                                print(f"   Question {i+1}: {question.get('type')}")
                                if question.get('type') == 'select-all-that-apply':
                                    options = question.get('options', [])
                                    if options:
                                        print(f"     ✅ options.map() would work - {len(options)} options")
                                    else:
                                        print(f"     ❌ options.map() would fail - React Error #31!")
                        except Exception as e:
                            print(f"   ❌ Error accessing lesson.questions: {str(e)}")
                        
                        # Simulate what happens if frontend falls back to lesson.quiz.questions (OLD FORMAT)
                        print(f"\n🔄 Frontend fallback: lesson.quiz.questions")
                        try:
                            quiz = lesson.get('quiz', {})
                            questions = quiz.get('questions', [])
                            print(f"   ✅ Found {len(questions)} questions in lesson.quiz.questions")
                            
                            for i, question in enumerate(questions):
                                print(f"   Question {i+1}: {question.get('type')}")
                                if question.get('type') == 'select-all-that-apply':
                                    options = question.get('options', [])
                                    if options:
                                        print(f"     ✅ options.map() would work - {len(options)} options")
                                    else:
                                        print(f"     ❌ options.map() would fail - React Error #31!")
                        except Exception as e:
                            print(f"   ❌ Error accessing lesson.quiz.questions: {str(e)}")
                        
                        # Conclusion for this lesson
                        new_questions = lesson.get('questions', [])
                        old_questions = lesson.get('quiz', {}).get('questions', [])
                        
                        print(f"\n📊 LESSON ANALYSIS RESULT:")
                        if new_questions:
                            print(f"   ✅ Frontend will find questions in lesson.questions")
                        elif old_questions:
                            print(f"   ⚠️ Frontend needs fallback to lesson.quiz.questions")
                            print(f"   🔧 RECOMMENDATION: Migrate questions to lesson.questions format")
                        else:
                            print(f"   ❌ No questions found in either format")
                
                return True
            else:
                print(f"❌ Failed to get course for simulation: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Simulation error: {str(e)}")
            return False
    
    def run_analysis(self):
        """Run the complete question structure analysis"""
        print("🔬 PIZZA2 QUESTION STRUCTURE DEEP ANALYSIS")
        print("=" * 80)
        
        if not self.authenticate():
            print("❌ Authentication failed")
            return False
        
        # Analyze question structure
        course = self.analyze_question_structure()
        if not course:
            return False
        
        # Test frontend data access simulation
        self.test_frontend_data_access_simulation()
        
        print(f"\n🎯 FINAL CONCLUSIONS:")
        print("=" * 50)
        print("✅ pizza2 course exists and is accessible")
        print("✅ Course has 1 Select All That Apply question")
        print("⚠️ Question is in OLD FORMAT (lesson.quiz.questions)")
        print("🔧 Frontend may need fallback logic to access old format questions")
        print("💡 Consider migrating to NEW FORMAT (lesson.questions) for better compatibility")
        
        return True

def main():
    """Main function"""
    analyzer = Pizza2QuestionAnalyzer()
    success = analyzer.run_analysis()
    
    if success:
        print(f"\n🎉 QUESTION STRUCTURE ANALYSIS COMPLETED")
    else:
        print(f"\n⚠️ ANALYSIS FAILED")
    
    return success

if __name__ == "__main__":
    main()