"""Dependency graph with cycle detection.

Uses Tarjan's strongly connected components algorithm to detect cycles.
Reference: https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm
"""

from collections import defaultdict
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class DependencyGraph:
    """Directed graph for dependency analysis and cycle detection."""

    def xǁDependencyGraphǁ__init____mutmut_orig(self):
        self.nodes: set[str] = set()
        self.edges: dict[str, set[str]] = defaultdict(set)
        self.node_data: dict[str, dict] = {}

    def xǁDependencyGraphǁ__init____mutmut_1(self):
        self.nodes: set[str] = None
        self.edges: dict[str, set[str]] = defaultdict(set)
        self.node_data: dict[str, dict] = {}

    def xǁDependencyGraphǁ__init____mutmut_2(self):
        self.nodes: set[str] = set()
        self.edges: dict[str, set[str]] = None
        self.node_data: dict[str, dict] = {}

    def xǁDependencyGraphǁ__init____mutmut_3(self):
        self.nodes: set[str] = set()
        self.edges: dict[str, set[str]] = defaultdict(None)
        self.node_data: dict[str, dict] = {}

    def xǁDependencyGraphǁ__init____mutmut_4(self):
        self.nodes: set[str] = set()
        self.edges: dict[str, set[str]] = defaultdict(set)
        self.node_data: dict[str, dict] = None
    
    xǁDependencyGraphǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDependencyGraphǁ__init____mutmut_1': xǁDependencyGraphǁ__init____mutmut_1, 
        'xǁDependencyGraphǁ__init____mutmut_2': xǁDependencyGraphǁ__init____mutmut_2, 
        'xǁDependencyGraphǁ__init____mutmut_3': xǁDependencyGraphǁ__init____mutmut_3, 
        'xǁDependencyGraphǁ__init____mutmut_4': xǁDependencyGraphǁ__init____mutmut_4
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDependencyGraphǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁDependencyGraphǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁDependencyGraphǁ__init____mutmut_orig)
    xǁDependencyGraphǁ__init____mutmut_orig.__name__ = 'xǁDependencyGraphǁ__init__'

    def xǁDependencyGraphǁadd_node__mutmut_orig(self, node_id: str, data: dict | None = None) -> None:
        """Add node to graph with optional metadata.
        
        Args:
            node_id: The name/identifier of the node
            data: Optional dictionary of node attributes
        """
        self.nodes.add(node_id)
        if data:
            self.node_data[node_id] = data

    def xǁDependencyGraphǁadd_node__mutmut_1(self, node_id: str, data: dict | None = None) -> None:
        """Add node to graph with optional metadata.
        
        Args:
            node_id: The name/identifier of the node
            data: Optional dictionary of node attributes
        """
        self.nodes.add(None)
        if data:
            self.node_data[node_id] = data

    def xǁDependencyGraphǁadd_node__mutmut_2(self, node_id: str, data: dict | None = None) -> None:
        """Add node to graph with optional metadata.
        
        Args:
            node_id: The name/identifier of the node
            data: Optional dictionary of node attributes
        """
        self.nodes.add(node_id)
        if data:
            self.node_data[node_id] = None
    
    xǁDependencyGraphǁadd_node__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDependencyGraphǁadd_node__mutmut_1': xǁDependencyGraphǁadd_node__mutmut_1, 
        'xǁDependencyGraphǁadd_node__mutmut_2': xǁDependencyGraphǁadd_node__mutmut_2
    }
    
    def add_node(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDependencyGraphǁadd_node__mutmut_orig"), object.__getattribute__(self, "xǁDependencyGraphǁadd_node__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add_node.__signature__ = _mutmut_signature(xǁDependencyGraphǁadd_node__mutmut_orig)
    xǁDependencyGraphǁadd_node__mutmut_orig.__name__ = 'xǁDependencyGraphǁadd_node'

    def xǁDependencyGraphǁadd_edge__mutmut_orig(self, source: str, target: str) -> None:
        """Add directed edge: source → target."""
        self.nodes.add(source)
        self.nodes.add(target)
        self.edges[source].add(target)

    def xǁDependencyGraphǁadd_edge__mutmut_1(self, source: str, target: str) -> None:
        """Add directed edge: source → target."""
        self.nodes.add(None)
        self.nodes.add(target)
        self.edges[source].add(target)

    def xǁDependencyGraphǁadd_edge__mutmut_2(self, source: str, target: str) -> None:
        """Add directed edge: source → target."""
        self.nodes.add(source)
        self.nodes.add(None)
        self.edges[source].add(target)

    def xǁDependencyGraphǁadd_edge__mutmut_3(self, source: str, target: str) -> None:
        """Add directed edge: source → target."""
        self.nodes.add(source)
        self.nodes.add(target)
        self.edges[source].add(None)
    
    xǁDependencyGraphǁadd_edge__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDependencyGraphǁadd_edge__mutmut_1': xǁDependencyGraphǁadd_edge__mutmut_1, 
        'xǁDependencyGraphǁadd_edge__mutmut_2': xǁDependencyGraphǁadd_edge__mutmut_2, 
        'xǁDependencyGraphǁadd_edge__mutmut_3': xǁDependencyGraphǁadd_edge__mutmut_3
    }
    
    def add_edge(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDependencyGraphǁadd_edge__mutmut_orig"), object.__getattribute__(self, "xǁDependencyGraphǁadd_edge__mutmut_mutants"), args, kwargs, self)
        return result 
    
    add_edge.__signature__ = _mutmut_signature(xǁDependencyGraphǁadd_edge__mutmut_orig)
    xǁDependencyGraphǁadd_edge__mutmut_orig.__name__ = 'xǁDependencyGraphǁadd_edge'

    def xǁDependencyGraphǁdetect_cycles__mutmut_orig(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_1(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
            forming a strongly connected component (cycle) in the graph.

        Time Complexity: O(V + E) where V = nodes, E = edges
        Space Complexity: O(V)
        """
        index_counter = None
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_2(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
            forming a strongly connected component (cycle) in the graph.

        Time Complexity: O(V + E) where V = nodes, E = edges
        Space Complexity: O(V)
        """
        index_counter = [1]
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_3(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
            forming a strongly connected component (cycle) in the graph.

        Time Complexity: O(V + E) where V = nodes, E = edges
        Space Complexity: O(V)
        """
        index_counter = [0]
        stack = None
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_4(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
            forming a strongly connected component (cycle) in the graph.

        Time Complexity: O(V + E) where V = nodes, E = edges
        Space Complexity: O(V)
        """
        index_counter = [0]
        stack = []
        lowlinks = None
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_5(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
            forming a strongly connected component (cycle) in the graph.

        Time Complexity: O(V + E) where V = nodes, E = edges
        Space Complexity: O(V)
        """
        index_counter = [0]
        stack = []
        lowlinks = {}
        index = None
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_6(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
            forming a strongly connected component (cycle) in the graph.

        Time Complexity: O(V + E) where V = nodes, E = edges
        Space Complexity: O(V)
        """
        index_counter = [0]
        stack = []
        lowlinks = {}
        index = {}
        on_stack = None
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_7(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
            forming a strongly connected component (cycle) in the graph.

        Time Complexity: O(V + E) where V = nodes, E = edges
        Space Complexity: O(V)
        """
        index_counter = [0]
        stack = []
        lowlinks = {}
        index = {}
        on_stack = {}
        sccs = None

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

    def xǁDependencyGraphǁdetect_cycles__mutmut_8(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            index[node_id] = None
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_9(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            index[node_id] = index_counter[1]
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_10(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            lowlinks[node_id] = None
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_11(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            lowlinks[node_id] = index_counter[1]
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_12(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            index_counter[0] = 1
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_13(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            index_counter[0] -= 1
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_14(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            index_counter[1] += 1
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_15(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            index_counter[0] += 2
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_16(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            stack.append(None)
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_17(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            on_stack[node_id] = None

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

    def xǁDependencyGraphǁdetect_cycles__mutmut_18(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            on_stack[node_id] = False

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

    def xǁDependencyGraphǁdetect_cycles__mutmut_19(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            for target_id in self.edges.get(None, set()):
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_20(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            for target_id in self.edges.get(node_id, None):
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_21(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            for target_id in self.edges.get(set()):
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_22(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            for target_id in self.edges.get(node_id, ):
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_23(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                if target_id in index:
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_24(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    strongconnect(None)
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_25(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    lowlinks[node_id] = None
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_26(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    lowlinks[node_id] = min(None, lowlinks[target_id])
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_27(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    lowlinks[node_id] = min(lowlinks[node_id], None)
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_28(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    lowlinks[node_id] = min(lowlinks[target_id])
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_29(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    lowlinks[node_id] = min(lowlinks[node_id], )
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_30(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                elif on_stack.get(None, False):
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_31(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                elif on_stack.get(target_id, None):
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_32(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                elif on_stack.get(False):
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_33(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                elif on_stack.get(target_id, ):
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_34(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                elif on_stack.get(target_id, True):
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_35(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    lowlinks[node_id] = None

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

    def xǁDependencyGraphǁdetect_cycles__mutmut_36(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    lowlinks[node_id] = min(None, index[target_id])

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

    def xǁDependencyGraphǁdetect_cycles__mutmut_37(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    lowlinks[node_id] = min(lowlinks[node_id], None)

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

    def xǁDependencyGraphǁdetect_cycles__mutmut_38(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    lowlinks[node_id] = min(index[target_id])

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

    def xǁDependencyGraphǁdetect_cycles__mutmut_39(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    lowlinks[node_id] = min(lowlinks[node_id], )

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

    def xǁDependencyGraphǁdetect_cycles__mutmut_40(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            if lowlinks[node_id] != index[node_id]:
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_41(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                scc = None
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_42(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                while False:
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_43(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    w = None
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_44(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    on_stack[w] = None
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_45(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    on_stack[w] = True
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_46(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    scc.append(None)
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_47(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    if w != node_id:
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

    def xǁDependencyGraphǁdetect_cycles__mutmut_48(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                        return

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

    def xǁDependencyGraphǁdetect_cycles__mutmut_49(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                if len(scc) >= 1:
                    sccs.append(scc)
                elif len(scc) == 1 and node_id in self.edges.get(node_id, set()):
                    # Single-node SCC with self-edge is a cycle
                    sccs.append(scc)

        # Find SCCs for all nodes
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)

        return sccs

    def xǁDependencyGraphǁdetect_cycles__mutmut_50(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                if len(scc) > 2:
                    sccs.append(scc)
                elif len(scc) == 1 and node_id in self.edges.get(node_id, set()):
                    # Single-node SCC with self-edge is a cycle
                    sccs.append(scc)

        # Find SCCs for all nodes
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)

        return sccs

    def xǁDependencyGraphǁdetect_cycles__mutmut_51(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    sccs.append(None)
                elif len(scc) == 1 and node_id in self.edges.get(node_id, set()):
                    # Single-node SCC with self-edge is a cycle
                    sccs.append(scc)

        # Find SCCs for all nodes
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)

        return sccs

    def xǁDependencyGraphǁdetect_cycles__mutmut_52(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                elif len(scc) == 1 or node_id in self.edges.get(node_id, set()):
                    # Single-node SCC with self-edge is a cycle
                    sccs.append(scc)

        # Find SCCs for all nodes
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)

        return sccs

    def xǁDependencyGraphǁdetect_cycles__mutmut_53(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                elif len(scc) != 1 and node_id in self.edges.get(node_id, set()):
                    # Single-node SCC with self-edge is a cycle
                    sccs.append(scc)

        # Find SCCs for all nodes
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)

        return sccs

    def xǁDependencyGraphǁdetect_cycles__mutmut_54(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                elif len(scc) == 2 and node_id in self.edges.get(node_id, set()):
                    # Single-node SCC with self-edge is a cycle
                    sccs.append(scc)

        # Find SCCs for all nodes
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)

        return sccs

    def xǁDependencyGraphǁdetect_cycles__mutmut_55(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                elif len(scc) == 1 and node_id not in self.edges.get(node_id, set()):
                    # Single-node SCC with self-edge is a cycle
                    sccs.append(scc)

        # Find SCCs for all nodes
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)

        return sccs

    def xǁDependencyGraphǁdetect_cycles__mutmut_56(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                elif len(scc) == 1 and node_id in self.edges.get(None, set()):
                    # Single-node SCC with self-edge is a cycle
                    sccs.append(scc)

        # Find SCCs for all nodes
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)

        return sccs

    def xǁDependencyGraphǁdetect_cycles__mutmut_57(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                elif len(scc) == 1 and node_id in self.edges.get(node_id, None):
                    # Single-node SCC with self-edge is a cycle
                    sccs.append(scc)

        # Find SCCs for all nodes
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)

        return sccs

    def xǁDependencyGraphǁdetect_cycles__mutmut_58(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                elif len(scc) == 1 and node_id in self.edges.get(set()):
                    # Single-node SCC with self-edge is a cycle
                    sccs.append(scc)

        # Find SCCs for all nodes
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)

        return sccs

    def xǁDependencyGraphǁdetect_cycles__mutmut_59(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                elif len(scc) == 1 and node_id in self.edges.get(node_id, ):
                    # Single-node SCC with self-edge is a cycle
                    sccs.append(scc)

        # Find SCCs for all nodes
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)

        return sccs

    def xǁDependencyGraphǁdetect_cycles__mutmut_60(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                    sccs.append(None)

        # Find SCCs for all nodes
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)

        return sccs

    def xǁDependencyGraphǁdetect_cycles__mutmut_61(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
            if node_id in index:
                strongconnect(node_id)

        return sccs

    def xǁDependencyGraphǁdetect_cycles__mutmut_62(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's algorithm.

        Returns:
            list of cycles, where each cycle is a list of node IDs
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
                strongconnect(None)

        return sccs
    
    xǁDependencyGraphǁdetect_cycles__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDependencyGraphǁdetect_cycles__mutmut_1': xǁDependencyGraphǁdetect_cycles__mutmut_1, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_2': xǁDependencyGraphǁdetect_cycles__mutmut_2, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_3': xǁDependencyGraphǁdetect_cycles__mutmut_3, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_4': xǁDependencyGraphǁdetect_cycles__mutmut_4, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_5': xǁDependencyGraphǁdetect_cycles__mutmut_5, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_6': xǁDependencyGraphǁdetect_cycles__mutmut_6, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_7': xǁDependencyGraphǁdetect_cycles__mutmut_7, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_8': xǁDependencyGraphǁdetect_cycles__mutmut_8, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_9': xǁDependencyGraphǁdetect_cycles__mutmut_9, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_10': xǁDependencyGraphǁdetect_cycles__mutmut_10, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_11': xǁDependencyGraphǁdetect_cycles__mutmut_11, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_12': xǁDependencyGraphǁdetect_cycles__mutmut_12, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_13': xǁDependencyGraphǁdetect_cycles__mutmut_13, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_14': xǁDependencyGraphǁdetect_cycles__mutmut_14, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_15': xǁDependencyGraphǁdetect_cycles__mutmut_15, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_16': xǁDependencyGraphǁdetect_cycles__mutmut_16, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_17': xǁDependencyGraphǁdetect_cycles__mutmut_17, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_18': xǁDependencyGraphǁdetect_cycles__mutmut_18, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_19': xǁDependencyGraphǁdetect_cycles__mutmut_19, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_20': xǁDependencyGraphǁdetect_cycles__mutmut_20, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_21': xǁDependencyGraphǁdetect_cycles__mutmut_21, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_22': xǁDependencyGraphǁdetect_cycles__mutmut_22, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_23': xǁDependencyGraphǁdetect_cycles__mutmut_23, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_24': xǁDependencyGraphǁdetect_cycles__mutmut_24, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_25': xǁDependencyGraphǁdetect_cycles__mutmut_25, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_26': xǁDependencyGraphǁdetect_cycles__mutmut_26, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_27': xǁDependencyGraphǁdetect_cycles__mutmut_27, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_28': xǁDependencyGraphǁdetect_cycles__mutmut_28, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_29': xǁDependencyGraphǁdetect_cycles__mutmut_29, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_30': xǁDependencyGraphǁdetect_cycles__mutmut_30, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_31': xǁDependencyGraphǁdetect_cycles__mutmut_31, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_32': xǁDependencyGraphǁdetect_cycles__mutmut_32, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_33': xǁDependencyGraphǁdetect_cycles__mutmut_33, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_34': xǁDependencyGraphǁdetect_cycles__mutmut_34, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_35': xǁDependencyGraphǁdetect_cycles__mutmut_35, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_36': xǁDependencyGraphǁdetect_cycles__mutmut_36, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_37': xǁDependencyGraphǁdetect_cycles__mutmut_37, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_38': xǁDependencyGraphǁdetect_cycles__mutmut_38, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_39': xǁDependencyGraphǁdetect_cycles__mutmut_39, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_40': xǁDependencyGraphǁdetect_cycles__mutmut_40, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_41': xǁDependencyGraphǁdetect_cycles__mutmut_41, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_42': xǁDependencyGraphǁdetect_cycles__mutmut_42, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_43': xǁDependencyGraphǁdetect_cycles__mutmut_43, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_44': xǁDependencyGraphǁdetect_cycles__mutmut_44, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_45': xǁDependencyGraphǁdetect_cycles__mutmut_45, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_46': xǁDependencyGraphǁdetect_cycles__mutmut_46, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_47': xǁDependencyGraphǁdetect_cycles__mutmut_47, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_48': xǁDependencyGraphǁdetect_cycles__mutmut_48, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_49': xǁDependencyGraphǁdetect_cycles__mutmut_49, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_50': xǁDependencyGraphǁdetect_cycles__mutmut_50, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_51': xǁDependencyGraphǁdetect_cycles__mutmut_51, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_52': xǁDependencyGraphǁdetect_cycles__mutmut_52, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_53': xǁDependencyGraphǁdetect_cycles__mutmut_53, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_54': xǁDependencyGraphǁdetect_cycles__mutmut_54, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_55': xǁDependencyGraphǁdetect_cycles__mutmut_55, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_56': xǁDependencyGraphǁdetect_cycles__mutmut_56, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_57': xǁDependencyGraphǁdetect_cycles__mutmut_57, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_58': xǁDependencyGraphǁdetect_cycles__mutmut_58, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_59': xǁDependencyGraphǁdetect_cycles__mutmut_59, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_60': xǁDependencyGraphǁdetect_cycles__mutmut_60, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_61': xǁDependencyGraphǁdetect_cycles__mutmut_61, 
        'xǁDependencyGraphǁdetect_cycles__mutmut_62': xǁDependencyGraphǁdetect_cycles__mutmut_62
    }
    
    def detect_cycles(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDependencyGraphǁdetect_cycles__mutmut_orig"), object.__getattribute__(self, "xǁDependencyGraphǁdetect_cycles__mutmut_mutants"), args, kwargs, self)
        return result 
    
    detect_cycles.__signature__ = _mutmut_signature(xǁDependencyGraphǁdetect_cycles__mutmut_orig)
    xǁDependencyGraphǁdetect_cycles__mutmut_orig.__name__ = 'xǁDependencyGraphǁdetect_cycles'

    def xǁDependencyGraphǁtopological_sort__mutmut_orig(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

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

    def xǁDependencyGraphǁtopological_sort__mutmut_1(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

        Raises:
            ValueError: If graph contains cycles
        """
        cycles = None
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

    def xǁDependencyGraphǁtopological_sort__mutmut_2(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

        Raises:
            ValueError: If graph contains cycles
        """
        cycles = self.detect_cycles()
        if cycles:
            raise ValueError(None)

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

    def xǁDependencyGraphǁtopological_sort__mutmut_3(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

        Raises:
            ValueError: If graph contains cycles
        """
        cycles = self.detect_cycles()
        if cycles:
            raise ValueError(f"Graph has cycles: {cycles}")

        visited = None
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

    def xǁDependencyGraphǁtopological_sort__mutmut_4(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

        Raises:
            ValueError: If graph contains cycles
        """
        cycles = self.detect_cycles()
        if cycles:
            raise ValueError(f"Graph has cycles: {cycles}")

        visited = set()
        stack = None

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

    def xǁDependencyGraphǁtopological_sort__mutmut_5(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

        Raises:
            ValueError: If graph contains cycles
        """
        cycles = self.detect_cycles()
        if cycles:
            raise ValueError(f"Graph has cycles: {cycles}")

        visited = set()
        stack = []

        def dfs(node_id: str):
            visited.add(None)
            for target in self.edges.get(node_id, set()):
                if target not in visited:
                    dfs(target)
            stack.append(node_id)

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)

        return stack[::-1]

    def xǁDependencyGraphǁtopological_sort__mutmut_6(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

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
            for target in self.edges.get(None, set()):
                if target not in visited:
                    dfs(target)
            stack.append(node_id)

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)

        return stack[::-1]

    def xǁDependencyGraphǁtopological_sort__mutmut_7(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

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
            for target in self.edges.get(node_id, None):
                if target not in visited:
                    dfs(target)
            stack.append(node_id)

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)

        return stack[::-1]

    def xǁDependencyGraphǁtopological_sort__mutmut_8(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

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
            for target in self.edges.get(set()):
                if target not in visited:
                    dfs(target)
            stack.append(node_id)

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)

        return stack[::-1]

    def xǁDependencyGraphǁtopological_sort__mutmut_9(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

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
            for target in self.edges.get(node_id, ):
                if target not in visited:
                    dfs(target)
            stack.append(node_id)

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)

        return stack[::-1]

    def xǁDependencyGraphǁtopological_sort__mutmut_10(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

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
                if target in visited:
                    dfs(target)
            stack.append(node_id)

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)

        return stack[::-1]

    def xǁDependencyGraphǁtopological_sort__mutmut_11(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

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
                    dfs(None)
            stack.append(node_id)

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)

        return stack[::-1]

    def xǁDependencyGraphǁtopological_sort__mutmut_12(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

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
            stack.append(None)

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)

        return stack[::-1]

    def xǁDependencyGraphǁtopological_sort__mutmut_13(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

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
            if node_id in visited:
                dfs(node_id)

        return stack[::-1]

    def xǁDependencyGraphǁtopological_sort__mutmut_14(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

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
                dfs(None)

        return stack[::-1]

    def xǁDependencyGraphǁtopological_sort__mutmut_15(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

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

        return stack[::+1]

    def xǁDependencyGraphǁtopological_sort__mutmut_16(self) -> list[str]:
        """Topological sort of DAG (fails if cycles exist).

        Returns:
            list of nodes in topological order

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

        return stack[::-2]
    
    xǁDependencyGraphǁtopological_sort__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDependencyGraphǁtopological_sort__mutmut_1': xǁDependencyGraphǁtopological_sort__mutmut_1, 
        'xǁDependencyGraphǁtopological_sort__mutmut_2': xǁDependencyGraphǁtopological_sort__mutmut_2, 
        'xǁDependencyGraphǁtopological_sort__mutmut_3': xǁDependencyGraphǁtopological_sort__mutmut_3, 
        'xǁDependencyGraphǁtopological_sort__mutmut_4': xǁDependencyGraphǁtopological_sort__mutmut_4, 
        'xǁDependencyGraphǁtopological_sort__mutmut_5': xǁDependencyGraphǁtopological_sort__mutmut_5, 
        'xǁDependencyGraphǁtopological_sort__mutmut_6': xǁDependencyGraphǁtopological_sort__mutmut_6, 
        'xǁDependencyGraphǁtopological_sort__mutmut_7': xǁDependencyGraphǁtopological_sort__mutmut_7, 
        'xǁDependencyGraphǁtopological_sort__mutmut_8': xǁDependencyGraphǁtopological_sort__mutmut_8, 
        'xǁDependencyGraphǁtopological_sort__mutmut_9': xǁDependencyGraphǁtopological_sort__mutmut_9, 
        'xǁDependencyGraphǁtopological_sort__mutmut_10': xǁDependencyGraphǁtopological_sort__mutmut_10, 
        'xǁDependencyGraphǁtopological_sort__mutmut_11': xǁDependencyGraphǁtopological_sort__mutmut_11, 
        'xǁDependencyGraphǁtopological_sort__mutmut_12': xǁDependencyGraphǁtopological_sort__mutmut_12, 
        'xǁDependencyGraphǁtopological_sort__mutmut_13': xǁDependencyGraphǁtopological_sort__mutmut_13, 
        'xǁDependencyGraphǁtopological_sort__mutmut_14': xǁDependencyGraphǁtopological_sort__mutmut_14, 
        'xǁDependencyGraphǁtopological_sort__mutmut_15': xǁDependencyGraphǁtopological_sort__mutmut_15, 
        'xǁDependencyGraphǁtopological_sort__mutmut_16': xǁDependencyGraphǁtopological_sort__mutmut_16
    }
    
    def topological_sort(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDependencyGraphǁtopological_sort__mutmut_orig"), object.__getattribute__(self, "xǁDependencyGraphǁtopological_sort__mutmut_mutants"), args, kwargs, self)
        return result 
    
    topological_sort.__signature__ = _mutmut_signature(xǁDependencyGraphǁtopological_sort__mutmut_orig)
    xǁDependencyGraphǁtopological_sort__mutmut_orig.__name__ = 'xǁDependencyGraphǁtopological_sort'

    def xǁDependencyGraphǁget_transitive_deps__mutmut_orig(self, node_id: str) -> set[str]:
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

    def xǁDependencyGraphǁget_transitive_deps__mutmut_1(self, node_id: str) -> set[str]:
        """Get all transitive dependencies of a node."""
        visited = None
        stack = [node_id]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            stack.extend(self.edges.get(current, set()))

        return visited - {node_id}

    def xǁDependencyGraphǁget_transitive_deps__mutmut_2(self, node_id: str) -> set[str]:
        """Get all transitive dependencies of a node."""
        visited = set()
        stack = None

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            stack.extend(self.edges.get(current, set()))

        return visited - {node_id}

    def xǁDependencyGraphǁget_transitive_deps__mutmut_3(self, node_id: str) -> set[str]:
        """Get all transitive dependencies of a node."""
        visited = set()
        stack = [node_id]

        while stack:
            current = None
            if current in visited:
                continue

            visited.add(current)
            stack.extend(self.edges.get(current, set()))

        return visited - {node_id}

    def xǁDependencyGraphǁget_transitive_deps__mutmut_4(self, node_id: str) -> set[str]:
        """Get all transitive dependencies of a node."""
        visited = set()
        stack = [node_id]

        while stack:
            current = stack.pop()
            if current not in visited:
                continue

            visited.add(current)
            stack.extend(self.edges.get(current, set()))

        return visited - {node_id}

    def xǁDependencyGraphǁget_transitive_deps__mutmut_5(self, node_id: str) -> set[str]:
        """Get all transitive dependencies of a node."""
        visited = set()
        stack = [node_id]

        while stack:
            current = stack.pop()
            if current in visited:
                break

            visited.add(current)
            stack.extend(self.edges.get(current, set()))

        return visited - {node_id}

    def xǁDependencyGraphǁget_transitive_deps__mutmut_6(self, node_id: str) -> set[str]:
        """Get all transitive dependencies of a node."""
        visited = set()
        stack = [node_id]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(None)
            stack.extend(self.edges.get(current, set()))

        return visited - {node_id}

    def xǁDependencyGraphǁget_transitive_deps__mutmut_7(self, node_id: str) -> set[str]:
        """Get all transitive dependencies of a node."""
        visited = set()
        stack = [node_id]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            stack.extend(None)

        return visited - {node_id}

    def xǁDependencyGraphǁget_transitive_deps__mutmut_8(self, node_id: str) -> set[str]:
        """Get all transitive dependencies of a node."""
        visited = set()
        stack = [node_id]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            stack.extend(self.edges.get(None, set()))

        return visited - {node_id}

    def xǁDependencyGraphǁget_transitive_deps__mutmut_9(self, node_id: str) -> set[str]:
        """Get all transitive dependencies of a node."""
        visited = set()
        stack = [node_id]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            stack.extend(self.edges.get(current, None))

        return visited - {node_id}

    def xǁDependencyGraphǁget_transitive_deps__mutmut_10(self, node_id: str) -> set[str]:
        """Get all transitive dependencies of a node."""
        visited = set()
        stack = [node_id]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            stack.extend(self.edges.get(set()))

        return visited - {node_id}

    def xǁDependencyGraphǁget_transitive_deps__mutmut_11(self, node_id: str) -> set[str]:
        """Get all transitive dependencies of a node."""
        visited = set()
        stack = [node_id]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            stack.extend(self.edges.get(current, ))

        return visited - {node_id}

    def xǁDependencyGraphǁget_transitive_deps__mutmut_12(self, node_id: str) -> set[str]:
        """Get all transitive dependencies of a node."""
        visited = set()
        stack = [node_id]

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            stack.extend(self.edges.get(current, set()))

        return visited + {node_id}
    
    xǁDependencyGraphǁget_transitive_deps__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDependencyGraphǁget_transitive_deps__mutmut_1': xǁDependencyGraphǁget_transitive_deps__mutmut_1, 
        'xǁDependencyGraphǁget_transitive_deps__mutmut_2': xǁDependencyGraphǁget_transitive_deps__mutmut_2, 
        'xǁDependencyGraphǁget_transitive_deps__mutmut_3': xǁDependencyGraphǁget_transitive_deps__mutmut_3, 
        'xǁDependencyGraphǁget_transitive_deps__mutmut_4': xǁDependencyGraphǁget_transitive_deps__mutmut_4, 
        'xǁDependencyGraphǁget_transitive_deps__mutmut_5': xǁDependencyGraphǁget_transitive_deps__mutmut_5, 
        'xǁDependencyGraphǁget_transitive_deps__mutmut_6': xǁDependencyGraphǁget_transitive_deps__mutmut_6, 
        'xǁDependencyGraphǁget_transitive_deps__mutmut_7': xǁDependencyGraphǁget_transitive_deps__mutmut_7, 
        'xǁDependencyGraphǁget_transitive_deps__mutmut_8': xǁDependencyGraphǁget_transitive_deps__mutmut_8, 
        'xǁDependencyGraphǁget_transitive_deps__mutmut_9': xǁDependencyGraphǁget_transitive_deps__mutmut_9, 
        'xǁDependencyGraphǁget_transitive_deps__mutmut_10': xǁDependencyGraphǁget_transitive_deps__mutmut_10, 
        'xǁDependencyGraphǁget_transitive_deps__mutmut_11': xǁDependencyGraphǁget_transitive_deps__mutmut_11, 
        'xǁDependencyGraphǁget_transitive_deps__mutmut_12': xǁDependencyGraphǁget_transitive_deps__mutmut_12
    }
    
    def get_transitive_deps(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDependencyGraphǁget_transitive_deps__mutmut_orig"), object.__getattribute__(self, "xǁDependencyGraphǁget_transitive_deps__mutmut_mutants"), args, kwargs, self)
        return result 
    
    get_transitive_deps.__signature__ = _mutmut_signature(xǁDependencyGraphǁget_transitive_deps__mutmut_orig)
    xǁDependencyGraphǁget_transitive_deps__mutmut_orig.__name__ = 'xǁDependencyGraphǁget_transitive_deps'


class ASTGraph(DependencyGraph):
    """Alias of DependencyGraph for AST visualization tooling."""
