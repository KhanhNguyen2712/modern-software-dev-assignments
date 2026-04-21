from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem
from ..responses import success_response
from ..schemas import ActionItemCreate, ActionItemRead, SuccessEnvelope

router = APIRouter(prefix="/action-items", tags=["action_items"])


@router.get("/", response_model=SuccessEnvelope[list[ActionItemRead]])
def list_items(db: Session = Depends(get_db)):
    rows = db.execute(select(ActionItem)).scalars().all()
    return success_response([ActionItemRead.model_validate(row).model_dump(mode="json") for row in rows])


@router.post("/", response_model=SuccessEnvelope[ActionItemRead], status_code=201)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)):
    item = ActionItem(description=payload.description, completed=False)
    db.add(item)
    db.flush()
    db.refresh(item)
    return success_response(ActionItemRead.model_validate(item).model_dump(mode="json"), status_code=201)


@router.put("/{item_id}/complete", response_model=SuccessEnvelope[ActionItemRead])
def complete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    item.completed = True
    db.add(item)
    db.flush()
    db.refresh(item)
    return success_response(ActionItemRead.model_validate(item).model_dump(mode="json"))
