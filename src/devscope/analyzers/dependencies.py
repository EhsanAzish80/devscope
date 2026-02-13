"""Dependency detection from various manifest files."""

import json
import re
from pathlib import Path
from typing import Optional

from devscope.models import DependencyInfo


class DependencyDetector:
    """Detects and parses dependencies from manifest files."""

    def __init__(self, root_path: Path):
        """Initialize dependency detector.

        Args:
            root_path: Root directory to search for manifests
        """
        self.root_path = root_path

    def detect_all(self) -> list[DependencyInfo]:
        """Detect all dependency manifests in the project.

        Returns:
            List of detected dependency information
        """
        dependencies: list[DependencyInfo] = []

        # Try each detector
        detectors = [
            self._detect_python_poetry,
            self._detect_python_requirements,
            self._detect_javascript,
            self._detect_rust,
            self._detect_go,
            self._detect_swift,
            self._detect_cocoapods,
        ]

        for detector in detectors:
            result = detector()
            if result:
                dependencies.append(result)

        return dependencies

    def _detect_python_poetry(self) -> Optional[DependencyInfo]:
        """Detect Python dependencies from pyproject.toml."""
        pyproject_path = self.root_path / "pyproject.toml"
        if not pyproject_path.exists():
            return None

        try:
            content = pyproject_path.read_text(encoding="utf-8")

            # Simple TOML parsing for dependencies section
            deps: list[str] = []
            in_deps_section = False

            for line in content.split("\n"):
                line = line.strip()

                if line.startswith("[project.dependencies]") or line.startswith(
                    "[tool.poetry.dependencies]"
                ):
                    in_deps_section = True
                    continue

                if in_deps_section:
                    if line.startswith("["):
                        break
                    if "=" in line or ":" in line:
                        # Extract package name
                        pkg = line.split("=")[0].split(":")[0].strip().strip('"').strip("'")
                        if pkg and not pkg.startswith("#"):
                            deps.append(pkg)

            if deps:
                return DependencyInfo(
                    ecosystem="Python",
                    manifest_file="pyproject.toml",
                    dependency_count=len(deps),
                    dependencies=sorted(deps[:20]),  # Top 20
                )

        except (OSError, UnicodeDecodeError):
            pass

        return None

    def _detect_python_requirements(self) -> Optional[DependencyInfo]:
        """Detect Python dependencies from requirements.txt."""
        req_path = self.root_path / "requirements.txt"
        if not req_path.exists():
            return None

        try:
            content = req_path.read_text(encoding="utf-8")
            deps: list[str] = []

            for line in content.split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    # Extract package name (before ==, >=, etc.)
                    pkg = re.split(r"[=<>!;]", line)[0].strip()
                    if pkg:
                        deps.append(pkg)

            if deps:
                return DependencyInfo(
                    ecosystem="Python",
                    manifest_file="requirements.txt",
                    dependency_count=len(deps),
                    dependencies=sorted(deps[:20]),
                )

        except (OSError, UnicodeDecodeError):
            pass

        return None

    def _detect_javascript(self) -> Optional[DependencyInfo]:
        """Detect JavaScript dependencies from package.json."""
        package_path = self.root_path / "package.json"
        if not package_path.exists():
            return None

        try:
            content = package_path.read_text(encoding="utf-8")
            data = json.loads(content)

            deps: list[str] = []

            # Get dependencies and devDependencies
            if "dependencies" in data:
                deps.extend(data["dependencies"].keys())
            if "devDependencies" in data:
                deps.extend(data["devDependencies"].keys())

            if deps:
                return DependencyInfo(
                    ecosystem="JavaScript/Node.js",
                    manifest_file="package.json",
                    dependency_count=len(deps),
                    dependencies=sorted(deps[:20]),
                )

        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            pass

        return None

    def _detect_rust(self) -> Optional[DependencyInfo]:
        """Detect Rust dependencies from Cargo.toml."""
        cargo_path = self.root_path / "Cargo.toml"
        if not cargo_path.exists():
            return None

        try:
            content = cargo_path.read_text(encoding="utf-8")
            deps: list[str] = []
            in_deps = False

            for line in content.split("\n"):
                line = line.strip()

                if line.startswith("[dependencies]"):
                    in_deps = True
                    continue

                if in_deps:
                    if line.startswith("["):
                        break
                    if "=" in line:
                        pkg = line.split("=")[0].strip()
                        if pkg and not pkg.startswith("#"):
                            deps.append(pkg)

            if deps:
                return DependencyInfo(
                    ecosystem="Rust",
                    manifest_file="Cargo.toml",
                    dependency_count=len(deps),
                    dependencies=sorted(deps[:20]),
                )

        except (OSError, UnicodeDecodeError):
            pass

        return None

    def _detect_go(self) -> Optional[DependencyInfo]:
        """Detect Go dependencies from go.mod."""
        go_mod_path = self.root_path / "go.mod"
        if not go_mod_path.exists():
            return None

        try:
            content = go_mod_path.read_text(encoding="utf-8")
            deps: list[str] = []

            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("require "):
                    # Single line require
                    parts = line.split()
                    if len(parts) >= 2:
                        deps.append(parts[1])
                elif line and not line.startswith("module") and not line.startswith("go "):
                    # Multi-line require block
                    parts = line.split()
                    if parts and not parts[0].startswith("//"):
                        if "/" in parts[0]:  # Looks like a module path
                            deps.append(parts[0])

            if deps:
                return DependencyInfo(
                    ecosystem="Go",
                    manifest_file="go.mod",
                    dependency_count=len(deps),
                    dependencies=sorted(deps[:20]),
                )

        except (OSError, UnicodeDecodeError):
            pass

        return None

    def _detect_swift(self) -> Optional[DependencyInfo]:
        """Detect Swift dependencies from Package.swift."""
        package_path = self.root_path / "Package.swift"
        if not package_path.exists():
            return None

        try:
            content = package_path.read_text(encoding="utf-8")

            # Look for .package patterns
            deps: list[str] = []
            package_pattern = r'\.package\([^)]*url:\s*"([^"]+)"'

            for match in re.finditer(package_pattern, content):
                url = match.group(1)
                # Extract package name from URL
                pkg_name = url.rstrip("/").split("/")[-1].replace(".git", "")
                deps.append(pkg_name)

            if deps:
                return DependencyInfo(
                    ecosystem="Swift",
                    manifest_file="Package.swift",
                    dependency_count=len(deps),
                    dependencies=sorted(deps[:20]),
                )

        except (OSError, UnicodeDecodeError):
            pass

        return None

    def _detect_cocoapods(self) -> Optional[DependencyInfo]:
        """Detect CocoaPods dependencies from Podfile."""
        podfile_path = self.root_path / "Podfile"
        if not podfile_path.exists():
            return None

        try:
            content = podfile_path.read_text(encoding="utf-8")
            deps: list[str] = []

            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("pod "):
                    # Extract pod name
                    match = re.match(r"pod\s+['\"]([^'\"]+)['\"]", line)
                    if match:
                        deps.append(match.group(1))

            if deps:
                return DependencyInfo(
                    ecosystem="iOS/CocoaPods",
                    manifest_file="Podfile",
                    dependency_count=len(deps),
                    dependencies=sorted(deps[:20]),
                )

        except (OSError, UnicodeDecodeError):
            pass

        return None
