# Google Street View Driving Simulator - Modernization Plan
**Date**: October 14, 2025  
**Python Version**: 3.13.7  
**Current State**: Functional legacy code  
**Target State**: Modern Python project with full testing, CI/CD, and quality tooling

---

## Executive Summary

This plan transforms the Google Street View Driving Simulator from functional legacy code into a modern, maintainable Python project aligned with 2025 best practices. The modernization is divided into 6 phases, prioritized by impact and dependencies.

**Estimated Timeline**: 2-3 days of focused work  
**Difficulty**: Medium  
**Risk Level**: Low (all changes are backward-compatible)

---

## Phase 1: Foundation & Project Structure ⭐ CRITICAL
**Time**: 2-3 hours  
**Priority**: MUST DO FIRST

### 1.1 Create Modern Package Structure
```
GoogleStreetViewDrivingSimulator/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .agents/
│   ├── memory.instruction.md
│   └── MODERNIZATION_PLAN.md (this file)
├── src/
│   └── streetview_simulator/
│       ├── __init__.py
│       ├── __main__.py
│       ├── api.py (was StreetViewAPI.py)
│       ├── calculations.py (was Calculations.py)
│       └── py.typed
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_calculations.py
│   └── test_integration.py
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
└── CONTRIBUTING.md
```

**Actions**:
- [ ] Create `pyproject.toml` with modern PEP 621 metadata
- [ ] Move source code to `src/streetview_simulator/`
- [ ] Create `tests/` directory structure
- [ ] Add `.gitignore` for Python projects
- [ ] Add LICENSE file (recommend MIT or Apache 2.0)
- [ ] Create CHANGELOG.md following Keep a Changelog format
- [ ] Create CONTRIBUTING.md with development guidelines

### 1.2 Create pyproject.toml
```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "streetview-simulator"
version = "2.0.0"
description = "Generate time-lapse videos from Google Street View drives"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = ["google", "streetview", "video", "timelapse", "driving", "maps"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]

dependencies = [
    "opencv-python>=4.8.0,<5.0.0",
    "polyline>=2.0.0,<3.0.0",
    "requests>=2.31.0,<3.0.0",
    "tqdm>=4.66.0,<5.0.0",  # For progress bars
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "pytest-timeout>=2.2.0",
    "mypy>=1.7.0",
    "ruff>=0.1.0",
    "pre-commit>=3.5.0",
    "types-requests>=2.31.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.4.0",
    "mkdocstrings[python]>=0.24.0",
]
security = [
    "pip-audit>=2.6.0",
    "safety>=2.3.0",
]

[project.scripts]
streetview-simulator = "streetview_simulator.__main__:main"

[project.urls]
Homepage = "https://github.com/tomazb/GoogleStreetViewDrivingSimulator"
Documentation = "https://github.com/tomazb/GoogleStreetViewDrivingSimulator#readme"
Repository = "https://github.com/tomazb/GoogleStreetViewDrivingSimulator"
Issues = "https://github.com/tomazb/GoogleStreetViewDrivingSimulator/issues"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
streetview_simulator = ["py.typed"]

# Ruff configuration (modern all-in-one linter & formatter)
[tool.ruff]
line-length = 120
target-version = "py39"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "DTZ",    # flake8-datetimez
    "T10",    # flake8-debugger
    "EM",     # flake8-errmsg
    "ISC",    # flake8-implicit-str-concat
    "ICN",    # flake8-import-conventions
    "PIE",    # flake8-pie
    "PT",     # flake8-pytest-style
    "Q",      # flake8-quotes
    "RET",    # flake8-return
    "SIM",    # flake8-simplify
    "TID",    # flake8-tidy-imports
    "PTH",    # flake8-use-pathlib
    "ERA",    # eradicate
    "PL",     # pylint
    "RUF",    # ruff-specific rules
]
ignore = [
    "PLR0913",  # Too many arguments
    "PLR2004",  # Magic value comparison
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "S101",    # Allow assert in tests
    "PLR2004", # Allow magic values in tests
]

# MyPy configuration (static type checking)
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
strict_optional = true
show_error_codes = true

[[tool.mypy.overrides]]
module = "cv2.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "polyline.*"
ignore_missing_imports = true

# Pytest configuration
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=streetview_simulator",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-branch",
    "--cov-fail-under=70",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]

# Coverage configuration
[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/site-packages/*",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
    "@abc.abstractmethod",
]
```

