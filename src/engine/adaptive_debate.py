"""
Adaptive Debate Engine

Orchestrates the adversarial debate between agents.
Implements adaptive cycles with quality-driven termination.
"""

import asyncio
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum
import os

from ..agents.proponent import ProponentAgent
from ..agents.reviewer import ReviewerAgent
from ..citation_moat.moat_engine import CitationMoatEngine, MoatReport
from .scoring import ScoringSystem, RoundScore
from .voting import VotingEngine, VotingResult


class DebateStatus(Enum):
    """Current status of the debate."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    CONVERGED = "converged"
    MAX_ROUNDS_REACHED = "max_rounds_reached"
    CONSENSUS_REACHED = "consensus_reached"
    DEADLOCK = "deadlock"


@dataclass
class DebateRound:
    """Record of a single debate round."""
    round_number: int
    proponent_response: str
    reviewer_response: str
    proponent_claims: List[str] = field(default_factory=list)
    reviewer_critiques: List[str] = field(default_factory=list)
    round_score: Optional[RoundScore] = None
    citation_report: Optional[MoatReport] = None


@dataclass
class DebateResult:
    """Final result of the debate."""
    status: DebateStatus
    total_rounds: int
    final_position: str
    final_score: float
    voting_result: Optional[VotingResult] = None
    rounds: List[DebateRound] = field(default_factory=list)
    consensus_points: List[str] = field(default_factory=list)
    disputed_points: List[str] = field(default_factory=list)
    re_evaluations: int = 0


class AdaptiveDebateEngine:
    """
    Orchestrates adversarial debate with adaptive cycles.
    
    Features:
    - Dynamic round adjustment
    - Quality threshold monitoring
    - Convergence detection
    - Citation moat integration
    """
    
    def __init__(
        self,
        proponent: ProponentAgent = None,
        reviewer: ReviewerAgent = None,
        max_rounds: int = None,
        quality_threshold: float = None,
        convergence_rounds: int = 3
    ):
        """
        Initialize the debate engine.
        
        Args:
            proponent: Agent A
            reviewer: Agent B
            max_rounds: Maximum rounds (default from env)
            quality_threshold: Quality score to reach (default from env)
            convergence_rounds: Rounds of stable scores for convergence
        """
        self.proponent = proponent or ProponentAgent()
        self.reviewer = reviewer or ReviewerAgent()
        
        self.max_rounds = max_rounds or int(os.getenv("MAX_DEBATE_ROUNDS", "20"))
        self.quality_threshold = quality_threshold or float(os.getenv("QUALITY_THRESHOLD", "85"))
        self.convergence_rounds = convergence_rounds
        
        self.scorer = ScoringSystem()
        self.voting_engine = VotingEngine()
        self.citation_moat = CitationMoatEngine(
            proponent_agent=self.proponent,
            reviewer_agent=self.reviewer
        )
        
        self.rounds: List[DebateRound] = []
        self.status = DebateStatus.NOT_STARTED
    
    async def run_debate(
        self,
        question: str,
        context: Optional[str] = None
    ) -> DebateResult:
        """
        Run a full debate on the given question.
        
        Args:
            question: The question or topic to debate
            context: Optional context (e.g., paper content)
            
        Returns:
            DebateResult with full debate record
        """
        self.status = DebateStatus.IN_PROGRESS
        self.rounds = []
        re_evaluations = 0
        
        # Step 1: Get initial position from proponent
        initial_response = await self.proponent.generate_initial_position(
            question, context
        )
        
        current_position = initial_response.content
        
        # Step 2: Iterative debate rounds
        round_num = 0
        recent_scores = []
        
        while round_num < self.max_rounds:
            round_num += 1
            
            # Reviewer critiques the position
            review_response = await self.reviewer.review_position(
                current_position, context
            )
            
            # Proponent responds to critique
            defense_response = await self.proponent.respond_to_critique(
                review_response.content,
                current_position
            )
            
            # Verify citations in both responses
            combined_text = f"{defense_response.content}\n{review_response.content}"
            citation_report = await self.citation_moat.verify_text(combined_text)
            
            # Score this round
            round_score = self.scorer.score_round(
                proponent_response=defense_response.content,
                reviewer_response=review_response.content,
                citation_report=citation_report
            )
            
            # Record the round
            debate_round = DebateRound(
                round_number=round_num,
                proponent_response=defense_response.content,
                reviewer_response=review_response.content,
                round_score=round_score,
                citation_report=citation_report
            )
            self.rounds.append(debate_round)
            
            # Update current position
            current_position = defense_response.content
            
            # Check for convergence
            recent_scores.append(round_score.total_score)
            if len(recent_scores) > self.convergence_rounds:
                recent_scores.pop(0)
            
            if self._check_convergence(recent_scores):
                self.status = DebateStatus.CONVERGED
                break
            
            # Check for quality threshold
            if round_score.total_score >= self.quality_threshold:
                if len(recent_scores) >= self.convergence_rounds:
                    if all(s >= self.quality_threshold for s in recent_scores):
                        self.status = DebateStatus.CONSENSUS_REACHED
                        break
        
        if self.status == DebateStatus.IN_PROGRESS:
            self.status = DebateStatus.MAX_ROUNDS_REACHED
        
        # Step 3: Multi-round voting
        voting_result = await self._run_voting(current_position)
        
        # Step 4: Re-evaluation if voting fails
        while not voting_result.passed and re_evaluations < 3:
            re_evaluations += 1
            
            # Get targeted revision
            revision_response = await self._request_revision(
                current_position,
                voting_result
            )
            current_position = revision_response
            
            # Re-run voting
            voting_result = await self._run_voting(current_position)
        
        # Step 5: Get final position
        final_response = await self.proponent.provide_final_position()
        
        # Extract consensus and disputed points
        consensus, disputed = self._extract_points(self.rounds)
        
        return DebateResult(
            status=self.status,
            total_rounds=len(self.rounds),
            final_position=final_response.content,
            final_score=voting_result.weighted_average,
            voting_result=voting_result,
            rounds=self.rounds,
            consensus_points=consensus,
            disputed_points=disputed,
            re_evaluations=re_evaluations
        )
    
    def _check_convergence(self, recent_scores: List[float]) -> bool:
        """Check if scores have converged (stable for N rounds)."""
        if len(recent_scores) < self.convergence_rounds:
            return False
        
        # Check if variance is low
        avg = sum(recent_scores) / len(recent_scores)
        variance = sum((s - avg) ** 2 for s in recent_scores) / len(recent_scores)
        
        return variance < 25.0  # Less than 5 points standard deviation
    
    async def _run_voting(self, position: str) -> VotingResult:
        """Run multi-round voting on a position."""
        return await self.voting_engine.vote(position)
    
    async def _request_revision(
        self,
        current_position: str,
        voting_result: VotingResult
    ) -> str:
        """Request targeted revision based on voting feedback."""
        # Identify failed criteria
        failed_criteria = [
            c for c, s in voting_result.criterion_scores.items()
            if s < self.voting_engine.pass_threshold
        ]
        
        prompt = f"""Your position failed voting on these criteria: {', '.join(failed_criteria)}

