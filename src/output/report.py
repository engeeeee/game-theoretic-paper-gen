"""
Report Generator

Generates comprehensive verification reports.
"""

from datetime import datetime
from typing import Optional
from ..engine.adaptive_debate import DebateResult
from ..engine.voting import VotingResult
from ..citation_moat.moat_engine import MoatReport
from .consensus import Consensus


class ReportGenerator:
    """
    Generates detailed verification reports.
    
    Includes:
    - Executive summary
    - Citation audit
    - Scoring breakdown
    - Debate transcript
    - Voting results
    """
    
    def generate_full_report(
        self,
        debate_result: DebateResult,
        consensus: Consensus,
        voting_result: Optional[VotingResult] = None
    ) -> str:
        """
        Generate a complete verification report.
        
        Args:
            debate_result: Results from the debate
            consensus: Generated consensus
            voting_result: Voting results
            
        Returns:
            Formatted report string
        """
        sections = [
            self._header(),
            self._executive_summary(debate_result, consensus),
            self._citation_audit(debate_result),
            self._scoring_breakdown(debate_result, voting_result),
            self._debate_summary(debate_result),
            self._consensus_section(consensus),
            self._footer(),
        ]
        
        return "\n\n".join(sections)
    
    def _header(self) -> str:
        """Generate report header."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""{'=' * 70}
ACADEMIC VERIFICATION REPORT
Game-Theoretic Multi-Agent System
{'=' * 70}
Generated: {timestamp}
{'=' * 70}"""
    
    def _executive_summary(
        self,
        debate_result: DebateResult,
        consensus: Consensus
    ) -> str:
        """Generate executive summary."""
        return f"""EXECUTIVE SUMMARY
{'-' * 40}
Verdict: {consensus.verdict}
Academic Integrity: {"VERIFIED" if consensus.confidence >= 75 else "NEEDS REVIEW"}
Confidence Score: {consensus.confidence:.1f}/100

Debate Status: {debate_result.status.value}
Total Rounds: {debate_result.total_rounds}
Re-evaluations: {debate_result.re_evaluations}

Verified Claims: {len(consensus.verified_claims)}
Rejected Claims: {len(consensus.rejected_claims)}
Remaining Disputes: {len(consensus.remaining_disputes)}"""
    
    def _citation_audit(self, debate_result: DebateResult) -> str:
        """Generate citation audit section."""
        # Aggregate citation stats from all rounds
        total = 0
        verified = 0
        modified = 0
        deleted = 0
        
        for round in debate_result.rounds:
            if round.citation_report:
                total += round.citation_report.total_citations
                verified += round.citation_report.verified_count
                modified += round.citation_report.modified_count
                deleted += round.citation_report.deleted_count
        
        verification_rate = (verified / total * 100) if total > 0 else 0
        
        return f"""CITATION AUDIT
{'-' * 40}
Total Citations Processed: {total}
Verified: {verified} ({verification_rate:.1f}%)
Modified: {modified}
Deleted: {deleted}

Citation Moat Status: {"PASSED" if verification_rate >= 80 else "NEEDS ATTENTION"}"""
    
    def _scoring_breakdown(
        self,
        debate_result: DebateResult,
        voting_result: Optional[VotingResult]
    ) -> str:
        """Generate scoring breakdown."""
        lines = [
            "SCORING BREAKDOWN",
            "-" * 40,
        ]
        
        if voting_result:
            lines.extend([
                "Criterion Scores:",
                f"  {'Criterion':<15} {'Score':>8} {'Status':>8}",
                f"  {'-' * 35}",
            ])
            
            for criterion, score in voting_result.criterion_scores.items():
                status = "PASS" if score >= 75 else "FAIL"
                lines.append(f"  {criterion.capitalize():<15} {score:>8.1f} {status:>8}")
            
            lines.extend([
                f"  {'-' * 35}",
                f"  {'WEIGHTED AVG':<15} {voting_result.weighted_average:>8.1f} "
                f"{'PASS' if voting_result.passed else 'FAIL':>8}",
            ])
        else:
            lines.append(f"  Final Score: {debate_result.final_score:.1f}/100")
        
        return "\n".join(lines)
    
    def _debate_summary(self, debate_result: DebateResult) -> str:
        """Generate debate summary."""
        lines = [
            "REVIEW ITERATIONS",
            "-" * 40,
            f"Total Rounds: {debate_result.total_rounds}",
            f"Re-evaluations: {debate_result.re_evaluations}",
            f"Final Status: {debate_result.status.value}",
            "",
            "Round Progression:",
        ]
        
        for round in debate_result.rounds[-5:]:  # Last 5 rounds
            score = round.round_score.total_score if round.round_score else 0
            lines.append(f"  Round {round.round_number}: Score {score:.1f}")
        
        return "\n".join(lines)
    
    def _consensus_section(self, consensus: Consensus) -> str:
        """Generate consensus section."""
        lines = [
            "VERIFIED CONSENSUS",
            "-" * 40,
        ]
        
        if consensus.verified_claims:
            lines.append("Accepted Claims:")
            for claim in consensus.verified_claims[:5]:
                lines.append(f"  - {claim[:80]}...")
        
        if consensus.rejected_claims:
            lines.extend(["", "Rejected Claims:"])
            for claim in consensus.rejected_claims[:5]:
                lines.append(f"  - {claim[:80]}...")
        
        lines.extend(["", consensus.summary])
        
        return "\n".join(lines)
    
    def _footer(self) -> str:
        """Generate report footer."""
        return f"""{'=' * 70}
END OF REPORT
{'=' * 70}

This report was generated by the Game-Theoretic Multi-Agent System.
All claims have undergone dual-agent verification with citation moat.
Only verified claims are included in the final consensus."""
    
    def save_report(
        self,
        report: str,
        filepath: str
    ) -> None:
        """Save report to file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
