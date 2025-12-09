"""
Base Agent Class with Anti-Hallucination Constraints

This module provides the abstract base class for all agents in the system.
Every agent must enforce citation requirements and confidence scoring.

Supports DUAL API KEY system for true agent independence.
"""

import os
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

import openai
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Smart config loading: tries .env first, falls back to .env.example
# This allows users to just edit .env.example directly without renaming
env_path = Path(__file__).parent.parent.parent / ".env"
env_example_path = Path(__file__).parent.parent.parent / ".env.example"

if env_path.exists():
    load_dotenv(env_path)
elif env_example_path.exists():
    load_dotenv(env_example_path)
else:
    load_dotenv()  # Try default locations


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    GOOGLE = "google"


class AgentRole(Enum):
    """Agent roles for API key selection."""
    AGENT_A = "agent_a"  # Proponent
    AGENT_B = "agent_b"  # Reviewer
    UTILITY = "utility"  # For other uses (uses Agent A's key)


@dataclass
class Citation:
    """Represents a citation with verification status."""
    text: str
    source: str
    doi: Optional[str] = None
    url: Optional[str] = None
    verified: bool = False
    verification_method: Optional[str] = None


@dataclass
class Claim:
    """Represents a claim with its supporting citations and confidence."""
    statement: str
    citations: List[Citation] = field(default_factory=list)
    confidence: float = 0.0  # 0-100
    verified: bool = False


@dataclass
class AgentResponse:
    """Structured response from an agent."""
    content: str
    claims: List[Claim] = field(default_factory=list)
    overall_confidence: float = 0.0
    citations_count: int = 0
    verified_citations_count: int = 0
    raw_response: Optional[str] = None


def get_agent_config(role: AgentRole) -> dict:
    """
    Get API configuration for a specific agent role.
    
    Supports dual API key system where Agent A and Agent B
    use completely different API keys for true independence.
    
    Args:
        role: The agent role (AGENT_A, AGENT_B, or UTILITY)
        
    Returns:
        Dict with provider, api_key, and model
    """
    if role == AgentRole.AGENT_A or role == AgentRole.UTILITY:
        # Agent A configuration
        provider = os.getenv("AGENT_A_PROVIDER", "").lower()
        api_key = os.getenv("AGENT_A_API_KEY", "")
        model = os.getenv("AGENT_A_MODEL", "")
        
        # Fall back to legacy config if Agent A specific not set
        if not api_key:
            provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
            if provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY", "")
                model = os.getenv("OPENAI_MODEL", "gpt-4o")
            else:
                api_key = os.getenv("GOOGLE_API_KEY", "")
                model = os.getenv("GOOGLE_MODEL", "gemini-pro")
        
        if not provider:
            provider = "openai"
        if not model:
            model = "gpt-4o" if provider == "openai" else "gemini-pro"
            
    else:  # AGENT_B
        # Agent B configuration
        provider = os.getenv("AGENT_B_PROVIDER", "").lower()
        api_key = os.getenv("AGENT_B_API_KEY", "")
        model = os.getenv("AGENT_B_MODEL", "")
        
        # Fall back to legacy config if Agent B specific not set
        if not api_key:
            provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
            if provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY", "")
                model = os.getenv("OPENAI_MODEL", "gpt-4o")
            else:
                api_key = os.getenv("GOOGLE_API_KEY", "")
                model = os.getenv("GOOGLE_MODEL", "gemini-pro")
        
        if not provider:
            provider = "google"  # Default Agent B to Google for diversity
        if not model:
            model = "gemini-pro" if provider == "google" else "gpt-4o"
    
    return {
        "provider": LLMProvider(provider),
        "api_key": api_key,
        "model": model
    }


