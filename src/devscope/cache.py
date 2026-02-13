"""Caching layer for devscope to speed up repeated scans."""

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cached metadata and analysis results for a single file."""

    file_path: str
    size_bytes: int
    mtime: float
    lines: int
    language: Optional[str]

    def is_valid(self, actual_size: int, actual_mtime: float) -> bool:
        """Check if cache entry is still valid for the file."""
        return self.size_bytes == actual_size and self.mtime == actual_mtime


@dataclass
class CacheStats:
    """Statistics about cache performance."""

    enabled: bool
    hits: int = 0
    misses: int = 0
    total_files: int = 0
    time_saved_estimate: float = 0.0  # seconds

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate as percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.hits / self.total_files) * 100.0


class CacheManager:
    """Manages file metadata caching for faster repeated scans."""

    def __init__(self, cache_dir: Path, enabled: bool = True):
        """Initialize cache manager.

        Args:
            cache_dir: Directory to store cache files
            enabled: Whether caching is enabled
        """
        self.cache_dir = cache_dir
        self.enabled = enabled
        self.cache_file = cache_dir / "file_metadata.json"
        self._cache: dict[str, CacheEntry] = {}
        self.stats = CacheStats(enabled=enabled)

        if enabled:
            self._load_cache()

    def _load_cache(self) -> None:
        """Load cache from disk. Ignores corrupt cache."""
        if not self.cache_file.exists():
            return

        try:
            with open(self.cache_file, encoding="utf-8") as f:
                data = json.load(f)

            # Validate structure
            if not isinstance(data, dict):
                logger.warning("Cache file has invalid structure, ignoring")
                return

            # Load entries
            for key, entry_dict in data.items():
                try:
                    self._cache[key] = CacheEntry(**entry_dict)
                except (TypeError, ValueError) as e:
                    logger.debug(f"Skipping invalid cache entry for {key}: {e}")

            logger.debug(f"Loaded {len(self._cache)} entries from cache")

        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load cache, will rebuild: {e}")
            self._cache = {}

    def _save_cache(self) -> None:
        """Save cache to disk."""
        if not self.enabled:
            return

        try:
            # Ensure cache directory exists
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            # Write cache file
            cache_data = {key: asdict(entry) for key, entry in self._cache.items()}

            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, sort_keys=True)

            logger.debug(f"Saved {len(self._cache)} entries to cache")

        except OSError as e:
            logger.warning(f"Failed to save cache: {e}")

    def get(self, file_path: Path) -> Optional[CacheEntry]:
        """Get cached entry for a file if valid.

        Args:
            file_path: Path to the file

        Returns:
            CacheEntry if valid, None otherwise
        """
        if not self.enabled:
            return None

        self.stats.total_files += 1

        try:
            stat = file_path.stat()
            key = str(file_path)

            entry = self._cache.get(key)
            if entry and entry.is_valid(stat.st_size, stat.st_mtime):
                self.stats.hits += 1
                # Estimate time saved (rough heuristic: ~0.1ms per file)
                self.stats.time_saved_estimate += 0.0001
                logger.debug(f"Cache hit: {file_path}")
                return entry

            self.stats.misses += 1
            return None

        except OSError:
            self.stats.misses += 1
            return None

    def set(self, file_path: Path, lines: int, language: Optional[str]) -> None:
        """Store analysis results in cache.

        Args:
            file_path: Path to the file
            lines: Number of lines in file
            language: Detected language (None if unknown)
        """
        if not self.enabled:
            return

        try:
            stat = file_path.stat()
            key = str(file_path)

            entry = CacheEntry(
                file_path=key,
                size_bytes=stat.st_size,
                mtime=stat.st_mtime,
                lines=lines,
                language=language,
            )

            self._cache[key] = entry
            logger.debug(f"Cached: {file_path}")

        except OSError as e:
            logger.debug(f"Failed to cache {file_path}: {e}")

    def clear(self) -> None:
        """Clear all cached data."""
        self._cache = {}
        if self.cache_file.exists():
            try:
                self.cache_file.unlink()
                logger.info("Cache cleared")
            except OSError as e:
                logger.warning(f"Failed to delete cache file: {e}")

    def save(self) -> None:
        """Persist cache to disk."""
        self._save_cache()

    def get_cache_dir(self, repo_root: Optional[Path] = None) -> Path:
        """Get appropriate cache directory.

        Args:
            repo_root: Repository root path (if in a git repo)

        Returns:
            Path to cache directory
        """
        # Prefer repo-local cache
        if repo_root:
            cache_dir = repo_root / ".devscope_cache"
            try:
                cache_dir.mkdir(parents=True, exist_ok=True)
                return cache_dir
            except OSError:
                pass

        # Fallback to user cache directory
        import platformdirs

        cache_dir = Path(platformdirs.user_cache_dir("devscope"))
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
