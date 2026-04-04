from __future__ import annotations

from datetime import datetime

from src.schemas import SafetyAnalysis


def build_markdown_report(
    analysis: SafetyAnalysis,
    *,
    filename: str,
    project_type: str,
    work_activity: str,
    notes: str,
) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    hazard_lines = []
    for index, hazard in enumerate(analysis.hazards, start=1):
        hazard_lines.append(
            "\n".join(
                [
                    f"{index}. {hazard.title} ({hazard.category}, severity: {hazard.severity})",
                    f"   Evidence: {hazard.evidence}",
                    f"   Action: {hazard.recommendation}",
                ]
            )
        )

    return f"""# Construction Safety Copilot Report

Generated: {timestamp}
Image: {filename}
Project type: {project_type or "Not provided"}
Work activity: {work_activity or "Not provided"}
Notes: {notes or "Not provided"}

## Overall Risk
{analysis.overall_risk}

## Scene Summary
{analysis.scene_summary}

## Hazards
{chr(10).join(hazard_lines) if hazard_lines else "No clear hazards identified from the provided image."}

## PPE Recommendations
{chr(10).join(f"- {item}" for item in analysis.ppe_recommendations)}

## Supervisor Follow-Up Questions
{chr(10).join(f"- {item}" for item in analysis.supervisor_questions)}

## Toolbox Talk Points
{chr(10).join(f"- {item}" for item in analysis.toolbox_talk_points)}

## Report Summary
{analysis.report_summary}

## Disclaimer
This output is an AI-assisted preliminary observation and should be reviewed by a qualified safety professional before any jobsite decision is made.
"""
