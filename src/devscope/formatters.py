"""Formatters for devscope output - badges, markdown, summaries."""

import os
from typing import Any, Optional
from urllib.parse import quote

from devscope.models import AnalysisResult, OnboardingDifficulty, RiskLevel


def is_ci_environment() -> bool:
    """Detect if running in a CI environment.

    Returns:
        True if running in CI, False otherwise
    """
    ci_indicators = [
        "CI",
        "GITHUB_ACTIONS",
        "GITLAB_CI",
        "CIRCLECI",
        "TRAVIS",
        "JENKINS_HOME",
        "BUILDKITE",
    ]
    return any(os.environ.get(var) for var in ci_indicators)


def get_grade_color(grade: str) -> str:
    """Get badge color for maintainability grade.

    Args:
        grade: Letter grade (A-F)

    Returns:
        shields.io color name
    """
    color_map = {
        "A": "brightgreen",
        "B": "green",
        "C": "yellowgreen",
        "D": "yellow",
        "E": "orange",
        "F": "red",
    }
    return color_map.get(grade.upper(), "lightgrey")


def get_risk_color(risk: RiskLevel) -> str:
    """Get badge color for risk level.

    Args:
        risk: Risk level enum

    Returns:
        shields.io color name
    """
    color_map = {
        RiskLevel.LOW: "green",
        RiskLevel.MEDIUM: "orange",
        RiskLevel.HIGH: "red",
    }
    return color_map.get(risk, "lightgrey")


def get_onboarding_color(difficulty: OnboardingDifficulty) -> str:
    """Get badge color for onboarding difficulty.

    Args:
        difficulty: Onboarding difficulty enum

    Returns:
        shields.io color name
    """
    color_map = {
        OnboardingDifficulty.EASY: "blue",
        OnboardingDifficulty.MODERATE: "yellow",
        OnboardingDifficulty.HARD: "red",
    }
    return color_map.get(difficulty, "lightgrey")


def get_cache_color(hit_rate: float) -> str:
    """Get badge color for cache hit rate.

    Args:
        hit_rate: Cache hit rate percentage (0-100)

    Returns:
        shields.io color name
    """
    if hit_rate >= 90:
        return "success"
    elif hit_rate >= 70:
        return "green"
    elif hit_rate >= 50:
        return "yellow"
    else:
        return "orange"


def generate_badge_url(label: str, message: str, color: str) -> str:
    """Generate shields.io badge URL.

    Args:
        label: Badge label (left side)
        message: Badge message (right side)
        color: Badge color

    Returns:
        Full shields.io URL
    """
    label_encoded = quote(label)
    message_encoded = quote(message)
    return f"https://img.shields.io/badge/{label_encoded}-{message_encoded}-{color}"


def generate_badges(result: AnalysisResult) -> dict[str, str]:
    """Generate all badge URLs for an analysis result.

    Args:
        result: Analysis result with health score

    Returns:
        Dictionary mapping badge names to URLs
    """
    badges = {}

    if result.health_score:
        # Maintainability badge
        grade = result.health_score.maintainability_grade
        color = get_grade_color(grade)
        badges["maintainability"] = generate_badge_url("maintainability", grade, color)

        # Risk badge
        risk_value = result.health_score.risk_level.value
        risk_color = get_risk_color(result.health_score.risk_level)
        badges["risk"] = generate_badge_url("risk", risk_value, risk_color)

        # Onboarding badge
        onboarding_value = result.health_score.onboarding_difficulty.value
        onboarding_color = get_onboarding_color(result.health_score.onboarding_difficulty)
        badges["onboarding"] = generate_badge_url("onboarding", onboarding_value, onboarding_color)

    # Cache badge (if available)
    if result.cache_stats and result.cache_stats.get("enabled"):
        hit_rate = result.cache_stats.get("hit_rate", 0)

        # In CI with low cache hit, show "cold" instead of "0%"
        if is_ci_environment() and hit_rate < 10:
            cache_message = "cold"
            cache_color = "lightgrey"
        else:
            cache_message = f"{hit_rate:.0f}%"
            cache_color = get_cache_color(hit_rate)

        badges["cache"] = generate_badge_url("cache", cache_message, cache_color)

    return badges


