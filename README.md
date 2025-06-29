# Google Classroom Creator

A comprehensive tool for converting Moodle course backups (.mbz files) to Google Classroom courses with support for human-readable markdown exports.

## 🚀 Features

### Core Functionality
- **Moodle to Google Classroom Conversion**: Convert Moodle backup files (.mbz) to Google Classroom courses
- **HTML Formatting Preservation**: Maintain rich formatting in assignment descriptions
- **Automatic Section Mapping**: Intelligently map assignments to their correct sections
- **Unique Course Names**: Automatically append numbers to prevent naming conflicts
- **Authentication Caching**: Stay logged in across multiple commands

### Markdown Import/Export
- **Human-Readable Exports**: Export courses to organized markdown structure
- **Bidirectional Conversion**: Import markdown back to JSON format
- **Structured Organization**: Section-based folder hierarchy with metadata
- **Navigation Support**: Built-in navigation links between sections and assignments

### Course Management
- **Course Listing**: View all created courses with status and links
- **Archive/Delete/Restore**: Manage course lifecycle
- **Import Verification**: Verify that all assignments were properly imported
- **Status Tracking**: Track course creation dates and assignment counts

## 📁 Project Structure

```
google-classroom-creator/
├── src/core/                           # Core functionality
│   ├── mbz_to_json.py                  # Convert MBZ to JSON
│   ├── moodle_json_to_google_classroom.py  # Import to Google Classroom
│   ├── moodle_to_markdown.py           # Markdown import/export
│   ├── manage_courses.py               # Course management
│   ├── manage_auth.py                  # Authentication management
│   ├── verify_import.py                # Import verification
│   └── auth_cache.py                   # Credential caching
├── class_data/                         # Course data storage
│   ├── imports/                        # JSON course files
│   ├── exports/                        # Markdown exports
│   └── courses.json                    # Course tracking
├── temp_data/                          # Temporary files
├── cli.py                              # Command-line interface
└── requirements.txt                    # Dependencies
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd google-classroom-creator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google API credentials**:
   - Download `credentials.json` from Google Cloud Console
   - Place it in the project root
   - Add it to `.gitignore` (already included)

## 🔧 Usage

### Command-Line Interface (Recommended)

The CLI provides easy access to all features:

```bash
# Show help
python cli.py

# Convert Moodle backup to JSON
python cli.py convert temp_data/backup.mbz

# Import JSON to Google Classroom
python cli.py import class_data/imports/course.json

# Export JSON to markdown
python cli.py export class_data/imports/course.json

# Import markdown back to JSON
python cli.py import-md class_data/exports/course-folder/

# List all courses
python cli.py list-courses

# Archive a course
python cli.py archive 123456789

# Verify import
python cli.py verify 123456789
```

### Complete Workflow

1. **Convert Moodle Backup**:
   ```bash
   python cli.py convert temp_data/backup-moodle2-course-57-nov24-lv4-20250626-0543-nu-nf.mbz
   ```

2. **Import to Google Classroom**:
   ```bash
   python cli.py import class_data/imports/20250629_181517_November_Cohort_2024__-_Pathway_4.json
   ```

3. **Export to Markdown** (Optional):
   ```bash
   python cli.py export class_data/imports/20250629_181517_November_Cohort_2024__-_Pathway_4.json
   ```

4. **Import Markdown** (Optional):
   ```bash
   python cli.py import-md class_data/exports/20250629_223335_november-cohort-2024-pathway-4/
   ```

## 📖 Markdown Export Structure

The markdown export creates a human-readable structure:

```
course-export/
├── README.md                    # Main navigation
├── course-info.md               # Course overview and metadata
├── section-01-important-links/  # First section
│   ├── section.md               # Moodle metadata
│   ├── README.md                # Human-readable summary
│   └── assignment-01-links/     # First assignment
│       └── assignment.md        # Assignment content
├── section-02-erd-problems/     # Second section
│   ├── section.md
│   ├── README.md
│   └── assignment-01-erd/       # Assignment folder
│       └── assignment.md
└── ...
```

### Markdown Features
- **Section-based organization** with numbered folders
- **Assignment folders** with descriptive names
- **Navigation links** between sections and assignments
- **Metadata preservation** in separate files
- **HTML to Markdown conversion** for readable content

## 🔐 Authentication

The tool uses Google Classroom API with OAuth2 authentication:

1. **First-time setup**: Run any command and follow the browser authentication
2. **Cached credentials**: Tokens are stored in `temp_data/token.pickle`
3. **Automatic refresh**: Credentials are automatically refreshed when needed

### Managing Authentication
```bash
# Clear cached credentials
python cli.py auth
```

## 📊 Course Management

### List Courses
```bash
python cli.py list-courses
```

### Archive/Delete/Restore
```bash
python cli.py archive 123456789
python cli.py delete 123456789
python cli.py restore 123456789
```

### Verify Import
```bash
python cli.py verify 123456789
```

## 🎯 Key Features Explained

### HTML Formatting Preservation
- Converts HTML to plain text with Markdown-style formatting
- Preserves headings, lists, bold/italic text, links, and code blocks
- Ensures Google Classroom compatibility

### Intelligent Section Mapping
- Uses Moodle's sequence data to map assignments to correct sections
- Derives meaningful section names from first activity when needed
- Handles sections with no activities gracefully

### Unique Course Names
- Automatically detects existing courses with same name
- Appends numbers (e.g., "Course Name (1)", "Course Name (2)")
- Prevents conflicts in Google Classroom

### Markdown Export Benefits
- **Human-readable**: Easy to browse and edit course content
- **Version control friendly**: Markdown files work well with Git
- **Portable**: Can be shared, edited, and re-imported
- **Structured**: Organized folder hierarchy with navigation

## 🔧 Advanced Usage

### Direct Script Usage
You can also use the individual scripts directly:

```bash
# Convert MBZ to JSON
python src/core/mbz_to_json.py temp_data/backup.mbz

# Import to Google Classroom
python src/core/moodle_json_to_google_classroom.py course.json

# Export to markdown
python src/core/moodle_to_markdown.py export course.json

# Import markdown
python src/core/moodle_to_markdown.py import markdown-folder/
```

### Custom Output Directories
```bash
# Export to custom directory
python cli.py export course.json /path/to/custom/export/

# Import from custom directory
python cli.py import-md /path/to/markdown/folder/
```

## 📝 File Formats

### Input Formats
- **MBZ files**: Moodle backup files (zip or tar archives)
- **JSON files**: Course data exported from MBZ conversion
- **Markdown folders**: Human-readable course exports

### Output Formats
- **JSON files**: Structured course data (stored in `class_data/imports/`)
- **Markdown folders**: Human-readable exports (stored in `class_data/exports/`)
- **Google Classroom courses**: Live courses with topics and assignments

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Clear cached credentials: `python cli.py auth`
   - Re-authenticate through browser

2. **Course Name Conflicts**:
   - The tool automatically handles this by appending numbers
   - Check existing courses: `python cli.py list-courses`

3. **Import Failures**:
   - Verify the course: `python cli.py verify <course_id>`
   - Check assignment descriptions for invalid characters

4. **MBZ File Issues**:
   - Ensure the file is a valid Moodle backup
   - Check file permissions and path

### Debug Mode
For detailed debugging, you can run individual scripts with verbose output or examine the generated files in the `class_data/` directory.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Classroom API for course management
- Moodle community for backup format documentation
- BeautifulSoup for HTML parsing and conversion 