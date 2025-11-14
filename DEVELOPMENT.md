# Development Guide

This document provides information for developers contributing to mkdocs-exam.

## Table of Contents

- [Setup](#setup)
- [Type Checking with JSDoc](#type-checking-with-jsdoc)
- [Running Tests](#running-tests)
- [Code Style](#code-style)

## Setup

### Python Environment

```bash
# Clone the repository
git clone https://github.com/kjanat/mkdocs-exam.git
cd mkdocs-exam

# Install in editable mode
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```

### JavaScript/TypeScript Setup

```bash
# Install dependencies using bun (fast package manager)
bun install

# Alternative: using npm
npm install
```

**Note:** This project uses [bun](https://bun.sh) for faster package management and script execution. The `bun.lockb` file is committed for reproducible builds.

## Type Checking with JSDoc

This project uses **JSDoc comments** for JavaScript documentation and **TypeScript** for type checking (without compilation).

### Why JSDoc + TypeScript?

- **Documentation**: JSDoc provides inline documentation for all functions
- **Type Safety**: TypeScript validates types based on JSDoc annotations
- **No Build Step**: JavaScript runs directly in browsers, no compilation needed
- **IDE Support**: Modern editors provide autocomplete and type hints
- **Fast Type Checking**: Uses TypeScript Native Preview (Go implementation) for faster checks

### Running Type Checks

```bash
# Run type check once (using fast native TypeScript)
npm run typecheck

# Run type check in watch mode (continuous)
npm run typecheck:watch

# Type check with pretty output
npm run lint:types

# Legacy type check using standard TypeScript (slower)
npm run typecheck:legacy
```

**Performance:** The project uses `@typescript/native-preview` (TypeScript Native Port) which is significantly faster than the standard TypeScript compiler. This is especially noticeable on larger codebases or in watch mode.

### Writing JSDoc Comments

#### Function Documentation

```javascript
/**
 * Brief description of the function
 * @param {Type} paramName - Description of the parameter
 * @returns {ReturnType} Description of what is returned
 */
function myFunction(paramName) {
  // implementation
}
```

#### Type Definitions

```javascript
/**
 * @typedef {Object} MyType
 * @property {string} name - Person's name
 * @property {number} age - Person's age
 * @property {boolean} [isActive] - Optional: whether person is active
 */
```

#### Variable Types

```javascript
/** @type {string} - Description of the variable */
const MY_CONSTANT = "value";

/** @type {number[]} - Array of numbers */
const numbers = [1, 2, 3];
```

### Current Type Checking Configuration

The project uses a **pragmatic approach** to type checking:

- **JSDoc comments required**: All public functions must have JSDoc
- **Type checking disabled** (`checkJs: false`): Allows gradual adoption
- **Type definitions available**: `mkdocs_exam/js/types.d.ts` defines custom types

#### Files

- `tsconfig.json`: TypeScript configuration
- `package.json`: npm scripts for type checking
- `mkdocs_exam/js/types.d.ts`: Type definitions for custom properties
- `mkdocs_exam/js/exam.js`: Main JavaScript file with JSDoc comments

### Incremental Strictness

To enable stricter type checking in the future:

1. Edit `tsconfig.json`
2. Set `"checkJs": true`
3. Enable strict options:
   ```json
   {
     "compilerOptions": {
       "strict": true,
       "strictNullChecks": true,
       "noImplicitAny": true
     }
   }
   ```
4. Fix type errors incrementally
5. Run `npm run typecheck` to verify

## Running Tests

### Python Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_plugin.py

# Run with coverage
pytest --cov=mkdocs_exam

# Run in watch mode
pytest-watch
```

### Test Structure

```
tests/
├── test_plugin.py         # Main plugin tests (31 tests)
├── conftest.py           # Pytest configuration (if exists)
└── fixtures/             # Test fixtures (if exists)
```

## Code Style

### Python

- **PEP 8**: Follow Python style guide
- **Type Hints**: Use type hints where possible
- **Docstrings**: All public functions should have docstrings
- **Black**: Code formatting (if configured)
- **Ruff**: Linting (if configured)

### JavaScript

- **Semicolons**: Use semicolons
- **2-space indentation**: Consistent indentation
- **JSDoc**: All functions must have JSDoc comments
- **Naming**: camelCase for functions, UPPER_CASE for constants
- **Modern ES6+**: Use modern JavaScript features

### Example JavaScript Function

```javascript
/**
 * Save exam state to localStorage with timestamp
 * @param {number} examIndex - Zero-based index of exam on the page
 * @param {ExamState} state - The exam state to save
 * @returns {void}
 */
function saveExamState(examIndex, state) {
  try {
    /** @type {StoredExamData} */
    const data = {
      timestamp: Date.now(),
      state: state,
    };
    localStorage.setItem(getStorageKey(examIndex), JSON.stringify(data));
  } catch (e) {
    console.warn("Failed to save exam state:", e);
  }
}
```

## Git Workflow

### Branching

- `main`: Stable release branch
- `develop`: Development branch
- Feature branches: `feature/feature-name`
- Bug fixes: `fix/bug-name`

### Commit Messages

Use clear, descriptive commit messages:

```
Add JSDoc comments and type checking setup

- Add comprehensive JSDoc to all functions
- Create tsconfig.json for type validation
- Add type definitions in types.d.ts
- Update package.json with type check scripts
```

### Pull Requests

1. Create a feature branch
2. Make your changes
3. Add tests for new features
4. Run tests and type checks
5. Update documentation
6. Submit PR with clear description

## Documentation

### Updating Documentation

- **README.md**: Main user-facing documentation
- **TODO.md**: Feature roadmap and status
- **DEVELOPMENT.md**: This file (developer guide)
- **example/docs/**: Example pages with live demos

### Adding Examples

When adding new features:

1. Add example to `example/docs/`
2. Update `example/mkdocs.yml` navigation
3. Add comprehensive JSDoc comments
4. Write tests
5. Update TODO.md with completion status

## Troubleshooting

### Type Check Errors

If you see type errors:

1. Check JSDoc syntax is correct
2. Ensure types.d.ts includes necessary definitions
3. Consider adding `// @ts-ignore` for edge cases (sparingly)
4. If stuck, disable checking for that file temporarily

### Test Failures

1. Run `pytest -v` for detailed output
2. Check test isolation issues
3. Verify fixtures are correct
4. Clear `__pycache__` if stale

### Build Issues

```bash
# Clean build artifacts
rm -rf build/ dist/ *.egg-info/

# Reinstall
pip uninstall mkdocs-exam
pip install -e .
```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG (if exists)
3. Run all tests: `pytest -v`
4. Run type checks: `npm run typecheck`
5. Build: `python -m build`
6. Tag release: `git tag v0.x.0`
7. Push: `git push && git push --tags`
8. Publish to PyPI: `twine upload dist/*`

## Resources

- [MkDocs Plugin Development](https://www.mkdocs.org/dev-guide/plugins/)
- [JSDoc Reference](https://jsdoc.app/)
- [TypeScript JSDoc Support](https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html)
- [pytest Documentation](https://docs.pytest.org/)
