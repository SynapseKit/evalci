# Security Policy

## Reporting a Vulnerability

**Please do not report security vulnerabilities via public GitHub issues.**

Email us at: **security@synapsekit.dev**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge your report within 48 hours and aim to resolve critical issues within 7 days.

## Scope

Security issues in scope:
- `entrypoint.py` — command injection, path traversal, token leakage
- `action.yml` — unsafe use of inputs in shell steps
- Dependency vulnerabilities in `synapsekit` itself (report to the [main repo](https://github.com/SynapseKit/SynapseKit/security))

## Supported Versions

| Version | Supported |
|---|---|
| `v1` (latest) | ✅ |
