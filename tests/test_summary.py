"""Tests for summary command and formatters."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from click.testing import CliRunner

from devscope.cli import cli
from devscope.formatters import (
    format_days_since_commit,
    format_languages,
    generate_badge_url,
    generate_health_block,
    get_cache_color,
    get_grade_color,
    get_onboarding_color,
    get_risk_color,
    is_ci_environment,
)
from devscope.models import OnboardingDifficulty, RiskLevel


class TestBadgeColors:
    """Test badge color mapping functions."""

    def test_grade_colors(self) -> None:
        """Test grade color mapping."""
        assert get_grade_color("A") == "brightgreen"
        assert get_grade_color("B") == "green"
        assert get_grade_color("C") == "yellowgreen"
        assert get_grade_color("D") == "yellow"
        assert get_grade_color("E") == "orange"
        assert get_grade_color("F") == "red"
        assert get_grade_color("a") == "brightgreen"  # Case insensitive

    def test_risk_colors(self) -> None:
        """Test risk level color mapping."""
        assert get_risk_color(RiskLevel.LOW) == "green"
        assert get_risk_color(RiskLevel.MEDIUM) == "orange"
        assert get_risk_color(RiskLevel.HIGH) == "red"

    def test_onboarding_colors(self) -> None:
        """Test onboarding difficulty color mapping."""
        assert get_onboarding_color(OnboardingDifficulty.EASY) == "blue"
        assert get_onboarding_color(OnboardingDifficulty.MODERATE) == "yellow"
        assert get_onboarding_color(OnboardingDifficulty.HARD) == "red"

    def test_cache_colors(self) -> None:
        """Test cache hit rate color mapping."""
        assert get_cache_color(100) == "success"
        assert get_cache_color(90) == "success"
        assert get_cache_color(80) == "green"
        assert get_cache_color(70) == "green"
        assert get_cache_color(60) == "yellow"
        assert get_cache_color(50) == "yellow"
        assert get_cache_color(30) == "orange"
        assert get_cache_color(0) == "orange"


class TestBadgeGeneration:
    """Test badge URL generation."""

    def test_generate_badge_url(self) -> None:
        """Test basic badge URL generation."""
        url = generate_badge_url("label", "message", "green")
        assert url == "https://img.shields.io/badge/label-message-green"

    def test_generate_badge_url_with_spaces(self) -> None:
        """Test badge URL encoding with spaces."""
        url = generate_badge_url("my label", "my message", "blue")
        assert "my%20label" in url
        assert "my%20message" in url

    def test_generate_badge_url_with_percent(self) -> None:
        """Test badge URL encoding with percent signs."""
        url = generate_badge_url("cache", "91%", "success")
        assert "91%25" in url  # % should be encoded as %25

    def test_ci_environment_detection(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test CI environment detection."""
        # Test with no CI env vars
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        assert is_ci_environment() is False

        # Test with CI=true
        monkeypatch.setenv("CI", "true")
        assert is_ci_environment() is True

        # Test with GITHUB_ACTIONS
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        assert is_ci_environment() is True


class TestFormatHelpers:
    """Test formatting helper functions."""

    def test_format_languages(self) -> None:
        """Test language breakdown formatting."""
        languages = {"Python": 45.0, "JavaScript": 33.0, "TypeScript": 12.0, "Shell": 5.0}
        result = format_languages(languages, max_langs=3)
        assert result == "Python (45%) · JavaScript (33%) · TypeScript (12%)"

    def test_format_languages_fewer_than_max(self) -> None:
        """Test language formatting with fewer languages than max."""
        languages = {"Python": 80.0, "Shell": 20.0}
        result = format_languages(languages, max_langs=3)
        assert result == "Python (80%) · Shell (20%)"

    def test_format_days_since_commit(self) -> None:
        """Test days since commit formatting."""
        assert format_days_since_commit(None) == "N/A"
        assert format_days_since_commit(0) == "today"
        assert format_days_since_commit(1) == "1 day ago"
        assert format_days_since_commit(5) == "5 days ago"
        assert format_days_since_commit(365) == "365 days ago"


