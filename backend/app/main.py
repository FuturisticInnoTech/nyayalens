from datetime import datetime, timedelta, timezone
from io import BytesIO
import hashlib
import os
from pathlib import PurePath
from re import match
import secrets
import time
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response
import fitz
from docx import Document as DocxDocument
from pydantic import BaseModel, Field

from .database import create_session, delete_document as delete_persisted_document
from .database import ensure_demo_user, ensure_firebase_user, get_session_user, grant_demo_access
from .database import get_document as get_persisted_document
from .database import initialize_database, list_documents as list_persisted_documents
from .database import save_document
from .firebase_auth import verify_id_token

app = FastAPI(title="NyayaLens API", version="1.0.0", description="Document-grounded legal information MVP")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","), allow_methods=["*"], allow_headers=["*"], allow_credentials=True)

RATE_BUCKETS: dict[str, list[float]] = {}

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    now = time.monotonic()
    address = request.client.host if request.client else "unknown"
    recent = [stamp for stamp in RATE_BUCKETS.get(address, []) if now - stamp < 60]
    if len(recent) >= 120:
        return Response(content="Too many requests", status_code=429, headers={"Retry-After": "60"})
    recent.append(now)
    RATE_BUCKETS[address] = recent
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    return response

DEMO_ID = "demo-rental-v1"
DEMO_COMPARE_ID = "demo-rental-v2"

class Citation(BaseModel):
    document_id: str
    clause_id: str
    page: int
    excerpt: str

class Clause(BaseModel):
    id: str
    document_id: str
    category: str
    heading: str
    page: int
    text: str
    order: int

class Obligation(BaseModel):
    id: str
    party: str
    action: str
    trigger: str
    amount: str | None = None
    clause_id: str
    certainty: str = "Explicit in document"

class AttentionFlag(BaseModel):
    id: str
    title: str
    kind: str
    explanation: str
    why: str
    question: str
    clause_ids: list[str]

class Overview(BaseModel):
    document_type: str
    parties: list[str]
    effective_date: str
    duration: str
    jurisdiction: str
    summary: str
    limitations: list[str]

class Document(BaseModel):
    id: str
    name: str
    type: str
    status: str
    updated_at: str
    pages: int
    is_demo: bool = False
    overview: Overview
    clauses: list[Clause]
    obligations: list[Obligation]
    flags: list[AttentionFlag]

class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=800)

class GroundedAnswer(BaseModel):
    answer: str
    direct_facts: str
    interpretation: str
    citations: list[Citation]
    supported: bool

class ComparisonChange(BaseModel):
    heading: str
    change_type: str
    summary: str
    before: str
    after: str
    citations: list[Citation]

class Comparison(BaseModel):
    id: str
    left_document_id: str
    right_document_id: str
    title: str
    changes: list[ComparisonChange]
    limitation: str


