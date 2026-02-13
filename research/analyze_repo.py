#!/usr/bin/env python3
"""Script to analyze repositories and generate research dataset."""
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from devscope.analyzer import CodebaseAnalyzer
from devscope.formatters import generate_compact_summary, generate_markdown_summary


def analyze_github_repo(
    repo_url: str,
    repo_name: str,
    output_dir: Path,
) -> dict:
    """Clone and analyze a GitHub repository.
    
    Args:
        repo_url: GitHub clone URL
        repo_name: Display name for the repo
        output_dir: Directory to save results
        
    Returns:
        Analysis metadata dictionary
    """
    print(f"\n{'='*60}")
    print(f"Analyzing: {repo_name}")
    print(f"URL: {repo_url}")
    print(f"{'='*60}\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir) / "repo"
        
        # Clone repository
        print(f"📥 Cloning repository...")
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(repo_dir)],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clone: {e.stderr}")
            return None
        
        # Analyze
        print(f"🔍 Running analysis...")
        start_time = datetime.now()
        
        analyzer = CodebaseAnalyzer(
            repo_dir,
            detect_git=True,
            enable_intelligence=True,
        )
        result = analyzer.analyze()
        
        end_time = datetime.now()
        scan_duration = (end_time - start_time).total_seconds()
        
        # Create output directory for this repo
        safe_name = repo_name.replace("/", "_").replace(" ", "_")
        repo_output = output_dir / safe_name
        repo_output.mkdir(exist_ok=True)
        
        # Generate outputs
        print(f"📝 Generating reports...")
        
        # 1. Compact summary
        compact = generate_compact_summary(result)
        (repo_output / "summary_compact.txt").write_text(compact)
        
        # 2. Full markdown report
        markdown = generate_markdown_summary(result)
        (repo_output / "report.md").write_text(markdown)
        
        # 3. Metadata JSON
        metadata = {
            "repo_name": repo_name,
            "repo_url": repo_url,
            "analyzed_at": datetime.now().isoformat(),
            "scan_time_seconds": scan_duration,
            "metrics": {
                "total_files": result.total_files,
                "total_lines": result.total_lines,
                "maintainability_grade": result.health_score.maintainability_grade if result.health_score else None,
                "overall_score": result.health_score.score_breakdown.get("overall", 0) if result.health_score else None,
                "risk_level": result.health_score.risk_level.value if result.health_score else None,
                "test_ratio": result.test_metrics.test_ratio if result.test_metrics else 0.0,
            },
            "languages": result.languages,
        }
        
        with open(repo_output / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Analysis complete!")
        print(f"   Grade: {metadata['metrics']['maintainability_grade']}")
        print(f"   Files: {result.total_files}")
        print(f"   Lines: {result.total_lines:,}")
        print(f"   Scan time: {scan_duration:.2f}s")
        print(f"   Output: {repo_output}")
        
        return metadata


def main():
    """Run analysis on curated list of repositories."""
    output_dir = Path(__file__).parent
    
    # Curated list of notable repositories
    repositories = [
        {
            "name": "facebook/react",
            "url": "https://github.com/facebook/react.git",
            "description": "A JavaScript library for building user interfaces"
        },
        {
            "name": "django/django",
            "url": "https://github.com/django/django.git",
            "description": "The Web framework for perfectionists with deadlines"
        },
        {
            "name": "pallets/flask",
            "url": "https://github.com/pallets/flask.git",
            "description": "The Python micro framework for building web applications"
        },
        {
            "name": "kubernetes/kubernetes",
            "url": "https://github.com/kubernetes/kubernetes.git",
            "description": "Production-Grade Container Orchestration"
        },
        {
            "name": "microsoft/vscode",
            "url": "https://github.com/microsoft/vscode.git",
            "description": "Visual Studio Code"
        },
    ]
    
    # Analyze each repository
    results = []
    for repo in repositories:
        metadata = analyze_github_repo(
            repo["url"],
            repo["name"],
            output_dir,
        )
        if metadata:
            metadata["description"] = repo["description"]
            results.append(metadata)
    
    # Save summary index
    with open(output_dir / "index.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ Research dataset complete!")
    print(f"📊 Analyzed {len(results)} repositories")
    print(f"📁 Results saved to: {output_dir}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