Current position:
{current_position}

Feedback:
{voting_result.feedback}

Please revise your position to specifically address these issues.
Focus on improving: {', '.join(failed_criteria)}"""
        
        response = await self.proponent.generate_response(prompt)
        return response.content
    
    def _extract_points(
        self,
        rounds: List[DebateRound]
    ) -> Tuple[List[str], List[str]]:
        """Extract consensus and disputed points from debate."""
        consensus = []
        disputed = []
        
        # Simple extraction - in production, use NLP
        for round in rounds[-3:]:  # Look at last 3 rounds
            content = round.proponent_response.lower()
            
            if "agree" in content or "concede" in content:
                consensus.append(f"Round {round.round_number}: Agreement reached")
            if "disagree" in content or "dispute" in content:
                disputed.append(f"Round {round.round_number}: Dispute continues")
        
        return consensus, disputed
    
    def get_debate_transcript(self) -> str:
        """Generate a readable debate transcript."""
        lines = [
            "=" * 60,
            "DEBATE TRANSCRIPT",
            "=" * 60,
        ]
        
        for round in self.rounds:
            lines.extend([
                f"\n{'─' * 40}",
                f"ROUND {round.round_number}",
                f"{'─' * 40}",
                "\n[PROPONENT AGENT A]:",
                round.proponent_response[:500] + "..." if len(round.proponent_response) > 500 else round.proponent_response,
                "\n[REVIEWER AGENT B]:",
                round.reviewer_response[:500] + "..." if len(round.reviewer_response) > 500 else round.reviewer_response,
            ])
            
            if round.round_score:
                lines.append(f"\n[ROUND SCORE: {round.round_score.total_score:.1f}/100]")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
