# TEMPUS OWASP Top 10 Mapping

## Overview

This document maps TEMPUS security controls to the OWASP Top 10 2021 security risks, demonstrating how the system addresses each category of web application security risk.

## OWASP Top 10 2021 Mapping

### A01:2021 – Broken Access Control

**Description**: Users can act outside of their intended permissions.

**TEMPUS Controls**:
- **Device-Based Authentication**: Unique device tokens with JWT session management
- **RBAC Implementation**: Role-based access control with scoped permissions
- **ABAC Implementation**: Attribute-based access control for fine-grained permissions
- **Runtime Permission Checks**: Re-validation of permissions at tool call time
- **Least Privilege Principle**: Skills and agents granted minimum required permissions
- **Permission Audit Trail**: All permission grants and revocations logged
- **API Authorization**: FastAPI dependency injection for auth checks on all endpoints
- **CORS Enforcement**: Locked to extension origins only

**Evidence**:
- `apps/core/app/auth/device_auth.py` - Device authentication
- `apps/core/app/auth/jwt_handler.py` - JWT token management
- `apps/core/app/mcp_host/permissions/permission_service.py` - Runtime permission checks
- `apps/core/app/guardrails/tool_authorization.py` - Tool authorization

**Testing**:
- Permission escalation tests in `test/security/test_tool_authorization.py`
- Access control tests in integration test suite

**Residual Risk**: Low

---

### A02:2021 – Cryptographic Failures

**Description**: Failures related to cryptography (or lack thereof), leading to exposure of sensitive data.

**TEMPUS Controls**:
- **Encryption at Rest**: AES-256-GCM for sensitive data (credentials, tokens)
- **Encryption in Transit**: TLS 1.3 for all external communications
- **Key Management**: Separate encryption keys from encrypted data
- **PII Redaction**: Automatic PII detection and redaction before cloud calls
- **Sensitivity-Based Routing**: High-sensitivity data processed locally only
- **Secure Random Generation**: Cryptographically secure random for tokens and keys
- **Hashed Passwords**: Argon2 for password hashing (if applicable)
- **Certificate Management**: Proper certificate validation and pinning

**Evidence**:
- `apps/core/app/database/crypto.py` - Encryption helpers
- `apps/core/app/guardrails/pii/pii_redactor.py` - PII redaction
- `apps/core/app/router/policy/routing_policy.py` - Sensitivity routing
- TLS configuration in FastAPI and all external clients

**Testing**:
- Encryption audit tests in `test/security/test_encryption_audit.py`
- PII redaction tests in `test/guardrails/test_pii_redaction.py`

**Residual Risk**: Low

---

### A03:2021 – Injection

**Description**: Injection vulnerabilities (SQL, NoSQL, OS command, etc.)

**TEMPUS Controls**:
- **ORM Usage**: SQLAlchemy 2.0 with SQLModel exclusively (no raw SQL)
- **Parameterized Queries**: All database queries use ORM parameterization
- **Input Validation**: Pydantic schema validation on all API inputs
- **Output Encoding**: Proper encoding for all outputs
- **Subprocess Isolation**: No shell=True in subprocess calls, parameter sanitization
- **Command Injection Prevention**: Strict input sanitization for subprocess parameters
- **XSS Protection**: Content Security Policy (CSP) headers
- **SQL Injection Prevention**: ORM prevents SQL injection entirely

**Evidence**:
- All database access via `apps/core/app/database/repositories/` using SQLAlchemy
- Pydantic models for all API inputs in `apps/core/app/api/`
- Subprocess isolation in `apps/core/app/mcp_host/skills/skill_runner.py`
- CSP headers in `apps/core/app/security/cors_config.py`

**Testing**:
- SQL injection tests in integration test suite
- Command injection tests in `test/security/test_sandbox_escape.py`

**Residual Risk**: Very Low

---

### A04:2021 – Insecure Design

**Description**: Design flaws that lead to security vulnerabilities.

**TEMPUS Controls**:
- **Threat Modeling**: Comprehensive threat model documented and reviewed
- **Secure by Design**: Security considered from initial architecture
- **Defense in Depth**: Multiple security controls at each layer
- **Zero Trust Architecture**: Verify all requests, regardless of source
- **Guardrails Layer**: Multi-layer security checks for autonomous actions
- **Provenance Tagging**: Content provenance tracked throughout system
- **Human-in-the-Loop**: Approval required for high-impact actions
- **Security Requirements**: Security requirements in all component specifications

**Evidence**:
- `docs/enterprise/threat-model.md` - Comprehensive threat model
- `apps/core/app/guardrails/` - Multi-layer guardrails implementation
- Provenance tagging in `apps/core/app/guardrails/injection_defense/provenance.py`
- Architecture Decision Records (ADRs) for security decisions

