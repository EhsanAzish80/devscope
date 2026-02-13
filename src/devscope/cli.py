"""CLI interface for devscope."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from devscope.analyzer import CodebaseAnalyzer
from devscope.cache import CacheManager
from devscope.formatters import (
    generate_compact_summary,
    generate_health_block,
    generate_json_summary,
    generate_markdown_summary,
)
from devscope.models import (
    AnalysisResult,
    CIResult,
    CIThresholds,
    Grade,
    OnboardingDifficulty,
    RiskLevel,
)

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
        inverse_ratio = f"(1:{1 / tests.test_ratio:.1f})" if tests.test_ratio > 0 else "(0:∞)"

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


def check_ci_thresholds(result: AnalysisResult, thresholds: CIThresholds) -> CIResult:
    """Check if analysis result meets CI thresholds.

    Args:
        result: Analysis result to check
        thresholds: CI threshold configuration

    Returns:
        CIResult with pass/fail status and failure reasons
    """
    failures: list[str] = []
    actual_grade = None
    actual_risk = None
    actual_onboarding = None

    if not result.health_score:
        # No health score available - fail if any thresholds set
        if thresholds.min_grade or thresholds.max_risk or thresholds.max_onboarding:
            failures.append("Health score not available (run with intelligence enabled)")
            return CIResult(
                passed=False,
                thresholds=thresholds,
                failures=failures,
            )
        # No thresholds, no health score - pass
        return CIResult(passed=True, thresholds=thresholds)

    health = result.health_score
    actual_grade = health.maintainability_grade
    actual_risk = health.risk_level.value
    actual_onboarding = health.onboarding_difficulty.value

    # Check grade threshold
    if thresholds.min_grade:
        try:
            current_grade = Grade.from_string(health.maintainability_grade)
            if current_grade > thresholds.min_grade:
                failures.append(
                    f"Grade {current_grade.value} is below minimum {thresholds.min_grade.value}"
                )
        except ValueError as e:
            failures.append(f"Invalid grade comparison: {e}")

    # Check risk level threshold
    if thresholds.max_risk and health.risk_level > thresholds.max_risk:
        failures.append(
            f"Risk level {health.risk_level.value} exceeds maximum {thresholds.max_risk.value}"
        )

    # Check onboarding difficulty threshold
    if thresholds.max_onboarding and health.onboarding_difficulty > thresholds.max_onboarding:
        failures.append(
            f"Onboarding difficulty {health.onboarding_difficulty.value} exceeds maximum {thresholds.max_onboarding.value}"
        )

    return CIResult(
        passed=len(failures) == 0,
        thresholds=thresholds,
        actual_grade=actual_grade,
        actual_risk=actual_risk,
        actual_onboarding=actual_onboarding,
        failures=failures,
    )


def print_ci_summary(result: AnalysisResult, ci_result: CIResult) -> None:
    """Print compact CI summary.

    Args:
        result: Analysis result
        ci_result: CI threshold check result
    """
    console.print("\n[bold cyan]═══ CI Analysis Summary ═══[/bold cyan]\n")

    # Repository info
    console.print(f"[dim]Repository:[/dim] {result.repo_name or 'Unknown'}")
    console.print(f"[dim]Files:[/dim] {result.total_files:,}  [dim]Lines:[/dim] {result.total_lines:,}\n")

    # Health metrics
    if result.health_score:
        health = result.health_score
        grade_color = {
            "A": "green",
            "B": "green",
            "C": "yellow",
            "D": "orange",
            "F": "red",
        }.get(health.maintainability_grade, "white")

        console.print("[bold]Code Health:[/bold]")
        console.print(f"  Grade: [{grade_color}]{health.maintainability_grade}[/{grade_color}]")
        console.print(f"  Risk Level: {health.risk_level.value}")
        console.print(f"  Onboarding: {health.onboarding_difficulty.value}\n")

    # Thresholds
    if (
        ci_result.thresholds.min_grade
        or ci_result.thresholds.max_risk
        or ci_result.thresholds.max_onboarding
    ):
        console.print("[bold]Thresholds:[/bold]")
        if ci_result.thresholds.min_grade:
            console.print(f"  Minimum Grade: {ci_result.thresholds.min_grade.value}")
        if ci_result.thresholds.max_risk:
            console.print(f"  Maximum Risk: {ci_result.thresholds.max_risk.value}")
        if ci_result.thresholds.max_onboarding:
            console.print(f"  Maximum Onboarding: {ci_result.thresholds.max_onboarding.value}")
        console.print()

    # Result status
    if ci_result.passed:
        console.print("[bold green]✓ All thresholds passed[/bold green]\n")
    else:
        console.print("[bold red]✗ Threshold violations:[/bold red]")
        for failure in ci_result.failures:
            console.print(f"  • {failure}")
        console.print()


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
@click.option("--no-cache", is_flag=True, help="Disable caching for this scan")
@click.option("--clear-cache", is_flag=True, help="Clear cache before scanning")
def scan(path: Optional[str], no_git: bool, basic: bool, output_json: bool, no_cache: bool, clear_cache: bool) -> None:
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
        # Set up cache manager
        cache_manager = None
        if not no_cache:
            cache_dir = Path(scan_path) / ".devscope_cache"
            cache_manager = CacheManager(cache_dir, enabled=True)

            if clear_cache:
                cache_manager.clear()
                if not output_json:
                    console.print("[dim]Cache cleared[/dim]\n")

        # Initialize analyzer
        analyzer = CodebaseAnalyzer(scan_path, detect_git=not no_git, enable_intelligence=not basic, cache_manager=cache_manager)

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
            msg = f"[green]✓[/green] Analysis complete in [cyan]{result.scan_time:.2f}s[/cyan]"
            if result.cache_stats and result.cache_stats["enabled"]:
                hit_rate = result.cache_stats["hit_rate"]
                time_saved = result.cache_stats["time_saved_estimate"]
                if hit_rate > 0:
                    msg += f" [dim](cache: {hit_rate:.0f}% hit rate, ~{time_saved:.2f}s saved)[/dim]"
            console.print(msg)

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
@click.option(
    "--fail-under",
    type=click.Choice(["A", "B", "C", "D", "E", "F"], case_sensitive=False),
    help="Fail if grade is below this threshold (A is best, F is worst)",
)
@click.option(
    "--max-risk",
    type=click.Choice(["Low", "Medium", "High"], case_sensitive=False),
    help="Fail if risk level exceeds this threshold",
)
@click.option(
    "--max-onboarding",
    type=click.Choice(["Easy", "Moderate", "Hard"], case_sensitive=False),
    help="Fail if onboarding difficulty exceeds this threshold",
)
@click.option("--json", "output_json", is_flag=True, help="Output results as JSON")
@click.option("--no-cache", is_flag=True, help="Disable caching for this scan")
@click.option("--clear-cache", is_flag=True, help="Clear cache before scanning")
def ci(
    path: Optional[str],
    no_git: bool,
    fail_under: Optional[str],
    max_risk: Optional[str],
    max_onboarding: Optional[str],
    output_json: bool,
    no_cache: bool,
    clear_cache: bool,
) -> None:
    """CI-friendly analysis with threshold checking.

    Designed for automation, performs full intelligence analysis and checks
    against specified thresholds. Exit codes:
      - 0: Analysis passed all thresholds
      - 1: Runtime error (invalid path, permissions, etc.)
      - 2: One or more thresholds violated

    PATH: Directory to analyze (defaults to current directory)
    """
    # Determine scan path
    scan_path = Path(path) if path else Path.cwd()
    scan_path = scan_path.resolve()

    try:
        # Set up cache manager
        cache_manager = None
        if not no_cache:
            cache_dir = Path(scan_path) / ".devscope_cache"
            cache_manager = CacheManager(cache_dir, enabled=True)

            if clear_cache:
                cache_manager.clear()

        # Initialize analyzer with full intelligence
        analyzer = CodebaseAnalyzer(scan_path, detect_git=not no_git, enable_intelligence=True, cache_manager=cache_manager)

        # Run analysis (no progress indicators)
        result = analyzer.analyze()

        # Build threshold configuration
        thresholds = CIThresholds(
            min_grade=Grade.from_string(fail_under) if fail_under else None,
            max_risk=RiskLevel[max_risk.upper()] if max_risk else None,
            max_onboarding=OnboardingDifficulty[max_onboarding.upper()] if max_onboarding else None,
        )

        # Check thresholds
        ci_result = check_ci_thresholds(result, thresholds)

        # Output results
        if output_json:
            # JSON output with CI section
            output_dict = result.to_json_dict()
            output_dict["ci"] = ci_result.to_dict()
            print(json.dumps(output_dict, indent=2, sort_keys=True))
        else:
            # Human-readable CI summary
            print_ci_summary(result, ci_result)

        # Exit with appropriate code
        if not ci_result.passed:
            sys.exit(2)  # Threshold violations

    except Exception as e:
        if output_json:
            error_output = {
                "schema_version": "1.0",
                "error": str(e),
                "success": False,
            }
            print(json.dumps(error_output, indent=2))
        else:
            console.print(f"\n[red]Error:[/red] {str(e)}", style="bold")

        sys.exit(1)  # Runtime error


@cli.command()
@click.argument("path", type=click.Path(exists=True), required=False)
@click.option("--no-git", is_flag=True, help="Skip git repository detection")
@click.option("--markdown", "output_markdown", is_flag=True, default=True, help="Output as markdown (default)")
@click.option("--badges", is_flag=True, help="Include shields.io badges in markdown")
@click.option("--compact", is_flag=True, help="Single-line condensed summary")
@click.option("--json", "output_json", is_flag=True, help="Machine-readable JSON summary")
@click.option("--no-cache", is_flag=True, help="Disable caching for this scan")
@click.option("--clear-cache", is_flag=True, help="Clear cache before scanning")
def summary(
    path: Optional[str],
    no_git: bool,
    output_markdown: bool,  # noqa: ARG001
    badges: bool,
    compact: bool,
    output_json: bool,
    no_cache: bool,
    clear_cache: bool,
) -> None:
    """Generate shareable markdown summary for READMEs and PRs.

    Produces copy-paste-ready output for embedding in documentation,
    pull request comments, audit reports, and CI summaries.

    PATH: Directory to analyze (defaults to current directory)
    """
    # Determine scan path
    scan_path = Path(path) if path else Path.cwd()
    scan_path = scan_path.resolve()

    try:
        # Set up cache manager
        cache_manager = None
        if not no_cache:
            cache_dir = Path(scan_path) / ".devscope_cache"
            cache_manager = CacheManager(cache_dir, enabled=True)

            if clear_cache:
                cache_manager.clear()

        # Initialize analyzer with full intelligence
        analyzer = CodebaseAnalyzer(
            scan_path, detect_git=not no_git, enable_intelligence=True, cache_manager=cache_manager
        )

        # Run analysis (no progress indicators)
        result = analyzer.analyze()

        # Determine output format
        if output_json:
            # JSON summary mode
            summary_dict = generate_json_summary(result)
            print(json.dumps(summary_dict, indent=2, sort_keys=True))
        elif compact:
            # Compact one-line mode
            compact_text = generate_compact_summary(result)
            print(compact_text)
        else:
            # Markdown mode (default)
            markdown_text = generate_markdown_summary(result, include_badges=badges)
            print(markdown_text)

    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}", style="bold")
        sys.exit(1)


@cli.command()
@click.argument("readme_path", type=click.Path(exists=True), required=False)
@click.option("--repo", "repo_path", type=click.Path(exists=True), help="Repository path to analyze (default: same as README)")
@click.option("--no-git", is_flag=True, help="Skip git repository detection")
@click.option("--no-cache", is_flag=True, help="Disable caching for this scan")
@click.option("--check", is_flag=True, help="Check if injection is needed without writing")
@click.option("--start-marker", default="<!-- DEVSCOPE_START -->", help="Start marker for injection block")
@click.option("--end-marker", default="<!-- DEVSCOPE_END -->", help="End marker for injection block")
def inject(
    readme_path: Optional[str],
    repo_path: Optional[str],
    no_git: bool,
    no_cache: bool,
    check: bool,
    start_marker: str,
    end_marker: str,
) -> None:
    """Inject health metrics into README between markers.
    
    Updates README.md (or specified file) with current health metrics between
    marker comments. Only writes if content has changed (idempotent).
    
    Markers in your README:
        <!-- DEVSCOPE_START -->
        (health block will be injected here)
        <!-- DEVSCOPE_END -->
    
    README_PATH: Path to README file (default: ./README.md)
    
    Exit codes:
      - 0: Success (content updated or unchanged)
      - 1: Error (missing markers, invalid path, etc.)
      - 2: Check mode - update needed
    """
    # Determine paths
    readme_file = Path(readme_path) if readme_path else Path.cwd() / "README.md"
    scan_path = Path(repo_path) if repo_path else readme_file.parent
    
    readme_file = readme_file.resolve()
    scan_path = scan_path.resolve()
    
    # Validate README exists
    if not readme_file.exists():
        console.print(f"[red]Error:[/red] README not found: {readme_file}")
        sys.exit(1)
    
    try:
        # Read current README content
        with open(readme_file, "r", encoding="utf-8") as f:
            original_content = f.read()
        
        # Check for markers
        if start_marker not in original_content or end_marker not in original_content:
            console.print(f"[red]Error:[/red] Markers not found in {readme_file.name}")
            console.print(f"\nAdd these markers to your README:\n")
            console.print(f"    {start_marker}")
            console.print(f"    {end_marker}\n")
            sys.exit(1)
        
        # Set up cache manager
        cache_manager = None
        if not no_cache:
            cache_dir = Path(scan_path) / ".devscope_cache"
            cache_manager = CacheManager(cache_dir, enabled=True)
        
        # Run analysis
        analyzer = CodebaseAnalyzer(
            scan_path, 
            detect_git=not no_git, 
            enable_intelligence=True, 
            cache_manager=cache_manager
        )
        
        if not check:
            console.print(f"[dim]Analyzing {scan_path.name}...[/dim]")
        
        result = analyzer.analyze()
        
        # Generate health block
        health_block = generate_health_block(result)
        
        # Build new content
        start_idx = original_content.find(start_marker)
        end_idx = original_content.find(end_marker)
        
        if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
            console.print(f"[red]Error:[/red] Invalid marker positions in {readme_file.name}")
            sys.exit(1)
        
        # Extract sections carefully to preserve spacing
        before_marker = original_content[:start_idx + len(start_marker)]
        after_marker = original_content[end_idx:]
        
        # Build new content with health block
        # Ensure exactly one newline before health block, and health block ends with newline
        if not health_block.endswith('\n'):
            health_block += '\n'
        
        new_content = f"{before_marker}\n{health_block}{after_marker}"
        
        # Check if content changed
        if new_content == original_content:
            if check:
                console.print(f"[green]✓[/green] No changes needed")
                sys.exit(0)
            else:
                console.print(f"[green]✓[/green] Health block up to date (no changes)")
                return
        
        # Check mode - report difference and exit
        if check:
            console.print(f"[yellow]⚠[/yellow]  Health block needs update")
            sys.exit(2)
        
        # Write updated content
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        console.print(f"[green]✓[/green] Updated {readme_file.name}")
        console.print(f"[dim]  Grade: {result.health_score.maintainability_grade if result.health_score else 'N/A'}[/dim]")
        console.print(f"[dim]  Scan time: {result.scan_time:.2f}s[/dim]")
    
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}", style="bold")
        import traceback
        if "--debug" in sys.argv:
            traceback.print_exc()
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
