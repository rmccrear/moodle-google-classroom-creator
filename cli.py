#!/usr/bin/env python3
"""
Google Classroom Creator CLI
A command-line interface for converting Moodle courses to Google Classroom.
"""

import sys
import os
from pathlib import Path

def print_usage():
    """Print the usage information"""
    print("""
🎓 Google Classroom Creator CLI

USAGE:
  python cli.py <command> [options]

COMMANDS:
  convert <mbz_file>                    Convert Moodle backup to JSON
  import <json_file>                    Import JSON to Google Classroom
  export <json_file> [output_dir]       Export JSON to markdown format
  import-md <markdown_dir>              Import markdown back to JSON
  list-courses                          List all created courses
  archive <course_id>                   Archive a course
  delete <course_id>                    Delete a course
  restore <course_id>                   Restore an archived course
  verify <course_id>                    Verify course import status
  auth                                  Manage authentication

EXAMPLES:
  # Convert Moodle backup to JSON
  python cli.py convert temp_data/backup.mbz

  # Import to Google Classroom
  python cli.py import class_data/imports/course.json

  # Export to markdown
  python cli.py export class_data/imports/course.json

  # Import markdown back to JSON
  python cli.py import-md class_data/exports/course-folder/

  # List all courses
  python cli.py list-courses

  # Archive a course
  python cli.py archive 123456789

  # Verify import
  python cli.py verify 123456789

WORKFLOW:
  1. Convert Moodle backup: convert <mbz_file>
  2. Import to Classroom: import <json_file>
  3. (Optional) Export to markdown: export <json_file>
  4. (Optional) Import markdown: import-md <markdown_dir>
""")

def run_command(command, args):
    """Run the specified command"""
    
    if command == 'convert':
        if len(args) < 1:
            print("❌ Error: Please provide an MBZ file path")
            return 1
        
        mbz_file = args[0]
        if not os.path.exists(mbz_file):
            print(f"❌ Error: MBZ file not found: {mbz_file}")
            return 1
        
        print(f"🔄 Converting {mbz_file} to JSON...")
        os.system(f"python src/core/mbz_to_json.py {mbz_file}")
        return 0
    
    elif command == 'import':
        if len(args) < 1:
            print("❌ Error: Please provide a JSON file path")
            return 1
        
        json_file = args[0]
        if not os.path.exists(json_file):
            print(f"❌ Error: JSON file not found: {json_file}")
            return 1
        
        print(f"🔄 Importing {json_file} to Google Classroom...")
        os.system(f"python src/core/moodle_json_to_google_classroom.py {json_file}")
        return 0
    
    elif command == 'export':
        if len(args) < 1:
            print("❌ Error: Please provide a JSON file path")
            return 1
        
        json_file = args[0]
        output_dir = args[1] if len(args) > 1 else None
        
        if not os.path.exists(json_file):
            print(f"❌ Error: JSON file not found: {json_file}")
            return 1
        
        cmd = f"python src/core/moodle_to_markdown.py export {json_file}"
        if output_dir:
            cmd += f" {output_dir}"
        
        print(f"🔄 Exporting {json_file} to markdown...")
        os.system(cmd)
        return 0
    
    elif command == 'import-md':
        if len(args) < 1:
            print("❌ Error: Please provide a markdown directory path")
            return 1
        
        markdown_dir = args[0]
        if not os.path.exists(markdown_dir):
            print(f"❌ Error: Markdown directory not found: {markdown_dir}")
            return 1
        
        print(f"🔄 Importing markdown from {markdown_dir}...")
        os.system(f"python src/core/moodle_to_markdown.py import {markdown_dir}")
        return 0
    
    elif command == 'list-courses':
        print("📋 Listing all courses...")
        os.system("python src/core/manage_courses.py list")
        return 0
    
    elif command == 'archive':
        if len(args) < 1:
            print("❌ Error: Please provide a course ID")
            return 1
        
        course_id = args[0]
        print(f"📦 Archiving course {course_id}...")
        os.system(f"python src/core/manage_courses.py archive {course_id}")
        return 0
    
    elif command == 'delete':
        if len(args) < 1:
            print("❌ Error: Please provide a course ID")
            return 1
        
        course_id = args[0]
        print(f"🗑️  Deleting course {course_id}...")
        os.system(f"python src/core/manage_courses.py delete {course_id}")
        return 0
    
    elif command == 'restore':
        if len(args) < 1:
            print("❌ Error: Please provide a course ID")
            return 1
        
        course_id = args[0]
        print(f"🔄 Restoring course {course_id}...")
        os.system(f"python src/core/manage_courses.py restore {course_id}")
        return 0
    
    elif command == 'verify':
        if len(args) < 1:
            print("❌ Error: Please provide a course ID")
            return 1
        
        course_id = args[0]
        print(f"✅ Verifying course {course_id}...")
        os.system(f"python src/core/verify_import.py {course_id}")
        return 0
    
    elif command == 'auth':
        print("🔑 Managing authentication...")
        os.system("python src/core/manage_auth.py")
        return 0
    
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()
        return 1

def main():
    """Main CLI function"""
    if len(sys.argv) < 2:
        print_usage()
        return 0
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    # Handle help
    if command in ['help', '--help', '-h']:
        print_usage()
        return 0
    
    # Run the command
    return run_command(command, args)

if __name__ == '__main__':
    sys.exit(main()) 