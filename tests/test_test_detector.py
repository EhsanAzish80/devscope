"""Tests for test detector."""

from pathlib import Path
from tempfile import TemporaryDirectory

from devscope.analyzers.tests import TestDetector


class TestTestDetector:
    """Test the TestDetector class."""

    def test_initialization(self) -> None:
        """Test detector initialization."""
        with TemporaryDirectory() as tmpdir:
            detector = TestDetector(Path(tmpdir))
            assert detector.root_path == Path(tmpdir)

    def test_no_tests(self) -> None:
        """Test detection when no tests exist."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create only source files
            (root / "main.py").write_text("print('hello')")
            (root / "utils.py").write_text("def util(): pass")

            files = list(root.glob("*.py"))
            detector = TestDetector(root)
            result = detector.detect(files)

            assert result.has_tests is False
            assert result.test_file_count == 0
            assert result.source_file_count == 2
            assert result.test_ratio == 0.0

    def test_test_directory_detection(self) -> None:
        """Test detection of test directories."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create test directory
            test_dir = root / "tests"
            test_dir.mkdir()
            (test_dir / "test_main.py").write_text("def test_main(): pass")
            (test_dir / "test_utils.py").write_text("def test_utils(): pass")

            # Create source files
            (root / "main.py").write_text("print('hello')")

            files = list(root.rglob("*.py"))
            detector = TestDetector(root)
            result = detector.detect(files)

            assert result.has_tests is True
            assert result.test_file_count == 2
            assert result.source_file_count == 1

    def test_test_file_pattern_detection(self) -> None:
        """Test detection of test file patterns."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create files with test patterns
            (root / "test_module.py").write_text("def test_func(): pass")
            (root / "module_test.py").write_text("def test_func(): pass")
            (root / "module.test.js").write_text("test('works', () => {});")

            # Create source files
            (root / "module.py").write_text("def func(): pass")
            (root / "app.js").write_text("console.log('hi');")

            files = list(root.glob("*"))
            detector = TestDetector(root)
            result = detector.detect(files)

            assert result.has_tests is True
            assert result.test_file_count == 3
            assert result.source_file_count == 2

    def test_test_ratio_calculation(self) -> None:
        """Test test ratio calculation."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create 2 test files
            (root / "test_a.py").write_text("test")
            (root / "test_b.py").write_text("test")

            # Create 4 source files
            (root / "src1.py").write_text("code")
            (root / "src2.py").write_text("code")
            (root / "src3.py").write_text("code")
            (root / "src4.py").write_text("code")

            files = list(root.glob("*.py"))
            detector = TestDetector(root)
            result = detector.detect(files)

            # Ratio should be 2/4 = 0.5
            assert abs(result.test_ratio - 0.5) < 0.01

    def test_get_test_files(self) -> None:
        """Test getting the set of test files."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create test and source files
            test_file = root / "test_main.py"
            source_file = root / "main.py"

            test_file.write_text("test")
            source_file.write_text("code")

            files = [test_file, source_file]
            detector = TestDetector(root)
            test_files = detector.get_test_files(files)

            assert test_file in test_files
            assert source_file not in test_files

    def test_various_test_extensions(self) -> None:
        """Test detection of various test file extensions."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create test files with different extensions
            (root / "test.spec.js").write_text("test")
            (root / "test.test.ts").write_text("test")
            (root / "test_spec.rb").write_text("test")

            files = list(root.glob("*"))
            detector = TestDetector(root)
            result = detector.detect(files)

            assert result.has_tests is True
            assert result.test_file_count >= 2  # At least JS and TS

    def test_is_source_file(self) -> None:
        """Test source file identification."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            detector = TestDetector(root)

            assert detector._is_source_file(Path("test.py")) is True
            assert detector._is_source_file(Path("test.js")) is True
            assert detector._is_source_file(Path("test.java")) is True
            assert detector._is_source_file(Path("test.txt")) is False
            assert detector._is_source_file(Path("test.md")) is False
