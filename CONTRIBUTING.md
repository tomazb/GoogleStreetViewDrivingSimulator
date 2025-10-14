# Contributing to Google Street View Driving Simulator

Thank you for considering contributing! This document provides guidelines for contributing to this project.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tomazb/GoogleStreetViewDrivingSimulator.git
   cd GoogleStreetViewDrivingSimulator
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

## Code Quality Standards

This project uses several tools to maintain code quality:

- **Ruff**: Modern all-in-one linter and formatter
- **MyPy**: Static type checking
- **Pytest**: Testing framework with coverage reporting
- **Pre-commit**: Automated quality checks (optional but recommended)

### Running Quality Checks

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Lint with auto-fix
ruff check --fix .

# Type check
mypy src tests

# Run tests
pytest

# Run tests with coverage
pytest --cov
```

## Testing Guidelines

- Write tests for all new features
- Maintain at least 70% code coverage
- Use descriptive test names that explain what is being tested
- Group related tests in classes
- Mark slow tests with `@pytest.mark.slow`
- Use fixtures from `tests/conftest.py` for common test data

### Test Structure

```python
class TestFeatureName:
    """Test suite for feature description."""
    
    def test_specific_behavior(self):
        """Test that specific behavior works correctly."""
        # Arrange
        input_data = setup_test_data()
        
        # Act
        result = function_under_test(input_data)
        
        # Assert
        assert result == expected_value
```

## Commit Message Guidelines

Follow conventional commits format for clear history:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring without behavior change
- `style`: Code style/formatting changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD configuration changes

### Examples

```
feat(api): add rate limiting for API requests
fix(calculations): correct bearing calculation for edge cases
docs(readme): update installation instructions
test(api): add tests for error handling
refactor(models): convert to dataclasses for better structure
```

## Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes:**
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Ensure quality:**
   ```bash
   # Run all checks
   ruff format .
   ruff check .
   mypy src tests
   pytest
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat(scope): descriptive message"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feat/your-feature-name
   ```

6. **Open a pull request:**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure CI passes

## Code Review Process

All submissions require review. We review:

- **Code quality**: Follows project standards and best practices
- **Test coverage**: New code has appropriate tests
- **Documentation**: Public APIs are documented
- **Performance**: No unnecessary performance degradation
- **Security**: No security vulnerabilities introduced

## Project Structure

```
GoogleStreetViewDrivingSimulator/
├── src/streetview_simulator/    # Main package source
│   ├── __init__.py
│   ├── __main__.py             # CLI entry point
│   ├── api.py                  # Google APIs integration
│   ├── calculations.py         # Geographic calculations
│   └── models.py               # Data models
├── tests/                       # Test suite
│   ├── conftest.py             # Shared fixtures
│   ├── test_api.py
│   └── test_calculations.py
├── .github/workflows/           # CI/CD configuration
├── pyproject.toml              # Project configuration
└── README.md                    # User documentation
```

## Getting Help

- **Questions**: Open a GitHub issue with the `question` label
- **Bugs**: Open a GitHub issue with detailed reproduction steps
- **Feature requests**: Open a GitHub issue describing the use case

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes for significant contributions
- CHANGELOG.md for feature additions

Thank you for helping improve this project! 🎉
