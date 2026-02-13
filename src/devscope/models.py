"""Data models for devscope."""

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional

from devscope import __version__


class RiskLevel(Enum):
    """Risk level classification."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

    def __lt__(self, other: "RiskLevel") -> bool:
        """Compare risk levels (LOW is best, HIGH is worst)."""
        if not isinstance(other, RiskLevel):
            return NotImplemented
        order = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2}
        return order[self] < order[other]

    def __le__(self, other: "RiskLevel") -> bool:
        """Compare risk levels (less than or equal)."""
        return self == other or self < other

    def __gt__(self, other: "RiskLevel") -> bool:
        """Compare risk levels (greater than)."""
        if not isinstance(other, RiskLevel):
            return NotImplemented
        order = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2}
        return order[self] > order[other]

    def __ge__(self, other: "RiskLevel") -> bool:
        """Compare risk levels (greater than or equal)."""
        return self == other or self > other


class OnboardingDifficulty(Enum):
    """Onboarding difficulty classification."""

    EASY = "Easy"
    MODERATE = "Moderate"
    HARD = "Hard"

    def __lt__(self, other: "OnboardingDifficulty") -> bool:
        """Compare onboarding difficulty (EASY is best, HARD is worst)."""
        if not isinstance(other, OnboardingDifficulty):
            return NotImplemented
        order = {OnboardingDifficulty.EASY: 0, OnboardingDifficulty.MODERATE: 1, OnboardingDifficulty.HARD: 2}
        return order[self] < order[other]

    def __le__(self, other: "OnboardingDifficulty") -> bool:
        """Compare onboarding difficulty (less than or equal)."""
        return self == other or self < other

    def __gt__(self, other: "OnboardingDifficulty") -> bool:
        """Compare onboarding difficulty (greater than)."""
        if not isinstance(other, OnboardingDifficulty):
            return NotImplemented
        order = {OnboardingDifficulty.EASY: 0, OnboardingDifficulty.MODERATE: 1, OnboardingDifficulty.HARD: 2}
        return order[self] > order[other]

    def __ge__(self, other: "OnboardingDifficulty") -> bool:
        """Compare onboarding difficulty (greater than or equal)."""
        return self == other or self > other


class Grade(Enum):
    """Code health grade classification."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"

    def __lt__(self, other: "Grade") -> bool:
        """Compare grades (A is best, F is worst)."""
        if not isinstance(other, Grade):
            return NotImplemented
        order = {Grade.A: 0, Grade.B: 1, Grade.C: 2, Grade.D: 3, Grade.E: 4, Grade.F: 5}
        return order[self] < order[other]

    def __le__(self, other: "Grade") -> bool:
        """Compare grades (less than or equal)."""
        return self == other or self < other

    def __gt__(self, other: "Grade") -> bool:
        """Compare grades (greater than)."""
        if not isinstance(other, Grade):
            return NotImplemented
        order = {Grade.A: 0, Grade.B: 1, Grade.C: 2, Grade.D: 3, Grade.E: 4, Grade.F: 5}
        return order[self] > order[other]

    def __ge__(self, other: "Grade") -> bool:
        """Compare grades (greater than or equal)."""
        return self == other or self > other

    @classmethod
    def from_string(cls, grade_str: str) -> "Grade":
        """Convert string to Grade enum."""
        grade_str = grade_str.upper()
        for grade in cls:
            if grade.value == grade_str:
                return grade
        raise ValueError(f"Invalid grade: {grade_str}")


@dataclass
class ComplexityMetrics:
    """Code complexity metrics."""

    avg_file_size: float
    max_directory_depth: int
    largest_files: list[tuple[str, int]]  # (file_path, size_in_bytes)
    deep_nesting_warning: bool


@dataclass
class RiskHotspot:
    """A code hotspot with elevated risk."""

    file_path: str
    risk_score: float
    lines_of_code: int
    depth: int
    has_nearby_tests: bool
    reason: str


@dataclass
class DependencyInfo:
    """Dependency information from manifest files."""

    ecosystem: str  # e.g., "Python", "JavaScript", "Rust"
    manifest_file: str
    dependency_count: int
    dependencies: list[str]  # top-level dependency names


