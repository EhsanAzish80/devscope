"""CLI interface for devscope."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from devscope.analyzer import CodebaseAnalyzer
from devscope.models import AnalysisResult

console = Console()


def print_banner() -> None:
    """Display the startup banner."""
    banner = """
[bold cyan]╔═══════════════════════════════════════╗[/bold cyan]
[bold cyan]║[/bold cyan]     [bold white]devscope[/bold white] [dim]v0.1.0[/dim]              [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]  [dim]Code Intelligence at a glance[/dim]   [bold cyan]║[/bold cyan]
[bold cyan]╚═══════════════════════════════════════╝[/bold cyan]
    """
    console.print(banner)


def format_number(num: int) -> str:
    """Format large numbers with comma separators."""
    return f"{num:,}"


def create_report_table(result: AnalysisResult) -> Table:
    """Create the basic analysis report table."""
    table = Table(title="📊 Codebase Overview", show_header=False, box=None, padding=(0, 2))
    table.add_column("Metric", style="bold cyan", width=25)
    table.add_column("Value", style="white")

    # Repository info
    table.add_row("Repository", result.repo_name or "Unknown")
    table.add_row("Total Files", format_number(result.total_files))
    table.add_row("Total Lines", format_number(result.total_lines))
    table.add_row("", "")  # Spacer

    # Languages
    if result.languages:
        table.add_row("[bold]Languages", "")
        for lang, pct in sorted(result.languages.items(), key=lambda x: x[1], reverse=True)[:5]:
            table.add_row(f"  {lang}", f"{pct:.1f}%")
        table.add_row("", "")  # Spacer

    # Largest directories
    if result.largest_dirs:
        table.add_row("[bold]Largest Directories", "")
        for dir_name, file_count in result.largest_dirs[:5]:
            table.add_row(f"  {dir_name}", f"{file_count} files")

    return table


def create_health_panel(result: AnalysisResult) -> Panel:
    """Create code health score panel."""
    if not result.health_score:
        return Panel("Extended analysis not available", title="💚 Code Health")

    health = result.health_score

    # Color code the grade
    grade_colors = {"A": "green", "B": "green", "C": "yellow", "D": "orange", "F": "red"}
    grade_color = grade_colors.get(health.maintainability_grade, "white")

    # Create content
    content = f"""[bold]Grade:[/bold] [{grade_color}]{health.maintainability_grade}[/{grade_color}]
[bold]Risk Level:[/bold] {health.risk_level.value}
[bold]Onboarding:[/bold] {health.onboarding_difficulty.value}

[bold]Components:[/bold]"""

    # Add score breakdown
    for component, score in sorted(health.score_breakdown.items()):
        bar_length = int(score / 5)
        bar = "█" * bar_length
        content += f"\\n  {component}: {score:.1f}/100 [{bar:20}]"

    return Panel(content, title="💊 Code Health", border_style="green")


def create_complexity_panel(result: AnalysisResult) -> Panel:
    """Create complexity metrics panel."""
    if not result.complexity:
        return Panel("No complexity data", title="🔄 Complexity Signals")

    complexity = result.complexity

    content = f"""[bold]Avg File Size:[/bold] {complexity.avg_file_size:.1f} bytes
