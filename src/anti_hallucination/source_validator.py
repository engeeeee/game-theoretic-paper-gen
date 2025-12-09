"""
Source Validator

Validates that sources exist and are accessible.
Part of the anti-hallucination triple layer.
"""

import asyncio
import aiohttp
import re
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class SourceStatus(Enum):
    """Status of a source."""
    ACCESSIBLE = "accessible"
    PAYWALL = "paywall"
    NOT_FOUND = "not_found"
    INVALID_FORMAT = "invalid_format"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class SourceValidation:
    """Result of source validation."""
    source: str
    status: SourceStatus
    http_status: Optional[int] = None
    final_url: Optional[str] = None
    content_type: Optional[str] = None
    error_message: Optional[str] = None
    is_academic: bool = False


class SourceValidator:
    """
    Validates sources by checking accessibility.
    
    Checks:
    - URL accessibility
    - DOI resolution
    - Academic source detection
    """
    
    # Known academic domains
    ACADEMIC_DOMAINS = [
        "doi.org", "arxiv.org", "pubmed", "ncbi.nlm.nih.gov",
        "springer.com", "wiley.com", "sciencedirect.com",
        "nature.com", "science.org", "jstor.org", "ieee.org",
        "acm.org", "plos.org", "frontiersin.org", "mdpi.com",
        "semanticscholar.org", "researchgate.net", "academia.edu"
    ]
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    async def validate_url(self, url: str) -> SourceValidation:
        """
        Validate a URL by checking if it's accessible.
        
        Args:
            url: URL to validate
            
        Returns:
            SourceValidation with results
        """
        validation = SourceValidation(
            source=url,
            status=SourceStatus.ERROR
        )
        
        # Validate URL format
        if not self._is_valid_url(url):
            validation.status = SourceStatus.INVALID_FORMAT
            validation.error_message = "Invalid URL format"
            return validation
        
        # Check if academic domain
        validation.is_academic = self._is_academic_url(url)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(
                    url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    allow_redirects=True,
                    headers={"User-Agent": "Mozilla/5.0 (Academic Citation Validator)"}
                ) as response:
                    validation.http_status = response.status
                    validation.final_url = str(response.url)
                    validation.content_type = response.headers.get("Content-Type")
                    
                    if response.status == 200:
                        validation.status = SourceStatus.ACCESSIBLE
                    elif response.status in [401, 403]:
                        validation.status = SourceStatus.PAYWALL
                    elif response.status == 404:
                        validation.status = SourceStatus.NOT_FOUND
                    else:
                        validation.status = SourceStatus.ERROR
                        validation.error_message = f"HTTP {response.status}"
                        
        except asyncio.TimeoutError:
            validation.status = SourceStatus.TIMEOUT
            validation.error_message = "Request timed out"
        except aiohttp.ClientError as e:
            validation.status = SourceStatus.ERROR
            validation.error_message = str(e)
        except Exception as e:
            validation.status = SourceStatus.ERROR
            validation.error_message = str(e)
        
        return validation
    
    async def validate_doi(self, doi: str) -> SourceValidation:
        """
        Validate a DOI by attempting resolution.
        
        Args:
            doi: DOI to validate
            
        Returns:
            SourceValidation with results
        """
        url = f"https://doi.org/{doi}"
        validation = await self.validate_url(url)
        validation.source = f"DOI:{doi}"
        validation.is_academic = True
        return validation
    
    async def batch_validate(
        self,
        sources: List[str]
    ) -> List[SourceValidation]:
        """
        Validate multiple sources concurrently.
        
        Args:
            sources: List of URLs or DOIs
            
        Returns:
            List of SourceValidation results
        """
        tasks = []
        for source in sources:
            if source.startswith("10.") or "doi.org" in source:
                # It's a DOI
                doi = self._extract_doi(source)
                if doi:
                    tasks.append(self.validate_doi(doi))
                else:
                    tasks.append(self.validate_url(source))
            else:
                tasks.append(self.validate_url(source))
        
        return await asyncio.gather(*tasks)
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if a string is a valid URL."""
        pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$',
            re.IGNORECASE
        )
        return bool(pattern.match(url))
    
    def _is_academic_url(self, url: str) -> bool:
        """Check if URL is from an academic domain."""
        url_lower = url.lower()
        return any(domain in url_lower for domain in self.ACADEMIC_DOMAINS)
    
    def _extract_doi(self, text: str) -> Optional[str]:
        """Extract DOI from text."""
        match = re.search(r'10\.\d{4,}/[^\s]+', text)
        if match:
            return match.group(0).rstrip('.,;:)\'"')
        return None
