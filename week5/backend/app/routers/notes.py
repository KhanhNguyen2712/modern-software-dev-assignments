from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note
from ..responses import success_response
from ..schemas import NoteCreate, NoteRead, SuccessEnvelope

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=SuccessEnvelope[list[NoteRead]])
def list_notes(db: Session = Depends(get_db)):
    rows = db.execute(select(Note)).scalars().all()
    return success_response([NoteRead.model_validate(row).model_dump(mode="json") for row in rows])


@router.post("/", response_model=SuccessEnvelope[NoteRead], status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)):
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return success_response(NoteRead.model_validate(note).model_dump(mode="json"), status_code=201)


@router.get("/search/", response_model=SuccessEnvelope[list[NoteRead]])
def search_notes(q: str | None = None, db: Session = Depends(get_db)):
    if not q:
        rows = db.execute(select(Note)).scalars().all()
    else:
        rows = (
            db.execute(select(Note).where((Note.title.contains(q)) | (Note.content.contains(q))))
            .scalars()
            .all()
        )
    return success_response([NoteRead.model_validate(row).model_dump(mode="json") for row in rows])


@router.get("/{note_id}", response_model=SuccessEnvelope[NoteRead])
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return success_response(NoteRead.model_validate(note).model_dump(mode="json"))
