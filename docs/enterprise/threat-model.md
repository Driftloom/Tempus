# TEMPUS Threat Model

## Executive Summary

This threat model identifies potential security threats to the TEMPUS personal intelligence system and provides mitigation strategies. TEMPUS processes sensitive personal data (emails, tasks, memory) and performs autonomous actions, making security a critical concern.

## System Boundaries

### Trust Boundaries
1. **User Machine**: Trusted boundary for local processing
2. **TEMPUS Core**: Trusted boundary for data processing and storage
3. **External Services**: Untrusted boundary (cloud APIs, email providers)
4. **Connectors/Skills**: Semi-trusted boundary (user-installed code)

### Data Classification
- **High Sensitivity**: Health data, financial information, personal identifiers
- **Medium Sensitivity**: Work-related data, professional communications
- **Low Sensitivity**: General knowledge, public information, preferences

### Attack Surfaces
- **Web API**: REST and WebSocket endpoints
- **External Integrations**: OAuth flows, API calls to external services
- **Extension Communication**: Chrome and VS Code extension messages
- **Connector/Skill Execution**: MCP protocol, subprocess isolation
- **Agent Actions**: Autonomous tool execution

## Threat Categories

### 1. Authentication & Authorization Threats

#### Threat 1.1: Credential Theft
**Description**: Attacker steals device authentication tokens or OAuth tokens

**Impact**: High - Unauthorized access to user data and actions

**Likelihood**: Medium

**Attack Vector**:
- Malicious browser extension
- Compromised local machine
- Token storage vulnerability

**Mitigation**:
- Store tokens in secure storage (chrome.storage.local, VS Code SecretStorage)
- Use short-lived JWT tokens with refresh mechanism
- Implement token rotation
- Encrypt tokens at rest in database
- Monitor for suspicious token usage

**Residual Risk**: Low

#### Threat 1.2: Permission Escalation
**Description**: Attacker gains higher privileges than intended

**Impact**: High - Unauthorized access to sensitive data or actions

**Likelihood**: Medium

**Attack Vector**:
- Exploiting permission model bugs
- Social engineering for permission grants
- Compromised skill with excessive permissions

**Mitigation**:
- Principle of least privilege
- Runtime permission checks (not just install-time)
- Permission change requires re-approval
- Audit all permission grants
- Regular permission audits

**Residual Risk**: Low

#### Threat 1.3: Session Hijacking
**Description**: Attacker hijacks active user session

**Impact**: Medium - Temporary unauthorized access

**Likelihood**: Low

**Attack Vector**:
- Session token theft via XSS
- Man-in-the-middle attack
- Session fixation

**Mitigation**:
- Secure cookie flags (HttpOnly, Secure, SameSite)
- Short session timeouts
- IP-based session validation (optional)
- Session invalidation on suspicious activity

**Residual Risk**: Low

### 2. Data Protection Threats

#### Threat 2.1: Sensitive Data Exposure
**Description**: Sensitive data sent to cloud LLMs inappropriately

**Impact**: High - Privacy violation, data leakage

**Likelihood**: Medium

**Attack Vector**:
- Misclassification of content sensitivity
- Bug in routing policy
- Classifier bypass

**Mitigation**:
- Sensitivity-based routing (high → local only)
- PII redaction before cloud calls
- Defense-in-depth (redaction even for low-sensitivity)
- Regular classifier testing and validation
- Audit all cloud-bound data

**Residual Risk**: Low

#### Threat 2.2: Data at Rest Exposure
**Description**: Unauthorized access to stored data

**Impact**: High - Complete data breach

**Likelihood**: Low

**Attack Vector**:
- Database compromise
- Backup exposure
- Physical access to storage

**Mitigation**:
- Encryption at rest (AES-256-GCM)
- Encrypted backups
- Key management (separate from data)
- Access controls (RBAC)
- Regular access audits

**Residual Risk**: Low

#### Threat 2.3: Data in Transit Exposure
**Description**: Interception of data in transit

**Impact**: Medium - Data leakage

**Likelihood**: Low

**Attack Vector**:
- Man-in-the-middle attack
- TLS downgrade
- Certificate compromise

**Mitigation**:
- TLS 1.3 for all communications
- Certificate pinning (for critical endpoints)
- HSTS enforcement
- Regular certificate rotation

**Residual Risk**: Low

### 3. Injection & Manipulation Threats

#### Threat 3.1: Prompt Injection
**Description**: Malicious content in email/web influences agent behavior

**Impact**: High - Unauthorized actions, data exfiltration

**Likelihood**: Medium

**Attack Vector**:
- Email with embedded instructions
- Web content with malicious prompts
- Compromised connector data

