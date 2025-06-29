import zipfile
import tarfile
import os
import tempfile
import json
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
        for folder in sorted(os.listdir(section_dir)):
            xml_path = os.path.join(section_dir, folder, 'section.xml')
            tree = etree.parse(xml_path)
            section_id = tree.findtext('.//sectionid')
            title = tree.findtext('.//title') or tree.findtext('.//summary')
            if title:
                html_elem = etree.HTML(title)
                title = ''.join(html_elem.itertext()).strip() if html_elem is not None else ''
            else:
                title = f"Section {folder[-3:]}"
            section_map[section_id] = {'name': title, 'assignments': []}
            sections.append(section_map[section_id])

        # 3. Load assignments
        activity_dir = os.path.join(tmpdir, 'activities')
        for folder in os.listdir(activity_dir):
            if folder.startswith('assign_'):
                xml_path = os.path.join(activity_dir, folder, 'assign.xml')
                if not os.path.exists(xml_path):
                    continue
                tree = etree.parse(xml_path)
                title = tree.findtext('.//name')
                desc = tree.findtext('.//intro')
                if desc:
                    html_elem = etree.HTML(desc)
                    desc = ''.join(html_elem.itertext()).strip() if html_elem is not None else ''
                else:
                    desc = ""
                section_id = tree.findtext('.//sectionid')
                assignment = {'title': title.strip(), 'description': desc}
                if section_id and section_id in section_map:
                    section_map[section_id]['assignments'].append(assignment)
                else:
                    sections[0]['assignments'].append(assignment)  # fallback

        # 4. Final output
        return {
            'course_name': course_name,
            'topics': sections
        }

def write_json(data, output_file='course.json'):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python mbz_to_json.py course.mbz")
        sys.exit(1)

    mbz_file = sys.argv[1]
    course_data = parse_mbz(mbz_file)
    write_json(course_data)
    print("✅ course.json created.")
