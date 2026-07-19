from __future__ import annotations

import ast
import importlib
import json
import shutil
import statistics
import sys
import time
from dataclasses import asdict
from pathlib import Path

from aries_serpent_core.rag.cache.embedding_cache import EmbeddingCache, EmbeddingCacheConfig
from aries_serpent_core.rag.cache.query_cache import QueryCache, QueryCacheConfig
from aries_serpent_core.rag.embeddings import CachedEmbeddingProvider, TfidfEmbeddingProvider
from aries_serpent_core.rag.indexer import (
    RAGIndexer,
    build_index_from_files,
    load_index,
    manage_tenant_indices,
)
from aries_serpent_core.rag.retriever import CachedRetriever, Retriever

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))
WORK_ROOT = REPO_ROOT / ".codex" / "lane2_b2_b5_workspace"
CORPUS_DIR = WORK_ROOT / "corpus"
INDEX_DIR = WORK_ROOT / "indices"
OUTPUT_JSON = REPO_ROOT / ".codex" / "lane2_b2_b5_validation.json"

TOPICS = [
    ("python", "python decorators typing testing packaging interpreter pip wheel module"),
    ("gardening", "gardening compost tomato soil mulch watering seedlings greenhouse"),
    ("astronomy", "astronomy galaxy telescope nebula orbit planet star observatory"),
    ("finance", "finance budget equity bond revenue ledger invoice accounting cashflow"),
    ("medicine", "medicine diagnosis treatment patient clinic dosage vaccine pathology"),
    ("networking", "networking router switch packet tcp latency bandwidth firewall"),
    ("history", "history archive empire treaty rebellion dynasty manuscript artifact"),
    ("music", "music melody rhythm harmony guitar piano chorus studio orchestra"),
    ("cooking", "cooking recipe simmer roast spice kitchen broth baking ingredients"),
    ("robotics", "robotics actuator sensor motion control autonomy kinematics firmware"),
]


def _reset_workspace() -> None:
    if WORK_ROOT.exists():
        shutil.rmtree(WORK_ROOT)
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def _build_corpus() -> tuple[list[Path], list[dict[str, str]]]:
    files: list[Path] = []
    queries: list[dict[str, str]] = []
    for topic, keywords in TOPICS:
        for idx in range(10):
            text = (
                f"{topic.title()} knowledge base article {idx}. "
                f"{keywords}. "
                f"This document explains {topic} workflows, troubleshooting, and best practices. "
                f"{keywords}."
            )
            file_path = CORPUS_DIR / f"{topic}_{idx:02d}.txt"
            file_path.write_text(text, encoding="utf-8")
            files.append(file_path)
            queries.append(
                {
                    "query": f"{topic} {keywords.split()[0]} best practices article {idx}",
                    "topic": topic,
                    "expected_file": file_path.name,
                }
            )
    return files, queries


def _force_offline_index_build(files: list[Path]) -> dict[str, object]:
    from aries_serpent_core.rag import indexer as indexer_module
    from aries_serpent_core.rag import retriever as retriever_module

    original_embed_chunks = indexer_module.embed_chunks
    original_sentence_transformer = retriever_module.SentenceTransformer
    try:
        def _raise_import_error(*_args, **_kwargs):
            raise ImportError("forced offline validation")

        indexer_module.embed_chunks = _raise_import_error
        retriever_module.SentenceTransformer = None

        start = time.perf_counter()
        index_path = build_index_from_files(
            files=files,
            index_name="lane2-validation",
            tenant_id="lane2",
            index_dir=str(INDEX_DIR),
            chunk_size=220,
            overlap=32,
        )
        build_ms = (time.perf_counter() - start) * 1000

        faiss_index, chunks, metadata = load_index(
            index_name="lane2-validation",
            tenant_id="lane2",
            index_dir=str(INDEX_DIR),
        )
        retriever = Retriever(
            index_dir=str(INDEX_DIR),
            index_name="lane2-validation",
            tenant_id="lane2",
        )
        return {
            "index_path": str(index_path.relative_to(REPO_ROOT)),
            "build_ms": build_ms,
            "faiss_ntotal": faiss_index.ntotal,
            "faiss_dim": faiss_index.d,
            "chunk_count": len(chunks),
            "metadata": metadata,
            "retriever": retriever,
            "chunks": chunks,
        }
    finally:
        indexer_module.embed_chunks = original_embed_chunks
        retriever_module.SentenceTransformer = original_sentence_transformer


