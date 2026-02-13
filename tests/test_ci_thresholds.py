"""Tests for CI threshold functionality."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from click.testing import CliRunner

from devscope.cli import cli
from devscope.models import (
    Grade,
    OnboardingDifficulty,
    RiskLevel,
)


class TestGradeOrdering:
    """Test grade comparison operators."""

    def test_grade_from_string(self) -> None:
        """Test Grade.from_string() parsing."""
        assert Grade.from_string("A") == Grade.A
        assert Grade.from_string("a") == Grade.A
        assert Grade.from_string("B") == Grade.B
        assert Grade.from_string("F") == Grade.F

    def test_grade_from_string_invalid(self) -> None:
        """Test Grade.from_string() with invalid input."""
        with pytest.raises(ValueError):
            Grade.from_string("G")
        with pytest.raises(ValueError):
            Grade.from_string("Z")
        with pytest.raises(ValueError):
            Grade.from_string("1")

    def test_grade_ordering_less_than(self) -> None:
        """Test grade less than comparisons (A < F, better < worse)."""
        assert Grade.A < Grade.B
        assert Grade.B < Grade.C
        assert Grade.C < Grade.D
        assert Grade.D < Grade.E
        assert Grade.E < Grade.F

    def test_grade_ordering_greater_than(self) -> None:
        """Test grade greater than comparisons (F > A, worse > better)."""
        assert Grade.F > Grade.E
        assert Grade.E > Grade.D
        assert Grade.D > Grade.C
        assert Grade.C > Grade.B
        assert Grade.B > Grade.A

    def test_grade_ordering_less_than_or_equal(self) -> None:
        """Test grade <= comparisons."""
        assert Grade.A <= Grade.A
        assert Grade.A <= Grade.B
        assert Grade.C <= Grade.F

    def test_grade_ordering_greater_than_or_equal(self) -> None:
        """Test grade >= comparisons."""
        assert Grade.F >= Grade.F
        assert Grade.F >= Grade.E
        assert Grade.B >= Grade.A


class TestRiskLevelOrdering:
    """Test risk level comparison operators."""

    def test_risk_level_ordering_less_than(self) -> None:
        """Test risk level less than comparisons (Low < High)."""
        assert RiskLevel.LOW < RiskLevel.MEDIUM
        assert RiskLevel.MEDIUM < RiskLevel.HIGH
        assert RiskLevel.LOW < RiskLevel.HIGH

    def test_risk_level_ordering_greater_than(self) -> None:
        """Test risk level greater than comparisons (High > Low)."""
        assert RiskLevel.HIGH > RiskLevel.MEDIUM
        assert RiskLevel.MEDIUM > RiskLevel.LOW
        assert RiskLevel.HIGH > RiskLevel.LOW

    def test_risk_level_ordering_less_than_or_equal(self) -> None:
        """Test risk level <= comparisons."""
        assert RiskLevel.LOW <= RiskLevel.LOW
        assert RiskLevel.LOW <= RiskLevel.MEDIUM
        assert RiskLevel.MEDIUM <= RiskLevel.HIGH

    def test_risk_level_ordering_greater_than_or_equal(self) -> None:
        """Test risk level >= comparisons."""
        assert RiskLevel.HIGH >= RiskLevel.HIGH
        assert RiskLevel.HIGH >= RiskLevel.MEDIUM
        assert RiskLevel.MEDIUM >= RiskLevel.LOW


class TestOnboardingDifficultyOrdering:
    """Test onboarding difficulty comparison operators."""

    def test_onboarding_difficulty_ordering_less_than(self) -> None:
        """Test onboarding difficulty less than comparisons (Easy < Hard)."""
        assert OnboardingDifficulty.EASY < OnboardingDifficulty.MODERATE
        assert OnboardingDifficulty.MODERATE < OnboardingDifficulty.HARD
        assert OnboardingDifficulty.EASY < OnboardingDifficulty.HARD

    def test_onboarding_difficulty_ordering_greater_than(self) -> None:
        """Test onboarding difficulty greater than comparisons (Hard > Easy)."""
        assert OnboardingDifficulty.HARD > OnboardingDifficulty.MODERATE
        assert OnboardingDifficulty.MODERATE > OnboardingDifficulty.EASY
        assert OnboardingDifficulty.HARD > OnboardingDifficulty.EASY

    def test_onboarding_difficulty_ordering_less_than_or_equal(self) -> None:
        """Test onboarding difficulty <= comparisons."""
        assert OnboardingDifficulty.EASY <= OnboardingDifficulty.EASY
        assert OnboardingDifficulty.EASY <= OnboardingDifficulty.MODERATE
        assert OnboardingDifficulty.MODERATE <= OnboardingDifficulty.HARD

    def test_onboarding_difficulty_ordering_greater_than_or_equal(self) -> None:
        """Test onboarding difficulty >= comparisons."""
        assert OnboardingDifficulty.HARD >= OnboardingDifficulty.HARD
        assert OnboardingDifficulty.HARD >= OnboardingDifficulty.MODERATE
        assert OnboardingDifficulty.MODERATE >= OnboardingDifficulty.EASY


class TestCICommandExitCodes:
    """Test CI command exit codes with various thresholds."""

    def test_ci_command_default_passes(self) -> None:
        """Test ci command with no thresholds (should always pass with exit code 0)."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result = runner.invoke(cli, ["ci", str(root), "--no-git"])

            assert result.exit_code == 0

    def test_ci_command_fail_under_passes(self) -> None:
        """Test ci command with --fail-under threshold that passes."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            # Small file should get C grade, so --fail-under D should pass
            result = runner.invoke(cli, ["ci", str(root), "--no-git", "--fail-under", "D"])

            assert result.exit_code == 0

    def test_ci_command_fail_under_fails(self) -> None:
        """Test ci command with --fail-under threshold that fails."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n")

            runner = CliRunner()
            # Tiny file should get C grade, so --fail-under B should fail
            result = runner.invoke(cli, ["ci", str(root), "--no-git", "--fail-under", "B"])

            assert result.exit_code == 2  # Threshold violation

    def test_ci_command_max_risk_passes(self) -> None:
        """Test ci command with --max-risk threshold that passes."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result = runner.invoke(cli, ["ci", str(root), "--no-git", "--max-risk", "High"])

            assert result.exit_code == 0

    def test_ci_command_max_onboarding_passes(self) -> None:
        """Test ci command with --max-onboarding threshold that passes."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result = runner.invoke(cli, ["ci", str(root), "--no-git", "--max-onboarding", "Hard"])

            assert result.exit_code == 0

    def test_ci_command_multiple_thresholds_passes(self) -> None:
        """Test ci command with multiple thresholds that pass."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result = runner.invoke(
                cli, ["ci", str(root), "--no-git", "--fail-under", "D", "--max-risk", "High", "--max-onboarding", "Hard"]
            )

            assert result.exit_code == 0

    def test_ci_command_multiple_thresholds_fails(self) -> None:
        """Test ci command with multiple thresholds where one fails."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n")

            runner = CliRunner()
            result = runner.invoke(
                cli, ["ci", str(root), "--no-git", "--fail-under", "A", "--max-risk", "Low", "--max-onboarding", "Easy"]
            )

            # Should fail because small file won't get A grade
            assert result.exit_code == 2

    def test_ci_command_json_includes_ci_section(self) -> None:
        """Test ci command --json output includes CI section."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result = runner.invoke(
                cli, ["ci", str(root), "--no-git", "--fail-under", "C", "--max-risk", "Medium", "--json"]
            )

            assert result.exit_code in (0, 2)  # Could pass or fail depending on scoring
            output_data = json.loads(result.output)

            # Check CI section exists
            assert "ci" in output_data
            ci_data = output_data["ci"]

            # Check CI section structure
            assert "passed" in ci_data
            assert "thresholds" in ci_data
            assert "actual" in ci_data
            assert "failures" in ci_data

            # Check thresholds are recorded
            assert "min_grade" in ci_data["thresholds"]
            assert "max_risk" in ci_data["thresholds"]

            # Check actual values are recorded
            assert "grade" in ci_data["actual"]
            assert "risk_level" in ci_data["actual"]
            assert "onboarding_difficulty" in ci_data["actual"]

    def test_ci_command_json_failure_messages(self) -> None:
        """Test ci command --json failure messages when thresholds violated."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n")

            runner = CliRunner()
            result = runner.invoke(cli, ["ci", str(root), "--no-git", "--fail-under", "A", "--json"])

            assert result.exit_code == 2
            output_data = json.loads(result.output)

            ci_data = output_data["ci"]
            assert ci_data["passed"] is False
            assert len(ci_data["failures"]) > 0

            # Should have at least one failure message about grade
            failures_str = " ".join(ci_data["failures"]).lower()
            assert "grade" in failures_str
