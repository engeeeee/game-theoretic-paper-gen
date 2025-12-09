"""
Fact Checker

Cross-references claims against known facts.
Part of the anti-hallucination triple layer.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from enum import Enum


class FactStatus(Enum):
    """Status of fact verification."""
    VERIFIED = "verified"
    CONTRADICTED = "contradicted"
    UNVERIFIED = "unverified"
    PARTIALLY_VERIFIED = "partially_verified"


@dataclass
class FactCheckResult:
    """Result of fact checking a claim."""
    claim: str
    status: FactStatus
    confidence: float  # 0-100
    supporting_facts: List[str] = None
    contradicting_facts: List[str] = None
    sources_checked: List[str] = None
    explanation: str = ""
    
    def __post_init__(self):
        if self.supporting_facts is None:
            self.supporting_facts = []
        if self.contradicting_facts is None:
            self.contradicting_facts = []
        if self.sources_checked is None:
            self.sources_checked = []


class FactChecker:
    """
    Cross-references claims against known facts.
    
    Methods:
    - Contradiction detection between claims
    - Consistency checking
    - Basic fact validation
    """
    
    def __init__(self):
        # Simple knowledge base for demonstration
        # In production, this would connect to external fact-checking APIs
        self._known_facts = {}
    
    def check_claim(
        self,
        claim: str,
        context: Optional[str] = None,
        related_claims: Optional[List[str]] = None
    ) -> FactCheckResult:
        """
        Check a claim for factual accuracy.
        
        Args:
            claim: The claim to check
            context: Optional context for the claim
            related_claims: Other claims to check consistency against
            
        Returns:
            FactCheckResult with verification status
        """
        result = FactCheckResult(
            claim=claim,
            status=FactStatus.UNVERIFIED,
            confidence=50.0  # Default uncertainty
        )
        
        # Check for contradictions with related claims
        if related_claims:
            contradictions = self._find_contradictions(claim, related_claims)
            if contradictions:
                result.status = FactStatus.CONTRADICTED
                result.contradicting_facts = contradictions
                result.confidence = 30.0
                result.explanation = "Claim contradicts other statements"
                return result
        
        # Check for known patterns that might indicate fabrication
        fabrication_indicators = self._check_fabrication_indicators(claim)
        if fabrication_indicators:
            result.status = FactStatus.UNVERIFIED
            result.confidence = 20.0
            result.explanation = f"Potential fabrication indicators: {', '.join(fabrication_indicators)}"
            return result
        
        # If no issues found, mark as unverified (not confirmed)
        result.status = FactStatus.UNVERIFIED
        result.confidence = 50.0
        result.explanation = "Claim requires external verification"
        
        return result
    
    def check_consistency(
        self,
        claims: List[str]
    ) -> Tuple[bool, List[Tuple[str, str]]]:
        """
        Check if a list of claims is internally consistent.
        
        Args:
            claims: List of claims to check
            
        Returns:
            Tuple of (is_consistent, list of contradiction pairs)
        """
        contradictions = []
        
        for i, claim1 in enumerate(claims):
            for claim2 in claims[i + 1:]:
                if self._are_contradictory(claim1, claim2):
                    contradictions.append((claim1, claim2))
        
        return len(contradictions) == 0, contradictions
    
    def _find_contradictions(
        self,
        claim: str,
        other_claims: List[str]
    ) -> List[str]:
        """Find claims that contradict the given claim."""
        contradictions = []
        for other in other_claims:
            if self._are_contradictory(claim, other):
                contradictions.append(other)
        return contradictions
    
    def _are_contradictory(self, claim1: str, claim2: str) -> bool:
        """Check if two claims contradict each other."""
        claim1_lower = claim1.lower()
        claim2_lower = claim2.lower()
        
        # Simple negation patterns
        negation_patterns = [
            (r"(\w+) is (\w+)", r"\1 is not \2"),
            (r"(\w+) are (\w+)", r"\1 are not \2"),
            (r"(\w+) was (\w+)", r"\1 was not \2"),
            (r"(\w+) increases", r"\1 decreases"),
            (r"(\w+) improved", r"\1 worsened"),
            (r"supports", r"contradicts"),
            (r"confirms", r"denies"),
            (r"significant", r"insignificant"),
            (r"reliable", r"unreliable"),
            (r"valid", r"invalid"),
        ]
        
        for positive, negative in negation_patterns:
            # Check if one claim matches positive and other matches negative
            pos_match1 = re.search(positive, claim1_lower)
            neg_match2 = re.search(negative, claim2_lower)
            if pos_match1 and neg_match2:
                return True
            
            pos_match2 = re.search(positive, claim2_lower)
            neg_match1 = re.search(negative, claim1_lower)
            if pos_match2 and neg_match1:
                return True
        
        return False
    
    def _check_fabrication_indicators(self, claim: str) -> List[str]:
        """Check for indicators that a claim might be fabricated."""
        indicators = []
        claim_lower = claim.lower()
        
        # Check for overly specific but unverifiable details
        if re.search(r'\d{1,2}\.\d{1,5}%', claim):
            # Very precise percentages might be fabricated
            indicators.append("Suspiciously precise statistics")
        
        # Check for future predictions stated as fact
        future_patterns = [
            r"will definitely",
            r"is guaranteed to",
            r"will certainly",
        ]
        for pattern in future_patterns:
            if re.search(pattern, claim_lower):
                indicators.append("Absolute prediction stated as fact")
        
        # Check for universal claims without hedging
        universal_patterns = [
            r"all (\w+) (are|is)",
            r"every (\w+) (has|have)",
            r"no (\w+) (can|will)",
            r"never",
            r"always",
        ]
        for pattern in universal_patterns:
            if re.search(pattern, claim_lower):
                indicators.append("Universal claim without hedging")
        
        return indicators
    
    def batch_check(
        self,
        claims: List[str],
        check_consistency: bool = True
    ) -> List[FactCheckResult]:
        """
        Check multiple claims.
        
        Args:
            claims: List of claims to check
            check_consistency: Whether to check for internal consistency
            
        Returns:
            List of FactCheckResult
        """
        results = []
        
        for i, claim in enumerate(claims):
            # Get other claims for consistency check
            other_claims = claims[:i] + claims[i + 1:] if check_consistency else None
            result = self.check_claim(claim, related_claims=other_claims)
            results.append(result)
        
        return results
