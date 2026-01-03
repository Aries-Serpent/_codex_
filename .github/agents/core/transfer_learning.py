"""
Transfer Learning Engine for Cognitive Brain.

Phase 8.4 Implementation:
- TransferLearningEngine: Cross-domain knowledge transfer
- DomainAdapter: Domain adaptation for different task types
- KnowledgeDistiller: Extract transferable knowledge

Status: Skeleton implementation - Full implementation pending
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from abc import ABC, abstractmethod


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
