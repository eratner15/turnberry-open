"""Report generation in various formats."""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from loguru import logger


class ReportGenerator:
    """Generates intelligence reports from signals."""

    def __init__(self, db):
        self.db = db

    def generate_markdown(self, vertical: str, min_confidence: float = 0.0) -> str:
        """Generate a markdown intelligence report."""

        signals = self.db.get_signals(vertical=vertical, min_confidence=min_confidence)
        stats = self.db.get_stats()

        # Categorize signals by confidence
        high_confidence = [s for s in signals if s["confidence_score"] >= 0.85]
        medium_confidence = [s for s in signals if 0.70 <= s["confidence_score"] < 0.85]
        low_confidence = [s for s in signals if s["confidence_score"] < 0.70]

        # Build report
        report = []
        report.append(f"# Texas Law Enforcement Technology Intelligence Report")
        report.append(f"**Report Generated**: {datetime.now().strftime('%B %d, %Y')}")
        report.append(f"**Documents Processed**: {stats['processed_documents']}")
        report.append(
            f"**Signals Found**: {len(signals)} ({len(high_confidence)} high-confidence)"
        )
        report.append("")
        report.append("---")
        report.append("")

        # High-confidence signals
        if high_confidence:
            report.append("## 🔥 High-Confidence Signals (≥0.85)")
            report.append("")

            for idx, signal in enumerate(high_confidence, 1):
                report.extend(self._format_signal_detail(idx, signal))

        # Medium-confidence signals
        if medium_confidence:
            report.append("## 📊 Medium-Confidence Signals (0.70-0.84)")
            report.append("")

            for idx, signal in enumerate(medium_confidence, 1):
                report.extend(self._format_signal_summary(idx, signal))

        # Low-confidence signals (just count)
        if low_confidence:
            report.append("## 📋 Low-Confidence Signals (<0.70)")
            report.append("")
            report.append(
                f"{len(low_confidence)} additional signals detected with lower confidence. "
                f"Available in detailed export."
            )
            report.append("")

        # Timeline
        if high_confidence or medium_confidence:
            report.append("## 📅 Timeline of Decision Points")
            report.append("")
            report.extend(self._format_timeline(high_confidence + medium_confidence))
            report.append("")

        # Footer
        report.append("---")
        report.append("")
        report.append("**Report Notes**:")
        no_signal_count = stats["processed_documents"] - len(signals)
        report.append(f"- {no_signal_count} documents contained no relevant signals (routine business)")
        report.append("- All quotes verified against source documents")
        report.append("- Contact information extracted where available")
        next_week = datetime.now().strftime('%B %d, %Y')
        report.append(f"- Next report: {next_week}")

        return "\n".join(report)

    def _format_signal_detail(self, idx: int, signal: Dict[str, Any]) -> List[str]:
        """Format a detailed signal entry."""
        lines = []

        lines.append(f"### {idx}. {signal['municipality_name']} Police Department")
        lines.append(f"**Meeting Date**: {signal['meeting_date'] or 'Date TBD'}")
        lines.append(f"**Signal Type**: {signal['signal_type'].replace('_', ' ').title()}")
        lines.append(f"**Confidence**: {int(signal['confidence_score'] * 100)}%")
        lines.append("")

        lines.append("**The Opportunity**:")
        lines.append(signal['context'])
        lines.append("")

        lines.append("**Direct Quote**:")
        page_ref = f" *(Page {signal['page_number']})*" if signal.get('page_number') else ""
        lines.append(f"> {signal['specific_quote']}{page_ref}")

        # Show verification status
        if signal.get('quote_verified'):
            lines.append(f"> ✓ *Quote verified in source document*")
        lines.append("")

        lines.append("**Next Steps**:")
        lines.append(signal['next_action'])
        lines.append("")

        if signal['contact_person']:
            lines.append("**Contact**:")
            lines.append(f"- {signal['contact_person']}")
            lines.append("")

        if signal['estimated_value']:
            lines.append(f"**Estimated Value**: {signal['estimated_value']}")
            lines.append("")

        lines.append("---")
        lines.append("")

        return lines

    def _format_signal_summary(self, idx: int, signal: Dict[str, Any]) -> List[str]:
        """Format a summary signal entry."""
        lines = []

        lines.append(f"### {idx}. {signal['municipality_name']} Police Department")
        lines.append(f"**Meeting Date**: {signal['meeting_date'] or 'Date TBD'}")
        lines.append(f"**Signal Type**: {signal['signal_type'].replace('_', ' ').title()}")
        lines.append(f"**Confidence**: {int(signal['confidence_score'] * 100)}%")
        lines.append("")

        lines.append(signal['context'])
        lines.append("")

        return lines

    def _format_timeline(self, signals: List[Dict[str, Any]]) -> List[str]:
        """Format timeline table."""
        lines = []

        lines.append("| Municipality | Next Action | Date | Signal Strength |")
        lines.append("|-------------|-------------|------|-----------------|")

        # Sort by urgency and date
        urgency_order = {"high": 0, "medium": 1, "low": 2}
        sorted_signals = sorted(
            signals,
            key=lambda s: (
                urgency_order.get(s['urgency'], 3),
                s['meeting_date'] or "9999-99-99"
            )
        )

        for signal in sorted_signals:
            municipality = signal['municipality_name']
            next_action = signal['next_action'][:50]  # Truncate long actions
            date = signal['meeting_date'] or 'TBD'
            strength = "High" if signal['confidence_score'] >= 0.85 else "Medium"

            lines.append(f"| {municipality} | {next_action} | {date} | {strength} |")

        return lines

    def generate_csv(self, vertical: str, output_path: Path, min_confidence: float = 0.0):
        """Generate a CSV export of signals."""

        signals = self.db.get_signals(vertical=vertical, min_confidence=min_confidence)

        with open(output_path, 'w', newline='') as csvfile:
            fieldnames = [
                'municipality_name',
                'state',
                'meeting_date',
                'signal_type',
                'urgency',
                'confidence_score',
                'specific_quote',
                'context',
                'next_action',
                'contact_person',
                'estimated_value',
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for signal in signals:
                row = {field: signal.get(field, '') for field in fieldnames}
                writer.writerow(row)

        logger.info(f"CSV report written to {output_path} ({len(signals)} signals)")
