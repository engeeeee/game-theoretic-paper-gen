"""
Paper Requirements Parser

Parses complex paper requirements and extracts structured information.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class PaperRequirements:
    """Structured paper requirements."""
    # Core requirements
    topic: str = ""
    thesis_focus: str = ""
    research_question: str = ""
    
    # Structure requirements
    required_sections: List[str] = field(default_factory=list)
    word_count: Optional[int] = None
    page_count: Optional[int] = None
    
    # Citation requirements
    citation_style: str = "APA"  # APA, MLA, Chicago, Harvard, IEEE
    min_sources: int = 5
    source_requirements: List[str] = field(default_factory=list)  # e.g., "peer-reviewed", "recent 5 years"
    
    # Methodology
    methodology_type: str = ""  # qualitative, quantitative, mixed
    research_approach: str = ""
    
    # Specific requirements
    key_arguments: List[str] = field(default_factory=list)
    must_include: List[str] = field(default_factory=list)
    must_avoid: List[str] = field(default_factory=list)
    
    # Academic level
    academic_level: str = "graduate"  # undergraduate, graduate, phd
    
    # Format
    format_type: str = "essay"  # essay, research paper, thesis, dissertation, literature review
    
    # Raw input
    raw_input: str = ""


class RequirementsParser:
    """
    Parses complex paper requirements from natural language input.
    
    Can understand inputs like:
    - "Write a 3000-word essay on climate change impact using APA style with at least 10 peer-reviewed sources"
    - "I need a literature review on machine learning in healthcare, focusing on diagnostic applications"
    - "Research paper analyzing the effectiveness of monetary policy, must include quantitative analysis"
    """
    
    def __init__(self):
        self._init_patterns()
    
    def _init_patterns(self):
        """Initialize regex patterns for parsing."""
        # Word/page count patterns
        self.word_patterns = [
            r'(\d+)[\s-]*(word|words)',
            r'(\d+)[\s-]*(页|字)',
            r'word\s*count[:\s]*(\d+)',
            r'约?(\d+)字',
        ]
        
        self.page_patterns = [
            r'(\d+)[\s-]*(page|pages)',
            r'(\d+)[\s-]*(张|页)',
        ]
        
        # Citation style patterns
        self.citation_styles = {
            'apa': r'\bAPA\b',
            'mla': r'\bMLA\b',
            'chicago': r'\bChicago\b',
            'harvard': r'\bHarvard\b',
            'ieee': r'\bIEEE\b',
            'vancouver': r'\bVancouver\b',
        }
        
        # Source count patterns
        self.source_patterns = [
            r'(\d+)\s*(sources?|references?|citations?)',
            r'at\s*least\s*(\d+)',
            r'minimum\s*(\d+)',
            r'至少(\d+)篇',
        ]
        
        # Format type patterns
        self.format_patterns = {
            'essay': r'\b(essay|文章)\b',
            'research paper': r'\b(research paper|论文|学术论文)\b',
            'thesis': r'\b(thesis|毕业论文)\b',
            'dissertation': r'\b(dissertation|博士论文)\b',
            'literature review': r'\b(literature review|文献综述)\b',
            'case study': r'\b(case study|案例分析)\b',
            'report': r'\b(report|报告)\b',
        }
        
        # Methodology patterns
        self.methodology_patterns = {
            'quantitative': r'\b(quantitative|定量|数据分析)\b',
            'qualitative': r'\b(qualitative|定性)\b',
            'mixed': r'\b(mixed method|混合方法)\b',
            'empirical': r'\b(empirical|实证)\b',
            'theoretical': r'\b(theoretical|理论)\b',
        }
        
        # Section patterns
        self.section_keywords = {
            'abstract': ['abstract', '摘要'],
            'introduction': ['introduction', '引言', '导论'],
            'literature review': ['literature review', '文献综述'],
            'methodology': ['methodology', 'methods', '方法', '研究方法'],
            'results': ['results', 'findings', '结果'],
            'discussion': ['discussion', '讨论'],
            'conclusion': ['conclusion', '结论'],
            'references': ['references', 'bibliography', '参考文献'],
        }
    
    def parse(self, input_text: str) -> PaperRequirements:
        """
        Parse paper requirements from natural language input.
        
        Args:
            input_text: Natural language description of paper requirements
            
        Returns:
            PaperRequirements with extracted information
        """
        req = PaperRequirements(raw_input=input_text)
        input_lower = input_text.lower()
        
        # Extract word/page count
        req.word_count = self._extract_word_count(input_text)
        req.page_count = self._extract_page_count(input_text)
        
        # Extract citation style
        req.citation_style = self._extract_citation_style(input_text)
        
        # Extract minimum sources
        req.min_sources = self._extract_source_count(input_text)
        
        # Extract format type
        req.format_type = self._extract_format_type(input_lower)
        
        # Extract methodology
        req.methodology_type = self._extract_methodology(input_lower)
        
        # Extract required sections
        req.required_sections = self._extract_sections(input_lower)
        
        # Extract source requirements
        req.source_requirements = self._extract_source_requirements(input_lower)
        
        # Extract topic and thesis focus
        req.topic, req.thesis_focus = self._extract_topic_and_focus(input_text)
        
        # Extract research question
        req.research_question = self._extract_research_question(input_text)
        
        # Extract must include/avoid
        req.must_include = self._extract_must_include(input_text)
        req.must_avoid = self._extract_must_avoid(input_text)
        
        # Extract key arguments
        req.key_arguments = self._extract_key_arguments(input_text)
        
        # Extract academic level
        req.academic_level = self._extract_academic_level(input_lower)
        
        return req
    
    def _extract_word_count(self, text: str) -> Optional[int]:
        """Extract word count requirement."""
        for pattern in self.word_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def _extract_page_count(self, text: str) -> Optional[int]:
        """Extract page count requirement."""
        for pattern in self.page_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def _extract_citation_style(self, text: str) -> str:
        """Extract citation style."""
        for style, pattern in self.citation_styles.items():
            if re.search(pattern, text, re.IGNORECASE):
                return style.upper()
        return "APA"  # Default
    
    def _extract_source_count(self, text: str) -> int:
        """Extract minimum source count."""
        for pattern in self.source_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 5  # Default
    
    def _extract_format_type(self, text: str) -> str:
        """Extract paper format type."""
        for format_type, pattern in self.format_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return format_type
        return "research paper"  # Default
    
    def _extract_methodology(self, text: str) -> str:
        """Extract methodology type."""
        for method, pattern in self.methodology_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return method
        return ""
    
    def _extract_sections(self, text: str) -> List[str]:
        """Extract required sections."""
        sections = []
        for section, keywords in self.section_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    sections.append(section)
                    break
        
        # If no sections found, use default academic structure
        if not sections:
            sections = ['introduction', 'literature review', 'methodology', 
                       'results', 'discussion', 'conclusion']
        
        return sections
    
    def _extract_source_requirements(self, text: str) -> List[str]:
        """Extract source requirements."""
        requirements = []
        
        patterns = {
            'peer-reviewed': r'peer[\s-]?reviewed',
            'recent (last 5 years)': r'(recent|last\s*\d+\s*years|近\d+年)',
            'academic journals': r'(academic|journal|scholarly)',
            'primary sources': r'primary\s*sources?',
            'empirical studies': r'empirical\s*(studies|research)',
        }
        
        for req, pattern in patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                requirements.append(req)
        
        return requirements
    
    def _extract_topic_and_focus(self, text: str) -> tuple:
        """Extract main topic and thesis focus."""
        # Common patterns for topic extraction
        topic_patterns = [
            r'(?:about|on|regarding|concerning)\s+(.+?)(?:\.|,|using|with|\n|$)',
            r'(?:topic|subject)[:\s]+(.+?)(?:\.|,|\n|$)',
            r'(?:关于|论述|分析)\s*(.+?)(?:\.|,|。|，)',
        ]
        
        topic = ""
        for pattern in topic_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                topic = match.group(1).strip()
                break
        
        # Extract focus
        focus_patterns = [
            r'(?:focus|focusing|focused)\s+(?:on\s+)?(.+?)(?:\.|,|\n|$)',
            r'(?:specifically|particularly)\s+(.+?)(?:\.|,|\n|$)',
            r'(?:重点|聚焦)\s*(.+?)(?:\.|,|。|，)',
        ]
        
        focus = ""
        for pattern in focus_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                focus = match.group(1).strip()
                break
        
        # If no topic found, use a summarized version of input
        if not topic:
            # Take first meaningful sentence as topic
            sentences = text.split('.')
            if sentences:
                topic = sentences[0].strip()[:200]
        
        return topic, focus
    
    def _extract_research_question(self, text: str) -> str:
        """Extract research question if present."""
        patterns = [
            r'research\s*question[:\s]+(.+?)(?:\?|\.|$)',
            r'investigate\s+(.+?)(?:\.|,|\n)',
            r'examine\s+(.+?)(?:\.|,|\n)',
            r'analyze\s+(.+?)(?:\.|,|\n)',
            r'研究问题[：:]\s*(.+?)(?:\?|？|\.|。)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_must_include(self, text: str) -> List[str]:
        """Extract must-include requirements."""
        items = []
        patterns = [
            r'(?:must|should|need to)\s+include\s+(.+?)(?:\.|,|$)',
            r'(?:including|include)[:\s]+(.+?)(?:\.|$)',
            r'(?:必须|需要|要求).*(?:包含|包括)\s*(.+?)(?:\.|,|。|，)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            items.extend([m.strip() for m in matches])
        
        return items
    
    def _extract_must_avoid(self, text: str) -> List[str]:
        """Extract must-avoid requirements."""
        items = []
        patterns = [
            r'(?:do not|don\'t|avoid|exclude)\s+(.+?)(?:\.|,|$)',
            r'(?:不要|避免|不能)\s*(.+?)(?:\.|,|。|，)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            items.extend([m.strip() for m in matches])
        
        return items
    
    def _extract_key_arguments(self, text: str) -> List[str]:
        """Extract key arguments or points to make."""
        items = []
        patterns = [
            r'(?:argue|argument|point)[:\s]+(.+?)(?:\.|,|$)',
            r'(?:thesis|claim)[:\s]+(.+?)(?:\.|,|$)',
            r'(?:论点|观点|主张)[：:]\s*(.+?)(?:\.|,|。|，)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            items.extend([m.strip() for m in matches])
        
        return items
    
    def _extract_academic_level(self, text: str) -> str:
        """Extract academic level."""
        patterns = {
            'undergraduate': r'(undergraduate|本科|bachelor)',
            'graduate': r'(graduate|master|硕士|研究生)',
            'phd': r'(phd|doctoral|dissertation|博士)',
        }
        
        for level, pattern in patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return level
        
        return "graduate"  # Default
    
    def format_requirements(self, req: PaperRequirements) -> str:
        """Format parsed requirements as readable text."""
        lines = [
            "=" * 50,
            "PARSED PAPER REQUIREMENTS",
            "=" * 50,
            "",
            f"Topic: {req.topic}",
            f"Format: {req.format_type.title()}",
            f"Academic Level: {req.academic_level.title()}",
        ]
        
        if req.thesis_focus:
            lines.append(f"Focus: {req.thesis_focus}")
        
        if req.research_question:
            lines.append(f"Research Question: {req.research_question}")
        
        lines.append("")
        lines.append("-" * 30)
        lines.append("STRUCTURE")
        lines.append("-" * 30)
        
        if req.word_count:
            lines.append(f"Word Count: {req.word_count}")
        if req.page_count:
            lines.append(f"Page Count: {req.page_count}")
        
        if req.required_sections:
            lines.append(f"Sections: {', '.join(req.required_sections)}")
        
        lines.append("")
        lines.append("-" * 30)
        lines.append("SOURCES")
        lines.append("-" * 30)
        lines.append(f"Citation Style: {req.citation_style}")
        lines.append(f"Minimum Sources: {req.min_sources}")
        
        if req.source_requirements:
            lines.append(f"Source Requirements: {', '.join(req.source_requirements)}")
        
        if req.methodology_type:
            lines.append(f"Methodology: {req.methodology_type}")
        
        if req.must_include:
            lines.append("")
            lines.append("-" * 30)
            lines.append("MUST INCLUDE")
            lines.append("-" * 30)
            for item in req.must_include:
                lines.append(f"  - {item}")
        
        if req.must_avoid:
            lines.append("")
            lines.append("-" * 30)
            lines.append("MUST AVOID")
            lines.append("-" * 30)
            for item in req.must_avoid:
                lines.append(f"  - {item}")
        
        lines.append("")
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def to_agent_prompt(self, req: PaperRequirements) -> str:
        """Convert requirements to a structured prompt for agents."""
        prompt = f"""PAPER REQUIREMENTS:

