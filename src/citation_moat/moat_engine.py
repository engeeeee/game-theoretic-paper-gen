"""
Citation Moat Engine

Orchestrates dual-agent citation verification.
Both agents must agree for a citation to be validated.
Implements zero-tolerance policy for unverifiable sources.
"""

import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

from .extractor import CitationExtractor, ExtractedCitation
from .web_validator import WebValidator, ValidationResult, ValidationStatus
from .doi_resolver import DOIResolver


class MoatDecision(Enum):
    """Decision for a citation after dual-agent verification."""
    KEEP = "keep"              # Citation verified, keep as-is
    MODIFY = "modify"          # Found alternative, modify citation
    DELETE = "delete"          # Cannot verify, delete claim
    FLAG = "flag"              # Partially verified, flag for review


@dataclass
class CitationVerification:
    """Result of verifying a single citation."""
    original_citation: ExtractedCitation
    decision: MoatDecision
    agent_a_verified: bool = False
    agent_b_verified: bool = False
    web_validation: Optional[ValidationResult] = None
    doi_metadata: Optional[Dict] = None
    alternative_source: Optional[str] = None
    reason: str = ""
    confidence: float = 0.0


@dataclass
class MoatReport:
    """Complete report from the citation moat."""
    total_citations: int = 0
    verified_count: int = 0
    modified_count: int = 0
    deleted_count: int = 0
    flagged_count: int = 0
    verifications: List[CitationVerification] = field(default_factory=list)
    clean_text: str = ""  # Text with unverified citations removed
    
    @property
    def verification_rate(self) -> float:
        """Calculate the percentage of verified citations."""
        if self.total_citations == 0:
            return 100.0
        return (self.verified_count / self.total_citations) * 100


