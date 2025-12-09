"""
Proponent Agent (Agent A)

This agent proposes and defends positions with citations.
It generates initial stances and responds to critiques.

Uses AGENT_A_API_KEY for LLM calls.
"""

from typing import Optional
from .base_agent import BaseAgent, AgentResponse, LLMProvider, AgentRole


class ProponentAgent(BaseAgent):
    """
    Agent A: Proposes positions and defends them with evidence.
    
    Uses AGENT_A_API_KEY for true independence from Agent B.
    
    Responsibilities:
    - Generate initial position with citations
    - Defend against critiques
    - Concede when evidence is insufficient
    - Modify position based on valid criticism
    """
    
    def __init__(
        self,
        provider: LLMProvider = None,
        model: str = None,
        api_key: str = None,
        temperature: float = 0.7
    ):
        super().__init__(
            name="Proponent Agent A",
            role=AgentRole.AGENT_A,  # Uses AGENT_A_API_KEY
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=temperature
        )
    
    def get_role_prompt(self) -> str:
        """Get the proponent-specific role prompt."""
        return """You are the PROPONENT AGENT (Agent A) in an academic debate system.

YOUR ROLE:
1. Propose well-reasoned positions supported by evidence
2. Cite academic sources for every factual claim
3. Defend your position against critiques with additional evidence
4. CONCEDE points when the evidence is against you
5. MODIFY your position when presented with valid counter-evidence

BEHAVIOR RULES:
- Be intellectually honest - admit when you're uncertain
- Prioritize truth over winning the debate
- If a critique is valid, acknowledge it and adjust
- Never fabricate sources to defend a weak position
- If you cannot find supporting evidence, say so explicitly

OUTPUT STRUCTURE:
For initial position:
[POSITION: Your main thesis]
[CLAIM: Specific factual claim]
[CITATION: Source for the claim]
[CONFIDENCE: X%]
... repeat for each claim ...
[SUMMARY: Brief summary of your position]

For defense/response:
[RESPONSE TO: What critique you're addressing]
[DEFENSE/CONCESSION: Your response - either defend or concede]
[NEW EVIDENCE: Any new citations if defending]
[MODIFIED POSITION: If you've changed your view]
[CONFIDENCE: X%]"""
    
    async def generate_initial_position(
        self,
        question: str,
        context: Optional[str] = None
    ) -> AgentResponse:
        """
        Generate an initial position on the given question.
        
        Args:
            question: The question or topic to analyze
            context: Optional additional context (e.g., paper content)
            
        Returns:
            AgentResponse with the initial position
        """
        prompt = f"""Analyze the following question and provide a well-reasoned position:

QUESTION: {question}

Provide your initial position following the output structure. Include:
1. Your main thesis
2. Supporting claims with citations
3. Confidence levels for each claim
4. A summary of your position

Remember: Every factual claim MUST have a citation. If you cannot cite a source,
explicitly mark it as opinion or inference."""
        
        return await self.generate_response(prompt, context)
    
    async def respond_to_critique(
        self,
        critique: str,
        original_position: str
    ) -> AgentResponse:
        """
        Respond to a critique from the Reviewer Agent.
        
        Args:
            critique: The critique from Agent B
            original_position: Your original position being critiqued
            
        Returns:
            AgentResponse with defense or concession
        """
        prompt = f"""The Reviewer Agent has critiqued your position. Respond appropriately.

YOUR ORIGINAL POSITION:
{original_position}

REVIEWER'S CRITIQUE:
{critique}

INSTRUCTIONS:
1. Carefully consider each point in the critique
2. For valid criticisms: CONCEDE and modify your position
3. For invalid criticisms: DEFEND with additional evidence
4. If evidence is insufficient: acknowledge uncertainty
5. Provide updated confidence levels

Be intellectually honest. Winning the debate is less important than finding the truth."""
        
        return await self.generate_response(prompt)
    
    async def provide_final_position(self) -> AgentResponse:
        """
        Provide the final, refined position after debate.
        
        Returns:
            AgentResponse with the final position
        """
        prompt = """Based on the entire debate, provide your FINAL POSITION.

Include:
1. Your refined thesis (incorporating valid criticisms)
2. Claims you are confident in (with citations)
3. Points of uncertainty
4. What you conceded during the debate
5. Overall confidence in your final position

Be honest about what remains uncertain or contested."""
        
        return await self.generate_response(prompt)
    
    async def verify_citation(
        self,
        claim: str,
        citation: str
    ) -> AgentResponse:
        """
        Verify if a citation supports the claim (from Proponent perspective).
        
        Args:
            claim: The claim being made
            citation: The cited source
            
        Returns:
            AgentResponse with verification result
        """
        prompt = f"""Verify if the citation supports the claim.

CLAIM: {claim}

CITED SOURCE: {citation}

As the Proponent, verify:
1. Does this source appear to be a valid academic source?
2. Does the citation format look correct?
3. Would this source logically support this claim?
4. Is there any reason to doubt this source?

[VERIFICATION: Verified/Unverified/Uncertain]
[CONFIDENCE: X%]
[REASON: Your assessment]"""
        
        return await self.generate_response(prompt)