def demo_document(version: int = 1) -> Document:
    document_id = DEMO_ID if version == 1 else DEMO_COMPARE_ID
    annual_increase = "$1,350" if version == 1 else "$1,425"
    notice = "30 days" if version == 1 else "60 days"
    clauses = [
        Clause(id=f"{document_id}-c1", document_id=document_id, category="Parties & definitions", heading="1. Parties and premises", page=1, order=1, text="This Residential Rental Agreement is between Maya Rao (Landlord) and Jordan Lee (Tenant) for the apartment at 14 Cedar Lane, Pune.",),
        Clause(id=f"{document_id}-c2", document_id=document_id, category="Payments", heading="2. Rent and deposit", page=1, order=2, text=f"Monthly rent is {annual_increase}, due on the first day of each month. The Tenant will pay a refundable security deposit of $2,700 before move-in.",),
        Clause(id=f"{document_id}-c3", document_id=document_id, category="Duties & responsibilities", heading="3. Utilities and care", page=2, order=3, text="The Tenant pays electricity and internet. The Landlord pays water and building maintenance. The Tenant must keep the premises reasonably clean and promptly report material damage.",),
        Clause(id=f"{document_id}-c4", document_id=document_id, category="Renewal & termination", heading="4. Term and renewal", page=2, order=4, text=f"The term begins 1 April 2026 and ends 31 March 2027. It renews for successive one-year periods unless either party gives {notice} written notice before the end of the current term.",),
        Clause(id=f"{document_id}-c5", document_id=document_id, category="Penalties & liability", heading="5. Early departure", page=3, order=5, text="If the Tenant leaves before the end of the term without an agreed replacement tenant, the Tenant remains responsible for rent until the premises are re-let, subject to applicable law.",),
        Clause(id=f"{document_id}-c6", document_id=document_id, category="Dispute resolution", heading="6. Governing law", page=3, order=6, text="The parties will first try in good faith to resolve disputes by discussion. This agreement states that the laws of Maharashtra apply.",),
    ]
    obligations = [
        Obligation(id=f"{document_id}-o1", party="Tenant", action="Pay monthly rent", trigger="First day of each month", amount=annual_increase, clause_id=clauses[1].id),
        Obligation(id=f"{document_id}-o2", party="Tenant", action="Pay refundable security deposit", trigger="Before move-in", amount="$2,700", clause_id=clauses[1].id),
        Obligation(id=f"{document_id}-o3", party="Tenant", action="Give written notice before non-renewal", trigger=f"{notice} before term end", clause_id=clauses[3].id),
        Obligation(id=f"{document_id}-o4", party="Both parties", action="Try to resolve disputes by discussion", trigger="Before escalating a dispute", clause_id=clauses[5].id),
    ]
    flags = [
        AttentionFlag(id=f"{document_id}-f1", title="Renewal timing deserves attention", kind="Potential concern", explanation=f"The agreement renews automatically unless written notice is given {notice} before the term ends.", why="Missing the notice window could extend the agreement. The document does not say how notice must be delivered.", question="How should written non-renewal notice be delivered and acknowledged?", clause_ids=[clauses[3].id]),
        AttentionFlag(id=f"{document_id}-f2", title="Early departure cost is open-ended", kind="Needs clarification", explanation="The clause links responsibility to the time needed to re-let the premises but does not state a fixed amount or maximum.", why="A reader may want to understand how replacement tenants and mitigation would work in practice.", question="What steps will be taken to re-let the premises, and when would the Tenant's responsibility end?", clause_ids=[clauses[4].id]),
        AttentionFlag(id=f"{document_id}-f3", title="Notice delivery method is missing", kind="Information missing", explanation="The agreement requires written notice but does not identify an address, email, or accepted delivery method.", why="The document does not explain how either party can reliably prove notice was received.", question="Which contact details and delivery methods should be used for formal notices?", clause_ids=[clauses[3].id]),
    ]
    return Document(id=document_id, name="Cedar Lane Rental Agreement" + (" - revised" if version == 2 else ""), type="Residential rental agreement", status="Analyzed", updated_at="26 Sep 2026", pages=3, is_demo=True, overview=Overview(document_type="Residential rental agreement", parties=["Maya Rao (Landlord)", "Jordan Lee (Tenant)"], effective_date="1 April 2026", duration="12 months", jurisdiction="Maharashtra (stated in document)", summary="A fictional one-year rental agreement covering rent, utilities, renewal, early departure, and an informal dispute discussion step.", limitations=["This is a fictional demonstration document, not a legal template.", "The analysis describes document text and does not determine enforceability.", "No external legal sources were used for this analysis."]), clauses=clauses, obligations=obligations, flags=flags)

DOCUMENTS: dict[str, Document] = {DEMO_ID: demo_document(), DEMO_COMPARE_ID: demo_document(2)}
initialize_database()
DEMO_USER_ID = ensure_demo_user()
if not list_persisted_documents():
    for fixture in DOCUMENTS.values():
        save_document(fixture.model_dump(), DEMO_USER_ID)
grant_demo_access([DEMO_ID, DEMO_COMPARE_ID], DEMO_USER_ID)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024

def current_user(request: Request) -> str:
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        try:
            claims = verify_id_token(authorization[7:].strip())
            user_id = str(claims["uid"])
            ensure_firebase_user(user_id, claims.get("email") if isinstance(claims.get("email"), str) else None, claims.get("name") if isinstance(claims.get("name"), str) else None)
            grant_demo_access([DEMO_ID, DEMO_COMPARE_ID], user_id)
            return user_id
        except Exception as error:
            raise HTTPException(status_code=401, detail="Invalid Firebase authentication token") from error
    token = request.cookies.get("nyaya_session")
    user_id = get_session_user(hashlib.sha256(token.encode()).hexdigest(), datetime.now(timezone.utc)) if token else None
    if not user_id or os.getenv("NYAYALENS_MODE", "demo") == "production":
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id

def issue_demo_session(response: Response) -> None:
    token = secrets.token_urlsafe(32)
    create_session(hashlib.sha256(token.encode()).hexdigest(), DEMO_USER_ID, datetime.now(timezone.utc) + timedelta(hours=12))
    response.set_cookie("nyaya_session", token, httponly=True, samesite=os.getenv("COOKIE_SAMESITE", "lax"), secure=os.getenv("COOKIE_SECURE", "false").lower() == "true", max_age=43200)

