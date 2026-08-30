cargo check --manifest-path src/codex_core/Cargo.toml
python -m pip install maturin
maturin build --manifest-path src/codex_core/Cargo.toml --release --out dist
pip install codex_core --no-index --find-links dist --force-reinstall
python scripts/test_orchestrator.py