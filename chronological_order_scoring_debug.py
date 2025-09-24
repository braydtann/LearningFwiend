#!/usr/bin/env python3
"""
Chronological Order Question Scoring Debug Investigation
========================================================

This script investigates the specific chronological order question scoring issue
where a student got 66.7% on a 3-question final exam, indicating the chronological
order question was marked incorrect.

Investigation Focus:
- Test ID: 6e6d6c00-565f-4821-9f4d-d5324b7ab079
- Program ID: 9d606116-dcb5-4067-b11b-78132451ddb6  
- Question ID: 1b4f453d-39c7-4663-b2bf-7a4127135163
- Student answer: [0, 1, 2, 3] (clicked sequence: 1→3→2→4)
- Expected items: ["1", "3", "2", "4"]
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

class ChronologicalOrderDebugger:
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
    
    async def find_test_by_id(self, test_id: str) -> Optional[Dict]:
        """Find the specific test by ID"""
        print(f"\n🔍 Searching for test with ID: {test_id}")
        
        # Search in programs collection for final tests
        program = await self.db.programs.find_one({"finalTest.id": test_id})
        if program:
            print(f"✅ Found test in program: {program.get('title', 'Unknown')}")
            return program.get('finalTest')
        
        # Search in courses collection for quizzes
        course = await self.db.courses.find_one({"modules.lessons.id": test_id})
        if course:
            print(f"✅ Found test in course: {course.get('title', 'Unknown')}")
            # Find the specific lesson
            for module in course.get('modules', []):
                for lesson in module.get('lessons', []):
                    if lesson.get('id') == test_id:
                        return lesson
        
        print(f"❌ Test with ID {test_id} not found")
        return None
    
    async def find_program_by_id(self, program_id: str) -> Optional[Dict]:
        """Find the specific program by ID"""
        print(f"\n🔍 Searching for program with ID: {program_id}")
        
        program = await self.db.programs.find_one({"id": program_id})
        if program:
            print(f"✅ Found program: {program.get('title', 'Unknown')}")
            return program
        
        print(f"❌ Program with ID {program_id} not found")
        return None
    
    async def analyze_chronological_question(self, question: Dict, question_id: str) -> Dict:
        """Analyze a chronological order question structure"""
        print(f"\n📊 Analyzing chronological order question: {question_id}")
        
        analysis = {
            "question_id": question_id,
            "question_type": question.get('type', 'unknown'),
            "question_text": question.get('question', 'No question text'),
            "has_items": 'items' in question,
            "items": question.get('items', []),
            "has_correct_order": 'correctOrder' in question,
            "correct_order": question.get('correctOrder', []),
            "items_count": len(question.get('items', [])),
            "correct_order_count": len(question.get('correctOrder', [])),
            "data_structure": {}
        }
        
        # Detailed data structure analysis
        for key, value in question.items():
            analysis["data_structure"][key] = {
                "type": type(value).__name__,
                "value": value if not isinstance(value, (list, dict)) else f"{type(value).__name__} with {len(value)} items"
            }
        
        print(f"   Question Type: {analysis['question_type']}")
        print(f"   Question Text: {analysis['question_text'][:100]}...")
        print(f"   Has Items: {analysis['has_items']}")
        print(f"   Items: {analysis['items']}")
        print(f"   Has Correct Order: {analysis['has_correct_order']}")
        print(f"   Correct Order: {analysis['correct_order']}")
        
        return analysis
    
    async def simulate_scoring(self, question: Dict, student_answer: List[int]) -> Dict:
        """Simulate the scoring logic for chronological order question"""
        print(f"\n🎯 Simulating scoring for student answer: {student_answer}")
        
        items = question.get('items', [])
        correct_order = question.get('correctOrder', [])
        
        scoring_result = {
            "student_answer": student_answer,
            "student_sequence": [],
            "correct_order": correct_order,
            "items": items,
            "scoring_method": "unknown",
            "is_correct": False,
            "score": 0.0,
            "explanation": ""
        }
        
        # Convert student answer indices to actual items
        if items and all(0 <= idx < len(items) for idx in student_answer):
            scoring_result["student_sequence"] = [items[idx] for idx in student_answer]
        
        # Method 1: Direct array comparison
        if student_answer == correct_order:
            scoring_result["scoring_method"] = "direct_array_comparison"
            scoring_result["is_correct"] = True
            scoring_result["score"] = 100.0
            scoring_result["explanation"] = "Student answer matches correctOrder array exactly"
        
        # Method 2: Item sequence comparison
        elif scoring_result["student_sequence"] and correct_order:
            if scoring_result["student_sequence"] == correct_order:
                scoring_result["scoring_method"] = "item_sequence_comparison"
                scoring_result["is_correct"] = True
                scoring_result["score"] = 100.0
                scoring_result["explanation"] = "Student sequence matches correct item sequence"
        
        # Method 3: Check if correctOrder contains indices instead of items
        if not scoring_result["is_correct"] and correct_order:
            try:
                # If correctOrder contains indices, convert to items for comparison
                if all(isinstance(x, int) and 0 <= x < len(items) for x in correct_order):
                    correct_sequence = [items[idx] for idx in correct_order]
                    if scoring_result["student_sequence"] == correct_sequence:
                        scoring_result["scoring_method"] = "index_to_item_conversion"
                        scoring_result["is_correct"] = True
                        scoring_result["score"] = 100.0
                        scoring_result["explanation"] = "Student sequence matches correctOrder after index conversion"
            except (TypeError, IndexError):
                pass
        
        if not scoring_result["is_correct"]:
            scoring_result["explanation"] = "Student answer does not match any expected format"
        
        print(f"   Student clicked sequence: {' → '.join(scoring_result['student_sequence']) if scoring_result['student_sequence'] else 'Unable to determine'}")
        print(f"   Correct order stored: {correct_order}")
        print(f"   Scoring method: {scoring_result['scoring_method']}")
        print(f"   Is correct: {scoring_result['is_correct']}")
        print(f"   Score: {scoring_result['score']}%")
        print(f"   Explanation: {scoring_result['explanation']}")
        
        return scoring_result
    
    async def investigate_test_scoring(self, test_id: str, program_id: str, question_id: str, student_answer: List[int]):
        """Main investigation method"""
        print("=" * 80)
        print("🔍 CHRONOLOGICAL ORDER SCORING INVESTIGATION")
        print("=" * 80)
        
        # Find the program
        program = await self.find_program_by_id(program_id)
        if not program:
            print("❌ Cannot proceed without program data")
            return
        
        # Look for final test in program
        final_test = program.get('finalTest')
        if not final_test:
            print("❌ No final test found in program")
            return
        
        print(f"\n📋 Final Test Details:")
        print(f"   Test ID: {final_test.get('id', 'Unknown')}")
        print(f"   Title: {final_test.get('title', 'Unknown')}")
        print(f"   Questions Count: {len(final_test.get('questions', []))}")
        
        # Find the specific chronological order question
        target_question = None
        for i, question in enumerate(final_test.get('questions', [])):
            if question.get('id') == question_id:
                target_question = question
                print(f"✅ Found target question at index {i}")
                break
        
        if not target_question:
            print(f"❌ Question with ID {question_id} not found in final test")
            # Let's check all questions to see what we have
            print("\n📝 Available questions in final test:")
            for i, q in enumerate(final_test.get('questions', [])):
                print(f"   {i+1}. ID: {q.get('id', 'No ID')}, Type: {q.get('type', 'Unknown')}")
            return
        
        # Analyze the question structure
        analysis = await self.analyze_chronological_question(target_question, question_id)
        
        # Simulate scoring
        scoring_result = await self.simulate_scoring(target_question, student_answer)
        
        # Final summary
        print("\n" + "=" * 80)
        print("📊 INVESTIGATION SUMMARY")
        print("=" * 80)
        print(f"✅ Found chronological order question in program final test")
        print(f"📝 Question has {len(analysis['items'])} items: {analysis['items']}")
        print(f"🎯 Correct order stored as: {analysis['correct_order']}")
        print(f"👤 Student clicked sequence: 1→3→2→4 (indices [0,1,2,3])")
        print(f"🔢 Student answer translates to: {scoring_result['student_sequence']}")
        print(f"❓ Question marked as: {'CORRECT' if scoring_result['is_correct'] else 'INCORRECT'}")
        print(f"💯 Score: {scoring_result['score']}%")
        print(f"📋 Explanation: {scoring_result['explanation']}")
        
        # Identify the issue
        print(f"\n🚨 ROOT CAUSE ANALYSIS:")
        if not scoring_result['is_correct']:
            print(f"   The student's answer [0,1,2,3] represents clicking items in order: {scoring_result['student_sequence']}")
            print(f"   The stored correctOrder is: {analysis['correct_order']}")
            print(f"   These don't match, causing the question to be marked incorrect")
            
            # Suggest what the correct order should be
            if analysis['items'] == ["1", "3", "2", "4"]:
                print(f"   If the correct chronological order should be 1→2→3→4:")
                print(f"   Then correctOrder should be [0,2,1,3] (indices) or ['1','2','3','4'] (items)")
                print(f"   Current correctOrder {analysis['correct_order']} doesn't match either format")
        else:
            print(f"   The scoring logic correctly identified the student's answer as correct")
        
        return {
            "analysis": analysis,
            "scoring_result": scoring_result,
            "program": program,
            "final_test": final_test
        }

async def main():
    """Main execution function"""
    debugger = ChronologicalOrderDebugger()
    
    try:
        # Connect to database
        if not await debugger.connect():
            return
        
        # Investigation parameters from the review request
        test_id = "6e6d6c00-565f-4821-9f4d-d5324b7ab079"
        program_id = "9d606116-dcb5-4067-b11b-78132451ddb6"
        question_id = "1b4f453d-39c7-4663-b2bf-7a4127135163"
        student_answer = [0, 1, 2, 3]  # Student clicked 1→3→2→4
        
        # Run the investigation
        result = await debugger.investigate_test_scoring(
            test_id, program_id, question_id, student_answer
        )
        
        if result:
            print(f"\n✅ Investigation completed successfully")
        else:
            print(f"\n❌ Investigation could not be completed")
            
    except Exception as e:
        print(f"❌ Error during investigation: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await debugger.close()

if __name__ == "__main__":
    asyncio.run(main())