# TEMPUS Testing & QA Strategy

## Overview

TEMPUS implements a comprehensive testing strategy covering unit tests, integration tests, contract tests, API tests, database tests, performance tests, load tests, security tests, and end-to-end tests. This strategy ensures code quality, system reliability, and security across all components.

## Testing Pyramid

```
                    ┌─────────────────┐
                    │   E2E Tests     │
                    │   (10%)         │
                    │  Playwright,    │
                    │  VS Code Tests  │
                    └─────────────────┘
                  ┌─────────────────────┐
                  │  Integration Tests   │
                  │  (30%)              │
                  │  API, Database,     │
                  │  Service Integration │
                  └─────────────────────┘
                ┌───────────────────────────┐
                │     Unit Tests             │
                │     (60%)                  │
                │     Service, Repository,   │
                │     Utility Functions      │
                └───────────────────────────┘
```

## Testing Types

### Unit Tests

**Purpose**: Test individual functions and classes in isolation

**Coverage Target**:
- Critical path: 100%
- Overall: 90%+

**Tools**:
- Python: `pytest` with `pytest-cov`
- TypeScript: `vitest` with coverage

**Examples**:
```python
# Test memory classification
def test_classify_working_memory():
    content = "User is currently looking at the Q3 report tab"
    layer = layer_classifier.classify(content, source="browser")
    assert layer == MemoryLayer.WORKING

# Test task parsing
def test_parse_task_with_due_date():
    input_text = "Finish the SafeVixAI README by tomorrow 9am"
    task = nl_parser.parse(input_text)
    assert task.due_at is not None
    assert task.title == "Finish the SafeVixAI README"
```

### Integration Tests

**Purpose**: Test interactions between components

**Coverage Target**: 80%+ of integration points

**Tools**:
- Python: `pytest` with `httpx.AsyncClient`
- TypeScript: `vitest` with test containers

**Examples**:
```python
# Test API integration
async def test_create_task_via_api():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/tasks",
            json={"input": "Test task", "source": "test"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["task"]["title"] == "Test task"

# Test database integration
async def test_memory_repository_create_and_query():
    memory = await memory_repo.create(
        content="Test memory",
        layer=MemoryLayer.SEMANTIC,
        user_id=test_user_id
    )
    queried = await memory_repo.query(
        query="test",
        user_id=test_user_id
    )
    assert len(queried) == 1
    assert queried[0].id == memory.id
```

### Contract Tests

**Purpose**: Verify API contracts between services

**Coverage Target**: 100% of public APIs

**Tools**:
- OpenAPI specification validation
- Schema validation tests

**Examples**:
```python
# Test OpenAPI schema compliance
def test_api_response_matches_schema():
    response = client.get("/api/v1/tasks")
    schema = openapi_schema["components"]["schemas"]["TaskListResponse"]
    validate(instance=response.json(), schema=schema)
```

### API Tests

**Purpose**: Test REST API endpoints

**Coverage Target**: 100% of API endpoints

**Tools**:
- Python: `pytest` with `httpx.AsyncClient`
- TypeScript: API testing frameworks

**Test Categories**:
- Happy path tests
- Error handling tests
- Authentication/authorization tests
- Rate limiting tests
- Input validation tests

**Examples**:
```python
# Test task creation endpoint
async def test_create_task_endpoint():
    response = await client.post(
        "/api/v1/tasks",
        json={"input": "Test task", "source": "test"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "task" in response.json()

# Test unauthorized access
async def test_unauthorized_access():
    response = await client.get("/api/v1/tasks")
    assert response.status_code == 401
```

### Database Tests

**Purpose**: Test database operations and migrations

**Coverage Target**: 100% of database operations

**Tools**:
- Test containers for PostgreSQL
- Alembic migration testing

**Test Categories**:
- CRUD operations
- Migration up/down
- Data integrity
- Performance queries
- Transaction handling

**Examples**:
```python
# Test repository operations
async def test_task_repository_crud():
    # Create
    task = await task_repo.create(
        title="Test task",
        user_id=test_user_id
    )
    assert task.id is not None
    
    # Read
    fetched = await task_repo.get(task.id)
    assert fetched.title == "Test task"
    
    # Update
    updated = await task_repo.update(
        task.id,
        title="Updated task"
    )
    assert updated.title == "Updated task"
    
    # Delete
    await task_repo.delete(task.id)
    with pytest.raises(NotFound):
        await task_repo.get(task.id)
```

