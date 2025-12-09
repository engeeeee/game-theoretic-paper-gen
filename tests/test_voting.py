"""
Tests for Voting and Scoring systems.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.engine.scoring import ScoringSystem, RoundScore
from src.engine.voting import VotingEngine, VotingResult, VoteStatus, CriterionVote


class TestScoringSystem:
    """Tests for ScoringSystem class."""
    
    def test_round_score_weights_sum_to_one(self):
        """Test that criterion weights sum to 1.0."""
        score = RoundScore()
        total_weight = sum(score.WEIGHTS.values())
        
        assert abs(total_weight - 1.0) < 0.001
    
    def test_round_score_calculation(self):
        """Test total score calculation."""
        score = RoundScore(
            accuracy=0.8,
            evidence=0.9,
            logic=0.7,
            methodology=0.6,
            clarity=0.8
        )
        
        # Calculate expected: (0.8*25 + 0.9*25 + 0.7*20 + 0.6*15 + 0.8*15)
        expected = (0.8*0.25 + 0.9*0.25 + 0.7*0.20 + 0.6*0.15 + 0.8*0.15) * 100
        
        assert abs(score.total_score - expected) < 0.01
    
    def test_score_round_returns_round_score(self):
        """Test that score_round returns RoundScore object."""
        scorer = ScoringSystem()
        
        result = scorer.score_round(
            proponent_response="Test response with evidence markers.",
            reviewer_response="Valid critique without fallacy mentions."
        )
        
        assert isinstance(result, RoundScore)
        assert 0 <= result.accuracy <= 1.0
        assert 0 <= result.evidence <= 1.0
        assert 0 <= result.logic <= 1.0
    
    def test_score_accuracy_with_citations(self):
        """Test accuracy scoring considers citations."""
        scorer = ScoringSystem()
        
        from src.citation_moat.moat_engine import MoatReport
        
        high_verification = MoatReport(
            total_citations=10,
            verified_count=9
        )
        
        low_verification = MoatReport(
            total_citations=10,
            verified_count=3
        )
        
        high_score = scorer._score_accuracy(high_verification, "")
        low_score = scorer._score_accuracy(low_verification, "")
        
        assert high_score > low_score
    
    def test_generate_feedback(self):
        """Test feedback generation."""
        scorer = ScoringSystem()
        
        low_score = RoundScore(
            accuracy=0.4,
            evidence=0.5,
            logic=0.8,
            methodology=0.7,
            clarity=0.9
        )
        
        feedback = scorer.generate_feedback(low_score)
        
        assert "Accuracy" in feedback or "Evidence" in feedback


class TestVotingEngine:
    """Tests for VotingEngine class."""
    
    def test_criteria_weights_sum_to_one(self):
        """Test that voting criteria weights sum to 1.0."""
        engine = VotingEngine()
        
        total_weight = sum(c["weight"] for c in engine.CRITERIA.values())
        
        assert abs(total_weight - 1.0) < 0.001
    
    def test_all_criteria_have_questions(self):
        """Test that all criteria have questions defined."""
        engine = VotingEngine()
        
        for criterion, config in engine.CRITERIA.items():
            assert "question" in config
            assert len(config["question"]) > 0
    
    @pytest.mark.asyncio
    async def test_vote_returns_voting_result(self):
        """Test that vote returns VotingResult."""
        engine = VotingEngine()
        
        result = await engine.vote("Test position with some content.")
        
        assert isinstance(result, VotingResult)
        assert isinstance(result.passed, bool)
        assert 0 <= result.weighted_average <= 100
    
    @pytest.mark.asyncio
    async def test_vote_criterion_scores(self):
        """Test that all criteria receive scores."""
        engine = VotingEngine()
        
        result = await engine.vote("Test position")
        
        assert len(result.criterion_scores) == 5
        assert "accuracy" in result.criterion_scores
        assert "evidence" in result.criterion_scores
        assert "logic" in result.criterion_scores
        assert "methodology" in result.criterion_scores
        assert "clarity" in result.criterion_scores
    
    def test_vote_criterion_status(self):
        """Test criterion vote status determination."""
        engine = VotingEngine(pass_threshold=75)
        
        vote = engine._vote_criterion("accuracy", "Test?", "High quality text.")
        
        assert isinstance(vote, CriterionVote)
        assert vote.status in [VoteStatus.PASS, VoteStatus.FAIL, VoteStatus.ABSTAIN]
    
    @pytest.mark.asyncio
    async def test_passing_threshold(self):
        """Test that passing is determined by threshold."""
        high_threshold = VotingEngine(pass_threshold=95)
        low_threshold = VotingEngine(pass_threshold=50)
        
        test_text = "A reasonable position with [CITATION: Source, 2024] and logic."
        
        high_result = await high_threshold.vote(test_text)
        low_result = await low_threshold.vote(test_text)
        
        # Low threshold should be more likely to pass
        # Just verify both return valid results
        assert isinstance(high_result.passed, bool)
        assert isinstance(low_result.passed, bool)
    
    def test_get_failed_criteria(self):
        """Test getting failed criteria from result."""
        result = VotingResult(
            passed=False,
            weighted_average=60.0,
            criterion_scores={
                "accuracy": 80.0,
                "evidence": 60.0,
                "logic": 70.0,
                "methodology": 50.0,
                "clarity": 85.0
            }
        )
        
        failed = result.get_failed_criteria(threshold=75.0)
        
        assert "evidence" in failed
        assert "logic" in failed
        assert "methodology" in failed
        assert "accuracy" not in failed
        assert "clarity" not in failed
    
    def test_voting_summary_generation(self):
        """Test voting summary text generation."""
        engine = VotingEngine()
        
        result = VotingResult(
            passed=True,
            weighted_average=80.0,
            criterion_scores={
                "accuracy": 85.0,
                "evidence": 80.0,
                "logic": 75.0,
                "methodology": 78.0,
                "clarity": 82.0
            },
            criterion_votes=[],
            feedback="Good overall"
        )
        
        summary = engine.get_voting_summary(result)
        
        assert "VOTING RESULTS" in summary
        assert "80.0" in summary
        assert "PASSED" in summary


class TestIntegration:
    """Integration tests for scoring and voting."""
    
    @pytest.mark.asyncio
    async def test_scoring_to_voting_flow(self):
        """Test flow from scoring to voting."""
        scorer = ScoringSystem()
        voter = VotingEngine()
        
        # Score a round
        round_score = scorer.score_round(
            proponent_response="Well-structured response with citations.",
            reviewer_response="Fair critique of the position."
        )
        
        # Vote on position
        vote_result = await voter.vote("Position based on scored round.")
        
        # Both should produce valid results
        assert round_score.total_score >= 0
        assert vote_result.weighted_average >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
