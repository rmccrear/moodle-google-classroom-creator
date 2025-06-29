import zipfile
import tarfile
import os
import tempfile
from lxml import etree

def debug_moodle_backup(mbz_path):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract the backup
        is_zip = zipfile.is_zipfile(mbz_path)
        is_tar = tarfile.is_tarfile(mbz_path)
        if is_zip:
            with zipfile.ZipFile(mbz_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)
        elif is_tar:
            with tarfile.open(mbz_path, 'r') as tar_ref:
                tar_ref.extractall(tmpdir)
        
        print("📁 Extracted backup structure:")
        for root, dirs, files in os.walk(tmpdir):
            level = root.replace(tmpdir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
        
        # Examine sections
        section_dir = os.path.join(tmpdir, 'sections')
        if os.path.exists(section_dir):
            print(f"\n📚 Sections found:")
            for folder in sorted(os.listdir(section_dir)):
                xml_path = os.path.join(section_dir, folder, 'section.xml')
                if os.path.exists(xml_path):
                    tree = etree.parse(xml_path)
                    section_id = tree.findtext('.//sectionid')
                    title = tree.findtext('.//title')
                    summary = tree.findtext('.//summary')
                    print(f"  📁 Folder: {folder}")
                    print(f"    🆔 Section ID: {section_id}")
                    print(f"    📖 Title: {title}")
                    print(f"    📝 Summary: {summary}")
                    print(f"    📄 XML path: {xml_path}")
                    print()
        
        # Examine one section XML file in detail
        section_587_xml = os.path.join(tmpdir, 'sections', 'section_587', 'section.xml')
        if os.path.exists(section_587_xml):
            print("🔍 Detailed examination of section_587/section.xml:")
            tree = etree.parse(section_587_xml)
            root = tree.getroot()
            
            print("📄 Full XML content:")
            print(etree.tostring(root, pretty_print=True, encoding='unicode'))
            
            print("\n🔍 All possible elements:")
            for elem in root.iter():
                print(f"  - {elem.tag}: {elem.text if elem.text else '(empty)'}")
        
        # Also check the main course XML
        course_xml = os.path.join(tmpdir, 'course', 'course.xml')
        if os.path.exists(course_xml):
            print(f"\n📚 Course XML structure:")
            tree = etree.parse(course_xml)
            root = tree.getroot()
            for elem in root.iter():
                print(f"  - {elem.tag}: {elem.text if elem.text else '(empty)'}")

        # Examine activities to see if we can derive section names
        print("🔍 Examining activities to derive section names:")
        
        # Get section sequences
        section_sequences = {}
        
        for folder in sorted(os.listdir(section_dir)):
            xml_path = os.path.join(section_dir, folder, 'section.xml')
            if os.path.exists(xml_path):
                tree = etree.parse(xml_path)
                sequence = tree.findtext('.//sequence')
                if sequence:
                    section_sequences[folder] = sequence.split(',')
        
        # Examine activities in each section
        activity_dir = os.path.join(tmpdir, 'activities')
        for section_folder, activity_ids in section_sequences.items():
            print(f"\n📚 Section {section_folder}:")
            print(f"  Activity IDs: {activity_ids}")
            
            section_activities = []
            for activity_id in activity_ids:
                # Look for assignment activities
                assign_folder = f"assign_{activity_id}"
                assign_xml = os.path.join(activity_dir, assign_folder, 'assign.xml')
                
                if os.path.exists(assign_xml):
                    tree = etree.parse(assign_xml)
                    title = tree.findtext('.//name')
                    section_id = tree.findtext('.//sectionid')
                    print(f"    📝 Assignment {activity_id}: {title}")
                    section_activities.append(title)
                
                # Look for page activities
                page_folder = f"page_{activity_id}"
                page_xml = os.path.join(activity_dir, page_folder, 'page.xml')
                
                if os.path.exists(page_xml):
                    tree = etree.parse(page_xml)
                    title = tree.findtext('.//name')
                    print(f"    📄 Page {activity_id}: {title}")
                    section_activities.append(title)
            
            # Try to derive a meaningful section name
            if section_activities:
                # Use the first assignment title as section name
                first_activity = section_activities[0]
                if len(first_activity) > 50:
                    first_activity = first_activity[:47] + "..."
                print(f"  💡 Suggested section name: {first_activity}")
            else:
                print(f"  ⚠️  No activities found for section {section_folder}")

        print("🔍 Debugging section and assignment mapping:")
        
        # Get section sequences
        section_dir = os.path.join(tmpdir, 'sections')
        print("\n📁 Sections:")
        section_map = {}
        for folder in sorted(os.listdir(section_dir)):
            xml_path = os.path.join(section_dir, folder, 'section.xml')
            tree = etree.parse(xml_path)
            section_id = tree.findtext('.//sectionid')
            sequence = tree.findtext('.//sequence')
            print(f"  Folder: {folder}")
            print(f"    Section ID: {section_id}")
            print(f"    Sequence: {sequence}")
            section_map[folder] = {'section_id': section_id, 'sequence': sequence}
        
        print("\n📝 Assignments:")
        activity_dir = os.path.join(tmpdir, 'activities')
        for folder in os.listdir(activity_dir):
            if folder.startswith('assign_'):
                xml_path = os.path.join(activity_dir, folder, 'assign.xml')
                if not os.path.exists(xml_path):
                    continue
                tree = etree.parse(xml_path)
                title = tree.findtext('.//name')
                assignment_section_id = tree.findtext('.//sectionid')
                print(f"  Assignment: {title}")
                print(f"    Section ID: {assignment_section_id}")
                
                # Check if this assignment matches any section
                matched_section = None
                for section_folder, section_info in section_map.items():
                    if section_info['section_id'] == assignment_section_id:
                        matched_section = section_folder
                        break
                
                if matched_section:
                    print(f"    ✅ Matches section: {matched_section}")
                else:
                    print(f"    ❌ No matching section found!")

if __name__ == '__main__':
    debug_moodle_backup('temp_data/backup-moodle2-course-57-nov24-lv4-20250626-0543-nu-nf.mbz') 