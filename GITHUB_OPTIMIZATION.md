# GitHub Discovery Optimization Checklist

This checklist tracks the steps to optimize the devscope repository for GitHub discovery and search.

## ✅ Completed (Automated)

- [x] Added PyPI version badge to README
- [x] Added PyPI downloads badge to README
- [x] Added CI status badge to README
- [x] Created CI workflow (.github/workflows/ci.yml)
- [x] Created optimization script (scripts/optimize-github.sh)
- [x] Created social preview specifications (.github/SOCIAL_PREVIEW_SPECS.md)

## 📋 Manual Steps Required

### 1. Install GitHub CLI (if not installed)

**macOS:**
```bash
brew install gh
```

**Linux:**
See: https://github.com/cli/cli/blob/trunk/docs/install_linux.md

**Authenticate:**
```bash
gh auth login
```

### 2. Run Repository Optimization Script

```bash
./scripts/optimize-github.sh
```

This will:
- Add repository topics (code-quality, developer-tools, cli, etc.)
- Update repository description
- Verify authentication

### 3. Create Social Preview Image

Follow the specifications in `.github/SOCIAL_PREVIEW_SPECS.md`:

**Quick specs:**
- Size: 1280 x 640 pixels
- Dark background (#0d1117)
- Title: "Devscope"
- Subtitle: "Universal Codebase Intelligence"
- Sample output: `Devscope: B · Low risk · Easy onboarding · 0.06s ⚡`

**Tools:**
- Figma: https://figma.com
- Canva: https://canva.com
- Photopea: https://photopea.com

### 4. Upload Social Preview

1. Go to: https://github.com/EhsanAzish80/devscope/settings
2. Scroll to "Social preview" section
3. Click "Upload an image"
4. Select your 1280x640 PNG file

### 5. Publish to PyPI (if not already done)

If the package isn't on PyPI yet, the version/downloads badges won't work. To publish:

```bash
# Build the package
uv build

# Publish (requires PyPI token)
uv publish
```

Set up PyPI token at: https://pypi.org/manage/account/token/

### 6. Verify Badges

After publishing and running CI:
- Check PyPI version badge works
- Check downloads badge shows data (may take 24h)
- Check CI badge shows passing status

## 📊 Expected Impact

### GitHub Search Rankings
- **Topics:** Improve discoverability in GitHub Explore
- **Description:** Better search result snippets
- **Social preview:** Higher click-through on shares

### Social Sharing
- **Twitter/X:** Rich preview cards
- **Discord/Slack:** Embedded images in link previews
- **LinkedIn:** Professional presentation

### Trust Signals
- **CI badge:** Shows active maintenance
- **Version badge:** Shows it's a real package
- **Downloads badge:** Shows adoption

## 🎯 Topics Added

The optimization script adds these topics:
- `code-quality`
- `developer-tools`
- `cli`
- `static-analysis`
- `ci-cd`
- `devops`
- `engineering-productivity`
- `python`
- `code-analysis`
- `maintainability`

These topics connect devscope to:
- GitHub's topic pages (e.g., github.com/topics/code-quality)
- "Explore" recommendations
- "Awesome" lists that filter by topics
- GitHub's dependency graph insights

## 📈 Metrics to Track

After optimization:
- Stars per week
- Clone traffic (Insights → Traffic)
- Referring sites
- Popular content (which pages get views)

Access at: https://github.com/EhsanAzish80/devscope/graphs/traffic
