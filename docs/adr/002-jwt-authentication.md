# ADR 002: Use JWT for Authentication

## Status
Accepted

## Context
TEMPUS needs a stateless authentication mechanism that works across multiple services (API, WebSocket, extensions). The system must support both web and extension-based authentication (Chrome, VS Code).

## Decision
Use JWT (JSON Web Tokens) with HMAC-SHA256 signing for authentication.

### Rationale
1. **Stateless**: No server-side session storage required, scales horizontally
2. **Cross-Service**: Same token works for API, WebSocket, and extensions
3. **Extension-Friendly**: Extensions can store tokens locally and include in requests
4. **Performance**: No database lookup required for each request
5. **Standard**: Widely adopted, well-understood security model

### Token Structure
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "iat": 1234567890,
  "exp": 1234571490
}
```

### Security Measures
- Secret key stored in environment variables (never hardcoded)
- Short expiration (60 minutes for access tokens)
- Refresh tokens with longer expiration (7 days)
- Rate limiting on token generation
- Token rotation on refresh

### Alternatives Considered
- **Session Cookies**: Not suitable for extensions, requires server-side storage
- **OAuth2 Only**: Too complex for internal authentication, better for external providers
- **API Keys**: No built-in expiration, harder to revoke

## Consequences
### Positive
- Simple to implement and debug
- Works across all client types
- No server-side session storage
- Easy to add claims for RBAC

### Negative
- Cannot revoke tokens without blacklist (acceptable trade-off)
- Token size larger than session IDs
- Requires careful secret management

## Implementation
```python
from app.auth.jwt_handler import JWTHandler

jwt_handler = JWTHandler()

# Create token
token = jwt_handler.create_access_token(
    data={"sub": user_id, "email": user.email}
)

# Verify token
payload = jwt_handler.decode_token(token)
```

## References
- JWT RFC: https://tools.ietf.org/html/rfc7519
- OWASP JWT Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
