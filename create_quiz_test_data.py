#!/usr/bin/env python3
"""
Create test data for QuizResults component testing
"""

import requests
import json
import sys

def create_quiz_test_data():
    base_url = "https://lms-analytics-hub.preview.emergentagent.com/api"
    
    # Login as admin
    admin_creds = {'username_or_email': 'brayden.t@covesmart.com', 'password': 'Hawaii2020!'}
    response = requests.post(f'{base_url}/auth/login', json=admin_creds)
    if response.status_code != 200:
        print(f"❌ Admin login failed: {response.status_code}")
        return False
    
    admin_token = response.json()['access_token']
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Get students
    users_response = requests.get(f'{base_url}/auth/admin/users', headers=admin_headers)
    if users_response.status_code != 200:
        print(f"❌ Failed to get users: {users_response.status_code}")
        return False
    
    users = users_response.json()
    students = [u for u in users if u['role'] == 'learner']
    
    if len(students) < 2:
        print(f"❌ Need at least 2 students, found {len(students)}")
        return False
    
    # Get courses
    courses_response = requests.get(f'{base_url}/courses', headers=admin_headers)
    if courses_response.status_code != 200:
        print(f"❌ Failed to get courses: {courses_response.status_code}")
        return False
    
    courses = courses_response.json()
    if len(courses) < 2:
        print(f"❌ Need at least 2 courses, found {len(courses)}")
        return False
    
    print(f"✅ Found {len(students)} students and {len(courses)} courses")
    
    # Create enrollments with different progress levels
    enrollments_created = 0
    
    for i, student in enumerate(students):
        for j, course in enumerate(courses):
            # Create enrollment
            enrollment_data = {'courseId': course['id']}
            
            # Login as student first
            student_creds = {'username_or_email': student['email'], 'password': 'StudentPermanent123!'}
            student_login = requests.post(f'{base_url}/auth/login', json=student_creds)
            
            if student_login.status_code != 200:
                print(f"⚠️  Student {student['email']} login failed, skipping")
                continue
            
            student_token = student_login.json()['access_token']
            student_headers = {'Authorization': f'Bearer {student_token}'}
            
            # Create enrollment
            enroll_response = requests.post(f'{base_url}/enrollments', json=enrollment_data, headers=student_headers)
            
            if enroll_response.status_code == 200:
                # Update progress with different levels
                progress_levels = [25.0, 50.0, 75.0, 100.0]
                progress = progress_levels[(i + j) % len(progress_levels)]
                
                progress_data = {
                    'progress': progress,
                    'currentModuleId': course.get('modules', [{}])[0].get('id') if course.get('modules') else None,
                    'currentLessonId': None
                }
                
                progress_response = requests.put(
                    f'{base_url}/enrollments/{course["id"]}/progress',
                    json=progress_data,
                    headers=student_headers
                )
                
                if progress_response.status_code == 200:
                    enrollments_created += 1
                    print(f"✅ Created enrollment: {student['full_name']} -> {course['title']} ({progress}%)")
                else:
                    print(f"⚠️  Failed to update progress: {progress_response.status_code}")
            elif enroll_response.status_code == 400 and "already enrolled" in enroll_response.text:
                # Already enrolled, just update progress
                progress_levels = [25.0, 50.0, 75.0, 100.0]
                progress = progress_levels[(i + j) % len(progress_levels)]
                
                progress_data = {
                    'progress': progress,
                    'currentModuleId': course.get('modules', [{}])[0].get('id') if course.get('modules') else None,
                    'currentLessonId': None
                }
                
                progress_response = requests.put(
                    f'{base_url}/enrollments/{course["id"]}/progress',
                    json=progress_data,
                    headers=student_headers
                )
                
                if progress_response.status_code == 200:
                    enrollments_created += 1
                    print(f"✅ Updated enrollment: {student['full_name']} -> {course['title']} ({progress}%)")
                else:
                    print(f"⚠️  Failed to update progress: {progress_response.status_code}")
            else:
                print(f"⚠️  Failed to create enrollment: {enroll_response.status_code}")
    
    print(f"\n🎉 Created/updated {enrollments_created} enrollments with quiz progress data")
    return enrollments_created > 0

if __name__ == "__main__":
    success = create_quiz_test_data()
    sys.exit(0 if success else 1)