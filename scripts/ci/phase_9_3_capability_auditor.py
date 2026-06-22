#!/usr/bin/env python3
"""
Phase 9.3 Task 1: Capability Corpus Auditor
============================================
Build searchable semantic index of all 145 active agents.

Extracts capabilities from AGENT_REGISTRY.yaml and agent documentation,
generates embeddings using sentence-transformers, and builds FAISS index.

Output: .codex/PHASE_9_3_CAPABILITY_INDEX.json (searchable index)
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


@dataclass
class AgentCapability:
    """Represents a single agent's metadata and capabilities."""
    agent_id: str
    name: str
    version: str
    status: str
    category: str
    subcategory: str
    description: str
    capabilities: List[str]
    capability_tags: List[str]
    primary_skill: str
    secondary_skill: str
    purpose: str
    embedding_vector: List[float]
    embedding_dimension: int
    autonomy_model: str
    maturity: str
    has_tests: bool
    has_docs: bool
    created: str
    updated: str
    maintainer: str


def load_agent_registry(registry_path: str) -> Dict[str, Any]:
    """Load and parse AGENT_REGISTRY.yaml."""
    with open(registry_path, 'r') as f:
        return yaml.safe_load(f)


def build_agent_text_profile(agent: Dict[str, Any]) -> str:
    """
    Build comprehensive text profile for an agent for embedding.
    Combines all textual metadata into semantic context.
    """
    parts = []
    
    # Primary identifiers
    parts.append(f"Agent: {agent.get('name', '')}")
    parts.append(f"ID: {agent.get('id', '')}")
    
    # Description and purpose
    if agent.get('description'):
        parts.append(f"Description: {agent['description']}")
    if agent.get('purpose'):
        parts.append(f"Purpose: {agent['purpose']}")
    
    # Skills
    if agent.get('primary_skill'):
        parts.append(f"Primary skill: {agent['primary_skill']}")
    if agent.get('secondary_skill'):
        parts.append(f"Secondary skill: {agent['secondary_skill']}")
    
    # Capabilities
    if agent.get('capabilities'):
        capabilities_text = ", ".join(agent['capabilities'])
        parts.append(f"Capabilities: {capabilities_text}")
    
    # Capability tags
    if agent.get('capability_tags'):
        tags_text = ", ".join(agent['capability_tags'])
        parts.append(f"Tags: {tags_text}")
    
    # Category and subcategory
    parts.append(f"Category: {agent.get('category', '')} / {agent.get('subcategory', '')}")
    
    # Metadata
    parts.append(f"Maturity: {agent.get('maturity', '')}")
    parts.append(f"Autonomy: {agent.get('autonomy_model', '')}")
    
    return " ".join(parts)


def extract_agents_from_registry(registry: Dict[str, Any]) -> List[AgentCapability]:
    """
    Extract active agents from registry and build capability objects.
    Filter to only active agents (status = 'active').
    """
    agents = []
    registry_agents = registry.get('agents', [])
    
    print(f"Processing {len(registry_agents)} total agents from registry...")
    active_count = 0
    
    for agent in registry_agents:
        if agent.get('status') != 'active':
            continue
        
        active_count += 1
        
        try:
            agent_id = agent.get('id', '')
            name = agent.get('name', agent_id)
            version = agent.get('version', '1.0.0')
            status = agent.get('status', 'unknown')
            category = agent.get('category', 'uncategorized')
            subcategory = agent.get('subcategory', 'general')
            description = agent.get('description', '')
            capabilities = agent.get('capabilities', [])
            capability_tags = agent.get('capability_tags', [])
            primary_skill = agent.get('primary_skill', '')
            secondary_skill = agent.get('secondary_skill', '')
            purpose = agent.get('purpose', '')
            autonomy_model = agent.get('autonomy_model', 'E')
            maturity = agent.get('maturity', 'beta')
            has_tests = agent.get('has_tests', False)
            has_docs = agent.get('has_docs', False)
            created = agent.get('created', '2026-01-01')
            updated = agent.get('updated', '2026-01-01')
            maintainer = agent.get('maintainer', 'unknown')
            
            agent_obj = AgentCapability(
                agent_id=agent_id,
                name=name,
                version=version,
                status=status,
                category=category,
                subcategory=subcategory,
                description=description,
                capabilities=capabilities if isinstance(capabilities, list) else [],
                capability_tags=capability_tags if isinstance(capability_tags, list) else [],
                primary_skill=primary_skill,
                secondary_skill=secondary_skill,
                purpose=purpose,
                embedding_vector=[],  # Will be filled during embedding
                embedding_dimension=0,  # Will be filled during embedding
                autonomy_model=autonomy_model,
                maturity=maturity,
                has_tests=has_tests,
                has_docs=has_docs,
                created=created,
                updated=updated,
                maintainer=maintainer,
            )
            agents.append(agent_obj)
            
        except Exception as e:
            print(f"Error processing agent {agent.get('id', 'unknown')}: {e}")
            continue
    
    print(f"Extracted {active_count} active agents from {len(registry_agents)} total")
    return agents


