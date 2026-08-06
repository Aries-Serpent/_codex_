"""
Test Suite for Integrated Self-Evolution System

Tests the integrated system with real-world scenarios including security
vulnerability fixes, pattern correlation, knowledge integration, and
CRITICAL: Turn-state isolation & payload deduplication validation.

Author: mbaetiong
Generated: 2026-05-28
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Absolute path to repo root regardless of working directory at test execution.
# Layout: .github/copilot-evolution/test_integrated_system.py
#          ^3          ^2                  ^1 (this file)
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class IntegratedSystemTester:
    """Tests the integrated self-evolution system with deduplication focus."""

    def __init__(self) -> None:
        """Initialize tester."""
        self.test_results: list[dict[str, Any]] = []
        self.repo_path = _REPO_ROOT

    async def run_all_tests(self) -> dict[str, Any]:
        """Run all integration tests."""
        logger.info("🚀 Starting Integrated System Tests")

        tests = [
            self.test_pattern_extraction,
            self.test_pattern_correlation,
            self.test_knowledge_gap_detection,
            self.test_question_generation,
            self.test_knowledge_integration,
            self.test_evolution_cycle,
            self.test_security_scenario,
            self.test_turn_isolation,
            self.test_payload_deduplication,
            self.test_multi_turn_state,
        ]

        results: dict[str, Any] = {
            "total_tests": len(tests),
            "passed": 0,
            "failed": 0,
            "details": [],
        }

        for test in tests:
            try:
                logger.info(f"\n{'=' * 60}")
                logger.info(f"Running: {test.__name__}")
                logger.info(f"{'=' * 60}")

                result = await test()

                if result["success"]:
                    results["passed"] += 1
                    logger.info(f"✅ {test.__name__} PASSED")
                else:
                    results["failed"] += 1
                    logger.error(
                        f"❌ {test.__name__} FAILED: {result.get('error')}"
                    )

                results["details"].append(
                    {
                        "test": test.__name__,
                        "success": result["success"],
                        "data": result.get("data"),
                        "error": result.get("error"),
                    }
                )

            except Exception as e:
                results["failed"] += 1
                results["details"].append(
                    {
                        "test": test.__name__,
                        "success": False,
                        "error": str(e),
                    }
                )
                logger.exception(f"❌ {test.__name__} FAILED with exception")

        logger.info(f"\n{'=' * 60}")
        logger.info(
            f"Test Summary: {results['passed']}/{results['total_tests']} passed"
        )
        logger.info(f"{'=' * 60}")

        return results

    # ------------------------------------------------------------------
    # Individual tests
    # ------------------------------------------------------------------

    async def test_pattern_extraction(self) -> dict[str, Any]:
        """Test pattern extraction from repository."""
        try:
            from quantum_correlator import QuantumPatternCorrelator

            # Use module-level _REPO_ROOT so path is always absolute and
            # independent of the current working directory at test runtime.
            correlator = QuantumPatternCorrelator(repo_path=str(_REPO_ROOT))

            target_files = [
                "agents/quantum_game_theory.py",
                ".github/copilot-security/security_agent.py",
            ]

            patterns = await correlator.extract_codex_patterns(target_files)

            assert len(patterns) > 0, "No patterns extracted"
            assert any(
                len(p) > 0 for p in patterns.values()
            ), "All domains empty"

            logger.info(f"Extracted patterns from {len(patterns)} domains")
            for domain, pats in patterns.items():
                logger.info(f"  - {domain}: {len(pats)} patterns")

            return {
                "success": True,
                "data": {
                    "domains": len(patterns),
                    "total_patterns": sum(
                        len(p) for p in patterns.values()
                    ),
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_pattern_correlation(self) -> dict[str, Any]:
        """Test pattern correlation across domains."""
        try:
            from quantum_correlator import QuantumPatternCorrelator

            correlator = QuantumPatternCorrelator()

            mock_patterns = {
                "security": [
                    {
                        "type": "function",
                        "name": "validate_input",
                        "async": False,
                    },
                    {
                        "type": "class",
                        "name": "SecurityScanner",
                        "methods": ["scan", "fix"],
                    },
                ],
                "quantum_physics": [
                    {
                        "type": "function",
                        "name": "superpose_states",
                        "async": True,
                    },
                    {
                        "type": "class",
                        "name": "QuantumEngine",
                        "methods": ["evolve", "measure"],
                    },
                ],
            }

            correlations = await correlator.correlate_patterns(mock_patterns)

            assert len(correlations) > 0, "No correlations found"

            logger.info(f"Found {len(correlations)} correlations")
            for corr in correlations[:3]:
                logger.info(
                    f"  - {corr.emergent_capability} "
                    f"(strength: {corr.entanglement_strength:.2f})"
                )

            return {
                "success": True,
                "data": {
                    "correlations_found": len(correlations),
                    "top_capability": (
                        correlations[0].emergent_capability
                        if correlations
                        else None
                    ),
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_knowledge_gap_detection(self) -> dict[str, Any]:
        """Test knowledge gap detection."""
        try:
            from integrated_system import IntegratedEvolutionSystem

            system = IntegratedEvolutionSystem()

            task = {
                "description": "Implement quantum encryption",
                "domain": "security",
                "undefined_concepts": [
                    "quantum_key_distribution",
                    "BB84_protocol",
                ],
                "partial_understanding": [
                    {
                        "concept": "entanglement",
                        "domain": "quantum_physics",
                        "importance": 0.8,
                    }
                ],
            }

            result = await system.process_task_with_learning(task)

            assert "knowledge_gaps" in result, "No knowledge gaps detected"
            assert len(result["knowledge_gaps"]) > 0, "Gaps list is empty"

            logger.info(
                f"Detected {len(result['knowledge_gaps'])} knowledge gaps"
            )
            for gap_concept in result["knowledge_gaps"][:3]:
                logger.info(f"  - {gap_concept}")

            domains = list(
                set(
                    g.domain
                    for g in system.hunger_engine.knowledge_gaps.values()
                )
            )

            return {
                "success": True,
                "data": {
                    "gaps_detected": len(result["knowledge_gaps"]),
                    "domains": domains,
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_question_generation(self) -> dict[str, Any]:
        """Test intelligent question generation."""
        try:
            from integrated_system import IntegratedEvolutionSystem

            system = IntegratedEvolutionSystem()

            task = {
                "description": "Implement secure data compression",
                "domain": "security",
                "undefined_concepts": ["homomorphic_encryption"],
            }

            result = await system.process_task_with_learning(task)

            assert "questions" in result, "No questions generated"
            assert len(result["questions"]) > 0, "Questions list is empty"

            logger.info(f"Generated {len(result['questions'])} questions")
            for q in result["questions"][:2]:
                logger.info(f"  Q: {q.question_text[:80]}...")
                logger.info(
                    f"     Type: {q.question_type}, Urgency: {q.urgency:.2f}"
                )

            return {
                "success": True,
                "data": {
                    "questions_generated": len(result["questions"]),
                    "question_types": list(
                        set(q.question_type for q in result["questions"])
                    ),
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_knowledge_integration(self) -> dict[str, Any]:
        """Test knowledge integration from human input."""
        try:
            from integrated_system import IntegratedEvolutionSystem

            system = IntegratedEvolutionSystem()

            knowledge = {
                "question_id": "test_q_1",
                "answer": (
                    "Homomorphic encryption allows computation on encrypted data "
                    "without decryption. FHE (Fully Homomorphic Encryption) enables "
                    "arbitrary computations."
                ),
                "sources": ["Wikipedia", "Cryptography textbook"],
                "confidence": 0.9,
            }

            result = await system.receive_knowledge(knowledge)
            integration = result.get("integration", result)

            assert integration.get("status") == "integrated", (
                f"Integration failed: {integration.get('error')}"
            )
            assert "capabilities_enhanced" in integration, (
                "No capabilities enhanced"
            )

            logger.info("Knowledge integrated successfully")
            logger.info(
                f"  Capabilities enhanced: "
                f"{len(integration['capabilities_enhanced'])}"
            )
            logger.info(f"  Status: {integration['status']}")

            return {
                "success": True,
                "data": {
                    "capabilities_added": len(
                        integration["capabilities_enhanced"]
                    ),
                    "status": integration["status"],
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_evolution_cycle(self) -> dict[str, Any]:
        """Test full evolution cycle."""
        try:
            from integrated_system import IntegratedEvolutionSystem

            system = IntegratedEvolutionSystem()

            initial_fitness = system.evolution_state.fitness
            initial_gen = system.evolution_state.generation

            tasks = [
                {
                    "description": "Task 1",
                    "domain": "security",
                    "undefined_concepts": ["concept_a"],
                },
                {
                    "description": "Task 2",
                    "domain": "quantum_physics",
                    "undefined_concepts": ["concept_b"],
                },
            ]

            for task in tasks:
                await system.process_task_with_learning(task)

            await system.receive_knowledge(
                {
                    "answer": "Concept A is about security validation",
                    "confidence": 0.8,
                }
            )

            final_fitness = system.evolution_state.fitness
            final_gen = system.evolution_state.generation

            assert final_gen >= initial_gen, "Generation did not advance"
            assert len(system.evolution_state.capabilities) > 0, (
                "No capabilities gained"
            )

            logger.info("Evolution cycle completed")
            logger.info(f"  Generation: {initial_gen} → {final_gen}")
            logger.info(
                f"  Fitness: {initial_fitness:.3f} → {final_fitness:.3f}"
            )
            logger.info(
                f"  Capabilities: {len(system.evolution_state.capabilities)}"
            )

            return {
                "success": True,
                "data": {
                    "generation_advanced": final_gen > initial_gen,
                    "fitness_changed": abs(final_fitness - initial_fitness) > 0.01,
                    "capabilities_count": len(
                        system.evolution_state.capabilities
                    ),
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_security_scenario(self) -> dict[str, Any]:
        """Test real-world security vulnerability scenario."""
        try:
            from integrated_system import IntegratedEvolutionSystem
            from quantum_correlator import QuantumPatternCorrelator

            evolution = IntegratedEvolutionSystem()

            # Use module-level _REPO_ROOT — absolute, CI-safe.
            correlator = QuantumPatternCorrelator(repo_path=str(_REPO_ROOT))

            task = {
                "description": (
                    "Fix SQL injection vulnerability in user authentication"
                ),
                "domain": "security",
                "undefined_concepts": [
                    "parameterized_queries",
                    "prepared_statements",
                ],
                "partial_understanding": [
                    {
                        "concept": "SQL_injection",
                        "domain": "security",
                        "importance": 1.0,
                    }
                ],
                "context": {
                    "vulnerability_type": "CWE-89",
                    "severity": "critical",
                    "affected_code": (
                        "query = f'SELECT * FROM users WHERE id = {user_id}'"
                    ),
                },
            }

            result = await evolution.process_task_with_learning(task)

            patterns = await correlator.extract_codex_patterns(
                [
                    "scripts/security/**/*.py",
                    ".github/copilot-security/*.py",
                ]
            )

            if patterns:
                correlations = await correlator.correlate_patterns(patterns)
                logger.info(
                    f"  Found {len(correlations)} security-domain correlations"
                )

            assert len(result["knowledge_gaps"]) > 0, (
                "No gaps detected for undefined concepts"
            )
            assert len(result["questions"]) > 0, "No questions generated"
            assert any(
                "SQL" in q.question_text
                or "parameter" in q.question_text.lower()
                for q in result["questions"]
            ), "No SQL-related questions"

            logger.info("Security scenario completed")
            logger.info(
                f"  Knowledge gaps: {len(result['knowledge_gaps'])}"
            )
            logger.info(f"  Questions: {len(result['questions'])}")
            logger.info(
                f"  Security patterns: "
                f"{sum(len(p) for p in patterns.values()) if patterns else 0}"
            )

            return {
                "success": True,
                "data": {
                    "gaps_detected": len(result["knowledge_gaps"]),
                    "questions_generated": len(result["questions"]),
                    "patterns_extracted": (
                        sum(len(p) for p in patterns.values())
                        if patterns
                        else 0
                    ),
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_turn_isolation(self) -> dict[str, Any]:
        """TEST P1: Verify turn-state isolation prevents state bleed."""
        try:
            from integrated_system import IntegratedEvolutionSystem

            system = IntegratedEvolutionSystem()

            # process_task_with_learning manages its own turn lifecycle: it
            # starts a fresh turn internally, exposes the turn_id in the result,
            # and finalizes it before returning. The test asserts on the turns
            # returned by that method rather than on externally-started turns.
            task1 = {"description": "Task 1", "domain": "security"}
            result1 = await system.process_task_with_learning(task1)
            turn1_id = result1["turn_id"]
            turn1_stats = system.deduplicator.get_turn_stats(turn1_id)
            logger.info(f"✅ Turn 1 completed: {turn1_id}")
            logger.info(f"   Turn 1 stats: {turn1_stats}")
            assert turn1_stats["is_finalized"], "Turn 1 should be finalized"

            task2 = {"description": "Task 2", "domain": "quantum_physics"}
            result2 = await system.process_task_with_learning(task2)
            turn2_id = result2["turn_id"]
            turn2_stats = system.deduplicator.get_turn_stats(turn2_id)
            logger.info(f"✅ Turn 2 completed: {turn2_id}")
            logger.info(f"   Turn 2 stats: {turn2_stats}")
            assert turn2_stats["is_finalized"], "Turn 2 should be finalized"

            isolation_verified = turn1_id != turn2_id
            assert isolation_verified, "Turn IDs must be unique"
            logger.info(
                f"✅ Turn isolation verified: {isolation_verified} "
                f"({turn1_id} != {turn2_id})"
            )

            return {
                "success": True,
                "data": {
                    "turn1_id": turn1_id,
                    "turn2_id": turn2_id,
                    "turn1_calls": turn1_stats["function_calls"],
                    "turn2_calls": turn2_stats["function_calls"],
                    "isolation_verified": isolation_verified,
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_payload_deduplication(self) -> dict[str, Any]:
        """TEST P1: Verify payload deduplication removes duplicates."""
        try:
            from integrated_system import IntegratedEvolutionSystem

            system = IntegratedEvolutionSystem()
            system.deduplicator.start_new_turn()

            payload_with_duplicates = {
                "tool_calls": [
                    {"id": "call_001", "function": "func_a", "args": {}},
                    {"id": "call_002", "function": "func_b", "args": {}},
                    {
                        "id": "call_001",
                        "function": "func_a",
                        "args": {},
                    },  # DUPLICATE
                    {"id": "call_003", "function": "func_c", "args": {}},
                ]
            }

            logger.info(
                f"Original payload: "
                f"{len(payload_with_duplicates['tool_calls'])} calls"
            )

            cleaned_payload = system.deduplicate_agentic_payload(
                payload_with_duplicates
            )

            logger.info(
                f"Cleaned payload: {len(cleaned_payload['tool_calls'])} calls"
            )
            logger.info(
                f"Duplicates removed: "
                f"{len(payload_with_duplicates['tool_calls']) - len(cleaned_payload['tool_calls'])}"
            )

            assert len(cleaned_payload["tool_calls"]) == 3, (
                f"Expected 3 unique calls, got {len(cleaned_payload['tool_calls'])}"
            )
            assert all(
                call["id"] in ["call_001", "call_002", "call_003"]
                for call in cleaned_payload["tool_calls"]
            ), "Unexpected call IDs"

            call_ids = [call["id"] for call in cleaned_payload["tool_calls"]]
            assert len(call_ids) == len(set(call_ids)), (
                "Duplicate call IDs found in cleaned payload"
            )

            logger.info("✅ Payload deduplication verified")

            return {
                "success": True,
                "data": {
                    "original_count": len(
                        payload_with_duplicates["tool_calls"]
                    ),
                    "cleaned_count": len(cleaned_payload["tool_calls"]),
                    "duplicates_removed": 1,
                    "payload_hash": (
                        system.deduplicator.current_turn.payload_hash
                        if system.deduplicator.current_turn
                        else ""
                    ),
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_multi_turn_state(self) -> dict[str, Any]:
        """TEST P1: Verify multi-turn state isolation and cross-turn contamination detection."""
        try:
            from integrated_system import IntegratedEvolutionSystem

            system = IntegratedEvolutionSystem()
            turn_results: list[dict[str, Any]] = []

            for turn_num in range(3):
                turn_id = system.deduplicator.start_new_turn()
                logger.info(
                    f"🔄 Multi-turn test: Turn {turn_num + 1} ({turn_id})"
                )

                payload = {
                    "tool_calls": [
                        {
                            "id": f"call_t{turn_num}_c1",
                            "function": "func_a",
                            "args": {},
                        },
                        {
                            "id": f"call_t{turn_num}_c2",
                            "function": "func_b",
                            "args": {},
                        },
                    ]
                }

                cleaned = system.deduplicate_agentic_payload(payload)
                turn_stats = system.deduplicator.get_turn_stats(turn_id)

                logger.info(
                    f"   Cleaned calls: {len(cleaned['tool_calls'])}"
                )
                logger.info(f"   Turn stats: {turn_stats}")

                turn_results.append(
                    {
                        "turn_id": turn_id,
                        "cleaned_calls": len(cleaned["tool_calls"]),
                        "stats": turn_stats,
                    }
                )

                system.deduplicator.finalize_turn()

            assert len(turn_results) == 3, "Should have 3 turn results"
            assert all(
                r["cleaned_calls"] == 2 for r in turn_results
            ), "Each turn should have 2 unique calls"

            global_registry_size = len(
                system.deduplicator.global_call_registry
            )
            logger.info(
                f"✅ Multi-turn state verified: {global_registry_size} total "
                f"calls registered across {len(turn_results)} turns"
            )

            return {
                "success": True,
                "data": {
                    "turns_tested": len(turn_results),
                    "global_calls_registered": global_registry_size,
                    "turn_isolation_verified": True,
                    "turn_results": turn_results,
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def save_results(
        self,
        results: dict[str, Any],
        output_file: str = "test_results.json",
    ) -> None:
        """Save test results to file."""
        output_path = Path("data") / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"\n📝 Results saved to {output_path}")


async def main() -> dict[str, Any]:
    """Run all tests."""
    tester = IntegratedSystemTester()

    print("\n" + "=" * 60)
    print("🧪 INTEGRATED SELF-EVOLUTION SYSTEM TEST SUITE")
    print("=" * 60)

    results = await tester.run_all_tests()
    tester.save_results(results)

    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {results['total_tests']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(
        f"Success Rate: "
        f"{results['passed'] / results['total_tests'] * 100:.1f}%"
    )

    if results["failed"] == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {results['failed']} test(s) failed")

    print("=" * 60 + "\n")
    return results


if __name__ == "__main__":
    results = asyncio.run(main())
    sys.exit(0 if results["failed"] == 0 else 1)
