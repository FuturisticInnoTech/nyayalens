# NyayaLens

NyayaLens is a document-grounded legal information MVP. It helps a reader find important clauses, track explicit obligations, compare agreement versions, and prepare questions for a legal professional. It is not legal advice and does not determine whether a term is valid or enforceable.

## What works in this MVP

- Responsive React/Vite interface with landing page, dashboard, upload entry, document workspace, comparison, settings, and not-found states.
- Offline demo mode with two clearly fictional Cedar Lane rental agreement versions.
- Clause explorer, overview fields, obligation tracker, attention flags, source page references, grounded question answering, and downloadable action brief.
- FastAPI REST API with Pydantic response contracts, SQLite/SQLAlchemy persistence, health endpoint, upload limits, deterministic demo provider, comparison endpoint, and safe demo deletion behavior.
- Backend tests for citation integrity, unsupported questions, comparisons, and demo deletion protection.

## Run locally

Prerequisites: Node.js 20+ and Python 3.12+.

```powershell
npm install
npm run dev
```

In another terminal:

```powershell
python -m pip install -r backend/requirements.txt
python -m alembic -c alembic.ini upgrade head
python -m uvicorn backend.app.main:app --reload --port 8000
```

Open `http://localhost:5173`. The frontend expects the API at `http://localhost:8000/api/v1`; set `VITE_API_URL` in `.env` to change it.

## Checks

```powershell
npm run build
npm run lint
python -m pytest backend/tests -q
```

## API surface

- `GET /api/v1/health`
- `POST /api/v1/auth/demo`
- `POST /api/v1/auth/logout`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{document_id}`
- `GET /api/v1/documents/{document_id}/clauses`
- `GET /api/v1/documents/{document_id}/obligations`
- `GET /api/v1/documents/{document_id}/flags`
- `POST /api/v1/documents/{document_id}/questions`
- `POST /api/v1/comparisons`
- `POST /api/v1/documents` (validates PDF/DOCX signatures and extracts selectable text in demo mode)
- `GET /api/v1/documents/{document_id}/export`

FastAPI exposes interactive OpenAPI documentation at `http://localhost:8000/docs`.

Database schema changes are managed with Alembic. Run `python -m alembic -c alembic.ini upgrade head` before starting a fresh deployment; migrations create documents, clauses, obligations, attention flags, users, sessions, and document access mappings with cascading document deletion. The demo client bootstraps an HttpOnly session through `/api/v1/auth/demo`; production deployments should replace this with a real login provider.

## Deployment

The recommended low-ops deployment for this plan is Netlify from GitHub for the Vite build and Cloud Run for the FastAPI API. Firebase provides identity through Firebase Auth; it does not need to host the FastAPI service.

### Hackathon demo path

For a public hackathon demo with no real users, Firebase Auth and PostgreSQL are optional. Use the deterministic demo session and ephemeral SQLite storage:

```powershell
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/nyayalens/api --file backend/Dockerfile backend
gcloud run deploy nyayalens-api --image REGION-docker.pkg.dev/PROJECT_ID/nyayalens/api --region REGION --allow-unauthenticated --port 8000 --set-env-vars "NYAYALENS_MODE=demo,CORS_ORIGINS=https://YOUR_NETLIFY_DOMAIN,COOKIE_SECURE=true,COOKIE_SAMESITE=none"
```

Connect the repository to Netlify, set only `VITE_API_URL=https://nyayalens-api-REGION.a.run.app/api/v1`, and let Netlify build from [netlify.toml](netlify.toml). Do not upload real or sensitive documents in this mode; Cloud Run's local SQLite data can disappear when the instance is replaced.

1. Create a Firebase project, enable Google (or another provider) under Authentication, and add the Netlify domain to Firebase Auth authorized domains.
2. Deploy the API to Cloud Run. The container honors the platform `PORT` variable:

```powershell
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/nyayalens/api --file backend/Dockerfile backend
gcloud run deploy nyayalens-api --image REGION-docker.pkg.dev/PROJECT_ID/nyayalens/api --region REGION --allow-unauthenticated --port 8000 --set-env-vars "NYAYALENS_MODE=production,CORS_ORIGINS=https://YOUR_NETLIFY_DOMAIN,COOKIE_SECURE=true,COOKIE_SAMESITE=none"
```

3. Connect the GitHub repository to Netlify. Netlify reads [netlify.toml](netlify.toml), runs `npm run build`, and publishes `dist`. Configure these Netlify environment variables from `.env.example`: `VITE_API_URL` plus all `VITE_FIREBASE_*` values from the Firebase Web app configuration.

```powershell
$env:VITE_API_URL="https://nyayalens-api-REGION.a.run.app/api/v1"
npm run build
```

For anything beyond a disposable demo, use Cloud SQL PostgreSQL or another durable database through `NYAYALENS_DATABASE_URL`. Cloud Run's local filesystem and SQLite are ephemeral. Run `python -m alembic -c alembic.ini upgrade head` against the production database before serving traffic. Store API keys and service credentials in Secret Manager, never in Firebase config or source control.

When the `VITE_FIREBASE_*` variables are present, the frontend shows a Google sign-in gate and sends Firebase ID tokens to the API. Set `NYAYALENS_MODE=production` on Cloud Run so the demo session endpoint is disabled. Do not expose `/api/v1/auth/demo` in a real user-data deployment.

## Architecture and limitations

The demo uses SQLite fixture and uploaded documents so it runs without API keys or PostgreSQL. PDF and DOCX uploads are signature-validated, extracted with PyMuPDF/python-docx, normalized, and segmented into page-aware clauses. SQLAlchemy/Alembic persists documents, clauses, obligations, attention flags, users, sessions, and access mappings. The backend separates typed document entities, citations, grounded answers, and comparison changes. Every demo answer either cites clauses from the requested document or returns an explicit unsupported response.

A production deployment still needs verified Firebase ID-token login in the frontend/API, private object storage, background processing, OCR for scanned pages, embeddings, CSRF review for the chosen auth flow, and a configured LLM adapter. No live provider is contacted by this repository, and no claim of legal compliance or encryption certification is made.

## Privacy and responsible use

Do not upload documents you are not authorized to share. A live deployment should disclose what excerpts are sent to a configured provider, retention duration, deletion behavior, and provider terms before processing sensitive material. Document text is untrusted input and must never authorize tools, network requests, or database operations. The interface labels demo content, source-backed facts, interpretation, and uncertainty separately.

The sample agreements are fictional demonstration materials, not legal templates. For high-stakes decisions, consult a qualified legal professional.
