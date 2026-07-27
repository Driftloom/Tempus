# Contributing to TEMPUS

Thank you for your interest in contributing to TEMPUS! This document provides guidelines for contributing to the project.

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- pnpm (for monorepo management)

### Development Setup

1. **Clone the repository:**
```bash
git clone https://github.com/tempus-ai/tempus.git
cd tempus
```

2. **Install dependencies:**
```bash
# Install Python dependencies
cd apps/core
pip install -e ".[dev]"

# Install Node.js dependencies
cd apps/chrome-extension
pnpm install

cd apps/vscode-extension
pnpm install

cd packages/core-sdk
pnpm install
```

3. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run database migrations:**
```bash
cd apps/core
alembic upgrade head
```

5. **Start development servers:**
```bash
# Start backend
cd apps/core
uvicorn app.main:app --reload --port 8000

# Start Chrome extension (in another terminal)
cd apps/chrome-extension
pnpm dev

# Start VS Code extension (in another terminal)
cd apps/vscode-extension
pnpm dev
```

## Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Critical fixes

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions/changes
- `chore`: Build process or auxiliary tool changes

**Example:**
```
feat(tasks): add task priority sorting

Add ability to sort tasks by priority level in the task list view.
Implements user request from issue #123.
```

### Pull Request Process

1. **Create a branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**
- Write code following project standards
- Add tests for new functionality
- Update documentation as needed

3. **Commit your changes:**
```bash
git add .
git commit -m "feat: your feature description"
```

4. **Push to GitHub:**
```bash
git push origin feature/your-feature-name
```

5. **Create Pull Request:**
- Go to GitHub and create PR
- Fill out PR template
- Link to related issues
- Request reviews from maintainers

### PR Review Checklist

- [ ] Code follows project style guidelines
- [ ] Code includes appropriate tests
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] No breaking changes without discussion
- [ ] Security implications considered

## Coding Standards

### Python

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Maximum line length: 100 characters
- Use meaningful variable names

### TypeScript

- Follow ESLint rules
- Use TypeScript strict mode
- Write JSDoc comments
- Maximum line length: 100 characters
- Use meaningful variable names

### Testing

- Write unit tests for all new functions
- Write integration tests for API endpoints
- Maintain > 90% test coverage
- Use descriptive test names

## Documentation

### Code Documentation

- All public functions must have docstrings
- Complex logic must be commented
- Update README.md for user-facing changes

### API Documentation

- Update OpenAPI specification for API changes
- Add examples for new endpoints
- Document breaking changes

## Issue Reporting

### Bug Reports

Include:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Screenshots (if applicable)

### Feature Requests

Include:
- Description of the feature
- Use case for the feature
- Proposed implementation (if known)
- Potential alternatives considered

## Questions and Discussion

For questions and discussion:
- GitHub Discussions for general questions
- GitHub Issues for bugs and feature requests
- Discord/Slack for real-time chat (if available)

## License

By contributing to TEMPUS, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project website (if applicable)

Thank you for contributing to TEMPUS!