def generate_embeddings(agents: List[AgentCapability], model_name: str = "all-MiniLM-L6-v2") -> Tuple[List[AgentCapability], np.ndarray]:
    """
    Generate semantic embeddings for all agents.
    Uses sentence-transformers all-MiniLM-L6-v2 (384-dimensional, fast, accurate).
    """
    print(f"Loading SentenceTransformer model: {model_name}")
    model = SentenceTransformer(model_name)
    
    # Build text profiles for all agents
    agent_texts = []
    for agent in agents:
        text_profile = build_agent_text_profile(asdict(agent))
        agent_texts.append(text_profile)
    
    print(f"Generating embeddings for {len(agent_texts)} agents...")
    embeddings = model.encode(agent_texts, show_progress_bar=True, convert_to_numpy=True)
    
    # Attach embeddings to agents
    for i, agent in enumerate(agents):
        agent.embedding_vector = embeddings[i].tolist()
        agent.embedding_dimension = embeddings[i].shape[0]
    
    print(f"Generated embeddings: {embeddings.shape}")
    return agents, embeddings


def build_faiss_index(embeddings: np.ndarray) -> Tuple[Any, np.ndarray]:
    """
    Build FAISS index for fast semantic similarity search.
    Uses L2 distance (Euclidean) metric.
    """
    print(f"Building FAISS index on {embeddings.shape[0]} embeddings...")
    
    # Normalize embeddings for cosine similarity
    embeddings_normalized = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    # Create FAISS index (L2 metric, normalized = cosine)
    dimension = embeddings_normalized.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_normalized.astype(np.float32))
    
    print(f"FAISS index created with {index.ntotal} vectors, dimension={dimension}")
    return index, embeddings_normalized


def build_capability_index_json(
    agents: List[AgentCapability],
    faiss_index: Any,
    embeddings: np.ndarray,
    output_path: str
) -> Dict[str, Any]:
    """
    Build comprehensive searchable JSON index.
    Includes agent metadata, embeddings, and search structure.
    """
    print(f"Building JSON capability index...")
    
    # Build agent lookup by ID and category
    agents_by_id = {agent.agent_id: asdict(agent) for agent in agents}
    agents_by_category = {}
    agents_by_tag = {}
    agents_by_autonomy = {}
    
    for agent in agents:
        # By category
        cat_key = f"{agent.category}/{agent.subcategory}"
        if cat_key not in agents_by_category:
            agents_by_category[cat_key] = []
        agents_by_category[cat_key].append(agent.agent_id)
        
        # By capability tags
        for tag in agent.capability_tags:
            if tag not in agents_by_tag:
                agents_by_tag[tag] = []
            agents_by_tag[tag].append(agent.agent_id)
        
        # By autonomy model
        autonomy = agent.autonomy_model
        if autonomy not in agents_by_autonomy:
            agents_by_autonomy[autonomy] = []
        agents_by_autonomy[autonomy].append(agent.agent_id)
    
    # Build index document
    index_data = {
        "metadata": {
            "version": "1.0",
            "total_agents": len(agents),
            "active_agents": len([a for a in agents if a.status == "active"]),
            "embedding_model": "all-MiniLM-L6-v2",
            "embedding_dimension": agents[0].embedding_dimension if agents else 0,
            "similarity_metric": "cosine",
            "faiss_index_type": "IndexFlatL2",
            "created": "2026-06-22T11:12:24Z",
            "build_timestamp": "2026-06-22T11:12:24Z",
        },
        "agents": agents_by_id,
        "indices": {
            "by_id": {agent.agent_id: idx for idx, agent in enumerate(agents)},
            "by_category": agents_by_category,
            "by_tag": agents_by_tag,
            "by_autonomy": agents_by_autonomy,
            "id_to_agent": {idx: agent.agent_id for idx, agent in enumerate(agents)},
        },
        "capabilities": {
            "categories": list(set(a.category for a in agents)),
            "subcategories": list(set(f"{a.category}/{a.subcategory}" for a in agents)),
            "all_tags": sorted(list(set([tag for a in agents for tag in a.capability_tags]))),
            "autonomy_models": sorted(list(set(a.autonomy_model for a in agents))),
        },
        "search_hints": {
            "query_examples": [
                "ci testing agent",
                "security vulnerability scanning",
                "coverage analysis",
                "documentation quality",
                "performance monitoring",
            ],
            "similarity_threshold": 0.85,
            "top_k_default": 5,
        },
    }
    
    # Save JSON index
    print(f"Writing capability index to {output_path}")
    with open(output_path, 'w') as f:
        json.dump(index_data, f, indent=2)
    
    print(f"Capability index saved: {len(index_data['agents'])} agents indexed")
    return index_data


