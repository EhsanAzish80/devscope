"""Tests for caching functionality."""

import json
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from click.testing import CliRunner

from devscope.cache import CacheEntry, CacheManager, CacheStats
from devscope.cli import cli


class TestCacheEntry:
    """Test CacheEntry dataclass."""

    def test_cache_entry_creation(self) -> None:
        """Test creating a cache entry."""
        entry = CacheEntry(
            file_path="/path/to/file.py",
            size_bytes=1024,
            mtime=1234567890.0,
            lines=50,
            language="Python",
        )

        assert entry.file_path == "/path/to/file.py"
        assert entry.size_bytes == 1024
        assert entry.mtime == 1234567890.0
        assert entry.lines == 50
        assert entry.language == "Python"

    def test_cache_entry_is_valid(self) -> None:
        """Test cache entry validation."""
        entry = CacheEntry(
            file_path="/path/to/file.py",
            size_bytes=1024,
            mtime=1234567890.0,
            lines=50,
            language="Python",
        )

        # Same size and mtime - valid
        assert entry.is_valid(1024, 1234567890.0)

        # Different size - invalid
        assert not entry.is_valid(2048, 1234567890.0)

        # Different mtime - invalid
        assert not entry.is_valid(1024, 1234567891.0)

        # Both different - invalid
        assert not entry.is_valid(2048, 1234567891.0)


class TestCacheStats:
    """Test CacheStats dataclass."""

    def test_cache_stats_hit_rate(self) -> None:
        """Test cache hit rate calculation."""
        stats = CacheStats(enabled=True, hits=75, misses=25, total_files=100)
        assert stats.hit_rate == 75.0

        stats = CacheStats(enabled=True, hits=50, misses=50, total_files=100)
        assert stats.hit_rate == 50.0

        stats = CacheStats(enabled=True, hits=0, misses=100, total_files=100)
        assert stats.hit_rate == 0.0

        stats = CacheStats(enabled=True, hits=100, misses=0, total_files=100)
        assert stats.hit_rate == 100.0

    def test_cache_stats_zero_files(self) -> None:
        """Test cache hit rate with zero files."""
        stats = CacheStats(enabled=True, hits=0, misses=0, total_files=0)
        assert stats.hit_rate == 0.0


class TestCacheManager:
    """Test CacheManager class."""

    def test_cache_manager_initialization(self) -> None:
        """Test cache manager initialization."""
        with TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".cache"
            manager = CacheManager(cache_dir, enabled=True)

            assert manager.enabled
            assert manager.cache_dir == cache_dir
            assert manager.stats.enabled

    def test_cache_manager_disabled(self) -> None:
        """Test cache manager with caching disabled."""
        with TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".cache"
            manager = CacheManager(cache_dir, enabled=False)

            assert not manager.enabled
            assert not manager.stats.enabled

    def test_cache_set_and_get(self) -> None:
        """Test caching a file and retrieving it."""
        with TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".cache"
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("x = 1\n")

            manager = CacheManager(cache_dir, enabled=True)

            # First get - should be miss
            entry = manager.get(test_file)
            assert entry is None
            assert manager.stats.hits == 0
            assert manager.stats.misses == 1

            # Set cache
            manager.set(test_file, lines=1, language="Python")

            # Second get - should be hit
            entry = manager.get(test_file)
            assert entry is not None
            assert entry.lines == 1
            assert entry.language == "Python"
            assert manager.stats.hits == 1
            assert manager.stats.misses == 1

    def test_cache_invalidation_on_file_change(self) -> None:
        """Test cache invalidation when file is modified."""
        with TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".cache"
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("x = 1\n")

            manager = CacheManager(cache_dir, enabled=True)

            # Cache the file
            manager.set(test_file, lines=1, language="Python")
            entry = manager.get(test_file)
            assert entry is not None
            assert entry.lines == 1

            # Modify the file
            time.sleep(0.01)  # Ensure mtime changes
            test_file.write_text("x = 1\ny = 2\n")

            # Get should now be a miss (file changed)
            entry = manager.get(test_file)
            assert entry is None

    def test_cache_persistence(self) -> None:
        """Test cache persists across manager instances."""
        with TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".cache"
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("x = 1\n")

            # First manager - cache the file
            manager1 = CacheManager(cache_dir, enabled=True)
            manager1.set(test_file, lines=1, language="Python")
            manager1.save()

            # Second manager - should load from disk
            manager2 = CacheManager(cache_dir, enabled=True)
            entry = manager2.get(test_file)
            assert entry is not None
            assert entry.lines == 1
            assert entry.language == "Python"

    def test_cache_clear(self) -> None:
        """Test cache clearing."""
        with TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".cache"
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("x = 1\n")

            manager = CacheManager(cache_dir, enabled=True)

            # Cache the file
            manager.set(test_file, lines=1, language="Python")
            manager.save()
            assert manager.cache_file.exists()

            # Clear cache
            manager.clear()
            assert not manager.cache_file.exists()

            # Get should now be miss
            entry = manager.get(test_file)
            assert entry is None

    def test_cache_corrupt_file(self) -> None:
        """Test handling of corrupt cache file."""
        with TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".cache"
            cache_dir.mkdir()

            # Write invalid JSON
            cache_file = cache_dir / "file_metadata.json"
            cache_file.write_text("{ invalid json }")

            # Should not crash, just ignore corrupt cache
            manager = CacheManager(cache_dir, enabled=True)
            assert manager.enabled
            assert len(manager._cache) == 0

    def test_cache_disabled_operations(self) -> None:
        """Test cache operations when disabled."""
        with TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / ".cache"
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("x = 1\n")

            manager = CacheManager(cache_dir, enabled=False)

            # Set should do nothing
            manager.set(test_file, lines=1, language="Python")

            # Get should always return None
            entry = manager.get(test_file)
            assert entry is None

            # Save should do nothing
            manager.save()
            assert not manager.cache_file.exists()


