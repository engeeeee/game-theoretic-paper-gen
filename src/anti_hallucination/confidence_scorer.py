"""
Confidence Scorer

Calculates confidence scores for claims based on evidence.
Part of the anti-hallucination triple layer.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum


class EvidenceStrength(Enum):
    """Strength of supporting evidence."""
    STRONG = "strong"          # Primary source, peer-reviewed
    MODERATE = "moderate"      # Secondary source, reputable
    WEAK = "weak"              # Opinion, blog, or unverified
    NONE = "none"              # No evidence provided


@dataclass
class ClaimConfidence:
    """Confidence assessment for a claim."""
    claim: str
    score: float  # 0-100
    evidence_strength: EvidenceStrength
    has_citation: bool
    citation_verified: bool
    is_opinion: bool
    is_inference: bool
    factors: Dict[str, float] = None
    recommendation: str = ""
    
    def __post_init__(self):
        if self.factors is None:
            self.factors = {}


class ConfidenceScorer:
    """
    Calculates confidence scores for claims.
    
    Scoring factors:
    - Citation presence (0-30 points)
    - Citation verification (0-25 points)
    - Source quality (0-20 points)
    - Claim type (0-15 points)
    - Consistency (0-10 points)
    """
    
    # Weights for different factors
    WEIGHTS = {
        "citation_presence": 30.0,
        "citation_verified": 25.0,
        "source_quality": 20.0,
        "claim_type": 15.0,
        "consistency": 10.0,
    }
    
    # Thresholds
    THRESHOLD_HIGH = 80.0
    THRESHOLD_MEDIUM = 60.0
    THRESHOLD_LOW = 40.0
    
    def score_claim(
        self,
        claim: str,
        has_citation: bool = False,
        citation_verified: bool = False,
        is_primary_source: bool = False,
        is_opinion: bool = False,
        is_inference: bool = False,
        consistency_score: float = 100.0
    ) -> ClaimConfidence:
        """
        Calculate confidence score for a claim.
        
        Args:
            claim: The claim text
            has_citation: Whether claim has a citation
            citation_verified: Whether citation was verified
            is_primary_source: Whether citing primary source
            is_opinion: Whether marked as opinion
            is_inference: Whether marked as inference
            consistency_score: Consistency with other claims (0-100)
            
        Returns:
            ClaimConfidence with score and details
        """
        factors = {}
        
        # Factor 1: Citation presence
        if has_citation:
            factors["citation_presence"] = self.WEIGHTS["citation_presence"]
        else:
            factors["citation_presence"] = 0.0
        
        # Factor 2: Citation verification
        if citation_verified:
            factors["citation_verified"] = self.WEIGHTS["citation_verified"]
        elif has_citation:
            factors["citation_verified"] = self.WEIGHTS["citation_verified"] * 0.3
        else:
            factors["citation_verified"] = 0.0
        
        # Factor 3: Source quality
        if is_primary_source:
            factors["source_quality"] = self.WEIGHTS["source_quality"]
        elif has_citation:
            factors["source_quality"] = self.WEIGHTS["source_quality"] * 0.6
        else:
            factors["source_quality"] = 0.0
        
        # Factor 4: Claim type
        if is_opinion:
            factors["claim_type"] = self.WEIGHTS["claim_type"] * 0.4
        elif is_inference:
            factors["claim_type"] = self.WEIGHTS["claim_type"] * 0.7
        else:
            factors["claim_type"] = self.WEIGHTS["claim_type"]
        
        # Factor 5: Consistency
        factors["consistency"] = (consistency_score / 100.0) * self.WEIGHTS["consistency"]
        
        # Calculate total score
        score = sum(factors.values())
        
        # Determine evidence strength
        if citation_verified and is_primary_source:
            evidence_strength = EvidenceStrength.STRONG
        elif citation_verified or (has_citation and is_primary_source):
            evidence_strength = EvidenceStrength.MODERATE
        elif has_citation:
            evidence_strength = EvidenceStrength.WEAK
        else:
            evidence_strength = EvidenceStrength.NONE
        
        # Generate recommendation
        recommendation = self._get_recommendation(score, has_citation, citation_verified)
        
        return ClaimConfidence(
            claim=claim,
            score=score,
            evidence_strength=evidence_strength,
            has_citation=has_citation,
            citation_verified=citation_verified,
            is_opinion=is_opinion,
            is_inference=is_inference,
            factors=factors,
            recommendation=recommendation
        )
    
    def _get_recommendation(
        self,
        score: float,
        has_citation: bool,
        citation_verified: bool
    ) -> str:
        """Generate recommendation based on score."""
        if score >= self.THRESHOLD_HIGH:
            return "ACCEPT: High confidence, well-supported claim"
        elif score >= self.THRESHOLD_MEDIUM:
            if not citation_verified:
                return "VERIFY: Citation needs verification"
            return "REVIEW: Moderate confidence, may need additional support"
        elif score >= self.THRESHOLD_LOW:
            if not has_citation:
                return "CITE: Needs citation to support claim"
            return "STRENGTHEN: Weak evidence, needs better sources"
        else:
            return "REJECT: Insufficient evidence, consider removing"
    
    def batch_score(
        self,
        claims: List[Dict]
    ) -> List[ClaimConfidence]:
        """
        Score multiple claims.
        
        Args:
            claims: List of claim dicts with scoring parameters
            
        Returns:
            List of ClaimConfidence results
        """
        results = []
        for claim_data in claims:
            result = self.score_claim(
                claim=claim_data.get("claim", ""),
                has_citation=claim_data.get("has_citation", False),
                citation_verified=claim_data.get("citation_verified", False),
                is_primary_source=claim_data.get("is_primary_source", False),
                is_opinion=claim_data.get("is_opinion", False),
                is_inference=claim_data.get("is_inference", False),
                consistency_score=claim_data.get("consistency_score", 100.0)
            )
            results.append(result)
        return results
    
    def get_average_confidence(
        self,
        confidences: List[ClaimConfidence]
    ) -> float:
        """Calculate average confidence across claims."""
        if not confidences:
            return 0.0
        return sum(c.score for c in confidences) / len(confidences)
    
    def get_summary(
        self,
        confidences: List[ClaimConfidence]
    ) -> Dict:
        """Get summary statistics for a list of claims."""
        if not confidences:
            return {
                "total": 0,
                "average": 0.0,
                "high_confidence": 0,
                "medium_confidence": 0,
                "low_confidence": 0,
                "reject": 0
            }
        
        return {
            "total": len(confidences),
            "average": self.get_average_confidence(confidences),
            "high_confidence": sum(1 for c in confidences if c.score >= self.THRESHOLD_HIGH),
            "medium_confidence": sum(1 for c in confidences if self.THRESHOLD_MEDIUM <= c.score < self.THRESHOLD_HIGH),
            "low_confidence": sum(1 for c in confidences if self.THRESHOLD_LOW <= c.score < self.THRESHOLD_MEDIUM),
            "reject": sum(1 for c in confidences if c.score < self.THRESHOLD_LOW)
        }
