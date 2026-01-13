# GitHub Secrets CLI

A command-line tool for managing GitHub secrets across different scopes (organization, repository, environment, and Codespaces) with client-side encryption and secure authentication.

## Features

- **Multi-Scope Support**: Manage secrets at organization, repository, environment, and user/Codespaces levels
- **Client-Side Encryption**: Uses NaCl sealed box encryption with fetch-on-demand public keys
- **Flexible Authentication**: 
  - OAuth2 Device Flow for interactive sessions
  - Fine-Grained Personal Access Tokens (PAT) for automation
  - Secure token persistence via system keyring
- **Audit Trail**: JSON-formatted audit logs for compliance
- **Idempotent Operations**: Safe to run multiple times with `--dry-run` mode

## Installation

```bash
cd tools/github-secrets-cli
go build -o github-secrets-cli
./github-secrets-cli --help
```

## Usage

### Authentication

#### Interactive (OAuth2 Device Flow)
```bash
github-secrets-cli auth login
# Follow the displayed instructions to authenticate
```

#### Non-Interactive (PAT)
```bash
export GITHUB_TOKEN=ghp_your_fine_grained_pat
github-secrets-cli set --scope repo --repo owner/repo --name SECRET_NAME --value "secret_value"
```

### Managing Secrets

#### Set a Repository Secret
```bash
github-secrets-cli set \
  --scope repo \
  --repo Aries-Serpent/_codex_ \
  --name CODEX_MASTER_KEY \
  --value "$(openssl rand -base64 32)"
```

#### Set an Organization Secret
```bash
github-secrets-cli set \
  --scope org \
  --org Aries-Serpent \
  --name ORG_WIDE_SECRET \
  --value "secret_value" \
  --visibility selected \
  --selected-repos "_codex_,other-repo"
```

#### Set an Environment Secret
```bash
github-secrets-cli set \
  --scope env \
  --repo Aries-Serpent/_codex_ \
  --env production \
  --name PROD_API_KEY \
  --value "prod_key_value"
```

#### Set a Codespaces Secret
```bash
github-secrets-cli set \
  --scope user \
  --name CODESPACES_SECRET \
  --value "value" \
  --selected-repos "_codex_"
```

#### List Secrets
```bash
# List repository secrets
github-secrets-cli list --scope repo --repo Aries-Serpent/_codex_

# List organization secrets
github-secrets-cli list --scope org --org Aries-Serpent

# List environment secrets
github-secrets-cli list --scope env --repo Aries-Serpent/_codex_ --env production

# List user/Codespaces secrets
github-secrets-cli list --scope user
```

#### Delete a Secret
```bash
github-secrets-cli delete \
  --scope repo \
  --repo Aries-Serpent/_codex_ \
  --name SECRET_TO_DELETE
```

#### Audit Secret Access
```bash
# Get audit trail for a specific secret
github-secrets-cli audit \
  --scope repo \
  --repo Aries-Serpent/_codex_ \
  --name SECRET_NAME \
  --json

# Output format:
# {
#   "secret_name": "SECRET_NAME",
#   "scope": "repository",
#   "created_at": "2026-01-13T20:00:00Z",
#   "updated_at": "2026-01-13T20:05:00Z",
#   "last_used_at": "2026-01-13T20:10:00Z",
#   "access_count": 42
# }
```

### Dry Run Mode

Test operations without making changes:

```bash
github-secrets-cli set \
  --scope repo \
  --repo Aries-Serpent/_codex_ \
  --name TEST_SECRET \
  --value "test_value" \
  --dry-run
```

## Configuration

### Environment Variables

- `GITHUB_TOKEN`: Fine-Grained PAT for authentication (alternative to OAuth)
- `GITHUB_API_URL`: GitHub API endpoint (default: https://api.github.com)
- `GITHUB_SECRETS_CLI_LOG_LEVEL`: Log level (debug, info, warn, error)

### Token Permissions

For Fine-Grained PATs, the following permissions are required:

**Repository Secrets**:
- Repository permissions: Secrets (Read and Write)

**Organization Secrets**:
- Organization permissions: Secrets (Read and Write)

**Environment Secrets**:
- Repository permissions: Secrets (Read and Write), Environments (Read)

**User/Codespaces Secrets**:
- Account permissions: Codespaces secrets (Read and Write)

## Security

### Encryption

Secrets are encrypted client-side using NaCl sealed box (Curve25519, XSalsa20, Poly1305):
1. Fetch public key from GitHub API for the target scope
2. Encrypt secret value using the public key
3. Send encrypted value to GitHub API

### Token Storage

Tokens are stored securely using the system keyring:
- **Linux**: Secret Service API (GNOME Keyring, KWallet)
- **macOS**: Keychain
- **Windows**: Credential Manager

### Audit Trail

All operations are logged to `~/.config/github-secrets-cli/audit.log`:
```json
{
  "timestamp": "2026-01-13T20:15:00Z",
  "operation": "set",
  "scope": "repository",
  "target": "Aries-Serpent/_codex_",
  "secret_name": "CODEX_MASTER_KEY",
  "user": "mbaetiong",
  "success": true
}
```

## GitHub Copilot Agent Integration

This CLI can be invoked by GitHub Copilot Agents with FULL ACCESS to:
- Automate secret injection during repository setup
- Rotate secrets on a schedule
- Sync secrets across environments
- Generate and store encryption keys

Example agent workflow:
```python
import subprocess
import json

def set_repository_secret(repo, name, value):
    """Set a repository secret via GitHub Secrets CLI."""
    result = subprocess.run([
        "github-secrets-cli", "set",
        "--scope", "repo",
        "--repo", repo,
        "--name", name,
        "--value", value,
        "--json"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Failed to set secret: {result.stderr}")
    
    return json.loads(result.stdout)
```

## Development

### Building from Source

```bash
cd tools/github-secrets-cli
go mod download
go build -o github-secrets-cli
```

### Running Tests

```bash
go test ./... -v
```

### Code Structure

```
tools/github-secrets-cli/
├── main.go           # CLI entry point and command definitions
├── go.mod            # Go module dependencies
├── README.md         # This file
├── auth/             # Authentication (OAuth2, PAT, keyring)
├── crypto/           # Encryption/decryption using NaCl
├── client/           # GitHub API client
├── audit/            # Audit logging
└── tests/            # Unit and integration tests
```

## Troubleshooting

### Token not found in keyring
```
Error: no GitHub token found
Solution: Run 'github-secrets-cli auth login' or set GITHUB_TOKEN environment variable
```

### Insufficient permissions
```
Error: 403 Forbidden - token does not have required permissions
Solution: Check token permissions at https://github.com/settings/tokens
```

### Public key not found
```
Error: failed to fetch public key for repository
Solution: Verify repository exists and token has read access
```

## License

See repository root LICENSE file.

## Support

For issues and feature requests, please open an issue in the Aries-Serpent/_codex_ repository.
