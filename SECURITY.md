# Security Notes

## Supported deployment

Local-only on the same computer, bound to `127.0.0.1`. Do not expose the Streamlit port directly to a LAN or the internet.

## Current scope

This version has no login system, administrator routes, database, API keys, API calls, or app-managed upload endpoint. These controls are not present to audit. If those features are added, implement authentication, authorization/least privilege, CSRF review, per-user rate limits, abuse/spend limits, database access controls, secret management, and deployment-specific CORS/TLS/security headers before release.

## Report a vulnerability

Please do not publish sensitive file paths, private files, credentials, or exploit details in a public issue. Revoke any exposed credentials immediately and report the issue privately to the repository owner.
