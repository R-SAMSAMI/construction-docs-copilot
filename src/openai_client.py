from __future__ import annotations

import base64
import mimetypes
import os

from openai import OpenAI, RateLimitError

from src.schemas import HazardItem, SafetyAnalysis


SYSTEM_PROMPT = """You identify visible construction safety concerns from one image and brief jobsite notes.

Rules:
- Treat this as a preliminary observation, not a certified inspection.
- Focus on the most important visible risks only.
- Be specific, concise, and practical.
- If the image is unclear, say so instead of guessing.
"""


class SafetyCopilotQuotaError(RuntimeError):
    """Raised when API quota or billing is unavailable."""


def _to_data_url(image_bytes: bytes, filename: str) -> str:
    mime_type = mimetypes.guess_type(filename)[0] or "image/jpeg"
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def _trim_notes(notes: str, max_chars: int = 240) -> str:
    compact = " ".join((notes or "").split())
    if len(compact) <= max_chars:
        return compact or "Not provided"
    return compact[: max_chars - 3] + "..."


def build_demo_analysis(*, project_type: str, work_activity: str, notes: str) -> SafetyAnalysis:
    project_label = project_type or "active construction site"
    activity_label = work_activity or "general site work"
    note_summary = _trim_notes(notes, max_chars=120)

    return SafetyAnalysis(
        overall_risk="medium",
        scene_summary=(
            f"Preliminary demo review for {project_label} during {activity_label}. "
            "The scene should be checked for access control, PPE compliance, and housekeeping."
        ),
        hazards=[
            HazardItem(
                category="ppe",
                title="Possible missing or inconsistent PPE",
                severity="medium",
                evidence="The demo workflow assumes active field work where head, eye, and foot protection should be confirmed.",
                recommendation="Verify all workers have task-appropriate PPE before continuing work.",
            ),
            HazardItem(
                category="housekeeping",
                title="Access and housekeeping need review",
                severity="medium",
                evidence="Construction areas often contain cords, materials, or debris that can obstruct safe movement.",
                recommendation="Clear walking paths and organize materials to reduce trips and blocked access.",
            ),
            HazardItem(
                category="pre-task planning",
                title="Task-specific controls should be confirmed",
                severity="low",
                evidence=f"Notes provided: {note_summary}",
                recommendation="Confirm the pre-task plan, crew briefing, and any permit or exclusion-zone requirements.",
            ),
        ],
        ppe_recommendations=[
            "Hard hat, high-visibility vest, safety boots, and safety glasses",
            "Gloves matched to the task and material handling risk",
            "Fall protection if work is occurring at height",
        ],
        supervisor_questions=[
            "Has the crew completed a task-specific pre-job briefing today?",
            "Are access routes, exclusion zones, and material staging areas clearly controlled?",
            "Are any temporary power, overhead work, or mobile equipment interactions present?",
        ],
        toolbox_talk_points=[
            "Maintain clear walking and working surfaces throughout the shift.",
            "Stop work if PPE or access controls are missing or incomplete.",
            "Reconfirm communication between crews, spotters, and equipment operators.",
        ],
        report_summary=(
            f"Demo-mode site observation for {project_label}: review PPE compliance, housekeeping, and task controls "
            f"for {activity_label}. This sample output is intended for product demonstration when live API analysis is unavailable."
        ),
    )


def analyze_site_image(
    *,
    image_bytes: bytes,
    filename: str,
    project_type: str,
    work_activity: str,
    notes: str,
) -> SafetyAnalysis:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set. Add it to your environment or .env file.")

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    client = OpenAI(api_key=api_key)
    image_data_url = _to_data_url(image_bytes, filename)
    compact_notes = _trim_notes(notes)

    user_prompt = (
        "Review this construction image and return a short structured safety observation.\n"
        f"Project: {project_type or 'Not provided'}\n"
        f"Activity: {work_activity or 'Not provided'}\n"
        f"Notes: {compact_notes}\n"
        "Limit hazards to the most important 3 items."
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
                    "content": [
                        {"type": "input_text", "text": user_prompt},
                        {"type": "input_image", "image_url": image_data_url},
                    ],
                },
            ],
            max_output_tokens=450,
            text_format=SafetyAnalysis,
        )
    except RateLimitError as exc:
        raise SafetyCopilotQuotaError(
            "OpenAI API quota is unavailable for this key. Check billing or switch to Demo Mode."
        ) from exc

    if response.output_parsed is None:
        raise ValueError("The model did not return a structured safety analysis.")

    return response.output_parsed
