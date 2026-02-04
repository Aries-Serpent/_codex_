"""Content Diffing for Knowledge Crawler.

PS-06 Enhancement: Implements partial article change detection:
- Detect partial article changes for micro-updates
- Enable micro-updates for minor changes
- Semantic diffing for knowledge base content

This module extends the Knowledge Crawler Service with
intelligent content diffing to minimize unnecessary re-syncs.
"""

from __future__ import annotations

import difflib
import hashlib
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)
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


class ChangeType(Enum):
    """Type of content change detected."""
    
    NO_CHANGE = "no_change"
    MINOR = "minor"  # Typos, formatting
    MODERATE = "moderate"  # Paragraph changes
    MAJOR = "major"  # Structural changes
    COMPLETE = "complete"  # Complete rewrite


@dataclass
class DiffSegment:
    """A segment of text that was changed."""
    
    change_type: str  # "insert", "delete", "replace"
    old_content: str
    new_content: str
    line_start: int
    line_end: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "change_type": self.change_type,
            "old_content_preview": self.old_content[:100] + "..." if len(self.old_content) > 100 else self.old_content,
            "new_content_preview": self.new_content[:100] + "..." if len(self.new_content) > 100 else self.new_content,
            "line_start": self.line_start,
            "line_end": self.line_end,
        }


@dataclass
class ContentDiffResult:
    """Result of content comparison."""
    
    change_type: ChangeType
    change_ratio: float  # 0.0 = identical, 1.0 = completely different
    similarity_ratio: float  # 1.0 = identical, 0.0 = completely different
    old_hash: str
    new_hash: str
    segments: List[DiffSegment] = field(default_factory=list)
    old_line_count: int = 0
    new_line_count: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    lines_modified: int = 0
    
    @property
    def has_changes(self) -> bool:
        """Check if there are any changes between old and new content.
        
        Returns:
            True if changes were detected, False otherwise
        """
        return self.change_type != ChangeType.NO_CHANGE
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "change_type": self.change_type.value,
            "change_ratio": round(self.change_ratio, 4),
            "similarity_ratio": round(self.similarity_ratio, 4),
            "old_hash": self.old_hash,
            "new_hash": self.new_hash,
            "old_line_count": self.old_line_count,
            "new_line_count": self.new_line_count,
            "lines_added": self.lines_added,
            "lines_removed": self.lines_removed,
            "lines_modified": self.lines_modified,
            "segment_count": len(self.segments),
            "segments": [s.to_dict() for s in self.segments[:10]],  # Limit to first 10
        }
    
    def should_sync(self, min_change_ratio: float = 0.01) -> bool:
        """Determine if content should be synced based on change ratio.
        
        Args:
            min_change_ratio: Minimum change ratio to trigger sync (default 1%)
            
        Returns:
            True if content should be synced
        """
        return self.change_ratio >= min_change_ratio