### 1.3 Create .gitignore
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/
coverage.xml
*.cover
.hypothesis/

# Type checking
.mypy_cache/
.dmypy.json
dmypy.json
.pytype/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Project specific
*.mp4
*.jpg
*.png
streetview_frames_*/
videos/

# Environment variables
.env
.env.local
```

---

## Phase 2: Code Quality & Style 🎨 HIGH PRIORITY
**Time**: 3-4 hours  
**Priority**: HIGH - Do immediately after Phase 1

### 2.1 Fix Calculations.py Code Style Issues

**Problems to fix**:
- Type checking with `type()` instead of `isinstance()`
- Typo: `centercord` → `centercoord`, `currentcord` → `currentcoord`
- Inconsistent parameter naming: `pointA/pointB` → `point_a/point_b`
- Missing docstrings
- Poor formatting

**Modernized version**:
```python
"""Mathematical calculations for geographic coordinates and bearings."""

import math
from typing import Tuple

Coordinate = Tuple[float, float]


def calculate_initial_compass_bearing(point_a: Coordinate, point_b: Coordinate) -> float:
    """
    Calculate the bearing between two geographic points.
    
    Uses the formula:
        θ = atan2(sin(Δlong)·cos(lat2),
                  cos(lat1)·sin(lat2) − sin(lat1)·cos(lat2)·cos(Δlong))
    
    Based on implementation by jeromer: https://gist.github.com/jeromer/2005586
    
    Args:
        point_a: Tuple of (latitude, longitude) in decimal degrees for the first point
        point_b: Tuple of (latitude, longitude) in decimal degrees for the second point
    
    Returns:
        The bearing in degrees (0-360), where 0/360 is North
    
    Raises:
        TypeError: If points are not tuples
        ValueError: If coordinates are invalid
    
    Example:
        >>> calculate_initial_compass_bearing((40.7128, -74.0060), (51.5074, -0.1278))
        51.47
    """
    if not isinstance(point_a, tuple) or not isinstance(point_b, tuple):
        raise TypeError("Only tuples are supported as arguments")
    
    if len(point_a) != 2 or len(point_b) != 2:
        raise ValueError("Coordinates must be tuples of (latitude, longitude)")
    
    lat1 = math.radians(point_a[0])
    lat2 = math.radians(point_b[0])
    diff_long = math.radians(point_b[1] - point_a[1])
    
    x = math.sin(diff_long) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (
        math.sin(lat1) * math.cos(lat2) * math.cos(diff_long)
    )
    
    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    
    return compass_bearing


def calculate_distance(origin: Coordinate, destination: Coordinate) -> float:
    """
    Calculate the distance between two points using the Haversine formula.
    
    Based on implementation by Wayne Dyck.
    
    Args:
        origin: Tuple of (latitude, longitude) in decimal degrees
        destination: Tuple of (latitude, longitude) in decimal degrees
    
    Returns:
        Distance in kilometers
    
    Example:
        >>> calculate_distance((40.7128, -74.0060), (34.0522, -118.2437))
        3935.75
    """
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # Earth radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c
    
    return distance


def calculate_pitch(
    center_coord: Coordinate,
    current_coord: Coordinate,
    height: float,
) -> str:
    """
    Calculate the pitch angle to look at an object from a given position.
    
    Args:
        center_coord: Coordinate of the object being viewed
        current_coord: Current camera position coordinate
        height: Height of the object in kilometers
    
    Returns:
        Pitch angle as a formatted string with 4 decimal places
    
    Example:
        >>> calculate_pitch((40.7128, -74.0060), (40.7120, -74.0070), 0.3)
        '19.4712'
    """
    distance = calculate_distance(center_coord, current_coord)
    if distance == 0:
        return "0.0000"
    
    pitch_radians = math.atan(height / distance)
    pitch_degrees = math.degrees(pitch_radians)
    
    return f"{pitch_degrees:.4f}"
```

### 2.2 Refactor StreetViewAPI.py

**Key improvements**:
- Replace print statements with proper logging
- Use pathlib instead of os.path
- Add dataclasses for structured data
- Better error messages
- Remove hardcoded API key variable
- Add progress bars with tqdm

### 2.3 Setup Pre-commit Hooks

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-toml
      - id: debug-statements

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
        args: [--strict]
```

