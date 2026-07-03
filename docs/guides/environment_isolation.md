# Rust/Python Environment Isolation

To avoid conflicts in CI and local development, we strictly isolate Rust and Python environments.

## Python
- Always use a virtual environment (`.venv`).
- Dependencies are managed via `pip` inside the venv.

## Rust
- Managed via `rustup`.
- Toolchain is isolated to `~/.rustup` and `~/.cargo`.

## Cross-Language (PyO3/Maturin)
When building Python bindings for Rust:
1. Build Rust inside `maturin build`.
2. Install the generated `.whl` into the isolated Python virtual environment.
3. Do not run `cargo test` and `pytest` in the same shell session without resetting paths.
