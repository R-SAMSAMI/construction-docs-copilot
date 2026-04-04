from __future__ import annotations

from datetime import datetime

from src.schemas import DocumentAnswer


def build_markdown_report(
    answer: DocumentAnswer,
    *,
    filename: str,
    project_context: str,
    question: str,
) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    section_lines = [
        f"### {section.heading}\n{section.body}" for section in answer.answer_sections
    ]
    excerpt_lines = [
        "\n".join(
            [
                f"{index}. {excerpt.section_title}",
                f"   Excerpt: {excerpt.excerpt}",
                f"   Why it matters: {excerpt.relevance}",
            ]
        )
        for index, excerpt in enumerate(answer.source_excerpts, start=1)
    ]

    return f"""# Construction Document Q&A Report

Generated: {timestamp}
Document: {filename}
Project context: {project_context or "Not provided"}
Question: {question}

## Direct Answer
{answer.answer}

## Document Summary
{answer.document_summary}

## Confidence
{answer.confidence}

## Answer Breakdown
{chr(10).join(section_lines) if section_lines else "No answer sections returned."}

## Supporting Excerpts
{chr(10).join(excerpt_lines) if excerpt_lines else "No supporting excerpts returned."}

## Suggested Follow-Up Questions
{chr(10).join(f"- {item}" for item in answer.follow_up_questions)}

## Limitations
{chr(10).join(f"- {item}" for item in answer.limitations)}

## Disclaimer
This output is an AI-assisted document review and should be verified against the latest approved project documents before making field or compliance decisions.
"""