class ContentDiffer:
    """Intelligent content differ for knowledge base articles.
    
    Features:
    - Line-by-line diff comparison
    - Change classification (minor/moderate/major)
    - HTML-aware diffing
    - Semantic similarity calculation
    """
    
    # Thresholds for change classification
    MINOR_THRESHOLD = 0.05  # < 5% change
    MODERATE_THRESHOLD = 0.25  # < 25% change
    MAJOR_THRESHOLD = 0.75  # < 75% change
    
    def xǁContentDifferǁ__init____mutmut_orig(
        self,
        min_change_ratio: float = 0.01,
        strip_html: bool = True,
        ignore_whitespace: bool = True,
    ):
        """Initialize the content differ.
        
        Args:
            min_change_ratio: Minimum change to report (default 1%)
            strip_html: Strip HTML tags before comparison
            ignore_whitespace: Normalize whitespace before comparison
        """
        self.min_change_ratio = min_change_ratio
        self.strip_html = strip_html
        self.ignore_whitespace = ignore_whitespace
    
    def xǁContentDifferǁ__init____mutmut_1(
        self,
        min_change_ratio: float = 1.01,
        strip_html: bool = True,
        ignore_whitespace: bool = True,
    ):
        """Initialize the content differ.
        
        Args:
            min_change_ratio: Minimum change to report (default 1%)
            strip_html: Strip HTML tags before comparison
            ignore_whitespace: Normalize whitespace before comparison
        """
        self.min_change_ratio = min_change_ratio
        self.strip_html = strip_html
        self.ignore_whitespace = ignore_whitespace
    
    def xǁContentDifferǁ__init____mutmut_2(
        self,
        min_change_ratio: float = 0.01,
        strip_html: bool = False,
        ignore_whitespace: bool = True,
    ):
        """Initialize the content differ.
        
        Args:
            min_change_ratio: Minimum change to report (default 1%)
            strip_html: Strip HTML tags before comparison
            ignore_whitespace: Normalize whitespace before comparison
        """
        self.min_change_ratio = min_change_ratio
        self.strip_html = strip_html
        self.ignore_whitespace = ignore_whitespace
    
    def xǁContentDifferǁ__init____mutmut_3(
        self,
        min_change_ratio: float = 0.01,
        strip_html: bool = True,
        ignore_whitespace: bool = False,
    ):
        """Initialize the content differ.
        
        Args:
            min_change_ratio: Minimum change to report (default 1%)
            strip_html: Strip HTML tags before comparison
            ignore_whitespace: Normalize whitespace before comparison
        """
        self.min_change_ratio = min_change_ratio
        self.strip_html = strip_html
        self.ignore_whitespace = ignore_whitespace
    
    def xǁContentDifferǁ__init____mutmut_4(
        self,
        min_change_ratio: float = 0.01,
        strip_html: bool = True,
        ignore_whitespace: bool = True,
    ):
        """Initialize the content differ.
        
        Args:
            min_change_ratio: Minimum change to report (default 1%)
            strip_html: Strip HTML tags before comparison
            ignore_whitespace: Normalize whitespace before comparison
        """
        self.min_change_ratio = None
        self.strip_html = strip_html
        self.ignore_whitespace = ignore_whitespace
    
    def xǁContentDifferǁ__init____mutmut_5(
        self,
        min_change_ratio: float = 0.01,
        strip_html: bool = True,
        ignore_whitespace: bool = True,
    ):
        """Initialize the content differ.
        
        Args:
            min_change_ratio: Minimum change to report (default 1%)
            strip_html: Strip HTML tags before comparison
            ignore_whitespace: Normalize whitespace before comparison
        """
        self.min_change_ratio = min_change_ratio
        self.strip_html = None
        self.ignore_whitespace = ignore_whitespace
    
    def xǁContentDifferǁ__init____mutmut_6(
        self,
        min_change_ratio: float = 0.01,
        strip_html: bool = True,
        ignore_whitespace: bool = True,
    ):
        """Initialize the content differ.
        
        Args:
            min_change_ratio: Minimum change to report (default 1%)
            strip_html: Strip HTML tags before comparison
            ignore_whitespace: Normalize whitespace before comparison
        """
        self.min_change_ratio = min_change_ratio
        self.strip_html = strip_html
        self.ignore_whitespace = None
    
    xǁContentDifferǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContentDifferǁ__init____mutmut_1': xǁContentDifferǁ__init____mutmut_1, 
        'xǁContentDifferǁ__init____mutmut_2': xǁContentDifferǁ__init____mutmut_2, 
        'xǁContentDifferǁ__init____mutmut_3': xǁContentDifferǁ__init____mutmut_3, 
        'xǁContentDifferǁ__init____mutmut_4': xǁContentDifferǁ__init____mutmut_4, 
        'xǁContentDifferǁ__init____mutmut_5': xǁContentDifferǁ__init____mutmut_5, 
        'xǁContentDifferǁ__init____mutmut_6': xǁContentDifferǁ__init____mutmut_6
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContentDifferǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁContentDifferǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁContentDifferǁ__init____mutmut_orig)
    xǁContentDifferǁ__init____mutmut_orig.__name__ = 'xǁContentDifferǁ__init__'
    
    @staticmethod
    def _hash_content(content: str) -> str:
        """Generate SHA-256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def xǁContentDifferǁ_normalize_content__mutmut_orig(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_1(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = None
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_2(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(None, ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_3(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', None, content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_4(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', None)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_5(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_6(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_7(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', )
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_8(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'XX<[^>]+>XX', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_9(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', 'XX XX', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_10(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = None
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_11(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(None, ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_12(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', None, content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_13(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', None)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_14(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_15(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_16(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', )
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_17(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'XX&[a-z]+;XX', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_18(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[A-Z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_19(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', 'XX XX', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_20(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = None
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_21(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(None, ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_22(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', None, content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_23(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', None)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_24(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_25(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_26(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', )
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_27(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'XX\s+XX', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_28(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', 'XX XX', content)
            content = '\n'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_29(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = None
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_30(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(None)
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_31(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = 'XX\nXX'.join(line.strip() for line in content.split('\n'))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_32(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split(None))
        
        return content.strip()
    
    def xǁContentDifferǁ_normalize_content__mutmut_33(self, content: str) -> str:
        """Normalize content for comparison.
        
        Args:
            content: Raw content string
            
        Returns:
            Normalized content
        """
        if self.strip_html:
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = re.sub(r'&[a-z]+;', ' ', content)
        
        if self.ignore_whitespace:
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = '\n'.join(line.strip() for line in content.split('XX\nXX'))
        
        return content.strip()
    
    xǁContentDifferǁ_normalize_content__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContentDifferǁ_normalize_content__mutmut_1': xǁContentDifferǁ_normalize_content__mutmut_1, 
        'xǁContentDifferǁ_normalize_content__mutmut_2': xǁContentDifferǁ_normalize_content__mutmut_2, 
        'xǁContentDifferǁ_normalize_content__mutmut_3': xǁContentDifferǁ_normalize_content__mutmut_3, 
        'xǁContentDifferǁ_normalize_content__mutmut_4': xǁContentDifferǁ_normalize_content__mutmut_4, 
        'xǁContentDifferǁ_normalize_content__mutmut_5': xǁContentDifferǁ_normalize_content__mutmut_5, 
        'xǁContentDifferǁ_normalize_content__mutmut_6': xǁContentDifferǁ_normalize_content__mutmut_6, 
        'xǁContentDifferǁ_normalize_content__mutmut_7': xǁContentDifferǁ_normalize_content__mutmut_7, 
        'xǁContentDifferǁ_normalize_content__mutmut_8': xǁContentDifferǁ_normalize_content__mutmut_8, 
        'xǁContentDifferǁ_normalize_content__mutmut_9': xǁContentDifferǁ_normalize_content__mutmut_9, 
        'xǁContentDifferǁ_normalize_content__mutmut_10': xǁContentDifferǁ_normalize_content__mutmut_10, 
        'xǁContentDifferǁ_normalize_content__mutmut_11': xǁContentDifferǁ_normalize_content__mutmut_11, 
        'xǁContentDifferǁ_normalize_content__mutmut_12': xǁContentDifferǁ_normalize_content__mutmut_12, 
        'xǁContentDifferǁ_normalize_content__mutmut_13': xǁContentDifferǁ_normalize_content__mutmut_13, 
        'xǁContentDifferǁ_normalize_content__mutmut_14': xǁContentDifferǁ_normalize_content__mutmut_14, 
        'xǁContentDifferǁ_normalize_content__mutmut_15': xǁContentDifferǁ_normalize_content__mutmut_15, 
        'xǁContentDifferǁ_normalize_content__mutmut_16': xǁContentDifferǁ_normalize_content__mutmut_16, 
        'xǁContentDifferǁ_normalize_content__mutmut_17': xǁContentDifferǁ_normalize_content__mutmut_17, 
        'xǁContentDifferǁ_normalize_content__mutmut_18': xǁContentDifferǁ_normalize_content__mutmut_18, 
        'xǁContentDifferǁ_normalize_content__mutmut_19': xǁContentDifferǁ_normalize_content__mutmut_19, 
        'xǁContentDifferǁ_normalize_content__mutmut_20': xǁContentDifferǁ_normalize_content__mutmut_20, 
        'xǁContentDifferǁ_normalize_content__mutmut_21': xǁContentDifferǁ_normalize_content__mutmut_21, 
        'xǁContentDifferǁ_normalize_content__mutmut_22': xǁContentDifferǁ_normalize_content__mutmut_22, 
        'xǁContentDifferǁ_normalize_content__mutmut_23': xǁContentDifferǁ_normalize_content__mutmut_23, 
        'xǁContentDifferǁ_normalize_content__mutmut_24': xǁContentDifferǁ_normalize_content__mutmut_24, 
        'xǁContentDifferǁ_normalize_content__mutmut_25': xǁContentDifferǁ_normalize_content__mutmut_25, 
        'xǁContentDifferǁ_normalize_content__mutmut_26': xǁContentDifferǁ_normalize_content__mutmut_26, 
        'xǁContentDifferǁ_normalize_content__mutmut_27': xǁContentDifferǁ_normalize_content__mutmut_27, 
        'xǁContentDifferǁ_normalize_content__mutmut_28': xǁContentDifferǁ_normalize_content__mutmut_28, 
        'xǁContentDifferǁ_normalize_content__mutmut_29': xǁContentDifferǁ_normalize_content__mutmut_29, 
        'xǁContentDifferǁ_normalize_content__mutmut_30': xǁContentDifferǁ_normalize_content__mutmut_30, 
        'xǁContentDifferǁ_normalize_content__mutmut_31': xǁContentDifferǁ_normalize_content__mutmut_31, 
        'xǁContentDifferǁ_normalize_content__mutmut_32': xǁContentDifferǁ_normalize_content__mutmut_32, 
        'xǁContentDifferǁ_normalize_content__mutmut_33': xǁContentDifferǁ_normalize_content__mutmut_33
    }
    
    def _normalize_content(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContentDifferǁ_normalize_content__mutmut_orig"), object.__getattribute__(self, "xǁContentDifferǁ_normalize_content__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _normalize_content.__signature__ = _mutmut_signature(xǁContentDifferǁ_normalize_content__mutmut_orig)
    xǁContentDifferǁ_normalize_content__mutmut_orig.__name__ = 'xǁContentDifferǁ_normalize_content'
    
    def xǁContentDifferǁ_classify_change__mutmut_orig(self, change_ratio: float) -> ChangeType:
        """Classify the change based on ratio.
        
        Args:
            change_ratio: Ratio of change (0.0 to 1.0)
            
        Returns:
            ChangeType classification
        """
        if change_ratio == 0:
            return ChangeType.NO_CHANGE
        elif change_ratio < self.MINOR_THRESHOLD:
            return ChangeType.MINOR
        elif change_ratio < self.MODERATE_THRESHOLD:
            return ChangeType.MODERATE
        elif change_ratio < self.MAJOR_THRESHOLD:
            return ChangeType.MAJOR
        else:
            return ChangeType.COMPLETE
    
    def xǁContentDifferǁ_classify_change__mutmut_1(self, change_ratio: float) -> ChangeType:
        """Classify the change based on ratio.
        
        Args:
            change_ratio: Ratio of change (0.0 to 1.0)
            
        Returns:
            ChangeType classification
        """
        if change_ratio != 0:
            return ChangeType.NO_CHANGE
        elif change_ratio < self.MINOR_THRESHOLD:
            return ChangeType.MINOR
        elif change_ratio < self.MODERATE_THRESHOLD:
            return ChangeType.MODERATE
        elif change_ratio < self.MAJOR_THRESHOLD:
            return ChangeType.MAJOR
        else:
            return ChangeType.COMPLETE
    
    def xǁContentDifferǁ_classify_change__mutmut_2(self, change_ratio: float) -> ChangeType:
        """Classify the change based on ratio.
        
        Args:
            change_ratio: Ratio of change (0.0 to 1.0)
            
        Returns:
            ChangeType classification
        """
        if change_ratio == 1:
            return ChangeType.NO_CHANGE
        elif change_ratio < self.MINOR_THRESHOLD:
            return ChangeType.MINOR
        elif change_ratio < self.MODERATE_THRESHOLD:
            return ChangeType.MODERATE
        elif change_ratio < self.MAJOR_THRESHOLD:
            return ChangeType.MAJOR
        else:
            return ChangeType.COMPLETE
    
    def xǁContentDifferǁ_classify_change__mutmut_3(self, change_ratio: float) -> ChangeType:
        """Classify the change based on ratio.
        
        Args:
            change_ratio: Ratio of change (0.0 to 1.0)
            
        Returns:
            ChangeType classification
        """
        if change_ratio == 0:
            return ChangeType.NO_CHANGE
        elif change_ratio <= self.MINOR_THRESHOLD:
            return ChangeType.MINOR
        elif change_ratio < self.MODERATE_THRESHOLD:
            return ChangeType.MODERATE
        elif change_ratio < self.MAJOR_THRESHOLD:
            return ChangeType.MAJOR
        else:
            return ChangeType.COMPLETE
    
    def xǁContentDifferǁ_classify_change__mutmut_4(self, change_ratio: float) -> ChangeType:
        """Classify the change based on ratio.
        
        Args:
            change_ratio: Ratio of change (0.0 to 1.0)
            
        Returns:
            ChangeType classification
        """
        if change_ratio == 0:
            return ChangeType.NO_CHANGE
        elif change_ratio < self.MINOR_THRESHOLD:
            return ChangeType.MINOR
        elif change_ratio <= self.MODERATE_THRESHOLD:
            return ChangeType.MODERATE
        elif change_ratio < self.MAJOR_THRESHOLD:
            return ChangeType.MAJOR
        else:
            return ChangeType.COMPLETE
    
    def xǁContentDifferǁ_classify_change__mutmut_5(self, change_ratio: float) -> ChangeType:
        """Classify the change based on ratio.
        
        Args:
            change_ratio: Ratio of change (0.0 to 1.0)
            
        Returns:
            ChangeType classification
        """
        if change_ratio == 0:
            return ChangeType.NO_CHANGE
        elif change_ratio < self.MINOR_THRESHOLD:
            return ChangeType.MINOR
        elif change_ratio < self.MODERATE_THRESHOLD:
            return ChangeType.MODERATE
        elif change_ratio <= self.MAJOR_THRESHOLD:
            return ChangeType.MAJOR
        else:
            return ChangeType.COMPLETE
    
    xǁContentDifferǁ_classify_change__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContentDifferǁ_classify_change__mutmut_1': xǁContentDifferǁ_classify_change__mutmut_1, 
        'xǁContentDifferǁ_classify_change__mutmut_2': xǁContentDifferǁ_classify_change__mutmut_2, 
        'xǁContentDifferǁ_classify_change__mutmut_3': xǁContentDifferǁ_classify_change__mutmut_3, 
        'xǁContentDifferǁ_classify_change__mutmut_4': xǁContentDifferǁ_classify_change__mutmut_4, 
        'xǁContentDifferǁ_classify_change__mutmut_5': xǁContentDifferǁ_classify_change__mutmut_5
    }
    
    def _classify_change(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContentDifferǁ_classify_change__mutmut_orig"), object.__getattribute__(self, "xǁContentDifferǁ_classify_change__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _classify_change.__signature__ = _mutmut_signature(xǁContentDifferǁ_classify_change__mutmut_orig)
    xǁContentDifferǁ_classify_change__mutmut_orig.__name__ = 'xǁContentDifferǁ_classify_change'
    
    def xǁContentDifferǁdiff__mutmut_orig(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_1(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = False,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_2(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = None
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_3(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(None)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_4(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = None
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_5(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(None)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_6(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = None
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_7(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = None
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_8(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = None
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_9(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(None)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_10(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = None
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_11(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(None)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_12(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash != new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_13(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=None,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_14(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=None,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_15(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=None,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_16(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=None,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_17(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=None,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_18(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_19(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_20(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_21(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_22(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_23(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=1.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_24(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=2.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_25(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = None
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_26(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = None
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_27(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = None
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_28(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, None, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_29(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, None)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_30(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_31(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_32(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, )
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_33(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = None
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_34(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = None
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_35(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 + similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_36(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 2.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_37(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = None
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_38(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = None
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_39(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(None)
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_40(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(None, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_41(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, None))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_42(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_43(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, ))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_44(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = None
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_45(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(None)
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_46(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(2 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_47(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith(None))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_48(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('XX+ XX'))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_49(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = None
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_50(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(None)
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_51(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(2 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_52(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith(None))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_53(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('XX- XX'))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_54(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = None
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_55(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(None)
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_56(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(2 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_57(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith(None))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_58(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('XX? XX'))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_59(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = None
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_60(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(None, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_61(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, None)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_62(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_63(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, )
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_64(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = None
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_65(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(None)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_66(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=None,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_67(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=None,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_68(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=None,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_69(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=None,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_70(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=None,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_71(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=None,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_72(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=None,
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_73(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=None,
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_74(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=None,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_75(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=None,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_76(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=None,
        )
    
    def xǁContentDifferǁdiff__mutmut_77(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_78(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_79(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_80(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_81(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_82(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_83(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_84(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_85(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_removed=lines_removed,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_86(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_modified=lines_modified,
        )
    
    def xǁContentDifferǁdiff__mutmut_87(
        self,
        old_content: str,
        new_content: str,
        normalize: bool = True,
    ) -> ContentDiffResult:
        """Compute diff between old and new content.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            normalize: Whether to normalize content before comparison
            
        Returns:
            ContentDiffResult with detailed diff information
        """
        # Normalize if requested
        if normalize:
            old_normalized = self._normalize_content(old_content)
            new_normalized = self._normalize_content(new_content)
        else:
            old_normalized = old_content
            new_normalized = new_content
        
        # Compute hashes
        old_hash = self._hash_content(old_content)
        new_hash = self._hash_content(new_content)
        
        # Quick check for identical content
        if old_hash == new_hash:
            return ContentDiffResult(
                change_type=ChangeType.NO_CHANGE,
                change_ratio=0.0,
                similarity_ratio=1.0,
                old_hash=old_hash,
                new_hash=new_hash,
            )
        
        # Split into lines for comparison
        old_lines = old_normalized.splitlines()
        new_lines = new_normalized.splitlines()
        
        # Use SequenceMatcher for similarity calculation
        matcher = difflib.SequenceMatcher(None, old_normalized, new_normalized)
        similarity_ratio = matcher.ratio()
        change_ratio = 1.0 - similarity_ratio
        
        # Count line changes
        differ = difflib.Differ()
        diff_lines = list(differ.compare(old_lines, new_lines))
        
        lines_added = sum(1 for line in diff_lines if line.startswith('+ '))
        lines_removed = sum(1 for line in diff_lines if line.startswith('- '))
        lines_modified = sum(1 for line in diff_lines if line.startswith('? '))
        
        # Extract diff segments
        segments = self._extract_segments(old_lines, new_lines)
        
        # Classify change type
        change_type = self._classify_change(change_ratio)
        
        return ContentDiffResult(
            change_type=change_type,
            change_ratio=change_ratio,
            similarity_ratio=similarity_ratio,
            old_hash=old_hash,
            new_hash=new_hash,
            segments=segments,
            old_line_count=len(old_lines),
            new_line_count=len(new_lines),
            lines_added=lines_added,
            lines_removed=lines_removed,
            )
    
    xǁContentDifferǁdiff__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContentDifferǁdiff__mutmut_1': xǁContentDifferǁdiff__mutmut_1, 
        'xǁContentDifferǁdiff__mutmut_2': xǁContentDifferǁdiff__mutmut_2, 
        'xǁContentDifferǁdiff__mutmut_3': xǁContentDifferǁdiff__mutmut_3, 
        'xǁContentDifferǁdiff__mutmut_4': xǁContentDifferǁdiff__mutmut_4, 
        'xǁContentDifferǁdiff__mutmut_5': xǁContentDifferǁdiff__mutmut_5, 
        'xǁContentDifferǁdiff__mutmut_6': xǁContentDifferǁdiff__mutmut_6, 
        'xǁContentDifferǁdiff__mutmut_7': xǁContentDifferǁdiff__mutmut_7, 
        'xǁContentDifferǁdiff__mutmut_8': xǁContentDifferǁdiff__mutmut_8, 
        'xǁContentDifferǁdiff__mutmut_9': xǁContentDifferǁdiff__mutmut_9, 
        'xǁContentDifferǁdiff__mutmut_10': xǁContentDifferǁdiff__mutmut_10, 
        'xǁContentDifferǁdiff__mutmut_11': xǁContentDifferǁdiff__mutmut_11, 
        'xǁContentDifferǁdiff__mutmut_12': xǁContentDifferǁdiff__mutmut_12, 
        'xǁContentDifferǁdiff__mutmut_13': xǁContentDifferǁdiff__mutmut_13, 
        'xǁContentDifferǁdiff__mutmut_14': xǁContentDifferǁdiff__mutmut_14, 
        'xǁContentDifferǁdiff__mutmut_15': xǁContentDifferǁdiff__mutmut_15, 
        'xǁContentDifferǁdiff__mutmut_16': xǁContentDifferǁdiff__mutmut_16, 
        'xǁContentDifferǁdiff__mutmut_17': xǁContentDifferǁdiff__mutmut_17, 
        'xǁContentDifferǁdiff__mutmut_18': xǁContentDifferǁdiff__mutmut_18, 
        'xǁContentDifferǁdiff__mutmut_19': xǁContentDifferǁdiff__mutmut_19, 
        'xǁContentDifferǁdiff__mutmut_20': xǁContentDifferǁdiff__mutmut_20, 
        'xǁContentDifferǁdiff__mutmut_21': xǁContentDifferǁdiff__mutmut_21, 
        'xǁContentDifferǁdiff__mutmut_22': xǁContentDifferǁdiff__mutmut_22, 
        'xǁContentDifferǁdiff__mutmut_23': xǁContentDifferǁdiff__mutmut_23, 
        'xǁContentDifferǁdiff__mutmut_24': xǁContentDifferǁdiff__mutmut_24, 
        'xǁContentDifferǁdiff__mutmut_25': xǁContentDifferǁdiff__mutmut_25, 
        'xǁContentDifferǁdiff__mutmut_26': xǁContentDifferǁdiff__mutmut_26, 
        'xǁContentDifferǁdiff__mutmut_27': xǁContentDifferǁdiff__mutmut_27, 
        'xǁContentDifferǁdiff__mutmut_28': xǁContentDifferǁdiff__mutmut_28, 
        'xǁContentDifferǁdiff__mutmut_29': xǁContentDifferǁdiff__mutmut_29, 
        'xǁContentDifferǁdiff__mutmut_30': xǁContentDifferǁdiff__mutmut_30, 
        'xǁContentDifferǁdiff__mutmut_31': xǁContentDifferǁdiff__mutmut_31, 
        'xǁContentDifferǁdiff__mutmut_32': xǁContentDifferǁdiff__mutmut_32, 
        'xǁContentDifferǁdiff__mutmut_33': xǁContentDifferǁdiff__mutmut_33, 
        'xǁContentDifferǁdiff__mutmut_34': xǁContentDifferǁdiff__mutmut_34, 
        'xǁContentDifferǁdiff__mutmut_35': xǁContentDifferǁdiff__mutmut_35, 
        'xǁContentDifferǁdiff__mutmut_36': xǁContentDifferǁdiff__mutmut_36, 
        'xǁContentDifferǁdiff__mutmut_37': xǁContentDifferǁdiff__mutmut_37, 
        'xǁContentDifferǁdiff__mutmut_38': xǁContentDifferǁdiff__mutmut_38, 
        'xǁContentDifferǁdiff__mutmut_39': xǁContentDifferǁdiff__mutmut_39, 
        'xǁContentDifferǁdiff__mutmut_40': xǁContentDifferǁdiff__mutmut_40, 
        'xǁContentDifferǁdiff__mutmut_41': xǁContentDifferǁdiff__mutmut_41, 
        'xǁContentDifferǁdiff__mutmut_42': xǁContentDifferǁdiff__mutmut_42, 
        'xǁContentDifferǁdiff__mutmut_43': xǁContentDifferǁdiff__mutmut_43, 
        'xǁContentDifferǁdiff__mutmut_44': xǁContentDifferǁdiff__mutmut_44, 
        'xǁContentDifferǁdiff__mutmut_45': xǁContentDifferǁdiff__mutmut_45, 
        'xǁContentDifferǁdiff__mutmut_46': xǁContentDifferǁdiff__mutmut_46, 
        'xǁContentDifferǁdiff__mutmut_47': xǁContentDifferǁdiff__mutmut_47, 
        'xǁContentDifferǁdiff__mutmut_48': xǁContentDifferǁdiff__mutmut_48, 
        'xǁContentDifferǁdiff__mutmut_49': xǁContentDifferǁdiff__mutmut_49, 
        'xǁContentDifferǁdiff__mutmut_50': xǁContentDifferǁdiff__mutmut_50, 
        'xǁContentDifferǁdiff__mutmut_51': xǁContentDifferǁdiff__mutmut_51, 
        'xǁContentDifferǁdiff__mutmut_52': xǁContentDifferǁdiff__mutmut_52, 
        'xǁContentDifferǁdiff__mutmut_53': xǁContentDifferǁdiff__mutmut_53, 
        'xǁContentDifferǁdiff__mutmut_54': xǁContentDifferǁdiff__mutmut_54, 
        'xǁContentDifferǁdiff__mutmut_55': xǁContentDifferǁdiff__mutmut_55, 
        'xǁContentDifferǁdiff__mutmut_56': xǁContentDifferǁdiff__mutmut_56, 
        'xǁContentDifferǁdiff__mutmut_57': xǁContentDifferǁdiff__mutmut_57, 
        'xǁContentDifferǁdiff__mutmut_58': xǁContentDifferǁdiff__mutmut_58, 
        'xǁContentDifferǁdiff__mutmut_59': xǁContentDifferǁdiff__mutmut_59, 
        'xǁContentDifferǁdiff__mutmut_60': xǁContentDifferǁdiff__mutmut_60, 
        'xǁContentDifferǁdiff__mutmut_61': xǁContentDifferǁdiff__mutmut_61, 
        'xǁContentDifferǁdiff__mutmut_62': xǁContentDifferǁdiff__mutmut_62, 
        'xǁContentDifferǁdiff__mutmut_63': xǁContentDifferǁdiff__mutmut_63, 
        'xǁContentDifferǁdiff__mutmut_64': xǁContentDifferǁdiff__mutmut_64, 
        'xǁContentDifferǁdiff__mutmut_65': xǁContentDifferǁdiff__mutmut_65, 
        'xǁContentDifferǁdiff__mutmut_66': xǁContentDifferǁdiff__mutmut_66, 
        'xǁContentDifferǁdiff__mutmut_67': xǁContentDifferǁdiff__mutmut_67, 
        'xǁContentDifferǁdiff__mutmut_68': xǁContentDifferǁdiff__mutmut_68, 
        'xǁContentDifferǁdiff__mutmut_69': xǁContentDifferǁdiff__mutmut_69, 
        'xǁContentDifferǁdiff__mutmut_70': xǁContentDifferǁdiff__mutmut_70, 
        'xǁContentDifferǁdiff__mutmut_71': xǁContentDifferǁdiff__mutmut_71, 
        'xǁContentDifferǁdiff__mutmut_72': xǁContentDifferǁdiff__mutmut_72, 
        'xǁContentDifferǁdiff__mutmut_73': xǁContentDifferǁdiff__mutmut_73, 
        'xǁContentDifferǁdiff__mutmut_74': xǁContentDifferǁdiff__mutmut_74, 
        'xǁContentDifferǁdiff__mutmut_75': xǁContentDifferǁdiff__mutmut_75, 
        'xǁContentDifferǁdiff__mutmut_76': xǁContentDifferǁdiff__mutmut_76, 
        'xǁContentDifferǁdiff__mutmut_77': xǁContentDifferǁdiff__mutmut_77, 
        'xǁContentDifferǁdiff__mutmut_78': xǁContentDifferǁdiff__mutmut_78, 
        'xǁContentDifferǁdiff__mutmut_79': xǁContentDifferǁdiff__mutmut_79, 
        'xǁContentDifferǁdiff__mutmut_80': xǁContentDifferǁdiff__mutmut_80, 
        'xǁContentDifferǁdiff__mutmut_81': xǁContentDifferǁdiff__mutmut_81, 
        'xǁContentDifferǁdiff__mutmut_82': xǁContentDifferǁdiff__mutmut_82, 
        'xǁContentDifferǁdiff__mutmut_83': xǁContentDifferǁdiff__mutmut_83, 
        'xǁContentDifferǁdiff__mutmut_84': xǁContentDifferǁdiff__mutmut_84, 
        'xǁContentDifferǁdiff__mutmut_85': xǁContentDifferǁdiff__mutmut_85, 
        'xǁContentDifferǁdiff__mutmut_86': xǁContentDifferǁdiff__mutmut_86, 
        'xǁContentDifferǁdiff__mutmut_87': xǁContentDifferǁdiff__mutmut_87
    }
    
    def diff(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContentDifferǁdiff__mutmut_orig"), object.__getattribute__(self, "xǁContentDifferǁdiff__mutmut_mutants"), args, kwargs, self)
        return result 
    
    diff.__signature__ = _mutmut_signature(xǁContentDifferǁdiff__mutmut_orig)
    xǁContentDifferǁdiff__mutmut_orig.__name__ = 'xǁContentDifferǁdiff'
    
    def xǁContentDifferǁ_extract_segments__mutmut_orig(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_1(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = None
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_2(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = None
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_3(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(None)
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_4(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            None,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_5(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            None,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_6(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm=None,
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_7(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_8(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_9(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_10(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='XXXX',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_11(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = ""
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_12(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = None
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_13(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 1
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_14(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith(None):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_15(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('XX@@XX'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_16(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = None
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_17(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(None, line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_18(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', None)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_19(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_20(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', )
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_21(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'XX@@ -(\d+)XX', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_22(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = None
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_23(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(None)
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_24(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(None))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_25(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(2))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_26(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') or not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_27(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith(None) and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_28(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('XX-XX') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_29(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_30(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith(None):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_31(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('XX---XX'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_32(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment or current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_33(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type != 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_34(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'XXdeleteXX':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_35(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'DELETE':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_36(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content = '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_37(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content -= '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_38(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' - line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_39(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += 'XX\nXX' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_40(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[2:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_41(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = None
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_42(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(None)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_43(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = None
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_44(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type=None,
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_45(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=None,
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_46(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content=None,
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_47(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=None,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_48(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=None,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_49(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_50(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_51(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_52(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_53(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_54(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='XXdeleteXX',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_55(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='DELETE',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_56(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[2:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_57(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='XXXX',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_58(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num = 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_59(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num -= 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_60(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 2
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_61(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') or not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_62(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith(None) and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_63(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('XX+XX') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_64(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_65(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith(None):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_66(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('XX+++XX'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_67(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment or current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_68(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type != 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_69(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'XXinsertXX':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_70(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'INSERT':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_71(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content = '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_72(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content -= '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_73(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' - line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_74(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += 'XX\nXX' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_75(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[2:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_76(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = None
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_77(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment or current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_78(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type != 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_79(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'XXdeleteXX':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_80(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'DELETE':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_81(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = None
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_82(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'XXreplaceXX'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_83(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'REPLACE'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_84(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = None
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_85(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[2:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_86(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(None)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_87(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = None
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_88(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type=None,
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_89(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content=None,
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_90(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=None,
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_91(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=None,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_92(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=None,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_93(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_94(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_95(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_96(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_97(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_98(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='XXinsertXX',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_99(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='INSERT',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_100(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='XXXX',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_101(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[2:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_102(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(None)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_103(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = ""
                line_num += 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_104(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num = 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_105(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num -= 1
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_106(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 2
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def xǁContentDifferǁ_extract_segments__mutmut_107(
        self,
        old_lines: List[str],
        new_lines: List[str],
    ) -> List[DiffSegment]:
        """Extract changed segments from line diff.
        
        Args:
            old_lines: Lines from old content
            new_lines: Lines from new content
            
        Returns:
            List of DiffSegment objects
        """
        segments = []
        
        # Use unified diff for segment extraction
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
        ))
        
        current_segment = None
        line_num = 0
        
        for line in diff:
            if line.startswith('@@'):
                # Parse line numbers from diff header
                match = re.match(r'@@ -(\d+)', line)
                if match:
                    line_num = int(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                if current_segment and current_segment.change_type == 'delete':
                    current_segment.old_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='delete',
                        old_content=line[1:],
                        new_content='',
                        line_start=line_num,
                        line_end=line_num,
                    )
                line_num += 1
            elif line.startswith('+') and not line.startswith('+++'):
                if current_segment and current_segment.change_type == 'insert':
                    current_segment.new_content += '\n' + line[1:]
                    current_segment.line_end = line_num
                elif current_segment and current_segment.change_type == 'delete':
                    # Convert delete to replace
                    current_segment.change_type = 'replace'
                    current_segment.new_content = line[1:]
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = DiffSegment(
                        change_type='insert',
                        old_content='',
                        new_content=line[1:],
                        line_start=line_num,
                        line_end=line_num,
                    )
            else:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = None
                line_num += 1
        
        if current_segment:
            segments.append(None)
        
        return segments
    
    xǁContentDifferǁ_extract_segments__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContentDifferǁ_extract_segments__mutmut_1': xǁContentDifferǁ_extract_segments__mutmut_1, 
        'xǁContentDifferǁ_extract_segments__mutmut_2': xǁContentDifferǁ_extract_segments__mutmut_2, 
        'xǁContentDifferǁ_extract_segments__mutmut_3': xǁContentDifferǁ_extract_segments__mutmut_3, 
        'xǁContentDifferǁ_extract_segments__mutmut_4': xǁContentDifferǁ_extract_segments__mutmut_4, 
        'xǁContentDifferǁ_extract_segments__mutmut_5': xǁContentDifferǁ_extract_segments__mutmut_5, 
        'xǁContentDifferǁ_extract_segments__mutmut_6': xǁContentDifferǁ_extract_segments__mutmut_6, 
        'xǁContentDifferǁ_extract_segments__mutmut_7': xǁContentDifferǁ_extract_segments__mutmut_7, 
        'xǁContentDifferǁ_extract_segments__mutmut_8': xǁContentDifferǁ_extract_segments__mutmut_8, 
        'xǁContentDifferǁ_extract_segments__mutmut_9': xǁContentDifferǁ_extract_segments__mutmut_9, 
        'xǁContentDifferǁ_extract_segments__mutmut_10': xǁContentDifferǁ_extract_segments__mutmut_10, 
        'xǁContentDifferǁ_extract_segments__mutmut_11': xǁContentDifferǁ_extract_segments__mutmut_11, 
        'xǁContentDifferǁ_extract_segments__mutmut_12': xǁContentDifferǁ_extract_segments__mutmut_12, 
        'xǁContentDifferǁ_extract_segments__mutmut_13': xǁContentDifferǁ_extract_segments__mutmut_13, 
        'xǁContentDifferǁ_extract_segments__mutmut_14': xǁContentDifferǁ_extract_segments__mutmut_14, 
        'xǁContentDifferǁ_extract_segments__mutmut_15': xǁContentDifferǁ_extract_segments__mutmut_15, 
        'xǁContentDifferǁ_extract_segments__mutmut_16': xǁContentDifferǁ_extract_segments__mutmut_16, 
        'xǁContentDifferǁ_extract_segments__mutmut_17': xǁContentDifferǁ_extract_segments__mutmut_17, 
        'xǁContentDifferǁ_extract_segments__mutmut_18': xǁContentDifferǁ_extract_segments__mutmut_18, 
        'xǁContentDifferǁ_extract_segments__mutmut_19': xǁContentDifferǁ_extract_segments__mutmut_19, 
        'xǁContentDifferǁ_extract_segments__mutmut_20': xǁContentDifferǁ_extract_segments__mutmut_20, 
        'xǁContentDifferǁ_extract_segments__mutmut_21': xǁContentDifferǁ_extract_segments__mutmut_21, 
        'xǁContentDifferǁ_extract_segments__mutmut_22': xǁContentDifferǁ_extract_segments__mutmut_22, 
        'xǁContentDifferǁ_extract_segments__mutmut_23': xǁContentDifferǁ_extract_segments__mutmut_23, 
        'xǁContentDifferǁ_extract_segments__mutmut_24': xǁContentDifferǁ_extract_segments__mutmut_24, 
        'xǁContentDifferǁ_extract_segments__mutmut_25': xǁContentDifferǁ_extract_segments__mutmut_25, 
        'xǁContentDifferǁ_extract_segments__mutmut_26': xǁContentDifferǁ_extract_segments__mutmut_26, 
        'xǁContentDifferǁ_extract_segments__mutmut_27': xǁContentDifferǁ_extract_segments__mutmut_27, 
        'xǁContentDifferǁ_extract_segments__mutmut_28': xǁContentDifferǁ_extract_segments__mutmut_28, 
        'xǁContentDifferǁ_extract_segments__mutmut_29': xǁContentDifferǁ_extract_segments__mutmut_29, 
        'xǁContentDifferǁ_extract_segments__mutmut_30': xǁContentDifferǁ_extract_segments__mutmut_30, 
        'xǁContentDifferǁ_extract_segments__mutmut_31': xǁContentDifferǁ_extract_segments__mutmut_31, 
        'xǁContentDifferǁ_extract_segments__mutmut_32': xǁContentDifferǁ_extract_segments__mutmut_32, 
        'xǁContentDifferǁ_extract_segments__mutmut_33': xǁContentDifferǁ_extract_segments__mutmut_33, 
        'xǁContentDifferǁ_extract_segments__mutmut_34': xǁContentDifferǁ_extract_segments__mutmut_34, 
        'xǁContentDifferǁ_extract_segments__mutmut_35': xǁContentDifferǁ_extract_segments__mutmut_35, 
        'xǁContentDifferǁ_extract_segments__mutmut_36': xǁContentDifferǁ_extract_segments__mutmut_36, 
        'xǁContentDifferǁ_extract_segments__mutmut_37': xǁContentDifferǁ_extract_segments__mutmut_37, 
        'xǁContentDifferǁ_extract_segments__mutmut_38': xǁContentDifferǁ_extract_segments__mutmut_38, 
        'xǁContentDifferǁ_extract_segments__mutmut_39': xǁContentDifferǁ_extract_segments__mutmut_39, 
        'xǁContentDifferǁ_extract_segments__mutmut_40': xǁContentDifferǁ_extract_segments__mutmut_40, 
        'xǁContentDifferǁ_extract_segments__mutmut_41': xǁContentDifferǁ_extract_segments__mutmut_41, 
        'xǁContentDifferǁ_extract_segments__mutmut_42': xǁContentDifferǁ_extract_segments__mutmut_42, 
        'xǁContentDifferǁ_extract_segments__mutmut_43': xǁContentDifferǁ_extract_segments__mutmut_43, 
        'xǁContentDifferǁ_extract_segments__mutmut_44': xǁContentDifferǁ_extract_segments__mutmut_44, 
        'xǁContentDifferǁ_extract_segments__mutmut_45': xǁContentDifferǁ_extract_segments__mutmut_45, 
        'xǁContentDifferǁ_extract_segments__mutmut_46': xǁContentDifferǁ_extract_segments__mutmut_46, 
        'xǁContentDifferǁ_extract_segments__mutmut_47': xǁContentDifferǁ_extract_segments__mutmut_47, 
        'xǁContentDifferǁ_extract_segments__mutmut_48': xǁContentDifferǁ_extract_segments__mutmut_48, 
        'xǁContentDifferǁ_extract_segments__mutmut_49': xǁContentDifferǁ_extract_segments__mutmut_49, 
        'xǁContentDifferǁ_extract_segments__mutmut_50': xǁContentDifferǁ_extract_segments__mutmut_50, 
        'xǁContentDifferǁ_extract_segments__mutmut_51': xǁContentDifferǁ_extract_segments__mutmut_51, 
        'xǁContentDifferǁ_extract_segments__mutmut_52': xǁContentDifferǁ_extract_segments__mutmut_52, 
        'xǁContentDifferǁ_extract_segments__mutmut_53': xǁContentDifferǁ_extract_segments__mutmut_53, 
        'xǁContentDifferǁ_extract_segments__mutmut_54': xǁContentDifferǁ_extract_segments__mutmut_54, 
        'xǁContentDifferǁ_extract_segments__mutmut_55': xǁContentDifferǁ_extract_segments__mutmut_55, 
        'xǁContentDifferǁ_extract_segments__mutmut_56': xǁContentDifferǁ_extract_segments__mutmut_56, 
        'xǁContentDifferǁ_extract_segments__mutmut_57': xǁContentDifferǁ_extract_segments__mutmut_57, 
        'xǁContentDifferǁ_extract_segments__mutmut_58': xǁContentDifferǁ_extract_segments__mutmut_58, 
        'xǁContentDifferǁ_extract_segments__mutmut_59': xǁContentDifferǁ_extract_segments__mutmut_59, 
        'xǁContentDifferǁ_extract_segments__mutmut_60': xǁContentDifferǁ_extract_segments__mutmut_60, 
        'xǁContentDifferǁ_extract_segments__mutmut_61': xǁContentDifferǁ_extract_segments__mutmut_61, 
        'xǁContentDifferǁ_extract_segments__mutmut_62': xǁContentDifferǁ_extract_segments__mutmut_62, 
        'xǁContentDifferǁ_extract_segments__mutmut_63': xǁContentDifferǁ_extract_segments__mutmut_63, 
        'xǁContentDifferǁ_extract_segments__mutmut_64': xǁContentDifferǁ_extract_segments__mutmut_64, 
        'xǁContentDifferǁ_extract_segments__mutmut_65': xǁContentDifferǁ_extract_segments__mutmut_65, 
        'xǁContentDifferǁ_extract_segments__mutmut_66': xǁContentDifferǁ_extract_segments__mutmut_66, 
        'xǁContentDifferǁ_extract_segments__mutmut_67': xǁContentDifferǁ_extract_segments__mutmut_67, 
        'xǁContentDifferǁ_extract_segments__mutmut_68': xǁContentDifferǁ_extract_segments__mutmut_68, 
        'xǁContentDifferǁ_extract_segments__mutmut_69': xǁContentDifferǁ_extract_segments__mutmut_69, 
        'xǁContentDifferǁ_extract_segments__mutmut_70': xǁContentDifferǁ_extract_segments__mutmut_70, 
        'xǁContentDifferǁ_extract_segments__mutmut_71': xǁContentDifferǁ_extract_segments__mutmut_71, 
        'xǁContentDifferǁ_extract_segments__mutmut_72': xǁContentDifferǁ_extract_segments__mutmut_72, 
        'xǁContentDifferǁ_extract_segments__mutmut_73': xǁContentDifferǁ_extract_segments__mutmut_73, 
        'xǁContentDifferǁ_extract_segments__mutmut_74': xǁContentDifferǁ_extract_segments__mutmut_74, 
        'xǁContentDifferǁ_extract_segments__mutmut_75': xǁContentDifferǁ_extract_segments__mutmut_75, 
        'xǁContentDifferǁ_extract_segments__mutmut_76': xǁContentDifferǁ_extract_segments__mutmut_76, 
        'xǁContentDifferǁ_extract_segments__mutmut_77': xǁContentDifferǁ_extract_segments__mutmut_77, 
        'xǁContentDifferǁ_extract_segments__mutmut_78': xǁContentDifferǁ_extract_segments__mutmut_78, 
        'xǁContentDifferǁ_extract_segments__mutmut_79': xǁContentDifferǁ_extract_segments__mutmut_79, 
        'xǁContentDifferǁ_extract_segments__mutmut_80': xǁContentDifferǁ_extract_segments__mutmut_80, 
        'xǁContentDifferǁ_extract_segments__mutmut_81': xǁContentDifferǁ_extract_segments__mutmut_81, 
        'xǁContentDifferǁ_extract_segments__mutmut_82': xǁContentDifferǁ_extract_segments__mutmut_82, 
        'xǁContentDifferǁ_extract_segments__mutmut_83': xǁContentDifferǁ_extract_segments__mutmut_83, 
        'xǁContentDifferǁ_extract_segments__mutmut_84': xǁContentDifferǁ_extract_segments__mutmut_84, 
        'xǁContentDifferǁ_extract_segments__mutmut_85': xǁContentDifferǁ_extract_segments__mutmut_85, 
        'xǁContentDifferǁ_extract_segments__mutmut_86': xǁContentDifferǁ_extract_segments__mutmut_86, 
        'xǁContentDifferǁ_extract_segments__mutmut_87': xǁContentDifferǁ_extract_segments__mutmut_87, 
        'xǁContentDifferǁ_extract_segments__mutmut_88': xǁContentDifferǁ_extract_segments__mutmut_88, 
        'xǁContentDifferǁ_extract_segments__mutmut_89': xǁContentDifferǁ_extract_segments__mutmut_89, 
        'xǁContentDifferǁ_extract_segments__mutmut_90': xǁContentDifferǁ_extract_segments__mutmut_90, 
        'xǁContentDifferǁ_extract_segments__mutmut_91': xǁContentDifferǁ_extract_segments__mutmut_91, 
        'xǁContentDifferǁ_extract_segments__mutmut_92': xǁContentDifferǁ_extract_segments__mutmut_92, 
        'xǁContentDifferǁ_extract_segments__mutmut_93': xǁContentDifferǁ_extract_segments__mutmut_93, 
        'xǁContentDifferǁ_extract_segments__mutmut_94': xǁContentDifferǁ_extract_segments__mutmut_94, 
        'xǁContentDifferǁ_extract_segments__mutmut_95': xǁContentDifferǁ_extract_segments__mutmut_95, 
        'xǁContentDifferǁ_extract_segments__mutmut_96': xǁContentDifferǁ_extract_segments__mutmut_96, 
        'xǁContentDifferǁ_extract_segments__mutmut_97': xǁContentDifferǁ_extract_segments__mutmut_97, 
        'xǁContentDifferǁ_extract_segments__mutmut_98': xǁContentDifferǁ_extract_segments__mutmut_98, 
        'xǁContentDifferǁ_extract_segments__mutmut_99': xǁContentDifferǁ_extract_segments__mutmut_99, 
        'xǁContentDifferǁ_extract_segments__mutmut_100': xǁContentDifferǁ_extract_segments__mutmut_100, 
        'xǁContentDifferǁ_extract_segments__mutmut_101': xǁContentDifferǁ_extract_segments__mutmut_101, 
        'xǁContentDifferǁ_extract_segments__mutmut_102': xǁContentDifferǁ_extract_segments__mutmut_102, 
        'xǁContentDifferǁ_extract_segments__mutmut_103': xǁContentDifferǁ_extract_segments__mutmut_103, 
        'xǁContentDifferǁ_extract_segments__mutmut_104': xǁContentDifferǁ_extract_segments__mutmut_104, 
        'xǁContentDifferǁ_extract_segments__mutmut_105': xǁContentDifferǁ_extract_segments__mutmut_105, 
        'xǁContentDifferǁ_extract_segments__mutmut_106': xǁContentDifferǁ_extract_segments__mutmut_106, 
        'xǁContentDifferǁ_extract_segments__mutmut_107': xǁContentDifferǁ_extract_segments__mutmut_107
    }
    
    def _extract_segments(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContentDifferǁ_extract_segments__mutmut_orig"), object.__getattribute__(self, "xǁContentDifferǁ_extract_segments__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _extract_segments.__signature__ = _mutmut_signature(xǁContentDifferǁ_extract_segments__mutmut_orig)
    xǁContentDifferǁ_extract_segments__mutmut_orig.__name__ = 'xǁContentDifferǁ_extract_segments'
    
    def xǁContentDifferǁshould_resync__mutmut_orig(
        self,
        old_content: str,
        new_content: str,
    ) -> Tuple[bool, ChangeType, float]:
        """Quick check if content should be resynced.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Tuple of (should_resync, change_type, change_ratio)
        """
        result = self.diff(old_content, new_content)
        return (
            result.should_sync(self.min_change_ratio),
            result.change_type,
            result.change_ratio,
        )
    
    def xǁContentDifferǁshould_resync__mutmut_1(
        self,
        old_content: str,
        new_content: str,
    ) -> Tuple[bool, ChangeType, float]:
        """Quick check if content should be resynced.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Tuple of (should_resync, change_type, change_ratio)
        """
        result = None
        return (
            result.should_sync(self.min_change_ratio),
            result.change_type,
            result.change_ratio,
        )
    
    def xǁContentDifferǁshould_resync__mutmut_2(
        self,
        old_content: str,
        new_content: str,
    ) -> Tuple[bool, ChangeType, float]:
        """Quick check if content should be resynced.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Tuple of (should_resync, change_type, change_ratio)
        """
        result = self.diff(None, new_content)
        return (
            result.should_sync(self.min_change_ratio),
            result.change_type,
            result.change_ratio,
        )
    
    def xǁContentDifferǁshould_resync__mutmut_3(
        self,
        old_content: str,
        new_content: str,
    ) -> Tuple[bool, ChangeType, float]:
        """Quick check if content should be resynced.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Tuple of (should_resync, change_type, change_ratio)
        """
        result = self.diff(old_content, None)
        return (
            result.should_sync(self.min_change_ratio),
            result.change_type,
            result.change_ratio,
        )
    
    def xǁContentDifferǁshould_resync__mutmut_4(
        self,
        old_content: str,
        new_content: str,
    ) -> Tuple[bool, ChangeType, float]:
        """Quick check if content should be resynced.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Tuple of (should_resync, change_type, change_ratio)
        """
        result = self.diff(new_content)
        return (
            result.should_sync(self.min_change_ratio),
            result.change_type,
            result.change_ratio,
        )
    
    def xǁContentDifferǁshould_resync__mutmut_5(
        self,
        old_content: str,
        new_content: str,
    ) -> Tuple[bool, ChangeType, float]:
        """Quick check if content should be resynced.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Tuple of (should_resync, change_type, change_ratio)
        """
        result = self.diff(old_content, )
        return (
            result.should_sync(self.min_change_ratio),
            result.change_type,
            result.change_ratio,
        )
    
    def xǁContentDifferǁshould_resync__mutmut_6(
        self,
        old_content: str,
        new_content: str,
    ) -> Tuple[bool, ChangeType, float]:
        """Quick check if content should be resynced.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Tuple of (should_resync, change_type, change_ratio)
        """
        result = self.diff(old_content, new_content)
        return (
            result.should_sync(None),
            result.change_type,
            result.change_ratio,
        )
    
    xǁContentDifferǁshould_resync__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁContentDifferǁshould_resync__mutmut_1': xǁContentDifferǁshould_resync__mutmut_1, 
        'xǁContentDifferǁshould_resync__mutmut_2': xǁContentDifferǁshould_resync__mutmut_2, 
        'xǁContentDifferǁshould_resync__mutmut_3': xǁContentDifferǁshould_resync__mutmut_3, 
        'xǁContentDifferǁshould_resync__mutmut_4': xǁContentDifferǁshould_resync__mutmut_4, 
        'xǁContentDifferǁshould_resync__mutmut_5': xǁContentDifferǁshould_resync__mutmut_5, 
        'xǁContentDifferǁshould_resync__mutmut_6': xǁContentDifferǁshould_resync__mutmut_6
    }
    
    def should_resync(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁContentDifferǁshould_resync__mutmut_orig"), object.__getattribute__(self, "xǁContentDifferǁshould_resync__mutmut_mutants"), args, kwargs, self)
        return result 
    
    should_resync.__signature__ = _mutmut_signature(xǁContentDifferǁshould_resync__mutmut_orig)
    xǁContentDifferǁshould_resync__mutmut_orig.__name__ = 'xǁContentDifferǁshould_resync'


class IncrementalSyncDecider:
    """Decision logic for incremental sync based on content diffs.
    
    Uses content diffing to determine the optimal sync strategy:
    - Skip: No changes or changes below threshold
    - Micro-update: Minor changes, update only changed sections
    - Full update: Major changes, re-sync entire article
    """
    
    def xǁIncrementalSyncDeciderǁ__init____mutmut_orig(
        self,
        differ: Optional[ContentDiffer] = None,
        micro_update_threshold: float = 0.10,  # <10% change
        full_update_threshold: float = 0.50,  # >50% change
    ):
        """Initialize the sync decider.
        
        Args:
            differ: ContentDiffer instance
            micro_update_threshold: Max change for micro-update
            full_update_threshold: Min change for full update
        """
        self.differ = differ or ContentDiffer()
        self.micro_update_threshold = micro_update_threshold
        self.full_update_threshold = full_update_threshold
    
    def xǁIncrementalSyncDeciderǁ__init____mutmut_1(
        self,
        differ: Optional[ContentDiffer] = None,
        micro_update_threshold: float = 1.1,  # <10% change
        full_update_threshold: float = 0.50,  # >50% change
    ):
        """Initialize the sync decider.
        
        Args:
            differ: ContentDiffer instance
            micro_update_threshold: Max change for micro-update
            full_update_threshold: Min change for full update
        """
        self.differ = differ or ContentDiffer()
        self.micro_update_threshold = micro_update_threshold
        self.full_update_threshold = full_update_threshold
    
    def xǁIncrementalSyncDeciderǁ__init____mutmut_2(
        self,
        differ: Optional[ContentDiffer] = None,
        micro_update_threshold: float = 0.10,  # <10% change
        full_update_threshold: float = 1.5,  # >50% change
    ):
        """Initialize the sync decider.
        
        Args:
            differ: ContentDiffer instance
            micro_update_threshold: Max change for micro-update
            full_update_threshold: Min change for full update
        """
        self.differ = differ or ContentDiffer()
        self.micro_update_threshold = micro_update_threshold
        self.full_update_threshold = full_update_threshold
    
    def xǁIncrementalSyncDeciderǁ__init____mutmut_3(
        self,
        differ: Optional[ContentDiffer] = None,
        micro_update_threshold: float = 0.10,  # <10% change
        full_update_threshold: float = 0.50,  # >50% change
    ):
        """Initialize the sync decider.
        
        Args:
            differ: ContentDiffer instance
            micro_update_threshold: Max change for micro-update
            full_update_threshold: Min change for full update
        """
        self.differ = None
        self.micro_update_threshold = micro_update_threshold
        self.full_update_threshold = full_update_threshold
    
    def xǁIncrementalSyncDeciderǁ__init____mutmut_4(
        self,
        differ: Optional[ContentDiffer] = None,
        micro_update_threshold: float = 0.10,  # <10% change
        full_update_threshold: float = 0.50,  # >50% change
    ):
        """Initialize the sync decider.
        
        Args:
            differ: ContentDiffer instance
            micro_update_threshold: Max change for micro-update
            full_update_threshold: Min change for full update
        """
        self.differ = differ and ContentDiffer()
        self.micro_update_threshold = micro_update_threshold
        self.full_update_threshold = full_update_threshold
    
    def xǁIncrementalSyncDeciderǁ__init____mutmut_5(
        self,
        differ: Optional[ContentDiffer] = None,
        micro_update_threshold: float = 0.10,  # <10% change
        full_update_threshold: float = 0.50,  # >50% change
    ):
        """Initialize the sync decider.
        
        Args:
            differ: ContentDiffer instance
            micro_update_threshold: Max change for micro-update
            full_update_threshold: Min change for full update
        """
        self.differ = differ or ContentDiffer()
        self.micro_update_threshold = None
        self.full_update_threshold = full_update_threshold
    
    def xǁIncrementalSyncDeciderǁ__init____mutmut_6(
        self,
        differ: Optional[ContentDiffer] = None,
        micro_update_threshold: float = 0.10,  # <10% change
        full_update_threshold: float = 0.50,  # >50% change
    ):
        """Initialize the sync decider.
        
        Args:
            differ: ContentDiffer instance
            micro_update_threshold: Max change for micro-update
            full_update_threshold: Min change for full update
        """
        self.differ = differ or ContentDiffer()
        self.micro_update_threshold = micro_update_threshold
        self.full_update_threshold = None
    
    xǁIncrementalSyncDeciderǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIncrementalSyncDeciderǁ__init____mutmut_1': xǁIncrementalSyncDeciderǁ__init____mutmut_1, 
        'xǁIncrementalSyncDeciderǁ__init____mutmut_2': xǁIncrementalSyncDeciderǁ__init____mutmut_2, 
        'xǁIncrementalSyncDeciderǁ__init____mutmut_3': xǁIncrementalSyncDeciderǁ__init____mutmut_3, 
        'xǁIncrementalSyncDeciderǁ__init____mutmut_4': xǁIncrementalSyncDeciderǁ__init____mutmut_4, 
        'xǁIncrementalSyncDeciderǁ__init____mutmut_5': xǁIncrementalSyncDeciderǁ__init____mutmut_5, 
        'xǁIncrementalSyncDeciderǁ__init____mutmut_6': xǁIncrementalSyncDeciderǁ__init____mutmut_6
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIncrementalSyncDeciderǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁIncrementalSyncDeciderǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁIncrementalSyncDeciderǁ__init____mutmut_orig)
    xǁIncrementalSyncDeciderǁ__init____mutmut_orig.__name__ = 'xǁIncrementalSyncDeciderǁ__init__'
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_orig(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_1(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = None
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_2(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(None, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_3(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, None)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_4(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_5(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, )
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_6(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type != ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_7(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "XXactionXX": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_8(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "ACTION": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_9(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "XXskipXX",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_10(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "SKIP",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_11(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "XXreasonXX": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_12(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "REASON": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_13(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "XXNo changes detectedXX",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_14(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "no changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_15(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "NO CHANGES DETECTED",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_16(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "XXchange_ratioXX": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_17(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "CHANGE_RATIO": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_18(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 1.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_19(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "XXdiffXX": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_20(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "DIFF": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_21(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio <= self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_22(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "XXactionXX": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_23(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "ACTION": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_24(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "XXmicro_updateXX",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_25(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "MICRO_UPDATE",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_26(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "XXreasonXX": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_27(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "REASON": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_28(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "XXchange_ratioXX": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_29(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "CHANGE_RATIO": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_30(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "XXsegments_to_updateXX": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_31(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "SEGMENTS_TO_UPDATE": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_32(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "XXdiffXX": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_33(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "DIFF": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_34(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio > self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_35(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "XXactionXX": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_36(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "ACTION": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_37(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "XXfull_updateXX",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_38(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "FULL_UPDATE",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_39(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "XXreasonXX": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_40(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "REASON": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_41(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "XXchange_ratioXX": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_42(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "CHANGE_RATIO": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_43(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "XXdiffXX": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_44(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "DIFF": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_45(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "XXactionXX": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_46(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "ACTION": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_47(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "XXfull_updateXX",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_48(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "FULL_UPDATE",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_49(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "XXreasonXX": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_50(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "REASON": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_51(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "XXchange_ratioXX": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_52(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "CHANGE_RATIO": diff_result.change_ratio,
            "diff": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_53(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "XXdiffXX": diff_result.to_dict(),
        }
    
    def xǁIncrementalSyncDeciderǁdecide__mutmut_54(
        self,
        old_content: str,
        new_content: str,
    ) -> Dict[str, Any]:
        """Decide sync strategy for content change.
        
        Args:
            old_content: Previous content version
            new_content: New content version
            
        Returns:
            Decision dictionary with strategy and metadata
        """
        diff_result = self.differ.diff(old_content, new_content)
        
        if diff_result.change_type == ChangeType.NO_CHANGE:
            return {
                "action": "skip",
                "reason": "No changes detected",
                "change_ratio": 0.0,
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio < self.micro_update_threshold:
            return {
                "action": "micro_update",
                "reason": f"Minor change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "segments_to_update": len(diff_result.segments),
                "diff": diff_result.to_dict(),
            }
        
        if diff_result.change_ratio >= self.full_update_threshold:
            return {
                "action": "full_update",
                "reason": f"Major change ({diff_result.change_ratio:.1%})",
                "change_ratio": diff_result.change_ratio,
                "diff": diff_result.to_dict(),
            }
        
        # Moderate change - use full update for safety
        return {
            "action": "full_update",
            "reason": f"Moderate change ({diff_result.change_ratio:.1%})",
            "change_ratio": diff_result.change_ratio,
            "DIFF": diff_result.to_dict(),
        }
    
    xǁIncrementalSyncDeciderǁdecide__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁIncrementalSyncDeciderǁdecide__mutmut_1': xǁIncrementalSyncDeciderǁdecide__mutmut_1, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_2': xǁIncrementalSyncDeciderǁdecide__mutmut_2, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_3': xǁIncrementalSyncDeciderǁdecide__mutmut_3, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_4': xǁIncrementalSyncDeciderǁdecide__mutmut_4, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_5': xǁIncrementalSyncDeciderǁdecide__mutmut_5, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_6': xǁIncrementalSyncDeciderǁdecide__mutmut_6, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_7': xǁIncrementalSyncDeciderǁdecide__mutmut_7, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_8': xǁIncrementalSyncDeciderǁdecide__mutmut_8, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_9': xǁIncrementalSyncDeciderǁdecide__mutmut_9, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_10': xǁIncrementalSyncDeciderǁdecide__mutmut_10, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_11': xǁIncrementalSyncDeciderǁdecide__mutmut_11, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_12': xǁIncrementalSyncDeciderǁdecide__mutmut_12, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_13': xǁIncrementalSyncDeciderǁdecide__mutmut_13, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_14': xǁIncrementalSyncDeciderǁdecide__mutmut_14, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_15': xǁIncrementalSyncDeciderǁdecide__mutmut_15, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_16': xǁIncrementalSyncDeciderǁdecide__mutmut_16, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_17': xǁIncrementalSyncDeciderǁdecide__mutmut_17, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_18': xǁIncrementalSyncDeciderǁdecide__mutmut_18, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_19': xǁIncrementalSyncDeciderǁdecide__mutmut_19, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_20': xǁIncrementalSyncDeciderǁdecide__mutmut_20, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_21': xǁIncrementalSyncDeciderǁdecide__mutmut_21, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_22': xǁIncrementalSyncDeciderǁdecide__mutmut_22, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_23': xǁIncrementalSyncDeciderǁdecide__mutmut_23, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_24': xǁIncrementalSyncDeciderǁdecide__mutmut_24, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_25': xǁIncrementalSyncDeciderǁdecide__mutmut_25, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_26': xǁIncrementalSyncDeciderǁdecide__mutmut_26, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_27': xǁIncrementalSyncDeciderǁdecide__mutmut_27, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_28': xǁIncrementalSyncDeciderǁdecide__mutmut_28, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_29': xǁIncrementalSyncDeciderǁdecide__mutmut_29, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_30': xǁIncrementalSyncDeciderǁdecide__mutmut_30, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_31': xǁIncrementalSyncDeciderǁdecide__mutmut_31, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_32': xǁIncrementalSyncDeciderǁdecide__mutmut_32, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_33': xǁIncrementalSyncDeciderǁdecide__mutmut_33, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_34': xǁIncrementalSyncDeciderǁdecide__mutmut_34, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_35': xǁIncrementalSyncDeciderǁdecide__mutmut_35, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_36': xǁIncrementalSyncDeciderǁdecide__mutmut_36, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_37': xǁIncrementalSyncDeciderǁdecide__mutmut_37, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_38': xǁIncrementalSyncDeciderǁdecide__mutmut_38, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_39': xǁIncrementalSyncDeciderǁdecide__mutmut_39, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_40': xǁIncrementalSyncDeciderǁdecide__mutmut_40, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_41': xǁIncrementalSyncDeciderǁdecide__mutmut_41, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_42': xǁIncrementalSyncDeciderǁdecide__mutmut_42, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_43': xǁIncrementalSyncDeciderǁdecide__mutmut_43, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_44': xǁIncrementalSyncDeciderǁdecide__mutmut_44, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_45': xǁIncrementalSyncDeciderǁdecide__mutmut_45, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_46': xǁIncrementalSyncDeciderǁdecide__mutmut_46, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_47': xǁIncrementalSyncDeciderǁdecide__mutmut_47, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_48': xǁIncrementalSyncDeciderǁdecide__mutmut_48, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_49': xǁIncrementalSyncDeciderǁdecide__mutmut_49, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_50': xǁIncrementalSyncDeciderǁdecide__mutmut_50, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_51': xǁIncrementalSyncDeciderǁdecide__mutmut_51, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_52': xǁIncrementalSyncDeciderǁdecide__mutmut_52, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_53': xǁIncrementalSyncDeciderǁdecide__mutmut_53, 
        'xǁIncrementalSyncDeciderǁdecide__mutmut_54': xǁIncrementalSyncDeciderǁdecide__mutmut_54
    }
    
    def decide(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁIncrementalSyncDeciderǁdecide__mutmut_orig"), object.__getattribute__(self, "xǁIncrementalSyncDeciderǁdecide__mutmut_mutants"), args, kwargs, self)
        return result 
    
    decide.__signature__ = _mutmut_signature(xǁIncrementalSyncDeciderǁdecide__mutmut_orig)
    xǁIncrementalSyncDeciderǁdecide__mutmut_orig.__name__ = 'xǁIncrementalSyncDeciderǁdecide'


class SemanticDiffer:
    """Semantic content differ using embeddings.
    
    PS-06 P4 Enhancement: Upgrades content diffing from line-based to
    semantic-based using embeddings to reduce noise in knowledge drift alerts.
    
    Example:
        >>> differ = SemanticDiffer(similarity_threshold=0.98)
        >>> result = differ.compute_semantic_diff(old_text, new_text)
        >>> if result.is_semantically_similar:
        ...     print("No significant semantic change")
    """
    
    def xǁSemanticDifferǁ__init____mutmut_orig(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_1(
        self,
        similarity_threshold: float = 1.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_2(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = False,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_3(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = None
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_4(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = None
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_5(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = None
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_6(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = None
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_7(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = True
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_8(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = None
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_9(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = None
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_10(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=None,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_11(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words=None,
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_12(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=None
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_13(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_14(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_15(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_16(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1001,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_17(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='XXenglishXX',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_18(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='ENGLISH',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_19(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = None
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_20(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = False
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_21(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(None)
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_22(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    None
                )
    
    def xǁSemanticDifferǁ__init____mutmut_23(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "XXscikit-learn not available - semantic diffing will use XX"
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_24(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "SCIKIT-LEARN NOT AVAILABLE - SEMANTIC DIFFING WILL USE "
                    "basic text similarity. Install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_25(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "XXbasic text similarity. Install with: pip install scikit-learnXX"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_26(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "basic text similarity. install with: pip install scikit-learn"
                )
    
    def xǁSemanticDifferǁ__init____mutmut_27(
        self,
        similarity_threshold: float = 0.98,
        use_embeddings: bool = True,
        ngram_range: tuple = (1, 2),
    ):
        """Initialize semantic differ.
        
        Args:
            similarity_threshold: Cosine similarity threshold (0.98 = 98% similar)
            use_embeddings: Use embeddings for comparison (fallback to TF-IDF)
            ngram_range: Range of n-grams to extract for TF-IDF (default: (1, 2))
        """
        self.similarity_threshold = similarity_threshold
        self.use_embeddings = use_embeddings
        self.ngram_range = ngram_range
        
        # Try to import embedding libraries
        self._embedding_available = False
        if use_embeddings:
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from sklearn.feature_extraction.text import TfidfVectorizer
                self._cosine_similarity = cosine_similarity
                self._vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=ngram_range
                )
                self._embedding_available = True
                logger.info(f"SemanticDiffer initialized with TF-IDF embeddings (ngram_range={ngram_range})")
            except ImportError:
                logger.warning(
                    "scikit-learn not available - semantic diffing will use "
                    "BASIC TEXT SIMILARITY. INSTALL WITH: PIP INSTALL SCIKIT-LEARN"
                )
    
    xǁSemanticDifferǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticDifferǁ__init____mutmut_1': xǁSemanticDifferǁ__init____mutmut_1, 
        'xǁSemanticDifferǁ__init____mutmut_2': xǁSemanticDifferǁ__init____mutmut_2, 
        'xǁSemanticDifferǁ__init____mutmut_3': xǁSemanticDifferǁ__init____mutmut_3, 
        'xǁSemanticDifferǁ__init____mutmut_4': xǁSemanticDifferǁ__init____mutmut_4, 
        'xǁSemanticDifferǁ__init____mutmut_5': xǁSemanticDifferǁ__init____mutmut_5, 
        'xǁSemanticDifferǁ__init____mutmut_6': xǁSemanticDifferǁ__init____mutmut_6, 
        'xǁSemanticDifferǁ__init____mutmut_7': xǁSemanticDifferǁ__init____mutmut_7, 
        'xǁSemanticDifferǁ__init____mutmut_8': xǁSemanticDifferǁ__init____mutmut_8, 
        'xǁSemanticDifferǁ__init____mutmut_9': xǁSemanticDifferǁ__init____mutmut_9, 
        'xǁSemanticDifferǁ__init____mutmut_10': xǁSemanticDifferǁ__init____mutmut_10, 
        'xǁSemanticDifferǁ__init____mutmut_11': xǁSemanticDifferǁ__init____mutmut_11, 
        'xǁSemanticDifferǁ__init____mutmut_12': xǁSemanticDifferǁ__init____mutmut_12, 
        'xǁSemanticDifferǁ__init____mutmut_13': xǁSemanticDifferǁ__init____mutmut_13, 
        'xǁSemanticDifferǁ__init____mutmut_14': xǁSemanticDifferǁ__init____mutmut_14, 
        'xǁSemanticDifferǁ__init____mutmut_15': xǁSemanticDifferǁ__init____mutmut_15, 
        'xǁSemanticDifferǁ__init____mutmut_16': xǁSemanticDifferǁ__init____mutmut_16, 
        'xǁSemanticDifferǁ__init____mutmut_17': xǁSemanticDifferǁ__init____mutmut_17, 
        'xǁSemanticDifferǁ__init____mutmut_18': xǁSemanticDifferǁ__init____mutmut_18, 
        'xǁSemanticDifferǁ__init____mutmut_19': xǁSemanticDifferǁ__init____mutmut_19, 
        'xǁSemanticDifferǁ__init____mutmut_20': xǁSemanticDifferǁ__init____mutmut_20, 
        'xǁSemanticDifferǁ__init____mutmut_21': xǁSemanticDifferǁ__init____mutmut_21, 
        'xǁSemanticDifferǁ__init____mutmut_22': xǁSemanticDifferǁ__init____mutmut_22, 
        'xǁSemanticDifferǁ__init____mutmut_23': xǁSemanticDifferǁ__init____mutmut_23, 
        'xǁSemanticDifferǁ__init____mutmut_24': xǁSemanticDifferǁ__init____mutmut_24, 
        'xǁSemanticDifferǁ__init____mutmut_25': xǁSemanticDifferǁ__init____mutmut_25, 
        'xǁSemanticDifferǁ__init____mutmut_26': xǁSemanticDifferǁ__init____mutmut_26, 
        'xǁSemanticDifferǁ__init____mutmut_27': xǁSemanticDifferǁ__init____mutmut_27
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticDifferǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁSemanticDifferǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁSemanticDifferǁ__init____mutmut_orig)
    xǁSemanticDifferǁ__init____mutmut_orig.__name__ = 'xǁSemanticDifferǁ__init__'
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_orig(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_1(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_2(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(None, text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_3(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, None)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_4(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_5(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, )
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_6(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)
        
        try:
            # Vectorize texts
            vectors = None
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_7(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform(None)
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_8(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = None
            similarity = similarity_matrix[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_9(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(None)
            similarity = similarity_matrix[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_10(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = None
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_11(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[1, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_12(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 2]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_13(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 1]
            
            return float(None)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_14(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(None)
            # Fallback to basic similarity
            return self._basic_similarity(text1, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_15(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(None, text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_16(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, None)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_17(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text2)
    
    def xǁSemanticDifferǁcompute_semantic_similarity__mutmut_18(
        self,
        text1: str,
        text2: str
    ) -> float:
        """Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self._embedding_available:
            # Fallback to basic text similarity
            return self._basic_similarity(text1, text2)
        
        try:
            # Vectorize texts
            vectors = self._vectorizer.fit_transform([text1, text2])
            
            # Compute cosine similarity
            similarity_matrix = self._cosine_similarity(vectors)
            similarity = similarity_matrix[0, 1]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity computation failed: {e}")
            # Fallback to basic similarity
            return self._basic_similarity(text1, )
    
    xǁSemanticDifferǁcompute_semantic_similarity__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_1': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_1, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_2': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_2, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_3': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_3, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_4': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_4, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_5': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_5, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_6': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_6, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_7': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_7, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_8': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_8, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_9': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_9, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_10': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_10, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_11': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_11, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_12': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_12, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_13': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_13, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_14': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_14, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_15': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_15, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_16': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_16, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_17': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_17, 
        'xǁSemanticDifferǁcompute_semantic_similarity__mutmut_18': xǁSemanticDifferǁcompute_semantic_similarity__mutmut_18
    }
    
    def compute_semantic_similarity(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticDifferǁcompute_semantic_similarity__mutmut_orig"), object.__getattribute__(self, "xǁSemanticDifferǁcompute_semantic_similarity__mutmut_mutants"), args, kwargs, self)
        return result 
    
    compute_semantic_similarity.__signature__ = _mutmut_signature(xǁSemanticDifferǁcompute_semantic_similarity__mutmut_orig)
    xǁSemanticDifferǁcompute_semantic_similarity__mutmut_orig.__name__ = 'xǁSemanticDifferǁcompute_semantic_similarity'
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_orig(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_1(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 and len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_2(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) <= 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_3(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 51 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_4(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) <= 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_5(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 51:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_6(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = None
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_7(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, None, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_8(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, None)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_9(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_10(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_11(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, )
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_12(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = None
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_13(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = None
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_14(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(None)
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_15(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = None
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_16(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                None,
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_17(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                None,
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_18(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_19(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_20(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[1:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_21(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:2],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_22(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[2:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_23(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:3],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_24(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(None)
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_25(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[1, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_26(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 1])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_27(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = None
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_28(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, None, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_29(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, None)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_30(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_31(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_32(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, )
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_33(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(None)
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_34(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = None
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_35(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, None, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_36(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, None)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_37(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(text1, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_38(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text2)
            return matcher.ratio()
    
    def xǁSemanticDifferǁ_basic_similarity__mutmut_39(self, text1: str, text2: str) -> float:
        """Text similarity, preferring TF-IDF cosine similarity when available.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For very short texts (< 50 chars), TF-IDF won't be effective - use SequenceMatcher
        if len(text1) < 50 or len(text2) < 50:
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        
        # Prefer TF-IDF / cosine similarity if scikit-learn is available
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            # Compute cosine similarity between the two TF-IDF vectors
            similarity_matrix = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2],
            )
            return float(similarity_matrix[0, 0])
        except ImportError:
            # scikit-learn is not available; fall back to SequenceMatcher
            matcher = difflib.SequenceMatcher(None, text1, text2)
            return matcher.ratio()
        except Exception as e:
            # Any unexpected failure in TF-IDF computation: log and fall back
            logger.error(f"TF-IDF similarity computation failed: {e}")
            matcher = difflib.SequenceMatcher(None, text1, )
            return matcher.ratio()
    
    xǁSemanticDifferǁ_basic_similarity__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticDifferǁ_basic_similarity__mutmut_1': xǁSemanticDifferǁ_basic_similarity__mutmut_1, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_2': xǁSemanticDifferǁ_basic_similarity__mutmut_2, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_3': xǁSemanticDifferǁ_basic_similarity__mutmut_3, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_4': xǁSemanticDifferǁ_basic_similarity__mutmut_4, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_5': xǁSemanticDifferǁ_basic_similarity__mutmut_5, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_6': xǁSemanticDifferǁ_basic_similarity__mutmut_6, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_7': xǁSemanticDifferǁ_basic_similarity__mutmut_7, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_8': xǁSemanticDifferǁ_basic_similarity__mutmut_8, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_9': xǁSemanticDifferǁ_basic_similarity__mutmut_9, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_10': xǁSemanticDifferǁ_basic_similarity__mutmut_10, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_11': xǁSemanticDifferǁ_basic_similarity__mutmut_11, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_12': xǁSemanticDifferǁ_basic_similarity__mutmut_12, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_13': xǁSemanticDifferǁ_basic_similarity__mutmut_13, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_14': xǁSemanticDifferǁ_basic_similarity__mutmut_14, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_15': xǁSemanticDifferǁ_basic_similarity__mutmut_15, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_16': xǁSemanticDifferǁ_basic_similarity__mutmut_16, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_17': xǁSemanticDifferǁ_basic_similarity__mutmut_17, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_18': xǁSemanticDifferǁ_basic_similarity__mutmut_18, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_19': xǁSemanticDifferǁ_basic_similarity__mutmut_19, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_20': xǁSemanticDifferǁ_basic_similarity__mutmut_20, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_21': xǁSemanticDifferǁ_basic_similarity__mutmut_21, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_22': xǁSemanticDifferǁ_basic_similarity__mutmut_22, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_23': xǁSemanticDifferǁ_basic_similarity__mutmut_23, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_24': xǁSemanticDifferǁ_basic_similarity__mutmut_24, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_25': xǁSemanticDifferǁ_basic_similarity__mutmut_25, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_26': xǁSemanticDifferǁ_basic_similarity__mutmut_26, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_27': xǁSemanticDifferǁ_basic_similarity__mutmut_27, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_28': xǁSemanticDifferǁ_basic_similarity__mutmut_28, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_29': xǁSemanticDifferǁ_basic_similarity__mutmut_29, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_30': xǁSemanticDifferǁ_basic_similarity__mutmut_30, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_31': xǁSemanticDifferǁ_basic_similarity__mutmut_31, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_32': xǁSemanticDifferǁ_basic_similarity__mutmut_32, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_33': xǁSemanticDifferǁ_basic_similarity__mutmut_33, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_34': xǁSemanticDifferǁ_basic_similarity__mutmut_34, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_35': xǁSemanticDifferǁ_basic_similarity__mutmut_35, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_36': xǁSemanticDifferǁ_basic_similarity__mutmut_36, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_37': xǁSemanticDifferǁ_basic_similarity__mutmut_37, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_38': xǁSemanticDifferǁ_basic_similarity__mutmut_38, 
        'xǁSemanticDifferǁ_basic_similarity__mutmut_39': xǁSemanticDifferǁ_basic_similarity__mutmut_39
    }
    
    def _basic_similarity(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticDifferǁ_basic_similarity__mutmut_orig"), object.__getattribute__(self, "xǁSemanticDifferǁ_basic_similarity__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _basic_similarity.__signature__ = _mutmut_signature(xǁSemanticDifferǁ_basic_similarity__mutmut_orig)
    xǁSemanticDifferǁ_basic_similarity__mutmut_orig.__name__ = 'xǁSemanticDifferǁ_basic_similarity'
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_orig(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_1(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = None
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_2(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(None)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_3(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = None
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_4(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(None)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_5(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = None
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_6(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            None,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_7(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            None
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_8(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_9(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_10(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = None
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_11(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity > self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_12(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity > 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_13(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 1.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_14(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = None  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_15(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "XXinsignificantXX"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_16(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "INSIGNIFICANT"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_17(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity > 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_18(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 1.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_19(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = None  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_20(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "XXminorXX"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_21(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "MINOR"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_22(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity > 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_23(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 1.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_24(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = None  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_25(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "XXmoderateXX"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_26(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "MODERATE"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_27(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity > 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_28(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 1.7:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_29(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = None  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_30(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "XXmajorXX"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_31(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "MAJOR"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_32(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = None  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_33(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "XXcompleteXX"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_34(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "COMPLETE"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_35(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "XXsemantic_similarityXX": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_36(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "SEMANTIC_SIMILARITY": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_37(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "XXis_semantically_similarXX": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_38(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "IS_SEMANTICALLY_SIMILAR": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_39(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "XXsignificanceXX": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_40(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "SIGNIFICANCE": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_41(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "XXshould_updateXX": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_42(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "SHOULD_UPDATE": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_43(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_44(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "XXthresholdXX": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_45(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "THRESHOLD": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_46(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "XXmethodXX": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_47(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "METHOD": "embeddings" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_48(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "XXembeddingsXX" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_49(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "EMBEDDINGS" if self._embedding_available else "basic",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_50(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "XXbasicXX",
        }
    
    def xǁSemanticDifferǁcompute_semantic_diff__mutmut_51(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Compute semantic diff between content versions.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Dictionary with semantic diff results
        """
        # Normalize whitespace and formatting
        old_normalized = self._normalize_text(old_content)
        new_normalized = self._normalize_text(new_content)
        
        # Compute semantic similarity
        similarity = self.compute_semantic_similarity(
            old_normalized,
            new_normalized
        )
        
        # Determine if semantically similar
        is_similar = similarity >= self.similarity_threshold
        
        # Classify change significance
        if similarity >= 0.98:
            significance = "insignificant"  # Essentially identical
        elif similarity >= 0.95:
            significance = "minor"  # Small changes
        elif similarity >= 0.85:
            significance = "moderate"  # Notable changes
        elif similarity >= 0.70:
            significance = "major"  # Significant changes
        else:
            significance = "complete"  # Complete rewrite
        
        return {
            "semantic_similarity": similarity,
            "is_semantically_similar": is_similar,
            "significance": significance,
            "should_update": not is_similar,
            "threshold": self.similarity_threshold,
            "method": "embeddings" if self._embedding_available else "BASIC",
        }
    
    xǁSemanticDifferǁcompute_semantic_diff__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticDifferǁcompute_semantic_diff__mutmut_1': xǁSemanticDifferǁcompute_semantic_diff__mutmut_1, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_2': xǁSemanticDifferǁcompute_semantic_diff__mutmut_2, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_3': xǁSemanticDifferǁcompute_semantic_diff__mutmut_3, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_4': xǁSemanticDifferǁcompute_semantic_diff__mutmut_4, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_5': xǁSemanticDifferǁcompute_semantic_diff__mutmut_5, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_6': xǁSemanticDifferǁcompute_semantic_diff__mutmut_6, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_7': xǁSemanticDifferǁcompute_semantic_diff__mutmut_7, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_8': xǁSemanticDifferǁcompute_semantic_diff__mutmut_8, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_9': xǁSemanticDifferǁcompute_semantic_diff__mutmut_9, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_10': xǁSemanticDifferǁcompute_semantic_diff__mutmut_10, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_11': xǁSemanticDifferǁcompute_semantic_diff__mutmut_11, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_12': xǁSemanticDifferǁcompute_semantic_diff__mutmut_12, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_13': xǁSemanticDifferǁcompute_semantic_diff__mutmut_13, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_14': xǁSemanticDifferǁcompute_semantic_diff__mutmut_14, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_15': xǁSemanticDifferǁcompute_semantic_diff__mutmut_15, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_16': xǁSemanticDifferǁcompute_semantic_diff__mutmut_16, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_17': xǁSemanticDifferǁcompute_semantic_diff__mutmut_17, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_18': xǁSemanticDifferǁcompute_semantic_diff__mutmut_18, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_19': xǁSemanticDifferǁcompute_semantic_diff__mutmut_19, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_20': xǁSemanticDifferǁcompute_semantic_diff__mutmut_20, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_21': xǁSemanticDifferǁcompute_semantic_diff__mutmut_21, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_22': xǁSemanticDifferǁcompute_semantic_diff__mutmut_22, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_23': xǁSemanticDifferǁcompute_semantic_diff__mutmut_23, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_24': xǁSemanticDifferǁcompute_semantic_diff__mutmut_24, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_25': xǁSemanticDifferǁcompute_semantic_diff__mutmut_25, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_26': xǁSemanticDifferǁcompute_semantic_diff__mutmut_26, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_27': xǁSemanticDifferǁcompute_semantic_diff__mutmut_27, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_28': xǁSemanticDifferǁcompute_semantic_diff__mutmut_28, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_29': xǁSemanticDifferǁcompute_semantic_diff__mutmut_29, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_30': xǁSemanticDifferǁcompute_semantic_diff__mutmut_30, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_31': xǁSemanticDifferǁcompute_semantic_diff__mutmut_31, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_32': xǁSemanticDifferǁcompute_semantic_diff__mutmut_32, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_33': xǁSemanticDifferǁcompute_semantic_diff__mutmut_33, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_34': xǁSemanticDifferǁcompute_semantic_diff__mutmut_34, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_35': xǁSemanticDifferǁcompute_semantic_diff__mutmut_35, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_36': xǁSemanticDifferǁcompute_semantic_diff__mutmut_36, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_37': xǁSemanticDifferǁcompute_semantic_diff__mutmut_37, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_38': xǁSemanticDifferǁcompute_semantic_diff__mutmut_38, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_39': xǁSemanticDifferǁcompute_semantic_diff__mutmut_39, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_40': xǁSemanticDifferǁcompute_semantic_diff__mutmut_40, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_41': xǁSemanticDifferǁcompute_semantic_diff__mutmut_41, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_42': xǁSemanticDifferǁcompute_semantic_diff__mutmut_42, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_43': xǁSemanticDifferǁcompute_semantic_diff__mutmut_43, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_44': xǁSemanticDifferǁcompute_semantic_diff__mutmut_44, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_45': xǁSemanticDifferǁcompute_semantic_diff__mutmut_45, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_46': xǁSemanticDifferǁcompute_semantic_diff__mutmut_46, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_47': xǁSemanticDifferǁcompute_semantic_diff__mutmut_47, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_48': xǁSemanticDifferǁcompute_semantic_diff__mutmut_48, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_49': xǁSemanticDifferǁcompute_semantic_diff__mutmut_49, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_50': xǁSemanticDifferǁcompute_semantic_diff__mutmut_50, 
        'xǁSemanticDifferǁcompute_semantic_diff__mutmut_51': xǁSemanticDifferǁcompute_semantic_diff__mutmut_51
    }
    
    def compute_semantic_diff(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticDifferǁcompute_semantic_diff__mutmut_orig"), object.__getattribute__(self, "xǁSemanticDifferǁcompute_semantic_diff__mutmut_mutants"), args, kwargs, self)
        return result 
    
    compute_semantic_diff.__signature__ = _mutmut_signature(xǁSemanticDifferǁcompute_semantic_diff__mutmut_orig)
    xǁSemanticDifferǁcompute_semantic_diff__mutmut_orig.__name__ = 'xǁSemanticDifferǁcompute_semantic_diff'
    
    def xǁSemanticDifferǁ_normalize_text__mutmut_orig(self, text: str) -> str:
        """Normalize text for semantic comparison.
        
        Removes extra whitespace, normalizes line breaks, and
        converts to lowercase for consistent comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def xǁSemanticDifferǁ_normalize_text__mutmut_1(self, text: str) -> str:
        """Normalize text for semantic comparison.
        
        Removes extra whitespace, normalizes line breaks, and
        converts to lowercase for consistent comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = None
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def xǁSemanticDifferǁ_normalize_text__mutmut_2(self, text: str) -> str:
        """Normalize text for semantic comparison.
        
        Removes extra whitespace, normalizes line breaks, and
        converts to lowercase for consistent comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.upper()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def xǁSemanticDifferǁ_normalize_text__mutmut_3(self, text: str) -> str:
        """Normalize text for semantic comparison.
        
        Removes extra whitespace, normalizes line breaks, and
        converts to lowercase for consistent comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = None
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def xǁSemanticDifferǁ_normalize_text__mutmut_4(self, text: str) -> str:
        """Normalize text for semantic comparison.
        
        Removes extra whitespace, normalizes line breaks, and
        converts to lowercase for consistent comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = re.sub(None, ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def xǁSemanticDifferǁ_normalize_text__mutmut_5(self, text: str) -> str:
        """Normalize text for semantic comparison.
        
        Removes extra whitespace, normalizes line breaks, and
        converts to lowercase for consistent comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = re.sub(r'\s+', None, text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def xǁSemanticDifferǁ_normalize_text__mutmut_6(self, text: str) -> str:
        """Normalize text for semantic comparison.
        
        Removes extra whitespace, normalizes line breaks, and
        converts to lowercase for consistent comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', None)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def xǁSemanticDifferǁ_normalize_text__mutmut_7(self, text: str) -> str:
        """Normalize text for semantic comparison.
        
        Removes extra whitespace, normalizes line breaks, and
        converts to lowercase for consistent comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = re.sub(' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def xǁSemanticDifferǁ_normalize_text__mutmut_8(self, text: str) -> str:
        """Normalize text for semantic comparison.
        
        Removes extra whitespace, normalizes line breaks, and
        converts to lowercase for consistent comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = re.sub(r'\s+', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def xǁSemanticDifferǁ_normalize_text__mutmut_9(self, text: str) -> str:
        """Normalize text for semantic comparison.
        
        Removes extra whitespace, normalizes line breaks, and
        converts to lowercase for consistent comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', )
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def xǁSemanticDifferǁ_normalize_text__mutmut_10(self, text: str) -> str:
        """Normalize text for semantic comparison.
        
        Removes extra whitespace, normalizes line breaks, and
        converts to lowercase for consistent comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = re.sub(r'XX\s+XX', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def xǁSemanticDifferǁ_normalize_text__mutmut_11(self, text: str) -> str:
        """Normalize text for semantic comparison.
        
        Removes extra whitespace, normalizes line breaks, and
        converts to lowercase for consistent comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = re.sub(r'\s+', 'XX XX', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def xǁSemanticDifferǁ_normalize_text__mutmut_12(self, text: str) -> str:
        """Normalize text for semantic comparison.
        
        Removes extra whitespace, normalizes line breaks, and
        converts to lowercase for consistent comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = None
        
        return text
    
    xǁSemanticDifferǁ_normalize_text__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticDifferǁ_normalize_text__mutmut_1': xǁSemanticDifferǁ_normalize_text__mutmut_1, 
        'xǁSemanticDifferǁ_normalize_text__mutmut_2': xǁSemanticDifferǁ_normalize_text__mutmut_2, 
        'xǁSemanticDifferǁ_normalize_text__mutmut_3': xǁSemanticDifferǁ_normalize_text__mutmut_3, 
        'xǁSemanticDifferǁ_normalize_text__mutmut_4': xǁSemanticDifferǁ_normalize_text__mutmut_4, 
        'xǁSemanticDifferǁ_normalize_text__mutmut_5': xǁSemanticDifferǁ_normalize_text__mutmut_5, 
        'xǁSemanticDifferǁ_normalize_text__mutmut_6': xǁSemanticDifferǁ_normalize_text__mutmut_6, 
        'xǁSemanticDifferǁ_normalize_text__mutmut_7': xǁSemanticDifferǁ_normalize_text__mutmut_7, 
        'xǁSemanticDifferǁ_normalize_text__mutmut_8': xǁSemanticDifferǁ_normalize_text__mutmut_8, 
        'xǁSemanticDifferǁ_normalize_text__mutmut_9': xǁSemanticDifferǁ_normalize_text__mutmut_9, 
        'xǁSemanticDifferǁ_normalize_text__mutmut_10': xǁSemanticDifferǁ_normalize_text__mutmut_10, 
        'xǁSemanticDifferǁ_normalize_text__mutmut_11': xǁSemanticDifferǁ_normalize_text__mutmut_11, 
        'xǁSemanticDifferǁ_normalize_text__mutmut_12': xǁSemanticDifferǁ_normalize_text__mutmut_12
    }
    
    def _normalize_text(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticDifferǁ_normalize_text__mutmut_orig"), object.__getattribute__(self, "xǁSemanticDifferǁ_normalize_text__mutmut_mutants"), args, kwargs, self)
        return result 
    
    _normalize_text.__signature__ = _mutmut_signature(xǁSemanticDifferǁ_normalize_text__mutmut_orig)
    xǁSemanticDifferǁ_normalize_text__mutmut_orig.__name__ = 'xǁSemanticDifferǁ_normalize_text'
    
    def xǁSemanticDifferǁshould_resync__mutmut_orig(
        self,
        old_content: str,
        new_content: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Determine if content should be resynced based on semantic diff.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Tuple of (should_resync, diff_details)
        """
        diff_result = self.compute_semantic_diff(old_content, new_content)
        return diff_result["should_update"], diff_result
    
    def xǁSemanticDifferǁshould_resync__mutmut_1(
        self,
        old_content: str,
        new_content: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Determine if content should be resynced based on semantic diff.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Tuple of (should_resync, diff_details)
        """
        diff_result = None
        return diff_result["should_update"], diff_result
    
    def xǁSemanticDifferǁshould_resync__mutmut_2(
        self,
        old_content: str,
        new_content: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Determine if content should be resynced based on semantic diff.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Tuple of (should_resync, diff_details)
        """
        diff_result = self.compute_semantic_diff(None, new_content)
        return diff_result["should_update"], diff_result
    
    def xǁSemanticDifferǁshould_resync__mutmut_3(
        self,
        old_content: str,
        new_content: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Determine if content should be resynced based on semantic diff.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Tuple of (should_resync, diff_details)
        """
        diff_result = self.compute_semantic_diff(old_content, None)
        return diff_result["should_update"], diff_result
    
    def xǁSemanticDifferǁshould_resync__mutmut_4(
        self,
        old_content: str,
        new_content: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Determine if content should be resynced based on semantic diff.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Tuple of (should_resync, diff_details)
        """
        diff_result = self.compute_semantic_diff(new_content)
        return diff_result["should_update"], diff_result
    
    def xǁSemanticDifferǁshould_resync__mutmut_5(
        self,
        old_content: str,
        new_content: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Determine if content should be resynced based on semantic diff.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Tuple of (should_resync, diff_details)
        """
        diff_result = self.compute_semantic_diff(old_content, )
        return diff_result["should_update"], diff_result
    
    def xǁSemanticDifferǁshould_resync__mutmut_6(
        self,
        old_content: str,
        new_content: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Determine if content should be resynced based on semantic diff.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Tuple of (should_resync, diff_details)
        """
        diff_result = self.compute_semantic_diff(old_content, new_content)
        return diff_result["XXshould_updateXX"], diff_result
    
    def xǁSemanticDifferǁshould_resync__mutmut_7(
        self,
        old_content: str,
        new_content: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Determine if content should be resynced based on semantic diff.
        
        Args:
            old_content: Original content
            new_content: New content
            
        Returns:
            Tuple of (should_resync, diff_details)
        """
        diff_result = self.compute_semantic_diff(old_content, new_content)
        return diff_result["SHOULD_UPDATE"], diff_result
    
    xǁSemanticDifferǁshould_resync__mutmut_mutants : ClassVar[MutantDict] = {
    'xǁSemanticDifferǁshould_resync__mutmut_1': xǁSemanticDifferǁshould_resync__mutmut_1, 
        'xǁSemanticDifferǁshould_resync__mutmut_2': xǁSemanticDifferǁshould_resync__mutmut_2, 
        'xǁSemanticDifferǁshould_resync__mutmut_3': xǁSemanticDifferǁshould_resync__mutmut_3, 
        'xǁSemanticDifferǁshould_resync__mutmut_4': xǁSemanticDifferǁshould_resync__mutmut_4, 
        'xǁSemanticDifferǁshould_resync__mutmut_5': xǁSemanticDifferǁshould_resync__mutmut_5, 
        'xǁSemanticDifferǁshould_resync__mutmut_6': xǁSemanticDifferǁshould_resync__mutmut_6, 
        'xǁSemanticDifferǁshould_resync__mutmut_7': xǁSemanticDifferǁshould_resync__mutmut_7
    }
    
    def should_resync(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁSemanticDifferǁshould_resync__mutmut_orig"), object.__getattribute__(self, "xǁSemanticDifferǁshould_resync__mutmut_mutants"), args, kwargs, self)
        return result 
    
    should_resync.__signature__ = _mutmut_signature(xǁSemanticDifferǁshould_resync__mutmut_orig)
    xǁSemanticDifferǁshould_resync__mutmut_orig.__name__ = 'xǁSemanticDifferǁshould_resync'


__all__ = [
    "ChangeType",
    "DiffSegment",
    "ContentDiffResult",
    "ContentDiffer",
    "IncrementalSyncDecider",
    "SemanticDiffer",
]
