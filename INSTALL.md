# Installation Guide

This guide covers various ways to install **devscope**.

## Quick Install

### Using pipx (Recommended)

Pipx installs CLI tools in isolated environments, preventing dependency conflicts:

```bash
pipx install devscope
```

### Using pip

Install globally:

```bash
pip install devscope
```

Or in a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install devscope
```

## Development Installation

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager (optional but recommended)

### Using uv (Recommended)

1. Install uv if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:

```bash
git clone https://github.com/yourusername/devscope.git
cd devscope
```

3. Install in editable mode with all dependencies:

```bash
uv sync --all-extras
```

4. Run devscope:

```bash
uv run devscope scan
```

### Using pip

1. Clone the repository:

```bash
git clone https://github.com/yourusername/devscope.git
cd devscope
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in editable mode:

```bash
pip install -e ".[dev]"
```

4. Run devscope:

```bash
devscope scan
```

## Verifying Installation

Check if devscope is installed correctly:

```bash
devscope --version
```

You should see output like:

```
devscope, version 0.1.0
```

Run a quick scan:

```bash
devscope scan .
```

## Platform-Specific Notes

### macOS

If you encounter permission issues, you may need to use:

```bash
pip install --user devscope
```

Or install via Homebrew (when available):

```bash
brew install devscope
```

### Linux

Most modern Linux distributions come with Python 3.9+. If not, install it via your package manager:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.9 python3-pip
```

**Fedora:**
```bash
sudo dnf install python3.9 python3-pip
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip
```

### Windows

1. Install Python 3.9+ from [python.org](https://www.python.org/downloads/)
2. Ensure "Add Python to PATH" is checked during installation
3. Open Command Prompt or PowerShell and run:

```powershell
pip install devscope
```

For pipx on Windows:

```powershell
python -m pip install pipx
python -m pipx ensurepath
pipx install devscope
```

## Troubleshooting

### Command not found

If you get "command not found" after installation:

**For pip installations:**
- Add Python's Scripts directory to your PATH
- On Unix: `~/.local/bin`
- On Windows: `%APPDATA%\Python\Scripts`

**For pipx installations:**
- Run `pipx ensurepath` to add pipx bin directory to PATH
- Restart your terminal

### Permission Errors

If you encounter permission errors:

```bash
pip install --user devscope
```

Or use a virtual environment (recommended).

### Dependency Conflicts

If you experience dependency conflicts, use pipx:

```bash
pip install pipx
pipx install devscope
```

This installs devscope in an isolated environment.

## Updating

### pipx

```bash
pipx upgrade devscope
```

### pip

```bash
pip install --upgrade devscope
```

### Development

```bash
cd devscope
git pull
uv sync --all-extras
```

## Uninstalling

### pipx

```bash
pipx uninstall devscope
```

### pip

```bash
pip uninstall devscope
```

## Next Steps

After installation, check out the [README](README.md) for usage examples and the [Contributing Guide](CONTRIBUTING.md) if you'd like to contribute to the project.
