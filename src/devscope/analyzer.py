"""Core analysis engine for devscope."""

import time
from collections import defaultdict
from pathlib import Path
from typing import Optional

try:
    import git

    HAS_GIT = True
except ImportError:
    HAS_GIT = False

from devscope.analyzers.complexity import ComplexityAnalyzer
from devscope.analyzers.dependencies import DependencyDetector
from devscope.analyzers.git_intel import GitIntelligence
from devscope.analyzers.hotspots import HotspotDetector
from devscope.analyzers.scoring import ScoringEngine
from devscope.analyzers.tests import TestDetector
from devscope.models import AnalysisResult
from devscope.utils import get_gitignore_matcher, is_binary_file


class CodebaseAnalyzer:
    """Analyzes codebases and generates intelligence reports."""

    # File extensions to analyze
    LANGUAGE_MAP = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".jsx": "JavaScript",
        ".tsx": "TypeScript",
        ".java": "Java",
        ".c": "C",
        ".cpp": "C++",
        ".cc": "C++",
        ".cxx": "C++",
        ".h": "C/C++",
        ".hpp": "C++",
        ".cs": "C#",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".php": "PHP",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".scala": "Scala",
        ".sh": "Shell",
        ".bash": "Shell",
        ".zsh": "Shell",
        ".sql": "SQL",
        ".html": "HTML",
        ".css": "CSS",
        ".scss": "SCSS",
        ".sass": "Sass",
        ".less": "Less",
        ".md": "Markdown",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".xml": "XML",
        ".toml": "TOML",
        ".ini": "INI",
        ".vue": "Vue",
        ".r": "R",
        ".m": "MATLAB",
        ".pl": "Perl",
        ".lua": "Lua",
        ".dart": "Dart",
    }

    # Directories to skip
    SKIP_DIRS = {
        ".git",
        ".svn",
        ".hg",
        ".bzr",
        "node_modules",
        "venv",
        "env",
        ".env",
        "dist",
        "build",
        "target",
        "out",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        ".eggs",
        "*.egg-info",
        "vendor",
        "bower_components",
        ".vscode",
        ".idea",
        ".vs",
    }

    def __init__(self, root_path: Path, detect_git: bool = True, enable_intelligence: bool = True):
        """Initialize the analyzer.

        Args:
            root_path: Root directory to analyze
            detect_git: Whether to detect and use git repository info
            enable_intelligence: Whether to run extended intelligence analysis
        """
        self.root_path = root_path
        self.detect_git = detect_git
        self.enable_intelligence = enable_intelligence
        self.repo_name: Optional[str] = None
        self.git_root: Optional[Path] = None

        if detect_git and HAS_GIT:
            self._detect_git_repo()

        # Set up gitignore matcher
        self.gitignore_matcher = get_gitignore_matcher(self.git_root or self.root_path)

    def _detect_git_repo(self) -> None:
        """Detect git repository and extract info."""
        try:
            repo = git.Repo(self.root_path, search_parent_directories=True)
            self.git_root = Path(repo.working_dir)

            # Try to get repo name from remote URL or directory name
            try:
                remote_url = repo.remotes.origin.url
                # Extract repo name from URL (handles github.com/user/repo.git format)
                self.repo_name = remote_url.rstrip("/").rstrip(".git").split("/")[-1]
            except (AttributeError, IndexError):
                self.repo_name = self.git_root.name

        except (git.InvalidGitRepositoryError, git.GitCommandError):
            # Not a git repository
            self.repo_name = self.root_path.name

    def _should_skip_path(self, path: Path) -> bool:
        """Determine if a path should be skipped.

        Args:
            path: Path to check

        Returns:
            True if path should be skipped
        """
        # Check if any part matches skip dirs
        for part in path.parts:
            if part in self.SKIP_DIRS or part.startswith("."):
                return True

        # Check gitignore
        if self.gitignore_matcher:
            try:
                rel_path = path.relative_to(self.git_root or self.root_path)
                if self.gitignore_matcher.match_file(str(rel_path)):
                    return True
            except (ValueError, AttributeError):
                pass

        return False

    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file.

        Args:
            file_path: Path to file

        Returns:
            Number of lines, or 0 if file cannot be read
        """
        # Skip binary files
        if is_binary_file(file_path):
            return 0

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                return sum(1 for _ in f)
        except (OSError, UnicodeDecodeError):
            return 0

    def analyze(self) -> AnalysisResult:
        """Analyze the codebase and return results.

        Returns:
            AnalysisResult containing analysis data
        """
        start_time = time.time()

        # Counters
        total_files = 0
        total_lines = 0

        # Extended analysis tracking
        all_files: list[Path] = []
        file_line_counts: dict[Path, int] = {}
        extension_counts: dict[str, int] = defaultdict(int)
        dir_file_counts: dict[str, int] = defaultdict(int)

        # Walk the directory tree
        for item in self.root_path.rglob("*"):
            if item.is_file():
                # Skip if path should be ignored
                if self._should_skip_path(item):
                    continue

                # Count file
                total_files += 1
                all_files.append(item)

                # Count lines
                lines = self._count_lines(item)
                total_lines += lines

                # Track for extended analysis
                if lines > 0:
                    file_line_counts[item] = lines

                # Track extension
                if item.suffix:
                    extension_counts[item.suffix.lower()] += 1

                # Track directory
                try:
                    rel_dir = item.parent.relative_to(self.root_path)
                    dir_name = str(rel_dir) if str(rel_dir) != "." else "(root)"
                    dir_file_counts[dir_name] += 1
                except ValueError:
                    pass

        # Calculate language percentages
        languages: dict[str, float] = {}
        if total_files > 0:
            for ext, count in extension_counts.items():
                lang = self.LANGUAGE_MAP.get(ext, f"*{ext}")
                percentage = (count / total_files) * 100
                if lang in languages:
                    languages[lang] += percentage
                else:
                    languages[lang] = percentage

        # Get largest directories
        largest_dirs = sorted(dir_file_counts.items(), key=lambda x: x[1], reverse=True)

        scan_time = time.time() - start_time

        # Base result (backward compatible)
        result = AnalysisResult(
            repo_name=self.repo_name or self.root_path.name,
            total_files=total_files,
            total_lines=total_lines,
            languages=languages,
            largest_dirs=largest_dirs,
            scan_time=scan_time,
        )

        # Extended intelligence analysis
        if self.enable_intelligence:
            result = self._run_intelligence_analysis(result, all_files, file_line_counts)

        return result

    def _run_intelligence_analysis(
        self,
        base_result: AnalysisResult,
        all_files: list[Path],
        file_line_counts: dict[Path, int],
    ) -> AnalysisResult:
        """Run extended intelligence analysis.

        Args:
            base_result: Base analysis result
            all_files: List of all analyzed files
            file_line_counts: Map of files to line counts

        Returns:
            Enhanced AnalysisResult with intelligence data
        """
        # Complexity analysis
        complexity_analyzer = ComplexityAnalyzer(self.root_path)
        complexity = complexity_analyzer.analyze(all_files)

        # Test detection
        test_detector = TestDetector(self.root_path)
        test_metrics = test_detector.detect(all_files)
        test_files = test_detector.get_test_files(all_files)

        # Hotspot detection
        hotspot_detector = HotspotDetector(self.root_path)
        hotspots = hotspot_detector.detect(file_line_counts, test_files)

        # Dependency detection
        dependency_detector = DependencyDetector(self.root_path)
        dependencies = dependency_detector.detect_all()

        # Git intelligence
        git_intel = GitIntelligence(self.root_path)
        git_metrics = git_intel.analyze()

        # Calculate health score
        scoring_engine = ScoringEngine()
        health_score = scoring_engine.calculate_health_score(
            complexity=complexity,
            test_metrics=test_metrics,
            git_metrics=git_metrics,
            hotspots=hotspots,
            total_files=base_result.total_files,
            total_lines=base_result.total_lines,
        )

        # Update result with intelligence data
        base_result.complexity = complexity
        base_result.test_metrics = test_metrics
        base_result.hotspots = hotspots
        base_result.dependencies = dependencies
        base_result.git_metrics = git_metrics
        base_result.health_score = health_score

        return base_result