**Install pre-commit**:
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## Phase 3: Testing Infrastructure 🧪 HIGH PRIORITY
**Time**: 4-5 hours  
**Priority**: HIGH - Essential for maintainability

### 3.1 Create Test Structure

**Files to create**:
1. `tests/__init__.py` (empty)
2. `tests/conftest.py` (pytest fixtures)
3. `tests/test_calculations.py` (unit tests for math functions)
4. `tests/test_api.py` (unit tests with mocking)
5. `tests/test_integration.py` (integration tests, marked as slow)

### 3.2 Test Examples

**tests/conftest.py**:
```python
"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import Mock
import tempfile
from pathlib import Path


@pytest.fixture
def mock_api_key():
    """Provide a mock API key."""
    return "test_api_key_12345"


@pytest.fixture
def sample_coordinates():
    """Provide sample coordinates for testing."""
    return [
        (40.7128, -74.0060),  # New York
        (40.7589, -73.9851),  # Times Square
        (40.7614, -73.9776),  # Central Park
    ]


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_requests_session(monkeypatch):
    """Mock requests.Session for API tests."""
    mock_session = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "OK",
        "routes": [
            {
                "legs": [
                    {
                        "steps": [
                            {
                                "polyline": {
                                    "points": "test_polyline_string"
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }
    mock_session.get.return_value = mock_response
    return mock_session
```

**tests/test_calculations.py**:
```python
"""Unit tests for calculation functions."""

import pytest
import math
from streetview_simulator.calculations import (
    calculate_initial_compass_bearing,
    calculate_distance,
    calculate_pitch,
)


class TestCalculateInitialCompassBearing:
    """Test suite for bearing calculations."""
    
    def test_north_bearing(self):
        """Test bearing calculation for northward direction."""
        point_a = (40.0, -74.0)
        point_b = (41.0, -74.0)
        bearing = calculate_initial_compass_bearing(point_a, point_b)
        assert 359.0 < bearing < 361.0 or -1.0 < bearing < 1.0
    
    def test_east_bearing(self):
        """Test bearing calculation for eastward direction."""
        point_a = (40.0, -74.0)
        point_b = (40.0, -73.0)
        bearing = calculate_initial_compass_bearing(point_a, point_b)
        assert 89.0 < bearing < 91.0
    
    def test_invalid_input_not_tuple(self):
        """Test that non-tuple inputs raise TypeError."""
        with pytest.raises(TypeError, match="Only tuples are supported"):
            calculate_initial_compass_bearing([40.0, -74.0], (41.0, -74.0))
    
    def test_invalid_coordinate_length(self):
        """Test that invalid coordinate tuples raise ValueError."""
        with pytest.raises(ValueError, match="must be tuples"):
            calculate_initial_compass_bearing((40.0,), (41.0, -74.0))


class TestCalculateDistance:
    """Test suite for distance calculations."""
    
    def test_same_point_distance(self):
        """Test that distance from a point to itself is zero."""
        point = (40.7128, -74.0060)
        distance = calculate_distance(point, point)
        assert distance == 0.0
    
    def test_known_distance(self):
        """Test distance calculation with known values."""
        # New York to Los Angeles (approximate)
        ny = (40.7128, -74.0060)
        la = (34.0522, -118.2437)
        distance = calculate_distance(ny, la)
        # Expected ~3935 km
        assert 3900 < distance < 4000
    
    def test_symmetry(self):
        """Test that distance(A, B) == distance(B, A)."""
        point_a = (40.7128, -74.0060)
        point_b = (34.0522, -118.2437)
        assert calculate_distance(point_a, point_b) == calculate_distance(point_b, point_a)


class TestCalculatePitch:
    """Test suite for pitch angle calculations."""
    
    def test_zero_distance(self):
        """Test pitch when at the object location."""
        coord = (40.7128, -74.0060)
        pitch = calculate_pitch(coord, coord, 0.5)
        assert pitch == "0.0000"
    
    def test_pitch_format(self):
        """Test that pitch is formatted with 4 decimal places."""
        center = (40.7128, -74.0060)
        current = (40.7120, -74.0070)
        pitch = calculate_pitch(center, current, 0.3)
        assert "." in pitch
        decimals = pitch.split(".")[1]
        assert len(decimals) == 4
    
    def test_increasing_height(self):
        """Test that pitch increases with object height."""
        center = (40.7128, -74.0060)
        current = (40.7100, -74.0100)
        pitch_low = float(calculate_pitch(center, current, 0.1))
        pitch_high = float(calculate_pitch(center, current, 0.5))
        assert pitch_high > pitch_low
```

