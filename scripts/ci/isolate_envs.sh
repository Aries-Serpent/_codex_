#!/bin/bash
# Rust and Python Environment Isolation Setup

set -e

echo "Setting up isolated Python environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

echo "Setting up Rust environment..."
rustup default stable
rustup component add clippy rustfmt

echo "Environment isolation complete. Python uses .venv, Rust uses rustup."
