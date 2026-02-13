# Devscope Research Dataset

This directory contains **authority analysis data** from running Devscope on notable open-source repositories. The dataset serves as a benchmark for code health metrics and validates Devscope's analysis capabilities across diverse codebases.

## 📊 Dataset Overview

Each analyzed repository includes:

- **`summary_compact.txt`** - Single-line health summary (grade, metrics, scan time)
- **`report.md`** - Full markdown analysis report with detailed metrics
- **`metadata.json`** - Structured data including:
  - Repository name and URL
  - Analysis timestamp
  - Scan duration
  - Key metrics (grade, files, lines, test ratio, languages)
  - Health scores and risk assessment

## 🎯 Methodology

### Repository Selection Criteria

Repositories are selected based on:

1. **Popularity** - High star count and active community
2. **Diversity** - Multiple programming languages and domains
3. **Maturity** - Established projects with stable codebases
4. **Open Source** - Publicly accessible for reproducibility

### Analysis Configuration

All analyses use:

```python
CodebaseAnalyzer(
    repo_path,
    detect_git=True,        # Enable git metrics
    enable_intelligence=True # Enable advanced analysis
)
```

**Features enabled:**
- Complexity analysis (cyclomatic, cognitive)
- Test detection and ratio calculation
- Git metrics (commit frequency, age)
- Hotspot identification
- Maintainability scoring
- Risk assessment
- Onboarding difficulty evaluation

### Metrics Collected

| Metric | Description | Range |
|--------|-------------|-------|
| **Maintainability Grade** | Overall code health score | A (best) to F (worst) |
| **Risk Level** | Code maintenance risk | Low / Medium / High |
| **Onboarding Difficulty** | New developer learning curve | Easy / Moderate / Hard |
| **Test Ratio** | Test-to-code line ratio | 0.0 - 3.0+ |
| **Complexity** | Average cyclomatic complexity | 1.0+ |
| **Scan Time** | Analysis duration | Seconds |

## 📁 Dataset Structure

```
research/
├── README.md                    # This file
├── analyze_repo.py              # Script for analyzing GitHub repos
├── analyze_self.py              # Script for analyzing devscope itself
│
├── devscope_self_analysis/      # Devscope analyzing itself
│   ├── metadata.json
│   ├── report.md
│   └── summary_compact.txt
│
├── facebook_react/              # React library analysis
│   ├── metadata.json
│   ├── report.md
│   └── summary_compact.txt
│
└── index.json                   # Summary index of all analyses
```

## 🚀 Running Your Own Analysis

### Analyze a GitHub Repository

```bash
# Using the provided script
python research/analyze_repo.py

# Or manually analyze a specific repo
devscope scan /path/to/repo --markdown > output.md
```

### Analyze Devscope Itself

```bash
python research/analyze_self.py
```

### Analyze Custom Repository

```python
from pathlib import Path
from datetime import datetime
from devscope.analyzer import CodebaseAnalyzer
from devscope.formatters import generate_markdown_summary
import json

# Analyze repository
start = datetime.now()
analyzer = CodebaseAnalyzer(
    Path("/path/to/repo"),
    detect_git=True,
    enable_intelligence=True
)
result = analyzer.analyze()
scan_time = (datetime.now() - start).total_seconds()

# Generate report
report = generate_markdown_summary(result)
print(report)

# Save metadata
metadata = {
    "repo_name": "my-repo",
    "analyzed_at": datetime.now().isoformat(),
    "scan_time_seconds": scan_time,
    "maintainability_grade": result.health_score.maintainability_grade,
    # ... additional fields
}
```

## 📈 Research Applications

This dataset can be used for:

1. **Benchmarking** - Compare your project against industry standards
2. **Validation** - Verify Devscope's analysis accuracy
3. **Research** - Study code health patterns across languages
4. **Documentation** - Real-world examples of analysis output
5. **Training** - Learn what good/bad metrics look like

## 🔬 Example Analysis: Devscope Self-Analysis

**Repository:** [EhsanAzish80/Devscope](https://github.com/EhsanAzish80/Devscope)

**Quick Stats:**
- **Grade:** A
- **Files:** 51 Python files
- **Lines:** 10,399 LOC
- **Test Ratio:** 0.84 (excellent test coverage)
- **Risk:** Low
- **Scan Time:** 0.19s

**Key Findings:**
- Well-tested codebase with strong coverage
- Modern Python practices (type hints, dataclasses)
- Low complexity averages
- Comprehensive test suite
- Active development (recent commits)

See full analysis: [`devscope_self_analysis/report.md`](devscope_self_analysis/report.md)

## 📝 Data Format Specification

### metadata.json Schema

```json
{
  "repo_name": "owner/repository",
  "repo_url": "https://github.com/owner/repository",
  "analyzed_at": "2026-02-13T12:00:00.000000",
  "scan_time_seconds": 1.23,
  "metrics": {
    "total_files": 100,
    "total_lines": 50000,
    "maintainability_grade": "B",
    "overall_score": 85.5,
    "risk_level": "Low",
    "test_ratio": 0.75
  },
  "languages": {
    "Python": 45.2,
    "JavaScript": 30.1,
    "HTML": 24.7
  }
}
```

## 🤝 Contributing New Analyses

To add your repository analysis to this dataset:

1. **Run analysis** using `analyze_repo.py` or manual script
2. **Verify output** includes all required files
3. **Document findings** in your repository folder
4. **Update index.json** with new entry
5. **Submit PR** with descriptive commit message

**Requirements for inclusion:**
- Public repository (for reproducibility)
- Notable project (1000+ stars or significant community impact)
- Clean analysis (no errors or warnings)
- Complete metadata

## 📊 Dataset Statistics

**Last Updated:** February 13, 2026

| Repository | Grade | Files | Lines | Language | Scan Time |
|------------|-------|-------|-------|----------|-----------|
| devscope | A | 51 | 10,399 | Python | 0.19s |
| _(Add more as analyzed)_ | - | - | - | - | - |

## 🔗 Related Resources

- [Devscope Documentation](../README.md)
- [Analysis Methodology](../docs/methodology.md)
- [Scoring System](../docs/scoring.md)
- [GitHub Action](../devscope-action/README.md)

## 📄 License

This research dataset is provided under the same license as the Devscope project. Individual repositories analyzed remain under their original licenses.

## 🙏 Acknowledgments

Thanks to all open-source projects included in this dataset. Your work makes the software community better.

---

**Note:** Analysis results are point-in-time snapshots. Repository health may change as code evolves. Re-run analyses periodically for up-to-date metrics.