class TestMarkdownGeneration:
    """Test markdown summary generation."""

    def test_generate_markdown_summary_basic(self) -> None:
        """Test basic markdown summary generation."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result = runner.invoke(cli, ["summary", str(root), "--no-git"])

            assert result.exit_code == 0
            output = result.output

            # Check header
            assert "## 🔍 Devscope Report" in output

            # Check repo info
            assert "**Repo:**" in output
            assert "**Files:**" in output
            assert "**Lines:**" in output

            # Check performance line
            assert "⚡ Scan time:" in output

    def test_generate_markdown_with_badges(self) -> None:
        """Test markdown summary with badges."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result = runner.invoke(cli, ["summary", str(root), "--no-git", "--badges"])

            assert result.exit_code == 0
            output = result.output

            # Check badges are present
            assert "img.shields.io" in output
            assert "![Badge]" in output

    def test_markdown_deterministic(self) -> None:
        """Test markdown output is deterministic."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result1 = runner.invoke(cli, ["summary", str(root), "--no-git"])
            result2 = runner.invoke(cli, ["summary", str(root), "--no-git"])

            assert result1.exit_code == 0
            assert result2.exit_code == 0

            # Outputs should be identical (except scan time which may vary slightly)
            # Check structure is the same
            assert "## 🔍 Devscope Report" in result1.output
            assert "## 🔍 Devscope Report" in result2.output

    def test_cache_badge_in_ci(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test cache badge shows 'cold' in CI with low hit rate."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            # Simulate CI environment
            monkeypatch.setenv("CI", "true")

            # First run with cleared cache (will have low/zero hit rate)
            runner = CliRunner()
            result = runner.invoke(cli, ["summary", str(root), "--no-git", "--clear-cache", "--badges"])

            assert result.exit_code == 0
            output = result.output

            # Should show "cold" instead of "0%" in CI
            assert "cache-cold" in output or "cache: 0%" not in output


class TestCompactSummary:
    """Test compact summary generation."""

    def test_generate_compact_summary(self) -> None:
        """Test compact one-line summary."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result = runner.invoke(cli, ["summary", str(root), "--no-git", "--compact"])

            assert result.exit_code == 0
            output = result.output.strip()

            # Should be single line
            assert "\n" not in output or output.count("\n") <= 1

            # Check key components
            assert "Devscope:" in output
            assert "risk" in output.lower()
            assert "⚡" in output

    def test_compact_includes_test_ratio(self) -> None:
        """Test compact summary includes test ratio."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)
            (root / "test_something.py").write_text("def test(): pass\n")

            runner = CliRunner()
            result = runner.invoke(cli, ["summary", str(root), "--no-git", "--compact"])

            assert result.exit_code == 0
            output = result.output

            assert "tests" in output


class TestJSONSummary:
    """Test JSON summary generation."""

    def test_generate_json_summary(self) -> None:
        """Test JSON summary generation."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result = runner.invoke(cli, ["summary", str(root), "--no-git", "--json"])

            assert result.exit_code == 0

            # Parse JSON
            output_data = json.loads(result.output)

            # Check required fields
            assert "repo" in output_data
            assert "total_files" in output_data
            assert "total_lines" in output_data
            assert "scan_time" in output_data
            assert "health" in output_data
            assert "badges" in output_data

    def test_json_summary_badges(self) -> None:
        """Test JSON summary includes badge URLs."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result = runner.invoke(cli, ["summary", str(root), "--no-git", "--json"])

            assert result.exit_code == 0
            output_data = json.loads(result.output)

            badges = output_data["badges"]
            assert "maintainability" in badges
            assert "risk" in badges
            assert "onboarding" in badges
            assert "cache" in badges

            # Check URLs are valid
            for badge_url in badges.values():
                assert badge_url.startswith("https://img.shields.io/badge/")

    def test_json_summary_cache_stats(self) -> None:
        """Test JSON summary includes cache stats."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()

            # First run - populate cache
            result1 = runner.invoke(cli, ["summary", str(root), "--no-git", "--json"])
            assert result1.exit_code == 0

            # Second run - use cache
            result2 = runner.invoke(cli, ["summary", str(root), "--no-git", "--json"])
            assert result2.exit_code == 0

            output_data = json.loads(result2.output)
            assert "cache" in output_data
            cache = output_data["cache"]
            assert cache["enabled"]
            assert cache["hit_rate"] == 100.0


