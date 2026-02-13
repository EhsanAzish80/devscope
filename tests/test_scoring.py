"""Tests for scoring engine."""

from devscope.analyzers.scoring import ScoringEngine
from devscope.models import (
    ComplexityMetrics,
    GitMetrics,
    OnboardingDifficulty,
    RiskHotspot,
    RiskLevel,
    TestMetrics,
)


class TestScoringEngine:
    """Test the ScoringEngine class."""

    def test_perfect_score(self) -> None:
        """Test with ideal metrics."""
        engine = ScoringEngine()

        complexity = ComplexityMetrics(
            avg_file_size=15000,  # ~300 lines
            max_directory_depth=3,
            largest_files=[],
            deep_nesting_warning=False,
        )

        test_metrics = TestMetrics(
            has_tests=True, test_file_count=50, source_file_count=100, test_ratio=0.5
        )

        git_metrics = GitMetrics(
            commit_count=500,
            contributor_count=10,
            days_since_last_commit=5,
            is_git_repo=True,
        )

        hotspots: list[RiskHotspot] = []

        score = engine.calculate_health_score(
            complexity=complexity,
            test_metrics=test_metrics,
            git_metrics=git_metrics,
            hotspots=hotspots,
            total_files=100,
            total_lines=15000,
        )

        assert score.maintainability_grade in ["A", "B"]
        assert score.risk_level == RiskLevel.LOW
        assert score.onboarding_difficulty in [
            OnboardingDifficulty.EASY,
            OnboardingDifficulty.MODERATE,
        ]

    def test_poor_score(self) -> None:
        """Test with problematic metrics."""
        engine = ScoringEngine()

        complexity = ComplexityMetrics(
            avg_file_size=100000,  # Very large files
            max_directory_depth=10,  # Very deep
            largest_files=[],
            deep_nesting_warning=True,
        )

        test_metrics = TestMetrics(
            has_tests=False, test_file_count=0, source_file_count=200, test_ratio=0.0
        )

        git_metrics = GitMetrics(
            commit_count=5,
            contributor_count=1,
            days_since_last_commit=400,  # Stale
            is_git_repo=True,
        )

        hotspots = [
            RiskHotspot(
                file_path="big.py",
                risk_score=85.0,
                lines_of_code=2000,
                depth=5,
                has_nearby_tests=False,
                reason="Very large, no tests",
            )
            for _ in range(20)  # Many hotspots
        ]

        score = engine.calculate_health_score(
            complexity=complexity,
            test_metrics=test_metrics,
            git_metrics=git_metrics,
            hotspots=hotspots,
            total_files=100,
            total_lines=50000,
        )

        assert score.maintainability_grade in ["D", "F"]
        assert score.risk_level == RiskLevel.HIGH
        assert score.onboarding_difficulty == OnboardingDifficulty.HARD

    def test_score_to_grade_boundaries(self) -> None:
        """Test grade calculation boundaries."""
        engine = ScoringEngine()

        assert engine._score_to_grade(95) == "A"
        assert engine._score_to_grade(90) == "A"
        assert engine._score_to_grade(85) == "B"
        assert engine._score_to_grade(75) == "C"
        assert engine._score_to_grade(65) == "D"
        assert engine._score_to_grade(50) == "F"

    def test_complexity_scoring(self) -> None:
        """Test complexity component scoring."""
        engine = ScoringEngine()

        # Good complexity
        good = ComplexityMetrics(
            avg_file_size=20000,
            max_directory_depth=3,
            largest_files=[],
            deep_nesting_warning=False,
        )
        score1 = engine._score_complexity(good, 100)
        assert score1 > 85

        # Bad complexity
        bad = ComplexityMetrics(
            avg_file_size=80000,  # ~1600 lines
            max_directory_depth=10,
            largest_files=[],
            deep_nesting_warning=True,
        )
        score2 = engine._score_complexity(bad, 100)
        assert score2 < 70

    def test_test_scoring(self) -> None:
        """Test test coverage scoring."""
        engine = ScoringEngine()

        # No tests
        no_tests = TestMetrics(
            has_tests=False, test_file_count=0, source_file_count=100, test_ratio=0.0
        )
        assert engine._score_tests(no_tests) == 0.0

        # Good coverage
        good_tests = TestMetrics(
            has_tests=True, test_file_count=50, source_file_count=100, test_ratio=0.5
        )
        score = engine._score_tests(good_tests)
        assert score >= 90

        # Partial coverage
        partial_tests = TestMetrics(
            has_tests=True, test_file_count=20, source_file_count=100, test_ratio=0.2
        )
        score2 = engine._score_tests(partial_tests)
        assert 50 < score2 < 90

    def test_risk_level_calculation(self) -> None:
        """Test risk level calculation."""
        engine = ScoringEngine()

        # Low risk
        no_hotspots: list[RiskHotspot] = []
        good_tests = TestMetrics(
            has_tests=True, test_file_count=50, source_file_count=100, test_ratio=0.5
        )
        risk1 = engine._calculate_risk_level(no_hotspots, good_tests)
        assert risk1 == RiskLevel.LOW

        # High risk
        many_hotspots = [
            RiskHotspot(
                file_path=f"file{i}.py",
                risk_score=80.0,
                lines_of_code=1000,
                depth=3,
                has_nearby_tests=False,
                reason="Large",
            )
            for i in range(5)
        ]
        no_tests = TestMetrics(
            has_tests=False, test_file_count=0, source_file_count=100, test_ratio=0.0
        )
        risk2 = engine._calculate_risk_level(many_hotspots, no_tests)
        assert risk2 == RiskLevel.HIGH

    def test_onboarding_difficulty(self) -> None:
        """Test onboarding difficulty calculation."""
        engine = ScoringEngine()

        # Easy onboarding
        simple = ComplexityMetrics(
            avg_file_size=15000,
            max_directory_depth=2,
            largest_files=[],
            deep_nesting_warning=False,
        )
        good_tests = TestMetrics(
            has_tests=True, test_file_count=20, source_file_count=50, test_ratio=0.4
        )
        recent_git = GitMetrics(
            commit_count=100,
            contributor_count=3,
            days_since_last_commit=10,
            is_git_repo=True,
        )

        difficulty1 = engine._calculate_onboarding_difficulty(simple, 50, good_tests, recent_git)
        assert difficulty1 in [OnboardingDifficulty.EASY, OnboardingDifficulty.MODERATE]

        # Hard onboarding
        complex = ComplexityMetrics(
            avg_file_size=50000,
            max_directory_depth=10,
            largest_files=[],
            deep_nesting_warning=True,
        )
        no_tests = TestMetrics(
            has_tests=False, test_file_count=0, source_file_count=600, test_ratio=0.0
        )
        stale_git = GitMetrics(
            commit_count=10,
            contributor_count=1,
            days_since_last_commit=400,
            is_git_repo=True,
        )

        difficulty2 = engine._calculate_onboarding_difficulty(complex, 600, no_tests, stale_git)
        assert difficulty2 == OnboardingDifficulty.HARD

    def test_score_breakdown(self) -> None:
        """Test that score breakdown is complete."""
        engine = ScoringEngine()

        complexity = ComplexityMetrics(
            avg_file_size=20000,
            max_directory_depth=4,
            largest_files=[],
            deep_nesting_warning=False,
        )

        test_metrics = TestMetrics(
            has_tests=True, test_file_count=30, source_file_count=100, test_ratio=0.3
        )

        git_metrics = GitMetrics(
            commit_count=200,
            contributor_count=5,
            days_since_last_commit=20,
            is_git_repo=True,
        )

        score = engine.calculate_health_score(
            complexity=complexity,
            test_metrics=test_metrics,
            git_metrics=git_metrics,
            hotspots=[],
            total_files=100,
            total_lines=20000,
        )

        # Check all components exist
        assert "complexity" in score.score_breakdown
        assert "tests" in score.score_breakdown
        assert "git_activity" in score.score_breakdown
        assert "hotspots" in score.score_breakdown
        assert "structure" in score.score_breakdown
        assert "overall" in score.score_breakdown

        # All scores should be in valid range
        for _component, value in score.score_breakdown.items():
            assert 0 <= value <= 100
