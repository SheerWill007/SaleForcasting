# Contributing to Sales Forecasting

Thank you for your interest in contributing to the Sales Forecasting project! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [License Agreement](#license-agreement)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

There are many ways to contribute to this project:

- Report bugs and issues
- Suggest new features or enhancements
- Improve documentation
- Submit bug fixes
- Implement new features
- Review pull requests

## Reporting Bugs

Before creating a bug report, please check existing issues to avoid duplicates.

When filing a bug report, include:

- A clear and descriptive title
- Detailed steps to reproduce the issue
- Expected behavior vs. actual behavior
- Screenshots if applicable
- Environment details (OS, browser, Node.js version, Python version)
- Any relevant error messages or logs

## Suggesting Features

Feature suggestions are welcome! When proposing a new feature:

- Use a clear and descriptive title
- Provide a detailed description of the proposed feature
- Explain why this feature would be useful
- Include any relevant examples or mockups

## Development Setup

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Git

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend Setup

```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix/macOS:
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

uvicorn app.main:app --reload
```

The backend API will be available at `http://localhost:8000`

### Running Tests

#### Frontend Tests
```bash
cd frontend
npm test
```

#### Backend Tests
```bash
cd backend
pytest
```

## Pull Request Process

1. **Fork the repository** and create your branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our code style guidelines

3. **Add tests** for any new functionality

4. **Update documentation** as needed

5. **Ensure all tests pass**
   ```bash
   # Frontend
   cd frontend && npm test
   
   # Backend
   cd backend && pytest
   ```

6. **Commit your changes** with clear, descriptive commit messages
   ```bash
   git commit -m "feat: add feature description"
   ```

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request** with:
   - A clear title and description
   - Reference to any related issues
   - Screenshots for UI changes
   - Summary of changes made

9. **Wait for review** - maintainers will review your PR and may request changes

10. **Address feedback** if requested

## Code Style Guidelines

### Frontend (TypeScript/React)

- Use TypeScript for type safety
- Follow React best practices and hooks patterns
- Use functional components
- Format code with Prettier (automatically applied)
- Use meaningful variable and function names
- Add comments for complex logic

### Backend (Python)

- Follow PEP 8 style guide
- Use type hints for function signatures
- Write docstrings for functions and classes
- Keep functions focused and single-purpose
- Use meaningful variable names

### General Guidelines

- Write clean, readable, and maintainable code
- Keep functions small and focused
- Avoid deep nesting
- Use descriptive names for variables and functions
- Comment complex logic, not obvious code
- Remove commented-out code and debug statements

## Testing Requirements

All contributions should include appropriate tests:

### Frontend Testing

- Unit tests for utility functions
- Component tests for React components
- Integration tests for API interactions

### Backend Testing

- Unit tests for business logic
- API endpoint tests
- Model validation tests

### Test Coverage

- Aim for at least 70% code coverage for new code
- Critical paths should have 90%+ coverage
- All bug fixes should include a test that would have caught the bug

## Commit Message Guidelines

Use conventional commit format:

- `feat: ` - New feature
- `fix: ` - Bug fix
- `docs: ` - Documentation changes
- `style: ` - Code style changes (formatting, etc.)
- `refactor: ` - Code refactoring
- `test: ` - Adding or updating tests
- `chore: ` - Maintenance tasks

Examples:
```
feat: add inventory optimization algorithm
fix: correct forecast calculation for edge cases
docs: update API documentation for /forecast endpoint
```

## License Agreement

By contributing to this project, you agree that your contributions will be licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

You confirm that:

- You have the right to submit the contribution
- Your contribution is your original work or you have permission to submit it
- You understand and agree to the AGPL-3.0 license terms

## Questions?

If you have questions about contributing, feel free to:

- Open an issue with the `question` label
- Reach out to the maintainers

Thank you for contributing to Sales Forecasting!
