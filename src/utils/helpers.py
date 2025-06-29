"""
Utility functions for the CLI tool.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Union, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def load_file(file_path: str) -> Dict[str, Any]:
    """
    Load data from a file (JSON, YAML, or text).
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing the file data
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if path.suffix.lower() == '.json':
        with open(path, 'r') as f:
            return json.load(f)
    elif path.suffix.lower() in ['.yml', '.yaml']:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Treat as text file
        with open(path, 'r') as f:
            return {"content": f.read()}


def save_file(data: Any, file_path: str, format: str = "json") -> None:
    """
    Save data to a file.
    
    Args:
        data: Data to save
        file_path: Path to save the file
        format: Output format (json, yaml, text)
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if format.lower() == "json":
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    elif format.lower() in ["yml", "yaml"]:
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    else:
        # Save as text
        with open(path, 'w') as f:
            f.write(str(data))


def display_table(data: list, title: str = "Data") -> None:
    """
    Display data in a formatted table.
    
    Args:
        data: List of dictionaries to display
        title: Table title
    """
    if not data:
        console.print("[yellow]No data to display[/yellow]")
        return
    
    table = Table(title=title)
    
    # Add columns based on the first item
    for key in data[0].keys():
        table.add_column(key, style="cyan")
    
    # Add rows
    for item in data:
        table.add_row(*[str(value) for value in item.values()])
    
    console.print(table)


def display_panel(content: str, title: str = "Information") -> None:
    """
    Display content in a panel.
    
    Args:
        content: Content to display
        title: Panel title
    """
    panel = Panel(content, title=title, border_style="blue")
    console.print(panel)


def confirm_action(message: str) -> bool:
    """
    Ask user for confirmation.
    
    Args:
        message: Confirmation message
        
    Returns:
        True if user confirms, False otherwise
    """
    response = input(f"{message} (y/N): ").strip().lower()
    return response in ['y', 'yes']


def get_environment_info() -> Dict[str, str]:
    """
    Get basic environment information.
    
    Returns:
        Dictionary with environment info
    """
    return {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
        "current_directory": str(Path.cwd()),
        "user": os.getenv("USER", "unknown"),
    } 