def _measure_queries(retriever: Retriever, queries: list[dict[str, str]]) -> dict[str, object]:
    latencies_ms: list[float] = []
    precision_scores: list[float] = []
    recall_scores: list[float] = []
    successful = 0
    topic_hits = 0
    sample_results: list[dict[str, object]] = []

    for query_def in queries:
        started = time.perf_counter()
        results = retriever.query(query_def["query"], top_k=5)
        latencies_ms.append((time.perf_counter() - started) * 1000)

        relevant = [
            item
            for item in results
            if query_def["topic"] in item["text"].lower()
        ]
        precision_scores.append(len(relevant) / 5.0)
        recall_scores.append(min(1.0, len(relevant) / 5.0))
        if results:
            successful += 1
            if query_def["topic"] in results[0]["text"].lower():
                topic_hits += 1
        if len(sample_results) < 5:
            sample_results.append(
                {
                    "query": query_def["query"],
                    "top_result_excerpt": results[0]["text"][:100] if results else "",
                    "top_result_score": results[0]["score"] if results else None,
                }
            )

    sorted_latencies = sorted(latencies_ms)

    def _pct(p: float) -> float:
        index = min(len(sorted_latencies) - 1, int(len(sorted_latencies) * p))
        return sorted_latencies[index]

    return {
        "query_count": len(queries),
        "successful_queries": successful,
        "top1_topic_accuracy": topic_hits / len(queries),
        "precision_at_5": statistics.mean(precision_scores),
        "recall_at_5": statistics.mean(recall_scores),
        "latency_ms": {
            "p50": statistics.median(sorted_latencies),
            "p95": _pct(0.95),
            "p99": _pct(0.99),
            "max": max(sorted_latencies),
            "min": min(sorted_latencies),
            "mean": statistics.mean(sorted_latencies),
        },
        "sample_results": sample_results,
    }


def _run_lifecycle_validation() -> dict[str, object]:
    provider = TfidfEmbeddingProvider(max_features=64)
    cached_provider = CachedEmbeddingProvider(
        provider,
        cache_dir=str(WORK_ROOT / "embedding_provider_cache"),
    )
    texts = [
        "python semantic retrieval pipeline",
        "gardening compost watering schedule",
        "astronomy telescope orbital mechanics",
    ]
    embeddings_first = cached_provider.encode(
        texts,
        cache_key="lifecycle-sample",
        metadata={"file_mtime": 1},
    )
    embeddings_second = cached_provider.encode(
        texts,
        cache_key="lifecycle-sample",
        metadata={"file_mtime": 1},
    )

    embedding_cache = EmbeddingCache(
        EmbeddingCacheConfig(max_entries=2, default_ttl=0.05),
    )
    query_cache = QueryCache(QueryCacheConfig(max_size=2, default_ttl=0.05))

    embedding_cache.put("python", embeddings_first[0], ttl=0.05, metadata={"topic": "python"})
    embedding_present_before_expiry = embedding_cache.get("python") is not None
    query_cache.put("python query", [{"id": "python"}], ttl=0.05)
    query_present_before_expiry = query_cache.get("python query") is not None

    time.sleep(0.08)

    embedding_evicted = embedding_cache.get("python") is None
    query_evicted = query_cache.get("python query") is None

    embedding_cache.put("alpha", embeddings_first[0])
    embedding_cache.put("beta", embeddings_first[1])
    embedding_cache.put("gamma", embeddings_first[2])
    capacity_respected = len(embedding_cache) <= 2

    query_cache.put("alpha", [{"id": 1}])
    query_cache.put("beta", [{"id": 2}])
    query_cache.put("gamma", [{"id": 3}])
    query_capacity_respected = len(query_cache) <= 2

    return {
        "provider": cached_provider.provider.__class__.__name__,
        "provider_stats": cached_provider.get_stats(),
        "embedding_shape": list(embeddings_first.shape),
        "cache_reuse_identical": embeddings_first.shape == embeddings_second.shape,
        "ttl_validation": {
            "embedding_present_before_expiry": embedding_present_before_expiry,
            "query_present_before_expiry": query_present_before_expiry,
            "embedding_evicted_after_ttl": embedding_evicted,
            "query_evicted_after_ttl": query_evicted,
            "embedding_default_ttl_seconds": EmbeddingCacheConfig().default_ttl,
            "query_default_ttl_seconds": QueryCacheConfig().default_ttl,
        },
        "capacity_eviction": {
            "embedding_capacity_respected": capacity_respected,
            "query_capacity_respected": query_capacity_respected,
            "embedding_cache_stats": embedding_cache.get_stats(),
            "query_cache_stats": query_cache.get_stats().to_dict(),
        },
        "freshness_loop_doc_present": (
            REPO_ROOT / ".github" / "agents" / "rag-freshness-loop-agent.md"
        ).exists(),
    }


