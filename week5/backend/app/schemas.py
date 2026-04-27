from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

NoteTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
NoteContent = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=5000)]
ActionDescription = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)
]
TagName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50, pattern=r"^\w+$")
]


class TagCreate(BaseModel):
    name: TagName


class TagRead(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NoteCreate(BaseModel):
    title: NoteTitle
    content: NoteContent
    tags: list[str] = []


class NoteUpdate(BaseModel):
    title: NoteTitle
    content: NoteContent
    tags: list[str] = []


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    tags: list[TagRead] = []

    model_config = ConfigDict(from_attributes=True)


class ExtractionResult(BaseModel):
    action_items: list[str]
    tags: list[str]


class NoteSearchResponse(BaseModel):
    items: list[NoteRead]
    total: int
    page: int
    page_size: int


class ActionItemCreate(BaseModel):
    description: ActionDescription


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActionItemSearchResponse(BaseModel):
    items: list[ActionItemRead]
    total: int
    page: int
    page_size: int


class BulkCompleteRequest(BaseModel):
    ids: list[int] = Field(min_length=1)

    @field_validator("ids")
    @classmethod
    def validate_ids(cls, value: list[int]) -> list[int]:
        if any(item_id <= 0 for item_id in value):
            msg = "ids must contain only positive integers"
            raise ValueError(msg)
        return value


class BulkCompleteResponse(BaseModel):
    items: list[ActionItemRead]
    count: int
