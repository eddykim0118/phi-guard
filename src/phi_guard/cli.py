"""
PHI Guard CLI

Typer를 사용한 커맨드라인 인터페이스입니다.

사용법:
    phi-guard scan ./                    # 현재 디렉토리 스캔
    phi-guard scan ./test.py             # 특정 파일 스캔
    phi-guard scan ./ --threshold 0.7    # 신뢰도 임계값 조정
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from phi_guard.engine import Finding, scan_directory, scan_file

# Typer 앱 생성
# add_completion=False: 자동완성 명령어 숨김 (깔끔하게)
app = typer.Typer(
    name="phi-guard",
    help="HIPAA PHI scanner for CI/CD pipelines",
    add_completion=False,
)

# Rich 콘솔 (예쁜 출력용)
console = Console()


def display_findings(findings: list[Finding]) -> None:
    """
    Finding 리스트를 예쁜 테이블로 출력합니다.
    """
    if not findings:
        console.print("[green]No PHI found.[/green]")
        return

    # 테이블 생성
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
        # 파일 경로가 너무 길면 줄임
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


@app.command()
def scan(
    path: Path = typer.Argument(
        ...,
        help="File or directory to scan",
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
) -> None:
    """
    Scan files for Protected Health Information (PHI).

    Detects SSN, MRN, phone numbers, and other HIPAA-defined identifiers.
    """
    console.print(f"[bold]Scanning:[/bold] {path}")
    console.print(f"[dim]Threshold: {threshold}, Recursive: {recursive}[/dim]")
    console.print()

    try:
        if path.is_file():
            findings = scan_file(path, score_threshold=threshold)
        else:
            findings = scan_directory(
                path,
                score_threshold=threshold,
                recursive=recursive,
            )

        display_findings(findings)

        # PHI가 발견되면 exit code 1 (CI/CD에서 실패 처리용)
        if findings:
            raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)


@app.command()
def version() -> None:
    """
    Show PHI Guard version.
    """
    console.print("[bold]PHI Guard[/bold] v0.1.0")


def main() -> None:
    """
    CLI 진입점. pyproject.toml의 scripts에서 호출됨.
    """
    app()


if __name__ == "__main__":
    main()
