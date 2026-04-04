# Construction Docs Copilot

Construction Docs Copilot is a document intelligence tool for construction teams. It helps users review project documents, ask plain-English questions, and generate grounded answers with supporting excerpts and report-ready outputs.

It is designed for day-to-day document workflows involving safety manuals, specifications, method statements, procedures, and other operational references used by field and project teams.

## App Preview

Product preview:

![Construction Docs Copilot preview](assets/demo-preview.gif)

Full recording: [View the demo video](assets/demo-recording.mp4)

### Document Intake

![Document intake](assets/screenshot-intake.png)

### Grounded Answer Results

![Grounded answer results](assets/screenshot-results.png)

### Supporting Excerpts

![Supporting excerpts](assets/screenshot-excerpts.png)

### Report Output

![Report output](assets/screenshot-report.png)

## Product Purpose

Construction Docs Copilot helps construction teams work with document-heavy processes more efficiently. Instead of manually searching through long PDFs or procedures, users can upload a document, ask a focused question, and get a grounded answer tied back to the source text.

The product is intended to support document review, field coordination, pre-task planning, safety communication, and operational decision support.

## Target Workflows

- Reviewing safety manuals before work starts
- Checking specifications and method statements during planning
- Pulling key requirements from procedures or guidance documents
- Summarizing long documents for field teams or supervisors
- Preparing report-ready notes from document-based questions

## Core Capabilities

- Upload and process construction documents
- Ask plain-English questions against uploaded source material
- Generate grounded answers tied to extracted document text
- Produce structured document summaries
- Return supporting excerpts that explain the answer
- Suggest follow-up questions for deeper review
- Export a Markdown report for sharing or recordkeeping

## Operating Modes

The application supports two operating modes.

### Demo Mode

Use Demo Mode to explore the interface and workflow without calling the OpenAI API.

What it does:

- does not call the OpenAI API
- generates a realistic sample response
- allows the full UI and report flow to be tested without API usage

### Live API Mode

Use Live API Mode to run document question answering against uploaded files.

What it does:

- extracts text from the uploaded document
- sends the extracted content and user question to the OpenAI API
- returns a structured answer with summary, excerpts, and follow-up items

## Supported File Types

- PDF
- DOCX
- TXT
- Markdown

## Example Use Cases

- "When must employers provide fall protection?"
- "Summarize the key controls in this method statement."
- "Which sections mention PPE, inspections, or work planning?"
- "What should a supervisor review with the crew before starting work?"
- "What does this document say about confined space entry requirements?"

## How It Works

1. Upload a supported construction document.
2. Add optional project context.
3. Ask a question in plain English.
4. The system extracts document text and prepares a grounded response.
5. The application returns:
   - a direct answer
   - a document summary
   - supporting source excerpts
   - follow-up questions
   - limitations and uncertainty notes
6. Users can download the generated response as a Markdown report.

## Tech Stack

- Python
- Streamlit
- OpenAI Responses API
- Pydantic
- PyPDF
- python-docx
- python-dotenv

## Project Structure

```text
.
|-- app.py
|-- requirements.txt
|-- .env.example
|-- README.md
`-- src
    |-- __init__.py
    |-- document_utils.py
    |-- openai_client.py
    |-- reporting.py
    `-- schemas.py
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your API key:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

4. Start the app:

```bash
streamlit run app.py
```

## Example Demo Flow

Suggested demo file:

- `Fall_Protection_Construction.pdf`

Suggested demo question:

- `When must employers provide Fall Protection?`

Expected output:

- a summary of the document
- a direct grounded answer
- supporting excerpts tied to the source text
- follow-up questions for further review

## Demo File

Use [examples/fall-prevention-demo.md](examples/fall-prevention-demo.md) if you want a ready-to-run sample document for testing the workflow.

## Notes And Limitations

- This tool is designed to support document review, not replace formal compliance review, contract interpretation, or professional judgment.
- Output quality depends on the clarity and extractability of the uploaded document.
- Very large documents are clipped before being sent to the model in the current version.
- Answers are only as complete as the extracted text provided to the model.
- Demo Mode returns sample output and should not be treated as document-grounded analysis.

## Roadmap

### Near Term

- add chunked retrieval instead of simple text clipping
- improve section-level citation precision
- save question history for a document session
- support stronger document comparison workflows

### Future

- support multi-document querying across a project set
- add page-level or clause-level citation anchors
- add review workflows for submittals, specifications, and compliance checks

## Source Notes

The implementation uses the OpenAI Responses API with structured outputs and local document text extraction.
