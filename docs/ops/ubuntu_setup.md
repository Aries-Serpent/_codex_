# Ubuntu Setup

This guide describes how to prepare an Ubuntu machine for the Codex project.

## System dependencies

Run the following to install required packages:

```bash
make setup
```text
Set `CODEX_ENABLE_CUDA=1` to install the CUDA toolkit as well.

## Python virtual environment

Create the virtual environment and install Python requirements:

```bash
make venv
```text
Activate the environment with:

```bash
source .venv/bin/activate
```text
## Environment information

To display the current OS, Python and CUDA details:

```bash
make env-info
```text
## Verification

After activating the virtual environment, verify packages:

```bash
python -c "import torch, transformers"
```text