### Performance Tests

**Purpose**: Verify performance requirements

**Performance Targets**:
- API latency p95: < 200ms
- Memory query p95: < 300ms
- Agent step p95: < 5s

**Tools**:
- Python: `pytest-benchmark`
- Locust for load testing
- k6 for performance testing

**Examples**:
```python
# Benchmark memory query
def test_memory_query_performance(benchmark):
    result = benchmark(
        memory_service.query,
        query="test query",
        user_id=test_user_id
    )
    assert len(result) > 0

# Test API latency
def test_api_latency_performance():
    start = time.time()
    response = client.get("/api/v1/tasks")
    duration = time.time() - start
    assert duration < 0.2  # 200ms
```

### Load Tests

**Purpose**: Verify system behavior under load

**Load Scenarios**:
- 100 concurrent users
- 1000 tasks created per minute
- 100 memory queries per second
- 10 concurrent agent runs

**Tools**:
- Locust for Python load testing
- k6 for general load testing

**Example**:
```python
# Locust load test
class TaskUser(HttpUser):
    wait_time = between(1, 5)
    
    def on_start(self):
        self.login()
    
    @task
    def create_task(self):
        self.client.post(
            "/api/v1/tasks",
            json={"input": "Load test task", "source": "test"}
        )
    
    @task
    def list_tasks(self):
        self.client.get("/api/v1/tasks")
```

### Security Tests

**Purpose**: Verify security vulnerabilities are mitigated

**Coverage Target**: OWASP Top 10 + AI-specific security

**Tools**:
- SAST: Bandit, Semgrep
- DAST: OWASP ZAP
- Dependency scanning: Snyk, Dependabot
- Custom security tests

**Test Categories**:
- Authentication/authorization
- Input validation
- SQL injection
- XSS prevention
- CSRF protection
- Rate limiting
- Encryption verification
- Guardrails effectiveness

**Examples**:
```python
# Test SQL injection protection
def test_sql_injection_protection():
    malicious_input = "'; DROP TABLE tasks; --"
    response = client.post(
        "/api/v1/tasks",
        json={"input": malicious_input, "source": "test"}
    )
    assert response.status_code == 400  # Validation error
    
# Test permission denial
def test_permission_denial():
    # Create skill without write_tasks permission
    skill_id = create_skill(permissions=["read_tasks"])
    
    # Try to create task via skill
    response = client.post(
        f"/api/v1/skills/{skill_id}/execute",
        json={"action": "create_task"}
    )
    assert response.status_code == 403
```

### End-to-End Tests

**Purpose**: Test complete user workflows

**Coverage Target**: Critical user workflows

**Tools**:
- Chrome Extension: Playwright
- VS Code Extension: VS Code test runner

**Test Scenarios**:
- Chrome Extension:
  - Quick capture creates task
  - Memory search returns results
  - Connector status displays
  - Notification received
  
- VS Code Extension:
  - Timer start/stop
  - TODO to task conversion
  - Command palette actions

**Examples**:
```typescript
// Playwright E2E test for Chrome extension
test('quick capture creates task', async ({ page }) => {
  await page.goto('chrome-extension://<id>/side-panel.html');
  
  await page.fill('[data-testid="quick-capture-input"]', 'Test task');
  await page.click('[data-testid="quick-capture-submit"]');
  
  await expect(page.locator('[data-testid="task-list"]')).toContainText('Test task');
});
```

## Test Organization

### Directory Structure
```
apps/core/test/
├── unit/                    # Unit tests
│   ├── services/
│   ├── repositories/
│   └── utils/
├── integration/             # Integration tests
│   ├── api/
│   ├── database/
│   └── services/
├── contract/               # Contract tests
│   └── openapi/
├── performance/            # Performance tests
│   └── benchmarks/
├── security/               # Security tests
│   ├── injection/
│   ├── authorization/
│   └── encryption/
└── e2e/                    # End-to-end tests
    └── scenarios/

test/
├── e2e/
│   ├── chrome/             # Chrome extension E2E
│   └── vscode/             # VS Code extension E2E
└── load/                   # Load tests
    └── scenarios/
```

