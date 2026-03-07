"""PHI Guard CLI - Command-line interface using Typer."""

import json
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from phi_guard.engine import Finding, scan_directory, scan_file


class OutputFormat(str, Enum):
    TABLE = "table"
    JSON = "json"


app = typer.Typer(
    name="phi-guard",
    help="HIPAA PHI scanner for CI/CD pipelines",
    add_completion=False,
)

console = Console()


def display_findings(findings: list[Finding]) -> None:
    """Display findings as a formatted table."""
    if not findings:
        console.print("[green]No PHI found.[/green]")
        return

    table = Table(
        title=f"[bold red]PHI Found: {len(findings)} item(s)[/bold red]",
        show_header=True,
        header_style="bold magenta",
    )

    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Line", style="yellow", justify="right")
    table.add_column("Type", style="green")
    table.add_column("Value", style="red")
    table.add_column("Score", justify="right")

    for finding in findings:
        file_display = finding.file_path or "(text)"
        if len(file_display) > 40:
            file_display = "..." + file_display[-37:]

        table.add_row(
            file_display,
            str(finding.line_number) if finding.line_number else "-",
            finding.entity_type,
            finding.text,
            f"{finding.score:.2f}",
        )

    console.print(table)


def output_json(findings: list[Finding]) -> None:
    """Output findings as JSON for CI/CD parsing."""
    data = {
        "findings": [asdict(f) for f in findings],
        "count": len(findings),
    }
    print(json.dumps(data, indent=2))


@app.command()
def scan(
    paths: list[Path] = typer.Argument(
        ...,
        help="Files or directories to scan",
        exists=True,
    ),
    threshold: float = typer.Option(
        0.5,
        "--threshold", "-t",
        help="Minimum confidence score (0.0-1.0)",
        min=0.0,
        max=1.0,
    ),
    recursive: bool = typer.Option(
        True,
        "--recursive/--no-recursive", "-r/-R",
        help="Scan subdirectories recursively",
    ),
    exclude: Optional[list[str]] = typer.Option(
        None,
        "--exclude", "-e",
        help="Patterns to exclude (gitignore style). Can be used multiple times.",
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.TABLE,
        "--format", "-f",
        help="Output format: table (default) or json",
    ),
) -> None:
    """
    Scan files for Protected Health Information (PHI).

    Detects SSN, MRN, phone numbers, and other HIPAA-defined identifiers.
    """
    # Skip header output for JSON format
    if output_format != OutputFormat.JSON:
        paths_display = ", ".join(str(p) for p in paths[:3])
        if len(paths) > 3:
            paths_display += f" (+{len(paths) - 3} more)"
        console.print(f"[bold]Scanning:[/bold] {paths_display}")
        console.print(f"[dim]Threshold: {threshold}, Recursive: {recursive}[/dim]")
        if exclude:
            console.print(f"[dim]Excluding: {', '.join(exclude)}[/dim]")
        console.print()

    try:
        all_findings: list[Finding] = []
        for path in paths:
            if path.is_file():
                findings = scan_file(path, score_threshold=threshold)
            else:
                findings = scan_directory(
                    path,
                    score_threshold=threshold,
                    recursive=recursive,
                    exclude_patterns=exclude,
                )
            all_findings.extend(findings)
    except Exception as e:
        if output_format == OutputFormat.JSON:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)

    if output_format == OutputFormat.JSON:
        output_json(all_findings)
    else:
        display_findings(all_findings)

    # Exit with code 1 if PHI found (for CI/CD failure detection)
    if all_findings:
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Show PHI Guard version."""
    console.print("[bold]PHI Guard[/bold] v0.1.0")


def main() -> None:
    """CLI entry point. Called from pyproject.toml scripts."""
    app()


if __name__ == "__main__":
    main()
