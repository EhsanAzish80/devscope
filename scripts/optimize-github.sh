#!/bin/bash
# GitHub Repository Optimization Script
# Sets topics, description, and other metadata

REPO="EhsanAzish80/devscope"

echo "🔧 Optimizing GitHub repository: $REPO"
echo ""

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo ""
    echo "Install it with:"
    echo "  macOS:   brew install gh"
    echo "  Linux:   See https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    echo ""
    echo "Then run: gh auth login"
    echo ""
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI."
    echo "Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"
echo ""

# Add topics
echo "📌 Adding repository topics..."
gh repo edit "$REPO" \
    --add-topic code-quality \
    --add-topic developer-tools \
    --add-topic cli \
    --add-topic static-analysis \
    --add-topic ci-cd \
    --add-topic devops \
    --add-topic engineering-productivity \
    --add-topic python \
    --add-topic code-analysis \
    --add-topic maintainability

echo "✅ Topics added"
echo ""

# Update description
echo "📝 Updating repository description..."
gh repo edit "$REPO" \
    --description "Universal codebase intelligence. CI quality gates, maintainability grading, risk & onboarding metrics in seconds."

echo "✅ Description updated"
echo ""

echo "🎉 Repository optimization complete!"
echo ""
echo "Next steps:"
echo "  1. Upload .github/social-preview.png manually via GitHub web interface"
echo "  2. Go to: https://github.com/$REPO/settings"
echo "  3. Scroll to 'Social preview' and upload the image"
