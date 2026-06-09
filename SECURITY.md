# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | :white_check_mark: |

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
- Role-Based Access Control (RBAC) with granular permissions (admin, clinician, viewer)
- bcrypt password hashing
- HTTP Bearer token enforcement

### Data Protection (LGPD Compliance)
- Field-level encryption for personally identifiable information (PII) via Fernet AES
- Pseudonymization via SHA-256 hashing (CPF, email)
- Configurable data retention (default 5 years)
- Consent management system (`/api/v1/consent/`)
- Full audit logging of all data access
- UUID-based patient identification (no sequential IDs)

### Network & Application Security
- CORS restricted to configured origins
- Content-Security-Policy (CSP) headers
- HTTP Strict-Transport-Security (HSTS) with 1-year max-age
- Rate limiting: 100 requests/minute/IP on all API endpoints
- SQL injection protection on query parameters
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Referrer-Policy: strict-origin-when-cross-origin

### Secure SDLC
- Bandit SAST scanning for Python code (`python -m bandit -c .bandit -r app/ scripts/ db/`)
- Safety CLI for dependency vulnerability checks
- Pre-commit hooks with security checks
- Automated CI pipeline with linting, type checking, and security scanning
- Code review required for all changes
- Secrets detection in pre-commit hooks

### Dependency Security
- Regular automated dependency scanning via Safety CLI
- Bandit static analysis for Python code
- Automated security checks in CI pipeline

### Clinical Data Integrity
- 3-layer validation: Pydantic schema → ClinicalIntegrityService → DB CHECK constraints
- DB constraints: birth_date, intensity (0-10), duration (≥1), frequency enum, response values (0-10), probability/confidence (0-1)
- Data quality CLI: `python scripts/check_integrity.py`
