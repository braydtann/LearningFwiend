#!/usr/bin/env python3
"""
Fix Chronological Order Question - Correct Order Field
====================================================

This script fixes the correctOrder field for the specific chronological order question
that has array length mismatch (4 items but only 3 indices in correctOrder).

Target:
- Program ID: 9d606116-dcb5-4067-b11b-78132451ddb6
- Question ID: 1b4f453d-39c7-4663-b2bf-7a4127135163
- Items: ['1', '3', '2', '4']
- Fix correctOrder from [0, 1, 2] to [0, 2, 1, 3] (representing 1→2→3→4)
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# MongoDB connection setup
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/learningfriend_lms')
DB_NAME = os.environ.get('DB_NAME', 'learningfriend_lms')

async def fix_chronological_order():
    """Fix the correctOrder field for the chronological order question"""
    
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        print(f"✅ Connected to MongoDB: {DB_NAME}")
        
        # Target identifiers
        program_id = "9d606116-dcb5-4067-b11b-78132451ddb6"
        question_id = "1b4f453d-39c7-4663-b2bf-7a4127135163"
        
        print(f"\n🔍 Looking for program: {program_id}")
        print(f"🔍 Looking for question: {question_id}")
        
        # Find the program
        program = await db.programs.find_one({"id": program_id})
        if not program:
            print("❌ Program not found")
            return False
            
        print(f"✅ Found program: {program.get('title', 'Unknown')}")
        
        # Find and update the question
        final_test = program.get('finalTest')
        if not final_test:
            print("❌ No final test found in program")
            return False
            
        questions = final_test.get('questions', [])
        question_found = False
        
        for i, question in enumerate(questions):
            if question.get('id') == question_id:
                print(f"\n✅ Found target question at index {i}")
                print(f"   Current items: {question.get('items', [])}")
                print(f"   Current correctOrder: {question.get('correctOrder', [])}")
                
                # Update the correctOrder to represent 1→2→3→4 sequence
                # Items are: ['1', '3', '2', '4']
                # Correct chronological order should be: 1→2→3→4
                # Which maps to indices: [0, 2, 1, 3]
                new_correct_order = [0, 2, 1, 3]
                
                print(f"   New correctOrder: {new_correct_order}")
                print(f"   This represents sequence: 1→2→3→4")
                
                # Update the document in MongoDB
                update_result = await db.programs.update_one(
                    {"id": program_id, "finalTest.questions.id": question_id},
                    {"$set": {"finalTest.questions.$.correctOrder": new_correct_order}}
                )
                
                if update_result.modified_count > 0:
                    print(f"✅ Successfully updated correctOrder field")
                    question_found = True
                else:
                    print(f"❌ Failed to update correctOrder field")
                    
                break
        
        if not question_found:
            print(f"❌ Question with ID {question_id} not found")
            return False
            
        # Verify the update
        print(f"\n🔍 Verifying update...")
        updated_program = await db.programs.find_one({"id": program_id})
        if updated_program:
            updated_questions = updated_program.get('finalTest', {}).get('questions', [])
            for question in updated_questions:
                if question.get('id') == question_id:
                    print(f"✅ Verification successful:")
                    print(f"   Items: {question.get('items', [])}")
                    print(f"   Updated correctOrder: {question.get('correctOrder', [])}")
                    break
        
        client.close()
        print(f"\n🎉 Chronological Order question fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing chronological order: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_chronological_order())