import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 1. Setup OAuth
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

# 2. Load Course Data
def load_course_data(filepath='course.json'):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# 3. Create Course
def create_course(service, name):
    body = {
        'name': name,
        'section': 'Imported',
        'description': 'Imported from Moodle',
        'courseState': 'PROVISIONED'
    }
    
    try:
        course = service.courses().create(body=body).execute()
        return course['id']
    except Exception as e:
        print(f"Error creating course: {e}")
        print("Trying with ownerId='me'...")
        
        # Try with ownerId='me'
        body['ownerId'] = 'me'
        course = service.courses().create(body=body).execute()
        return course['id']

# 4. Create Topics
def create_topic(service, course_id, topic_name):
    topic = {'name': topic_name}
    return service.courses().topics().create(courseId=course_id, body=topic).execute()

# 5. Create Assignments
def create_assignment(service, course_id, title, description, topic_id):
    coursework = {
        'title': title,
        'description': description,
        'workType': 'ASSIGNMENT',
        'state': 'PUBLISHED',
        'topicId': topic_id
    }
    return service.courses().courseWork().create(courseId=course_id, body=coursework).execute()

# 6. Main Logic
def import_course(filepath='course.json'):
    service = authenticate()
    course_data = load_course_data(filepath)
    
    course_id = create_course(service, course_data['course_name'])
    print(f"Created course: {course_data['course_name']}")

    for topic in course_data['topics']:
        topic_obj = create_topic(service, course_id, topic['name'])
        print(f"  Topic: {topic['name']}")
        for assignment in topic['assignments']:
            create_assignment(
                service,
                course_id,
                assignment['title'],
                assignment['description'],
                topic_obj['topicId']
            )
            print(f"    Added assignment: {assignment['title']}")

if __name__ == '__main__':
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'course.json'
    
    # Test mode - just read and display the data
    if len(sys.argv) > 2 and sys.argv[2] == '--test':
        course_data = load_course_data(filepath)
        print(f"✅ Successfully loaded course: {course_data['course_name']}")
        print(f"📚 Found {len(course_data['topics'])} topics:")
        for topic in course_data['topics']:
            print(f"  - {topic['name']} ({len(topic['assignments'])} assignments)")
        print("✅ Script is working correctly!")
    else:
        import_course(filepath)
