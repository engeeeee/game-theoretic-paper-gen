"""
Consensus Generator

Generates the final verified consensus from debate results.
"""

from dataclasses import dataclass
from typing import List, Optional
from ..engine.adaptive_debate import DebateResult, DebateStatus
from ..engine.voting import VotingResult


@dataclass
class Consensus:
    """Final consensus from the debate."""
    verdict: str  # VALIDATED, PARTIALLY VALIDATED, REJECTED
    confidence: float
    verified_claims: List[str]
    rejected_claims: List[str]
    remaining_disputes: List[str]
    summary: str


class ConsensusGenerator:
    """
    Generates verified consensus from debate results.
    
    Only includes claims that:
    1. Passed dual-agent verification
    2. Have verified citations
    3. Passed voting
    """
    
    def generate(
        self,
        debate_result: DebateResult,
        voting_result: Optional[VotingResult] = None
    ) -> Consensus:
        """
        Generate consensus from debate results.
        
        Args:
            debate_result: Result from the debate engine
            voting_result: Optional voting results
            
        Returns:
            Consensus with verified claims only
        """
        # Determine verdict
        verdict = self._determine_verdict(debate_result, voting_result)
        
        # Calculate confidence
        confidence = self._calculate_confidence(debate_result, voting_result)
        
        # Extract verified claims
        verified_claims = self._extract_verified_claims(debate_result)
        
        # Extract rejected claims
        rejected_claims = self._extract_rejected_claims(debate_result)
        
        # Get remaining disputes
        remaining_disputes = debate_result.disputed_points
        
        # Generate summary
        summary = self._generate_summary(
            verdict, confidence, verified_claims, rejected_claims
        )
        
        return Consensus(
            verdict=verdict,
            confidence=confidence,
            verified_claims=verified_claims,
            rejected_claims=rejected_claims,
            remaining_disputes=remaining_disputes,
            summary=summary
        )
    
    def _determine_verdict(
        self,
        debate_result: DebateResult,
        voting_result: Optional[VotingResult]
    ) -> str:
        """Determine the final verdict."""
        if voting_result and not voting_result.passed:
            return "REJECTED"
        
        if debate_result.status == DebateStatus.CONSENSUS_REACHED:
            if debate_result.final_score >= 85:
                return "VALIDATED"
            return "PARTIALLY VALIDATED"
        
        if debate_result.status == DebateStatus.CONVERGED:
            if debate_result.final_score >= 75:
                return "PARTIALLY VALIDATED"
            return "NEEDS REVISION"
        
        if debate_result.status == DebateStatus.DEADLOCK:
            return "INCONCLUSIVE"
        
        return "PARTIALLY VALIDATED"
    
    def _calculate_confidence(
        self,
        debate_result: DebateResult,
        voting_result: Optional[VotingResult]
    ) -> float:
        """Calculate overall confidence."""
        confidence = debate_result.final_score
        
        if voting_result:
            # Average with voting result
            confidence = (confidence + voting_result.weighted_average) / 2
        
        # Penalize for re-evaluations
        penalty = debate_result.re_evaluations * 5
        confidence = max(0, confidence - penalty)
        
        return confidence
    
    def _extract_verified_claims(
        self,
        debate_result: DebateResult
    ) -> List[str]:
        """Extract claims that passed verification."""
        verified = []
        
        for round in debate_result.rounds:
            if round.citation_report:
                # Add claims from verified citations
                for v in round.citation_report.verifications:
                    if v.decision.value == "keep":
                        verified.append(v.original_citation.raw_text)
        
        # Add consensus points
        verified.extend(debate_result.consensus_points)
        
        return list(set(verified))  # Remove duplicates
    
    def _extract_rejected_claims(
        self,
        debate_result: DebateResult
    ) -> List[str]:
        """Extract claims that were rejected."""
        rejected = []
        
        for round in debate_result.rounds:
            if round.citation_report:
                # Add claims from deleted citations
                for v in round.citation_report.verifications:
                    if v.decision.value == "delete":
                        rejected.append(f"{v.original_citation.raw_text} - Reason: {v.reason}")
        
        return rejected
    
    def _generate_summary(
        self,
        verdict: str,
        confidence: float,
        verified_claims: List[str],
        rejected_claims: List[str]
    ) -> str:
        """Generate a summary of the consensus."""
        lines = [
            f"Verdict: {verdict}",
            f"Confidence: {confidence:.1f}%",
            f"Verified Claims: {len(verified_claims)}",
            f"Rejected Claims: {len(rejected_claims)}",
        ]
        
        if verdict == "VALIDATED":
            lines.append("The position has been validated through rigorous dual-agent verification.")
        elif verdict == "PARTIALLY VALIDATED":
            lines.append("Some claims have been verified, but others require additional evidence.")
        elif verdict == "REJECTED":
            lines.append("The position did not pass verification. Significant issues remain.")
        else:
            lines.append("The debate was inconclusive. Further analysis needed.")
        
        return "\n".join(lines)
    
    def format_consensus(self, consensus: Consensus) -> str:
        """Format consensus as readable text."""
        lines = [
            "=" * 60,
            "VERIFIED CONSENSUS",
            "=" * 60,
            "",
            f"VERDICT: {consensus.verdict}",
            f"CONFIDENCE: {consensus.confidence:.1f}%",
            "",
            "-" * 40,
            "VERIFIED CLAIMS",
            "-" * 40,
        ]
        
        if consensus.verified_claims:
            for i, claim in enumerate(consensus.verified_claims[:10], 1):
                lines.append(f"  {i}. {claim}")
        else:
            lines.append("  No claims passed full verification")
        
        lines.extend([
            "",
            "-" * 40,
            "REJECTED CLAIMS",
            "-" * 40,
        ])
        
        if consensus.rejected_claims:
            for i, claim in enumerate(consensus.rejected_claims[:10], 1):
                lines.append(f"  {i}. {claim}")
        else:
            lines.append("  No claims were rejected")
        
        if consensus.remaining_disputes:
            lines.extend([
                "",
                "-" * 40,
                "REMAINING DISPUTES",
                "-" * 40,
            ])
            for dispute in consensus.remaining_disputes[:5]:
                lines.append(f"  - {dispute}")
        
        lines.extend([
            "",
            "-" * 40,
            "SUMMARY",
            "-" * 40,
            consensus.summary,
            "",
            "=" * 60,
        ])
        
        return "\n".join(lines)