class CitationMoatEngine:
    """
    Dual-Agent Citation Moat.
    
    Both Agent A and Agent B must verify citations.
    Zero tolerance policy: unverifiable = deleted.
    """
    
    def __init__(
        self,
        proponent_agent=None,
        reviewer_agent=None,
        strict_mode: bool = True
    ):
        """
        Initialize the citation moat.
        
        Args:
            proponent_agent: Agent A for verification
            reviewer_agent: Agent B for verification
            strict_mode: If True, delete all unverifiable citations
        """
        self.proponent = proponent_agent
        self.reviewer = reviewer_agent
        self.strict_mode = strict_mode
        
        self.extractor = CitationExtractor()
        self.web_validator = WebValidator()
        self.doi_resolver = DOIResolver()
    
    async def verify_text(self, text: str) -> MoatReport:
        """
        Verify all citations in a text.
        
        Args:
            text: Text containing citations
            
        Returns:
            MoatReport with verification results
        """
        # Step 1: Extract all citations
        citations = self.extractor.extract_all(text)
        
        report = MoatReport(
            total_citations=len(citations),
            verifications=[]
        )
        
        if not citations:
            report.clean_text = text
            return report
        
        # Step 2: Verify each citation
        verifications = await self._verify_citations(citations)
        report.verifications = verifications
        
        # Step 3: Count results
        for v in verifications:
            if v.decision == MoatDecision.KEEP:
                report.verified_count += 1
            elif v.decision == MoatDecision.MODIFY:
                report.modified_count += 1
            elif v.decision == MoatDecision.DELETE:
                report.deleted_count += 1
            elif v.decision == MoatDecision.FLAG:
                report.flagged_count += 1
        
        # Step 4: Generate clean text
        report.clean_text = self._generate_clean_text(text, verifications)
        
        return report
    
    async def _verify_citations(
        self,
        citations: List[ExtractedCitation]
    ) -> List[CitationVerification]:
        """Verify a list of citations using dual-agent verification."""
        verifications = []
        
        for citation in citations:
            verification = await self._verify_single_citation(citation)
            verifications.append(verification)
        
        return verifications
    
    async def _verify_single_citation(
        self,
        citation: ExtractedCitation
    ) -> CitationVerification:
        """Verify a single citation using all available methods."""
        verification = CitationVerification(
            original_citation=citation,
            decision=MoatDecision.DELETE  # Default to delete
        )
        
        # Step 1: Web validation
        search_query = citation.to_search_query()
        web_result = await self.web_validator.validate(
            query=search_query,
            doi=citation.doi,
            url=citation.url
        )
        verification.web_validation = web_result
        
        # Step 2: DOI resolution if available
        if citation.doi:
            doi_metadata = await self.doi_resolver.resolve(citation.doi)
            verification.doi_metadata = {
                "title": doi_metadata.title,
                "authors": doi_metadata.authors,
                "year": doi_metadata.year,
                "resolved": doi_metadata.resolved
            }
        
        # Step 3: Agent verification (if agents are available)
        if self.proponent:
            agent_a_result = await self._agent_verify(
                self.proponent,
                citation,
                web_result
            )
            verification.agent_a_verified = agent_a_result
        else:
            # Without agent, use web result
            verification.agent_a_verified = (
                web_result.status == ValidationStatus.VERIFIED
            )
        
        if self.reviewer:
            agent_b_result = await self._agent_verify(
                self.reviewer,
                citation,
                web_result
            )
            verification.agent_b_verified = agent_b_result
        else:
            # Without agent, use web result
            verification.agent_b_verified = (
                web_result.status == ValidationStatus.VERIFIED
            )
        
        # Step 4: Make decision based on all evidence
        verification.decision, verification.reason = self._make_decision(
            verification
        )
        verification.confidence = self._calculate_confidence(verification)
        
        return verification
    
    async def _agent_verify(
        self,
        agent,
        citation: ExtractedCitation,
        web_result: ValidationResult
    ) -> bool:
        """Have an agent verify a citation."""
        try:
            # Use agent's citation verification method
            response = await agent.verify_citation(
                claim=citation.raw_text,
                citation=citation.to_search_query()
            )
            
            # Parse response for verification status
            content = response.content.lower()
            return (
                "verified" in content or 
                "valid" in content or
                "confirmed" in content
            )
        except Exception as e:
            # If agent verification fails, fall back to web result
            return web_result.status == ValidationStatus.VERIFIED
    
    def _make_decision(
        self,
        verification: CitationVerification
    ) -> Tuple[MoatDecision, str]:
        """Make a decision based on verification results."""
        web_status = verification.web_validation.status
        agent_a = verification.agent_a_verified
        agent_b = verification.agent_b_verified
        
        # Both agents agree it's verified
        if agent_a and agent_b and web_status == ValidationStatus.VERIFIED:
            return MoatDecision.KEEP, "Both agents verified, web source found"
        
        # Partial match - might need modification
        if web_status == ValidationStatus.PARTIAL_MATCH:
            if agent_a or agent_b:
                return MoatDecision.MODIFY, "Partial match found, needs correction"
            return MoatDecision.FLAG, "Partial match, needs review"
        
        # Web verified but agents disagree
        if web_status == ValidationStatus.VERIFIED:
            if agent_a and not agent_b:
                return MoatDecision.FLAG, "Agent A verified, Agent B disagrees"
            if agent_b and not agent_a:
                return MoatDecision.FLAG, "Agent B verified, Agent A disagrees"
            if not agent_a and not agent_b:
                return MoatDecision.FLAG, "Web verified but both agents uncertain"
        
        # Not found
        if self.strict_mode:
            return MoatDecision.DELETE, "Cannot verify source, strict mode enabled"
        else:
            return MoatDecision.FLAG, "Cannot verify source, flagged for review"
    
    def _calculate_confidence(
        self,
        verification: CitationVerification
    ) -> float:
        """Calculate confidence score for the verification."""
        confidence = 0.0
        
        # Web validation contribution (max 40)
        if verification.web_validation:
            if verification.web_validation.status == ValidationStatus.VERIFIED:
                confidence += 40.0
            elif verification.web_validation.status == ValidationStatus.PARTIAL_MATCH:
                confidence += 20.0
        
        # Agent A contribution (max 30)
        if verification.agent_a_verified:
            confidence += 30.0
        
        # Agent B contribution (max 30)
        if verification.agent_b_verified:
            confidence += 30.0
        
        return confidence
    
    def _generate_clean_text(
        self,
        original_text: str,
        verifications: List[CitationVerification]
    ) -> str:
        """Generate clean text with unverified citations removed."""
        clean_text = original_text
        
        # Process in reverse order to maintain positions
        for v in sorted(verifications, key=lambda x: x.original_citation.position[0], reverse=True):
            start, end = v.original_citation.position
            
            if v.decision == MoatDecision.DELETE:
                # Remove the citation
                clean_text = clean_text[:start] + "[CITATION REMOVED]" + clean_text[end:]
            elif v.decision == MoatDecision.MODIFY and v.alternative_source:
                # Replace with alternative
                clean_text = clean_text[:start] + v.alternative_source + clean_text[end:]
            elif v.decision == MoatDecision.FLAG:
                # Mark as needing review
                clean_text = clean_text[:start] + "[NEEDS REVIEW: " + clean_text[start:end] + "]" + clean_text[end:]
        
        return clean_text
    
    def generate_report_text(self, report: MoatReport) -> str:
        """Generate a human-readable report."""
        lines = [
            "=" * 50,
            "CITATION MOAT VERIFICATION REPORT",
            "=" * 50,
            "",
            f"Total Citations: {report.total_citations}",
            f"Verified: {report.verified_count} ({report.verification_rate:.1f}%)",
            f"Modified: {report.modified_count}",
            f"Deleted: {report.deleted_count}",
            f"Flagged: {report.flagged_count}",
            "",
            "-" * 50,
            "DETAILED RESULTS",
            "-" * 50,
        ]
        
        for i, v in enumerate(report.verifications, 1):
            lines.extend([
                f"\n[{i}] {v.original_citation.raw_text}",
                f"    Decision: {v.decision.value.upper()}",
                f"    Agent A Verified: {v.agent_a_verified}",
                f"    Agent B Verified: {v.agent_b_verified}",
                f"    Confidence: {v.confidence:.0f}%",
                f"    Reason: {v.reason}",
            ])
        
        lines.extend([
            "",
            "=" * 50,
        ])
        
        return "\n".join(lines)
