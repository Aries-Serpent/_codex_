"""Build Zendesk quantum packaging artifacts from a YAML spec."""

from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from pathlib import Path
from typing import Any

import yaml


def load_spec(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Spec not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def ensure_empty_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def write_manifest(package_root: Path, payload: dict[str, Any]) -> None:
    manifest_path = package_root / "manifest.json"
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_readme(package_root: Path, payload: dict[str, Any]) -> None:
    content = [f"# {payload['package_name']}", "", payload.get("description", "")]
    entry_point = payload.get("entry_point")
    if entry_point:
        content.extend(["", "## Entry Point", f"`{entry_point}`"])
    capabilities = payload.get("capabilities")
    if capabilities:
        content.extend(["", "## Capabilities"])
        content.extend([f"- {item}" for item in capabilities])
    (package_root / "README.md").write_text("\n".join(content) + "\n", encoding="utf-8")


def write_instructions(package_root: Path, payload: dict[str, Any]) -> None:
    content = [
        f"# {payload['package_name']} Setup",
        "",
        "1. Unzip the package.",
        "2. Review README.md for entry points and capabilities.",
        "3. Provide required environment variables for Zendesk integrations.",
    ]
    (package_root / "instructions.md").write_text("\n".join(content) + "\n", encoding="utf-8")


def ensure_skeleton_dirs(package_root: Path, skeleton_dirs: list[str]) -> None:
    for rel in skeleton_dirs:
        target = package_root / rel
        target.mkdir(parents=True, exist_ok=True)
        keep = target / ".keep"
        if not any(target.iterdir()):
            keep.write_text("", encoding="utf-8")


def copy_includes(package_root: Path, repo_root: Path, includes: list[str]) -> None:
    def ignore_paths(_: str, names: list[str]) -> set[str]:
        return {name for name in names if name == "__pycache__" or name.endswith(".pyc")}

    for entry in includes:
        source = repo_root / entry
        if not source.exists():
            print(f"⚠️  Warning: Missing include path: {source}")
            continue
        destination = package_root / entry
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True, ignore=ignore_paths)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)


def write_bundle_helpers(package_root: Path) -> None:
    (package_root / "MASTER_SETUP.md").write_text(
        "# Zendesk Complete Bundle Setup\n\nRefer to package README files.\n",
        encoding="utf-8",
    )
    integration_dir = package_root / "integration"
    integration_dir.mkdir(parents=True, exist_ok=True)
    (integration_dir / "deployment_orchestrator.py").write_text(
        '"""Deployment orchestrator placeholder."""\n\n'
        "def main():\n"
        "    print(\"Deploy Zendesk bundle\")\n",
        encoding="utf-8",
    )


def build_package(
    repo_root: Path,
    output_dir: Path,
    pkg: dict[str, Any],
    version_override: str | None,
    built_packages: dict[str, Path],
) -> Path:
    name = pkg["name"]
    version = version_override or pkg.get("version", "1.0.0")
    package_root = output_dir / name
    ensure_empty_dir(package_root)

    includes = pkg.get("includes", [])
    if includes:
        copy_includes(package_root, repo_root, includes)

    skeleton_dirs = pkg.get("skeleton_dirs", [])
    if skeleton_dirs:
        ensure_skeleton_dirs(package_root, skeleton_dirs)

    manifest_payload: dict[str, Any] = {
        "package_name": name,
        "version": version,
        "type": "mcp-quantum-deployment",
        "target_platform": pkg.get("target_platform", []),
        "physics_paradigms": pkg.get("physics_paradigms", []),
        "dependencies": pkg.get("dependencies", {}),
        "capabilities": pkg.get("capabilities", []),
        "entry_point": pkg.get("entry_point"),
        "description": pkg.get("description", ""),
    }
    if pkg.get("integration"):
        manifest_payload["integration"] = pkg["integration"]

    write_manifest(package_root, manifest_payload)
    write_readme(package_root, manifest_payload)
    write_instructions(package_root, manifest_payload)

    if pkg.get("bundle"):
        write_bundle_helpers(package_root)
        bundle_packages = pkg["bundle"].get("packages", [])
        packages_dir = package_root / "packages"
        packages_dir.mkdir(parents=True, exist_ok=True)
        for bundle_name in bundle_packages:
            bundle_path = built_packages.get(bundle_name)
            if bundle_path is None:
                print(f"⚠️  Warning: Bundle package missing: {bundle_name}")
                continue
            shutil.copy2(bundle_path, packages_dir / bundle_path.name)

    zip_path = output_dir / f"{name}.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_root.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(package_root.parent)
                zipf.write(file_path, arcname)

    built_packages[name] = zip_path
    return zip_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to packaging spec YAML",
    )
    parser.add_argument(
        "--version",
        type=str,
        default=None,
        help="Override package version",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Override output directory",
    )
    parser.add_argument(
        "--package",
        type=str,
        default="all",
        help="Package to build: all, core, rag, metrics, agent, testing, bundle",
    )
    parser.add_argument(
        "--include-bundle",
        action="store_true",
        help="Include zendesk-complete-bundle in build output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]

    spec = load_spec(args.config)
    output_dir = Path(args.output_dir or spec.get("output_dir", "build/zendesk_quantum"))
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    version_override = args.version or spec.get("version")

    package_map = {
        "core": "zendesk-quantum-core",
        "rag": "zendesk-rag-bridge",
        "metrics": "zendesk-mcp-metrics",
        "agent": "zendesk-agent-core",
        "testing": "zendesk-quantum-testing",
        "bundle": "zendesk-complete-bundle",
    }

    requested = package_map.get(args.package, args.package)
    spec_packages = spec.get("packages", [])
    if args.package == "all":
        packages = list(spec_packages)
    else:
        packages = [pkg for pkg in spec_packages if pkg["name"] == requested]
        if not packages:
            raise ValueError(f"Package '{args.package}' not found in spec")

    if args.include_bundle and all(
        pkg["name"] != package_map["bundle"] for pkg in packages
    ):
        packages.extend(
            pkg for pkg in spec_packages if pkg["name"] == package_map["bundle"]
        )

    if not args.include_bundle and args.package != "bundle":
        packages = [
            pkg for pkg in packages if pkg["name"] != package_map["bundle"]
        ]

    built_packages: dict[str, Path] = {}
    if any(pkg.get("bundle") for pkg in packages):
        bundle_pkg = next(pkg for pkg in packages if pkg.get("bundle"))
        bundle_names = bundle_pkg.get("bundle", {}).get("packages", [])
        for pkg in spec_packages:
            if pkg["name"] in bundle_names and pkg not in packages:
                packages.insert(0, pkg)

    seen: set[str] = set()
    ordered_packages: list[dict[str, Any]] = []
    for pkg in packages:
        name = pkg["name"]
        if name in seen:
            continue
        seen.add(name)
        ordered_packages.append(pkg)

    for pkg in ordered_packages:
        print(f"📦 Building {pkg['name']}...")
        build_package(repo_root, output_dir, pkg, version_override, built_packages)

    print(f"\n✅ Successfully created {len(built_packages)} package(s)")
    for name, path in built_packages.items():
        print(f"   {name}: {path}")


if __name__ == "__main__":
    main()