@dataclass
class TestMetrics:
    """Test coverage metrics."""

    has_tests: bool
    test_file_count: int
    source_file_count: int
    test_ratio: float  # test files / source files


@dataclass
class GitMetrics:
    """Git repository metrics."""

    commit_count: int
    contributor_count: int
    days_since_last_commit: Optional[int]
    is_git_repo: bool


@dataclass
class CodeHealthScore:
    """Overall code health scoring."""

    maintainability_grade: str  # A-F
    risk_level: RiskLevel
    onboarding_difficulty: OnboardingDifficulty
    score_breakdown: dict[str, float]  # component -> score


@dataclass
class AnalysisResult:
    """Result of codebase analysis.

    Backward-compatible: all new fields have defaults.
    """

    # Original fields (Phase 1)
    repo_name: Optional[str]
    total_files: int
    total_lines: int
    languages: dict[str, float]  # language -> percentage
    largest_dirs: list[tuple[str, int]]  # (dir_name, file_count)
    scan_time: float

    # Extended fields (Phase 2) - all optional for backward compatibility
    complexity: Optional[ComplexityMetrics] = None
    hotspots: list[RiskHotspot] = field(default_factory=list)
    dependencies: list[DependencyInfo] = field(default_factory=list)
    test_metrics: Optional[TestMetrics] = None
    git_metrics: Optional[GitMetrics] = None
    health_score: Optional[CodeHealthScore] = None

    def __post_init__(self) -> None:
        """Validate the analysis result."""
        if self.total_files < 0:
            raise ValueError("total_files must be non-negative")
        if self.total_lines < 0:
            raise ValueError("total_lines must be non-negative")
        if self.scan_time < 0:
            raise ValueError("scan_time must be non-negative")

    def to_json_dict(self) -> dict[str, Any]:
        """Convert analysis result to a JSON-serializable dictionary.

        Returns a stable, deterministic dict with schema versioning.
        Enum values are converted to strings, tuples to lists.
        """
        # Convert dataclass to dict
        data = asdict(self)

        # Process largest_dirs tuples -> list of dicts
        data["largest_dirs"] = [
            {"directory": dir_name, "file_count": count} for dir_name, count in self.largest_dirs
        ]

        # Process complexity metrics
        if self.complexity:
            data["complexity"]["largest_files"] = [
                {"file_path": path, "size_bytes": size}
                for path, size in self.complexity.largest_files
            ]

        # Process health score enums and nested dict
        if self.health_score:
            data["health_score"]["risk_level"] = self.health_score.risk_level.value
            data["health_score"]["onboarding_difficulty"] = (
                self.health_score.onboarding_difficulty.value
            )

        # Add metadata
        result = {
            "schema_version": "1.0",
            "devscope_version": __version__,
            "analysis": data,
        }

        return result

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string with stable formatting.

        Args:
            indent: Number of spaces for indentation (default: 2)

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_json_dict(), indent=indent, sort_keys=True)


@dataclass
class CIThresholds:
    """CI threshold configuration."""

    min_grade: Optional[Grade] = None
    max_risk: Optional[RiskLevel] = None
    max_onboarding: Optional[OnboardingDifficulty] = None


@dataclass
class CIResult:
    """Result of CI threshold evaluation."""

    passed: bool
    thresholds: CIThresholds
    actual_grade: Optional[str] = None
    actual_risk: Optional[str] = None
    actual_onboarding: Optional[str] = None
    failures: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert CI result to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "passed": self.passed,
            "thresholds": {},
            "actual": {},
            "failures": self.failures,
        }

        # Add threshold values if set
        if self.thresholds.min_grade:
            result["thresholds"]["min_grade"] = self.thresholds.min_grade.value
        if self.thresholds.max_risk:
            result["thresholds"]["max_risk"] = self.thresholds.max_risk.value
        if self.thresholds.max_onboarding:
            result["thresholds"]["max_onboarding"] = self.thresholds.max_onboarding.value

        # Add actual values
        if self.actual_grade:
            result["actual"]["grade"] = self.actual_grade
        if self.actual_risk:
            result["actual"]["risk_level"] = self.actual_risk
        if self.actual_onboarding:
            result["actual"]["onboarding_difficulty"] = self.actual_onboarding

        return result