**Testing**:
- Threat model review in security audits
- Design reviews in architecture reviews

**Residual Risk**: Low

---

### A05:2021 – Security Misconfiguration

**Description**: Misconfiguration of security settings, headers, or services.

**TEMPUS Controls**:
- **Infrastructure as Code**: Terraform/Kubernetes for consistent deployment
- **Secure Defaults**: Secure configurations by default
- **Hardened Images**: Minimal container images, no unnecessary packages
- **Configuration Management**: Environment-based configuration with validation
- **Security Headers**: Proper security headers (CSP, HSTS, X-Frame-Options)
- **CORS Configuration**: Locked to specific origins only
- **Secrets Management**: Environment variables for secrets, no hardcoded secrets
- **Startup Validation**: Secrets check fails fast if required secrets missing

**Evidence**:
- `apps/core/app/security/secrets_check.py` - Startup secrets validation
- `apps/core/app/security/cors_config.py` - CORS configuration
- `infra/docker-compose.yml` - Secure default configurations
- Terraform templates for infrastructure

**Testing**:
- Configuration validation in startup tests
- Security header validation in integration tests
- Secrets validation in CI/CD

**Residual Risk**: Low

---

### A06:2021 – Vulnerable and Outdated Components

**Description**: Use of components with known vulnerabilities.

**TEMPUS Controls**:
- **Dependency Pinning**: Lock files for Python (uv) and TypeScript (pnpm)
- **Regular Updates**: Automated dependency updates via Dependabot
- **Vulnerability Scanning**: Snyk, Dependabot, Trivy for vulnerability scanning
- **SBOM Generation**: Software Bill of Materials for all components
- **Container Scanning**: Image scanning in CI/CD pipeline
- **Private Registry**: Private package registry for critical dependencies
- **Patch Management**: Regular security patching
- **Component Inventory**: Complete inventory of all components

**Evidence**:
- `pyproject.lock` and `pnpm-lock.yaml` for dependency pinning
- GitHub Dependabot configuration
- SBOM generation in CI/CD
- Container scanning in `.github/workflows/`

**Testing**:
- Vulnerability scanning in CI/CD
- Dependency review in security audits

**Residual Risk**: Low

---

### A07:2021 – Identification and Authentication Failures

**Description**: Failures in user identity authentication and session management.

**TEMPUS Controls**:
- **Device-Based Authentication**: Unique device tokens for local-first deployment
- **JWT Implementation**: Short-lived JWT tokens with refresh mechanism
- **Secure Token Storage**: Tokens stored in secure storage (chrome.storage.local, SecretStorage)
- **Session Management**: Secure session handling with timeouts
- **Multi-Factor Authentication**: Support for MFA (future enhancement)
- **OAuth2 Implementation**: Proper OAuth2 flows for external services
- **Token Rotation**: Automatic token rotation for long-lived tokens
- **Session Invalidation**: Session invalidation on suspicious activity

**Evidence**:
- `apps/core/app/auth/device_auth.py` - Device authentication
- `apps/core/app/auth/jwt_handler.py` - JWT implementation
- OAuth2 flows in `apps/core/app/auth/oauth/oauth_flow_router.py`

**Testing**:
- Authentication tests in integration test suite
- Token validation tests in unit tests

**Residual Risk**: Low

---

### A08:2021 – Software and Data Integrity Failures

**Description**: Failures in software and data integrity, including CI/CD pipelines.

**TEMPUS Controls**:
- **Code Signing**: Skill and connector signing (future enhancement)
- **Immutable Infrastructure**: Immutable container images
- **CI/CD Security**: Branch protection, required reviews, security checks
- **Supply Chain Security**: Verified sources, SBOM generation
- **Backup Integrity**: Cryptographic verification of backups
- **Audit Log Immutability**: WORM storage for audit logs
- **Change Management**: Documented change management process
- **Data Validation**: Input validation on all data inputs

**Evidence**:
- GitHub Actions with required reviews
- Immutable container images in CI/CD
- Audit log immutability in database design
- Input validation via Pydantic models

**Testing**:
- Integrity checks in backup/restore tests
- Supply chain security in CI/CD tests

**Residual Risk**: Low

---

### A09:2021 – Security Logging and Monitoring Failures

**Description**: Failures in logging, monitoring, and incident response.

**TEMPUS Controls**:
- **Structured Logging**: JSON structured logging with consistent fields
- **Request Correlation**: Request IDs for log correlation
- **Comprehensive Logging**: All security-relevant events logged
- **Audit Trail**: Complete audit trail for all actions
- **Real-Time Monitoring**: Real-time security monitoring
- **Alerting**: Automated alerting for security events
- **Log Retention**: Appropriate log retention policies
- **Incident Response**: Documented incident response plan

