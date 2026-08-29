
# GitHub App (Permissions)

Use a **GitHub App** rather than OAuth for repo operations. Minimum suggested scopes:

- Repository permissions:
  - Contents: Read
  - Pull requests: Read & write

Export the following env vars for the ITA when enabling write operations:
- `GITHUB_APP_ID`
- `GITHUB_INSTALLATION_ID`
- `GITHUB_PRIVATE_KEY_PEM` (PEM text; keep secure)