TOPIC: {req.topic}

FORMAT: {req.format_type.title()}
ACADEMIC LEVEL: {req.academic_level.title()}
"""
        
        if req.thesis_focus:
            prompt += f"FOCUS AREA: {req.thesis_focus}\n"
        
        if req.research_question:
            prompt += f"RESEARCH QUESTION: {req.research_question}\n"
        
        prompt += f"""
STRUCTURE REQUIREMENTS:
- Word Count: {req.word_count or 'Not specified'}
- Page Count: {req.page_count or 'Not specified'}
- Required Sections: {', '.join(req.required_sections) if req.required_sections else 'Standard academic structure'}

CITATION REQUIREMENTS:
- Style: {req.citation_style}
- Minimum Sources: {req.min_sources}
- Source Requirements: {', '.join(req.source_requirements) if req.source_requirements else 'Peer-reviewed academic sources'}
"""
        
        if req.methodology_type:
            prompt += f"- Methodology: {req.methodology_type}\n"
        
        if req.must_include:
            prompt += f"\nMUST INCLUDE:\n"
            for item in req.must_include:
                prompt += f"- {item}\n"
        
        if req.must_avoid:
            prompt += f"\nMUST AVOID:\n"
            for item in req.must_avoid:
                prompt += f"- {item}\n"
        
        if req.key_arguments:
            prompt += f"\nKEY ARGUMENTS TO MAKE:\n"
            for item in req.key_arguments:
                prompt += f"- {item}\n"
        
        prompt += """
Please produce output that adheres to ALL the above requirements.
Ensure all claims are properly cited and verified."""
        
        return prompt