**Evidence**:
- `apps/core/app/observability/logging/structured_logger.py` - Structured logging
- `apps/core/app/observability/metrics/metrics.py` - Metrics collection
- `apps/core/app/observability/tracing/otel_setup.py` - Distributed tracing
- Complete audit logging in all services

**Testing**:
- Logging completeness tests in `test/security/`
- Monitoring validation in integration tests

**Residual Risk**: Low

---

### A10:2021 – Server-Side Request Forgery (SSRF)

**Description**: Server-side request forgery vulnerabilities.

**TEMPUS Controls**:
- **URL Validation**: Strict validation of all URLs
- **Allowlist**: Allowlist for permitted external services
- **Network Segmentation**: Network segmentation for external calls
- **Request Limitation**: Rate limiting on external requests
- **Response Validation**: Validation of external service responses
- **No Internal Access**: No access to internal metadata services
- **Proxy Configuration**: Proper proxy configuration for external calls
- **Timeout Enforcement**: Timeouts on all external requests

**Evidence**:
- URL validation in connector implementations
- Allowlist in `apps/core/app/router/gateway/provider_config.py`
- Rate limiting in `apps/core/app/security/rate_limit.py`

**Testing**:
- SSRF tests in security test suite
- External request validation tests

**Residual Risk**: Low

---

## Additional Security Considerations

### AI-Specific Security

**Prompt Injection**:
- Provenance tagging for all content
- Injection classifier for suspicious patterns
- Untrusted content cannot authorize tool calls
- Human-in-the-loop for high-risk actions
- Output filtering for instruction-following language

**Model Security**:
- Sensitivity-based routing (high → local only)
- PII redaction before cloud calls
- Budget enforcement to prevent cost attacks
- Prompt template management

**Agent Security**:
- Hard step ceiling to prevent infinite loops
- Budget enforcement (steps, time, cost)
- Cancellation support
- State validation
- Comprehensive audit logging

### Privacy-Specific Security

**Data Minimization**:
- Collect only necessary data
- Automatic data expiration (TTL for working memory)
- Right-to-be-forgotten API
- Data classification and routing

**Consent Management**:
- Explicit consent for data processing
- Granular permission controls
- Consent revocation
- Audit of consent changes

**Data Sovereignty**:
- Local-first deployment option
- Data residency controls
- No forced cloud processing
- User-controlled data location

## Security Testing Coverage

### Automated Testing
- **SAST**: Static application security testing in CI
- **DAST**: Dynamic application security testing in CI
- **Dependency Scanning**: Continuous dependency monitoring
- **Container Scanning**: Image scanning in CI/CD
- **Secret Scanning**: Automated secret detection

### Manual Testing
- **Penetration Testing**: Quarterly external penetration testing
- **Security Audits**: Annual comprehensive security audit
- **Code Reviews**: Security-focused code reviews
- **Architecture Reviews**: Security architecture reviews

### Continuous Monitoring
- **Vulnerability Monitoring**: Continuous vulnerability scanning
- **Security Monitoring**: Real-time security event monitoring
- **Compliance Monitoring**: Continuous compliance checking
- **Anomaly Detection**: Behavioral analysis for anomalies

## Compliance Mapping

### GDPR Compliance
- **Data Protection**: Encryption, access controls (A01, A02)
- **User Rights**: Right to access, rectification, erasure (A07)
- **Consent**: Consent management (A07)
- **Breach Notification**: Logging and monitoring (A09)

### SOC 2 Compliance
- **Security**: Access controls, encryption (A01, A02)
- **Availability**: Monitoring and incident response (A09)
- **Processing Integrity**: Audit logging (A09)
- **Confidentiality**: Data classification and protection (A02)
- **Privacy**: Consent and data minimization (A07)

### ISO 27001 Compliance
- **Information Security**: Comprehensive security controls (all categories)
- **Risk Management**: Threat modeling and risk assessment (A04)
- **Access Control**: RBAC and ABAC (A01)
- **Cryptography**: Encryption standards (A02)
- **Operations Security**: Change management and monitoring (A08, A09)

## Conclusion

TEMPUS addresses all OWASP Top 10 2021 security risks through comprehensive security controls implemented at multiple layers of the system. The defense-in-depth approach, combined with continuous security testing and monitoring, provides strong protection against common web application security vulnerabilities.

The key strengths are:
1. **Comprehensive Coverage**: All OWASP Top 10 risks addressed
2. **Defense in Depth**: Multiple controls at each layer
3. **AI-Specific Security**: Additional controls for AI-specific threats
4. **Privacy-First**: Strong privacy protections beyond OWASP
5. **Continuous Testing**: Automated and manual security testing
6. **Compliance Ready**: Designed for GDPR, SOC 2, ISO 27001 compliance

Regular security assessments and updates will ensure the security posture remains effective as threats evolve.
