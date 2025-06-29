import json
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

def verify_import():
    service = authenticate()
    
    # Get all courses
    courses = service.courses().list().execute()
    
    # Find our imported course
    imported_course = None
    for course in courses.get('courses', []):
        if 'November Cohort 2024' in course.get('name', ''):
            imported_course = course
            break
    
    if not imported_course:
        print("❌ Imported course not found!")
        return
    
    course_id = imported_course['id']
    course_name = imported_course['name']
    
    print(f"✅ Found imported course: {course_name} (ID: {course_id})")
    
    # Get topics
    topics = service.courses().topics().list(courseId=course_id).execute()
    print(f"\n📚 Topics found: {len(topics.get('topic', []))}")
    
    for topic in topics.get('topic', []):
        topic_name = topic.get('name', 'Unknown')
        topic_id = topic.get('topicId', '')
        print(f"  - {topic_name} (ID: {topic_id})")
    
    # Get coursework (assignments)
    coursework = service.courses().courseWork().list(courseId=course_id).execute()
    print(f"\n📝 Classwork/Assignments found: {len(coursework.get('courseWork', []))}")
    
    for work in coursework.get('courseWork', []):
        title = work.get('title', 'Unknown')
        work_type = work.get('workType', 'Unknown')
        state = work.get('state', 'Unknown')
        topic_id = work.get('topicId', 'No topic')
        
        print(f"  - {title}")
        print(f"    Type: {work_type}")
        print(f"    State: {state}")
        print(f"    Topic ID: {topic_id}")
        print()
    
    # Get course materials
    materials = service.courses().courseWorkMaterials().list(courseId=course_id).execute()
    print(f"📋 Course materials found: {len(materials.get('courseWorkMaterial', []))}")

if __name__ == '__main__':
    verify_import() 