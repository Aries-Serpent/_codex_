"""Semantic similarity detection using MinHash algorithm."""

import hashlib
import re
from collections import defaultdict
from pathlib import Path

from .schema import DuplicateGroup, MemberFile


class MinHashDetector:
    """Detects similar code using MinHash algorithm."""

    def __init__(
        self,
        root_path: Path,
        threshold: float = 0.75,
        num_perm: int = 128,
        shingle_size: int = 5,
        exclude_patterns: list[str] = None,
        respect_gitignore: bool = True,
    ):
        """
        Initialize MinHash detector.

        Args:
            root_path: Repository root path
            threshold: Similarity threshold (0.0-1.0)
            num_perm: Number of permutations for MinHash
            shingle_size: Size of shingles (token sequences)
            exclude_patterns: Patterns to exclude
            respect_gitignore: Whether to respect .gitignore
        """
        self.root_path = Path(root_path)
        self.threshold = threshold
        self.num_perm = num_perm
        self.shingle_size = shingle_size
        self.exclude_patterns = exclude_patterns or []
        self.respect_gitignore = respect_gitignore

    def tokenize(self, code: str) -> list[str]:
        """
        Tokenize code into meaningful tokens.

        Args:
            code: Source code string

        Returns:
            List of tokens
        """
        # Remove comments (simple approach)
        code = re.sub(r"#.*$", "", code, flags=re.MULTILINE)
        code = re.sub(r"//.*$", "", code, flags=re.MULTILINE)
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)

        # Remove strings (replace with placeholder)
        code = re.sub(r'"[^"]*"', "STRING", code)
        code = re.sub(r"'[^']*'", "STRING", code)

        # Tokenize by splitting on non-alphanumeric
        return re.findall(r"\w+", code.lower())


    def create_shingles(self, tokens: list[str]) -> set[str]:
        """
        Create shingles (n-grams) from tokens.

        Args:
            tokens: List of tokens

        Returns:
            Set of shingles
        """
        shingles = set()
        for i in range(len(tokens) - self.shingle_size + 1):
            shingle = " ".join(tokens[i : i + self.shingle_size])
            shingles.add(shingle)
        return shingles

    def compute_minhash(self, shingles: set[str]) -> list[int]:
        """
        Compute MinHash signature.

        Uses deterministic hashing for consistent results across runs.

        Args:
            shingles: Set of shingles

        Returns:
            MinHash signature (list of hash values)
        """
        if not shingles:
            return [0] * self.num_perm

        signature = []
        for i in range(self.num_perm):
            min_hash = float("inf")
            for shingle in shingles:
                # Use deterministic hash (SHA256) for consistent results
                hash_input = f"{shingle}:{i}".encode("utf-8")
                h = int(hashlib.sha256(hash_input).hexdigest()[:8], 16)
                min_hash = min(min_hash, h)
            signature.append(min_hash)

        return signature

    def jaccard_similarity(self, sig1: list[int], sig2: list[int]) -> float:
        """
        Estimate Jaccard similarity from MinHash signatures.

        Args:
            sig1: First signature
            sig2: Second signature

        Returns:
            Estimated similarity (0.0-1.0)
        """
        if len(sig1) != len(sig2):
            return 0.0

        matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return matches / len(sig1)

    def scan(self) -> list[DuplicateGroup]:
        """
        Scan repository for semantically similar code.

        Returns:
            List of duplicate groups
        """
        # Find all source files
        files = self._find_source_files()

        # Compute MinHash signatures for all files
        signatures: dict[str, list[int]] = {}
        file_content: dict[str, str] = {}

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tokens = self.tokenize(content)
                if len(tokens) < self.shingle_size:
                    continue

                shingles = self.create_shingles(tokens)
                signature = self.compute_minhash(shingles)

                rel_path = str(self._make_relative(file_path))
                signatures[rel_path] = signature
                file_content[rel_path] = content

            except Exception:
                continue

        # Find similar pairs
        similar_pairs = self._find_similar_pairs(signatures)

        # Cluster similar files
        clusters = self._cluster_similar(similar_pairs)

        # Create duplicate groups
        duplicate_groups = []
        for cluster_id, (paths, avg_similarity) in enumerate(clusters, 1):
            if len(paths) < 2:
                continue

            # Create member files
            member_files = []
            for path in paths:
                member = MemberFile(
                    path=path,
                    file_hash=hashlib.sha256(file_content[path].encode()).hexdigest()[:16],
                    similarity_score=avg_similarity,
                )
                member_files.append(member)

            # Get representative (shortest path)
            representative = min(paths, key=len)

            # Create summary
            summary = file_content[representative][:200]

            group = DuplicateGroup(
                id=f"dup-semantic-{cluster_id:03d}",
                type="semantic-cluster",
                language="multi",
                representative_path=representative,
                member_files=member_files,
                reason=f"Semantically similar code (similarity: {avg_similarity:.2f})",
                suggested_action="refactor",
                confidence="medium" if avg_similarity > 0.85 else "low",
                tags=["semantic-similar", "minhash"],
                meta={
                    "detection_method": ["semantic", "minhash"],
                    "similarity_threshold": self.threshold,
                    "avg_similarity": round(avg_similarity, 3),
                },
                summary=summary,
            )

            duplicate_groups.append(group)

        return duplicate_groups

    def _find_similar_pairs(self, signatures: dict[str, list[int]]) -> list[tuple[str, str, float]]:
        """Find pairs of files with similarity above threshold."""
        similar_pairs = []
        paths = list(signatures.keys())

        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                path1, path2 = paths[i], paths[j]
                similarity = self.jaccard_similarity(signatures[path1], signatures[path2])

                if similarity >= self.threshold:
                    similar_pairs.append((path1, path2, similarity))

        return similar_pairs

    def _cluster_similar(
        self, pairs: list[tuple[str, str, float]]
    ) -> list[tuple[list[str], float]]:
        """
        Cluster similar files using union-find.

        Returns:
            List of (cluster_paths, avg_similarity) tuples
        """
        if not pairs:
            return []

        # Build adjacency list
        graph: dict[str, set[str]] = defaultdict(set)
        similarities: dict[tuple[str, str], float] = {}

        for path1, path2, sim in pairs:
            graph[path1].add(path2)
            graph[path2].add(path1)
            similarities[(path1, path2)] = sim
            similarities[(path2, path1)] = sim

        # Find connected components
        visited = set()
        clusters = []

        for node in graph:
            if node in visited:
                continue

            # BFS to find cluster
            cluster = []
            queue = [node]
            visited.add(node)

            while queue:
                current = queue.pop(0)
                cluster.append(current)

                for neighbor in graph[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            # Calculate average similarity for cluster
            if len(cluster) >= 2:
                sims = []
                for i in range(len(cluster)):
                    for j in range(i + 1, len(cluster)):
                        key = (cluster[i], cluster[j])
                        if key in similarities:
                            sims.append(similarities[key])

                avg_sim = sum(sims) / len(sims) if sims else 0.0
                clusters.append((cluster, avg_sim))

        return clusters

    def _find_source_files(self) -> list[Path]:
        """Find all source files in repository."""
        source_files = []

        # Common source extensions
        extensions = {".py", ".js", ".ts", ".java", ".go", ".rb", ".php", ".cpp", ".c", ".h"}

        # Exclusion patterns
        exclude_dirs = {
            ".git",
            "node_modules",
            "vendor",
            "third_party",
            "__pycache__",
            "build",
            "dist",
            ".venv",
            "venv",
        }

        for ext in extensions:
            for path in self.root_path.rglob(f"*{ext}"):
                if any(part in exclude_dirs for part in path.parts):
                    continue
                source_files.append(path)

        return source_files

    def _make_relative(self, file_path: Path) -> Path:
        """Make file path relative to repository root."""
        try:
            return file_path.relative_to(self.root_path)
        except ValueError:
            return file_path
