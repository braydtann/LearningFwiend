#!/usr/bin/env python3
"""
URGENT QUIZ DATA STRUCTURE INVESTIGATION - OLD VS NEW QUIZZES
Investigation of data structure differences between old and new quizzes causing React Error #31

Focus Areas:
1. Examine existing quiz data structures from old courses
2. Check options field for multiple-choice questions  
3. Check items field for chronological-order questions
4. Check correctAnswers field for select-all-that-apply questions
5. Identify missing/malformed arrays causing React Error #31
6. Compare question types and data structures
7. Sample problematic quiz data analysis
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = "https://lms-evolution.emergent.host/api"
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class QuizDataStructureInvestigator:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.problematic_quizzes = []
        self.data_structure_issues = []
        
    async def setup_session(self):
        """Setup HTTP session and authenticate"""
        self.session = aiohttp.ClientSession()
        
        # Authenticate as admin
        async with self.session.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS) as response:
            if response.status == 200:
                auth_data = await response.json()
                self.auth_token = auth_data["access_token"]
                print(f"✅ Admin authentication successful: {auth_data['user']['full_name']}")
                return True
            else:
                error_text = await response.text()
                print(f"❌ Admin authentication failed: {response.status} - {error_text}")
                return False
    
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    async def get_all_courses_with_quizzes(self):
        """Get all courses and identify which ones have quizzes"""
        print("\n🔍 STEP 1: Identifying courses with quiz content...")
        
        try:
            async with self.session.get(f"{BACKEND_URL}/courses", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    courses = await response.json()
                    print(f"📚 Found {len(courses)} total courses")
                    
                    quiz_courses = []
                    for course in courses:
                        has_quiz = self.check_course_has_quiz(course)
                        if has_quiz:
                            quiz_courses.append(course)
                    
                    print(f"🎯 Found {len(quiz_courses)} courses with quiz content")
                    return quiz_courses
                else:
                    print(f"❌ Failed to get courses: {response.status}")
                    return []
        except Exception as e:
            print(f"❌ Error getting courses: {str(e)}")
            return []
    
    def check_course_has_quiz(self, course: Dict) -> bool:
        """Check if a course has quiz lessons"""
        modules = course.get('modules', [])
        for module in modules:
            lessons = module.get('lessons', [])
            for lesson in lessons:
                if lesson.get('type') == 'quiz':
                    return True
        return False
    
    async def analyze_quiz_data_structures(self, quiz_courses: List[Dict]):
        """Analyze quiz data structures in detail"""
        print("\n🔬 STEP 2: Analyzing quiz data structures for React Error #31 causes...")
        
        for i, course in enumerate(quiz_courses[:10]):  # Limit to first 10 for detailed analysis
            print(f"\n📖 Analyzing Course {i+1}: '{course['title'][:50]}...'")
            print(f"   Course ID: {course['id']}")
            print(f"   Created: {course.get('created_at', 'Unknown')}")
            
            await self.analyze_course_quiz_structure(course)
    
    async def analyze_course_quiz_structure(self, course: Dict):
        """Analyze quiz structure for a specific course"""
        course_issues = []
        
        modules = course.get('modules', [])
        for module_idx, module in enumerate(modules):
            lessons = module.get('lessons', [])
            for lesson_idx, lesson in enumerate(lessons):
                if lesson.get('type') == 'quiz':
                    print(f"   🎯 Found Quiz Lesson: '{lesson.get('title', 'Untitled')}'")
                    
                    # Analyze quiz questions
                    questions = lesson.get('questions', [])
                    if not questions:
                        issue = {
                            'course_id': course['id'],
                            'course_title': course['title'],
                            'course_created': course.get('created_at'),
                            'module_idx': module_idx,
                            'lesson_idx': lesson_idx,
                            'lesson_title': lesson.get('title', 'Untitled'),
                            'question_idx': 0,
                            'question_type': 'quiz',
                            'issue_type': 'NO_QUESTIONS',
                            'description': 'Quiz lesson has no questions array or empty questions',
                            'severity': 'CRITICAL'
                        }
                        course_issues.append(issue)
                        print(f"      ❌ ISSUE: No questions found in quiz")
                        continue
                    
                    print(f"      📝 Analyzing {len(questions)} questions...")
                    
                    for q_idx, question in enumerate(questions):
                        question_issues = self.analyze_question_structure(
                            question, course, module_idx, lesson_idx, q_idx
                        )
                        course_issues.extend(question_issues)
        
        if course_issues:
            self.data_structure_issues.extend(course_issues)
            self.problematic_quizzes.append({
                'course': course,
                'issues': course_issues
            })
    
    def analyze_question_structure(self, question: Dict, course: Dict, module_idx: int, lesson_idx: int, q_idx: int) -> List[Dict]:
        """Analyze individual question structure for React Error #31 causes"""
        issues = []
        question_type = question.get('type', 'unknown')
        question_text = question.get('question', 'No question text')[:50]
        
        print(f"         Question {q_idx + 1}: {question_type} - '{question_text}...'")
        
        # Check for common React Error #31 causes
        if question_type == 'multiple-choice':
            options = question.get('options')
            if options is None:
                issues.append(self.create_issue(
                    course, module_idx, lesson_idx, q_idx, question_type,
                    'MISSING_OPTIONS_FIELD', 
                    'Multiple choice question missing options field (null/undefined)'
                ))
                print(f"            ❌ CRITICAL: Missing 'options' field")
            elif not isinstance(options, list):
                issues.append(self.create_issue(
                    course, module_idx, lesson_idx, q_idx, question_type,
                    'INVALID_OPTIONS_TYPE',
                    f'Options field is {type(options).__name__} instead of array'
                ))
                print(f"            ❌ CRITICAL: 'options' is {type(options).__name__}, not array")
            elif len(options) == 0:
                issues.append(self.create_issue(
                    course, module_idx, lesson_idx, q_idx, question_type,
                    'EMPTY_OPTIONS_ARRAY',
                    'Options array is empty'
                ))
                print(f"            ⚠️  WARNING: Empty options array")
            else:
                print(f"            ✅ Options field OK: {len(options)} options")
        
        elif question_type == 'chronological-order':
            items = question.get('items')
            if items is None:
                issues.append(self.create_issue(
                    course, module_idx, lesson_idx, q_idx, question_type,
                    'MISSING_ITEMS_FIELD',
                    'Chronological order question missing items field (null/undefined) - CAUSES REACT ERROR #31'
                ))
                print(f"            ❌ CRITICAL: Missing 'items' field - REACT ERROR #31 CAUSE")
            elif not isinstance(items, list):
                issues.append(self.create_issue(
                    course, module_idx, lesson_idx, q_idx, question_type,
                    'INVALID_ITEMS_TYPE',
                    f'Items field is {type(items).__name__} instead of array - CAUSES REACT ERROR #31'
                ))
                print(f"            ❌ CRITICAL: 'items' is {type(items).__name__}, not array - REACT ERROR #31 CAUSE")
            elif len(items) == 0:
                issues.append(self.create_issue(
                    course, module_idx, lesson_idx, q_idx, question_type,
                    'EMPTY_ITEMS_ARRAY',
                    'Items array is empty'
                ))
                print(f"            ⚠️  WARNING: Empty items array")
            else:
                print(f"            ✅ Items field OK: {len(items)} items")
        
        elif question_type == 'select-all-that-apply':
            options = question.get('options')
            correct_answers = question.get('correctAnswers')
            
            if options is None:
                issues.append(self.create_issue(
                    course, module_idx, lesson_idx, q_idx, question_type,
                    'MISSING_OPTIONS_FIELD',
                    'Select all that apply question missing options field'
                ))
                print(f"            ❌ CRITICAL: Missing 'options' field")
            elif not isinstance(options, list):
                issues.append(self.create_issue(
                    course, module_idx, lesson_idx, q_idx, question_type,
                    'INVALID_OPTIONS_TYPE',
                    f'Options field is {type(options).__name__} instead of array'
                ))
                print(f"            ❌ CRITICAL: 'options' is {type(options).__name__}, not array")
            
            if correct_answers is None:
                issues.append(self.create_issue(
                    course, module_idx, lesson_idx, q_idx, question_type,
                    'MISSING_CORRECT_ANSWERS_FIELD',
                    'Select all that apply question missing correctAnswers field'
                ))
                print(f"            ❌ CRITICAL: Missing 'correctAnswers' field")
            elif not isinstance(correct_answers, list):
                issues.append(self.create_issue(
                    course, module_idx, lesson_idx, q_idx, question_type,
                    'INVALID_CORRECT_ANSWERS_TYPE',
                    f'CorrectAnswers field is {type(correct_answers).__name__} instead of array'
                ))
                print(f"            ❌ CRITICAL: 'correctAnswers' is {type(correct_answers).__name__}, not array")
            
            if isinstance(options, list) and isinstance(correct_answers, list):
                print(f"            ✅ Options and correctAnswers fields OK: {len(options)} options, {len(correct_answers)} correct")
        
        else:
            print(f"            ℹ️  Question type '{question_type}' - basic structure check")
            # Check for basic required fields
            if not question.get('question'):
                issues.append(self.create_issue(
                    course, module_idx, lesson_idx, q_idx, question_type,
                    'MISSING_QUESTION_TEXT',
                    'Question missing question text'
                ))
        
        return issues
    
    def create_issue(self, course: Dict, module_idx: int, lesson_idx: int, q_idx: int, 
                    question_type: str, issue_type: str, description: str) -> Dict:
        """Create a standardized issue record"""
        return {
            'course_id': course['id'],
            'course_title': course['title'],
            'course_created': course.get('created_at'),
            'module_idx': module_idx,
            'lesson_idx': lesson_idx,
            'question_idx': q_idx,
            'question_type': question_type,
            'issue_type': issue_type,
            'description': description,
            'severity': 'CRITICAL' if 'REACT ERROR #31' in description else 'WARNING'
        }
    
    async def generate_sample_problematic_data(self):
        """Generate sample data showing problematic quiz structures"""
        print("\n📋 STEP 3: Generating sample problematic quiz data structures...")
        
        if not self.problematic_quizzes:
            print("✅ No problematic quiz data structures found!")
            return
        
        print(f"\n🚨 Found {len(self.problematic_quizzes)} courses with quiz data structure issues:")
        
        for i, problematic_quiz in enumerate(self.problematic_quizzes[:3]):  # Show first 3
            course = problematic_quiz['course']
            issues = problematic_quiz['issues']
            
            print(f"\n📖 PROBLEMATIC COURSE {i+1}:")
            print(f"   Title: {course['title']}")
            print(f"   ID: {course['id']}")
            print(f"   Created: {course.get('created_at', 'Unknown')}")
            print(f"   Issues Found: {len(issues)}")
            
            # Show critical issues first
            critical_issues = [issue for issue in issues if issue['severity'] == 'CRITICAL']
            if critical_issues:
                print(f"\n   🚨 CRITICAL ISSUES (React Error #31 causes):")
                for issue in critical_issues:
                    print(f"      - {issue['issue_type']}: {issue['description']}")
                    print(f"        Location: Module {issue['module_idx']}, Lesson {issue['lesson_idx']}, Question {issue['question_idx']}")
            
            # Show sample JSON structure
            print(f"\n   📄 SAMPLE PROBLEMATIC JSON STRUCTURE:")
            await self.show_sample_json_structure(course, issues[0] if issues else None)
    
    async def show_sample_json_structure(self, course: Dict, sample_issue: Optional[Dict]):
        """Show sample JSON structure of problematic quiz data"""
        modules = course.get('modules', [])
        if not modules:
            print("      No modules found")
            return
        
        # Find the problematic lesson
        if sample_issue:
            module_idx = sample_issue['module_idx']
            lesson_idx = sample_issue['lesson_idx']
            question_idx = sample_issue['question_idx']
            
            if module_idx < len(modules):
                module = modules[module_idx]
                lessons = module.get('lessons', [])
                if lesson_idx < len(lessons):
                    lesson = lessons[lesson_idx]
                    questions = lesson.get('questions', [])
                    if question_idx < len(questions):
                        question = questions[question_idx]
                        
                        print(f"      Problematic Question JSON:")
                        print(f"      {json.dumps(question, indent=8, default=str)}")
                        return
        
        # Fallback: show first quiz lesson structure
        for module in modules:
            lessons = module.get('lessons', [])
            for lesson in lessons:
                if lesson.get('type') == 'quiz':
                    questions = lesson.get('questions', [])
                    if questions:
                        print(f"      Sample Quiz Question JSON:")
                        print(f"      {json.dumps(questions[0], indent=8, default=str)}")
                        return
    
    async def analyze_old_vs_new_quiz_patterns(self):
        """Analyze patterns between old and new quizzes"""
        print("\n🕰️  STEP 4: Analyzing OLD vs NEW quiz patterns...")
        
        if not self.data_structure_issues:
            print("✅ No data structure issues found to analyze patterns")
            return
        
        # Group issues by creation date
        old_quiz_issues = []
        new_quiz_issues = []
        
        for issue in self.data_structure_issues:
            created_at = issue.get('course_created')
            if created_at:
                try:
                    # Parse creation date
                    if isinstance(created_at, str):
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        created_date = created_at
                    
                    # Consider courses created before 2024-08-01 as "old"
                    cutoff_date = datetime(2024, 8, 1)
                    if created_date < cutoff_date:
                        old_quiz_issues.append(issue)
                    else:
                        new_quiz_issues.append(issue)
                except:
                    # If we can't parse date, consider it old
                    old_quiz_issues.append(issue)
            else:
                old_quiz_issues.append(issue)
        
        print(f"\n📊 PATTERN ANALYSIS RESULTS:")
        print(f"   Old Quiz Issues (before Aug 2024): {len(old_quiz_issues)}")
        print(f"   New Quiz Issues (after Aug 2024): {len(new_quiz_issues)}")
        
        if old_quiz_issues:
            print(f"\n🕰️  OLD QUIZ ISSUES:")
            old_issue_types = {}
            for issue in old_quiz_issues:
                issue_type = issue['issue_type']
                old_issue_types[issue_type] = old_issue_types.get(issue_type, 0) + 1
            
            for issue_type, count in old_issue_types.items():
                print(f"      - {issue_type}: {count} occurrences")
        
        if new_quiz_issues:
            print(f"\n🆕 NEW QUIZ ISSUES:")
            new_issue_types = {}
            for issue in new_quiz_issues:
                issue_type = issue['issue_type']
                new_issue_types[issue_type] = new_issue_types.get(issue_type, 0) + 1
            
            for issue_type, count in new_issue_types.items():
                print(f"      - {issue_type}: {count} occurrences")
    
    async def generate_recommendations(self):
        """Generate recommendations based on findings"""
        print("\n💡 STEP 5: Generating recommendations...")
        
        critical_issues = [issue for issue in self.data_structure_issues if issue['severity'] == 'CRITICAL']
        
        if not critical_issues:
            print("✅ RECOMMENDATION: No critical data structure issues found!")
            print("   - React Error #31 is likely not caused by quiz data structure problems")
            print("   - The issue may be frontend-related or already resolved")
            return
        
        print(f"🚨 CRITICAL FINDINGS: {len(critical_issues)} critical data structure issues found")
        
        # Count issue types
        issue_type_counts = {}
        for issue in critical_issues:
            issue_type = issue['issue_type']
            issue_type_counts[issue_type] = issue_type_counts.get(issue_type, 0) + 1
        
        print(f"\n📈 ISSUE BREAKDOWN:")
        for issue_type, count in issue_type_counts.items():
            print(f"   - {issue_type}: {count} occurrences")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        
        if 'MISSING_ITEMS_FIELD' in issue_type_counts:
            print(f"   A) CHRONOLOGICAL ORDER QUESTIONS - CRITICAL FIX NEEDED:")
            print(f"      - {issue_type_counts['MISSING_ITEMS_FIELD']} questions missing 'items' field")
            print(f"      - This DIRECTLY CAUSES React Error #31 when frontend calls .map() on undefined")
            print(f"      - SOLUTION: Add empty array [] as default for 'items' field")
        
        if 'MISSING_OPTIONS_FIELD' in issue_type_counts:
            print(f"   B) MULTIPLE CHOICE QUESTIONS - CRITICAL FIX NEEDED:")
            print(f"      - {issue_type_counts['MISSING_OPTIONS_FIELD']} questions missing 'options' field")
            print(f"      - This can cause React Error #31 when frontend tries to iterate options")
            print(f"      - SOLUTION: Add empty array [] as default for 'options' field")
        
        if 'MISSING_CORRECT_ANSWERS_FIELD' in issue_type_counts:
            print(f"   C) SELECT ALL THAT APPLY QUESTIONS - FIX NEEDED:")
            print(f"      - {issue_type_counts['MISSING_CORRECT_ANSWERS_FIELD']} questions missing 'correctAnswers' field")
            print(f"      - SOLUTION: Add empty array [] as default for 'correctAnswers' field")
        
        print(f"\n🔧 IMPLEMENTATION STRATEGY:")
        print(f"   1. DATA MIGRATION: Run database update to add missing array fields")
        print(f"   2. BACKEND VALIDATION: Ensure all new quiz questions have required array fields")
        print(f"   3. FRONTEND DEFENSIVE: Add null checks before calling .map() on arrays")
        print(f"   4. TESTING: Create new quiz to verify structure vs fixing old quizzes")
        
        print(f"\n✅ ANSWER TO USER QUESTION:")
        if critical_issues:
            print(f"   - OLD QUIZZES: Have data structure issues causing React Error #31")
            print(f"   - NEW QUIZZES: Should work better if backend validation is fixed")
            print(f"   - RECOMMENDATION: Try creating a NEW quiz to test if the issue persists")
        else:
            print(f"   - Both old and new quizzes appear to have proper data structures")
            print(f"   - React Error #31 is likely caused by frontend code issues, not data")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def run_investigation(self):
        """Run the complete quiz data structure investigation"""
        print("🚨 URGENT QUIZ DATA STRUCTURE INVESTIGATION - OLD VS NEW QUIZZES")
        print("=" * 80)
        print("Investigating data structure differences causing React Error #31")
        print("Focus: options, items, correctAnswers fields in quiz questions")
        print("=" * 80)
        
        try:
            # Setup
            if not await self.setup_session():
                return False
            
            # Get courses with quizzes
            quiz_courses = await self.get_all_courses_with_quizzes()
            if not quiz_courses:
                print("❌ No quiz courses found to analyze")
                return False
            
            # Analyze quiz data structures
            await self.analyze_quiz_data_structures(quiz_courses)
            
            # Generate sample problematic data
            await self.generate_sample_problematic_data()
            
            # Analyze old vs new patterns
            await self.analyze_old_vs_new_quiz_patterns()
            
            # Generate recommendations
            await self.generate_recommendations()
            
            print(f"\n🎉 INVESTIGATION COMPLETE")
            print(f"   - Courses analyzed: {len(quiz_courses)}")
            print(f"   - Data structure issues found: {len(self.data_structure_issues)}")
            print(f"   - Problematic courses: {len(self.problematic_quizzes)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Investigation failed: {str(e)}")
            return False
        finally:
            await self.cleanup()

async def main():
    """Main function"""
    investigator = QuizDataStructureInvestigator()
    success = await investigator.run_investigation()
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)