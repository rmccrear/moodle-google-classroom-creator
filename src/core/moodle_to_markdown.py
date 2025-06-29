import json
import os
from pathlib import Path
from datetime import datetime
import re
from bs4 import BeautifulSoup

def sanitize_filename(name):
    """Convert a string to a safe filename"""
    # Remove or replace invalid characters
    safe = re.sub(r'[<>:"/\\|?*]', '', name)
    # Replace spaces and other separators with hyphens
    safe = re.sub(r'[\s\-_]+', '-', safe)
    # Remove leading/trailing hyphens and limit length
    safe = safe.strip('-')[:50]
    return safe.lower()

def html_to_markdown(html_content):
    """Convert HTML content to markdown format"""
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Convert headings
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        level = int(tag.name[1])
        tag.string = f"{'#' * level} {tag.get_text(strip=True)}\n\n"
        tag.name = 'p'
    
    # Convert bold and italic
    for tag in soup.find_all('strong'):
        tag.string = f"**{tag.get_text(strip=True)}**"
        tag.name = 'span'
    
    for tag in soup.find_all('em'):
        tag.string = f"*{tag.get_text(strip=True)}*"
        tag.name = 'span'
    
    # Convert lists
    for tag in soup.find_all('ul'):
        items = []
        for li in tag.find_all('li'):
            items.append(f"- {li.get_text(strip=True)}")
        tag.string = '\n'.join(items) + '\n\n'
        tag.name = 'p'
    
    for tag in soup.find_all('ol'):
        items = []
        for i, li in enumerate(tag.find_all('li'), 1):
            items.append(f"{i}. {li.get_text(strip=True)}")
        tag.string = '\n'.join(items) + '\n\n'
        tag.name = 'p'
    
    # Convert links
    for tag in soup.find_all('a'):
        href = tag.get('href', '')
        text = tag.get_text(strip=True)
        tag.string = f"[{text}]({href})"
        tag.name = 'span'
    
    # Convert code blocks
    for tag in soup.find_all('code'):
        tag.string = f"`{tag.get_text(strip=True)}`"
        tag.name = 'span'
    
    # Convert paragraphs
    for tag in soup.find_all('p'):
        if tag.get_text(strip=True):
            tag.string = f"{tag.get_text(strip=True)}\n\n"
    
    # Get the final text
    text = soup.get_text()
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    return text.strip()

