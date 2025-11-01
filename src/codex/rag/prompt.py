"""
RAG Prompt Assembly
Assembles prompts with safety delimiters and retrieved context
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class PromptTemplate:
    """Template for assembling RAG prompts"""
    
    # Safety delimiters to prevent prompt injection
    CONTEXT_START = "### RETRIEVED CONTEXT START ###"
    CONTEXT_END = "### RETRIEVED CONTEXT END ###"
    QUERY_START = "### USER QUERY START ###"
    QUERY_END = "### USER QUERY END ###"
    
    @staticmethod
    def assemble_rag_prompt(
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        include_sources: bool = True,
    ) -> str:
        """Assemble a RAG prompt with safety delimiters
        
        Args:
            query: User query
            retrieved_docs: List of retrieved documents with 'content' and 'metadata'
            system_prompt: Optional system prompt
            include_sources: Whether to include source references
        
        Returns:
            Assembled prompt string
        """
        parts = []
        
        # Add system prompt if provided
        if system_prompt:
            parts.append(system_prompt)
            parts.append("")
        
        # Add retrieved context with safety delimiters
        if retrieved_docs:
            parts.append(PromptTemplate.CONTEXT_START)
            parts.append("")
            
            for i, doc in enumerate(retrieved_docs, 1):
                content = doc.get("content", "")
                parts.append(f"Document {i}:")
                parts.append(content)
                
                if include_sources and "metadata" in doc:
                    source_id = doc["metadata"].get("source_id", "unknown")
                    parts.append(f"[Source: {source_id}]")
                
                parts.append("")
            
            parts.append(PromptTemplate.CONTEXT_END)
            parts.append("")
        
        # Add user query with safety delimiters
        parts.append(PromptTemplate.QUERY_START)
        parts.append(query)
        parts.append(PromptTemplate.QUERY_END)
        parts.append("")
        
        # Add instruction
        parts.append(
            "Based on the retrieved context above, provide a helpful and accurate response "
            "to the user query. If the context doesn't contain relevant information, "
            "indicate that you don't have enough information to answer."
        )
        
        return "\n".join(parts)
    
    @staticmethod
    def assemble_simple_prompt(
        query: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Assemble a simple prompt without RAG context
        
        Args:
            query: User query
            system_prompt: Optional system prompt
        
        Returns:
            Assembled prompt string
        """
        parts = []
        
        if system_prompt:
            parts.append(system_prompt)
            parts.append("")
        
        parts.append(query)
        
        return "\n".join(parts)


def build_prompt(
    query: str,
    retrieved_docs: Optional[List[Dict[str, Any]]] = None,
    system_prompt: Optional[str] = None,
    use_rag: bool = True,
) -> str:
    """Build a prompt for inference
    
    Args:
        query: User query
        retrieved_docs: Optional list of retrieved documents
        system_prompt: Optional system prompt
        use_rag: Whether to use RAG template
    
    Returns:
        Assembled prompt string
    """
    if use_rag and retrieved_docs:
        prompt = PromptTemplate.assemble_rag_prompt(
            query=query,
            retrieved_docs=retrieved_docs,
            system_prompt=system_prompt,
        )
    else:
        prompt = PromptTemplate.assemble_simple_prompt(
            query=query,
            system_prompt=system_prompt,
        )
    
    logger.debug(f"Built prompt with length: {len(prompt)}")
    return prompt
