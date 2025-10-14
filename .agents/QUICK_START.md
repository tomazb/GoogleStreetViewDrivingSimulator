# Modernization Quick Start Guide

## 🚀 Ready to Start? Follow These Steps

### Step 1: Backup Current Code
```bash
git checkout -b modernization-backup
git add -A
git commit -m "backup: preserve original code before modernization"
git checkout -b feat/modernization
```

### Step 2: Install Development Tools
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install tools
pip install --upgrade pip
pip install ruff mypy pytest pytest-cov pre-commit build
```

### Step 3: Start with Phase 1 (Critical)
1. Create `pyproject.toml` (copy from MODERNIZATION_PLAN.md)
2. Create `.gitignore` (copy from MODERNIZATION_PLAN.md)
3. Create directory structure:
   ```bash
   mkdir -p src/streetview_simulator tests .github/workflows
   ```
4. Move files:
   ```bash
   mv Calculations.py src/streetview_simulator/calculations.py
   mv StreetViewAPI.py src/streetview_simulator/api.py
   mv GoogleStreetViewDrivingSimulator.py src/streetview_simulator/__main__.py
   ```
5. Create `src/streetview_simulator/__init__.py`

### Step 4: Fix Code Style (Phase 2)
```bash
# Auto-fix most issues
ruff check --fix src/
ruff format src/

# Check what needs manual fixing
mypy src/
```

### Step 5: Add Basic Tests (Phase 3)
Start with easy wins:
- Test `calculations.py` functions (pure math, easy to test)
- Add pytest configuration to `pyproject.toml`
- Run: `pytest -v`

### Step 6: Setup CI (Phase 5)
- Copy `.github/workflows/ci.yml` from plan
- Push branch and check GitHub Actions

## 📋 Priority Order

**Do First** (Can't skip):
1. ✅ Create `pyproject.toml`
2. ✅ Move code to `src/` structure
3. ✅ Fix `calculations.py` style issues
4. ✅ Add basic tests

**Do Second** (Important):
5. ⚠️ Setup pre-commit hooks
6. ⚠️ Add type hints
7. ⚠️ Setup CI/CD

**Do Third** (Polish):
8. 🔵 Add comprehensive docs
9. 🔵 Add dataclasses
10. 🔵 Convert to pathlib

## ⚡ Quick Commands Reference

```bash
# Format code
ruff format .

# Lint code
ruff check . --fix

# Type check
mypy src tests

# Run tests
pytest

# Run tests with coverage
pytest --cov

# Install package locally
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Build package
python -m build

# Setup pre-commit
pre-commit install
pre-commit run --all-files
```

## 🐛 Common Issues & Solutions

### Issue: Import errors after moving files
**Solution**: Add `__init__.py` files and update imports

### Issue: mypy errors about missing types
**Solution**: Add type stubs or ignore with `# type: ignore[import]`

### Issue: Tests can't find modules
**Solution**: Install package in editable mode: `pip install -e .`

### Issue: Pre-commit failing
**Solution**: Run manually first: `ruff format . && ruff check --fix .`

## 📊 Progress Tracking

Use this checklist to track your progress:

```markdown
- [ ] Phase 1: Foundation (2-3 hours)
  - [ ] pyproject.toml created
  - [ ] Code moved to src/
  - [ ] Tests directory created
  - [ ] Package installable

- [ ] Phase 2: Code Quality (3-4 hours)
  - [ ] Ruff formatting applied
  - [ ] calculations.py refactored
  - [ ] Type hints added
  - [ ] Pre-commit setup

- [ ] Phase 3: Testing (4-5 hours)
  - [ ] Test structure created
  - [ ] Unit tests for calculations
  - [ ] Unit tests for API
  - [ ] Coverage >70%

- [ ] Phase 4: Modern Features (3-4 hours)
  - [ ] Dataclasses added
  - [ ] Pathlib conversion
  - [ ] Logging added
  - [ ] Progress bars

- [ ] Phase 5: CI/CD (2-3 hours)
  - [ ] GitHub Actions workflow
  - [ ] Tests passing in CI
  - [ ] Badges added to README

- [ ] Phase 6: Documentation (3-4 hours)
  - [ ] Docstrings complete
  - [ ] README updated
  - [ ] CONTRIBUTING.md added
  - [ ] CHANGELOG.md added
```

## 🆘 Need Help?

1. **Read the full plan**: `.agents/MODERNIZATION_PLAN.md`
2. **Check Python docs**: https://docs.python.org/3/
3. **Ruff docs**: https://docs.astral.sh/ruff/
4. **Pytest docs**: https://docs.pytest.org/
5. **MyPy docs**: https://mypy.readthedocs.io/

## 🎯 Success Criteria

You're done when:
- ✅ `pip install -e .` works
- ✅ `pytest` passes with >70% coverage
- ✅ `mypy src` has no errors
- ✅ `ruff check .` has no violations
- ✅ GitHub Actions CI is green
- ✅ Package can be built: `python -m build`

Good luck! 🚀
