#!/usr/bin/env python3
"""
Phase 3 Lane 2: RAG Index Builder
Builds core + runtime RAG indexes for _codex_ repository governance docs
"""

import json
import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import re

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from rag.pipelines import ChunkingPipeline, EmbeddingPipeline
except ImportError as e:
    print(f"Warning: Could not import RAG pipelines: {e}")
    print("Continuing with mock RAG implementation...")


class RAGIndexBuilder:
    """Builds RAG indexes for core and runtime profiles."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.repo_root = base_path.parent  # .codex is in repo root, not two levels up
        self.index_dir = base_path / "rag_indexes"
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.core_documents = []
        self.runtime_documents = []
        self.core_index = None
        self.runtime_index = None
        self.stats = {
            "core": {
                "documents_ingested": 0,
                "total_tokens": 0,
                "embedding_count": 0,
                "files": []
            },
            "runtime": {
                "documents_ingested": 0,
                "total_tokens": 0,
                "embedding_count": 0,
                "files": []
            },
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    
    def collect_governance_docs(self) -> None:
        """Collect all governance documents for indexing."""
        
        print("[*] Collecting governance documents...")
        
        # Core Profile Documents (Policy & Agency)
        core_files = [
            "CODEBASE_AGENCY_POLICY.md",
            "AGENTIC_REPO_STATE.md",
        ]
        
        # Runtime Profile Documents (.github/docs)
        runtime_files = []
        github_docs = self.repo_root / ".github" / "docs"
        if github_docs.exists():
            runtime_files = [f for f in github_docs.glob("*.md")]
        
        # Collect core documents
        for file in core_files:
            file_path = self.base_path / file
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    self.core_documents.append({
                        "path": f".codex/{file}",
                        "content": content,
                        "source": "core_policy",
                        "ingestion_time": datetime.now().isoformat()
                    })
                    self.stats["core"]["files"].append(f".codex/{file}")
                    print(f"  ✓ Ingested core: {file} ({len(content)} chars)")
                except Exception as e:
                    print(f"  ✗ Error reading {file}: {e}")
        
        # Collect runtime documents
        for file_path in runtime_files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                rel_path = file_path.relative_to(self.repo_root)
                self.runtime_documents.append({
                    "path": str(rel_path),
                    "content": content,
                    "source": "governance",
                    "ingestion_time": datetime.now().isoformat()
                })
                self.stats["runtime"]["files"].append(str(rel_path))
                print(f"  ✓ Ingested runtime: {rel_path.name} ({len(content)} chars)")
            except Exception as e:
                print(f"  ✗ Error reading {file_path}: {e}")
        
        print(f"\n[+] Collected {len(self.core_documents)} core documents")
        print(f"[+] Collected {len(self.runtime_documents)} runtime documents")
    
    def chunk_documents(self) -> Tuple[List[Dict], List[Dict]]:
        """Chunk all collected documents."""
        
        print("\n[*] Chunking documents...")
        
        core_chunks = []
        runtime_chunks = []
        
        # Simple chunking: split by sections (marked with #)
        for doc in self.core_documents:
            chunks = self._chunk_document(doc)
            core_chunks.extend(chunks)
            self.stats["core"]["total_tokens"] += sum(len(c["content"].split()) for c in chunks)
        
        for doc in self.runtime_documents:
            chunks = self._chunk_document(doc)
            runtime_chunks.extend(chunks)
            self.stats["runtime"]["total_tokens"] += sum(len(c["content"].split()) for c in chunks)
        
        print(f"[+] Created {len(core_chunks)} core chunks")
        print(f"[+] Created {len(runtime_chunks)} runtime chunks")
        
        return core_chunks, runtime_chunks
    
    def _chunk_document(self, doc: Dict, chunk_size: int = 512) -> List[Dict]:
        """Simple chunking strategy: split by headers and word count."""
        
        content = doc["content"]
        chunks = []
        
        # Split by top-level headers (##)
        sections = re.split(r'(^## .*?$)', content, flags=re.MULTILINE)
        
        current_section = ""
        for section in sections:
            if section.startswith("##"):
                if current_section:
                    # Process accumulated section
                    for chunk in self._split_section(current_section, chunk_size):
                        chunks.append({
                            "path": doc["path"],
                            "source": doc["source"],
                            "content": chunk,
                            "tokens": len(chunk.split()),
                            "hash": hashlib.md5(chunk.encode()).hexdigest()[:8]
                        })
                current_section = section
            else:
                current_section += section
        
        # Process final section
        if current_section:
            for chunk in self._split_section(current_section, chunk_size):
                chunks.append({
                    "path": doc["path"],
                    "source": doc["source"],
                    "content": chunk,
                    "tokens": len(chunk.split()),
                    "hash": hashlib.md5(chunk.encode()).hexdigest()[:8]
                })
        
        return chunks if chunks else [
            {
                "path": doc["path"],
                "source": doc["source"],
                "content": content[:1000] if len(content) > 1000 else content,
                "tokens": len(content.split()),
                "hash": hashlib.md5(content.encode()).hexdigest()[:8]
            }
        ]
    
    def _split_section(self, text: str, chunk_size: int = 512) -> List[str]:
        """Split section into chunks by word count."""
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks if chunks else [text] if text.strip() else []
    
    def build_indexes(self, core_chunks: List[Dict], runtime_chunks: List[Dict]) -> None:
        """Build the core and runtime indexes."""
        
        print("\n[*] Building RAG indexes...")
        
        # Create core index
        self.core_index = {
            "version": "1.0.0",
            "profile": "core",
            "created_at": datetime.now().isoformat(),
            "chunks": core_chunks,
            "metadata": {
                "documents_count": len(self.core_documents),
                "chunks_count": len(core_chunks),
                "total_tokens": self.stats["core"]["total_tokens"]
            }
        }
        
        # Create runtime index
        self.runtime_index = {
            "version": "1.0.0",
            "profile": "runtime",
            "created_at": datetime.now().isoformat(),
            "chunks": runtime_chunks,
            "metadata": {
                "documents_count": len(self.runtime_documents),
                "chunks_count": len(runtime_chunks),
                "total_tokens": self.stats["runtime"]["total_tokens"]
            }
        }
        
        # Update stats
        self.stats["core"]["documents_ingested"] = len(self.core_documents)
        self.stats["core"]["embedding_count"] = len(core_chunks)
        self.stats["runtime"]["documents_ingested"] = len(self.runtime_documents)
        self.stats["runtime"]["embedding_count"] = len(runtime_chunks)
        
        print(f"[+] Core index: {len(core_chunks)} chunks, {self.stats['core']['total_tokens']} tokens")
        print(f"[+] Runtime index: {len(runtime_chunks)} chunks, {self.stats['runtime']['total_tokens']} tokens")
    
    def save_indexes(self) -> None:
        """Save indexes to disk."""
        
        print("\n[*] Saving indexes to disk...")
        
        # Save core index
        core_file = self.index_dir / "core_index.json"
        core_file.write_text(json.dumps(self.core_index, indent=2))
        print(f"[+] Saved core index: {core_file}")
        
        # Save runtime index
        runtime_file = self.index_dir / "runtime_index.json"
        runtime_file.write_text(json.dumps(self.runtime_index, indent=2))
        print(f"[+] Saved runtime index: {runtime_file}")
        
        # Save statistics
        stats_file = self.index_dir / "build_stats.json"
        stats_file.write_text(json.dumps(self.stats, indent=2))
        print(f"[+] Saved statistics: {stats_file}")
    
    def run(self) -> Dict[str, Any]:
        """Run the full RAG index building pipeline."""
        
        print("=" * 70)
        print("RAG INDEX BUILDER - Phase 3 Lane 2")
        print("=" * 70)
        
        self.collect_governance_docs()
        core_chunks, runtime_chunks = self.chunk_documents()
        self.build_indexes(core_chunks, runtime_chunks)
        self.save_indexes()
        
        print("\n" + "=" * 70)
        print("RAG INDEX BUILDING COMPLETE")
        print("=" * 70)
        
        return self.stats


def main():
    """Main entry point."""
    
    base_path = Path(__file__).parent
    builder = RAGIndexBuilder(base_path)
    stats = builder.run()
    
    print("\n[SUMMARY]")
    print(json.dumps(stats, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
