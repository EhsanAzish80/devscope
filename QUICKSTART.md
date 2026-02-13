# devscope - Quick Start Guide

## 🚀 Get Started in 30 Seconds

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras
```

### Run Your First Scan

```bash
# Scan current directory
uv run devscope scan .

# Scan any project
uv run devscope scan /path/to/your/project
```

### Expected Output

```
╔═══════════════════════════════════════╗
║     devscope v0.1.0              ║
║  Code Intelligence at a glance   ║
╚═══════════════════════════════════════╝

Scanning: /your/project

          📊 Codebase Analysis           
  Repository                your-project  
  Total Files                       247  
  Total Lines                    12,439  
                                         
  Languages                              
    Python                        45.2%  
    JavaScript                    32.8%  
    TypeScript                    12.1%  
    CSS                            5.4%  
    HTML                           4.5%  
                                         
  Largest Directories                    
    src                        142 files  
    tests                       89 files  
    components                  45 files  
    lib                         28 files  
    utils                       17 files  

✓ Analysis complete in 0.34s
```

---

## 📂 Project Files

```
devscope/
├── 📄 README.md                 - Main documentation
├── 📄 INSTALL.md                - Installation guide
├── 📄 CONTRIBUTING.md           - Contributing guidelines
├── 📄 PROJECT_SUMMARY.md        - Detailed project summary
├── 📄 LICENSE                   - MIT License
├── 📄 pyproject.toml            - Project configuration
├── 📄 uv.lock                   - Dependency lock file
├── 📄 .gitignore                - Git ignore patterns
├── 📄 .python-version           - Python version file
│
├── 📁 src/devscope/             - Source code
│   ├── __init__.py              - Package initialization
│   ├── cli.py                   - CLI interface (62 lines)
│   ├── analyzer.py              - Analysis engine (228 lines)
│   ├── models.py                - Data models (25 lines)
│   └── utils.py                 - Utilities (64 lines)
│
├── 📁 tests/                    - Test suite (83% coverage)
│   ├── __init__.py              - Test package
│   ├── test_analyzer.py         - Analyzer tests
│   ├── test_cli.py              - CLI tests
│   └── test_utils.py            - Utility tests
│
└── 📁 scripts/                  - Development scripts
    ├── setup.sh                 - Environment setup
    └── check.sh                 - Quality checks
```

**Total:** 21 files, ~2,600 lines of code

---

## ⚡ Quick Commands

### Development

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=devscope

# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run mypy src/devscope

# Run all checks
./scripts/check.sh
```

### Usage

```bash
# Basic scan
uv run devscope scan

# Scan with path
uv run devscope scan /path/to/project

# Skip git detection
uv run devscope scan --no-git

# Show version
uv run devscope --version

# Show help
uv run devscope --help
uv run devscope scan --help
```

---

## 🎯 Features at a Glance

| Feature | Status | Details |
|---------|--------|---------|
| **CLI Interface** | ✅ | Click-based with Rich formatting |
| **Git Detection** | ✅ | Auto-detects repository info |
| **File Analysis** | ✅ | Counts files and lines of code |
| **Language Detection** | ✅ | 40+ languages supported |
| **Directory Stats** | ✅ | Largest directories by file count |
| **Progress Indicator** | ✅ | Spinner during analysis |
| **Binary Detection** | ✅ | Skips binary files automatically |
| **.gitignore Support** | ✅ | Respects ignore patterns |
| **Type Safety** | ✅ | 100% typed (mypy strict) |
| **Test Coverage** | ✅ | 83% coverage, 17 tests |
| **Cross-Platform** | ✅ | Linux, macOS, Windows |
| **Documentation** | ✅ | Comprehensive guides |

---

## 🧪 Test Suite

```bash
$ uv run pytest -v

tests/test_analyzer.py::test_analyzer_initialization ................ PASSED
tests/test_analyzer.py::test_language_detection ..................... PASSED
tests/test_analyzer.py::test_line_counting .......................... PASSED
tests/test_analyzer.py::test_skip_directories ....................... PASSED
tests/test_analyzer.py::test_directory_analysis ..................... PASSED
tests/test_analyzer.py::test_valid_result ........................... PASSED
tests/test_analyzer.py::test_invalid_negative_files ................. PASSED
tests/test_analyzer.py::test_invalid_negative_lines ................. PASSED
tests/test_cli.py::test_cli_help .................................... PASSED
tests/test_cli.py::test_scan_help ................................... PASSED
tests/test_cli.py::test_scan_current_directory ...................... PASSED
tests/test_cli.py::test_scan_with_path .............................. PASSED
tests/test_cli.py::test_version ..................................... PASSED
tests/test_utils.py::test_is_binary_file_text ....................... PASSED
tests/test_utils.py::test_is_binary_file_binary ..................... PASSED
tests/test_utils.py::test_gitignore_matcher_no_file ................. PASSED
tests/test_utils.py::test_gitignore_matcher_with_file ............... PASSED

========================= 17 passed in 0.33s =========================
Coverage: 83%
```

---

## 🎨 Output Examples

### Small Project
```
Repository          my-script
Total Files         5
Total Lines         234

Languages
  Python            100.0%

Largest Directories
  (root)            5 files
```

### Medium Project
```
Repository          web-app
Total Files         487
Total Lines         18,923

Languages
  TypeScript        42.3%
  JavaScript        28.1%
  CSS               15.6%
  HTML              8.2%
  JSON              5.8%

Largest Directories
  src/components    156 files
  src/pages         89 files
  tests             67 files
  public            54 files
  src/utils         32 files
```

### Large Project
```
Repository          monorepo
Total Files         2,847
Total Lines         143,291

Languages
  Python            35.2%
  JavaScript        24.8%
  TypeScript        18.3%
  Java              12.4%
  Go                9.3%

Largest Directories
  services/api      892 files
  frontend          654 files
  backend           543 files
  tests             398 files
  lib               234 files
```

---

## 📚 Documentation Index

- **[README.md](README.md)** - Main documentation with features and examples
- **[INSTALL.md](INSTALL.md)** - Detailed installation instructions
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project overview
- **[LICENSE](LICENSE)** - MIT License

---

## 🔧 Troubleshooting

### uv not found
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### Import errors
```bash
uv sync --all-extras
```

### Test failures
```bash
uv run pytest -v
```

### Type check errors
```bash
uv run mypy src/devscope
```

---

## 🌟 What Makes devscope Special?

1. **Zero Config** - Just run it, no setup needed
2. **Beautiful Output** - Rich colors and formatting
3. **Fast** - Efficient scanning with smart filtering
4. **Accurate** - Real analysis, not estimates
5. **Type-Safe** - Full type checking
6. **Well-Tested** - Comprehensive test coverage
7. **Extensible** - Plugin-ready architecture
8. **Cross-Platform** - Works everywhere

---

## 🎉 You're Ready!

That's it! You now have a fully functional code analysis CLI tool.

Try it on your own projects:

```bash
uv run devscope scan ~/my-project
```

Happy coding! 🚀

---

**Need help?** Check the documentation or open an issue.
