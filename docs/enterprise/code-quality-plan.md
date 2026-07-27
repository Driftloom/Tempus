# Code Quality Plan

## Executive Summary

This document outlines the code quality strategy for TEMPUS including linting, type checking, code formatting, consistency standards, and refactoring guidelines to achieve Fortune 500 production code quality.

## Code Quality Standards

### Python Standards

**Linting:**
- **Ruff** for fast linting
- **Bandit** for security linting
- **MyPy** for type checking
- **Black** for code formatting
- **isort** for import sorting

**Configuration:**

**ruff.toml:**
```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by black)
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
```

**pyproject.toml (MyPy):**
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

### TypeScript Standards

**Linting:**
- **ESLint** for linting
- **Prettier** for formatting
- **TypeScript** for type checking

**Configuration:**

**.eslintrc.json:**
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended"
  ],
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "no-console": "warn"
  }
}
```

**prettier.config.js:**
```javascript
module.exports = {
  semi: true,
  singleQuote: true,
  tabWidth: 2,
  trailingComma: 'es5',
  printWidth: 100
};
```

## Code Consistency

### Naming Conventions

**Python:**
- Classes: `PascalCase` (e.g., `TaskService`)
- Functions/Methods: `snake_case` (e.g., `create_task`)
- Variables: `snake_case` (e.g., `user_id`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- Private members: `_leading_underscore` (e.g., `_internal_method`)

**TypeScript:**
- Classes/Interfaces: `PascalCase` (e.g., `TaskComponent`)
- Functions/Methods: `camelCase` (e.g., `createTask`)
- Variables: `camelCase` (e.g., `userId`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- Private members: `_leadingUnderscore` (e.g., `_internalMethod`)

### File Organization

**Python Structure:**
```python
"""Module docstring."""

# Standard library imports
from datetime import datetime
from typing import Optional

# Third-party imports
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Local imports
from app.database.models.task import Task
from app.database.repositories.base import BaseRepository

# Constants
MAX_RETRIES = 3

# Classes
class TaskService:
    """Service class docstring."""
    
    def __init__(self):
        """Initialize service."""
        pass

# Functions
async def create_task(db: AsyncSession, task_data: dict) -> Task:
    """Create a new task."""
    pass
```

**TypeScript Structure:**
```typescript
// Standard library imports
import { useState, useEffect } from 'react';

// Third-party imports
import { Button } from '@shadcn/ui/button';

// Local imports
import { Task } from '@/types/task';

// Constants
const MAX_RETRIES = 3;

// Types
interface TaskProps {
  task: Task;
  onComplete: (id: string) => void;
}

// Components
export function TaskComponent({ task, onComplete }: TaskProps) {
  // Component implementation
}
```

### Docstring Standards

**Python Docstrings (Google Style):**
```python
def create_task(
    db: AsyncSession,
    user_id: str,
    title: str,
    priority: TaskPriority = TaskPriority.MEDIUM
) -> Task:
    """Create a new task for the user.
    
    Args:
        db: Database session for persistence.
        user_id: ID of the user creating the task.
        title: Title of the task.
        priority: Priority level of the task.
        
    Returns:
        The created Task object.
        
    Raises:
        ValueError: If title is empty.
        DatabaseError: If database operation fails.
        
    Example:
        >>> task = create_task(db, "user-123", "Test task")
        >>> print(task.id)
        'task-456'
    """
    pass
```

**TypeScript JSDoc:**
```typescript
/**
 * Creates a new task for the user.
 * 
 * @param userId - ID of the user creating the task
 * @param title - Title of the task
 * @param priority - Priority level of the task
 * @returns The created Task object
 * @throws {Error} If title is empty
 * 
 * @example
 * ```ts
 * const task = createTask('user-123', 'Test task');
 * console.log(task.id);
 * ```
 */