[bold]Max Depth:[/bold] {complexity.max_directory_depth} levels"""

    if complexity.largest_files:
        content += "\n\n[bold]Largest Files:[/bold]"
        for file_path, size in complexity.largest_files[:5]:
            size_kb = size / 1024
            content += f"\n  • {file_path} [dim]({size_kb:.1f} KB)[/dim]"

    if complexity.deep_nesting_warning:
        content += "\n\n[yellow]⚠️  Deep directory nesting detected[/yellow]"

    return Panel(content, title="🔄 Complexity Signals", border_style="blue")


def create_hotspots_panel(result: AnalysisResult) -> Panel:
    """Create risk hotspots panel."""
    if not result.hotspots:
        return Panel("[green]No significant hotspots detected[/green]", title="🔥 Risk Hotspots")

    content = "[bold]Top Risk Areas:[/bold]\n\n"

    for hotspot in result.hotspots[:5]:
        # Color code risk score
        if hotspot.risk_score > 70:
            risk_color = "red"
        elif hotspot.risk_score > 50:
            risk_color = "yellow"
        else:
            risk_color = "orange"

        content += f"[{risk_color}]•[/{risk_color}] {hotspot.file_path}\n"
        content += f"  [dim]Score: {hotspot.risk_score:.0f} | LOC: {hotspot.lines_of_code} | {hotspot.reason}[/dim]\n\n"

    if len(result.hotspots) > 5:
        content += f"[dim]... and {len(result.hotspots) - 5} more hotspots[/dim]"

    return Panel(content.rstrip(), title="🔥 Risk Hotspots", border_style="red")


def create_dependencies_panel(result: AnalysisResult) -> Panel:
    """Create dependencies panel."""
    if not result.dependencies:
        return Panel("No dependency manifests found", title="📦 Dependencies")

    content = ""

    for dep_info in result.dependencies:
        content += f"[bold]{dep_info.ecosystem}[/bold] [dim]({dep_info.manifest_file})[/dim]\n"
        content += f"  {dep_info.dependency_count} dependencies"

        if dep_info.dependencies:
            top_deps = ", ".join(dep_info.dependencies[:5])
            content += f"\n  [dim]{top_deps}"
            if len(dep_info.dependencies) > 5:
                content += f", +{len(dep_info.dependencies) - 5} more"
            content += "[/dim]"

        content += "\n\n"

    return Panel(content.rstrip(), title="📦 Dependencies", border_style="magenta")


def create_tests_panel(result: AnalysisResult) -> Panel:
    """Create test metrics panel."""
    if not result.test_metrics:
        return Panel("No test data", title="🧪 Tests")

    tests = result.test_metrics

    if not tests.has_tests:
        content = "[yellow]⚠️  No tests detected[/yellow]"
    else:
        ratio_pct = tests.test_ratio * 100
        ratio_color = (
            "green" if tests.test_ratio >= 0.3 else "yellow" if tests.test_ratio >= 0.1 else "red"
        )

        # Calculate inverse ratio, handle zero case
        if tests.test_ratio > 0:
            inverse_ratio = f"(1:{1 / tests.test_ratio:.1f})"
        else:
            inverse_ratio = "(0:∞)"

        content = f"""[bold]Test Files:[/bold] {tests.test_file_count}
[bold]Source Files:[/bold] {tests.source_file_count}
[bold]Test Ratio:[/bold] [{ratio_color}]{ratio_pct:.1f}%[/{ratio_color}] [dim]{inverse_ratio}[/dim]"""

    return Panel(content, title="🧪 Test Coverage", border_style="cyan")


def create_git_panel(result: AnalysisResult) -> Panel:
    """Create git activity panel."""
    if not result.git_metrics or not result.git_metrics.is_git_repo:
        return Panel("Not a git repository", title="📊 Git Activity")

    git = result.git_metrics

    content = f"""[bold]Commits:[/bold] {format_number(git.commit_count)}
