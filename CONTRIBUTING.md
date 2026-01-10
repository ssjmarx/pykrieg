# Contributing to Pykrieg

Thank you for your interest in contributing to Pykrieg! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. Be constructive, welcoming, and respectful in all interactions.

## Getting Started

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/pykrieg.git
   cd pykrieg
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

5. Install pre-commit hooks (optional but recommended):
   ```bash
   pre-commit install
   ```

## Development Workflow

### Branch Strategy

- `main`: Stable production code
- Create feature branches from `main`: `feature/your-feature-name`
- Use descriptive branch names

### Making Changes

1. Create a new branch for your feature or bugfix
2. Make your changes following the coding standards below
3. Write tests for your changes
4. Ensure all tests pass: `pytest`
5. Run linting: `ruff check .` and `mypy src/`
6. Format code: `black .` and `isort .`
7. Commit your changes with a clear message
8. Push to your fork
9. Submit a pull request

### Commit Messages

Follow conventional commits format:
- `feat: add new unit type system`
- `fix: resolve combat calculation bug`
- `docs: update API documentation`
- `test: add integration tests for movement`
- `refactor: simplify board representation`

## Coding Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use Black for formatting (line length: 100)
- Use isort for import sorting
- Use type hints for all function signatures
- Include docstrings for all public functions and classes
- Use descriptive variable names

### Testing

- Maintain minimum 85% code coverage (90%+ for core game logic)
- Write unit tests for individual components
- Write integration tests for component interactions
- Use pytest markers to categorize tests:
  - `@pytest.mark.unit`: Unit tests
  - `@pytest.mark.integration`: Integration tests
  - `@pytest.mark.slow`: Slow tests

### Documentation

- Update README.md if user-facing changes
- Add/update docstrings for modified code
- Include examples in docstrings
- Update inline comments for complex logic

## Pull Request Process

### Before Submitting

- Ensure your code passes all tests
- Update documentation as needed
- Add tests for new functionality
- Run pre-commit hooks locally

### Pull Request Template

When submitting a PR, include:

1. **Description**: What changes were made and why
2. **Type of change**: Bug fix, new feature, breaking change, documentation
3. **Testing**: How the changes were tested
4. **Screenshots**: If UI changes, include screenshots
5. **Related Issues**: Reference any related issues

### Review Process

- Maintainers will review your PR
- Address feedback from reviewers
- Once approved, your PR will be merged
- Thank you for your contribution!

## Development Phases

This project follows a phased approach (see `docs/prompt`). When contributing, consider which phase your changes align with:

- **Phase 1**: Foundation and Core Infrastructure
- **Phase 2**: Core Game Mechanics
- **Phase 3**: Advanced Mechanics
- **Phase 4**: Integration and Polish
- **Phase 5**: Community and Ecosystem

## Reporting Issues

When reporting bugs or requesting features:

1. Search existing issues first
2. Use appropriate issue templates
3. Provide clear, reproducible bug reports
4. Include environment information (Python version, OS)
5. Add relevant code examples or screenshots

## Questions and Support

- Open a GitHub issue for bugs or feature requests
- Use GitHub Discussions for questions
- Check existing documentation before asking

## Recognition

Contributors will be acknowledged in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for helping make Pykrieg better!