def format_languages(languages: dict[str, float], max_langs: int = 3) -> str:
    """Format language breakdown as a compact string.

    Args:
        languages: Language name to percentage mapping
        max_langs: Maximum number of languages to show

    Returns:
        Formatted string like "Python (45%) · JS (33%) · TS (12%)"
    """
    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
    top_langs = sorted_langs[:max_langs]

    parts = [f"{name} ({pct:.0f}%)" for name, pct in top_langs]
    return " · ".join(parts)


def format_dependencies(result: AnalysisResult) -> str:
    """Format dependency ecosystems as a compact string.

    Args:
        result: Analysis result

    Returns:
        Formatted string like "Python · Node · Ruby"
    """
    if not result.dependencies:
        return "None"

    ecosystems = sorted({dep.ecosystem for dep in result.dependencies})
    return " · ".join(ecosystems)


def format_days_since_commit(days: Optional[int]) -> str:
    """Format days since last commit.

    Args:
        days: Days since last commit (None if not a git repo)

    Returns:
        Human-readable string
    """
    if days is None:
        return "N/A"
    elif days == 0:
        return "today"
    elif days == 1:
        return "1 day ago"
    else:
        return f"{days} days ago"


def generate_markdown_summary(result: AnalysisResult, include_badges: bool = False) -> str:
    """Generate full markdown summary.

    Args:
        result: Analysis result
        include_badges: Whether to include shields.io badges

    Returns:
        Markdown-formatted summary
    """
    lines = ["## 🔍 Devscope Report\n"]

    # Badges (optional)
    if include_badges:
        badges = generate_badges(result)
        for badge_url in badges.values():
            lines.append(f"![Badge]({badge_url})")
        lines.append("")  # Blank line after badges

    # Repo intelligence block
    lines.append(f"**Repo:** {result.repo_name or 'unknown'}  ")
    lines.append(f"**Files:** {result.total_files:,}  ")
    lines.append(f"**Lines:** {result.total_lines:,}  ")

    if result.languages:
        lang_str = format_languages(result.languages)
        lines.append(f"**Languages:** {lang_str}\n")
    else:
        lines.append("")

    # Health metrics
    if result.health_score:
        grade = result.health_score.maintainability_grade
        overall_score = result.health_score.score_breakdown.get("overall", 0)
        lines.append(f"**Health:** {grade} ({overall_score:.1f})  ")
        lines.append(f"**Risk:** {result.health_score.risk_level.value}  ")
        lines.append(f"**Onboarding:** {result.health_score.onboarding_difficulty.value}  \n")

    # Test metrics
    if result.test_metrics:
        test_ratio = result.test_metrics.test_ratio
        lines.append(f"**Tests:** {test_ratio:.2f} ratio  ")

    # Dependencies
    if result.dependencies:
        deps_str = format_dependencies(result)
        lines.append(f"**Dependencies:** {deps_str}  ")

    # Git metrics
    if result.git_metrics and result.git_metrics.is_git_repo:
        days = result.git_metrics.days_since_last_commit
        days_str = format_days_since_commit(days)
        lines.append(f"**Last commit:** {days_str}  \n")
    else:
        lines.append("")

    # Top hotspot
    if result.hotspots:
        hotspot = result.hotspots[0]
        lines.append(f"**Top hotspot:** {hotspot.file_path} ({hotspot.lines_of_code} LOC, {hotspot.reason})\n")

    # Performance line
    cache_info = ""
    if result.cache_stats and result.cache_stats.get("enabled"):
        hit_rate = result.cache_stats.get("hit_rate", 0)
        if hit_rate > 0:
            cache_info = f" (cache: {hit_rate:.0f}% hit rate)"

    lines.append(f"⚡ Scan time: {result.scan_time:.2f}s{cache_info}")

    return "\n".join(lines)


def generate_compact_summary(result: AnalysisResult) -> str:
    """Generate compact one-line summary.

    Args:
        result: Analysis result

    Returns:
        Single-line summary string
    """
    parts = ["Devscope:"]

    if result.health_score:
        grade = result.health_score.maintainability_grade
        risk = result.health_score.risk_level.value
        onboarding = result.health_score.onboarding_difficulty.value
        parts.append(f"{grade} · {risk} risk · {onboarding} onboarding")

    if result.test_metrics:
        test_ratio = result.test_metrics.test_ratio
        parts.append(f"· {test_ratio:.2f} tests")

    parts.append(f"· {result.scan_time:.2f}s ⚡")

    return " ".join(parts)


