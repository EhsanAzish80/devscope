#!/usr/bin/env python3
"""Analyze devscope repository itself."""
from pathlib import Path
from datetime import datetime
from devscope.analyzer import CodebaseAnalyzer
from devscope.formatters import generate_compact_summary, generate_markdown_summary
import json

# Analyze devscope itself
print('Analyzing devscope repository...')
start = datetime.now()
analyzer = CodebaseAnalyzer(Path.cwd(), detect_git=True, enable_intelligence=True)
result = analyzer.analyze()
duration = (datetime.now() - start).total_seconds()

# Create output directory
output = Path('research/devscope_self_analysis')
output.mkdir(exist_ok=True)

# Save outputs
(output / 'summary_compact.txt').write_text(generate_compact_summary(result))
(output / 'report.md').write_text(generate_markdown_summary(result))

# Save metadata
metadata = {
    'repo_name': 'devscope',
    'repo_url': 'https://github.com/EhsanAzish80/Devscope',
    'analyzed_at': datetime.now().isoformat(),
    'scan_time_seconds': duration,
    'metrics': {
        'total_files': result.total_files,
        'total_lines': result.total_lines,
        'maintainability_grade': result.health_score.maintainability_grade if result.health_score else None,
        'overall_score': result.health_score.score_breakdown.get('overall', 0) if result.health_score else None,
        'risk_level': result.health_score.risk_level.value if result.health_score else None,
        'test_ratio': result.test_metrics.test_ratio if result.test_metrics else 0.0,
    },
    'languages': result.languages,
}

with open(output / 'metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print(f'✓ Analysis complete! Saved to {output}')
print(f'  Grade: {metadata["metrics"]["maintainability_grade"]}')
print(f'  Files: {result.total_files}')
print(f'  Lines: {result.total_lines:,}')
print(f'  Scan time: {duration:.2f}s')
