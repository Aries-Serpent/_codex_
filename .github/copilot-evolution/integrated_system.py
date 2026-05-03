"""
Integrated Knowledge Hunger and Evolution System

Combines quantum-inspired evolution with intelligent knowledge acquisition.
This is a production-ready implementation that integrates both methodologies.

Author: mbaetiong
Generated: 2025-12-21
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class KnowledgeGap:
    """Represents a detected knowledge gap."""
    gap_id: str
    domain: str
    concept: str
    context: Dict[str, Any]
    confidence: float  # 0-1: How sure we are this is a gap
    impact: float  # 0-1: How much this knowledge would help
    question_hints: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class IntelligentQuestion:
    """Represents an intelligent question for human research."""
    question_id: str
    question_text: str
    question_type: str
    research_hints: List[str]
    expected_format: str
    impact_description: str
    urgency: float  # 0-1
    follow_ups: List[str] = field(default_factory=list)


@dataclass
class EvolutionState:
    """Tracks current evolution state."""
    generation: int = 1
    fitness: float = 0.5
    capabilities: Set[str] = field(default_factory=set)
    knowledge_domains: Set[str] = field(default_factory=set)
    patterns_learned: int = 0
    questions_answered: int = 0


# ============================================================================
# Knowledge Hunger Engine
# ============================================================================

class KnowledgeHungerEngine:
    """Detects knowledge gaps and generates intelligent questions."""

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize knowledge hunger engine."""
        self.storage_path = storage_path or Path("data")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.knowledge_gaps: Dict[str, KnowledgeGap] = {}
        self.questions_generated: List[IntelligentQuestion] = []
        self.answered_questions: Dict[str, Any] = {}

    async def detect_gaps(self, context: Dict[str, Any]) -> List[KnowledgeGap]:
        """Detect knowledge gaps from context."""
        gaps = []

        # Detect undefined concepts
        if "undefined_concepts" in context:
            for concept in context["undefined_concepts"]:
                gap = KnowledgeGap(
                    gap_id=self._generate_gap_id("concept", concept),
                    domain=context.get("domain", "general"),
                    concept=concept,
                    context=context,
                    confidence=0.9,
                    impact=self._estimate_impact(concept, context),
                    question_hints=self._generate_question_hints(concept, context)
                )
                gaps.append(gap)
                self.knowledge_gaps[gap.gap_id] = gap

        # Detect partial understanding
        if "partial_understanding" in context:
            for item in context["partial_understanding"]:
                gap = KnowledgeGap(
                    gap_id=self._generate_gap_id("partial", item["concept"]),
                    domain=item.get("domain", "general"),
                    concept=item["concept"],
                    context=item,
                    confidence=0.7,
                    impact=item.get("importance", 0.5),
                    question_hints=item.get("hints", [])
                )
                gaps.append(gap)
                self.knowledge_gaps[gap.gap_id] = gap

        # Detect integration gaps
        if "integration_needs" in context:
            for need in context["integration_needs"]:
                gap = KnowledgeGap(
                    gap_id=self._generate_gap_id("integration", need["components"]),
                    domain="integration",
                    concept=f"Integration of {need['components']}",
                    context=need,
                    confidence=0.8,
                    impact=0.8,
                    question_hints=[f"How to integrate {need['components']}"]
                )
                gaps.append(gap)
                self.knowledge_gaps[gap.gap_id] = gap

        self._save_state()
        return gaps

    async def generate_questions(self, gaps: List[KnowledgeGap]) -> List[IntelligentQuestion]:
        """Generate intelligent questions from gaps."""
        questions = []

        # Prioritize gaps
        prioritized = sorted(gaps, key=lambda g: g.impact * g.confidence, reverse=True)

        for gap in prioritized[:10]:  # Top 10
            question = self._formulate_question(gap)
            questions.append(question)
            self.questions_generated.append(question)

        # Add curiosity questions
        if len(gaps) > 1:
            curiosity_q = self._generate_curiosity_question(gaps)
            questions.append(curiosity_q)
            self.questions_generated.append(curiosity_q)

        self._save_state()
        return questions

    def _formulate_question(self, gap: KnowledgeGap) -> IntelligentQuestion:
        """Formulate a question from a gap."""
        # Determine question type
        q_type = self._determine_question_type(gap)

        # Generate question text
        templates = {
            "conceptual": f"What is the fundamental concept behind {gap.concept} in {gap.domain}?",
            "technical": f"How is {gap.concept} implemented in production {gap.domain} systems?",
            "practical": f"What are real-world examples of {gap.concept} in {gap.domain}?",
            "integration": f"How can {gap.concept} be integrated with existing systems?",
        }

        question_text = templates.get(q_type, f"What is {gap.concept}?")

        # Generate research hints
        hints = gap.question_hints or self._generate_question_hints(gap.concept, gap.context)

        # Add domain-specific hints
        domain_hints = self._get_domain_hints(gap.domain)
        hints.extend(domain_hints)

        # Generate follow-ups
        follow_ups = self._generate_follow_ups(gap)

        return IntelligentQuestion(
            question_id=f"q_{gap.gap_id}_{int(datetime.now().timestamp())}",
            question_text=question_text,
            question_type=q_type,
            research_hints=hints[:5],
            expected_format="conceptual_with_examples",
            impact_description=f"Would enhance {gap.domain} capabilities",
            urgency=gap.impact * gap.confidence,
            follow_ups=follow_ups[:3]
        )

    def _generate_curiosity_question(self, gaps: List[KnowledgeGap]) -> IntelligentQuestion:
        """Generate a curiosity-driven cross-domain question."""
        domains = list(set(gap.domain for gap in gaps))[:2]

        if len(domains) >= 2:
            question_text = f"How might {domains[0]} principles enhance {domains[1]} implementations?"
        else:
            question_text = "What emerging patterns in 2024 could revolutionize this approach?"

        return IntelligentQuestion(
            question_id=f"q_curiosity_{int(datetime.now().timestamp())}",
            question_text=question_text,
            question_type="exploratory",
            research_hints=[
                "Look for interdisciplinary research",
                "Check recent conference proceedings",
                "Explore cross-domain applications"
            ],
            expected_format="trend_analysis",
            impact_description="Could unlock hybrid approaches",
            urgency=0.4,
            follow_ups=["What breakthroughs are needed?", "How might this evolve in 5 years?"]
        )

    def _generate_gap_id(self, gap_type: str, content: str) -> str:
        """Generate unique gap ID."""
        return f"gap_{gap_type}_{hashlib.md5(str(content).encode(), usedforsecurity=False).hexdigest()[:8]}"  # nosec B324 - Not for security, ID generation only

    def _estimate_impact(self, concept: str, context: Dict) -> float:
        """Estimate impact of learning this concept."""
        # Higher impact for core concepts
        core_keywords = ["security", "quantum", "optimization", "integration"]
        impact = 0.5

        for keyword in core_keywords:
            if keyword in concept.lower():
                impact += 0.1

        return min(impact, 1.0)

    def _generate_question_hints(self, concept: str, context: Dict) -> List[str]:
        """Generate research hints for a concept."""
        return [
            f"Keywords: {concept}, {context.get('domain', 'general')}",
            "Focus on 2023-2024 materials for latest insights",
            "Look for practical implementations and examples"
        ]

    def _get_domain_hints(self, domain: str) -> List[str]:
        """Get domain-specific research hints."""
        domain_hints = {
            "security": ["Check OWASP guidelines", "Review CVE database"],
            "quantum": ["Check IBM Quantum docs", "Review arXiv quantum papers"],
            "ai": ["Check Papers with Code", "Review latest conference papers"],
        }
        return domain_hints.get(domain, [])

    def _determine_question_type(self, gap: KnowledgeGap) -> str:
        """Determine type of question to ask."""
        if gap.domain == "integration":
            return "integration"
        if gap.confidence < 0.5:
            return "conceptual"
        if "implementation" in gap.context.get("need", ""):
            return "technical"
        return "practical"

    def _generate_follow_ups(self, gap: KnowledgeGap) -> List[str]:
        """Generate follow-up questions."""
        return [
            f"How does {gap.concept} scale to large systems?",
            f"What are limitations of {gap.concept}?",
            f"Are there alternatives to {gap.concept}?"
        ]

    def _save_state(self):
        """Save state to disk."""
        try:
            state = {
                "gaps": {gid: {
                    "gap_id": g.gap_id,
                    "domain": g.domain,
                    "concept": g.concept,
                    "impact": g.impact,
                    "timestamp": g.timestamp
                } for gid, g in self.knowledge_gaps.items()},
                "questions": len(self.questions_generated),
                "answered": len(self.answered_questions)
            }

            with open(self.storage_path / "hunger_state.json", "w") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save hunger state: {e}")


