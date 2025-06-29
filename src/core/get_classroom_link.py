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

def get_classroom_link():
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
    
    # Generate the classroom URL
    classroom_url = f"https://classroom.google.com/c/{course_id}"
    
    print(f"✅ Course: {course_name}")
    print(f"🆔 Course ID: {course_id}")
    print(f"🔗 Classroom URL: {classroom_url}")
    print(f"\n📋 Direct link to Classwork: {classroom_url}/c/{course_id}/t/all")

if __name__ == '__main__':
    get_classroom_link() 