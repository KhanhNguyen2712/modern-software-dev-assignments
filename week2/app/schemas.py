from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class NoteCreateRequest(BaseModel):
    content: str = Field(..., description="Free-form note content.")

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        content = value.strip()
        if not content:
            raise ValueError("content is required")
        return content


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


class ExtractActionItemsRequest(BaseModel):
    text: str = Field(..., description="Raw notes to analyze.")
    save_note: bool = Field(default=False, description="Persist the source note before extracting.")

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("text is required")
        return text


class ActionItemResponse(BaseModel):
    id: int
    note_id: int | None
    text: str
    done: bool = False
    created_at: str | None = None


class ActionItemsExtractionResponse(BaseModel):
    note_id: int | None
    items: list[ActionItemResponse]


class MarkActionItemDoneRequest(BaseModel):
    done: bool = True
