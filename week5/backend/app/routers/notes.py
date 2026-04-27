from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem, Note, Tag
from ..schemas import (
    ExtractionResult,
    NoteCreate,
    NoteRead,
    NoteSearchResponse,
    NoteUpdate,
)
from ..services.extract import extract_action_items, extract_hashtags

router = APIRouter(prefix="/notes", tags=["notes"])

NOTE_SORTS = {
    "created_desc": (desc(Note.created_at), desc(Note.id)),
    "created_asc": (Note.created_at.asc(), Note.id.asc()),
    "title_asc": (Note.title.asc(), Note.id.asc()),
    "title_desc": (desc(Note.title), desc(Note.id)),
}


def get_or_create_tags(db: Session, names: list[str]) -> list[Tag]:
    if not names:
        return []
    normalized = list(dict.fromkeys(name.strip().lower() for name in names if name.strip()))
    existing = db.execute(select(Tag).where(Tag.name.in_(normalized))).scalars().all()
    existing_names = {t.name for t in existing}
    new_tags = [Tag(name=name) for name in normalized if name not in existing_names]
    for t in new_tags:
        db.add(t)
    db.flush()
    return list(existing) + new_tags


@router.get("/", response_model=list[NoteRead])
def list_notes(db: Session = Depends(get_db)) -> list[NoteRead]:
    rows = db.execute(select(Note).order_by(*NOTE_SORTS["created_desc"])).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    if payload.tags:
        note.tags = get_or_create_tags(db, payload.tags)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.get("/search", response_model=NoteSearchResponse)
def search_notes(
    q: str = "",
    tag: str = "",
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    sort: str = Query("created_desc"),
    db: Session = Depends(get_db),
) -> NoteSearchResponse:
    sort_columns = NOTE_SORTS.get(sort)
    if sort_columns is None:
        raise HTTPException(status_code=400, detail="Unsupported sort value")

    stmt = select(Note)
    if tag:
        stmt = stmt.join(Note.tags).where(Tag.name == tag.lower())

    query = q.strip().lower()
    if query:
        pattern = f"%{query}%"
        stmt = stmt.where(
            or_(
                func.lower(Note.title).like(pattern),
                func.lower(Note.content).like(pattern),
            )
        )

    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.execute(count_stmt).scalar_one()
    rows = (
        db.execute(
            stmt.order_by(*sort_columns).offset((page - 1) * page_size).limit(page_size)
        )
        .scalars()
        .all()
    )
    return NoteSearchResponse(
        items=[NoteRead.model_validate(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)


@router.put("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note.title = payload.title
    note.content = payload.content
    note.tags = get_or_create_tags(db, payload.tags)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> Response:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.flush()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{note_id}/extract", response_model=ExtractionResult)
def extract_from_note(
    note_id: int, apply: bool = False, db: Session = Depends(get_db)
) -> ExtractionResult:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    action_items = extract_action_items(note.content)
    tags = extract_hashtags(note.content)

    if apply:
        # Create action items if they don't exist
        for desc_text in action_items:
            existing = db.execute(
                select(ActionItem).where(ActionItem.description == desc_text)
            ).scalar_one_or_none()
            if not existing:
                item = ActionItem(description=desc_text)
                db.add(item)

        # Update note tags
        if tags:
            new_tags = get_or_create_tags(db, tags)
            current_tag_ids = {t.id for t in note.tags}
            for t in new_tags:
                if t.id not in current_tag_ids:
                    note.tags.append(t)
            db.add(note)

        db.flush()

    return ExtractionResult(action_items=action_items, tags=tags)
