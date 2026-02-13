"""Tests for devscope analyzer."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from devscope.analyzer import CodebaseAnalyzer
from devscope.models import AnalysisResult


class TestCodebaseAnalyzer:
    """Test the CodebaseAnalyzer class."""

    def test_analyzer_initialization(self) -> None:
        """Test analyzer initialization."""
        with TemporaryDirectory() as tmpdir:
            analyzer = CodebaseAnalyzer(Path(tmpdir), detect_git=False)
            assert analyzer.root_path == Path(tmpdir)
            assert analyzer.detect_git is False

    def test_language_detection(self) -> None:
        """Test language detection from file extensions."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create test files
            (root / "test.py").write_text("print('hello')\n")
            (root / "test.js").write_text("console.log('hello');\n")
            (root / "test.txt").write_text("some text\n")

            analyzer = CodebaseAnalyzer(root, detect_git=False)
            result = analyzer.analyze()

            assert "Python" in result.languages
            assert "JavaScript" in result.languages
            assert result.total_files >= 2

    def test_line_counting(self) -> None:
        """Test line counting functionality."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create a file with known line count
            test_file = root / "test.py"
            test_file.write_text("line1\nline2\nline3\n")

            analyzer = CodebaseAnalyzer(root, detect_git=False)
            result = analyzer.analyze()

            assert result.total_lines >= 3
            assert result.total_files >= 1

    def test_skip_directories(self) -> None:
        """Test that certain directories are skipped."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create files in directories that should be skipped
            node_modules = root / "node_modules"
            node_modules.mkdir()
            (node_modules / "test.js").write_text("test")

            # Create file that should be counted
            (root / "main.py").write_text("print('hello')\n")

            analyzer = CodebaseAnalyzer(root, detect_git=False)
            result = analyzer.analyze()

            # Should only count main.py
            assert result.total_files == 1

    def test_directory_analysis(self) -> None:
        """Test directory file counting."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create nested structure
            subdir = root / "src"
            subdir.mkdir()
            (subdir / "file1.py").write_text("test")
            (subdir / "file2.py").write_text("test")
            (root / "main.py").write_text("test")

            analyzer = CodebaseAnalyzer(root, detect_git=False)
            result = analyzer.analyze()

            assert len(result.largest_dirs) > 0
            assert result.total_files == 3


class TestAnalysisResult:
    """Test the AnalysisResult model."""

    def test_valid_result(self) -> None:
        """Test creating a valid result."""
        result = AnalysisResult(
            repo_name="test",
            total_files=10,
            total_lines=100,
            languages={"Python": 50.0, "JavaScript": 50.0},
            largest_dirs=[("src", 5), ("tests", 5)],
            scan_time=1.5,
        )

        assert result.repo_name == "test"
        assert result.total_files == 10
        assert result.total_lines == 100

    def test_invalid_negative_files(self) -> None:
        """Test that negative file count raises error."""
        with pytest.raises(ValueError, match="total_files must be non-negative"):
            AnalysisResult(
                repo_name="test",
                total_files=-1,
                total_lines=100,
                languages={},
                largest_dirs=[],
                scan_time=1.0,
            )

    def test_invalid_negative_lines(self) -> None:
        """Test that negative line count raises error."""
        with pytest.raises(ValueError, match="total_lines must be non-negative"):
            AnalysisResult(
                repo_name="test",
                total_files=10,
                total_lines=-1,
                languages={},
                largest_dirs=[],
                scan_time=1.0,
            )
