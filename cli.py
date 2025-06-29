#!/usr/bin/env python3
"""
Main CLI entry point for the application.
"""

import click
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.config import Config
from src.core.logger import setup_logger

console = Console()
logger = setup_logger()


@click.group()
@click.version_option(version="1.0.0")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to config file")
@click.pass_context
def cli(ctx, verbose, config):
    """
    A skeleton Python CLI tool.
    
    This tool provides a foundation for building command-line applications.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Store options in context
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config
    
    # Load configuration
    try:
        ctx.obj["config_obj"] = Config.from_file(config) if config else Config()
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        sys.exit(1)
    
    # Set up logging level
    if verbose:
        logger.setLevel("DEBUG")
    
    # Display welcome message
    if not ctx.invoked_subcommand:
        welcome_text = Text("Welcome to the CLI Tool!", style="bold blue")
        console.print(Panel(welcome_text, title="CLI Tool", border_style="green"))


@cli.command()
@click.option("--name", "-n", default="World", help="Name to greet")
@click.pass_context
def hello(ctx, name):
    """Say hello to someone."""
    console.print(f"[green]Hello, {name}![/green]")
    logger.info(f"Greeted user: {name}")


@cli.command()
@click.option("--input", "-i", type=click.Path(exists=True), help="Input file path")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.pass_context
def process(ctx, input, output):
    """Process files or data."""
    if input:
        console.print(f"[blue]Processing input file: {input}[/blue]")
        logger.info(f"Processing file: {input}")
        
        if output:
            console.print(f"[blue]Output will be written to: {output}[/blue]")
            logger.info(f"Output file: {output}")
    else:
        console.print("[yellow]No input file specified. Use --input to specify a file.[/yellow]")


@cli.command()
@click.pass_context
def status(ctx):
    """Show the current status of the application."""
    config = ctx.obj["config_obj"]
    verbose = ctx.obj["verbose"]
    
    console.print("[bold]Application Status:[/bold]")
    console.print(f"  Config loaded: {'Yes' if config else 'No'}")
    console.print(f"  Verbose mode: {'Yes' if verbose else 'No'}")
    console.print(f"  Log level: {logger.level}")


if __name__ == "__main__":
    cli() 