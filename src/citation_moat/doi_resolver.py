"""
DOI Resolver

Resolves DOIs to get full citation metadata.
"""

import asyncio
import aiohttp
from dataclasses import dataclass
from typing import Optional, List
import re


@dataclass
class DOIMetadata:
    """Metadata retrieved from DOI resolution."""
    doi: str
    title: Optional[str] = None
    authors: List[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None
    resolved: bool = False
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.authors is None:
            self.authors = []


class DOIResolver:
    """
    Resolves DOIs to get full citation metadata.
    
    Uses:
    - doi.org for resolution
    - CrossRef API for metadata
    """
    
    CROSSREF_API = "https://api.crossref.org/works"
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def extract_doi(self, text: str) -> Optional[str]:
        """
        Extract a DOI from text.
        
        Args:
            text: Text that may contain a DOI
            
        Returns:
            Extracted DOI or None
        """
        patterns = [
            r'10\.\d{4,}/[^\s\]]+',
            r'doi:?\s*(10\.\d{4,}/[^\s\]]+)',
            r'https?://doi\.org/(10\.\d{4,}/[^\s\]]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                doi = match.group(1) if match.lastindex else match.group(0)
                # Clean up common trailing characters
                doi = doi.rstrip('.,;:)\'"')
                return doi
        
        return None
    
    async def resolve(self, doi: str) -> DOIMetadata:
        """
        Resolve a DOI to get its metadata.
        
        Args:
            doi: The DOI to resolve
            
        Returns:
            DOIMetadata with resolved information
        """
        metadata = DOIMetadata(doi=doi)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Try CrossRef first for structured metadata
                async with session.get(
                    f"{self.CROSSREF_API}/{doi}",
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers={"Accept": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        message = data.get("message", {})
                        
                        metadata.title = message.get("title", [None])[0]
                        
                        # Extract authors
                        authors = message.get("author", [])
                        metadata.authors = [
                            f"{a.get('given', '')} {a.get('family', '')}".strip()
                            for a in authors
                        ]
                        
                        # Extract year
                        published = message.get("published-print") or message.get("published-online")
                        if published:
                            date_parts = published.get("date-parts", [[]])[0]
                            if date_parts:
                                metadata.year = date_parts[0]
                        
                        metadata.journal = message.get("container-title", [None])[0]
                        metadata.url = message.get("URL")
                        metadata.abstract = message.get("abstract")
                        metadata.resolved = True
                        
                        return metadata
                    
                    elif response.status == 404:
                        metadata.error = "DOI not found in CrossRef"
                        
        except asyncio.TimeoutError:
            metadata.error = "Timeout while resolving DOI"
        except Exception as e:
            metadata.error = str(e)
        
        # If CrossRef failed, try direct doi.org resolution
        if not metadata.resolved:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"https://doi.org/{doi}",
                        timeout=aiohttp.ClientTimeout(total=self.timeout),
                        allow_redirects=True
                    ) as response:
                        if response.status == 200:
                            metadata.url = str(response.url)
                            metadata.resolved = True
                            metadata.error = None
            except Exception as e:
                if not metadata.error:
                    metadata.error = str(e)
        
        return metadata
    
    async def batch_resolve(self, dois: List[str]) -> List[DOIMetadata]:
        """
        Resolve multiple DOIs concurrently.
        
        Args:
            dois: List of DOIs to resolve
            
        Returns:
            List of DOIMetadata in same order
        """
        tasks = [self.resolve(doi) for doi in dois]
        return await asyncio.gather(*tasks)
    
    def format_citation(
        self,
        metadata: DOIMetadata,
        style: str = "apa"
    ) -> str:
        """
        Format metadata as a citation string.
        
        Args:
            metadata: The resolved metadata
            style: Citation style (apa, mla, chicago)
            
        Returns:
            Formatted citation string
        """
        if not metadata.resolved:
            return f"[Unresolved DOI: {metadata.doi}]"
        
        authors = ", ".join(metadata.authors) if metadata.authors else "Unknown"
        year = metadata.year or "n.d."
        title = metadata.title or "Untitled"
        journal = metadata.journal or ""
        
        if style == "apa":
            citation = f"{authors} ({year}). {title}."
            if journal:
                citation += f" {journal}."
            citation += f" https://doi.org/{metadata.doi}"
            return citation
        
        elif style == "mla":
            citation = f'{authors}. "{title}."'
            if journal:
                citation += f" {journal},"
            citation += f" {year}. https://doi.org/{metadata.doi}"
            return citation
        
        else:  # Default format
            return f"{authors} ({year}). {title}. DOI: {metadata.doi}"
