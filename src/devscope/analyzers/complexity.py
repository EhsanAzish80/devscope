"""Complexity analysis based on filesystem metrics."""

from pathlib import Path

from devscope.models import ComplexityMetrics


class ComplexityAnalyzer:
    """Analyzes code complexity using filesystem-based heuristics."""

    # Threshold for deep nesting warning
    DEEP_NESTING_THRESHOLD = 6

    # Threshold for considering a file "large" (in bytes)
    LARGE_FILE_THRESHOLD = 50_000

    def __init__(self, root_path: Path):
        """Initialize complexity analyzer.

        Args:
            root_path: Root directory to analyze
        """
        self.root_path = root_path

    def _calculate_depth(self, path: Path) -> int:
        """Calculate the depth of a path relative to root.

        Args:
            path: Path to calculate depth for

        Returns:
            Depth level (0 for root)
        """
        try:
            rel_path = path.relative_to(self.root_path)
            return len(rel_path.parts) - 1 if str(rel_path) != "." else 0
        except ValueError:
            return 0

    def analyze(self, files: list[Path], skip_binary: bool = True) -> ComplexityMetrics:
        """Analyze complexity metrics.

        Args:
            files: List of files to analyze
            skip_binary: Whether to skip binary files

        Returns:
            ComplexityMetrics with analysis results
        """
        if not files:
            return ComplexityMetrics(
                avg_file_size=0.0,
                max_directory_depth=0,
                largest_files=[],
                deep_nesting_warning=False,
            )

        # Calculate file sizes
        file_sizes: list[tuple[str, int]] = []
        total_size = 0
        max_depth = 0

        for file_path in files:
            try:
                if not file_path.exists():
                    continue

                size = file_path.stat().st_size

                # Skip if binary and requested
                if skip_binary and self._is_likely_binary(file_path, size):
                    continue

                file_sizes.append((str(file_path.relative_to(self.root_path)), size))
                total_size += size

                # Track depth
                depth = self._calculate_depth(file_path.parent)
                max_depth = max(max_depth, depth)

            except (OSError, ValueError):
                continue

        # Calculate metrics
        avg_file_size = total_size / len(file_sizes) if file_sizes else 0.0

        # Get top 10 largest files
        largest_files = sorted(file_sizes, key=lambda x: x[1], reverse=True)[:10]

        # Check for deep nesting
        deep_nesting = max_depth >= self.DEEP_NESTING_THRESHOLD

        return ComplexityMetrics(
            avg_file_size=avg_file_size,
            max_directory_depth=max_depth,
            largest_files=largest_files,
            deep_nesting_warning=deep_nesting,
        )

    def _is_likely_binary(self, file_path: Path, size: int) -> bool:
        """Quick heuristic to detect binary files.

        Args:
            file_path: Path to check
            size: File size in bytes

        Returns:
            True if likely binary
        """
        # Common binary extensions
        binary_extensions = {
            ".pyc",
            ".pyo",
            ".so",
            ".dll",
            ".dylib",
            ".exe",
            ".bin",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".pdf",
            ".zip",
            ".tar",
            ".gz",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
            ".ico",
        }

        if file_path.suffix.lower() in binary_extensions:
            return True

        # If very small, likely not worth checking
        if size == 0:
            return True

        # Quick byte check for null bytes
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(min(8192, size))
                if b"\x00" in chunk:
                    return True
        except OSError:
            return True

        return False
