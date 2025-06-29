import json
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Setup OAuth
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses',
    'https://www.googleapis.com/auth/classroom.courseworkmaterials',
    'https://www.googleapis.com/auth/classroom.topics',
    'https://www.googleapis.com/auth/classroom.coursework.students'
]

def authenticate():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return build('classroom', 'v1', credentials=creds)

def load_course_records():
    """Load course records from class_data/courses.json"""
    courses_file = 'class_data/courses.json'
    if os.path.exists(courses_file):
        with open(courses_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'courses': []}

def save_course_records(courses_data):
    """Save course records to class_data/courses.json"""
    os.makedirs('class_data', exist_ok=True)
    with open('class_data/courses.json', 'w', encoding='utf-8') as f:
        json.dump(courses_data, f, ensure_ascii=False, indent=2)

def list_courses():
    """List all courses from both Google Classroom and local records"""
    service = authenticate()
    
    # Get courses from Google Classroom
    courses = service.courses().list().execute()
    
    print("📚 Google Classroom Courses:")
    print("=" * 50)
    
    for course in courses.get('courses', []):
        course_id = course['id']
        name = course.get('name', 'Unknown')
        state = course.get('courseState', 'Unknown')
        print(f"🆔 {course_id}")
        print(f"📖 {name}")
        print(f"📊 State: {state}")
        print(f"🔗 https://classroom.google.com/c/{course_id}")
        print("-" * 30)
    
    # Get local records
    courses_data = load_course_records()
    print(f"\n📝 Local Records ({len(courses_data['courses'])} courses):")
    print("=" * 50)
    
    for course in courses_data['courses']:
        print(f"🆔 {course['id']}")
        print(f"📖 {course['name']}")
        print(f"📅 Created: {course['created_at']}")
        print(f"📊 Topics: {course['topics_count']}, Assignments: {course['assignments_count']}")
        print(f"🔗 {course['classroom_url']}")
        print(f"📋 Status: {course['status']}")
        print("-" * 30)

def archive_course(course_id):
    """Archive a course in Google Classroom"""
    service = authenticate()
    
    try:
        # First get the current course to preserve its name
        course = service.courses().get(id=course_id).execute()
        course_name = course.get('name', 'Unknown Course')
        
        # Update course state to ARCHIVED while preserving the name
        body = {
            'name': course_name,
            'courseState': 'ARCHIVED'
        }
        updated_course = service.courses().update(id=course_id, body=body).execute()
        
        print(f"✅ Course {course_id} archived successfully!")
        
        # Update local record
        courses_data = load_course_records()
        for course_record in courses_data['courses']:
            if course_record['id'] == course_id:
                course_record['status'] = 'archived'
                break
        
        save_course_records(courses_data)
        print(f"📝 Local record updated")
        
    except Exception as e:
        print(f"❌ Error archiving course: {e}")

def delete_course(course_id):
    """Delete a course from Google Classroom"""
    service = authenticate()
    
    try:
        # Delete the course
        service.courses().delete(id=course_id).execute()
        print(f"✅ Course {course_id} deleted successfully!")
        
        # Remove from local records
        courses_data = load_course_records()
        courses_data['courses'] = [c for c in courses_data['courses'] if c['id'] != course_id]
        save_course_records(courses_data)
        print(f"📝 Removed from local records")
        
    except Exception as e:
        print(f"❌ Error deleting course: {e}")

def restore_course(course_id):
    """Restore an archived course"""
    service = authenticate()
    
    try:
        # Update course state to ACTIVE
        body = {'courseState': 'ACTIVE'}
        course = service.courses().update(id=course_id, body=body).execute()
        
        print(f"✅ Course {course_id} restored successfully!")
        
        # Update local record
        courses_data = load_course_records()
        for course_record in courses_data['courses']:
            if course_record['id'] == course_id:
                course_record['status'] = 'active'
                break
        
        save_course_records(courses_data)
        print(f"📝 Local record updated")
        
    except Exception as e:
        print(f"❌ Error restoring course: {e}")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_courses.py list                    # List all courses")
        print("  python manage_courses.py archive <course_id>     # Archive a course")
        print("  python manage_courses.py delete <course_id>      # Delete a course")
        print("  python manage_courses.py restore <course_id>     # Restore archived course")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_courses()
    
    elif command == 'archive':
        if len(sys.argv) < 3:
            print("❌ Please provide a course ID")
            return
        course_id = sys.argv[2]
        archive_course(course_id)
    
    elif command == 'delete':
        if len(sys.argv) < 3:
            print("❌ Please provide a course ID")
            return
        course_id = sys.argv[2]
        confirm = input(f"⚠️  Are you sure you want to DELETE course {course_id}? (yes/no): ")
        if confirm.lower() == 'yes':
            delete_course(course_id)
        else:
            print("❌ Deletion cancelled")
    
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("❌ Please provide a course ID")
            return
        course_id = sys.argv[2]
        restore_course(course_id)
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == '__main__':
    main() 