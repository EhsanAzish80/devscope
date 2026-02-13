"""Tests for dependency detector."""

from pathlib import Path
from tempfile import TemporaryDirectory

from devscope.analyzers.dependencies import DependencyDetector


class TestDependencyDetector:
    """Test the DependencyDetector class."""

    def test_initialization(self) -> None:
        """Test detector initialization."""
        with TemporaryDirectory() as tmpdir:
            detector = DependencyDetector(Path(tmpdir))
            assert detector.root_path == Path(tmpdir)

    def test_no_manifests(self) -> None:
        """Test when no manifest files exist."""
        with TemporaryDirectory() as tmpdir:
            detector = DependencyDetector(Path(tmpdir))
            dependencies = detector.detect_all()

            assert len(dependencies) == 0

    def test_python_requirements_txt(self) -> None:
        """Test detection of Python requirements.txt."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create requirements.txt
            requirements = root / "requirements.txt"
            requirements.write_text("click>=8.0.0\nrich>=13.0.0\nrequests==2.28.0")

            detector = DependencyDetector(root)
            dependencies = detector.detect_all()

            assert len(dependencies) >= 1

            python_deps = [d for d in dependencies if d.ecosystem == "Python"][0]
            assert python_deps.manifest_file == "requirements.txt"
            assert python_deps.dependency_count == 3
            assert "click" in python_deps.dependencies
            assert "rich" in python_deps.dependencies

    def test_python_pyproject_toml(self) -> None:
        """Test detection of Python pyproject.toml."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create pyproject.toml
            pyproject = root / "pyproject.toml"
            pyproject.write_text("""
[project.dependencies]
click = ">=8.0.0"
rich = ">=13.0.0"
pytest = ">=7.0.0"
""")

            detector = DependencyDetector(root)
            dependencies = detector.detect_all()

            assert len(dependencies) >= 1

            python_deps = [d for d in dependencies if d.ecosystem == "Python"][0]
            assert "pyproject.toml" in python_deps.manifest_file
            assert python_deps.dependency_count >= 3

    def test_javascript_package_json(self) -> None:
        """Test detection of JavaScript package.json."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create package.json
            package_json = root / "package.json"
            package_json.write_text("""{
    "dependencies": {
        "react": "^18.0.0",
        "lodash": "^4.17.0"
    },
    "devDependencies": {
        "jest": "^29.0.0"
    }
}""")

            detector = DependencyDetector(root)
            dependencies = detector.detect_all()

            assert len(dependencies) >= 1

            js_deps = [d for d in dependencies if "JavaScript" in d.ecosystem][0]
            assert js_deps.manifest_file == "package.json"
            assert js_deps.dependency_count == 3
            assert "react" in js_deps.dependencies
            assert "jest" in js_deps.dependencies

    def test_rust_cargo_toml(self) -> None:
        """Test detection of Rust Cargo.toml."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create Cargo.toml
            cargo = root / "Cargo.toml"
            cargo.write_text("""
[package]
name = "myapp"

[dependencies]
serde = "1.0"
tokio = { version = "1.0", features = ["full"] }
""")

            detector = DependencyDetector(root)
            dependencies = detector.detect_all()

            assert len(dependencies) >= 1

            rust_deps = [d for d in dependencies if d.ecosystem == "Rust"][0]
            assert rust_deps.manifest_file == "Cargo.toml"
            assert "serde" in rust_deps.dependencies
            assert "tokio" in rust_deps.dependencies

    def test_go_mod(self) -> None:
        """Test detection of Go go.mod."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create go.mod
            go_mod = root / "go.mod"
            go_mod.write_text("""
module example.com/myapp

go 1.20

require (
    github.com/gin-gonic/gin v1.9.0
    github.com/stretchr/testify v1.8.0
)
""")

            detector = DependencyDetector(root)
            dependencies = detector.detect_all()

            assert len(dependencies) >= 1

            go_deps = [d for d in dependencies if d.ecosystem == "Go"][0]
            assert go_deps.manifest_file == "go.mod"
            assert go_deps.dependency_count >= 2

    def test_multiple_ecosystems(self) -> None:
        """Test detection of multiple ecosystems in same project."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create multiple manifest files
            (root / "requirements.txt").write_text("flask>=2.0.0")
            (root / "package.json").write_text('{"dependencies": {"express": "^4.0.0"}}')

            detector = DependencyDetector(root)
            dependencies = detector.detect_all()

            assert len(dependencies) >= 2

            ecosystems = {d.ecosystem for d in dependencies}
            assert "Python" in ecosystems or any("JavaScript" in e for e in ecosystems)