**tests/test_api.py**:
```python
"""Unit tests for API functions."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from streetview_simulator.api import (
    fetch_route_coordinates,
    build_coords,
    unique,
    get_heading,
)


class TestFetchRouteCoordinates:
    """Test suite for route coordinate fetching."""
    
    def test_empty_origin_raises_error(self, mock_api_key):
        """Test that empty origin raises ValueError."""
        with pytest.raises(ValueError, match="Origin must not be empty"):
            fetch_route_coordinates("", "Los Angeles", api_key=mock_api_key)
    
    def test_empty_destination_raises_error(self, mock_api_key):
        """Test that empty destination raises ValueError."""
        with pytest.raises(ValueError, match="Destination must not be empty"):
            fetch_route_coordinates("New York", "", api_key=mock_api_key)
    
    @patch('streetview_simulator.api.requests.Session')
    def test_api_error_status(self, mock_session_class, mock_api_key):
        """Test handling of API error status."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ZERO_RESULTS",
            "error_message": "No route found"
        }
        mock_session.get.return_value = mock_response
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        with pytest.raises(RuntimeError, match="No route found"):
            fetch_route_coordinates("Invalid", "Location", api_key=mock_api_key)


class TestUniqueCoordinates:
    """Test suite for coordinate deduplication."""
    
    def test_removes_duplicates(self):
        """Test that duplicate coordinates are removed."""
        coords = [
            (40.7128, -74.0060),
            (40.7128, -74.0060),  # Duplicate
            (40.7589, -73.9851),
        ]
        result = unique(coords)
        assert len(result) == 2
    
    def test_rounds_to_precision(self):
        """Test that coordinates are rounded to 6 decimal places."""
        coords = [
            (40.7128001, -74.0060001),
            (40.7128002, -74.0060002),  # Should be considered duplicate
        ]
        result = unique(coords)
        assert len(result) == 1


class TestGetHeading:
    """Test suite for heading calculation."""
    
    def test_returns_string(self):
        """Test that heading is returned as a string."""
        start = (40.0, -74.0)
        end = (41.0, -74.0)
        heading = get_heading(start, end)
        assert isinstance(heading, str)
    
    def test_format_four_decimals(self):
        """Test that heading is formatted with 4 decimal places."""
        start = (40.0, -74.0)
        end = (41.0, -74.0)
        heading = get_heading(start, end)
        parts = heading.split(".")
        assert len(parts) == 2
        assert len(parts[1]) == 4
```

### 3.3 Test Coverage Goals

**Minimum coverage targets**:
- Overall: 70%
- calculations.py: 95% (simple math functions)
- api.py: 65% (complex with external dependencies)
- __main__.py: 50% (CLI entry point)

**Run tests**:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run only unit tests
pytest -m unit

# Run excluding slow tests
pytest -m "not slow"

# Run with verbose output
pytest -v
```

---

## Phase 4: Modern Python Features 🚀 MEDIUM PRIORITY
**Time**: 3-4 hours  
**Priority**: MEDIUM - Improves code quality significantly

### 4.1 Use Dataclasses for Structured Data

**Create models.py**:
```python
"""Data models for the Street View Simulator."""

from dataclasses import dataclass
from typing import Tuple
from pathlib import Path


Coordinate = Tuple[float, float]


@dataclass(frozen=True)
class FrameSize:
    """Represents video frame dimensions."""
    width: int
    height: int
    
    @classmethod
    def from_string(cls, size_str: str) -> "FrameSize":
        """Parse frame size from 'WIDTHxHEIGHT' string."""
        parts = size_str.lower().split("x")
        if len(parts) != 2:
            raise ValueError(f"Invalid frame size format: {size_str}")
        return cls(width=int(parts[0]), height=int(parts[1]))
    
    @property
    def as_tuple(self) -> Tuple[int, int]:
        """Return as (width, height) tuple for OpenCV."""
        return (self.width, self.height)
    
    def __str__(self) -> str:
        return f"{self.width}x{self.height}"