class BaseAgent(ABC):
    """
    Abstract base class for all agents with anti-hallucination constraints.
    
    Every agent must:
    1. Provide citations for factual claims
    2. Include confidence scores
    3. Self-verify before output
    
    Supports dual API key system for Agent A / Agent B independence.
    """
    
    def __init__(
        self,
        name: str,
        role: AgentRole = AgentRole.UTILITY,
        provider: LLMProvider = None,
        model: str = None,
        api_key: str = None,
        temperature: float = 0.7
    ):
        self.name = name
        self.role = role
        self.temperature = temperature
        
        # Get configuration based on role (supports dual API keys)
        config = get_agent_config(role)
        
        self.provider = provider or config["provider"]
        self.model = model or config["model"]
        self.api_key = api_key or config["api_key"]
        
        # Initialize LLM client
        self._init_client()
        
        # Conversation history
        self.history: List[Dict[str, str]] = []
        
    def _init_client(self):
        """Initialize the LLM client based on provider and role-specific API key."""
        if self.provider == LLMProvider.OPENAI:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
    
    def _get_system_prompt(self) -> str:
        """Get the base system prompt with anti-hallucination rules."""
        return """You are a rigorous academic agent. You MUST follow these rules:

ANTI-HALLUCINATION RULES:
1. Every factual claim MUST have a citation in the format [Author, Year] or [Source URL]
2. If you cannot cite a source, explicitly state "This is my analysis/opinion, not a cited fact"
3. Rate your confidence (0-100) for each major claim
4. Never fabricate citations - if unsure, say "citation needed"
5. Distinguish between: verified facts, logical inferences, and opinions

OUTPUT FORMAT:
- Use [CLAIM: ...] for factual claims
- Use [CITATION: ...] immediately after claims
- Use [CONFIDENCE: X%] to rate certainty
- Use [OPINION: ...] for non-factual analysis

If you cannot verify something, DO NOT claim it as fact."""
    
    @abstractmethod
    def get_role_prompt(self) -> str:
        """Get the specific role prompt for this agent type."""
        pass
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None
    ) -> AgentResponse:
        """
        Generate a response with anti-hallucination enforcement.
        
        Args:
            prompt: The input prompt
            context: Optional additional context
            
        Returns:
            AgentResponse with structured claims and citations
        """
        # Build full prompt
        system_prompt = self._get_system_prompt() + "\n\n" + self.get_role_prompt()
        
        full_prompt = prompt
        if context:
            full_prompt = f"Context:\n{context}\n\nQuery:\n{prompt}"
        
        # Add to history
        self.history.append({"role": "user", "content": full_prompt})
        
        # Generate response based on provider
        if self.provider == LLMProvider.OPENAI:
            raw_response = await self._generate_openai(system_prompt, full_prompt)
        else:
            raw_response = await self._generate_google(system_prompt, full_prompt)
        
        # Parse response into structured format
        response = self._parse_response(raw_response)
        
        # Add to history
        self.history.append({"role": "assistant", "content": raw_response})
        
        return response
    
    async def _generate_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response using OpenAI."""
        messages = [
            {"role": "system", "content": system_prompt},
            *self.history[:-1],  # Previous history
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature
        )
        
        return response.choices[0].message.content
    
    async def _generate_google(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response using Google Gemini."""
        # Build conversation for Gemini
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = self.client.generate_content(full_prompt)
        
        return response.text
    
    def _parse_response(self, raw_response: str) -> AgentResponse:
        """Parse raw response into structured AgentResponse."""
        import re
        
        claims = []
        
        # Extract claims with pattern [CLAIM: ...]
        claim_pattern = r'\[CLAIM:\s*([^\]]+)\]'
        citation_pattern = r'\[CITATION:\s*([^\]]+)\]'
        confidence_pattern = r'\[CONFIDENCE:\s*(\d+)%?\]'
        
        # Find all claims
        claim_matches = re.finditer(claim_pattern, raw_response)
        
        for match in claim_matches:
            claim_text = match.group(1)
            
            # Find associated citation (next occurrence after claim)
            remaining_text = raw_response[match.end():]
            
            citations = []
            citation_match = re.search(citation_pattern, remaining_text[:500])
            if citation_match:
                citation_text = citation_match.group(1)
                citations.append(Citation(
                    text=claim_text,
                    source=citation_text,
                    verified=False
                ))
            
            # Find confidence
            confidence = 50.0  # Default
            conf_match = re.search(confidence_pattern, remaining_text[:500])
            if conf_match:
                confidence = float(conf_match.group(1))
            
            claims.append(Claim(
                statement=claim_text,
                citations=citations,
                confidence=confidence,
                verified=False
            ))
        
        # Calculate overall confidence
        if claims:
            overall_confidence = sum(c.confidence for c in claims) / len(claims)
        else:
            overall_confidence = 0.0
        
        # Count citations
        total_citations = sum(len(c.citations) for c in claims)
        
        return AgentResponse(
            content=raw_response,
            claims=claims,
            overall_confidence=overall_confidence,
            citations_count=total_citations,
            verified_citations_count=0,  # Will be updated by citation moat
            raw_response=raw_response
        )
    
    def reset_history(self):
        """Clear conversation history."""
        self.history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.history.copy()
