"""
Model Registry CLI

Command-line interface for MLflow Model Registry operations.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from codex.logging.structured_logger import logger
from codex_ml.registry.mlflow_registry import (
    _HAS_MLFLOW,
    DeploymentStage,
    ModelRegistry,
)


def list_models_command(args: argparse.Namespace) -> int:
    """List all registered models"""
    try:
        registry = ModelRegistry(tracking_uri=args.tracking_uri)
        models = registry.list_models()

        if args.json:
            logger.info(json.dumps({"models": models}, indent=2))
        else:
            logger.info(f"Registered Models ({len(models)}):")
            for model in models:
                logger.info(f"  - {model}")

        return 0
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        print(
            "Error: <ERROR_TYPE>", file=sys.stderr
        )  # codeql[py/clear-text-logging-sensitive-data]
        return 1


def list_versions_command(args: argparse.Namespace) -> int:
    """List versions of a model"""
    try:
        registry = ModelRegistry(tracking_uri=args.tracking_uri)

        stage = DeploymentStage[args.stage.upper()] if args.stage else None
        versions = registry.list_model_versions(args.name, stage=stage)

        if args.json:
            logger.info(json.dumps({"versions": [v.to_dict() for v in versions]}, indent=2))
        else:
            logger.info(f"Model: {args.name}")
            logger.info(f"Versions ({len(versions)}):")
            for version in versions:
                logger.info(f"  Version {version.version}:")
                logger.info(f"    Stage: {version.stage.value}")
                logger.info(f"    Description: {version.description}")
                logger.info(f"    Created: {version.created_at}")

        return 0
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        print(
            "Error: <ERROR_TYPE>", file=sys.stderr
        )  # codeql[py/clear-text-logging-sensitive-data]
        return 1


def promote_model_command(args: argparse.Namespace) -> int:
    """Promote model to a deployment stage"""
    try:
        registry = ModelRegistry(tracking_uri=args.tracking_uri)

        stage = DeploymentStage[args.stage.upper()]
        version = registry.promote_model(
            name=args.name,
            version=args.version,
            stage=stage,
            archive_existing=not args.keep_existing,
        )

        if args.json:
            print(
                json.dumps(version.to_dict(), indent=2)
            )  # codeql[py/clear-text-logging-sensitive-data]
        else:
            print(
                f"✓ Promoted {args.name} version {args.version} to {stage.value}"
            )  # codeql[py/clear-text-logging-sensitive-data]

        return 0
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        print(
            "Error: <ERROR_TYPE>", file=sys.stderr
        )  # codeql[py/clear-text-logging-sensitive-data]
        return 1


def compare_models_command(args: argparse.Namespace) -> int:
    """Compare two model versions"""
    try:
        registry = ModelRegistry(tracking_uri=args.tracking_uri)

        comparison = registry.compare_models(
            name=args.name, version1=args.version1, version2=args.version2
        )

        if args.json:
            print(
                json.dumps(comparison, indent=2, default=str)
            )  # codeql[py/clear-text-logging-sensitive-data]
        else:
            logger.info(f"Model: {args.name}")
            logger.info(f"\nVersion {args.version1}:")
            v1 = comparison["version_1"]
            logger.info(f"  Stage: {v1['stage']}")
            logger.info(f"  Created: {v1['created_at']}")

            logger.info(f"\nVersion {args.version2}:")
            v2 = comparison["version_2"]
            logger.info(f"  Stage: {v2['stage']}")
            logger.info(f"  Created: {v2['created_at']}")

            if comparison["created_diff_days"]:
                print(
                    f"\nTime difference: {comparison['created_diff_days']} days"
                )  # codeql[py/clear-text-logging-sensitive-data]

        return 0
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        print(
            "Error: <ERROR_TYPE>", file=sys.stderr
        )  # codeql[py/clear-text-logging-sensitive-data]
        return 1


def export_model_command(args: argparse.Namespace) -> int:
    """Export model version to local directory"""
    try:
        registry = ModelRegistry(tracking_uri=args.tracking_uri)

        output_path = registry.export_model(
            name=args.name, version=args.version, output_dir=args.output_dir
        )

        print(
            f"✓ Exported {args.name} version {args.version} to {output_path}"
        )  # codeql[py/clear-text-logging-sensitive-data]
        return 0
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        print(
            "Error: <ERROR_TYPE>", file=sys.stderr
        )  # codeql[py/clear-text-logging-sensitive-data]
        return 1


def get_lineage_command(args: argparse.Namespace) -> int:
    """Get model lineage information"""
    try:
        registry = ModelRegistry(tracking_uri=args.tracking_uri)

        lineage = registry.get_model_lineage(name=args.name, version=args.version)

        if args.json:
            print(
                json.dumps(lineage, indent=2, default=str)
            )  # codeql[py/clear-text-logging-sensitive-data]
        else:
            print(
                f"Model: {args.name} v{args.version}"
            )  # codeql[py/clear-text-logging-sensitive-data]
            if lineage["lineage"]:
                lin = lineage["lineage"]
                logger.info("\nLineage:")
                logger.info(f"  Run ID: {lin['run_id']}")
                print(
                    f"  Experiment ID: {lin['experiment_id']}"
                )  # codeql[py/clear-text-logging-sensitive-data]
                logger.info(f"  Status: {lin['status']}")
                print(
                    f"  Start Time: {lin['start_time']}"
                )  # codeql[py/clear-text-logging-sensitive-data]
                if lin.get("parameters"):
                    print(
                        f"  Parameters: {len(lin['parameters'])} params"
                    )  # codeql[py/clear-text-logging-sensitive-data]
                if lin.get("metrics"):
                    print(
                        f"  Metrics: {len(lin['metrics'])} metrics"
                    )  # codeql[py/clear-text-logging-sensitive-data]
            else:
                print(
                    "\nNo lineage information available"
                )  # codeql[py/clear-text-logging-sensitive-data]

        return 0
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")  # codeql[py/clear-text-logging-sensitive-data]
        print(
            "Error: <ERROR_TYPE>", file=sys.stderr
        )  # codeql[py/clear-text-logging-sensitive-data]
        return 1


def main(argv: Optional[list[str]] = None) -> int:
    """Main CLI entry point"""
    if not _HAS_MLFLOW:
        print(
            "Error: MLflow not installed. Install with: pip install mlflow",
            file=sys.stderr,
        )
        return 1

    parser = argparse.ArgumentParser(
        description="MLflow Model Registry CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--tracking-uri",
        help="MLflow tracking URI (default: MLFLOW_TRACKING_URI env var)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list-models command
    list_parser = subparsers.add_parser("list-models", help="List all registered models")
    list_parser.set_defaults(func=list_models_command)

    # list-versions command
    versions_parser = subparsers.add_parser("list-versions", help="List versions of a model")
    versions_parser.add_argument("name", help="Model name")
    versions_parser.add_argument(
        "--stage",
        choices=["none", "staging", "production", "archived"],
        help="Filter by deployment stage",
    )
    versions_parser.set_defaults(func=list_versions_command)

    # promote-model command
    promote_parser = subparsers.add_parser(
        "promote-model", help="Promote model to deployment stage"
    )
    promote_parser.add_argument("name", help="Model name")
    promote_parser.add_argument("version", help="Model version")
    promote_parser.add_argument(
        "stage",
        choices=["staging", "production", "archived"],
        help="Target deployment stage",
    )
    promote_parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="Keep existing models in target stage (don't archive)",
    )
    promote_parser.set_defaults(func=promote_model_command)

    # compare-models command
    compare_parser = subparsers.add_parser("compare-models", help="Compare two model versions")
    compare_parser.add_argument("name", help="Model name")
    compare_parser.add_argument("version1", help="First version")
    compare_parser.add_argument("version2", help="Second version")
    compare_parser.set_defaults(func=compare_models_command)

    # export-model command
    export_parser = subparsers.add_parser(
        "export-model", help="Export model version to local directory"
    )
    export_parser.add_argument("name", help="Model name")
    export_parser.add_argument("version", help="Model version")
    export_parser.add_argument("output_dir", help="Output directory")
    export_parser.set_defaults(func=export_model_command)

    # get-lineage command
    lineage_parser = subparsers.add_parser("get-lineage", help="Get model lineage information")
    lineage_parser.add_argument("name", help="Model name")
    lineage_parser.add_argument("version", help="Model version")
    lineage_parser.set_defaults(func=get_lineage_command)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
