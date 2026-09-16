# Publishing Guide for pytest-param-table

This guide explains how to publish new versions of pytest-param-table to PyPI.

## Automated Release (Recommended)

The project uses GitHub Actions for automated releases via trusted publishing (OIDC).

### One-Time Setup

1. **Configure PyPI Trusted Publishing**
   - Go to https://pypi.org/manage/account/publishing/
   - Click "Add a new pending publisher"
   - Fill in:
     - PyPI Project Name: `pytest-param-table`
     - Owner: `rajatscode` (your GitHub username/org)
     - Repository name: `param-table`
     - Workflow name: `release.yml`
     - Environment name: `pypi`
   - Click "Add"

2. **Configure GitHub Environment** (optional but recommended)
   - Go to your GitHub repo → Settings → Environments
   - Create environment named `pypi`
   - Add protection rules (e.g., require approval for releases)

### Creating a Release

Once setup is complete, releases are automatic:

```bash
# 1. Update version in pyproject.toml
# Edit: version = "0.2.0"

# 2. Commit and push changes
git add pyproject.toml
git commit -m "Bump version to 0.2.0"
git push

# 3. Create and push a tag
git tag v0.2.0
git push origin v0.2.0
```

The GitHub Action will automatically:
- ✅ Build the package with uv
- ✅ Publish to PyPI using trusted publishing (no token needed!)
- ✅ Create a GitHub release with auto-generated notes
- ✅ Attach distribution files to the release

### What Happens Next

1. **Build Job**: Creates wheel and source distributions
2. **Publish Job**: Uploads to PyPI using OIDC authentication
3. **Release Job**: Creates GitHub release with changelog

You can monitor progress at: `https://github.com/rajatscode/param-table/actions`

---

## Manual Release (Alternative)

If you prefer manual releases or automated publishing isn't set up yet:

### 1. Install Build Tools

```bash
uv pip install build twine
```

### 2. Update Version

Edit `pyproject.toml`:
```toml
version = "0.2.0"
```

### 3. Build Distribution

```bash
uv build
```

This creates:
- `dist/pytest_param_table-0.2.0.tar.gz`
- `dist/pytest_param_table-0.2.0-py3-none-any.whl`

### 4. Test on TestPyPI (Optional)

```bash
# Upload to TestPyPI
uv run twine upload --repository testpypi dist/*

# Test installation
uv pip install --index-url https://test.pypi.org/simple/ pytest-param-table
```

### 5. Publish to PyPI

```bash
uv run twine upload dist/*
```

You'll need a PyPI API token:
- Username: `__token__`
- Password: Your PyPI API token (from https://pypi.org/manage/account/token/)

### 6. Create Git Tag

```bash
git tag v0.2.0
git push origin v0.2.0
```

### 7. Create GitHub Release

Go to https://github.com/rajatscode/param-table/releases/new
- Choose tag: v0.2.0
- Release title: Release v0.2.0
- Auto-generate release notes
- Attach dist files
- Publish

---

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.2.0): New features, backwards compatible
- **PATCH** (0.1.1): Bug fixes, backwards compatible

### Pre-release Versions

For pre-releases, use:
- Alpha: `0.2.0a1`
- Beta: `0.2.0b1`
- Release Candidate: `0.2.0rc1`

---

## Pre-Release Checklist

Before creating a release:

- [ ] All tests passing locally: `uv run pytest`
- [ ] 100% test coverage maintained
- [ ] Pre-commit hooks passing: `uv run pre-commit run --all-files`
- [ ] Version number updated in `pyproject.toml`
- [ ] CHANGELOG updated (if exists)
- [ ] Documentation updated for new features
- [ ] All PRs merged to main branch

---

## Troubleshooting

### "Project does not exist" on PyPI

For the first release, you need to register the project manually or create an API token with "Add a new project" scope.

### Trusted Publishing Failed

1. Verify the publisher configuration on PyPI
2. Check workflow name matches exactly: `release.yml`
3. Ensure environment name matches: `pypi`
4. Verify tag format: must start with `v` (e.g., `v0.1.0`)

### Build Failed

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Rebuild
uv build
```

### Wrong Version Published

You cannot overwrite a version on PyPI. You must:
1. Increment version number
2. Publish new version
3. Optionally yank the incorrect version on PyPI

---

## CI/CD Workflows

The project has two workflows:

### `test.yml` - Continuous Testing
- Runs on: Push to main/develop, Pull Requests
- Tests on: Ubuntu, macOS, Windows
- Python versions: 3.10, 3.11, 3.12
- Runs: Tests, coverage, linting, type checking

### `release.yml` - Automated Release
- Runs on: Tag push (v*)
- Builds package
- Publishes to PyPI
- Creates GitHub release

---

## Support

For issues with publishing:
- GitHub Actions logs: Check the Actions tab
- PyPI publishing: https://pypi.org/help/
- Trusted publishing docs: https://docs.pypi.org/trusted-publishers/
