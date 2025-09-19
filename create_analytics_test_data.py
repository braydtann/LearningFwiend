#!/usr/bin/env python3
"""
Create test data for analytics dashboard testing
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class AnalyticsTestDataCreator:
    def __init__(self):
        self.base_url = "https://lms-debugfix.preview.emergentagent.com/api"
        self.admin_token = None
        self.student_token = None
        
        # Test credentials
        self.admin_credentials = {
            "username_or_email": "brayden.t@covesmart.com",
            "password": "Hawaii2020!"
        }
        
        self.student_credentials = {
            "username_or_email": "karlo.student@alder.com", 
            "password": "StudentPermanent123!"
        }

    def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=self.admin_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                print("✅ Admin authenticated successfully")
                return True
            else:
                print(f"❌ Admin authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Admin authentication error: {str(e)}")
            return False

    def authenticate_student(self) -> bool:
        """Authenticate as student user"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=self.student_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data.get("access_token")
                print("✅ Student authenticated successfully")
                return True
            else:
                print(f"❌ Student authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Student authentication error: {str(e)}")
            return False

    def get_available_courses(self) -> List[Dict]:
        """Get all available courses"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.base_url}/courses", headers=headers, timeout=10)
            
            if response.status_code == 200:
                courses = response.json()
                print(f"✅ Found {len(courses)} courses")
                return courses
            else:
                print(f"❌ Failed to get courses: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting courses: {str(e)}")
            return []

    def enroll_student_in_courses(self, courses: List[Dict]) -> List[str]:
        """Enroll student in all available courses"""
        enrolled_course_ids = []
        
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            for course in courses:
                course_id = course.get('id')
                course_title = course.get('title', 'Unknown')
                
                enrollment_data = {"courseId": course_id}
                
                response = requests.post(
                    f"{self.base_url}/enrollments",
                    json=enrollment_data,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    enrolled_course_ids.append(course_id)
                    print(f"✅ Enrolled in course: {course_title}")
                else:
                    print(f"❌ Failed to enroll in {course_title}: {response.status_code}")
            
            print(f"✅ Successfully enrolled in {len(enrolled_course_ids)} courses")
            return enrolled_course_ids
            
        except Exception as e:
            print(f"❌ Error enrolling in courses: {str(e)}")
            return []

    def simulate_quiz_attempts(self, course_ids: List[str]) -> bool:
        """Simulate quiz attempts by updating enrollment progress"""
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            
            # Different scores to create variety
            test_scores = [50, 75, 85, 100, 65, 90, 45, 80, 95, 70]
            
            for i, course_id in enumerate(course_ids):
                score = test_scores[i % len(test_scores)]
                
                progress_data = {
                    "progress": score,
                    "currentModuleId": "module-1",
                    "currentLessonId": "lesson-1",
                    "timeSpent": 300 + (i * 60)  # Varying time spent
                }
                
                response = requests.put(
                    f"{self.base_url}/enrollments/{course_id}/progress",
                    json=progress_data,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"✅ Updated progress for course {course_id}: {score}%")
                else:
                    print(f"❌ Failed to update progress for course {course_id}: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error simulating quiz attempts: {str(e)}")
            return False

    def create_test_data(self):
        """Create comprehensive test data for analytics"""
        print("🎯 CREATING ANALYTICS TEST DATA")
        print("=" * 50)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            return False
        
        if not self.authenticate_student():
            return False
        
        # Step 2: Get available courses
        courses = self.get_available_courses()
        if not courses:
            print("❌ No courses available for enrollment")
            return False
        
        # Step 3: Enroll student in courses
        enrolled_course_ids = self.enroll_student_in_courses(courses)
        if not enrolled_course_ids:
            print("❌ Failed to enroll in any courses")
            return False
        
        # Step 4: Simulate quiz attempts
        if not self.simulate_quiz_attempts(enrolled_course_ids):
            print("❌ Failed to simulate quiz attempts")
            return False
        
        print("\n🎉 SUCCESS: Analytics test data created successfully!")
        print(f"   - Enrolled in {len(enrolled_course_ids)} courses")
        print(f"   - Simulated quiz attempts with varying scores")
        print("   - Analytics dashboard should now show actual data")
        
        return True

def main():
    """Main execution function"""
    creator = AnalyticsTestDataCreator()
    
    try:
        success = creator.create_test_data()
        
        if success:
            print("\n✅ Test data creation completed successfully!")
            return 0
        else:
            print("\n❌ Test data creation failed!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Test data creation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)