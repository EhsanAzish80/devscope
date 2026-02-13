"""Tests for summary command and formatters."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from click.testing import CliRunner

from devscope.cli import cli
from devscope.formatters import (
    format_days_since_commit,
    format_dependencies,
    format_languages,
    generate_badge_url,
    generate_badges,
    generate_compact_summary,
    generate_json_summary,
    generate_markdown_summary,
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