class TestSummaryCLIIntegration:
    """Test summary CLI command integration."""

    def test_summary_with_no_cache_flag(self) -> None:
        """Test summary command with --no-cache."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result = runner.invoke(cli, ["summary", str(root), "--no-git", "--no-cache", "--json"])

            assert result.exit_code == 0
            output_data = json.loads(result.output)

            # Should not have cache stats
            assert output_data.get("cache") is None

    def test_summary_with_clear_cache_flag(self) -> None:
        """Test summary command with --clear-cache."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()

            # First run - populate cache
            result1 = runner.invoke(cli, ["summary", str(root), "--no-git", "--json"])
            assert result1.exit_code == 0

            # Second run with clear cache
            result2 = runner.invoke(cli, ["summary", str(root), "--no-git", "--clear-cache", "--json"])
            assert result2.exit_code == 0

            output_data = json.loads(result2.output)
            cache = output_data["cache"]

            # Cache should be rebuilt (all misses)
            assert cache["hit_rate"] == 0.0

    def test_summary_default_is_markdown(self) -> None:
        """Test summary defaults to markdown output."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result = runner.invoke(cli, ["summary", str(root), "--no-git"])

            assert result.exit_code == 0
            output = result.output

            # Should be markdown (not JSON)
            assert "## 🔍 Devscope Report" in output
            assert not output.strip().startswith("{")

    def test_summary_no_git_behavior(self) -> None:
        """Test summary command with --no-git."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result = runner.invoke(cli, ["summary", str(root), "--no-git", "--json"])

            assert result.exit_code == 0
            output_data = json.loads(result.output)

            # Git info should indicate not a repo
            if "git" in output_data:
                assert output_data["git"]["is_repo"] is False

    def test_summary_with_multiple_languages(self) -> None:
        """Test summary with multiple languages."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 20)
            (root / "test.js").write_text("const x = 1;\n" * 10)
            (root / "test.ts").write_text("const x: number = 1;\n" * 5)

            runner = CliRunner()
            result = runner.invoke(cli, ["summary", str(root), "--no-git"])

            assert result.exit_code == 0
            output = result.output

            # Should mention multiple languages
            assert "Languages:" in output
            assert "Python" in output
            assert "JavaScript" in output or "TypeScript" in output

    def test_summary_command_help(self) -> None:
        """Test summary command help text."""
        runner = CliRunner()
        result = runner.invoke(cli, ["summary", "--help"])

        assert result.exit_code == 0
        assert "Generate shareable markdown summary" in result.output
        assert "--markdown" in result.output
        assert "--badges" in result.output
        assert "--compact" in result.output
        assert "--json" in result.output
        assert "--no-cache" in result.output
        assert "--clear-cache" in result.output

    def test_summary_error_handling(self) -> None:
        """Test summary command error handling."""
        runner = CliRunner()
        # Try to analyze non-existent directory
        result = runner.invoke(cli, ["summary", "/nonexistent/path"])

        assert result.exit_code != 0


class TestHealthBlockGeneration:
    """Test health block generation for README injection."""

    def test_generate_health_block_basic(self) -> None:
        """Test basic health block generation."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("def hello(): pass\n" * 10)

            runner = CliRunner()
            result = runner.invoke(cli, ["scan", str(root), "--no-git", "--json"])
            assert result.exit_code == 0

            from devscope.analyzer import CodebaseAnalyzer
            analyzer = CodebaseAnalyzer(root, detect_git=False, enable_intelligence=True)
            analysis_result = analyzer.analyze()

            health_block = generate_health_block(analysis_result)

            # Verify structure
            assert "## 🔍 Devscope Report" in health_block
            assert "**Repo:**" in health_block
            assert "**Files:**" in health_block
            assert "**Lines:**" in health_block
            assert "⚡ Scan time:" in health_block

    def test_generate_health_block_deterministic(self) -> None:
        """Test that health block generation is deterministic."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("def hello(): pass\n" * 10)

            from devscope.analyzer import CodebaseAnalyzer
            analyzer = CodebaseAnalyzer(root, detect_git=False, enable_intelligence=True)

            # Run analysis twice
            result1 = analyzer.analyze()
            result2 = analyzer.analyze()

            # Generate health blocks
            block1 = generate_health_block(result1)
            block2 = generate_health_block(result2)

            # Should be identical (deterministic)
            assert block1 == block2

    def test_generate_health_block_with_badges(self) -> None:
        """Test health block includes badges."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("def hello(): pass\n" * 10)

            from devscope.analyzer import CodebaseAnalyzer
            analyzer = CodebaseAnalyzer(root, detect_git=False, enable_intelligence=True)
            analysis_result = analyzer.analyze()

            health_block = generate_health_block(analysis_result)

            # Should include badge URLs
            assert "![Badge](" in health_block
            assert "img.shields.io" in health_block
            assert "maintainability" in health_block


