# ABOUTME: Report generation and suggestion tracking tools
# ABOUTME: Create structured reports and track suggestions over time

from claude_agent_sdk import tool
from typing import Any, Dict, List
from datetime import datetime
from pathlib import Path


class ReportTools:
    def __init__(self, memory_manager, reports_dir: str = "storage/reports"):
        self.memory = memory_manager
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def get_tools(self):
        """Return list of report and suggestion tools"""
        return [
            self._create_report_tool(),
            self._add_suggestion_tool(),
            self._list_suggestions_tool()
        ]

    def _create_report_tool(self):
        @tool(
            "create_report",
            "Generate a structured report with sections, findings, and recommendations. Saves as markdown.",
            {
                "title": str,
                "summary": str,
                "sections": list,  # List of {"heading": str, "content": str}
                "recommendations": list  # List of recommendation strings
            }
        )
        async def create_report(args: Dict[str, Any]) -> Dict[str, Any]:
            title = args["title"]
            summary = args["summary"]
            sections = args.get("sections", [])
            recommendations = args.get("recommendations", [])

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
            safe_title = safe_title.replace(' ', '_')[:50]
            filename = f"report_{timestamp}_{safe_title}.md"
            file_path = self.reports_dir / filename

            # Build report
            report = f"# {title}\n\n"
            report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            report += "---\n\n"

            report += "## Executive Summary\n\n"
            report += f"{summary}\n\n"

            if sections:
                for section in sections:
                    heading = section.get("heading", "Section")
                    content = section.get("content", "")
                    report += f"## {heading}\n\n{content}\n\n"

            if recommendations:
                report += "## Recommendations\n\n"
                for i, rec in enumerate(recommendations, 1):
                    report += f"{i}. {rec}\n"
                report += "\n"

            # Save to file
            file_path.write_text(report, encoding="utf-8")

            return {
                "content": [{
                    "type": "text",
                    "text": f"[OK] Report created: {title}\n"
                           f"File: {file_path}\n"
                           f"Sections: {len(sections)}\n"
                           f"Recommendations: {len(recommendations)}"
                }]
            }

        return create_report

    def _add_suggestion_tool(self):
        @tool(
            "add_suggestion",
            "Record a suggestion or recommendation for future action. Can include context.",
            {
                "content": str,
                "context": str  # Optional context
            }
        )
        async def add_suggestion(args: Dict[str, Any]) -> Dict[str, Any]:
            content = args["content"]
            context = args.get("context", "")

            suggestion_id = await self.memory.save_suggestion(
                content=content,
                context=context,
                session_id=None  # Will be set by client
            )

            return {
                "content": [{
                    "type": "text",
                    "text": f"[OK] Suggestion saved (ID: {suggestion_id})\n"
                           f"{content}"
                }]
            }

        return add_suggestion

    def _list_suggestions_tool(self):
        @tool(
            "list_suggestions",
            "List recent suggestions with context",
            {
                "limit": int  # Max suggestions to return, default 10
            }
        )
        async def list_suggestions(args: Dict[str, Any]) -> Dict[str, Any]:
            limit = args.get("limit", 10)

            # Query database
            async with self.memory.db_path as db_path:
                import aiosqlite
                async with aiosqlite.connect(self.memory.db_path) as db:
                    cursor = await db.execute(
                        """SELECT id, content, context, created_at
                           FROM suggestions
                           ORDER BY created_at DESC
                           LIMIT ?""",
                        (limit,)
                    )
                    rows = await cursor.fetchall()

            if not rows:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[INFO] No suggestions found"
                    }]
                }

            output = f"[OK] Recent suggestions ({len(rows)}):\n\n"
            for row in rows:
                output += f"**Suggestion #{row[0]}**\n"
                output += f"{row[1]}\n"
                if row[2]:
                    output += f"  Context: {row[2]}\n"
                output += f"  Created: {row[3]}\n\n"

            return {
                "content": [{
                    "type": "text",
                    "text": output
                }]
            }

        return list_suggestions
