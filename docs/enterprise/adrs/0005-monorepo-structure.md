# ADR-005: Monorepo Structure

## Status

Accepted

## Context

TEMPUS consists of multiple components:
- Core backend (Python/FastAPI)
- Chrome extension (TypeScript/React)
- VS Code extension (TypeScript)
- Core SDK (TypeScript/Python)

We need to decide between monorepo and polyrepo structure.

## Decision

We chose a monorepo structure using pnpm for TypeScript workspaces and uv for Python dependency management.

## Rationale

### Monorepo Advantages

**1. Code Sharing**
- Shared TypeScript types across extensions
- Shared SDK code
- Shared utilities and helpers
- Single source of truth

**2. Simplified CI/CD**
- Single CI pipeline for all components
- Atomic commits across components
- Simplified release management
- Unified testing

**3. Dependency Management**
- pnpm workspaces for TypeScript
- uv for Python dependency management
- Shared dependencies where possible
- Consistent versions across components

**4. Developer Experience**
- Single repository clone
- Cross-component development
- Unified tooling
- Simplified onboarding

**5. Versioning**
- Semantic versioning across components
- Coordinated releases
- Simplified dependency tracking

### Tooling

**TypeScript Workspaces**
- pnpm for efficient workspace management
- Shared dependencies via workspace protocol
- Build scripts in root package.json
- TypeScript project references

**Python Management**
- uv for fast Python dependency management
- Shared Python packages via local packages
- Virtual environment per component
- Lock files for reproducibility

### Alternatives Considered

**Polyrepo**
- Pros: Independent versioning, clear boundaries
- Cons: Code duplication, complex CI/CD, dependency hell

**Turborepo**
- Pros: Build system optimization
- Cons: Additional complexity, not needed for current scale

**Nx**
- Pros: Powerful monorepo tools
- Cons: Overkill for current needs, steep learning curve

## Consequences

### Positive

- **Code Sharing**: Shared types, SDK, utilities
- **CI/CD**: Simplified pipeline, atomic commits
- **Developer Experience**: Single repo, unified tooling
- **Versioning**: Coordinated releases
- **Dependencies**: Efficient workspace management

### Negative

- **Repo Size**: Larger repository
- **Build Time**: Longer builds (mitigated with caching)
- **Tooling**: More complex tooling setup

## Mitigation Strategies

- **Repo Size**: Git LFS for large files if needed
- **Build Time**: pnpm build caching, parallel builds
- **Tooling**: Well-documented setup scripts
- **CI/CD**: Cached dependencies, parallel jobs

## References

- pnpm Workspaces: https://pnpm.io/workspaces
- uv Documentation: https://github.com/astral-sh/uv
- Monorepo Best Practices: https://monorepo.tools/