@dataclass
class VideoConfig:
    """Configuration for video generation."""
    origin: str
    destination: str
    output_path: Path
    fps: int = 16
    frame_size: FrameSize = FrameSize(640, 480)
    max_workers: int = 8
    codec: str = "mp4v"
    
    # Drive-by mode settings
    driveby: bool = False
    center_coord: Coordinate | None = None
    object_height: float = 0.0
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.driveby and self.center_coord is None:
            raise ValueError("center_coord required when driveby is True")
        if self.fps <= 0:
            raise ValueError("fps must be positive")
        if self.max_workers <= 0:
            raise ValueError("max_workers must be positive")


@dataclass
class RouteData:
    """Represents a route with coordinates."""
    origin: str
    destination: str
    coordinates: list[Coordinate]
    
    @property
    def num_frames(self) -> int:
        """Number of frames in the route."""
        return len(self.coordinates)
    
    @property
    def distance_km(self) -> float:
        """Approximate total distance in kilometers."""
        from .calculations import calculate_distance
        total = 0.0
        for i in range(len(self.coordinates) - 1):
            total += calculate_distance(
                self.coordinates[i],
                self.coordinates[i + 1]
            )
        return total
```

### 4.2 Convert to pathlib

**Replace all os.path usage**:
```python
# Old way
import os
output_dir = os.path.dirname(os.path.abspath(output_path))
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)
dest_path = os.path.join(temp_dir, f"{index:06d}.jpg")

# New way
from pathlib import Path
output_dir = Path(output_path).resolve().parent
output_dir.mkdir(parents=True, exist_ok=True)
dest_path = Path(temp_dir) / f"{index:06d}.jpg"
```

### 4.3 Add Proper Logging

**Replace print statements**:
```python
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


# Replace print statements
# OLD: print(f"Downloaded {completed}/{total_frames} frames", end="\r")
# NEW: Use tqdm progress bar
with tqdm(total=total_frames, desc="Downloading frames") as pbar:
    for future in concurrent.futures.as_completed(futures):
        frame_index, path = future.result()
        pbar.update(1)
```

### 4.4 Use Modern Type Hints (Python 3.10+ syntax)

```python
# Old way (Python 3.9 compatible)
from typing import Optional, List, Tuple, Sequence

def func(x: Optional[str], y: List[int]) -> Tuple[str, int]:
    pass

# New way (Python 3.10+)
def func(x: str | None, y: list[int]) -> tuple[str, int]:
    pass
```

**Note**: Keep 3.9 compatibility for broader adoption, or require 3.10+ and use modern syntax.

---

## Phase 5: CI/CD Pipeline 🔄 MEDIUM PRIORITY
**Time**: 2-3 hours  
**Priority**: MEDIUM - Essential for team collaboration

### 5.1 GitHub Actions Workflow

**Create `.github/workflows/ci.yml`**:
```yaml
name: CI

on:
  push:
    branches: [master, main, develop]
  pull_request:
    branches: [master, main, develop]
  workflow_dispatch:

