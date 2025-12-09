"""
Scoring System

Multi-dimensional scoring rubric for debate evaluation.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from ..citation_moat.moat_engine import MoatReport


@dataclass
class RoundScore:
    """Score for a single debate round."""
    accuracy: float = 0.0      # 25%
    evidence: float = 0.0      # 25%
    logic: float = 0.0         # 20%
    methodology: float = 0.0   # 15%
    clarity: float = 0.0       # 15%
    
    # Weights
    WEIGHTS = {
        "accuracy": 0.25,
        "evidence": 0.25,
        "logic": 0.20,
        "methodology": 0.15,
        "clarity": 0.15,
    }
    
    @property
    def total_score(self) -> float:
        """Calculate weighted total score."""
        return (
            self.accuracy * self.WEIGHTS["accuracy"] +
            self.evidence * self.WEIGHTS["evidence"] +
            self.logic * self.WEIGHTS["logic"] +
            self.methodology * self.WEIGHTS["methodology"] +
            self.clarity * self.WEIGHTS["clarity"]
        ) * 100
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "accuracy": self.accuracy,
            "evidence": self.evidence,
            "logic": self.logic,
            "methodology": self.methodology,
            "clarity": self.clarity,
            "total": self.total_score,
        }


class ScoringSystem:
    """
    Multi-dimensional scoring for debate rounds.
    
    Criteria (weights):
    - Accuracy: 25% - Factual correctness
    - Evidence: 25% - Quality of citations
    - Logic: 20% - Argument coherence
    - Methodology: 15% - Soundness of approach
    - Clarity: 15% - Clear expression
    """
    
    def score_round(
        self,
        proponent_response: str,
        reviewer_response: str,
        citation_report: Optional[MoatReport] = None
    ) -> RoundScore:
        """
        Score a debate round.
        
        Args:
            proponent_response: Agent A's response
            reviewer_response: Agent B's response
            citation_report: Citation verification results
            
        Returns:
            RoundScore with all dimension scores
        """
        score = RoundScore()
        
        # Score accuracy (based on citation verification)
        score.accuracy = self._score_accuracy(citation_report, reviewer_response)
        
        # Score evidence quality
        score.evidence = self._score_evidence(proponent_response, citation_report)
        
        # Score logical coherence
        score.logic = self._score_logic(proponent_response, reviewer_response)
        
        # Score methodology
        score.methodology = self._score_methodology(proponent_response)
        
        # Score clarity
        score.clarity = self._score_clarity(proponent_response)
        
        return score
    
    def _score_accuracy(
        self,
        citation_report: Optional[MoatReport],
        reviewer_response: str
    ) -> float:
        """Score factual accuracy based on citations and reviewer feedback."""
        score = 0.5  # Base score
        
        if citation_report:
            # Higher verification rate = higher accuracy
            score = citation_report.verification_rate / 100.0
        
        # Adjust based on reviewer feedback
        reviewer_lower = reviewer_response.lower()
        if "inaccurate" in reviewer_lower or "incorrect" in reviewer_lower:
            score *= 0.7
        elif "accurate" in reviewer_lower or "correct" in reviewer_lower:
            score = min(1.0, score * 1.2)
        
        return min(1.0, max(0.0, score))
    
    def _score_evidence(
        self,
        proponent_response: str,
        citation_report: Optional[MoatReport]
    ) -> float:
        """Score quality of evidence and citations."""
        score = 0.5  # Base score
        
        if citation_report:
            if citation_report.total_citations > 0:
                # Ratio of verified to total
                verified_ratio = citation_report.verified_count / citation_report.total_citations
                score = 0.3 + (verified_ratio * 0.7)
            else:
                # No citations = low evidence score
                score = 0.2
        
        # Check for evidence markers in response
        response_lower = proponent_response.lower()
        evidence_markers = ["study shows", "research indicates", "evidence suggests", "data demonstrates"]
        marker_count = sum(1 for m in evidence_markers if m in response_lower)
        score += marker_count * 0.05
        
        return min(1.0, max(0.0, score))
    
    def _score_logic(
        self,
        proponent_response: str,
        reviewer_response: str
    ) -> float:
        """Score logical coherence of arguments."""
        score = 0.6  # Base score
        
        response_lower = proponent_response.lower()
        reviewer_lower = reviewer_response.lower()
        
        # Positive: Logical transition words
        logic_words = ["therefore", "because", "thus", "consequently", "hence", "follows that"]
        logic_count = sum(1 for w in logic_words if w in response_lower)
        score += logic_count * 0.05
        
        # Negative: Logical fallacy indicators in reviewer response
        fallacy_indicators = ["fallacy", "non sequitur", "circular", "strawman", "ad hominem"]
        fallacy_count = sum(1 for f in fallacy_indicators if f in reviewer_lower)
        score -= fallacy_count * 0.15
        
        return min(1.0, max(0.0, score))
    
    def _score_methodology(self, proponent_response: str) -> float:
        """Score soundness of methodology/approach."""
        score = 0.6  # Base score
        
        response_lower = proponent_response.lower()
        
        # Positive: Methodological rigor indicators
        method_markers = ["methodology", "systematic", "peer-reviewed", "replicated", "controlled"]
        marker_count = sum(1 for m in method_markers if m in response_lower)
        score += marker_count * 0.08
        
        # Positive: Acknowledgment of limitations
        if "limitation" in response_lower or "caveat" in response_lower:
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def _score_clarity(self, proponent_response: str) -> float:
        """Score clarity of expression."""
        score = 0.7  # Base score
        
        # Penalize very long responses (might be unclear)
        word_count = len(proponent_response.split())
        if word_count > 1000:
            score -= 0.1
        elif word_count < 100:
            score -= 0.1  # Too brief might lack clarity too
        
        # Check for structure markers
        structure_markers = ["first", "second", "finally", "in conclusion", "to summarize"]
        structure_count = sum(1 for s in structure_markers if s in proponent_response.lower())
        score += structure_count * 0.05
        
        return min(1.0, max(0.0, score))
    
    def generate_feedback(self, score: RoundScore) -> str:
        """Generate feedback based on scores."""
        feedback = []
        
        if score.accuracy < 0.6:
            feedback.append("Accuracy needs improvement. Verify factual claims.")
        if score.evidence < 0.6:
            feedback.append("Evidence is weak. Add more citations from credible sources.")
        if score.logic < 0.6:
            feedback.append("Logical coherence is lacking. Strengthen argument structure.")
        if score.methodology < 0.6:
            feedback.append("Methodology concerns. Be more rigorous in approach.")
        if score.clarity < 0.6:
            feedback.append("Clarity needs work. Simplify and structure your response.")
        
        if not feedback:
            feedback.append("Good performance across all criteria.")
        
        return " ".join(feedback)