def normalize_text(value: str) -> str:
    return " ".join(value.replace("\x00", " ").split())

def validate_upload(data: bytes) -> str:
    if data.startswith(b"%PDF-"):
        return "pdf"
    if data.startswith(b"PK\x03\x04"):
        return "docx"
    raise HTTPException(status_code=415, detail="Only valid PDF or DOCX files are supported")

def extracted_clauses(document_id: str, pages: list[str]) -> list[Clause]:
    clauses: list[Clause] = []
    order = 1
    for page_number, page_text in enumerate(pages, start=1):
        for paragraph in page_text.split("\n"):
            text = normalize_text(paragraph)
            if not text:
                continue
            heading_match = match(r"^(\d+(?:\.\d+)*[.)]?\s+)?(.{3,80})$", text)
            heading = heading_match.group(2).strip() if heading_match else f"Extracted text {order}"
            clauses.append(Clause(id=f"{document_id}-c{order}", document_id=document_id, category="Other / unclassified", heading=heading, page=page_number, text=text, order=order))
            order += 1
    return clauses

def extract_upload(document_id: str, filename: str, data: bytes) -> Document:
    file_type = validate_upload(data)
    if file_type == "pdf":
        try:
            pdf = fitz.open(stream=data, filetype="pdf")
            if pdf.needs_pass:
                raise HTTPException(status_code=422, detail="Encrypted PDFs are not supported")
            pages = [page.get_text("text") for page in pdf]
            page_count = len(pages)
            pdf.close()
        except HTTPException:
            raise
        except Exception as error:
            raise HTTPException(status_code=422, detail="The PDF could not be read") from error
    else:
        try:
            word_document = DocxDocument(BytesIO(data))
            pages = ["\n".join(paragraph.text for paragraph in word_document.paragraphs)]
            page_count = 1
        except Exception as error:
            raise HTTPException(status_code=422, detail="The DOCX could not be read") from error
    clauses = extracted_clauses(document_id, pages)
    if not clauses:
        raise HTTPException(status_code=422, detail="No selectable text was found; OCR is not configured")
    clean_name = PurePath(filename or f"uploaded-{document_id}").name
    overview = Overview(document_type="Uploaded document", parties=[], effective_date="Not found", duration="Not found", jurisdiction="Not found", summary="Text was extracted from the uploaded document. Structured analysis is pending review.", limitations=["This upload has extracted text but no AI analysis has been run.", "Parties, dates, and jurisdiction are not inferred when they are not explicit."])
    return Document(id=document_id, name=clean_name, type="PDF" if file_type == "pdf" else "DOCX", status="Extracted", updated_at=datetime.now(timezone.utc).strftime("%d %b %Y"), pages=page_count, overview=overview, clauses=clauses, obligations=[], flags=[])

@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "demo", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/api/v1/auth/demo")
def demo_login(response: Response) -> dict[str, str]:
    if os.getenv("NYAYALENS_MODE", "demo") == "production":
        raise HTTPException(status_code=404, detail="Demo authentication is disabled")
    issue_demo_session(response)
    return {"user_id": DEMO_USER_ID, "display_name": "Jordan Lee", "mode": "demo"}

@app.post("/api/v1/auth/logout", status_code=204)
def logout(response: Response) -> None:
    response.delete_cookie("nyaya_session")

@app.get("/api/v1/documents", response_model=list[Document])
def list_documents(user_id: str = Depends(current_user)) -> list[Document]:
    return [Document.model_validate(document) for document in list_persisted_documents(user_id)]

