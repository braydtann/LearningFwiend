#!/usr/bin/env python3
"""
Comprehensive Chronological Order Debug Investigation
====================================================

This script performs a comprehensive search for the chronological order question
and related test data across all collections in the database.
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

class ComprehensiveDebugger:
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
    
    async def search_all_collections(self, target_ids: Dict[str, str]):
        """Search for target IDs across all collections"""
        print("=" * 80)
        print("🔍 COMPREHENSIVE DATABASE SEARCH")
        print("=" * 80)
        
        collections = await self.db.list_collection_names()
        print(f"📚 Found {len(collections)} collections: {', '.join(collections)}")
        
        results = {}
        
        for collection_name in collections:
            print(f"\n🔍 Searching collection: {collection_name}")
            collection = self.db[collection_name]
            
            # Search for each target ID
            for id_type, target_id in target_ids.items():
                try:
                    # Search in various fields that might contain IDs
                    search_queries = [
                        {"id": target_id},
                        {"_id": target_id},
                        {f"{id_type}": target_id},
                        # Search in nested structures
                        {"finalTest.id": target_id},
                        {"questions.id": target_id},
                        {"modules.lessons.id": target_id},
                        {"modules.lessons.questions.id": target_id},
                        # Search in arrays
                        {"courseIds": target_id},
                        {"programIds": target_id},
                        {"studentIds": target_id},
                    ]
                    
                    for query in search_queries:
                        try:
                            docs = await collection.find(query).to_list(10)
                            if docs:
                                if collection_name not in results:
                                    results[collection_name] = {}
                                if id_type not in results[collection_name]:
                                    results[collection_name][id_type] = []
                                results[collection_name][id_type].extend(docs)
                                print(f"   ✅ Found {len(docs)} documents with {id_type}: {target_id}")
                        except Exception as e:
                            # Skip invalid queries for this collection
                            pass
                            
                except Exception as e:
                    print(f"   ❌ Error searching {collection_name}: {str(e)}")
        
        return results
    
    async def analyze_found_documents(self, results: Dict):
        """Analyze the found documents for chronological order questions"""
        print("\n" + "=" * 80)
        print("📊 DOCUMENT ANALYSIS")
        print("=" * 80)
        
        chronological_questions = []
        
        for collection_name, id_results in results.items():
            print(f"\n📚 Collection: {collection_name}")
            
            for id_type, documents in id_results.items():
                print(f"   🔍 {id_type} results: {len(documents)} documents")
                
                for doc in documents:
                    # Look for chronological order questions in various structures
                    questions = self.extract_questions_from_document(doc)
                    
                    for question in questions:
                        if question.get('type') == 'chronological-order':
                            chronological_questions.append({
                                'collection': collection_name,
                                'document_id': doc.get('id', doc.get('_id', 'unknown')),
                                'document_title': doc.get('title', 'Unknown'),
                                'question': question
                            })
                            print(f"      ✅ Found chronological-order question: {question.get('id', 'No ID')}")
        
        return chronological_questions
    
    def extract_questions_from_document(self, doc: Dict) -> List[Dict]:
        """Extract all questions from a document regardless of structure"""
        questions = []
        
        # Direct questions array
        if 'questions' in doc and isinstance(doc['questions'], list):
            questions.extend(doc['questions'])
        
        # Final test questions
        if 'finalTest' in doc and isinstance(doc['finalTest'], dict):
            final_test = doc['finalTest']
            if 'questions' in final_test and isinstance(final_test['questions'], list):
                questions.extend(final_test['questions'])
        
        # Module lessons questions
        if 'modules' in doc and isinstance(doc['modules'], list):
            for module in doc['modules']:
                if 'lessons' in module and isinstance(module['lessons'], list):
                    for lesson in module['lessons']:
                        if 'questions' in lesson and isinstance(lesson['questions'], list):
                            questions.extend(lesson['questions'])
                        # Sometimes the lesson itself is a question
                        if lesson.get('type') in ['quiz', 'test']:
                            questions.append(lesson)
        
        return questions
    
    async def search_quiz_attempts(self):
        """Search for quiz attempts and results"""
        print("\n" + "=" * 80)
        print("🎯 QUIZ ATTEMPTS AND RESULTS SEARCH")
        print("=" * 80)
        
        # Check for quiz attempts/results collections
        collections_to_check = ['quiz_attempts', 'quiz_results', 'test_results', 'enrollments', 'progress']
        
        for collection_name in collections_to_check:
            try:
                collection = self.db[collection_name]
                count = await collection.count_documents({})
                if count > 0:
                    print(f"📊 {collection_name}: {count} documents")
                    
                    # Get recent documents
                    recent_docs = await collection.find().sort("_id", -1).limit(5).to_list(5)
                    for doc in recent_docs:
                        print(f"   📄 Sample document keys: {list(doc.keys())}")
                        
                        # Look for scoring information
                        if 'score' in doc or 'answers' in doc or 'results' in doc:
                            print(f"      🎯 Contains scoring data")
                            if 'answers' in doc:
                                print(f"         Answers: {doc.get('answers', {})}")
                            if 'score' in doc:
                                print(f"         Score: {doc.get('score', 'N/A')}")
                else:
                    print(f"📊 {collection_name}: No documents found")
            except Exception as e:
                print(f"❌ Error checking {collection_name}: {str(e)}")
    
    async def analyze_chronological_scoring_logic(self, questions: List[Dict]):
        """Analyze the scoring logic for found chronological questions"""
        print("\n" + "=" * 80)
        print("🧮 CHRONOLOGICAL ORDER SCORING ANALYSIS")
        print("=" * 80)
        
        if not questions:
            print("❌ No chronological order questions found to analyze")
            return
        
        for i, q_data in enumerate(questions):
            question = q_data['question']
            print(f"\n📝 Question {i+1} from {q_data['collection']}:")
            print(f"   ID: {question.get('id', 'No ID')}")
            print(f"   Text: {question.get('question', 'No question text')[:100]}...")
            print(f"   Items: {question.get('items', [])}")
            print(f"   Correct Order: {question.get('correctOrder', [])}")
            
            # Simulate the scoring issue
            items = question.get('items', [])
            correct_order = question.get('correctOrder', [])
            student_answer = [0, 1, 2, 3]  # The reported student answer
            
            print(f"\n   🎯 Scoring Simulation:")
            print(f"      Student answer indices: {student_answer}")
            
            if items and len(items) >= 4:
                student_sequence = [items[idx] for idx in student_answer if idx < len(items)]
                print(f"      Student clicked sequence: {' → '.join(student_sequence)}")
                
                # Check different scoring methods
                print(f"      Correct order field: {correct_order}")
                
                # Method 1: Direct comparison
                if student_answer == correct_order:
                    print(f"      ✅ Direct comparison: CORRECT")
                else:
                    print(f"      ❌ Direct comparison: INCORRECT")
                
                # Method 2: Item sequence comparison
                if isinstance(correct_order, list) and len(correct_order) > 0:
                    if all(isinstance(x, str) for x in correct_order):
                        # correctOrder contains items
                        if student_sequence == correct_order:
                            print(f"      ✅ Item sequence comparison: CORRECT")
                        else:
                            print(f"      ❌ Item sequence comparison: INCORRECT")
                            print(f"         Expected: {correct_order}")
                            print(f"         Got: {student_sequence}")
                    elif all(isinstance(x, int) for x in correct_order):
                        # correctOrder contains indices
                        if student_answer == correct_order:
                            print(f"      ✅ Index comparison: CORRECT")
                        else:
                            print(f"      ❌ Index comparison: INCORRECT")
                            print(f"         Expected indices: {correct_order}")
                            print(f"         Got indices: {student_answer}")
            
            # Check if this matches the target question
            if question.get('id') == "1b4f453d-39c7-4663-b2bf-7a4127135163":
                print(f"      🎯 THIS IS THE TARGET QUESTION!")
    
    async def run_comprehensive_investigation(self):
        """Run the complete investigation"""
        target_ids = {
            "test_id": "6e6d6c00-565f-4821-9f4d-d5324b7ab079",
            "program_id": "9d606116-dcb5-4067-b11b-78132451ddb6",
            "question_id": "1b4f453d-39c7-4663-b2bf-7a4127135163"
        }
        
        # Search all collections
        results = await self.search_all_collections(target_ids)
        
        # Analyze found documents
        chronological_questions = await self.analyze_found_documents(results)
        
        # Search for quiz attempts
        await self.search_quiz_attempts()
        
        # Analyze scoring logic
        await self.analyze_chronological_scoring_logic(chronological_questions)
        
        # Final summary
        print("\n" + "=" * 80)
        print("📋 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        if chronological_questions:
            print(f"✅ Found {len(chronological_questions)} chronological order questions")
            target_found = any(q['question'].get('id') == "1b4f453d-39c7-4663-b2bf-7a4127135163" 
                             for q in chronological_questions)
            if target_found:
                print(f"🎯 Target question found and analyzed")
            else:
                print(f"❌ Target question ID not found among chronological questions")
        else:
            print(f"❌ No chronological order questions found in database")
        
        print(f"\n🔍 Search Results Summary:")
        for collection, id_results in results.items():
            for id_type, docs in id_results.items():
                print(f"   {collection}.{id_type}: {len(docs)} matches")

async def main():
    """Main execution function"""
    debugger = ComprehensiveDebugger()
    
    try:
        # Connect to database
        if not await debugger.connect():
            return
        
        # Run comprehensive investigation
        await debugger.run_comprehensive_investigation()
            
    except Exception as e:
        print(f"❌ Error during investigation: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await debugger.close()

if __name__ == "__main__":
    asyncio.run(main())