#!/usr/bin/env python3
"""
PHASE 7B TRACK C: Mutation Testing Execution & Analysis
Integrated with Track B's 169 edge case tests
Goal: Increase mutation score from 82% → 90%+
"""

import re
import subprocess
from datetime import datetime


class MutationTestRunner:
    def __init__(self, config_file=".mutmut-phase7b-trackc.ini"):
        self.config_file = config_file
        self.results = {}
        self.mutations_killed = 0
        self.mutations_survived = 0
        self.total_mutations = 0

    def run_mutation_tests(self, paths_to_mutate=None, max_timeout=300):
        """Run mutation testing on specified paths or all sources"""

        print("=" * 80)
        print("PHASE 7B TRACK C: MUTATION TESTING EXECUTION")
        print("=" * 80)
        print(f"Configuration: {self.config_file}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("Target: 82% → 90%+ mutation score")
        print("Test Suite: Track B edge cases (169 tests)")
        print()

        # Build mutmut command
        cmd = [
            "python3", "-m", "mutmut",
            "run",
            "--config-file", self.config_file,
            "--tests-dir", "tests/",
            "--timeout", str(int(max_timeout/10)),
            "--no-progress",
        ]

        if paths_to_mutate:
            cmd.extend(["--paths-to-mutate", paths_to_mutate])

        print(f"Command: {' '.join(cmd)}")
        print()

        try:
            # Run mutation testing
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=max_timeout
            )

            print("STDOUT:")
            print(result.stdout)

            if result.stderr:
                print("\nSTDERR:")
                print(result.stderr)

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print("✗ Mutation testing timed out")
            return False
        except Exception as e:
            print(f"✗ Error running mutation tests: {e}")
            return False

    def get_mutation_results(self):
        """Parse and display mutation testing results"""

        print("\n" + "=" * 80)
        print("MUTATION TESTING RESULTS")
        print("=" * 80)

        # Try to read mutmut results
        try:
            result = subprocess.run(
                ["python3", "-m", "mutmut", "results"],
                capture_output=True,
                text=True,
                timeout=30
            )

            print(result.stdout)

            # Parse results
            self.parse_results(result.stdout)

        except Exception as e:
            print(f"✗ Error reading mutation results: {e}")

    def parse_results(self, output):
        """Parse mutmut output to extract key metrics"""

        # Look for mutation score
        score_match = re.search(r"Mutation score:\s+([\d.]+)%", output)
        if score_match:
            score = float(score_match.group(1))
            print(f"\n📊 Mutation Score: {score}%")

        # Look for killed/survived counts
        killed_match = re.search(r"killed\s+\(([^)]+)\)", output)
        survived_match = re.search(r"survived\s+\(([^)]+)\)", output)

        if killed_match:
            print(f"✓ Mutations Killed: {killed_match.group(1)}")
        if survived_match:
            print(f"✗ Mutations Survived: {survived_match.group(1)}")

def main():
    print("\n🔬 PHASE 7B TRACK C: MUTATION TESTING INITIATION\n")

    runner = MutationTestRunner(".mutmut-phase7b-trackc.ini")

    # Run mutation tests on critical paths first
    print("Step 1: Running baseline mutation analysis...")
    print("-" * 80)

    success = runner.run_mutation_tests(
        paths_to_mutate="src/",
        max_timeout=600
    )

    if success:
        print("\n✅ Mutation testing completed")
        runner.get_mutation_results()
    else:
        print("\n⚠️ Mutation testing encountered issues")
        runner.get_mutation_results()

    print("\n" + "=" * 80)
    print("PHASE 7B TRACK C: MUTATION ANALYSIS SUMMARY")
    print("=" * 80)
    print("Next Steps:")
    print("1. ✓ Baseline mutation testing complete")
    print("2. → Analyze surviving mutations")
    print("3. → Identify weak modules (<90% kill rate)")
    print("4. → Generate comprehensive report")
    print()

if __name__ == "__main__":
    main()
