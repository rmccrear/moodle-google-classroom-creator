import json
import os
from datetime import datetime
from googleapiclient.discovery import build
from auth_cache import get_cached_credentials
import re
from bs4 import BeautifulSoup

# Helper function to get unique course name
def get_unique_course_name(service, base_name):
    """Check if course name exists and return a unique name with number suffix if needed"""
    try:
        # Get all courses
        courses = service.courses().list().execute()
        
        if 'courses' not in courses:
            return base_name
        
        existing_names = []
        for course in courses['courses']:
            # Only check active courses (not archived)
            if course.get('courseState') != 'ARCHIVED':
                existing_names.append(course['name'])
        
        # If base name doesn't exist, return it
        if base_name not in existing_names:
            return base_name
        
        # Find the next available number
        counter = 1
        while True:
            new_name = f"{base_name} ({counter})"
            if new_name not in existing_names:
                return new_name
            counter += 1
            
    except Exception as e:
        print(f"Warning: Could not check existing courses: {e}")
        return base_name

# 2. Load Course Data
def load_course_data(filepath='course.json'):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# 3. Create Course
def create_course(service, name):
    # Get unique course name
    unique_name = get_unique_course_name(service, name)
    
    if unique_name != name:
        print(f"⚠️  Course name '{name}' already exists. Using '{unique_name}' instead.")
    
    body = {
        'name': unique_name,
        'section': 'Imported',
        'description': 'Imported from Moodle',
        'courseState': 'PROVISIONED'
    }
    
    try:
        course = service.courses().create(body=body).execute()
        return course['id'], unique_name
    except Exception as e:
        print(f"Error creating course: {e}")
        print("Trying with ownerId='me'...")
        
        # Try with ownerId='me'
        body['ownerId'] = 'me'
        course = service.courses().create(body=body).execute()
        return course['id'], unique_name

# 4. Create Topics
def sanitize_topic_name(name):
    """Sanitize topic name for Google Classroom by removing invalid characters"""
    # Handle None or empty names
    if not name:
        return "Untitled Topic"
    
    # Remove or replace characters that cause issues in Google Classroom
    # Remove parentheses, brackets, and other special characters
    sanitized = name.replace('(', '').replace(')', '')
    sanitized = sanitized.replace('[', '').replace(']', '')
    sanitized = sanitized.replace('{', '').replace('}', '')
    sanitized = sanitized.replace('<', '').replace('>', '')
    sanitized = sanitized.replace('&', 'and')
    sanitized = sanitized.replace('|', '-')
    sanitized = sanitized.replace(':', ' -')
    sanitized = sanitized.replace(';', '')
    sanitized = sanitized.replace('"', '').replace("'", '')
    sanitized = sanitized.replace('/', ' - ')
    sanitized = sanitized.replace('\\', ' - ')
    
    # Remove extra spaces and trim
    sanitized = ' '.join(sanitized.split())
    
    # Ensure the name isn't too long (Google Classroom has limits)
    if len(sanitized) > 100:
        sanitized = sanitized[:97] + "..."
    
    return sanitized

def create_topic(service, course_id, topic_name):
    """Create a topic in the course"""
    topic = {
        'name': sanitize_topic_name(topic_name)
    }
    return service.courses().topics().create(courseId=course_id, body=topic).execute()

# 5. Create Assignments
def convert_html_for_classroom(html):
    """
    Convert HTML to plain text with Markdown-style formatting that Google Classroom will display.
    - Headings -> ALL CAPS with line breaks
    - Bold -> **text**
    - Italic -> *text*
    - Lists -> - item
    - Tables -> simple text format
    - Links -> [text](url)
    - Code -> `code`
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Convert headings to ALL CAPS with line breaks
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        tag.string = f"\n\n{tag.get_text(strip=True).upper()}\n\n"
        tag.name = 'p'
    
    # Convert <strong> and <b> to **text**
    for tag in soup.find_all(['strong', 'b']):
        tag.string = f"**{tag.get_text(strip=True)}**"
        tag.name = 'span'
    
    # Convert <em> and <i> to *text*
    for tag in soup.find_all(['em', 'i']):
        tag.string = f"*{tag.get_text(strip=True)}*"
        tag.name = 'span'
    
    # Convert <u> to _text_
    for tag in soup.find_all('u'):
        tag.string = f"_{tag.get_text(strip=True)}_"
        tag.name = 'span'
    
    # Convert <code> to `code`
    for tag in soup.find_all('code'):
        tag.string = f"`{tag.get_text(strip=True)}`"
        tag.name = 'span'
    
    # Convert <pre> to code blocks
    for tag in soup.find_all('pre'):
        tag.string = f"\n```\n{tag.get_text(strip=True)}\n```\n"
        tag.name = 'p'
    
    # Convert <hr> to dashed line
    for tag in soup.find_all('hr'):
        tag.string = "\n\n---\n\n"
        tag.name = 'p'
    
    # Convert tables to simple text format
    for table in soup.find_all('table'):
        table_text = "\n"
        for row in table.find_all('tr'):
            row_text = " | ".join(cell.get_text(strip=True) for cell in row.find_all(['td', 'th']))
            table_text += row_text + "\n"
        table.string = table_text
        table.name = 'p'
    
    # Convert <ul> and <ol> to Markdown lists
    for tag in soup.find_all(['ul', 'ol']):
        list_items = []
        for li in tag.find_all('li'):
            list_items.append(f"- {li.get_text(strip=True)}")
        tag.string = "\n" + "\n".join(list_items) + "\n"
        tag.name = 'p'
    
    # Convert <a> to [text](url)
    for tag in soup.find_all('a'):
        href = tag.get('href', '')
        text = tag.get_text(strip=True)
        if href:
            tag.string = f"[{text}]({href})"
        else:
            tag.string = text
        tag.name = 'span'
    
    # Convert <p> to plain text with line breaks
    for tag in soup.find_all('p'):
        if tag.get_text(strip=True):
            tag.string = tag.get_text(strip=True) + "\n\n"
    
    # Convert <br> to line breaks
    for tag in soup.find_all('br'):
        tag.string = "\n"
        tag.name = 'span'
    
    # Remove all other tags but keep their content
    for tag in soup.find_all(True):
        if tag.name not in ['p', 'span']:
            tag.unwrap()
    
    # Get the final text and clean it up
    text = soup.get_text()
    
    # Clean up extra whitespace and line breaks
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Remove excessive line breaks
    text = re.sub(r' +', ' ', text)  # Remove excessive spaces
    text = text.strip()
    
    return text

def create_assignment(service, course_id, title, description, topic_id):
    # Convert description HTML to supported format
    description = convert_html_for_classroom(description)
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
    
    course_id, course_name = create_course(service, course_data['course_name'])
    print(f"Created course: {course_name}")

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
        course_name, 
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