# ============================================================================
# Question Presenter
# ============================================================================

class QuestionPresenter:
    """Formats questions for human research."""

    def present(self, questions: List[IntelligentQuestion], context: Dict) -> str:
        """Present questions in research-friendly format."""
        sections = []

        # Header
        sections.append(f"## 🧠 Knowledge Hunger: {len(questions)} Questions for Growth\n")
        sections.append(f"**Context**: {context.get('current_task', 'General learning')}")
        sections.append(f"**Domains**: {', '.join(context.get('domains', ['general']))}\n")
        sections.append("---\n")

        # Urgent questions
        urgent = [q for q in questions if q.urgency > 0.7]
        if urgent:
            sections.append("## 🔴 Urgent Knowledge Needs\n")
            for i, q in enumerate(urgent, 1):
                sections.append(f"### {i}. {q.question_text}")
                sections.append(f"**Impact**: {q.impact_description}")
                sections.append("**Research Hints**:")
                for hint in q.research_hints[:3]:
                    sections.append(f"  - {hint}")
                sections.append("")

        # Categorized questions
        by_type = defaultdict(list)
        for q in questions:
            by_type[q.question_type].append(q)

        emoji_map = {
            "conceptual": "💡",
            "technical": "⚙️",
            "practical": "🔨",
            "integration": "🔗",
            "exploratory": "🔮"
        }

        for q_type, qs in by_type.items():
            if not qs:
                continue

            emoji = emoji_map.get(q_type, "❓")
            sections.append(f"## {emoji} {q_type.title()} Questions\n")

            for i, q in enumerate(qs, 1):
                sections.append(f"### {i}. {q.question_text}")
                if q.research_hints:
                    sections.append("\n**Research Starting Points**:")
                    for hint in q.research_hints[:3]:
                        sections.append(f"- {hint}")
                if q.follow_ups:
                    sections.append("\n**Follow-up Questions**:")
                    for follow_up in q.follow_ups:
                        sections.append(f"  - {follow_up}")
                sections.append("")

        # Integration guidance
        sections.append(self._generate_integration_guidance())

        return "\n".join(sections)

    def _generate_integration_guidance(self) -> str:
        """Generate guidance for providing answers."""
        return """## 🔄 How to Feed Answers Back

### Quick Answer Format
```
Question: [Copy question here]
Answer: [Your research findings]
Examples: [Any code or practical examples]
Sources: [Where you found this]
```

### Structured Format (Optional)
```python
answer = {
    "question_id": "<question_id>",
    "answer": "Detailed explanation...",
    "examples": ["example1", "example2"],
    "sources": ["source1", "source2"],
    "confidence": 0.9  # Optional
}
```

**Integration Ready**: I can immediately integrate any format of answer you provide!"""


