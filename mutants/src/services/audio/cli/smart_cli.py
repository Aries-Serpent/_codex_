#!/usr/bin/env python3
"""Smart CLI for audio tuning and transcription."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="🎵 Intelligent Audio Workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    tune_parser = subparsers.add_parser("tune", help="Run auto-tune workflow")
    tune_parser.add_argument("path", type=str, help="Path to audio file or directory")
    tune_parser.add_argument("--output", "-o", type=str, help="Output directory")
    tune_parser.add_argument("--preview", "-p", action="store_true", help="Generate preview")
    tune_parser.add_argument("--aggressive", "-a", action="store_true", help="Aggressive cleaning")
    tune_parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")

    transcribe_parser = subparsers.add_parser("transcribe", help="Run transcription workflow")
    transcribe_parser.add_argument("path", type=str, help="Path to media file or directory")
    transcribe_parser.add_argument("--output", "-o", type=str, help="Output directory")
    transcribe_parser.add_argument(
        "--speaker-map",
        type=str,
        default=None,
        help="Path to JSON speaker map (e.g. SPEAKER_00 -> Alice)",
    )
    transcribe_parser.add_argument(
        "--interactive-speakers",
        action="store_true",
        help="Prompt for speaker naming when map values are missing",
    )
    transcribe_parser.add_argument(
        "--formats",
        type=str,
        default="txt,json",
        help="Comma-separated output formats: txt,json,srt,vtt",
    )
    transcribe_parser.add_argument(
        "--diarization-backend",
        type=str,
        default="acoustic-clustering",
        choices=["acoustic-clustering", "pyannote"],
        help="Speaker diarization backend",
    )
    transcribe_parser.add_argument(
        "--backend",
        type=str,
        default="mock",
        choices=["mock", "faster-whisper"],
        help="Transcription backend",
    )
    transcribe_parser.add_argument(
        "--model-size",
        type=str,
        default="small",
        help="Model size selection for backend runtime",
    )
    transcribe_parser.add_argument(
        "--max-speakers",
        type=int,
        default=4,
        help="Maximum number of speakers to detect",
    )
    transcribe_parser.add_argument(
        "--max-duration-seconds",
        type=int,
        default=4 * 60 * 60,
        help="Memory-safe duration limit in seconds",
    )

    return parser


def apply_backward_compatible_default_command(argv: list[str]) -> list[str]:
    if len(argv) <= 1:
        return argv

    first_arg = argv[1]
    if first_arg.startswith("-"):
        return argv

    known_commands = {"tune", "transcribe"}
    if first_arg not in known_commands:
        return [argv[0], "tune", *argv[1:]]

    return argv


def _run_tune(args: argparse.Namespace) -> int:
    from services.audio.workflow.auto_tune_workflow import AutoTuneWorkflow

    workflow = AutoTuneWorkflow(cognitive_mode=True)
    result = workflow.process_path(  # type: ignore[call-arg]
        input_path=args.path,
        output_dir=args.output,
        preview=args.preview,
        aggressive=args.aggressive,
        interactive=args.interactive,
    )

    print("\n" + "=" * 60)
    print("AUTO-TUNE COMPLETE")
    print("=" * 60)

    if result.success:
        print(f"✅ Successfully processed {result.total_files} file(s)")
        print(f"   Success rate: {result.success_rate:.1%}")  # type: ignore[attr-defined]
        print(f"   Average quality improvement: {result.avg_improvement:.1f}/10")  # type: ignore[attr-defined]
        print(f"   Total time: {result.total_time:.1f}s")  # type: ignore[attr-defined]
        print(f"   Output location: {result.output_dir}")  # type: ignore[attr-defined]
        return 0

    print(f"❌ Processing failed: {result.error}")
    return 1


def _run_transcribe(args: argparse.Namespace) -> int:
    from services.audio.workflow.transcription_workflow import (
        AudioTranscriptionWorkflow,
        TranscriptionConfig,
        load_speaker_map,
    )

    speaker_map = load_speaker_map(args.speaker_map)
    output_formats = [part.strip() for part in args.formats.split(",") if part.strip()]

    workflow = AudioTranscriptionWorkflow(
        config=TranscriptionConfig(
            max_speakers=args.max_speakers,
            max_duration_seconds=args.max_duration_seconds,
            diarization_backend=args.diarization_backend,
            model_size=args.model_size,
            transcription_backend=args.backend,
        )
    )

    result = workflow.process_path(
        input_path=args.path,
        output_dir=args.output,
        speaker_map=speaker_map,
        interactive_speakers=args.interactive_speakers,
        output_formats=output_formats,
    )

    print("\n" + "=" * 60)
    print("TRANSCRIPTION COMPLETE")
    print("=" * 60)

    if not result.success:
        print(f"❌ Transcription failed: {result.error or 'see file errors below'}")

    for item in result.results:
        rel_name = item.input_path.name
        if item.success:
            produced = ", ".join(
                f"{fmt}:{Path(path).name}" for fmt, path in item.output_files.items()
            )
            speakers = ", ".join(item.detected_speakers) if item.detected_speakers else "none"
            print(f"✅ {rel_name} -> speakers [{speakers}] -> {produced}")
        else:
            print(f"❌ {rel_name}: {item.error}")

    print(
        f"Processed={result.processed_files} Failed={result.failed_files} "
        f"Total={result.processed_files + result.failed_files}"
    )
    return 0 if result.failed_files == 0 else 1


def main() -> int:
    argv = apply_backward_compatible_default_command(sys.argv)
    parser = _build_parser()
    args = parser.parse_args(argv[1:])

    if not args.command:
        parser.print_help()
        return 1

    print("🎵" * 30)
    print("   INTELLIGENT AUDIO WORKFLOWS")
    print("🎵" * 30)

    try:
        if args.command == "tune":
            return _run_tune(args)
        if args.command == "transcribe":
            return _run_transcribe(args)
        parser.print_help()
        return 1
    except (ValueError, TypeError) as exc:
        type(exc).__name__
        print("❌ Error: <ERROR_TYPE>")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
