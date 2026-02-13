# 🚀 Quick Release Reference

## Pre-Release Checklist

```bash
# 1. Build and verify
uv build
uv run twine check dist/*

# 2. Run full test suite
uv run pytest -v

# 3. Check types and linting
uv run mypy src/devscope
uv run ruff check .

# 4. Verify version in pyproject.toml
grep 'version = ' pyproject.toml
```

## 🎯 Production Release (3 Commands)

```bash
# 1. Bump version and commit
git add pyproject.toml
git commit -m "chore: bump version to 0.1.0"
git push

# 2. Create and push tag
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0

# 3. Monitor workflow
open https://github.com/EhsanAzish80/Devscope/actions
```

**That's it!** Workflow auto-publishes to TestPyPI → PyPI → GitHub Release

## 🔧 One-Time Setup Required

Before first release, configure PyPI trusted publishing:

### PyPI Setup
1. Go to: https://pypi.org/manage/account/publishing/
2. Add pending publisher:
   - Project: `devscope`
   - Owner: `EhsanAzish80`
   - Repo: `Devscope`
   - Workflow: `release.yml`
   - Environment: `pypi`

### TestPyPI Setup
1. Go to: https://test.pypi.org/manage/account/publishing/
2. Same settings as above, but Environment: `testpypi`

### GitHub Environments
1. Go to: https://github.com/EhsanAzish80/Devscope/settings/environments
2. Create: `pypi` and `testpypi`

## ✅ Post-Release Verification

```bash
# Wait 1-2 minutes, then:
pipx install devscope
devscope --version
devscope .
```

Check:
- ✅ PyPI: https://pypi.org/project/devscope
- ✅ GitHub Release: https://github.com/EhsanAzish80/Devscope/releases
- ✅ Badges update automatically in README

## 📝 Version Bumping

Edit `pyproject.toml`:

```toml
version = "0.1.0"  # Initial release
version = "0.2.0"  # Feature release
version = "0.2.1"  # Bugfix release
version = "1.0.0"  # Stable API
```

## 🐛 Common Issues

**"Project not found"**: Configure PyPI trusted publishing first  
**"Permission denied"**: Check GitHub environments exist  
**"Version exists"**: Bump version, can't overwrite on PyPI

## 📚 Full Documentation

See [RELEASE.md](RELEASE.md) for complete guide with troubleshooting.
