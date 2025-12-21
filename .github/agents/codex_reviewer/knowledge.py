"""
Knowledge Gap Detection Components

This module contains logic for detecting areas where additional knowledge
would improve review quality.
"""

from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class KnowledgeGapDetector:
    """
    Detects areas where additional knowledge would improve review.
    
    Identifies:
    - Unfamiliar file types
    - Domain-specific terminology
    - External system references
    - Custom patterns and conventions
    """
    
    async def detect_gaps(self, context) -> List[str]:
        """
        Detect knowledge gaps based on context.
        
        Args:
            context: ReviewContext with PR information
            
        Returns:
            List of identified knowledge gaps
        """
        gaps = []
        
        # Check for unfamiliar file types
        unknown_extensions = self._find_unknown_extensions(context.files_changed)
        if unknown_extensions:
            gaps.append(f"Unfamiliar file types: {', '.join(unknown_extensions)}")
        
        # Check for domain-specific terms in PR description
        domain_terms = self._extract_domain_terms(context.description)
        if domain_terms:
            gaps.append(f"Domain-specific terminology: {', '.join(domain_terms[:3])}")
        
        # Check for references to external systems
        external_refs = self._find_external_references(context.diff)
        if external_refs:
            gaps.append(f"External system references: {', '.join(external_refs[:3])}")
        
        # Check for custom patterns
        if self._has_custom_patterns(context.files_changed):
            gaps.append("Repository-specific patterns or conventions")
        
        logger.info(f"Detected {len(gaps)} knowledge gaps")
        return gaps
    
    def _find_unknown_extensions(self, files: List[str]) -> List[str]:
        """Find file extensions that are uncommon."""
        # Known extensions
        known = {
            '.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h',
            '.yml', '.yaml', '.json', '.xml', '.md', '.txt', '.sh', '.bash',
            '.html', '.css', '.scss', '.less', '.sql', '.env', '.toml'
        }
        
        unknown = set()
        for file in files:
            ext = '.' + file.split('.')[-1] if '.' in file else ''
            if ext and ext not in known:
                unknown.add(ext)
        
        return list(unknown)
    
    def _extract_domain_terms(self, description: str) -> List[str]:
        """Extract domain-specific terms from description."""
        # TODO: Implement NLP-based domain term extraction
        # For now, look for capitalized words that might be domain terms
        import re
        words = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', description)
        return list(set(words))[:5]
    
    def _find_external_references(self, diff: str) -> List[str]:
        """Find references to external systems or services."""
        # Look for common external service patterns
        import re
        patterns = [
            r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            r'@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        ]
        
        refs = set()
        for pattern in patterns:
            matches = re.findall(pattern, diff)
            refs.update(matches)
        
        return list(refs)[:5]
    
    def _has_custom_patterns(self, files: List[str]) -> bool:
        """Check if files suggest custom patterns."""
        # Check for custom configuration or pattern files
        pattern_indicators = [
            'custom', 'config', 'pattern', 'convention',
            '.codex', '.config', 'settings'
        ]
        
        return any(
            any(indicator in file.lower() for indicator in pattern_indicators)
            for file in files
        )