jobs:
  lint:
    name: Lint & Format Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
          restore-keys: |
            ${{ runner.os }}-pip-
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      
      - name: Run ruff linting
        run: ruff check .
      
      - name: Run ruff formatting check
        run: ruff format --check .
      
      - name: Run mypy
        run: mypy src tests

  test:
    name: Test Python ${{ matrix.python-version }}
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12', '3.13']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-${{ matrix.python-version }}-pip-${{ hashFiles('**/pyproject.toml') }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      
      - name: Run tests
        run: pytest -v --cov --cov-report=xml --cov-report=term
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.13'
        with:
          files: ./coverage.xml
          flags: unittests
          name: codecov-umbrella

  security:
    name: Security Audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pip-audit safety
      
      - name: Run pip-audit
        run: pip-audit .
        continue-on-error: true
      
      - name: Check with safety
        run: safety check --json
        continue-on-error: true

  build:
    name: Build Package
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      
      - name: Install build tools
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Check package
        run: twine check dist/*
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist-packages
          path: dist/
```

### 5.2 Add Status Badges to README

```markdown
# Google Street View Driving Simulator

[![CI](https://github.com/tomazb/GoogleStreetViewDrivingSimulator/workflows/CI/badge.svg)](https://github.com/tomazb/GoogleStreetViewDrivingSimulator/actions)
[![codecov](https://codecov.io/gh/tomazb/GoogleStreetViewDrivingSimulator/branch/master/graph/badge.svg)](https://codecov.io/gh/tomazb/GoogleStreetViewDrivingSimulator)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
```

---

## Phase 6: Documentation & Polish 📚 LOW PRIORITY
**Time**: 3-4 hours  
**Priority**: LOW - But important for adoption

### 6.1 Create Comprehensive Docstrings

**Add to all public functions**:
```python
def fetch_route_coordinates(
    origin: str,
    destination: str,
    *,
    session: requests.Session | None = None,
    api_key: str | None = None,
) -> list[Coordinate]:
    """
    Fetch route coordinates between two locations using Google Directions API.
    
    This function queries the Google Maps Directions API to retrieve the polyline
    coordinates that define the route between the specified origin and destination.
    
    Args:
        origin: Starting location (address or coordinates as "lat,lng")
        destination: Ending location (address or coordinates as "lat,lng")
        session: Optional requests.Session for connection pooling
        api_key: Google Maps API key (overrides environment variable)
    
    Returns:
        List of (latitude, longitude) coordinate tuples representing the route
    
    Raises:
        ValueError: If origin or destination is empty
        RuntimeError: If API request fails or returns an error status
    
    Example:
        >>> coords = fetch_route_coordinates(
        ...     "New York, NY",
        ...     "Boston, MA",
        ...     api_key="your_key_here"
        ... )
        >>> len(coords)
        245
        >>> coords[0]
        (40.7128, -74.0060)
    
    Note:
        Requires a valid Google Maps Platform API key with Directions API enabled.
        See: https://developers.google.com/maps/documentation/directions
    """
```

### 6.2 Create CONTRIBUTING.md

```markdown
# Contributing to Google Street View Driving Simulator

Thank you for considering contributing! This document provides guidelines
for contributing to this project.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/tomazb/GoogleStreetViewDrivingSimulator.git
   cd GoogleStreetViewDrivingSimulator
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Code Quality Standards

This project uses several tools to maintain code quality:

- **Ruff**: Linting and formatting
- **MyPy**: Static type checking
- **Pytest**: Testing framework
- **Pre-commit**: Automated checks

### Running Quality Checks

```bash
# Format code
ruff format .

# Lint code
ruff check . --fix

# Type check
mypy src tests

# Run tests
pytest

# Run all checks (same as CI)
pre-commit run --all-files
```

## Testing Guidelines

- Write tests for all new features
- Maintain at least 70% code coverage
- Use descriptive test names
- Group related tests in classes
- Mark slow tests with `@pytest.mark.slow`

## Commit Message Guidelines

Follow conventional commits format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Maintenance tasks

Examples:
```
feat(api): add rate limiting for API requests
fix(calculations): correct bearing calculation for edge cases
docs(readme): update installation instructions
test(api): add tests for error handling
```

## Pull Request Process

1. Create a feature branch: `git checkout -b feat/your-feature`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass: `pytest`
5. Ensure code quality checks pass: `pre-commit run --all-files`
6. Commit your changes with descriptive messages
7. Push to your fork: `git push origin feat/your-feature`
8. Open a pull request with a clear description

## Code Review

All submissions require review. We review:

- Code quality and style
- Test coverage
- Documentation
- Performance implications
- Security considerations

## Questions?

Feel free to open an issue for questions or discussions!
```

### 6.3 Create CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-14

### Added
- Modern project structure with `pyproject.toml`
- Comprehensive test suite with pytest
- Type checking with mypy
- Linting and formatting with ruff
- Pre-commit hooks for code quality
- GitHub Actions CI/CD pipeline
- Progress bars with tqdm
- Proper logging infrastructure
- Dataclasses for structured data
- Full type hints throughout codebase

### Changed
- Moved source code to `src/streetview_simulator/` package structure
- Refactored `Calculations.py` with modern Python style
- Replaced print statements with logging
- Converted to pathlib from os.path
- Updated all docstrings to Google style
- Improved error messages with actionable guidance

### Fixed
- Type checking issues in calculations module
- Typos in parameter names (centercord → centercoord)
- Inconsistent code style
- Missing error handling edge cases

### Removed
- Hardcoded API key variable (security improvement)
- Old-style type checking with `type()`

## [1.0.0] - Previous

### Initial Release
- Basic functionality for generating Street View driving videos
- Support for both interactive and CLI modes
- Drive-by mode for focusing on landmarks
- Concurrent image downloading
- Automatic resource cleanup
```

### 6.4 Add LICENSE File

**Recommend MIT License**:
```text
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Implementation Checklist

### Phase 1: Foundation ⭐
- [ ] Create `.agents/` directory structure
- [ ] Create `pyproject.toml` with all configurations
- [ ] Create `.gitignore`
- [ ] Create `LICENSE` file
- [ ] Create `CHANGELOG.md`
- [ ] Create `CONTRIBUTING.md`
- [ ] Create `src/streetview_simulator/` directory
- [ ] Create `tests/` directory structure
- [ ] Move existing code to new structure

### Phase 2: Code Quality 🎨
- [ ] Refactor `Calculations.py` with modern style
- [ ] Add docstrings to all functions
- [ ] Replace `os.path` with `pathlib`
- [ ] Add proper logging
- [ ] Remove hardcoded API key
- [ ] Setup pre-commit hooks
- [ ] Run `ruff format` on all code
- [ ] Run `ruff check --fix` on all code
- [ ] Run `mypy` and fix all type errors

### Phase 3: Testing 🧪
- [ ] Create `tests/conftest.py` with fixtures
- [ ] Write unit tests for `calculations.py`
- [ ] Write unit tests for `api.py`
- [ ] Write integration tests
- [ ] Achieve 70%+ test coverage
- [ ] Add test documentation
- [ ] Configure pytest in `pyproject.toml`

### Phase 4: Modern Features 🚀
- [ ] Create `models.py` with dataclasses
- [ ] Replace tuple coordinates with typed objects
- [ ] Add progress bars with tqdm
- [ ] Update type hints to modern syntax
- [ ] Add rate limiting for API calls
- [ ] Improve error messages

### Phase 5: CI/CD 🔄
- [ ] Create `.github/workflows/ci.yml`
- [ ] Add status badges to README
- [ ] Setup Codecov integration
- [ ] Test CI pipeline with dummy PR
- [ ] Configure branch protection rules

### Phase 6: Documentation 📚
- [ ] Write comprehensive docstrings
- [ ] Update README with new structure
- [ ] Create API documentation
- [ ] Add usage examples
- [ ] Document configuration options
- [ ] Create troubleshooting guide

---

## Migration Strategy

### For Existing Users

**Backward Compatibility**:
- Old command-line interface remains the same
- Old module names aliased to new locations
- Environment variable `GOOGLE_STREETVIEW_API_KEY` still works

**Migration Path**:
```python
# Old way (still works)
python GoogleStreetViewDrivingSimulator.py --origin "NYC" --destination "Boston"

# New way (preferred)
streetview-simulator --origin "NYC" --destination "Boston"

# Or as module
python -m streetview_simulator --origin "NYC" --destination "Boston"
```

### Deprecation Timeline

- **v2.0.0**: New structure introduced, old structure deprecated but working
- **v2.1.0**: Warning messages added for old import paths
- **v3.0.0**: Old structure removed (12+ months later)

---

## Success Metrics

After modernization, the project should have:

✅ **Quality Metrics**:
- Test coverage: ≥70%
- Type coverage: 100% (mypy strict)
- Ruff linting: 0 violations
- Documentation coverage: ≥80%

✅ **Automation**:
- CI pipeline passing on all platforms
- Pre-commit hooks preventing bad commits
- Automated dependency updates

✅ **Developer Experience**:
- Clear contribution guidelines
- Fast test execution (<30 seconds)
- Simple setup process (3 commands)
- Helpful error messages

✅ **Maintainability**:
- Modern Python patterns
- Clear code organization
- Comprehensive tests
- Good documentation

---

## Estimated Effort

| Phase | Time | Difficulty | Priority |
|-------|------|------------|----------|
| Phase 1: Foundation | 2-3 hours | Medium | ⭐ Critical |
| Phase 2: Code Quality | 3-4 hours | Medium | 🔴 High |
| Phase 3: Testing | 4-5 hours | High | 🔴 High |
| Phase 4: Modern Features | 3-4 hours | Medium | 🟡 Medium |
| Phase 5: CI/CD | 2-3 hours | Medium | 🟡 Medium |
| Phase 6: Documentation | 3-4 hours | Low | 🔵 Low |
| **Total** | **17-23 hours** | **Medium** | - |

**Realistic Timeline**: 2-3 days of focused work, or 1-2 weeks of part-time effort.

---

## Questions or Issues?

If you encounter any issues during modernization:

1. Check this plan for guidance
2. Review relevant documentation
3. Look at similar Python projects for examples
4. Ask questions in GitHub issues

**Good luck with the modernization! 🚀**
