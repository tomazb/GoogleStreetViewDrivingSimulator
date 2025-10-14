# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-14

### Added

#### Phase 1 - Foundation
- Modern project structure with `src/` layout
- Complete `pyproject.toml` with PEP 621 metadata
- Modern `.gitignore` for Python projects
- Package now installable with `pip install -e ".[dev]"`
- Entry point command: `streetview-simulator`
- PEP 561 `py.typed` marker for type checking support

#### Phase 2 - Code Quality
- Comprehensive docstrings for all public functions
- Modern Python 3.9+ type hints throughout
- Fixed typo: `centercord` → `centercoord` in calculations
- Changed `type()` checks to `isinstance()` for better practices
- Removed hardcoded API key constant for security
- Applied Ruff formatting across entire codebase
- Fixed 40+ linting issues automatically

#### Phase 3 - Testing
- Comprehensive test suite with pytest
- 64 unit tests with 43.48% code coverage
- Test fixtures in `tests/conftest.py`
- Mocked API tests to avoid external dependencies
- Coverage reporting (terminal, HTML, XML)
- 100% coverage for `calculations.py` module

#### Phase 4 - Modern Features
- Dataclasses for structured data (`models.py`):
  * `FrameSize`: Immutable frame dimension representation
  * `VideoConfig`: Complete video generation configuration
  * `RouteData`: Route information with calculated properties
- Progress bars with tqdm for better UX
- Graceful fallback if tqdm not available

#### Phase 5 - CI/CD
- GitHub Actions workflow for automated testing
- Matrix testing: Python 3.9-3.13 on Ubuntu/Windows/macOS
- Automated linting with Ruff
- Type checking with MyPy
- Security auditing with pip-audit
- Package building and validation
- Codecov integration for coverage tracking
- Status badges in README

#### Phase 6 - Documentation
- `CONTRIBUTING.md` with development guidelines
- `CHANGELOG.md` (this file)
- Enhanced README with badges and modern examples
- `.agents/` directory with modernization documentation:
  * `MODERNIZATION_PLAN.md`: Complete modernization strategy
  * `PLAN_B_PROGRESS.md`: Implementation progress tracking
  * `ENV_USAGE.md`: Environment variable usage guide
  * `ROADMAP.md`: Visual modernization roadmap

#### API Integration Tools
- `.env.example` template for secure API key management
- `run_with_env.sh`: Helper script to auto-load .env and venv
- `test_with_api.sh`: Automated API testing script
- `manual_test.py`: Interactive API testing with Python
- `test_fps.sh`: FPS comparison testing tool

### Changed

- **Breaking**: API key now via environment variable only (no hardcoded constant)
- **Breaking**: Minimum Python version now 3.9+ (was unspecified)
- Improved error messages following best practices (EM101/EM102)
- Progress display now uses tqdm progress bars instead of print statements
- Package structure migrated from flat layout to src/ layout
- Testing framework standardized on pytest (was ad-hoc)

### Fixed

- Fixed ambiguous Unicode character `­` in docstring
- Fixed return statement redundancies in calculations
- Fixed error message formatting to use variables
- Fixed type hint compatibility (List/Tuple → list/tuple)
- Improved coordinate validation and error handling

### Removed

- Removed `GOOGLE_STREETVIEW_API_KEY` hardcoded constant
- Removed legacy `requirements.txt` in favor of `pyproject.toml`
- Removed old-style type hints from `typing` module

### Security

- API keys now only via environment variables
- Added security auditing in CI pipeline
- Added `.env` to `.gitignore`
- Created `.env.example` template for safe onboarding

### Documentation

- Comprehensive docstrings added to all modules
- Type hints provide inline documentation
- Testing examples in `CONTRIBUTING.md`
- API key setup documented in multiple places
- FPS configuration examples provided

## [1.0.0] - Previous

### Initial Release

- Basic functionality for generating Street View time-lapses
- Interactive and CLI modes
- Drive-by feature for focusing on landmarks
- Basic Google Maps API integration
- Polyline decoding for routes
- OpenCV-based video generation

---

## Migration Guide (v1 → v2)

### API Key Management

**Before (v1.x):**
```python
# Hardcoded in StreetViewAPI.py
GOOGLE_STREETVIEW_API_KEY = "your_key_here"
```

**After (v2.x):**
```bash
# In .env file
GOOGLE_STREETVIEW_API_KEY=your_key_here

# Run with helper script
./run_with_env.sh streetview-simulator --origin "NYC" --destination "LA" --output video.mp4
```

### Installation

**Before (v1.x):**
```bash
pip install -r requirements.txt
python GoogleStreetViewDrivingSimulator.py
```

**After (v2.x):**
```bash
pip install -e ".[dev]"
streetview-simulator --help
```

### Running Tests

**Before (v1.x):**
```bash
# No tests available
```

**After (v2.x):**
```bash
pytest
pytest --cov  # With coverage
```

---

[2.0.0]: https://github.com/tomazb/GoogleStreetViewDrivingSimulator/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/tomazb/GoogleStreetViewDrivingSimulator/releases/tag/v1.0.0
