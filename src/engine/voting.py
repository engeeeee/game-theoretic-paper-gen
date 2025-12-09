"""
Voting Engine

Multi-round voting mechanism for final consensus validation.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class VoteStatus(Enum):
    """Status of a vote."""
    PASS = "pass"
    FAIL = "fail"
    ABSTAIN = "abstain"


@dataclass
class CriterionVote:
    """Vote on a single criterion."""
    criterion: str
    score: float  # 0-100
    status: VoteStatus
    feedback: str = ""


@dataclass
class VotingResult:
    """Result of multi-round voting."""
    passed: bool
    weighted_average: float
    criterion_scores: Dict[str, float] = field(default_factory=dict)
    criterion_votes: List[CriterionVote] = field(default_factory=list)
    feedback: str = ""
    voting_rounds: int = 0
    
    def get_failed_criteria(self, threshold: float = 75.0) -> List[str]:
        """Get list of criteria that failed."""
        return [c for c, s in self.criterion_scores.items() if s < threshold]


class VotingEngine:
    """
    Multi-round voting for final validation.
    
    Voting rounds:
    1. Accuracy Vote
    2. Evidence Vote
    3. Logic Vote
    4. Methodology Vote
    5. Clarity Vote
    """
    
    # Voting criteria with weights
    CRITERIA = {
        "accuracy": {
            "weight": 0.25,
            "question": "Does the claim match cited evidence?",
        },
        "evidence": {
            "weight": 0.25,
            "question": "Are sources credible and relevant?",
        },
        "logic": {
            "weight": 0.20,
            "question": "Is the reasoning valid?",
        },
        "methodology": {
            "weight": 0.15,
            "question": "Is the approach sound?",
        },
        "clarity": {
            "weight": 0.15,
            "question": "Is it clearly expressed?",
        },
    }
    
    def __init__(
        self,
        pass_threshold: float = None,
        max_retries: int = None
    ):
        """
        Initialize voting engine.
        
        Args:
            pass_threshold: Score needed to pass (default from env)
            max_retries: Maximum re-evaluation attempts
        """
        self.pass_threshold = pass_threshold or float(
            os.getenv("VOTING_PASS_THRESHOLD", "75")
        )
        self.max_retries = max_retries or int(os.getenv("MAX_RETRIES", "3"))
    
    async def vote(
        self,
        position: str,
        agent_a_input: Optional[str] = None,
        agent_b_input: Optional[str] = None
    ) -> VotingResult:
        """
        Conduct multi-round voting on a position.
        
        Args:
            position: The position to vote on
            agent_a_input: Optional input from Agent A
            agent_b_input: Optional input from Agent B
            
        Returns:
            VotingResult with all votes
        """
        votes = []
        criterion_scores = {}
        
        # Vote on each criterion
        for criterion, config in self.CRITERIA.items():
            vote = self._vote_criterion(
                criterion=criterion,
                question=config["question"],
                position=position
            )
            votes.append(vote)
            criterion_scores[criterion] = vote.score
        
        # Calculate weighted average
        weighted_avg = sum(
            criterion_scores[c] * self.CRITERIA[c]["weight"]
            for c in criterion_scores
        )
        
        # Determine pass/fail
        passed = weighted_avg >= self.pass_threshold
        
        # Generate feedback
        feedback = self._generate_feedback(votes, weighted_avg)
        
        return VotingResult(
            passed=passed,
            weighted_average=weighted_avg,
            criterion_scores=criterion_scores,
            criterion_votes=votes,
            feedback=feedback,
            voting_rounds=len(votes)
        )
    
    def _vote_criterion(
        self,
        criterion: str,
        question: str,
        position: str
    ) -> CriterionVote:
        """Vote on a single criterion."""
        # Score based on content analysis
        score = self._analyze_criterion(criterion, position)
        
        # Determine status
        if score >= self.pass_threshold:
            status = VoteStatus.PASS
        elif score >= self.pass_threshold * 0.7:
            status = VoteStatus.ABSTAIN
        else:
            status = VoteStatus.FAIL
        
        # Generate feedback
        feedback = self._criterion_feedback(criterion, score)
        
        return CriterionVote(
            criterion=criterion,
            score=score,
            status=status,
            feedback=feedback
        )
    
    def _analyze_criterion(self, criterion: str, position: str) -> float:
        """Analyze position against a criterion."""
        position_lower = position.lower()
        base_score = 60.0  # Base score
        
        if criterion == "accuracy":
            # Check for verification markers
            if "[verified]" in position_lower or "confirmed" in position_lower:
                base_score += 20
            if "citation removed" in position_lower:
                base_score -= 15
            if "[claim:" in position_lower and "[citation:" in position_lower:
                base_score += 10
                
        elif criterion == "evidence":
            # Count citations
            citation_count = position_lower.count("[citation:")
            citation_count += position_lower.count("doi:")
            citation_count += position_lower.count("http")
            base_score += min(citation_count * 5, 25)
            
        elif criterion == "logic":
            # Check for logical structure
            logic_markers = ["therefore", "because", "thus", "hence", "consequently"]
            marker_count = sum(1 for m in logic_markers if m in position_lower)
            base_score += min(marker_count * 5, 20)
            
            # Penalize fallacy indicators
            if "fallacy" in position_lower or "invalid" in position_lower:
                base_score -= 10
                
        elif criterion == "methodology":
            # Check for methodological rigor
            method_markers = ["systematic", "peer-reviewed", "methodology", "analysis"]
            marker_count = sum(1 for m in method_markers if m in position_lower)
            base_score += min(marker_count * 5, 20)
            
        elif criterion == "clarity":
            # Check for structure
            structure_markers = ["first,", "second,", "finally,", "in summary"]
            marker_count = sum(1 for m in structure_markers if m in position_lower)
            base_score += min(marker_count * 5, 15)
            
            # Penalize very long unstructured text
            if len(position) > 5000 and marker_count < 2:
                base_score -= 10
        
        return min(100.0, max(0.0, base_score))
    
    def _criterion_feedback(self, criterion: str, score: float) -> str:
        """Generate feedback for a criterion."""
        if score >= 85:
            return f"{criterion.capitalize()}: Excellent"
        elif score >= 75:
            return f"{criterion.capitalize()}: Good"
        elif score >= 60:
            return f"{criterion.capitalize()}: Needs improvement"
        else:
            return f"{criterion.capitalize()}: Significant issues"
    
    def _generate_feedback(
        self,
        votes: List[CriterionVote],
        weighted_avg: float
    ) -> str:
        """Generate overall feedback."""
        lines = [f"Overall Score: {weighted_avg:.1f}/100"]
        
        failed = [v for v in votes if v.status == VoteStatus.FAIL]
        if failed:
            lines.append("\nFailed Criteria:")
            for v in failed:
                lines.append(f"  - {v.criterion}: {v.score:.1f} - {v.feedback}")
        
        passed = [v for v in votes if v.status == VoteStatus.PASS]
        if passed:
            lines.append("\nPassed Criteria:")
            for v in passed:
                lines.append(f"  - {v.criterion}: {v.score:.1f}")
        
        if weighted_avg >= self.pass_threshold:
            lines.append("\nVERDICT: PASSED")
        else:
            lines.append(f"\nVERDICT: FAILED (threshold: {self.pass_threshold})")
        
        return "\n".join(lines)
    
    def get_voting_summary(self, result: VotingResult) -> str:
        """Generate a summary of voting results."""
        lines = [
            "=" * 50,
            "VOTING RESULTS",
            "=" * 50,
            f"Status: {'PASSED' if result.passed else 'FAILED'}",
            f"Weighted Average: {result.weighted_average:.1f}/100",
            f"Pass Threshold: {self.pass_threshold}",
            "",
            "Criterion Breakdown:",
            "-" * 30,
        ]
        
        for criterion, score in result.criterion_scores.items():
            status = "PASS" if score >= self.pass_threshold else "FAIL"
            weight = self.CRITERIA[criterion]["weight"] * 100
            lines.append(f"  {criterion.capitalize():12} {score:5.1f}  [{status}]  (weight: {weight:.0f}%)")
        
        lines.extend([
            "",
            "-" * 30,
            result.feedback,
            "=" * 50,
        ])
        
        return "\n".join(lines)
