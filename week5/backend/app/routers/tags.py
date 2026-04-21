from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Tag
from ..responses import success_response
from ..schemas import SuccessEnvelope, TagCreate, TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=SuccessEnvelope[list[TagRead]])
def list_tags(db: Session = Depends(get_db)):
    rows = db.execute(select(Tag).order_by(Tag.name.asc())).scalars().all()
    return success_response([TagRead.model_validate(row).model_dump(mode="json") for row in rows])


@router.post("/", response_model=SuccessEnvelope[TagRead], status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)):
    existing = db.execute(select(Tag).where(Tag.name == payload.name)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")

    tag = Tag(name=payload.name)
    db.add(tag)
    db.flush()
    db.refresh(tag)
    return success_response(TagRead.model_validate(tag).model_dump(mode="json"), status_code=201)


@router.delete("/{tag_id}", response_model=SuccessEnvelope[dict[str, object]])
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    db.delete(tag)
    db.flush()
    return success_response({"deleted": True, "id": tag_id})
