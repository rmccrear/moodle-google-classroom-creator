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
   
   ### Step 1: Access Google Cloud Console
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Sign in with your Google Workspace (formerly G Suite) account
   - Make sure you have admin privileges or can create projects
   
   ### Step 2: Create or Select a Project
   - Click on the project dropdown at the top of the page
   - Click "New Project" or select an existing project
   - Give your project a name (e.g., "Google Classroom Creator")
   - Click "Create"
   
   ### Step 3: Enable Google Classroom API
   - In the left sidebar, go to "APIs & Services" > "Library"
   - Search for "Google Classroom API"
   - Click on "Google Classroom API"
   - Click "Enable"
   
   ### Step 4: Create Credentials
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - If prompted, configure the OAuth consent screen:
     - Choose "External" or "Internal" (Internal if you have Google Workspace)
     - Fill in the required fields (App name, User support email, Developer contact)
     - Add scopes: `https://www.googleapis.com/auth/classroom.courses`
     - Add test users if needed
   - For Application type, choose "Desktop application"
   - Give it a name (e.g., "Google Classroom Creator CLI")
   - Click "Create"
   
   ### Step 5: Download Credentials
   - After creating the OAuth client, click "Download JSON"
   - Rename the downloaded file to `credentials.json`
   - Place it in the project root directory
   
   ### Step 6: Organization-Specific Setup
   
   **For Google Workspace Organizations:**
   - Contact your Google Workspace admin
   - Request access to Google Classroom API for your account
   - The admin may need to enable the API in the Google Workspace Admin Console:
     1. Go to [Admin Console](https://admin.google.com/)
     2. Navigate to "Apps" > "Google Workspace" > "Google Classroom"
     3. Ensure "Google Classroom API" is enabled
     4. Check that your user account has the necessary permissions
   
   **For Personal Google Accounts:**
   - The API should work with personal accounts
   - You may need to verify your app in the OAuth consent screen
   - Consider using "Internal" user type if you have a Google Workspace account
   
   ### Step 7: Verify Setup
   - Run any command (e.g., `python cli.py list-courses`)
   - Follow the browser authentication flow
   - Grant permissions to your application
   - Credentials will be cached for future use
   
   **Troubleshooting:**
   - **"Access Denied"**: Contact your Google Workspace admin
   - **"API not enabled"**: Ensure Google Classroom API is enabled in your project
   - **"Invalid credentials"**: Check that `credentials.json` is in the project root
   - **"Quota exceeded"**: Check your Google Cloud Console quotas

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