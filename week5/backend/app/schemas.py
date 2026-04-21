from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, StringConstraints

T = TypeVar("T")

NonEmptyTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
NonEmptyContent = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=5000)]
NonEmptyDescription = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=500),
]


class NoteCreate(BaseModel):
    title: NonEmptyTitle
    content: NonEmptyContent


class NoteUpdate(BaseModel):
    title: NonEmptyTitle
    content: NonEmptyContent


class NoteRead(BaseModel):
    id: int
    title: str
    content: str

    model_config = ConfigDict(from_attributes=True)


class ActionItemCreate(BaseModel):
    description: NonEmptyDescription


class BulkCompleteRequest(BaseModel):
    ids: list[int]


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool

    model_config = ConfigDict(from_attributes=True)


class ErrorInfo(BaseModel):
    code: str
    message: str


class ErrorEnvelope(BaseModel):
    ok: Literal[False] = False
    error: ErrorInfo


class SuccessEnvelope(BaseModel, Generic[T]):
    ok: Literal[True] = True
    data: T


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class DeleteResult(BaseModel):
    deleted: Literal[True]
    id: int
