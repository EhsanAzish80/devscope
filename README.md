# devscope

> **Code intelligence at a glance** 🔍

A zero-config Python CLI tool that analyzes any codebase and outputs beautiful, fast terminal reports with core repository intelligence.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

## ✨ Features

- 🚀 **Zero configuration** - Just point and scan
- 🎨 **Beautiful output** - Rich terminal UI with colors and formatting
- ⚡ **Fast analysis** - Efficiently processes large codebases
- 📊 **Real metrics** - Actual file system analysis, not mocked data
- 🔌 **Plugin-ready** - Modular analyzer architecture for extensibility
- 🌍 **Cross-platform** - Works on Linux, macOS, and Windows
- 🎯 **Type-safe** - Full type annotations with mypy strict mode
- 📦 **Easy install** - Install via pipx or pip

## 🎯 What It Does

`devscope` scans your codebase and provides:

- **Repository information** - Detects git repository and extracts metadata
- **File statistics** - Total file count across the project
- **Lines of code** - Real line counting (excluding binary files)
- **Language breakdown** - Primary languages by file extension percentage
- **Directory analysis** - Largest directories by file count
- **Smart filtering** - Respects .gitignore and skips common build/cache directories

## 🚀 Installation

### Using pipx (Recommended)

```bash
pipx install devscope
```

### Using pip

```bash
pip install devscope
```

### From source

```bash
git clone https://github.com/yourusername/devscope.git
cd devscope
pip install -e .
```

## 📖 Usage

### Basic usage

Scan the current directory:

```bash
devscope scan
```

Scan a specific path:

```bash
devscope scan /path/to/project
```

### JSON Output Mode

Get machine-readable JSON output for automation and CI/CD:

```bash
# Scan with JSON output
devscope scan --json

# Basic analysis (faster, no intelligence)
devscope scan --json --basic

# Works with --no-git
devscope scan --json --no-git /path/to/project
```

### CI Command

Purpose-built for automation - always outputs JSON with full intelligence:

```bash
# CI-friendly analysis (no interactive elements)
devscope ci

# Analyze specific path in CI
devscope ci /path/to/project

# Skip git detection in CI
devscope ci --no-git
```

### Options

```bash
devscope scan --help
```

Available options:
- `--no-git` - Skip git repository detection
- `--basic` - Show only basic analysis (faster, no intelligence)
- `--json` - Output results as JSON (for automation)
- `--version` - Show version information

## 📊 Example Output

### Terminal Output (Default)

```
╔═══════════════════════════════════════╗
║     devscope v0.1.0                   ║
║  Code Intelligence at a glance        ║
╚═══════════════════════════════════════╝

Scanning: /Users/dev/my-project

        📊 Codebase Analysis        

Repository          my-project
Total Files         1,247
Total Lines         45,892

Languages
  Python            45.2%
  TypeScript        32.8%
  JavaScript        12.1%
  CSS               5.4%
  HTML              4.5%

Largest Directories
  src               523 files
  tests             189 files
  components        145 files
  lib               98 files
  utils             67 files

✓ Analysis complete in 0.82s
```

### JSON Output Example

```json
{
  "analysis": {
    "complexity": {
      "avg_file_size": 368.5,
      "deep_nesting_warning": false,
      "largest_files": [
        {
          "file_path": "src/analyzer.py",
          "size_bytes": 9856
        },
        {
          "file_path": "src/cli.py",
          "size_bytes": 12887
        }
      ],
      "max_directory_depth": 3
    },
    "dependencies": [
      {
        "dependency_count": 8,
        "dependencies": ["click", "rich", "gitpython", "pathspec"],
        "ecosystem": "Python",
        "manifest_file": "pyproject.toml"
      }
    ],
    "git_metrics": {
      "commit_count": 42,
      "contributor_count": 2,
      "days_since_last_commit": 0,
      "is_git_repo": true
    },
    "health_score": {
      "maintainability_grade": "B",
      "onboarding_difficulty": "Moderate",
      "risk_level": "Medium",
      "score_breakdown": {
        "complexity": 80.2,
        "git_activity": 75.0,
        "hotspots": 85.0,
        "overall": 78.5,
        "structure": 90.0,
        "tests": 70.0
      }
    },
    "hotspots": [
      {
        "depth": 2,
        "file_path": "src/analyzer.py",
        "has_nearby_tests": true,
        "lines_of_code": 321,
        "reason": "Large file with high complexity",
        "risk_score": 75.3
      }
    ],
    "languages": {
      "Python": 52.9,
      "Markdown": 17.6,
      "Shell": 11.8,
      "TOML": 5.9
    },
    "largest_dirs": [
      {
        "directory": "(root)",
        "file_count": 6
      },
      {
        "directory": "src/devscope",
        "file_count": 5
      }
    ],
    "repo_name": "devscope",
    "scan_time": 0.15,
    "test_metrics": {
      "has_tests": true,
      "source_file_count": 12,
      "test_file_count": 8,
      "test_ratio": 0.667
    },
    "total_files": 60,
    "total_lines": 3800
  },
  "devscope_version": "0.1.0",
  "schema_version": "1.0"
}
```

