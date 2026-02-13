"""Utility functions for devscope."""

from pathlib import Path
from typing import Any

try:
    import pathspec

    HAS_PATHSPEC = True
except ImportError:
    HAS_PATHSPEC = False


def get_gitignore_matcher(root: Path) -> Any:
    """Create a gitignore pattern matcher.

    Args:
        root: Root directory to search for .gitignore

    Returns:
        PathSpec matcher or None if not available
    """
    if not HAS_PATHSPEC:
        return None

    gitignore_path = root / ".gitignore"
    if not gitignore_path.exists():
        return None

    try:
        with open(gitignore_path, encoding="utf-8") as f:
            patterns = f.read()
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns.splitlines())
    except (OSError, ValueError):
        return None


def is_binary_file(file_path: Path, sample_size: int = 8192) -> bool:
    """Check if a file is binary.

    Args:
        file_path: Path to file
        sample_size: Number of bytes to sample

    Returns:
        True if file appears to be binary
    """
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(sample_size)

        # Check for null bytes
        if b"\x00" in chunk:
            return True

        # Check text/binary ratio
        text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
        non_text = sum(1 for byte in chunk if byte not in text_chars)

        return non_text / len(chunk) > 0.3 if chunk else False

    except OSError:
        return True
