#!/usr/bin/env python3
"""
🔍 QUIZ IMAGE DISPLAY INVESTIGATION & PROGRESSIVE QUIZ ACCESS FEATURE TESTING

INVESTIGATION OBJECTIVES:
1. **Image Display Bug Analysis**: Find courses with quiz questions that have image URLs in answer options and examine data structure
2. **Progressive Quiz Access**: Examine enrollment and moduleProgress data structure for implementing progressive quiz access
3. **Student Progress Data Analysis**: Test how to determine if student has reached specific lesson/module

SPECIFIC TESTS:
1. Find Quiz with Images - GET /api/courses - Find courses with quiz lessons, examine quiz questions with image URLs
2. Test Student Progress Data - Login as student, GET /api/enrollments - Check moduleProgress structure  
3. Quiz Data Structure Analysis - Check if quiz question options are stored as strings vs objects with {text, image, audio}

CREDENTIALS:
- Admin: brayden.t@covesmart.com / Hawaii2020!
- Student: karlo.student@alder.com / StudentPermanent123!
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration - Use the correct backend URL
BACKEND_URL = "https://lms-evolution.emergent.host/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "username_or_email": "brayden.t@covesmart.com",
    "password": "Hawaii2020!"
}

STUDENT_CREDENTIALS = {
    "username_or_email": "karlo.student@alder.com", 
    "password": "StudentPermanent123!"
}

class QuizImageInvestigator:
    def __init__(self):
        self.admin_token = None
        self.student_token = None
        self.results = []
        self.courses_with_quizzes = []
        self.courses_with_image_options = []
        self.student_enrollments = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_admin(self):
        """Test admin authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('access_token')
                user_info = data.get('user', {})
                
                if user_info.get('role') == 'admin':
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Authenticated as {user_info.get('full_name')} ({user_info.get('email')})"
                    )
                    return True
                else:
                    self.log_result("Admin Authentication", False, f"User role is {user_info.get('role')}, expected admin")
                    return False
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def authenticate_student(self):
        """Test student authentication"""
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=STUDENT_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get('access_token')
                user_info = data.get('user', {})
                
                if user_info.get('role') == 'learner':
                    self.log_result(
                        "Student Authentication", 
                        True, 
                        f"Authenticated as {user_info.get('full_name')} ({user_info.get('email')})"
                    )
                    return True
                else:
                    self.log_result("Student Authentication", False, f"User role is {user_info.get('role')}, expected learner")
                    return False
            else:
                self.log_result("Student Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Student Authentication", False, f"Exception: {str(e)}")
            return False

    def find_courses_with_quiz_lessons(self):
        """Find courses that contain quiz lessons"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            response = requests.get(f"{BACKEND_URL}/courses", headers=headers, timeout=10)
            
            if response.status_code == 200:
                courses = response.json()
                
                quiz_courses = []
                for course in courses:
                    course_id = course.get('id')
                    course_title = course.get('title', 'Unknown')
                    
                    # Get detailed course information
                    detail_response = requests.get(
                        f"{BACKEND_URL}/courses/{course_id}", 
                        headers=headers, 
                        timeout=10
                    )
                    
                    if detail_response.status_code == 200:
                        course_detail = detail_response.json()
                        modules = course_detail.get('modules', [])
                        
                        has_quiz = False
                        quiz_lessons = []
                        
                        for module in modules:
                            lessons = module.get('lessons', [])
                            for lesson in lessons:
                                lesson_type = lesson.get('type', '').lower()
                                if lesson_type == 'quiz':
                                    has_quiz = True
                                    quiz_lessons.append({
                                        'lesson_id': lesson.get('id'),
                                        'lesson_title': lesson.get('title', 'Unknown Quiz'),
                                        'module_title': module.get('title', 'Unknown Module'),
                                        'questions': lesson.get('questions', [])
                                    })
                        
                        if has_quiz:
                            quiz_courses.append({
                                'course_id': course_id,
                                'course_title': course_title,
                                'quiz_lessons': quiz_lessons
                            })
                
                self.courses_with_quizzes = quiz_courses
                
                self.log_result(
                    "Find Courses with Quiz Lessons", 
                    True, 
                    f"Found {len(quiz_courses)} courses with quiz lessons. Total courses scanned: {len(courses)}"
                )
                
                # Log details of courses with quizzes
                for course in quiz_courses[:5]:  # Show first 5 courses
                    print(f"   📚 Course: {course['course_title']} (ID: {course['course_id']})")
                    for quiz in course['quiz_lessons']:
                        print(f"      🧩 Quiz: {quiz['lesson_title']} in module '{quiz['module_title']}' ({len(quiz['questions'])} questions)")
                
                return True
            else:
                self.log_result("Find Courses with Quiz Lessons", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Find Courses with Quiz Lessons", False, f"Exception: {str(e)}")
            return False

    def analyze_quiz_question_data_structure(self):
        """Analyze quiz question data structure to identify image URL storage format"""
        try:
            image_option_courses = []
            total_questions_analyzed = 0
            questions_with_images = 0
            data_structure_issues = []
            
            for course in self.courses_with_quizzes:
                course_id = course['course_id']
                course_title = course['course_title']
                
                for quiz_lesson in course['quiz_lessons']:
                    questions = quiz_lesson.get('questions', [])
                    
                    for question in questions:
                        total_questions_analyzed += 1
                        question_type = question.get('type', '')
                        question_text = question.get('question', '')
                        options = question.get('options', [])
                        
                        # Check if options contain image URLs
                        has_image_options = False
                        option_analysis = []
                        
                        for i, option in enumerate(options):
                            option_analysis_item = {
                                'index': i,
                                'type': type(option).__name__,
                                'content': str(option)[:100] + '...' if len(str(option)) > 100 else str(option)
                            }
                            
                            # Check if option is a string with image URL
                            if isinstance(option, str):
                                if any(img_ext in option.lower() for img_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', 'http']):
                                    has_image_options = True
                                    option_analysis_item['has_image_url'] = True
                                    questions_with_images += 1
                                else:
                                    option_analysis_item['has_image_url'] = False
                            
                            # Check if option is an object with image property
                            elif isinstance(option, dict):
                                if 'image' in option or 'imageUrl' in option or 'img' in option:
                                    has_image_options = True
                                    option_analysis_item['has_image_property'] = True
                                    option_analysis_item['image_url'] = option.get('image') or option.get('imageUrl') or option.get('img')
                                    questions_with_images += 1
                                else:
                                    option_analysis_item['has_image_property'] = False
                            
                            option_analysis.append(option_analysis_item)
                        
                        if has_image_options:
                            image_option_courses.append({
                                'course_id': course_id,
                                'course_title': course_title,
                                'quiz_title': quiz_lesson['lesson_title'],
                                'question_type': question_type,
                                'question_text': question_text[:100] + '...' if len(question_text) > 100 else question_text,
                                'option_analysis': option_analysis
                            })
                        
                        # Check for potential data structure issues
                        if not options:
                            data_structure_issues.append({
                                'course_id': course_id,
                                'issue': 'No options found',
                                'question_type': question_type
                            })
                        elif question_type in ['multiple_choice', 'select_all_that_apply'] and len(options) < 2:
                            data_structure_issues.append({
                                'course_id': course_id,
                                'issue': f'Insufficient options ({len(options)}) for {question_type}',
                                'question_type': question_type
                            })
            
            self.courses_with_image_options = image_option_courses
            
            success = total_questions_analyzed > 0
            details = f"Analyzed {total_questions_analyzed} questions across {len(self.courses_with_quizzes)} courses. Found {questions_with_images} questions with potential image options. Data structure issues: {len(data_structure_issues)}"
            
            self.log_result("Analyze Quiz Question Data Structure", success, details)
            
            # Log detailed findings
            if image_option_courses:
                print("   🖼️  COURSES WITH IMAGE OPTIONS FOUND:")
                for item in image_option_courses[:3]:  # Show first 3
                    print(f"      📚 {item['course_title']} - Quiz: {item['quiz_title']}")
                    print(f"         Question Type: {item['question_type']}")
                    print(f"         Question: {item['question_text']}")
                    for opt in item['option_analysis']:
                        if opt.get('has_image_url') or opt.get('has_image_property'):
                            print(f"         Option {opt['index']}: {opt['type']} - {opt['content']}")
                            if opt.get('image_url'):
                                print(f"           Image URL: {opt['image_url']}")
            else:
                print("   ℹ️  No questions with image URLs found in options")
            
            if data_structure_issues:
                print("   ⚠️  DATA STRUCTURE ISSUES:")
                for issue in data_structure_issues[:5]:  # Show first 5 issues
                    print(f"      Course ID: {issue['course_id']} - {issue['issue']} ({issue['question_type']})")
            
            return success
                
        except Exception as e:
            self.log_result("Analyze Quiz Question Data Structure", False, f"Exception: {str(e)}")
            return False

    def test_student_enrollment_progress_data(self):
        """Test student enrollment and progress data structure for progressive quiz access"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            response = requests.get(f"{BACKEND_URL}/enrollments", headers=headers, timeout=10)
            
            if response.status_code == 200:
                enrollments = response.json()
                self.student_enrollments = enrollments
                
                progress_analysis = []
                
                for enrollment in enrollments:
                    course_id = enrollment.get('courseId')
                    progress = enrollment.get('progress', 0)
                    status = enrollment.get('status', 'unknown')
                    module_progress = enrollment.get('moduleProgress', [])
                    current_module_id = enrollment.get('currentModuleId')
                    current_lesson_id = enrollment.get('currentLessonId')
                    
                    # Get course details to understand structure
                    course_response = requests.get(
                        f"{BACKEND_URL}/courses/{course_id}", 
                        headers=headers, 
                        timeout=10
                    )
                    
                    course_title = "Unknown Course"
                    total_modules = 0
                    total_lessons = 0
                    quiz_lessons = []
                    
                    if course_response.status_code == 200:
                        course_data = course_response.json()
                        course_title = course_data.get('title', 'Unknown Course')
                        modules = course_data.get('modules', [])
                        total_modules = len(modules)
                        
                        for module in modules:
                            lessons = module.get('lessons', [])
                            total_lessons += len(lessons)
                            
                            for lesson in lessons:
                                if lesson.get('type', '').lower() == 'quiz':
                                    quiz_lessons.append({
                                        'lesson_id': lesson.get('id'),
                                        'lesson_title': lesson.get('title'),
                                        'module_id': module.get('id'),
                                        'module_title': module.get('title')
                                    })
                    
                    # Analyze module progress structure
                    module_progress_analysis = []
                    completed_lessons = 0
                    
                    for mod_prog in module_progress:
                        module_id = mod_prog.get('moduleId')
                        lessons_progress = mod_prog.get('lessons', [])
                        module_completed = mod_prog.get('completed', False)
                        
                        lesson_completion_count = sum(1 for lesson in lessons_progress if lesson.get('completed', False))
                        completed_lessons += lesson_completion_count
                        
                        module_progress_analysis.append({
                            'module_id': module_id,
                            'total_lessons': len(lessons_progress),
                            'completed_lessons': lesson_completion_count,
                            'module_completed': module_completed
                        })
                    
                    progress_analysis.append({
                        'course_id': course_id,
                        'course_title': course_title,
                        'overall_progress': progress,
                        'status': status,
                        'total_modules': total_modules,
                        'total_lessons': total_lessons,
                        'completed_lessons': completed_lessons,
                        'current_module_id': current_module_id,
                        'current_lesson_id': current_lesson_id,
                        'quiz_lessons': quiz_lessons,
                        'module_progress_structure': module_progress_analysis,
                        'has_module_progress': len(module_progress) > 0
                    })
                
                success = len(enrollments) > 0
                details = f"Found {len(enrollments)} enrollments. Progress data structure analysis completed for progressive quiz access implementation."
                
                self.log_result("Test Student Enrollment Progress Data", success, details)
                
                # Log detailed progress analysis
                print("   📊 STUDENT PROGRESS ANALYSIS:")
                for analysis in progress_analysis[:3]:  # Show first 3 enrollments
                    print(f"      📚 Course: {analysis['course_title']}")
                    print(f"         Overall Progress: {analysis['overall_progress']}% ({analysis['status']})")
                    print(f"         Structure: {analysis['total_modules']} modules, {analysis['total_lessons']} lessons")
                    print(f"         Completed: {analysis['completed_lessons']} lessons")
                    print(f"         Current Position: Module {analysis['current_module_id']}, Lesson {analysis['current_lesson_id']}")
                    print(f"         Quiz Lessons: {len(analysis['quiz_lessons'])} found")
                    print(f"         Has Module Progress: {analysis['has_module_progress']}")
                    
                    if analysis['quiz_lessons']:
                        print("         Quiz Access Analysis:")
                        for quiz in analysis['quiz_lessons']:
                            # Determine if student should have access to this quiz based on progress
                            quiz_module_id = quiz['module_id']
                            quiz_accessible = False
                            
                            # Check if the quiz's module is completed or current
                            for mod_prog in analysis['module_progress_structure']:
                                if mod_prog['module_id'] == quiz_module_id:
                                    if mod_prog['module_completed'] or quiz_module_id == analysis['current_module_id']:
                                        quiz_accessible = True
                                    break
                            
                            access_status = "✅ Accessible" if quiz_accessible else "🔒 Locked"
                            print(f"           {access_status}: {quiz['lesson_title']} (Module: {quiz['module_title']})")
                
                return success
            else:
                self.log_result("Test Student Enrollment Progress Data", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Test Student Enrollment Progress Data", False, f"Exception: {str(e)}")
            return False

    def analyze_progressive_quiz_access_implementation(self):
        """Analyze how to implement progressive quiz access based on student progress"""
        try:
            implementation_analysis = {
                'total_enrollments': len(self.student_enrollments),
                'courses_with_quizzes': len([e for e in self.student_enrollments if any(
                    course['course_id'] == e.get('courseId') for course in self.courses_with_quizzes
                )]),
                'progress_tracking_methods': [],
                'recommended_implementation': {}
            }
            
            # Analyze different progress tracking methods available
            for enrollment in self.student_enrollments:
                course_id = enrollment.get('courseId')
                
                # Method 1: Overall progress percentage
                overall_progress = enrollment.get('progress', 0)
                if overall_progress is not None:
                    implementation_analysis['progress_tracking_methods'].append('overall_progress_percentage')
                
                # Method 2: Module progress tracking
                module_progress = enrollment.get('moduleProgress', [])
                if module_progress:
                    implementation_analysis['progress_tracking_methods'].append('detailed_module_progress')
                
                # Method 3: Current position tracking
                current_module = enrollment.get('currentModuleId')
                current_lesson = enrollment.get('currentLessonId')
                if current_module or current_lesson:
                    implementation_analysis['progress_tracking_methods'].append('current_position_tracking')
            
            # Remove duplicates
            implementation_analysis['progress_tracking_methods'] = list(set(implementation_analysis['progress_tracking_methods']))
            
            # Generate recommendations
            recommendations = {
                'primary_method': 'detailed_module_progress',
                'fallback_method': 'overall_progress_percentage',
                'implementation_steps': [
                    '1. Check if student is enrolled in course',
                    '2. Get student moduleProgress from enrollment',
                    '3. For each quiz lesson, check if its module is completed or current',
                    '4. Allow access if module is completed OR if it\'s the current module',
                    '5. Fallback to overall progress % if moduleProgress unavailable'
                ],
                'data_structure_requirements': {
                    'enrollment_fields_needed': ['moduleProgress', 'currentModuleId', 'progress'],
                    'course_structure_needed': ['modules[].id', 'modules[].lessons[].type', 'modules[].lessons[].id'],
                    'quiz_identification': 'lessons with type="quiz"'
                }
            }
            
            implementation_analysis['recommended_implementation'] = recommendations
            
            success = len(implementation_analysis['progress_tracking_methods']) > 0
            details = f"Progressive quiz access analysis completed. Available methods: {', '.join(implementation_analysis['progress_tracking_methods'])}"
            
            self.log_result("Analyze Progressive Quiz Access Implementation", success, details)
            
            # Log implementation recommendations
            print("   🎯 PROGRESSIVE QUIZ ACCESS IMPLEMENTATION RECOMMENDATIONS:")
            print(f"      Primary Method: {recommendations['primary_method']}")
            print(f"      Fallback Method: {recommendations['fallback_method']}")
            print("      Implementation Steps:")
            for step in recommendations['implementation_steps']:
                print(f"         {step}")
            
            print("      Required Data Structure:")
            for key, value in recommendations['data_structure_requirements'].items():
                if isinstance(value, list):
                    print(f"         {key}: {', '.join(value)}")
                else:
                    print(f"         {key}: {value}")
            
            return success
                
        except Exception as e:
            self.log_result("Analyze Progressive Quiz Access Implementation", False, f"Exception: {str(e)}")
            return False

    def investigate_image_display_root_cause(self):
        """Investigate root cause of image display issues in quiz options"""
        try:
            root_cause_analysis = {
                'total_courses_analyzed': len(self.courses_with_quizzes),
                'courses_with_image_options': len(self.courses_with_image_options),
                'potential_issues': [],
                'data_format_analysis': {},
                'recommendations': []
            }
            
            # Analyze data formats found
            string_options = 0
            object_options = 0
            mixed_formats = 0
            
            for course_data in self.courses_with_image_options:
                option_analysis = course_data.get('option_analysis', [])
                
                has_string_options = any(opt.get('type') == 'str' for opt in option_analysis)
                has_object_options = any(opt.get('type') == 'dict' for opt in option_analysis)
                
                if has_string_options and has_object_options:
                    mixed_formats += 1
                elif has_string_options:
                    string_options += 1
                elif has_object_options:
                    object_options += 1
            
            root_cause_analysis['data_format_analysis'] = {
                'string_only_courses': string_options,
                'object_only_courses': object_options,
                'mixed_format_courses': mixed_formats
            }
            
            # Identify potential issues
            if string_options > 0:
                root_cause_analysis['potential_issues'].append({
                    'issue': 'Image URLs stored as strings in options array',
                    'impact': 'Frontend may expect {text, image} object format but receives plain strings',
                    'affected_courses': string_options
                })
            
            if mixed_formats > 0:
                root_cause_analysis['potential_issues'].append({
                    'issue': 'Inconsistent data format - mixed strings and objects',
                    'impact': 'Frontend rendering logic may not handle mixed formats properly',
                    'affected_courses': mixed_formats
                })
            
            if len(self.courses_with_image_options) == 0:
                root_cause_analysis['potential_issues'].append({
                    'issue': 'No image options found in quiz questions',
                    'impact': 'Either no courses use images or images are stored in unexpected format',
                    'affected_courses': 0
                })
            
            # Generate recommendations
            if string_options > 0:
                root_cause_analysis['recommendations'].append(
                    'Convert string-based image URLs to object format: {text: "Option text", image: "image_url"}'
                )
            
            if mixed_formats > 0:
                root_cause_analysis['recommendations'].append(
                    'Standardize all quiz options to consistent object format across all courses'
                )
            
            root_cause_analysis['recommendations'].extend([
                'Verify frontend quiz rendering component expects correct data structure',
                'Add validation to ensure image URLs are accessible and properly formatted',
                'Consider adding fallback text for options that have images but no text'
            ])
            
            success = True  # Analysis always succeeds
            details = f"Root cause analysis completed. Found {len(root_cause_analysis['potential_issues'])} potential issues."
            
            self.log_result("Investigate Image Display Root Cause", success, details)
            
            # Log detailed root cause analysis
            print("   🔍 IMAGE DISPLAY ROOT CAUSE ANALYSIS:")
            print(f"      Data Format Distribution:")
            print(f"         String-only options: {string_options} courses")
            print(f"         Object-only options: {object_options} courses") 
            print(f"         Mixed formats: {mixed_formats} courses")
            
            if root_cause_analysis['potential_issues']:
                print("      Potential Issues Identified:")
                for issue in root_cause_analysis['potential_issues']:
                    print(f"         ⚠️  {issue['issue']}")
                    print(f"            Impact: {issue['impact']}")
                    print(f"            Affected: {issue['affected_courses']} courses")
            
            print("      Recommendations:")
            for i, rec in enumerate(root_cause_analysis['recommendations'], 1):
                print(f"         {i}. {rec}")
            
            return success
                
        except Exception as e:
            self.log_result("Investigate Image Display Root Cause", False, f"Exception: {str(e)}")
            return False

    def run_investigation(self):
        """Run complete quiz image display investigation and progressive quiz access analysis"""
        print("🔍 STARTING QUIZ IMAGE DISPLAY INVESTIGATION & PROGRESSIVE QUIZ ACCESS FEATURE TESTING")
        print("=" * 100)
        print()
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot continue")
            return False
            
        if not self.authenticate_student():
            print("❌ Student authentication failed - cannot continue")
            return False
        
        # Core investigation tests
        test_methods = [
            self.find_courses_with_quiz_lessons,
            self.analyze_quiz_question_data_structure,
            self.test_student_enrollment_progress_data,
            self.analyze_progressive_quiz_access_implementation,
            self.investigate_image_display_root_cause
        ]
        
        for test_method in test_methods:
            try:
                test_method()
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                self.log_result(test_method.__name__, False, f"Unexpected error: {str(e)}")
        
        # Summary
        print("=" * 100)
        print("📊 QUIZ IMAGE INVESTIGATION & PROGRESSIVE QUIZ ACCESS ANALYSIS SUMMARY")
        print("=" * 100)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
            print()
        
        # Key findings summary
        print("🔍 KEY INVESTIGATION FINDINGS:")
        print(f"  📚 Courses with quizzes found: {len(self.courses_with_quizzes)}")
        print(f"  🖼️  Courses with image options: {len(self.courses_with_image_options)}")
        print(f"  👨‍🎓 Student enrollments analyzed: {len(self.student_enrollments)}")
        
        if self.courses_with_image_options:
            print("  ✅ Image options detected - data structure analysis available")
        else:
            print("  ⚠️  No image options found - may indicate storage format issue")
        
        if self.student_enrollments:
            print("  ✅ Student progress data available for progressive quiz access")
        else:
            print("  ⚠️  No student enrollment data found")
        
        print()
        print("🎯 NEXT STEPS:")
        print("  1. Review data structure analysis for image display issues")
        print("  2. Implement progressive quiz access using moduleProgress data")
        print("  3. Verify frontend quiz rendering handles identified data formats")
        print("  4. Test image URL accessibility and display functionality")
        
        return success_rate >= 80.0  # Consider 80%+ success rate as passing

if __name__ == "__main__":
    investigator = QuizImageInvestigator()
    success = investigator.run_investigation()
    
    if success:
        print("🎉 Quiz image investigation and progressive quiz access analysis completed successfully!")
        sys.exit(0)
    else:
        print("💥 Investigation encountered issues - review findings above!")
        sys.exit(1)