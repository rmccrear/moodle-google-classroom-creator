# Python CLI Tool Skeleton

A well-structured skeleton for building Python command-line interface (CLI) tools with modern best practices.

## Features

- 🚀 **Click-based CLI**: Modern command-line interface using Click
- 🎨 **Rich Output**: Beautiful terminal output with colors and formatting
- ⚙️ **Configuration Management**: Type-safe configuration with Pydantic
- 📝 **Structured Logging**: Rich logging with file and console output
- 🛠️ **Modular Design**: Clean, extensible architecture
- 📦 **Easy Setup**: Simple installation and development workflow

## Installation

1. **Clone or download this skeleton**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Make the CLI executable**:
   ```bash
   chmod +x cli.py
   ```

## Usage

### Basic Commands

```bash
# Show help
python cli.py --help

# Say hello
python cli.py hello
python cli.py hello --name "Your Name"

# Show status
python cli.py status

# Process files
python cli.py process --input input.txt --output output.txt

# Enable verbose mode
python cli.py --verbose hello
```

### Configuration

The tool supports configuration through:
- Environment variables
- Configuration files
- Command-line options

Example environment variables:
```bash
export APP_NAME="My CLI Tool"
export LOG_LEVEL="DEBUG"
export COLOR_OUTPUT="true"
```

## Project Structure

```
├── cli.py                 # Main CLI entry point
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── src/                  # Source code
│   ├── __init__.py
│   ├── core/            # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py    # Configuration management
│   │   └── logger.py    # Logging setup
│   └── utils/           # Utility functions
│       ├── __init__.py
│       └── helpers.py   # Common helper functions
└── tests/               # Test files (to be added)
```

## Development

### Adding New Commands

1. **Create a new command module** in `src/commands/`
2. **Import and register** the command in `cli.py`
3. **Add tests** in the `tests/` directory

Example command:
```python
@cli.command()
@click.option("--option", "-o", help="An option")
@click.pass_context
def my_command(ctx, option):
    """Description of my command."""
    # Command implementation
    pass
```

### Adding New Utilities

1. **Add utility functions** to `src/utils/helpers.py`
2. **Import and use** in your commands
3. **Document** the functions with docstrings

### Testing

```bash
# Run tests (when implemented)
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/
```

## Configuration

The tool uses Pydantic for type-safe configuration. Key configuration options:

- `app_name`: Application name
- `version`: Application version
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `log_file`: Optional log file path
- `output_format`: Output format (text, json, yaml)
- `color_output`: Enable/disable colored output

## Logging

The tool provides structured logging with:
- Console output with rich formatting
- Optional file logging
- Configurable log levels
- Beautiful tracebacks

## Dependencies

- **Click**: Command-line interface creation kit
- **Rich**: Rich text and beautiful formatting in the terminal
- **Pydantic**: Data validation using Python type annotations
- **python-dotenv**: Environment variable management
- **PyYAML**: YAML file support (optional)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Examples

### Custom Command Example

```python
@cli.command()
@click.option("--file", "-f", type=click.Path(exists=True), required=True)
@click.option("--format", type=click.Choice(["json", "yaml", "text"]), default="json")
@click.pass_context
def analyze(ctx, file, format):
    """Analyze a file and display results."""
    from src.utils.helpers import load_file, display_table
    
    try:
        data = load_file(file)
        display_table([data], title="File Analysis")
    except Exception as e:
        console.print(f"[red]Error analyzing file: {e}[/red]")
```

### Configuration Example

```python
# config.yaml
app_name: "My Custom CLI"
log_level: "DEBUG"
output_format: "json"
color_output: true
settings:
  api_key: "your-api-key"
  base_url: "https://api.example.com"
```

This skeleton provides a solid foundation for building professional CLI tools with modern Python practices. 