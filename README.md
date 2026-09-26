
# NyayaLens
### Understand Legal Documents. Identify What Matters. Make Informed Decisions.

NyayaLens is a GenAI-powered legal document understanding and review platform that makes everyday legal information more accessible.

Legal agreements often contain complex terminology, lengthy clauses, hidden obligations, and ambiguous language that can be difficult for non-lawyers to understand. NyayaLens helps users understand what a document says, identify important clauses, compare agreement versions, track responsibilities, and prepare informed questions for a qualified legal professional.

Instead of presenting an unexplained AI-generated summary, NyayaLens is designed around **document-grounded answers, clause-level evidence, transparent uncertainty, and user control.**

The platform supports a complete document-review workflow:

1. Upload or select a legal document.
2. Understand its contents through a structured, plain-language overview.
3. Explore individual clauses with references to their original locations.
4. Identify obligations, deadlines, risks, and ambiguous provisions.
5. Ask questions about the document and verify answers against source text.
6. Compare agreements to understand additions, removals, and modifications.
7. Generate an actionable review brief for discussion with a legal professional.

> **Important:** NyayaLens provides legal information and document-understanding assistance, not legal advice. It does not independently determine whether a clause is valid, lawful, or enforceable. High-stakes decisions should be reviewed by a qualified legal professional.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Our Solution](#our-solution)
- [Core Features](#core-features)
- [AI and Document Intelligence](#ai-and-document-intelligence)
- [Document Comparison](#document-comparison)
- [Responsible AI and Privacy](#responsible-ai-and-privacy)
- [Accessibility and User Experience](#accessibility-and-user-experience)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Testing and Quality Assurance](#testing-and-quality-assurance)
- [Performance and Efficiency](#performance-and-efficiency)
- [Deployment](#deployment)
- [Current Implementation and Roadmap](#current-implementation-and-roadmap)
- [Limitations](#limitations)
- [Responsible Use](#responsible-use)

---

## Problem Statement

Legal documents are essential to everyday activities such as renting a home, accepting employment, purchasing services, and entering business agreements.

However, many people encounter barriers when trying to understand these documents:

- **Complex language:** Legal terminology and lengthy sentences make agreements difficult to interpret.
- **Information overload:** Important provisions may be buried in lengthy documents.
- **Unclear responsibilities:** Users may overlook payment terms, deadlines, penalties, renewal conditions, and termination requirements.
- **Difficult comparisons:** Identifying meaningful differences between agreement versions can require extensive manual review.
- **Limited access to assistance:** Professional legal consultation may not be immediately accessible for every preliminary question.
- **Lack of traceability:** Generic AI summaries can omit important qualifications or produce statements that cannot be verified against the original document.

NyayaLens addresses these challenges by helping users navigate legal documents through structured extraction, plain-language explanations, source references, and document-grounded assistance.

## Our Solution

NyayaLens provides a unified workspace for understanding and reviewing legal documents.

The platform separates three important layers:

| Layer | Purpose |
|---|---|
| Source document | Preserves the original text and document structure. |
| Extracted information | Organizes clauses, obligations, dates, and relevant provisions. |
| Explanations and insights | Helps users understand the extracted information while retaining references to the source. |

This separation helps users distinguish what a document explicitly states from an explanation of what that language may mean.

### Design principles

- **Grounded:** Document-specific claims should be supported by relevant source passages.
- **Transparent:** Users should be able to inspect the evidence behind an answer.
- **Accessible:** Legal information should be understandable without requiring legal expertise.
- **Privacy-conscious:** Sensitive documents should not be sent to external services without appropriate disclosure and authorization.
- **Human-centered:** The system supports informed decisions rather than making legal decisions for users.
- **Honest about uncertainty:** Missing evidence, ambiguous wording, and unsupported questions should be identified explicitly.

---

## Core Features

### 1. Legal Document Workspace

A structured interface for reviewing an agreement without losing access to the original document.

Features include:

- Document overview and metadata.
- Page-aware clause navigation.
- Search and filtering of extracted clauses.
- Source references and citation navigation.
- Obligation tracking.
- Attention flags for provisions requiring closer review.
- Document-specific questions.
- Exportable action brief.

The workspace is designed to make document review navigable, traceable, and efficient.

### 2. Plain-Language Legal Understanding

NyayaLens is designed to help users understand complex provisions in accessible language.

For each supported clause, the intended analysis distinguishes:

- **Original text:** The exact wording in the agreement.
- **Plain-language explanation:** A simplified description of the provision.
- **Practical implications:** What the provision explicitly requires or describes.
- **Important qualifications:** Conditions, exceptions, or limitations present in the source.
- **Uncertainty:** Interpretations that require additional context or professional review.
- **Source reference:** The location of the underlying text.

Simplification must preserve material conditions, exceptions, dates, amounts, and obligations. A shorter explanation should not silently change the meaning of the original provision.

### 3. Obligation and Deadline Tracker

Important responsibilities can be organized into a structured checklist.

Examples include:

- Payments and associated due dates.
- Notice periods.
- Renewal and termination requirements.
- Maintenance responsibilities.
- Required documentation.
- Explicit restrictions and conditions.

Each obligation should retain a reference to the clause from which it was extracted.

The tracker distinguishes explicitly stated requirements from inferred implications. Missing deadlines or unspecified responsibilities must not be invented.

### 4. Attention Flags

NyayaLens helps readers locate provisions that deserve closer inspection.

Potential review categories include:

- Financial commitments and penalties.
- Automatic renewal provisions.
- Termination and notice conditions.
- Unusually broad responsibilities.
- Restrictions and exceptions.
- Ambiguous or internally inconsistent wording.
- Missing information relevant to the user's stated concern.

An attention flag is a review prompt, not a determination that a clause is illegal, unfair, or unenforceable.

### 5. Document-Grounded Questions and Answers

Users can ask questions about a specific agreement in natural language.

Example questions:

- What payments does this agreement require?
- How much notice is required before termination?
- Can the agreement renew automatically?
- Which party is responsible for maintenance?
- What happens if a payment is delayed?
- Which clauses should I clarify before signing?

A reliable answer should:

1. Identify relevant passages from the requested document.
2. Answer only to the extent supported by those passages.
3. Include navigable source references.
4. Preserve relevant conditions and exceptions.
5. State when the document does not contain enough information.
6. Avoid inventing clauses, legal rules, or obligations.

If the evidence is insufficient, NyayaLens should explain what is missing instead of generating a confident but unsupported answer.

### 6. Agreement Comparison

Compare two versions of an agreement to identify:

- Added clauses.
- Removed clauses.
- Modified wording.
- Changed dates, amounts, or deadlines.
- Changes to responsibilities and conditions.
- Provisions requiring closer human review.

Each identified change should reference the relevant source text from both versions.

Textual differences must be distinguished from legal significance. A change in wording does not automatically establish that a party's legal position has improved or worsened.

### 7. Review Brief Export

Generate a concise review brief containing:

- Document overview.
- Important obligations and deadlines.
- Clauses requiring clarification.
- Relevant source references.
- Questions to discuss with a legal professional.
- A summary of changes when comparing versions.

The brief is intended to help users prepare for a discussion, not replace professional legal advice.

---

## AI and Document Intelligence

NyayaLens is designed around a source-grounded document intelligence pipeline.

### Intended processing pipeline

```text
PDF / DOCX
    |
    v
File validation
    |
    v
Text extraction
    |
    v
Page-aware segmentation
    |
    v
Clause identification
    |
    v
Relevant passage retrieval
    |
    v
Structured AI analysis
    |
    +--------------------------+
    |                          |
    v                          v
Plain-language           Obligations,
explanations              deadlines and
                          attention flags
    |                          |
    +-------------+------------+
                  |
                  v
        Source-reference checks
                  |
                  v
        Document review workspace
```

### Document processing

The current MVP supports PDF and DOCX uploads.

The backend:

- Validates supported file types and file signatures.
- Enforces upload-size limits.
- Extracts selectable text.
- Normalizes extracted content.
- Segments content into page-aware clauses.
- Persists document and clause records.
- Maintains source references for supported document operations.

Scanned documents require OCR and are not treated as successfully analyzed merely because a file was uploaded.

### Grounded generation

The production AI integration is intended to use retrieved document passages as the evidence for document-specific answers.

The model should not be treated as an authoritative source of legal facts.

A grounded answer should contain:

- A direct response to the user's question.
- Supporting passages from the relevant document.
- Source locations.
- Relevant conditions and exceptions.
- An uncertainty or insufficient-evidence indication when necessary.

The system should validate source references against the document's actual extracted passages. A citation must never be fabricated to make an answer appear reliable.

### Structured outputs

AI-generated information should follow typed schemas rather than being rendered directly from arbitrary model output.

Structured results should distinguish:

- Explanations.
- Explicit obligations.
- Dates and monetary values.
- Attention flags.
- Comparison changes.
- Evidence references.
- Uncertainty and unsupported claims.

Schema validation, source-reference validation, and safe fallback responses help prevent malformed or unsupported results from being presented as verified facts.

### Current AI integration status

The repository currently implements deterministic document processing and demo workflows. It does **not** contact a live generative AI provider.

The existing demo fixtures and extracted uploads must not be represented as having received live AI analysis.

A production AI adapter, retrieval pipeline, structured generation, and output validation are required to activate the full generative legal-assistance workflow.

---

## Document Comparison

The comparison workflow is designed to help users understand what changed between two agreement versions.

### Comparison process

1. Load the two authorized documents.
2. Normalize their extracted text while preserving source locations.
3. Identify matching and potentially changed clauses.
4. Classify additions, removals, and modifications.
5. Present the original and revised text side by side.
6. Highlight changes in relevant amounts, dates, responsibilities, and conditions.
7. Provide source references for both versions.

Comparison results should preserve the distinction between:

- Exact textual differences.
- Structured differences in extracted information.
- Potential practical implications.
- Questions requiring professional interpretation.

The comparison feature should not claim that a modification is legally valid or determine which agreement a user should accept.

---

## Responsible AI and Privacy

Legal documents may contain personal information, financial details, addresses, signatures, and confidential business information.

NyayaLens follows a privacy-conscious design approach.

### Data protection principles

- Validate document access on the server.
- Restrict document operations to authorized users.
- Avoid exposing document contents in public URLs.
- Keep credentials and API keys out of source control.
- Use secure transport and appropriately configured session cookies.
- Provide clear information about document retention and deletion.
- Disclose external AI processing before sending document excerpts to a provider.
- Minimize the amount of document content shared with external services.
- Avoid logging complete document contents or sensitive user questions unnecessarily.
- Treat uploaded documents and their contents as untrusted input.

### Prompt-injection resistance

Instructions contained inside an uploaded agreement must be treated as document content, not as instructions to the AI system.

Document text must never independently authorize:

- Tool execution.
- Network requests.
- Database operations.
- Access to other users' documents.
- Disclosure of system instructions or confidential information.

AI-generated output must also be treated as untrusted until validated against the expected schema and application rules.

### Authentication and authorization

The backend includes demo authentication and document-access checks.

Production deployment requires verified Firebase ID-token validation on the server, appropriately scoped authorization, secure session handling, and durable storage configuration.

Firebase client configuration is not a substitute for backend authorization.

### Responsible use

NyayaLens is an informational tool. It does not establish an attorney-client relationship, guarantee legal correctness, or replace a qualified professional.

---

## Accessibility and User Experience

The interface is designed to make document review usable across different screen sizes and interaction preferences.

Current interface features include:

- Responsive layouts.
- Semantic navigation and accessible workspace tabs.
- Named controls and meaningful accessible labels.
- Visible keyboard focus.
- Reduced-motion support.
- Semantic alerts and status regions.
- Keyboard-accessible citation navigation.
- Useful empty, loading, error, and not-found states.
- Retryable failures.
- Clear distinctions between demo content and document-derived information.

### Accessibility goals

- Maintain sufficient text and interface contrast.
- Support keyboard-only navigation.
- Ensure interactive elements have accessible names.
- Avoid relying exclusively on color to communicate risk or status.
- Preserve readable layouts at increased zoom.
- Associate validation errors with the relevant controls.
- Keep focus behavior predictable when changing tabs or opening dialogs.

Accessibility should be verified through automated checks and manual keyboard and screen-reader testing.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, JavaScript/TypeScript as configured |
| UI | Responsive component-based interface |
| Frontend performance | Concurrent rendering and deferred filtering |
| Backend | Python, FastAPI |
| API contracts | Pydantic |
| ORM | SQLAlchemy |
| Database | SQLite for the demo; PostgreSQL recommended for production |
| Migrations | Alembic |
| PDF extraction | PyMuPDF |
| DOCX extraction | python-docx |
| Authentication | Demo sessions; Firebase Authentication integration for production |
| Testing | pytest and frontend build/lint checks |
| Frontend deployment | Netlify |
| Backend deployment | Google Cloud Run |
| Production secrets | Google Cloud Secret Manager |

The stack separates presentation, API contracts, document processing, persistence, and authentication to support independent testing and future extension.

---

## System Architecture

```text
                  React + Vite
                       |
                       | HTTPS / REST
                       v
                 FastAPI Backend
                       |
          +------------+------------+
          |            |            |
          v            v            v
     Authentication  Document    Comparison
                      Service      Service
          |            |            |
          +------------+------------+
                       |
                       v
              SQLAlchemy ORM
                       |
              +--------+--------+
              |                 |
              v                 v
            SQLite          PostgreSQL
          (demo/local)     (production)

     Future production AI integration
                       |
                       v
              Retrieval + LLM
                       |
                       v
          Validated, grounded output
```

### Architectural considerations

- Typed request and response contracts.
- Server-side document-access checks.
- Centralized document-processing logic.
- Database migrations for schema evolution.
- Page-aware source references.
- Explicit handling of unsupported questions.
- Separate demo and production configuration.
- A replaceable AI integration layer.

---

## Getting Started

### Prerequisites

- Node.js 20 or later.
- Python 3.12 or later.
- Git.

### 1. Install frontend dependencies

```powershell
npm install
```

### 2. Install backend dependencies

```powershell
python -m pip install -r backend/requirements.txt
```

### 3. Initialize the database

```powershell
python -m alembic -c alembic.ini upgrade head
```

### 4. Start the backend

In one terminal:

```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

### 5. Start the frontend

In another terminal:

```powershell
npm run dev
```

Open:

http://localhost:5173

The Vite development server proxies `/api/v1` requests to the FastAPI service at `http://localhost:8000/api/v1`.

Interactive API documentation is available at:

http://localhost:8000/docs

### Demo mode

The offline demo includes two fictional Cedar Lane rental agreement versions.

These fixtures allow users to explore the document workspace, clause navigation, obligations, attention flags, comparison workflow, and review brief without requiring an external AI provider.

Uploaded files in demo mode undergo text extraction; they are not automatically given AI-generated legal analysis.

---

## Configuration

Configure the frontend API endpoint in `.env`:

```dotenv
VITE_API_URL=http://localhost:8000/api/v1
```

Use `.env.example` as the reference for the available configuration variables.

For production, configure the Firebase web application values through the deployment environment:

```dotenv
VITE_FIREBASE_API_KEY=
VITE_FIREBASE_AUTH_DOMAIN=
VITE_FIREBASE_PROJECT_ID=
VITE_FIREBASE_APP_ID=
```

These values configure the frontend Firebase client. They must not be used as a substitute for server-side token verification.

Backend configuration should include:

```dotenv
NYAYALENS_MODE=production
NYAYALENS_DATABASE_URL=
CORS_ORIGINS=
COOKIE_SECURE=true
COOKIE_SAMESITE=none
```

Configure provider credentials through a secret manager when a live AI adapter is introduced. Never commit production credentials to Git.

---

## API Reference

Base path: `/api/v1`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health |
| POST | `/auth/demo` | Create a demo session |
| POST | `/auth/logout` | End the current session |
| GET | `/documents` | List accessible documents |
| GET | `/documents/{document_id}` | Retrieve a document |
| GET | `/documents/{document_id}/clauses` | Retrieve document clauses |
| GET | `/documents/{document_id}/obligations` | Retrieve obligations |
| GET | `/documents/{document_id}/flags` | Retrieve attention flags |
| POST | `/documents/{document_id}/questions` | Submit a document question |
| POST | `/comparisons` | Compare two documents |
| POST | `/documents` | Upload and extract a supported document |
| GET | `/documents/{document_id}/export` | Export the review brief |

The upload endpoint validates PDF/DOCX signatures and extracts selectable text in demo mode.

The question endpoint supports the current deterministic demo behavior; it should not be described as a live LLM-powered endpoint until the production AI adapter is configured.

### Database migrations

Apply migrations before starting a fresh deployment:

```powershell
python -m alembic -c alembic.ini upgrade head
```

The schema includes documents, clauses, obligations, attention flags, users, sessions, and document-access mappings.

Document deletion uses cascading database relationships where configured. Demo deletion protections prevent the sample fixtures from being accidentally removed.

---

## Testing and Quality Assurance

The project includes backend tests covering:

- Health and demo fixtures.
- Citation integrity.
- Unsupported questions.
- Document comparison.
- Authentication.
- Upload validation.
- File-signature validation.
- Demo deletion protection.

Run the checks from the repository root:

```powershell
npm run build
npm run lint
python -m pytest backend/tests -q
```

### Additional recommended tests

For a production legal-document assistant, the test suite should also cover:

- PDF and DOCX extraction across different document structures.
- Empty, malformed, encrypted, and oversized files.
- Scanned PDFs and OCR failure states.
- Citation accuracy against the original document.
- Preservation of dates, monetary values, exceptions, and negations.
- Unsupported questions and insufficient evidence.
- Prompt-injection attempts inside uploaded documents.
- Cross-user document-access attempts.
- Comparison accuracy for additions, removals, and modifications.
- Concurrent requests and database transaction failures.
- Keyboard navigation and screen-reader behavior.
- API latency and memory use with large documents.

AI evaluation should measure factual grounding, citation correctness, completeness, unsupported-claim frequency, and preservation of material contractual conditions.

---

## Performance and Efficiency

NyayaLens uses a modular backend and a responsive frontend to keep document review manageable.

### Current optimizations

- Deferred clause filtering to avoid unnecessary synchronous rendering work.
- Concurrent React rendering for non-blocking interface updates.
- Vite development proxying to simplify local API integration.
- Database-backed document entities rather than repeatedly embedding complete document records in every API response.
- Page-aware segmentation for targeted clause access.
- Typed API contracts to reduce inconsistent data handling.

### Further optimization opportunities

- Paginate clause and document listings.
- Avoid reprocessing unchanged documents.
- Cache safe, document-scoped extraction results.
- Process large uploads through background jobs.
- Limit the amount of text included in each AI request.
- Retrieve only relevant passages for document questions.
- Use bounded concurrency for document processing.
- Apply request timeouts, upload limits, and rate limits.
- Measure API latency, memory consumption, and document-processing time.

Performance claims should be supported by measurements on representative document sizes rather than assumed from the architecture alone.

---

## Deployment

Recommended deployment:

- **Frontend:** Netlify.
- **Backend:** Google Cloud Run.
- **Authentication:** Firebase Authentication.
- **Production database:** Cloud SQL for PostgreSQL or another durable PostgreSQL service.
- **Secrets:** Google Cloud Secret Manager.
- **Document storage:** Private object storage when persistent file storage is required.

### Hackathon demo deployment

The deterministic demo can use SQLite and fictional sample documents.

Build and deploy the backend image:

```powershell
gcloud builds submit `
  --tag REGION-docker.pkg.dev/PROJECT_ID/nyayalens/api `
  --file backend/Dockerfile `
  backend
```

Deploy to Cloud Run:

```powershell
gcloud run deploy nyayalens-api `
  --image REGION-docker.pkg.dev/PROJECT_ID/nyayalens/api `
  --region REGION `
  --allow-unauthenticated `
  --port 8000 `
  --set-env-vars "NYAYALENS_MODE=demo,CORS_ORIGINS=https://YOUR_NETLIFY_DOMAIN,COOKIE_SECURE=true,COOKIE_SAMESITE=none"
```

Configure the Netlify environment variable:

```dotenv
VITE_API_URL=https://nyayalens-api-REGION.a.run.app/api/v1
```

Connect the GitHub repository to Netlify and use the existing `netlify.toml` build configuration.

**Demo deployment warning:** Cloud Run's local filesystem is ephemeral. SQLite data may disappear when an instance is replaced. Do not upload real or sensitive legal documents to a publicly accessible demo deployment.

### Production deployment

Before handling real user documents:

1. Enable a supported Firebase Authentication provider.
2. Verify Firebase ID tokens on the backend.
3. Disable demo authentication.
4. Configure durable PostgreSQL storage.
5. Configure private document storage and retention policies.
6. Enforce server-side document authorization.
7. Configure secrets through Secret Manager.
8. Restrict CORS to trusted frontend origins.
9. Review cookie, CSRF, and session security.
10. Configure request limits, rate limits, and monitoring.
11. Add a production AI adapter with explicit data-processing disclosures.
12. Run database migrations and the complete test suite.

Cloud Run should honor the platform-provided `PORT` environment variable.

---

## Current Implementation and Roadmap

NyayaLens distinguishes implemented functionality from planned production capabilities.

| Capability | Status |
|---|---|
| Responsive React/Vite interface | Implemented |
| Document workspace and navigation | Implemented |
| Fictional agreement demo | Implemented |
| PDF/DOCX signature validation | Implemented |
| Selectable-text extraction | Implemented |
| Page-aware clause segmentation | Implemented |
| Demo obligation and attention-flag workflow | Implemented |
| Deterministic document Q&A | Implemented |
| Document comparison workflow | Implemented |
| Source-reference validation | Implemented for supported demo operations |
| Review brief export | Implemented |
| Backend persistence and migrations | Implemented |
| Live generative AI analysis | Not yet integrated |
| AI-generated clause explanations for arbitrary uploads | Not yet integrated |
| Production retrieval-augmented generation | Planned |
| OCR for scanned documents | Planned |
| Verified production authentication | Required before production use |
| Durable private document storage | Required before production use |
| AI-specific quality evaluation | Requires implementation and measurement |

### Roadmap

**Phase 1 — Reliable document processing**
- Improve extraction quality.
- Preserve document structure and source locations.
- Expand malformed-file and edge-case handling.
- Improve comparison accuracy.

**Phase 2 — Grounded legal-document AI**
- Integrate a configurable LLM provider.
- Implement document-scoped retrieval.
- Generate structured clause explanations.
- Extract explicit obligations, deadlines, and attention flags.
- Validate citations against source passages.
- Return explicit unsupported responses.

**Phase 3 — Safety and evaluation**
- Evaluate groundedness and citation precision.
- Test prompt-injection resistance.
- Measure hallucination and unsupported-claim rates.
- Test preservation of exceptions and material conditions.
- Add privacy, authorization, and cross-user isolation tests.

**Phase 4 — Production readiness**
- Add OCR and background processing.
- Deploy durable database and private file storage.
- Complete production authentication and authorization.
- Add monitoring, rate limiting, and retention controls.
- Conduct accessibility and performance testing.

---

## Limitations

The current repository is a functional MVP and demonstration of the legal-document review workflow.

It does not currently provide:

- Live LLM-generated legal analysis.
- Guaranteed legal interpretation.
- A determination of whether a clause is enforceable.
- OCR-based processing of scanned documents.
- Guaranteed extraction accuracy for every PDF or DOCX.
- Verified production authentication and authorization for a public deployment.
- Durable document storage in the demo configuration.
- Certification of legal compliance, security, or encryption.

A successful upload confirms that a supported file was accepted and processed by the configured extraction workflow. It does not establish that the document has been fully analyzed by AI.

---

## Responsible Use

NyayaLens is designed to improve access to legal information by helping users understand documents, identify relevant provisions, and prepare better questions.

It is not a substitute for a lawyer, legal aid service, or qualified professional.

Users should:

- Upload only documents they are authorized to share.
- Verify important information against the original agreement.
- Review the full clause, including its exceptions and surrounding context.
- Avoid treating attention flags as legal conclusions.
- Seek qualified legal assistance for high-stakes decisions.

The sample Cedar Lane agreements are fictional demonstration materials and are not legal templates.

---

## Contributing

Contributions are welcome.

When proposing changes:

1. Keep document-derived claims traceable to their source.
2. Avoid presenting unsupported AI output as fact.
3. Preserve privacy and document-access controls.
4. Add tests for new API behavior.
5. Include accessibility considerations in UI changes.
6. Document new configuration and deployment requirements.
7. Distinguish implemented capabilities from planned features.

---

## License

Add the repository's chosen license and attribution requirements before distributing the project.

---

**NyayaLens — Making legal information easier to understand, one document at a time.**