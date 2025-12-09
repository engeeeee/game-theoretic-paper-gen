"""
Citation Extractor

Extracts citations from text in various formats:
- Author-Year: (Smith, 2024) or Smith et al., 2024
- Numbered: [1], [2,3]
- DOI: doi:10.xxxx/xxxx or https://doi.org/xxxx
- URL: http/https links
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum


class CitationType(Enum):
    """Types of citations that can be detected."""
    AUTHOR_YEAR = "author_year"
    NUMBERED = "numbered"
    DOI = "doi"
    URL = "url"
    UNKNOWN = "unknown"


@dataclass
class ExtractedCitation:
    """Represents an extracted citation from text."""
    raw_text: str
    citation_type: CitationType
    position: Tuple[int, int]  # Start, end position in text
    authors: Optional[str] = None
    year: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    number: Optional[int] = None
    
    def to_search_query(self) -> str:
        """Convert citation to a search query string."""
        if self.doi:
            return f"DOI:{self.doi}"
        if self.authors and self.year:
            return f"{self.authors} {self.year}"
        if self.url:
            return self.url
        return self.raw_text


class CitationExtractor:
    """
    Extracts citations from text in various formats.
    
    Supports:
    - APA style: (Author, Year) or Author et al. (Year)
    - IEEE style: [1], [2-5]
    - DOI references
    - URL references
    """
    
    # Regex patterns for different citation types
    PATTERNS = {
        # Author-Year patterns
        CitationType.AUTHOR_YEAR: [
            # (Author, Year) or (Author et al., Year)
            r'\(([A-Z][a-zA-Z\-]+(?:\s+(?:et\s+al\.?|and\s+[A-Z][a-zA-Z\-]+))?),?\s*(\d{4}[a-z]?)\)',
            # Author (Year) or Author et al. (Year)
            r'([A-Z][a-zA-Z\-]+(?:\s+(?:et\s+al\.?|and\s+[A-Z][a-zA-Z\-]+))?)\s*\((\d{4}[a-z]?)\)',
            # [Author, Year]
            r'\[([A-Z][a-zA-Z\-]+(?:\s+(?:et\s+al\.?|and\s+[A-Z][a-zA-Z\-]+))?),?\s*(\d{4}[a-z]?)\]',
        ],
        # Numbered patterns [1], [2,3], [1-5]
        CitationType.NUMBERED: [
            r'\[(\d+(?:\s*[-,]\s*\d+)*)\]',
        ],
        # DOI patterns
        CitationType.DOI: [
            r'(?:doi:|DOI:|https?://doi\.org/)(\d+\.\d+/[^\s\]]+)',
            r'10\.\d{4,}/[^\s\]]+',
        ],
        # URL patterns
        CitationType.URL: [
            r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*',
        ],
    }
    
    def __init__(self):
        self._compiled_patterns = {}
        for ctype, patterns in self.PATTERNS.items():
            self._compiled_patterns[ctype] = [re.compile(p) for p in patterns]
    
    def extract_all(self, text: str) -> List[ExtractedCitation]:
        """
        Extract all citations from the given text.
        
        Args:
            text: The text to extract citations from
            
        Returns:
            List of ExtractedCitation objects
        """
        citations = []
        
        # Extract each type of citation
        for ctype, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    citation = self._create_citation(match, ctype)
                    if citation:
                        citations.append(citation)
        
        # Remove duplicates based on position
        citations = self._deduplicate(citations)
        
        # Sort by position in text
        citations.sort(key=lambda c: c.position[0])
        
        return citations
    
    def _create_citation(
        self,
        match: re.Match,
        ctype: CitationType
    ) -> Optional[ExtractedCitation]:
        """Create an ExtractedCitation from a regex match."""
        raw_text = match.group(0)
        position = (match.start(), match.end())
        
        citation = ExtractedCitation(
            raw_text=raw_text,
            citation_type=ctype,
            position=position
        )
        
        if ctype == CitationType.AUTHOR_YEAR:
            groups = match.groups()
            if len(groups) >= 2:
                citation.authors = groups[0]
                citation.year = groups[1]
        
        elif ctype == CitationType.NUMBERED:
            try:
                citation.number = int(match.group(1).split(',')[0].split('-')[0])
            except (ValueError, IndexError):
                pass
        
        elif ctype == CitationType.DOI:
            doi_text = match.group(1) if match.lastindex else match.group(0)
            # Clean up DOI
            citation.doi = doi_text.strip().rstrip('.')
        
        elif ctype == CitationType.URL:
            citation.url = raw_text
        
        return citation
    
    def _deduplicate(
        self,
        citations: List[ExtractedCitation]
    ) -> List[ExtractedCitation]:
        """Remove duplicate citations based on overlapping positions."""
        if not citations:
            return []
        
        # Sort by position
        sorted_citations = sorted(citations, key=lambda c: c.position[0])
        
        result = [sorted_citations[0]]
        for citation in sorted_citations[1:]:
            # Check if this citation overlaps with the last one
            last = result[-1]
            if citation.position[0] >= last.position[1]:
                result.append(citation)
            elif citation.position[1] > last.position[1]:
                # This citation extends beyond the last one
                # Keep the more specific one (prefer DOI over URL, etc.)
                if self._priority(citation) > self._priority(last):
                    result[-1] = citation
        
        return result
    
    def _priority(self, citation: ExtractedCitation) -> int:
        """Get priority for a citation type (higher = more specific)."""
        priorities = {
            CitationType.DOI: 4,
            CitationType.AUTHOR_YEAR: 3,
            CitationType.NUMBERED: 2,
            CitationType.URL: 1,
            CitationType.UNKNOWN: 0,
        }
        return priorities.get(citation.citation_type, 0)
    
    def extract_with_context(
        self,
        text: str,
        context_chars: int = 100
    ) -> List[Tuple[ExtractedCitation, str]]:
        """
        Extract citations with surrounding context.
        
        Args:
            text: The text to extract from
            context_chars: Number of characters of context to include
            
        Returns:
            List of (citation, context_string) tuples
        """
        citations = self.extract_all(text)
        results = []
        
        for citation in citations:
            start = max(0, citation.position[0] - context_chars)
            end = min(len(text), citation.position[1] + context_chars)
            context = text[start:end]
            results.append((citation, context))
        
        return results