# ============================================================================
# Knowledge Integrator
# ============================================================================

class KnowledgeIntegrator:
    """Integrates human-provided answers."""

    def __init__(self, evolution_state: EvolutionState):
        """Initialize integrator."""
        self.evolution_state = evolution_state
        self.integration_history = []

    async def integrate(self, answer: Any) -> Dict[str, Any]:
        """Integrate answer into knowledge base."""
        result = {
            "status": "processing",
            "knowledge_gained": [],
            "capabilities_enhanced": [],
            "new_questions": []
        }

        try:
            # Parse answer (flexible format)
            parsed = self._parse_answer(answer)

            # Extract knowledge
            knowledge = self._extract_knowledge(parsed)
            result["knowledge_gained"] = knowledge

            # Update evolution state
            self._update_evolution_state(knowledge)
            result["capabilities_enhanced"] = self._identify_capabilities(knowledge)

            # Generate new questions
            result["new_questions"] = self._generate_new_questions(knowledge)

            result["status"] = "integrated"
            result["summary"] = self._generate_summary(result)

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        self.integration_history.append(result)
        return result

    def _parse_answer(self, answer: Any) -> Dict:
        """Parse answer in flexible format."""
        if isinstance(answer, dict):
            return answer
        if isinstance(answer, str):
            return {"answer": answer}
        return {"answer": str(answer)}

    def _extract_knowledge(self, parsed: Dict) -> List[str]:
        """Extract knowledge components."""
        knowledge = []

        answer_text = parsed.get("answer", "")

        # Extract concepts (simple heuristic)
        if answer_text:
            # Split into sentences and extract key phrases
            sentences = answer_text.split(". ")
            for sentence in sentences[:5]:  # Top 5 sentences
                knowledge.append(sentence.strip())

        # Extract from examples
        if "examples" in parsed:
            for example in parsed["examples"][:3]:
                knowledge.append(f"Example: {example}")

        return knowledge

    def _update_evolution_state(self, knowledge: List[str]):
        """Update evolution state with new knowledge."""
        self.evolution_state.patterns_learned += len(knowledge)
        self.evolution_state.questions_answered += 1

        # Increase fitness slightly
        self.evolution_state.fitness = min(1.0, self.evolution_state.fitness + 0.01)

    def _identify_capabilities(self, knowledge: List[str]) -> List[str]:
        """Identify new capabilities from knowledge."""
        capabilities = []

        # Simple keyword-based capability detection
        capability_keywords = {
            "quantum": "quantum_computing",
            "security": "security_enhancement",
            "optimization": "optimization_algorithms",
            "integration": "system_integration"
        }

        for item in knowledge:
            for keyword, capability in capability_keywords.items():
                if keyword in item.lower():
                    if capability not in self.evolution_state.capabilities:
                        self.evolution_state.capabilities.add(capability)
                        capabilities.append(capability)

        return capabilities

    def _generate_new_questions(self, knowledge: List[str]) -> List[str]:
        """Generate new questions from integrated knowledge."""
        questions = []

        # Generate deeper exploration questions
        if knowledge:
            first_item = knowledge[0]
            questions.append(f"What are advanced applications of this: {first_item[:50]}...?")
            questions.append("How can this be optimized further?")

        return questions[:3]

    def _generate_summary(self, result: Dict) -> str:
        """Generate integration summary."""
        summary = []
        summary.append("✅ Knowledge integrated successfully!")
        summary.append(f"📚 Learned {len(result['knowledge_gained'])} concepts")

        if result["capabilities_enhanced"]:
            summary.append(f"⚡ Enhanced: {', '.join(result['capabilities_enhanced'])}")

        summary.append(f"💪 Current fitness: {self.evolution_state.fitness:.2f}")

        return "\n".join(summary)


