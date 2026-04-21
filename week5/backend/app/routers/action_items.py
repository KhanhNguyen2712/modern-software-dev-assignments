from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem
from ..responses import success_response
from ..schemas import (
    ActionItemCreate,
    ActionItemRead,
    BulkCompleteRequest,
    PaginatedData,
    SuccessEnvelope,
)

router = APIRouter(prefix="/action-items", tags=["action_items"])


@router.get("/", response_model=SuccessEnvelope[PaginatedData[ActionItemRead]])
def list_items(
    completed: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    base_query = select(ActionItem)
    count_query = select(func.count()).select_from(ActionItem)
    if completed is not None:
        base_query = base_query.where(ActionItem.completed.is_(completed))
        count_query = count_query.where(ActionItem.completed.is_(completed))

    total = db.scalar(count_query) or 0
    offset = (page - 1) * page_size
    rows = db.execute(base_query.offset(offset).limit(page_size)).scalars().all()
    items = [ActionItemRead.model_validate(row).model_dump(mode="json") for row in rows]
    return success_response({"items": items, "total": total, "page": page, "page_size": page_size})


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


@router.post("/bulk-complete", response_model=SuccessEnvelope[dict[str, list[ActionItemRead]]])
def bulk_complete_items(payload: BulkCompleteRequest, db: Session = Depends(get_db)):
    rows = db.execute(select(ActionItem).where(ActionItem.id.in_(payload.ids))).scalars().all()
    items_by_id = {item.id: item for item in rows}

    missing_ids = [item_id for item_id in payload.ids if item_id not in items_by_id]
    if missing_ids:
        raise HTTPException(status_code=404, detail=f"Action item not found: {missing_ids[0]}")

    completed_items = []
    for item_id in payload.ids:
        item = items_by_id[item_id]
        item.completed = True
        db.add(item)
        completed_items.append(item)

    db.flush()
    for item in completed_items:
        db.refresh(item)

    return success_response(
        {
            "items": [
                ActionItemRead.model_validate(item).model_dump(mode="json")
                for item in completed_items
            ]
        }
    )
