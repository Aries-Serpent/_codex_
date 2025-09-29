# Torch CPU Policy — Relaxing the “+cpu” suffix when CPU index is enforced

**Why:** PyTorch’s official CPU-only install path is to point pip at the CPU index URL and use a standard spec like `torch==2.8.0` (no `+cpu` suffix).  
**So:** When `PIP_INDEX_URL` or `PIP_EXTRA_INDEX_URL` contains `download.pytorch.org/whl/cpu` (or `CODEX_FORCE_CPU=1`), the validator should accept a wheel **without** the `+cpu` suffix as compliant — provided CUDA is not available and `torch` imports successfully.

Reference (PyTorch CPU index URL): https://download.pytorch.org/whl/cpu  (see official “pip” instructions).  

Operational helpers added:
- `make torch-policy-check` — prints a JSON status and policy outcome.
- `make torch-repair-cpu` — forces reinstall from the CPU index and re-checks.


---

**References**

* uv CLI (`--locked` requires up-to-date lockfile; run `uv lock` to update). ([Astral Docs][2])
* PyTorch CPU wheel index & pip usage (CPU-only installs). ([PyTorch Documentation][1])
* pre-commit docs (`autoupdate`) + community references for `migrate-config`. ([GitHub Docs][3])
* GitHub Docs — Copilot in the CLI overview (general background). ([npm][4])

[1]: https://docs.pytorch.org/FBGEMM/fbgemm_gpu/development/InstallationInstructions.html?utm_source=chatgpt.com "Installation Instructions — FBGEMM 1.3.0 documentation"
[2]: https://docs.astral.sh/uv/reference/cli/?utm_source=chatgpt.com "Commands | uv - Astral Docs"
[3]: https://docs.github.com/copilot/managing-copilot/configure-personal-settings/installing-the-github-copilot-extension-in-your-environment?utm_source=chatgpt.com "Installing the GitHub Copilot extension in your environment"
[4]: https://www.npmjs.com/package/api-copilot?utm_source=chatgpt.com "api-copilot"

