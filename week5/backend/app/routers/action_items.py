from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem
from ..schemas import (
    ActionItemCreate,
    ActionItemRead,
    ActionItemSearchResponse,
    BulkCompleteRequest,
    BulkCompleteResponse,
)

router = APIRouter(prefix="/action-items", tags=["action_items"])


@router.get("/", response_model=ActionItemSearchResponse)
def list_items(
    completed: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> ActionItemSearchResponse:
    stmt = select(ActionItem)
    if completed is not None:
        stmt = stmt.where(ActionItem.completed.is_(completed))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar_one()

    rows = (
        db.execute(
            stmt.order_by(desc(ActionItem.created_at), desc(ActionItem.id))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .scalars()
        .all()
    )
    return ActionItemSearchResponse(
        items=[ActionItemRead.model_validate(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=ActionItemRead, status_code=201)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> ActionItemRead:
    item = ActionItem(description=payload.description, completed=False)
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.post("/bulk-complete", response_model=BulkCompleteResponse)
def bulk_complete_items(
    payload: BulkCompleteRequest, db: Session = Depends(get_db)
) -> BulkCompleteResponse:
    unique_ids = list(dict.fromkeys(payload.ids))
    rows = (
        db.execute(select(ActionItem).where(ActionItem.id.in_(unique_ids)).order_by(ActionItem.id.asc()))
        .scalars()
        .all()
    )
    found_ids = {row.id for row in rows}
    missing_ids = [item_id for item_id in unique_ids if item_id not in found_ids]
    if missing_ids:
        raise HTTPException(status_code=404, detail=f"Action items not found: {missing_ids}")

    order_lookup = {item_id: index for index, item_id in enumerate(unique_ids)}
    for row in rows:
        row.completed = True
        db.add(row)

    db.flush()
    for row in rows:
        db.refresh(row)

    ordered_rows = sorted(rows, key=lambda row: order_lookup[row.id])
    items = [ActionItemRead.model_validate(row) for row in ordered_rows]
    return BulkCompleteResponse(items=items, count=len(items))


@router.put("/{item_id}/complete", response_model=ActionItemRead)
def complete_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    item.completed = True
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)