**JSON Schema Features:**
- ✅ Deterministic ordering (`sort_keys=True`)
- ✅ Versioned schema (`schema_version: "1.0"`)
- ✅ Tool version included (`devscope_version`)
- ✅ Stable key names (no breaking changes)
- ✅ Works with `--no-git` (graceful nulls)
- ✅ All Phase 1 + Phase 2 metrics included

## 🤖 Automation & CI/CD

### Use Cases

**GitHub Actions:**
```yaml
- name: Analyze codebase
  run: devscope ci --json > analysis.json

- name: Check code health
  run: |
    GRADE=$(jq -r '.analysis.health_score.maintainability_grade' analysis.json)
    if [[ "$GRADE" == "F" ]]; then
      echo "Code health grade F - failing build"
      exit 1
    fi
```

**GitLab CI:**
```yaml
analyze:
  script:
    - devscope ci --json > analysis.json
    - cat analysis.json
  artifacts:
    reports:
      codequality: analysis.json
```

**Pre-commit Hook:**
```bash
#!/bin/bash
devscope scan --json > /tmp/devscope.json
HOTSPOTS=$(jq '.analysis.hotspots | length' /tmp/devscope.json)
if [ "$HOTSPOTS" -gt 10 ]; then
  echo "Too many risk hotspots: $HOTSPOTS"
  exit 1
fi
```

**Badge Generation:**
```bash
# Extract grade and generate badge
GRADE=$(devscope ci --json | jq -r '.analysis.health_score.maintainability_grade')
curl "https://img.shields.io/badge/code%20health-$GRADE-brightgreen"
```

## 🏗️ Architecture

devscope follows a clean, modular architecture:

```
devscope/
├── cli.py          # CLI interface with Rich formatting
├── analyzer.py     # Core analysis engine
├── models.py       # Data models (typed)
└── utils.py        # Utility functions
```

### Design Principles

1. **Separation of Concerns** - CLI layer separated from analysis logic
2. **Type Safety** - Full type annotations throughout
3. **Extensibility** - Plugin-ready analyzer system
4. **Performance** - Efficient file system traversal with smart filtering
5. **User Experience** - Beautiful terminal output with progress indicators

## 🛠️ Development

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) (recommended) or poetry

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/devscope.git
cd devscope
```

2. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Install dependencies:
```bash
uv sync --all-extras
```

4. Run in development mode:
```bash
uv run devscope scan
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=devscope --cov-report=html

# Run specific test file
uv run pytest tests/test_analyzer.py
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint
uv run ruff check .

# Type check
uv run mypy src/devscope

# Run all checks
./scripts/check.sh
```

### Project Structure

```
devscope/
├── src/
│   └── devscope/
│       ├── __init__.py
│       ├── cli.py          # CLI interface
│       ├── analyzer.py     # Analysis engine
│       ├── models.py       # Data models
│       └── utils.py        # Utilities
├── tests/
│   ├── test_analyzer.py
│   ├── test_cli.py
│   └── test_utils.py
├── scripts/
│   ├── setup.sh           # Dev environment setup
│   └── check.sh           # Quality checks
├── pyproject.toml         # Project configuration
├── LICENSE
└── README.md
```

## 🧪 Testing

The project includes comprehensive tests:

- **Unit tests** - Core functionality testing
- **CLI tests** - Command-line interface testing  
- **Integration tests** - End-to-end testing with temporary directories
- **Type tests** - Static type checking with mypy

Coverage target: >80%

## 📋 Requirements

### Runtime Dependencies

- `click>=8.1.0` - CLI framework
- `rich>=13.0.0` - Terminal formatting
- `gitpython>=3.1.0` - Git repository detection
- `pathspec>=0.11.0` - Gitignore pattern matching

### Development Dependencies

- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `ruff>=0.1.0` - Linting and formatting
- `mypy>=1.7.0` - Static type checking

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Project foundation with uv
- ✅ Basic CLI with Rich output
- ✅ File system analysis
- ✅ Language detection
- ✅ Git repository detection
- ✅ Testing infrastructure

### Phase 2 (Upcoming)
- [ ] Code complexity metrics
- [ ] Dependency analysis
- [ ] Security scanning  
- [ ] Performance benchmarking
- [ ] Export formats (JSON, HTML, PDF)
- [ ] Configuration file support

### Phase 3 (Future)
- [ ] LSP integration
- [ ] CI/CD integration
- [ ] Historical analysis
- [ ] Team analytics
- [ ] Plugin system
- [ ] Web dashboard

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks (`./scripts/check.sh`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [uv](https://github.com/astral-sh/uv) for fast dependency management
- Terminal UI powered by [Rich](https://github.com/Textualize/rich)
- CLI framework by [Click](https://github.com/pallets/click)
- Inspired by tools like [tokei](https://github.com/XAMPPRocky/tokei) and [cloc](https://github.com/AlDanial/cloc)

## 📞 Support

- 🐛 [Report a bug](https://github.com/yourusername/devscope/issues)
- 💡 [Request a feature](https://github.com/yourusername/devscope/issues)
- 📖 [Documentation](https://github.com/yourusername/devscope#readme)

---

Made with ❤️ by the devscope community