@app.get("/api/v1/documents/{document_id}", response_model=Document)
def get_document(document_id: str, user_id: str = Depends(current_user)) -> Document:
    document = get_persisted_document(document_id, user_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return Document.model_validate(document)

@app.delete("/api/v1/documents/{document_id}", status_code=204)
def delete_document(document_id: str, user_id: str = Depends(current_user)) -> None:
    document = get_persisted_document(document_id, user_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    document = Document.model_validate(document)
    if document.is_demo:
        raise HTTPException(status_code=409, detail="Demo documents cannot be deleted")
    delete_persisted_document(document_id, user_id)

@app.get("/api/v1/documents/{document_id}/clauses", response_model=list[Clause])
def get_clauses(document_id: str, user_id: str = Depends(current_user)) -> list[Clause]:
    return get_document(document_id, user_id).clauses

@app.get("/api/v1/documents/{document_id}/obligations", response_model=list[Obligation])
def get_obligations(document_id: str, user_id: str = Depends(current_user)) -> list[Obligation]:
    return get_document(document_id, user_id).obligations

@app.get("/api/v1/documents/{document_id}/flags", response_model=list[AttentionFlag])
def get_flags(document_id: str, user_id: str = Depends(current_user)) -> list[AttentionFlag]:
    return get_document(document_id, user_id).flags

@app.post("/api/v1/documents/{document_id}/questions", response_model=GroundedAnswer)
def ask_question(document_id: str, request: QuestionRequest, user_id: str = Depends(current_user)) -> GroundedAnswer:
    document = get_document(document_id, user_id)
    question = request.question.lower()
    matches: list[Clause] = []
    if any(word in question for word in ["rent", "pay", "deposit", "amount"]):
        matches = [document.clauses[1]]
        answer = "The document says the Tenant pays the monthly rent on the first day of each month and pays a refundable security deposit before move-in."
        facts = "Direct fact: the payment amounts and timing appear in clause 2."
        interpretation = "This is a summary of the stated payment terms; it does not assess whether they are legally enforceable."
    elif any(word in question for word in ["terminate", "leave", "early", "renew", "notice"]):
        matches = [document.clauses[3], document.clauses[4]]
        answer = "The term ends on 31 March 2027 and renews unless either party gives the stated written notice before the term ends. Leaving early may leave the Tenant responsible until the premises are re-let, subject to applicable law."
        facts = "Direct fact: renewal timing is in clause 4 and early departure language is in clause 5."
        interpretation = "The early departure clause leaves practical details open, so it is worth clarifying how re-letting and notice would work."
    elif any(word in question for word in ["dispute", "law", "jurisdiction"]):
        matches = [document.clauses[5]]
        answer = "The parties agree to try to resolve disputes by discussion first, and the document states that Maharashtra law applies."
        facts = "Direct fact: both points are stated in clause 6."
        interpretation = "The document statement is evidence of what the parties wrote; it is not a determination of which law controls every issue."
    else:
        return GroundedAnswer(answer="I could not find enough support in this document to answer that question.", direct_facts="No matching clause was identified.", interpretation="Try asking about rent, deposit, renewal, early departure, notice, disputes, or governing law.", citations=[], supported=False)
    citations = [Citation(document_id=document.id, clause_id=clause.id, page=clause.page, excerpt=clause.text) for clause in matches]
    return GroundedAnswer(answer=answer, direct_facts=facts, interpretation=interpretation, citations=citations, supported=True)

@app.post("/api/v1/comparisons", response_model=Comparison)
def compare_documents(payload: dict[str, str], user_id: str = Depends(current_user)) -> Comparison:
    left = get_document(payload.get("left_document_id", DEMO_ID), user_id)
    right = get_document(payload.get("right_document_id", DEMO_COMPARE_ID), user_id)
    changes: list[ComparisonChange] = []
    for left_clause, right_clause in zip(left.clauses, right.clauses):
        if left_clause.text != right_clause.text:
            changes.append(ComparisonChange(heading=left_clause.heading, change_type="Modified", summary="The wording or value changed between versions.", before=left_clause.text, after=right_clause.text, citations=[Citation(document_id=left.id, clause_id=left_clause.id, page=left_clause.page, excerpt=left_clause.text), Citation(document_id=right.id, clause_id=right_clause.id, page=right_clause.page, excerpt=right_clause.text)]))
    return Comparison(id=str(uuid4()), left_document_id=left.id, right_document_id=right.id, title="Cedar Lane agreement comparison", changes=changes, limitation="This comparison identifies textual changes. It does not decide whether a change alters legal effect.")

@app.post("/api/v1/documents", response_model=Document, status_code=201)
async def upload_document(file: UploadFile = File(...), user_id: str = Depends(current_user)) -> Document:
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Files must be smaller than 10 MB")
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    document_id = str(uuid4())
    document = extract_upload(document_id, file.filename or "uploaded-document", data)
    save_document(document.model_dump(), user_id)
    return document

@app.get("/api/v1/documents/{document_id}/export", response_class=PlainTextResponse)
def export_action_brief(document_id: str, user_id: str = Depends(current_user)) -> str:
    document = get_document(document_id, user_id)
    lines = ["NYAYALENS ACTION BRIEF", "Demonstration material - not legal advice", "", document.name, "", "SUMMARY", document.overview.summary, "", "KEY OBLIGATIONS"]
    lines.extend(f"- {item.party}: {item.action} ({item.trigger})" for item in document.obligations)
    lines.extend(["", "QUESTIONS TO CLARIFY"])
    lines.extend(f"- {item.question} [source: {', '.join(item.clause_ids)}]" for item in document.flags)
    return "\n".join(lines)