def generate_health_block(result: AnalysisResult, include_timing: bool = False) -> str:
    """Generate deterministic health block for README injection.
    
    This produces a stable, consistent markdown block that can be injected
    into README files. Output is deterministic - same inputs produce identical
    output, preventing unnecessary commits.
    
    Args:
        result: Analysis result with health metrics
        include_timing: Include scan time (makes output non-deterministic)
        
    Returns:
        Markdown health block for README embedding
    """
    lines = ["## 🔍 Devscope Report\n"]
    
    # Badges - exclude cache badge (non-deterministic)
    # Only include stable metrics: maintainability, risk, onboarding
    badges = generate_badges(result)
    badge_order = ["maintainability", "risk", "onboarding"]  # Exclude cache
    for badge_name in badge_order:
        if badge_name in badges:
            lines.append(f"![Badge]({badges[badge_name]})")
    lines.append("")  # Blank line after badges
    
    # Repository metadata - consistent formatting
    lines.append(f"**Repo:** {result.repo_name or 'Unknown'}  ")
    lines.append(f"**Files:** {result.total_files}  ")
    lines.append(f"**Lines:** {result.total_lines}  ")
    
    # Languages - sorted for determinism
    if result.languages:
        lang_str = format_languages(result.languages)
        lines.append(f"**Languages:** {lang_str}\n")
    else:
        lines.append("")
    
    # Health metrics
    if result.health_score:
        grade = result.health_score.maintainability_grade
        overall_score = result.health_score.score_breakdown.get("overall", 0)
        lines.append(f"**Health:** {grade} ({overall_score:.1f})  ")
        lines.append(f"**Risk:** {result.health_score.risk_level.value}  ")
        lines.append(f"**Onboarding:** {result.health_score.onboarding_difficulty.value}  \n")
    
    # Test metrics
    if result.test_metrics:
        test_ratio = result.test_metrics.test_ratio
        lines.append(f"**Tests:** {test_ratio:.2f} ratio  ")
    
    # Git metrics
    if result.git_metrics and result.git_metrics.is_git_repo:
        days = result.git_metrics.days_since_last_commit
        days_str = format_days_since_commit(days)
        lines.append(f"**Last commit:** {days_str}  \n")
    else:
        lines.append("")
    
    # Top hotspot (if any)
    if result.hotspots:
        hotspot = result.hotspots[0]
        lines.append(f"**Top hotspot:** {hotspot.file_path} ({hotspot.lines_of_code} LOC, {hotspot.reason})\n")
    
    # Performance - only if explicitly requested (non-deterministic)
    if include_timing:
        lines.append(f"⚡ Scan time: {result.scan_time:.2f}s\n")
    
    return "\n".join(lines)


def generate_json_summary(result: AnalysisResult) -> dict[str, Any]:
    """Generate JSON summary for bots and integrations.

    Args:
        result: Analysis result

    Returns:
        Dictionary with summary data
    """
    summary: dict[str, Any] = {
        "repo": result.repo_name,
        "total_files": result.total_files,
        "total_lines": result.total_lines,
        "languages": result.languages,
        "scan_time": result.scan_time,
    }

    if result.health_score:
        summary["health"] = {
            "grade": result.health_score.maintainability_grade,
            "score": result.health_score.score_breakdown.get("overall", 0.0),
            "risk": result.health_score.risk_level.value,
            "onboarding": result.health_score.onboarding_difficulty.value,
        }

    if result.test_metrics:
        summary["test_ratio"] = result.test_metrics.test_ratio

    if result.hotspots:
        hotspot = result.hotspots[0]
        summary["top_hotspot"] = {
            "file_path": hotspot.file_path,
            "lines_of_code": hotspot.lines_of_code,
            "reason": hotspot.reason,
            "risk_score": hotspot.risk_score,
        }

    if result.dependencies:
        summary["dependencies"] = [dep.ecosystem for dep in result.dependencies]

    if result.git_metrics:
        summary["git"] = {
            "is_repo": result.git_metrics.is_git_repo,
            "days_since_commit": result.git_metrics.days_since_last_commit,
        }

    if result.cache_stats:
        summary["cache"] = result.cache_stats

    # Add badge URLs
    summary["badges"] = generate_badges(result)

    return summary
