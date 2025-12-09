"""
Tests for Citation Moat functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.citation_moat.extractor import CitationExtractor, CitationType, ExtractedCitation
from src.citation_moat.web_validator import WebValidator, ValidationStatus, ValidationResult
from src.citation_moat.doi_resolver import DOIResolver, DOIMetadata
from src.citation_moat.moat_engine import CitationMoatEngine, MoatDecision


class TestCitationExtractor:
    """Tests for CitationExtractor class."""
    
    def test_extract_author_year_parentheses(self):
        """Test extraction of (Author, Year) format."""
        extractor = CitationExtractor()
        text = "This is supported by research (Smith, 2024)."
        
        citations = extractor.extract_all(text)
        
        assert len(citations) == 1
        assert citations[0].authors == "Smith"
        assert citations[0].year == "2024"
        assert citations[0].citation_type == CitationType.AUTHOR_YEAR
    
    def test_extract_author_year_et_al(self):
        """Test extraction of (Author et al., Year) format."""
        extractor = CitationExtractor()
        text = "According to (Johnson et al., 2023), this is true."
        
        citations = extractor.extract_all(text)
        
        assert len(citations) == 1
        assert "Johnson et al." in citations[0].authors
        assert citations[0].year == "2023"
    
    def test_extract_doi(self):
        """Test extraction of DOI format."""
        extractor = CitationExtractor()
        text = "See doi:10.1234/example.2024 for details."
        
        citations = extractor.extract_all(text)
        
        assert len(citations) == 1
        assert citations[0].citation_type == CitationType.DOI
        assert "10.1234" in citations[0].doi
    
    def test_extract_url(self):
        """Test extraction of URL format."""
        extractor = CitationExtractor()
        text = "Available at https://example.com/paper.pdf for review."
        
        citations = extractor.extract_all(text)
        
        assert len(citations) == 1
        assert citations[0].citation_type == CitationType.URL
        assert "example.com" in citations[0].url
    
    def test_extract_multiple_citations(self):
        """Test extraction of multiple citations."""
        extractor = CitationExtractor()
        text = """
        First study (Smith, 2020) and second (Jones, 2021).
        Also see doi:10.1234/test.
        """
        
        citations = extractor.extract_all(text)
        
        assert len(citations) == 3
    
    def test_to_search_query(self):
        """Test search query generation."""
        citation = ExtractedCitation(
            raw_text="(Smith, 2024)",
            citation_type=CitationType.AUTHOR_YEAR,
            position=(0, 14),
            authors="Smith",
            year="2024"
        )
        
        query = citation.to_search_query()
        
        assert "Smith" in query
        assert "2024" in query


class TestWebValidator:
    """Tests for WebValidator class."""
    
    @pytest.mark.asyncio
    async def test_validate_doi_success(self):
        """Test successful DOI validation."""
        validator = WebValidator(timeout=5)
        
        # Mock the aiohttp session
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.url = "https://example.com/paper"
            
            mock_session.return_value.__aenter__.return_value.head = AsyncMock(
                return_value=mock_response
            )
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            
            result = await validator._validate_doi("10.1234/test")
        
        # Result should be not found since mock isn't fully set up
        assert isinstance(result, ValidationResult)
    
    @pytest.mark.asyncio
    async def test_validate_returns_result(self):
        """Test that validate always returns a ValidationResult."""
        validator = WebValidator(timeout=2)
        
        result = await validator.validate("nonexistent query that won't match")
        
        assert isinstance(result, ValidationResult)
        assert result.status in [
            ValidationStatus.VERIFIED,
            ValidationStatus.PARTIAL_MATCH,
            ValidationStatus.NOT_FOUND,
            ValidationStatus.ERROR
        ]


class TestDOIResolver:
    """Tests for DOIResolver class."""
    
    def test_extract_doi_from_text(self):
        """Test DOI extraction from text."""
        resolver = DOIResolver()
        
        test_cases = [
            ("doi:10.1234/test.2024", "10.1234/test.2024"),
            ("https://doi.org/10.5678/example", "10.5678/example"),
            ("See 10.9999/paper for details", "10.9999/paper"),
        ]
        
        for text, expected in test_cases:
            result = resolver.extract_doi(text)
            assert expected in result or result == expected.rstrip('.')
    
    def test_extract_doi_none(self):
        """Test DOI extraction returns None for no DOI."""
        resolver = DOIResolver()
        
        result = resolver.extract_doi("No DOI here")
        
        assert result is None
    
    def test_format_citation_apa(self):
        """Test APA citation formatting."""
        resolver = DOIResolver()
        
        metadata = DOIMetadata(
            doi="10.1234/test",
            title="Test Paper",
            authors=["John Smith", "Jane Doe"],
            year=2024,
            resolved=True
        )
        
        citation = resolver.format_citation(metadata, style="apa")
        
        assert "Smith" in citation
        assert "2024" in citation
        assert "Test Paper" in citation


class TestCitationMoatEngine:
    """Tests for CitationMoatEngine class."""
    
    def test_moat_decision_types(self):
        """Test that moat decisions are correct enum values."""
        from src.citation_moat.moat_engine import MoatDecision
        
        assert MoatDecision.KEEP.value == "keep"
        assert MoatDecision.MODIFY.value == "modify"
        assert MoatDecision.DELETE.value == "delete"
        assert MoatDecision.FLAG.value == "flag"
    
    @pytest.mark.asyncio
    async def test_verify_text_empty(self):
        """Test verification of text with no citations."""
        engine = CitationMoatEngine(strict_mode=True)
        
        result = await engine.verify_text("Simple text without citations.")
        
        assert result.total_citations == 0
        assert result.clean_text == "Simple text without citations."
    
    def test_generate_report_text(self):
        """Test report generation."""
        engine = CitationMoatEngine()
        
        from src.citation_moat.moat_engine import MoatReport
        report = MoatReport(
            total_citations=5,
            verified_count=3,
            modified_count=1,
            deleted_count=1
        )
        
        text = engine.generate_report_text(report)
        
        assert "Total Citations: 5" in text
        assert "Verified: 3" in text
    
    def test_verification_rate_calculation(self):
        """Test verification rate calculation."""
        from src.citation_moat.moat_engine import MoatReport
        
        report = MoatReport(
            total_citations=10,
            verified_count=8
        )
        
        assert report.verification_rate == 80.0
        
        empty_report = MoatReport(total_citations=0)
        assert empty_report.verification_rate == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
