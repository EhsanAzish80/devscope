# PyPI Release Guide

This document explains how to release devscope to PyPI using modern trusted publishing (OIDC).

## 🎯 Overview

**Current Version**: 0.1.0  
**Package Name**: devscope  
**PyPI URL**: https://pypi.org/project/devscope  
**TestPyPI URL**: https://test.pypi.org/project/devscope

## 🔧 One-Time Setup: Configure Trusted Publishing

### Step 1: Configure PyPI Trusted Publishing

1. **Go to PyPI**: https://pypi.org/manage/account/publishing/
2. **Click**: "Add a new pending publisher"
3. **Fill in**:
   - **PyPI Project Name**: `devscope`
   - **Owner**: `EhsanAzish80` (your GitHub username)
   - **Repository name**: `Devscope` (case-sensitive)
   - **Workflow name**: `release.yml`
   - **Environment name**: `pypi`
4. **Save**

### Step 2: Configure TestPyPI Trusted Publishing

1. **Go to TestPyPI**: https://test.pypi.org/manage/account/publishing/
2. **Repeat the same process** with:
   - **PyPI Project Name**: `devscope`
   - **Owner**: `EhsanAzish80`
   - **Repository name**: `Devscope`
   - **Workflow name**: `release.yml`
   - **Environment name**: `testpypi`
3. **Save**

### Step 3: Create GitHub Environments

1. **Go to**: https://github.com/EhsanAzish80/Devscope/settings/environments
2. **Create two environments**:
   - `testpypi`
   - `pypi`
3. **Optional**: Add protection rules
   - Required reviewers for `pypi` environment
   - Restrict to main branch only

## 🧪 Testing: Manual TestPyPI Publish

Before creating a release, you can test manually:

```bash
# Build the package
uv build

# Verify package
uv run twine check dist/*

# Publish to TestPyPI (requires API token)
uv run twine upload --repository testpypi dist/*

# Test installation
pipx install --index-url https://test.pypi.org/simple/ --pip-args="--extra-index-url https://pypi.org/simple/" devscope
```

**Note**: Manual publishing requires a TestPyPI API token from https://test.pypi.org/manage/account/token/

## 🚀 Production Release Process

### Step 1: Update Version

Edit `pyproject.toml`:

```toml
[project]
version = "0.1.0"  # Update this
```

### Step 2: Commit and Push

```bash
git add pyproject.toml
git commit -m "chore: bump version to 0.1.0"
git push
```

### Step 3: Create and Push Tag

```bash
# Create annotated tag
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release"

# Push tag to GitHub
git push origin v0.1.0
```

### Step 4: Monitor Workflow

1. **Go to**: https://github.com/EhsanAzish80/Devscope/actions/workflows/release.yml
2. **Watch the workflow**:
   - ✅ Build distribution
   - ✅ Publish to TestPyPI
   - ✅ Publish to PyPI
   - ✅ Create GitHub Release with signed artifacts

### Step 5: Verify Publication

```bash
# Wait 1-2 minutes for PyPI to index

# Install from PyPI
pipx install devscope

# Verify version
devscope --version

# Test functionality
devscope .
```

### Step 6: Verify GitHub Release

1. **Go to**: https://github.com/EhsanAzish80/Devscope/releases
2. **Check**:
   - Release created with tag `v0.1.0`
   - Distribution files attached (`.tar.gz`, `.whl`)
   - Sigstore signatures attached (`.sigstore`)

## 📦 What Gets Published

Each release includes:

- **Source Distribution**: `devscope-0.1.0.tar.gz`
- **Wheel**: `devscope-0.1.0-py3-none-any.whl`
- **Sigstore Signatures**: Cryptographic verification files

## 🔐 Security: Trusted Publishing Benefits

**No API Tokens**:
- No tokens to rotate or leak
- GitHub OIDC provides temporary credentials
- Automatic authentication via GitHub Actions

**Verified Chain**:
- Sigstore signatures prove provenance
- Verifiable connection between GitHub commit → PyPI release
- Supply chain security built-in

## 🔄 Release Versioning

### Version Scheme

- **0.1.0**: Initial public release
- **0.2.0**: Next feature release
- **0.2.1**: Patch/bugfix release
- **1.0.0**: Stable API release

### Pre-release Versions

For testing:

```bash
# Alpha release
git tag v0.2.0a1

# Beta release
git tag v0.2.0b1

# Release candidate
git tag v0.2.0rc1
```

## 🎯 Post-Release Checklist

After successful release:

- [ ] Verify package on PyPI: https://pypi.org/project/devscope
- [ ] Test installation: `pipx install devscope`
- [ ] Update README badges (PyPI version auto-updates)
- [ ] Announce on GitHub Discussions
- [ ] Tweet/share on social media
- [ ] Update any external documentation

## 🐛 Troubleshooting

### "Project not found" on PyPI

**Solution**: Complete Step 1 (Configure Trusted Publishing) to create the pending publisher.

### "Permission denied" during publish

**Solution**: 
1. Verify GitHub environment names match (`pypi`, `testpypi`)
2. Check repository name is correct (case-sensitive: `Devscope`)
3. Ensure workflow name is `release.yml`

### Version already exists on PyPI

**Solution**: PyPI doesn't allow overwriting versions. Bump version and create new tag.

### Workflow fails at "Publish to TestPyPI"

**Solution**: 
1. Configure TestPyPI trusted publishing (Step 2)
2. Create `testpypi` environment in GitHub

## 📚 Additional Resources

- **PyPI Trusted Publishing**: https://docs.pypi.org/trusted-publishers/
- **GitHub Actions OIDC**: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect
- **Sigstore**: https://www.sigstore.dev/
- **Python Packaging Guide**: https://packaging.python.org/

## 🎉 First Release

For the initial 0.1.0 release:

```bash
# Ensure everything is committed
git status

# Create and push tag
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release

Features:
- Zero-config codebase analysis
- Beautiful terminal reports
- Git intelligence and hotspot detection
- Test coverage mapping
- Multi-language support (Python, JS, TS, Go, Rust, Java)
- CI/CD integration ready
- 133 tests, 81% coverage
"

git push origin v0.1.0
```

Then monitor: https://github.com/EhsanAzish80/Devscope/actions

**That's it! No tokens, no secrets, just tags.** 🚀