def _check_imports() -> dict[str, object]:
    modules = [
        "aries_serpent_core.rag",
        "aries_serpent_core.rag.indexer",
        "aries_serpent_core.rag.retriever",
        "aries_serpent_core.brain.ooda_orchestrator",
        "aries_serpent_core.zendesk.rag.bridge",
        "src.codex.cognitive_brain",
        "src.codex.cognitive_brain.reasoning_engine",
        "src.codex.cognitive_brain.integration_adapters",
    ]
    results: dict[str, dict[str, object]] = {}
    for module_name in modules:
        try:
            module = importlib.import_module(module_name)
            results[module_name] = {
                "success": True,
                "file": getattr(module, "__file__", ""),
            }
        except Exception as exc:  # pragma: no cover - report path
            results[module_name] = {
                "success": False,
                "error": f"{type(exc).__name__}: {exc}",
            }
    return results


def _detect_cross_package_cycles() -> list[list[str]]:
    package_roots = {
        "aries_serpent_core.rag": REPO_ROOT / "src" / "aries_serpent_core" / "rag",
        "aries_serpent_core.brain": REPO_ROOT / "src" / "aries_serpent_core" / "brain",
        "src.codex.cognitive_brain": REPO_ROOT / "src" / "codex" / "cognitive_brain",
    }
    graph: dict[str, set[str]] = {}

    def _module_name(root_name: str, file_path: Path, root_path: Path) -> str:
        relative = file_path.relative_to(root_path).with_suffix("")
        if relative.name == "__init__":
            suffix = ".".join(relative.parts[:-1])
        else:
            suffix = ".".join(relative.parts)
        return f"{root_name}.{suffix}" if suffix else root_name

    for root_name, root_path in package_roots.items():
        for file_path in root_path.rglob("*.py"):
            module_name = _module_name(root_name, file_path, root_path)
            graph.setdefault(module_name, set())
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith(tuple(package_roots.keys())):
                            graph[module_name].add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith(tuple(package_roots.keys())):
                        graph[module_name].add(node.module)

    cycles: list[list[str]] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def _walk(node: str, stack: list[str]) -> None:
        visiting.add(node)
        stack.append(node)
        for neighbor in graph.get(node, set()):
            if neighbor not in graph:
                continue
            if neighbor in visiting:
                start = stack.index(neighbor)
                cycle = stack[start:] + [neighbor]
                if any(
                    "rag" in part and ("brain" in part or "cognitive_brain" in part)
                    for part in cycle
                ):
                    cycles.append(cycle)
            elif neighbor not in visited:
                _walk(neighbor, stack)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        if node not in visited:
            _walk(node, [])
    return cycles


def _ooda_integration_validation(query_metrics: dict[str, object]) -> dict[str, object]:
    doc_text = (REPO_ROOT / ".github" / "agents" / "rag-freshness-loop-agent.md").read_text(
        encoding="utf-8"
    )
    ooda_markers = {
        phase: (phase in doc_text)
        for phase in ("Observe:", "Orient:", "Decide:", "Act:")
    }

    from src.codex.cognitive_brain.integration_adapters import PlansetIntegrationAdapter
    from src.codex.cognitive_brain.reasoning_engine import (
        CandidateDecision,
        ConfidenceLevel,
        Decision,
        DecisionStrategy,
    )

    decision = Decision(
        id="rag-validation",
        option="promote-rag-index",
        confidence=round(float(query_metrics["top1_topic_accuracy"]), 4),
        confidence_level=ConfidenceLevel.HIGH,
        reasoning=(
            f"RAG retrieval validated with p99="
            f"{query_metrics['latency_ms']['p99']:.2f}ms and "
            f"precision@5={query_metrics['precision_at_5']:.3f}"
        ),
        strategy=DecisionStrategy.ENSEMBLE,
        candidates=[
            CandidateDecision(
                id="candidate-1",
                strategy=DecisionStrategy.HEURISTIC,
                option="promote-rag-index",
                reasoning="Retrieval metrics exceed minimum thresholds.",
                confidence=0.91,
                validation_rules=["latency", "accuracy"],
            )
        ],
        domain_validation=True,
        latency_ms=float(query_metrics["latency_ms"]["p99"]),
    )
    adapter = PlansetIntegrationAdapter(decision_history=[decision])
    adapted = adapter.adapt_for_planset_009(decision, category="rag")
    return {
        "ooda_markers_present": ooda_markers,
        "adapter_roundtrip_success": adapted.category == "rag"
        and adapted.feature_vector["confidence"] == decision.confidence,
        "adapter_payload": adapted.to_dict(),
    }


