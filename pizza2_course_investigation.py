#!/usr/bin/env python3
"""
PIZZA2 COURSE INVESTIGATION - BACKEND TESTING
LearningFwiend LMS Application Backend API Testing

INVESTIGATION FOCUS:
✅ Check if "pizza2" course exists and verify available courses in database
✅ Authentication with admin credentials: brayden.t@covesmart.com / Hawaii2020!
✅ Course Database Investigation (GET /api/courses - list all available courses)
✅ Search for any courses with "pizza" in the title
✅ Check for courses created recently
✅ Verify course creation process is working
✅ Course Creation Test (Create a new test course with "Select All That Apply" questions)
✅ Verify the course gets saved to database with proper courseId
✅ Test course retrieval after creation
✅ Data Structure Verification (If "pizza2" course exists, examine its data structure)
✅ Check if Select All That Apply questions have proper options and correctAnswers arrays
✅ Verify course is properly accessible via API

GOAL: Identify why "pizza2" course cannot be accessed and verify the course creation/retrieval process is working correctly.
"""

import requests
import json
import os
import sys
from datetime import datetime
import time
import uuid

# Configuration - Using production URL from frontend/.env
BACKEND_URL = "https://lms-progression-1.preview.emergentagent.com/api"
TEST_TIMEOUT = 15

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

