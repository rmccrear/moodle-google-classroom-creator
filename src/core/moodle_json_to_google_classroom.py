import json
import os
from datetime import datetime
from googleapiclient.discovery import build
from auth_cache import get_cached_credentials

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

# 6. Record Course Data
def record_course_data(course_id, course_name, topics_count, assignments_count, source_file):
    # Ensure class_data directory exists
    os.makedirs('class_data', exist_ok=True)
    
    # Load existing data or create new
    courses_file = 'class_data/courses.json'
    if os.path.exists(courses_file):
        with open(courses_file, 'r', encoding='utf-8') as f:
            courses_data = json.load(f)
    else:
        courses_data = {'courses': []}
    
    # Create new course record
    course_record = {
        'id': course_id,
        'name': course_name,
        'created_at': datetime.now().isoformat(),
        'topics_count': topics_count,
        'assignments_count': assignments_count,
        'source_file': source_file,
        'classroom_url': f"https://classroom.google.com/c/{course_id}",
        'status': 'active'
    }
    
    # Add to courses list
    courses_data['courses'].append(course_record)
    
    # Save updated data
    with open(courses_file, 'w', encoding='utf-8') as f:
        json.dump(courses_data, f, ensure_ascii=False, indent=2)
    
    print(f"📝 Course record saved to {courses_file}")

# 7. Main Logic
def import_course(filepath='course.json'):
    # Use cached credentials
    creds = get_cached_credentials()
    service = build('classroom', 'v1', credentials=creds)
    
    course_data = load_course_data(filepath)
    
    course_id = create_course(service, course_data['course_name'])
    print(f"Created course: {course_data['course_name']}")

    topics_count = 0
    assignments_count = 0
    
    for topic in course_data['topics']:
        topic_obj = create_topic(service, course_id, topic['name'])
        topics_count += 1
        print(f"  Topic: {topic['name']}")
        for assignment in topic['assignments']:
            create_assignment(
                service,
                course_id,
                assignment['title'],
                assignment['description'],
                topic_obj['topicId']
            )
            assignments_count += 1
            print(f"    Added assignment: {assignment['title']}")
    
    # Record the course data
    record_course_data(
        course_id, 
        course_data['course_name'], 
        topics_count, 
        assignments_count,
        filepath
    )
    
    print(f"\n🎉 Course import completed!")
    print(f"📊 Summary: {topics_count} topics, {assignments_count} assignments")
    print(f"🔗 Classroom URL: https://classroom.google.com/c/{course_id}")

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