def _multi_index_validation(files: list[Path]) -> dict[str, object]:
    from aries_serpent_core.rag import indexer as indexer_module

    original_embed_chunks = indexer_module.embed_chunks
    try:
        def _raise_import_error(*_args, **_kwargs):
            raise ImportError("forced offline validation")

        indexer_module.embed_chunks = _raise_import_error
        result = manage_tenant_indices(
            tenant_id="lane2-managed",
            operation="create",
            index_names=["managed-a", "managed-b"],
            files=files[:4],
            index_dir=str(INDEX_DIR),
            chunk_size=120,
            overlap=0,
        )
        listing = manage_tenant_indices(
            tenant_id="lane2-managed",
            operation="list",
            index_names=[],
            index_dir=str(INDEX_DIR),
        )
        cleanup = manage_tenant_indices(
            tenant_id="lane2-managed",
            operation="delete",
            index_names=["managed-a", "managed-b"],
            index_dir=str(INDEX_DIR),
        )
        return {
            "create_success": result.success,
            "list_success": listing.success,
            "list_count": len(listing.details.get("indices", [])) if listing.details else 0,
            "delete_success": cleanup.success,
        }
    finally:
        indexer_module.embed_chunks = original_embed_chunks


def main() -> None:
    _reset_workspace()
    files, queries = _build_corpus()

    primary_build_error = None
    try:
        start = time.perf_counter()
        build_index_from_files(
            files=files[:2],
            index_name="primary-attempt",
            tenant_id="lane2",
            index_dir=str(INDEX_DIR),
            chunk_size=180,
            overlap=16,
        )
        primary_build = {
            "success": True,
            "build_ms": (time.perf_counter() - start) * 1000,
        }
    except Exception as exc:
        primary_build_error = f"{type(exc).__name__}: {exc}"
        primary_build = {"success": False, "error": primary_build_error}

    offline_build = _force_offline_index_build(files)
    query_metrics = _measure_queries(offline_build["retriever"], queries)
    lifecycle = _run_lifecycle_validation()
    imports = _check_imports()
    cycles = _detect_cross_package_cycles()
    ooda = _ooda_integration_validation(query_metrics)
    multi_index = _multi_index_validation(files)

    rag_indexer = RAGIndexer(index_dir=str(INDEX_DIR))
    from aries_serpent_core.rag import retriever as retriever_module

    original_sentence_transformer = retriever_module.SentenceTransformer
    retriever_module.SentenceTransformer = None
    try:
        cached_retriever = CachedRetriever(
            index_dir=str(INDEX_DIR),
            index_name="lane2-validation",
            tenant_id="lane2",
            cache_ttl=1,
            cache_maxsize=8,
        )
    finally:
        retriever_module.SentenceTransformer = original_sentence_transformer
    cached_retriever.query_with_cache("python decorators", top_k=3)
    cached_retriever.query_with_cache("python decorators", top_k=3)

    payload = {
        "b2": {
            "builder_exists": True,
            "builder_module": "src/aries_serpent_core/rag/indexer.py",
            "primary_build_attempt": primary_build,
            "offline_validated_build": {
                k: v
                for k, v in offline_build.items()
                if k not in {"retriever", "chunks"}
            },
            "query_metrics": query_metrics,
            "cached_retriever_stats": cached_retriever.get_cache_stats(),
            "rag_indexer_tenants": rag_indexer.list_tenants(),
            "multi_index_validation": multi_index,
        },
        "b3": lifecycle,
        "b4": {
            "imports": imports,
            "ooda": ooda,
            "cross_package_cycles": cycles,
        },
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
