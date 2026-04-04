from __future__ import annotations

from pydantic import BaseModel, Field


class AnswerSection(BaseModel):
    heading: str = Field(description="Short heading for one part of the answer.")
    body: str = Field(description="Plain-English explanation for that section.")


class SourceExcerpt(BaseModel):
    section_title: str = Field(description="Approximate section or heading from the source document.")
    excerpt: str = Field(description="Short supporting excerpt or paraphrased source passage.")
    relevance: str = Field(description="Why this excerpt matters to the answer.")


class DocumentAnswer(BaseModel):
    document_summary: str = Field(
        description="A richer document brief covering title, year, publisher or source when available, intended audience, and the main topics covered."
    )
    answer: str = Field(description="Direct answer to the user's question.")
    confidence: str = Field(description="One of low, medium, or high.")
    answer_sections: list[AnswerSection] = Field(description="Organized breakdown of the answer.")
    source_excerpts: list[SourceExcerpt] = Field(description="Evidence pulled from the document text.")
    follow_up_questions: list[str] = Field(description="Suggested follow-up questions the user might ask next.")
    limitations: list[str] = Field(description="What the answer could not fully confirm from the source text.")
