# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-04

### Added

- **Plugin Configuration**: Added configuration options for customizing exam behavior
  - `submit_text`: Customize submit button text (default: "Submit")
  - `reset_text`: Customize reset button text (default: "Try Again")
  - `show_score`: Toggle score display (default: true)
  - `allow_retry`: Toggle reset button (default: true)
  - `essay_rows`: Configure textarea rows for essay questions (default: 4)

- **Reset Functionality**: Added reset button to allow users to retry exams
- **Scoring System**: Added score display showing correct/total answers
- **Accessibility Improvements**:
  - Added ARIA attributes (`aria-label`, `aria-invalid`, `aria-live`)
  - Added screen reader announcements for exam results
  - Added checkmark (✓) and cross (✗) icons for visual feedback
  - Added keyboard focus management
  - Added support for `prefers-reduced-motion`
  - Added support for `prefers-contrast: high`

- **Error Handling**: Added comprehensive error handling with user-friendly error messages
- **XSS Protection**: Implemented HTML escaping for all user-provided content
- **Type Hints**: Added complete type annotations throughout the codebase
- **Test Coverage**:
  - Added pytest-cov for coverage reporting
  - Added 30+ comprehensive tests
  - Added edge case tests
  - Added XSS vulnerability tests

- **Documentation**:
  - Added CONTRIBUTING.md with development guidelines
  - Added this CHANGELOG.md
  - Added JSDoc comments to JavaScript code

### Changed

- **Code Organization**: Refactored into modular structure
  - Created `constants.py` for centralized configuration
  - Created `parser.py` for exam block parsing
  - Created `html_builder.py` for HTML generation
  - Improved separation of concerns

- **CSS Improvements**:
  - Added dark mode support via `prefers-color-scheme`
  - Added print styles
  - Added responsive design for mobile devices
  - Added CSS custom properties for theming
  - Added screen reader-only utility class (`.sr-only`)
  - Improved button styling with hover and active states

- **JavaScript Improvements**:
  - Added strict mode (`'use strict'`)
  - Added comprehensive JSDoc documentation
  - Refactored validation logic into separate functions
  - Improved accessibility with ARIA announcements

- **Performance**: CSS and JavaScript are now only injected on pages with exams

### Fixed

- **Security**: Fixed XSS vulnerability by escaping HTML in questions and answers
- **Validation**: Fixed edge cases in answer validation
- **Accessibility**: Fixed missing ARIA attributes and labels

### Removed

- Removed inline magic strings (now in constants.py)

## [0.1.0] - Initial Release

### Added

- Initial release with basic exam functionality
- Support for 7 question types:
  - Single choice (radio buttons)
  - Multiple choice (checkboxes)
  - True/false
  - Short answer
  - Fill in the blank
  - Essay
  - Matching
- Basic styling with Material Design theme integration
- Client-side validation
- MkDocs integration via plugin API
- Example documentation site

[0.2.0]: https://github.com/kjanat/mkdocs-exam/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/kjanat/mkdocs-exam/releases/tag/v0.1.0