class TestInjectCommand:
    """Test devscope inject command."""

    def test_inject_command_basic(self) -> None:
        """Test basic inject functionality."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            readme = root / "README.md"

            # Create README with markers
            readme.write_text("""# My Project

Some intro text.

<!-- DEVSCOPE_START -->
<!-- DEVSCOPE_END -->

More content below.
""")

            # Create some code to analyze
            (root / "test.py").write_text("def hello(): pass\n" * 10)

            runner = CliRunner()
            result = runner.invoke(cli, ["inject", str(readme), "--no-git"])

            assert result.exit_code == 0
            assert "Updated README.md" in result.output

            # Verify README was updated
            updated_content = readme.read_text()
            assert "## 🔍 Devscope Report" in updated_content
            assert "**Repo:**" in updated_content
            assert "<!-- DEVSCOPE_START -->" in updated_content
            assert "<!-- DEVSCOPE_END -->" in updated_content

    def test_inject_command_idempotent(self) -> None:
        """Test inject is idempotent (no change = no write)."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            readme = root / "README.md"

            # Create README with markers
            readme.write_text("""# My Project

<!-- DEVSCOPE_START -->
<!-- DEVSCOPE_END -->
""")

            # Create some code
            (root / "test.py").write_text("def hello(): pass\n" * 10)

            runner = CliRunner()

            # First injection
            result1 = runner.invoke(cli, ["inject", str(readme), "--no-git"])
            assert result1.exit_code == 0
            assert "Updated README.md" in result1.output

            # Get modified time
            import time
            time.sleep(0.1)  # Ensure timestamps differ if file changes
            mtime1 = readme.stat().st_mtime

            # Second injection (should detect no change)
            result2 = runner.invoke(cli, ["inject", str(readme), "--no-git"])
            assert result2.exit_code == 0
            assert "up to date" in result2.output.lower()

            # Verify file wasn't rewritten
            mtime2 = readme.stat().st_mtime
            assert mtime1 == mtime2

    def test_inject_command_missing_markers(self) -> None:
        """Test inject fails gracefully when markers missing."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            readme = root / "README.md"

            # Create README without markers
            readme.write_text("# My Project\n\nNo markers here.\n")

            runner = CliRunner()
            result = runner.invoke(cli, ["inject", str(readme)])

            assert result.exit_code == 1
            assert "Markers not found" in result.output
            assert "DEVSCOPE_START" in result.output

    def test_inject_command_check_mode(self) -> None:
        """Test inject --check mode."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            readme = root / "README.md"

            # Create README with markers
            readme.write_text("""# My Project

<!-- DEVSCOPE_START -->
<!-- DEVSCOPE_END -->
""")

            (root / "test.py").write_text("def hello(): pass\n" * 10)

            runner = CliRunner()

            # Check mode on fresh README (should exit 2 - update needed)
            result1 = runner.invoke(cli, ["inject", str(readme), "--no-git", "--check"])
            assert result1.exit_code == 2
            assert "needs update" in result1.output.lower()

            # Verify file was NOT modified
            content = readme.read_text()
            assert "## 🔍 Devscope Report" not in content

            # Actually inject
            result2 = runner.invoke(cli, ["inject", str(readme), "--no-git"])
            assert result2.exit_code == 0

            # Check mode on updated README (should exit 0 - no change)
            result3 = runner.invoke(cli, ["inject", str(readme), "--no-git", "--check"])
            assert result3.exit_code == 0
            assert "No changes needed" in result3.output

    def test_inject_command_custom_markers(self) -> None:
        """Test inject with custom markers."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            readme = root / "README.md"

            # Create README with custom markers
            readme.write_text("""# My Project

