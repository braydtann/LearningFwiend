#!/usr/bin/env python3
"""
Fix New Chronological Order Question
===================================

Fix the correctOrder field for the new chronological order question.
The user says correct sequence should be "1", "3", "2", "4" (original order)
which means correctOrder should be [0, 1, 2, 3], not [0, 2, 1, 3].
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection setup
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/learningfriend_lms')
DB_NAME = os.environ.get('DB_NAME', 'learningfriend_lms')

async def fix_new_chronological_order():
    """Fix the correctOrder field for the new chronological order question"""
    
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        print(f"✅ Connected to MongoDB: {DB_NAME}")
        
        # Find the most recent final test with chronological order
        tests = await db.final_tests.find({"questions.type": "chronological-order"}).sort("createdAt", -1).limit(5).to_list(length=5)
        
        print(f"\n🔍 Found {len(tests)} tests with chronological order questions")
        
        for test in tests:
            print(f"\nTest: {test.get('title', 'Unknown')} (ID: {test.get('id')})")
            
            for i, question in enumerate(test.get('questions', [])):
                if question.get('type') == 'chronological-order':
                    items = question.get('items', [])
                    current_correct_order = question.get('correctOrder', [])
                    
                    print(f"  Question {i+1}: {question.get('question', 'No text')[:50]}...")
                    print(f"    Items: {items}")
                    print(f"    Current correctOrder: {current_correct_order}")
                    
                    # Check if this looks like the new test (items "1", "3", "2", "4")
                    if items == ['1', '3', '2', '4']:
                        print(f"    ✅ Found target question! Updating correctOrder...")
                        
                        # User says correct sequence is "1", "3", "2", "4" (original order)
                        # This means correctOrder should be [0, 1, 2, 3]
                        new_correct_order = [0, 1, 2, 3]
                        
                        update_result = await db.final_tests.update_one(
                            {"id": test.get('id'), "questions.id": question.get('id')},
                            {"$set": {"questions.$.correctOrder": new_correct_order}}
                        )
                        
                        if update_result.modified_count > 0:
                            print(f"    ✅ Successfully updated correctOrder to {new_correct_order}")
                        else:
                            print(f"    ❌ Failed to update correctOrder")
        
        client.close()
        print(f"\n🎉 Chronological Order fix completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_new_chronological_order())