[bold]Contributors:[/bold] {git.contributor_count}"""

    if git.days_since_last_commit is not None:
        if git.days_since_last_commit == 0:
            last_commit = "today"
            color = "green"
        elif git.days_since_last_commit == 1:
            last_commit = "yesterday"
            color = "green"
        elif git.days_since_last_commit < 30:
            last_commit = f"{git.days_since_last_commit} days ago"
            color = "green"
        elif git.days_since_last_commit < 90:
            last_commit = f"{git.days_since_last_commit} days ago"
            color = "yellow"
        else:
            last_commit = f"{git.days_since_last_commit} days ago"
            color = "red"

        content += f"\n[bold]Last Commit:[/bold] [{color}]{last_commit}[/{color}]"

    return Panel(content, title="📊 Git Activity", border_style="blue")


@click.group()
@click.version_option(version="0.1.0", prog_name="devscope")
def cli() -> None:
    """devscope - Code intelligence at a glance."""
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True), required=False)
@click.option("--no-git", is_flag=True, help="Skip git repository detection")
@click.option("--basic", is_flag=True, help="Show only basic analysis (faster)")
@click.option("--json", "output_json", is_flag=True, help="Output results as JSON")
def scan(path: Optional[str], no_git: bool, basic: bool, output_json: bool) -> None:
    """Scan a codebase and generate an analysis report.

    PATH: Directory to analyze (defaults to current directory)
    """
    # Skip banner for JSON mode
    if not output_json:
        print_banner()

    # Determine scan path
    scan_path = Path(path) if path else Path.cwd()
    scan_path = scan_path.resolve()

    if not output_json:
        console.print(f"\n[dim]Scanning:[/dim] [cyan]{scan_path}[/cyan]\n")

    try:
        # Initialize analyzer
        analyzer = CodebaseAnalyzer(scan_path, detect_git=not no_git, enable_intelligence=not basic)

        # Run analysis with progress indicator (skip for JSON mode)
        if not output_json:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task_desc = "Analyzing codebase..." if basic else "Running intelligence analysis..."
                progress.add_task(description=task_desc, total=None)
                result = analyzer.analyze()
        else:
            result = analyzer.analyze()

        # Output results
        if output_json:
            print(result.to_json())
        else:
            # Display results with Rich formatting
            console.print()

            # Basic overview (always shown)
            table = create_report_table(result)
            console.print(table)
            console.print()

            # Extended intelligence (if enabled)
            if not basic and result.health_score:
                # Health score panel
                console.print(create_health_panel(result))
                console.print()

                # Create layout for remaining panels (2 columns)
                console.print("[bold cyan]═══ Detailed Intelligence ═══[/bold cyan]\n")

                # Row 1: Complexity and Tests
                console.print(create_complexity_panel(result), create_tests_panel(result))
                console.print()

                # Row 2: Dependencies and Git
                console.print(create_dependencies_panel(result), create_git_panel(result))
                console.print()

                # Hotspots (full width)
                console.print(create_hotspots_panel(result))
                console.print()

            # Success message
            console.print(
                f"[green]✓[/green] Analysis complete in [cyan]{result.scan_time:.2f}s[/cyan]"
            )

    except Exception as e:
        if output_json:
            import json

            error_output = {
                "schema_version": "1.0",
                "error": str(e),
                "success": False,
            }
            print(json.dumps(error_output, indent=2))
            sys.exit(1)
        else:
            console.print(f"\n[red]Error:[/red] {str(e)}", style="bold")
            import traceback

            if "--debug" in sys.argv:
                traceback.print_exc()
            sys.exit(1)


@cli.command()
@click.argument("path", type=click.Path(exists=True), required=False)
@click.option("--no-git", is_flag=True, help="Skip git repository detection")
def ci(path: Optional[str], no_git: bool) -> None:
    """CI-friendly analysis with JSON output and no interactive elements.

    Designed for automation, always outputs JSON and performs full intelligence analysis.

    PATH: Directory to analyze (defaults to current directory)
    """
    # Determine scan path
    scan_path = Path(path) if path else Path.cwd()
    scan_path = scan_path.resolve()

    try:
        # Initialize analyzer with full intelligence
        analyzer = CodebaseAnalyzer(scan_path, detect_git=not no_git, enable_intelligence=True)

        # Run analysis (no progress indicators)
        result = analyzer.analyze()

        # Always output JSON
        print(result.to_json())

    except Exception as e:
        import json

        error_output = {
            "schema_version": "1.0",
            "error": str(e),
            "success": False,
        }
        print(json.dumps(error_output, indent=2))
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