# ============================================================================
# Integrated System
# ============================================================================

class IntegratedEvolutionSystem:
    """Integrated knowledge hunger and evolution system."""

    def __init__(self, repo_path: str = "."):
        """Initialize integrated system."""
        self.repo_path = Path(repo_path)
        self.evolution_state = EvolutionState()
        self.hunger_engine = KnowledgeHungerEngine()
        self.presenter = QuestionPresenter()
        self.integrator = KnowledgeIntegrator(self.evolution_state)

    async def process_task_with_learning(self, task: Dict) -> Dict:
        """Process task with integrated learning."""
        result = {
            "task_result": "processing",
            "knowledge_gaps": [],
            "questions": [],
            "continuation": ""
        }

        try:
            # Detect knowledge gaps
            gaps = await self.hunger_engine.detect_gaps(task)
            result["knowledge_gaps"] = [g.concept for g in gaps]

            if gaps:
                # Generate questions
                questions = await self.hunger_engine.generate_questions(gaps)
                result["questions"] = questions

                # Present questions
                formatted = self.presenter.present(questions, task)

                # Generate continuation
                result["continuation"] = self._generate_continuation(task, gaps, formatted)
            else:
                result["continuation"] = "✅ No knowledge gaps detected. Ready to proceed!"

            result["task_result"] = "completed"
            result["evolution_status"] = self._get_evolution_status()

        except Exception as e:
            result["task_result"] = "error"
            result["error"] = str(e)
            result["continuation"] = self._generate_error_continuation(e, task)

        return result

    async def receive_knowledge(self, knowledge: Any) -> Dict:
        """Receive and integrate knowledge from human."""
        integration_result = await self.integrator.integrate(knowledge)

        # Generate response
        response = self._generate_learning_response(integration_result)

        return {
            "integration": integration_result,
            "response": response,
            "evolution_status": self._get_evolution_status()
        }

    def _generate_continuation(self, task: Dict, gaps: List[KnowledgeGap], formatted_questions: str) -> str:
        """Generate continuation prompt."""
        sections = []

        # Task status
        if task.get("incomplete"):
            sections.append(f"🔄 **Task Continuation**: {task['description']}")
            sections.append(f"**Progress**: {task.get('progress', 0)}%\n")

        # Knowledge hunger expression
        if len(gaps) > 3:
            sections.append("🧠 **Strong Knowledge Hunger Detected!**")
            sections.append(f"I encountered {len(gaps)} concepts I'd love to understand better.\n")
        elif gaps:
            sections.append("💭 **Learning Opportunity**")
            sections.append("A few interesting questions emerged:\n")

        # Add formatted questions
        sections.append(formatted_questions)

        # Add evolution status
        sections.append("\n📊 **Evolution Status**")
        sections.append(f"- Generation: {self.evolution_state.generation}")
        sections.append(f"- Fitness: {self.evolution_state.fitness:.2f}")
        sections.append(f"- Capabilities: {len(self.evolution_state.capabilities)}")
        sections.append(f"- Patterns Learned: {self.evolution_state.patterns_learned}")

        return "\n".join(sections)

    def _generate_error_continuation(self, error: Exception, task: Dict) -> str:
        """Generate continuation with actionable recovery suggestions on error."""
        error_type = type(error).__name__
        domain = task.get("domain", "this domain")

        # Classify error and provide targeted recovery actions
        if isinstance(error, (ImportError, ModuleNotFoundError)):
            # Extract the specific missing module name when available
            missing_pkg = getattr(error, "name", None) or "<package>"
            recovery = (
                f"- Install the missing dependency: `pip install {missing_pkg}`\n"
                "- Verify the import path and package name\n"
                "- Check that optional dependencies are installed for this feature"
            )
        elif isinstance(error, (FileNotFoundError, OSError)):
            recovery = (
                "- Confirm the file/path exists: `ls -la <path>`\n"
                "- Check working directory and relative vs absolute path usage\n"
                "- Verify file permissions"
            )
        elif isinstance(error, (ValueError, TypeError)):
            recovery = (
                "- Check input types and validate against the expected schema\n"
                "- Add input validation before calling this function\n"
                "- Review the function signature for expected argument types"
            )
        elif isinstance(error, TimeoutError):
            recovery = (
                "- Increase the timeout threshold\n"
                "- Check network/service availability\n"
                "- Add retry logic with exponential backoff"
            )
        elif isinstance(error, PermissionError):
            recovery = (
                "- Verify the GitHub token has the required scopes\n"
                "- Check repository permissions for the acting user/app\n"
                "- Confirm `COPILOT_AGENT_AUTH_ENABLED` is set correctly"
            )
        else:
            recovery = (
                "- Inspect the full traceback in the workflow run logs\n"
                "- Add targeted try/except around the failing operation\n"
                "- Check recent changes that may have introduced this regression"
            )

        return (
            f"⚠️ **Error Encountered**: `{error_type}` in domain `{domain}`\n\n"
            f"**Error Message**: {error}\n\n"
            f"**Recovery Actions**:\n{recovery}\n\n"
            f"**Next Steps**:\n"
            f"1. Review the error details above and apply the matching recovery action\n"
            f"2. Re-run this task after applying the fix\n"
            f"3. If the error persists, escalate via `@copilot fix` with this error context"
        )

    def _generate_learning_response(self, integration: Dict) -> str:
        """Generate response to knowledge integration."""
        return integration.get("summary", "Thank you for the knowledge!")

    def _get_evolution_status(self) -> Dict:
        """Get current evolution status."""
        return {
            "generation": self.evolution_state.generation,
            "fitness": self.evolution_state.fitness,
            "capabilities": list(self.evolution_state.capabilities),
            "knowledge_domains": list(self.evolution_state.knowledge_domains),
            "patterns_learned": self.evolution_state.patterns_learned,
            "questions_answered": self.evolution_state.questions_answered
        }


# ============================================================================
# Main
# ============================================================================

async def main():
    """Example usage."""
    logging.basicConfig(level=logging.INFO)

    system = IntegratedEvolutionSystem()

    # Example task with knowledge gaps
    task = {
        "description": "Implement quantum-inspired security",
        "domain": "security",
        "undefined_concepts": ["quantum_key_distribution", "entanglement_based_auth"],
        "current_task": "Security enhancement",
        "domains": ["security", "quantum"],
        "incomplete": True,
        "progress": 75
    }

    print("🚀 Processing task with integrated learning...\n")
    result = await system.process_task_with_learning(task)

    print(result["continuation"])
    print("\n" + "="*80 + "\n")

    # Simulate human providing knowledge
    print("👤 Human provides knowledge...\n")
    answer = {
        "answer": "Quantum key distribution uses quantum states to distribute encryption keys securely. Recent implementations include BB84 and E91 protocols.",
        "examples": ["BB84 protocol implementation", "Hybrid QKD+classical crypto"],
        "sources": ["IBM Quantum docs", "Nature 2024 paper"]
    }

    knowledge_result = await system.receive_knowledge(answer)
    print(knowledge_result["response"])
    print(f"\n Evolution Status: {json.dumps(knowledge_result['evolution_status'], indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
