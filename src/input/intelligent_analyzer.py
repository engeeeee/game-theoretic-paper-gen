"""
Intelligent Requirements Analyzer

Uses LLM to understand ANY format of paper requirements adaptively.
Not template-based - truly understands natural language input.

Uses AGENT_A_API_KEY for LLM calls (as per user requirement).
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import openai
import google.generativeai as genai
from dotenv import load_dotenv

# Import agent configuration for using Agent A's API key
from ..agents.base_agent import get_agent_config, AgentRole, LLMProvider

load_dotenv()


@dataclass
class Section:
    """A section requirement for the paper."""
    name: str
    description: str = ""
    word_count: Optional[int] = None
    key_points: List[str] = field(default_factory=list)
    must_include: List[str] = field(default_factory=list)


@dataclass
class IntelligentRequirements:
    """
    Intelligently parsed requirements from any input format.
    """
    # Core understanding
    main_objective: str = ""
    topic: str = ""
    research_questions: List[str] = field(default_factory=list)
    thesis_direction: str = ""
    
    # Structure (adaptive)
    paper_type: str = ""
    total_word_count: Optional[int] = None
    total_page_count: Optional[int] = None
    sections: List[Section] = field(default_factory=list)
    
    # Sources and citations
    citation_style: str = ""
    min_sources: Optional[int] = None
    source_types: List[str] = field(default_factory=list)
    source_constraints: List[str] = field(default_factory=list)
    
    # Methodology
    methodology_requirements: List[str] = field(default_factory=list)
    analysis_type: str = ""
    
    # Constraints
    must_include: List[str] = field(default_factory=list)
    must_avoid: List[str] = field(default_factory=list)
    specific_requirements: List[str] = field(default_factory=list)
    
    # Audience and tone
    academic_level: str = ""
    target_audience: str = ""
    writing_style: str = ""
    
    # Deadlines and format
    special_formatting: List[str] = field(default_factory=list)
    
    # Original input
    raw_input: str = ""
    
    # Confidence in parsing
    parsing_confidence: float = 0.0
    unclear_aspects: List[str] = field(default_factory=list)


class IntelligentAnalyzer:
    """
    Uses LLM to intelligently understand paper requirements from ANY input format.
    
    Uses Agent A's API key for LLM calls (AGENT_A_API_KEY).
    
    Can handle:
    - Casual descriptions
    - Formal assignment briefs
    - Bullet point lists
    - Paragraph-form requirements
    - Mixed language input
    - Partial/incomplete specifications
    """
    
    ANALYSIS_PROMPT = '''You are an expert at understanding academic paper requirements.

Analyze the following input and extract ALL requirements. The input may be in ANY format:
- Natural language description
- Assignment brief
- Bullet points
- Email/conversation format
- Any language

INPUT TO ANALYZE:
{input_text}

Extract and return a JSON object with the following structure. Be thorough but only include what you can confidently extract:

{{
    "main_objective": "What the user ultimately wants to achieve",
    "topic": "The main topic/subject",
    "research_questions": ["List of research questions if identifiable"],
    "thesis_direction": "The expected argument or direction",
    
    "paper_type": "essay/research paper/thesis/dissertation/literature review/report/other",
    "total_word_count": null or number,
    "total_page_count": null or number,
    "sections": [
        {{
            "name": "Section name",
            "description": "What this section should contain",
            "word_count": null or number,
            "key_points": ["Points to cover"],
            "must_include": ["Required elements"]
        }}
    ],
    
    "citation_style": "APA/MLA/Chicago/Harvard/IEEE or empty if unspecified",
    "min_sources": null or number,
    "source_types": ["peer-reviewed", "academic journals", etc.],
    "source_constraints": ["last 5 years", "primary sources", etc.],
    
    "methodology_requirements": ["Any methodology requirements"],
    "analysis_type": "quantitative/qualitative/mixed/theoretical/empirical or empty",
    
    "must_include": ["Things that MUST be included"],
    "must_avoid": ["Things to avoid or exclude"],
    "specific_requirements": ["Any other specific requirements"],
    
    "academic_level": "undergraduate/graduate/phd or empty",
    "target_audience": "Who will read this",
    "writing_style": "formal academic/technical/accessible or empty",
    
    "special_formatting": ["Any special format requirements"],
    
    "parsing_confidence": 0.0 to 1.0,
    "unclear_aspects": ["Aspects that need clarification"]
}}

Return ONLY valid JSON, no other text.'''

    def __init__(self):
        """
        Initialize using Agent A's API configuration.
        This ensures the intelligent analyzer uses AGENT_A_API_KEY.
        """
        # Get Agent A's configuration
        config = get_agent_config(AgentRole.AGENT_A)
        
        self.provider = config["provider"]
        self.api_key = config["api_key"]
        self.model = config["model"]
        
        self._init_client()
    
    def _init_client(self):
        """Initialize LLM client using Agent A's API key."""
        if self.provider == LLMProvider.OPENAI:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
    
    async def analyze(self, input_text: str) -> IntelligentRequirements:
        """
        Intelligently analyze any input format to extract requirements.
        
        Uses Agent A's API key for LLM calls.
        
        Args:
            input_text: Any format of paper requirements description
            
        Returns:
            IntelligentRequirements with all extracted information
        """
        prompt = self.ANALYSIS_PROMPT.format(input_text=input_text)
        
        # Call LLM using Agent A's API
        if self.provider == LLMProvider.OPENAI:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at parsing academic requirements. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3  # Low temperature for consistency
            )
            result_text = response.choices[0].message.content
        else:
            response = self.client.generate_content(prompt)
            result_text = response.text
        
        # Parse JSON response
        try:
            # Clean up response if needed
            result_text = result_text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            parsed = json.loads(result_text.strip())
        except json.JSONDecodeError:
            # Fallback to basic parsing
            return self._fallback_parse(input_text)
        
        # Convert to IntelligentRequirements
        return self._dict_to_requirements(parsed, input_text)
    
    def analyze_sync(self, input_text: str) -> IntelligentRequirements:
        """Synchronous version of analyze."""
        import asyncio
        return asyncio.run(self.analyze(input_text))
    
    def _dict_to_requirements(self, data: dict, raw_input: str) -> IntelligentRequirements:
        """Convert parsed dict to IntelligentRequirements."""
        sections = []
        for s in data.get("sections", []):
            sections.append(Section(
                name=s.get("name", ""),
                description=s.get("description", ""),
                word_count=s.get("word_count"),
                key_points=s.get("key_points", []),
                must_include=s.get("must_include", [])
            ))
        
        return IntelligentRequirements(
            main_objective=data.get("main_objective", ""),
            topic=data.get("topic", ""),
            research_questions=data.get("research_questions", []),
            thesis_direction=data.get("thesis_direction", ""),
            
            paper_type=data.get("paper_type", ""),
            total_word_count=data.get("total_word_count"),
            total_page_count=data.get("total_page_count"),
            sections=sections,
            
            citation_style=data.get("citation_style", ""),
            min_sources=data.get("min_sources"),
            source_types=data.get("source_types", []),
            source_constraints=data.get("source_constraints", []),
            
            methodology_requirements=data.get("methodology_requirements", []),
            analysis_type=data.get("analysis_type", ""),
            
            must_include=data.get("must_include", []),
            must_avoid=data.get("must_avoid", []),
            specific_requirements=data.get("specific_requirements", []),
            
            academic_level=data.get("academic_level", ""),
            target_audience=data.get("target_audience", ""),
            writing_style=data.get("writing_style", ""),
            
            special_formatting=data.get("special_formatting", []),
            
            raw_input=raw_input,
            parsing_confidence=data.get("parsing_confidence", 0.5),
            unclear_aspects=data.get("unclear_aspects", [])
        )
    
    def _fallback_parse(self, input_text: str) -> IntelligentRequirements:
        """Fallback basic parsing if LLM fails."""
        return IntelligentRequirements(
            main_objective="Unable to parse - please review input",
            topic=input_text[:200],
            raw_input=input_text,
            parsing_confidence=0.1,
            unclear_aspects=["LLM parsing failed - using fallback"]
        )
    
    def to_agent_prompt(self, req: IntelligentRequirements) -> str:
        """Convert requirements to structured agent prompt."""
        prompt = f"""PAPER REQUIREMENTS (Intelligently Parsed):

MAIN OBJECTIVE: {req.main_objective}

TOPIC: {req.topic}
"""
        
        if req.thesis_direction:
            prompt += f"THESIS DIRECTION: {req.thesis_direction}\n"
        
        if req.research_questions:
            prompt += "\nRESEARCH QUESTIONS:\n"
            for rq in req.research_questions:
                prompt += f"- {rq}\n"
        
        prompt += f"\nPAPER TYPE: {req.paper_type or 'Research Paper'}\n"
        
        if req.total_word_count:
            prompt += f"TARGET WORD COUNT: {req.total_word_count}\n"
        if req.total_page_count:
            prompt += f"TARGET PAGE COUNT: {req.total_page_count}\n"
        
        if req.sections:
            prompt += "\nREQUIRED SECTIONS:\n"
            for section in req.sections:
                prompt += f"\n### {section.name}\n"
                if section.description:
                    prompt += f"Description: {section.description}\n"
                if section.word_count:
                    prompt += f"Word Count: {section.word_count}\n"
                if section.key_points:
                    prompt += "Key Points:\n"
                    for kp in section.key_points:
                        prompt += f"  - {kp}\n"
        
        prompt += f"""
CITATION REQUIREMENTS:
- Style: {req.citation_style or 'Academic standard'}
- Minimum Sources: {req.min_sources or 'As needed'}
- Source Types: {', '.join(req.source_types) if req.source_types else 'Peer-reviewed academic sources'}
- Constraints: {', '.join(req.source_constraints) if req.source_constraints else 'None specified'}
"""
        
        if req.methodology_requirements:
            prompt += "\nMETHODOLOGY REQUIREMENTS:\n"
            for m in req.methodology_requirements:
                prompt += f"- {m}\n"
        
        if req.analysis_type:
            prompt += f"ANALYSIS TYPE: {req.analysis_type}\n"
        
        if req.must_include:
            prompt += "\nMUST INCLUDE:\n"
            for item in req.must_include:
                prompt += f"- {item}\n"
        
        if req.must_avoid:
            prompt += "\nMUST AVOID:\n"
            for item in req.must_avoid:
                prompt += f"- {item}\n"
        
        if req.specific_requirements:
            prompt += "\nSPECIFIC REQUIREMENTS:\n"
            for item in req.specific_requirements:
                prompt += f"- {item}\n"
        
        if req.academic_level:
            prompt += f"\nACADEMIC LEVEL: {req.academic_level}\n"
        if req.target_audience:
            prompt += f"TARGET AUDIENCE: {req.target_audience}\n"
        if req.writing_style:
            prompt += f"WRITING STYLE: {req.writing_style}\n"
        
        if req.special_formatting:
            prompt += "\nSPECIAL FORMATTING:\n"
            for f in req.special_formatting:
                prompt += f"- {f}\n"
        
        if req.unclear_aspects:
            prompt += "\nNOTE - UNCLEAR ASPECTS (may need clarification):\n"
            for ua in req.unclear_aspects:
                prompt += f"- {ua}\n"
        
        prompt += "\nPlease produce output that adheres to ALL the above requirements."
        
        return prompt
    
    def format_for_display(self, req: IntelligentRequirements) -> str:
        """Format requirements for human-readable display."""
        lines = [
            "=" * 60,
            "INTELLIGENTLY PARSED REQUIREMENTS",
            f"Parsing Confidence: {req.parsing_confidence * 100:.0f}%",
            "=" * 60,
            "",
            f"Main Objective: {req.main_objective}",
            f"Topic: {req.topic}",
        ]
        
        if req.thesis_direction:
            lines.append(f"Thesis Direction: {req.thesis_direction}")
        
        if req.research_questions:
            lines.append("\nResearch Questions:")
            for rq in req.research_questions:
                lines.append(f"  - {rq}")
        
        lines.extend([
            "",
            "-" * 40,
            "STRUCTURE",
            "-" * 40,
            f"Paper Type: {req.paper_type or 'Not specified'}",
        ])
        
        if req.total_word_count:
            lines.append(f"Word Count: {req.total_word_count}")
        if req.total_page_count:
            lines.append(f"Page Count: {req.total_page_count}")
        
        if req.sections:
            lines.append("\nSections:")
            for s in req.sections:
                lines.append(f"  [{s.name}]")
                if s.description:
                    lines.append(f"    {s.description}")
                if s.key_points:
                    for kp in s.key_points[:3]:
                        lines.append(f"    - {kp}")
        
        lines.extend([
            "",
            "-" * 40,
            "SOURCES & CITATIONS",
            "-" * 40,
            f"Style: {req.citation_style or 'Not specified'}",
            f"Min Sources: {req.min_sources or 'Not specified'}",
        ])
        
        if req.source_types:
            lines.append(f"Source Types: {', '.join(req.source_types)}")
        if req.source_constraints:
            lines.append(f"Constraints: {', '.join(req.source_constraints)}")
        
        if req.must_include:
            lines.extend([
                "",
                "-" * 40,
                "MUST INCLUDE",
                "-" * 40,
            ])
            for item in req.must_include:
                lines.append(f"  * {item}")
        
        if req.must_avoid:
            lines.extend([
                "",
                "-" * 40,
                "MUST AVOID",
                "-" * 40,
            ])
            for item in req.must_avoid:
                lines.append(f"  * {item}")
        
        if req.unclear_aspects:
            lines.extend([
                "",
                "-" * 40,
                "NEEDS CLARIFICATION",
                "-" * 40,
            ])
            for ua in req.unclear_aspects:
                lines.append(f"  ? {ua}")
        
        lines.extend(["", "=" * 60])
        
        return "\n".join(lines)
