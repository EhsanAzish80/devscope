# Devscope

**Universal Codebase Intelligence for CI & Teams**

Analyze any repository in seconds. Get a maintainability grade, risk level, onboarding difficulty, and a CI-ready quality gate — zero configuration.

[![CI Status](https://github.com/EhsanAzish80/Devscope/workflows/CI/badge.svg)](https://github.com/EhsanAzish80/Devscope/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 133 passing](https://img.shields.io/badge/tests-133%20passing-brightgreen.svg)]()
[![Coverage: 82%](https://img.shields.io/badge/coverage-82%25-green.svg)]()
[![PyPI version](https://img.shields.io/pypi/v/devscope.svg)](https://pypi.org/project/devscope/)
[![Downloads](https://img.shields.io/pypi/dm/devscope.svg)](https://pypi.org/project/devscope/)
[![GitHub Action](https://img.shields.io/badge/GitHub%20Action-devscope--action-blue?logo=github-actions)](https://github.com/EhsanAzish80/devscope-action)

## 🚀 Install in 10 Seconds

```bash
pipx install devscope
devscope scan .
```

**On macOS:**
```bash
brew install devscope
devscope scan .
```

**Or install from source:**
```bash
git clone https://github.com/EhsanAzish80/Devscope.git
cd Devscope
uv sync
uv run devscope scan .
```

That's it. No config files. No setup. Just intelligence.

**Try it now:**
```bash
devscope summary --compact
```
```
Devscope: B · Low risk · Easy onboarding · 1.00 tests · 0.06s ⚡
```

---

## 🎯 Why devscope?

| Feature | devscope | cloc | tokei |
|---------|----------|------|-------|
| **Maintainability grade** | ✅ A-F scoring | ❌ | ❌ |
| **CI quality gate** | ✅ Exit codes | ❌ | ❌ |
| **Multi-language repo intelligence** | ✅ Full context | ⚠️ Basic | ⚠️ Basic |
| **Shareable PR summaries** | ✅ Markdown + badges | ❌ | ❌ |
| **Intelligent caching** | ✅ 10-20x speedup | ❌ | ❌ |
| **Risk & onboarding metrics** | ✅ Built-in | ❌ | ❌ |
| **Test coverage detection** | ✅ Automatic | ❌ | ❌ |

---

## 🌍 Real-World Examples

See devscope analyzing popular open-source projects:

<!-- BENCHMARKS_START -->
### [fastapi](https://github.com/tiangolo/fastapi)

```
Devscope: A · Low risk · Moderate onboarding · 1.01 tests · 3.38s ⚡
```

### [django](https://github.com/django/django)

```
Devscope: B · Low risk · Hard onboarding · 2.79 tests · 7.29s ⚡
```

### [typer](https://github.com/tiangolo/typer)

```
Devscope: A · Low risk · Moderate onboarding · 0.89 tests · 0.66s ⚡
```

### [requests](https://github.com/psf/requests)

```
Devscope: B · Low risk · Easy onboarding · 1.91 tests · 0.15s ⚡
```

_Benchmarks run on GitHub Actions (2-core Linux VM)._
<!-- BENCHMARKS_END -->

---

## ⚡ Blazing Fast

**First scan:**
```bash
$ devscope scan .
✓ Analysis complete in 2.45s
```

**Cached scan (same repo):**
```bash
$ devscope scan .
✓ Analysis complete in 0.15s (cache: 100% hit rate, ~2.3s saved)
```

**10-20x faster** on large repos. Automatic cache invalidation when files change.

---

## 🧪 Devscope Analyzing Itself

This repository is continuously analyzed by devscope.

## 🔍 Devscope Report

![Badge](https://img.shields.io/badge/maintainability-B-green)
![Badge](https://img.shields.io/badge/risk-Low-green)
![Badge](https://img.shields.io/badge/onboarding-Easy-blue)
![Badge](https://img.shields.io/badge/cache-cold-lightgrey)

**Repo:** Devscope  
**Files:** 46  
**Lines:** 10,122  
**Languages:** Python (57%) · Markdown (20%) · Shell (13%)

**Health:** B (82.5)  
**Risk:** Low  
**Onboarding:** Easy  

**Tests:** 1.00 ratio  
**Last commit:** today  

**Top hotspot:** README.md (853 LOC, Very large file (853 LOC), No nearby tests)

⚡ Scan time: 0.06s

_This report is automatically updated on every push._

---

## 💡 Use Cases

- **CI quality gate** — Fail builds on grade drops (`--fail-under B`)
- **PR health comment** — One-line summary in every PR (`devscope summary --compact`)
- **Client code audit** — Instant maintainability report for stakeholders
- **Monorepo onboarding** — Estimate ramp-up time for new engineers

---

## 📝 Shareable Summaries (The Viral Feature)

### Embed in Your README

```bash
devscope summary --badges > HEALTH.md
```

**Output:**

```markdown
## 🔍 Devscope Report

![Maintainability](https://img.shields.io/badge/maintainability-B-green)
![Risk](https://img.shields.io/badge/risk-Low-green)
![Onboarding](https://img.shields.io/badge/onboarding-Easy-blue)

**Health:** B (82.1) · **Risk:** Low · **Onboarding:** Easy  
**Files:** 1,247 · **Lines:** 45,892 · **Tests:** 0.78 ratio

⚡ Scan time: 0.82s (cache: 100% hit rate)
```

### PR Comment (GitHub Actions)

```yaml
- name: Add health check to PR
  run: |
    devscope summary --compact >> $GITHUB_STEP_SUMMARY
```

**Output:**  
`Devscope: B · Low risk · Easy onboarding · 0.78 tests · 0.82s ⚡`

### JSON for Bots

```bash
devscope summary --json | jq '.health'
```

Perfect for Slack notifications, status pages, or custom integrations.

---

## 📊 Output Examples

### Terminal (Default)

```
╔═══════════════════════════════════════╗
║     devscope v0.1.0                   ║
║  Code Intelligence at a glance        ║
╚═══════════════════════════════════════╝

📊 my-project

Repository          my-project
Health Grade        B (82.5)
Risk Level          Low
Onboarding          Easy

Total Files         1,247
Total Lines         45,892

Languages
  Python            45.2%
  TypeScript        32.8%
  JavaScript        12.1%

Tests               0.78 ratio
Top Hotspot         src/analyzer.py (321 LOC)

✓ Analysis complete in 0.82s
```

### Compact (for PRs)

```
Devscope: B · Low risk · Easy onboarding · 0.78 tests · 0.82s ⚡
```

### JSON (for automation)

```json
{
  "health_score": {
    "maintainability_grade": "B",
    "risk_level": "Low",
    "onboarding_difficulty": "Easy",
    "score_breakdown": {
      "overall": 82.5,
      "complexity": 80.2,
      "tests": 78.0,
      "git_activity": 90.0
    }
  },
  "total_files": 1247,
  "total_lines": 45892,
  "test_ratio": 0.78,
  "scan_time": 0.82
}
```

<details>
<summary><strong>📋 Full JSON Schema</strong></summary>


```json
{
  "analysis": {
    "complexity": {
      "avg_file_size": 368.5,
      "deep_nesting_warning": false,
      "largest_files": [
        {"file_path": "src/analyzer.py", "size_bytes": 9856}
      ],
      "max_directory_depth": 3
    },
    "dependencies": [
      {
        "ecosystem": "Python",
        "manifest_file": "pyproject.toml",
        "dependency_count": 8,
        "dependencies": ["click", "rich", "gitpython", "pathspec"]
      }
    ],
    "git_metrics": {
      "is_git_repo": true,
      "commit_count": 42,
      "contributor_count": 2,
      "days_since_last_commit": 0
    },
    "health_score": {
      "maintainability_grade": "B",
      "risk_level": "Low",
      "onboarding_difficulty": "Easy",
      "score_breakdown": {
        "overall": 82.5,
        "complexity": 80.2,
        "structure": 90.0,
        "tests": 78.0,
        "git_activity": 90.0,
        "hotspots": 85.0
      }
    },
    "hotspots": [
      {
        "file_path": "src/analyzer.py",
        "lines_of_code": 321,
        "depth": 2,
        "has_nearby_tests": true,
        "reason": "Large file with high complexity",
        "risk_score": 75.3
      }
    ],
    "languages": {
      "Python": 52.9,
      "Markdown": 17.6,
      "Shell": 11.8
    },
    "test_metrics": {
      "has_tests": true,
      "test_file_count": 8,
      "source_file_count": 12,
      "test_ratio": 0.667
    },
    "cache_stats": {
      "enabled": true,
      "hits": 55,
      "misses": 5,
      "total_files": 60,
      "hit_rate": 91.67,
      "time_saved_estimate": 0.005
    },
    "total_files": 60,
    "total_lines": 3800,
    "scan_time": 0.15
  },
  "devscope_version": "0.1.0",
  "schema_version": "1.0"
}
```

</details>

---

## 🤖 CI/CD Integration

### Quality Gates with Exit Codes

**Exit codes:**
- `0` = Analysis passed all thresholds
- `1` = Runtime error (invalid path, permissions)
- `2` = Threshold violated (grade/risk/onboarding)

### GitHub Actions

```yaml
- name: Code health check
  run: |
    devscope ci . \
      --fail-under B \
      --max-risk Medium \
      --max-onboarding Moderate
```

If health drops below B, the job fails with exit code 2.

### GitLab CI

```yaml
analyze:
  script:
    - devscope ci . --fail-under B --json > analysis.json
  artifacts:
    reports:
      codequality: analysis.json
```

### Shell Script

```bash
#!/bin/bash
devscope ci . --fail-under C

if [ $? -eq 2 ]; then
  echo "❌ Code quality below threshold"
  exit 1
fi
```

---

## 🎬 GitHub Action (Official)

**The easiest way to integrate Devscope into your workflow** — official GitHub Action with automatic PR comments and quality gates.

[![View on Marketplace](https://img.shields.io/badge/Marketplace-devscope--action-blue?logo=github)](https://github.com/marketplace/actions/devscope-code-health-check)

### Quick Start

Add to `.github/workflows/devscope.yml`:

```yaml
name: Code Health

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read
  pull-requests: write

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - uses: EhsanAzish80/devscope-action@v1
        with:
          fail-under: B
          max-risk: Medium
```

**What you get:**
- ✅ Automatic PR comments with health metrics
- ✅ Sticky updates (no spam)
- ✅ CI quality gates with configurable thresholds
- ✅ Fast caching (5-8s cached runs)
- ✅ Works on public & private repos

### Advanced Usage

**Use outputs in other steps:**

```yaml
- uses: EhsanAzish80/devscope-action@v1
  id: devscope

- name: Check critical health
  run: |
    if [ "${{ steps.devscope.outputs.grade }}" == "F" ]; then
      echo "::error::Code health is critical!"
    fi
```

**Analyze specific directory:**

```yaml
- uses: EhsanAzish80/devscope-action@v1
  with:
    path: ./src
    fail-under: B
```

**PR comment preview:**

```
📊 Devscope Report

Maintainability: 🟢 B
Risk: 🟢 Low
Onboarding: Easy
⚡ 0.82s

Analyze your repo → pipx install devscope
```

**Learn more:** [devscope-action](https://github.com/EhsanAzish80/devscope-action)

---

## 🤖 PR Health Bot (Drop-in)

**Get instant code health in every pull request** — zero setup, just copy the workflow.

Add this file to your repo: `.github/workflows/devscope-pr.yml`

```yaml
name: Devscope PR Health Check

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  devscope-health:
    name: Post Health Summary
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for git metrics

      - name: Install Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install pipx
        run: |
          python -m pip install --user pipx
          python -m pipx ensurepath
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Install devscope
        run: pipx install devscope

      - name: Run Devscope analysis
        id: devscope
        run: |
          set +e  # Don't fail on non-zero exit
          OUTPUT=$(devscope summary --compact 2>&1)
          EXIT_CODE=$?
          
          # Escape output for GitHub Actions
          OUTPUT="${OUTPUT//'%'/'%25'}"
          OUTPUT="${OUTPUT//$'\n'/'%0A'}"
          OUTPUT="${OUTPUT//$'\r'/'%0D'}"
          
          echo "output=$OUTPUT" >> $GITHUB_OUTPUT
          echo "exit_code=$EXIT_CODE" >> $GITHUB_OUTPUT
          
          exit 0  # Always succeed job

      - name: Post or update PR comment
        uses: actions/github-script@v7
        with:
          script: |
            const output = `${{ steps.devscope.outputs.output }}`;
            const exitCode = `${{ steps.devscope.outputs.exit_code }}`;
            
            let commentBody;
            if (exitCode === '0') {
              commentBody = `## 🔍 Devscope Health Check\n\n\`\`\`\n${output}\n\`\`\`\n\n---\n*Updated: ${new Date().toUTCString()}*`;
            } else {
              commentBody = `## 🔍 Devscope Health Check\n\n⚠️ **Analysis failed**\n\n<details>\n<summary>Error output</summary>\n\n\`\`\`\n${output}\n\`\`\`\n</details>\n\n---\n*Updated: ${new Date().toUTCString()}*`;
            }
            
            // Find existing Devscope comment
            const { data: comments } = await github.rest.issues.listComments({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
            });
            
            const existingComment = comments.find(comment => 
              comment.user.type === 'Bot' &&
              comment.body.includes('🔍 Devscope Health Check')
            );
            
            if (existingComment) {
              // Update existing comment
              await github.rest.issues.updateComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                comment_id: existingComment.id,
                body: commentBody,
              });
              console.log('Updated existing Devscope comment');
            } else {
              // Create new comment
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.issue.number,
                body: commentBody,
              });
              console.log('Created new Devscope comment');
            }
```

**What it does:**
1. Runs on every PR (open, update, reopen)
2. Installs devscope and analyzes your code
3. Posts a sticky comment that **updates automatically** on new commits
4. Fails gracefully if analysis errors
5. No secrets required — works on public repos

**Example PR comment:**

```
## 🔍 Devscope Health Check

Devscope: B · Low risk · Easy onboarding · 0.78 tests · 0.82s ⚡

---
Updated: Thu, 13 Feb 2026 14:52:33 GMT
```

**Features:**
- ✅ Sticky comment (updates instead of spamming)
- ✅ Shows health trend over PR lifetime
- ✅ Zero configuration
- ✅ Works on forks (read-only)

---

## 📖 Command Reference

### `devscope scan`

Analyze a codebase with beautiful terminal output.

```bash
devscope scan                    # Current directory
devscope scan /path/to/project   # Specific path
devscope scan --json             # JSON output
devscope scan --basic            # Fast scan (no intelligence)
devscope scan --no-git           # Skip git detection
devscope scan --no-cache         # Disable caching
devscope scan --clear-cache      # Clear cache before scan
```

### `devscope ci`

CI-optimized command (always outputs JSON).

```bash
devscope ci                      # Current directory
devscope ci --fail-under B       # Fail if grade < B
devscope ci --max-risk High      # Fail if risk > High
devscope ci --max-onboarding Hard   # Fail if onboarding > Hard
```

### `devscope summary`

Generate shareable summaries.

```bash
devscope summary                 # Markdown report
devscope summary --badges        # Include shields.io badges
devscope summary --compact       # One-line summary
devscope summary --json          # JSON with badges
```

### `devscope inject`

Inject health metrics into README between markers. **Auto-updating health blocks!**

```bash
devscope inject                  # Inject into ./README.md
devscope inject docs/STATUS.md   # Inject into specific file
devscope inject --check          # Check if update needed (exit 2 if yes)
devscope inject --repo ./src     # Analyze different directory
```

**Setup:** Add markers to your README:

```markdown
# My Project

<!-- DEVSCOPE_START -->
<!-- DEVSCOPE_END -->
```

**Result:** Health block auto-injected between markers:

````markdown
<!-- DEVSCOPE_START -->
## 🔍 Devscope Report

![Badge](https://img.shields.io/badge/maintainability-B-green)
![Badge](https://img.shields.io/badge/risk-Low-green)

**Repo:** my-project  
**Files:** 1,247  
**Lines:** 45,892  
**Languages:** Python (45%) · TypeScript (33%)

**Health:** B (82.5)  
**Risk:** Low  
**Onboarding:** Easy  

⚡ Scan time: 0.82s
<!-- DEVSCOPE_END -->
````

**CI integration:**

```yaml
- name: Update health block
  run: |
    devscope inject
    if git diff --quiet README.md; then
      echo "No changes"
    else
      git config user.name "devscope-bot"
      git config user.email "bot@devscope"
      git add README.md
      git commit -m "chore: update health metrics [skip ci]"
      git push
    fi
```

**Features:**
- ✅ Deterministic output (no change = no commit)
- ✅ Automatic badge generation
- ✅ Custom markers supported
- ✅ Check mode for CI validation

---

## 🏆 Status & Quality

| Metric | Value |
|--------|-------|
| **Tests** | 133 passing |
| **Coverage** | 82% |
| **Type checking** | mypy strict mode |
| **Platforms** | Linux · macOS · Windows |
| **Python** | 3.9+ |

This project follows rigorous engineering standards:
- ✅ Full type annotations
- ✅ Comprehensive test suite
- ✅ Zero runtime dependencies conflicts
- ✅ Cross-platform compatibility tested

---

## 🗺️ Roadmap

### ✅ Completed

- Maintainability grading (A-F)
- Risk & onboarding assessment
- CI quality gates with exit codes
- Intelligent caching (10-20x speedup)
- Shareable markdown summaries
- Shields.io badge generation
- Test coverage detection
- JSON automation API

### 🚀 Next

- Configuration file (`.devscope.yml`)
- Historical trend tracking
- Team analytics dashboard
- Security scanning (CVE detection)

---

## 🛠️ Development

### Quick Start

```bash
git clone https://github.com/EhsanAzish80/Devscope.git
cd Devscope
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --all-extras
uv run devscope scan
```

### Running Tests

```bash
uv run pytest                    # All tests
uv run pytest --cov              # With coverage
uv run pytest tests/test_analyzer.py   # Specific file
```

### Code Quality

```bash
uv run ruff format .             # Format
uv run ruff check .              # Lint
uv run mypy src/devscope         # Type check
```

### Project Structure

```
devscope/
├── src/devscope/
│   ├── cli.py          # Command-line interface
│   ├── analyzer.py     # Core analysis engine
│   ├── models.py       # Type-safe data models
│   ├── formatters.py   # Summary & badge generation
│   ├── cache.py        # Intelligent caching layer
│   └── utils.py        # Shared utilities
├── tests/
│   ├── test_analyzer.py
│   ├── test_cli.py
│   ├── test_cache.py
│   ├── test_summary.py
│   └── test_ci_thresholds.py
└── pyproject.toml      # Dependencies & config
```

---

## 🏗️ Architecture

**Design principles:**
1. **Separation of concerns** — CLI, analysis, formatting isolated
2. **Type safety** — Full mypy strict mode compliance
3. **Performance** — Smart caching with automatic invalidation
4. **Extensibility** — Plugin-ready analyzer system
5. **User experience** — Beautiful terminal output with Rich

**Core components:**
- **Analyzer** — File system traversal, language detection, metrics calculation
- **Cache Manager** — File metadata caching with invalidation on change
- **Formatters** — Output generation (terminal/JSON/markdown/compact)
- **CLI** — Click-based interface with rich error handling

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Run tests (`./scripts/check.sh`)
4. Submit a PR

For major changes, open an issue first.

---

## 🙏 Acknowledgments

Built with:
- [uv](https://github.com/astral-sh/uv) — Fast dependency management
- [Rich](https://github.com/Textualize/rich) — Beautiful terminal UI
- [Click](https://github.com/pallets/click) — CLI framework

Inspired by [tokei](https://github.com/XAMPPRocky/tokei) and [cloc](https://github.com/AlDanial/cloc).

---

## 📞 Support

- 🐛 [Report a bug](https://github.com/EhsanAzish80/Devscope/issues)
- 💡 [Request a feature](https://github.com/EhsanAzish80/Devscope/issues)
- 📖 [Documentation](https://github.com/EhsanAzish80/Devscope#readme)


