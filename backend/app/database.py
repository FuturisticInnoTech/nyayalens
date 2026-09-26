from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, create_engine, delete, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

DATABASE_URL = os.getenv("NYAYALENS_DATABASE_URL", "sqlite:///./backend/nyayalens.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

class Base(DeclarativeBase):
    pass

class UserRecord(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

class SessionRecord(Base):
    __tablename__ = "sessions"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

class DocumentAccess(Base):
    __tablename__ = "document_access"

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    pages: Mapped[int] = mapped_column(Integer, nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    overview: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    legacy_obligations: Mapped[list[dict[str, Any]]] = mapped_column("obligations", JSON, nullable=False, default=list)
    legacy_flags: Mapped[list[dict[str, Any]]] = mapped_column("flags", JSON, nullable=False, default=list)
    clauses: Mapped[list[ClauseRecord]] = relationship(back_populates="document", cascade="all, delete-orphan")
    obligation_records: Mapped[list[ObligationRecord]] = relationship(back_populates="document", cascade="all, delete-orphan")
    flag_records: Mapped[list[FlagRecord]] = relationship(back_populates="document", cascade="all, delete-orphan")

class ClauseRecord(Base):
    __tablename__ = "clauses"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    heading: Mapped[str] = mapped_column(String(255), nullable=False)
    page: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    clause_order: Mapped[int] = mapped_column(Integer, nullable=False)
    document: Mapped[DocumentRecord] = relationship(back_populates="clauses")

class ObligationRecord(Base):
    __tablename__ = "obligations"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    party: Mapped[str] = mapped_column(String(120), nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    trigger: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[str | None] = mapped_column(String(120), nullable=True)
    clause_id: Mapped[str] = mapped_column(String(100), nullable=False)
    certainty: Mapped[str] = mapped_column(String(120), nullable=False)
    document: Mapped[DocumentRecord] = relationship(back_populates="obligation_records")

class FlagRecord(Base):
    __tablename__ = "attention_flags"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[str] = mapped_column(String(80), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    why: Mapped[str] = mapped_column(Text, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    clause_ids: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    document: Mapped[DocumentRecord] = relationship(back_populates="flag_records")

def initialize_database() -> None:
    Base.metadata.create_all(engine)

def ensure_demo_user() -> str:
    with Session(engine) as session:
        user = session.scalar(select(UserRecord).where(UserRecord.email == "demo@nyayalens.local"))
        if user is None:
            user = UserRecord(id="demo-user", email="demo@nyayalens.local", display_name="Jordan Lee", created_at=datetime.now())
            session.add(user)
            session.commit()
        return user.id

def ensure_firebase_user(user_id: str, email: str | None, display_name: str | None) -> str:
    with Session(engine) as session:
        user = session.get(UserRecord, user_id)
        if user is None:
            user = UserRecord(id=user_id, email=email or f"{user_id}@firebase.local", display_name=display_name or "NyayaLens user", created_at=datetime.now())
            session.add(user)
            session.commit()
        return user.id

def create_session(token_hash: str, user_id: str, expires_at: datetime) -> None:
    with Session(engine) as session:
        session.add(SessionRecord(token_hash=token_hash, user_id=user_id, expires_at=expires_at))
        session.commit()

def get_session_user(token_hash: str, now: datetime) -> str | None:
    with Session(engine) as session:
        record = session.scalar(select(SessionRecord).where(SessionRecord.token_hash == token_hash, SessionRecord.expires_at > now))
        return record.user_id if record else None

def save_document(payload: dict[str, Any], owner_id: str | None = None) -> None:
    owner_id = owner_id or ensure_demo_user()
    with Session(engine) as session:
        record = DocumentRecord(
            id=payload["id"], name=payload["name"], document_type=payload["type"], status=payload["status"],
            updated_at=datetime.now(), pages=payload["pages"], is_demo=payload.get("is_demo", False), overview=payload["overview"],
            legacy_obligations=[], legacy_flags=[],
            clauses=[ClauseRecord(id=clause["id"], document_id=payload["id"], category=clause["category"], heading=clause["heading"], page=clause["page"], text=clause["text"], clause_order=clause["order"]) for clause in payload.get("clauses", [])],
            obligation_records=[ObligationRecord(document_id=payload["id"], **obligation) for obligation in payload.get("obligations", [])],
            flag_records=[FlagRecord(document_id=payload["id"], **flag) for flag in payload.get("flags", [])],
        )
        session.merge(record)
        session.merge(DocumentAccess(document_id=payload["id"], user_id=owner_id))
        session.commit()

def _to_payload(record: DocumentRecord) -> dict[str, Any]:
    clauses = sorted(record.clauses, key=lambda clause: clause.clause_order)
    obligations = sorted(record.obligation_records, key=lambda item: item.id)
    flags = sorted(record.flag_records, key=lambda item: item.id)
    return {
        "id": record.id, "name": record.name, "type": record.document_type, "status": record.status,
        "updated_at": record.updated_at.strftime("%d %b %Y"), "pages": record.pages, "is_demo": record.is_demo,
        "overview": record.overview,
        "obligations": [{"id": item.id, "party": item.party, "action": item.action, "trigger": item.trigger, "amount": item.amount, "clause_id": item.clause_id, "certainty": item.certainty} for item in obligations],
        "flags": [{"id": item.id, "title": item.title, "kind": item.kind, "explanation": item.explanation, "why": item.why, "question": item.question, "clause_ids": item.clause_ids} for item in flags],
        "clauses": [{"id": clause.id, "document_id": clause.document_id, "category": clause.category, "heading": clause.heading, "page": clause.page, "text": clause.text, "order": clause.clause_order} for clause in clauses],
    }

def get_document(document_id: str, user_id: str | None = None) -> dict[str, Any] | None:
    with Session(engine) as session:
        record = session.scalar(select(DocumentRecord).where(DocumentRecord.id == document_id))
        if record and user_id and session.scalar(select(DocumentAccess).where(DocumentAccess.document_id == document_id, DocumentAccess.user_id == user_id)) is None:
            return None
        return _to_payload(record) if record else None

def list_documents(user_id: str | None = None) -> list[dict[str, Any]]:
    with Session(engine) as session:
        statement = select(DocumentRecord).order_by(DocumentRecord.updated_at.desc())
        if user_id:
            statement = statement.join(DocumentAccess, DocumentAccess.document_id == DocumentRecord.id).where(DocumentAccess.user_id == user_id)
        records = session.scalars(statement).all()
        return [_to_payload(record) for record in records]

def delete_document(document_id: str, user_id: str | None = None) -> None:
    with Session(engine) as session:
        if user_id and session.scalar(select(DocumentAccess).where(DocumentAccess.document_id == document_id, DocumentAccess.user_id == user_id)) is None:
            return
        session.execute(delete(DocumentRecord).where(DocumentRecord.id == document_id))
        session.commit()

def grant_demo_access(document_ids: list[str], user_id: str) -> None:
    with Session(engine) as session:
        for document_id in document_ids:
            if session.scalar(select(DocumentAccess).where(DocumentAccess.document_id == document_id, DocumentAccess.user_id == user_id)) is None:
                session.add(DocumentAccess(document_id=document_id, user_id=user_id))
        session.commit()
