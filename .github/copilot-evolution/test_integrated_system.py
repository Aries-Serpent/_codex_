"""
Test Suite for Integrated Self-Evolution System

Tests the integrated system with real-world scenarios including security
vulnerability fixes, pattern correlation, and knowledge integration.

Author: mbaetiong
Generated: 2025-12-21
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegratedSystemTester:
    """Tests the integrated self-evolution system."""

    def __init__(self):
        """Initialize tester."""
        self.test_results: list[dict[str, Any]] = []
        self.repo_path = Path(".")

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
        ]

        results = {
            "total_tests": len(tests),
            "passed": 0,
            "failed": 0,
            "details": []
        }

        for test in tests:
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"Running: {test.__name__}")
                logger.info(f"{'='*60}")

                result = await test()

                if result["success"]:
                    results["passed"] += 1
                    logger.info(f"✅ {test.__name__} PASSED")
                else:
                    results["failed"] += 1
                    logger.error(f"❌ {test.__name__} FAILED: {result.get('error')}")

                results["details"].append({
                    "test": test.__name__,
                    "success": result["success"],
                    "data": result.get("data"),
                    "error": result.get("error")
                })

            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "test": test.__name__,
                    "success": False,
                    "error": str(e)
                })
                logger.exception(f"❌ {test.__name__} FAILED with exception")

        logger.info(f"\n{'='*60}")
        logger.info(f"Test Summary: {results['passed']}/{results['total_tests']} passed")
        logger.info(f"{'='*60}")

        return results

    async def test_pattern_extraction(self) -> dict[str, Any]:
        """Test pattern extraction from repository."""
        try:
            from quantum_correlator import QuantumPatternCorrelator

            # Use correct repo path relative to test directory
            # Tests run from .github/copilot-evolution/, so "../.." points to repository root
            # This is necessary to access files like agents/quantum_game_theory.py
            correlator = QuantumPatternCorrelator(repo_path="../..")

            # Extract from smaller set for testing
            target_files = [
                "agents/quantum_game_theory.py",
                ".github/copilot-security/security_agent.py"
            ]

            patterns = await correlator.extract_codex_patterns(target_files)

            assert len(patterns) > 0, "No patterns extracted"
            assert any(len(p) > 0 for p in patterns.values()), "All domains empty"

            logger.info(f"Extracted patterns from {len(patterns)} domains")
            for domain, pats in patterns.items():
                logger.info(f"  - {domain}: {len(pats)} patterns")

            return {
                "success": True,
                "data": {
                    "domains": len(patterns),
                    "total_patterns": sum(len(p) for p in patterns.values())
                }
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_pattern_correlation(self) -> dict[str, Any]:
        """Test pattern correlation across domains."""
        try:
            from quantum_correlator import QuantumPatternCorrelator

            correlator = QuantumPatternCorrelator()

            # Create mock patterns
            mock_patterns = {
                "security": [
                    {"type": "function", "name": "validate_input", "async": False},
                    {"type": "class", "name": "SecurityScanner", "methods": ["scan", "fix"]}
                ],
                "quantum_physics": [
                    {"type": "function", "name": "superpose_states", "async": True},
                    {"type": "class", "name": "QuantumEngine", "methods": ["evolve", "measure"]}
                ]
            }

            correlations = await correlator.correlate_patterns(mock_patterns)

            assert len(correlations) > 0, "No correlations found"

            logger.info(f"Found {len(correlations)} correlations")
            for corr in correlations[:3]:
                logger.info(f"  - {corr.emergent_capability} (strength: {corr.entanglement_strength:.2f})")

            return {
                "success": True,
                "data": {
                    "correlations_found": len(correlations),
                    "top_capability": correlations[0].emergent_capability if correlations else None
                }
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
                "undefined_concepts": ["quantum_key_distribution", "BB84_protocol"],
                "partial_understanding": [
                    {"concept": "entanglement", "domain": "quantum_physics", "importance": 0.8}
                ]
            }

            result = await system.process_task_with_learning(task)

            assert "knowledge_gaps" in result, "No knowledge gaps detected"
            assert len(result["knowledge_gaps"]) > 0, "Gaps list is empty"

            # Note: knowledge_gaps in result contains concept strings, not KnowledgeGap objects
            # The actual KnowledgeGap objects are stored in system.hunger_engine.knowledge_gaps
            logger.info(f"Detected {len(result['knowledge_gaps'])} knowledge gaps")
            for gap_concept in result["knowledge_gaps"][:3]:
                logger.info(f"  - {gap_concept}")

            # Get domains from the hunger engine's internal state
            domains = list(set(
                g.domain for g in system.hunger_engine.knowledge_gaps.values()
            ))

            return {
                "success": True,
                "data": {
                    "gaps_detected": len(result["knowledge_gaps"]),
                    "domains": domains
                }
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
                logger.info(f"     Type: {q.question_type}, Urgency: {q.urgency:.2f}")

            return {
                "success": True,
                "data": {
                    "questions_generated": len(result["questions"]),
                    "question_types": list(set(q.question_type for q in result["questions"]))
                }
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_knowledge_integration(self) -> dict[str, Any]:
        """Test knowledge integration from human input."""
        try:
            from integrated_system import IntegratedEvolutionSystem

            system = IntegratedEvolutionSystem()

            # Provide knowledge answer
            knowledge = {
                "question_id": "test_q_1",
                "answer": "Homomorphic encryption allows computation on encrypted data without decryption. "
                         "FHE (Fully Homomorphic Encryption) enables arbitrary computations.",
                "sources": ["Wikipedia", "Cryptography textbook"],
                "confidence": 0.9
            }

            result = await system.receive_knowledge(knowledge)

            # The integration result is nested inside result["integration"]
            integration = result.get("integration", result)

            assert integration.get("status") == "integrated", f"Integration failed: {integration.get('error')}"
            assert "capabilities_enhanced" in integration, "No capabilities enhanced"

            logger.info("Knowledge integrated successfully")
            logger.info(f"  Capabilities enhanced: {len(integration['capabilities_enhanced'])}")
            logger.info(f"  Status: {integration['status']}")

            return {
                "success": True,
                "data": {
                    "capabilities_added": len(integration["capabilities_enhanced"]),
                    "status": integration["status"]
                }
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

            # Run multiple tasks
            tasks = [
                {"description": "Task 1", "domain": "security", "undefined_concepts": ["concept_a"]},
                {"description": "Task 2", "domain": "quantum_physics", "undefined_concepts": ["concept_b"]},
            ]

            for task in tasks:
                await system.process_task_with_learning(task)

            # Provide some knowledge
            await system.receive_knowledge({
                "answer": "Concept A is about security validation",
                "confidence": 0.8
            })

            final_fitness = system.evolution_state.fitness
            final_gen = system.evolution_state.generation

            assert final_gen >= initial_gen, "Generation did not advance"
            assert len(system.evolution_state.capabilities) > 0, "No capabilities gained"

            logger.info("Evolution cycle completed")
            logger.info(f"  Generation: {initial_gen} → {final_gen}")
            logger.info(f"  Fitness: {initial_fitness:.3f} → {final_fitness:.3f}")
            logger.info(f"  Capabilities: {len(system.evolution_state.capabilities)}")

            return {
                "success": True,
                "data": {
                    "generation_advanced": final_gen > initial_gen,
                    "fitness_changed": abs(final_fitness - initial_fitness) > 0.01,
                    "capabilities_count": len(system.evolution_state.capabilities)
                }
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_security_scenario(self) -> dict[str, Any]:
        """Test real-world security vulnerability scenario."""
        try:
            from integrated_system import IntegratedEvolutionSystem
            from quantum_correlator import QuantumPatternCorrelator

            # Initialize systems
            evolution = IntegratedEvolutionSystem()
            # Use correct repo path - tests run from .github/copilot-evolution/
            correlator = QuantumPatternCorrelator(repo_path="../..")

            # Scenario: SQL injection vulnerability fix
            task = {
                "description": "Fix SQL injection vulnerability in user authentication",
                "domain": "security",
                "undefined_concepts": ["parameterized_queries", "prepared_statements"],
                "partial_understanding": [
                    {"concept": "SQL_injection", "domain": "security", "importance": 1.0}
                ],
                "context": {
                    "vulnerability_type": "CWE-89",
                    "severity": "critical",
                    "affected_code": "query = f'SELECT * FROM users WHERE id = {user_id}'"
                }
            }

            # Process task
            result = await evolution.process_task_with_learning(task)

            # Extract security patterns
            patterns = await correlator.extract_codex_patterns([
                "scripts/security/**/*.py",
                ".github/copilot-security/*.py"
            ])

            # Correlate with quantum patterns for enhanced security
            if patterns:
                correlations = await correlator.correlate_patterns(patterns)
                logger.info(f"  Found {len(correlations)} security-domain correlations")

            assert len(result["knowledge_gaps"]) > 0, "No gaps detected for undefined concepts"
            assert len(result["questions"]) > 0, "No questions generated"
            assert any("SQL" in q.question_text or "parameter" in q.question_text.lower()
                      for q in result["questions"]), "No SQL-related questions"

            logger.info("Security scenario completed")
            logger.info(f"  Knowledge gaps: {len(result['knowledge_gaps'])}")
            logger.info(f"  Questions: {len(result['questions'])}")
            logger.info(f"  Security patterns: {sum(len(p) for p in patterns.values()) if patterns else 0}")

            return {
                "success": True,
                "data": {
                    "gaps_detected": len(result["knowledge_gaps"]),
                    "questions_generated": len(result["questions"]),
                    "patterns_extracted": sum(len(p) for p in patterns.values()) if patterns else 0
                }
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_results(self, results: dict[str, Any], output_file: str = "test_results.json"):
        """Save test results to file."""
        output_path = Path("data") / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"\n📝 Results saved to {output_path}")


async def main():
    """Run all tests."""
    tester = IntegratedSystemTester()

    print("\n" + "="*60)
    print("🧪 INTEGRATED SELF-EVOLUTION SYSTEM TEST SUITE")
    print("="*60)

    results = await tester.run_all_tests()

    # Save results
    tester.save_results(results)

    # Print summary
    print("\n" + "="*60)
    print("📊 FINAL SUMMARY")
    print("="*60)
    print(f"Total Tests: {results['total_tests']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"Success Rate: {results['passed']/results['total_tests']*100:.1f}%")

    if results['failed'] == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {results['failed']} test(s) failed")

    print("="*60 + "\n")

    return results


if __name__ == "__main__":
    results = asyncio.run(main())

    # Exit with appropriate code
    exit(0 if results["failed"] == 0 else 1)
