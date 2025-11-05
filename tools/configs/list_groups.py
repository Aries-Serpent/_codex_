#!/usr/bin/env python3
"""List Hydra config groups and options (offline discovery).

This tool helps discover available Hydra configuration groups and search paths
without requiring network access or full application initialization.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def discover_config_roots() -> dict[str, list[str] | str]:
    """Discover Hydra config search paths.
    
    Returns
    -------
    dict
        JSON-serializable dict with 'roots' list and 'note' string
    """
    result: dict[str, list[str] | str] = {
        "roots": [],
        "note": "For fuller group listing, use Hydra's compose API with a live config"
    }
    
    try:
        # Try to import Hydra
        from hydra._internal.utils import create_config_search_path
        from hydra.core.global_hydra import GlobalHydra
        
        # Initialize if needed
        if not GlobalHydra.instance().is_initialized():
            try:
                from hydra import initialize_config_dir
                # Try to find config directory
                repo_root = Path(__file__).resolve().parent.parent.parent
                config_dir = repo_root / "configs"
                if config_dir.exists():
                    initialize_config_dir(
                        version_base=None,
                        config_dir=str(config_dir.resolve())
                    )
            except Exception:
                pass  # Continue with uninitialized state
        
        # Get search path
        try:
            search_path = create_config_search_path("codex")
            roots = []
            for provider in search_path.provider:
                path = provider.path
                if path:
                    roots.append(str(path))
            result["roots"] = roots
        except Exception as e:
            result["roots"] = []
            result["error"] = f"Failed to get search path: {e}"
    
    except ImportError:
        result["error"] = "Hydra not available (install with: pip install hydra-core)"
    except Exception as e:
        result["error"] = f"Discovery failed: {e}"
    
    return result


def main() -> int:
    """Main entry point."""
    try:
        result = discover_config_roots()
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        error_result = {
            "roots": [],
            "error": str(e)
        }
        print(json.dumps(error_result, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
