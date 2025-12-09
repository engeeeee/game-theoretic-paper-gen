"""
Tests for Agent classes.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.base_agent import BaseAgent, AgentResponse, LLMProvider, Claim, Citation
from src.agents.proponent import ProponentAgent
from src.agents.reviewer import ReviewerAgent


class TestBaseAgent:
    """Tests for BaseAgent class."""
    
    def test_parse_response_extracts_claims(self):
        """Test that claims are extracted from response."""
        # Create a concrete implementation for testing
        class TestAgent(BaseAgent):
            def get_role_prompt(self):
                return "Test agent"
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            agent = TestAgent(name="Test", provider=LLMProvider.OPENAI)
        
        response_text = """
        [CLAIM: The sky is blue]
        [CITATION: Physics textbook, 2020]
        [CONFIDENCE: 90%]
        
        [CLAIM: Water is wet]
        [CITATION: Chemistry basics, 2021]
        [CONFIDENCE: 85%]
        """
        
        result = agent._parse_response(response_text)
        
        assert isinstance(result, AgentResponse)
        assert len(result.claims) == 2
        assert result.claims[0].statement == "The sky is blue"
        assert result.claims[0].confidence == 90.0
        assert result.claims[1].statement == "Water is wet"
        assert result.claims[1].confidence == 85.0
    
    def test_parse_response_handles_no_claims(self):
        """Test parsing when no claims are found."""
        class TestAgent(BaseAgent):
            def get_role_prompt(self):
                return "Test agent"
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            agent = TestAgent(name="Test", provider=LLMProvider.OPENAI)
        
        response_text = "Just a simple response without structured claims."
        
        result = agent._parse_response(response_text)
        
        assert len(result.claims) == 0
        assert result.overall_confidence == 0.0


class TestProponentAgent:
    """Tests for ProponentAgent class."""
    
    def test_role_prompt_contains_required_elements(self):
        """Test that role prompt has required elements."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            agent = ProponentAgent(provider=LLMProvider.OPENAI)
        
        prompt = agent.get_role_prompt()
        
        assert "PROPONENT" in prompt
        assert "citation" in prompt.lower()
        assert "defend" in prompt.lower()
        assert "concede" in prompt.lower()
    
    @pytest.mark.asyncio
    async def test_generate_initial_position(self):
        """Test initial position generation."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            agent = ProponentAgent(provider=LLMProvider.OPENAI)
        
        # Mock the generate_response method
        mock_response = AgentResponse(
            content="[POSITION: Test position] [CLAIM: Test claim] [CITATION: Test, 2024]",
            claims=[Claim(statement="Test claim", confidence=80.0)],
            overall_confidence=80.0
        )
        
        agent.generate_response = AsyncMock(return_value=mock_response)
        
        result = await agent.generate_initial_position("Test question")
        
        assert result.content is not None
        assert "Test" in result.content


class TestReviewerAgent:
    """Tests for ReviewerAgent class."""
    
    def test_role_prompt_varies_by_strictness(self):
        """Test that role prompt changes with strictness level."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            high_agent = ReviewerAgent(provider=LLMProvider.OPENAI, strictness="high")
            low_agent = ReviewerAgent(provider=LLMProvider.OPENAI, strictness="low")
        
        high_prompt = high_agent.get_role_prompt()
        low_prompt = low_agent.get_role_prompt()
        
        assert "HIGH" in high_prompt
        assert "LOW" in low_prompt
        assert high_prompt != low_prompt
    
    def test_professional_reviewer_characteristics(self):
        """Test that reviewer has professional characteristics."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            agent = ReviewerAgent(provider=LLMProvider.OPENAI)
        
        prompt = agent.get_role_prompt()
        
        # Should mention academic/professional review criteria
        assert "peer" in prompt.lower() or "academic" in prompt.lower()
        assert "methodology" in prompt.lower()
        assert "evidence" in prompt.lower()


class TestAgentInteraction:
    """Tests for agent interactions."""
    
    @pytest.mark.asyncio
    async def test_proponent_reviewer_exchange(self):
        """Test basic exchange between proponent and reviewer."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
            proponent = ProponentAgent(provider=LLMProvider.OPENAI)
            reviewer = ReviewerAgent(provider=LLMProvider.OPENAI)
        
        # Mock responses
        proponent_response = AgentResponse(
            content="[POSITION: Test] [CLAIM: Claim 1] [CITATION: Source, 2024]",
            claims=[],
            overall_confidence=75.0
        )
        
        reviewer_response = AgentResponse(
            content="[VERDICT: WEAK] [CRITIQUE: Needs more evidence]",
            claims=[],
            overall_confidence=60.0
        )
        
        proponent.generate_response = AsyncMock(return_value=proponent_response)
        reviewer.generate_response = AsyncMock(return_value=reviewer_response)
        
        # Simulate exchange
        initial = await proponent.generate_initial_position("Test question")
        review = await reviewer.review_position(initial.content)
        
        assert initial.content is not None
        assert review.content is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
