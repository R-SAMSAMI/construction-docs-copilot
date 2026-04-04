from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from src.openai_client import (
    SafetyCopilotQuotaError,
    analyze_site_image,
    build_demo_analysis,
)
from src.reporting import build_markdown_report

load_dotenv()

st.set_page_config(
    page_title="Construction Safety Copilot",
    page_icon=":building_construction:",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

    :root {
        --bg: #f5efe3;
        --panel: rgba(255, 252, 246, 0.86);
        --panel-strong: rgba(245, 238, 226, 0.96);
        --ink: #1f2a22;
        --muted: #5c665f;
        --accent: #c65a28;
        --accent-dark: #8f3d17;
        --line: rgba(31, 42, 34, 0.09);
        --shadow: 0 18px 45px rgba(75, 56, 38, 0.12);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(198, 90, 40, 0.18), transparent 24%),
            radial-gradient(circle at top right, rgba(110, 124, 69, 0.18), transparent 22%),
            linear-gradient(180deg, #f9f3e8 0%, var(--bg) 100%);
        color: var(--ink);
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--ink);
        letter-spacing: -0.02em;
    }

    .hero {
        background: linear-gradient(135deg, rgba(255,252,246,0.96), rgba(245,238,226,0.88));
        border: 1px solid var(--line);
        border-radius: 28px;
        padding: 1.8rem 1.8rem 1.4rem 1.8rem;
        box-shadow: var(--shadow);
        margin-bottom: 1.2rem;
        position: relative;
        overflow: hidden;
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        right: -60px;
        top: -110px;
        background: radial-gradient(circle, rgba(198,90,40,0.20) 0%, rgba(198,90,40,0) 70%);
    }

    .eyebrow {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.78rem;
        font-weight: 700;
        color: var(--accent-dark);
        margin-bottom: 0.65rem;
    }

    .hero-title {
        font-size: 3rem;
        line-height: 1;
        margin-bottom: 0.65rem;
        max-width: 760px;
    }

    .hero-copy {
        color: var(--muted);
        font-size: 1.02rem;
        max-width: 760px;
        margin-bottom: 1.1rem;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 0.4rem;
    }

    .chip {
        background: rgba(198, 90, 40, 0.08);
        border: 1px solid rgba(198, 90, 40, 0.16);
        color: var(--accent-dark);
        border-radius: 999px;
        padding: 0.45rem 0.8rem;
        font-size: 0.88rem;
        font-weight: 600;
    }

    .panel {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 1.1rem 1.1rem 0.9rem 1.1rem;
        box-shadow: var(--shadow);
    }

    .panel-strong {
        background: var(--panel-strong);
    }

    [data-testid="stSidebar"] {
        background: rgba(255, 249, 238, 0.92);
        border-right: 1px solid var(--line);
    }

    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.55);
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 1rem;
    }

    div[data-testid="stFileUploader"],
    div[data-testid="stTextInput"],
    div[data-testid="stTextArea"] {
        background: rgba(255,255,255,0.45);
        border-radius: 18px;
        padding: 0.3rem 0.5rem 0.5rem 0.5rem;
        border: 1px solid rgba(31, 42, 34, 0.05);
    }

    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, var(--accent), #d77538) !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 0.75rem 1rem !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 24px rgba(198, 90, 40, 0.22);
    }

    .hazard-card {
        background: rgba(255,255,255,0.6);
        border: 1px solid var(--line);
        border-left: 6px solid var(--accent);
        border-radius: 20px;
        padding: 1rem 1rem 0.9rem 1rem;
        margin-bottom: 0.8rem;
    }

    .hazard-meta {
        color: var(--muted);
        font-size: 0.92rem;
        margin-bottom: 0.4rem;
    }

    .section-note {
        color: var(--muted);
        margin-top: -0.25rem;
        margin-bottom: 0.9rem;
    }

    @media (max-width: 900px) {
        .hero-title {
            font-size: 2.3rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
        <div class="eyebrow">Portfolio MVP | Multimodal GenAI for Construction</div>
        <div class="hero-title">Construction Safety Copilot</div>
        <div class="hero-copy">
            Review a jobsite image, combine it with field context, and generate a structured safety
            observation that feels useful to a superintendent, project manager, or safety lead.
        </div>
        <div class="chip-row">
            <div class="chip">Image Understanding</div>
            <div class="chip">Hazard Reasoning</div>
            <div class="chip">PPE Guidance</div>
            <div class="chip">Report Drafting</div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Why This Demo Works")
    st.write(
        "This version is built as a recruiter-friendly product demo, not just a notebook. "
        "It turns a construction image into a practical safety observation workflow."
    )
    st.info(
        "AI-assisted output only. Final site decisions should always be reviewed by a qualified safety professional."
    )
    demo_mode = st.toggle("Demo mode (no API cost)", value=True)
    if demo_mode:
        st.success("Demo mode is on. The app will generate a realistic sample analysis without calling the API.")
    else:
        st.warning("Live API mode is on. This uses your OpenAI API credits.")
    st.markdown("**Suggested demo inputs**")
    st.write("- Active site with visible workers or equipment")
    st.write("- Scaffold, ladder, trench, or roof work")
    st.write("- Material storage or housekeeping concerns")

input_col, preview_col = st.columns([1.05, 0.95], gap="large")

with input_col:
    st.markdown('<div class="panel panel-strong">', unsafe_allow_html=True)
    st.subheader("Inspection Intake")
    st.caption("Add just enough context to make the analysis more credible and jobsite-specific.")
    uploaded_file = st.file_uploader(
        "Upload a jobsite image",
        type=["png", "jpg", "jpeg", "webp"],
    )
    project_type = st.text_input(
        "Project type",
        placeholder="Commercial tower, bridge rehabilitation, roadway widening, residential framing...",
    )
    work_activity = st.text_input(
        "Work activity",
        placeholder="Excavation, concrete pour, facade work, steel erection, roofing...",
    )
    notes = st.text_area(
        "Additional notes",
        placeholder="Crew size, weather, nearby traffic, temporary power, overhead work, subcontractor scope...",
        height=150,
    )
    analyze_button = st.button("Analyze Site", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with preview_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Image Preview")
    st.caption("A strong portfolio demo usually uses one sharp, realistic site image with clear activity.")
    if uploaded_file:
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)
    else:
        st.markdown(
            """
            <div style="padding: 2.1rem 1rem; text-align: center; color: #5c665f; border: 1px dashed rgba(31,42,34,0.16); border-radius: 18px; background: rgba(255,255,255,0.35);">
                Upload an image to preview it here and generate the safety observation.
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

if analyze_button:
    if not uploaded_file:
        st.error("Please upload an image before running the safety analysis.")
    else:
        image_bytes = uploaded_file.getvalue()
        with st.spinner("Reviewing the image and drafting the safety observation..."):
            try:
                if demo_mode:
                    analysis = build_demo_analysis(
                        project_type=project_type,
                        work_activity=work_activity,
                        notes=notes,
                    )
                else:
                    analysis = analyze_site_image(
                        image_bytes=image_bytes,
                        filename=uploaded_file.name,
                        project_type=project_type,
                        work_activity=work_activity,
                        notes=notes,
                    )
                report_markdown = build_markdown_report(
                    analysis,
                    filename=uploaded_file.name,
                    project_type=project_type,
                    work_activity=work_activity,
                    notes=notes,
                )
            except SafetyCopilotQuotaError as exc:
                st.error(str(exc))
                st.info(
                    "Tip: turn on Demo Mode in the sidebar to keep presenting the app without using API quota."
                )
            except Exception as exc:
                st.exception(exc)
            else:
                st.success("Demo analysis ready." if demo_mode else "Safety analysis ready.")

                top_left, top_mid, top_right = st.columns([2.4, 1, 1], gap="large")
                with top_left:
                    st.markdown('<div class="panel">', unsafe_allow_html=True)
                    st.subheader("Scene Summary")
                    st.markdown(
                        '<div class="section-note">High-level interpretation of the visible work environment.</div>',
                        unsafe_allow_html=True,
                    )
                    st.write(analysis.scene_summary)
                    st.markdown("</div>", unsafe_allow_html=True)
                with top_mid:
                    st.metric("Overall Risk", analysis.overall_risk.title())
                with top_right:
                    st.metric("Hazards Flagged", len(analysis.hazards))

                st.subheader("Detected Hazards")
                st.markdown(
                    '<div class="section-note">These are likely safety concerns inferred from the image and your notes. They should be reviewed by a human.</div>',
                    unsafe_allow_html=True,
                )
                if analysis.hazards:
                    for hazard in analysis.hazards:
                        st.markdown(
                            f"""
                            <div class="hazard-card">
                                <h4 style="margin: 0 0 0.35rem 0;">{hazard.title}</h4>
                                <div class="hazard-meta">Category: {hazard.category} | Severity: {hazard.severity}</div>
                                <div><strong>Evidence:</strong> {hazard.evidence}</div>
                                <div style="margin-top: 0.45rem;"><strong>Recommended action:</strong> {hazard.recommendation}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No clear hazards were identified from the provided image.")

                details_left, details_right = st.columns(2, gap="large")
                with details_left:
                    st.markdown('<div class="panel">', unsafe_allow_html=True)
                    st.subheader("PPE Recommendations")
                    for item in analysis.ppe_recommendations:
                        st.write(f"- {item}")
                    st.markdown("</div>", unsafe_allow_html=True)
                with details_right:
                    st.markdown('<div class="panel">', unsafe_allow_html=True)
                    st.subheader("Supervisor Follow-Up")
                    for item in analysis.supervisor_questions:
                        st.write(f"- {item}")
                    st.markdown("</div>", unsafe_allow_html=True)

                lower_left, lower_right = st.columns([1.1, 0.9], gap="large")
                with lower_left:
                    st.markdown('<div class="panel">', unsafe_allow_html=True)
                    st.subheader("Toolbox Talk Points")
                    for item in analysis.toolbox_talk_points:
                        st.write(f"- {item}")
                    st.markdown("</div>", unsafe_allow_html=True)
                with lower_right:
                    st.markdown('<div class="panel">', unsafe_allow_html=True)
                    st.subheader("Report Summary")
                    st.write(analysis.report_summary)
                    st.download_button(
                        "Download Markdown Report",
                        data=report_markdown.encode("utf-8"),
                        file_name="construction-safety-report.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

                with st.expander("View generated report"):
                    st.code(report_markdown, language="markdown")
