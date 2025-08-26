# Deep Research Prompts for Repository TODOs

This document enumerates all current TODO comments in the repository and provides suggested prompts for ChatGPT-5 Deep Research to investigate and address them.

## Pipeline Step Handlers
- **Locations:** `tools/apply_hydra_scaffold.py:155`, `src/codex_ml/cli/main.py:46`
- **TODO:** Implement real step handlers; currently the pipeline simply reports success.
- **Research Prompt:** "Investigate common step-handler patterns for Hydra-managed ML pipelines. Propose a modular design for real step implementations (e.g., data prep, training, evaluation) and outline how to integrate them into the existing `_dispatch_pipeline` function. Include sample code and error-handling strategies."

## GPU Training Example
- **Locations:** `tools/apply_stack_polish.py:553`, `codex_script.py:516`, `notebooks/gpu_training_example.ipynb:4`
- **TODO:** Fill the GPU training example with an end-to-end demo.
- **Research Prompt:** "Develop a complete GPU training demonstration notebook. Select a modest dataset, configure training with PyTorch, and show metrics visualization. Ensure the example runs on a single GPU and includes explanatory markdown."

## Interface Constructor Arguments
- **Locations:** `tools/apply_interfaces.py:209`, `tools/apply_interfaces.py:222`, `tools/apply_interfaces.py:229`, `tests/test_interfaces_compat.py:28`, `tests/test_interfaces_compat.py:42`, `tests/test_interfaces_compat.py:50`
- **TODO:** Supply constructor kwargs where needed when instantiating Tokenizer, RewardModel, and RLAgent implementations.
- **Research Prompt:** "For each interface (TokenizerAdapter, RewardModel, RLAgent), determine the minimal constructor parameters required by common implementations. Propose updates to tests that pass these arguments so instantiation succeeds without relying on default constructors."

## Interface Test Enhancements
- **Locations:** `tools/apply_interfaces.py:240-241`, `tests/test_interfaces_compat.py:62-63`
- **TODOs:**
  - Update tests to pass minimal viable config if implementations require constructor arguments.
  - Wire a config reader to set `CODEX_*_PATH` from `configs/interfaces.yaml` during pytest collection.
- **Research Prompt:** "Design a configuration mechanism that reads module paths from `configs/interfaces.yaml` and sets `CODEX_*_PATH` environment variables before tests run. Describe how to adjust tests to consume this configuration and to provide constructor arguments when required."

## Interface Configuration Placeholders
- **Locations:** `configs/interfaces.example.yaml:3`, `tools/apply_interfaces.py:249`
- **TODO:** Replace placeholder `yourpkg.tokenizers.hf:HFTokenizer` with actual module and class names.
- **Research Prompt:** "Identify realistic tokenizer, reward model, and RL agent implementations suitable for this project. Supply concrete `module:Class` strings and document why they are appropriate defaults."

## README Badge Slug
- **Location:** `tools/apply_ci_precommit.py:14`
- **TODO:** README badges still reference a TODO repository slug.
- **Research Prompt:** "Determine the correct GitHub repository slug and provide the updated badge markdown snippets that should appear in `README.md`."

## PEFT LoRA Integration
- **Location:** `codex_script.py:244`
- **TODO:** Wire `peft.get_peft_model(model, LoraConfig(**cfg))` into `apply_lora`.
- **Research Prompt:** "Explain how to integrate PEFT's LoRA adaptation into `apply_lora`. Include necessary imports, configuration schema, and example usage, ensuring graceful fallback when `peft` is unavailable."

