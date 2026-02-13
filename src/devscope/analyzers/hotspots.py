"""Hotspot detection for identifying high-risk code areas."""

from pathlib import Path

from devscope.models import RiskHotspot


class HotspotDetector:
    """Detects code hotspots using LOC, depth, and test proximity."""

    # Risk scoring weights
    WEIGHT_LOC = 0.4
    WEIGHT_DEPTH = 0.3
    WEIGHT_NO_TESTS = 0.3

    # Thresholds
    HIGH_LOC_THRESHOLD = 500
    MEDIUM_LOC_THRESHOLD = 200
    HIGH_DEPTH_THRESHOLD = 4

    def __init__(self, root_path: Path):
        """Initialize hotspot detector.

        Args:
            root_path: Root directory of the project
        """
        self.root_path = root_path

    def detect(
        self,
        file_line_counts: dict[Path, int],
        test_files: set[Path],
        max_results: int = 10,
    ) -> list[RiskHotspot]:
        """Detect code hotspots.

        Args:
            file_line_counts: Map of file paths to line counts
            test_files: Set of identified test files
            max_results: Maximum number of hotspots to return

        Returns:
            List of risk hotspots, sorted by risk score
        """
        hotspots: list[RiskHotspot] = []

        for file_path, loc in file_line_counts.items():
            # Skip test files themselves
            if file_path in test_files:
                continue

            # Calculate risk components
            depth = self._calculate_depth(file_path)
            has_nearby_tests = self._has_nearby_tests(file_path, test_files)

            # Calculate risk score (0-100)
            risk_score = self._calculate_risk_score(loc, depth, has_nearby_tests)

            # Generate explanation
            reason = self._generate_risk_reason(loc, depth, has_nearby_tests)

            # Only include files with meaningful risk
            if risk_score > 30:  # Threshold for inclusion
                try:
                    rel_path = str(file_path.relative_to(self.root_path))
                except ValueError:
                    rel_path = str(file_path)

                hotspots.append(
                    RiskHotspot(
                        file_path=rel_path,
                        risk_score=risk_score,
                        lines_of_code=loc,
                        depth=depth,
                        has_nearby_tests=has_nearby_tests,
                        reason=reason,
                    )
                )

        # Sort by risk score and return top results
        hotspots.sort(key=lambda x: x.risk_score, reverse=True)
        return hotspots[:max_results]

    def _calculate_depth(self, file_path: Path) -> int:
        """Calculate directory depth of a file.

        Args:
            file_path: Path to calculate depth for

        Returns:
            Directory depth level
        """
        try:
            rel_path = file_path.relative_to(self.root_path)
            return len(rel_path.parts) - 1  # Subtract file itself
        except ValueError:
            return 0

    def _has_nearby_tests(self, file_path: Path, test_files: set[Path]) -> bool:
        """Check if file has tests nearby.

        Args:
            file_path: File to check
            test_files: Set of test files

        Returns:
            True if tests found nearby
        """
        # Check same directory
        file_dir = file_path.parent
        for test_file in test_files:
            if test_file.parent == file_dir:
                return True

        # Check common test directory patterns
        try:
            rel_path = file_path.relative_to(self.root_path)
            path_parts = rel_path.parts

            # Look for tests/ or __tests__/ as sibling or parent
            for i, _part in enumerate(path_parts[:-1]):
                test_dir = self.root_path / Path(*path_parts[:i]) / "tests"
                if test_dir.exists() and any(tf.is_relative_to(test_dir) for tf in test_files):
                    return True

                test_dir = self.root_path / Path(*path_parts[:i]) / "__tests__"
                if test_dir.exists() and any(tf.is_relative_to(test_dir) for tf in test_files):
                    return True

        except (ValueError, AttributeError):
            pass

        return False

    def _calculate_risk_score(self, loc: int, depth: int, has_nearby_tests: bool) -> float:
        """Calculate risk score for a file.

        Args:
            loc: Lines of code
            depth: Directory depth
            has_nearby_tests: Whether tests are nearby

        Returns:
            Risk score (0-100)
        """
        # LOC component (0-100)
        if loc > self.HIGH_LOC_THRESHOLD:
            loc_score = 100.0
        elif loc > self.MEDIUM_LOC_THRESHOLD:
            loc_score = 50 + (loc - self.MEDIUM_LOC_THRESHOLD) * 50 / (
                self.HIGH_LOC_THRESHOLD - self.MEDIUM_LOC_THRESHOLD
            )
        else:
            loc_score = loc * 50 / self.MEDIUM_LOC_THRESHOLD

        # Depth component (0-100)
        depth_score = float(min(100, (depth / self.HIGH_DEPTH_THRESHOLD) * 100))

        # Test proximity component (0 or 100)
        test_score = 0 if has_nearby_tests else 100

        # Weighted combination
        risk_score = (
            self.WEIGHT_LOC * loc_score
            + self.WEIGHT_DEPTH * depth_score
            + self.WEIGHT_NO_TESTS * test_score
        )

        return round(risk_score, 1)

    def _generate_risk_reason(self, loc: int, depth: int, has_nearby_tests: bool) -> str:
        """Generate human-readable risk explanation.

        Args:
            loc: Lines of code
            depth: Directory depth
            has_nearby_tests: Whether tests are nearby

        Returns:
            Risk explanation string
        """
        reasons = []

        if loc > self.HIGH_LOC_THRESHOLD:
            reasons.append(f"Very large file ({loc} LOC)")
        elif loc > self.MEDIUM_LOC_THRESHOLD:
            reasons.append(f"Large file ({loc} LOC)")

        if depth >= self.HIGH_DEPTH_THRESHOLD:
            reasons.append(f"Deeply nested (depth {depth})")
        elif depth >= 3:
            reasons.append(f"Nested structure (depth {depth})")

        if not has_nearby_tests:
            reasons.append("No nearby tests")

        return ", ".join(reasons) if reasons else "Potential complexity"
