"""
Reviewer Agent (Agent B) - Professional Peer Reviewer

This agent provides academic journal-level critique and verification.
It challenges claims, verifies citations, and identifies weaknesses.

Uses AGENT_B_API_KEY for true independence from Agent A.
"""

from typing import Optional, List
from .base_agent import BaseAgent, AgentResponse, LLMProvider, AgentRole


class ReviewerAgent(BaseAgent):
    """
    Agent B: Professional Peer Reviewer.
    
    Uses AGENT_B_API_KEY for true independence from Agent A.
    
    Operates at academic journal reviewer level:
    - Scrutinizes methodology
    - Challenges statistical validity
    - Identifies logical fallacies
    - Verifies citation accuracy
    - Demands evidence for claims
    """
    
    def __init__(
        self,
        provider: LLMProvider = None,
        model: str = None,
        api_key: str = None,
        temperature: float = 0.5,  # Lower temperature for more rigorous critique
        strictness: str = "high"  # high, medium, low
    ):
        super().__init__(
            name="Reviewer Agent B",
            role=AgentRole.AGENT_B,  # Uses AGENT_B_API_KEY
            provider=provider,
            model=model,
            api_key=api_key,
            temperature=temperature
        )
        self.strictness = strictness
    
    def get_role_prompt(self) -> str:
        """Get the reviewer-specific role prompt."""
        strictness_modifier = ""
        if self.strictness == "high":
            strictness_modifier = """
STRICTNESS LEVEL: HIGH
- Reject any claim without proper citation
- Demand primary sources, not secondary references
- Challenge statistical methods rigorously
- No tolerance for logical fallacies
- Every weakness must be identified"""
        elif self.strictness == "medium":
            strictness_modifier = """
STRICTNESS LEVEL: MEDIUM
- Allow well-reasoned inferences with caveats
- Secondary sources acceptable if reputable
- Focus on major methodological issues
- Identify key weaknesses"""
        else:
            strictness_modifier = """
STRICTNESS LEVEL: LOW
- Focus on major factual errors only
- Accept reasonable inferences
- Highlight only critical issues"""
        
        return f"""You are the REVIEWER AGENT (Agent B) - a professional academic peer reviewer.

YOUR ROLE:
You review academic work as if reviewing for a top-tier journal (Nature, Science, JAMA level).

REVIEW CRITERIA:
1. ACCURACY: Are factual claims correct and verifiable?
2. EVIDENCE: Are citations relevant, recent, and from credible sources?
3. LOGIC: Is the reasoning valid? Any logical fallacies?
4. METHODOLOGY: Is the approach sound? Any statistical issues?
5. CLARITY: Is the argument clearly expressed?
6. COMPLETENESS: Are there gaps or missing considerations?

{strictness_modifier}

CRITIQUE STRUCTURE:
[REVIEWING: What claim/section you're reviewing]
[VERDICT: ACCEPT / WEAK / REJECT]
[ISSUE TYPE: Accuracy/Evidence/Logic/Methodology/Clarity]
[CRITIQUE: Detailed explanation of the problem]
[EVIDENCE REQUIRED: What evidence would address this]
[CITATION CHECK: Is the cited source valid? If checkable, verify]
[SEVERITY: Critical/Major/Minor]

BEHAVIOR RULES:
- Be thorough but fair
- Acknowledge valid points
- Distinguish between fatal flaws and minor issues
- Provide constructive feedback, not just criticism
- If a claim is well-supported, say so
- Check if cited papers actually support the claims made

ACADEMIC INTEGRITY:
- Flag any potential fabricated citations
- Identify claims that seem to lack any source
- Note if citations are misrepresented or taken out of context"""
    
    async def review_position(
        self,
        position: str,
        context: Optional[str] = None
    ) -> AgentResponse:
        """
        Review a position from the Proponent Agent.
        
        Args:
            position: The position to review
            context: Optional additional context
            
        Returns:
            AgentResponse with detailed critique
        """
        prompt = f"""Conduct a thorough peer review of the following position:

POSITION TO REVIEW:
{position}

INSTRUCTIONS:
1. Examine each claim for accuracy and evidence
2. Check if citations appear valid and relevant
3. Identify logical fallacies or weak reasoning
4. Note any methodological concerns
5. Highlight both strengths and weaknesses
6. Provide a verdict for each major claim
7. Give an overall assessment

Be rigorous but fair. Acknowledge what is done well."""
        
        return await self.generate_response(prompt, context)
    
    async def evaluate_defense(
        self,
        original_critique: str,
        defense: str
    ) -> AgentResponse:
        """
        Evaluate the Proponent's defense against critique.
        
        Args:
            original_critique: Your original critique
            defense: The Proponent's defense/response
            
        Returns:
            AgentResponse with evaluation
        """
        prompt = f"""Evaluate the Proponent's response to your critique.

YOUR ORIGINAL CRITIQUE:
{original_critique}

PROPONENT'S DEFENSE:
{defense}

INSTRUCTIONS:
1. Has the Proponent adequately addressed each concern?
2. Is new evidence valid and relevant?
3. Are concessions appropriate?
4. Are there remaining issues?
5. Has the position improved?

For each point:
[ORIGINAL ISSUE: What you critiqued]
[DEFENSE ASSESSMENT: Adequate/Partial/Inadequate]
[REASON: Why the defense succeeds or fails]
[REMAINING CONCERNS: If any]
[STATUS: Resolved/Partially Resolved/Unresolved]"""
        
        return await self.generate_response(prompt)
    
    async def verify_citation(
        self,
        claim: str,
        citation: str
    ) -> AgentResponse:
        """
        Verify if a citation supports the claim.
        
        Args:
            claim: The claim being made
            citation: The cited source
            
        Returns:
            AgentResponse with verification result
        """
        prompt = f"""Verify if the citation supports the claim.

CLAIM: {claim}

CITED SOURCE: {citation}

VERIFICATION CHECKLIST:
1. Does this source likely exist? (Based on format, author, journal)
2. Would this source logically contain this information?
3. Is the citation format correct?
4. Are there any red flags suggesting fabrication?
5. Is the source appropriate for this type of claim?

[CITATION: The source being verified]
[VERIFICATION STATUS: Verified/Unverified/Suspicious/Needs Manual Check]
[CONFIDENCE: How confident are you in this assessment]
[REASON: Explanation]
[RED FLAGS: Any concerns]"""
        
        return await self.generate_response(prompt)
    
    async def provide_final_assessment(
        self,
        debate_history: List[str]
    ) -> AgentResponse:
        """
        Provide final assessment after the debate.
        
        Args:
            debate_history: List of debate exchanges
            
        Returns:
            AgentResponse with final assessment
        """
        history_text = "\n\n---\n\n".join(debate_history)
        
        prompt = f"""Provide your FINAL ASSESSMENT of the debate.

DEBATE HISTORY:
{history_text}

FINAL ASSESSMENT STRUCTURE:
[OVERALL VERDICT: Accept/Accept with Revisions/Reject]
[QUALITY SCORE: 0-100]

[RESOLVED ISSUES: What was successfully addressed]
[UNRESOLVED ISSUES: What remains problematic]
[STRONGEST POINTS: Best supported claims]
[WEAKEST POINTS: Claims that remain unsupported]

[RECOMMENDATION: Your final recommendation]
[CONFIDENCE IN ASSESSMENT: X%]"""
        
        return await self.generate_response(prompt)
