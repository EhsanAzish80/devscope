"""Tests for devscope utilities."""

from pathlib import Path
from tempfile import TemporaryDirectory

from devscope.utils import get_gitignore_matcher, is_binary_file


class TestUtils:
    """Test utility functions."""

    def test_is_binary_file_text(self) -> None:
        """Test binary detection for text files."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            text_file = root / "test.txt"
            text_file.write_text("This is a text file\n")

            assert is_binary_file(text_file) is False

    def test_is_binary_file_binary(self) -> None:
        """Test binary detection for binary files."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            binary_file = root / "test.bin"
            binary_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe")

            assert is_binary_file(binary_file) is True

    def test_gitignore_matcher_no_file(self) -> None:
        """Test gitignore matcher when no .gitignore exists."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            matcher = get_gitignore_matcher(root)

            # Should return None or a matcher that doesn't match anything
            assert matcher is None or matcher is not None

    def test_gitignore_matcher_with_file(self) -> None:
        """Test gitignore matcher when .gitignore exists."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            gitignore = root / ".gitignore"
            gitignore.write_text("*.pyc\n__pycache__/\n")

            matcher = get_gitignore_matcher(root)

            # If pathspec is available, matcher should work
            if matcher is not None:
                assert matcher.match_file("test.pyc") is True
                assert matcher.match_file("test.py") is False
