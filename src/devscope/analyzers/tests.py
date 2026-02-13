"""Test detection using heuristics and naming patterns."""

from pathlib import Path

from devscope.models import TestMetrics


class TestDetector:
    """Detects test files and calculates test coverage metrics."""

    # Common test directory names
    TEST_DIRS = {
        "test",
        "tests",
        "__tests__",
        "spec",
        "specs",
        "testing",
        "test_unit",
        "test_integration",
    }

    # Test file patterns (prefix or contains)
    TEST_PATTERNS = {
        "test_",
        "_test",
        "test.",
        ".test.",
        "spec.",
        ".spec.",
        "_spec",
    }

    # Test file extensions
    TEST_EXTENSIONS = {
        "_test.py",
        "_test.js",
        "_test.ts",
        ".test.js",
        ".test.ts",
        ".test.jsx",
        ".test.tsx",
        ".spec.js",
        ".spec.ts",
        ".spec.jsx",
        ".spec.tsx",
        "_spec.rb",
        "_test.go",
        "Test.java",
        "Tests.java",
        "Test.kt",
        "Tests.kt",
        "Test.swift",
    }

    def __init__(self, root_path: Path):
        """Initialize test detector.

        Args:
            root_path: Root directory of the project
        """
        self.root_path = root_path

    def detect(self, all_files: list[Path]) -> TestMetrics:
        """Detect test files and calculate metrics.

        Args:
            all_files: List of all files in the project

        Returns:
            TestMetrics with test coverage information
        """
        test_files: set[Path] = set()
        source_files: set[Path] = set()

        for file_path in all_files:
            try:
                rel_path = file_path.relative_to(self.root_path)
                path_str = str(rel_path).lower()
                file_name = file_path.name.lower()

                # Check if it's a test file
                if self._is_test_file(rel_path, file_name, path_str):
                    test_files.add(file_path)
                else:
                    # Consider it a source file if it's code
                    if self._is_source_file(file_path):
                        source_files.add(file_path)

            except ValueError:
                continue

        test_count = len(test_files)
        source_count = len(source_files)
        has_tests = test_count > 0
        test_ratio = test_count / source_count if source_count > 0 else 0.0

        return TestMetrics(
            has_tests=has_tests,
            test_file_count=test_count,
            source_file_count=source_count,
            test_ratio=round(test_ratio, 3),
        )

    def get_test_files(self, all_files: list[Path]) -> set[Path]:
        """Get the set of test files.

        Args:
            all_files: List of all files in the project

        Returns:
            Set of identified test files
        """
        test_files: set[Path] = set()

        for file_path in all_files:
            try:
                rel_path = file_path.relative_to(self.root_path)
                path_str = str(rel_path).lower()
                file_name = file_path.name.lower()

                if self._is_test_file(rel_path, file_name, path_str):
                    test_files.add(file_path)

            except ValueError:
                continue

        return test_files

    def _is_test_file(self, rel_path: Path, file_name: str, path_str: str) -> bool:
        """Check if a file is a test file.

        Args:
            rel_path: Relative path to the file
            file_name: Lowercase file name
            path_str: Lowercase full path string

        Returns:
            True if the file is identified as a test file
        """
        # Check if in a test directory
        for part in rel_path.parts:
            if part.lower() in self.TEST_DIRS:
                return True

        # Check file name patterns
        for pattern in self.TEST_PATTERNS:
            if pattern in file_name:
                return True

        # Check specific extensions
        for ext in self.TEST_EXTENSIONS:
            if file_name.endswith(ext.lower()):
                return True

        # Special cases
        if "test" in path_str and ("/" in path_str or "\\" in path_str):
            # Contains "test" in path
            parts = [p.lower() for p in rel_path.parts]
            if any("test" in p for p in parts):
                return True

        return False

    def _is_source_file(self, file_path: Path) -> bool:
        """Check if a file is a source code file.

        Args:
            file_path: Path to check

        Returns:
            True if the file is identified as source code
        """
        # List of common source code extensions
        source_extensions = {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".kt",
            ".scala",
            ".rb",
            ".php",
            ".go",
            ".rs",
            ".c",
            ".cpp",
            ".cc",
            ".cxx",
            ".h",
            ".hpp",
            ".cs",
            ".swift",
            ".m",
            ".mm",
            ".dart",
            ".lua",
            ".pl",
            ".r",
            ".vue",
        }

        return file_path.suffix.lower() in source_extensions
