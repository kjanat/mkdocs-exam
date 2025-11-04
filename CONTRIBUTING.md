# Contributing to MkDocs Exam Plugin

Thank you for considering contributing to mkdocs-exam! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

This project follows a standard code of conduct. Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/mkdocs-exam.git
   cd mkdocs-exam
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/kjanat/mkdocs-exam.git
   ```

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Install Dependencies

```bash
# Install the package in editable mode with dev dependencies
uv pip install -e .[dev]
```

### Install Pre-commit Hooks

```bash
pre-commit install
```

This will run linters and formatters automatically before each commit.

## Project Structure

```
mkdocs-exam/
├── mkdocs_exam/           # Main package
│   ├── plugin.py          # Plugin entry point
│   ├── parser.py          # Exam block parser
│   ├── html_builder.py    # HTML generation
│   ├── constants.py       # Constants and defaults
│   ├── css/               # Stylesheets
│   │   └── exam.css
│   └── js/                # JavaScript
│       └── exam.js
├── tests/                 # Test suite
│   └── test_plugin.py
├── example/               # Example documentation site
│   ├── mkdocs.yml
│   └── docs/
└── .github/               # CI/CD workflows
```

## Making Changes

### Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Code Guidelines

- **Python**: Follow PEP 8 style guide
  - Use type hints for all function signatures
  - Write docstrings for all public functions and classes
  - Maximum line length: 120 characters

- **JavaScript**: Follow JavaScript Standard Style
  - Use strict mode (`'use strict'`)
  - Add JSDoc comments for all functions
  - Use `const` and `let` instead of `var`

- **CSS**: Follow BEM naming convention where applicable
  - Use CSS custom properties for theming
  - Include comments for complex selectors

### Writing Tests

All new features and bug fixes should include tests.

```python
def test_your_feature():
    """Test description in imperative mood."""
    # Arrange
    markdown = textwrap.dedent(
        """
        <exam>
        question: Test?
        answer-correct: Yes
        content:
        <p>Content</p>
        </exam>
        """
    )

    # Act
    plugin = MkDocsExamPlugin()
    plugin.config = {}
    result = plugin.on_page_markdown(markdown, DummyPage(), None)

    # Assert
    assert "expected-output" in result
```

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Tests with Coverage

```bash
pytest tests/ -v --cov=mkdocs_exam --cov-report=term-missing --cov-report=html
```

View the HTML coverage report at `htmlcov/index.html`.

### Run Specific Test

```bash
pytest tests/test_plugin.py::test_specific_function -v
```

### Run Pre-commit Checks Manually

```bash
pre-commit run --all-files
```

## Code Style

### Python

We use [ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check for issues
ruff check mkdocs_exam/ tests/

# Auto-fix issues
ruff check --fix mkdocs_exam/ tests/

# Format code
ruff format mkdocs_exam/ tests/
```

### JavaScript

We use [standard](https://standardjs.com/) for JavaScript linting:

```bash
standard mkdocs_exam/js/exam.js
```

### CSS/Markdown/YAML

We use [prettier](https://prettier.io/) for formatting:

```bash
prettier --write "**/*.{css,md,yml,yaml,json}"
```

## Development Workflow

### Testing Changes Locally

1. **Install the plugin in editable mode**:
   ```bash
   uv pip install -e .
   ```

2. **Run the example site**:
   ```bash
   cd example
   uv run mkdocs serve
   ```

3. **View at** http://localhost:8008

### Debugging

Add logging statements using the logger:

```python
import logging
logger = logging.getLogger("mkdocs.plugins.mkdocs-exam")
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

Run MkDocs with verbose logging:

```bash
mkdocs serve --verbose
```

## Submitting Changes

### Before Submitting

1. **Run tests**: Ensure all tests pass
   ```bash
   pytest tests/ -v
   ```

2. **Check coverage**: Aim for >80% coverage
   ```bash
   pytest tests/ --cov=mkdocs_exam --cov-report=term-missing
   ```

3. **Run linters**: Fix any linting issues
   ```bash
   pre-commit run --all-files
   ```

4. **Update documentation**: Update README, CHANGELOG, docstrings as needed

5. **Update CHANGELOG**: Add entry under `[Unreleased]` section

### Pull Request Process

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes (formatting)
   - `refactor:` Code refactoring
   - `test:` Adding or updating tests
   - `chore:` Maintenance tasks

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request** on GitHub:
   - Provide clear title and description
   - Reference any related issues
   - Include screenshots/GIFs for UI changes
   - List any breaking changes

4. **Address review feedback**: Make requested changes and push updates

5. **Wait for CI**: Ensure all GitHub Actions checks pass

## Release Process

(For maintainers only)

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md**: Move `[Unreleased]` items to new version section
3. **Commit changes**: `git commit -m "chore: bump version to X.Y.Z"`
4. **Create tag**: `git tag -a vX.Y.Z -m "Release X.Y.Z"`
5. **Push**: `git push && git push --tags`
6. **Build**: `python -m build`
7. **Publish to PyPI**: `python -m twine upload dist/*`
8. **Create GitHub Release**: Add release notes from CHANGELOG

## Questions or Issues?

- **Bug reports**: Open an issue with the "bug" label
- **Feature requests**: Open an issue with the "enhancement" label
- **Questions**: Open a discussion or issue with the "question" label

## Development Tips

### Useful Make Targets

```bash
make install          # Install package with pip
make build-plugin     # Build distribution
make clean            # Remove build artifacts
```

### Testing Different Question Types

The `example/` directory contains examples of all question types. Modify these to test your changes.

### Updating Dependencies

```bash
# Update all dependencies
uv pip install --upgrade -e .[dev]

# Update pre-commit hooks
pre-commit autoupdate
```

### Performance Testing

Check bundle size:

```bash
du -sh mkdocs_exam/css/exam.css
du -sh mkdocs_exam/js/exam.js
```

### Accessibility Testing

- Test with screen readers (NVDA, JAWS, VoiceOver)
- Test keyboard navigation (Tab, Space, Enter)
- Check color contrast ratios
- Test with dark mode enabled

## Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!
