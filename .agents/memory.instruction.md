---
applyTo: '**'
---

# Coding Preferences
- Python 3.13+ project (user has Python 3.13.7)
- Prefers modern Python practices and tooling
- Values code quality, testing, and maintainability

# Project Architecture
- Google Street View Driving Simulator - generates time-lapse videos from Street View
- Structure: 3 main Python modules (GoogleStreetViewDrivingSimulator.py, StreetViewAPI.py, Calculations.py)
- Dependencies: opencv-python, polyline, requests
- Uses Google Maps APIs (Directions API, Street View Static API)
- Concurrent image downloading with ThreadPoolExecutor
- Temporary file management with context managers

# Solutions Repository
- Project needs modernization from legacy code to 2025 standards
- Current state: functional but lacks modern tooling, testing, and packaging
- Key issues: no pyproject.toml, unpinned dependencies, no tests, code style issues
