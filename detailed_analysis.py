#!/usr/bin/env python3
"""
DETAILED COURSE AND ENROLLMENT ANALYSIS
Get detailed information about the course structure and enrollment data
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://lms-evolution.emergent.host/api"
TEST_TIMEOUT = 15

ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "test.student@cleanenv.com",
    "password": "CleanEnv123!"
}

def get_tokens():
    """Get both admin and student tokens"""
    tokens = {}
    
    # Admin token
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=ADMIN_CREDENTIALS,
            timeout=TEST_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            tokens['admin'] = response.json().get('access_token')
    except:
        pass
    
    # Student token
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=STUDENT_CREDENTIALS,
            timeout=TEST_TIMEOUT,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            data = response.json()
            tokens['student'] = data.get('access_token')
            tokens['student_info'] = data.get('user')
    except:
        pass
    
    return tokens

def get_detailed_course_info(tokens):
    """Get detailed course information"""
    if 'admin' not in tokens:
        return None
    
    try:
        # Get all courses
        response = requests.get(
            f"{BACKEND_URL}/courses",
            timeout=TEST_TIMEOUT,
            headers={'Authorization': f'Bearer {tokens["admin"]}'}
        )
        
        if response.status_code == 200:
            courses = response.json()
            target_course = None
            
            for course in courses:
                if course.get('title') == 'Production Test Course - Clean Environment':
                    target_course = course
                    break
            
            if target_course:
                print("📚 DETAILED COURSE ANALYSIS")
                print("=" * 50)
                print(f"Course ID: {target_course.get('id')}")
                print(f"Title: {target_course.get('title')}")
                print(f"Description: {target_course.get('description')}")
                print(f"Category: {target_course.get('category')}")
                print(f"Instructor: {target_course.get('instructor')} (ID: {target_course.get('instructorId')})")
                print(f"Status: {target_course.get('status')}")
                print(f"Access Type: {target_course.get('accessType')}")
                print(f"Enrolled Students: {target_course.get('enrolledStudents')}")
                print(f"Created: {target_course.get('created_at')}")
                print(f"Updated: {target_course.get('updated_at')}")
                
                # Analyze modules
                modules = target_course.get('modules', [])
                print(f"\n📖 MODULES ANALYSIS ({len(modules)} modules)")
                print("-" * 30)
                
                total_lessons = 0
                for i, module in enumerate(modules, 1):
                    lessons = module.get('lessons', [])
                    total_lessons += len(lessons)
                    print(f"Module {i}: {module.get('title', 'Untitled')}")
                    print(f"  ID: {module.get('id')}")
                    print(f"  Lessons: {len(lessons)}")
                    
                    for j, lesson in enumerate(lessons, 1):
                        print(f"    Lesson {j}: {lesson.get('title', 'Untitled')}")
                        print(f"      ID: {lesson.get('id')}")
                        print(f"      Type: {lesson.get('type', 'unknown')}")
                        if lesson.get('content'):
                            content_preview = lesson.get('content', '')[:100] + '...' if len(lesson.get('content', '')) > 100 else lesson.get('content', '')
                            print(f"      Content: {content_preview}")
                
                print(f"\nTotal Lessons: {total_lessons}")
                return target_course
            else:
                print("❌ Target course not found")
                return None
    except Exception as e:
        print(f"❌ Error getting course info: {str(e)}")
        return None

def get_detailed_enrollment_info(tokens, course_id):
    """Get detailed enrollment information"""
    if 'student' not in tokens:
        return None
    
    try:
        # Get student enrollments
        response = requests.get(
            f"{BACKEND_URL}/enrollments",
            timeout=TEST_TIMEOUT,
            headers={'Authorization': f'Bearer {tokens["student"]}'}
        )
        
        if response.status_code == 200:
            enrollments = response.json()
            
            print("\n📝 DETAILED ENROLLMENT ANALYSIS")
            print("=" * 50)
            print(f"Total Enrollments: {len(enrollments)}")
            
            target_enrollment = None
            for enrollment in enrollments:
                if enrollment.get('courseId') == course_id:
                    target_enrollment = enrollment
                    break
            
            if target_enrollment:
                print(f"\n🎯 TARGET COURSE ENROLLMENT")
                print("-" * 30)
                print(f"Enrollment ID: {target_enrollment.get('id')}")
                print(f"User ID: {target_enrollment.get('userId')}")
                print(f"Course ID: {target_enrollment.get('courseId')}")
                print(f"Enrolled At: {target_enrollment.get('enrolledAt')}")
                print(f"Progress: {target_enrollment.get('progress', 0)}%")
                print(f"Status: {target_enrollment.get('status')}")
                print(f"Completed At: {target_enrollment.get('completedAt', 'Not completed')}")
                print(f"Last Accessed: {target_enrollment.get('lastAccessedAt', 'Never')}")
                
                # Check for module progress
                module_progress = target_enrollment.get('moduleProgress')
                if module_progress:
                    print(f"\n📊 MODULE PROGRESS")
                    print("-" * 20)
                    for i, module_prog in enumerate(module_progress, 1):
                        print(f"Module {i} (ID: {module_prog.get('moduleId')})")
                        print(f"  Completed: {module_prog.get('completed', False)}")
                        print(f"  Completed At: {module_prog.get('completedAt', 'Not completed')}")
                        
                        lessons = module_prog.get('lessons', [])
                        print(f"  Lessons: {len(lessons)}")
                        for j, lesson_prog in enumerate(lessons, 1):
                            print(f"    Lesson {j} (ID: {lesson_prog.get('lessonId')})")
                            print(f"      Completed: {lesson_prog.get('completed', False)}")
                            print(f"      Time Spent: {lesson_prog.get('timeSpent', 0)} seconds")
                else:
                    print("\n⚠️ No module progress data found")
                
                return target_enrollment
            else:
                print(f"\n❌ No enrollment found for course ID: {course_id}")
                return None
        else:
            print(f"❌ Failed to get enrollments: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting enrollment info: {str(e)}")
        return None

def test_frontend_compatibility(tokens, course_id):
    """Test what the frontend would receive"""
    if 'student' not in tokens:
        return False
    
    print("\n🖥️ FRONTEND COMPATIBILITY TEST")
    print("=" * 50)
    
    try:
        # Test GET /api/courses/{id} (what CourseDetail.js calls)
        response = requests.get(
            f"{BACKEND_URL}/courses/{course_id}",
            timeout=TEST_TIMEOUT,
            headers={'Authorization': f'Bearer {tokens["student"]}'}
        )
        
        if response.status_code == 200:
            course_data = response.json()
            print("✅ Course data retrieval successful")
            
            # Check required fields for CourseDetail.js
            required_fields = ['id', 'title', 'description', 'modules', 'instructor']
            missing_fields = []
            
            for field in required_fields:
                if field not in course_data or course_data[field] is None:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Missing required fields: {', '.join(missing_fields)}")
                return False
            else:
                print("✅ All required fields present")
            
            # Check modules structure
            modules = course_data.get('modules', [])
            if not modules:
                print("❌ No modules found - this could cause issues")
                return False
            
            print(f"✅ Found {len(modules)} modules")
            
            # Check lessons structure
            total_lessons = 0
            for module in modules:
                lessons = module.get('lessons', [])
                total_lessons += len(lessons)
                
                for lesson in lessons:
                    required_lesson_fields = ['id', 'title', 'type']
                    for field in required_lesson_fields:
                        if field not in lesson:
                            print(f"❌ Lesson missing field: {field}")
                            return False
            
            if total_lessons == 0:
                print("❌ No lessons found - this could cause display issues")
                return False
            
            print(f"✅ Found {total_lessons} lessons with proper structure")
            
            # Test enrollment data compatibility
            enrollment_response = requests.get(
                f"{BACKEND_URL}/enrollments",
                timeout=TEST_TIMEOUT,
                headers={'Authorization': f'Bearer {tokens["student"]}'}
            )
            
            if enrollment_response.status_code == 200:
                enrollments = enrollment_response.json()
                target_enrollment = None
                
                for enrollment in enrollments:
                    if enrollment.get('courseId') == course_id:
                        target_enrollment = enrollment
                        break
                
                if target_enrollment:
                    print("✅ Enrollment data found")
                    
                    # Check enrollment fields
                    required_enrollment_fields = ['id', 'userId', 'courseId', 'progress', 'status']
                    missing_enrollment_fields = []
                    
                    for field in required_enrollment_fields:
                        if field not in target_enrollment:
                            missing_enrollment_fields.append(field)
                    
                    if missing_enrollment_fields:
                        print(f"❌ Enrollment missing fields: {', '.join(missing_enrollment_fields)}")
                        return False
                    else:
                        print("✅ Enrollment has all required fields")
                        return True
                else:
                    print("❌ No enrollment found for target course")
                    return False
            else:
                print(f"❌ Failed to get enrollment data: {enrollment_response.status_code}")
                return False
        else:
            print(f"❌ Course data retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend compatibility test error: {str(e)}")
        return False

def main():
    print("🔍 DETAILED COURSE AND ENROLLMENT ANALYSIS")
    print("=" * 60)
    
    # Get authentication tokens
    tokens = get_tokens()
    
    if 'admin' not in tokens:
        print("❌ Failed to get admin token")
        return False
    
    if 'student' not in tokens:
        print("❌ Failed to get student token")
        return False
    
    print(f"✅ Authentication successful")
    print(f"Student: {tokens['student_info'].get('full_name')} ({tokens['student_info'].get('email')})")
    
    # Get detailed course information
    course = get_detailed_course_info(tokens)
    
    if not course:
        print("❌ Failed to get course information")
        return False
    
    course_id = course.get('id')
    
    # Get detailed enrollment information
    enrollment = get_detailed_enrollment_info(tokens, course_id)
    
    # Test frontend compatibility
    frontend_compatible = test_frontend_compatibility(tokens, course_id)
    
    print(f"\n🎯 FINAL ANALYSIS")
    print("=" * 30)
    
    if enrollment and frontend_compatible:
        print("✅ CONCLUSION: Backend data is complete and compatible")
        print("   - Student is properly enrolled in the target course")
        print("   - Course has proper structure with modules and lessons")
        print("   - All required fields are present for frontend")
        print("   - White screen issue is likely frontend-related:")
        print("     * React component rendering issues")
        print("     * JavaScript errors in browser console")
        print("     * State management problems")
        print("     * Browser caching issues")
        return True
    else:
        print("❌ CONCLUSION: Backend data issues found")
        if not enrollment:
            print("   - Student enrollment issues detected")
        if not frontend_compatible:
            print("   - Frontend compatibility issues detected")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)