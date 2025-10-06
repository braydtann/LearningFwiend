#!/usr/bin/env python3
"""
Detailed Course Analysis for Multi-Quiz Testing
===============================================

Deep analysis of course structures to understand quiz lesson distribution
and identify courses suitable for multi-quiz progression testing.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-progression.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

def authenticate_admin():
    """Authenticate admin user"""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
        
        if response.status_code == 200:
            data = response.json()
            return data["access_token"]
        else:
            print(f"❌ Admin authentication failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Admin authentication error: {str(e)}")
        return None

def get_headers(token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {token}"}

def analyze_all_courses():
    """Analyze all courses for quiz lesson structures"""
    token = authenticate_admin()
    if not token:
        return
    
    print("🔍 Analyzing All Courses for Quiz Structures")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/courses", headers=get_headers(token))
        
        if response.status_code != 200:
            print(f"❌ Failed to get courses: {response.status_code}")
            return
        
        courses = response.json()
        print(f"📚 Found {len(courses)} total courses")
        print()
        
        courses_with_quizzes = []
        courses_with_multiple_quizzes = []
        
        for i, course in enumerate(courses):
            course_id = course["id"]
            course_title = course.get("title", "Unknown Course")
            
            print(f"🔍 Analyzing Course {i+1}/{len(courses)}: '{course_title}'")
            
            # Get detailed course information
            detail_response = requests.get(
                f"{BACKEND_URL}/courses/{course_id}",
                headers=get_headers(token)
            )
            
            if detail_response.status_code == 200:
                course_detail = detail_response.json()
                modules = course_detail.get("modules", [])
                
                print(f"   📁 Modules: {len(modules)}")
                
                total_lessons = 0
                quiz_lessons = []
                
                for j, module in enumerate(modules):
                    module_id = module.get("id", f"module_{j}")
                    module_title = module.get("title", f"Module {j+1}")
                    lessons = module.get("lessons", [])
                    
                    print(f"   📂 Module {j+1}: '{module_title}' ({len(lessons)} lessons)")
                    
                    for k, lesson in enumerate(lessons):
                        total_lessons += 1
                        lesson_id = lesson.get("id", f"lesson_{k}")
                        lesson_title = lesson.get("title", f"Lesson {k+1}")
                        lesson_type = lesson.get("type", "unknown")
                        
                        print(f"      📄 Lesson {k+1}: '{lesson_title}' (type: {lesson_type})")
                        
                        if lesson_type == "quiz":
                            quiz_data = lesson.get("quiz", {})
                            questions = quiz_data.get("questions", [])
                            
                            quiz_info = {
                                "lessonId": lesson_id,
                                "moduleId": module_id,
                                "lessonTitle": lesson_title,
                                "moduleTitle": module_title,
                                "hasQuizData": bool(quiz_data),
                                "questionCount": len(questions),
                                "passingScore": quiz_data.get("passingScore", "Not set"),
                                "maxAttempts": quiz_data.get("maxAttempts", "Not set")
                            }
                            
                            quiz_lessons.append(quiz_info)
                            
                            print(f"         🎯 QUIZ FOUND: {len(questions)} questions, passing: {quiz_info['passingScore']}, attempts: {quiz_info['maxAttempts']}")
                
                print(f"   📊 Total lessons: {total_lessons}, Quiz lessons: {len(quiz_lessons)}")
                
                if quiz_lessons:
                    courses_with_quizzes.append({
                        "courseId": course_id,
                        "title": course_title,
                        "totalLessons": total_lessons,
                        "totalModules": len(modules),
                        "quizLessons": quiz_lessons
                    })
                    
                    if len(quiz_lessons) >= 2:
                        courses_with_multiple_quizzes.append({
                            "courseId": course_id,
                            "title": course_title,
                            "totalQuizzes": len(quiz_lessons),
                            "quizLessons": quiz_lessons
                        })
                        print(f"   🎉 MULTI-QUIZ COURSE FOUND: {len(quiz_lessons)} quizzes!")
                
                print()
            else:
                print(f"   ❌ Failed to get course details: {detail_response.status_code}")
                print()
        
        print("📊 ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Total courses analyzed: {len(courses)}")
        print(f"Courses with quizzes: {len(courses_with_quizzes)}")
        print(f"Courses with multiple quizzes: {len(courses_with_multiple_quizzes)}")
        print()
        
        if courses_with_quizzes:
            print("📋 COURSES WITH QUIZZES:")
            for course in courses_with_quizzes:
                print(f"  • '{course['title']}' - {len(course['quizLessons'])} quiz(s)")
                for quiz in course['quizLessons']:
                    print(f"    - {quiz['lessonTitle']} ({quiz['questionCount']} questions)")
            print()
        
        if courses_with_multiple_quizzes:
            print("🎯 MULTI-QUIZ COURSES (2+ quizzes):")
            for course in courses_with_multiple_quizzes:
                print(f"  • '{course['title']}' - {course['totalQuizzes']} quizzes")
                for quiz in course['quizLessons']:
                    print(f"    - Module: {quiz['moduleTitle']}")
                    print(f"      Quiz: {quiz['lessonTitle']} ({quiz['questionCount']} questions)")
            print()
        else:
            print("⚠️  No courses with multiple quizzes found.")
            print("   This explains why multi-quiz progression testing couldn't find test subjects.")
            print()
        
        # Additional analysis: Look for courses that could be converted to multi-quiz
        print("💡 RECOMMENDATIONS:")
        single_quiz_courses = [c for c in courses_with_quizzes if len(c['quizLessons']) == 1]
        if single_quiz_courses:
            print(f"  • Found {len(single_quiz_courses)} courses with single quizzes that could be enhanced with additional quizzes")
            print("  • Consider adding more quiz lessons to test multi-quiz progression functionality")
        
        if not courses_with_quizzes:
            print("  • No quiz lessons found in any course")
            print("  • Multi-quiz progression feature cannot be tested without quiz content")
            print("  • Consider creating test courses with multiple quiz lessons")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")

if __name__ == "__main__":
    analyze_all_courses()