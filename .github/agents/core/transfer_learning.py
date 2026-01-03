"""
Transfer Learning Engine for Cognitive Brain.

Phase 8.4 Implementation (100% Complete):
- TransferLearningEngine: Cross-domain knowledge transfer
- DomainAdapter: Domain adaptation for different task types
- KnowledgeDistiller: Extract transferable knowledge
- MetaLearningFramework: Cross-domain adaptation optimization
- DynamicDomainDetector: Automatic domain detection from Q-tables
- CrossAgentKnowledgeSharing: Protocol for agent-to-agent knowledge transfer

Status: Complete implementation with 51+ tests
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Callable, Set
from abc import ABC, abstractmethod
import hashlib
import json
from collections import defaultdict


@dataclass
class DomainInfo:
    """Information about a learning domain.
    
    Attributes:
        name: Domain identifier
        features: Domain feature dimensions
        action_space: Available actions in domain
        knowledge_base: Stored domain knowledge
    """
    name: str
    features: List[str] = field(default_factory=list)
    action_space: List[str] = field(default_factory=list)
    knowledge_base: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransferableKnowledge:
    """Knowledge that can be transferred between domains.
    
    Attributes:
        source_domain: Origin domain
        target_domain: Destination domain
        patterns: Transferable patterns
        weights: Importance weights
        compatibility_score: How well knowledge transfers
    """
    source_domain: str
    target_domain: str
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    weights: Dict[str, float] = field(default_factory=dict)
    compatibility_score: float = 0.0


class DomainAdapter(ABC):
    """Abstract base for domain adaptation.
    
    Adapts knowledge from source to target domain by:
    - Feature mapping
    - Action space alignment
    - Reward shaping translation
    """
    
    @abstractmethod
    def adapt_features(
        self,
        source_features: Dict[str, Any],
        source_domain: DomainInfo,
        target_domain: DomainInfo,
    ) -> Dict[str, Any]:
        """Adapt features from source to target domain.
        
        Args:
            source_features: Features from source domain
            source_domain: Source domain info
            target_domain: Target domain info
            
        Returns:
            Adapted features for target domain
        """
        pass
    
    @abstractmethod
    def adapt_actions(
        self,
        source_action: str,
        source_domain: DomainInfo,
        target_domain: DomainInfo,
    ) -> Optional[str]:
        """Adapt action from source to target domain.
        
        Args:
            source_action: Action from source domain
            source_domain: Source domain info
            target_domain: Target domain info
            
        Returns:
            Equivalent action in target domain, or None if no mapping
        """
        pass
    
    @abstractmethod
    def compute_compatibility(
        self,
        source_domain: DomainInfo,
        target_domain: DomainInfo,
    ) -> float:
        """Compute compatibility score between domains.
        
        Args:
            source_domain: Source domain info
            target_domain: Target domain info
            
        Returns:
            Compatibility score [0, 1]
        """
        pass


class SimpleDomainAdapter(DomainAdapter):
    """Simple domain adapter using feature/action name matching.
    
    Implements basic transfer by matching feature and action names
    between domains.
    """
    
    def adapt_features(
        self,
        source_features: Dict[str, Any],
        source_domain: DomainInfo,
        target_domain: DomainInfo,
    ) -> Dict[str, Any]:
        """Adapt features using name matching."""
        adapted = {}
        
        for feature_name, value in source_features.items():
            # Direct match
            if feature_name in target_domain.features:
                adapted[feature_name] = value
            # Prefix match
            else:
                for target_feature in target_domain.features:
                    if feature_name.lower() in target_feature.lower():
                        adapted[target_feature] = value
                        break
        
        return adapted
    
    def adapt_actions(
        self,
        source_action: str,
        source_domain: DomainInfo,
        target_domain: DomainInfo,
    ) -> Optional[str]:
        """Adapt action using name matching."""
        # Direct match
        if source_action in target_domain.action_space:
            return source_action
        
        # Fuzzy match
        for target_action in target_domain.action_space:
            if source_action.lower() in target_action.lower():
                return target_action
            if target_action.lower() in source_action.lower():
                return target_action
        
        return None
    
    def compute_compatibility(
        self,
        source_domain: DomainInfo,
        target_domain: DomainInfo,
    ) -> float:
        """Compute compatibility based on feature/action overlap."""
        # Feature overlap
        source_features = set(f.lower() for f in source_domain.features)
        target_features = set(f.lower() for f in target_domain.features)
        
        if not source_features or not target_features:
            feature_overlap = 0.0
        else:
            common_features = source_features & target_features
            feature_overlap = len(common_features) / max(len(source_features), len(target_features))
        
        # Action overlap
        source_actions = set(a.lower() for a in source_domain.action_space)
        target_actions = set(a.lower() for a in target_domain.action_space)
        
        if not source_actions or not target_actions:
            action_overlap = 0.0
        else:
            common_actions = source_actions & target_actions
            action_overlap = len(common_actions) / max(len(source_actions), len(target_actions))
        
        # Weighted combination
        return 0.6 * feature_overlap + 0.4 * action_overlap


class KnowledgeDistiller:
    """Extracts transferable knowledge from learning experiences.
    
    Identifies patterns and knowledge that generalize across domains
    for efficient transfer learning.
    
    Attributes:
        min_confidence: Minimum confidence for transferable patterns
        max_patterns: Maximum patterns to retain per domain
        state_signature_length: Length of state signature for generalization
    """
    
    # Class constant for state signature truncation
    STATE_SIGNATURE_LENGTH = 8
    
    def __init__(
        self,
        min_confidence: float = 0.7,
        max_patterns: int = 100,
    ):
        """Initialize knowledge distiller.
        
        Args:
            min_confidence: Minimum pattern confidence
            max_patterns: Maximum patterns per domain
        """
        self.min_confidence = min_confidence
        self.max_patterns = max_patterns
        self.distilled_knowledge: Dict[str, List[Dict[str, Any]]] = {}
    
    def distill(
        self,
        q_table: Dict[str, Dict[str, float]],
        domain: DomainInfo,
    ) -> List[Dict[str, Any]]:
        """Distill transferable knowledge from Q-table.
        
        Args:
            q_table: Q-values from learning engine
            domain: Domain information
            
        Returns:
            List of transferable patterns
        """
        patterns = []
        
        for state, actions in q_table.items():
            if not actions:
                continue
            
            # Find best action
            best_action = max(actions, key=actions.get)
            best_q = actions[best_action]
            
            # Calculate confidence (normalized Q-value, clamped to [0, 1])
            all_q = list(actions.values())
            q_range = max(all_q) - min(all_q) if len(all_q) > 1 else 1.0
            raw_confidence = best_q / (q_range + 1e-6) if q_range > 0 else 0.5
            confidence = max(0.0, min(1.0, raw_confidence))  # Clamp to [0, 1]
            
            if confidence >= self.min_confidence:
                patterns.append({
                    'state_signature': state[:self.STATE_SIGNATURE_LENGTH],
                    'best_action': best_action,
                    'q_value': best_q,
                    'confidence': confidence,
                    'domain': domain.name,
                })
        
        # Keep top patterns by confidence
        patterns.sort(key=lambda p: p['confidence'], reverse=True)
        patterns = patterns[:self.max_patterns]
        
        self.distilled_knowledge[domain.name] = patterns
        return patterns
    
    def get_applicable_patterns(
        self,
        state_signature: str,
        domain_name: str,
    ) -> List[Dict[str, Any]]:
        """Get patterns applicable to a state.
        
        Args:
            state_signature: State signature prefix
            domain_name: Domain to search
            
        Returns:
            Applicable patterns
        """
        if domain_name not in self.distilled_knowledge:
            return []
        
        applicable = []
        sig_length = self.STATE_SIGNATURE_LENGTH
        for pattern in self.distilled_knowledge[domain_name]:
            if pattern['state_signature'] == state_signature[:sig_length]:
                applicable.append(pattern)
        
        return applicable


class TransferLearningEngine:
    """Main transfer learning engine.
    
    Coordinates knowledge transfer between domains using:
    - Domain adaptation for feature/action mapping
    - Knowledge distillation for pattern extraction
    - Progressive transfer for gradual adaptation
    
    Attributes:
        domains: Registered domains
        adapter: Domain adapter instance
        distiller: Knowledge distiller instance
        transfer_history: Record of transfer operations
    """
    
    def __init__(
        self,
        adapter: Optional[DomainAdapter] = None,
        distiller: Optional[KnowledgeDistiller] = None,
    ):
        """Initialize transfer learning engine.
        
        Args:
            adapter: Domain adapter (uses SimpleDomainAdapter if None)
            distiller: Knowledge distiller (creates new if None)
        """
        self.domains: Dict[str, DomainInfo] = {}
        self.adapter = adapter or SimpleDomainAdapter()
        self.distiller = distiller or KnowledgeDistiller()
        self.transfer_history: List[Dict[str, Any]] = []
    
    def register_domain(self, domain: DomainInfo) -> None:
        """Register a learning domain.
        
        Args:
            domain: Domain information
        """
        self.domains[domain.name] = domain
    
    def prepare_transfer(
        self,
        source_domain: str,
        target_domain: str,
        source_q_table: Dict[str, Dict[str, float]],
    ) -> TransferableKnowledge:
        """Prepare knowledge for transfer.
        
        Args:
            source_domain: Source domain name
            target_domain: Target domain name
            source_q_table: Q-table from source domain
            
        Returns:
            Transferable knowledge package
        """
        if source_domain not in self.domains:
            raise ValueError(f"Unknown source domain: {source_domain}")
        if target_domain not in self.domains:
            raise ValueError(f"Unknown target domain: {target_domain}")
        
        src_info = self.domains[source_domain]
        tgt_info = self.domains[target_domain]
        
        # Compute compatibility
        compatibility = self.adapter.compute_compatibility(src_info, tgt_info)
        
        # Distill knowledge
        patterns = self.distiller.distill(source_q_table, src_info)
        
        # Create transferable knowledge
        knowledge = TransferableKnowledge(
            source_domain=source_domain,
            target_domain=target_domain,
            patterns=patterns,
            compatibility_score=compatibility,
        )
        
        return knowledge
    
    def apply_transfer(
        self,
        knowledge: TransferableKnowledge,
        target_q_table: Dict[str, Dict[str, float]],
        transfer_rate: float = 0.5,
    ) -> Dict[str, Dict[str, float]]:
        """Apply transferred knowledge to target Q-table.
        
        Args:
            knowledge: Transferable knowledge package
            target_q_table: Target domain Q-table
            transfer_rate: How much to incorporate (0-1)
            
        Returns:
            Updated Q-table
        """
        if knowledge.target_domain not in self.domains:
            raise ValueError(f"Unknown target domain: {knowledge.target_domain}")
        
        tgt_info = self.domains[knowledge.target_domain]
        src_info = self.domains[knowledge.source_domain]
        
        # Adjust transfer rate by compatibility
        effective_rate = transfer_rate * knowledge.compatibility_score
        
        # Apply patterns
        for pattern in knowledge.patterns:
            # Adapt action
            adapted_action = self.adapter.adapt_actions(
                pattern['best_action'],
                src_info,
                tgt_info,
            )
            
            if adapted_action is None:
                continue
            
            state = pattern['state_signature']
            if state not in target_q_table:
                target_q_table[state] = {}
            
            # Blend Q-values
            current_q = target_q_table[state].get(adapted_action, 0.0)
            transferred_q = pattern['q_value'] * effective_rate
            target_q_table[state][adapted_action] = (
                (1 - effective_rate) * current_q + transferred_q
            )
        
        # Record transfer
        self.transfer_history.append({
            'source': knowledge.source_domain,
            'target': knowledge.target_domain,
            'patterns_transferred': len(knowledge.patterns),
            'compatibility': knowledge.compatibility_score,
            'effective_rate': effective_rate,
        })
        
        return target_q_table
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get transfer learning statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'domains_registered': len(self.domains),
            'transfers_completed': len(self.transfer_history),
            'distilled_domains': len(self.distiller.distilled_knowledge),
            'transfer_history': self.transfer_history[-10:],  # Last 10
        }


# =============================================================================
# META-LEARNING FRAMEWORK
# =============================================================================


@dataclass
class MetaLearningConfig:
    """Configuration for meta-learning optimization.
    
    Attributes:
        learning_rate: Meta-learning rate for hyperparameter updates
        adaptation_steps: Number of adaptation steps per domain
        meta_batch_size: Batch size for meta-training
        inner_lr: Inner loop learning rate
        outer_lr: Outer loop learning rate
    """
    learning_rate: float = 0.01
    adaptation_steps: int = 5
    meta_batch_size: int = 4
    inner_lr: float = 0.1
    outer_lr: float = 0.001


class MetaLearningFramework:
    """Meta-learning framework for cross-domain adaptation optimization.
    
    Implements MAML-inspired meta-learning for rapid domain adaptation.
    Optimizes initialization parameters for fast transfer.
    
    Attributes:
        config: Meta-learning configuration
        meta_parameters: Shared meta-learned parameters
        domain_specific_params: Per-domain adapted parameters
        adaptation_history: Record of adaptation outcomes
    """
    
    def __init__(self, config: Optional[MetaLearningConfig] = None):
        """Initialize meta-learning framework.
        
        Args:
            config: Meta-learning configuration
        """
        self.config = config or MetaLearningConfig()
        self.meta_parameters: Dict[str, float] = {
            'transfer_rate': 0.5,
            'confidence_threshold': 0.7,
            'exploration_bonus': 0.1,
            'adaptation_speed': 0.2,
        }
        self.domain_specific_params: Dict[str, Dict[str, float]] = {}
        self.adaptation_history: List[Dict[str, Any]] = []
        self.task_gradients: Dict[str, Dict[str, float]] = defaultdict(dict)
    
    def adapt_to_domain(
        self,
        domain_name: str,
        sample_experiences: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """Adapt meta-parameters to a specific domain.
        
        Performs rapid adaptation using a few sample experiences
        from the target domain.
        
        Args:
            domain_name: Target domain identifier
            sample_experiences: Sample experiences from domain
            
        Returns:
            Adapted parameters for this domain
        """
        # Start from meta-parameters
        adapted = dict(self.meta_parameters)
        
        if not sample_experiences:
            self.domain_specific_params[domain_name] = adapted
            return adapted
        
        # Compute adaptation direction from experiences
        for _ in range(self.config.adaptation_steps):
            # Calculate gradient estimate from experiences
            gradient = self._estimate_gradient(adapted, sample_experiences)
            
            # Update adapted parameters
            for param, grad in gradient.items():
                if param in adapted:
                    adapted[param] = adapted[param] + self.config.inner_lr * grad
                    # Clamp parameters to valid range
                    adapted[param] = max(0.01, min(1.0, adapted[param]))
        
        self.domain_specific_params[domain_name] = adapted
        
        self.adaptation_history.append({
            'domain': domain_name,
            'samples_used': len(sample_experiences),
            'adapted_params': dict(adapted),
            'steps': self.config.adaptation_steps,
        })
        
        return adapted
    
    def _estimate_gradient(
        self,
        params: Dict[str, float],
        experiences: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """Estimate gradient from experiences.
        
        Uses performance of experiences to estimate parameter gradients.
        
        Args:
            params: Current parameters
            experiences: Sample experiences
            
        Returns:
            Gradient estimates for each parameter
        """
        gradient = {}
        
        # Aggregate experience metrics
        avg_reward = sum(
            exp.get('reward', 0) for exp in experiences
        ) / len(experiences) if experiences else 0
        
        avg_confidence = sum(
            exp.get('confidence', 0.5) for exp in experiences
        ) / len(experiences) if experiences else 0.5
        
        # Gradient direction based on performance
        if avg_reward > 0:
            gradient['transfer_rate'] = 0.1 * avg_reward
            gradient['adaptation_speed'] = 0.05 * avg_reward
        else:
            gradient['transfer_rate'] = -0.05
            gradient['adaptation_speed'] = -0.025
        
        # Adjust confidence threshold based on observed confidence
        if avg_confidence > params.get('confidence_threshold', 0.7):
            gradient['confidence_threshold'] = 0.02
        else:
            gradient['confidence_threshold'] = -0.02
        
        gradient['exploration_bonus'] = -0.01 if avg_reward > 0.5 else 0.02
        
        return gradient
    
    def update_meta_parameters(
        self,
        domain_results: Dict[str, Dict[str, Any]],
    ) -> None:
        """Update meta-parameters based on multiple domain results.
        
        Implements outer loop of meta-learning using results from
        multiple domains.
        
        Args:
            domain_results: Results per domain (domain_name -> metrics)
        """
        if not domain_results:
            return
        
        # Aggregate gradients across domains
        meta_gradient: Dict[str, float] = defaultdict(float)
        
        for domain_name, results in domain_results.items():
            # Get domain-specific params if available
            domain_params = self.domain_specific_params.get(
                domain_name,
                self.meta_parameters,
            )
            
            # Calculate improvement direction
            success_rate = results.get('success_rate', 0.5)
            transfer_efficiency = results.get('transfer_efficiency', 0.5)
            
            for param in self.meta_parameters:
                if success_rate > 0.7:
                    meta_gradient[param] += (
                        domain_params.get(param, self.meta_parameters[param])
                        - self.meta_parameters[param]
                    ) * 0.1
                else:
                    meta_gradient[param] -= (
                        domain_params.get(param, self.meta_parameters[param])
                        - self.meta_parameters[param]
                    ) * 0.05
        
        # Apply outer loop update
        for param, grad in meta_gradient.items():
            if param in self.meta_parameters:
                self.meta_parameters[param] += self.config.outer_lr * grad
                # Clamp parameters
                self.meta_parameters[param] = max(
                    0.01,
                    min(1.0, self.meta_parameters[param])
                )
    
    def get_domain_parameters(self, domain_name: str) -> Dict[str, float]:
        """Get parameters for a specific domain.
        
        Returns domain-specific parameters if available,
        otherwise returns meta-parameters.
        
        Args:
            domain_name: Domain identifier
            
        Returns:
            Parameters for the domain
        """
        return self.domain_specific_params.get(domain_name, dict(self.meta_parameters))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get meta-learning statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'meta_parameters': dict(self.meta_parameters),
            'domains_adapted': len(self.domain_specific_params),
            'total_adaptations': len(self.adaptation_history),
            'recent_adaptations': self.adaptation_history[-5:],
        }


# =============================================================================
# DYNAMIC DOMAIN DETECTION
# =============================================================================


class DynamicDomainDetector:
    """Automatic domain detection from Q-table patterns.
    
    Analyzes Q-table structure and statistics to identify and
    classify learning domains without explicit labeling.
    
    Attributes:
        known_domains: Registered domain fingerprints
        detection_threshold: Similarity threshold for domain matching
        fingerprint_size: Size of domain fingerprints
    """
    
    # Length of state prefix for signature calculation
    STATE_PREFIX_LENGTH = 8
    
    def __init__(
        self,
        detection_threshold: float = 0.75,
        fingerprint_size: int = 32,
    ):
        """Initialize domain detector.
        
        Args:
            detection_threshold: Threshold for domain matching
            fingerprint_size: Size of fingerprint vectors
        """
        self.detection_threshold = detection_threshold
        self.fingerprint_size = fingerprint_size
        self.known_domains: Dict[str, Dict[str, Any]] = {}
        self.detection_history: List[Dict[str, Any]] = []
    
    def extract_fingerprint(
        self,
        q_table: Dict[str, Dict[str, float]],
    ) -> Dict[str, Any]:
        """Extract domain fingerprint from Q-table.
        
        Creates a characteristic fingerprint based on Q-table
        statistical properties.
        
        Args:
            q_table: Q-table to analyze
            
        Returns:
            Domain fingerprint dictionary
        """
        if not q_table:
            return {
                'state_count': 0,
                'action_count': 0,
                'q_mean': 0.0,
                'q_std': 0.0,
                'sparsity': 1.0,
                'state_signature': '',
                'action_signature': '',
            }
        
        # Collect statistics
        all_q_values = []
        all_actions: Set[str] = set()
        state_signatures = []
        
        for state, actions in q_table.items():
            all_q_values.extend(actions.values())
            all_actions.update(actions.keys())
            # Use first STATE_PREFIX_LENGTH chars of state as signature component
            prefix_len = self.STATE_PREFIX_LENGTH
            state_signatures.append(state[:prefix_len] if len(state) >= prefix_len else state)
        
        # Calculate statistics
        q_mean = sum(all_q_values) / len(all_q_values) if all_q_values else 0.0
        q_std = (
            (sum((q - q_mean) ** 2 for q in all_q_values) / len(all_q_values)) ** 0.5
            if all_q_values else 0.0
        )
        
        # Calculate sparsity (ratio of non-zero entries)
        # Handle empty action dictionaries safely
        action_counts = [len(a) for a in q_table.values()]
        max_action_count = max(action_counts) if action_counts else 0
        max_entries = len(q_table) * max_action_count if max_action_count > 0 else 1
        actual_entries = sum(action_counts)
        sparsity = 1.0 - (actual_entries / max_entries) if max_entries > 0 else 1.0
        
        # Create signatures
        sorted_states = sorted(state_signatures)[:self.fingerprint_size]
        state_signature = hashlib.sha256(
            '|'.join(sorted_states).encode()
        ).hexdigest()[:16]
        
        sorted_actions = sorted(all_actions)
        action_signature = hashlib.sha256(
            '|'.join(sorted_actions).encode()
        ).hexdigest()[:16]
        
        return {
            'state_count': len(q_table),
            'action_count': len(all_actions),
            'q_mean': q_mean,
            'q_std': q_std,
            'sparsity': sparsity,
            'state_signature': state_signature,
            'action_signature': action_signature,
        }
    
    def compute_similarity(
        self,
        fp1: Dict[str, Any],
        fp2: Dict[str, Any],
    ) -> float:
        """Compute similarity between two domain fingerprints.
        
        Args:
            fp1: First fingerprint
            fp2: Second fingerprint
            
        Returns:
            Similarity score [0, 1]
        """
        # Statistical similarity
        mean_diff = abs(fp1.get('q_mean', 0) - fp2.get('q_mean', 0))
        std_diff = abs(fp1.get('q_std', 0) - fp2.get('q_std', 0))
        sparsity_diff = abs(fp1.get('sparsity', 0) - fp2.get('sparsity', 0))
        
        # Normalize differences
        stat_similarity = 1.0 - min(1.0, (mean_diff + std_diff + sparsity_diff) / 3)
        
        # Action signature similarity
        action_match = 1.0 if fp1.get('action_signature') == fp2.get('action_signature') else 0.0
        
        # State signature similarity (partial matching)
        state_sim = 0.0
        s1 = fp1.get('state_signature', '')
        s2 = fp2.get('state_signature', '')
        if s1 and s2:
            common_chars = sum(1 for c1, c2 in zip(s1, s2) if c1 == c2)
            state_sim = common_chars / max(len(s1), len(s2))
        
        # Weighted combination
        return 0.4 * stat_similarity + 0.3 * action_match + 0.3 * state_sim
    
    def detect_domain(
        self,
        q_table: Dict[str, Dict[str, float]],
    ) -> Tuple[Optional[str], float]:
        """Detect domain from Q-table.
        
        Analyzes Q-table and matches against known domains.
        
        Args:
            q_table: Q-table to analyze
            
        Returns:
            Tuple of (domain_name or None, confidence score)
        """
        fingerprint = self.extract_fingerprint(q_table)
        
        best_match = None
        best_similarity = 0.0
        
        for domain_name, known_fp in self.known_domains.items():
            similarity = self.compute_similarity(fingerprint, known_fp)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = domain_name
        
        self.detection_history.append({
            'fingerprint': fingerprint,
            'matched_domain': best_match if best_similarity >= self.detection_threshold else None,
            'similarity': best_similarity,
            'threshold': self.detection_threshold,
        })
        
        if best_similarity >= self.detection_threshold:
            return best_match, best_similarity
        
        return None, best_similarity
    
    def register_domain(
        self,
        domain_name: str,
        q_table: Dict[str, Dict[str, float]],
    ) -> Dict[str, Any]:
        """Register a new domain from Q-table.
        
        Extracts fingerprint and registers as known domain.
        
        Args:
            domain_name: Name for the domain
            q_table: Representative Q-table
            
        Returns:
            Extracted fingerprint
        """
        fingerprint = self.extract_fingerprint(q_table)
        self.known_domains[domain_name] = fingerprint
        return fingerprint
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detection statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'known_domains': list(self.known_domains.keys()),
            'total_detections': len(self.detection_history),
            'recent_detections': self.detection_history[-5:],
        }


# =============================================================================
# CROSS-AGENT KNOWLEDGE SHARING
# =============================================================================


@dataclass
class KnowledgePackage:
    """Package for sharing knowledge between agents.
    
    Attributes:
        source_agent: Originating agent identifier
        target_agent: Destination agent identifier (None for broadcast)
        domain_info: Domain information
        knowledge_type: Type of knowledge (patterns, q_values, policy)
        payload: Actual knowledge data
        timestamp: Creation timestamp
        priority: Priority level for processing
        signature: Package signature for verification
    """
    source_agent: str
    target_agent: Optional[str]
    domain_info: DomainInfo
    knowledge_type: str
    payload: Dict[str, Any]
    timestamp: str = ""
    priority: int = 0
    signature: str = ""
    
    def __post_init__(self):
        """Initialize computed fields."""
        if not self.timestamp:
            from datetime import datetime
            self.timestamp = datetime.utcnow().isoformat()
        if not self.signature:
            self.signature = self._compute_signature()
    
    def _compute_signature(self) -> str:
        """Compute package signature for verification."""
        content = json.dumps({
            'source': self.source_agent,
            'target': self.target_agent,
            'domain': self.domain_info.name,
            'type': self.knowledge_type,
            'timestamp': self.timestamp,
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def verify(self) -> bool:
        """Verify package integrity."""
        expected = self._compute_signature()
        return self.signature == expected


class CrossAgentKnowledgeSharing:
    """Protocol for agent-to-agent knowledge transfer.
    
    Manages knowledge sharing between multiple cognitive agents,
    enabling distributed learning and collaboration.
    
    Attributes:
        agent_registry: Registered agents
        message_queue: Pending knowledge packages
        sharing_history: Record of sharing operations
        trust_scores: Trust scores between agents
    """
    
    def __init__(self, agent_id: str):
        """Initialize knowledge sharing protocol.
        
        Args:
            agent_id: This agent's identifier
        """
        self.agent_id = agent_id
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        self.message_queue: List[KnowledgePackage] = []
        self.sharing_history: List[Dict[str, Any]] = []
        self.trust_scores: Dict[str, float] = defaultdict(lambda: 0.5)
        self.received_packages: List[KnowledgePackage] = []
    
    def register_agent(
        self,
        agent_id: str,
        capabilities: List[str],
        domains: List[str],
    ) -> None:
        """Register an agent for knowledge sharing.
        
        Args:
            agent_id: Agent identifier
            capabilities: Agent capabilities
            domains: Domains the agent operates in
        """
        self.agent_registry[agent_id] = {
            'capabilities': capabilities,
            'domains': domains,
            'packages_sent': 0,
            'packages_received': 0,
            'last_interaction': None,
        }
    
    def create_package(
        self,
        target_agent: Optional[str],
        domain: DomainInfo,
        knowledge_type: str,
        payload: Dict[str, Any],
        priority: int = 0,
    ) -> KnowledgePackage:
        """Create a knowledge package for sharing.
        
        Args:
            target_agent: Target agent (None for broadcast)
            domain: Domain information
            knowledge_type: Type of knowledge
            payload: Knowledge data
            priority: Package priority
            
        Returns:
            Created knowledge package
        """
        return KnowledgePackage(
            source_agent=self.agent_id,
            target_agent=target_agent,
            domain_info=domain,
            knowledge_type=knowledge_type,
            payload=payload,
            priority=priority,
        )
    
    def send_package(self, package: KnowledgePackage) -> bool:
        """Queue a package for sending.
        
        Args:
            package: Knowledge package to send
            
        Returns:
            True if queued successfully
        """
        if not package.verify():
            return False
        
        self.message_queue.append(package)
        
        self.sharing_history.append({
            'action': 'send',
            'target': package.target_agent,
            'domain': package.domain_info.name,
            'type': package.knowledge_type,
            'timestamp': package.timestamp,
        })
        
        # Update registry
        if package.target_agent and package.target_agent in self.agent_registry:
            self.agent_registry[package.target_agent]['packages_sent'] = (
                self.agent_registry[package.target_agent].get('packages_sent', 0) + 1
            )
        
        return True
    
    def receive_package(self, package: KnowledgePackage) -> bool:
        """Process a received knowledge package.
        
        Args:
            package: Received package
            
        Returns:
            True if processed successfully
        """
        # Verify package integrity
        if not package.verify():
            return False
        
        # Check if package is for us
        if package.target_agent is not None and package.target_agent != self.agent_id:
            return False
        
        self.received_packages.append(package)
        
        # Update trust score based on successful receipt
        self.trust_scores[package.source_agent] = min(
            1.0,
            self.trust_scores[package.source_agent] + 0.01
        )
        
        self.sharing_history.append({
            'action': 'receive',
            'source': package.source_agent,
            'domain': package.domain_info.name,
            'type': package.knowledge_type,
            'timestamp': package.timestamp,
        })
        
        # Update registry
        if package.source_agent in self.agent_registry:
            self.agent_registry[package.source_agent]['packages_received'] = (
                self.agent_registry[package.source_agent].get('packages_received', 0) + 1
            )
            from datetime import datetime
            self.agent_registry[package.source_agent]['last_interaction'] = (
                datetime.utcnow().isoformat()
            )
        
        return True
    
    def get_pending_packages(
        self,
        target_agent: Optional[str] = None,
    ) -> List[KnowledgePackage]:
        """Get pending packages for a target agent.
        
        Args:
            target_agent: Filter by target (None for all)
            
        Returns:
            List of pending packages
        """
        if target_agent is None:
            return list(self.message_queue)
        
        return [
            p for p in self.message_queue
            if p.target_agent == target_agent or p.target_agent is None
        ]
    
    def get_received_by_type(
        self,
        knowledge_type: str,
    ) -> List[KnowledgePackage]:
        """Get received packages by knowledge type.
        
        Args:
            knowledge_type: Type to filter by
            
        Returns:
            Matching packages
        """
        return [
            p for p in self.received_packages
            if p.knowledge_type == knowledge_type
        ]
    
    def clear_processed(self, package: KnowledgePackage) -> None:
        """Mark a package as processed and remove from queue.
        
        Args:
            package: Package to remove
        """
        if package in self.message_queue:
            self.message_queue.remove(package)
        if package in self.received_packages:
            self.received_packages.remove(package)
    
    def get_compatible_agents(
        self,
        domain_name: str,
    ) -> List[str]:
        """Get agents compatible with a domain.
        
        Args:
            domain_name: Domain to match
            
        Returns:
            List of compatible agent IDs
        """
        compatible = []
        for agent_id, info in self.agent_registry.items():
            if agent_id == self.agent_id:
                continue
            if domain_name in info.get('domains', []):
                compatible.append(agent_id)
        return compatible
    
    def get_trust_score(self, agent_id: str) -> float:
        """Get trust score for an agent.
        
        Args:
            agent_id: Agent to check
            
        Returns:
            Trust score [0, 1]
        """
        return self.trust_scores.get(agent_id, 0.5)
    
    def update_trust(self, agent_id: str, success: bool) -> None:
        """Update trust score based on interaction outcome.
        
        Args:
            agent_id: Agent to update
            success: Whether interaction was successful
        """
        current = self.trust_scores[agent_id]
        if success:
            self.trust_scores[agent_id] = min(1.0, current + 0.05)
        else:
            self.trust_scores[agent_id] = max(0.0, current - 0.1)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get sharing statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'agent_id': self.agent_id,
            'registered_agents': len(self.agent_registry),
            'pending_packages': len(self.message_queue),
            'received_packages': len(self.received_packages),
            'total_interactions': len(self.sharing_history),
            'trust_scores': dict(self.trust_scores),
        }