class TestCLICacheIntegration:
    """Test cache integration with CLI commands."""

    def test_scan_with_cache_first_run(self) -> None:
        """Test scan command with cache on first run (all misses)."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result = runner.invoke(cli, ["scan", str(root), "--no-git", "--json"])

            assert result.exit_code == 0
            output_data = json.loads(result.output)

            cache_stats = output_data["analysis"]["cache_stats"]
            assert cache_stats["enabled"]
            assert cache_stats["hits"] == 0
            assert cache_stats["misses"] > 0
            assert cache_stats["hit_rate"] == 0.0

    def test_scan_with_cache_second_run(self) -> None:
        """Test scan command with cache on second run (all hits)."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()

            # First scan - populate cache
            result1 = runner.invoke(cli, ["scan", str(root), "--no-git", "--json"])
            assert result1.exit_code == 0

            # Second scan - use cache
            result2 = runner.invoke(cli, ["scan", str(root), "--no-git", "--json"])
            assert result2.exit_code == 0

            output_data = json.loads(result2.output)
            cache_stats = output_data["analysis"]["cache_stats"]

            assert cache_stats["enabled"]
            assert cache_stats["hits"] > 0
            assert cache_stats["misses"] == 0
            assert cache_stats["hit_rate"] == 100.0
            # Time saved estimate might be small (rounded to 3 decimals)
            assert cache_stats["time_saved_estimate"] >= 0

    def test_scan_with_no_cache_flag(self) -> None:
        """Test scan command with --no-cache flag."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()
            result = runner.invoke(cli, ["scan", str(root), "--no-git", "--no-cache", "--json"])

            assert result.exit_code == 0
            output_data = json.loads(result.output)

            # No cache stats when caching disabled
            assert output_data["analysis"]["cache_stats"] is None

    def test_scan_with_clear_cache_flag(self) -> None:
        """Test scan command with --clear-cache flag."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()

            # First scan - populate cache
            result1 = runner.invoke(cli, ["scan", str(root), "--no-git", "--json"])
            assert result1.exit_code == 0
            output1 = json.loads(result1.output)
            assert output1["analysis"]["cache_stats"]["hit_rate"] == 0.0

            # Second scan without clearing - should hit cache
            result2 = runner.invoke(cli, ["scan", str(root), "--no-git", "--json"])
            assert result2.exit_code == 0
            output2 = json.loads(result2.output)
            assert output2["analysis"]["cache_stats"]["hit_rate"] == 100.0

            # Third scan with cache clearing - should be misses again
            result3 = runner.invoke(cli, ["scan", str(root), "--no-git", "--clear-cache", "--json"])
            assert result3.exit_code == 0
            output3 = json.loads(result3.output)
            assert output3["analysis"]["cache_stats"]["hit_rate"] == 0.0

    def test_ci_command_with_cache(self) -> None:
        """Test ci command uses cache."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "test.py").write_text("x = 1\n" * 50)

            runner = CliRunner()

            # First run - populate cache
            result1 = runner.invoke(cli, ["ci", str(root), "--no-git", "--json"])
            assert result1.exit_code == 0
            output1 = json.loads(result1.output)
            assert output1["analysis"]["cache_stats"]["hit_rate"] == 0.0

            # Second run - use cache
            result2 = runner.invoke(cli, ["ci", str(root), "--no-git", "--json"])
            assert result2.exit_code == 0
            output2 = json.loads(result2.output)
            assert output2["analysis"]["cache_stats"]["hit_rate"] == 100.0

    def test_cache_invalidation_integration(self) -> None:
        """Test cache invalidation when files change."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            test_file = root / "test.py"
            test_file.write_text("x = 1\n")

            runner = CliRunner()

            # First scan
            result1 = runner.invoke(cli, ["scan", str(root), "--no-git", "--json"])
            assert result1.exit_code == 0
            output1 = json.loads(result1.output)
            assert output1["analysis"]["total_lines"] == 1

            # Modify file
            time.sleep(0.01)  # Ensure mtime changes
            test_file.write_text("x = 1\ny = 2\n")

            # Second scan - cache should invalidate
            result2 = runner.invoke(cli, ["scan", str(root), "--no-git", "--json"])
            assert result2.exit_code == 0
            output2 = json.loads(result2.output)
            assert output2["analysis"]["total_lines"] == 2
            # Should have at least one miss for the changed file
            assert output2["analysis"]["cache_stats"]["misses"] > 0