**Mitigation**:
- Provenance tagging for all content
- Untrusted content cannot authorize tool calls
- Injection classifier for suspicious patterns
- Human-in-the-loop for high-risk actions
- Output filtering for instruction-following language

**Residual Risk**: Low

#### Threat 3.2: SQL Injection
**Description**: SQL injection through API inputs

**Impact**: High - Data breach, data corruption

**Likelihood**: Low

**Attack Vector**:
- Malicious API input
- ORM bypass
- Raw query execution

**Mitigation**:
- Use ORM (SQLAlchemy) exclusively
- Input validation via Pydantic
- Parameterized queries only
- Regular security audits
- No raw query execution

**Residual Risk**: Very Low

#### Threat 3.3: Command Injection
**Description**: Command injection through skill execution

**Impact**: High - System compromise

**Likelihood**: Low

**Attack Vector**:
- Malicious skill code
- Subprocess parameter injection
- Environment variable manipulation

**Mitigation**:
- Subprocess isolation with resource limits
- Scrubbed environment for skill execution
- No shell=True in subprocess calls
- Input sanitization for subprocess parameters
- Skill code review and signing

**Residual Risk**: Low

### 4. Autonomous Action Threats

#### Threat 4.1: Unauthorized Autonomous Actions
**Description**: Agent performs actions without user approval

**Impact**: High - Data loss, unauthorized communications

**Likelihood**: Medium

**Attack Vector**:
- Guardrails bypass
- Policy misconfiguration
- Agent goal manipulation

**Mitigation**:
- Multi-layer guardrails (input, tool, output)
- Human-in-the-loop for irreversible actions
- Policy engine with declarative rules
- Comprehensive audit logging
- Action confirmation for high-impact operations

**Residual Risk**: Low

#### Threat 4.2: Agent Loop Exploitation
**Description**: Attacker causes agent to perform harmful repeated actions

**Impact**: Medium - Resource exhaustion, unauthorized actions

**Likelihood**: Low

**Attack Vector**:
- Infinite loop in agent logic
- Budget circumvention
- State manipulation

**Mitigation**:
- Hard step ceiling (e.g., 25 steps)
- Budget enforcement (steps, time, cost)
- Cancellation support
- State validation
- Loop detection

**Residual Risk**: Low

#### Threat 4.3: Skill/Connector Misuse
**Description**: Malicious skill or connector performs unauthorized actions

**Impact**: High - Data breach, system compromise

**Likelihood**: Medium

**Attack Vector**:
- Compromised skill from marketplace
- Malicious connector
- Permission abuse

**Mitigation**:
- Subprocess isolation for skills
- Permission model with runtime checks
- Skill signing and verification
- Marketplace moderation
- Audit all skill/connector actions

**Residual Risk**: Low

### 5. Supply Chain Threats

#### Threat 5.1: Dependency Compromise
**Description**: Malicious code in dependencies

**Impact**: High - System compromise

**Likelihood**: Low

**Attack Vector**:
- Malicious Python package
- Compromised npm package
- Dependency confusion

**Mitigation**:
- Dependency pinning (lock files)
- SBOM generation
- Regular dependency updates
- Vulnerability scanning (Snyk, Dependabot)
- Private package registry

**Residual Risk**: Low

#### Threat 5.2: Container Image Compromise
**Description**: Malicious container image

**Impact**: High - System compromise

**Likelihood**: Low

**Attack Vector**:
- Compromised base image
- Malicious layer
- Image supply chain attack

**Mitigation**:
- Use official base images
- Image scanning (Trivy, Clair)
- Image signing (cosign)
- Minimal images (alpine, distroless)
- Regular image updates

**Residual Risk**: Low

### 6. Denial of Service Threats

#### Threat 6.1: API Rate Limiting Bypass
**Description**: Attacker overwhelms API with requests

**Impact**: Medium - Service disruption

**Likelihood**: Medium

**Attack Vector**:
- Distributed attack
- Rate limit bypass
- Resource exhaustion

**Mitigation**:
- Per-consumer rate limiting
- IP-based rate limiting
- Request throttling
- Circuit breakers
- Auto-scaling (cloud deployment)

**Residual Risk**: Low

#### Threat 6.2: Resource Exhaustion
**Description**: Attacker exhausts system resources

**Impact**: Medium - Service disruption

**Likelihood**: Low

**Attack Vector**:
- Memory exhaustion
- CPU exhaustion
- Disk exhaustion

**Mitigation**:
- Resource limits per container
- Memory limits for skills
- Query timeouts
- Disk quota enforcement
- Resource monitoring

**Residual Risk**: Low

### 7. Compliance & Privacy Threats

#### Threat 7.1: GDPR Violation
**Description**: Failure to comply with GDPR requirements