### Test Data Management

**Fixtures**: Reusable test data and configurations

**Test Database**: Separate test database with known state

**Test Data**: Synthetic test data, no real user data

**Cleanup**: Automatic cleanup after each test

## Continuous Integration

### CI Pipeline

**Python Pipeline**:
```yaml
- Install dependencies (uv)
- Run linter (ruff)
- Run type checker (mypy)
- Run unit tests (pytest with coverage)
- Run integration tests (pytest)
- Run security tests (bandit, safety)
- Upload coverage reports
```

**TypeScript Pipeline**:
```yaml
- Install dependencies (pnpm)
- Run linter (eslint)
- Run type checker (tsc)
- Run unit tests (vitest with coverage)
- Run integration tests
- Upload coverage reports
```

**E2E Pipeline**:
```yaml
- Build extensions
- Start test environment (docker-compose)
- Run Chrome E2E tests (Playwright)
- Run VS Code E2E tests
- Stop test environment
- Upload test results
```

### Coverage Gates

**Minimum Coverage**:
- Python: 90% overall, 100% critical path
- TypeScript: 85% overall, 95% critical path

**Coverage Reports**:
- HTML coverage reports
- Coverage trends over time
- PR coverage diffs

### Quality Gates

**All PRs Must Pass**:
- Linting: No errors
- Type checking: No errors
- Unit tests: 100% pass rate
- Integration tests: 100% pass rate
- Coverage: Above minimum threshold
- Security scans: No critical vulnerabilities

## Test Data Management

### Test Fixtures

**User Fixtures**:
```python
@pytest.fixture
def test_user():
    return User(
        id="test-user-id",
        email="test@example.com",
        display_name="Test User"
    )

@pytest.fixture
def test_task(test_user):
    return Task(
        id="test-task-id",
        title="Test Task",
        user_id=test_user.id,
        status=TaskStatus.PENDING
    )
```

### Test Database

**Setup**:
```python
@pytest.fixture(scope="session")
def test_db():
    # Create test database
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    # Cleanup
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(test_db):
    Session = sessionmaker(bind=test_db)
    session = Session()
    yield session
    session.rollback()
    session.close()
```

### Test Data Factory

**Factory Boy**:
```python
class TaskFactory(factory.Factory):
    class Meta:
        model = Task
    
    id = factory.Sequence(lambda n: f"task-{n}")
    title = factory.Faker('sentence')
    status = TaskStatus.PENDING
    user_id = factory.LazyAttribute(lambda o: test_user.id)
```

## Testing Best Practices

### Test Naming
- Descriptive test names that explain what is being tested
- Use `test_<function>_<scenario>_<expected_result>` format

### Test Independence
- Each test should be independent
- No shared state between tests
- Proper setup and teardown

### Test Speed
- Unit tests should run in < 1 second
- Integration tests should run in < 10 seconds
- Use mocking for external dependencies

### Test Maintenance
- Regular test maintenance
- Remove obsolete tests
- Update tests for code changes
- Keep tests DRY (Don't Repeat Yourself)

### Test Documentation
- Document complex test scenarios
- Explain why certain tests exist
- Document test data requirements

## Regression Testing

### Regression Test Suite
- Critical path tests
- High-risk functionality
- Security-critical components
- Performance-critical paths

### Regression Prevention
- Automated regression gating in CI
- Performance regression detection
- Security regression detection
- API contract regression detection

### Regression Testing Schedule
- Every PR: Automated regression tests
- Nightly: Full regression suite
- Weekly: Performance regression tests
- Monthly: Security regression tests

## Test Reporting

### Test Reports
- HTML test reports
- Coverage reports
- Performance reports
- Security scan reports

### Metrics
- Test execution time
- Test pass rate
- Coverage percentage
- Flaky test rate

### Alerts
- Test failures in CI
- Coverage drops
- Performance regressions
- Security vulnerabilities

## Conclusion

TEMPUS implements a comprehensive testing strategy covering all aspects of the system. The combination of unit tests, integration tests, contract tests, API tests, database tests, performance tests, security tests, and end-to-end tests ensures code quality, system reliability, and security.

Regular review and updates to the testing strategy ensure it remains effective as the system evolves and testing best practices improve.
