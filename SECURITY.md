# Security Policy

## Supported Versions

Currently supported versions of TEMPUS:

| Version | Supported Until |
|---------|----------------|
| 0.1.0   | TBD           |

## Reporting a Vulnerability

If you discover a security vulnerability in TEMPUS, please report it responsibly.

### How to Report

**Email:** security@tempus.ai

**Please Include:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any proof-of-concept code (if applicable)

### Response Time

- **Initial Response:** Within 24 hours
- **Detailed Assessment:** Within 48 hours
- **Patch Release:** Within 7 days (critical), 14 days (high)

### Disclosure Policy

TEMPUS follows responsible disclosure:

1. Acknowledge receipt of report within 24 hours
2. Investigate and validate the vulnerability
3. Develop and test a fix
4. Coordinate disclosure timeline with reporter
5. Release security advisory with fix
6. Credit reporter (if desired)

## Security Best Practices

### For Users

1. **Keep Dependencies Updated**
   - Regularly update TEMPUS to the latest version
   - Monitor security advisories

2. **Secure Configuration**
   - Use strong secrets for JWT and encryption
   - Enable HTTPS in production
   - Configure proper CORS policies
   - Use secrets manager for sensitive data

3. **Access Control**
   - Implement RBAC for multi-user environments
   - Use least privilege principle
   - Regularly review access permissions

4. **Monitoring**
   - Enable security logging
   - Set up security alerts
   - Monitor for suspicious activity

### For Developers

1. **Code Security**
   - Follow OWASP guidelines
   - Use parameterized queries
   - Validate all inputs
   - Sanitize all outputs

2. **Dependency Management**
   - Regularly update dependencies
   - Use dependency scanning tools
   - Review security advisories

3. **Testing**
   - Include security tests in CI/CD
   - Perform penetration testing
   - Conduct security code reviews

## Security Features

TEMPUS includes the following security features:

- **Authentication:** JWT-based authentication with refresh tokens
- **Authorization:** Role-based access control (RBAC)
- **Encryption:** AES-256 encryption for sensitive data
- **Input Validation:** Comprehensive input validation and sanitization
- **Output Encoding:** Automatic output encoding to prevent XSS
- **SQL Injection Protection:** Parameterized queries via SQLAlchemy
- **CSRF Protection:** CSRF tokens for state-changing operations
- **Rate Limiting:** Per-user and per-endpoint rate limiting
- **Security Headers:** OWASP-recommended security headers
- **Audit Logging:** Comprehensive audit trail for security events
- **Provenance Tracking:** Content source tracking for security
- **PII Redaction:** Automatic PII detection and redaction
- **Prompt Injection Defense:** Detection and blocking of injection attempts
- **OAuth2:** Secure OAuth2 flows for external connectors

## Security Audits

TEMPUS undergoes regular security audits:

- **Quarterly:** External penetration testing
- **Monthly:** Internal security review
- **Continuous:** Automated dependency scanning
- **On Release:** Security-focused code review

## Security Advisories

Past security advisories will be documented here.

### [2024-01-16] Initial Release
- No known vulnerabilities at initial release
