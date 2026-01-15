# Codex Authentication Examples

This directory contains example scripts demonstrating the Codex authentication system.

## Prerequisites

1. Python 3.11 or higher
2. Install dependencies: `pip install httpx`
3. Set up environment variables (copy `.env.example` to `.env`)

## Examples

### 01_oauth_flow.py
Complete GitHub OAuth2 authentication flow with PKCE.

```bash
python examples/authentication/01_oauth_flow.py
```

**Features:**
- OAuth2 authorization code flow
- PKCE security
- Token exchange
- User information retrieval
- Token refresh

### 02_mfa_setup.py
Multi-factor authentication setup and verification.

```bash
python examples/authentication/02_mfa_setup.py
```

**Features:**
- TOTP secret generation
- QR code provisioning URI
- Backup codes generation
- Code verification
- Rate limiting demonstration

### 03_token_management.py
Token generation, validation, and session management.

```bash
python examples/authentication/03_token_management.py
```

**Features:**
- Access token generation
- Refresh token management
- Session creation
- Token validation
- Token revocation
- Session cleanup

### 04_complete_flow.py
Complete authentication flow combining all features.

```bash
python examples/authentication/04_complete_flow.py
```

**Features:**
- GitHub OAuth login
- MFA setup and verification
- Token issuance
- Session management
- Complete security workflow

## Environment Setup

1. Create GitHub OAuth App:
   - Go to: https://github.com/settings/developers
   - Click "New OAuth App"
   - Set callback URL to: `http://localhost:8000/callback`
   - Copy Client ID and Client Secret

2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and add your credentials:
   ```bash
   GITHUB_CLIENT_ID=your_client_id
   GITHUB_CLIENT_SECRET=your_client_secret
   TOKEN_SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(64))")
   ```

## Usage Tips

- Run examples in order (01 → 02 → 03 → 04) to understand the flow
- Examples are self-contained and can be run independently
- All examples include detailed output explaining each step
- MFA examples work without actual authenticator apps (demo mode)

## Security Notes

- Never commit `.env` file or credentials
- Use HTTPS in production
- Store tokens securely
- Enable MFA for all users
- Rotate secrets regularly

## Additional Resources

- [User Guide](../../docs/authentication/USER_GUIDE.md)
- [Implementation Guide](../../PHASE_11_1_AUTHENTICATION_IMPLEMENTATION.md)
- [Test Suite](../../tests/auth/)
