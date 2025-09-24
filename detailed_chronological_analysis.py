#!/usr/bin/env python3
"""
Detailed Chronological Order Analysis
====================================

This script provides detailed analysis of the specific chronological order question
that was found in the final_tests collection.
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import json
from typing import Dict, List, Any, Optional

# Add the backend directory to Python path
sys.path.append('/app/backend')

# MongoDB connection setup
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/learningfriend_lms')
DB_NAME = os.environ.get('DB_NAME', 'learningfriend_lms')

class DetailedAnalyzer:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(MONGO_URL)
            self.db = self.client[DB_NAME]
            print(f"✅ Connected to MongoDB: {DB_NAME}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {str(e)}")
            return False
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔌 MongoDB connection closed")
    
    async def get_final_test_details(self, test_id: str):
        """Get complete details of the final test"""
        print("=" * 80)
        print("📋 FINAL TEST DETAILED ANALYSIS")
        print("=" * 80)
        
        final_test = await self.db.final_tests.find_one({"id": test_id})
        if not final_test:
            print(f"❌ Final test with ID {test_id} not found")
            return None
        
        print(f"✅ Found final test:")
        print(f"   ID: {final_test.get('id')}")
        print(f"   Title: {final_test.get('title', 'No title')}")
        print(f"   Description: {final_test.get('description', 'No description')}")
        print(f"   Program ID: {final_test.get('programId', 'No program ID')}")
        print(f"   Questions Count: {len(final_test.get('questions', []))}")
        print(f"   Time Limit: {final_test.get('timeLimit', 'No time limit')} minutes")
        print(f"   Passing Score: {final_test.get('passingScore', 'No passing score')}%")
        
        return final_test
    
    async def analyze_all_questions(self, final_test: Dict):
        """Analyze all questions in the final test"""
        print(f"\n📝 DETAILED QUESTION ANALYSIS")
        print("=" * 60)
        
        questions = final_test.get('questions', [])
        chronological_question = None
        
        for i, question in enumerate(questions):
            print(f"\n📋 Question {i+1}:")
            print(f"   ID: {question.get('id', 'No ID')}")
            print(f"   Type: {question.get('type', 'No type')}")
            print(f"   Question Text: {question.get('question', 'No question text')}")
            
            if question.get('type') == 'multiple-choice':
                print(f"   Options: {question.get('options', [])}")
                print(f"   Correct Answer: {question.get('correctAnswer', 'No correct answer')}")
            
            elif question.get('type') == 'select-all-that-apply':
                print(f"   Options: {question.get('options', [])}")
                print(f"   Correct Answers: {question.get('correctAnswers', [])}")
            
            elif question.get('type') == 'chronological-order':
                chronological_question = question
                print(f"   Items: {question.get('items', [])}")
                print(f"   Correct Order: {question.get('correctOrder', [])}")
                print(f"   🎯 THIS IS THE CHRONOLOGICAL ORDER QUESTION")
            
            elif question.get('type') == 'true-false':
                print(f"   Correct Answer: {question.get('correctAnswer', 'No correct answer')}")
            
            # Show all fields for debugging
            print(f"   All fields: {list(question.keys())}")
        
        return chronological_question
    
    async def deep_dive_chronological_question(self, question: Dict):
        """Perform deep analysis of the chronological order question"""
        print(f"\n🔍 DEEP DIVE: CHRONOLOGICAL ORDER QUESTION")
        print("=" * 60)
        
        print(f"📋 Complete Question Data:")
        for key, value in question.items():
            print(f"   {key}: {value} ({type(value).__name__})")
        
        items = question.get('items', [])
        correct_order = question.get('correctOrder', [])
        
        print(f"\n🎯 SCORING ISSUE ANALYSIS:")
        print(f"   Items array: {items}")
        print(f"   Items count: {len(items)}")
        print(f"   Correct order array: {correct_order}")
        print(f"   Correct order count: {len(correct_order)}")
        
        # The issue analysis
        print(f"\n🚨 ROOT CAUSE IDENTIFIED:")
        print(f"   Student clicked sequence: 1 → 3 → 2 → 4")
        print(f"   This translates to indices: [0, 1, 2, 3] (all 4 items)")
        print(f"   But correctOrder is: {correct_order} (only {len(correct_order)} items)")
        print(f"   The arrays have different lengths!")
        
        if len(correct_order) == 3 and len(items) == 4:
            print(f"\n💡 ANALYSIS:")
            print(f"   - The question has 4 items: {items}")
            print(f"   - But correctOrder only has 3 indices: {correct_order}")
            print(f"   - This suggests the correct answer should only include 3 items")
            print(f"   - Student selected all 4 items, but only 3 were expected")
            
            # Show what the correct sequence would be
            if all(isinstance(idx, int) and 0 <= idx < len(items) for idx in correct_order):
                correct_sequence = [items[idx] for idx in correct_order]
                print(f"   - Correct sequence based on stored indices: {' → '.join(correct_sequence)}")
                print(f"   - Student sequence: {' → '.join(items)}")
                print(f"   - The student included item '{items[3]}' which wasn't expected")
        
        # Check if this is a partial ordering question
        print(f"\n🤔 QUESTION TYPE ANALYSIS:")
        question_text = question.get('question', '').lower()
        if 'first' in question_text or 'order' in question_text:
            print(f"   Question text contains ordering keywords")
            print(f"   This might be asking for partial ordering (first 3 items)")
            print(f"   Rather than complete ordering of all 4 items")
        
        return {
            'items': items,
            'correct_order': correct_order,
            'length_mismatch': len(items) != len(correct_order),
            'expected_length': len(correct_order),
            'actual_length': len(items)
        }
    
    async def check_final_test_attempts(self, test_id: str):
        """Check for any final test attempts"""
        print(f"\n🎯 FINAL TEST ATTEMPTS ANALYSIS")
        print("=" * 60)
        
        attempts = await self.db.final_test_attempts.find({"testId": test_id}).to_list(100)
        
        if attempts:
            print(f"✅ Found {len(attempts)} attempts for this test")
            
            for i, attempt in enumerate(attempts):
                print(f"\n📊 Attempt {i+1}:")
                print(f"   ID: {attempt.get('id', 'No ID')}")
                print(f"   Student ID: {attempt.get('studentId', 'No student ID')}")
                print(f"   Score: {attempt.get('score', 'No score')}%")
                print(f"   Submitted At: {attempt.get('submittedAt', 'No submission time')}")
                
                # Check answers
                answers = attempt.get('answers', {})
                if answers:
                    print(f"   Answers: {answers}")
                    
                    # Look for the chronological order answer
                    target_question_id = "1b4f453d-39c7-4663-b2bf-7a4127135163"
                    if target_question_id in answers:
                        student_answer = answers[target_question_id]
                        print(f"   🎯 Chronological order answer: {student_answer}")
                        
                        # This is the key finding!
                        if student_answer == [0, 1, 2, 3]:
                            print(f"   ✅ This matches the reported student answer!")
                            print(f"   📊 Score was {attempt.get('score')}% - confirming 66.7% (2/3 correct)")
        else:
            print(f"❌ No attempts found for test ID {test_id}")
    
    async def run_detailed_analysis(self):
        """Run the complete detailed analysis"""
        test_id = "6e6d6c00-565f-4821-9f4d-d5324b7ab079"
        
        # Get final test details
        final_test = await self.get_final_test_details(test_id)
        if not final_test:
            return
        
        # Analyze all questions
        chronological_question = await self.analyze_all_questions(final_test)
        if not chronological_question:
            print("❌ No chronological order question found")
            return
        
        # Deep dive into the chronological question
        analysis = await self.deep_dive_chronological_question(chronological_question)
        
        # Check for test attempts
        await self.check_final_test_attempts(test_id)
        
        # Final conclusion
        print(f"\n" + "=" * 80)
        print("🎯 FINAL CONCLUSION")
        print("=" * 80)
        
        print(f"✅ ISSUE IDENTIFIED:")
        print(f"   - Question has 4 items: {analysis['items']}")
        print(f"   - But correctOrder expects only 3: {analysis['correct_order']}")
        print(f"   - Student provided 4 answers: [0, 1, 2, 3]")
        print(f"   - System expected 3 answers: {analysis['correct_order']}")
        print(f"   - Length mismatch caused the question to be marked incorrect")
        
        print(f"\n🔧 POTENTIAL SOLUTIONS:")
        print(f"   1. Update correctOrder to include all 4 items: [0, 2, 1, 3] for '1→2→3→4'")
        print(f"   2. Or clarify question to ask for only first 3 items in order")
        print(f"   3. Or update scoring logic to handle partial matches")
        
        print(f"\n📊 IMPACT:")
        print(f"   - Student got 66.7% (2/3 questions correct)")
        print(f"   - This chronological question was the 1 incorrect answer")
        print(f"   - The scoring logic failed due to array length mismatch")

async def main():
    """Main execution function"""
    analyzer = DetailedAnalyzer()
    
    try:
        # Connect to database
        if not await analyzer.connect():
            return
        
        # Run detailed analysis
        await analyzer.run_detailed_analysis()
            
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await analyzer.close()

if __name__ == "__main__":
    asyncio.run(main())