#!/usr/bin/env python3
"""Smart CLI for audio tuning."""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="🎵 Intelligent Audio Auto-Tune",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('path', type=str, help='Path to audio file or directory')
    parser.add_argument('--output', '-o', type=str, help='Output directory')
    parser.add_argument('--preview', '-p', action='store_true', help='Generate preview')
    parser.add_argument('--aggressive', '-a', action='store_true', help='Aggressive cleaning')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    print("🎵" * 30)
    print("   INTELLIGENT AUDIO AUTO-TUNE")
    print("🎵" * 30)
    
    try:
        from services.audio.workflow.auto_tune_workflow import AutoTuneWorkflow
        workflow = AutoTuneWorkflow(cognitive_mode=True)
        result = workflow.process_path(
            input_path=args.path,
            output_dir=args.output,
            preview=args.preview,
            aggressive=args.aggressive,
            interactive=args.interactive
        )
        
        print("\n" + "="*60)
        print("PROCESSING COMPLETE")
        print("="*60)
        
        if result.success:
            print(f"✅ Successfully processed {result.total_files} file(s)")
            print(f"   Success rate: {result.success_rate:.1%}")
            print(f"   Average quality improvement: {result.avg_improvement:.1f}/10")
            print(f"   Total time: {result.total_time:.1f}s")
            print(f"   Output location: {result.output_dir}")
        else:
            print(f"❌ Processing failed: {result.error}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
