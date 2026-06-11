# Security

## Threat Model

Primary risks:

- Secret leakage
- Accidental live-trading functionality
- Market-data spoofing or corruption
- Prompt injection into AI explanations
- Unsafe development authentication
- Financially harmful UI language

## Secret Handling

- Keep secrets in `.env.local` or secret stores.
- Do not commit `.env.local`.
- Do not log API keys, exchange credentials, or authorization headers.

## Authentication Mode

The local MVP may use documented development authentication. Do not expose a development-auth instance publicly.

## Production Hardening Checklist

- Disable development authentication.
- Configure strict CORS.
- Add rate limiting.
- Add secure headers.
- Use least-privilege database users.
- Add dependency scanning.
- Verify no live order placement code exists.

