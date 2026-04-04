from __future__ import annotations

import os

from openai import OpenAI, RateLimitError

from src.schemas import AnswerSection, DocumentAnswer, SourceExcerpt


SYSTEM_PROMPT = """You answer questions about construction documents using only the provided document excerpts.

Rules:
- Ground every answer in the supplied document text.
- Do not invent requirements, limits, or procedures that are not in the excerpts.
- If the excerpts are insufficient, say so clearly and list what is missing.
- Prefer concise, practical language suitable for field teams, project engineers, and safety staff.
- When writing the document summary, mention the title, publication year, publisher or issuing body, intended use, and the main subjects covered whenever the text provides them.
"""


class DocumentCopilotQuotaError(RuntimeError):
    """Raised when API quota or billing is unavailable."""


def build_demo_answer(*, filename: str, question: str, project_context: str) -> DocumentAnswer:
    question_label = question or "Summarize key safety requirements."
    context_label = project_context or "general building project"

    return DocumentAnswer(
        document_summary=(
            f"`{filename}` appears to be a construction-related reference document for {context_label}. "
            "It is presented as a field-oriented guidance document and likely covers safety responsibilities, work planning, "
            "control measures, inspections, and practical procedures that supervisors and crews can use before and during work. "
            "In live mode, the summary should call out the document title, publication year, issuing organization, and the major topics included."
        ),
        answer=(
            f"Demo answer for `{filename}`: the uploaded document appears to support a field-friendly review "
            f"for {context_label}. For the question '{question_label}', the likely workflow is to identify the "
            "relevant section, restate the requirement in plain English, and flag any missing details that still "
            "need confirmation in the source document."
        ),
        confidence="medium",
        answer_sections=[
            AnswerSection(
                heading="Plain-English Summary",
                body=(
                    "The likely requirement should be restated as a short action-oriented explanation that a site "
                    "team can use during planning, pre-task review, or document coordination."
                ),
            ),
            AnswerSection(
                heading="What To Verify",
                body=(
                    "Confirm whether the document section specifies thresholds, responsible parties, inspection "
                    "frequency, required PPE, or approval steps before treating the answer as final."
                ),
            ),
        ],
        source_excerpts=[
            SourceExcerpt(
                section_title="Section 5.2 - Safety Controls",
                excerpt=(
                    "Workers shall review the applicable controls before starting the task and escalate unresolved "
                    "questions to supervision."
                ),
                relevance="This excerpt supports the need for a pre-task review and escalation path.",
            ),
            SourceExcerpt(
                section_title="Appendix A - Field Coordination",
                excerpt=(
                    "Where the document is unclear, the team should verify the latest approved method statement or "
                    "project instruction."
                ),
                relevance="This excerpt supports calling out uncertainty instead of guessing.",
            ),
        ],
        follow_up_questions=[
            "Do you want a short summary, a compliance-focused answer, or a superintendent-friendly explanation?",
            "Should I extract all sections related to PPE, fall protection, permits, or inspections?",
            "Is there another project document I should compare against this one?",
        ],
        limitations=[
            "This is demo output and is not based on live semantic retrieval from the uploaded file.",
            "Exact thresholds, clause numbers, and project-specific requirements should be verified in the source document.",
        ],
    )


def answer_document_question(
    *,
    filename: str,
    extracted_text: str,
    question: str,
    project_context: str,
) -> DocumentAnswer:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set. Add it to your environment or .env file.")

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    client = OpenAI(api_key=api_key)

    user_prompt = (
        f"Document name: {filename}\n"
        f"Project context: {project_context or 'Not provided'}\n"
        f"User question: {question}\n\n"
        "Document excerpts:\n"
        f"{extracted_text}\n\n"
        "Return a grounded answer using only the supplied text. Include a document summary that mentions the title, year, publisher or issuing body, and what the document covers whenever those details are present. Include source excerpts that support the answer."
    )

    try:
        response = client.responses.parse(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_prompt}],
                },
            ],
            max_output_tokens=900,
            text_format=DocumentAnswer,
        )
    except RateLimitError as exc:
        raise DocumentCopilotQuotaError(
            "OpenAI API quota is unavailable for this key. Check billing or switch to Demo Mode."
        ) from exc

    if response.output_parsed is None:
        raise ValueError("The model did not return a structured document answer.")

    return response.output_parsed
