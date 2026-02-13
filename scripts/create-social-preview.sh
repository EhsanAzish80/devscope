#!/bin/bash
# Simple script to create a placeholder social preview image
# Requires ImageMagick (brew install imagemagick)

OUTPUT=".github/social-preview.png"

if ! command -v convert &> /dev/null; then
    echo "❌ ImageMagick not installed."
    echo ""
    echo "Install with:"
    echo "  macOS:   brew install imagemagick"
    echo "  Ubuntu:  sudo apt-get install imagemagick"
    echo ""
    echo "Or create the image manually using the specs in:"
    echo "  .github/SOCIAL_PREVIEW_SPECS.md"
    exit 1
fi

echo "🎨 Creating social preview image..."

# Create a 1280x640 dark gradient image with text
convert -size 1280x640 \
    gradient:'#0a0e27-#1a1f3a' \
    -font Helvetica-Bold -pointsize 120 -fill '#58a6ff' \
    -gravity north -annotate +0+150 'Devscope' \
    -font Helvetica -pointsize 48 -fill '#c9d1d9' \
    -gravity center -annotate +0-50 'Universal Codebase Intelligence' \
    -font Courier -pointsize 38 -fill '#79c0ff' \
    -gravity south -annotate +0+120 'Devscope: B · Low risk · Easy onboarding · 0.06s ⚡' \
    "$OUTPUT"

if [ -f "$OUTPUT" ]; then
    echo "✅ Social preview created: $OUTPUT"
    echo ""
    echo "Next steps:"
    echo "  1. Review the image"
    echo "  2. Optionally edit with design tool for better polish"
    echo "  3. Upload to: https://github.com/EhsanAzish80/devscope/settings"
    echo "     (Scroll to 'Social preview' section)"
else
    echo "❌ Failed to create image"
    exit 1
fi
