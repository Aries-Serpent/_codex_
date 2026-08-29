# 1) Rust compile check
cargo check --manifest-path src/codex_core/Cargo.toml

# 2) Build wheel locally (optional)
python -m pip install maturin
maturin build --manifest-path src/codex_core/Cargo.toml --release --out dist

# 3) Install and test integration
pip install codex_core --no-index --find-links dist --force-reinstall
python scripts/test_orchestrator.py