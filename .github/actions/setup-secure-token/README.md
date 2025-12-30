# Setup Secure Token Action

This composite action configures secure token retrieval for Copilot workflows in the _codex_ repository.

## Features

- ✅ Supports multiple token retrieval methods (AES-256-GCM, Base64, fallback)
- ✅ Automatic fallback to `GITHUB_TOKEN` if encrypted tokens unavailable
- ✅ No token exposure in logs
- ✅ Compatible with existing workflows

## Usage

### Basic Usage

```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v6
  
  - name: Setup secure token
    uses: ./.github/actions/setup-secure-token
    env:
      CODEX_GHP_TOKEN_BASE64: ${{ secrets.CODEX_GHP_TOKEN_BASE64 }}
      CODEX_GHP_TOKEN_CONFIG: ${{ secrets.CODEX_GHP_TOKEN_CONFIG }}
    with:
      fallback-token: ${{ secrets.GITHUB_TOKEN }}
```

### Advanced Usage

```yaml
steps:
  - name: Setup secure token (skip crypto install)
    uses: ./.github/actions/setup-secure-token
    env:
      CODEX_GHP_TOKEN_BASE64: ${{ secrets.CODEX_GHP_TOKEN_BASE64 }}
    with:
      fallback-token: ${{ secrets.GITHUB_TOKEN }}
      install-crypto: 'false'  # Skip if already installed
```

### Using Token in Scripts

After running this action, use the token decoder in your scripts:

```python
from scripts.security.copilot_token_decoder import copilot_get_github_token

token = copilot_get_github_token()
# Use token for GitHub API operations
```

Or use the safe version that never raises:

```python
from scripts.security.copilot_token_decoder import copilot_get_github_token_safe

token = copilot_get_github_token_safe()
if not token:
    print("No token configured, skipping GitHub API operations")
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `fallback-token` | Fallback token if encrypted tokens unavailable | No | `''` |
| `install-crypto` | Whether to install cryptography dependencies | No | `'true'` |

## Outputs

| Output | Description |
|--------|-------------|
| `token-configured` | Whether a token was successfully configured (`true`/`false`) |
| `token-method` | Method used for token retrieval (`aes`/`base64`/`fallback`/`none`) |

## Environment Variables

The action expects these environment variables to be set (via secrets):

- `CODEX_GHP_TOKEN_BASE64` - Base64-encoded token (simple encoding)
- `CODEX_GHP_TOKEN_CONFIG` - AES-256-GCM encrypted token configuration (most secure)

## Token Retrieval Priority

1. **AES-256-GCM** - If `CODEX_GHP_TOKEN_CONFIG` is set and cryptography is available
2. **Base64** - If `CODEX_GHP_TOKEN_BASE64` is set
3. **Fallback** - Uses the `fallback-token` input (typically `secrets.GITHUB_TOKEN`)

## Security Notes

- ✅ Tokens are never exposed in logs
- ✅ Owner-only file permissions (0o700) on extracted tools
- ✅ Automatic cleanup of sensitive data
- ✅ Graceful fallback to standard `GITHUB_TOKEN`

## See Also

- [Admin Token Setup Guide](../../../docs/admin/security/ADMIN_TOKEN_SETUP.md)
- [Copilot Token Usage Guide](../../../docs/admin/security/COPILOT_TOKEN_USAGE.md)
- [Token Encryption Tool](../../../scripts/security/token_encryption_tool.py)
- [Token Decoder Module](../../../scripts/security/copilot_token_decoder.py)
