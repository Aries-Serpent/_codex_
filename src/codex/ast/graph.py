"""Dependency graph with cycle detection.

Uses Tarjan's strongly connected components algorithm to detect cycles.
Reference: https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm
"""

from typing import Dict, List, Set
from collections import defaultdict


class DependencyGraph:
    """Directed graph for dependency analysis and cycle detection."""
    
    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: Dict[str, Set[str]] = defaultdict(set)
    
    def add_node(self, node_id: str) -> None:
        """Add node to graph."""
        self.nodes.add(node_id)
    
    def add_edge(self, source: str, target: str) -> None:
        """Add directed edge: source → target."""
        self.nodes.add(source)
        self.nodes.add(target)
        self.edges[source].add(target)
    
    def detect_cycles(self) -> List[List[str]]:
        """Detect all cycles using Tarjan's algorithm.
        
        Returns:
            List of cycles, where each cycle is a list of node IDs
            forming a strongly connected component (cycle) in the graph.
        
        Time Complexity: O(V + E) where V = nodes, E = edges
        Space Complexity: O(V)
        """
        index_counter = [0]
        stack = []
        lowlinks = {}
        index = {}
        on_stack = {}
        sccs = []
        
        def strongconnect(node_id: str):
            """Recursive SCC detection for single node."""
            index[node_id] = index_counter[0]
            lowlinks[node_id] = index_counter[0]
            index_counter[0] += 1
            stack.append(node_id)
            on_stack[node_id] = True
            
            # Process successors
            for target_id in self.edges.get(node_id, set()):
                if target_id not in index:
                    # Successor not yet visited
                    strongconnect(target_id)
                    lowlinks[node_id] = min(lowlinks[node_id], lowlinks[target_id])
                elif on_stack.get(target_id, False):
                    # Successor on stack = back edge (cycle indicator)
                    lowlinks[node_id] = min(lowlinks[node_id], index[target_id])
            
            # If node is a root node of SCC, pop the stack
            if lowlinks[node_id] == index[node_id]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    scc.append(w)
                    if w == node_id:
                        break
                
                # Record cycles: multi-node SCCs or single-node self-loops
                if len(scc) > 1:
                    sccs.append(scc)
                elif len(scc) == 1 and node_id in self.edges.get(node_id, set()):
                    # Single-node SCC with self-edge is a cycle
                    sccs.append(scc)
        
        # Find SCCs for all nodes
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)
        
        return sccs
    
    def topological_sort(self) -> List[str]:
        """Topological sort of DAG (fails if cycles exist).
        
        Returns:
            List of nodes in topological order
        
        Raises:
            ValueError: If graph contains cycles
        """
        cycles = self.detect_cycles()
        if cycles:
            raise ValueError(f"Graph has cycles: {cycles}")
        
        visited = set()
        stack = []
        
        def dfs(node_id: str):
            visited.add(node_id)
            for target in self.edges.get(node_id, set()):
                if target not in visited:
                    dfs(target)
            stack.append(node_id)
        
        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)
        
        return stack[::-1]
    
    def get_transitive_deps(self, node_id: str) -> Set[str]:
        """Get all transitive dependencies of a node."""
        visited = set()
        stack = [node_id]
        
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            
            visited.add(current)
            stack.extend(self.edges.get(current, set()))
        
        return visited - {node_id}