def save_faiss_index(faiss_index: Any, output_path: str):
    """Save FAISS index to disk."""
    faiss.write_index(faiss_index, output_path)
    print(f"FAISS index saved to {output_path}")


def generate_search_statistics(
    agents: List[AgentCapability],
    index_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate summary statistics for audited agent corpus."""
    stats = {
        "total_agents": len(agents),
        "by_category": {},
        "by_maturity": {},
        "by_autonomy": {},
        "capabilities_per_agent": [],
        "tags_per_agent": [],
    }
    
    for agent in agents:
        # By category
        cat = agent.category
        if cat not in stats["by_category"]:
            stats["by_category"][cat] = 0
        stats["by_category"][cat] += 1
        
        # By maturity
        mat = agent.maturity
        if mat not in stats["by_maturity"]:
            stats["by_maturity"][mat] = 0
        stats["by_maturity"][mat] += 1
        
        # By autonomy
        aut = agent.autonomy_model
        if aut not in stats["by_autonomy"]:
            stats["by_autonomy"][aut] = 0
        stats["by_autonomy"][aut] += 1
        
        # Capabilities per agent
        stats["capabilities_per_agent"].append(len(agent.capabilities))
        
        # Tags per agent
        stats["tags_per_agent"].append(len(agent.capability_tags))
    
    stats["avg_capabilities_per_agent"] = np.mean(stats["capabilities_per_agent"])
    stats["avg_tags_per_agent"] = np.mean(stats["tags_per_agent"])
    
    return stats


def main():
    """Main execution for Task 9.3.1: Build capability index."""
    
    # Paths
    registry_path = ".github/agents/AGENT_REGISTRY.yaml"
    output_dir = ".codex"
    index_json_path = os.path.join(output_dir, "PHASE_9_3_CAPABILITY_INDEX.json")
    faiss_index_path = os.path.join(output_dir, "PHASE_9_3_AGENT_EMBEDDINGS.faiss")
    stats_path = os.path.join(output_dir, "PHASE_9_3_AGENT_CORPUS_STATS.json")
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("PHASE 9.3 TASK 1: AUDIT 145-AGENT CAPABILITY CORPUS")
    print("=" * 80)
    
    # Step 1: Load registry
    print("\n[1/6] Loading AGENT_REGISTRY.yaml...")
    registry = load_agent_registry(registry_path)
    print(f"Registry version: {registry.get('version')}")
    print(f"Total agents: {registry.get('total_agents')}, Active: {registry.get('active_agents')}")
    
    # Step 2: Extract active agents
    print("\n[2/6] Extracting active agents...")
    agents = extract_agents_from_registry(registry)
    print(f"Extracted {len(agents)} active agents")
    
    # Step 3: Generate embeddings
    print("\n[3/6] Generating semantic embeddings...")
    agents, embeddings = generate_embeddings(agents)
    print(f"Embeddings shape: {embeddings.shape}")
    
    # Step 4: Build FAISS index
    print("\n[4/6] Building FAISS index...")
    faiss_index, embeddings_normalized = build_faiss_index(embeddings)
    
    # Step 5: Build JSON index
    print("\n[5/6] Building JSON capability index...")
    index_data = build_capability_index_json(agents, faiss_index, embeddings_normalized, index_json_path)
    
    # Step 6: Save FAISS index
    print("\n[6/6] Saving FAISS index...")
    save_faiss_index(faiss_index, faiss_index_path)
    
    # Generate statistics
    print("\n[BONUS] Generating corpus statistics...")
    stats = generate_search_statistics(agents, index_data)
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"Statistics saved to {stats_path}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("TASK 9.3.1 COMPLETE: 145-AGENT CAPABILITY INDEX BUILT")
    print("=" * 80)
    print(f"✓ Capability index: {index_json_path} ({len(agents)} agents)")
    print(f"✓ FAISS embeddings: {faiss_index_path} ({embeddings.shape})")
    print(f"✓ Corpus statistics: {stats_path}")
    print(f"\nAgent Distribution:")
    for category, count in sorted(stats["by_category"].items()):
        print(f"  • {category}: {count} agents")
    print(f"\nMaturity Levels:")
    for maturity, count in sorted(stats["by_maturity"].items()):
        print(f"  • {maturity}: {count} agents")
    print("\nIndex ready for semantic routing engine (Task 9.3.2)")
    print("=" * 80)


if __name__ == "__main__":
    main()
