from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from src.document_utils import build_document_preview, clip_text_for_prompt, extract_document_text
from src.openai_client import (
    DocumentCopilotQuotaError,
    answer_document_question,
    build_demo_answer,
)
from src.reporting import build_markdown_report

load_dotenv()


def _friendly_document_error(exc: Exception) -> None:
    st.error(str(exc))

st.set_page_config(
    page_title="Construction Docs Copilot",
    page_icon=":bookmark_tabs:",
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

    .source-card {
        background: rgba(255,255,255,0.64);
        border: 1px solid var(--line);
        border-left: 6px solid var(--accent);
        border-radius: 20px;
        padding: 1rem 1rem 0.9rem 1rem;
        margin-bottom: 0.8rem;
    }

    .source-meta {
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
            <div class="eyebrow">Portfolio MVP | Applied GenAI for Construction</div>
        <div class="hero-title">Construction Docs Copilot</div>
        <div class="hero-copy">
            Upload a spec, safety manual, or method statement, ask a plain-English question, and get a grounded
            answer with supporting excerpts that feels useful to project engineers, supers, and safety teams.
        </div>
        <div class="chip-row">
            <div class="chip">Document Q&A</div>
            <div class="chip">Grounded Answers</div>
            <div class="chip">Source Excerpts</div>
            <div class="chip">Report Download</div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Why This Demo Works")
    st.write(
        "This version carries the same product language as the safety app while showing a different AI workflow. "
        "It turns a construction document into a practical grounded Q&A experience."
    )
    st.info(
        "AI-assisted output only. Final compliance, contractual, and field decisions should always be verified against approved documents."
    )
    demo_mode = st.toggle("Demo mode (no API cost)", value=True)
    if demo_mode:
        st.success("Demo mode is on. The app will generate a realistic answer without calling the API.")
    else:
        st.warning("Live API mode is on. This uses your OpenAI API credits.")
    st.markdown("**Suggested demo questions**")
    st.write("- What are the main safety requirements in this document?")
    st.write("- Summarize the key controls the field team should follow.")
    st.write("- Which sections mention PPE, inspections, or work planning?")

input_col, preview_col = st.columns([1.05, 0.95], gap="large")

with input_col:
    st.markdown('<div class="panel panel-strong">', unsafe_allow_html=True)
    st.subheader("Document Intake")
    st.caption("Upload one project document and ask a practical question in plain English.")
    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["pdf", "docx", "txt", "md"],
        help="Supports PDF, DOCX, TXT, and Markdown documents.",
    )
    project_context = st.text_input(
        "Project context",
        placeholder="Hospital expansion, bridge rehabilitation, warehouse buildout, school renovation...",
    )
    user_question = st.text_area(
        "Question to ask",
        placeholder="What are the main safety requirements in this document?",
        height=130,
    )
    ask_button = st.button("Ask Document", type="primary", width="stretch")
    st.markdown("</div>", unsafe_allow_html=True)

with preview_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Document Summary")
    st.caption("High-level orientation for the uploaded file and the latest generated summary.")
    if uploaded_file:
        try:
            extracted_preview_text = extract_document_text(uploaded_file.name, uploaded_file.getvalue())
            preview_text = build_document_preview(extracted_preview_text)
        except Exception as exc:
            _friendly_document_error(exc)
        else:
            st.write(f"**File:** {uploaded_file.name}")
            st.write(f"**File type:** {uploaded_file.name.split('.')[-1].upper()}")
            st.write(f"**Extracted text length:** {len(extracted_preview_text):,} characters")
            latest_summary = st.session_state.get("latest_document_summary")
            latest_filename = st.session_state.get("latest_document_name")
            if latest_summary and latest_filename == uploaded_file.name:
                st.markdown("**Generated summary**")
                st.write(latest_summary)
            else:
                st.markdown("**Preview snippet**")
                st.code(preview_text or "No extractable text found in the uploaded document.", language="markdown")
    else:
        st.markdown(
            """
            <div style="padding: 2.1rem 1rem; text-align: center; color: #5f675e; border: 1px dashed rgba(31,41,35,0.16); border-radius: 18px; background: rgba(255,255,255,0.35);">
                Upload a document and ask a question to see its generated summary here.
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

if ask_button:
    if not uploaded_file:
        st.error("Please upload a document before asking a question.")
    elif not user_question.strip():
        st.error("Please enter a question before running the document assistant.")
    else:
        with st.spinner("Reading the document and preparing a grounded answer..."):
            try:
                file_bytes = uploaded_file.getvalue()
                extracted_text = extract_document_text(uploaded_file.name, file_bytes)
                if not extracted_text:
                    raise ValueError("No readable text could be extracted from this file.")

                if demo_mode:
                    answer = build_demo_answer(
                        filename=uploaded_file.name,
                        question=user_question,
                        project_context=project_context,
                    )
                else:
                    answer = answer_document_question(
                        filename=uploaded_file.name,
                        extracted_text=clip_text_for_prompt(extracted_text),
                        question=user_question,
                        project_context=project_context,
                    )

                report_markdown = build_markdown_report(
                    answer,
                    filename=uploaded_file.name,
                    project_context=project_context,
                    question=user_question,
                )
                st.session_state["latest_document_summary"] = answer.document_summary
                st.session_state["latest_document_name"] = uploaded_file.name
            except DocumentCopilotQuotaError as exc:
                st.error(str(exc))
                st.info(
                    "Tip: turn on Demo Mode in the sidebar to keep presenting the app without using API quota."
                )
            except Exception as exc:
                _friendly_document_error(exc)
            else:
                st.success("Demo answer ready." if demo_mode else "Document answer ready.")

                top_left, top_mid, top_right = st.columns([2.4, 1, 1], gap="large")
                with top_left:
                    st.markdown('<div class="panel">', unsafe_allow_html=True)
                    st.subheader("Direct Answer")
                    st.markdown(
                        '<div class="section-note">Grounded response to the user question based on extracted document text.</div>',
                        unsafe_allow_html=True,
                    )
                    st.write(answer.answer)
                    st.markdown("</div>", unsafe_allow_html=True)
                with top_mid:
                    st.metric("Confidence", answer.confidence.title())
                with top_right:
                    st.metric("Sources Used", len(answer.source_excerpts))

                st.subheader("Answer Breakdown")
                st.markdown(
                    '<div class="section-note">Organized explanation designed to feel useful to project teams instead of generic chatbot output.</div>',
                    unsafe_allow_html=True,
                )
                for section in answer.answer_sections:
                    st.markdown('<div class="panel">', unsafe_allow_html=True)
                    st.markdown(f"### {section.heading}")
                    st.write(section.body)
                    st.markdown("</div>", unsafe_allow_html=True)

                st.subheader("Supporting Excerpts")
                st.markdown(
                    '<div class="section-note">These source snippets are the grounding evidence for the answer.</div>',
                    unsafe_allow_html=True,
                )
                if answer.source_excerpts:
                    for excerpt in answer.source_excerpts:
                        st.markdown(
                            f"""
                            <div class="source-card">
                                <h4 style="margin: 0 0 0.35rem 0;">{excerpt.section_title}</h4>
                                <div class="source-meta">Document support for the answer</div>
                                <div><strong>Excerpt:</strong> {excerpt.excerpt}</div>
                                <div style="margin-top: 0.45rem;"><strong>Why it matters:</strong> {excerpt.relevance}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No supporting excerpts were returned.")

                lower_left, lower_right = st.columns(2, gap="large")
                with lower_left:
                    st.markdown('<div class="panel">', unsafe_allow_html=True)
                    st.subheader("Suggested Follow-Up")
                    for item in answer.follow_up_questions:
                        st.write(f"- {item}")
                    st.markdown("</div>", unsafe_allow_html=True)
                with lower_right:
                    st.markdown('<div class="panel">', unsafe_allow_html=True)
                    st.subheader("Limitations")
                    for item in answer.limitations:
                        st.write(f"- {item}")
                    st.download_button(
                        "Download Markdown Report",
                        data=report_markdown.encode("utf-8"),
                        file_name="construction-document-answer.md",
                        mime="text/markdown",
                        width="stretch",
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

                with st.expander("View generated report"):
                    st.code(report_markdown, language="markdown")
