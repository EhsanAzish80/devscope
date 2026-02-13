"""Tests for complexity analyzer."""

from pathlib import Path
from tempfile import TemporaryDirectory

from devscope.analyzers.complexity import ComplexityAnalyzer


class TestComplexityAnalyzer:
    """Test the ComplexityAnalyzer class."""

    def test_analyzer_initialization(self) -> None:
        """Test analyzer initialization."""
        with TemporaryDirectory() as tmpdir:
            analyzer = ComplexityAnalyzer(Path(tmpdir))
            assert analyzer.root_path == Path(tmpdir)

    def test_empty_filelist(self) -> None:
        """Test analysis with no files."""
        with TemporaryDirectory() as tmpdir:
            analyzer = ComplexityAnalyzer(Path(tmpdir))
            result = analyzer.analyze([])

            assert result.avg_file_size == 0.0
            assert result.max_directory_depth == 0
            assert len(result.largest_files) == 0
            assert result.deep_nesting_warning is False

    def test_average_file_size(self) -> None:
        """Test average file size calculation."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create files with known sizes
            (root / "small.txt").write_text("x" * 100)
            (root / "large.txt").write_text("x" * 1000)

            files = list(root.glob("*.txt"))
            analyzer = ComplexityAnalyzer(root)
            result = analyzer.analyze(files, skip_binary=False)

            # Average should be 550
            assert 500 <= result.avg_file_size <= 600

    def test_directory_depth(self) -> None:
        """Test directory depth calculation."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create nested structure
            deep_path = root / "a" / "b" / "c" / "d" / "e"
            deep_path.mkdir(parents=True)
            (deep_path / "deep.txt").write_text("deep file")

            files = list(root.rglob("*.txt"))
            analyzer = ComplexityAnalyzer(root)
            result = analyzer.analyze(files)

            assert result.max_directory_depth >= 4

    def test_deep_nesting_warning(self) -> None:
        """Test deep nesting warning."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create very deep structure
            deep_path = root / "a" / "b" / "c" / "d" / "e" / "f" / "g"
            deep_path.mkdir(parents=True)
            (deep_path / "file.txt").write_text("content")

            files = list(root.rglob("*.txt"))
            analyzer = ComplexityAnalyzer(root)
            result = analyzer.analyze(files)

            assert result.deep_nesting_warning is True

    def test_largest_files_tracking(self) -> None:
        """Test that largest files are tracked correctly."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create files of various sizes
            (root / "tiny.txt").write_text("x" * 10)
            (root / "small.txt").write_text("x" * 100)
            (root / "medium.txt").write_text("x" * 1000)
            (root / "large.txt").write_text("x" * 10000)

            files = list(root.glob("*.txt"))
            analyzer = ComplexityAnalyzer(root)
            result = analyzer.analyze(files, skip_binary=False)

            assert len(result.largest_files) > 0
            # Largest should be first
            assert result.largest_files[0][0] == "large.txt"
            assert result.largest_files[0][1] == 10000

    def test_binary_file_detection(self) -> None:
        """Test binary file detection."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create a binary file
            (root / "binary.bin").write_bytes(b"\x00\x01\x02\xff\xfe")
            # Create a text file
            (root / "text.txt").write_text("hello world")

            list(root.glob("*"))
            analyzer = ComplexityAnalyzer(root)

            # Binary file should be detected
            assert analyzer._is_likely_binary(root / "binary.bin", 5) is True
            assert analyzer._is_likely_binary(root / "text.txt", 11) is False
