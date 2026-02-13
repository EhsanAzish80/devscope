"""Scoring system for code health assessment."""

from devscope.models import (
    CodeHealthScore,
    ComplexityMetrics,
    GitMetrics,
    OnboardingDifficulty,
    RiskHotspot,
    RiskLevel,
    TestMetrics,
)


class ScoringEngine:
    """Calculates code health scores using heuristic-based analysis.

    Scoring is deterministic and based on observable metrics:
    - Complexity signals
    - Test coverage
    - Git activity
    - Risk hotspots
    - Code organization
    """

    # Score weights (sum to 1.0)
    WEIGHT_COMPLEXITY = 0.25
    WEIGHT_TESTS = 0.30
    WEIGHT_GIT_ACTIVITY = 0.15
    WEIGHT_HOTSPOTS = 0.20
    WEIGHT_STRUCTURE = 0.10

    def calculate_health_score(
        self,
        complexity: ComplexityMetrics,
        test_metrics: TestMetrics,
        git_metrics: GitMetrics,
        hotspots: list[RiskHotspot],
        total_files: int,
        total_lines: int,
    ) -> CodeHealthScore:
        """Calculate overall code health score.

        Args:
            complexity: Complexity metrics
            test_metrics: Test coverage metrics
            git_metrics: Git repository metrics
            hotspots: Detected risk hotspots
            total_files: Total number of files
            total_lines: Total lines of code

        Returns:
            CodeHealthScore with grades and classifications
        """
        # Calculate component scores (0-100)
        complexity_score = self._score_complexity(complexity, total_files)
        test_score = self._score_tests(test_metrics)
        git_score = self._score_git_activity(git_metrics)
        hotspot_score = self._score_hotspots(hotspots, total_files)
        structure_score = self._score_structure(total_files, total_lines)

        # Combine scores
        overall_score = (
            self.WEIGHT_COMPLEXITY * complexity_score
            + self.WEIGHT_TESTS * test_score
            + self.WEIGHT_GIT_ACTIVITY * git_score
            + self.WEIGHT_HOTSPOTS * hotspot_score
            + self.WEIGHT_STRUCTURE * structure_score
        )

        # Calculate grade (A-F)
        grade = self._score_to_grade(overall_score)

        # Calculate risk level
        risk_level = self._calculate_risk_level(hotspots, test_metrics)

        # Calculate onboarding difficulty
        onboarding = self._calculate_onboarding_difficulty(
            complexity, total_files, test_metrics, git_metrics
        )

        return CodeHealthScore(
            maintainability_grade=grade,
            risk_level=risk_level,
            onboarding_difficulty=onboarding,
            score_breakdown={
                "complexity": round(complexity_score, 1),
                "tests": round(test_score, 1),
                "git_activity": round(git_score, 1),
                "hotspots": round(hotspot_score, 1),
                "structure": round(structure_score, 1),
                "overall": round(overall_score, 1),
            },
        )

    def _score_complexity(self, complexity: ComplexityMetrics, total_files: int) -> float:
        """Score complexity metrics.

        Args:
            complexity: Complexity metrics
            total_files: Total number of files

        Returns:
            Score from 0-100 (higher is better)
        """
        score = 100.0

        # Penalize large average file size
        # Ideal: < 500 lines, concerning: > 1000 lines
        avg_size = complexity.avg_file_size
        if avg_size > 50_000:  # ~1000 lines at 50 bytes/line
            score -= 20
        elif avg_size > 25_000:  # ~500 lines
            score -= 10

        # Penalize deep nesting
        if complexity.deep_nesting_warning:
            score -= 15

        # Penalize very deep structures
        if complexity.max_directory_depth > 8:
            score -= 15
        elif complexity.max_directory_depth > 6:
            score -= 10

        # Bonus for moderate complexity (well-organized)
        if 2 <= complexity.max_directory_depth <= 4:
            score += 5

        return max(0, min(100, score))

    def _score_tests(self, test_metrics: TestMetrics) -> float:
        """Score test coverage.

        Args:
            test_metrics: Test metrics

        Returns:
            Score from 0-100
        """
        if not test_metrics.has_tests:
            return 0.0

        # Base score for having tests
        score = 40.0

        # Score based on test ratio
        ratio = test_metrics.test_ratio

        if ratio >= 0.5:  # 1:2 or better (ideal)
            score += 60
        elif ratio >= 0.3:  # 1:3
            score += 45
        elif ratio >= 0.2:  # 1:5
            score += 30
        elif ratio >= 0.1:  # 1:10
            score += 15
        else:
            score += 5

        return min(100, score)

    def _score_git_activity(self, git_metrics: GitMetrics) -> float:
        """Score git activity and health.

        Args:
            git_metrics: Git metrics

        Returns:
            Score from 0-100
        """
        if not git_metrics.is_git_repo:
            return 50.0  # Neutral score

        score = 100.0

        # Penalize low commit count (suggests new/unmaintained project)
        if git_metrics.commit_count < 10:
            score -= 30
        elif git_metrics.commit_count < 50:
            score -= 15

        # Penalize single contributor (bus factor)
        if git_metrics.contributor_count == 1:
            score -= 20
        elif git_metrics.contributor_count == 2:
            score -= 10

        # Penalize stale repos
        if git_metrics.days_since_last_commit is not None:
            days = git_metrics.days_since_last_commit
            if days > 365:  # > 1 year
                score -= 30
            elif days > 180:  # > 6 months
                score -= 20
            elif days > 90:  # > 3 months
                score -= 10

        return max(0, min(100, score))

    def _score_hotspots(self, hotspots: list[RiskHotspot], total_files: int) -> float:
        """Score based on risk hotspots.

        Args:
            hotspots: List of risk hotspots
            total_files: Total number of files

        Returns:
            Score from 0-100
        """
        if total_files == 0:
            return 100.0

        score = 100.0

        # Penalize number of hotspots
        hotspot_ratio = len(hotspots) / max(1, total_files)

        if hotspot_ratio > 0.2:  # > 20% of files are hotspots
            score -= 40
        elif hotspot_ratio > 0.1:  # > 10%
            score -= 25
        elif hotspot_ratio > 0.05:  # > 5%
            score -= 15

        # Penalize severity of hotspots
        if hotspots:
            avg_risk = sum(h.risk_score for h in hotspots) / len(hotspots)
            if avg_risk > 70:
                score -= 20
            elif avg_risk > 50:
                score -= 10

        return max(0, min(100, score))

    def _score_structure(self, total_files: int, total_lines: int) -> float:
        """Score project structure.

        Args:
            total_files: Total number of files
            total_lines: Total lines of code

        Returns:
            Score from 0-100
        """
        score = 100.0

        # Check for reasonable file/line ratio
        if total_files > 0:
            avg_lines_per_file = total_lines / total_files

            # Ideal: 100-500 lines per file
            if avg_lines_per_file > 1000:
                score -= 20
            elif avg_lines_per_file > 500:
                score -= 10
            elif avg_lines_per_file < 50:
                score -= 10  # Too fragmented

        # Bonus for moderate-sized projects (sweet spot)
        if 10 <= total_files <= 1000:
            score += 5

        return max(0, min(100, score))

    def _score_to_grade(self, score: float) -> str:
        """Convert a score to a letter grade.

        Args:
            score: Score from 0-100

        Returns:
            Letter grade (A-F)
        """
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _calculate_risk_level(
        self, hotspots: list[RiskHotspot], test_metrics: TestMetrics
    ) -> RiskLevel:
        """Calculate overall risk level.

        Args:
            hotspots: List of risk hotspots
            test_metrics: Test metrics

        Returns:
            Risk level classification
        """
        risk_score = 0

        # Risk from hotspots
        if hotspots:
            high_risk_count = sum(1 for h in hotspots if h.risk_score > 70)
            if high_risk_count >= 3:
                risk_score += 30
            elif high_risk_count >= 1:
                risk_score += 20
            elif len(hotspots) >= 5:
                risk_score += 10

        # Risk from lack of tests
        if not test_metrics.has_tests:
            risk_score += 40
        elif test_metrics.test_ratio < 0.1:
            risk_score += 20

        # Classify
        if risk_score >= 50:
            return RiskLevel.HIGH
        elif risk_score >= 25:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _calculate_onboarding_difficulty(
        self,
        complexity: ComplexityMetrics,
        total_files: int,
        test_metrics: TestMetrics,
        git_metrics: GitMetrics,
    ) -> OnboardingDifficulty:
        """Calculate onboarding difficulty.

        Args:
            complexity: Complexity metrics
            total_files: Total number of files
            test_metrics: Test metrics
            git_metrics: Git metrics

        Returns:
            Onboarding difficulty classification
        """
        difficulty_score = 0

        # Large codebase is harder to onboard
        if total_files > 500:
            difficulty_score += 30
        elif total_files > 200:
            difficulty_score += 15

        # Deep nesting makes navigation harder
        if complexity.deep_nesting_warning:
            difficulty_score += 20

        # No tests means harder to understand
        if not test_metrics.has_tests:
            difficulty_score += 25
        elif test_metrics.test_ratio < 0.1:
            difficulty_score += 10

        # Low activity suggests outdated/stale docs
        if git_metrics.is_git_repo and git_metrics.days_since_last_commit:
            if git_metrics.days_since_last_commit > 365:
                difficulty_score += 15

        # Classify
        if difficulty_score >= 50:
            return OnboardingDifficulty.HARD
        elif difficulty_score >= 25:
            return OnboardingDifficulty.MODERATE
        else:
            return OnboardingDifficulty.EASY