function createTask(
  userId: string,
  title: string,
  priority: TaskPriority = TaskPriority.MEDIUM
): Task {
  // Implementation
}
```

## Refactoring Guidelines

### Refactoring Triggers

**When to Refactor:**
- Code duplication > 3 times
- Function length > 50 lines
- Cyclomatic complexity > 10
- Class length > 300 lines
- Parameter count > 5
- Nesting depth > 4

### Refactoring Techniques

**1. Extract Method:**
```python
# Before
def process_task(task: Task):
    if task.status == TaskStatus.PENDING:
        if task.priority == TaskPriority.HIGH:
            send_notification(task.user_id, "High priority task pending")
        else:
            send_notification(task.user_id, "Task pending")
    elif task.status == TaskStatus.COMPLETED:
        send_notification(task.user_id, "Task completed")

# After
def process_task(task: Task):
    if task.status == TaskStatus.PENDING:
        handle_pending_task(task)
    elif task.status == TaskStatus.COMPLETED:
        handle_completed_task(task)

def handle_pending_task(task: Task):
    message = "High priority task pending" if task.priority == TaskPriority.HIGH else "Task pending"
    send_notification(task.user_id, message)

def handle_completed_task(task: Task):
    send_notification(task.user_id, "Task completed")
```

**2. Extract Class:**
```python
# Before
class TaskService:
    def __init__(self):
        self.notification_service = NotificationService()
        self.email_service = EmailService()
        self.sms_service = SMSService()
    
    def send_notification(self, user_id: str, message: str):
        # Complex notification logic
        pass

# After
class NotificationService:
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
    
    def send_notification(self, user_id: str, message: str):
        # Notification logic
        pass

class TaskService:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service
```

**3. Replace Conditional with Polymorphism:**
```python
# Before
def process_connector(connector_type: str):
    if connector_type == "gmail":
        return GmailConnector()
    elif connector_type == "outlook":
        return OutlookConnector()
    elif connector_type == "exchange":
        return ExchangeConnector()

# After
class ConnectorFactory:
    _connectors = {
        "gmail": GmailConnector,
        "outlook": OutlookConnector,
        "exchange": ExchangeConnector
    }
    
    @classmethod
    def create(cls, connector_type: str):
        connector_class = cls._connectors.get(connector_type)
        if not connector_class:
            raise ValueError(f"Unknown connector type: {connector_type}")
        return connector_class()
```

## Code Review Process

### Review Checklist

**Functionality:**
- [ ] Code implements the requirements
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] Logging is added where needed

**Code Quality:**
- [ ] Code follows naming conventions
- [ ] Code is properly documented
- [ ] Code is DRY (no duplication)
- [ ] Code is readable and maintainable

**Testing:**
- [ ] Unit tests are added
- [ ] Tests cover edge cases
- [ ] Tests are passing
- [ ] Coverage is adequate

**Security:**
- [ ] No hardcoded secrets
- [ ] Input validation is present
- [ ] SQL injection prevention
- [ ] XSS prevention

**Performance:**
- [ ] No unnecessary database queries
- [ ] Efficient algorithms used
- [ ] Proper caching implemented
- [ ] No memory leaks

### Review Guidelines

**Reviewer Responsibilities:**
- Provide constructive feedback
- Explain reasoning for changes
- Suggest improvements
- Approve only when satisfied

**Author Responsibilities:**
- Address all feedback
- Explain design decisions
- Update documentation
- Ensure tests pass

## Pre-commit Hooks

**Configuration (.pre-commit-config.yaml):**
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.6.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
  
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-ll]
```

## CI/CD Quality Gates

**Quality Gate Requirements:**
- Linting: No errors, no warnings
- Type checking: No errors
- Tests: 100% pass rate
- Coverage: > 90% overall, 100% critical path
- Security scans: No critical vulnerabilities

## Implementation Timeline

### Week 1: Linting and Type Checking
- Configure Ruff
- Configure MyPy
- Add pre-commit hooks
- Fix existing linting issues

### Week 2: Code Formatting
- Configure Black
- Configure Prettier
- Format all code
- Add formatting to CI

### Week 3: Refactoring
- Identify code duplication
- Refactor large functions
- Extract classes
- Apply design patterns

### Week 4: Documentation and Standards
- Document coding standards
- Create review checklist
- Train team on standards
- Implement quality gates

## Conclusion

This code quality plan provides comprehensive guidelines for linting, type checking, code formatting, consistency, and refactoring. Implementation will ensure code quality meets Fortune 500 production standards.

**Total Estimated Effort:** 80-120 hours
**Timeline:** 4 weeks for full implementation
