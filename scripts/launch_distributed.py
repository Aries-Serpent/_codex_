#!/usr/bin/env python
"""
Launch Distributed

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/launch_distributed.py [options]

    Examples:
    $ python scripts/launch_distributed.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


import argparse
import logging

logger = logging.getLogger(__name__)
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="Launch distributed training")
    parser.add_argument("script", help="Training script to run")
    parser.add_argument("--num-gpus", type=int, default=1, help="GPUs per node")
    parser.add_argument("--num-nodes", type=int, default=1, help="Number of nodes")
    parser.add_argument("--node-rank", type=int, default=0, help="Rank of this node")
    parser.add_argument("--master-addr", default="localhost", help="Master address")
    parser.add_argument("--master-port", default="29500", help="Master port")
    parser.add_argument("script_args", nargs="*", help="Arguments for training script")

    args = parser.parse_args()

    world_size = args.num_gpus * args.num_nodes

    # Use torchrun for distributed launch
    cmd = [
        sys.executable,
        "-m",
        "torch.distributed.run",
        f"--nproc_per_node={args.num_gpus}",
        f"--nnodes={args.num_nodes}",
        f"--node_rank={args.node_rank}",
        f"--master_addr={args.master_addr}",
        f"--master_port={args.master_port}",
        args.script,
    ] + args.script_args

    print("=" * 70)
    print("DISTRIBUTED TRAINING LAUNCHER")
    print("=" * 70)
    print(f"World size: {world_size}")
    print(f"Nodes: {args.num_nodes}")
    print(f"GPUs per node: {args.num_gpus}")
    print(f"Node rank: {args.node_rank}")
    print(f"Master address: {args.master_addr}:{args.master_port}")
    print(f"Script: {args.script}")
    print(f"Arguments: {' '.join(args.script_args)}")
    print("=" * 70)
    print(f"\nCommand: {' '.join(cmd)}\n")
    print("=" * 70)

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nError: Training script failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
