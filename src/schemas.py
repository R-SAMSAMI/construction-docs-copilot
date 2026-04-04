from __future__ import annotations

from pydantic import BaseModel, Field


class HazardItem(BaseModel):
    category: str = Field(
        description="Hazard category such as fall, struck-by, electrical, PPE, housekeeping, or equipment."
    )
    title: str = Field(description="Short hazard label.")
    severity: str = Field(description="One of low, medium, or high.")
    evidence: str = Field(description="What in the image or notes suggests the hazard exists.")
    recommendation: str = Field(description="Immediate corrective action.")


class SafetyAnalysis(BaseModel):
    overall_risk: str = Field(description="Overall site risk level: low, medium, or high.")
    scene_summary: str = Field(description="Short description of the visible work scene.")
    hazards: list[HazardItem] = Field(description="Detected or likely hazards.")
    ppe_recommendations: list[str] = Field(description="Recommended PPE for the scene.")
    supervisor_questions: list[str] = Field(description="Follow-up questions a supervisor should ask.")
    toolbox_talk_points: list[str] = Field(description="Brief safety discussion points.")
    report_summary: str = Field(description="Professional site observation summary for reporting.")
