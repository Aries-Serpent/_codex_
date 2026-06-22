# Codex Authentication System - User Guide

**Version**: 1.0
**Last Updated**: 2026-06-22

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Setting Up GitHub OAuth](#setting-up-github-oauth)
3. <!-- BROKEN ANCHOR: [Enabling Multi-Factor Authentication](#enabling-multi-factor-authentication) -->
4. <!-- BROKEN ANCHOR: [Working with Tokens](#working-with-tokens) -->
5. <!-- BROKEN ANCHOR: [Session Management](#session-management) -->
6. <!-- BROKEN ANCHOR: [Security Best Practices](#security-best-practices) -->
7. <!-- BROKEN ANCHOR: [Troubleshooting](#troubleshooting) -->

---

## Quick Start

### Installation

The authentication module is already included in the Codex project. No additional installation is required.

### Basic Usage

```python
from src.codex.auth import OAuthManager, MFAProvider, TokenManager

# Initialize components
oauth = OAuthManager()
mfa = MFAProvider()
tokens = TokenManager()

print("Authentication system ready!")
```

---

## Setting Up GitHub OAuth

### Step 1: Create GitHub OAuth App

1. Go to GitHub Settings → Developer Settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: Codex Auth
4. Click "Register application"
5. Copy the **Client ID** and **Client Secret**

### Step 2: Configure Environment

Create a `.env` file in your project root:

```bash
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here
TOKEN_SECRET_KEY=your_random_secret_key_here
```

**Generate a secure secret key**:
```python
import secrets
print(secrets.token_urlsafe(64))
```

---

## Complete Example

See `examples/authentication/` directory for full working examples.

---

**Document Version**: 1.0
**Last Updated**: 2026-06-22
