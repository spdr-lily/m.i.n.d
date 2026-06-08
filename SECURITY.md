# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

This project handles sensitive mental health data. If you discover a security
vulnerability, please report it privately before public disclosure.

**Do not** report security issues via the public issue tracker.

### How to Report

Send an email to the security team at **security@mind-cdss.example.com**
(placeholder — replace with actual contact).

Include as much detail as possible:
- Type of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if known)

### Response Timeline

- **24h**: Acknowledgment of receipt
- **7 days**: Initial assessment and priority classification
- **30 days**: Fix deployed for critical/high severity issues

## Security Measures

### Authentication & Authorization
- JWT-based authentication with configurable token expiration
- Role-Based Access Control (RBAC) with granular permissions
- bcrypt password hashing
- HTTP Bearer token enforcement

### Data Protection (LGPD Compliance)
- Field-level encryption for personally identifiable information (PII)
- Pseudonymization via SHA-256 hashing
- Configurable data retention (default 5 years)
- Consent management system
- Full audit logging of all data access

### Network Security
- CORS restricted to configured origins
- Content-Security-Policy headers
- HSTS with 1-year max-age
- Rate limiting on API endpoints
- SQL injection protection on query parameters
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Referrer-Policy: strict-origin-when-cross-origin

### Dependency Security
- Regular automated dependency scanning
- Bandit SAST scanning for Python code
- Safety CLI for dependency vulnerability checks

### Secure SDLC
- Pre-commit hooks with security checks
- Automated CI pipeline with linting and type checking
- Code review required for all changes
- Secrets detection in pre-commit hooks
