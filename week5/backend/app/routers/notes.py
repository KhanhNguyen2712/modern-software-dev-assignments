from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note
from ..responses import success_response
from ..schemas import DeleteResult, NoteCreate, NoteRead, NoteUpdate, PaginatedData, SuccessEnvelope

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=SuccessEnvelope[PaginatedData[NoteRead]])
def list_notes(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.scalar(select(func.count()).select_from(Note)) or 0
    offset = (page - 1) * page_size
    rows = db.execute(select(Note).offset(offset).limit(page_size)).scalars().all()
    items = [NoteRead.model_validate(row).model_dump(mode="json") for row in rows]
    return success_response({"items": items, "total": total, "page": page, "page_size": page_size})


@router.post("/", response_model=SuccessEnvelope[NoteRead], status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)):
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return success_response(NoteRead.model_validate(note).model_dump(mode="json"), status_code=201)


@router.get("/search", response_model=SuccessEnvelope[PaginatedData[NoteRead]])
def search_notes(
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort: Literal["created_desc", "title_asc"] = "created_desc",
    db: Session = Depends(get_db),
):
    base_query = select(Note)
    count_query = select(func.count()).select_from(Note)

    if q:
        filter_clause = or_(Note.title.ilike(f"%{q}%"), Note.content.ilike(f"%{q}%"))
        base_query = base_query.where(filter_clause)
        count_query = count_query.where(filter_clause)

    if sort == "title_asc":
        base_query = base_query.order_by(Note.title.asc(), Note.id.asc())
    else:
        base_query = base_query.order_by(desc(Note.id))

    total = db.scalar(count_query) or 0
    offset = (page - 1) * page_size
    rows = db.execute(base_query.offset(offset).limit(page_size)).scalars().all()
    items = [NoteRead.model_validate(row).model_dump(mode="json") for row in rows]
    return success_response({"items": items, "total": total, "page": page, "page_size": page_size})


@router.get("/{note_id}", response_model=SuccessEnvelope[NoteRead])
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return success_response(NoteRead.model_validate(note).model_dump(mode="json"))


@router.put("/{note_id}", response_model=SuccessEnvelope[NoteRead])
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note.title = payload.title
    note.content = payload.content
    db.add(note)
    db.flush()
    db.refresh(note)
    return success_response(NoteRead.model_validate(note).model_dump(mode="json"))


@router.delete("/{note_id}", response_model=SuccessEnvelope[DeleteResult])
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.flush()
    return success_response({"deleted": True, "id": note_id})
