"""
Dependency graph implementation with cycle detection.

Provides directed graph operations for tracking code dependencies,
including cycle detection using Tarjan's algorithm and topological sorting.
"""

from typing import Any, Optional

from codex_ml.ast.core.exceptions import CycleDetectedError


class DependencyGraph:
    """Directed dependency graph with cycle detection.

    Tracks dependencies between code entities (modules, functions, classes)
    and provides operations for analyzing dependency relationships.

    Example:
        graph = DependencyGraph()
        graph.add_node("module_a", ["module_b", "module_c"])
        graph.add_node("module_b", ["module_c"])
        graph.add_node("module_c", [])

        if not graph.has_cycle():
            order = graph.topological_sort()
            logger.info(order)  # ['module_c', 'module_b', 'module_a']
    """

    def __init__(self) -> None:
        """Initialize empty dependency graph."""
        self.nodes: dict[str, set[str]] = {}
        self.reverse_edges: dict[str, set[str]] = {}  # Track reverse dependencies
        self.node_data: dict[str, dict[str, Any]] = {}  # Store arbitrary node data

    def add_node(
        self,
        node_id: str,
        dependencies: Optional[list[str]] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> None:
        """Add a node with its dependencies and optional data.

        Args:
            node_id: Unique identifier for the node
            dependencies: List of node IDs this node depends on
            data: Optional dictionary of node attributes/metadata
        """
        deps = set(dependencies or [])
        self.nodes[node_id] = deps

        # Store or update node data
        if node_id not in self.node_data:
            self.node_data[node_id] = data or {}
        elif data:
            # Update existing node data
            self.node_data[node_id].update(data)

        # Initialize reverse edges for new nodes
        if node_id not in self.reverse_edges:
            self.reverse_edges[node_id] = set()

        # Update reverse edges
        for dep in deps:
            if dep not in self.nodes:
                self.nodes[dep] = set()
            if dep not in self.reverse_edges:
                self.reverse_edges[dep] = set()
            if dep not in self.node_data:
                self.node_data[dep] = {}
            self.reverse_edges[dep].add(node_id)

    def remove_node(self, node_id: str) -> bool:
        """Remove a node and all its edges.

        Args:
            node_id: Node to remove

        Returns:
            True if node was removed, False if not found
        """
        if node_id not in self.nodes:
            return False

        # Remove forward edges
        del self.nodes[node_id]

        # Remove node data
        if node_id in self.node_data:
            del self.node_data[node_id]

        # Remove from reverse edges
        if node_id in self.reverse_edges:
            del self.reverse_edges[node_id]

        # Clean up references in other nodes
        for deps in self.nodes.values():
            deps.discard(node_id)

        for dependents in self.reverse_edges.values():
            dependents.discard(node_id)

        return True

    def add_edge(self, from_node: str, to_node: str) -> None:
        """Add a dependency edge from one node to another.

        Args:
            from_node: The dependent node
            to_node: The dependency
        """
        if from_node not in self.nodes:
            self.nodes[from_node] = set()
        if to_node not in self.nodes:
            self.nodes[to_node] = set()

        self.nodes[from_node].add(to_node)

        if to_node not in self.reverse_edges:
            self.reverse_edges[to_node] = set()
        self.reverse_edges[to_node].add(from_node)

    def remove_edge(self, from_node: str, to_node: str) -> bool:
        """Remove a dependency edge.

        Args:
            from_node: The dependent node
            to_node: The dependency

        Returns:
            True if edge was removed, False if not found
        """
        if from_node not in self.nodes:
            return False
        if to_node not in self.nodes[from_node]:
            return False

        self.nodes[from_node].discard(to_node)
        if to_node in self.reverse_edges:
            self.reverse_edges[to_node].discard(from_node)

        return True

    def get_dependencies(self, node_id: str) -> set[str]:
        """Get direct dependencies of a node.

        Args:
            node_id: Node to query

        Returns:
            Set of node IDs that this node depends on
        """
        return self.nodes.get(node_id, set()).copy()

    def get_dependents(self, node_id: str) -> set[str]:
        """Get nodes that depend on the given node.

        Args:
            node_id: Node to query

        Returns:
            Set of node IDs that depend on this node
        """
        return self.reverse_edges.get(node_id, set()).copy()

    def get_node_data(self, node_id: str) -> dict[str, Any]:
        """Get data associated with a node.

        Args:
            node_id: Node to query

        Returns:
            Dictionary of node data (empty dict if node has no data)
        """
        return self.node_data.get(node_id, {}).copy()

    def set_node_data(self, node_id: str, data: dict[str, Any]) -> None:
        """Set or update data for a node.

        Args:
            node_id: Node to update
            data: Dictionary of node attributes to set/update

        Raises:
            KeyError: If node does not exist
        """
        if node_id not in self.nodes:
            raise KeyError(f"Node '{node_id}' does not exist in graph")
        if node_id not in self.node_data:
            self.node_data[node_id] = {}
        self.node_data[node_id].update(data)

    def get_all_dependencies(self, node_id: str) -> set[str]:
        """Get all transitive dependencies of a node.

        Args:
            node_id: Node to query

        Returns:
            Set of all node IDs that this node depends on (directly or transitively)
        """
        visited = set()

        def dfs(node: str) -> None:
            for dep in self.nodes.get(node, []):
                if dep not in visited:
                    visited.add(dep)
                    dfs(dep)

        dfs(node_id)
        return visited

    def has_cycle(self) -> bool:
        """Check if the graph contains any cycles.

        Uses depth-first search with recursion stack tracking
        (Tarjan's algorithm variant).

        Returns:
            True if a cycle exists, False otherwise
        """
        visited = set()
        rec_stack = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.nodes.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        return any(node not in visited and dfs(node) for node in self.nodes)

    def find_cycle(self) -> Optional[list[str]]:
        """Find a cycle in the graph if one exists.

        Returns:
            List of node IDs forming a cycle, or None if no cycle exists
        """
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str) -> Optional[list[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.nodes.get(node, []):
                if neighbor not in visited:
                    result = dfs(neighbor)
                    if result:
                        return result
                elif neighbor in rec_stack:
                    # Found cycle - extract it from path
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]

            path.pop()
            rec_stack.remove(node)
            return None

        for node in self.nodes:
            if node not in visited:
                cycle = dfs(node)
                if cycle:
                    return cycle

        return None

    def topological_sort(self) -> list[str]:
        """Return nodes in topological order (dependencies first).

        Returns:
            List of node IDs in topological order

        Raises:
            CycleDetectedError: If the graph contains a cycle
        """
        if self.has_cycle():
            cycle = self.find_cycle()
            raise CycleDetectedError(
                f"Cannot topologically sort graph with cycle: {' -> '.join(cycle or [])}",
                cycle=cycle,
            )

        visited = set()
        order = []

        def visit(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            for dep in self.nodes.get(node, []):
                visit(dep)
            order.append(node)

        for node in self.nodes:
            visit(node)

        return order

    def reverse_topological_sort(self) -> list[str]:
        """Return nodes in reverse topological order (dependents first).

        Returns:
            List of node IDs in reverse topological order

        Raises:
            CycleDetectedError: If the graph contains a cycle
        """
        return list(reversed(self.topological_sort()))

    def get_strongly_connected_components(self) -> list[set[str]]:
        """Find all strongly connected components using Tarjan's algorithm.

        Returns:
            List of sets, each containing node IDs in a strongly connected component
        """
        index_counter = [0]
        stack = []
        lowlink = {}
        index = {}
        on_stack = {}
        sccs = []

        def strongconnect(node: str) -> None:
            index[node] = index_counter[0]
            lowlink[node] = index_counter[0]
            index_counter[0] += 1
            stack.append(node)
            on_stack[node] = True

            for neighbor in self.nodes.get(node, []):
                if neighbor not in index:
                    strongconnect(neighbor)
                    lowlink[node] = min(lowlink[node], lowlink[neighbor])
                elif on_stack.get(neighbor, False):
                    lowlink[node] = min(lowlink[node], index[neighbor])

            if lowlink[node] == index[node]:
                scc = set()
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    scc.add(w)
                    if w == node:
                        break
                sccs.append(scc)

        for node in self.nodes:
            if node not in index:
                strongconnect(node)

        return sccs

    def get_roots(self) -> set[str]:
        """Get nodes with no dependencies (roots of the DAG).

        Returns:
            Set of node IDs with no dependencies
        """
        return {node for node, deps in self.nodes.items() if not deps}

    def get_leaves(self) -> set[str]:
        """Get nodes with no dependents (leaves of the DAG).

        Returns:
            Set of node IDs with no dependents
        """
        return {node for node in self.nodes if not self.reverse_edges.get(node)}

    def __len__(self) -> int:
        """Return number of nodes in the graph."""
        return len(self.nodes)

    def __contains__(self, node_id: str) -> bool:
        """Check if a node exists in the graph."""
        return node_id in self.nodes

    def edge_count(self) -> int:
        """Return number of edges in the graph.

        Note: This is O(n) where n is number of nodes. For frequent access,
        consider caching if the graph is large and mostly static.
        """
        return sum(len(deps) for deps in self.nodes.values())

    def __repr__(self) -> str:
        # Use node count only for efficiency; edge_count() is available if needed
        return f"DependencyGraph(nodes={len(self.nodes)})"