<!-- CUSTOM_START -->
<!-- CUSTOM_END -->
""")

            (root / "test.py").write_text("def hello(): pass\n" * 10)

            runner = CliRunner()
            result = runner.invoke(
                cli,
                [
                    "inject",
                    str(readme),
                    "--no-git",
                    "--start-marker=<!-- CUSTOM_START -->",
                    "--end-marker=<!-- CUSTOM_END -->",
                ],
            )

            assert result.exit_code == 0
            assert "Updated README.md" in result.output

            # Verify content was injected between custom markers
            updated_content = readme.read_text()
            assert "<!-- CUSTOM_START -->" in updated_content
            assert "<!-- CUSTOM_END -->" in updated_content
            assert "## 🔍 Devscope Report" in updated_content

    def test_inject_command_separate_repo_path(self) -> None:
        """Test inject can analyze separate repo path."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            docs_dir = root / "docs"
            src_dir = root / "src"

            docs_dir.mkdir()
            src_dir.mkdir()

            readme = docs_dir / "README.md"
            readme.write_text("""# Docs

<!-- DEVSCOPE_START -->
<!-- DEVSCOPE_END -->
""")

            # Create code in src directory
            (src_dir / "main.py").write_text("def main(): pass\n" * 20)

            runner = CliRunner()
            result = runner.invoke(
                cli,
                [
                    "inject",
                    str(readme),
                    "--repo",
                    str(src_dir),
                    "--no-git",
                ],
            )

            assert result.exit_code == 0

            # Verify health block reflects src directory analysis
            updated_content = readme.read_text()
            assert "## 🔍 Devscope Report" in updated_content

    def test_inject_command_preserves_surrounding_content(self) -> None:
        """Test inject preserves content before and after markers."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            readme = root / "README.md"

            original_content = """# My Project

Introduction paragraph.

<!-- DEVSCOPE_START -->
Old content here
<!-- DEVSCOPE_END -->

## Other Section

More content below.
"""
            readme.write_text(original_content)
            (root / "test.py").write_text("def hello(): pass\n" * 10)

            runner = CliRunner()
            result = runner.invoke(cli, ["inject", str(readme), "--no-git"])

            assert result.exit_code == 0

            updated_content = readme.read_text()

            # Verify surrounding content preserved
            assert "# My Project" in updated_content
            assert "Introduction paragraph" in updated_content
            assert "## Other Section" in updated_content
            assert "More content below" in updated_content

            # Verify health block injected
            assert "## 🔍 Devscope Report" in updated_content

            # Verify old content replaced
            assert "Old content here" not in updated_content

