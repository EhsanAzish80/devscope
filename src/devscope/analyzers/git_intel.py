"""Extended git intelligence for repository metrics."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import git

    HAS_GIT = True
except ImportError:
    HAS_GIT = False

from devscope.models import GitMetrics


class GitIntelligence:
    """Provides extended git repository intelligence."""

    def __init__(self, root_path: Path):
        """Initialize git intelligence.

        Args:
            root_path: Root directory of the project
        """
        self.root_path = root_path
        self.repo: Optional[object] = None
        self._initialize_repo()

    def _initialize_repo(self) -> None:
        """Initialize the git repository if available."""
        if not HAS_GIT:
            return

        try:
            self.repo = git.Repo(self.root_path, search_parent_directories=True)
        except (git.InvalidGitRepositoryError, git.GitCommandError):
            self.repo = None

    def analyze(self) -> GitMetrics:
        """Analyze git repository metrics.

        Returns:
            GitMetrics with repository information
        """
        if not HAS_GIT or self.repo is None:
            return GitMetrics(
                commit_count=0,
                contributor_count=0,
                days_since_last_commit=None,
                is_git_repo=False,
            )

        try:
            # Get commit count
            commit_count = self._get_commit_count()

            # Get contributor count
            contributor_count = self._get_contributor_count()

            # Get days since last commit
            days_since_last = self._get_days_since_last_commit()

            return GitMetrics(
                commit_count=commit_count,
                contributor_count=contributor_count,
                days_since_last_commit=days_since_last,
                is_git_repo=True,
            )

        except (git.GitCommandError, AttributeError, ValueError):
            return GitMetrics(
                commit_count=0,
                contributor_count=0,
                days_since_last_commit=None,
                is_git_repo=True,
            )

    def _get_commit_count(self) -> int:
        """Get the total number of commits.

        Returns:
            Number of commits
        """
        if self.repo is None:
            return 0

        try:
            # Count commits in the current branch
            return sum(1 for _ in self.repo.iter_commits())
        except (git.GitCommandError, AttributeError, ValueError):
            return 0

    def _get_contributor_count(self) -> int:
        """Get the number of unique contributors.

        Returns:
            Number of contributors
        """
        if self.repo is None:
            return 0

        try:
            # Get unique authors
            authors: set[str] = set()
            for commit in self.repo.iter_commits():
                if commit.author and commit.author.email:
                    authors.add(commit.author.email)

            return len(authors)
        except (git.GitCommandError, AttributeError, ValueError):
            return 0

    def _get_days_since_last_commit(self) -> Optional[int]:
        """Get the number of days since the last commit.

        Returns:
            Days since last commit, or None if unavailable
        """
        if self.repo is None:
            return None

        try:
            # Get the most recent commit
            last_commit = next(self.repo.iter_commits(), None)
            if last_commit is None:
                return None

            # Calculate days since last commit
            committed_date = datetime.fromtimestamp(last_commit.committed_date, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            delta = now - committed_date

            return delta.days

        except (git.GitCommandError, AttributeError, ValueError, StopIteration):
            return None
