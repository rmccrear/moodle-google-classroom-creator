import zipfile
import tarfile
import os
import tempfile
import json
from datetime import datetime
from pathlib import Path
from lxml import etree

def parse_mbz(mbz_path):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Detect archive type
        is_zip = zipfile.is_zipfile(mbz_path)
        is_tar = tarfile.is_tarfile(mbz_path)
        if is_zip:
            with zipfile.ZipFile(mbz_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)
        elif is_tar:
            with tarfile.open(mbz_path, 'r') as tar_ref:
                tar_ref.extractall(tmpdir)
        else:
            raise ValueError("Unsupported archive format. Only .zip, .mbz, or .tar are supported.")

        # 1. Load course name
        backup_xml_path = os.path.join(tmpdir, 'moodle_backup.xml')
        backup_tree = etree.parse(backup_xml_path)
        course_name = backup_tree.findtext('.//original_course_fullname')

        # 2. Map sectionid -> section name
        sections = []
        section_map = {}
        section_dir = os.path.join(tmpdir, 'sections')
        
        # First pass: collect section sequences and basic info
        section_sequences = {}
        for folder in sorted(os.listdir(section_dir)):
            xml_path = os.path.join(section_dir, folder, 'section.xml')
            tree = etree.parse(xml_path)
            section_id = tree.findtext('.//sectionid')
            title = tree.findtext('.//name') or tree.findtext('.//title') or tree.findtext('.//summary')
            sequence = tree.findtext('.//sequence')
            
            if title and title != '$@NULL@$':
                # Preserve HTML formatting instead of stripping it
                title = title.strip()
            else:
                title = None  # Will try to derive from activities later
            section_map[folder] = {'name': title, 'assignments': [], 'sequence': sequence, 'section_id': section_id}
            section_sequences[folder] = sequence
            sections.append(section_map[folder])
        
        # 3. Load assignments and other activities
        activity_dir = os.path.join(tmpdir, 'activities')
        for folder in os.listdir(activity_dir):
            xml_path = os.path.join(activity_dir, folder, 'assign.xml')
            if not os.path.exists(xml_path):
                # Try other activity types
                if folder.startswith('page_'):
                    xml_path = os.path.join(activity_dir, folder, 'page.xml')
                elif folder.startswith('forum_'):
                    xml_path = os.path.join(activity_dir, folder, 'forum.xml')
                elif folder.startswith('resource_'):
                    xml_path = os.path.join(activity_dir, folder, 'resource.xml')
                else:
                    continue
                
            if not os.path.exists(xml_path):
                continue
                
            tree = etree.parse(xml_path)
            title = tree.findtext('.//name')
            desc = tree.findtext('.//intro')
            if desc:
                desc = desc.strip()
            else:
                desc = ""
            
            # Extract activity ID from folder name (e.g., "assign_2835" -> "2835")
            activity_id = folder.split('_')[1]
            
            # Find which section contains this activity using the sequence field
            section_folder = None
            for f, s in section_map.items():
                if s['sequence'] and activity_id in s['sequence'].split(','):
                    section_folder = f
                    break
            
            if section_folder:
                if folder.startswith('assign_'):
                    # This is an assignment - store with sequence position for sorting
                    sequence_list = section_map[section_folder]['sequence'].split(',')
                    sequence_position = sequence_list.index(activity_id) if activity_id in sequence_list else 999
                    assignment = {
                        'title': title.strip(), 
                        'description': desc,
                        'sequence_position': sequence_position,
                        'activity_id': activity_id
                    }
                    section_map[section_folder]['assignments'].append(assignment)
                else:
                    # This is another activity type (page, forum, etc.)
                    if 'activities' not in section_map[section_folder]:
                        section_map[section_folder]['activities'] = []
                    activity = {'title': title.strip(), 'description': desc, 'type': folder.split('_')[0]}
                    section_map[section_folder]['activities'].append(activity)

        # 4. Sort assignments by sequence position and clean up
        for section in sections:
            if section['assignments']:
                # Sort assignments by their sequence position
                section['assignments'].sort(key=lambda x: x['sequence_position'])
                # Remove the temporary fields used for sorting
                for assignment in section['assignments']:
                    del assignment['sequence_position']
                    del assignment['activity_id']

        # 5. Assign names to sections with no name
        for section in sections:
            if not section['name']:
                # First try to use assignment titles
                if section['assignments']:
                    section['name'] = section['assignments'][0]['title']
                # Then try other activity types
                elif 'activities' in section and section['activities']:
                    # Look for meaningful activity names
                    meaningful_names = ['syllabus', 'course information', 'introduction', 'overview', 'important links']
                    for activity in section['activities']:
                        activity_title_lower = activity['title'].lower()
                        if any(name in activity_title_lower for name in meaningful_names):
                            section['name'] = activity['title']
                            break
                    # If no meaningful name found, use the first activity
                    if not section['name']:
                        section['name'] = section['activities'][0]['title']
                else:
                    section['name'] = 'Untitled Section'

        # 6. Prepare output
        output = {
            'course_name': course_name,
            'topics': [
                {
                    'name': s['name'], 
                    'assignments': s['assignments'],
                    'activities': s.get('activities', [])  # Include other activities
                } for s in sections if s['assignments'] or s.get('activities') or s['name']
            ]
        }

        return output

def write_json(data, output_file='temp_data/current_course.json'):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def write_json_to_imports(data, course_name):
    """Write JSON data to class_data/imports directory with timestamp and course name"""
    # Create imports directory if it doesn't exist
    imports_dir = Path('class_data/imports')
    imports_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename with timestamp and sanitized course name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Sanitize course name for filename (remove special characters)
    safe_course_name = "".join(c for c in course_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_course_name = safe_course_name.replace(' ', '_')
    
    filename = f"{timestamp}_{safe_course_name}.json"
    output_path = imports_dir / filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_path

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python mbz_to_json.py course.mbz")
        sys.exit(1)

    mbz_file = sys.argv[1]
    course_data = parse_mbz(mbz_file)
    
    # Save to imports directory
    output_path = write_json_to_imports(course_data, course_data['course_name'])
    print(f"✅ Course data saved to: {output_path}")
    
    # Also save as current_course.json for backward compatibility
    write_json(course_data)
    print("✅ temp_data/current_course.json created (for backward compatibility).")
