#!/bin/bash
set -e

# Benchmark script for devscope on popular repositories
# Outputs compact summary for inclusion in README

REPOS=(
    "tiangolo/fastapi"
    "django/django"
    "tiangolo/typer"
    "psf/requests"
)

TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

for REPO in "${REPOS[@]}"; do
    REPO_NAME=$(basename "$REPO")
    echo "### [$REPO_NAME](https://github.com/$REPO)"
    echo ""
    
    # Clone shallow
    git clone --depth 1 "https://github.com/$REPO.git" "$TEMP_DIR/$REPO_NAME" 2>/dev/null
    
    # Run devscope with no cache (CI-style)
    RESULT=$(devscope summary "$TEMP_DIR/$REPO_NAME" --compact --no-cache --no-git 2>/dev/null || echo "Analysis failed")
    
    echo '```'
    echo "$RESULT"
    echo '```'
    echo ""
    
    # Clean up this repo
    rm -rf "$TEMP_DIR/$REPO_NAME"
done

echo "_Benchmarks run on GitHub Actions (2-core Linux VM)._"