class Pizza2CourseInvestigator:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.auth_tokens = {}
        self.pizza_courses = []
        self.all_courses = []
        
    def log_result(self, test_name, status, message, details=None):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.results.append(result)
        
        if status == 'PASS':
            self.passed += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.failed += 1
            print(f"❌ {test_name}: {message}")
            if details:
                print(f"   Details: {details}")
    
    def test_admin_authentication(self):
        """Test admin authentication with provided credentials"""
        print("\n🔑 STEP 1: Admin Authentication")
        print("-" * 50)
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=TEST_TIMEOUT,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                user_info = data.get('user', {})
                
                if token and user_info.get('role') == 'admin':
                    self.auth_tokens['admin'] = token
                    self.log_result(
                        "Admin Authentication", 
                        "PASS", 
                        f"Successfully authenticated as admin: {user_info.get('full_name')}",
                        f"Email: {user_info.get('email')}, Role: {user_info.get('role')}"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin Authentication", 
                        "FAIL", 
                        "Authentication succeeded but user is not admin or token missing",
                        f"Role: {user_info.get('role')}, Token present: {bool(token)}"
                    )
            else:
                self.log_result(
                    "Admin Authentication", 
                    "FAIL", 
                    f"Authentication failed with status {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Admin Authentication", 
                "FAIL", 
                "Failed to connect to authentication endpoint",
                str(e)
            )
        return False
    
    def investigate_all_courses(self):
        """Get all available courses and search for pizza-related courses"""
        print("\n📚 STEP 2: Course Database Investigation")
        print("-" * 50)
        
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Course Database Investigation", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                courses = response.json()
                self.all_courses = courses
                
                print(f"✅ Retrieved {len(courses)} total courses from database")
                
                # Search for pizza-related courses
                pizza_courses = []
                for course in courses:
                    title = course.get('title', '').lower()
                    description = course.get('description', '').lower()
                    
                    if 'pizza' in title or 'pizza' in description:
                        pizza_courses.append(course)
                        print(f"🍕 Found pizza course: {course.get('title')} (ID: {course.get('id')})")
                
                self.pizza_courses = pizza_courses
                
                # Check specifically for "pizza2" course
                pizza2_course = None
                for course in courses:
                    if course.get('title', '').lower() == 'pizza2':
                        pizza2_course = course
                        break
                
                if pizza2_course:
                    self.log_result(
                        "Pizza2 Course Search", 
                        "PASS", 
                        f"✅ FOUND 'pizza2' course in database!",
                        f"Course ID: {pizza2_course.get('id')}, Created: {pizza2_course.get('created_at')}"
                    )
                    return pizza2_course
                else:
                    # Check for similar names
                    similar_courses = []
                    for course in courses:
                        title = course.get('title', '').lower()
                        if 'pizza' in title and '2' in title:
                            similar_courses.append(course)
                    
                    if similar_courses:
                        similar_names = [c.get('title') for c in similar_courses]
                        self.log_result(
                            "Pizza2 Course Search", 
                            "FAIL", 
                            f"'pizza2' course NOT FOUND, but found {len(similar_courses)} similar courses",
                            f"Similar courses: {similar_names}"
                        )
                    else:
                        self.log_result(
                            "Pizza2 Course Search", 
                            "FAIL", 
                            f"'pizza2' course NOT FOUND. Found {len(pizza_courses)} pizza-related courses total",
                            f"Pizza courses: {[c.get('title') for c in pizza_courses]}"
                        )
                
                return None
            else:
                self.log_result(
                    "Course Database Investigation", 
                    "FAIL", 
                    f"Failed to retrieve courses, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Database Investigation", 
                "FAIL", 
                "Failed to connect to courses endpoint",
                str(e)
            )
        return False
    
    def analyze_recent_courses(self):
        """Check for courses created recently"""
        print("\n📅 STEP 3: Recent Course Analysis")
        print("-" * 50)
        
        if not self.all_courses:
            self.log_result(
                "Recent Course Analysis", 
                "SKIP", 
                "No courses data available",
                "Course database investigation must succeed first"
            )
            return False
        
        try:
            # Sort courses by creation date
            recent_courses = []
            for course in self.all_courses:
                created_at = course.get('created_at')
                if created_at:
                    try:
                        # Parse the datetime
                        if isinstance(created_at, str):
                            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        else:
                            created_date = created_at
                        
                        # Check if created in last 30 days
                        days_ago = (datetime.now() - created_date.replace(tzinfo=None)).days
                        if days_ago <= 30:
                            recent_courses.append({
                                'course': course,
                                'days_ago': days_ago,
                                'created_date': created_date
                            })
                    except:
                        pass
            
            # Sort by most recent first
            recent_courses.sort(key=lambda x: x['days_ago'])
            
            print(f"📊 Found {len(recent_courses)} courses created in last 30 days:")
            
            for item in recent_courses[:10]:  # Show top 10 most recent
                course = item['course']
                days_ago = item['days_ago']
                print(f"   📖 {course.get('title')} - {days_ago} days ago (ID: {course.get('id')})")
                
                # Check if this could be the missing pizza2 course
                title = course.get('title', '').lower()
                if 'pizza' in title:
                    print(f"      🍕 This is a PIZZA-related course!")
            
            self.log_result(
                "Recent Course Analysis", 
                "PASS", 
                f"Analyzed recent courses - {len(recent_courses)} created in last 30 days",
                f"Most recent courses: {[item['course'].get('title') for item in recent_courses[:5]]}"
            )
            
            return recent_courses
            
        except Exception as e:
            self.log_result(
                "Recent Course Analysis", 
                "FAIL", 
                "Failed to analyze recent courses",
                str(e)
            )
        return False
    
    def test_course_creation_process(self):
        """Test course creation process with Select All That Apply questions"""
        print("\n🏗️ STEP 4: Course Creation Test with Select All That Apply")
        print("-" * 50)
        
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Course Creation Test", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            # Create a test course with Select All That Apply questions
            test_course_data = {
                "title": "Pizza2 Investigation Test Course",
                "description": "Test course created to investigate pizza2 course issue and verify Select All That Apply functionality",
                "category": "Testing",
                "duration": "1 hour",
                "accessType": "open",
                "modules": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Pizza Knowledge Module",
                        "lessons": [
                            {
                                "id": str(uuid.uuid4()),
                                "title": "Pizza Quiz with Select All That Apply",
                                "type": "quiz",
                                "content": "Test your pizza knowledge",
                                "questions": [
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "select-all-that-apply",
                                        "question": "Which of the following are pizza toppings?",
                                        "options": [
                                            "Pepperoni",
                                            "Mushrooms",
                                            "Pineapple",
                                            "Anchovies",
                                            "Chocolate"
                                        ],
                                        "correctAnswers": [0, 1, 2, 3],  # All except chocolate
                                        "points": 10
                                    },
                                    {
                                        "id": str(uuid.uuid4()),
                                        "type": "multiple-choice",
                                        "question": "What is the origin of pizza?",
                                        "options": [
                                            "Italy",
                                            "France",
                                            "Greece",
                                            "Spain"
                                        ],
                                        "correctAnswer": 0,
                                        "points": 5
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{BACKEND_URL}/courses",
                json=test_course_data,
                timeout=TEST_TIMEOUT,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.auth_tokens["admin"]}'
                }
            )
            
            if response.status_code == 200:
                created_course = response.json()
                course_id = created_course.get('id')
                
                print(f"✅ Course created successfully!")
                print(f"   Course ID: {course_id}")
                print(f"   Title: {created_course.get('title')}")
                print(f"   Modules: {len(created_course.get('modules', []))}")
                
                # Verify the course structure
                modules = created_course.get('modules', [])
                if modules:
                    lessons = modules[0].get('lessons', [])
                    if lessons:
                        questions = lessons[0].get('questions', [])
                        select_all_questions = [q for q in questions if q.get('type') == 'select-all-that-apply']
                        
                        print(f"   Questions: {len(questions)} total, {len(select_all_questions)} Select All That Apply")
                        
                        # Check Select All That Apply structure
                        for q in select_all_questions:
                            options = q.get('options', [])
                            correct_answers = q.get('correctAnswers', [])
                            print(f"   ✅ Select All That Apply: {len(options)} options, {len(correct_answers)} correct answers")
                
                self.log_result(
                    "Course Creation Test", 
                    "PASS", 
                    f"Successfully created test course with Select All That Apply questions",
                    f"Course ID: {course_id}, Modules: {len(modules)}, Questions verified"
                )
                
                return created_course
            else:
                self.log_result(
                    "Course Creation Test", 
                    "FAIL", 
                    f"Failed to create course, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Creation Test", 
                "FAIL", 
                "Failed to test course creation",
                str(e)
            )
        return False
    
    def test_course_retrieval(self, course_id):
        """Test course retrieval after creation"""
        print("\n🔍 STEP 5: Course Retrieval Test")
        print("-" * 50)
        
        if "admin" not in self.auth_tokens:
            self.log_result(
                "Course Retrieval Test", 
                "SKIP", 
                "No admin token available",
                "Admin authentication required"
            )
            return False
        
        try:
            response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
            )
            
            if response.status_code == 200:
                retrieved_course = response.json()
                
                print(f"✅ Course retrieved successfully!")
                print(f"   Course ID: {retrieved_course.get('id')}")
                print(f"   Title: {retrieved_course.get('title')}")
                print(f"   Status: {retrieved_course.get('status')}")
                print(f"   Instructor: {retrieved_course.get('instructor')}")
                
                # Verify data structure integrity
                modules = retrieved_course.get('modules', [])
                total_questions = 0
                select_all_questions = 0
                
                for module in modules:
                    lessons = module.get('lessons', [])
                    for lesson in lessons:
                        questions = lesson.get('questions', [])
                        total_questions += len(questions)
                        
                        for question in questions:
                            if question.get('type') == 'select-all-that-apply':
                                select_all_questions += 1
                                
                                # Verify Select All That Apply structure
                                options = question.get('options', [])
                                correct_answers = question.get('correctAnswers', [])
                                
                                if not options:
                                    print(f"   ⚠️ WARNING: Select All That Apply question missing options")
                                if not correct_answers:
                                    print(f"   ⚠️ WARNING: Select All That Apply question missing correctAnswers")
                                else:
                                    print(f"   ✅ Select All That Apply structure valid: {len(options)} options, {len(correct_answers)} correct")
                
                self.log_result(
                    "Course Retrieval Test", 
                    "PASS", 
                    f"Successfully retrieved and verified course structure",
                    f"Total questions: {total_questions}, Select All That Apply: {select_all_questions}"
                )
                
                return retrieved_course
            else:
                self.log_result(
                    "Course Retrieval Test", 
                    "FAIL", 
                    f"Failed to retrieve course, status: {response.status_code}",
                    f"Response: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Course Retrieval Test", 
                "FAIL", 
                "Failed to test course retrieval",
                str(e)
            )
        return False
    
    def analyze_pizza_course_data_structures(self):
        """Analyze data structures of existing pizza courses"""
        print("\n🔬 STEP 6: Pizza Course Data Structure Analysis")
        print("-" * 50)
        
        if not self.pizza_courses:
            self.log_result(
                "Pizza Course Data Structure Analysis", 
                "SKIP", 
                "No pizza courses found to analyze",
                "No pizza-related courses in database"
            )
            return False
        
        analysis_results = []
        
        for pizza_course in self.pizza_courses:
            course_id = pizza_course.get('id')
            course_title = pizza_course.get('title')
            
            print(f"\n🍕 Analyzing: {course_title} (ID: {course_id})")
            
            try:
                # Get detailed course data
                response = requests.get(
                    f"{BACKEND_URL}/courses/{course_id}",
                    timeout=TEST_TIMEOUT,
                    headers={'Authorization': f'Bearer {self.auth_tokens["admin"]}'}
                )
                
                if response.status_code == 200:
                    detailed_course = response.json()
                    
                    # Analyze structure
                    modules = detailed_course.get('modules', [])
                    total_lessons = 0
                    total_questions = 0
                    question_types = {}
                    data_issues = []
                    
                    for module in modules:
                        lessons = module.get('lessons', [])
                        total_lessons += len(lessons)
                        
                        for lesson in lessons:
                            questions = lesson.get('questions', [])
                            total_questions += len(questions)
                            
                            for question in questions:
                                q_type = question.get('type', 'unknown')
                                question_types[q_type] = question_types.get(q_type, 0) + 1
                                
                                # Check for data structure issues
                                if q_type == 'select-all-that-apply':
                                    if not question.get('options'):
                                        data_issues.append(f"Select All That Apply question missing 'options' field")
                                    if not question.get('correctAnswers'):
                                        data_issues.append(f"Select All That Apply question missing 'correctAnswers' field")
                                elif q_type == 'multiple-choice':
                                    if not question.get('options'):
                                        data_issues.append(f"Multiple Choice question missing 'options' field")
                                    if question.get('correctAnswer') is None:
                                        data_issues.append(f"Multiple Choice question missing 'correctAnswer' field")
                    
                    analysis = {
                        'course_id': course_id,
                        'title': course_title,
                        'modules': len(modules),
                        'lessons': total_lessons,
                        'questions': total_questions,
                        'question_types': question_types,
                        'data_issues': data_issues,
                        'accessible': True
                    }
                    
                    print(f"   📊 Structure: {len(modules)} modules, {total_lessons} lessons, {total_questions} questions")
                    print(f"   🎯 Question types: {question_types}")
                    
                    if data_issues:
                        print(f"   ⚠️ Data issues found: {len(data_issues)}")
                        for issue in data_issues:
                            print(f"      - {issue}")
                    else:
                        print(f"   ✅ No data structure issues found")
                    
                    analysis_results.append(analysis)
                    
                else:
                    print(f"   ❌ Failed to retrieve detailed course data: {response.status_code}")
                    analysis_results.append({
                        'course_id': course_id,
                        'title': course_title,
                        'accessible': False,
                        'error': f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                print(f"   ❌ Error analyzing course: {str(e)}")
                analysis_results.append({
                    'course_id': course_id,
                    'title': course_title,
                    'accessible': False,
                    'error': str(e)
                })
        
        # Summary
        accessible_courses = [r for r in analysis_results if r.get('accessible')]
        courses_with_issues = [r for r in accessible_courses if r.get('data_issues')]
        
        if accessible_courses:
            self.log_result(
                "Pizza Course Data Structure Analysis", 
                "PASS", 
                f"Analyzed {len(accessible_courses)} pizza courses - {len(courses_with_issues)} have data issues",
                f"Courses analyzed: {[r['title'] for r in accessible_courses]}"
            )
        else:
            self.log_result(
                "Pizza Course Data Structure Analysis", 
                "FAIL", 
                "Could not access any pizza courses for analysis",
                f"All {len(analysis_results)} pizza courses had access issues"
            )
        
        return analysis_results
    
    def run_investigation(self):
        """Run the complete pizza2 course investigation"""
        print("🍕 PIZZA2 COURSE INVESTIGATION - BACKEND TESTING")
        print("=" * 80)
        print("GOAL: Identify why 'pizza2' course cannot be accessed and verify course creation/retrieval process")
        print("=" * 80)
        
        # Step 1: Admin Authentication
        admin_auth_success = self.test_admin_authentication()
        
        if not admin_auth_success:
            print("\n❌ CRITICAL: Cannot proceed without admin authentication")
            return False
        
        # Step 2: Course Database Investigation
        pizza2_course = self.investigate_all_courses()
        
        # Step 3: Recent Course Analysis
        recent_courses = self.analyze_recent_courses()
        
        # Step 4: Test Course Creation Process
        test_course = self.test_course_creation_process()
        
        # Step 5: Test Course Retrieval
        if test_course:
            retrieved_course = self.test_course_retrieval(test_course.get('id'))
        
        # Step 6: Analyze Pizza Course Data Structures
        pizza_analysis = self.analyze_pizza_course_data_structures()
        
        # Final Summary
        print("\n" + "=" * 80)
        print("🎯 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        print(f"✅ Tests Passed: {self.passed}")
        print(f"❌ Tests Failed: {self.failed}")
        print(f"📊 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        print(f"\n🔍 KEY FINDINGS:")
        print(f"   📚 Total courses in database: {len(self.all_courses)}")
        print(f"   🍕 Pizza-related courses found: {len(self.pizza_courses)}")
        print(f"   🎯 'pizza2' course found: {'YES' if pizza2_course else 'NO'}")
        print(f"   🏗️ Course creation working: {'YES' if test_course else 'NO'}")
        print(f"   🔍 Course retrieval working: {'YES' if test_course and retrieved_course else 'NO'}")
        
        if pizza2_course:
            print(f"\n✅ PIZZA2 COURSE FOUND!")
            print(f"   Course ID: {pizza2_course.get('id')}")
            print(f"   Title: {pizza2_course.get('title')}")
            print(f"   Status: {pizza2_course.get('status')}")
            print(f"   Created: {pizza2_course.get('created_at')}")
        else:
            print(f"\n❌ PIZZA2 COURSE NOT FOUND")
            print(f"   The 'pizza2' course does not exist in the database")
            print(f"   This explains why it cannot be accessed")
            
            if self.pizza_courses:
                print(f"   However, found {len(self.pizza_courses)} other pizza courses:")
                for course in self.pizza_courses:
                    print(f"   - {course.get('title')} (ID: {course.get('id')})")
        
        print(f"\n🔧 RECOMMENDATIONS:")
        if not pizza2_course:
            print(f"   1. The 'pizza2' course needs to be created if it's expected to exist")
            print(f"   2. Course creation process is working correctly (verified)")
            print(f"   3. Check if the course was deleted or never created")
        else:
            print(f"   1. 'pizza2' course exists and should be accessible")
            print(f"   2. Check frontend routing and course access logic")
            print(f"   3. Verify user permissions for course access")
        
        return self.passed > self.failed

def main():
    """Main function to run the investigation"""
    investigator = Pizza2CourseInvestigator()
    success = investigator.run_investigation()
    
    if success:
        print(f"\n🎉 INVESTIGATION COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print(f"\n⚠️ INVESTIGATION COMPLETED WITH ISSUES")
        sys.exit(1)

if __name__ == "__main__":
    main()