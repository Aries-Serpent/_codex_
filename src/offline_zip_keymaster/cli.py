from __future__ import annotations

import argparse
from pathlib import Path

from scripts.security.offline_zip_keymaster import (
    encrypt_directory,
    generate_local_key,
    local_key_probe,
    normalize_directory,
    rezip_clean_directory,
    unpack_archive,
)


DEFAULT_APP_WORKSPACE = Path("./offline_zip_keymaster_app")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Offline ZIP key generation and safe unpacking")
    subparsers = parser.add_subparsers(dest="command", required=True)

    key_cmd = subparsers.add_parser("generate-key", help="Generate a local key manifest")
    key_cmd.add_argument("--key-out", required=True, help="Where to store the generated key manifest")
    key_cmd.add_argument("--algorithm", choices=["aes-gcm", "fernet"], default="aes-gcm")

    encrypt_cmd = subparsers.add_parser("encrypt", help="Encrypt a directory into a protected ZIP archive")
    encrypt_cmd.add_argument("--input-dir", required=True, help="Directory to encrypt")
    encrypt_cmd.add_argument("--zip-out", required=True, help="Destination ZIP archive")
    encrypt_cmd.add_argument("--key-file", required=True, help="Local key manifest")

    unpack_cmd = subparsers.add_parser("unpack", help="Decrypt and unpack a protected ZIP archive")
    unpack_cmd.add_argument("--zip-path", required=True, help="Encrypted ZIP archive")
    unpack_cmd.add_argument("--key-file", required=True, help="Key manifest path")
    unpack_cmd.add_argument("--output-dir", default=".", help="Parent directory for the self-titled extraction folder")

    normalize_cmd = subparsers.add_parser("normalize", help="Normalize a directory into a deterministic manifest")
    normalize_cmd.add_argument("--input-dir", required=True, help="Directory to normalize")
    normalize_cmd.add_argument("--output-manifest", help="Optional output path for the JSON manifest")
    normalize_cmd.add_argument("--include-content", action="store_true", help="Embed file content in the JSON output")

    rezip_cmd = subparsers.add_parser("rezip-clean", help="Rebuild a clean zip archive from a normalized directory")
    rezip_cmd.add_argument("--input-dir", required=True, help="Dir to archive")
    rezip_cmd.add_argument("--zip-out", required=True, help="Output zip path")

    probe_cmd = subparsers.add_parser("probe-key", help="Run a bounded local-only key probe")
    probe_cmd.add_argument("--key-file", required=True, help="Key manifest path")
    probe_cmd.add_argument("--attempts", type=int, default=16, help="Local probe attempts")

    return parser


def _ensure_workspace(path: str | Path) -> Path:
    target = Path(path).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    return target


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "generate-key":
            key_path = Path(args.key_out).expanduser()
            result = generate_local_key(key_path, algorithm=args.algorithm)
            print(f"Generated offline key at {key_path} (fingerprint={result['fingerprint']})")
            return 0

        if args.command == "encrypt":
            workspace = _ensure_workspace(DEFAULT_APP_WORKSPACE)
            input_dir = Path(args.input_dir).expanduser().resolve()
            zip_path = Path(args.zip_out).expanduser().resolve()
            key_file = Path(args.key_file).expanduser().resolve()
            result = encrypt_directory(input_dir, zip_path, key_file)
            print(f"Encrypted archive created at {result['zip_path']} ({result['member_count']} files)")
            print(f"Workspace: {workspace}")
            return 0

        if args.command == "unpack":
            key_file = Path(args.key_file).expanduser().resolve()
            zip_path = Path(args.zip_path).expanduser().resolve()
            output_dir = Path(args.output_dir).expanduser().resolve()
            unpacked = unpack_archive(zip_path, key_file, output_dir=output_dir)
            print(f"Archive unpacked to {unpacked}")
            return 0

        if args.command == "normalize":
            manifest = normalize_directory(args.input_dir, output_manifest=args.output_manifest, include_content=args.include_content)
            print(f"Normalized manifest has {len(manifest.get('entries', []))} entries")
            return 0

        if args.command == "rezip-clean":
            zip_out = rezip_clean_directory(args.input_dir, args.zip_out)
            print(f"Clean zip rebuilt at {zip_out}")
            return 0

        if args.command == "probe-key":
            summary = local_key_probe(args.key_file, attempts=args.attempts)
            print(f"Probe complete: attempts={summary['attempts']} verified={summary['verified']}")
            return 0

        parser.error(f"Unsupported command: {args.command}")
        return 2
    except Exception as exc:  # pragma: no cover - app safety surface
        print(f"offline-zip-keymaster error: {exc}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
