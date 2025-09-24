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
        test_id = "6e6d6c00-565f-4821-9f4d-d5324b7ab079"
        
        print(f"\n🔍 Looking for final test: {test_id}")
        print(f"🔍 Looking for question: {question_id}")
        
        # Find the final test in final_tests collection
        final_test = await db.final_tests.find_one({"id": test_id})
        if not final_test:
            print("❌ Final test not found in final_tests collection")
            
            # Try looking in programs collection
            program = await db.programs.find_one({"id": program_id})
            if not program:
                print("❌ Program not found")
                return False
                
            print(f"✅ Found program: {program.get('title', 'Unknown')}")
            final_test = program.get('finalTest')
            if not final_test:
                print("❌ No final test found in program either")
                return False
            
            # Use program-based update
            questions = final_test.get('questions', [])
            question_found = False
            
            for i, question in enumerate(questions):
                if question.get('id') == question_id:
                    print(f"\n✅ Found target question at index {i} in program")
                    print(f"   Current items: {question.get('items', [])}")
                    print(f"   Current correctOrder: {question.get('correctOrder', [])}")
                    
                    # Update the correctOrder to represent 1→2→3→4 sequence
                    new_correct_order = [0, 2, 1, 3]
                    
                    print(f"   New correctOrder: {new_correct_order}")
                    print(f"   This represents sequence: 1→2→3→4")
                    
                    # Update the document in MongoDB
                    update_result = await db.programs.update_one(
                        {"id": program_id, "finalTest.questions.id": question_id},
                        {"$set": {"finalTest.questions.$.correctOrder": new_correct_order}}
                    )
                    
                    if update_result.modified_count > 0:
                        print(f"✅ Successfully updated correctOrder field in program")
                        question_found = True
                    else:
                        print(f"❌ Failed to update correctOrder field in program")
                        
                    break
        else:
            print(f"✅ Found final test: {final_test.get('title', 'Unknown')}")
            
            # Find and update the question in final_tests collection
            questions = final_test.get('questions', [])
            question_found = False
            
            for i, question in enumerate(questions):
                if question.get('id') == question_id:
                    print(f"\n✅ Found target question at index {i}")
                    print(f"   Current items: {question.get('items', [])}")
                    print(f"   Current correctOrder: {question.get('correctOrder', [])}")
                    
                    # Update the correctOrder to represent 1→2→3→4 sequence
                    new_correct_order = [0, 2, 1, 3]
                    
                    print(f"   New correctOrder: {new_correct_order}")
                    print(f"   This represents sequence: 1→2→3→4")
                    
                    # Update the document in MongoDB
                    update_result = await db.final_tests.update_one(
                        {"id": test_id, "questions.id": question_id},
                        {"$set": {"questions.$.correctOrder": new_correct_order}}
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
        updated_test = await db.final_tests.find_one({"id": test_id})
        if updated_test:
            updated_questions = updated_test.get('questions', [])
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