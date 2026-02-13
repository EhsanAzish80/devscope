# Contributing to devscope

Thank you for your interest in contributing to devscope! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and considerate in all interactions.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/yourusername/devscope.git
cd devscope
```

### 2. Set Up Development Environment

**Using uv (Recommended):**

```bash
# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras

# Verify setup
uv run devscope --version
```

**Using pip:**

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=devscope

# Run specific test file
uv run pytest tests/test_analyzer.py

# Run specific test
uv run pytest tests/test_analyzer.py::TestCodebaseAnalyzer::test_language_detection
```

### Code Quality Checks

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check . --fix

# Type check
uv run mypy src/devscope

# Run all checks at once
./scripts/check.sh
```

### Manual Testing

```bash
# Test on current directory
uv run devscope scan .

# Test on specific path
uv run devscope scan /path/to/project

# Test with options
uv run devscope scan . --no-git
```

## Coding Standards

### Python Style

- Follow PEP 8 conventions
- Use type hints for all functions
- Maximum line length: 100 characters
- Use ruff for formatting and linting

### Type Annotations

All functions must have type annotations:

```python
def analyze_code(path: Path, depth: int = 3) -> AnalysisResult:
    """Analyze code at the given path.
    
    Args:
        path: Path to analyze
        depth: Maximum directory depth
        
    Returns:
        Analysis results
    """
    ...
```

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include examples for complex functionality

```python
def complex_function(arg1: str, arg2: int) -> dict[str, Any]:
    """Brief description.
    
    Longer description with more details.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something goes wrong
        
    Examples:
        >>> result = complex_function("test", 42)
        >>> result["status"]
        "success"
    """
    ...
```

## Testing Guidelines

### Writing Tests

- Aim for >80% code coverage
- Test both success and failure cases
- Use descriptive test names
- Keep tests focused and isolated

```python
class TestAnalyzer:
    """Test the analyzer module."""
    
    def test_language_detection_with_python_files(self) -> None:
        """Test that Python files are detected correctly."""
        # Arrange
        ...
        
        # Act
        result = analyzer.analyze()
        
        # Assert
        assert "Python" in result.languages
```

### Test Organization

```
tests/
├── test_analyzer.py    # Core analysis tests
├── test_cli.py         # CLI interface tests
└── test_utils.py       # Utility function tests
```

## Adding Features

### 1. Plan Your Feature

- Open an issue to discuss the feature first
- Get feedback before starting implementation
- Break down large features into smaller PRs

### 2. Implement

- Write tests first (TDD recommended)
- Keep changes focused and atomic
- Add documentation
- Update README if needed

### 3. Architecture

Follow the modular architecture:

- **CLI Layer** (`cli.py`): User interface, argument parsing
- **Analysis Engine** (`analyzer.py`): Core logic
- **Models** (`models.py`): Data structures
- **Utilities** (`utils.py`): Helper functions

Example of adding a new analyzer:

```python
# src/devscope/analyzers/complexity.py
from devscope.models import AnalysisResult

class ComplexityAnalyzer:
    """Analyze code complexity metrics."""
    
    def analyze(self, path: Path) -> dict[str, Any]:
        """Analyze complexity."""
        ...
```

## Pull Request Process

### Before Submitting

1. **Run all checks:**
   ```bash
   ./scripts/check.sh
   ```

2. **Update tests:**
   - Add tests for new functionality
   - Ensure all tests pass
   - Maintain or improve coverage

3. **Update documentation:**
   - Update README if needed
   - Add docstrings
   - Update CHANGELOG

4. **Commit messages:**
   ```
   feat: Add complexity analysis

   - Implement cyclomatic complexity calculation
   - Add complexity metrics to report
   - Include tests and documentation
   ```

   Use conventional commits:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation
   - `test:` Tests
   - `refactor:` Code refactoring
   - `chore:` Maintenance

### Submitting

1. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request on GitHub

3. Fill out the PR template:
   - Description of changes
   - Motivation and context
   - How to test
   - Checklist items

### Review Process

- Maintainers will review your PR
- Address feedback promptly
- Be open to suggestions
- CI must pass before merging

## Common Tasks

### Adding a New Language

1. Update `LANGUAGE_MAP` in `analyzer.py`:
   ```python
   LANGUAGE_MAP = {
       ...
       ".new": "NewLang",
   }
   ```

2. Add tests:
   ```python
   def test_new_language_detection(self) -> None:
       """Test NewLang file detection."""
       ...
   ```

### Adding a CLI Option

1. Update `cli.py`:
   ```python
   @click.option("--new-option", help="Description")
   def scan(path: str, new_option: bool) -> None:
       ...
   ```

2. Update analyzer to use the option
3. Add tests for the new option
4. Update README

### Improving Performance

1. Profile first:
   ```bash
   python -m cProfile -o profile.stats -m devscope scan large-repo
   ```

2. Analyze results:
   ```bash
   python -m pstats profile.stats
   ```

3. Make targeted improvements
4. Add benchmarks if needed

## Project Structure

```
devscope/
├── src/devscope/        # Source code
│   ├── __init__.py
│   ├── cli.py           # CLI interface
│   ├── analyzer.py      # Analysis engine
│   ├── models.py        # Data models
│   └── utils.py         # Utilities
├── tests/               # Test suite
│   ├── test_analyzer.py
│   ├── test_cli.py
│   └── test_utils.py
├── scripts/             # Dev scripts
│   ├── setup.sh
│   └── check.sh
├── pyproject.toml       # Project config
├── README.md
├── INSTALL.md
└── CONTRIBUTING.md
```

## Release Process

(For maintainers)

1. Update version in `pyproject.toml` and `__init__.py`
2. Update CHANGELOG.md
3. Create release tag:
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```
4. Build and publish:
   ```bash
   uv build
   uv publish
   ```

## Getting Help

- 📖 Read the [README](README.md)
- 💬 Open a [Discussion](https://github.com/yourusername/devscope/discussions)
- 🐛 Report [Issues](https://github.com/yourusername/devscope/issues)
- 📧 Email maintainers (if provided)

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to devscope! 🚀