def export_course_to_markdown(course_data, output_dir):
    """Export course data to markdown-based schema"""
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create course-info.md at root
    course_info_content = f"""# {course_data['course_name']}

## Course Overview
This course was exported from Moodle on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.

## Course Structure
This course contains {len(course_data['topics'])} sections with a total of {sum(len(topic['assignments']) for topic in course_data['topics'])} assignments.

## Sections
"""
    
    for i, topic in enumerate(course_data['topics'], 1):
        if topic['assignments']:
            course_info_content += f"{i}. [{topic['name']}](section-{i:02d}-{sanitize_filename(topic['name'])}/README.md) - {len(topic['assignments'])} assignments\n"
    
    course_info_content += "\n## Export Information\n- **Export Date:** " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    course_info_content += "\n- **Source:** Moodle Course Backup"
    course_info_content += "\n- **Format:** Markdown-based schema"
    
    with open(output_path / "course-info.md", 'w', encoding='utf-8') as f:
        f.write(course_info_content)
    
    # Process each section
    for i, topic in enumerate(course_data['topics'], 1):
        if not topic['assignments']:
            continue
            
        # Create section folder
        section_name = sanitize_filename(topic['name'])
        section_folder = output_path / f"section-{i:02d}-{section_name}"
        section_folder.mkdir(exist_ok=True)
        
        # Create section.md (Moodle metadata)
        section_metadata = f"""# Section: {topic['name']}

## Section Information
- **Section Number:** {i}
- **Section Name:** {topic['name']}
- **Number of Assignments:** {len(topic['assignments'])}
- **Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Moodle Metadata
This section was extracted from Moodle with the following structure:
- Original section name: {topic['name']}
- Assignment count: {len(topic['assignments'])}

## Assignments in this Section
"""
        
        for j, assignment in enumerate(topic['assignments'], 1):
            assignment_filename = f"assignment-{j:02d}-{sanitize_filename(assignment['title'])}"
            section_metadata += f"{j}. [{assignment['title']}]({assignment_filename}/assignment.md)\n"
        
        with open(section_folder / "section.md", 'w', encoding='utf-8') as f:
            f.write(section_metadata)
        
        # Create README.md (human-readable summary)
        readme_content = f"""# {topic['name']}

## Section Overview
This section contains {len(topic['assignments'])} assignments focused on {topic['name'].lower()}.

## Quick Links
"""
        
        for j, assignment in enumerate(topic['assignments'], 1):
            assignment_filename = f"assignment-{j:02d}-{sanitize_filename(assignment['title'])}"
            readme_content += f"- **[Assignment {j}]({assignment_filename}/assignment.md)**: {assignment['title']}\n"
        
        readme_content += f"""

## Section Summary
This section covers {topic['name'].lower()} with practical assignments and theoretical content.

## Navigation
- [← Previous Section](../section-{i-1:02d}-{sanitize_filename(course_data['topics'][i-2]['name']) if i > 1 else 'index'}/README.md)
- [↑ Course Overview](../course-info.md)
- [Next Section →](../section-{i+1:02d}-{sanitize_filename(course_data['topics'][i]['name']) if i < len(course_data['topics']) else 'index'}/README.md)
"""
        
        with open(section_folder / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Create assignment folders and files
        for j, assignment in enumerate(topic['assignments'], 1):
            assignment_folder = section_folder / f"assignment-{j:02d}-{sanitize_filename(assignment['title'])}"
            assignment_folder.mkdir(exist_ok=True)
            
            # Convert HTML description to markdown
            markdown_description = html_to_markdown(assignment['description'])
            
            # Create assignment.md
            assignment_content = f"""# {assignment['title']}

## Assignment Information
- **Assignment Number:** {j}
- **Section:** {topic['name']}
- **Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Assignment Description
{markdown_description}

## Assignment Details
- **Type:** Assignment
- **Section:** {topic['name']}
- **Order:** {j} of {len(topic['assignments'])} in this section

## Navigation
- [← Previous Assignment](../assignment-{j-1:02d}-{sanitize_filename(topic['assignments'][j-2]['title']) if j > 1 else 'index'}/assignment.md)
- [↑ Section Overview](../README.md)
- [Next Assignment →](../assignment-{j+1:02d}-{sanitize_filename(topic['assignments'][j]['title']) if j < len(topic['assignments']) else 'index'}/assignment.md)
"""
            
            with open(assignment_folder / "assignment.md", 'w', encoding='utf-8') as f:
                f.write(assignment_content)
    
    # Create main README.md at root
    main_readme = f"""# {course_data['course_name']}

## Welcome to the Course Export

This folder contains a human-readable export of the Moodle course "{course_data['course_name']}".

## Quick Start
1. Read [course-info.md](course-info.md) for an overview
2. Navigate through sections using the numbered folders
3. Each section contains assignments and resources

## Folder Structure
```
{output_path.name}/
├── course-info.md          # Course overview and metadata
├── section-01-*/           # First section
│   ├── section.md          # Moodle metadata
│   ├── README.md           # Human-readable summary
│   └── assignment-01-*/    # First assignment
│       └── assignment.md   # Assignment content
├── section-02-*/           # Second section
│   └── ...
└── ...
```

## Navigation Tips
- Each section folder starts with a number (e.g., `section-01-`)
- Assignments within sections are also numbered (e.g., `assignment-01-`)
- Use the README.md files in each section for quick navigation
- The course-info.md file provides the overall structure

## Export Information
- **Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Source:** Moodle Course Backup
- **Format:** Markdown-based schema
- **Total Sections:** {len([t for t in course_data['topics'] if t['assignments']])}
- **Total Assignments:** {sum(len(topic['assignments']) for topic in course_data['topics'])}

## Getting Started
Start by reading the [course overview](course-info.md) to understand the course structure.
"""
    
    with open(output_path / "README.md", 'w', encoding='utf-8') as f:
        f.write(main_readme)
    
    return output_path

def import_markdown_to_course(markdown_dir):
    """Import markdown-based schema back to course data structure"""
    markdown_path = Path(markdown_dir)
    
    if not markdown_path.exists():
        raise ValueError(f"Markdown directory does not exist: {markdown_dir}")
    
    # Read course info
    course_info_file = markdown_path / "course-info.md"
    if not course_info_file.exists():
        raise ValueError("course-info.md not found in markdown directory")
    
    with open(course_info_file, 'r', encoding='utf-8') as f:
        course_info_content = f.read()
    
    # Extract course name from first line
    course_name = course_info_content.split('\n')[0].replace('# ', '')
    
    # Find all section folders
    section_folders = sorted([d for d in markdown_path.iterdir() 
                            if d.is_dir() and d.name.startswith('section-')])
    
    topics = []
    
    for section_folder in section_folders:
        # Read section metadata
        section_md_file = section_folder / "section.md"
        if not section_md_file.exists():
            continue
        
        with open(section_md_file, 'r', encoding='utf-8') as f:
            section_content = f.read()
        
        # Extract section name
        section_name = section_content.split('\n')[0].replace('# Section: ', '')
        
        # Find all assignment folders
        assignment_folders = sorted([d for d in section_folder.iterdir() 
                                   if d.is_dir() and d.name.startswith('assignment-')])
        
        assignments = []
        
        for assignment_folder in assignment_folders:
            assignment_md_file = assignment_folder / "assignment.md"
            if not assignment_md_file.exists():
                continue
            
            with open(assignment_md_file, 'r', encoding='utf-8') as f:
                assignment_content = f.read()
            
            # Extract assignment title and description
            lines = assignment_content.split('\n')
            title = lines[0].replace('# ', '')
            
            # Find description section
            description_start = None
            for i, line in enumerate(lines):
                if line.strip() == "## Assignment Description":
                    description_start = i + 1
                    break
            
            if description_start:
                description_lines = []
                for line in lines[description_start:]:
                    if line.startswith('## '):
                        break
                    description_lines.append(line)
                description = '\n'.join(description_lines).strip()
            else:
                description = ""
            
            assignments.append({
                'title': title,
                'description': description
            })
        
        topics.append({
            'name': section_name,
            'assignments': assignments
        })
    
    return {
        'course_name': course_name,
        'topics': topics
    }

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Export: python moodle_to_markdown.py export <json_file> [output_dir]")
        print("  Import: python moodle_to_markdown.py import <markdown_dir> [output_json]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'export':
        json_file = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None
        
        # Load course data
        with open(json_file, 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        
        # Generate output directory name if not provided
        if not output_dir:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_course_name = sanitize_filename(course_data['course_name'])
            output_dir = f"class_data/exports/{timestamp}_{safe_course_name}"
        
        # Export to markdown
        output_path = export_course_to_markdown(course_data, output_dir)
        print(f"✅ Course exported to: {output_path}")
        
    elif command == 'import':
        markdown_dir = sys.argv[2]
        output_json = sys.argv[3] if len(sys.argv) > 3 else None
        
        # Import from markdown
        course_data = import_markdown_to_course(markdown_dir)
        
        # Save to JSON
        if not output_json:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_course_name = sanitize_filename(course_data['course_name'])
            output_json = f"class_data/imports/{timestamp}_{safe_course_name}.json"
        
        # Ensure directory exists
        Path(output_json).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(course_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Course imported from markdown to: {output_json}")
        
    else:
        print("Invalid command. Use 'export' or 'import'.")
        sys.exit(1) 