**Impact**: High - Legal penalties, reputational damage

**Likelihood**: Low

**Attack Vector**:
- Inadequate data protection
- Missing right-to-be-forgotten
- Insufficient consent management

**Mitigation**:
- Right-to-be-forgotten API
- Consent management
- Data minimization
- Data portability
- Regular compliance audits

**Residual Risk**: Low

#### Threat 7.2: Audit Trail Manipulation
**Description**: Attacker modifies or deletes audit logs

**Impact**: High - Compliance violation, forensic loss

**Likelihood**: Low

**Attack Vector**:
- Database compromise
- Log file manipulation
- Audit system bypass

**Mitigation**:
- Immutable audit logs (WORM storage)
- Log forwarding to external system
- Regular audit log integrity checks
- Separate audit database
- Write-once, read-many storage

**Residual Risk**: Low

## Security Controls

### Preventive Controls
- **Authentication**: Multi-factor authentication, device auth
- **Authorization**: RBAC + ABAC, runtime permission checks
- **Encryption**: AES-256-GCM at rest, TLS 1.3 in transit
- **Input Validation**: Pydantic schema validation
- **Sandboxing**: Subprocess isolation for skills
- **Guardrails**: Multi-layer security checks

### Detective Controls
- **Logging**: Comprehensive structured logging
- **Monitoring**: Real-time security monitoring
- **Audit Trail**: Complete action audit logging
- **Anomaly Detection**: Behavioral analysis
- **Alerting**: Security incident alerts

### Corrective Controls
- **Incident Response**: Security incident response plan
- **Backup/Restore**: Regular backups with tested restore
- **Revocation**: Token and permission revocation
- **Patching**: Regular security updates
- **Isolation**: Compartmentalization for containment

## Compliance Mapping

### GDPR
- **Data Protection**: Encryption, access controls, data minimization
- **User Rights**: Right to access, rectification, erasure, portability
- **Consent**: Explicit consent management
- **Breach Notification**: 72-hour breach notification process

### SOC 2
- **Security**: Access controls, encryption, monitoring
- **Availability**: 99.9% uptime, disaster recovery
- **Processing Integrity**: Audit logging, change management
- **Confidentiality**: Data classification, access controls
- **Privacy**: Consent management, data minimization

### ISO 27001
- **Information Security Policies**: Comprehensive security policies
- **Risk Management**: Threat modeling, risk assessment
- **Asset Management**: Asset inventory, classification
- **Access Control**: RBAC, ABAC, least privilege
- **Cryptography**: Encryption standards, key management
- **Operations Security**: Change management, incident response
- **Business Continuity**: Disaster recovery, backup/restore

## Incident Response

### Incident Categories
1. **Critical**: Active data breach, system compromise
2. **High**: Unauthorized access, data exposure
3. **Medium**: Security control bypass, policy violation
4. **Low**: Suspicious activity, potential vulnerability

### Response Process
1. **Detection**: Automated monitoring, user reports
2. **Analysis**: Incident classification, impact assessment
3. **Containment**: Isolate affected systems, prevent spread
4. **Eradication**: Remove threat, patch vulnerabilities
5. **Recovery**: Restore systems, validate integrity
6. **Lessons Learned**: Post-incident review, process improvement

### Escalation Matrix
- **Level 1**: Security team (low/medium incidents)
- **Level 2**: Security leadership (high incidents)
- **Level 3**: Executive team (critical incidents)
- **Level 4**: Legal/PR (critical incidents with public impact)

## Security Testing

### Regular Testing
- **Penetration Testing**: Quarterly external penetration testing
- **Vulnerability Scanning**: Weekly automated scanning
- **Dependency Scanning**: Continuous dependency monitoring
- **Security Audits**: Annual comprehensive security audit

### Continuous Testing
- **SAST**: Static application security testing in CI
- **DAST**: Dynamic application security testing in CI
- **Container Scanning**: Image scanning in CI/CD
- **Secret Scanning**: Automated secret detection in code

## Conclusion

TEMPUS faces significant security threats due to its processing of sensitive personal data and autonomous action capabilities. However, through a comprehensive defense-in-depth approach including sensitivity-based routing, multi-layer guardrails, comprehensive audit logging, and regular security testing, these threats can be effectively mitigated to an acceptable residual risk level.

The key security principles are:
1. **Privacy-First**: Protect sensitive data through routing and encryption
2. **Defense-in-Depth**: Multiple security controls at each layer
3. **Zero Trust**: Verify all requests, regardless of source
4. **Audit Everything**: Complete audit trail for all actions
5. **Human-in-the-Loop**: Require approval for high-impact actions

Regular threat model reviews and security assessments will ensure the security posture remains effective as the system evolves.
