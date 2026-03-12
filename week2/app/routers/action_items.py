from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import (
    ActionItemResponse,
    ActionItemsExtractionResponse,
    ExtractActionItemsRequest,
    MarkActionItemDoneRequest,
)
from ..services.extract import (
    ExtractionServiceError,
    extract_action_items,
    extract_action_items_llm,
)


router = APIRouter(prefix="/action-items", tags=["action-items"])


def _persist_extracted_items(items: list[str], note_id: int | None) -> list[ActionItemResponse]:
    ids = db.insert_action_items(items, note_id=note_id)
    return [
        ActionItemResponse(id=item_id, note_id=note_id, text=text, done=False, created_at=None)
        for item_id, text in zip(ids, items)
    ]


@router.post("/extract", response_model=ActionItemsExtractionResponse)
def extract(payload: ExtractActionItemsRequest) -> ActionItemsExtractionResponse:
    note_id = db.insert_note(payload.text) if payload.save_note else None
    items = extract_action_items(payload.text)
    return ActionItemsExtractionResponse(
        note_id=note_id, items=_persist_extracted_items(items, note_id)
    )


@router.post("/extract-llm", response_model=ActionItemsExtractionResponse)
def extract_llm(payload: ExtractActionItemsRequest) -> ActionItemsExtractionResponse:
    note_id = db.insert_note(payload.text) if payload.save_note else None
    try:
        items = extract_action_items_llm(payload.text)
    except ExtractionServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return ActionItemsExtractionResponse(
        note_id=note_id, items=_persist_extracted_items(items, note_id)
    )


@router.get("", response_model=list[ActionItemResponse])
def list_all(note_id: int | None = None) -> list[ActionItemResponse]:
    rows = db.list_action_items(note_id=note_id)
    return [
        ActionItemResponse(
            id=r["id"],
            note_id=r["note_id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{action_item_id}/done", response_model=ActionItemResponse)
def mark_done(action_item_id: int, payload: MarkActionItemDoneRequest) -> ActionItemResponse:
    updated = db.mark_action_item_done(action_item_id, payload.done)
    if not updated:
        raise HTTPException(status_code=404, detail="action item not found")

    row = db.get_action_item(action_item_id)
    assert row is not None
    return ActionItemResponse(
        id=row["id"],
        note_id=row["note_id"],
        text=row["text"],
        done=bool(row["done"]),
        created_at=row["created_at"],
    )
