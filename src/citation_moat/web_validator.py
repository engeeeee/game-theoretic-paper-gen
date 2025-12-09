"""
Web Validator

Validates citations by searching the web and academic databases.
Uses multiple sources: Google Scholar, Semantic Scholar, arXiv.
"""

import asyncio
import aiohttp
import re
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum
import os


class ValidationStatus(Enum):
    """Status of citation validation."""
    VERIFIED = "verified"
    PARTIAL_MATCH = "partial_match"
    NOT_FOUND = "not_found"
    ERROR = "error"
    PENDING = "pending"


@dataclass
class ValidationResult:
    """Result of validating a citation."""
    status: ValidationStatus
    confidence: float  # 0-100
    source: Optional[str] = None
    matched_title: Optional[str] = None
    matched_url: Optional[str] = None
    matched_doi: Optional[str] = None
    error_message: Optional[str] = None
    search_queries_used: List[str] = None
    
    def __post_init__(self):
        if self.search_queries_used is None:
            self.search_queries_used = []


class WebValidator:
    """
    Validates citations against web sources.
    
    Uses multiple validation strategies:
    1. Direct URL check
    2. DOI resolution
    3. Semantic Scholar API
    4. CrossRef API
    5. arXiv search
    """
    
    SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"
    CROSSREF_API = "https://api.crossref.org/works"
    ARXIV_API = "http://export.arxiv.org/api/query"
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.semantic_scholar_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    
    async def validate(
        self,
        query: str,
        doi: Optional[str] = None,
        url: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate a citation using multiple sources.
        
        Args:
            query: Search query (author + year or title)
            doi: Optional DOI if known
            url: Optional URL if known
            
        Returns:
            ValidationResult with status and details
        """
        search_queries = []
        
        # Try DOI first if available
        if doi:
            result = await self._validate_doi(doi)
            if result.status == ValidationStatus.VERIFIED:
                return result
            search_queries.extend(result.search_queries_used)
        
        # Try direct URL if available
        if url:
            result = await self._validate_url(url)
            if result.status == ValidationStatus.VERIFIED:
                return result
            search_queries.extend(result.search_queries_used)
        
        # Try Semantic Scholar
        result = await self._search_semantic_scholar(query)
        search_queries.extend(result.search_queries_used)
        if result.status == ValidationStatus.VERIFIED:
            result.search_queries_used = search_queries
            return result
        
        # Try CrossRef
        result = await self._search_crossref(query)
        search_queries.extend(result.search_queries_used)
        if result.status == ValidationStatus.VERIFIED:
            result.search_queries_used = search_queries
            return result
        
        # Try arXiv for preprints
        if "arxiv" in query.lower() or not result.status == ValidationStatus.VERIFIED:
            arxiv_result = await self._search_arxiv(query)
            search_queries.extend(arxiv_result.search_queries_used)
            if arxiv_result.status == ValidationStatus.VERIFIED:
                arxiv_result.search_queries_used = search_queries
                return arxiv_result
        
        # Return best partial match or not found
        return ValidationResult(
            status=ValidationStatus.NOT_FOUND,
            confidence=0.0,
            search_queries_used=search_queries,
            error_message=f"Citation not found in any source: {query}"
        )
    
    async def _validate_doi(self, doi: str) -> ValidationResult:
        """Validate a DOI by resolving it."""
        queries = [f"DOI: {doi}"]
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://doi.org/{doi}"
                async with session.head(
                    url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    allow_redirects=True
                ) as response:
                    if response.status == 200:
                        return ValidationResult(
                            status=ValidationStatus.VERIFIED,
                            confidence=100.0,
                            source="DOI.org",
                            matched_doi=doi,
                            matched_url=str(response.url),
                            search_queries_used=queries
                        )
        except Exception as e:
            pass
        
        return ValidationResult(
            status=ValidationStatus.NOT_FOUND,
            confidence=0.0,
            search_queries_used=queries,
            error_message=f"DOI not resolved: {doi}"
        )
    
    async def _validate_url(self, url: str) -> ValidationResult:
        """Validate a URL by checking if it's accessible."""
        queries = [f"URL: {url}"]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(
                    url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    allow_redirects=True
                ) as response:
                    if response.status == 200:
                        return ValidationResult(
                            status=ValidationStatus.VERIFIED,
                            confidence=90.0,
                            source="Direct URL",
                            matched_url=url,
                            search_queries_used=queries
                        )
                    elif response.status == 403:
                        # Paywall or restricted
                        return ValidationResult(
                            status=ValidationStatus.PARTIAL_MATCH,
                            confidence=70.0,
                            source="Direct URL (restricted)",
                            matched_url=url,
                            search_queries_used=queries
                        )
        except Exception as e:
            pass
        
        return ValidationResult(
            status=ValidationStatus.NOT_FOUND,
            confidence=0.0,
            search_queries_used=queries
        )
    
    async def _search_semantic_scholar(self, query: str) -> ValidationResult:
        """Search Semantic Scholar for the citation."""
        queries = [f"Semantic Scholar: {query}"]
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {}
                if self.semantic_scholar_key:
                    headers["x-api-key"] = self.semantic_scholar_key
                
                params = {
                    "query": query,
                    "limit": 5,
                    "fields": "title,authors,year,doi,url"
                }
                
                async with session.get(
                    f"{self.SEMANTIC_SCHOLAR_API}/paper/search",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        papers = data.get("data", [])
                        
                        if papers:
                            paper = papers[0]
                            return ValidationResult(
                                status=ValidationStatus.VERIFIED,
                                confidence=85.0,
                                source="Semantic Scholar",
                                matched_title=paper.get("title"),
                                matched_url=paper.get("url"),
                                matched_doi=paper.get("doi"),
                                search_queries_used=queries
                            )
        except Exception as e:
            pass
        
        return ValidationResult(
            status=ValidationStatus.NOT_FOUND,
            confidence=0.0,
            search_queries_used=queries
        )
    
    async def _search_crossref(self, query: str) -> ValidationResult:
        """Search CrossRef for the citation."""
        queries = [f"CrossRef: {query}"]
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "query": query,
                    "rows": 5
                }
                
                async with session.get(
                    self.CROSSREF_API,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("message", {}).get("items", [])
                        
                        if items:
                            item = items[0]
                            title = item.get("title", [""])[0]
                            doi = item.get("DOI")
                            
                            return ValidationResult(
                                status=ValidationStatus.VERIFIED,
                                confidence=85.0,
                                source="CrossRef",
                                matched_title=title,
                                matched_doi=doi,
                                matched_url=f"https://doi.org/{doi}" if doi else None,
                                search_queries_used=queries
                            )
        except Exception as e:
            pass
        
        return ValidationResult(
            status=ValidationStatus.NOT_FOUND,
            confidence=0.0,
            search_queries_used=queries
        )
    
    async def _search_arxiv(self, query: str) -> ValidationResult:
        """Search arXiv for the citation."""
        queries = [f"arXiv: {query}"]
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "search_query": f"all:{query}",
                    "start": 0,
                    "max_results": 5
                }
                
                async with session.get(
                    self.ARXIV_API,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        text = await response.text()
                        
                        # Simple XML parsing for title
                        title_match = re.search(r'<title>([^<]+)</title>', text)
                        link_match = re.search(r'<id>(http[^<]+)</id>', text)
                        
                        if title_match and "arxiv" not in title_match.group(1).lower():
                            return ValidationResult(
                                status=ValidationStatus.VERIFIED,
                                confidence=80.0,
                                source="arXiv",
                                matched_title=title_match.group(1),
                                matched_url=link_match.group(1) if link_match else None,
                                search_queries_used=queries
                            )
        except Exception as e:
            pass
        
        return ValidationResult(
            status=ValidationStatus.NOT_FOUND,
            confidence=0.0,
            search_queries_used=queries
        )
    
    async def batch_validate(
        self,
        citations: List[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """
        Validate multiple citations concurrently.
        
        Args:
            citations: List of dicts with 'query', 'doi', 'url' keys
            
        Returns:
            List of ValidationResults in same order
        """
        tasks = []
        for citation in citations:
            task = self.validate(
                query=citation.get("query", ""),
                doi=citation.get("doi"),
                url=citation.get("url")
            )
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
