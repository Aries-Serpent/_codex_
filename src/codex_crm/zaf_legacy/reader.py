from __future__ import annotations

import json
import pathlib
import zipfile


class ZAFParseError(Exception):
    """Raised when a Zendesk App Framework package cannot be parsed."""


def read_zaf(zip_path: str) -> dict[str, object]:
    """Read a Zendesk App Framework ZIP export into a Python structure."""

    try:
        with zipfile.ZipFile(zip_path) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            files: dict[str, str] = {}
            for name in archive.namelist():
                if name.endswith("/"):
                    continue
                if name == "manifest.json":
                    continue
                files[name] = archive.read(name).decode("utf-8", "ignore")
    except Exception as exc:  # pragma: no cover - wrapped for context
        raise ZAFParseError(str(exc)) from exc

    return {"manifest": manifest, "files": files}


def _normalize_manifest(manifest: dict[str, object]) -> dict[str, object]:
    """Inject Codex defaults into a Zendesk App manifest."""

    manifest = dict(manifest)
    manifest.setdefault("name", "codex_app_template")
    parameters = list(manifest.get("parameters", []))
    if not any(param.get("name") == "API_BASE" for param in parameters if isinstance(param, dict)):
        parameters.append({"name": "API_BASE", "type": "text", "required": False})
    manifest["parameters"] = parameters
    return manifest


def scaffold_template(zaf: dict[str, object], out_dir: str) -> None:
    """Write a normalized Zendesk App scaffold to ``out_dir``."""

    output = pathlib.Path(out_dir)
    (output / "src").mkdir(parents=True, exist_ok=True)
    manifest = _normalize_manifest(zaf.get("manifest", {}))
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    files = zaf.get("files", {})
    for original_path, content in files.items():
        suffix = pathlib.Path(original_path).suffix
        if suffix not in {".js", ".css", ".hbs", ".json"}:
            continue
        target = output / "src" / pathlib.Path(original_path).name
        target.write_text(content, encoding="utf-8")
